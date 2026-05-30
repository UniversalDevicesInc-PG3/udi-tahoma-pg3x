<!-- markdownlint-disable MD022 MD013 -->
# Phantom Blinds NodeServer for PG3x

NodeServer for Universal Devices **EISY** or **Polisy** (Polyglot V3) that controls Phantom Blinds and other Somfy RTS shades through a TaHoma gateway using the Developer Mode local API.

## Requirements

- Universal Devices **EISY** or **Polisy** with Polyglot V3 (PG3x)
- Somfy TaHoma RTS/Zigbee gateway (Item #1811731)
- Phantom Blinds (or other Somfy RTS devices) paired in the TaHoma app
- TaHoma Developer Mode enabled with a Bearer token
- Network connectivity between Polisy/EISY and TaHoma (2.4 GHz Wi‑Fi or Ethernet)

## Features

- Local API control (direct connection on your LAN; no Somfy cloud required)
- Automatic discovery of RTS shades and TaHoma scenes
- Open, Close, Stop, My Position, and position control where supported
- Real-time status via event polling
- Tilt control on compatible blinds

## Installation

### 1. Prepare TaHoma

Before installing the NodeServer:

1. Install and power the TaHoma gateway; confirm it is on your network (green LED).
2. Pair your shades in the TaHoma mobile app.
3. Enable Developer Mode and generate a Bearer token (see [POLYGLOT_CONFIG.md](POLYGLOT_CONFIG.md#generating-a-bearer-token)).
4. Note your Gateway PIN (`XXXX-XXXX-XXXX`) from the device label or TaHoma app.

### 2. Install the NodeServer

**From the Polyglot Store (recommended)**

1. Open the Polyglot UI (`http://<polisy-or-eisy-ip>:3000`).
2. Go to **NodeServer Store**.
3. Search for **Phantom Blinds** and click **Install**.

**From GitHub**

1. In the NodeServer Store, choose **Install from GitHub**.
2. Enter the repository URL and select the `main` branch.
3. Click **Install**.

### 3. Configure and start

1. Open the NodeServer **Configuration** tab.
2. Enter your settings (see [POLYGLOT_CONFIG.md](POLYGLOT_CONFIG.md) for parameter details).
3. Click **Save**, then **Start**, and check the **Log** tab for a successful TaHoma connection.

### 4. Discover devices

1. In the ISY Admin Console, expand the NodeServer folder.
2. Right-click **Phantom Blinds Controller** → **Discover**.
3. Shade and scene nodes should appear within about a minute.

## Configuration

All settings are entered in the Polyglot UI Configuration page (not a YAML file).

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `gateway_pin` | Yes | `0000-0000-0000` | Your TaHoma PIN (`XXXX-XXXX-XXXX`) |
| `tahoma_token` | Yes | (64 zeros) | Bearer token from Developer Mode |
| `gateway_ip` | No | `gateway-0000-0000-0000.local` | Ignored by default; set IP if mDNS fails |
| `verify_ssl` | No | `false` | See config doc for `true` |

Full setup steps and troubleshooting: **[POLYGLOT_CONFIG.md](POLYGLOT_CONFIG.md)**

## Usage

Each shade node supports position, Open, Close, Stop, and My Position where the motor supports them. Scenes from TaHoma appear as separate nodes. Use ISY programs, schedules, or the Admin Console to control shades.

After upgrading the NodeServer, update the profile in Polyglot if prompted, then run **Discover** again.

## Troubleshooting

Common issues (invalid PIN, token errors, connection failures, discovery, commands) are covered in [POLYGLOT_CONFIG.md — Troubleshooting](POLYGLOT_CONFIG.md#troubleshooting).

Enable debug logging in Polyglot for detailed diagnostics. Check the NodeServer **Log** tab first.

## Documentation

- **[POLYGLOT_CONFIG.md](POLYGLOT_CONFIG.md)** — Configuration, TaHoma setup, troubleshooting
- **[VersionHistory.md](VersionHistory.md)** — Release notes

## Support

- GitHub Issues: [udi-phantomblinds-pg3x](https://github.com/sejgit/udi-phantomblinds-pg3x/issues)
- [Universal Devices Forum](https://forum.universal-devices.com)

## License

See [LICENSE](LICENSE).
