# Phase 21: Tileset & LDtk Pipeline - Context

**Gathered:** 2026-04-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Reconfigure the LDtk project and tileset for 16x16 grid, update the game's tile loading code, and verify autoLayerTiles render correctly in-game. This phase covers LDtk JSON migration, tileset file consolidation, coordinate math updates in map.py, and simplified export patching. No entity collision changes, no physics tuning -- those are Phase 22.

</domain>

<decisions>
## Implementation Decisions

### Tileset Image Strategy
- **D-01:** Upscale tileset to 16px via nearest-neighbor 2x from Aseprite re-export. The 256x256 image stays 256x256 but with a 16x16 tile grid (256 tiles) instead of 32x32 (1024 tiles).
- **D-02:** tiles.png (256x256) is the new complete 16px tileset with auto-tiles in the upper region and entity icons grafted at y=160 from the original tileset.png upscaled 200%. This file already exists and is ready.
- **D-03:** tileset.png (256x256, old 8px) becomes the single authoritative tileset file referenced by LDtk. Replace its content with the new tiles.png during migration.

### File Organization
- **D-04:** Move tiles.png -> tilesets/cavern.png (overwrite). Move tiles.aseprite -> tilesets/cavern.aseprite. Delete old tileset.png.
- **D-05:** Update entity-schema.json tileset field from "assets/tiles.png" to "assets/tilesets/cavern.png".
- **D-06:** Update LDtk relPath from "tileset.png" to "tilesets/cavern.png".
- **D-07:** tilesets/cavern.png becomes the single source of truth for all tileset references (entity-schema, LDtk, game sprite loading).

### LDtk Project Reconfiguration
- **D-08:** Script-patch output.ldtk (authoritative) programmatically. No LDtk editor needed. Reproducible migration script.
- **D-09:** cave.ldtk is NOT authoritative -- output.ldtk is what the pml-to-ldtk converter produces and the game loads. Patch output.ldtk.
- **D-10:** Auto-layer rules survive grid scaling. Rules reference IntGrid neighbors (not pixel coords). Only tile source coordinates need scaling.
- **D-11:** Migration script changes: defaultGridSize 8->16, tileset tileGridSize 8->16, layer gridSize 8->16, autoLayerTile src coords *2, tile IDs recalculated (tiles_per_row 32->16).

### IntGrid Downsampling
- **D-12:** IntGrid data downsampled from 40x22 (8px) to 20x11 (16px) using top-left-wins strategy. Take the top-left cell of each 2x2 block.

### Entity Position Snapping
- **D-13:** Entity positions snap to nearest 16px grid. Round px values to nearest multiple of 16.
- **D-14:** Only 2 of 42 entities are misaligned (PlayerStart y=88->96, SavePoint x=152->160). All others already 16px-aligned.

### Auto-tile Coordinate Pipeline
- **D-15:** Replace hardcoded grid_size=8 in map.py:181 with TILE_SIZE from constants.py (already 16).
- **D-16:** Update both loaders: load_from_ldtk_simplified AND load_autotiles_from_ldtk to use TILE_SIZE consistently.

### Simplified Export Patching
- **D-17:** Patch both output.ldtk AND simplified export (IntGrid.csv + data.json per level).
- **D-18:** IntGrid.csv downsampled from 40x22 to 20x11 (top-left wins). data.json grid metadata updated.
- **D-19:** Skip PNG regeneration in simplified export -- game doesn't use the PNGs, they're LDtk visual exports.

### Migration Script
- **D-20:** Keep migration script as scripts/migrate_ldtk_16px.py. Useful for Phase 23 converter handoff documentation.
- **D-21:** Script handles: tileset file moves, LDtk JSON patching, simplified export patching, entity snapping. One command does everything.

### tile_coords
- **D-22:** entity-schema tile_coords [col, row] values stay the same. The tileset layout is identical -- each tile just occupies 2x the pixels in place. Col/row indices unchanged.

### Background Layer
- **D-23:** Skip bg tilemap layer (tilemap 1) -- it's empty and won't have content until a future phase.

### Verification
- **D-24:** Use Pyxel MCP tools (run_and_capture, inspect_tilemap, inspect_screen) to verify tiles render at correct positions with no gaps or misalignment.
- **D-25:** Add regression test validating tile loading counts and 16px-aligned coordinates from load_autotiles_from_ldtk.

