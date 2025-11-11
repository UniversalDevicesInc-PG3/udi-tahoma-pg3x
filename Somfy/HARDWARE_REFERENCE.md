# TaHoma Hardware Reference

<!-- markdownlint-disable MD022 MD013 -->

This document provides hardware specifications and physical installation requirements for the Somfy TaHoma RTS/Zigbee interface, extracted from the official product documentation.

## Product Information

**Full Name**: TaHoma® RTS/Zigbee Smartphone and Tablet Interface
**Item Number**: 1811731
**Manufacturer**: Somfy Systems, Inc.
**Documentation Date**: July 2021 (Brochure), August 2021 (Programming Guide)

## Overview

The TaHoma interface is a WiFi-to-RTS and WiFi-to-Zigbee bridge that enables control of motorized window coverings and other devices through:

- Mobile apps (iOS/Android)
- Third-party control systems
- Voice assistants (Alexa, Google)
- Developer API (local and cloud)

## Technical Specifications

### Radio Protocols

| Protocol | Frequency | Use Case |
|----------|-----------|----------|
| **RTS** | 433 MHz | Somfy motorized shades, blinds, screens |
| **Zigbee 3.0** | 2.4 GHz | Zigbee-compatible devices |
| **WiFi** | 2.4 GHz only | Network connectivity |

⚠️ **Note**: TaHoma only supports 2.4 GHz WiFi networks, not 5 GHz.

### Capacity Limits

- **RTS Channels**: Up to 40 channels per TaHoma interface
- **Zigbee Devices**: Up to 50 devices per TaHoma interface
- **Scenes**: Maximum 40 scenes with schedules per installation
- **Multi-Gateway**: Up to 10 TaHoma interfaces can be joined (RTS only) for multi-zone control

### Physical Specifications

| Specification | Value |
|---------------|-------|
| **Dimensions** | 2.76" L × 2.76" W × 6.69" H (70mm × 70mm × 170mm) |
| **Weight** | 136g (4.8 oz) |
| **Material** | ABS (PE UL94V-0 Flame Rating) |
| **Operating Temperature** | 32°F to 95°F (0°C to 35°C) |
| **IP Rating** | IP30 (indoor use only) |

### Power Requirements

| Specification | Value |
|---------------|-------|
| **Input Power** | USB 5V / 2A (via included power supply) |
| **AC Input** | 100-240V, 50/60 Hz (power supply) |
| **Rated Current** | 10 to 50 milliamps |
| **Insulation Class** | Class II |

### Connectivity

**Standard (WiFi)**:

- 2.4 GHz WiFi connection
- Micro USB port for power

**Optional (Ethernet)**:

