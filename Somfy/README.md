# Somfy API Documentation for Phantom Blinds

<!-- markdownlint-disable MD022 MD013 -->

This folder contains information about the Somfy API used by Phantom Blinds.

## Overview

Phantom Blinds use Somfy-based controls with the **TaHoma** gateway system. The integration uses a local REST API with event-based notifications for real-time updates.

## Official Resources

- **Official Somfy TaHoma Developer Mode**: <https://github.com/Somfy-Developer/Somfy-TaHoma-Developer-Mode>
- **API Documentation**: <https://somfy-developer.github.io/Somfy-TaHoma-Developer-Mode>
- **OpenAPI Spec**: Available in the official repository

## API Structure

### Base Concepts

- **Gateway**: TaHoma hub that manages io-homecontrol devices
- **Devices**: Individual motorized products (shades, blinds, screens)
- **Setup**: Complete configuration including all devices
- **Events**: Real-time event notifications via registered listeners
- **Executions**: Action commands sent to devices

### Key Components

1. **REST API**: HTTPS-based local API (port 8443)
2. **Event Listeners**: Register listeners and poll for events
3. **Commands**: Execute actions on devices (move, stop, etc.)
4. **States**: Device state monitoring (position, battery, etc.)

## Authentication

The TaHoma local API requires **Bearer token** authentication:

1. Enable Developer Mode in TaHoma app (tap version 7 times)
2. Generate token from Developer Mode menu
3. Use `Authorization: Bearer <token>` header

## Documentation Files

- `README.md` - This overview document
- `HARDWARE_REFERENCE.md` - Hardware specifications and installation requirements
- `FUTURE_ENHANCEMENTS.md` - Optional features and future improvements
- `API_ENDPOINTS.md` - Complete TaHoma API endpoint reference
- `EVENTS.md` - Event listener system and event types
- `DATA_STRUCTURES.md` - JSON schemas from OpenAPI spec
- `CONTROL_COMMANDS.md` - Device control examples
- `EXAMPLES.md` - Complete workflow examples
- `MOTOR_INFO.md` - Somfy motor types and protocols
- `QUICK_REFERENCE.md` - Quick reference guide
- `HARDWARE_TESTING_GUIDE.md` - Hardware testing procedures
- `TABLE_OF_CONTENTS.md` - Complete documentation index

## Important Notes

⚠️ **Security**: TaHoma uses self-signed certificates. Add CA cert from <https://ca.overkiz.com/overkiz-root-ca-2048.crt>

⚠️ **Port**: Default HTTPS port is 8443

⚠️ **Event Polling**: Events must be polled (no SSE), listeners expire after 10 minutes of inactivity
