---
phase: 20-grid-constants-schema-metadata
plan: 02
subsystem: tests, documentation
tags: [grid-migration, tests, schema, converter-docs]
dependency_graph:
  requires: [20-01]
  provides: [grid-contract-tests, schema-version-tests, converter-doc-update]
  affects: [tests/test_sprite_scale.py, tests/test_schema.py, "PML-to-LDtk Converter.md"]
tech_stack:
  added: []
  patterns: [contract-tests, importability-guard]
key_files:
  created: []
  modified:
    - tests/test_sprite_scale.py
    - tests/test_schema.py
    - "PML-to-LDtk Converter.md"
decisions:
  - Removed draw_sprite offset and load_sprite_tags tests from test_sprite_scale.py (Phase 22 scope / unrelated to grid constants)
metrics:
  duration: 78s
  completed: "2026-04-08T02:12:06Z"
---

# Phase 20 Plan 02: Test Rewrite and Converter Doc Update Summary

Contract tests asserting 16x16 grid migration: TILE_SIZE==16, SPRITE_SIZE==16, BOSS_SPRITE_SIZE==32, TILE_EMPTY==(15,15), SPRITE_SCALE removal via ImportError, schema v2.0.0 with grid_size==16, plus converter doc updated to 16px/20x11 rooms.

## Tasks Completed

### Task 1: Rewrite test_sprite_scale.py and update test_schema.py
- **Commit:** 2276ec3
- Complete rewrite of test_sprite_scale.py: 5 focused contract tests replacing 5 old Phase 13 tests
- Removed obsolete SPRITE_SCALE==2 assertion, SPRITE_SIZE derivation test, draw_sprite offset test, load_sprite_tags test
- Added SPRITE_SCALE ImportError guard test
- Updated test_schema.py: version assertion 1.0.0 -> 2.0.0, added grid_size==16 test
- All 27 tests pass

### Task 2: Update PML-to-LDtk Converter.md
- **Commit:** e2f7e92
- Tile size: 8px -> 16px
- Standard room tiles: 40x22 -> 20x11
- Tall shaft tiles: 40x44 -> 20x22
- Wide arena tiles: 80x22 -> 40x11
- Zero stale 8px references remain

## Verification

- `python -m pytest tests/test_sprite_scale.py tests/test_schema.py tests/test_screen_constants.py -x -q` -- 36 passed
- No stale 8px, 40x22, or SPRITE_SCALE references in any modified file (except comment/test explaining removal)

## Deviations from Plan

None -- plan executed exactly as written.

## Known Stubs

None.

## Self-Check: PASSED

- All 3 modified files exist on disk
- Both task commits (2276ec3, e2f7e92) verified in git log
