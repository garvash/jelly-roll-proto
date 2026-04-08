# Phase 20: Grid Constants & Schema Metadata - Research

**Researched:** 2026-04-08
**Domain:** Game constant migration, JSON schema update, test refactoring
**Confidence:** HIGH

## Summary

Phase 20 is a constant-value migration: change TILE_SIZE from 8 to 16, remove the SPRITE_SCALE indirection layer, update derived constants, bump the entity-schema.json version, and fix tests. The scope is narrow and well-defined -- no collision box changes, no physics tuning, no tileset art. Every file that needs changing imports from `src/core/constants.py` or reads `assets/entity-schema.json`, making the blast radius predictable.

The key risk is TILE_EMPTY sentinel value: map.py clears all 256x256 tilemap cells to TILE_EMPTY on load, so the new value (15, 15) must be correct for the 16px grid or the entire tilemap renders garbage. The export_tilemap_csv.py script also needs tiles-per-row updated from 32 to 16.

**Primary recommendation:** Change constants.py first (TILE_SIZE, remove SPRITE_SCALE, set SPRITE_SIZE/BOSS_SPRITE_SIZE as direct values, update TILE_EMPTY), then entity-schema.json, then export script, then tests. Each step is independently verifiable.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Derive tile counts from pixel size / grid_size. No hardcoded tile counts in constants or schema. default_room_size stays as [320, 176] pixels; tile counts (20x11) are computed.
- **D-02:** Delete SPRITE_SCALE entirely from constants.py.
- **D-03:** Keep SPRITE_SIZE as a named constant = 16 (= TILE_SIZE). Reads clearly in draw_sprite() calls and separates rendering concept from collision grid concept.
- **D-04:** BOSS_SPRITE_SIZE = 32 (= 2 * TILE_SIZE). Defined as a direct constant, no SPRITE_SCALE indirection.
- **D-05:** Bump entity-schema.json from v1.0.0 to v2.0.0 (major). grid_size 8->16 is a breaking change for the pml-to-ldtk converter contract.
- **D-06:** Update tile_coords description in schema from "8px tile grid" to "16px tile grid". Leave actual coordinate values unchanged -- Phase 21 will update them when the 16px tileset is ready.
- **D-07:** Change TILE_EMPTY from (31, 31) to (15, 15). Bottom-right corner of a 256x256 image bank at 16px tile size is (15, 15).
- **D-08:** Update the CSV export script's tile count math and tiles-per-row calculation for 16px (256/16=16 tiles per row). Keep the script functional.
- **D-09:** Replace test_sprite_scale.py assertions with new contract: TILE_SIZE == 16, SPRITE_SIZE == 16, BOSS_SPRITE_SIZE == 32, and assert SPRITE_SCALE is no longer importable.

### Claude's Discretion
- Constants ordering and comment updates in constants.py
- Schema field ordering and note updates in entity-schema.json
- variable_rooms_note text update (currently references "40x22 tiles")

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GRID-01 | Game uses 16x16 as the base tile size (TILE_SIZE=16) | Change line 2 of constants.py: `TILE_SIZE = 16` |
| GRID-02 | SPRITE_SCALE indirection removed | Delete lines 15-17 of constants.py (SPRITE_SCALE and derived formulas), replace with direct values |
| GRID-03 | All derived constants updated for 16x16 base | SPRITE_SIZE = 16, BOSS_SPRITE_SIZE = 32, TILE_EMPTY = (15, 15), export script tiles-per-row = 16 |
| GRID-04 | Room dimensions are 20x11 tiles (320x176 pixels) | No code change needed: 320/16=20, 176/16=11. Update variable_rooms_note in schema. Verify VIEWPORT_W/H % 16 == 0 |
| LDTK-01 | entity-schema.json grid_size updated to 16 | Change `"grid_size": 8` to `"grid_size": 16` on line 12 |
| LDTK-05 | Schema version bumped to reflect breaking grid change | Change `"version": "1.0.0"` to `"version": "2.0.0"` on line 6 |
</phase_requirements>

## Architecture Patterns

### Change Map (Before -> After)

