# Phase 17: Unified Schema Definition - Research

**Researched:** 2026-04-05
**Domain:** JSON schema design, Pyxel tilemap data model, biome tileset architecture
**Confidence:** HIGH

## Summary

Phase 17 extends the existing `assets/entity-schema.json` (v0.6.0) to include tile-type visual definitions (IntGrid-to-tileset-coordinate mappings), layer definitions with z-order and parallax, and a per-biome tileset structure. The schema remains a plain JSON data file -- not a JSON Schema validator -- that serves as the single source of truth for both tiles and entities.

The current schema already has a well-structured `intgrid.values` section defining tile behaviors. The key addition is a top-level `biomes` key that maps biome names to their visual definitions: tileset image path, IntGrid-value-to-tile-coordinate mappings, and ordered layer definitions. This cleanly separates "what tiles DO" (intgrid) from "what tiles LOOK LIKE" (biomes).

The tileset file `assets/sprites/tiles.png` must be copied (not moved -- see Pitfall 2) to `assets/tilesets/cavern.png`, and the `SPRITE_MANIFEST` in `main.py` must be updated to reference the new path. The `assets/tilesets/` directory does not exist yet and must be created.

**Primary recommendation:** Extend entity-schema.json with a `biomes` key containing `cavern` as the only biome, populated from the 9 IntGrid-to-tile mappings currently hardcoded in `map.py` lines 35-45 and `constants.py` lines 19-32. Move tiles.png to assets/tilesets/cavern.png. Bump version to 1.0.0.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** `intgrid.values` stays behavior-only (name, behavior, broken_by) -- shared across all biomes
- **D-02:** New top-level `biomes` key holds per-biome visual definitions: tileset image path, IntGrid-value-to-tile-coordinate mappings, and layer definitions
- **D-03:** Separation of concerns: `intgrid` = what tiles DO, `biomes` = what tiles LOOK LIKE
- **D-04:** Tile coordinates use `[col, row]` grid format matching existing constants.py convention -- e.g., `[0, 1]` means column 0, row 1 on the 8px tile grid
- **D-05:** Coordinates map directly to `pyxel.tilemaps[].pset(tx, ty, (u, v))` with zero conversion
- **D-06:** One tileset PNG per biome (e.g., `cavern.png`, `jungle.png`)
- **D-07:** Tileset images live in `assets/tilesets/` subfolder -- current `tiles.png` moves to `assets/tilesets/cavern.png`
- **D-08:** Schema references tileset via relative path in each biome's definition
- **D-09:** Layers defined per-biome as an ordered list with: name, tilemap index, z-order, scroll rate
- **D-10:** Cavern starts with 2 layers: background (tilemap 1, z: -1, scroll: 0.5) and terrain (tilemap 0, z: 0, scroll: 1.0)
- **D-11:** Foreground layer deferred -- can be added to cavern later without schema changes
- **D-12:** Biomes are fully self-contained -- no inheritance or base/default merging
- **D-13:** Each biome defines its own complete tile_coords + layers + tileset path
- **D-14:** If biomes share tile coords, they duplicate them (simple > clever for prototype)
- **D-15:** Bump schema version to v1.0.0 -- marks the unified schema milestone (tiles + entities in one file)
- **D-16:** IntGrid values 0 (empty) and 4 (deprecated) are excluded from biome tile_coords -- absence means no visual tile
- **D-17:** `TILE_EMPTY = (31, 31)` stays as a code-level constant for tile clearing operations
- **D-18:** IntGrid value 4 can be reclaimed for a new purpose in a future phase if needed

### Claude's Discretion
- Exact key naming within the schema (e.g., `tile_coords` vs `tiles`, `scroll` vs `scroll_rate`) -- as long as the structure matches the decisions above
- Whether to add a `$schema` self-reference or JSON Schema validation for the new biomes section
- How to handle the `reserved_ranges` section in intgrid -- update or leave as-is

### Deferred Ideas (OUT OF SCOPE)
- IntGrid value 4 reclamation -- find a new purpose for the deprecated value (future phase)
- Foreground layer for cavern biome -- add when foreground tile art exists
- Biome inheritance/defaults -- revisit if biome count grows and duplication becomes painful
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SCHEMA-01 | Unified JSON schema file defines tile types (IntGrid values, tileset coordinates) and entity types (sprite bank, sprite coordinates) in one place | Existing entity-schema.json extended with `biomes` key; 9 IntGrid-to-tile mappings from constants.py/map.py migrated into `cavern.tile_coords` |
| SCHEMA-04 | Schema structure supports per-biome tileset sections with a default biome populated | `biomes.cavern` section with self-contained tileset path, tile_coords, and layers; extensible for future biomes |
| TILE-05 | Schema defines tilemap layers with z-order and optional parallax scroll rate | Per-biome `layers` array with name, tilemap index, z-order, and scroll rate fields |
</phase_requirements>

