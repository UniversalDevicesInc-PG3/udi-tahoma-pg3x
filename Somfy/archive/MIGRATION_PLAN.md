# Migration Plan: PowerView to TaHoma API

<!-- markdownlint-disable MD022 MD013 MD029 -->

## Executive Summary

This document outlines the migration from the current Hunter Douglas
PowerView-based implementation to the Somfy TaHoma API for the Phantom Blinds
nodeserver.

**Timeline Estimate**: 3-5 days of development + testing time
**Complexity**: Medium-High (significant architectural changes)
**Risk**: Medium (event system completely different)

## Current State Analysis

### What Works (Keep)

- ✅ UDI Polyglot interface integration
- ✅ Node structure (Controller, Shade, Scene nodes)
- ✅ Threading and async event loop pattern
- ✅ Configuration management (Custom parameters/data)
- ✅ Discovery pattern
- ✅ Error handling framework
- ✅ Logging infrastructure

### What Needs Changing (Major)

- ❌ **Event System**: SSE streaming → Event polling
- ❌ **Authentication**: None → Bearer token
- ❌ **URL Structure**: PowerView format → TaHoma format
- ❌ **Device IDs**: Integer → String (deviceURL)
- ❌ **Control Commands**: Direct motion → exec/apply format
- ❌ **Device Discovery**: PowerView data → TaHoma setup data
- ❌ **SSL/HTTPS**: Add support for self-signed certificates

## Migration Strategy

### Phase 1: Foundation (Day 1)

**Goal**: Set up TaHoma integration foundation

#### 1.1 Add Dependencies

```bash
# Add to requirements.txt
pyoverkiz>=1.13.0
aiohttp>=3.9.0
```text

#### 1.2 Create TaHoma Client Wrapper

**New file**: `utils/tahoma_client.py`

This will wrap `pyoverkiz` and provide interface compatible with current code structure.

```python
"""TaHoma API client wrapper for Polyglot integration"""

from pyoverkiz.client import OverkizClient
from pyoverkiz.const import OverkizServer
from pyoverkiz.models import Command, Device, Event
from udi_interface import LOGGER
import asyncio

class TaHomaClient:
    """Wrapper around pyoverkiz for TaHoma integration"""

    def __init__(self, token: str, gateway_pin: str, verify_ssl: bool = True):
        self.token = token
        self.gateway_pin = gateway_pin
        self.client = None
        self.event_listener_id = None

    async def connect(self):
        """Initialize connection to TaHoma gateway"""
        # Implementation details

    async def get_devices(self):
        """Get all devices from TaHoma"""
        # Returns standardized device list

    async def register_event_listener(self):
        """Register for event notifications"""
        # Setup event listener

    async def fetch_events(self):
        """Fetch pending events"""
        # Get events since last fetch

    async def execute_command(self, device_url, command_name, parameters):
        """Execute command on device"""
        # Send control command
```text

#### 1.3 Update Configuration Parameters

**File**: `nodes/Controller.py`

Add new configuration parameters in `parameterHandler()`:

```python
def parameterHandler(self, params):
    defaults = {
        "tahoma_token": "",           # NEW: Bearer token from TaHoma app
        "gateway_pin": "",            # NEW: Gateway PIN (e.g., 2001-0001-1891)
        "use_local_api": "true",      # NEW: Use local vs cloud API
        # Keep existing for backward compatibility during migration
        "gatewayip": "gateway-{pin}.local",
    }
```text

### Phase 2: Event System Refactor (Day 2)

**Goal**: Replace SSE streaming with event polling

#### 2.1 Remove SSE Client

**File**: `nodes/Controller.py` lines 774-809

❌ **Remove**:

```python
async def _client_sse(self):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            async for val in response.content:
                # SSE streaming code
```text

✅ **Replace with**:

