# CLARIFICATION: OAuth and SSE in TaHoma

<!-- markdownlint-disable MD022 MD013 -->

## You Were Right

You correctly questioned my initial findings. Let me clarify the **two
different Somfy APIs**:

## Two Different Somfy TaHoma APIs

### 1. LOCAL API (Developer Mode)

**What I initially documented** - This is what the official Somfy Developer Mode uses:

- **URL**: `https://gateway-{pin}.local:8443/enduser-mobile-web/1/enduserAPI/`
- **Authentication**: Bearer token (generated from app, no OAuth)
- **Events**: **Polling** (register listener, fetch events every 1 second)
- **Use Case**: Direct local access to your TaHoma gateway

**From Official Docs**:

```python
# Events are polled, not streamed
await client.register_event_listener()  # Returns listener_id
events = await client.fetch_events()    # Poll this every ~1 second
```text

### 2. CLOUD API (Somfy Open API)

**What you were thinking of** - This is the cloud-based API:

- **URL**: `https://tahomalink.com/enduser-mobile-web/1/enduserAPI/`
- **Authentication**: **OAuth 2.0** (with client_id and client_secret)
- **Events**: **Polling** (same event listener pattern)
- **Use Case**: Cloud access via Somfy's servers

**OAuth Flow**:

```python
# From pyoverkiz/client.py lines 276-303
async def somfy_tahoma_get_access_token(self) -> str:
    async with self.session.post(
        SOMFY_API + "/oauth/oauth/v2/token/jwt",
        data=FormData({
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "client_id": SOMFY_CLIENT_ID,
            "client_secret": SOMFY_CLIENT_SECRET,
        }),
    ) as response:
        token = await response.json()
        self._access_token = token["access_token"]
        self._refresh_token = token["refresh_token"]
```text

## The SSE Question

**Neither API uses SSE (Server-Sent Events)!**

Both APIs use **event polling**:

```python
# From pyoverkiz/client.py
async def register_event_listener(self) -> str:
    """Register event listener and return listener ID"""
    response = await self.__post("events/register")
    return response.get("id")

async def fetch_events(self) -> list[Event]:
    """
    Fetch new events from registered listener.
    Rate-limit: 1 call per 1 SECOND
    """
    response = await self.__post(f"events/{self.event_listener_id}/fetch")
    return [Event(**e) for e in response]
```text

The typical pattern is:

```python
# Register once
listener_id = await client.register_event_listener()

# Then poll continuously
while True:
    events = await client.fetch_events()
    # Process events...
    await asyncio.sleep(1)  # Wait 1 second between polls
```text

## Why I Was Confused

1. **Your Hunter Douglas code uses SSE** - It streams events continuously
2. **TaHoma uses polling** - It requires you to fetch events periodically
3. **I initially found the Local API first** - Which has simple Bearer tokens

## Comparison Table

| Feature | Local API | Cloud API | Your Current Code (PowerView) |
|---------|-----------|-----------|-------------------------------|
| **Authentication** | Bearer token (from app) | OAuth 2.0 | None |
| **URL** | `https://gateway-{pin}.local:8443/...` | `https://tahomalink.com/...` | `http://{ip}/home/...` |
| **Events** | Polling (fetch every 1s) | Polling (fetch every 1s) | **SSE streaming** |
| **Listener** | Register + poll | Register + poll | Continuous stream |
| **Token Refresh** | Not needed | Yes (every ~2 weeks) | N/A |

## What This Means for Your Plugin

### Option 1: Use Local API (Simplest)

**Pros**:

- Direct local connection (no cloud dependency)
- Simpler auth (just generate token in app)
- Lower latency
- No OAuth complexity

**Cons**:

- Requires Developer Mode enabled
- User must generate token manually
- Need to handle self-signed certificates

### Option 2: Use Cloud API

**Pros**:

- Works from anywhere (cloud access)
- More "production ready" feel
- Automatic token refresh

**Cons**:

- OAuth 2.0 complexity
- Requires Somfy developer account
- Requires client_id and client_secret
- Cloud dependency
- Rate limited (1 call per minute for GET endpoints)

### Option 3: Support Both

Like the `python-overkiz-api` library does.

## Example: Event Handling Comparison

### Your Current PowerView SSE Code

```python
async def _client_sse(self):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            async for line in response.content:
                # Events stream continuously
                event = json.loads(line.decode())
                self.process_event(event)
```text

### What TaHoma Needs (Polling)

```python
async def _poll_events(self):
    # Register listener once
    listener_id = await self.register_event_listener()

    # Then poll continuously
    while not self.stop_event.is_set():
        try:
            events = await self.fetch_events(listener_id)
            for event in events:
                self.process_event(event)
        except Exception as e:
            # Re-register if listener expired
            listener_id = await self.register_event_listener()

        await asyncio.sleep(1)  # Poll every 1 second max
```text

## Recommendation for Your Project

Since you're setting up **local Phantom Blinds** in your home:

**Use the Local API** (Developer Mode):

1. Enable Developer Mode in TaHoma app
2. Generate token
3. Store token in Polyglot config
4. Use simpler Bearer auth
5. Poll events every 1-2 seconds

This is simpler than OAuth and works great for home automation!

## Key Takeaways

✅ **OAuth**: Only for Cloud API (not required for Local API)
✅ **SSE**: Neither API uses SSE - both use polling
✅ **Your intuition was correct** - There IS OAuth for cloud API
✅ **My initial docs were correct** - For Local API (no OAuth, just Bearer token)
✅ **Big difference from PowerView** - Polling vs. SSE streaming

## References

- Local API: <https://github.com/Somfy-Developer/Somfy-TaHoma-Developer-Mode>
- Cloud API: <https://github.com/tetienne/somfy-open-api>
- Python Client (both): <https://github.com/iMicknl/python-overkiz-api>
- Home Assistant Integration: <https://github.com/home-assistant/core/tree/dev/homeassistant/components/overkiz>

---

**Bottom Line**: You can choose Local API (simple, local only) or Cloud API (OAuth, works anywhere). Both use **event polling**, not SSE.