## Standard Stack

This phase is purely schema/data work with a file move. No new libraries needed.

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Python json module | stdlib | Read/validate schema in tests | Built-in, no dependencies |
| pytest | 9.0.2 | Schema validation tests | Already used by project |

### Supporting
| Tool | Purpose | When to Use |
|------|---------|-------------|
| git mv | Move tiles.png to new location | Preserves file history |
| shutil (stdlib) | Copy file if git mv is insufficient | Fallback for file operations |

## Architecture Patterns

### Current Schema Structure (v0.6.0)
```
entity-schema.json
  $schema
  title, description, version, updated
  level { ... }
  intgrid { values: { ... }, reserved_ranges: { ... } }
  entities { PlayerStart, Door, Snail, ... }
  converter_mapping { direct, category, ... }
  pivot_convention { ... }
  simplified_export { ... }
```

### Target Schema Structure (v1.0.0)
```
entity-schema.json
  $schema
  title, description, version, updated
  level { ... }
  intgrid { values: { ... }, reserved_ranges: { ... } }     # UNCHANGED
  biomes {                                                     # NEW
    cavern {
      tileset: "assets/tilesets/cavern.png"
      tile_coords: { "1": [0, 1], "2": [1, 1], ... }
      layers: [
        { name: "bg", tilemap: 1, z: -1, scroll: 0.5 },
        { name: "terrain", tilemap: 0, z: 0, scroll: 1.0 }
      ]
    }
  }
  entities { ... }                                             # UNCHANGED
  converter_mapping { ... }                                    # UNCHANGED
  pivot_convention { ... }                                     # UNCHANGED
  simplified_export { ... }                                    # UNCHANGED
```

### Pattern 1: IntGrid Value to Tile Coordinate Mapping

The complete mapping extracted from `constants.py` (lines 19-32) and `map.py` (lines 35-45):

| IntGrid Value | Name | Constant | Tile Coord (col, row) |
|---------------|------|----------|----------------------|
| 0 | empty | TILE_EMPTY | (31, 31) -- code constant only, NOT in schema |
| 1 | solid | TILE_SOLID | (0, 1) |
| 2 | hazard | TILE_HAZARD | (1, 1) |
| 3 | soft_block | TILE_DESTRUCTIBLE | (2, 1) |
| 4 | reserved | -- | EXCLUDED (deprecated, D-16) |
| 5 | switch | TILE_SWITCH | (5, 1) |
| 6 | water | TILE_WATER | (9, 1) |
| 7 | acid | TILE_ACID | (10, 1) |
| 8 | lava | TILE_LAVA | (11, 1) |
| 11 | cracked_h | TILE_CRACKED_H | (7, 1) |
| 12 | cracked_v | TILE_CRACKED_V | (8, 1) |

**Total: 9 entries in biome tile_coords** (values 1, 2, 3, 5, 6, 7, 8, 11, 12).

### Pattern 2: Layer Definition Model

Per D-09/D-10, cavern biome layers:

```json
"layers": [
  { "name": "bg",      "tilemap": 1, "z": -1, "scroll": 0.5 },
  { "name": "terrain", "tilemap": 0, "z": 0,  "scroll": 1.0 }
]
```

- `tilemap` = Pyxel tilemap index (0-7 available, game currently uses tilemap 0 only)
- `z` = rendering order (lower = further back)
- `scroll` = parallax scroll rate (1.0 = camera speed, 0.5 = half speed for depth effect)
- Array order defines layer ordering; `z` makes it explicit for consumers

### Pattern 3: File Organization After Phase

```
assets/
  entity-schema.json          # v1.0.0 with biomes section
  tilesets/
    cavern.png                 # Copied from assets/sprites/tiles.png
  sprites/
    tiles.png                  # KEPT (still referenced by SPRITE_MANIFEST)
    player.png, slime.png ...  # Unchanged
```

### Anti-Patterns to Avoid
- **Biome inheritance/merging:** D-12/D-14 explicitly reject this. Each biome is self-contained, even if it means duplication.
- **Storing visual coords in intgrid.values:** D-01/D-03 mandate behavior and visuals are separate. Never add tile coordinates to the intgrid section.
- **Using pixel coordinates instead of grid coordinates:** D-04 specifies `[col, row]` grid format. Never use pixel offsets.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON validation | Custom validation logic | pytest assertions comparing schema against known IntGrid values | Tests catch drift; no runtime validator needed for a prototype |
| Schema documentation | Separate documentation file | `description` and `note` fields inline in schema | Follows existing pattern in entity-schema.json |

## Common Pitfalls

