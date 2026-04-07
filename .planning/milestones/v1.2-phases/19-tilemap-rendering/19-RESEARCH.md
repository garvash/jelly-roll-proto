# Phase 19: Tilemap Rendering - Research

**Researched:** 2026-04-06
**Domain:** LDtk autoLayerTiles parsing, Pyxel tilemap rendering, multi-layer parallax
**Confidence:** HIGH

## Summary

Phase 19 replaces the current uniform IntGrid-to-tile visual rendering with proper auto-tile visuals from the LDtk project file (`assets/output.ldtk`). The full LDtk file contains 18,094 autoLayerTiles across 18 levels with 32 unique tile source coordinates from a 96x80 tileset (`tiles.png`). All flip flags are 0 and all alpha values are 1, simplifying implementation significantly.

The simplified export (`assets/output/simplified/`) does NOT contain autoLayerTiles data -- only IntGrid.csv and basic data.json with entities. A new parser must read the full LDtk JSON to extract autoLayerTiles. The world fits within Pyxel's 256x256 tilemap (240x132 tiles used). Collision detection stays on IntGrid.csv, visual rendering moves to autoLayerTiles `src` coordinates.

**Primary recommendation:** Add a dedicated LDtk full-file parser that extracts autoLayerTiles from `assets/output.ldtk`, populates `pyxel.tilemaps[0]` with the auto-tile visuals (replacing the IntGrid-to-tile mapping for visuals), and expand the draw loop to render schema-defined layers with parallax scroll offsets.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Hybrid approach -- keep simplified export for collision/entities, add autoLayerTiles from full LDtk project file.
- **D-02:** Read autoLayerTiles from `assets/output.ldtk` (46 auto-tile rules, 26 unique tile variants, 18 levels). Not cave.ldtk.
- **D-03:** autoLayerTiles fields used: `px` (position), `src` (tileset source), `f` (flip flag), `a` (opacity). Skip tiles with `a=0`.
- **D-04:** Defer flip support. All 18,094 autoLayerTiles have `f=0`. Parse the flag but log warning if non-zero encountered.
- **D-05:** `f=1` values in cave.ldtk were artifacts -- output.ldtk has complete tileset with explicit tiles for all orientations.
- **D-06:** Build multi-layer `bltm()` rendering pipeline. Each layer drawn at `camera_x * scroll_rate` offset.
- **D-07:** Background layer (tilemap 1, scroll 0.5) is empty for now. Pipeline ready for future content.
- **D-08:** Terrain layer (tilemap 0, scroll 1.0) receives autoLayerTiles data. Primary visual layer.
- **D-09:** Layer draw order follows schema `z` values (lower z drawn first).
- **D-10:** 46 auto-tile rules and 26 tile variants in output.ldtk are complete. No procedural generation needed.
- **D-11:** Tileset uses LDtk standard auto-tile template layout (two templates stacked).
- **D-12:** `assets/tiles.png` (96x80) is canonical tileset. Target 128x128 to allow future tile types.
- **D-13:** Update schema `biomes.cavern.tileset` to reference correct tileset path.
- **D-14:** Tileset loaded into Pyxel image bank 0 (256x256 capacity, 8px grid = 32x32 tile slots).
- **D-15:** Collision uses IntGrid.csv via simplified export loader. Fully independent from visual tiles.
- **D-16:** Visual rendering uses autoLayerTiles `src` coordinates. No dependency on IntGrid-to-tile schema mappings for visuals.

### Claude's Discretion
- How to structure the LDtk full-file parser (separate module or extension of existing map.py)
- Whether to cache parsed autoLayerTiles data or re-read per room load
- Exact parallax camera offset math in the draw loop
- How to handle the tileset path update (rename, copy, or update schema reference)

### Deferred Ideas (OUT OF SCOPE)
- Background layer content (tileset art or LDtk background layer)
- Foreground parallax layer
- Tile flip support (pre-baking or per-tile blt)
- Biome-specific tileset switching (BIOME-02)
- Merging cave.ldtk and output.ldtk
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TILE-01 | Game parses autoLayerTiles array from LDtk data for each level | Full LDtk file parser for `output.ldtk` -- autoLayerTiles in IntGrid layer with `px`, `src`, `f`, `a` fields. Simplified export lacks this data. |
| TILE-02 | AutoLayerTiles rendered on pyxel.tilemaps[0] for terrain visuals | `pset(tx, ty, (src_x//8, src_y//8))` pattern proven in existing `load_from_ldtk()` line 350-356. 32 unique tile variants provide edge/corner/inner variation. |
| TILE-03 | Tile flip flags handled correctly | All 18,094 tiles have `f=0`. Parse flag, log warning if non-zero. No active flip handling needed per D-04. |
| TILE-04 | Collision uses IntGrid.csv, visual uses autoLayerTiles -- cleanly separated | Collision stays in `load_from_ldtk_simplified()` with `collision_data` dict. Visuals overwritten by autoLayerTiles after collision load. |
| TILE-06 | Multiple tilemap layers at independent scroll rates | Schema defines 2 layers (bg: tilemap 1, scroll 0.5; terrain: tilemap 0, scroll 1.0). `bltm()` calls loop over layers with camera offset = `cam * scroll`. |
</phase_requirements>

