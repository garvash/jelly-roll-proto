---
phase: 18-schema-driven-integration
plan: 02
subsystem: core-tile-system
tags: [schema, intgrid, refactor, tile-system]
dependency_graph:
  requires: [18-01]
  provides: [schema-driven-tiles, intgrid-collision-data]
  affects: [map.py, constants.py, player.py, main.py]
tech_stack:
  added: []
  patterns: [schema-cache-lazy-init, intgrid-behavior-sets]
key_files:
  created: []
  modified:
    - src/core/constants.py
    - src/level/map.py
    - src/entities/player.py
    - main.py
    - tests/test_map_identification.py
    - tests/test_destruction.py
    - tests/test_persistence.py
    - tests/test_hazard_zones.py
    - tests/test_bubble_shield.py
    - tests/test_ram.py
    - tests/test_cracked_v.py
    - tests/test_goo_mold_removal.py
    - tests/test_schema.py
decisions:
  - Lazy-init schema cache in map.py behavior methods via _ensure_schema_cache() for test compatibility
  - Named INTGRID_CRACKED_H/V constants in player.py instead of magic numbers per project convention
metrics:
  duration: 454s
  completed: "2026-04-05T16:19:33Z"
  tasks_completed: 1
  tasks_total: 1
  files_modified: 13
---

# Phase 18 Plan 02: IntGrid Migration & Constants Cleanup Summary

Schema-driven IntGrid ints replace all hardcoded TILE_* visual constants; collision_data stores ints, behavior checks use schema-built sets, 13 files updated atomically.

## What Changed

### Production Code (4 files)

**src/core/constants.py:** Removed 9 TILE_* visual constants (TILE_SOLID, TILE_HAZARD, TILE_DESTRUCTIBLE, TILE_SWITCH, TILE_CRACKED_H, TILE_CRACKED_V, TILE_WATER, TILE_ACID, TILE_LAVA). Kept TILE_EMPTY = (31, 31) per D-17. Updated HAZARD_DRAIN_RATES keys from tuple to IntGrid ints (6, 7, 8).

**src/level/map.py:** Replaced import block to remove all TILE_* imports. Added `from src.core import schema` and module-level schema cache with lazy initialization via `_ensure_schema_cache()`. `load_from_ldtk_simplified()` now stores IntGrid ints in collision_data and uses schema val_to_tile for visual pset. All behavior methods (is_solid, is_hazard, is_destructible, is_switch) use schema-built sets. `get_zone_hazard_type()` returns IntGrid ints. `restore_tile()` looks up visual coordinates from schema.

**src/entities/player.py:** Added named constants `INTGRID_CRACKED_H = 11` and `INTGRID_CRACKED_V = 12`. Replaced all TILE_CRACKED_H/V references with named IntGrid constants.

**main.py:** Added `from src.core import schema` import. Added `schema.init()` call in Game.__init__ before _load_sprites(). Updated _load_sprites() to use schema-driven tileset path for tiles bank.

### Test Code (9 files)

All test files updated to use IntGrid ints instead of TILE_* constants:
- test_map_identification.py: Uses INTGRID_SOLID/HAZARD/DESTRUCTIBLE ints, added schema.init() fixture
- test_destruction.py: Uses INTGRID_SOLID/DESTRUCTIBLE, added schema.init() in setUp
- test_persistence.py: Uses INTGRID_DESTRUCTIBLE/CRACKED_H/CRACKED_V
- test_hazard_zones.py: Uses INTGRID_WATER/ACID/LAVA/SOLID, verifies int keys in HAZARD_DRAIN_RATES
- test_bubble_shield.py: Replaced TILE_WATER/ACID/LAVA with INTGRID_WATER/ACID/LAVA
- test_ram.py: Removed TILE_CRACKED_H/SOLID imports (unused in assertions)
- test_cracked_v.py: Checks for INTGRID_CRACKED_V in source instead of TILE_CRACKED_V
- test_goo_mold_removal.py: Updated source-text assertion for schema-driven map.py
- test_schema.py: Removed xfail marker from test_no_hardcoded_tile_constants (now passes)

## Decisions Made

1. **Lazy-init schema cache in behavior methods:** Added `_ensure_schema_cache()` calls to is_solid, is_hazard, is_destructible, is_switch, get_zone_hazard_type, and restore_tile. The None check is O(1) after first call, ensuring tests that directly set collision_data work without requiring explicit schema cache initialization.

2. **Named INTGRID constants in player.py:** Used `INTGRID_CRACKED_H = 11` and `INTGRID_CRACKED_V = 12` instead of magic numbers, following the project convention of avoiding magic numbers (from MEMORY.md).

## Deviations from Plan

None - plan executed exactly as written.

## Verification

- `python -m pytest tests/ -q --ignore=tests/test_phase05_gaps.py`: 311 passed, 5 pre-existing failures (unrelated to tile system)
- `grep -r "TILE_SOLID\|TILE_HAZARD\|..." src/ --include="*.py"`: Zero matches
- All 19 acceptance criteria verified passing

## Known Pre-existing Test Failures

These failures exist before and after the refactor (not caused by this plan):
- test_phase05_gaps.py::test_bat_returning_state (bat y-value assertion)
- test_phase05_nyquist.py::test_input_ignored_during_knockback (knockback dx)
- test_phase05_nyquist.py::test_room_spawn_update (spawn position)
- test_ram.py::TestRamCollision::test_ram_snaps_to_wall_left (wall snap)
- test_save_system.py::TestGameStates::test_death_timer_increments (death timer)
- test_slime.py::test_drill_dive_activation (drill activation cost)

## Known Stubs

None -- all data paths are fully wired to schema.py.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1    | e56b0be | Atomic refactor of 4 production + 9 test files for IntGrid migration |
