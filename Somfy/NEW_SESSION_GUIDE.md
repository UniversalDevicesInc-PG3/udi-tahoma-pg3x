<!-- markdownlint-disable MD013 MD022 -->
# Getting Started with This Project (New Session Guide)

## Quick Context

This is a Polyglot v3 plugin for Universal Devices EISY/Polisy that integrates **Phantom Blinds** (Somfy TaHoma-based motorized shades) with the ISY automation system.

## Project Status

- **Phase**: Development (pre-hardware testing)
- **Hardware**: Waiting for Phantom Blinds installation with Somfy TaHoma hub
- **Testing**: Cannot test against real hardware yet

## Key Architecture

1. **TaHoma Integration**: Uses `pyoverkiz` library for Somfy TaHoma API
   - OAuth2 authentication
   - Local API preferred (cloud fallback)
   - SSE for real-time events

2. **Polyglot Interface**: Via `udi_interface` (PG3x)
   - Controller node manages TaHoma connection
   - Shade nodes represent individual blinds
   - NLS files define UI strings
   - Profile defines node structure

3. **Clean Somfy Implementation**: Focused on TaHoma integration

## Important Files

### Documentation (Start Here)

- `Somfy/README.md` - TaHoma integration overview
- `Somfy/HARDWARE_REFERENCE.md` - Hardware specs and installation requirements
- `Somfy/API_ENDPOINTS.md` - TaHoma API details
- `Somfy/HARDWARE_TESTING_GUIDE.md` - Testing guide for when hardware arrives
- `Somfy/TABLE_OF_CONTENTS.md` - Index of all Somfy docs
- `Somfy/archive/` - Historical migration documentation

### Code (Primary)

- `nodes/Controller.py` - Main controller, TaHoma connection
- `nodes/PhantomBlind.py` - Individual shade node
- `profile/` - ISY node definitions and UI

### Configuration

- `requirements.txt` - Python dependencies (includes pyoverkiz)
- `server.json` - Polyglot plugin manifest
- `exampleConfigFile.yaml` - Configuration template

## Development Workflow

```bash
# Setup environment
make install          # Install dependencies via pipenv

# Testing
make test            # Run pytest
make testfull        # Run pytest + pyright + pre-commit hooks
make coverage        # Generate coverage report

# Linting
make pyright         # Type checking
make pre-commit      # All pre-commit hooks (includes markdownlint)
```

## What's Completed (Pre-Hardware)

- ✅ TaHoma API integration via pyoverkiz
- ✅ Event handling structure (polling-based)
- ✅ Authentication flow planning
- ✅ Documentation complete
- ✅ Linting/testing infrastructure updated

## What's Needed (Post-Hardware)

1. **Test with real TaHoma hub** - Authentication, device discovery
2. **Refine shade controls** - Position, tilt, open/close commands
3. **Validate event polling** - Real-time status updates
4. **Error handling** - Network issues, auth failures
5. **Production polish** - Logging, edge cases

## Testing Without Hardware

- Unit tests exist but mock TaHoma responses
- Cannot verify actual API behavior until hardware arrives
- Focus has been on structure and integration patterns

## Key Decisions Made

1. **pyoverkiz library**: Using established TaHoma integration library
2. **Local API preferred**: Better performance than cloud
3. **Standard Polyglot patterns**: Following UDI NodeServer best practices

## When You Get Hardware

1. Review `Somfy/HARDWARE_TESTING_GUIDE.md` for testing steps
2. Test authentication flow in `Controller.py`
3. Verify device discovery and shade commands
4. Check event polling behavior
5. Update docs with any API quirks discovered

## Questions to Answer with Hardware

- Does local API work reliably?
- What device types does TaHoma expose?
- Are position/tilt ranges 0-100 or different?
- How fast are event updates?
- Any rate limiting or connection issues?

## Contact Points

- `udi_interface` docs: PG3x integration reference
- `pyoverkiz` GitHub: TaHoma library issues/questions
- Somfy TaHoma Developer Mode: API reference

---

**Last Updated**: 2025-11-11
**Status**: Ready for hardware testing