### Claude's Discretion
- Migration script internal structure and error handling
- Order of operations within the script (file moves vs JSON patching)
- Specific test assertions beyond tile count and alignment
- data.json field updates in simplified export

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### LDtk Files (Migration Targets)
- `assets/output.ldtk` -- Authoritative LDtk project file. Contains autoLayerTiles, tileset defs, layer defs. Currently 8px grid. Main migration target.
- `assets/output/simplified/` -- Simplified export directory. Per-level folders with IntGrid.csv, data.json. Currently 40x22 at 8px.
- `assets/cave.ldtk` -- Non-authoritative LDtk project (may be stale). Not loaded by game.

### Tileset Files
- `assets/tiles.png` -- New 16px tileset (256x256). Complete with auto-tiles + entity icons at y=160. Source for migration.
- `assets/tiles.aseprite` -- Aseprite source file for tiles.png.
- `assets/tileset.png` -- Old 8px tileset (256x256). Referenced by LDtk relPath. To be replaced.
- `assets/tilesets/cavern.png` -- Old copy. Destination for new tileset.

### Game Code (Coordinate Math)
- `src/level/map.py` -- load_autotiles_from_ldtk() at line 157 (hardcoded grid_size=8 at line 181). load_from_ldtk_simplified() for collision/entity loading.
- `src/core/constants.py` -- TILE_SIZE=16, TILE_EMPTY=(15,15), SPRITE_SIZE=16.
- `src/core/schema.py` -- get_tileset_path() returns tileset path from entity-schema.

### Schema
- `assets/entity-schema.json` -- v2.0.0, grid_size=16. tileset field needs updating to "assets/tilesets/cavern.png". tile_coords values stay the same.

### Prior Phase Context
- `.planning/phases/20-grid-constants-schema-metadata/20-CONTEXT.md` -- Phase 20 decisions. D-06 deferred tile_coords value updates to Phase 21 (now resolved: values stay same). D-07 set TILE_EMPTY=(15,15).

### Requirements
- `.planning/REQUIREMENTS.md` -- LDTK-02, LDTK-03, LDTK-04

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/level/map.py:load_autotiles_from_ldtk()` -- Existing auto-tile loader. Only needs grid_size constant swap.
- `src/level/map.py:load_from_ldtk_simplified()` -- Simplified export loader. Uses grid-dependent math for entity positions and IntGrid parsing.
- `src/core/schema.py:get_tileset_path()` -- Central tileset path accessor. Will automatically return the new path after entity-schema update.
- `main.py:195` -- Calls load_autotiles_from_ldtk("assets/output.ldtk"). Path doesn't change.
- `main.py:274` -- Loads tileset via schema.get_tileset_path() into Pyxel image bank.

### Established Patterns
- Game loads simplified export first (collision + entities), then overlays auto-tile visuals from output.ldtk
- All grid math uses `// grid_size` or `// TILE_SIZE` pattern
- Entity-schema is the source of truth for tileset paths, grid dimensions, and tile mappings

### Integration Points
- `export_tilemap_csv.py` -- Tile count math (256/TILE_SIZE=16 tiles per row). Already updated in Phase 20.
- Tests: `test_schema.py` checks tileset path = "assets/tiles.png" (needs updating). `test_sprite_assets.py` checks tilesets/cavern.png exists.
- `test_tilemap.py` -- May have grid-dependent assertions.

</code_context>

<specifics>
## Specific Ideas

- The pml-to-ldtk converter will need matching updates to produce 16px output. This is Phase 23 handoff scope, but the migration script serves as documentation of exactly what changed.
- tiles.png already has entity icons grafted at y=160 (row 10 in 16px grid) from the original tileset.png at 200% scale. No further art work needed.
- Only 2 of 42 entities need position snapping -- minimal disruption to level layouts.

</specifics>

<deferred>
## Deferred Ideas

- **pml-to-ldtk converter update** -- The converter needs to generate 16px output matching the new specs. Noted for Phase 23 handoff.

</deferred>

---

*Phase: 21-tileset-ldtk-pipeline*
*Context gathered: 2026-04-08*