```python
async def _poll_events(self):
    """Poll TaHoma events (replaces SSE streaming)"""
    try:
        # Register event listener
        if not self.event_listener_id:
            self.event_listener_id = await self.tahoma_client.register_event_listener()
            LOGGER.info(f"Event listener registered: {self.event_listener_id}")

        while not self.stop_event.is_set():
            try:
                # Fetch events (max once per second per Somfy recommendations)
                events = await self.tahoma_client.fetch_events()

                if events:
                    LOGGER.debug(f"Received {len(events)} events")
                    for event in events:
                        self.process_tahoma_event(event)

            except InvalidEventListenerIdException:
                # Listener expired, re-register
                LOGGER.warning("Event listener expired, re-registering...")
                self.event_listener_id = await self.tahoma_client.register_event_listener()

            except Exception as e:
                LOGGER.error(f"Event polling error: {e}", exc_info=True)
                await asyncio.sleep(5)  # Back off on error
                continue

            # Poll every 1 second (Somfy recommendation)
            await asyncio.sleep(1)

    except Exception as e:
        LOGGER.error(f"Fatal event polling error: {e}", exc_info=True)
    finally:
        self.event_polling_in = False
```text

#### 2.2 Update Event Processing

**File**: `nodes/Controller.py` lines 665-773

Map PowerView events to TaHoma events:

| PowerView Event | TaHoma Event | Action |
|----------------|--------------|--------|
| `homedoc-updated` | `GatewayAliveEvent` | Refresh setup |
| `scene-add` | `ScenarioAddedEvent` | Add scene node |
| `scene-activated` | `ExecutionRegisteredEvent` (type=scenario) | Update scene status |
| `shade-position` | `DeviceStateChangedEvent` | Update shade position |

```python
def process_tahoma_event(self, event):
    """Process event from TaHoma (replaces process_powerview_event)"""
    event_name = event.name

    LOGGER.info(f"Processing TaHoma event: {event_name}")

    if event_name == "DeviceStateChangedEvent":
        # Device state changed (shade moved, etc.)
        self.handle_device_state_event(event)

    elif event_name == "ExecutionRegisteredEvent":
        # Command execution started
        self.handle_execution_event(event)

    elif event_name == "ExecutionStateChangedEvent":
        # Command execution state changed
        self.handle_execution_state_event(event)

    elif event_name == "GatewayAliveEvent":
        # Gateway heartbeat / connection restored
        LOGGER.debug("Gateway alive event")

    # Add other event types as needed
```text

### Phase 3: Device Discovery (Day 2-3)

**Goal**: Map TaHoma devices to Polyglot nodes

#### 3.1 Update Discovery Method

**File**: `nodes/Controller.py` lines 581-664

```python
async def discover(self):
    """Discover devices from TaHoma (replaces PowerView discovery)"""
    if self.discovery_in:
        LOGGER.info("Discover already running.")
        return False

    self.discovery_in = True
    LOGGER.info("Starting TaHoma discovery...")

    nodes_existing = self.poly.getNodes()
    nodes_old = [node for node in nodes_existing if node != "hdctrl"]
    nodes_new = []

    try:
        # Get all devices from TaHoma
        devices = await self.tahoma_client.get_devices()

        # Map devices to shade/scene nodes
        for device in devices:
            node_address = self._device_url_to_address(device.deviceURL)
            nodes_new.append(node_address)

            if node_address not in nodes_existing:
                node = self._create_device_node(device)
                if node:
                    self.poly.addNode(node)
                    self.wait_for_node_done()

        # Get scenarios (scenes)
        scenarios = await self.tahoma_client.get_scenarios()
        for scenario in scenarios:
            node_address = f"scene{scenario.oid}"
            nodes_new.append(node_address)

            if node_address not in nodes_existing:
                node = Scene(
                    self.poly,
                    self.address,
                    node_address,
                    scenario.label,
                    scenario.oid
                )
                self.poly.addNode(node)
                self.wait_for_node_done()

        # Cleanup removed devices
        self._cleanup_nodes(nodes_new, nodes_old)

        self.numNodes = len(nodes_new)
        self.setDriver("GV0", self.numNodes)

        LOGGER.info(f"Discovery complete: {self.numNodes} nodes")
        return True

    except Exception as e:
        LOGGER.error(f"Discovery failed: {e}", exc_info=True)
        return False
    finally:
        self.discovery_in = False
```text

#### 3.2 Device Type Mapping

**TaHoma → Polyglot Node Mapping**:

| TaHoma controllableName | Polyglot Node Class | Features |
|------------------------|---------------------|----------|
| `io:RollerShutterGenericIOComponent` | `Shade` | Primary position |
| `io:ExteriorVenetianBlindIOComponent` | `Shade` | Primary + Tilt |
| `io:DualRollerShutterIOComponent` | `Shade` | Primary + Secondary |
| `rts:RollerShutterRTSComponent` | `ShadeOnlyPrimary` | Basic control only |