### Pitfall 1: Missing IntGrid Values
**What goes wrong:** An IntGrid value used in levels has no tile_coords entry, causing invisible tiles at runtime.
**Why it happens:** Forgetting an entry during manual migration from constants.py to schema.
**How to avoid:** Write a test that cross-references all IntGrid values in `intgrid.values` (excluding 0 and 4) against `biomes.cavern.tile_coords`. Any value with behavior != "none" must have a tile coord.
**Warning signs:** Tiles render as empty/transparent in-game despite IntGrid.csv having non-zero values.

### Pitfall 2: Destructive File Move Breaks SPRITE_MANIFEST
**What goes wrong:** Moving (git mv) `assets/sprites/tiles.png` to `assets/tilesets/cavern.png` breaks the SPRITE_MANIFEST entry `"tiles": (0, 0, 0, "assets/sprites/tiles.png")` in main.py, causing a crash at startup.
**Why it happens:** D-07 says "tiles.png moves to assets/tilesets/cavern.png" but the game loads tiles via SPRITE_MANIFEST, not via the schema (yet -- that is Phase 18).
**How to avoid:** Two options: (a) Copy the file to the new location AND update SPRITE_MANIFEST to point to the new path, or (b) Copy to the new location and keep the original in place. Option (a) is cleaner -- the schema's tileset path and SPRITE_MANIFEST path match. The old `assets/sprites/tiles.png` can be removed once confirmed working.
**Warning signs:** Game fails to start with "file not found" error on tiles.png.

### Pitfall 3: Breaking the pml-to-ldtk Converter
**What goes wrong:** Schema changes break the converter's ability to read entity-schema.json.
**Why it happens:** Adding new top-level keys or restructuring existing sections.
**How to avoid:** This phase only ADDS a new `biomes` top-level key and bumps the version. The `converter_mapping`, `entities`, `intgrid`, and all other existing sections remain unchanged. The converter should ignore unknown keys.
**Warning signs:** pml-to-ldtk errors after schema update.

### Pitfall 4: Coordinate Format Mismatch
**What goes wrong:** Schema stores coordinates as `[col, row]` but code tries to use them as `(row, col)` or pixel offsets.
**Why it happens:** Confusion between grid coordinates and pixel coordinates, or between (x, y) and (u, v) conventions.
**How to avoid:** Document the convention in the schema description. The `[col, row]` format maps directly to `pyxel.tilemaps[].pset(tx, ty, (col, row))` per D-05.
**Warning signs:** Tiles render with wrong graphics (swapped or offset).

### Pitfall 5: Schema Key Type for IntGrid Values
**What goes wrong:** JSON requires string keys for objects, but IntGrid values are integers. Consumer code may compare `int` against `str` keys.
**Why it happens:** JSON spec mandates string keys; the intgrid.values section already uses string keys ("1", "2", etc.).
**How to avoid:** Use string keys in `tile_coords` (matching existing `intgrid.values` convention). Consumer code must convert IntGrid CSV values to strings for lookup, or convert keys to ints at load time. Document this in the schema.
**Warning signs:** KeyError when looking up tile coordinates.

## Code Examples

### Complete Biomes Section (Target Output)

```json
"biomes": {
  "description": "Per-biome visual definitions. Each biome maps IntGrid values to tileset coordinates and defines rendering layers.",
  "cavern": {
    "tileset": "assets/tilesets/cavern.png",
    "tile_coords": {
      "1":  [0, 1],
      "2":  [1, 1],
      "3":  [2, 1],
      "5":  [5, 1],
      "6":  [9, 1],
      "7":  [10, 1],
      "8":  [11, 1],
      "11": [7, 1],
      "12": [8, 1]
    },
    "layers": [
      { "name": "bg",      "tilemap": 1, "z": -1, "scroll": 0.5 },
      { "name": "terrain", "tilemap": 0, "z": 0,  "scroll": 1.0 }
    ]
  }
}
```

### Updated SPRITE_MANIFEST Entry

```python
# main.py - update tiles path to match new tilesets location
SPRITE_MANIFEST = {
    "tiles":      (0, 0, 0,   "assets/tilesets/cavern.png"),
    # ... rest unchanged
}
```

### Test: Schema IntGrid Coverage

```python
import json
import pytest

def test_schema_biome_covers_all_intgrid_values():
    """Every non-empty, non-deprecated IntGrid value has a tile_coords entry."""
    with open("assets/entity-schema.json") as f:
        schema = json.load(f)
    
    excluded = {"0", "4"}  # empty and deprecated
    behavior_values = {
        k for k, v in schema["intgrid"]["values"].items()
        if k not in excluded and v.get("behavior") != "none"
    }
    
    cavern_coords = set(schema["biomes"]["cavern"]["tile_coords"].keys())
    missing = behavior_values - cavern_coords
    assert not missing, f"IntGrid values missing from cavern tile_coords: {missing}"
```

### Test: Schema Version Bump

