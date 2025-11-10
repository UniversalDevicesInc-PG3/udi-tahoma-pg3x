# Phantom Blinds Device Controller (TaHoma Integration)
<!-- markdownlint-disable-file MD036 MD007 MD022 MD013 -->
See [README for manual][readme]

**NEED TO SELECT ISY ACCESS AND SAVE IN CONFIGURATION**
Required for variable write access

**After updating you MAY need to restart your Admin Console**

## Initial Setup

### Step 1: Somfy/TaHoma Account

Before configuring this NodeServer, ensure you have:

1. A Somfy TaHoma box installed and connected to your network
2. Your Phantom Blinds configured in the Somfy/TaHoma app
3. Your Somfy account credentials (email and password)

### Step 2: Configuration Parameters
The following configuration parameters are **REQUIRED**:

#### **username** (Required)

Your Somfy account email address.

- Example: `user@example.com`

#### **password** (Required)

Your Somfy account password.

- Note: Password is stored securely and used only for authentication with Somfy servers

#### **server** (Optional)

Somfy server region. Default is `somfy_europe`.

- Options:
  - `somfy_europe` - European servers (default)
  - `somfy_australia` - Australian servers
  - `somfy_north_america` - North American servers
  - `hi_kuwait` - Kuwait servers
  - `rexel_france` - Rexel France servers

#### **polling_interval** (Optional)

How often (in seconds) to poll for device state updates.

- Default: `300` (5 minutes)
- Range: `60` to `3600` seconds (1 minute to 1 hour)
- Note: More frequent polling provides faster updates but increases API usage

#### **short_poll** (Optional)

Short polling interval in seconds.

- Default: `60`
- Range: `10` to `300` seconds

#### **long_poll** (Optional)

Long polling interval in seconds.

- Default: `300`
- Range: `60` to `3600` seconds

### Step 3: Save Configuration

1. Enter your credentials in the Configuration page
2. Click **Save**
3. The NodeServer will automatically:
   - Connect to your TaHoma box
   - Discover your Phantom Blinds devices
   - Create nodes for each device in the ISY

### Step 4: Verify Connection

After saving the configuration:

1. Check the NodeServer logs for connection success
2. Wait 30-60 seconds for device discovery
3. Verify your blinds appear in the ISY Admin Console
4. Test basic commands (Open, Close, Stop)

## Supported Device Types

### Phantom Blinds

- **Open/Close**: Full range motion control
- **Position**: Set to specific percentage (0-100%)
- **Stop**: Halt motion at current position
- **Orientation**: Adjust slat angle (if supported)
- **Status Monitoring**: Battery level, position, connectivity

## Troubleshooting

### No Devices Discovered

- Verify your TaHoma box is online and accessible
- Check that devices are properly configured in the Somfy/TaHoma app
- Ensure correct server region is selected
- Review NodeServer logs for authentication errors

### Authentication Failures

- Verify username and password are correct
- Check that your Somfy account is active
- Ensure you're using the correct server region
- Try logging into the Somfy/TaHoma app to verify credentials

### Commands Not Working

- Check device battery levels
- Verify TaHoma box connectivity
- Ensure devices respond in the Somfy/TaHoma app
- Review execution logs in the NodeServer

### State Updates Delayed

- Adjust `polling_interval` to a lower value (minimum 60 seconds)
- Note: The TaHoma system may have inherent delays in status reporting
- Event subscriptions should provide near real-time updates for most changes

## Advanced Configuration

### Multiple TaHoma Boxes

This NodeServer supports one TaHoma account. If you have multiple locations:

- Use separate NodeServer instances for each account
- Or ensure all devices are registered to the same Somfy account

### API Rate Limiting

Somfy may implement rate limiting on API requests:

- Avoid setting `polling_interval` below 60 seconds
- The NodeServer uses efficient batching to minimize API calls
- Event subscriptions reduce the need for frequent polling

## Support

For issues, feature requests, or questions:

- GitHub Issues: [udi-phantomblinds-pg3x](https://github.com/sejgit/udi-phantomblinds-pg3x/issues)
- UDI Forum: [Phantom Blinds NodeServer Discussion](https://forum.universal-devices.com)

## References

- [Somfy TaHoma Documentation][somfy-docs]
- [PyOverkiz Library][pyoverkiz]
- [README][readme]

[readme]: https://github.com/sejgit/udi-phantomblinds-pg3x/blob/main/README.md
[somfy-docs]: https://www.somfy.com/support
[pyoverkiz]: https://github.com/iMicknl/python-overkiz-api
