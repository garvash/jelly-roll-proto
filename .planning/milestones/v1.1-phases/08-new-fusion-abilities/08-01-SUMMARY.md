---
phase: 08-new-fusion-abilities
plan: 01
subsystem: input
tags: [pyxel, input-abstraction, wasd, keybinding]

requires:
  - phase: 07-macro-map-room-persistence
    provides: WorldManager and room-based gameplay loop
provides:
  - Input abstraction module (src/core/input.py) with btn/btnp/btnr/update/hold_frames/was_tap
  - WASD+JK secondary key mapping for all player controls
  - Hold duration tracking for tap-vs-hold detection
affects: [08-02, 08-03, 08-04, input, player, fusion-abilities]

tech-stack:
  added: []
  patterns: [input-abstraction-layer, logical-action-mapping]

key-files:
  created: [src/core/input.py, tests/test_input.py]
  modified: [src/entities/player.py, tests/test_physics.py, tests/test_slime.py, tests/test_phase05_gaps.py, tests/test_phase05_nyquist.py]

key-decisions:
  - "Input module uses logical action names (left/right/jump/spit/dash) mapped to physical key lists"
  - "Hold duration tracked via _prev_hold_frames for accurate was_tap detection on release frame"
  - "input_manager.update() called as first line of Player.update() before any input checks"

patterns-established:
  - "Input abstraction: all new input checks must use input_manager.btn/btnp/btnr, never raw pyxel calls"
  - "Test mock pattern: tests must patch src.entities.player.input_manager (not pyxel) for input assertions"

requirements-completed: []

duration: 7min
completed: 2026-03-28
---

# Phase 08 Plan 01: Input Abstraction Layer Summary

**Input abstraction module with WASD+JK secondary mapping and hold duration tracking for tap-vs-hold detection**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-28T06:00:05Z
- **Completed:** 2026-03-28T06:07:13Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- Created src/core/input.py with full API: btn, btnp, btnr, update, hold_frames, was_tap
- Migrated all 13 direct pyxel input calls in player.py to use input abstraction
- WASD+JK secondary mapping (D-09) now works automatically for all existing controls
- 10 unit tests covering primary/secondary keys, hold tracking, and tap detection

## Task Commits

Each task was committed atomically:

1. **Task 1: Create input abstraction module and test scaffold** - `ab0f33f` (feat)
2. **Task 2: Migrate all player.py input calls to use input module** - `0347a41` (feat)

## Files Created/Modified
- `src/core/input.py` - Input abstraction layer with action-to-key mapping and hold tracking
- `tests/test_input.py` - 10 unit tests for input module
- `src/entities/player.py` - All pyxel.btn/btnp/btnr calls replaced with input_manager equivalents
- `tests/test_physics.py` - Updated to mock input_manager instead of pyxel for input assertions
- `tests/test_slime.py` - Updated drill dive activation test to use input_manager mock
- `tests/test_phase05_gaps.py` - Added input module mock to integration test setup
- `tests/test_phase05_nyquist.py` - Updated knockback and room spawn tests for input_manager

## Decisions Made
- Input module uses logical action names mapped to physical key lists, allowing easy remapping
- Hold duration tracking stores previous frame's hold count for accurate release-frame tap detection
- input_manager.update() placed as first call in Player.update() to ensure frame-accurate tracking

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed test mock isolation for input module**
- **Found during:** Task 2 (migration verification)
- **Issue:** When tests run in alphabetical order, src.core.input gets imported with the first test file's mock_pyxel, causing test_input.py's mock to be ignored
- **Fix:** Added pyxel reference swap and _ACTION_MAP rebuild in test_input.py's autouse fixture
- **Files modified:** tests/test_input.py
- **Verification:** All 10 input tests pass regardless of test ordering
- **Committed in:** 0347a41 (Task 2 commit)

**2. [Rule 3 - Blocking] Updated existing tests to use input_manager mock**
- **Found during:** Task 2 (full suite verification)
- **Issue:** Tests that patched src.entities.player.pyxel for input assertions no longer worked because player.py now uses input_manager
- **Fix:** Updated test_physics.py, test_slime.py, test_phase05_gaps.py, test_phase05_nyquist.py to patch input_manager
- **Files modified:** tests/test_physics.py, tests/test_slime.py, tests/test_phase05_gaps.py, tests/test_phase05_nyquist.py
- **Verification:** 86/89 tests pass (3 pre-existing failures unrelated to this plan)
- **Committed in:** 0347a41 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking)
**Impact on plan:** Both fixes necessary for test suite correctness after migration. No scope creep.

## Issues Encountered
- 3 pre-existing test failures (test_duplication_prevention, test_combat_projectile_collision, test_room_spawn_update) unrelated to input migration -- these tests use outdated assumptions about room tracking and combat logic from Phase 7 refactoring

## Known Stubs
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Input abstraction layer ready for all subsequent Phase 8 plans
- Plan 02 can use input_manager for kick removal and drill retcon
- Plan 03 can use hold_frames/was_tap for charge-to-fuse mechanic

---
*Phase: 08-new-fusion-abilities*
*Completed: 2026-03-28*
