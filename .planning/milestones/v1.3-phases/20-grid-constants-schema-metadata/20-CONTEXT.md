# Phase 20: Grid Constants & Schema Metadata - Context

**Gathered:** 2026-04-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Flip the codebase from 8x8 tile grid (with SPRITE_SCALE=2 indirection) to a uniform 16x16 tile grid. This phase covers constants, derived values, schema metadata, and test updates only. No entity collision changes, no physics tuning, no tileset art — those are Phases 21-22.

</domain>

<decisions>
## Implementation Decisions

### Room Dimensions
- **D-01:** Derive tile counts from pixel size / grid_size. No hardcoded tile counts in constants or schema. default_room_size stays as [320, 176] pixels; tile counts (20x11) are computed.

### SPRITE_SCALE Removal
- **D-02:** Delete SPRITE_SCALE entirely from constants.py.
- **D-03:** Keep SPRITE_SIZE as a named constant = 16 (= TILE_SIZE). Reads clearly in draw_sprite() calls and separates rendering concept from collision grid concept.
- **D-04:** BOSS_SPRITE_SIZE = 32 (= 2 * TILE_SIZE). Defined as a direct constant, no SPRITE_SCALE indirection.

### Schema Version
- **D-05:** Bump entity-schema.json from v1.0.0 to v2.0.0 (major). grid_size 8->16 is a breaking change for the pml-to-ldtk converter contract.

### Tileset Coordinate Mapping
- **D-06:** Update tile_coords description in schema from "8px tile grid" to "16px tile grid". Leave actual coordinate values unchanged — Phase 21 will update them when the 16px tileset is ready.

### TILE_EMPTY Sentinel
- **D-07:** Change TILE_EMPTY from (31, 31) to (15, 15). Bottom-right corner of a 256x256 image bank at 16px tile size is (15, 15).

### export_tilemap_csv.py
- **D-08:** Update the CSV export script's tile count math and tiles-per-row calculation for 16px (256/16=16 tiles per row). Keep the script functional.

### Test Migration
- **D-09:** Replace test_sprite_scale.py assertions with new contract: TILE_SIZE == 16, SPRITE_SIZE == 16, BOSS_SPRITE_SIZE == 32, and assert SPRITE_SCALE is no longer importable.

### Claude's Discretion
- Constants ordering and comment updates in constants.py
- Schema field ordering and note updates in entity-schema.json
- variable_rooms_note text update (currently references "40x22 tiles")

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Grid & Constants
- `src/core/constants.py` — Central constants file; TILE_SIZE, SPRITE_SCALE, SPRITE_SIZE, BOSS_SPRITE_SIZE, TILE_EMPTY all defined here
- `assets/entity-schema.json` — Shared schema contract with pml-to-ldtk converter; grid_size, default_room_size, tile_coords, entity sizes

### Rendering & Collision
- `src/level/map.py` — Heavy TILE_SIZE usage in collision queries (get_solid_tiles, get_hazard_tiles, etc.)
- `src/core/sprite_utils.py` — Imports SPRITE_SIZE and BOSS_SPRITE_SIZE for draw_sprite()

### Entity Draw Calls
- `src/entities/player.py` — Uses TILE_SIZE for block-breaking snap math, SPRITE_SIZE for draw
- `src/entities/boss.py` — Uses BOSS_SPRITE_SIZE for draw, TILE_SIZE for collision
- `src/entities/items.py` — Uses SPRITE_SIZE for draw
- `src/entities/effects.py` — Uses SPRITE_SIZE for explosion draw
- `src/entities/slime.py` — Uses TILE_SIZE for follow step, SPRITE_SIZE for draw

### Utility Scripts
- `export_tilemap_csv.py` — Uses TILE_SIZE for tile count math; hardcodes 32 tiles per row

### Tests
- `tests/test_sprite_scale.py` — Asserts SPRITE_SCALE and BOSS_SPRITE_SIZE relationships (to be replaced)

### Requirements
- `.planning/REQUIREMENTS.md` — GRID-01 through GRID-04, LDTK-01, LDTK-05

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `constants.py` is the single source of truth for all game constants — clean central location for the migration
- `entity-schema.json` already has structured `level.grid_size` and `biomes.cavern.tile_coords` — well-organized for updates

### Established Patterns
- All entity files import from `src.core.constants` using `from src.core.constants import *` or named imports
- TILE_SIZE is used for pixel-to-tile conversion: `int(x // TILE_SIZE)` pattern throughout map.py
- SPRITE_SIZE is used exclusively in draw_sprite() width/height arguments
- BOSS_SPRITE_SIZE is used only in boss.py draw calls

### Integration Points
- `src/level/map.py` — Most TILE_SIZE references (collision math). Will automatically use new value via import.
- `src/core/sprite_utils.py:draw_sprite()` — Central rendering function imports SPRITE_SIZE/BOSS_SPRITE_SIZE
- `export_tilemap_csv.py` — Standalone script, not imported by game code

</code_context>

<specifics>
## Specific Ideas

No specific requirements — standard constant migration with clear before/after values.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 20-grid-constants-schema-metadata*
*Context gathered: 2026-04-08*
