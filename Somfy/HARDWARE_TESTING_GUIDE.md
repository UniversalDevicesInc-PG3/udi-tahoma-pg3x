<!-- markdownlint-disable MD022 MD013 MD029 -->
# TaHoma Hardware Testing Guide

**Status**: Ready for testing when hardware arrives
**Prerequisites**: TaHoma gateway installed and configured

📖 **See Also**: [HARDWARE_REFERENCE.md](HARDWARE_REFERENCE.md) for hardware specifications and installation requirements.

## Quick Start Checklist

### Before You Begin

- [ ] TaHoma gateway physically installed (see [placement requirements](HARDWARE_REFERENCE.md#rf-range-and-placement))
- [ ] TaHoma app installed on mobile device
- [ ] Phantom Blinds paired with TaHoma
- [ ] Network connectivity verified (WiFi 2.4GHz or Ethernet)
- [ ] Polyglot NodeServer installed

---

## Step 1: Enable TaHoma Developer Mode

### In TaHoma App

1. Open TaHoma app
2. Go to **Settings** → **Developer Mode**
3. Enable Developer Mode
4. Note your **Gateway PIN** (format: `1234-5678-9012`)

### Generate Bearer Token

1. Still in Developer Mode
2. Click **Generate Token**
3. Copy the full token (starts with `Bearer ...`)
4. Store securely - you'll need this for configuration

**Expected Output:**

```text
Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Gateway PIN: 1234-5678-9012
```text

---

## Step 2: Configure NodeServer

### In Polyglot UI

1. Navigate to **NodeServers** → **Phantom Blinds**
2. Click **Configuration**
3. Add Custom Parameters:

   ```yaml
   tahoma_token: "Bearer <your-token-here>"
   gateway_pin: "1234-5678-9012"
   use_local_api: "true"
   verify_ssl: "true"
   ```

1. **Save Configuration**
2. **Restart NodeServer**

---

## Step 3: Initial Connection Test

### Check Logs

```bash
# Monitor NodeServer logs
tail -f ~/.polyglot/pg3/ns/<nodeserver-uuid>/logs/debug.log
```text

### Expected Log Messages

```text
INFO: TaHoma client initialized
INFO: Connecting to TaHoma gateway...
INFO: Connected to TaHoma successfully
INFO: Starting event polling...
```text

### If Connection Fails

1. Verify token is correct (copy entire Bearer token)
2. Check gateway PIN format (xxxx-xxxx-xxxx)
3. Verify network connectivity
4. Check TaHoma gateway is online
5. Try regenerating token in app

---

## Step 4: Discover Devices

### In Polyglot UI

1. Go to **Phantom Blinds Controller** node
2. Click **Discover Devices**
3. Wait 10-15 seconds

### Expected Results

- Controller node appears
- Shade nodes appear (one per device)
- Scene nodes appear (one per scenario)

### Check Logs

```text
INFO: Discovery initiated
INFO: Found 5 devices
INFO: Found 2 scenarios
INFO: Creating shade nodes...
INFO: Created shade: Living Room Blind
INFO: Created shade: Bedroom Blind
INFO: Discovery complete
```text

---

## Step 5: Test Basic Commands

### Test Shade Control

#### 1. Open Command

- **In ISY**: Select a shade node
- **Action**: Send `OPEN` command
- **Expected**: Shade opens fully
- **Log**: `INFO: Executing command 'open' on device <id>`

#### 2. Close Command

- **In ISY**: Send `CLOSE` command
- **Expected**: Shade closes fully
- **Log**: `INFO: Executing command 'close' on device <id>`

#### 3. Stop Command

- **In ISY**: Send `OPEN`, then quickly `STOP`
- **Expected**: Shade stops immediately
- **Log**: `INFO: Executing command 'stop' on device <id>`

#### 4. Position Command

- **In ISY**: Send `SETPOS` with value `50`
- **Expected**: Shade moves to 50% position
- **Log**: `INFO: Setting position to 50%`

---

## Step 6: Test State Updates

### Manual Shade Movement

1. Use TaHoma app to move a shade
2. Check ISY for state update
3. Verify position reflects actual shade position

### Expected Behavior

- State updates within 1-2 seconds
- Position accurate (within 1-2%)
- Motion status updates correctly

### Check Logs

```text
INFO: Event received: DeviceStateChangedEvent
INFO: Device <id> state changed: position=75
INFO: Updating shade node drivers
```text

---

## Step 7: Test Scenarios

### Activate Scenario

1. **In ISY**: Select a scene node
2. **Action**: Send `ACTIVATE` command
3. **Expected**: All shades in scenario move to positions

### Check Logs

```text
INFO: Activating scenario <name>
INFO: Execution ID: exec-12345
INFO: Scenario activated successfully
```text

---

## Step 8: Monitor Event System

### Check Event Polling

```bash
# Watch for events in logs
grep "Event received" debug.log

# Should see regular activity:
INFO: Polling events... (every 1 second)
INFO: Event received: DeviceStateChangedEvent
INFO: Event received: ExecutionStateChangedEvent
```text

### Verify

- [ ] Events arrive consistently
- [ ] No error messages
- [ ] Position updates accurate
- [ ] Motion status correct

---

## Common Issues & Solutions

### Issue: Connection Timeout

**Symptoms:**

```text
ERROR: Failed to connect to TaHoma gateway
ERROR: Connection timeout after 30 seconds
```text

**Solutions:**

1. Verify gateway is online (check TaHoma app)
2. Check network connectivity
3. Verify token hasn't expired
4. Try regenerating token
5. Restart TaHoma gateway

---

### Issue: Authentication Failed

**Symptoms:**

```text
ERROR: Authentication failed: 401 Unauthorized
ERROR: Invalid token or gateway PIN
```text

**Solutions:**

1. Regenerate token in TaHoma app
2. Verify full Bearer token copied (including "Bearer ")
3. Check gateway PIN format (xxxx-xxxx-xxxx)
4. Ensure Developer Mode is still enabled

---

### Issue: Devices Not Discovered

**Symptoms:**

```text
INFO: Found 0 devices
WARNING: No devices discovered
```text

**Solutions:**

1. Verify devices paired in TaHoma app
2. Check device types are supported
3. Run discovery again (can take 10-15 seconds)
4. Check logs for device type errors
5. Restart NodeServer

---

### Issue: Commands Not Executing

**Symptoms:**

```text
ERROR: Failed to execute command: <error>
ERROR: Device not responding
```text

**Solutions:**

1. Check device is online in TaHoma app
2. Verify command name is correct
3. Try command in TaHoma app first
4. Check for execution errors in logs
5. Verify event polling is active

---

### Issue: State Not Updating

**Symptoms:**

- Shade moves but ISY state doesn't change
- Position stuck at old value

**Solutions:**

1. Check event polling is running
2. Verify no event errors in logs
3. Manually query node (Query command)
4. Check device state in TaHoma app
5. Restart NodeServer to reset state

---

## Performance Expectations

### Normal Operation

- **Connection**: < 5 seconds
- **Discovery**: 5-15 seconds
- **Command execution**: 1-2 seconds
- **State updates**: 1-2 seconds (via events)
- **Event polling**: Every 1 second

### Resource Usage

- **CPU**: < 5% (idle), < 15% (during discovery)
- **Memory**: ~50-100 MB
- **Network**: Minimal (local API preferred)

---

## Troubleshooting Commands

### View Current State

```bash
# Check if NodeServer is running
ps aux | grep phantom

# View recent logs
tail -100 ~/.polyglot/pg3/ns/<uuid>/logs/debug.log

# Check for errors
grep ERROR ~/.polyglot/pg3/ns/<uuid>/logs/debug.log

# Monitor live activity
tail -f ~/.polyglot/pg3/ns/<uuid>/logs/debug.log
```text

### Restart NodeServer

1. In Polyglot UI: **Stop NodeServer**
2. Wait 5 seconds
3. **Start NodeServer**
4. Check logs for startup messages

### Reset Configuration

1. Stop NodeServer
2. Remove custom parameters
3. Re-add parameters with correct values
4. Start NodeServer
5. Run discovery

---

## Validation Checklist

### ✅ Basic Functionality

- [ ] Connection successful
- [ ] Devices discovered
- [ ] Commands execute
- [ ] States update
- [ ] Scenarios activate

### ✅ Shade Commands

- [ ] OPEN works
- [ ] CLOSE works
- [ ] STOP works
- [ ] SETPOS works (various positions)
- [ ] TILTOPEN works (if supported)
- [ ] TILTCLOSE works (if supported)

### ✅ State Updates

- [ ] Position updates via events
- [ ] Motion status changes
- [ ] Battery status (if supported)
- [ ] Signal strength updates

### ✅ Event System

- [ ] Events poll regularly
- [ ] No polling errors
- [ ] State changes reflected
- [ ] Execution tracking works

### ✅ Scenarios

- [ ] Scenarios discovered
- [ ] ACTIVATE command works
- [ ] All devices respond
- [ ] Positions correct

### ✅ Stability

- [ ] Runs for 24+ hours
- [ ] No memory leaks
- [ ] No connection drops
- [ ] No error accumulation

---

## Next Steps After Validation

### If Everything Works ✅

1. Document any command adjustments needed
2. Note any device type additions
3. Test edge cases (network issues, etc.)
4. Begin normal usage

### If Issues Found ⚠️

1. Document specific failures
2. Collect full log output
3. Note error messages
4. Test individual components
5. Report issues with context

---

## Getting Help

### Log Files to Provide

```bash
# Full debug log
~/.polyglot/pg3/ns/<uuid>/logs/debug.log

# Configuration
~/.polyglot/pg3/ns/<uuid>/configuration
```text

### Information to Include

- TaHoma gateway model
- Blind/device types
- Error messages
- Steps to reproduce
- Expected vs actual behavior

### Resources

- **pyoverkiz**: <https://github.com/iMicknl/python-overkiz-api>
- **UDI Forums**: <https://forum.universal-devices.com>
- **Project Docs**: `/Somfy/` directory

---

## Success Metrics

### You'll know it's working when

1. ✅ All devices appear in ISY
2. ✅ Commands execute within 2 seconds
3. ✅ States update automatically
4. ✅ Scenarios work correctly
5. ✅ No errors in logs
6. ✅ Stable for 24+ hours

---

**Good luck with testing!** 🎉

The code is solid and ready. Any issues are likely configuration or network related and easily resolved. Comprehensive logging will help identify any problems quickly.
