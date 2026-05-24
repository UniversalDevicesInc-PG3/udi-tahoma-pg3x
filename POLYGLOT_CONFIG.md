# Phantom Blinds Device Controller (TaHoma Integration)
<!-- markdownlint-disable-file MD036 MD007 MD022 MD013 -->

**NEED TO SELECT ISY ACCESS AND SAVE IN CONFIGURATION**
Required for variable write access

**After updating you MAY need to restart your Admin Console**

## Initial Setup

### Step 1: Prerequisites

Before configuring this NodeServer, ensure you have:

1. ✅ Somfy TaHoma RTS/Zigbee gateway (Item #1811731) installed and connected to network
2. ✅ Your Phantom Blinds configured in the TaHoma mobile app
3. ✅ TaHoma Developer Mode enabled (see [INSTALLATION.md](INSTALLATION.md) for detailed steps)
4. ✅ Bearer token generated in TaHoma app (save securely - only shown once)
5. ✅ Gateway PIN (found on bottom of TaHoma device or in app)

### Step 2: Required Configuration Parameters

The following configuration parameters are **REQUIRED** to connect to your TaHoma gateway:

#### **gateway_pin** (Required)

Your TaHoma gateway PIN in format: `XXXX-XXXX-XXXX` (e.g., `2001-0001-1891`)

- **Format**: 4 digits, dash, 4 digits, dash, 4 digits (12 total digits with dashes)
- **Where to find**:
  - On a label on the bottom of your TaHoma device
  - In TaHoma app: Menu → Help & Advanced Features → My Setup → TaHoma PIN
- **Example**: `2001-0001-1891`

#### **bearer_token** (Required)

Authentication token from TaHoma app Developer Mode.

- **How to generate**:
  1. Open TaHoma app on mobile device
  2. Tap Menu (bottom right) → Help & Advanced Features → Advanced Features
  3. Tap on version number 7 times to enable Developer Mode
  4. Go back to Menu → Developer Mode
  5. Tap "Generate Token"
  6. Copy token immediately (only shown once!)
- **Format**: Long alphanumeric string (typically 50+ characters)
- **Security**: Token is stored securely and never transmitted to cloud

### Step 3: Optional Configuration Parameters

#### **gateway_ip** (Optional)

IP address of TaHoma gateway on your network (for cases where DNS/mDNS doesn't work)

- **Example**: `192.168.1.100`
- **When to use**: If automatic hostname resolution (`gateway-XXXX-XXXX-XXXX.local`) fails
- **Default**: Uses hostname when not specified

#### **use_local_api** (Optional)

Use local API (direct connection) vs cloud API

- **Default**: `true` (recommended)
- **Recommended**: `true` for better performance and privacy
- **Note**: Local API requires TaHoma to be on same network

#### **verify_ssl** (Optional)

Whether to verify SSL certificates

- **Default**: `false` (TaHoma uses self-signed certificate)
- **Recommended**: `false` for local network
- **Note**: Can install Somfy root CA for strict verification if desired

### Step 4: Save Configuration

1. Enter your Gateway PIN in the format `XXXX-XXXX-XXXX`
2. Enter your Bearer Token (generated from TaHoma app)
3. Optionally enter Gateway IP if needed
4. Click **Save**
5. The NodeServer will automatically:
   - Validate your configuration
   - Connect to your TaHoma gateway
   - Discover your Phantom Blinds devices
   - Create nodes for each device in the ISY

### Step 5: Verify Connection

After saving the configuration:

1. Check the NodeServer logs for connection success
2. Wait 30-60 seconds for device discovery
3. Verify your shades appear in the ISY Admin Console
4. Test basic commands (Open, Close, Stop)

## Supported Device Types

### Phantom Blinds and RTS Devices

- **Open/Close**: Full range motion control
- **Position**: Set to specific percentage (0-100%)
- **Stop**: Halt motion at current position
- **Tilt** (if supported): Adjust slat angle for blinds
- **Status Monitoring**: Position, connectivity
- **Scenes**: Execute TaHoma scenes from ISY

## Troubleshooting

### Configuration Errors

**Invalid Gateway PIN format**

- PIN must be in format: `XXXX-XXXX-XXXX` (12 digits with dashes)
- Example: `2001-0001-1891`
- Found on bottom of TaHoma device or in app

**Bearer Token not valid**

- Token appears to be placeholder text - replace with actual token from TaHoma app
- Token must be 50+ characters
- Generate new token if needed - old tokens may have expired
- Only shown once when created, save securely

### Connection Issues

**Cannot connect to TaHoma gateway**

- Verify TaHoma is connected to your network (check LED is green)
- If using hostname resolution fails, try entering Gateway IP address manually
- Check that your firewall allows port 8443 (HTTPS) to TaHoma
- Try pinging: `gateway-XXXX-XXXX-XXXX.local` or your Gateway IP
- Restart TaHoma device

**No Devices Discovered**

- Verify devices are properly configured in TaHoma app
- Check that devices are online in TaHoma app
- Try initiating discovery again: Right-click Controller → Discover
- Review NodeServer logs for specific error messages

**Devices Don't Respond to Commands**

- Test commands in TaHoma app first to verify devices work
- Check device batteries if battery-powered
- Verify TaHoma RF range (RTS requires 25-35 feet line of sight)
- Check NodeServer logs for command execution errors

### Network Troubleshooting

**Use Gateway IP instead of hostname**

If automatic hostname resolution doesn't work:

1. Find your TaHoma IP address (check router or TaHoma app)
2. Enter IP address in `gateway_ip` configuration parameter (optional)
3. Save configuration and restart NodeServer

**SSL Certificate Errors**

- Set `verify_ssl` to `false` (safe for local network)
- Alternatively, install Somfy root CA certificate

## Support

For issues, feature requests, or questions:

- GitHub Issues: [udi-phantomblinds-pg3x](https://github.com/sejgit/udi-phantomblinds-pg3x/issues)
- UDI Forum: [Phantom Blinds NodeServer Discussion](https://forum.universal-devices.com)
- See [INSTALLATION.md](INSTALLATION.md) for detailed setup guide

## References

- [Complete Installation Guide](INSTALLATION.md)
- [README](README.md)
- [TaHoma Developer Mode Setup](INSTALLATION.md#step-2-configure-nodeserver)
