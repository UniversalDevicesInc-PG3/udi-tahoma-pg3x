# Future Enhancements

<!-- markdownlint-disable MD022 MD013 -->

This document tracks potential improvements and optional features for the Phantom Blinds TaHoma NodeServer.

## Priority: Medium

### YAML Configuration File Support

**Status**: Not implemented
**Date Added**: 2025-11-11
**Source**: User request for enhanced configuration management

**Description**:
Add support for reading configuration from a YAML file in addition to Polyglot
UI parameters. This would allow bulk configuration and easier management of
complex setups.

**Implementation Plan**:

1. Add `config_file` parameter to Polyglot configuration
   - User provides path to YAML file (e.g., `/path/to/config.yaml`)
   - Optional parameter - if not provided, use Polyglot params only

2. Load and merge configurations:

   ```python
   # In nodes/Controller.py parameterHandler()
   config_file = self.Parameters.get("config_file", "")
   if config_file and os.path.exists(config_file):
       yaml_params = load_yaml_config(config_file)
       # Merge: Polyglot params take precedence over YAML
       merged_params = {**yaml_params, **polyglot_params}
   ```

3. Configuration precedence (highest to lowest):
   - Polyglot UI parameters (always win)
   - YAML file parameters
   - Default values

4. YAML structure follows `exampleConfigFile.yaml`:
   - `gateway.pin` → `gateway_pin`
   - `gateway.token` → `tahoma_token`
   - `gateway.use_local_api` → `use_local_api`
   - `gateway.verify_ssl` → `verify_ssl`
   - Additional optional parameters as nested structure

**Benefits**:

- Easier bulk configuration management
- Version control for configuration
- Simpler multi-gateway setup (future)
- Template-based deployment
- Better documentation of configuration options

**Code Locations**:

- `nodes/Controller.py` - Add YAML loading in `parameterHandler()`
- `utils/config_validation.py` - Add YAML validation function
- `exampleConfigFile.yaml` - Update with clearer mapping to Polyglot params
- `INSTALLATION.md` - Document YAML config usage

**Considerations**:

- Requires `pyyaml` dependency
- Need error handling for invalid YAML
- Security: Validate file path to prevent directory traversal
- Clear documentation on parameter name mapping
- Polyglot UI should always override YAML (for safety)

**Example Usage**:

```yaml
# myconfig.yaml
gateway:
  pin: "1234-5678-9012"
  token: "abc123xyz..."
  use_local_api: true
  verify_ssl: false
```

Then in Polyglot UI, set: `config_file = /home/polyglot/myconfig.yaml`

---

### Mock Testing with Real API Responses

**Status**: Deferred until post-hardware testing
**Date Added**: 2025-11-11
**Source**: Pre-hardware preparation task #6

**Description**:
Create mock tests using actual TaHoma API responses to validate code behavior without hardware.

**Current State**:

- 84 unit tests exist for utility functions
- No tests for TaHoma API interactions
- No mock responses available

**Implementation Plan**:

1. **During hardware testing**: Record actual API responses
   - Device discovery responses (various device types)
   - Command execution responses (success/failure)
   - Event stream data (motion started/stopped, etc.)
   - Error responses (auth failures, timeouts, etc.)
   - State queries and updates

2. **Create mock fixtures**:

   ```python
   # test/fixtures/tahoma_responses.py
   DISCOVERY_RESPONSE = {...}  # Real response
   COMMAND_SUCCESS = {...}
   COMMAND_FAILURE = {...}
   EVENT_MOTION_STARTED = {...}
   ```

3. **Write mock tests**:
   - `test/test_tahoma_discovery.py` - Device discovery scenarios
   - `test/test_tahoma_commands.py` - Command execution
   - `test/test_tahoma_events.py` - Event handling
   - `test/test_tahoma_errors.py` - Error scenarios

**Benefits**:

- Test without hardware dependency
- Validate error handling paths
- Faster test execution
- Catch regressions early
- Document expected API behavior

**Test Coverage Goals**:

- Device discovery (shades, scenes, various types)
- Command execution (open, close, stop, my, tilt)
- Event processing (motion events, battery alerts)
- Error handling (connection, auth, timeout)
- State management (position updates, status)

**Code Locations**:

- `test/fixtures/` - Store recorded responses
- `test/test_tahoma_*.py` - Mock test files
- `utils/tahoma_client.py` - Code under test

---

### Capacity Limit Warnings

**Status**: Not implemented
**Date Added**: 2025-11-11
**Source**: TaHoma Programming Guide PDF

**Description**:
Add validation and warnings when approaching TaHoma hardware capacity limits.

**Limits** (per TaHoma interface):

- 40 RTS channels
- 50 Zigbee devices
- 40 scenes with schedules