## Architecture Patterns

### Recommended Approach: Extend map.py with Full LDtk Parser

**Recommendation:** Add a new method `load_autotiles_from_ldtk(ldtk_path)` to `LevelMap` rather than a separate module. Rationale: it shares the same tilemap population pattern (`pset`), needs access to `self.tilemap_id`, and the existing `load_from_ldtk()` method at line 318 already demonstrates the pattern.

### Data Flow

```
Startup:
  1. schema.init()                          -- loads layer defs, tileset path
  2. _load_sprites()                        -- loads tileset into bank 0
  3. load_from_ldtk_simplified(root_dir)    -- loads collision_data + entities + basic tile visuals
  4. load_autotiles_from_ldtk(ldtk_path)    -- NEW: overwrites visual tiles with auto-tile data
  
Draw loop (per frame):
  for layer in sorted(schema.get_layers(), key=lambda l: l["z"]):
      cam_offset_x = offset_x * layer["scroll"]
      cam_offset_y = offset_y * layer["scroll"]
      pyxel.camera(cam_offset_x, cam_offset_y)
      pyxel.bltm(0, 0, layer["tilemap"], 0, 0, 2048, 2048)
  pyxel.camera(offset_x, offset_y)  -- restore for entities
```

### LDtk Full File Structure (Verified)

```
output.ldtk (JSON):
  levels[]:                          -- 18 levels
    identifier: "Level_0"
    worldX, worldY: world-space px   -- need same origin normalization as simplified loader
    pxWid, pxHei: level dimensions
    layerInstances[]:                -- 2 layers per level (Entities, IntGrid)
      __identifier: "IntGrid"
      __type: "IntGrid"
      __gridSize: 8
      __tilesetRelPath: "tiles.png"
      autoLayerTiles[]:              -- THE DATA WE NEED
        px: [x, y]                   -- pixel position within level (not world-space!)
        src: [sx, sy]                -- pixel coords into tileset
        f: 0                         -- flip flag (always 0 in this dataset)
        t: int                       -- tile ID (internal)
        d: [ruleId, cellIdx]         -- rule debug info (ignore)
        a: 1                         -- opacity (always 1 in this dataset)
```

### Critical: Coordinate Normalization

The `px` values in autoLayerTiles are **level-local** pixel coordinates (0-based within each level). The `worldX`/`worldY` on the level object gives the world-space offset. The same origin normalization used in `load_from_ldtk_simplified()` (lines 57-72) must be applied:

```python
# Same pattern as simplified loader
origin_x = (min_wx // 8) * 8  # snap to tile boundary
origin_y = (min_wy // 8) * 8

# Per level:
world_x = level["worldX"] - origin_x
world_y = level["worldY"] - origin_y

# Per autoLayerTile:
px_world_x = world_x + tile["px"][0]  # level-local to world
px_world_y = world_y + tile["px"][1]
tx = px_world_x // 8  # pixel to tile coords
ty = px_world_y // 8
u = tile["src"][0] // 8  # tileset pixel to tile coords
v = tile["src"][1] // 8
pyxel.tilemaps[0].pset(tx, ty, (u, v))
```

### World Bounds (Verified from output.ldtk)

| Property | Value |
|----------|-------|
| World pixel range | (0, -176) to (1920, 880) |
| World size | 1920 x 1056 pixels |
| Tile grid size | 240 x 132 tiles |
| Pyxel tilemap capacity | 256 x 256 tiles |
| Fits? | Yes (93% x, 52% y) |
| Total autoLayerTiles | 18,094 |
| All flip flags | 0 (confirmed) |
| All alpha values | 1 (confirmed) |
| Unique src coordinates | 32 |
| Tileset referenced | tiles.png (uid 64, 96x80, 8px grid) |

### Tileset Path Update Strategy

**Current state:** Schema says `assets/tilesets/cavern.png` (256x256). AutoLayerTiles reference `tiles.png` (96x80). SPRITE_MANIFEST loads from schema path into bank 0.

