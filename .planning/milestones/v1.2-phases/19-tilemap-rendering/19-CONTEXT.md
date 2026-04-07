# Phase 19: Tilemap Rendering - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Load and render autoLayerTiles from the LDtk project file for proper terrain visuals (edges, corners, tile variation), with collision remaining IntGrid-driven via the simplified export. Set up multi-layer parallax rendering pipeline with scroll-rate camera offsets. Update the tileset reference to the new tiles.png.

</domain>

<decisions>
## Implementation Decisions

### Auto-tile Data Source
- **D-01:** Hybrid approach — keep simplified export (`cave/simplified/`) for collision data (IntGrid.csv) and entity loading. Add autoLayerTiles parsing from the full LDtk project file.
- **D-02:** Read autoLayerTiles from `assets/output.ldtk` — this file has 46 auto-tile rules, 26 unique tile variants, and 18 levels. The `cave.ldtk` file has minimal/placeholder rules.
- **D-03:** autoLayerTiles fields used: `px` (position), `src` (tileset source), `f` (flip flag), `a` (opacity). Skip tiles with `a=0`.

### Tile Flip Handling
- **D-04:** Defer flip support. All 18,094 autoLayerTiles in output.ldtk have `f=0` (no flips). Parse the flip flag but log a warning if non-zero values are encountered.
- **D-05:** The `f=1` (flipX) values observed in cave.ldtk were artifacts of incomplete tile supply — output.ldtk has the correct complete tileset with explicit tiles for all orientations.

### Parallax Layer Rendering
- **D-06:** Build multi-layer `bltm()` rendering pipeline. Each layer drawn at `camera_x * scroll_rate` offset per schema layer definitions.
- **D-07:** Background layer (tilemap 1, scroll 0.5) is empty for now. Pipeline is ready for content when a LDtk background layer or tileset art is added later.
- **D-08:** Terrain layer (tilemap 0, scroll 1.0) receives autoLayerTiles data. This is the primary visual layer.
- **D-09:** Layer draw order follows schema `z` values (lower z drawn first).

### Auto-tile Rule Quality
- **D-10:** The 46 auto-tile rules and 26 tile variants in output.ldtk are complete. Code renders what LDtk produces — no procedural tile generation needed.
- **D-11:** Tileset uses LDtk standard auto-tile template layout (two templates stacked).

### Tileset Image
- **D-12:** `assets/tiles.png` (currently 96x80) is the canonical tileset for autoLayerTiles. Target size is 128x128 to allow room for future tile types.
- **D-13:** Update schema `biomes.cavern.tileset` to reference the correct tileset path (tiles.png or copy to tilesets/cavern.png). Any missing tiles from old cavern.png must be merged into the new tileset.
- **D-14:** Tileset loaded into Pyxel image bank 0 (256x256 capacity, 8px grid = 32x32 tile slots).

### Collision/Visual Separation
- **D-15:** Collision detection continues using IntGrid.csv data (integer values) via the existing simplified export loader. Fully independent from visual tile rendering.
- **D-16:** Visual rendering uses autoLayerTiles `src` coordinates to set tilemap tiles. No dependency on IntGrid-to-tile schema mappings for visuals — autoLayerTiles already specify exact tile coordinates.

### Claude's Discretion
- How to structure the LDtk full-file parser (separate module or extension of existing map.py)
- Whether to cache parsed autoLayerTiles data or re-read per room load
- Exact parallax camera offset math in the draw loop
- How to handle the tileset path update (rename, copy, or update schema reference)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### LDtk Project File
- `assets/output.ldtk` — Production LDtk file with 46 auto-tile rules, 18 levels, autoLayerTiles data. IntGrid layer uses tileset uid 64 (Tiles, tiles.png, 8px grid).

### Tileset
- `assets/tiles.png` — New canonical tileset (96x80 currently, target 128x128). LDtk standard auto-tile template layout. Referenced by output.ldtk tileset uid 64.
- `assets/tilesets/cavern.png` — Old tileset (256x256). Schema currently references this. Needs updating to match tiles.png.