**Implementation Ideas**:

1. Track device counts during discovery
2. Log warnings at 80% capacity (32 RTS, 40 Zigbee, 32 scenes)
3. Log errors at 95% capacity (38 RTS, 48 Zigbee, 38 scenes)
4. Display capacity status in controller node
5. Add custom driver to show capacity percentage

**Benefits**:

- Prevents users from hitting limits unexpectedly
- Helps plan multi-gateway installations
- Provides visibility into system capacity

**Code Locations**:

- `nodes/Controller.py` - Add capacity tracking in discovery methods
- Add driver GV7 for RTS capacity, GV8 for Zigbee capacity, GV9 for scene capacity
- Update `profile/nodedef/nodedefs.xml` to add capacity drivers

---

## Priority: Low

### Persistent State Storage for Shades and Scenes

**Status**: Not implemented
**Date Added**: 2025-11-11
**Source**: User request for improved state persistence

**Description**:
Store shade and scene state data in Polyglot's Data storage using the
udi_interface library. This would preserve state across NodeServer restarts
and allow faster startup without querying TaHoma.

**Current State**:

- Shade and scene states stored in memory only (Controller.devices_map,
  scenarios_map)
- State lost on NodeServer restart
- Must query TaHoma on every startup
- No historical state data

**Implementation Plan**:

1. Use existing `utils/node_funcs.py` helper functions:
   - `load_persistent_data()` - Load state on node startup
   - `store_values()` - Save state to Polyglot Data
   - `_apply_state()` - Apply values with defaults
   - `_push_drivers()` - Update ISY drivers

2. Define FieldSpec for shade state:

   ```python
   # In nodes/Shade.py
   FIELDS: dict[str, FieldSpec] = {
       # State variables (pushed to drivers)
       "primary_position": FieldSpec(driver="GV2", default=0, data_type="state"),
       "secondary_position": FieldSpec(driver="GV3", default=0, data_type="state"),
       "tilt_position": FieldSpec(driver="GV4", default=0, data_type="state"),
       "battery_status": FieldSpec(driver="GV6", default=0, data_type="state"),
       # Config data (not pushed to drivers)
       "device_url": FieldSpec(driver=None, default="", data_type="config"),
       "last_updated": FieldSpec(driver=None, default="", data_type="config"),
   }
   ```

3. Define FieldSpec for scene state:

   ```python
   # In nodes/Scene.py
   FIELDS: dict[str, FieldSpec] = {
       "active": FieldSpec(driver="ST", default=0, data_type="state"),
       "scene_oid": FieldSpec(driver=None, default="", data_type="config"),
       "last_activated": FieldSpec(driver=None, default="", data_type="config"),
   }
   ```

4. Modify node start() methods:

   ```python
   def start(self):
       self.data = {}  # Initialize data dict
       load_persistent_data(self, FIELDS)
       # Continue with existing startup...
   ```

5. Store state on updates:

   ```python
   def updatePositions(self, positions):
       # Update positions
       self.data["primary_position"] = positions.get("primary")
       # ... update other fields
       store_values(self)  # Persist to Polyglot
   ```

**Benefits**:

