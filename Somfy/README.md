# Somfy / TaHoma — Developer Reference

<!-- markdownlint-disable MD022 MD013 -->

Internal documentation for working on this NodeServer. **End users** should use [README.md](../README.md) and [POLYGLOT_CONFIG.md](../POLYGLOT_CONFIG.md) only.

## Integration summary

This plugin talks to a **Somfy TaHoma** gateway via the **Developer Mode local API** (HTTPS port 8443), using **pyoverkiz** and a **Bearer token** from the TaHoma app. Status updates use **event listener polling** (~1 s), not SSE streaming.

Official API reference: [Somfy TaHoma Developer Mode](https://github.com/Somfy-Developer/Somfy-TaHoma-Developer-Mode)

## Reference docs

| Document | Purpose |
|----------|---------|
| [CLARIFICATION_OAUTH_SSE.md](CLARIFICATION_OAUTH_SSE.md) | Local vs cloud auth; polling vs SSE |
| [HARDWARE_REFERENCE.md](HARDWARE_REFERENCE.md) | TaHoma gateway specs and placement |
| [HARDWARE_TESTING_GUIDE.md](HARDWARE_TESTING_GUIDE.md) | Dev/hardware validation checklist |

## Code entry points

- `nodes/Controller.py` — connection, discovery, event polling
- `nodes/Shade.py` — shade nodes
- `nodes/Scene.py` — TaHoma scenario nodes
- `utils/tahoma_client.py` — pyoverkiz wrapper
- `utils/config_validation.py` — Polyglot parameter validation
- `utils/device_capabilities.py` — per-device capability profiles
