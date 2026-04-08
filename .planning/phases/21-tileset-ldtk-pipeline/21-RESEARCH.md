# Phase 21: Tileset & LDtk Pipeline - Research

**Researched:** 2026-04-08
**Domain:** LDtk JSON migration, tileset consolidation, Pyxel tile loading
**Confidence:** HIGH

## Summary

This phase migrates the LDtk project (output.ldtk) and simplified exports from 8px to 16px grid, consolidates tileset files, and updates game-side tile loading code. The migration is entirely programmatic -- a Python script patches JSON structures, downsamples IntGrid CSVs, snaps entity positions, and moves tileset files. Game code changes are minimal: replace hardcoded `// 8` divisors with TILE_SIZE, and update `% 32` / `// 32` tile ID math to use 16 tiles per row.

The LDtk project uses auto-layer rules that reference tile IDs computed from a 12-column tileset (old tiles.png, 96x80 at 8px). The new tileset (tilesets/cavern.png, 256x256 at 16px) has 16 columns per row. Tile (col, row) positions are preserved but linear IDs change: `new_id = row * 16 + col` vs old `old_id = row * 12 + col`. Auto-tile `src` pixel coordinates in level data must be doubled. IntGrid data downsamples from 40x22 to 20x11 using top-left-wins strategy.

**Primary recommendation:** Build a single migration script (scripts/migrate_ldtk_16px.py) that handles all file moves, JSON patching, and CSV downsampling in one reproducible command. Update map.py hardcoded values separately. Verify with Pyxel MCP tools.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- D-01: Upscale tileset to 16px via nearest-neighbor 2x from Aseprite re-export. The 256x256 image stays 256x256 but with a 16x16 tile grid (256 tiles) instead of 32x32 (1024 tiles).
- D-02: tiles.png (256x256) is the new complete 16px tileset with auto-tiles in the upper region and entity icons grafted at y=160 from the original tileset.png upscaled 200%. This file already exists and is ready.
- D-03: tileset.png (256x256, old 8px) becomes the single authoritative tileset file referenced by LDtk. Replace its content with the new tiles.png during migration.
- D-04: Move tiles.png -> tilesets/cavern.png (overwrite). Move tiles.aseprite -> tilesets/cavern.aseprite. Delete old tileset.png.
- D-05: Update entity-schema.json tileset field from "assets/tiles.png" to "assets/tilesets/cavern.png".
- D-06: Update LDtk relPath from "tileset.png" to "tilesets/cavern.png".
- D-07: tilesets/cavern.png becomes the single source of truth for all tileset references (entity-schema, LDtk, game sprite loading).
- D-08: Script-patch output.ldtk (authoritative) programmatically. No LDtk editor needed. Reproducible migration script.
- D-09: cave.ldtk is NOT authoritative -- output.ldtk is what the pml-to-ldtk converter produces and the game loads. Patch output.ldtk.
- D-10: Auto-layer rules survive grid scaling. Rules reference IntGrid neighbors (not pixel coords). Only tile source coordinates need scaling.
- D-11: Migration script changes: defaultGridSize 8->16, tileset tileGridSize 8->16, layer gridSize 8->16, autoLayerTile src coords *2, tile IDs recalculated (tiles_per_row 32->16).
- D-12: IntGrid data downsampled from 40x22 (8px) to 20x11 (16px) using top-left-wins strategy.
- D-13: Entity positions snap to nearest 16px grid. Round px values to nearest multiple of 16.
- D-14: Only 2 of 42 entities are misaligned (PlayerStart y=88->96, SavePoint x=152->160). All others already 16px-aligned.
- D-15: Replace hardcoded grid_size=8 in map.py:181 with TILE_SIZE from constants.py (already 16).
- D-16: Update both loaders: load_from_ldtk_simplified AND load_autotiles_from_ldtk to use TILE_SIZE consistently.
- D-17: Patch both output.ldtk AND simplified export (IntGrid.csv + data.json per level).
- D-18: IntGrid.csv downsampled from 40x22 to 20x11 (top-left wins). data.json grid metadata updated.
- D-19: Skip PNG regeneration in simplified export -- game doesn't use the PNGs, they're LDtk visual exports.
- D-20: Keep migration script as scripts/migrate_ldtk_16px.py. Useful for Phase 23 converter handoff documentation.
- D-21: Script handles: tileset file moves, LDtk JSON patching, simplified export patching, entity snapping. One command does everything.
- D-22: entity-schema tile_coords [col, row] values stay the same. The tileset layout is identical -- each tile just occupies 2x the pixels in place. Col/row indices unchanged.
- D-23: Skip bg tilemap layer (tilemap 1) -- it's empty and won't have content until a future phase.
- D-24: Use Pyxel MCP tools (run_and_capture, inspect_tilemap, inspect_screen) to verify tiles render at correct positions with no gaps or misalignment.
- D-25: Add regression test validating tile loading counts and 16px-aligned coordinates from load_autotiles_from_ldtk.

