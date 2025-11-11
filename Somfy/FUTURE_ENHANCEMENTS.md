# Future Enhancements

<!-- markdownlint-disable MD022 MD013 -->

This document tracks potential improvements and optional features for the Phantom Blinds TaHoma NodeServer.

## Priority: Medium

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