**constants.py changes:**
```python
# BEFORE
TILE_SIZE = 8
SPRITE_SCALE = 2
SPRITE_SIZE = TILE_SIZE * SPRITE_SCALE  # 16
BOSS_SPRITE_SIZE = 16 * SPRITE_SCALE    # 32
TILE_EMPTY = (31, 31)

# AFTER
TILE_SIZE = 16
SPRITE_SIZE = 16      # Standard entity visual dimensions (= TILE_SIZE)
BOSS_SPRITE_SIZE = 32  # Boss entity visual dimensions (= 2 * TILE_SIZE)
TILE_EMPTY = (15, 15)  # Bottom-right of 256x256 bank at 16px grid
```

**entity-schema.json changes:**
```json
// BEFORE
"version": "1.0.0",
"grid_size": 8,
"tile_coords.description": "...8px tile grid..."
"variable_rooms_note": "...40x22 tiles..."

// AFTER
"version": "2.0.0",
"grid_size": 16,
"tile_coords.description": "...16px tile grid..."
"variable_rooms_note": "...20x11 tiles..."
```

**export_tilemap_csv.py changes:**
```python
# BEFORE: 256 / 8 = 32 tiles per row
tile_id = v * 32 + u

# AFTER: 256 / 16 = 16 tiles per row
tile_id = v * 16 + u
```

### Files Affected (Complete List)

| File | What Changes | Auto or Manual |
|------|-------------|----------------|
| `src/core/constants.py` | TILE_SIZE, remove SPRITE_SCALE, SPRITE_SIZE, BOSS_SPRITE_SIZE, TILE_EMPTY | Manual edit |
| `assets/entity-schema.json` | version, grid_size, tile_coords description, variable_rooms_note | Manual edit |
| `export_tilemap_csv.py` | tiles-per-row constant (32 -> 16), comment update | Manual edit |
| `tests/test_sprite_scale.py` | Replace all assertions with new contract | Manual rewrite |
| `tests/test_schema.py` | test_schema_version_is_1_0_0 -> assert v2.0.0 | Manual edit |
| `tests/test_screen_constants.py` | No change needed -- tile alignment checks pass with TILE_SIZE=16 (320%16==0, 176%16==0) | Auto-pass |
| `PML-to-LDtk Converter.md` | Tile size 8->16, room tiles 40x22->20x11, tiles-per-row references | Manual edit |

### Files NOT Affected (Important Boundaries)

These files import TILE_SIZE or SPRITE_SIZE but require NO code changes because they reference by name, not value:

| File | Why No Change Needed |
|------|---------------------|
| `src/level/map.py` | Uses `TILE_SIZE` by name in `int(x // TILE_SIZE)` -- automatically correct |
| `src/core/sprite_utils.py` | Imports SPRITE_SIZE/BOSS_SPRITE_SIZE by name -- automatically correct |
| `src/entities/player.py` | Uses TILE_SIZE for snap math by name |
| `src/entities/boss.py` | Uses BOSS_SPRITE_SIZE by name |
| `src/entities/enemies.py` | Uses TILE_SIZE and SPRITE_SIZE by name |
| `src/entities/slime.py` | Uses TILE_SIZE and SPRITE_SIZE by name |
| `src/entities/items.py` | Uses SPRITE_SIZE by name |
| `src/entities/effects.py` | Uses SPRITE_SIZE by name |
| `src/entities/projectile.py` | Uses TILE_SIZE and SPRITE_SIZE by name |

### Anti-Patterns to Avoid
- **Hardcoding tile counts:** Do not add `ROOM_TILES_W = 20` or `ROOM_TILES_H = 11` as constants. Per D-01, tile counts are always derived: `VIEWPORT_W // TILE_SIZE`.
- **Leaving SPRITE_SCALE as 1:** Do not set SPRITE_SCALE = 1 "for compatibility." D-02 says delete it entirely.
- **Updating tile_coords values:** Per D-06, the actual coordinate pairs in tile_coords stay unchanged. Only the description text changes. Phase 21 handles the tileset migration.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Tile count computation | Named constants ROOM_W_TILES | `VIEWPORT_W // TILE_SIZE` inline | D-01 locked decision -- derive, don't declare |

## Common Pitfalls

