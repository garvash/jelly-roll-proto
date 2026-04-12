---
phase: 27-diagnostic-overlays
plan: 02
subsystem: debug-tools
tags: [pyxel, overlays, input-blips, slime-follow, event-bus, coyote, stuck-detection]

# Dependency graph
requires:
  - phase: 27-01
    provides: Overlay manager with F2/F3 overlays and stub functions for F4/F5
  - phase: 26-animation-system
    provides: event_bus subscribe/emit API for blip placement
provides:
  - F4 input state blip overlay with coyote/buffer spatial visualization
  - F5 slime follow overlay with breadcrumb trail, distance circles, stuck detection
  - Complete main.py integration for all four diagnostic overlays
affects: [28-live-tuning-panel, 29-input-audit, 30-slime-tuning]

# Tech tracking
tech-stack:
  added: []
  patterns: [event bus subscription for blip placement, lazy init guard for idempotent subscriptions, room transition blip clearing via camera snap detection]

key-files:
  created: [src/anim/__init__.py, src/anim/event_bus.py]
  modified: [src/core/overlays.py, main.py, tests/test_overlays.py]

key-decisions:
  - "Constants imported from src.core.constants (SLIME_MAX_DIST, SLIME_REFORM_DIST) instead of tuning.py — matches actual codebase"
  - "Stuck detection counter is overlay-internal state, not entity state — preserves read-only contract"
  - "Test mock isolation uses overlays.pyxel reference instead of sys.modules to prevent cross-suite contamination"
  - "Buffer blip detection checks is_grounded=False AND coyote_timer<=0 to distinguish buffered from normal jumps"

patterns-established:
  - "Event callback pattern: module-level _game_ref for accessing player position in event callbacks"
  - "Room transition detection: camera snap > ROOM_CHANGE_THRESHOLD (160px) clears ephemeral state"
  - "Blip age filtering: skip blips older than BLIP_FADE_FRAMES, split into full-color and dim phases"

requirements-completed: [TOOL-08, TOOL-09]

# Metrics
duration: 18min
completed: 2026-04-12
---

# Phase 27 Plan 02: F4 Input Blips + F5 Slime Overlay Summary

**F4 coyote/buffer spatial blips with event bus subscriptions and F5 slime breadcrumb trail with distance circles and stuck detection, fully wired into main.py game loop**

## Performance

- **Duration:** 18 min
- **Started:** 2026-04-12T09:23:46Z
- **Completed:** 2026-04-12T09:42:17Z
- **Tasks:** 1 of 2 (Task 2 is human-verify checkpoint)
- **Files modified:** 5

## Accomplishments
- F4 input overlay: coyote blips (green) at ground-leave positions, jump blips (red) at jump-press, buffer blips (blue) for airborne presses, connector lines (yellow/pink) showing spatial gaps, active timer pixel indicators
- F5 slime overlay: breadcrumb trail with 3-tier age coloring (green/dark-green/grey), SLIME_MAX_DIST red circle, SLIME_REFORM_DIST yellow circle, pink follow-target dot, flashing red X for stuck detection (vel < 0.1 for 10+ frames), blue catch-up arrow toward target
- Event bus subscriptions for fall_start, jump_start, land with lazy init guard preventing duplicates
- Room transition blip clearing via camera snap detection (> 160px threshold)
- main.py fully wired: overlays.init(self) in __init__, overlays.update() after debug.update(), overlays.draw(self) after player.draw() in world-space, overlays.draw_indicator() after camera reset in screen-space
- 16 total tests (8 from Plan 01, 8 new Plan 02 tests), full suite 319 green

## Task Commits

Each task was committed atomically:

1. **Task 1 (RED): Failing tests for F4/F5 overlays** - `4dbd119` (test)
2. **Task 1 (GREEN): Implement F4/F5 overlays + wire main.py** - `88f8c2d` (feat)

## Files Created/Modified
- `src/core/overlays.py` - Complete overlay module: F4 input blips with event callbacks, F5 slime trail/circles/stuck/catchup, room transition clearing
- `main.py` - Wired overlays.init(), update(), draw(), draw_indicator() at correct game loop positions
- `tests/test_overlays.py` - 16 tests total, fixed mock isolation for cross-suite stability
- `src/anim/__init__.py` - Restored from Phase 26 commit (needed by overlays import)
- `src/anim/event_bus.py` - Restored from Phase 26 commit (subscribe/emit/reset API)

## Decisions Made
- Used `src.core.constants` for SLIME_MAX_DIST/SLIME_REFORM_DIST (plan referenced tuning.py but constants.py is the actual source)
- Test mock isolation: switched from `sys.modules["pyxel"]` to `overlays.pyxel` reference to prevent other test files' pyxel imports from breaking mock comparisons
- Stuck detection uses overlay-internal `_slime_stuck_frames` counter rather than entity state, preserving T-27-01 read-only contract

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed test mock isolation for full-suite stability**
- **Found during:** Task 1 GREEN phase verification
- **Issue:** Original Plan 01 test mock setup used `sys.modules.setdefault("pyxel", MagicMock())` which fails when real pyxel is imported by other test files first. Toggle tests used `sys.modules["pyxel"]` reference which could diverge from overlays module's internal pyxel reference.
- **Fix:** Force-replace `sys.modules["pyxel"]` with mock, delete cached overlays module for re-import, use `overlays.pyxel` in tests for identity comparisons
- **Files modified:** tests/test_overlays.py
- **Commit:** 88f8c2d

**2. [Rule 1 - Bug] Used constants.py instead of tuning.py for SLIME distance thresholds**
- **Found during:** Task 1 implementation
- **Issue:** Plan referenced `tuning.SLIME_MAX_DIST` and `tuning.SLIME_REFORM_DIST` but these constants live in `src/core/constants.py`, not tuning.py
- **Fix:** Import from `src.core.constants` instead
- **Files modified:** src/core/overlays.py
- **Commit:** 88f8c2d

**3. [Rule 3 - Blocking] Restored src/anim/ directory in worktree**
- **Found during:** Task 1 implementation
- **Issue:** Worktree was created from main branch which lacks Phase 26's event_bus module. overlays.py imports event_bus at module level.
- **Fix:** Restored src/anim/__init__.py and src/anim/event_bus.py from Phase 26 commit (33bb7da)
- **Files modified:** src/anim/__init__.py, src/anim/event_bus.py
- **Commit:** 88f8c2d

## Known Stubs

None - all stubs from Plan 01 have been filled in.

## Issues Encountered
- Pre-existing test ordering issue from Plan 01 (pyxel mock setup) discovered during full-suite regression, fixed as deviation #1
- Worktree missing Phase 26 files required for import, fixed as deviation #3

## User Setup Required
None

## Checkpoint Status
Task 2 (human-verify) is pending. User needs to run `python main.py` and verify all four overlays visually.

---
*Phase: 27-diagnostic-overlays*
*Completed: 2026-04-12 (Task 1 only — Task 2 awaiting human verification)*
