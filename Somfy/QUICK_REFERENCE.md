# Quick Reference Guide

<!-- markdownlint-disable MD022 MD013 -->

## Quick Start

### 1. Connect to Gateway

```python
gateway = "192.168.1.100"  # or "phantom-gateway.local"
base_url = f"http://{gateway}"
```text

### 2. Get All Devices

```python
response = requests.get(f"{base_url}/home")
data = response.json()
```text

### 3. Control a Shade

```python
requests.put(
    f"{base_url}/home/shades/{shade_id}/motion",
    json={"positions": {"primary": 75}}
)
```text

### 4. Activate a Scene

```python
requests.put(f"{base_url}/home/scenes/{scene_id}/activate")
```text

## Common Commands

| Action | Endpoint | Method | Body |
|--------|----------|--------|------|
| Open shade | `/home/shades/{id}/motion` | PUT | `{"positions": {"primary": 100}}` |
| Close shade | `/home/shades/{id}/motion` | PUT | `{"positions": {"primary": 0}}` |
| Stop shade | `/home/shades/stop?ids={id}` | PUT | - |
| Activate scene | `/home/scenes/{id}/activate` | PUT | - |
| Get status | `/home/shades/positions?ids={id}` | GET | - |

## Position Values

| Position | Meaning |
|----------|---------|
| 0 | Fully closed/down |
| 50 | Half open |
| 100 | Fully open/up |

## Capability Codes

| Code | Features | Node Type |
|------|----------|-----------|
| 0, 3 | Primary only | ShadeOnlyPrimary |
| 1, 2, 4 | Primary + Tilt | ShadeNoSecondary |
| 5 | Tilt only | ShadeOnlyTilt |
| 6 | Secondary only | ShadeOnlySecondary |
| 7, 8 | Primary + Secondary | ShadeNoTilt |
| 9, 10 | Primary + Tilt (full) | Shade |

## Event Types

| Event | Description |
|-------|-------------|
| `homedoc-updated` | Configuration changed |
| `scene-add` | New scene added |
| `shade-position` | Shade moved |
| `scene-activated` | Scene started |
| `scene-deactivated` | Scene stopped |

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Not primary gateway |
| 404 | Not found |
| 503 | Setup incomplete |

## SSE Connection

```bash
curl -N "http://{gateway}/home/events?sse=false&raw=true"
```text

Heartbeat: `100 HELO`

## File Organization

| File | Purpose |
|------|---------|
| `README.md` | Overview and introduction |
| `API_ENDPOINTS.md` | Complete endpoint list |
| `SSE_EVENTS.md` | Event stream documentation |
| `DATA_STRUCTURES.md` | JSON schemas |
| `CONTROL_COMMANDS.md` | Control examples |
| `EXAMPLES.md` | Complete workflows |
| `MOTOR_INFO.md` | Somfy motor details |
| `RESEARCH_NOTES.md` | TODOs and gaps |
| `QUICK_REFERENCE.md` | This file |

## Python Quick Examples

### Move shade to 50%

```python
import requests
requests.put(
    f"http://{gateway}/home/shades/12345/motion",
    json={"positions": {"primary": 50, "velocity": 100}},
    headers={"accept": "application/json"}
)
```text

### Get active scenes

```python
response = requests.get(
    f"http://{gateway}/home/scenes/active",
    headers={"accept": "application/json"}
)
scenes = response.json()
```text

### Monitor events

```python
import aiohttp
async with aiohttp.ClientSession() as session:
    async with session.get(f"http://{gateway}/home/events?sse=false&raw=true") as response:
        async for line in response.content:
            print(line.decode().strip())
```text

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Gateway not found | Check IP/hostname, network connectivity |
| 400 error | Verify gateway is primary in multi-gateway setup |
| 503 error | Complete Phantom Blinds setup process |
| No events | Check SSE connection, firewall settings |
| Shade not moving | Verify shade ID, check power, test manually |

## Best Practices

1. **Use scenes** for multi-shade control
2. **Subscribe to SSE** for real-time updates
3. **Rate limit** to 1 update per 3 seconds minimum
4. **Handle retries** with exponential backoff
5. **Close positions** (0) when uncertain
6. **Validate responses** before assuming success

## Related Files in Project

- `nodes/Controller.py` - Main controller implementation
- `nodes/Shade.py` - Shade node types
- `nodes/Scene.py` - Scene node implementation
- `utils/time.py` - Time utilities for ISO dates

## Configuration

Gateway IP set in Polyglot custom parameters:

```yaml
gatewayip: "192.168.1.100"  # or ["192.168.1.100", "192.168.1.101"]
```text
