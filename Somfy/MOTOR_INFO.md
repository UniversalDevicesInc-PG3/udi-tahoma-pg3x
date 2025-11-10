# Somfy Motor and Protocol Information

<!-- markdownlint-disable MD022 MD013 -->

This document contains information about Somfy motors and their control
protocols.

## Somfy Motor Types

### RTS (Radio Technology Somfy)

- **Frequency**: 433.42 MHz
- **Protocol**: Proprietary one-way radio
- **Range**: Approximately 20 meters indoors
- **Features**:
  - Simple point-to-point control
  - No feedback from motors
  - Remote pairing required

### io-homecontrol®

- **Frequency**: 868.3 MHz (Europe) / 916 MHz (US)
- **Protocol**: Two-way encrypted communication
- **Range**: Better than RTS
- **Features**:
  - Bidirectional communication
  - Position feedback
  - Security encryption
  - Multiple motors can be synchronized
  - Battery-powered sensors support

### Comparison

| Feature | RTS | io-homecontrol |
|---------|-----|----------------|
| Communication | One-way | Two-way |
| Position Feedback | No | Yes |
| Security | Basic | Encrypted |
| Integration | Limited | Advanced |
| Smart Home | Limited | Full |

## Phantom Blinds Integration

Phantom Blinds typically use **io-homecontrol** motors for:

- Motorized retractable screens
- Motorized shades
- Motorized blinds

### Gateway Requirements

- Must support io-homecontrol protocol
- Should provide network API (REST/HTTP)
- SSE support for real-time events

## Position Control

### Standard Positions

- **0%**: Fully retracted/closed
- **100%**: Fully extended/open
- **Intermediate**: Partial positions (1-99%)

### Tilt Control (for applicable products)

- **0%**: Vanes horizontal (closed)
- **100%**: Vanes vertical (open)
- Rotation depends on motor type (90° or 180°)

### Favorites/Presets

Some Somfy motors support "My" position:

- User-defined favorite position
- Quickly accessible via remote
- API may support "MY" command

## Motor Capabilities

### Basic Motors

- Open/Close/Stop only
- No positioning
- No feedback

### Advanced Motors

- Precise positioning (0-100%)
- Position feedback via io-homecontrol
- Tilt control (if applicable)
- Slow speed for fine adjustments
- Obstacle detection

## Programming and Limits

### End Limits

- **Upper limit**: Maximum extension
- **Lower limit**: Minimum retraction
- Set during motor installation
- Can be adjusted via programming mode

### Intermediate Positions

- Some motors support multiple presets
- "My" position is most common
- Scenes can define multiple positions

## Network Protocol Notes

### Command Structure

The gateway translates network commands to Somfy motor commands:

**Network API** → **Gateway** → **io-homecontrol Radio** → **Motor**

### Response Time

- Command acknowledgment: Immediate (HTTP response)
- Motor movement start: 100-500ms
- Position feedback: During movement (via SSE)
- Movement completion: Depends on distance

## Power Considerations

### Motor Power Sources

1. **AC Powered**: Direct electrical connection
2. **DC Powered**: Low voltage (12-24V)
3. **Battery Powered**: Rechargeable or replaceable
4. **Solar Powered**: With battery backup

### Battery-Powered Implications

- Position updates may be less frequent
- Motor may "sleep" to conserve power
- Commands may have slight delay
- Low battery warnings via API

## Troubleshooting

### Motor Not Responding

1. Check power supply
2. Verify radio range
3. Check for obstacles
4. Confirm motor is paired with gateway

### Position Drift

- Recalibrate end limits
- Check for mechanical issues
- Update motor firmware if available

### Slow Response

- Radio interference (check 868/916 MHz band)
- Gateway overload (too many simultaneous commands)
- Network issues between API client and gateway

## API Considerations for Somfy Motors

### Positioning Accuracy

- Somfy motors typically accurate to ±2%
- Some drift over time due to mechanical wear
- Recalibration may be needed periodically

### Movement Speed

- Default speed: Full speed
- Velocity parameter: 0-100%
- Lower velocity for quieter operation
- Higher velocity for faster response

### Simultaneous Control

- io-homecontrol allows synchronized movement
- Gateway manages timing
- Use scenes for coordinated control

## Future Protocol Support

### Thread/Matter

- Next-generation smart home protocols
- Some newer Somfy products may support
- Check specific product compatibility

### Cloud Integration

- TaHoma (Somfy's cloud platform)
- Integration may be available
- Consider local API vs. cloud API

## References

**TODO**: Add specific references for:

- Somfy motor specifications
- io-homecontrol protocol documentation
- Phantom Blinds motor models
- Gateway firmware versions and capabilities

## Motor Identification

When discovering motors, the following information is useful:

- Motor model number
- Protocol version (RTS vs. io-homecontrol)
- Firmware version
- Supported features (tilt, multiple positions, etc.)

The API `capabilities` field helps identify motor features programmatically.
