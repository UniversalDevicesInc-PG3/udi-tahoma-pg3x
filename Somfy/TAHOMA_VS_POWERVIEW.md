# TaHoma vs PowerView: Key Differences

<!-- markdownlint-disable MD022 MD013 -->

This document outlines the differences between Somfy TaHoma API and Hunter
Douglas PowerView API, which is important since this plugin was adapted from
the PowerView pattern.

## Critical Differences

### 1. Base URL Structure

**PowerView (Current Implementation)**:

```text
http://{gateway_ip}/home/shades/{id}
```text

**TaHoma (Somfy)**:

```text
https://gateway-{pin}.local:8443/enduser-mobile-web/1/enduserAPI/setup/devices/{deviceURL}
```text

### 2. Authentication

| Feature | PowerView | TaHoma |
|---------|-----------|---------|
| Required | No | Yes (Bearer token) |
| Method | - | `Authorization: Bearer <token>` |
| Token Generation | - | Via Developer Mode in app |
| Token Lifespan | - | Persistent until deleted |

### 3. Event System

**PowerView**:

- Server-Sent Events (SSE)
- Streaming connection
- Real-time push notifications
- Endpoint: `GET /home/events?sse=false&raw=true`
- Heartbeat: `100 HELO`

**TaHoma**:

- Event listeners (polling-based)
- Register listener, then poll for events
- Listener expires after 10min inactivity
- Endpoints:
  - `POST /events/register` - Create listener
  - `POST /events/{listenerId}/fetch` - Poll events
  - `POST /events/{listenerId}/unregister` - Cleanup

### 4. Device Identification

**PowerView**:

```json
{
  "id": 12345,
  "name": "base64encodedname"
}
```text

**TaHoma**:

```json
{
  "deviceURL": "io://1234-5678-9012/12345678",
  "label": "Living Room Shade"
}
```text

### 5. Control Commands

**PowerView**:

```http
PUT /home/shades/12345/motion
{
  "positions": {
    "primary": 50,
    "tilt": 0
  }
}
```text

**TaHoma**:

```http
POST /exec/apply
{
  "label": "Move shade",
  "actions": [{
    "deviceURL": "io://1234-5678-9012/12345678",
    "commands": [{
      "name": "setClosure",
      "parameters": [50]
    }]
  }]
}
```text

### 6. State Query

**PowerView**:

```http
GET /home/shades/positions?ids=12345
```text

**TaHoma**:

```http
GET /setup/devices/{deviceURL}/states
GET /setup  # Gets all devices and states
```text

### 7. Security

| Aspect | PowerView | TaHoma |
|--------|-----------|--------|
| Protocol | HTTP | HTTPS |
| Port | 80 | 8443 |
| Certificate | - | Self-signed |
| CA Required | No | Yes (`https://ca.overkiz.com/overkiz-root-ca-2048.crt`) |

### 8. Discovery

**PowerView**:

- Default hostname: `powerview-g3.local`
- Or use IP address
- No special discovery protocol documented

**TaHoma**:

- mDNS service: `_kizboxdev._tcp`
- TXT records include:
  - `gateway_pin`: Gateway PIN (1234-5678-9012)
  - `api_version`: API version
  - `fw_version`: Firmware version

## Implementation Impact

### Current Code (PowerView-based)

```python
# From Controller.py
URL_GATEWAY = "http://{g}/gateway"
URL_HOME = "http://{g}/home"
URL_SHADES_MOTION = "http://{g}/home/shades/{id}/motion"
URL_EVENTS = "http://{g}/home/events?sse=false&raw=true"

# SSE client
async def _client_sse(self):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            async for val in response.content:
                # Process events...
```text

### Required Changes for TaHoma

```python
# New URL structure
URL_BASE = "https://gateway-{pin}.local:8443/enduser-mobile-web/1/enduserAPI"
URL_SETUP = f"{URL_BASE}/setup"
URL_DEVICES = f"{URL_BASE}/setup/devices"
URL_EXEC = f"{URL_BASE}/exec/apply"
URL_EVENT_REGISTER = f"{URL_BASE}/events/register"
URL_EVENT_FETCH = f"{URL_BASE}/events/{{listenerId}}/fetch"

# Add authentication
headers = {
    "Authorization": f"Bearer {self.token}",
    "accept": "application/json"
}

# Replace SSE with event polling
async def _poll_events(self):
    # Register listener
    response = await session.post(URL_EVENT_REGISTER, headers=headers)
    listener_id = response.json()["id"]

    # Poll for events
    while True:
        response = await session.post(
            URL_EVENT_FETCH.format(listenerId=listener_id),
            headers=headers
        )
        events = response.json()
        # Process events...
        await asyncio.sleep(1)  # Poll once per second
```text

## Data Structure Mapping

### Positions

**PowerView**:

```json
{
  "primary": 50,
  "secondary": 0,
  "tilt": 45
}
```text

**TaHoma**:
Uses device states with different names based on controllableName:

```json
{
  "name": "core:ClosureState",
  "type": 1,
  "value": 50
}
```text

### Capabilities

**PowerView**:

- Integer 0-10 indicating features
- See DATA_STRUCTURES.md for mapping

**TaHoma**:

- `controllableName`: String identifier (e.g., "io:RollerShutterGenericIOComponent")
- `definition.commands`: Array of supported commands
- Much more detailed capability description

## Migration Checklist

To adapt this plugin from PowerView to TaHoma:

- [ ] Update base URLs and port to 8443
- [ ] Implement SSL with self-signed cert handling
- [ ] Add Bearer token authentication
- [ ] Replace SSE client with event listener polling
- [ ] Change device ID from integer to deviceURL string
- [ ] Update command structure to use exec/apply format
- [ ] Map PowerView positions to TaHoma states
- [ ] Implement mDNS discovery for `_kizboxdev._tcp`
- [ ] Update configuration to include token storage
- [ ] Revise error handling for TaHoma error codes
- [ ] Update state parsing for TaHoma state types

## Can We Support Both?

Potentially yes, with abstraction:

```python
class GatewayInterface(ABC):
    @abstractmethod
    async def get_devices(self): pass

    @abstractmethod
    async def control_device(self, device_id, command, params): pass

    @abstractmethod
    async def start_event_listener(self): pass

class PowerViewGateway(GatewayInterface):
    # PowerView implementation

class TaHomaGateway(GatewayInterface):
    # TaHoma implementation
```text

This would allow supporting both Hunter Douglas PowerView and Somfy TaHoma from the same plugin.

## Recommendation

Given the significant differences, you have three options:

1. **Fork**: Create separate plugins for PowerView and TaHoma
2. **Abstraction**: Use interface pattern to support both
3. **Focus**: Choose one system and fully optimize for it

The abstraction approach is most flexible but requires more development effort.