### Pitfall 1: TILE_EMPTY Rendering Corruption
**What goes wrong:** If TILE_EMPTY is set incorrectly, the tilemap clear loop in map.py line 52-54 fills every cell with a visible tile instead of empty space, causing full-screen garbage rendering.
**Why it happens:** The sentinel must point to a genuinely empty/transparent tile in the image bank. At 16px grid on a 256x256 bank, the bottom-right tile is (15, 15), not (31, 31).
**How to avoid:** Verify the math: 256 / 16 = 16 tiles per axis, 0-indexed = max index 15. So (15, 15) is correct.
**Warning signs:** Full-screen tile garbage on room load.

### Pitfall 2: test_schema.py Version Assertion
**What goes wrong:** test_schema_version_is_1_0_0 (line 26-29 of test_schema.py) asserts `schema["version"] == "1.0.0"`. After bumping to v2.0.0, this test fails.
**Why it happens:** Easy to forget when focused on test_sprite_scale.py.
**How to avoid:** Update the assertion to `"2.0.0"` in the same task that bumps the schema version.

### Pitfall 3: export_tilemap_csv.py Comment Drift
**What goes wrong:** The script has a comment `# 320 / 8 = 40 tiles` on line 22. If the comment is not updated, future readers are confused.
**How to avoid:** Update both the computation and the comment: `# 320 / 16 = 20 tiles` and `# 256 / 16 = 16 tiles per row`.

### Pitfall 4: PML-to-LDtk Converter.md Stale References
**What goes wrong:** This markdown file references "Tile size 8px" and "40x22 tiles" in multiple places. If not updated, the converter team gets wrong specs.
**How to avoid:** Update all occurrences: tile size to 16px, standard room tiles to 20x11, tiles-per-row from 32 to 16, variable room examples (40x44 -> 20x22, 80x22 -> 40x11).

### Pitfall 5: SPRITE_SCALE Import Elsewhere
**What goes wrong:** Some file outside `src/` or `tests/` might import SPRITE_SCALE.
**Why it happens:** Grep might miss dynamic imports or non-.py files.
**How to avoid:** After deleting SPRITE_SCALE, run `pytest` -- any remaining import will produce ImportError. The D-09 test explicitly asserts SPRITE_SCALE is not importable.

## Code Examples

### New constants.py (Grid Section)

```python
# Tile Constants
TILE_SIZE = 16  # Base tile grid size (16x16 pixels)

# Screen / Display (D-01, D-02, D-08)
SCREEN_W = 320       # Full pyxel window width
SCREEN_H = 192       # Full pyxel window height
VIEWPORT_W = 320     # Playable area width (same as screen)
VIEWPORT_H = 176     # Playable area height (above HUD)
HUD_H = 16           # HUD strip height at bottom of screen

# Culling margin for off-screen entity despawn (boss, projectiles)
CULL_MARGIN = 16     # Extra pixels beyond viewport before culling

# Sprite Dimensions (Phase 20: direct values, no SPRITE_SCALE indirection)
SPRITE_SIZE = 16       # Standard entity visual dimensions (= TILE_SIZE)
BOSS_SPRITE_SIZE = 32  # Boss entity visual dimensions (= 2 * TILE_SIZE)

TILE_EMPTY = (15, 15)  # Empty tile sentinel: bottom-right of 256x256 bank at 16px grid
```

### New test_sprite_scale.py (Complete Replacement)

```python
"""Tests for Phase 20 grid constants contract (replaces Phase 13 sprite scale tests)."""
import pytest


def test_tile_size_is_16():
    from src.core.constants import TILE_SIZE
    assert TILE_SIZE == 16, "TILE_SIZE must be 16 (16x16 base grid)"


def test_sprite_size_is_16():
    from src.core.constants import SPRITE_SIZE
    assert SPRITE_SIZE == 16, "SPRITE_SIZE must be 16 (native 16x16 sprites)"


def test_boss_sprite_size_is_32():
    from src.core.constants import BOSS_SPRITE_SIZE
    assert BOSS_SPRITE_SIZE == 32, "BOSS_SPRITE_SIZE must be 32 (2x TILE_SIZE)"


def test_sprite_scale_removed():
    """SPRITE_SCALE must no longer be importable from constants."""
    with pytest.raises(ImportError):
        from src.core.constants import SPRITE_SCALE


def test_tile_empty_updated():
    from src.core.constants import TILE_EMPTY
    assert TILE_EMPTY == (15, 15), "TILE_EMPTY must be (15, 15) for 16px grid"
```

### Updated export_tilemap_csv.py (Key Lines)

