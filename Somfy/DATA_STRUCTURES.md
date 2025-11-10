# Data Structures

<!-- markdownlint-disable MD022 MD013 -->

This document describes the JSON data structures used in the Somfy API.

## Home Object

The main home object contains all configuration data:

```json
{
  "rooms": [...],
  "shades": [...],
  "scenes": [...]
}
```text

## Room Object

```json
{
  "_id": 1,
  "id": 1,
  "name": "Living Room",
  "order": 0,
  "shades": [...]
}
```text

### Fields

- `_id` (int): Internal room ID
- `id` (int): Room ID
- `name` (string): Room name (max 15 chars recommended)
- `order` (int): Display order
- `shades` (array): Array of shade objects in this room

## Shade Object

```json
{
  "id": 12345,
  "name": "bGl2aW5nIHJvb20gLSBzaGFkZSAx",
  "type": 1,
  "capabilities": 7,
  "positions": {
    "primary": 50,
    "secondary": 0,
    "tilt": 45,
    "velocity": 100
  },
  "room_id": 1
}
```text

### Fields

- `id` (int): Unique shade identifier
- `name` (string): Base64-encoded shade name
- `type` (int): Shade type (1-10, varies by manufacturer)
- `capabilities` (int): Capability flags (0-10)
- `positions` (object): Current position values
  - `primary` (int): Main shade position (0-100%)
  - `secondary` (int): Secondary position if dual shade (0-100%)
  - `tilt` (int): Tilt angle (0-100%)
  - `velocity` (int): Movement speed (0-100%)
- `room_id` (int): ID of the room containing this shade

### Capability Flags

The `capabilities` field indicates what the shade can do:

| Value | Description | Primary | Secondary | Tilt |
|-------|-------------|---------|-----------|------|
| 0 | Only Primary | ✓ | ✗ | ✗ |
| 1 | Primary + Tilt (90°) | ✓ | ✗ | 90° |
| 2 | Primary + Tilt (180°) | ✓ | ✗ | 180° |
| 3 | Only Primary (alt) | ✓ | ✗ | ✗ |
| 4 | Primary + Tilt (180°) | ✓ | ✗ | 180° |
| 5 | Only Tilt | ✗ | ✗ | ✓ |
| 6 | Only Secondary | ✗ | ✓ | ✗ |
| 7 | Primary + Secondary | ✓ | ✓ | ✗ |
| 8 | Primary + Secondary (alt) | ✓ | ✓ | ✗ |
| 9 | Primary + Tilt (90°) | ✓ | ✗ | 90° |
| 10 | Primary + Tilt (180°) | ✓ | ✗ | 180° |

**Note**: Capabilities determine which node type is created:

- 0, 3: `ShadeOnlyPrimary`
- 1, 2, 4: `ShadeNoSecondary` (Primary + Tilt)
- 5: `ShadeOnlyTilt`
- 6: `ShadeOnlySecondary`
- 7, 8: `ShadeNoTilt` (Primary + Secondary)
- 9, 10: `Shade` (Full featured)

## Scene Object

```json
{
  "_id": 100,
  "id": 100,
  "name": "Morning",
  "room_Id": 1,
  "order": 0,
  "shadeData": [
    {
      "id": 12345,
      "positions": {
        "primary": 75,
        "secondary": 0,
        "tilt": 0
      }
    }
  ]
}
```text

### Fields

- `_id` (int): Internal scene ID
- `id` (int): Scene ID
- `name` (string): Scene name
- `room_Id` (int|null): Room ID (null for multi-room scenes)
- `order` (int): Display order
- `shadeData` (array): Array of shade positions in this scene

## Position Object

Used in motion commands:

```json
{
  "positions": {
    "primary": 50,
    "secondary": 0,
    "tilt": 45,
    "velocity": 100
  }
}
```text

### Fields

All values are percentages (0-100):

- `primary`: Main shade position (0=closed, 100=open)
- `secondary`: Secondary shade position (for dual shades)
- `tilt`: Vane tilt angle
- `velocity`: Movement speed

## Active Scene Object

```json
{
  "id": 100,
  "name": "Morning",
  "activatedAt": "2025-11-07T19:55:10.531Z"
}
```text

### Fields

- `id` (int): Scene ID
- `name` (string): Scene name
- `activatedAt` (string): ISO 8601 timestamp when activated

## Gateway Object

```json
{
  "id": "ABCD1234",
  "name": "Phantom Gateway",
  "firmware": "3.2.1",
  "type": "G3",
  "isPrimary": true
}
```text

### Fields

- `id` (string): Gateway unique identifier
- `name` (string): Gateway name
- `firmware` (string): Firmware version
- `type` (string): Gateway type/generation
- `isPrimary` (bool): Whether this is the primary gateway in a multi-gateway setup

## Error Response

```json
{
  "message": "Not Found",
  "errMsg": "Error fetching from gateway, check configuration"
}
```text

## Notes

### Name Encoding

Shade names in the API are Base64-encoded. The plugin decodes them:

```python
name = base64.b64decode(sh.get("name", "shade")).decode()
```text

### Position Conversion

Raw position values are converted to percentages:

```python
newpos = math.trunc((float(pos) / divr * 100.0) + 0.5)
```text

For Gen 3 gateways, `divr = 1.0` (positions already in percentage).

### Valid Names

Room and shade names are combined and validated:

```python
sh["name"] = self.poly.getValidName(f"{room_name} - {shade_name}")
```text

This ensures names meet ISY naming requirements.