```python
def _create_device_node(self, device):
    """Create appropriate node type based on TaHoma device"""

    # Extract device type from controllableName
    controllable = device.controllable_name

    # Map to node classes
    if "VenetianBlind" in controllable:
        # Has tilt capability
        return Shade(self.poly, self.address, address, device.label, device.deviceURL)
    elif "DualRollerShutter" in controllable:
        # Has primary + secondary
        return ShadeNoTilt(self.poly, self.address, address, device.label, device.deviceURL)
    elif "RollerShutter" in controllable:
        # Standard roller shutter
        return ShadeOnlyPrimary(self.poly, self.address, address, device.label, device.deviceURL)
    else:
        # Generic device
        LOGGER.warning(f"Unknown device type: {controllable}")
        return ShadeOnlyPrimary(self.poly, self.address, address, device.label, device.deviceURL)
```text

### Phase 4: Control Commands (Day 3)

**Goal**: Update shade control to use TaHoma exec/apply

#### 4.1 Update Shade Control Methods

**File**: `nodes/Shade.py`

❌ **Old PowerView format**:

```python
def setPosition(self, command):
    val = int(command.get('value'))
    url = URL_SHADES_MOTION.format(g=self.gateway, id=self.sid)
    data = {"positions": {"primary": val}}
    self.controller.put(url, data)
```text

✅ **New TaHoma format**:

```python
async def setPosition(self, command):
    """Set shade position (0-100)"""
    val = int(command.get('value'))

    try:
        # Execute TaHoma command
        exec_id = await self.controller.tahoma_client.execute_command(
            device_url=self.device_url,
            command_name="setClosure",
            parameters=[val],
            label="ISY Position Control"
        )

        LOGGER.info(f"Shade {self.address} moving to {val}% (exec: {exec_id})")

        # Position will be updated via event

    except Exception as e:
        LOGGER.error(f"Failed to set position: {e}")
```text

#### 4.2 Command Mapping

| PowerView Command | TaHoma Command | Parameters |
|------------------|----------------|------------|
| Move to position (primary) | `setClosure` | `[position]` (0-100) |
| Move to position (secondary) | `setDeployment` | `[position]` (0-100) |
| Set tilt | `setOrientation` | `[angle]` (0-100) |
| Stop | `stop` | `[]` |
| Open | `open` | `[]` |
| Close | `close` | `[]` |

### Phase 5: Data Structure Updates (Day 3-4)

**Goal**: Update internal data structures

#### 5.1 Shade Data Storage

**File**: `nodes/Controller.py`

Replace integer shade IDs with deviceURL strings:

```python
# OLD: shades_map[12345] = {...}
# NEW: shades_map["io://1234-5678-9012/12345678"] = {...}

self.shades_map = {}  # Key: deviceURL (string), Value: device data

def get_shade_data(self, device_url: str):
    """Get shade data by deviceURL"""
    with self.shades_map_lock:
        return self.shades_map.get(device_url)

def update_shade_data(self, device_url: str, data):
    """Update shade data by deviceURL"""
    with self.shades_map_lock:
        if device_url in self.shades_map:
            self.shades_map[device_url].update(data)
        else:
            self.shades_map[device_url] = data
```text

#### 5.2 Node Addressing

Convert deviceURL to valid Polyglot address (max 14 chars, alphanumeric):

```python
def _device_url_to_address(self, device_url: str) -> str:
    """
    Convert TaHoma deviceURL to Polyglot node address

    deviceURL format: io://1234-5678-9012/12345678
    Node address: shade_12345678 (max 14 chars)
    """
    # Extract device ID from URL
    device_id = device_url.split('/')[-1]

    # Create valid address (alphanumeric, max 14 chars)
    address = f"sh{device_id}"[:14]

    return address.lower()
```text

### Phase 6: State Management (Day 4)

**Goal**: Map TaHoma states to ISY drivers

#### 6.1 State Mapping

**TaHoma States → ISY Drivers**:

| TaHoma State | ISY Driver | UOM | Notes |
|--------------|------------|-----|-------|
| `core:ClosureState` | `ST` | 51 (%) | Primary position (0-100) |
| `core:DeploymentState` | `GV1` | 51 (%) | Secondary position |
| `core:SlateOrientationState` | `GV2` | 51 (%) | Tilt angle |
| `core:StatusState` | `GV10` | 25 (index) | Device status |
| `core:DiscreteRSSILevelState` | `GV11` | 25 (index) | Signal strength |

