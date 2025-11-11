<!-- markdownlint-disable MD022 MD013 -->
# Profile Files Update Plan

**Date**: 2025-11-09
**Status**: 📋 In Progress

---

## Overview

The profile files define the interface between the NodeServer and the EISY/ISY controller.
They need to be updated to reflect the migration from Hunter Douglas PowerView to
Somfy TaHoma/Phantom Blinds.

---

## Files to Update

### 1. `/profile/nls/en_us.txt`
**Purpose**: Human-readable strings for the UI

**Changes Needed**:

- [ ] Controller name: "Hunter Douglas Controller" → "Phantom Blinds Controller"
- [ ] Update any PowerView-specific terminology
- [ ] Add TaHoma-specific strings if needed
- [ ] Keep all shade capability descriptions (still valid)
- [ ] Keep all battery status descriptions (still valid)
- [ ] Update comments/documentation

### 2. `/profile/nodedef/nodedefs.xml`
**Purpose**: Node definitions, commands, and states

**Changes Needed**:

- [ ] Update controller comments (line 3: "NODE DEF from 5.0...")
- [ ] Review all node IDs match code:
  - `hdctrl` - Controller ✓
  - `shadeid` - Full shade ✓
  - `shadenotiltid` - Shade without tilt ✓
  - `shadeonlyprimid` - Shade with only primary ✓
  - `shadeonlysecondid` - Shade with only secondary (may not be used?)
  - `shadenosecondid` - Shade without secondary (may not be used?)
  - `shadeonlytiltid` - Shade with only tilt (may not be used?)
  - `sceneid` - Scene ✓
- [ ] Verify all commands are still valid for TaHoma
- [ ] Verify all states are still valid for TaHoma
- [ ] Remove unused node types if any
- [ ] Update comments

### 3. `/profile/editor/editors.xml`
**Purpose**: UI editors for parameters

**Changes Needed**:

- [ ] Review SHADECAP values (may need TaHoma-specific updates)
- [ ] Review BATTERYST values (may need updates)
- [ ] Verify all editors are still needed
- [ ] Add any new editors if needed

---

## Current Node Types in Code

From `nodes/Controller.py` and `nodes/Shade.py`:

```python
# Controller
id = "hdctrl"  ✓ Matches profile

# Scene
id = "sceneid"  ✓ Matches profile

# Shade (full)
id = "shadeid"  ✓ Matches profile

# Shade (no tilt)
id = "shadenotiltid"  ✓ Matches profile

# Shade (only primary)
id = "shadeonlyprimid"  ✓ Matches profile
```text

### Potentially Unused Node Types

These are in the profile but not found in current code:

- `shadeonlysecondid` - Only secondary rail
- `shadenosecondid` - No secondary rail (has primary + tilt)
- `shadeonlytiltid` - Only tilt, no rails

**Action**: Need to verify if these are used in Shade.py or if they can be removed.

---

## Shade Capabilities Comparison

### PowerView Capabilities (Current Profile)

```text
0 = Bottom Up
1 = Bottom Up w/ 90° Tilt
2 = Bottom Up w/ 180° Tilt
3 = Vertical (Traversing)
4 = Vertical (Traversing) w/ 180° Tilt
5 = Tilt Only 180°
6 = Top Down
7 = Top-Down/Bottom-Up
8 = Duolite
9 = Duolite with 90° Tilt
10 = Duolite with 180° Tilt
```text

### TaHoma/Somfy Capabilities (Need to Map)

From `utils/tahoma_client.py`, supported device types:

```python
DEVICE_TYPE_MAP = {
    "io:RollerShutterGenericIOComponent": "roller_shutter",
    "io:ExteriorVenetianBlindIOComponent": "exterior_venetian",
    "io:VerticalInteriorBlindIOComponent": "vertical_interior",
    "io:WindowOpenerVeluxIOComponent": "window_opener",
    "rts:RollerShutterRTSComponent": "roller_shutter_rts",
    "io:HorizontalAwningIOComponent": "awning",
}
```text

**Action**: We may need to update the SHADECAP list to reflect TaHoma/Somfy device types,
or create a mapping between Somfy types and PowerView capabilities.

---

## Battery Status

Current profile values (seem generic enough to keep):

```text
0 = No Status
1 = Low
2 = Medium
3 = High
4 = Plugged In
```text

**Action**: Verify TaHoma reports battery status in a compatible way.

---

## Commands Verification

### Controller Commands (hdctrl)

- [x] `QUERY` - Still valid ✓
- [x] `DISCOVER` - Still valid ✓
- [x] `REMOVE_NOTICES_ALL` - Still valid ✓

### Shade Commands

- [ ] `OPEN` - Verify TaHoma command
- [ ] `CLOSE` - Verify TaHoma command
- [ ] `STOP` - Verify TaHoma command
- [ ] `TILTOPEN` - Verify TaHoma command
- [ ] `TILTCLOSE` - Verify TaHoma command
- [ ] `JOG` - Verify TaHoma command (may not be applicable)
- [ ] `SETPOS` - Verify TaHoma command
- [ ] `QUERY` - Still valid ✓

### Scene Commands

- [x] `ACTIVATE` - Still valid ✓
- [x] `QUERY` - Still valid ✓

---

## States Verification

### Controller States

- [x] `ST` - Connection status (CTD editor) ✓
- [x] `GV0` - Number of nodes ✓

### Shade States

- [ ] `ST` - Motion (BOOL) - Verify meaning for TaHoma
- [ ] `GV0` - ID
- [ ] `GV1` - RoomID - May not apply to TaHoma?
- [ ] `GV2` - Primary position
- [ ] `GV3` - Secondary position
- [ ] `GV4` - Tilt position
- [ ] `GV5` - Capabilities
- [ ] `GV6` - Battery status

### Scene States

- [x] `ST` - Activated (BOOL) ✓
- [x] `GV0` - ID ✓

---

## Action Items

### Phase 1: Analysis (Current)

1. [ ] Review Shade.py to find all used node types
2. [ ] Check TaHoma command names in Shade.py
3. [ ] Verify state usage in Shade.py
4. [ ] Determine which node types are unused

### Phase 2: Updates

1. [ ] Update controller name in en_us.txt
2. [ ] Remove unused node types from nodedefs.xml
3. [ ] Update SHADECAP if needed for TaHoma
4. [ ] Update any command names if different in TaHoma
5. [ ] Update comments and documentation

### Phase 3: Validation

1. [ ] Verify all node IDs match between code and profile
2. [ ] Verify all commands referenced in code exist in profile
3. [ ] Verify all states referenced in code exist in profile
4. [ ] Test with EISY (when hardware available)

---

## Questions to Resolve

1. **Shade Capabilities**: Should we map TaHoma device types to PowerView capabilities,
   or create new capability values?

2. **Room ID**: PowerView has rooms (GV1). Does TaHoma have an equivalent concept?

3. **JOG Command**: Is this applicable to Somfy/TaHoma blinds?

4. **Motion State (ST)**: What does this represent in TaHoma context?

5. **Unused Node Types**: Can we remove `shadeonlysecondid`, `shadenosecondid`,
   and `shadeonlytiltid` if they're not used?

---

## Next Steps

1. Analyze Shade.py to answer the questions above
2. Create updated profile files
3. Validate changes
4. Test with hardware when available