### Claude's Discretion
- Migration script internal structure and error handling
- Order of operations within the script (file moves vs JSON patching)
- Specific test assertions beyond tile count and alignment
- data.json field updates in simplified export

### Deferred Ideas (OUT OF SCOPE)
- pml-to-ldtk converter update -- The converter needs to generate 16px output matching the new specs. Noted for Phase 23 handoff.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LDTK-02 | LDtk project (cave.ldtk) reconfigured with 16x16 default grid | Migration script patches output.ldtk: defaultGridSize, layer gridSize, tileset tileGridSize all 8->16. Entity grid snapping. IntGrid downsampling. |
| LDTK-03 | autoLayerTiles coordinates and tile IDs correct at 16x16 | Auto-tile src coords doubled (*2). tileRectsIds recalculated: old 12-col -> new 16-col grid. Linear ID formula: `new_id = row * 16 + col`. |
| LDTK-04 | Tileset adapted for 16x16 tile definitions | tiles.png -> tilesets/cavern.png. LDtk tileset def updated: relPath, pxWid/pxHei, tileGridSize, __cWid/__cHei. entity-schema.json tileset path updated. |
</phase_requirements>

## Architecture Patterns

### Migration Script Structure
```
scripts/migrate_ldtk_16px.py
  1. File moves (tiles.png -> tilesets/cavern.png, tiles.aseprite -> tilesets/cavern.aseprite)
  2. Delete old tileset.png
  3. Patch output.ldtk JSON:
     a. Top-level: defaultGridSize 8->16
     b. Tileset defs: tileGridSize, relPath, pxWid/pxHei, __cWid/__cHei
     c. Layer defs: gridSize 8->16
     d. Auto-rule tileRectsIds: recalculate linear IDs (12-col -> 16-col)
     e. Level data: autoLayerTile src coords *2, px coords *2 (wait - px should NOT change, they're world coords)
     f. IntGrid coordId values: recalculate for 20x11 grid
     g. Entity positions: snap to nearest 16px
  4. Patch simplified export:
     a. IntGrid.csv: downsample 40x22 -> 20x11 (top-left wins)
     b. data.json: update width/height metadata if needed
  5. Patch entity-schema.json: tileset path
```

### Critical Coordinate Math

**autoLayerTile transformation in output.ldtk:**
- `src` array: multiply both values by 2 (8px tileset coords -> 16px tileset coords)
- `px` array: multiply both values by... NO. `px` is level-local pixel coordinates. The level size stays 320x176. At 8px grid, a tile at grid position (5,3) has px=[40,24]. At 16px grid, the same logical tile position is (5,3) -> px still needs to reflect the pixel position. But the room is now 20x11 tiles instead of 40x22. So an auto-tile at old px=[40,24] maps to what in 16px?

Actually, the IntGrid is downsampled 2:1. An 8px cell at grid (5,3) = px (40,24) maps to 16px cell at grid (2,1) = px (32,16) in the downsampled grid. But auto-tiles paint per-cell, so the auto-tile at old px=[40,24] should become px=[32,16]? No -- the auto-tiles need to be regenerated from the downsampled IntGrid. We can't simply transform the existing auto-tiles because the rule patterns operate on the downsampled grid which may produce different results.

**CRITICAL INSIGHT: Auto-tile regeneration is not possible without LDtk editor.** Per D-08, we patch programmatically. But auto-layer rules are computed by LDtk based on IntGrid values. If we downsample the IntGrid, the auto-tile results would change (different neighbor patterns at coarser resolution). However, D-10 says "Auto-layer rules survive grid scaling. Rules reference IntGrid neighbors (not pixel coords). Only tile source coordinates need scaling."

