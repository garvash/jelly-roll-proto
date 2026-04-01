---
phase: 12-screen-size-expansion
plan: 01
subsystem: core-constants
tags: [screen-size, constants, refactor, viewport]
dependency_graph:
  requires: []
  provides: [SCREEN_W, SCREEN_H, VIEWPORT_W, VIEWPORT_H, HUD_H, CULL_MARGIN]
  affects: [main.py, world.py, effects.py, boss.py, projectile.py, map.py, player.py]
tech_stack:
  added: []
  patterns: [central-constants, named-viewport-dimensions]
key_files:
  created:
    - tests/test_screen_constants.py
  modified:
    - src/core/constants.py
    - main.py
    - src/level/world.py
    - src/level/map.py
    - src/entities/effects.py
    - src/entities/boss.py
    - src/entities/projectile.py
    - src/entities/player.py
    - tests/test_world_manager.py
    - tests/test_phase05_gaps.py
    - tests/test_phase05_nyquist.py
decisions:
  - Central screen constants in constants.py as single source of truth (D-08)
  - Camera uses VIEWPORT dimensions (320x176), not SCREEN dimensions (320x192)
  - CULL_MARGIN used for boss/projectile boundary instead of hardcoded +16 offset
  - Gate scan loops and tile scan loops derive tile counts from VIEWPORT/TILE_SIZE
metrics:
  duration: 495s
  completed: "2026-03-28T15:14:00Z"
  tasks_completed: 3
  tasks_total: 3
  files_modified: 11
---

# Phase 12 Plan 01: Screen Constants and Magic Number Elimination Summary

Central screen constants (SCREEN_W=320, SCREEN_H=192, VIEWPORT_W=320, VIEWPORT_H=176, HUD_H=16, CULL_MARGIN=16) defined in constants.py with zero hardcoded 128/144 values remaining in production code.

## Completed Tasks

| # | Task | Commit | Key Changes |
|---|------|--------|-------------|
| 1 | Add screen constants (TDD) | cb42260 | constants.py gains 6 constants; test_screen_constants.py with 9 tests |
| 2 | Replace hardcoded 128/144 values | 6521cde | 7 production files updated to import/use named constants |
| 3 | Update test fixtures to 320x176 | 7e5a310 | 3 test files updated with VIEWPORT_W/VIEWPORT_H dimensions |

## Decisions Made

1. **Camera uses VIEWPORT not SCREEN**: WorldManager.SCREEN_W/H set to VIEWPORT_W/H (320x176) so camera math excludes the HUD strip (per RESEARCH Pitfall 1).
2. **CULL_MARGIN replaces +16 offset**: Boss and projectile culling now use `VIEWPORT + CULL_MARGIN` instead of hardcoded 144 (128+16).
3. **Tile scan loops derived from constants**: Gate scan loops in map.py and enemy scan in main.py compute tile counts as VIEWPORT_W // TILE_SIZE instead of hardcoded 16.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed player.py room detection using hardcoded 128**
- **Found during:** Task 2
- **Issue:** `src/entities/player.py` lines 158-159 used `// 128 * 128` for target room detection, not listed in plan inventory
- **Fix:** Replaced with `// VIEWPORT_W * VIEWPORT_W` and `// VIEWPORT_H * VIEWPORT_H`
- **Files modified:** src/entities/player.py
- **Commit:** 6521cde

**2. [Rule 1 - Bug] Fixed map.py gate scan loops using hardcoded tile count 16**
- **Found during:** Task 2
- **Issue:** open_gates/close_gates used `+ 16` tile range (128/8=16), would miss tiles in wider rooms
- **Fix:** Compute `tiles_w = VIEWPORT_W // TILE_SIZE`, `tiles_h = VIEWPORT_H // TILE_SIZE`
- **Files modified:** src/level/map.py
- **Commit:** 6521cde

**3. [Rule 3 - Blocking] Fixed test_phase05_gaps.py test_spawning_logic**
- **Found during:** Task 3
- **Issue:** Test didn't reset `game.enemies` or `game.level_map.entities` before calling `spawn_enemies()`, causing extra enemies with larger room scan
- **Fix:** Added `game.enemies = []` and `game.level_map.entities = []` reset before test assertions
- **Files modified:** tests/test_phase05_gaps.py
- **Commit:** 7e5a310

**4. [Rule 3 - Blocking] Fixed test_phase05_nyquist.py test_room_spawn_update**
- **Found during:** Task 3
- **Issue:** Test moved player to x=200 expecting room transition at 128, but VIEWPORT_W=320 means no transition
- **Fix:** Updated player position to VIEWPORT_W + 50 and assertion to match
- **Files modified:** tests/test_phase05_nyquist.py
- **Commit:** 7e5a310

## Verification Results

1. `python -m pytest tests/ -x -v` -- 68 passed
2. `grep -rn "\b128\b" --include="*.py" src/ main.py` -- zero matches
3. Constants import verification -- OK (SCREEN_W=320, SCREEN_H=192, VIEWPORT_W=320, VIEWPORT_H=176, HUD_H=16)

## Known Stubs

None - all constants are fully wired and operational.

## Self-Check: PASSED
