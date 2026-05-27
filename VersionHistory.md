# Version History

See `udi-PhantomBlinds-pg3x` for in-code release notes.

## 0.0.2

- Generic full-UI shade nodes for all discovered blinds; behavior tightens from gateway data and user logs
- Added `utils/device_capabilities.py` (`DeviceProfile`) built at discovery from protocol, commands, and states
- Discovery logs one INFO line per shade (controllable, commands, states, position feedback, battery) for field diagnostics
- RTS shades (e.g. `rts:ExteriorBlindRTSComponent`): protocol and hardwired battery display correctly; position fields show N/A instead of blank when there is no feedback; SETPOS logs a warning when the gateway reports no position commands (Open/Close/Stop/MY unchanged)
- Do not create shade nodes for TaHoma infrastructure (internal Pod/WiFi, Zigbee transceiver)
- Profile: `BATTERYST` editor includes 255; `SHADECAP` / GV5 renamed to Protocol (0–4)
- Shade `updateData` and state sync fixes; position/battery drivers updated from `device.states` and SSE events
- Discovery cleanup excludes controller node addresses (`controller`, `hdctrl`)
- Scene: initialize active-scene tracking on controller; avoid call to removed `updateAllFromServer`

**After upgrade:** Update Profile, then Discover.

## 0.0.1

- Initial repository and TaHoma PG3 NodeServer setup

## 0.0.0

- START new repo