```python
width = VIEWPORT_W // TILE_SIZE   # 320 / 16 = 20 tiles
height = VIEWPORT_H // TILE_SIZE  # 176 / 16 = 11 tiles

# ...

# 256 pixels / 16 = 16 tiles per row in the tileset
tile_id = v * 16 + u
```

### Updated entity-schema.json variable_rooms_note

```json
"variable_rooms_note": "Rooms can be any multiple of grid_size. Standard rooms are 320x176 (20x11 tiles). Large rooms use multiples like 320x352 (20x22 tiles) for vertical shafts or boss arenas."
```

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | None (default discovery) |
| Quick run command | `python -m pytest tests/test_sprite_scale.py tests/test_schema.py tests/test_screen_constants.py -x -q` |
| Full suite command | `python -m pytest tests/ -x -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| GRID-01 | TILE_SIZE == 16 | unit | `python -m pytest tests/test_sprite_scale.py::test_tile_size_is_16 -x` | Needs rewrite (Wave 0) |
| GRID-02 | SPRITE_SCALE not importable | unit | `python -m pytest tests/test_sprite_scale.py::test_sprite_scale_removed -x` | Needs rewrite (Wave 0) |
| GRID-03 | SPRITE_SIZE==16, BOSS_SPRITE_SIZE==32, TILE_EMPTY==(15,15) | unit | `python -m pytest tests/test_sprite_scale.py -x` | Needs rewrite (Wave 0) |
| GRID-04 | Room dimensions 20x11 (320/16, 176/16) | unit | `python -m pytest tests/test_screen_constants.py -x` | Exists (tile alignment tests pass automatically) |
| LDTK-01 | entity-schema.json grid_size == 16 | unit | `python -m pytest tests/test_schema.py -x` | Needs new assertion |
| LDTK-05 | Schema version == 2.0.0 | unit | `python -m pytest tests/test_schema.py::test_schema_version_is_1_0_0 -x` | Exists (needs value update) |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_sprite_scale.py tests/test_schema.py tests/test_screen_constants.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_sprite_scale.py` -- full rewrite to new contract (GRID-01, GRID-02, GRID-03)
- [ ] `tests/test_schema.py::test_schema_version_is_1_0_0` -- update assertion from "1.0.0" to "2.0.0"
- [ ] `tests/test_schema.py` -- add test for `grid_size == 16` (LDTK-01)

## Open Questions

1. **draw_sprite offset math after Phase 22**
   - What we know: Currently collision boxes are 8x8 and visuals are 16x16, producing an offset. Phase 22 will make collision = visual = 16x16, eliminating the offset.
   - What's unclear: Nothing for this phase -- draw_sprite uses SPRITE_SIZE by name so it auto-adjusts.
   - Recommendation: No action needed in Phase 20. Phase 22 will address collision box resizing.

2. **Bat start_y offset**
   - What we know: `enemies.py:104` has `self.start_y = y + TILE_SIZE` to offset bats down 1 tile from ceiling. With TILE_SIZE changing from 8 to 16, bats will offset 16px instead of 8px.
   - What's unclear: Whether this produces correct behavior with the new grid.
   - Recommendation: This is an entity alignment concern (Phase 22 scope, ENT-02). Flag but do not fix in Phase 20.

## Sources

### Primary (HIGH confidence)
- `src/core/constants.py` -- current constant definitions (lines 1-19)
- `assets/entity-schema.json` -- current schema (version 1.0.0, grid_size 8)
- `tests/test_sprite_scale.py` -- current test assertions
- `tests/test_schema.py` -- current schema test assertions
- `export_tilemap_csv.py` -- current CSV export logic
- `PML-to-LDtk Converter.md` -- current converter reference doc

### Secondary (MEDIUM confidence)
- `.planning/phases/20-grid-constants-schema-metadata/20-CONTEXT.md` -- locked decisions D-01 through D-09
- `.planning/REQUIREMENTS.md` -- GRID-01 through GRID-04, LDTK-01, LDTK-05

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no libraries, pure constant changes
- Architecture: HIGH -- complete file audit done, all affected files identified
- Pitfalls: HIGH -- verified TILE_EMPTY math, identified test_schema.py version assertion, export script tiles-per-row

**Research date:** 2026-04-08
**Valid until:** 2026-05-08 (stable -- no external dependency drift possible)