The approach must be: scale the existing auto-tile positions, not regenerate them. Each auto-tile at old px=[x,y] maps to new px=[x,y] (unchanged -- the room pixel dimensions are the same 320x176). The src coordinates change (*2 for tileset upscale). The grid_size change means the game's tile coordinate calculation changes: `tx = px_x // 16` instead of `tx = px_x // 8`, so the tile lands at a different tile coordinate, but the PIXEL position remains correct for rendering.

Wait -- Pyxel tilemaps use tile coordinates, not pixel coordinates. The game calls `pset(tx, ty, (u, v))` where tx/ty are tile grid coordinates. At 8px grid, a room has 40x22 tile positions. At 16px, it has 20x11. The tilemap has 256x256 tile slots. So the auto-tiles need to map to the correct 16px tile positions:
- Old: px=[40,24], tx = 40//8 = 5, ty = 24//8 = 3
- New: same pixel but 16px grid -> tx = 40//16 = 2, ty = 24//16 = 1

But there's a problem: two old 8px auto-tiles can map to the same 16px cell. For example, old tiles at px=[40,24] and px=[48,24] both map to tx=2 at 16px (40//16=2, 48//16=3... no, 48//16=3). So actually each old tile maps to a unique new tile position IF we simply divide by 16. But the old 40x22 grid has 880 cells; the new 20x11 has 220 cells. So 4 old cells map to 1 new cell. Only one auto-tile visual can survive per new cell.

**The correct approach per D-10 and D-11:** The auto-tiles in the level data need their px coordinates halved (not doubled): old px=[40,24] -> new px=[20,12]. Then the game divides by 16: tx=20//16=1, ty=12//16=0. Hmm, that gives wrong positions.

Let me re-examine. The room is 320x176 pixels at both 8px and 16px grids. At 8px: 40x22 tiles. At 16px: 20x11 tiles. A solid block in the top-left at 8px occupies 4 cells: (0,0), (1,0), (0,1), (1,1) in the 8px grid with auto-tiles at px=[0,0], [8,0], [0,8], [8,8]. At 16px, this is a single cell (0,0) at px=[0,0]. So we need to:
1. Discard 3 of 4 auto-tiles per 16px cell (keep top-left, matching IntGrid downsampling)
2. Keep the px coordinate of the surviving tile (which is already aligned to 16px boundaries for the top-left of each 2x2 block)

BUT the auto-tiles aren't just filling -- they're edge/corner variants. The auto-rule patterns at 8px generate specific tiles for edges, corners, etc. At 16px these same patterns applied to the downsampled IntGrid would produce different results. Since we can't run LDtk rules, we need to approximate.

Actually, per D-10: "Rules reference IntGrid neighbors (not pixel coords). Only tile source coordinates need scaling." This means the auto-rules are neighbor-pattern-based. The same neighbor pattern at 8px produces the same tile at 16px. So if the IntGrid downsampling preserves the topology (which top-left-wins does for border cells), the auto-tiles at the 16px boundary positions should have the correct variant.

**Practical approach:** For each 2x2 block of old auto-tiles, keep the one at the top-left position (the one with px coords divisible by 16). Update its src coords (*2). Discard the other 3. This gives us one auto-tile per 16px cell.

### Hardcoded Values in map.py Requiring Update

| Line | Current Code | Change To | Reason |
|------|-------------|-----------|--------|
| 71 | `origin_x = (min_wx // 8) * 8` | `(min_wx // TILE_SIZE) * TILE_SIZE` | Origin snap to tile boundary |
| 72 | `origin_y = (min_wy // 8) * 8` | `(min_wy // TILE_SIZE) * TILE_SIZE` | Origin snap to tile boundary |
| 86 | `base_tx, base_ty = world_x // 8, world_y // 8` | `world_x // TILE_SIZE, world_y // TILE_SIZE` | Tile position from world coords |
| 147 | `(v % 32, v // 32)` | `(v % 16, v // 16)` | Tile ID to (col, row) with 16 tiles/row |
| 181 | `grid_size = 8` | `grid_size = TILE_SIZE` | Auto-tile grid size |
| 465 | `u = real_id % 32` | `u = real_id % 16` | Tiled loader (not critical but should match) |
| 466 | `v = real_id // 32` | `v = real_id // 16` | Tiled loader (not critical but should match) |

