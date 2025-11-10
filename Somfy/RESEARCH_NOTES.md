# Research and Investigation Notes

<!-- markdownlint-disable MD022 MD013 -->

**CRITICAL DISCOVERY**: This plugin was originally based on Hunter Douglas
PowerView API patterns, but Phantom Blinds use the **Somfy TaHoma** API, which
is significantly different!

See [`TAHOMA_VS_POWERVIEW.md`](TAHOMA_VS_POWERVIEW.md) for detailed comparison.

## Major Findings

✅ **Official API Found**: <https://github.com/Somfy-Developer/Somfy-TaHoma-Developer-Mode>

### Key Facts About TaHoma API

1. **HTTPS only** on port 8443 (not HTTP)
2. **Bearer token authentication required** (not optional)
3. **Event polling** (not SSE streaming)
4. **Different URL structure** entirely
5. **Self-signed certificates** (need CA trust)
6. **mDNS discovery** with `_kizboxdev._tcp` service

## Current Plugin Status

The existing code in `Controller.py` implements PowerView patterns:

- ❌ HTTP on port 80
- ❌ No authentication
- ❌ SSE streaming for events
- ❌ PowerView URL structure

**Action Required**: Major refactoring needed to support TaHoma API properly.

---

This file contains areas where more information is needed about the Somfy/Phantom Blinds API.

## High Priority Research Items

### 1. Authentication ✅ RESOLVED

- [x] Does the API require authentication? **YES**
- [x] API keys, tokens, or credentials needed? **Bearer token**
- [x] OAuth support? **No**
- [x] Basic auth? **No, Bearer token only**
- [x] Certificate-based auth? **HTTPS with self-signed cert**

**Implementation**:

- Enable Developer Mode in TaHoma app (tap version 7 times)
- Generate token from Developer Mode menu
- Add `Authorization: Bearer <token>` to all requests
- Trust CA cert from `https://ca.overkiz.com/overkiz-root-ca-2048.crt`

### 2. Gateway Discovery ✅ RESOLVED

- [x] mDNS/Bonjour service name: **`_kizboxdev._tcp`**
- [x] Default hostname pattern: **`gateway-{pin}.local`** (e.g., `gateway-2001-0001-1891.local`)
- [x] Discovery protocol: **mDNS**
- [ ] Multi-gateway coordination: **TBD**

**TXT Records**:

- `gateway_pin`: Gateway PIN (e.g., 1234-5678-9012)
- `api_version`: Version of available REST API (e.g., 1)
- `fw_version`: Firmware version (e.g., 2019.4.3)

### 3. API Versioning ✅ RESOLVED

- [x] Are there different API versions? **Yes**
- [x] Version negotiation: **Via `/apiVersion` endpoint (no auth required)**
- [ ] Backward compatibility: **TBD**
- [x] Feature detection by API version: **Via protocolVersion in response**

**Example**:

```bash
GET /enduser-mobile-web/1/enduserAPI/apiVersion
# Returns: {"protocolVersion": "2022.1.3-1"}
```text

### 4. Rate Limiting ✅ RESOLVED

- [x] What are the rate limits? **NO rate limiting on local API**
- [x] Per-endpoint limits: **None**
- [x] Global request limits: **None (but gateway can be overloaded)**
- [x] Consequences of exceeding limits: **Gateway latency**
- [x] Retry-After headers: **Not applicable**

**Best Practices** (from Somfy):

- Call `/setup` at application start
- Register event listener with `/events/register`
- Fetch events on `/events/{listenerId}/fetch` **once per second maximum**
- Don't poll too frequently to avoid overloading gateway

### 5. Error Codes

Complete list of possible error codes and meanings:

- [ ] 400 - Bad Request details
- [ ] 401 - Unauthorized (if auth exists)
- [ ] 403 - Forbidden scenarios
- [ ] 404 - Not Found specifics
- [ ] 429 - Too Many Requests
- [ ] 500 - Server errors
- [ ] 503 - Service Unavailable details

## Medium Priority Research Items

### 6. Phantom Blinds Specifics

- [ ] Official Phantom Blinds API documentation
- [ ] Phantom-specific endpoints
- [ ] Differences from Hunter Douglas PowerView
- [ ] Phantom gateway models and capabilities

### 7. Motor Capabilities Detail

- [ ] Complete list of capability codes
- [ ] Motor type codes (1-10 and beyond)
- [ ] Which motors support which features
- [ ] Velocity range and behavior

### 8. Scene Behavior

- [ ] Scene execution timing
- [ ] Scene priority/queuing
- [ ] Conflict resolution (multiple active scenes)
- [ ] Scene duration limits

### 9. Event Stream Details

- [ ] Complete list of all event types
- [ ] Event retry behavior
- [ ] Maximum event age
- [ ] Event ordering guarantees
- [ ] Reconnection protocol after disconnect

### 10. Position Encoding

- [ ] Verify position scale (0-100 vs 0-65535)
- [ ] Generation differences (G2 vs G3)
- [ ] Precision requirements
- [ ] Rounding behavior