```python
def test_schema_version_is_1_0_0():
    """Schema version bumped to 1.0.0 for unified schema milestone."""
    with open("assets/entity-schema.json") as f:
        schema = json.load(f)
    assert schema["version"] == "1.0.0"
```

### Test: Cavern Tileset File Exists

```python
import os

def test_cavern_tileset_exists():
    """Cavern tileset PNG exists at the path specified in schema."""
    with open("assets/entity-schema.json") as f:
        schema = json.load(f)
    tileset_path = schema["biomes"]["cavern"]["tileset"]
    assert os.path.exists(tileset_path), f"Tileset missing: {tileset_path}"
```

### Test: Layer Structure

```python
def test_cavern_layers_structure():
    """Cavern biome has 2 layers with required fields."""
    with open("assets/entity-schema.json") as f:
        schema = json.load(f)
    layers = schema["biomes"]["cavern"]["layers"]
    assert len(layers) == 2
    for layer in layers:
        assert "name" in layer
        assert "tilemap" in layer
        assert "z" in layer
        assert "scroll" in layer
```

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | none (default discovery) |
| Quick run command | `python -m pytest tests/test_schema.py -x` |
| Full suite command | `python -m pytest tests/ -x` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SCHEMA-01 | Schema has both tile coords and entity defs in one file | unit | `python -m pytest tests/test_schema.py::test_schema_has_tiles_and_entities -x` | Wave 0 |
| SCHEMA-04 | Schema has per-biome tileset sections with cavern populated | unit | `python -m pytest tests/test_schema.py::test_schema_biome_covers_all_intgrid_values -x` | Wave 0 |
| TILE-05 | Schema defines tilemap layers with z-order and scroll | unit | `python -m pytest tests/test_schema.py::test_cavern_layers_structure -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_schema.py -x`
- **Per wave merge:** `python -m pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_schema.py` -- covers SCHEMA-01, SCHEMA-04, TILE-05
- No new framework install needed (pytest 9.0.2 already available)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hardcoded tile tuples in constants.py | Schema-driven tile definitions | This phase (v1.0.0) | Single source of truth for tiles + entities |
| tiles.png in sprites/ dir | Biome-specific tilesets in tilesets/ dir | This phase | Supports future multi-biome tilesets |
| No layer/parallax model | Schema-defined layers with z-order and scroll rate | This phase | Enables Phase 19 multi-layer rendering |

## Open Questions

1. **Should SPRITE_MANIFEST update happen in this phase or Phase 18?**
   - What we know: D-07 says tiles.png "moves" to assets/tilesets/cavern.png. SPRITE_MANIFEST in main.py currently points to assets/sprites/tiles.png. Phase 18 is "Schema-Driven Tile Loading" which replaces hardcoded constants.
   - What's unclear: Whether the SPRITE_MANIFEST path update is a Phase 17 concern (file move) or Phase 18 concern (code loading changes).
   - Recommendation: Update SPRITE_MANIFEST in this phase since the file physically moves. It is a one-line change that prevents breakage. Phase 18 may further restructure how tiles are loaded, but the path should be correct now.

2. **Should the old assets/sprites/tiles.png be deleted or kept?**
   - What we know: The file is being "moved" per D-07. SPRITE_MANIFEST is the only runtime consumer. Test file `test_sprite_assets.py` checks for `tiles.png` in sprites dir.
   - What's unclear: Whether keeping the old file causes confusion, or removing it breaks existing tests.
   - Recommendation: Copy to new location, update SPRITE_MANIFEST to new path, update test_sprite_assets.py to new path, then delete the old file. Clean break.

3. **Key naming for discretionary fields**
   - Recommendation: Use `tile_coords` (matches CONTEXT.md examples), `scroll` (shorter than `scroll_rate`, matches CONTEXT.md), `tileset` for the path. These match the preview structure in CONTEXT.md specifics section.

## Sources

### Primary (HIGH confidence)
- `assets/entity-schema.json` -- current v0.6.0 schema, read directly
- `src/core/constants.py` lines 19-32 -- all TILE_* constants with coordinates
- `src/level/map.py` lines 35-45 -- val_to_tile dict, the authoritative IntGrid-to-tile mapping
- `main.py` lines 138-150 -- SPRITE_MANIFEST, the tile loading path
- `.planning/phases/17-unified-schema-definition/17-CONTEXT.md` -- all locked decisions

### Secondary (MEDIUM confidence)
- `tests/test_sprite_assets.py` -- existing tests referencing tiles.png path

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new libraries, purely schema/data work
- Architecture: HIGH -- all decisions locked in CONTEXT.md, schema structure previewed
- Pitfalls: HIGH -- identified from direct code inspection of current tile loading pipeline

**Research date:** 2026-04-05
**Valid until:** 2026-05-05 (stable -- schema design, no external dependencies)