### LDtk JSON Fields to Patch in output.ldtk

**Top-level:**
- `defaultGridSize`: 8 -> 16

**Tileset definitions (defs.tilesets):**
- For uid=64 (Tiles, current auto-rule tileset):
  - `relPath`: "tiles.png" -> "tilesets/cavern.png"
  - `pxWid`: 96 -> 256
  - `pxHei`: 80 -> 256
  - `tileGridSize`: 8 -> 16
  - `__cWid`: 12 -> 16
  - `__cHei`: 10 -> 16
  - `cachedPixelData`: recalculate or clear (LDtk regenerates on open)
- For uid=61 (Tileset, old tileset.png): remove or update relPath since tileset.png is being deleted

**Layer definitions (defs.layers):**
- IntGrid layer (uid=2): `gridSize`: 8 -> 16
- Entities layer (uid=1): `gridSize`: 8 -> 16 (optional but consistent)

**Auto-rule tileRectsIds (within defs.layers[IntGrid].autoRuleGroups):**
- Recalculate IDs: `old_col = old_id % 12, old_row = old_id // 12` -> `new_id = old_row * 16 + old_col`
- Pattern values (the -1/0/1 arrays) stay unchanged (neighbor matching)

**Level instances (levels[].layerInstances[]):**
- IntGrid layer `intGridCsv` or coordId data: downsample
- autoLayerTiles: filter to top-left of each 2x2 block, update `src` coords (*2)

**Entity instances:**
- Snap `px` values to nearest multiple of 16

### Simplified Export Patching

**Per level directory (assets/output/simplified/Level_N/):**

`IntGrid.csv`:
- Currently 40 values per row, 22 rows (40x22 at 8px)
- Downsample to 20 values per row, 11 rows (20x11 at 16px)
- Strategy: top-left wins (take cell [2*r][2*c] from old grid)

`data.json`:
- `width` and `height` stay the same (320x176 pixels -- these are pixel dimensions, not tile counts)
- Entity positions: snap to nearest 16px (same as output.ldtk)

### Anti-Patterns to Avoid
- **Modifying px coords of auto-tiles instead of filtering:** The pixel positions of surviving auto-tiles don't change -- only 3 of 4 tiles per 2x2 block are discarded, the surviving top-left tile's px is already 16px-aligned.
- **Forgetting cachedPixelData:** LDtk tileset defs include cached pixel data strings sized to the old grid. These must be recalculated or cleared.
- **Updating cave.ldtk:** D-09 explicitly says cave.ldtk is not authoritative. Don't waste time patching it.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON patching | String replacement on LDtk JSON | Python json.load/dump with indent=2 | LDtk JSON has nested structures; string ops break |
| IntGrid downsampling | Manual cell iteration | Nested list comprehension with stride-2 indexing | Clean, debuggable, one-liner per row |
| File moves | os.rename | shutil.move + shutil.copy2 | Cross-device moves, preserves metadata |

## Common Pitfalls

### Pitfall 1: Tile ID Calculation Uses Wrong tiles_per_row
**What goes wrong:** Using 32 (old tileset.png had 32 cols at 8px) instead of 12 (actual auto-rule tileset tiles.png had 12 cols at 8px) for old tile ID decomposition.
**Why it happens:** D-11 mentions "tiles_per_row 32->16" but the actual auto-rule tileset (uid=64) is 96x80 with 12 cols, not 32.
**How to avoid:** Always derive tiles_per_row from tileset dimensions: `pxWid // tileGridSize`. Old = 96//8 = 12. New = 256//16 = 16.
**Warning signs:** Converted tile IDs produce incorrect visuals (wrong tile variant at edges/corners).

### Pitfall 2: Auto-tile px Coordinates vs src Coordinates
**What goes wrong:** Doubling px (position) coordinates instead of src (tileset source) coordinates, or vice versa.
**Why it happens:** Both are 2-element arrays in the same tile object. Easy to mix up.
**How to avoid:** `src` = tileset pixel coords, multiply by 2 (tileset upscaled 2x). `px` = level-local pixel position, do NOT modify (room dimensions unchanged). Instead, filter auto-tiles to keep only those at 16px-aligned positions.
**Warning signs:** Tiles render at double the intended position, or source the wrong tileset region.