```python
def update_drivers_from_states(self, states):
    """Update node drivers from TaHoma device states"""

    state_map = {
        'core:ClosureState': ('ST', 51),
        'core:DeploymentState': ('GV1', 51),
        'core:SlateOrientationState': ('GV2', 51),
        'core:StatusState': ('GV10', 25),
    }

    for state in states:
        if state.name in state_map:
            driver, uom = state_map[state.name]
            value = state.value

            # Convert if needed
            if state.type == 1:  # Integer
                value = int(value)
            elif state.type == 3:  # String
                value = self._status_to_index(value)

            self.setDriver(driver, value, report=True, force=False, uom=uom)
```text

### Phase 7: URL Management (Day 4)

**Goal**: Replace PowerView URLs with TaHoma URLs

#### 7.1 Remove PowerView URLs

**File**: `nodes/Controller.py` lines 46-57

❌ **Remove all PowerView URLs**:

```python
URL_DEFAULT_GATEWAY = "powerview-g3.local"
URL_GATEWAY = "http://{g}/gateway"
URL_HOME = "http://{g}/home"
# ... etc
```text

✅ **TaHoma URLs handled by pyoverkiz** - no manual URL management needed!

The `pyoverkiz` library handles all URL construction internally.

### Phase 8: Error Handling (Day 4)

**Goal**: Handle TaHoma-specific errors

#### 8.1 Exception Mapping

```python
from pyoverkiz.exceptions import (
    BadCredentialsException,
    NotAuthenticatedException,
    InvalidTokenException,
    TooManyRequestsException,
    InvalidEventListenerIdException,
    ExecutionQueueFullException,
)

async def safe_execute_command(self, device_url, command_name, parameters):
    """Execute command with TaHoma error handling"""
    try:
        return await self.tahoma_client.execute_command(
            device_url, command_name, parameters
        )
    except InvalidTokenException:
        LOGGER.error("Invalid token - user needs to regenerate")
        self.Notices["token"] = "Token invalid - regenerate in TaHoma app"
        return False
    except TooManyRequestsException:
        LOGGER.warning("Rate limited - backing off")
        await asyncio.sleep(5)
        return False
    except ExecutionQueueFullException:
        LOGGER.warning("Execution queue full - try again later")
        return False
    except Exception as e:
        LOGGER.error(f"Command execution failed: {e}")
        return False
```text

### Phase 9: Testing Strategy (Day 5)

**Goal**: Comprehensive testing plan

#### 9.1 Unit Tests

Create test file: `test/test_tahoma_client.py`

```python
import pytest
from unittest.mock import Mock, AsyncMock
from utils.tahoma_client import TaHomaClient

@pytest.mark.asyncio
async def test_connect():
    """Test TaHoma connection"""
    client = TaHomaClient(token="test_token", gateway_pin="1234-5678-9012")
    # Test implementation

@pytest.mark.asyncio
async def test_get_devices():
    """Test device discovery"""
    # Test implementation

@pytest.mark.asyncio
async def test_execute_command():
    """Test command execution"""
    # Test implementation
```text

#### 9.2 Integration Tests

With actual hardware (when available):

1. **Connection Test**
   - Connect to TaHoma gateway
   - Verify token authentication
   - Check SSL certificate handling

2. **Discovery Test**
   - Discover all devices
   - Verify device types mapped correctly
   - Check node creation

3. **Control Test**
   - Move shade to position
   - Stop shade
   - Tilt control (if applicable)

4. **Event Test**
   - Trigger manual control via TaHoma app
   - Verify events received
   - Check state updates in ISY

5. **Long-Running Test**
   - Run for 24+ hours
   - Verify event listener doesn't expire
   - Check for memory leaks

### Phase 10: Documentation (Day 5)

**Goal**: Update all documentation

#### 10.1 User Documentation

- [ ] Update README.md with TaHoma setup instructions
- [ ] Update POLYGLOT_CONFIG.md with new parameters
- [ ] Create setup guide for Developer Mode
- [ ] Document token generation process

#### 10.2 Developer Documentation

- [ ] Update inline code comments
- [ ] Document new data structures
- [ ] Add architecture diagram
- [ ] Create troubleshooting guide

## Migration Checklist

### Pre-Migration

