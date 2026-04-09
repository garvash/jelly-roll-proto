---
phase: 20-grid-constants-schema-metadata
plan: 01
subsystem: core/constants, schema
tags: [grid-migration, tile-size, schema-version]
dependency_graph:
  requires: []
  provides: [TILE_SIZE-16, entity-schema-v2, export-16-tiles-per-row]
  affects: [all-entity-files, level-map, schema-py, tests]
tech_stack:
  added: []
  patterns: [direct-constants-no-indirection]
key_files:
  created: []
  modified:
    - src/core/constants.py
    - assets/entity-schema.json
    - export_tilemap_csv.py
decisions:
  - SPRITE_SCALE removed entirely rather than set to 1 -- eliminates indirection layer
  - Schema version bumped to 2.0.0 (major) since grid_size change is breaking
metrics:
  duration: 112s
  completed: 2026-04-08
---

# Phase 20 Plan 01: Grid Constants, Schema Metadata, and Export Script Summary

TILE_SIZE flipped to 16, SPRITE_SCALE removed, entity-schema bumped to v2.0.0 with grid_size=16, export script updated for 16 tiles per row.

## What Changed

### Task 1: constants.py (e38501e)
- `TILE_SIZE` changed from 8 to 16
- Removed `SPRITE_SCALE` (was 2) and its derived formulas
- `SPRITE_SIZE = 16` and `BOSS_SPRITE_SIZE = 32` are now direct constants
- `TILE_EMPTY` changed from `(31, 31)` to `(15, 15)` (256/16=16 tiles, max index=15)

### Task 2: entity-schema.json (ea40584)
- Version bumped from `1.0.0` to `2.0.0` (breaking grid change)
- `grid_size` changed from 8 to 16
- `variable_rooms_note` updated: 40x22 -> 20x11, 40x44 -> 20x22
- `tile_coords` description updated from "8px tile grid" to "16px tile grid"
- All actual tile coordinate values left unchanged (Phase 21 scope)

### Task 3: export_tilemap_csv.py (047c636)
- `tile_id` formula changed from `v * 32 + u` to `v * 16 + u`
- Comments updated to reflect 16px grid math (20 tiles wide, 11 tiles tall, 16 tiles per row)

## Deviations from Plan

None -- plan executed exactly as written.

## Known Stubs

None.

## Verification Results

```
TILE_SIZE=16, SPRITE_SIZE=16, BOSS_SPRITE_SIZE=32, TILE_EMPTY=(15, 15)
version=2.0.0, grid_size=16
SPRITE_SCALE import raises ImportError (confirmed removed)
export script: v*16+u present, v*32 absent, file parses cleanly
```

## Self-Check: PASSED

- [x] src/core/constants.py modified (e38501e)
- [x] assets/entity-schema.json modified (ea40584)
- [x] export_tilemap_csv.py modified (047c636)
- [x] All commits verified in git log
