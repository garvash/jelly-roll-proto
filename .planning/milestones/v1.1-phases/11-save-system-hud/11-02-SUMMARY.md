---
phase: 11-save-system-hud
plan: 02
subsystem: game-loop
tags: [pyxel, state-machine, save-system, title-screen, death-animation, pause, tdd]

requires:
  - phase: 11-save-system-hud
    provides: SaveManager, SavePoint, capacity constants from Plan 01
provides:
  - "Full game state machine: TITLE/PLAYING/PAUSED/DEAD/WON"
  - "Title screen with Continue/New Game and erase confirmation"
  - "Death rollback to last save with 60-frame animation"
  - "Save point interaction (UP to save) wired into game loop"
  - "Pause toggle via ESC (stub, full implementation in Plan 03)"
  - "Capacity cap enforcement in Item.collect() and restore_from_save()"
  - "restore_from_save() with save room teleportation"
affects: [11-03-hud-pause-menu]

tech-stack:
  added: []
  patterns: [state-machine-dispatch, draw-method-extraction, inline-bounds-check]

key-files:
  created: []
  modified:
    - main.py
    - src/core/input.py
    - src/entities/items.py
    - tests/test_save_system.py
    - tests/test_input.py
    - tests/test_gamepad.py
    - tests/test_phase05_gaps.py
    - tests/test_phase05_nyquist.py

key-decisions:
  - "Fixed SaveManager data structure mismatch: event_flags, visited_rooms, save_room_id are top-level in save JSON, not nested under 'world'"
  - "Extracted _draw_game_world() from draw() so death and pause screens can reuse world rendering"
  - "Added stub methods in Task 1 for Task 2 methods to keep tests passing between commits"

patterns-established:
  - "State machine dispatch at top of update() and draw() with early return"
  - "_draw_game_world extraction pattern for overlay reuse"

requirements-completed: [SYS-01, SYS-03]

duration: 12min
completed: 2026-03-30
---

# Phase 11 Plan 02: Game Loop Wiring Summary

**Full game state machine with title screen, death rollback to save, save point interaction, and capacity cap enforcement**

## Performance

- **Duration:** 12 min
- **Started:** 2026-03-30T15:27:38Z
- **Completed:** 2026-03-30T15:39:34Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments
- Extended game state machine from PLAYING/WON to TITLE/PLAYING/PAUSED/DEAD/WON with proper dispatch
- Title screen with Continue (loads save), New Game, and erase confirmation dialog
- Death animation (30-frame freeze + 30-frame fade) with rollback to last save or return to title
- Save point interaction: walk onto SavePoint entity, press UP to save, see SAVED! confirmation
- Capacity cap enforcement: MAX_HP_CAP=5 and MAX_JUICE_CAP=300 in both Item.collect() and restore_from_save()
- 14 new tests covering state transitions, restore, pause toggle, and capacity caps (30 total in test_save_system.py)

## Task Commits

Each task was committed atomically:

1. **Task 1: Input mappings + state machine dispatch + SavePoint spawning + draw helpers** - `6e55c59` (feat)
2. **Task 2: restore_from_save + title/death methods + pause stub** - `c6ac171` (feat)
3. **Task 3: Game state transition tests + capacity caps** (TDD)
   - `9b8fb79` (test) - Failing tests for state transitions and capacity caps
   - `4abb6fe` (feat) - Enforce capacity caps in Item.collect()

## Files Created/Modified
- `main.py` - Extended with full state machine, title screen, death rollback, save point interaction, restore_from_save, _draw_game_world extraction
- `src/core/input.py` - Added "pause" (ESC/Start) and "confirm" (Z/Enter/A) actions
- `src/entities/items.py` - Added MAX_HP_CAP and MAX_JUICE_CAP enforcement in collect()
- `tests/test_save_system.py` - Added 14 tests: TestGameStates, TestRestoreFromSave, TestPauseToggle, TestCapacityUpgradeCaps
- `tests/test_input.py` - Updated _ACTION_MAP fixture and expected actions for pause/confirm
- `tests/test_gamepad.py` - Updated gamepad binding count from 7 to 9
- `tests/test_phase05_gaps.py` - Added game_state="PLAYING" for gameplay tests
- `tests/test_phase05_nyquist.py` - Added game_state="PLAYING" for gameplay tests

## Decisions Made
- Fixed data structure mismatch between plan and actual SaveManager.save() output: event_flags, visited_rooms, save_room_id are at top level of JSON, not nested under "world" key
- Extracted _draw_game_world() as a separate method so death freeze frame and future pause overlay can reuse the full world rendering pipeline
- Added stub methods in Task 1 (replaced in Task 2) to keep all 267 existing tests passing between atomic commits

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed existing test assertions broken by TITLE default state**
- **Found during:** Task 1
- **Issue:** Several gameplay tests (test_phase05_gaps, test_phase05_nyquist) created Game objects and called update(), but game_state now defaults to "TITLE" instead of "PLAYING", causing update() to dispatch to _update_title and skip gameplay
- **Fix:** Added `game.game_state = "PLAYING"` in affected tests after Game() construction
- **Files modified:** tests/test_phase05_gaps.py, tests/test_phase05_nyquist.py
- **Committed in:** 6e55c59

**2. [Rule 1 - Bug] Updated input test fixture for new actions**
- **Found during:** Task 1
- **Issue:** test_input.py rebuilds _ACTION_MAP in its fixture without pause/confirm, and test_gamepad.py hardcodes gamepad binding count as 7
- **Fix:** Updated _ACTION_MAP rebuild to include pause/confirm with mock keys, updated binding count to 9
- **Files modified:** tests/test_input.py, tests/test_gamepad.py
- **Committed in:** 6e55c59

**3. [Rule 1 - Bug] Fixed restore_from_save data access paths**
- **Found during:** Task 2
- **Issue:** Plan referenced event_flags, visited_rooms, save_room_id under data["world"] but SaveManager.save() stores them at top level
- **Fix:** Used data.get("event_flags"), data.get("visited_rooms"), data.get("save_room_id") at top level
- **Files modified:** main.py
- **Committed in:** c6ac171

---

**Total deviations:** 3 auto-fixed (3 bugs)
**Impact on plan:** All fixes necessary for correctness. No scope creep.

## Known Stubs
- `_update_pause()` and `_draw_pause_overlay()` in main.py are intentional stubs -- full pause menu implementation is in Plan 03 (11-03)

## Issues Encountered
- Plan 01 files were not in the worktree (created by parallel agent); resolved by merging Wave 1 commit (7bf6a54)

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- State machine fully wired, ready for Plan 03 to implement full pause menu with macro-map
- _draw_game_world extraction ready for pause overlay to draw world behind menu
- Save/load flow complete end-to-end: save at SavePoint, load on Continue, rollback on death

## Self-Check: PASSED

All 8 files found. All 4 commits verified.

---
*Phase: 11-save-system-hud*
*Completed: 2026-03-30*