- Faster startup (don't wait for TaHoma queries)
- State preserved across restarts
- Last known good state available offline
- Historical state tracking possible
- Reduced TaHoma API calls

**Code Locations**:

- `nodes/Shade.py` - Add FIELDS definition and use helper functions
- `nodes/Scene.py` - Add FIELDS definition and use helper functions
- `utils/node_funcs.py` - Already has required helper functions
- `test/test_node_funcs.py` - Already has tests for helper functions

**Considerations**:

- State may become stale if TaHoma controlled externally
- Need periodic refresh from TaHoma to stay synced
- Initial startup still needs TaHoma query for discovery
- Polyglot Data size limits (unlikely to be an issue)
- Backward compatibility with existing installations

**Implementation Steps**:

1. Add FieldSpec definitions to Shade and Scene nodes
2. Initialize `self.data = {}` in `__init__` methods
3. Call `load_persistent_data()` in `start()` methods
4. Call `store_values()` after state updates
5. Test state persistence across restarts
6. Add periodic refresh from TaHoma (every 5-10 minutes)

**Testing**:

- Verify state loads correctly on startup
- Verify state persists across NodeServer restart
- Verify state updates when positions change
- Verify state doesn't interfere with TaHoma updates

---

### Multi-Gateway Discovery

**Status**: Not implemented
**Date Added**: 2025-11-11
**Source**: TaHoma Programming Guide PDF

**Description**:
Support discovery and management of multiple TaHoma interfaces (up to 10) in a single installation.

**Current State**:

- Code assumes single TaHoma gateway
- Configuration accepts one gateway PIN/token

**Implementation Ideas**:

1. Allow multiple gateway configurations
2. Add gateway selection UI
3. Track which devices belong to which gateway
4. Coordinate commands across gateways
5. Handle gateway failover

**Benefits**:

- Support whole-house installations
- Better RF coverage (25-35 foot range per gateway)
- Zone-based control

**Considerations**:

- Multi-gateway is RTS only (not Zigbee per PDF)
- Each gateway needs its own token
- Complexity of managing multiple connections

---

### Internet Dependency Testing

**Status**: Needs hardware verification
**Date Added**: 2025-11-11
**Source**: TaHoma Programming Guide conflict

**Description**:
Test and document actual internet dependency when using Developer Mode API.

**Conflict**:

- Programming Guide states: "TaHoma does not support local control to operate any RTS products without an internet connection"
- Developer Mode API documentation suggests local operation is possible
- Need to verify actual behavior

**Testing Plan** (when hardware arrives):

1. Set up TaHoma with Developer Mode
2. Test commands with internet connected (baseline)
3. Disconnect internet (block gateway from cloud)
4. Test if local API commands still work
5. Document actual behavior

**Documentation Updates**:

- Update HARDWARE_REFERENCE.md with findings
- Update HARDWARE_TESTING_GUIDE.md with test results
- Add notes to README.md about internet requirements

---

## Priority: Very Low

### Scene Scheduling

**Status**: Not implemented
**Date Added**: 2025-11-11
**Source**: TaHoma supports scene schedules

**Description**:
Expose TaHoma scene schedules through the ISY interface.

**Current State**:

- Can activate scenes manually
- Cannot view or manage schedules

**Implementation Ideas**:

1. Query scene schedules from TaHoma
2. Display schedule status in scene nodes
3. Allow enable/disable of schedules via ISY
4. Possibly allow schedule creation (complex)

**Benefits**:

- Visibility into TaHoma automation
- Control schedules from ISY
- Integrate TaHoma schedules with ISY programs

**Considerations**:

- Schedules are better managed in TaHoma app
- ISY programs can replace scene schedules
- May add unnecessary complexity

---

### Battery Status Details

**Status**: Basic battery status implemented
**Date Added**: 2025-11-11
**Source**: TaHoma provides battery alerts

**Description**:
Enhance battery status reporting with more detail.

**Current State**:

- Basic battery status (Low/Medium/High/Plugged In)
- Battery alert events captured

**Implementation Ideas**:

1. Add battery percentage (if available from TaHoma)
2. Add "last battery check" timestamp
3. Add battery health indicator
4. Create ISY program trigger on low battery
5. Log battery history

**Benefits**:

- Proactive battery replacement
- Better maintenance planning
- Historical battery data

**Considerations**:

- May not be available for all motor types
- RTS devices may have limited battery reporting
- Require hardware testing to verify available data

---

### Zigbee Device Support

**Status**: Not implemented (RTS focus)
**Date Added**: 2025-11-11
**Source**: TaHoma supports Zigbee 3.0

**Description**:
Add support for Zigbee devices beyond just RTS.

**Current State**:

- Code is TaHoma-focused (works with any device type)
- Testing focused on RTS Phantom Blinds
- Zigbee devices should work but untested

**Implementation Ideas**:

1. Test with Zigbee devices
2. Map Zigbee-specific commands
3. Add Zigbee device type recognition
4. Document Zigbee capabilities

**Benefits**:

- Support full TaHoma capability
- Wider device compatibility
- Future-proofing

**Considerations**:

- Primary use case is RTS Phantom Blinds
- Zigbee adds complexity
- May require additional hardware for testing

---

## Completed Enhancements

### ✅ MY Preset Command
**Completed**: 2025-11-11
**Description**: Added RTS "MY" preset position command to all shade nodes.
**Files**: nodes/Shade.py, profile/nodedef/nodedefs.xml, profile/nls/en_us.txt

### ✅ Pre-Hardware Preparation (Tasks 1-5)
**Completed**: 2025-11-11
**Description**: Created installation guide, configuration validation, error messages, and documentation.
**Files**: INSTALLATION.md, utils/config_validation.py, exampleConfigFile.yaml, README.md
**Details**: See PRE_HARDWARE_COMPLETE.md

---

## How to Use This Document

1. Review before major development cycles
2. Prioritize based on user feedback
3. Update status as items are implemented
4. Archive completed items at bottom
5. Add new ideas as they arise

## Contributing Ideas

When adding enhancement ideas:

1. Add date and source
2. Clearly describe the feature
3. List benefits and considerations
4. Suggest implementation approach
5. Assign realistic priority

---

**Last Updated**: 2025-11-11
**Document Purpose**: Track optional features and future improvements