### Pitfall 3: IntGrid coordId Format in output.ldtk vs CSV in Simplified Export
**What goes wrong:** Treating IntGrid data the same way in both files.
**Why it happens:** output.ldtk uses `intGridCsv` (a flat 1D array) or legacy coordId format, while simplified export uses CSV files with rows.
**How to avoid:** Handle separately. For output.ldtk: reshape flat array to 2D using old width (40), downsample 2:1, flatten back. For CSV: parse rows, stride-2 on both axes.
**Warning signs:** Garbled collision data, solid blocks in wrong positions.

### Pitfall 4: Entity Snap Rounding Direction
**What goes wrong:** Using floor division instead of round-to-nearest for entity position snapping.
**Why it happens:** `// 16 * 16` floors; entities at x=152 go to 144 instead of 160.
**How to avoid:** Use `round(val / 16) * 16` for nearest-neighbor snapping. Per D-14, only PlayerStart y=88->96 and SavePoint x=152->160 need adjustment.
**Warning signs:** Entities visually offset from their intended tile positions.

### Pitfall 5: Test Assertions Hardcode Old Values
**What goes wrong:** Existing tests (test_schema.py, test_tilemap.py, test_sprite_assets.py) assert old tileset paths and 8px-based coordinate math.
**Why it happens:** Tests were written for the pre-migration state.
**How to avoid:** Update tests in the same commit as the code changes:
- `test_schema.py:84,86` assert tileset = "assets/tiles.png" -> "assets/tilesets/cavern.png"
- `test_schema.py:198` assert get_tileset_path() = "assets/tiles.png" -> "assets/tilesets/cavern.png"
- `test_tilemap.py` helper `_make_ldtk_data` uses `__gridSize: 8` -> 16, and test assertions on tile coords assume 8px math
- `test_sprite_assets.py:104,106` checks pixel at (0,8) for TILE_SOLID -> (0,16) at 16px grid

### Pitfall 6: Tileset uid=61 (Old Tileset) References
**What goes wrong:** Leaving references to the deleted tileset.png (uid=61) in output.ldtk.
**Why it happens:** The IntGrid layer uses uid=64 (Tiles), but uid=61 (Tileset) may be referenced elsewhere.
**How to avoid:** Either remove uid=61 tileset def entirely, or update its relPath. Search all `tilesetDefUid` and `__tilesetDefUid` references.
**Warning signs:** LDtk would error on missing tileset if ever opened in the editor.

## Code Examples

### IntGrid CSV Downsampling (top-left wins)
```python
def downsample_intgrid_csv(csv_path):
    """Downsample 40x22 IntGrid CSV to 20x11 using top-left-wins."""
    with open(csv_path) as f:
        rows = [line.strip().split(',') for line in f if line.strip()]
    
    # Take every other row, every other column
    new_rows = []
    for r in range(0, len(rows), 2):
        new_row = [rows[r][c] for c in range(0, len(rows[r]), 2) if rows[r][c].strip()]
        new_rows.append(','.join(new_row))
    
    with open(csv_path, 'w') as f:
        f.write('\n'.join(new_rows) + '\n')
```

### tileRectsIds Recalculation
```python
def convert_tile_id(old_id, old_cols_per_row=12, new_cols_per_row=16):
    """Convert linear tile ID from old grid to new grid.
    
    Col/row position is preserved; only the linear ID changes
    because tiles_per_row differs (12 -> 16).
    """
    old_col = old_id % old_cols_per_row
    old_row = old_id // old_cols_per_row
    return old_row * new_cols_per_row + old_col
```

### Auto-tile Filtering (keep top-left of 2x2 blocks)
```python
def filter_autotiles_16px(tiles):
    """Keep only auto-tiles at 16px-aligned positions, update src coords."""
    result = []
    for tile in tiles:
        px_x, px_y = tile["px"]
        # Keep only tiles at positions divisible by 16
        if px_x % 16 == 0 and px_y % 16 == 0:
            # Scale src coordinates (tileset upscaled 2x)
            tile["src"] = [tile["src"][0] * 2, tile["src"][1] * 2]
            result.append(tile)
    return result
```