**Recommendation:** Update schema `biomes.cavern.tileset` to `assets/tiles.png`. This flows through `schema.get_tileset_path()` to `_load_sprites()` automatically. The old cavern.png has IntGrid-mapped tiles at specific coordinates that are still used by `_val_to_tile` for collision-visual fallback (e.g., `restore_tile()` uses schema tile coords). Verify that the IntGrid tile coords in the schema (`tile_coords`) match positions in tiles.png, or update them.

**Important check:** The schema `tile_coords` maps IntGrid values to `(col, row)` in the tileset. These are currently designed for cavern.png layout. If tiles.png has different layout, tile_coords must be updated. However, since autoLayerTiles provide explicit `src` coordinates, the only code paths that still use `tile_coords` are:
1. `restore_tile()` -- restoring broken destructible blocks visually
2. The initial simplified loader visual tile placement (which gets overwritten by autoLayerTiles)

So tile_coords accuracy matters only for dynamic tile restoration.

### Parallax Camera Math

The current single `bltm()` call at line 791 uses global camera state set by `pyxel.camera()`. For parallax, each layer needs its own camera offset:

```python
# Current (single layer):
pyxel.camera(offset_x, offset_y)
pyxel.bltm(0, 0, 0, 0, 0, 2048, 2048)

# New (multi-layer):
layers = schema.get_layers()
for layer in sorted(layers, key=lambda l: l["z"]):
    scroll = layer["scroll"]
    pyxel.camera(offset_x * scroll, offset_y * scroll)
    pyxel.bltm(0, 0, layer["tilemap"], 0, 0, 2048, 2048)
# Restore camera for entity drawing at 1.0 scroll rate
pyxel.camera(offset_x, offset_y)
```

**Note:** `pyxel.bltm(x, y, tm, u, v, w, h, colkey)` -- the `tm` parameter selects which tilemap to render. The `colkey` parameter can be used to make a specific color transparent (not needed for terrain but may help with bg layer transparency).

### Pyxel API (Verified)

| API | Signature | Purpose |
|-----|-----------|---------|
| `pyxel.bltm()` | `bltm(x, y, tm, u, v, w, h, colkey=None, rotate=None, scale=None)` | Draw tilemap `tm` |
| `pyxel.tilemaps[]` | 8 tilemaps available (indices 0-7) | Schema uses 0 (terrain) and 1 (bg) |
| `tilemap.pset()` | `pset(x, y, tile)` where tile is `(u, v)` tuple | Set tile at position |
| `tilemap.pget()` | `pget(x, y)` returns `(u, v)` | Get tile at position |
| `tilemap.imgsrc` | Property -- which image bank the tilemap reads from | Set to 0 for both layers |
| `pyxel.camera()` | `camera(x, y)` | Set camera offset for all drawing |
| Pyxel version | 2.8.7 | Current installed version |

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Auto-tile rule evaluation | Procedural edge/corner detection | LDtk's pre-computed autoLayerTiles | 46 rules already evaluated by LDtk. `src` coords point directly to correct tile variant. |
| Tile flip rendering | Per-tile blt with flip math | Skip -- all `f=0` | No flipped tiles in dataset. Log warning for future detection. |
| Layer ordering | Manual z-sort logic | `sorted(layers, key=z)` from schema | Schema already defines z-order. |
| Coordinate normalization | New world-origin logic | Existing pattern from `load_from_ldtk_simplified()` lines 57-72 | Same min_wx/min_wy origin snapping. |

## Common Pitfalls

### Pitfall 1: Visual Tile Overwrite Order
**What goes wrong:** autoLayerTiles are loaded but then `load_from_ldtk_simplified()` overwrites them with IntGrid-mapped tiles.
**Why it happens:** Calling order matters -- simplified loader sets visual tiles via `_val_to_tile`.
**How to avoid:** Load autoLayerTiles AFTER the simplified loader, so auto-tile visuals overwrite the schema-mapped visuals. Collision data in `collision_data` dict is unaffected by visual tile changes.
**Warning signs:** Terrain looks uniform/flat despite loading autoLayerTiles.

### Pitfall 2: Origin Mismatch Between Loaders
**What goes wrong:** autoLayerTiles appear shifted relative to collision data.
**Why it happens:** Full LDtk file uses `worldX`/`worldY` while simplified export uses `data.json` `x`/`y`. These SHOULD be the same values, but origin normalization must match exactly.
**How to avoid:** Use the identical origin calculation (min world coords, snap to tile boundary) for both loaders. Consider sharing the computed origin or re-using the level_data_cache.
**Warning signs:** Visual tiles are offset by a consistent amount from where collision happens.

