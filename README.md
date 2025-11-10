<!-- markdownlint-disable MD022 MD013 -->
# Phantom Blinds Nodeserver for PG3x

## Overview

This nodeserver integrates Phantom Blinds motorized shades with the Universal Devices ISY/Polisy/EISY home automation systems through the Somfy TaHoma gateway. It provides comprehensive control and monitoring of Phantom motorized shades using the Somfy TaHoma API.

## Features

- **Automatic Discovery**: Automatically discovers all Somfy-compatible shades connected to your TaHoma gateway
- **Real-time Status**: Monitors shade position, battery level, and operational status through Server-Sent Events (SSE)
- **Full Control**: Control shade position, tilt, and presets through ISY programs and scenes
- **Scene Support**: Create and manage shade scenes for controlling multiple shades simultaneously
- **Robust Error Handling**: Automatic reconnection and error recovery for reliable operation
- **Secure Authentication**: OAuth 2.0 authentication for secure API access

## Requirements

- Universal Devices ISY994i, Polisy, or EISY with Polyglot V3 (PG3x)
- Somfy TaHoma gateway/hub
- Phantom Blinds motorized shades with Somfy motors
- Somfy TaHoma account with Developer API access
- Internet connection for cloud API access

## Supported Shade Types

- Roller shades
- Venetian blinds (with tilt control)
- Exterior venetian blinds
- Awnings
- Other Somfy RTS and io-homecontrol compatible devices

## Installation

1. **Install Nodeserver**
   - Navigate to PG3x (Polyglot) interface
   - Go to Nodeserver Store
   - Search for "Phantom Blinds"
   - Click Install

2. **Configure API Access**
   - Obtain Somfy Developer API credentials at <https://developer.somfy.com>
   - Enter your Client ID and Client Secret in the nodeserver configuration
   - Complete OAuth authentication flow when prompted
   - See [POLYGLOT_CONFIG.md][config] for detailed configuration instructions

3. **Discover Devices**
   - After authentication, the nodeserver will automatically discover your shades
   - Shades will appear as nodes in the ISY Admin Console
   - Configure shade names and settings as needed

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