### Schema
- `assets/entity-schema.json` — v1.0.0 unified schema. `biomes.cavern.tileset` path needs updating. `biomes.cavern.layers` defines parallax layer structure (bg: tilemap 1, z -1, scroll 0.5; terrain: tilemap 0, z 0, scroll 1.0).

### Existing Tile Loading Code
- `src/level/map.py` — `load_from_ldtk_simplified()` handles collision data and entity loading from simplified export. `load_from_ldtk()` (line 320+) has a basic autoLayerTiles path that can be referenced.
- `src/core/schema.py` — `get_layers()` returns layer definitions, `get_tileset_path()` returns tileset path. Both ready for consumption.

### Rendering
- `main.py:791` — Single `pyxel.bltm(0, 0, 0, 0, 0, 2048, 2048)` call. Needs expansion to multi-layer rendering with parallax offsets.

### Simplified Export
- `assets/cave/simplified/Level_*/` — IntGrid.csv and data.json for collision and entities. Stays as-is for collision data source.

### Prior Phase Context
- `.planning/phases/17-unified-schema-definition/17-CONTEXT.md` — Schema structure decisions (tile coords, layers, biome model).
- `.planning/phases/18-schema-driven-integration/18-CONTEXT.md` — Schema loading, constant elimination, behavior lookups.

### Requirements
- `.planning/REQUIREMENTS.md` — TILE-01, TILE-02, TILE-03, TILE-04, TILE-06 are this phase's requirements.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `schema.get_layers()`: Returns layer definitions with tilemap index, z-order, and scroll rate — ready for multi-layer rendering loop.
- `schema.get_tileset_path()`: Returns tileset path from schema — update the schema value and this feeds the existing loading pipeline.
- `load_from_ldtk()` (map.py:320): Existing parser that reads autoLayerTiles from full LDtk format. Can be referenced/adapted for the output.ldtk parser.
- `SPRITE_MANIFEST` (main.py:141): Tileset loading entry for bank 0 — path comes from schema.

### Established Patterns
- Tilemap population via `pyxel.tilemaps[id].pset(tx, ty, (u, v))` — same pattern for autoLayerTiles.
- Schema-driven initialization at startup via `schema.init()` — tileset path and layer data already available.
- Room-based loading: `load_from_ldtk_simplified()` processes per-level directories with coordinate normalization.

### Integration Points
- `main.py:791` — `bltm()` call needs expansion to loop over schema layers with parallax offsets.
- `main.py:262-264` — Tileset loading from schema path. Must load the correct tileset that matches autoLayerTiles src coordinates.
- `map.py:36` — `load_from_ldtk_simplified()` entry point. autoLayerTiles loading hooks in after collision data is loaded.

</code_context>

<specifics>
## Specific Ideas

- output.ldtk autoLayerTile format: `{"px": [x,y], "src": [sx,sy], "f": 0, "t": tileId, "d": [ruleId, cellIdx], "a": 1}`. The `src` values are pixel coordinates into tiles.png — divide by 8 for tilemap (u,v).
- Level coordinates in output.ldtk use world-space pixel positions — same normalization needed as in the simplified export loader (min_wx/min_wy offset).
- The existing `load_from_ldtk()` method (line 320) already does `tile['src'][0] // grid_size` conversion — proven pattern.
- Parallax: `pyxel.bltm(cam_x * scroll, cam_y * scroll, tm_id, ...)` where scroll comes from schema layer definition.

</specifics>

<deferred>
## Deferred Ideas

- Background layer content (tileset art or LDtk background layer) — ready when art exists
- Foreground parallax layer — add to schema when foreground tile art is available
- Tile flip support (pre-baking or per-tile blt) — implement if future auto-tile rules use non-zero flip flags
- Biome-specific tileset switching — future milestone (BIOME-02)
- Merging cave.ldtk and output.ldtk into a single canonical LDtk file

</deferred>

---

*Phase: 19-tilemap-rendering*
*Context gathered: 2026-04-06*
