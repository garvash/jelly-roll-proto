---
phase: 21-tileset-ldtk-pipeline
plan: 01
subsystem: ldtk-pipeline
tags: [migration, ldtk, tileset, 16px, intgrid]
dependency_graph:
  requires: [20-01, 20-02]
  provides: [migrated-output-ldtk, 16px-intgrid, cavern-tileset]
  affects: [map.py-autotile-loading, entity-schema, simplified-exports]
tech_stack:
  added: []
  patterns: [json-load-dump-patching, stride-2-downsampling, round-to-nearest-snap]
key_files:
  created:
    - scripts/migrate_ldtk_16px.py
    - tests/test_ldtk_migration.py
  modified:
    - assets/output.ldtk
    - assets/entity-schema.json
    - assets/tilesets/cavern.png
    - assets/output/simplified/Level_*/IntGrid.csv
    - assets/output/simplified/Level_*/data.json
    - tests/test_schema.py
    - tests/test_sprite_assets.py
    - tests/test_tilemap.py
  deleted:
    - assets/tileset.png
decisions:
  - "Migration script patches JSON programmatically -- no LDtk editor needed (D-08)"
  - "Auto-tile filtering keeps top-left of 2x2 blocks at 16px-aligned positions (D-10)"
  - "Entity snap uses round-to-nearest, not floor (D-13, D-14)"
  - "tileset.png deleted, tilesets/cavern.png is single source of truth (D-04, D-07)"
metrics:
  duration_seconds: 326
  completed: "2026-04-08T04:59:54Z"
  tasks_completed: 3
  tasks_total: 3
  files_created: 2
  files_modified: 41
---

# Phase 21 Plan 01: LDtk 8px-to-16px Migration Summary

Reproducible migration script converting output.ldtk, simplified exports, and entity-schema from 8px to 16px grid with IntGrid downsampling, auto-tile filtering, and entity position snapping.

## What Was Done

### Task 1: Create and run migration script
**Commit:** f9581f8

Created `scripts/migrate_ldtk_16px.py` (270+ lines) performing a complete one-command migration:
- File moves: tiles.png -> tilesets/cavern.png, deleted tileset.png
- output.ldtk patching: defaultGridSize 8->16, tileset defs (uid=64: relPath, pxWid/pxHei 256x256, tileGridSize 16, cWid/cHei 16), layer gridSizes, 47 auto-rule tileRectsIds recalculated (12-col -> 16-col)
- Level data: intGridCsv downsampled from 40x22 to 20x11 (stride-2, top-left wins), autoLayerTiles filtered to 16px-aligned positions with src coords doubled, entity positions snapped to nearest 16px
- Simplified exports: 18 level directories patched (IntGrid.csv downsampled, data.json entity positions snapped)
- entity-schema.json tileset path updated to assets/tilesets/cavern.png
- Only 2 entities required snapping: PlayerStart y=88->96, SavePoint x=152->160

### Task 2: Update existing tests for 16px values
**Commit:** 6c2ec26

- test_schema.py: tileset path assertions updated from "assets/tiles.png" to "assets/tilesets/cavern.png" (2 locations)
- test_sprite_assets.py: TILE_SOLID pixel check updated from pget(0,8) to pget(0,16)
- test_tilemap.py: __gridSize metadata updated from 8 to 16 in test helper

### Task 3: Create regression test for migration output (D-25)
**Commit:** 9023858

Created `tests/test_ldtk_migration.py` with 7 test functions:
1. test_ldtk_default_grid_size_is_16
2. test_intgrid_csv_dimensions_20x11
3. test_autotile_src_coords_16px_aligned
4. test_entity_positions_16px_snapped
5. test_tileset_relpath_cavern
6. test_layer_grid_sizes_are_16
7. test_autotile_px_positions_16px_aligned

## Deviations from Plan

### Deviation 1: tiles.aseprite not found
The plan specified copying tiles.aseprite -> tilesets/cavern.aseprite, but tiles.aseprite does not exist in the repository. The script handles this gracefully (logs info, continues). No impact -- the PNG is the authoritative asset.

### Deviation 2: test_tilemap.py coordinate assertions not updated
The plan specified updating coordinate assertions in test_autotiles_on_tilemap and test_autotiles_parsed to use 16px math. However, map.py still uses hardcoded `grid_size = 8` (line 181), which is scheduled for update in plan 21-02. Updating test assertions now would break tests. Only the `__gridSize` metadata was updated to 16. The coordinate assertion updates will happen alongside the map.py code change in 21-02.

## Known Stubs

None -- all changes are fully wired and functional.

## Self-Check: PASSED

All artifacts verified: 2 files created, 41 files modified, 1 file deleted. All 3 commits found in git log.