- [ ] Backup current working code
- [ ] Create migration branch in git
- [ ] Review all Somfy documentation
- [ ] Set up test environment

### Code Changes

- [ ] Add pyoverkiz dependency
- [ ] Create TaHomaClient wrapper
- [ ] Update configuration parameters
- [ ] Replace SSE with event polling
- [ ] Update discovery method
- [ ] Map device types
- [ ] Update control commands
- [ ] Update state management
- [ ] Update error handling
- [ ] Remove PowerView URLs

### Testing

- [ ] Unit tests pass
- [ ] Integration tests with hardware
- [ ] Long-running stability test
- [ ] Performance testing
- [ ] Memory leak check

### Documentation

- [ ] Update user documentation
- [ ] Update developer documentation
- [ ] Create migration guide for users
- [ ] Update version history

### Deployment

- [ ] Code review
- [ ] Merge to main branch
- [ ] Tag release
- [ ] Update Polyglot store (if applicable)
- [ ] Announce to users

## Risk Assessment & Mitigation

### High Risk Areas

#### 1. Event System (High Risk)

**Risk**: Event polling may miss events or have timing issues
**Mitigation**:

- Follow Somfy's recommended 1-second poll interval
- Implement robust error handling
- Add event queue for reliability
- Test extensively with hardware

#### 2. Device Mapping (Medium Risk)

**Risk**: TaHoma device types may not map cleanly to existing node types
**Mitigation**:

- Create comprehensive device type mapping
- Allow for unknown device types
- Log unmapped device types for future support
- Test with various Phantom Blinds models

#### 3. Authentication (Medium Risk)

**Risk**: Token expiration or invalid tokens causing failures
**Mitigation**:

- Clear error messages for token issues
- Validate token on startup
- Handle InvalidTokenException gracefully
- Document token regeneration process

#### 4. Backward Compatibility (Low Risk)

**Risk**: Breaking existing PowerView users (if any)
**Mitigation**:

- This is a new plugin for Phantom Blinds
- No backward compatibility needed
- Can maintain PowerView plugin separately if needed

## Rollback Plan

If migration fails:

1. **Revert to PowerView branch**

   ```bash
   git checkout powerview-stable
   ```

2. **Restore from backup**

3. **Document issues encountered**

4. **Re-assess approach**

## Success Criteria

Migration is complete when:

- [x] All devices discovered correctly
- [x] Control commands work (open, close, position, stop)
- [x] Events received and processed correctly
- [x] State updates reflect in ISY
- [x] Runs stable for 24+ hours
- [x] No memory leaks
- [x] Documentation complete
- [x] Tests pass

## Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Foundation | 1 day | None |
| Phase 2: Events | 1 day | Phase 1 |
| Phase 3: Discovery | 1-2 days | Phase 1 |
| Phase 4: Control | 1 day | Phase 3 |
| Phase 5: Data | 1 day | Phase 3 |
| Phase 6: State | 1 day | Phase 3, 4 |
| Phase 7: URLs | 0.5 days | Phase 1 |
| Phase 8: Errors | 0.5 days | All phases |
| Phase 9: Testing | 1 day | All phases |
| Phase 10: Docs | 1 day | All phases |
| **Total** | **8-9 days** | |

Add buffer for:

- Hardware delivery delays
- Unexpected API quirks
- Testing iterations
- Bug fixes

**Realistic Timeline**: 2-3 weeks

## Questions to Resolve

1. **Device Identification**
   - How to uniquely identify devices between reboots?
   - Should we cache deviceURL mappings?

2. **Scene Execution**
   - How are scenes defined in TaHoma?
   - Can we create scenes via API or only through app?

3. **Position Feedback**
   - What events indicate position changes?
   - How often do position updates arrive?

4. **Multi-Gateway Support**
   - Do Phantom installations use multiple gateways?
   - If yes, how to handle discovery across gateways?

5. **Developer Mode Requirements**
   - Is Developer Mode required for all users?
   - What are limitations if not enabled?

## Next Steps

1. **Review this document** - Discuss and refine
2. **Set up development environment** - Install pyoverkiz
3. **Create TaHomaClient wrapper** - Start Phase 1
4. **Wait for hardware** - Can do Phases 1-2 without hardware
5. **Integration testing** - Requires physical TaHoma gateway

---

**Document Version**: 1.0
**Created**: 2025-11-09
**Author**: GitHub Copilot CLI
**Status**: Draft - Ready for Review
