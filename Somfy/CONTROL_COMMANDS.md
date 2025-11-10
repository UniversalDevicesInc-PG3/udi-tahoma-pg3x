# Control Commands

<!-- markdownlint-disable MD022 MD013 -->

This document describes how to control Somfy-based Phantom Blinds.

## Shade Control

### Move Shade to Position

**Endpoint**: `PUT /home/shades/{shade_id}/motion`

**Request Body**:

```json
{
  "positions": {
    "primary": 50,
    "secondary": 0,
    "tilt": 45,
    "velocity": 100
  }
}
```text

**Example**:

```bash
curl -X PUT "http://192.168.1.100/home/shades/12345/motion" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "positions": {
      "primary": 75,
      "tilt": 0,
      "velocity": 100
    }
  }'
```text

### Stop Shade

**Endpoint**: `PUT /home/shades/stop?ids={shade_id}`

**Example**:

```bash
curl -X PUT "http://192.168.1.100/home/shades/stop?ids=12345" \
  -H "Accept: application/json"
```text

### Query Shade Position

**Endpoint**: `GET /home/shades/positions?ids={shade_id}`

**Response**:

```json
{
  "id": 12345,
  "positions": {
    "primary": 50,
    "secondary": 0,
    "tilt": 45,
    "velocity": 100
  }
}
```text

## Scene Control

### Activate Scene

**Endpoint**: `PUT /home/scenes/{scene_id}/activate`

**Example**:

```bash
curl -X PUT "http://192.168.1.100/home/scenes/100/activate" \
  -H "Accept: application/json"
```text

**Response**: Returns the activated scene object

### Get Active Scenes

**Endpoint**: `GET /home/scenes/active`

**Response**:

```json
[
  {
    "id": 100,
    "name": "Morning",
    "activatedAt": "2025-11-07T19:55:10.531Z"
  }
]
```text

## Position Values

### Primary Position

- `0` = Fully closed/down
- `100` = Fully open/up
- Intermediate values for partial positions

### Tilt Position

- `0` = Fully closed (horizontal)
- `50` = 45° angle
- `100` = Fully open (vertical)

For 90° tilt shades:

- Tilt range is limited to 90°

### Velocity

- `0` = Slowest
- `100` = Fastest
- Default is typically `100`

## Common Patterns

### Open Shade Fully

```json
{
  "positions": {
    "primary": 100
  }
}
```text

### Close Shade Fully

```json
{
  "positions": {
    "primary": 0
  }
}
```text

### Set to 50% with Tilt

```json
{
  "positions": {
    "primary": 50,
    "tilt": 50
  }
}
```text

### Dual Shade (Top-Down/Bottom-Up)

```json
{
  "positions": {
    "primary": 60,
    "secondary": 40
  }
}
```text

This creates a viewing band between 40% and 60%.

## Python Implementation Examples

### Using requests library

```python
import requests
import json

gateway = "192.168.1.100"
shade_id = 12345

def move_shade(shade_id, primary=None, secondary=None, tilt=None, velocity=100):
    url = f"http://{gateway}/home/shades/{shade_id}/motion"
    headers = {"accept": "application/json"}

    data = {"positions": {}}
    if primary is not None:
        data["positions"]["primary"] = primary
    if secondary is not None:
        data["positions"]["secondary"] = secondary
    if tilt is not None:
        data["positions"]["tilt"] = tilt
    data["positions"]["velocity"] = velocity

    response = requests.put(url, headers=headers, json=data, timeout=10)
    return response.json() if response.status_code == 200 else False

def stop_shade(shade_id):
    url = f"http://{gateway}/home/shades/stop?ids={shade_id}"
    headers = {"accept": "application/json"}
    response = requests.put(url, headers=headers, timeout=10)
    return response.status_code == 200

def activate_scene(scene_id):
    url = f"http://{gateway}/home/scenes/{scene_id}/activate"
    headers = {"accept": "application/json"}
    response = requests.put(url, headers=headers, timeout=10)
    return response.json() if response.status_code == 200 else False

# Examples
move_shade(12345, primary=75, tilt=0)  # Open to 75%, no tilt
stop_shade(12345)                       # Stop movement
activate_scene(100)                     # Activate scene
```text

### Error Handling

```python
try:
    response = requests.put(url, headers=headers, json=data, timeout=10)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return False

    return response.json()

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    return False
```text

## Rate Limiting

**TODO**: Document any rate limiting or throttling policies

- Minimum time between updates: 3 seconds (as implemented in plugin)
- This prevents overloading the gateway

## Command Timeout

- Default timeout: 10 seconds
- Commands should complete within this timeframe
- Use longer timeouts for scenes that move multiple shades

## Notes

### Position Persistence

- Shade positions are not guaranteed to persist after power loss
- Some Somfy motors may have battery backup for position memory
- Verify specific motor capabilities

### Simultaneous Commands

- Multiple shades can be controlled simultaneously via scenes
- Individual shade commands are processed sequentially
- Consider using scenes for coordinated multi-shade control

### Feedback

- Position changes trigger SSE events
- Subscribe to the event stream for real-time feedback
- Query endpoints for current state without triggering events
