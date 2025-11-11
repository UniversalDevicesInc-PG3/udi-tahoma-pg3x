<!-- markdownlint-disable MD022 MD013 -->
# Phantom Blinds Nodeserver for PG3x

## Overview

This nodeserver integrates Phantom Blinds motorized shades with the Universal Devices ISY/Polisy/EISY home automation systems through the Somfy TaHoma gateway. It provides comprehensive control and monitoring of Phantom motorized shades using the Somfy TaHoma Developer Mode Local API.

## Quick Start

1. **Prerequisites**: TaHoma gateway with Developer Mode enabled (see [INSTALLATION.md](INSTALLATION.md))
2. **Install**: Install NodeServer from Polyglot Store
3. **Configure**: Enter Gateway PIN and Bearer Token in Polyglot UI
4. **Discover**: Run Discover command to find all shades
5. **Control**: Use ISY programs to control your shades

📖 **Full Installation Guide**: [INSTALLATION.md](INSTALLATION.md)

## Features

- **Local API Control**: Direct connection to TaHoma on your network (no cloud required)
- **Automatic Discovery**: Discovers all RTS and Zigbee devices from TaHoma
- **Real-time Status**: Event-driven updates for shade position and status
- **Full Control**: Open, Close, Stop, My Position, Tilt control
- **Scene Support**: Execute TaHoma scenes from ISY
- **Robust Error Handling**: Automatic reconnection and error recovery

## Requirements

- Universal Devices ISY994i, Polisy, or EISY with Polyglot V3 (PG3x)
- Somfy TaHoma RTS/Zigbee gateway (Item #1811731)
- Phantom Blinds motorized shades with RTS motors
- TaHoma Developer Mode enabled with Bearer Token
- Network connectivity (2.4 GHz WiFi or Ethernet to TaHoma)

## Supported Devices

- **RTS Motorized Shades**: Roller shades, venetian blinds, awnings, screens
- **RTS with Tilt**: Blinds with slat tilt control
- **Dual Shades**: Top-down/bottom-up configurations
- **TaHoma Scenes**: Multi-shade coordinated actions
- **Zigbee Devices**: Zigbee 3.0 compatible devices (untested)

## Installation

**See**: [INSTALLATION.md](INSTALLATION.md) for complete installation instructions.

### Quick Installation

1. **Install NodeServer** in Polyglot UI from NodeServer Store
2. **Configure Settings**:
   - Gateway PIN: `1234-5678-9012` (from TaHoma device)
   - Bearer Token: Generate in TaHoma app Developer Mode
   - Use Local API: `true` (recommended)
3. **Start NodeServer** and verify connection in logs
4. **Discover Devices**: Right-click Controller → Discover

### Configuration Parameters

| Parameter | Required | Example | Description |
|-----------|----------|---------|-------------|
| Gateway PIN | Yes | `1234-5678-9012` | TaHoma gateway identifier |
| Bearer Token | Yes | `abc123...` | Authentication token from app |
| Use Local API | No | `true` | Local vs cloud (default: true) |
| Verify SSL | No | `false` | Certificate verification (default: false) |

📖 **Troubleshooting**: See [INSTALLATION.md](INSTALLATION.md#troubleshooting)

## Usage

### Shade Control

Each shade node provides the following controls:

- **Position**: Set shade position (0-100%)
- **Open/Close**: Fully open or close the shade
- **Stop**: Stop shade movement
- **My Position**: Move to programmed favorite position
- **Tilt** (if supported): Adjust slat angle

### Scenes

Create scenes to control multiple shades:

- Group shades by room or function
- Set coordinated positions for multiple shades
- Trigger scenes from ISY programs or schedules

### Status Monitoring

Monitor shade status in real-time:

- Current position
- Movement state (opening, closing, stopped)
- Battery level (for battery-powered shades)
- Connection status
- Last update timestamp

## Configuration

See [POLYGLOT_CONFIG.md][config] for detailed configuration options including:

- OAuth authentication setup
- API credentials configuration
- Polling intervals
- Logging levels
- Advanced settings

## Architecture

This nodeserver uses:

- **pyoverkiz**: Official Somfy/Overkiz Python library for TaHoma API
- **OAuth 2.0**: Secure authentication with token refresh
- **SSE**: Server-Sent Events for real-time status updates
- **udi_interface**: PG3x interface library for ISY integration

See [Somfy Documentation](Somfy/) for detailed API information and migration notes.

## Troubleshooting

### Authentication Issues

- Verify your Developer API credentials are correct
- Check that OAuth token hasn't expired (auto-refreshes every 30 days)
- Ensure your TaHoma account is active

### Discovery Issues

- Confirm shades are properly paired with TaHoma gateway
- Check network connectivity to TaHoma cloud
- Review nodeserver logs for error messages

### Control Issues

- Verify shade is online in TaHoma app
- Check for conflicting commands or schedules
- Ensure shade batteries are charged (if applicable)

### Logging

- Enable debug logging in Polyglot configuration
- Check `logs/debug.log` for detailed diagnostic information
- Look for connection errors or API rate limiting

## Version History

See [VersionHistory.md][versions] for release notes and update history.

## Support

- **Issues**: Report bugs on GitHub Issues
- **Documentation**: See Somfy folder for API documentation
- **Forum**: Universal Devices Forum

## License

See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Universal Devices for the ISY platform and PG3x framework
- Somfy for TaHoma API and pyoverkiz library
- Hunter Douglas PowerView plugin for implementation inspiration

## Related Links

- [Somfy Developer Portal](https://developer.somfy.com)
- [TaHoma Documentation](https://github.com/iMicknl/python-overkiz-api)
- [Universal Devices](https://www.universal-devices.com)
- [PG3x Documentation](https://github.com/UniversalDevicesInc/udi_python_interface)

[versions]: VersionHistory.md
[config]: POLYGLOT_CONFIG.md
