# API Examples

<!-- markdownlint-disable MD022 MD013 -->

This document provides practical examples of working with the Somfy API.

## Complete Workflow Examples

### 1. Initial Setup and Discovery

```python
import requests
import json

gateway = "192.168.1.100"
base_url = f"http://{gateway}"

# Step 1: Verify gateway is accessible
def check_gateway():
    try:
        response = requests.get(f"{base_url}/gateway",
                              headers={"accept": "application/json"},
                              timeout=5)
        if response.status_code == 200:
            print("✓ Gateway is accessible")
            return True
        else:
            print(f"✗ Gateway returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot reach gateway: {e}")
        return False

# Step 2: Get home configuration
def get_home_data():
    response = requests.get(f"{base_url}/home",
                          headers={"accept": "application/json"})
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Found {len(data['rooms'])} rooms")
        print(f"✓ Found {len(data['scenes'])} scenes")
        return data
    return None

# Step 3: List all shades
def list_shades(home_data):
    shades = []
    for room in home_data['rooms']:
        room_name = room['name']
        for shade in room.get('shades', []):
            shade_info = {
                'id': shade['id'],
                'room': room_name,
                'name': shade['name'],
                'type': shade.get('type'),
                'capabilities': shade.get('capabilities')
            }
            shades.append(shade_info)
            print(f"  - {room_name}: Shade {shade['id']} (cap: {shade.get('capabilities')})")
    return shades

# Run discovery
if check_gateway():
    home = get_home_data()
    if home:
        all_shades = list_shades(home)
```text

**Output**:

```text
✓ Gateway is accessible
✓ Found 3 rooms
✓ Found 5 scenes
  - Living Room: Shade 12345 (cap: 7)
  - Living Room: Shade 12346 (cap: 1)
  - Bedroom: Shade 12347 (cap: 0)
```text

### 2. Control Multiple Shades

```python
def control_shades_in_room(room_name, home_data, primary_position):
    """Set all shades in a room to the same position"""
    for room in home_data['rooms']:
        if room['name'] == room_name:
            for shade in room.get('shades', []):
                shade_id = shade['id']
                url = f"{base_url}/home/shades/{shade_id}/motion"
                data = {
                    "positions": {
                        "primary": primary_position,
                        "velocity": 100
                    }
                }
                response = requests.put(url,
                                      headers={"accept": "application/json"},
                                      json=data,
                                      timeout=10)
                if response.status_code == 200:
                    print(f"✓ Shade {shade_id} moving to {primary_position}%")
                else:
                    print(f"✗ Failed to move shade {shade_id}")

# Example: Close all living room shades
control_shades_in_room("Living Room", home, 0)
```text

### 3. Monitor Events in Real-Time

```python
import aiohttp
import asyncio
import json

async def monitor_events():
    """Connect to SSE stream and monitor events"""
    url = f"{base_url}/home/events?sse=false&raw=true"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print("Connected to event stream...")
            async for line in response.content:
                line_str = line.decode().strip()
                if not line_str:
                    continue

                # Handle heartbeat
                if line_str == "100 HELO":
                    print("❤ Heartbeat")
                    continue

                # Parse JSON event
                try:
                    event = json.loads(line_str)
                    event_type = event.get('evt')

                    if event_type == 'shade-position':
                        print(f"📍 Shade {event['id']} moved to {event['positions']}")
                    elif event_type == 'scene-activated':
                        print(f"🎬 Scene {event['id']} activated")
                    elif event_type == 'homedoc-updated':
                        print(f"🏠 Home configuration updated")
                    else:
                        print(f"📨 Event: {event}")
                except json.JSONDecodeError:
                    print(f"⚠ Non-JSON line: {line_str}")

# Run event monitor
asyncio.run(monitor_events())
```text

**Output**:

```text
Connected to event stream...
❤ Heartbeat
📍 Shade 12345 moved to {'primary': 50, 'tilt': 0}
🎬 Scene 100 activated
❤ Heartbeat
📍 Shade 12346 moved to {'primary': 75, 'tilt': 45}
```text

### 4. Create a Morning Routine