- TaHoma Ethernet Adaptor (Item #1870470, sold separately)
- Provides wired network connection
- 10/100 Mbps transmission speed
- Preferred for integration with third-party control systems

### LED Indicators

| Color | Status |
|-------|--------|
| **Blue** | Direct WiFi mode for configuration |
| **Red** | Powered on, unable to reach Somfy server |
| **Orange** | Starting up |
| **Green** | Successfully connected to network |

## Installation Requirements

### RF Range and Placement

⚠️ **Critical**: Place TaHoma within **25-35 feet** of the RTS/Zigbee devices it controls for optimal performance.

**Single Room Control**:

- One TaHoma per room or zone
- Keep within RF range of all devices

**Whole House Control**:

- Install up to 10 TaHoma interfaces
- Each interface covers its own zone
- Interfaces can be joined for coordinated control (RTS only)
- Plan zones based on 25-35 foot RF coverage

### Network Requirements

**Internet Connection**:

- ⚠️ **Required** for initial setup and configuration
- ⚠️ According to Programming Guide: "TaHoma does not support local control to operate any RTS products without an internet connection"
- 📝 **Note**: Developer Mode API may enable local control - to be verified with hardware

**Network Options**:

1. **WiFi** (2.4 GHz only)
   - Built-in WiFi connectivity
   - No additional hardware needed

2. **Ethernet** (Preferred for integrations)
   - Requires TaHoma Ethernet Adaptor (#1870470)
   - More stable connection
   - Recommended for third-party control systems
   - Faster setup and reliability

## Certifications

- **UL Listed**
- **FCC Certified** (FCC ID: DWNBEECON)
- **Zigbee 3.0 Certified**
- **Control4 Certified**
- **5-Year Warranty** (from date of manufacture)

## What's in the Box

- TaHoma RTS/Zigbee Interface (with base stand)
- USB Power Supply (5V/2A, 100-240V)
- Quick Start Guide

## Optional Accessories

| Item | Part Number | Purpose |
|------|-------------|---------|
| **TaHoma Ethernet Adaptor** | #1870470 | Wired network connection |
| **Zigbee Smart Plug and Repeater** | #1800127 | Extend Zigbee range, add outlets |
| **Situo 1 RTS Pure** | #1870571 | RTS remote control (1 channel) |
| **Situo 5 RTS Pure** | #1870575 | RTS remote control (5 channels) |
| **Situo 1 Zigbee Pure** | #1800194 | Zigbee remote control (1 channel) |
| **Situo 4 Zigbee Pure** | #1800195 | Zigbee remote control (4 channels) |

## Supported Commands

### RTS Motorized Products

| Command | Function |
|---------|----------|
| **Open/Raise/Extend** | Move to fully open position |
| **Close/Lower/Retract** | Move to fully closed position |
| **My** | Move to preset "My" position |
| **Stop** | Stop movement |
| **+/-** | Tilt (for products with tilt capability) |

### RTS Lighting Receivers

| Command | Function |
|---------|----------|
| **On/Off** | Turn lights on or off |
| **+/-** | Dim LED lights |

### Zigbee Devices

| Command | Function |
|---------|----------|
| **Open/Close** | Control Zigbee shades |
| **+/-** | Incremental control for tilt/dimming |
| **On/Off** | Control via Zigbee Smart Plug |

## Third-Party Integration Support

TaHoma is compatible with the following third-party systems:

### Professional Control Systems

- Control4® (Certified)
- Crestron
- ELAN
- SAVANT
- URC
- RTI
- Brilliant

### Consumer Platforms

- Amazon Alexa
- Google Assistant (via Google Home)
- SmartThings
- IFTTT
- Philips Hue (bridge integration)

### Developer Integration

- **Somfy Synergy™ API** (for professional integrators)
- **Developer Mode Local API** (HTTPS REST API on port 8443)

📝 **Note**: Third-party integration must be enabled in the TaHoma app. An Integration Report is generated containing the TaHoma PIN and IP address.

## Setup Prerequisites

Before setting up the TaHoma interface:

1. ✅ **RTS Motors Programmed**: All RTS motors must be fully operational with limits set
2. ✅ **Network Access**: 2.4 GHz WiFi or Ethernet connection available
3. ✅ **Internet Connection**: Required for setup and cloud features
4. ✅ **Mobile Device**: iOS 11+ or Android 7.0+ for TaHoma North America app
5. ✅ **Account**: Somfy account creation required

## Multi-Gateway Considerations

When using multiple TaHoma interfaces:

- **Maximum**: Up to 10 interfaces can be joined
- **Limitation**: Multi-gateway joining is for **RTS devices only**
- **Zone Planning**: Each interface covers approximately 25-35 foot radius
- **Device Assignment**: When adding RTS products, scan the QR code of the TaHoma closest to that device
- **Coordination**: Interfaces can execute coordinated scenes across zones

## Important Notes

### Limitations

- ⚠️ **WiFi Only**: 2.4 GHz WiFi support only (no 5 GHz)
- ⚠️ **Indoor Use**: IP30 rating means indoor use only
- ⚠️ **RF Range**: Limited to 25-35 feet from devices
- ⚠️ **Internet Dependency**: Standard operation requires internet connection
- ⚠️ **RTS Channel Limit**: Each interface supports only 40 RTS channels
- ⚠️ **Scene Limit**: Maximum 40 scenes with schedules per installation

### Best Practices

- ✅ Use Ethernet adapter for third-party control system integrations
- ✅ Place TaHoma centrally within each zone for optimal RF coverage
- ✅ Plan multi-gateway zones based on physical layout and RF range
- ✅ Ensure all motors are programmed before pairing with TaHoma
- ✅ Test RF range before permanent mounting

## Developer Mode Considerations

The official programming guide states that internet is required for operation. However, **Developer Mode** (documented in our other guides) may enable local-only operation:

- **Local API**: HTTPS on port 8443
- **Authentication**: Bearer token (generated in app)
- **Functionality**: Full device control without cloud dependency (to be verified)

See `HARDWARE_TESTING_GUIDE.md` for Developer Mode setup instructions.

## Support Resources

- **Technical Support**: (800) 22-SOMFY (76639)
- **Email**: <technicalsupport_us@somfy.com>
- **Documentation**: <https://www.somfypro.com/tahomadocumentation>
- **Developer Mode**: <https://github.com/Somfy-Developer/Somfy-TaHoma-Developer-Mode>

## References

- Product Brochure: [TaHoma RTS/Zigbee Spec Sheet](https://asset.somfy.com/Document/d60eab71-c5d0-4ecc-a1bc-f0ea8198ecc2_Tahoma-Zigbee%20Spec%20Sheet_v4.pdf) (Item #1811731)
- Programming Guide: [TaHoma RTS Programming Guide V1.2](https://asset.somfy.com/Document/40067bc5-3c40-450b-a145-2c3c154042e9_Programming%20Guide%20-%20TaHoma%20RTS%20%5BV1.2%5D.pdf) (Version 1.2, August 2021)
- Quick Start Guide: [TaHoma Quick Start Guide](https://asset.somfy.com/Document/aa639aa0-5787-474c-a170-6cb989e32e9b_TAHOMA%20BEECON-QuickStart-140x175-2021.6-WEB.pdf)
- Somfy Systems, Inc.: <www.somfypro.com>

---

**Last Updated**: 2025-11-11
**Status**: Pre-hardware reference (specifications extracted from official documentation)
