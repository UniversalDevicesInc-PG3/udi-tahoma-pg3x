# Phantom Blinds — Polyglot Configuration
<!-- markdownlint-disable-file MD036 MD007 MD022 MD013 -->

## Prerequisites

1. Somfy TaHoma RTS/Zigbee gateway (Item #1811731) on your network
2. Shades paired and working in the TaHoma mobile app
3. Developer Mode enabled in the TaHoma app
4. Bearer token generated and saved securely (shown only once)
5. Gateway PIN noted (`XXXX-XXXX-XXXX`)

## Configuration parameters

Enter all values in the Polyglot UI **Configuration** tab. There is no separate YAML config file.

New installs show **placeholder defaults** until you enter your real TaHoma settings. The NodeServer will not connect while placeholders remain.

### Required

#### `gateway_pin`

TaHoma gateway PIN in `XXXX-XXXX-XXXX` format (12 digits with dashes).

- **Default (placeholder):** `0000-0000-0000` — replace with your PIN before starting
- **Example:** `2001-0001-1891`
- **Where to find:** Label on the bottom of the TaHoma unit, or TaHoma app → Menu → Help & Advanced Features → My Setup → TaHoma PIN

#### `tahoma_token`

Bearer token from TaHoma Developer Mode.

- **Default (placeholder):** 20 zeros — replace with your token before starting
- **Format:** Long alphanumeric string (typically 50+ characters); paste the token only, not a `Bearer ` prefix
- **Security:** Stored in Polyglot; used only to authenticate to your local gateway

### Optional

#### `gateway_ip`

Optional. Leave at the default unless you need an explicit address.

- **Default (placeholder):** `gateway-0000-0000-0000.local` — ignored; the NodeServer uses `gateway-{pin}.local` from your PIN
- **When to change:** If mDNS to `gateway-{pin}.local` is unreliable, enter the TaHoma **IP address** (for example `192.168.1.100`)
- **Important:** Assign the TaHoma a static IP or router DHCP reservation if you use an IP here

#### `verify_ssl`

Whether to verify the TaHoma HTTPS certificate.

- **Default:** `false`
- **Recommended:** Leave at `false`. TaHoma presents a self-signed certificate on your LAN; verification is not required for normal home use.

Setting **`true`** is optional and only makes sense if you install the [Somfy root CA](https://ca.overkiz.com/overkiz-root-ca-2048.crt) on your **EISY or Polisy** so the system trusts that certificate. On FreeBSD (EISY/Polisy), that typically means copying the `.crt` file into the local trusted certs directory (for example `/usr/local/share/certs/`), then running `certctl rehash` as root over SSH. We do **not** recommend this for typical installations.

### Reference table

| Parameter | Required | Default | Example |
|-----------|----------|---------|---------|
| `gateway_pin` | Yes | `0000-0000-0000` | `2001-0001-1891` |
| `tahoma_token` | Yes | (20 zeros) | (token from app) |
| `gateway_ip` | No | `gateway-0000-0000-0000.local` (ignored) | `192.168.1.100` |
| `verify_ssl` | No | `false` | `false` |

## TaHoma setup

### Generating a Bearer token

1. Open the TaHoma app on your mobile device.
2. Tap **Menu** (bottom right) → **Configuration of the installation** → **Access the parameters**.
3. Tap the PIN number **7 times** to enable Developer Mode; accept the disclaimer.
4. Go to Menu → **Developer Mode**.
5. Tap **Generate Token** and copy the token immediately — it is only shown once.

If you lose the token, generate a new one in Developer Mode.

### Save and verify

1. Enter `gateway_pin` and `tahoma_token` (replace the placeholder defaults).
2. Leave `gateway_ip` at the default unless mDNS to `gateway-{pin}.local` fails; if you set an IP, use a static/reserved address on the TaHoma.
3. Leave `verify_ssl` at `false` unless you have installed the Somfy root CA on the EISY/Polisy.
4. Click **Save**.
5. Start the NodeServer and check the log for successful authentication.
6. Run **Discover** on the controller node in the Admin Console.
7. Test Open/Close on a shade node.

### Network

The NodeServer reaches TaHoma on your LAN over HTTPS (port **8443**).

- **Default:** `gateway-{pin}.local` via mDNS (for example `gateway-2001-0001-1891.local`)
- **Fallback:** `gateway_ip` if mDNS is unreliable (static/reserved IP on the TaHoma recommended)

Ensure firewall rules allow HTTPS to the gateway.

## Troubleshooting

### Configuration errors

**Invalid Gateway PIN**

- Must match `^\d{4}-\d{4}-\d{4}$` (e.g. `2001-0001-1891`, not digits without dashes).

**Invalid Bearer token**

- Replace placeholder text with the token from the TaHoma app.
- Token must be at least 20 characters (typically 50+); no spaces or line breaks.
- Generate a new token if the old one was lost or revoked.

### Connection issues

**Cannot connect to TaHoma**

- Confirm TaHoma is online (green LED) and on the same network as Polisy/EISY.
- Try `ping gateway-{pin}.local`. If that fails, set `gateway_ip` to the TaHoma’s static/reserved IP.
- Verify Developer Mode is enabled and the token is current.
- Leave `verify_ssl` at `false` unless you installed the Somfy root CA on the EISY/Polisy.

**NodeServer won't start**

- Check the Polyglot log for validation errors on `gateway_pin` or `tahoma_token`.
- Restart Polyglot if dependencies failed to install: `sudo systemctl restart polyglot`

### Discovery and control

**No devices discovered**

- Confirm shades appear and respond in the TaHoma app.
- Wait a minute after startup, then right-click the controller → **Discover**.
- Review the NodeServer log for API errors.

**Shades don't respond**

- Test the shade in the TaHoma app first.
- Check RTS range (roughly 25–35 feet line of sight to the gateway).
- Check battery-powered motors for low battery.

**Position not updating**

- Confirm the log shows the event polling loop running.
- Right-click the shade → **Query** to force a refresh.
- Restart the NodeServer if event polling stopped.

### SSL certificate errors

The default is `verify_ssl` **`false`**, which skips verification of TaHoma’s self-signed certificate. That is appropriate for normal home use on a local network.

If you set `verify_ssl` to **`true`**, you must install the [Somfy root CA](https://ca.overkiz.com/overkiz-root-ca-2048.crt) on the EISY or Polisy (SSH as root). On FreeBSD, copy the certificate into `/usr/local/share/certs/` (create the directory if needed), then run:

```bash
certctl rehash
```

We do not recommend enabling certificate verification unless you have a specific reason to do so.

## Uninstalling

1. Stop the NodeServer in Polyglot.
2. Delete the NodeServer.
3. Remove the NodeServer folder in the Admin Console if it remains.
4. Optionally revoke tokens in the TaHoma app Developer Mode.

## References

- [README.md](README.md) — Overview and installation
- [Somfy Developer Mode API](https://github.com/Somfy-Developer/Somfy-TaHoma-Developer-Mode)
- [TaHoma documentation (Somfy Pro)](https://www.somfypro.com/tahomadocumentation)