```python
import time

def morning_routine():
    """Example morning routine"""

    # 1. Activate "Morning" scene
    print("Activating morning scene...")
    scene_id = 100
    response = requests.put(f"{base_url}/home/scenes/{scene_id}/activate",
                          headers={"accept": "application/json"})

    if response.status_code == 200:
        print("✓ Morning scene activated")

    # 2. Wait for shades to move
    time.sleep(10)

    # 3. Adjust specific shade for privacy
    print("Adjusting bedroom shade for privacy...")
    shade_id = 12347
    response = requests.put(
        f"{base_url}/home/shades/{shade_id}/motion",
        headers={"accept": "application/json"},
        json={
            "positions": {
                "primary": 25,  # Slightly open
                "tilt": 75,     # Tilt for light but privacy
                "velocity": 100
            }
        }
    )

    if response.status_code == 200:
        print("✓ Bedroom shade adjusted")

morning_routine()
```text

### 5. Query Current State

```python
def get_shade_status(shade_id):
    """Get current position of a shade"""
    url = f"{base_url}/home/shades/positions?ids={shade_id}"
    response = requests.get(url, headers={"accept": "application/json"})

    if response.status_code == 200:
        data = response.json()
        positions = data.get('positions', {})
        print(f"Shade {shade_id} Status:")
        print(f"  Primary: {positions.get('primary', 'unknown')}%")
        print(f"  Secondary: {positions.get('secondary', 'unknown')}%")
        print(f"  Tilt: {positions.get('tilt', 'unknown')}%")
        return positions
    return None

def get_active_scenes():
    """Get all currently active scenes"""
    url = f"{base_url}/home/scenes/active"
    response = requests.get(url, headers={"accept": "application/json"})

    if response.status_code == 200:
        scenes = response.json()
        print("Active Scenes:")
        for scene in scenes:
            print(f"  - {scene['name']} (ID: {scene['id']})")
            print(f"    Activated at: {scene.get('activatedAt', 'unknown')}")
        return scenes
    return []

# Query status
get_shade_status(12345)
get_active_scenes()
```text

**Output**:

```text
Shade 12345 Status:
  Primary: 50%
  Secondary: 0%
  Tilt: 45%
Active Scenes:
  - Morning (ID: 100)
    Activated at: 2025-11-07T08:00:00.000Z
```text

### 6. Handle Errors Gracefully

```python
def safe_move_shade(shade_id, primary=None, tilt=None):
    """Move shade with error handling"""
    url = f"{base_url}/home/shades/{shade_id}/motion"

    data = {"positions": {"velocity": 100}}
    if primary is not None:
        data["positions"]["primary"] = primary
    if tilt is not None:
        data["positions"]["tilt"] = tilt

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.put(url,
                                  headers={"accept": "application/json"},
                                  json=data,
                                  timeout=10)

            if response.status_code == 200:
                print(f"✓ Shade {shade_id} command successful")
                return True
            elif response.status_code == 404:
                print(f"✗ Shade {shade_id} not found")
                return False
            else:
                print(f"⚠ Attempt {attempt + 1}: Status {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"⚠ Attempt {attempt + 1}: Timeout")
        except requests.exceptions.RequestException as e:
            print(f"⚠ Attempt {attempt + 1}: {e}")

        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff

    print(f"✗ Failed to control shade {shade_id} after {max_retries} attempts")
    return False

# Try to move shade with retries
safe_move_shade(12345, primary=75, tilt=0)
```text

## Testing with curl

### Quick Commands

```bash
# Get home configuration
curl "http://192.168.1.100/home" -H "Accept: application/json" | jq

# Open a shade
curl -X PUT "http://192.168.1.100/home/shades/12345/motion" \
  -H "Content-Type: application/json" \
  -d '{"positions": {"primary": 100, "velocity": 100}}'

# Stop a shade
curl -X PUT "http://192.168.1.100/home/shades/stop?ids=12345"

# Activate scene
curl -X PUT "http://192.168.1.100/home/scenes/100/activate"

# Monitor events
curl -N "http://192.168.1.100/home/events?sse=false&raw=true"
```text

## Integration with ISY Programs

Example of how the plugin translates API calls to ISY node states:

```text
API Position 0-100% → ISY Driver Value 0-100
Scene Activation → ISY Scene Node ST=1
Scene Deactivation → ISY Scene Node ST=0
```text

## Performance Considerations

- **Batch Operations**: Use scenes instead of individual shade commands when possible
- **Rate Limiting**: Wait at least 3 seconds between full home updates
- **Event-Driven**: Subscribe to SSE for real-time updates instead of polling
- **Connection Pooling**: Reuse HTTP sessions for better performance

```python
session = requests.Session()
session.headers.update({"accept": "application/json"})

# Reuse session for multiple requests
response1 = session.get(f"{base_url}/home")
response2 = session.put(f"{base_url}/home/shades/12345/motion", json=data)
```text
