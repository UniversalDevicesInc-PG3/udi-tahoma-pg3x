# FINDINGS SUMMARY - CRITICAL INFORMATION

<!-- markdownlint-disable MD022 MD013 -->

## What I Discovered

I searched GitHub and found the **official Somfy TaHoma Developer Mode
repository**:

- <https://github.com/Somfy-Developer/Somfy-TaHoma-Developer-Mode>
- Full OpenAPI specification available
- Complete API documentation

## The Problem

**Your current plugin is based on Hunter Douglas PowerView API**, but **Phantom Blinds use Somfy TaHoma API** - these are VERY different systems!

## Critical Differences

| Feature | Current Code (PowerView) | Actual Somfy TaHoma |
|---------|-------------------------|---------------------|
| **Protocol** | HTTP | **HTTPS** |
| **Port** | 80 | **8443** |
| **Auth** | None | **Bearer Token Required** |
| **Events** | SSE streaming | **Polling** (register listener) |
| **Base URL** | `http://{ip}/home/...` | `https://gateway-{pin}.local:8443/enduser-mobile-web/1/enduserAPI/...` |
| **Device ID** | Integer (12345) | **String URL** (`io://...`) |
| **Control** | `PUT /home/shades/{id}/motion` | **`POST /exec/apply`** with JSON actions |
| **Discovery** | IP-based | **mDNS** `_kizboxdev._tcp` |
| **Certificate** | N/A | **Self-signed** (need CA cert) |

## What This Means

### Your Current Implementation

```python
# From Controller.py - Lines 46-57
URL_DEFAULT_GATEWAY = "powerview-g3.local"
URL_GATEWAY = "http://{g}/gateway"
URL_HOME = "http://{g}/home"
URL_SHADES = "http://{g}/home/shades/{id}"
URL_SHADES_MOTION = "http://{g}/home/shades/{id}/motion"
URL_EVENTS = "http://{g}/home/events?sse=false&raw=true"  # SSE streaming

# Lines 774-809: SSE client
async def _client_sse(self):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            async for val in response.content:
                # Streams events continuously
```text

### What TaHoma Actually Needs

```python
# TaHoma structure
URL_BASE = "https://gateway-{pin}.local:8443/enduser-mobile-web/1/enduserAPI"
URL_SETUP = f"{URL_BASE}/setup"  # Get all devices
URL_EXEC = f"{URL_BASE}/exec/apply"  # Control devices
URL_EVENT_REGISTER = f"{URL_BASE}/events/register"
URL_EVENT_FETCH = f"{URL_BASE}/events/{{listenerId}}/fetch"

# Auth required on every request
headers = {"Authorization": f"Bearer {token}"}

# Event polling (NOT streaming)
async def poll_events():
    # 1. Register listener
    resp = await session.post(URL_EVENT_REGISTER, headers=headers)
    listener_id = resp.json()["id"]

    # 2. Poll events every 1 second
    while True:
        resp = await session.post(f"{URL_EVENT_FETCH.format(listenerId=listener_id)}", headers=headers)
        events = resp.json()
        # Process events...
        await asyncio.sleep(1)
```text

## Phantom Blinds vs TaHoma Question

**IMPORTANT QUESTION**: Does your Phantom Blinds system actually use:

1. **Somfy TaHoma** gateway/hub?
2. Or something else that happens to use PowerView-compatible API?

### To Check

- What is your gateway hardware model?
- Is there a "TaHoma" app involved?
- Or is it Hunter Douglas PowerView Gen 3?

## Next Steps - Three Options

### Option 1: Verify Your Hardware

Before making changes, confirm what API your Phantom Blinds actually use:

```bash
# Try PowerView endpoint
curl -v "http://{your_gateway_ip}/home"

# Try TaHoma endpoint (may need to ignore cert)
curl -k -v "https://{your_gateway_ip}:8443/enduser-mobile-web/1/enduserAPI/apiVersion"
```text

### Option 2: If It's TaHoma API

Major refactoring required:

1. Add HTTPS support with self-signed cert handling
2. Implement Bearer token authentication
3. Replace SSE with event listener polling
4. Update all URLs and data structures
5. Change device identification from int to deviceURL
6. Rewrite control commands for exec/apply format

Estimated effort: 2-3 days of development

### Option 3: If It's Actually PowerView

Continue with current approach, just change branding/naming.

## Documentation Status

I've created/updated these files in `Somfy/`:

- ✅ `README.md` - Updated with TaHoma info
- ✅ `TAHOMA_VS_POWERVIEW.md` - Complete comparison
- ✅ `RESEARCH_NOTES.md` - Updated with findings
- ✅ `API_ENDPOINTS.md` - Needs TaHoma update
- ✅ `SSE_EVENTS.md` - Should be renamed to EVENTS.md for TaHoma
- ✅ Other files - Need updates for TaHoma

## Immediate Action Items

1. **Identify your actual hardware/API**
   - Run test commands above
   - Check gateway model/brand
   - Review app being used

2. **If TaHoma**:
   - Review official docs: <https://somfy-developer.github.io/Somfy-TaHoma-Developer-Mode>
   - Plan migration strategy
   - Consider abstraction layer to support both

3. **If PowerView**:
   - Continue current implementation
   - Just update documentation/branding

## Questions to Answer

1. What gateway hardware do you have?
2. What mobile app do you use to control it?
3. Can you access `http://{gateway}/home` or `https://{gateway}:8443/...`?
4. Is "Developer Mode" available in your app?

Please verify your actual hardware/API before proceeding with code changes!

---

**Generated**: 2025-11-09
**Source**: <https://github.com/Somfy-Developer/Somfy-TaHoma-Developer-Mode>
**Status**: Awaiting hardware/API verification