### Entity Position Snapping
```python
def snap_entity_position(entity_data):
    """Snap entity px coordinates to nearest 16px multiple."""
    for field in ("x", "y"):  # or "px" depending on data format
        if field in entity_data:
            val = entity_data[field]
            entity_data[field] = round(val / 16) * 16
```

### map.py Hardcoded Value Fix
```python
# Before (line 181):
grid_size = 8  # 8px tile grid

# After:
grid_size = TILE_SIZE  # 16px tile grid (Phase 21, D-15)
```

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | none (default discovery) |
| Quick run command | `python -m pytest tests/test_tilemap.py tests/test_schema.py -x -q` |
| Full suite command | `python -m pytest tests/ -x -q` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LDTK-02 | output.ldtk has 16x16 defaultGridSize and 20x11 rooms | unit | `python -m pytest tests/test_ldtk_migration.py -x` | Wave 0 |
| LDTK-03 | autoLayerTiles load at correct 16px positions | unit | `python -m pytest tests/test_tilemap.py -x` | Exists (needs update) |
| LDTK-04 | Tileset at tilesets/cavern.png, schema path correct | unit | `python -m pytest tests/test_schema.py tests/test_sprite_assets.py -x` | Exists (needs update) |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_tilemap.py tests/test_schema.py tests/test_sprite_assets.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before verification

### Wave 0 Gaps
- [ ] `tests/test_ldtk_migration.py` -- validates migration script output (IntGrid dimensions, tile IDs, entity snapping)
- [ ] Update `tests/test_tilemap.py` -- change `__gridSize: 8` to 16 in test helpers, update coordinate assertions
- [ ] Update `tests/test_schema.py` -- change tileset path assertions from "assets/tiles.png" to "assets/tilesets/cavern.png"
- [ ] Update `tests/test_sprite_assets.py` -- change pixel coordinate check from (0,8) to (0,16) for TILE_SOLID

## Open Questions

1. **intGridCsv format in output.ldtk levels**
   - What we know: Simplified export uses CSV files. output.ldtk may use `intGridCsv` (flat array) or legacy coordId format.
   - What's unclear: Exact format of IntGrid data within level layerInstances in this project's output.ldtk.
   - Recommendation: Inspect the first level's IntGrid layer instance to determine format before writing migration code.

2. **cachedPixelData in tileset defs**
   - What we know: Each tileset def has opaqueTiles and averageColors strings sized to the grid.
   - What's unclear: Whether LDtk requires valid cachedPixelData or regenerates it.
   - Recommendation: Set to null or empty object. LDtk regenerates on open. Game doesn't read these fields.

3. **Auto-tile deduplication at 16px boundaries**
   - What we know: Multiple 8px auto-tiles may map to the same 16px cell. Top-left should be preferred.
   - What's unclear: Whether edge/corner variants at 8px boundaries produce correct visuals when only top-left survives.
   - Recommendation: Implement top-left filtering and verify visually with Pyxel MCP. If edge tiles look wrong, this indicates the auto-rules would need re-evaluation (which is LDtk's job and deferred to converter update in Phase 23).

## Sources

### Primary (HIGH confidence)
- `assets/output.ldtk` -- Direct inspection of LDtk JSON structure, tileset defs, auto-rules, and level data
- `src/level/map.py` -- Game tile loading code with hardcoded 8px values
- `src/core/constants.py` -- TILE_SIZE=16, TILE_EMPTY=(15,15)
- `assets/entity-schema.json` -- v2.0.0 schema with tile_coords and tileset path
- `tests/test_tilemap.py`, `tests/test_schema.py`, `tests/test_sprite_assets.py` -- Existing tests requiring updates

### Secondary (MEDIUM confidence)
- LDtk JSON format knowledge from training data and direct file inspection

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Python stdlib (json, shutil, os) only, no external deps
- Architecture: HIGH - All code files inspected, data formats verified by direct analysis
- Pitfalls: HIGH - Tile ID calculation verified empirically (old=12col grid, not 32)

**Research date:** 2026-04-08
**Valid until:** 2026-05-08 (stable -- data format is static)
