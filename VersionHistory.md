# Version History

See `udi-tahoma-pg3x` for in-code release notes.

## 0.0.15

- **Scene Last Command (GV7)**: TaHoma local API reports spurious `FAILED` on the parent exec when activating persisted action groups; scenes still run. Scenario exec tracking ignores that parent `FAILED` state and marks **Completed** ~5s after a successful Activate (or immediately on real `COMPLETED` / `NOT_TRANSMITTED`)
- Fix execution watch timeout log referencing undefined `shade_address`

## 0.0.14

- **Fix startup error on stale scene cleanup**: custom data keys must be removed with `Custom.delete()`, not `del` — v0.0.13 crashed discovery with `KeyError` while purging orphan scenes

## 0.0.13

- **Fix orphan scene cleanup**: discovery cleanup now compares against Polyglot DB nodes, not just in-memory nodes — stale UUID-named scenes from before v0.0.12 are removed on restart
- Clears orphaned `scenario_oid_*` / `device_url_*` custom data when a node is deleted

## 0.0.12

- Skip **unnamed actionGroups** during scenario discovery — TaHoma API can return orphan/system records with no label; these no longer appear as UUID-named scene nodes
- Skipped OIDs logged at INFO for troubleshooting

## 0.0.11

- **Fix startup lockup**: scene node addresses used full UUIDs (~43 chars); Polyglot allows max 14 — addresses now use `sc` + 10 hex chars
- Scene OID stored in custom data for restart; `wait_for_node_done` times out instead of hanging forever

## 0.0.10

- **Scenario discovery** via raw `actionGroups` API (works when pyoverkiz `Scenario` model mismatches the gateway)
- **Scenario nodes**: Activate command plus **Last Command (GV7)** — same feedback model as RTS shades
- Startup success notice includes scenario count

## 0.0.9

- Startup connect retries with exponential backoff for up to 10 minutes (survives gateway wake-up delay)
- Periodic TaHoma health check while running; automatic reconnect on local API failure
- shortPoll watchdog as secondary reconnect trigger

## 0.0.8

- **TaHoma plugin** branding: controller node **TaHoma Controller** (was Phantom Blinds TaHoma Controller)
- User docs: **Applications** section (RTS / io / Zigbee / other); Phantom Blinds as RTS application
- Entry script renamed to **`udi-tahoma-pg3x`** — delete old NodeServer on EISY/Polisy and install fresh
- After upgrade: **Update Profile** in Polyglot so the Admin Console shows the new controller name

## 0.0.7

- **RTS Shade** nodedef (`shadertsid`): Id, Battery, Last Command only; Open/Close/Stop/MY commands (no position or tilt fields)
- Discovery creates RTS Shade nodes for `rts://` devices; full Shade nodes for io/Zigbee
- Startup success Polyglot notice clears after 30 seconds
- User documentation for Last Command Pending delay on RTS (TaHoma gateway internal timer)

## 0.0.6

- **GV7 Last Command** on shade nodes: — (none) until first command, then Pending / Completed / Failed from TaHoma execution status
- Execution events logged at INFO; poll fallback when events are slow or missing
- Includes v0.0.5 startup notices and gateway unreachable messaging

## 0.0.5

- Config placeholder notice survives startup (no longer cleared by `Notices.clear()`)
- Success notice after connect/discovery (shade count and gateway PIN)
- Clearer error when TaHoma gateway is unreachable (timeout/offline) vs auth failure

## 0.0.4

- Fix shade discovery when TaHoma returns `CommandDefinition` objects in device definitions (all 8 RTS shades failed on EISY with `unhashable type: 'CommandDefinition'`)
- Default `tahoma_token` Polyglot placeholder shortened from 64 to 20 zeros

## 0.0.3

- Consolidated user documentation into **README.md** and **POLYGLOT_CONFIG.md**; removed **INSTALLATION.md** and **exampleConfigFile.yaml**
- Trimmed **Somfy/** to a small developer reference set; removed obsolete archive and PowerView-era API docs
- Removed **ISY994** and **ISY Access** references from user docs
- Removed unused **use_local_api** parameter; default **verify_ssl** to `false`
- Clearer log and Polyglot notice when SSL verification fails with **verify_ssl** `true`
- Polyglot **placeholder defaults** for `gateway_pin`, `tahoma_token`, and `gateway_ip`; ignored until replaced with real values

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
