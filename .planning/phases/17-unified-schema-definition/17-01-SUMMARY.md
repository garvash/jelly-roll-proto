---
phase: 17-unified-schema-definition
plan: 01
subsystem: schema
tags: [json-schema, tileset, biomes, intgrid, tilemap-layers]

# Dependency graph
requires:
  - phase: none
    provides: "existing entity-schema.json v0.6.0 and tiles.png"
provides:
  - "entity-schema.json v1.0.0 with biomes.cavern tile_coords and layers"
  - "Cavern tileset at assets/tilesets/cavern.png (biome-specific path)"
  - "SPRITE_MANIFEST updated to load from new tileset path"
  - "10 schema validation tests in tests/test_schema.py"
affects: [18-schema-driven-loading, 19-tilemap-rendering]

# Tech tracking
tech-stack:
  added: []
  patterns: ["biome-scoped tileset definitions in shared schema", "tile_coords as string-keyed IntGrid-to-[col,row] map"]

key-files:
  created: ["tests/test_schema.py", "assets/tilesets/cavern.png"]
  modified: ["assets/entity-schema.json", "main.py", "tests/test_sprite_assets.py"]

key-decisions:
  - "Schema version bumped to 1.0.0 (not 0.7.0) since biomes section is a major structural addition"
  - "tile_coords uses string keys matching intgrid.values keys for consistency"
  - "Original tiles.png kept as fallback until Phase 18 confirms schema-driven loading works"

patterns-established:
  - "Biome tileset files live under assets/tilesets/{biome}.png"
  - "Each biome in schema is self-contained: tileset path, tile_coords, and layers"
  - "Layer definitions include z-order and parallax scroll rate for renderer consumption"

requirements-completed: [SCHEMA-01, SCHEMA-04, TILE-05]

# Metrics
duration: 2min
completed: 2026-04-05
---

# Phase 17 Plan 01: Unified Schema Definition Summary

**entity-schema.json v1.0.0 with biomes.cavern mapping 9 IntGrid values to tile coordinates, 2 rendering layers, and biome-specific tileset at assets/tilesets/cavern.png**

## Performance

- **Duration:** 2 min
- **Started:** 2026-04-05T14:21:20Z
- **Completed:** 2026-04-05T14:23:49Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Extended entity-schema.json to v1.0.0 with biomes section unifying tile and entity definitions (SCHEMA-01)
- Added cavern biome with 9 tile_coords entries covering all active IntGrid values except 0/4 (SCHEMA-04)
- Defined 2 tilemap layers (bg with parallax, terrain at 1:1) with z-order and scroll rates (TILE-05)
- Moved tileset to biome-specific path assets/tilesets/cavern.png and updated all references

## Task Commits

Each task was committed atomically:

1. **Task 1: Create schema validation tests (RED phase)** - `0f948bf` (test)
2. **Task 2: Extend entity-schema.json with biomes section and move tileset** - `6e8f2c7` (feat)

## Files Created/Modified
- `tests/test_schema.py` - 10 schema validation tests covering version, biomes, tile_coords, layers, tileset existence
- `assets/tilesets/cavern.png` - Cavern biome tileset (copied from sprites/tiles.png)
- `assets/entity-schema.json` - v1.0.0 with biomes.cavern section added
- `main.py` - SPRITE_MANIFEST tiles entry updated to new tileset path
- `tests/test_sprite_assets.py` - Updated tileset path assertions to assets/tilesets/cavern.png

## Decisions Made
- Schema version bumped to 1.0.0 (major structural addition of biomes section)
- Kept original assets/sprites/tiles.png as fallback until Phase 18 confirms schema-driven loading
- tile_coords keys are strings matching intgrid.values keys (not integers) for JSON consistency

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Pre-existing test failures in test_map_identification.py (TILE_GATE import) and test_phase05_gaps.py (bat float precision) -- not caused by this plan's changes, documented as out-of-scope.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Schema v1.0.0 ready for Phase 18 (schema-driven loading) to consume biomes.cavern.tile_coords
- Layer definitions ready for Phase 19 (tilemap rendering) to use z-order and scroll rates
- Tileset at biome-specific path ready for multi-biome expansion

## Self-Check: PASSED

- FOUND: tests/test_schema.py
- FOUND: assets/tilesets/cavern.png
- FOUND: assets/entity-schema.json
- FOUND: 17-01-SUMMARY.md
- FOUND: commit 0f948bf
- FOUND: commit 6e8f2c7

---
*Phase: 17-unified-schema-definition*
*Completed: 2026-04-05*
