# PowerView Code Removal - Detailed Plan

## Status: ✅ Started - In Progress

## Completed Removals

### ✅ 1. Removed PowerView URL Constants (Lines 49-67)

- Removed all URL_* constants for PowerView API endpoints
- Kept only the asyncio event loop

## Remaining Removals

### Controller.py Methods and Attributes

#### Methods to Remove Entirely

1. **`_goodip()` (line ~546)** - PowerView Gen3 gateway validation
2. **`updateAllFromServerG3()` (line ~1240)** - PowerView data parsing
3. **`updateActiveFromServerG3()` (line ~1310)** - PowerView active scenes
4. **`getHomeG3()` (line ~1331)** - PowerView home data fetch
5. **`getScenesActiveG3()` (line ~1362)** - PowerView scenes fetch
6. **`get()` (line ~1393)** - HTTP GET for PowerView
7. **`put()` (line ~1465)** - HTTP PUT for PowerView
8. **`toPercent()` (line ~1446)** - PowerView percentage conversion

#### Attributes to Remove from `__init__`

- `self.generation`
- `self.gateway`
- `self.gateways`
- Any PowerView-specific storage structures

#### Code Blocks to Clean

- Remove PowerView logic from `poll()` method
- Clean up any `if self.generation == 2/3` blocks
- Remove PowerView event processing code

### Shade.py

#### Methods to Remove

1. **`_get_g2_positions()`** - Gen 2 position format
2. **`_get_g3_positions()`** - Gen 3 position format
3. **`setShadePosition()`** - PowerView position setting
4. **`fromPercent()`** - PowerView percentage conversion
5. **`cmdJog()`** - PowerView only
6. **`cmdCalibrate()`** - PowerView Gen 2 only

#### Classes to Remove

1. **`ShadeOnlySecondary`** - Not used for TaHoma
2. **`ShadeNoSecondary`** - Not used for TaHoma
3. **`ShadeOnlyTilt`** - Not used for TaHoma

#### Code to Clean

- Remove generation checks from command methods
- Remove capabilities-based driver mapping (use TaHoma states instead)
- Clean up PowerView comments

### Scene.py

#### Code to Clean in Scene

- Remove generation checks from `cmdActivate()`
- Remove PowerView URL references
- Clean up dual-path logic (keep only TaHoma)

### Node Classes

#### Files to Delete

- ✅ `nodes/VirtualGeneric.py` - Not used
- ✅ `nodes/Controller_V.py` - Old version

#### Update `nodes/__init__.py`

Remove exports:

- `ShadeOnlySecondary`
- `ShadeNoSecondary`
- `ShadeOnlyTilt`
- `VirtualGeneric`

## Imports to Clean

### Imports in Controller.py

- Remove `requests` import (only needed for PowerView HTTP)
- Keep `aiohttp` (used by TaHomaClient)

## Estimated Results

### Line Count Reductions

- **Controller.py**: 1507 → ~900 lines (600 lines removed)
- **Shade.py**: ~850 → ~500 lines (350 lines removed)
- **Scene.py**: ~520 → ~350 lines (170 lines removed)
- **Total cleanup**: ~1,120 lines removed

### Benefits

1. **Simpler codebase** - Single purpose (TaHoma only)
2. **Easier maintenance** - No dual-path logic
3. **Clearer intent** - Obviously for Phantom/TaHoma
4. **Fewer bugs** - Less code = fewer places for errors
5. **Better performance** - No unused code paths

## Next Steps

1. Remove methods listed above from Controller.py
2. Clean Shade.py command methods
3. Remove unused Shade classes
4. Clean Scene.py
5. Delete unused files
6. Update **init**.py
7. Run pyright to verify
8. Test basic functionality

## Notes

- Keep all TaHoma-specific code
- Keep Shade, ShadeNoTilt, ShadeOnlyPrimary classes (used by TaHoma)
- Keep Scene class
- All PowerView code is in git history if needed later
