# Upgrade Instructions for pyoverkiz v2 (Future)

> **⚠️ Note**: This document is for **future reference**. The current NodeServer uses **pyoverkiz v1.x** which is compatible with Python 3.11+ (currently on EISY). When EISY upgrades to Python 3.12+, this guide will help migrate to pyoverkiz v2.

---

This project can be updated to use **pyoverkiz v2.0.0+** (requires Python 3.12+) which includes breaking API changes. Follow the instructions below to upgrade when Python 3.12+ is available.

## Why the upgrade?

The pyoverkiz v1 API had connection timeout issues with the TaHoma gateway. Version 2 provides:
- Better error handling and retry logic
- Improved connection stability
- More robust event listener management
- Better timeout configuration

## Installation

Since v2 is currently in pre-release (release candidate), you need to use the `--pre` flag to install it:

### Option 1: Install from requirements.txt with --pre flag

```bash
pip install --pre -r requirements.txt
```

### Option 2: Install pyoverkiz manually first

```bash
# Install pre-release version
pip install --pre 'pyoverkiz>=2.0.0rc1'

# Then install other requirements
pip install -r requirements.txt
```

### Option 3: Specify exact version

```bash
pip install pyoverkiz==2.0.0rc1
pip install -r requirements.txt
```

## Verify Installation

Check that you have the correct version installed:

```bash
pip show pyoverkiz
```

You should see:
```
Name: pyoverkiz
Version: 2.0.0rc1
```

## What Changed?

The main changes in the codebase are:

1. **Exception names**: Changed from `*Exception` to `*Error` (e.g., `InvalidTokenException` → `InvalidTokenError`)
2. **Authentication**: Now uses `LocalTokenCredentials` instead of passing token as parameter
3. **API methods**: 
   - `execute_command()` now uses `execute_action_group()` internally
   - `execute_scenario()` now uses `execute_persisted_action_group()` internally
   - `get_scenarios()` returns `PersistedActionGroup` objects
4. **Connection handling**: Event listener registration is now separate from login to prevent timeout issues

## Rollback

If you need to rollback to v1 for any reason:

```bash
pip install 'pyoverkiz>=1.13.0,<2.0'
git checkout HEAD~1  # Revert code changes
```

## Notes

- The v2 API requires **Python 3.12 or later** (check pyoverkiz documentation for latest requirements)
- Once pyoverkiz v2 is officially released (not rc), you can remove the `--pre` flag
- All existing functionality should work the same from the user's perspective
