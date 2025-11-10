# Summary: OAuth, SSE, and Integration Approach

<!-- markdownlint-disable MD022 MD013 -->

## You Were Absolutely Right ✓

After deeper research, here's what I found:

### 1. OAuth - YES (for Cloud API)

**Cloud API** (<https://tahomalink.com>):

- ✅ Uses OAuth 2.0 password grant
- ✅ Has access_token and refresh_token
- ✅ Token expires and needs refresh

**Local API** (<https://gateway-{pin}.local:8443>):

- ❌ No OAuth
- ✅ Simple Bearer token (generate in app)
- ✅ Token doesn't expire

### 2. SSE - NO (Both APIs use polling)

**I was wrong about SSE**. Neither TaHoma API uses Server-Sent Events:

- **Both APIs**: Event polling with register/fetch pattern
- **Your PowerView code**: Uses SSE streaming
- **Major difference**: You'll need to replace SSE with polling

## The Full Picture

### Three APIs to Consider

| API | Auth | Events | Best For |
|-----|------|--------|----------|
| **PowerView** (Current) | None | SSE streaming | Hunter Douglas shades |
| **TaHoma Local** | Bearer token | Polling | Local Somfy control |
| **TaHoma Cloud** | OAuth 2.0 | Polling | Remote Somfy control |

## For Your Phantom Blinds Project

Since you're getting a Somfy TaHoma box, you need to switch from PowerView to TaHoma API.

### Recommended Approach: Local API

**Why Local API**:

1. ✅ Simpler (no OAuth complexity)
2. ✅ Lower latency
3. ✅ No cloud dependency
4. ✅ No rate limits (cloud has 1 call/min for GET)
5. ✅ Perfect for home automation

**Implementation**:

```python
# 1. User enables Developer Mode in TaHoma app
# 2. User generates token
# 3. Store token in Polyglot config
# 4. Use token for all requests

headers = {
    "Authorization": f"Bearer {token}",
    "accept": "application/json"
}
```text

## Integration Pattern from udi_python_interface

Looking at the **udi_python_interface** examples and patterns:

### Key Components You're Already Using

```python
from udi_interface import Node, LOGGER, Custom, LOG_HANDLER

class Controller(Node):
    def __init__(self, poly, primary, address, name):
        super().__init__(poly, primary, address, name)
        self.poly = poly

        # Custom data storage
        self.Parameters = Custom(self.poly, "customparams")
        self.Data = Custom(self.poly, "customdata")

        # Subscribe to events
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        self.poly.subscribe(self.poly.STOP, self.stop)
```text

### Pattern for API Integration

From looking at other UDI nodeservers (Ring, examples), here's the recommended pattern:

```python
class TaHomaController(Node):
    def __init__(self, poly, primary, address, name):
        super().__init__(poly, primary, address, name)

        # Initialize TaHoma client
        self.tahoma_client = None
        self.event_listener_id = None

        # Event loop for polling
        self.event_loop = asyncio.new_event_loop()
        self.event_thread = Thread(target=self._run_event_loop, daemon=True)

    def start(self):
        """Called once on startup"""
        # Get token from config
        token = self.Parameters.get('tahoma_token')

        # Initialize client
        self.tahoma_client = TaHomaClient(
            token=token,
            gateway=self.Parameters.get('gateway_ip')
        )

        # Start event polling
        self.event_thread.start()

        # Initial discovery
        asyncio.run_coroutine_threadsafe(
            self.discover(),
            self.event_loop
        )

    def _run_event_loop(self):
        """Run async event loop in thread"""
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_forever()

    async def start_event_polling(self):
        """Poll TaHoma events continuously"""
        # Register listener
        self.event_listener_id = await self.tahoma_client.register_event_listener()

        while not self.stop_event.is_set():
            try:
                # Fetch events (max once per second)
                events = await self.tahoma_client.fetch_events(
                    self.event_listener_id
                )

                # Process events
                for event in events:
                    self.process_event(event)

            except Exception as e:
                LOGGER.error(f"Event polling error: {e}")
                # Re-register listener if needed
                self.event_listener_id = await self.tahoma_client.register_event_listener()

            # Wait before next poll (1 second recommended)
            await asyncio.sleep(1)
```text

## Leveraging pyoverkiz Library

**Good news**: There's an excellent library that does the heavy lifting!

### Option 1: Use pyoverkiz (Recommended)

```python
# requirements.txt
pyoverkiz

# In your code
from pyoverkiz.client import OverkizClient
from pyoverkiz.const import OverkizServer

async def initialize_tahoma(self):
    """Initialize TaHoma connection"""
    token = self.Parameters.get('tahoma_token')
    gateway_pin = self.Parameters.get('gateway_pin')  # e.g., "2001-0001-1891"

    # Create client for local API
    self.client = OverkizClient(
        username="",  # Not needed for local API
        password="",  # Not needed for local API
        token=token,
        verify_ssl=True,
        server=OverkizServer(
            name="Somfy TaHoma (local)",
            endpoint=f"https://gateway-{gateway_pin}.local:8443/enduser-mobile-web/1/enduserAPI/",
            manufacturer="Somfy",
            configuration_url=None,
        ),
    )

    # Login (validates token)
    await self.client.login()

    # Get devices
    devices = await self.client.get_devices()
    for device in devices:
        # Create nodes for each device
        self.create_shade_node(device)

    # Start event polling
    asyncio.create_task(self.poll_events())

async def poll_events(self):
    """Poll for events"""
    while True:
        events = await self.client.fetch_events()
        for event in events:
            self.handle_event(event)
        await asyncio.sleep(1)  # Poll every second

async def control_shade(self, device_url, position):
    """Control a shade"""
    from pyoverkiz.models import Command

    command = Command(
        name="setClosure",
        parameters=[position]
    )

    exec_id = await self.client.execute_command(
        device_url,
        command,
        label="ISY Control"
    )

    return exec_id
```text

### Option 2: Build Your Own Client

If you want more control, implement TaHoma API directly. See `TAHOMA_VS_POWERVIEW.md` for details.

## Migration Checklist

From your current PowerView-based code to TaHoma:

- [ ] **Add pyoverkiz dependency** (`pip install pyoverkiz`)
- [ ] **Update configuration** to collect TaHoma token
- [ ] **Replace SSE with event polling**
- [ ] **Update device discovery** to use TaHoma data structures
- [ ] **Map device types** from PowerView capabilities to TaHoma controllableNames
- [ ] **Update control commands** from PowerView format to TaHoma exec/apply
- [ ] **Handle HTTPS with self-signed certs** (pyoverkiz handles this)
- [ ] **Add Bearer token auth** (pyoverkiz handles this)
- [ ] **Update URLs** to TaHoma format (pyoverkiz handles this)

## Conclusion

### You were right about

✅ OAuth exists (for Cloud API)
✅ There are options for authentication

### I was right about

✅ Local API uses simple Bearer token (not OAuth)
✅ Event polling (not SSE) for both APIs

### Best path forward

1. **Use Local API** (simpler, better for home automation)
2. **Use pyoverkiz library** (well-maintained, handles all API details)
3. **Keep your UDI interface patterns** (they're solid)
4. **Replace SSE with polling** (main code change needed)

## Next Steps

1. Review `pyoverkiz` documentation and examples
2. Look at Home Assistant's Overkiz integration for patterns
3. Plan migration from PowerView to TaHoma structure
4. Test with local TaHoma API when hardware arrives

Would you like me to create a detailed migration plan or start adapting your Controller.py for TaHoma?