## Low Priority Research Items

### 11. Firmware Updates

- [ ] API for checking firmware version
- [ ] Update mechanisms
- [ ] Version compatibility

### 12. Diagnostics

- [ ] Diagnostic endpoints
- [ ] Log access
- [ ] Error reporting
- [ ] Health check endpoints

### 13. Advanced Features

- [ ] Scheduling support
- [ ] Automation rules
- [ ] Sensor integration
- [ ] Weather-based control

### 14. Multi-Gateway Environments

- [ ] Primary/secondary designation
- [ ] Data synchronization
- [ ] Failover behavior
- [ ] Load balancing

### 15. Performance Characteristics

- [ ] Typical response times
- [ ] Concurrent request limits
- [ ] Memory usage patterns
- [ ] Network bandwidth requirements

## Testing Needed

### API Endpoint Testing

- [ ] Test all documented endpoints
- [ ] Verify request/response formats
- [ ] Check error conditions
- [ ] Validate data types

### Edge Case Testing

- [ ] Invalid shade IDs
- [ ] Out-of-range positions
- [ ] Disconnected motors
- [ ] Network interruptions
- [ ] Simultaneous commands

### Load Testing

- [ ] Multiple simultaneous requests
- [ ] Rapid successive commands
- [ ] Long-running SSE connections
- [ ] Memory leaks over time

### Integration Testing

- [ ] ISY integration verification
- [ ] Event handling accuracy
- [ ] State synchronization
- [ ] Recovery from errors

## Documentation Gaps

### User Documentation Needed

- [ ] Setup guide for Phantom Blinds
- [ ] Gateway configuration
- [ ] Troubleshooting guide
- [ ] FAQ section

### Developer Documentation Needed

- [ ] API client library examples
- [ ] SDK documentation (if available)
- [ ] Best practices guide
- [ ] Migration guide from other systems

## Comparison with Hunter Douglas PowerView

### Known Similarities

- REST API structure
- SSE for events
- Position control (0-100%)
- Scene support

### Known Differences

**TODO**: Document differences between Phantom/Somfy and Hunter Douglas:

- [ ] URL patterns
- [ ] Authentication methods
- [ ] Event types
- [ ] Motor capabilities encoding
- [ ] Gateway models

### Reusable Code

From the Hunter Douglas plugin, the following patterns are reused:

- SSE client implementation
- Event queue management
- Position conversion
- Node creation based on capabilities
- Room/shade mapping

## Questions for Phantom Blinds / Somfy

1. Is there official API documentation available?
2. What authentication is required for production use?
3. Are there API usage limits we should be aware of?
4. What is the recommended polling/update frequency?
5. How should we handle multi-gateway environments?
6. Is there a certification process for integrations?
7. What support is available for developers?
8. Are there any upcoming API changes we should prepare for?

## Resources to Investigate

### Potential Documentation Sources

- [ ] Phantom Blinds official website
- [ ] Somfy professional documentation
- [ ] io-homecontrol specifications
- [ ] Integration partner portals
- [ ] Developer forums

### Related Projects

- [ ] Home Assistant integrations
- [ ] OpenHAB bindings
- [ ] Other third-party integrations
- [ ] GitHub repositories

### Standards and Protocols

- [ ] io-homecontrol protocol specs
- [ ] Server-Sent Events (SSE) specification
- [ ] REST API best practices
- [ ] Home automation standards

## Notes from Code Analysis

Based on Controller.py analysis, the current implementation assumes:

1. Hunter Douglas PowerView G3 URL patterns
2. No authentication required
3. Direct JSON responses
4. SSE with "100 HELO" heartbeat
5. Base64-encoded shade names
6. Capabilities field 0-10

**Action Items**:

- [ ] Verify these assumptions for Phantom Blinds
- [ ] Test with actual Phantom hardware
- [ ] Document any necessary adjustments
- [ ] Update implementation if needed

## Testing Environment

### Required Hardware

- [ ] Phantom Blinds gateway
- [ ] At least one Phantom shade/screen
- [ ] Network connectivity
- [ ] ISY for integration testing

### Test Scenarios

1. Basic control (open/close/stop)
2. Position control (precise positioning)
3. Scene activation
4. Event monitoring
5. Error handling
6. Multi-shade coordination
7. Long-term stability

## Timeline

**Phase 1**: Initial API documentation (DONE)

- Created basic documentation structure
- Documented assumed API patterns
- Listed research items

**Phase 2**: Hardware testing (TODO)

- Acquire test hardware
- Verify API endpoints
- Document actual behavior

**Phase 3**: Documentation updates (TODO)

- Fill in gaps based on testing
- Update examples with real data
- Add troubleshooting guides

**Phase 4**: Implementation refinement (TODO)

- Adjust code based on findings
- Optimize for Phantom specifics
- Add missing features

---

**Last Updated**: 2025-11-09
**Status**: Initial documentation phase complete, awaiting hardware testing
