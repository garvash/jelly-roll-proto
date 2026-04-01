---
phase: 14-tech-debt-schema-cleanup
plan: 02
subsystem: testing
tags: [debug, god-mode, test-isolation, pyxel]

# Dependency graph
requires: []
provides:
  - "Runtime god-mode debug module (src/core/debug.py) with 3-tier toggles"
  - "Clean constants.py and player.py without DEBUG_ALL_ABILITIES"
  - "All 6 previously failing tests fixed and full suite green"
affects: [any-future-test-plans, gameplay-debugging]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Runtime debug toggles via module-level flags + Ctrl+N key combos"]

key-files:
  created:
    - src/core/debug.py
    - tests/test_debug.py
  modified:
    - src/core/constants.py
    - src/entities/player.py
    - main.py
    - src/entities/items.py
    - tests/test_phase05_gaps.py
    - tests/test_sprite_scale.py

key-decisions:
  - "Runtime god-mode toggles via Ctrl+1/2/3 key combos instead of compile-time constant"
  - "God-mode ability check placed at top of Player.update() for per-frame override"

patterns-established:
  - "Debug flags: module-level booleans in src/core/debug.py, toggled via key combos, never True at import"

requirements-completed: []

# Metrics
duration: 3min
completed: 2026-03-29
---

# Phase 14 Plan 02: Debug Decoupling Summary

**Replaced compile-time DEBUG_ALL_ABILITIES with runtime god-mode toggles (Ctrl+1/2/3) and fixed all 6 failing tests**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-29T15:08:58Z
- **Completed:** 2026-03-29T15:12:21Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments
- Removed DEBUG_ALL_ABILITIES from constants.py and player.py, eliminating import-time side effects that broke tests
- Created src/core/debug.py with 3-tier runtime god-mode toggles (abilities, invincible, infinite juice)
- Fixed all 6 previously failing tests: 3 bubble shield drain, 1 drill retcon, 1 projectile mock, 1 sprite isolation
- Full test suite green: 249 passed, 3 skipped, 0 failures

## Task Commits

Each task was committed atomically:

1. **Task 1: Create debug.py + remove DEBUG_ALL_ABILITIES + fix player.py + wire into Game.update()** - `5df5d1d` (feat)
2. **Task 2: Fix 6 test failures** - `60bb4a4` (fix)

## Files Created/Modified
- `src/core/debug.py` - Runtime god-mode toggles with Ctrl+1/2/3 key combos
- `tests/test_debug.py` - Tests for god-mode defaults and DEBUG_ALL_ABILITIES removal
- `src/core/constants.py` - Removed DEBUG_ALL_ABILITIES constant
- `src/entities/player.py` - Removed DEBUG_ALL_ABILITIES block, added runtime debug.god_abilities check
- `main.py` - Added debug.update() call in Game.update()
- `src/entities/items.py` - Removed legacy "DRILL" key from ITEM_FRAMES dict
- `tests/test_phase05_gaps.py` - Fixed MagicMock level_map returning truthy for check_collision
- `tests/test_sprite_scale.py` - Fixed monkeypatch to use module-path form for pyxel.blt

## Decisions Made
- Runtime god-mode toggles via Ctrl+1/2/3 key combos instead of compile-time constant -- decouples debug playtesting from test execution
- God-mode ability check placed at top of Player.update() so abilities override each frame only when toggled

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Known Stubs
None

## Next Phase Readiness
- Debug module ready for future phases to add more god-mode tiers
- Test suite fully green, ready for Plan 03 execution

---
*Phase: 14-tech-debt-schema-cleanup*
*Completed: 2026-03-29*