### Pitfall 3: autoLayerTile px is Level-Local, Not World-Space
**What goes wrong:** Tiles render at wrong positions because `px` values are treated as world-space.
**Why it happens:** `px: [x, y]` in autoLayerTiles is relative to the level's top-left corner, NOT world origin.
**How to avoid:** Always add `level.worldX` + `tile.px[0]` before applying origin normalization.
**Warning signs:** All tiles from different levels overlap in the top-left area.

### Pitfall 4: Background Tilemap Not Cleared
**What goes wrong:** Background layer (tilemap 1) renders garbage or leftover data.
**Why it happens:** Pyxel tilemaps may contain default/uninitialized data.
**How to avoid:** Clear tilemap 1 with TILE_EMPTY before rendering. Since D-07 says bg layer is empty, it just needs to be cleared once.
**Warning signs:** Random tile artifacts behind the terrain layer.

### Pitfall 5: Schema tileset_path Test Breakage
**What goes wrong:** Existing test `test_cavern_tileset_path_in_schema` (line 78) and `test_tileset_path` (line 190) fail.
**Why it happens:** Changing schema `biomes.cavern.tileset` from `assets/tilesets/cavern.png` to `assets/tiles.png` breaks these assertions.
**How to avoid:** Update tests alongside schema change.
**Warning signs:** Test suite fails on schema tests.

### Pitfall 6: restore_tile() Visual Mismatch
**What goes wrong:** When a destructible block regenerates, it restores to the old IntGrid-mapped visual instead of the auto-tile visual.
**Why it happens:** `restore_tile()` uses `_val_to_tile` which maps to generic tile coords, not the specific auto-tile variant that was there.
**How to avoid:** Accept this as a known limitation for now -- restored blocks will show a generic tile. The collision behavior is correct regardless. To fix properly would require caching the original auto-tile visual per tile position.
**Warning signs:** Regenerated blocks look different from surrounding terrain.

### Pitfall 7: Entity Drawing Camera State
**What goes wrong:** Entities render at wrong positions after parallax layer rendering.
**Why it happens:** The parallax loop changes `pyxel.camera()` to each layer's scroll rate. If camera isn't restored to 1.0 scroll before entity drawing, entities shift.
**How to avoid:** After the layer loop, explicitly restore `pyxel.camera(offset_x, offset_y)` before drawing entities.
**Warning signs:** Entities appear shifted, especially at camera extremes far from origin.

## Code Examples

### Parsing autoLayerTiles from output.ldtk

```python
# Source: Verified against assets/output.ldtk structure
import json

def load_autotiles_from_ldtk(ldtk_path, tilemap_id=0):
    """Load autoLayerTiles from full LDtk project file into Pyxel tilemap."""
    with open(ldtk_path) as f:
        data = json.load(f)
    
    levels = data["levels"]
    grid_size = 8  # Verified: __gridSize = 8 in output.ldtk
    
    # Pass 1: Find world origin (same normalization as simplified loader)
    min_wx = min(lv["worldX"] for lv in levels)
    min_wy = min(lv["worldY"] for lv in levels)
    origin_x = (min_wx // grid_size) * grid_size
    origin_y = (min_wy // grid_size) * grid_size
    
    tiles_loaded = 0
    for level in levels:
        world_x = level["worldX"] - origin_x
        world_y = level["worldY"] - origin_y
        
        for layer in level.get("layerInstances", []):
            for tile in layer.get("autoLayerTiles", []):
                if tile.get("a", 1) == 0:
                    continue  # Skip transparent tiles (D-03)
                
                # Log warning for non-zero flip flags (D-04)
                if tile.get("f", 0) != 0:
                    print(f"WARNING: Non-zero flip flag {tile['f']} at {tile['px']}")
                
                # px is level-local, convert to world tile coords
                px_x = world_x + tile["px"][0]
                px_y = world_y + tile["px"][1]
                tx = px_x // grid_size
                ty = px_y // grid_size
                
                # src is tileset pixel coords, convert to tile coords
                u = tile["src"][0] // grid_size
                v = tile["src"][1] // grid_size
                
                pyxel.tilemaps[tilemap_id].pset(tx, ty, (u, v))
                tiles_loaded += 1
    
    return tiles_loaded
```

### Multi-Layer Parallax Draw Loop

