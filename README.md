<!-- markdownlint-disable MD022 MD013 -->
# Somfy TaHoma NodeServer for PG3x

NodeServer for Universal Devices **EISY** or **Polisy** (Polyglot V3) that controls shades and automations through a **Somfy TaHoma** gateway using the Developer Mode local API.

This is a **TaHoma plugin**. Specific shade families (Phantom Blinds, io-homecontrol rollers, Zigbee motors, and others) are supported as **applications** on top of the same gateway connection — see [Applications](#applications) below.

Users also report compatibility with the Somfy Beecon, though I cannot guarantee
with all features.

## Requirements

- Universal Devices **EISY** or **Polisy** with Polyglot V3 (PG3x)
- Somfy TaHoma RTS/Zigbee gateway (Item #1811731)
- Shades paired and working in the TaHoma mobile app
- TaHoma Developer Mode enabled with a Bearer token
- Network connectivity between Polisy/EISY and TaHoma (2.4 GHz Wi‑Fi or Ethernet)

## Features

- **Shade control over local API** — direct LAN connection; no Somfy cloud required
- Automatic discovery of shades and TaHoma app scenes (scene Activate is optional; see below)
- Application-specific node types (RTS Shade vs full Shade) based on device protocol
- Open, Close, Stop, My Position; position and tilt where the gateway supports them
- **Last Command** status (Pending / Completed / Failed) for ISY programs
- Real-time updates via event polling
- **Optional scene Activate** via Somfy cloud when you enter TaHoma app credentials

## Applications

The plugin discovers whatever shades and scenarios exist on your TaHoma. How they appear in the ISY depends on the **protocol** reported by the gateway:

- **RTS** (one-way radio)
  - Examples: **Phantom Blinds**, Somfy RTS rollers/awnings
  - Node type: **RTS Shade**
  - Feedback: Commands + Last Command; no position or motion
- **io** (io-homecontrol)
  - Examples: Somfy RS100, many wired/two-way rollers
  - Node type: **Shade**
  - Feedback: Position (and often tilt) when the gateway reports states
- **Zigbee**
  - Examples: TaHoma-paired Zigbee motors
  - Node type: **Shade**
  - Feedback: Varies by device; position when reported
- **Other**
  - Examples: Less common TaHoma device types
  - Node type: **Shade**
  - Feedback: Best-effort; capabilities learned at discovery

### Phantom Blinds (RTS application)

**Phantom Blinds** are the primary RTS application this project was built for: Somfy RTS motors controlled through TaHoma with no position feedback from the gateway. They appear as **RTS Shade** nodes (Id, Battery, Last Command) with Open, Close, Stop, and My Position.

If you only have Phantom Blinds or other RTS shades, you only need the RTS Shade behavior — you do not need position fields in the Admin Console.

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
3. Search for **TaHoma** (or your store listing name) and click **Install**.

**From Git**

1. In the NodeServer Store, choose **Install from GitHub** (or your Git host).
2. Enter the repository URL and select the `main` branch.
3. Click **Install**.

### 3. Configure and start

1. Open the NodeServer **Configuration** tab.
2. Enter your settings (see [POLYGLOT_CONFIG.md](POLYGLOT_CONFIG.md) for parameter details).
3. Click **Save**, then **Start**, and check the **Log** tab for a successful TaHoma connection.

### 4. Discover devices

1. In the ISY Admin Console, expand the NodeServer folder.
2. Right-click **TaHoma Controller** → **Discover**.
3. Shade nodes should appear within about a minute. **Scene** nodes may also appear; they are optional — see [Scenes](#scenes-optional).

## Configuration

All settings are entered in the Polyglot UI Configuration page (not a YAML file).

- **`gateway_pin`** — Required. Default: `0000-0000-0000`. Your TaHoma PIN (`XXXX-XXXX-XXXX`)
- **`tahoma_token`** — Required. Default: 20 zeros. Bearer token from Developer Mode
- **`gateway_ip`** — Optional. Default: `gateway-0000-0000-0000.local` (ignored). Set IP if mDNS fails
- **`verify_ssl`** — Optional. Default: `false`. See config doc for `true`
- **`tahoma_cloud_email`** — Optional. Default: empty. TaHoma app login for scene Activate
- **`tahoma_cloud_password`** — Optional. Default: empty. Paired with cloud email
- **`tahoma_cloud_region`** — Optional. Default: **`somfy_america`**. Somfy cloud hub (NA default)

Full setup steps and troubleshooting: **[POLYGLOT_CONFIG.md](POLYGLOT_CONFIG.md)**

## Usage

See [Applications](#applications) for how RTS vs io/Zigbee nodes differ.

**RTS shades** (including Phantom Blinds) use **RTS Shade** nodes — see [POLYGLOT_CONFIG.md — RTS shades and Last Command](POLYGLOT_CONFIG.md#rts-shades-and-last-command).

**io / Zigbee shades** use full **Shade** nodes with position fields where supported.

### Scenes (optional)

TaHoma **app scenes** appear as **Scenario** nodes with **Activate** and **Last Command (GV7)**. This is **optional**:

- **Shades:** always local API — no cloud account needed
- **Scene Activate:** Somfy cloud only (when you set cloud email/password)
- **No cloud credentials:** scene nodes may still appear; Activate is skipped with no error state

Details, region table, and troubleshooting: **[POLYGLOT_CONFIG.md — TaHoma app scenes](POLYGLOT_CONFIG.md#tahoma-app-scenes-optional)**

After upgrading the NodeServer, **Update Profile** in Polyglot, then run **Discover** again.

## Troubleshooting

Common issues (invalid PIN, token errors, connection failures, discovery, commands) are covered in [POLYGLOT_CONFIG.md — Troubleshooting](POLYGLOT_CONFIG.md#troubleshooting).

Enable debug logging in Polyglot for detailed diagnostics. Check the NodeServer **Log** tab first.

## Documentation

- **[POLYGLOT_CONFIG.md](POLYGLOT_CONFIG.md)** — Configuration, applications, TaHoma setup, troubleshooting
- **[CHANGELOG.md](CHANGELOG.md)** — Release notes

## Support

- GitHub Issues: [udi-tahoma-pg3x](https://github.com/sejgit/udi-tahoma-pg3x/issues)
- [Universal Devices Forum](https://forum.universal-devices.com)

## License

See [LICENSE](LICENSE).
