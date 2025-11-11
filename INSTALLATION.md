# Installation Guide - Phantom Blinds TaHoma NodeServer

<!-- markdownlint-disable MD022 MD013 -->

This guide walks through installing and configuring the Phantom Blinds TaHoma NodeServer for Universal Devices ISY/Polisy/EISY systems.

## Prerequisites

### Hardware Requirements

- Universal Devices EISY, Polisy, or ISY994 with Polisy
- Somfy TaHoma RTS/Zigbee interface (Item #1811731)
- Phantom Blinds with RTS motors (or other Somfy RTS devices)
- Network connectivity (2.4 GHz WiFi or Ethernet)

### Software Requirements

- Polyglot v3 installed and running
- Python 3.9 or higher
- Network access to TaHoma gateway

### TaHoma Setup Requirements

Before installing the NodeServer, ensure:

1. ✅ TaHoma gateway is physically installed and powered
2. ✅ TaHoma is connected to your network (WiFi or Ethernet)
3. ✅ TaHoma mobile app is installed (iOS 11+ or Android 7.0+)
4. ✅ All Phantom Blinds are paired with TaHoma
5. ✅ You have enabled Developer Mode in TaHoma app
6. ✅ You have generated a Bearer token

**See**: [HARDWARE_TESTING_GUIDE.md](Somfy/HARDWARE_TESTING_GUIDE.md) for TaHoma setup details.

---

## Installation Steps

### Step 1: Install NodeServer in Polyglot

#### Option A: Install from Polyglot Store (Recommended)

1. Open Polyglot UI (<http://your-polisy-ip:3000>)
2. Go to **NodeServer Store**
3. Search for **"Phantom Blinds"**
4. Click **Install**
5. Wait for installation to complete

#### Option B: Install from GitHub

1. Open Polyglot UI
2. Go to **NodeServer Store**
3. Click **Install from GitHub**
4. Enter repository URL: `https://github.com/yourusername/udi-phantomblinds-pg3x`
5. Select branch: `main`
6. Click **Install**

### Step 2: Configure NodeServer

Once installed, configure the TaHoma connection:

1. In Polyglot UI, click on **Phantom Blinds NodeServer**
2. Go to **Configuration** tab
3. Enter the following parameters:

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Gateway PIN** | `1234-5678-9012` | Found on bottom of TaHoma or in app |
| **Bearer Token** | `abc123...` | Generated in Developer Mode |
| **Use Local API** | `true` | Recommended for better performance |
| **Verify SSL** | `false` | TaHoma uses self-signed certificate |

#### Finding Your Gateway PIN

The Gateway PIN is in format `1234-5678-9012` and can be found:

- On a label on the bottom of TaHoma device
- In TaHoma app: Menu → My Setup → TaHoma PIN

#### Generating Bearer Token

1. Open TaHoma app on mobile device
2. Tap **Menu** (bottom right)
3. Tap **Help & Advanced Features** → **Advanced Features**
4. Tap on the version number **7 times** (e.g., "2025.1.4-11")
5. Developer Mode is now enabled
6. Go to Menu → **Developer Mode**
7. Tap **Generate Token**
8. Copy the token immediately (it's only shown once!)
9. Save token securely for future reference

⚠️ **Important**: The token is only visible when first created. If you lose it, generate a new one.

### Step 3: Start NodeServer

1. Click **Start** button in Polyglot UI
2. Wait 10-15 seconds for NodeServer to initialize
3. Check **Log** tab for any errors
4. Status should show **Connected**

Expected log messages:

```text
INFO: Phantom Blinds TaHoma Controller started
INFO: Connecting to TaHoma gateway at gateway-1234-5678-9012.local
INFO: Successfully authenticated with TaHoma
INFO: Event listener registered
```

### Step 4: Discover Devices

1. In ISY Admin Console, expand **NodeServer** folder
2. Find **Phantom Blinds Controller** node
3. Right-click → **Discover**
4. Wait 30-60 seconds for discovery to complete
5. New shade and scene nodes will appear

Expected results:

- One controller node
- One node per shade
- One node per TaHoma scene
- Nodes organized by room (if configured)

---

## Verification

### Check NodeServer Status

In Polyglot UI:

- ✅ Status: **Connected**
- ✅ Log shows: "Event listener registered"
- ✅ No error messages

In ISY Admin Console:

- ✅ Controller node shows **ST: 1** (Connected)
- ✅ Shade nodes appear with names
- ✅ Shade positions show current state

### Test Basic Commands

1. Select a shade node in ISY Admin Console
2. Click **Open** command
3. Verify shade opens
4. Click **Close** command
5. Verify shade closes
6. Click **Query** command
7. Verify position updates

If commands don't work, see [Troubleshooting](#troubleshooting) below.

---

## Configuration Reference

### Required Parameters

| Parameter | Description | Example | Where to Find |
|-----------|-------------|---------|---------------|
| `gateway_pin` | TaHoma gateway PIN | `1234-5678-9012` | Bottom of device or app |
| `token` | Bearer authentication token | `abc123def456...` | Generate in Developer Mode |

### Optional Parameters

| Parameter | Description | Default | Notes |
|-----------|-------------|---------|-------|
| `use_local_api` | Use local vs cloud API | `true` | Local recommended |
| `verify_ssl` | Verify SSL certificate | `false` | TaHoma uses self-signed cert |
| `poll_interval` | Event poll interval (sec) | `1.0` | Max 1 second per TaHoma |
| `include_room` | Include room in node names | `true` | e.g., "Living Room - Shade" |

### Network Configuration

The NodeServer automatically discovers your TaHoma gateway on the local network using:

- **mDNS discovery** for `_kizboxdev._tcp` service
- **Hostname**: `gateway-{pin}.local` (e.g., `gateway-1234-5678-9012.local`)
- **Port**: 8443 (HTTPS)
- **Protocol**: REST API

---

## Troubleshooting

### NodeServer Won't Start

**Symptom**: NodeServer shows "Stopped" or "Error" status

**Solutions**:

1. Check Polyglot logs for specific error
2. Verify Python 3.9+ is installed: `python3 --version`
3. Check dependencies installed: `pip3 list | grep pyoverkiz`
4. Restart Polyglot: `sudo systemctl restart polyglot`

### Cannot Connect to TaHoma

**Symptom**: Log shows "Connection failed" or "Authentication failed"

**Solutions**:

1. **Check Network Connectivity**

   ```bash
   ping gateway-1234-5678-9012.local
   ```

   - If fails: TaHoma not reachable on network
   - Check TaHoma WiFi/Ethernet connection
   - Verify TaHoma LED is green (connected)

2. **Check Developer Mode**
   - Open TaHoma app
   - Go to Menu → Developer Mode
   - Verify Developer Mode is enabled
   - Verify token is valid (generate new one if needed)

3. **Check Gateway PIN**
   - Verify PIN format: `1234-5678-9012` (with dashes)
   - Verify PIN matches label on TaHoma device
   - Try accessing: `https://gateway-{pin}.local:8443`

4. **Check SSL Certificate**
   - Set `verify_ssl` to `false` in configuration
   - Or install Somfy root CA: <https://ca.overkiz.com/overkiz-root-ca-2048.crt>

### No Devices Discovered

**Symptom**: Discovery completes but no shade nodes appear

**Solutions**:

1. **Check TaHoma Setup**
   - Open TaHoma app
   - Go to Menu → My Products
   - Verify shades are listed
   - Try controlling shades in app

2. **Check API Permissions**
   - Developer Mode must be enabled
   - Token must have full access
   - Try generating new token

3. **Check Logs**
   - Look for "Device discovery returned 0 devices"
   - Check for API errors
   - Enable debug logging: Set log level to DEBUG

4. **Manual Discovery**
   - Wait 2-3 minutes after startup
   - Right-click Controller → Discover
   - Check logs for discovery progress

### Shades Don't Respond to Commands

**Symptom**: Commands sent but shades don't move

**Solutions**:

1. **Test in TaHoma App**
   - Control shade in TaHoma app
   - If works in app but not ISY: API issue
   - If doesn't work in app: TaHoma/motor issue

2. **Check RF Range**
   - TaHoma must be within 25-35 feet of shades
   - RTS is 433 MHz with limited range
   - Move TaHoma closer or add additional gateway

3. **Check Motor Status**
   - Verify motor has power
   - Check battery level (if battery powered)
   - Verify motor is paired with TaHoma

4. **Check Command Execution**
   - Look in logs for "Command execution ID: abc123"
   - Query execution status in TaHoma app
   - Check for error responses

### Position Not Updating

**Symptom**: Shades move but position in ISY doesn't update

**Solutions**:

1. **Check Event Polling**
   - Log should show "Event listener registered"
   - Events should poll every ~1 second
   - Look for "Processing events" messages

2. **Manual Query**
   - Right-click shade node → Query
   - Position should update immediately
   - If works: Event polling issue
   - If doesn't work: Communication issue

3. **Restart Event Polling**
   - Restart NodeServer
   - Events re-register automatically
   - Check logs for event listener status

### SSL Certificate Errors

**Symptom**: "SSL: CERTIFICATE_VERIFY_FAILED" in logs

**Solutions**:

1. **Disable SSL Verification** (Quick fix)
   - Set `verify_ssl` to `false`
   - This is safe for local network

2. **Install Root CA** (Proper fix)

   ```bash
   curl -o /usr/local/share/ca-certificates/overkiz-root-ca.crt \
     https://ca.overkiz.com/overkiz-root-ca-2048.crt
   sudo update-ca-certificates
   ```

---

## Advanced Configuration

### Using Cloud API

To use Somfy cloud API instead of local:

1. Set `use_local_api` to `false`
2. TaHoma will connect through Somfy servers
3. Internet required for operation
4. Slightly higher latency

**Note**: Cloud API may have rate limits. Local API is recommended.

### Multiple TaHoma Gateways

The NodeServer currently supports one TaHoma gateway per instance.

For multiple gateways:

1. Install multiple NodeServer instances
2. Configure each with different gateway PIN/token
3. Each instance manages its own devices

**Note**: Multiple gateway coordination is a future enhancement.

### Custom Polling Intervals

Default event polling is 1 second (TaHoma maximum).

To adjust:

1. Modify `poll_interval` in configuration
2. Minimum: 0.5 seconds (not recommended)
3. Maximum: 5 seconds (may miss events)
4. Recommended: 1.0 seconds

---

## Uninstallation

To remove the NodeServer:

1. In Polyglot UI, click **Stop** on NodeServer
2. Click **Delete NodeServer**
3. In ISY Admin Console, delete NodeServer folder
4. (Optional) Disable Developer Mode in TaHoma app
5. (Optional) Delete generated tokens in TaHoma app

---

## Getting Help

### Documentation

- [README.md](Somfy/README.md) - Overview
- [HARDWARE_TESTING_GUIDE.md](Somfy/HARDWARE_TESTING_GUIDE.md) - Hardware setup
- [QUICK_REFERENCE.md](Somfy/QUICK_REFERENCE.md) - Command reference
- [HARDWARE_REFERENCE.md](Somfy/HARDWARE_REFERENCE.md) - Hardware specs

### Support Resources

- **Somfy Technical Support**: (800) 22-SOMFY (76639)
- **Somfy Email**: <technicalsupport_us@somfy.com>
- **TaHoma Documentation**: <https://www.somfypro.com/tahomadocumentation>
- **Developer Mode API**: <https://github.com/Somfy-Developer/Somfy-TaHoma-Developer-Mode>

### Log Collection

When reporting issues, include:

1. **Polyglot Logs**
   - Go to NodeServer → Log tab
   - Copy last 50-100 lines
   - Include startup messages

2. **Configuration** (redact tokens!)
   - Gateway PIN (format only)
   - Use local API: true/false
   - Python version

3. **Network Info**
   - Can ping TaHoma: yes/no
   - TaHoma LED color
   - Network type (WiFi/Ethernet)

---

**Last Updated**: 2025-11-11
**Version**: 1.0.0
**Status**: Pre-hardware (untested with actual TaHoma)