```python
# Source: Pyxel 2.8.7 API + schema layer definitions
from src.core import schema

def _draw_game_world(self):
    pyxel.clip(0, 0, VIEWPORT_W, VIEWPORT_H)
    
    offset_x = self.cam_x
    offset_y = self.cam_y
    if self.shake_timer > 0:
        offset_x += pyxel.rndi(-2, 2)
        offset_y += pyxel.rndi(-2, 2)
    
    # Draw tilemap layers in z-order with parallax
    layers = schema.get_layers()
    for layer in sorted(layers, key=lambda l: l["z"]):
        scroll = layer["scroll"]
        pyxel.camera(offset_x * scroll, offset_y * scroll)
        pyxel.bltm(0, 0, layer["tilemap"], 0, 0, 2048, 2048)
    
    # Restore camera to 1.0 scroll for entities
    pyxel.camera(offset_x, offset_y)
    
    # ... entity drawing continues as before ...
```

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (no config file -- convention-based) |
| Config file | none -- tests in `tests/` directory |
| Quick run command | `py -m pytest tests/test_schema.py -x -q` |
| Full suite command | `py -m pytest tests/ -x -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TILE-01 | autoLayerTiles parsed from LDtk file | unit | `py -m pytest tests/test_tilemap.py::test_autotiles_parsed -x` | Wave 0 |
| TILE-02 | AutoLayerTiles rendered on tilemaps[0] | unit | `py -m pytest tests/test_tilemap.py::test_autotiles_on_tilemap -x` | Wave 0 |
| TILE-03 | Flip flags parsed, warning logged for non-zero | unit | `py -m pytest tests/test_tilemap.py::test_flip_flag_warning -x` | Wave 0 |
| TILE-04 | Collision uses IntGrid, visuals use autoLayerTiles | unit | `py -m pytest tests/test_tilemap.py::test_collision_visual_separation -x` | Wave 0 |
| TILE-06 | Multi-layer rendering with parallax scroll rates | manual-only | Visual inspection: bg layer scrolls slower than terrain | N/A |

### Sampling Rate
- **Per task commit:** `py -m pytest tests/test_tilemap.py tests/test_schema.py -x -q`
- **Per wave merge:** `py -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_tilemap.py` -- covers TILE-01, TILE-02, TILE-03, TILE-04
- [ ] Update `tests/test_schema.py` assertions for new tileset path (Pitfall 5)

**Note:** TILE-06 (parallax) is inherently visual and best verified via `run_and_capture` or manual play. A unit test can verify that the draw loop calls `bltm` for each layer, but the visual correctness of parallax scroll rates requires visual inspection.

## Open Questions

1. **tile_coords alignment with tiles.png**
   - What we know: Schema `tile_coords` currently maps IntGrid values to positions designed for cavern.png layout. tiles.png is a different size (96x80 vs 256x256).
   - What's unclear: Whether the IntGrid tile positions in tile_coords (e.g., `1: [0,1]`) are valid in tiles.png. This matters for `restore_tile()`.
   - Recommendation: Visually inspect tiles.png layout. If tile_coords positions don't match, update them. If they do match (because cavern.png was derived from similar layout), no change needed.

2. **colkey for background layer transparency**
   - What we know: `pyxel.bltm()` supports `colkey` parameter for color transparency.
   - What's unclear: Whether the empty background tilemap (all TILE_EMPTY = (31,31)) will render as transparent or as whatever is at image bank position (31,31).
   - Recommendation: Test with TILE_EMPTY. If it renders visible pixels, use `colkey` to make that color transparent, or use a known transparent tile position.

## Sources

### Primary (HIGH confidence)
- `assets/output.ldtk` -- Direct analysis of 18 levels, 18,094 autoLayerTiles, all `f=0`, all `a=1`
- `src/level/map.py` -- Existing `load_from_ldtk()` pattern at line 318, simplified loader at line 36
- `src/core/schema.py` -- `get_layers()`, `get_tileset_path()` API verified
- Pyxel 2.8.7 API -- `bltm()` signature, tilemap count (8), verified via runtime introspection

### Secondary (MEDIUM confidence)
- `assets/entity-schema.json` -- Layer definitions (bg: tilemap 1, z -1, scroll 0.5; terrain: tilemap 0, z 0, scroll 1.0)
- `main.py` -- Current rendering at line 791, sprite loading at line 260-266

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- Pyxel API verified at runtime, LDtk data structure verified by parsing actual file
- Architecture: HIGH -- Existing code patterns in map.py provide proven templates, world bounds verified to fit tilemap
- Pitfalls: HIGH -- Identified from direct code analysis and data verification

**Research date:** 2026-04-06
**Valid until:** 2026-05-06 (stable -- Pyxel 2.8.7 API unlikely to change)
