---
phase: 26-event-bus-animation-fsm-skeleton
plan: 01
subsystem: animation
tags: [anim, event-bus, fsm, skeleton, tdd]
dependency_graph:
  requires: []
  provides: [src/anim/event_bus.py, src/anim/anim_clip.py, src/anim/anim_player.py, src/anim/state_machine.py, src/anim/player_anim.py]
  affects: [tests/test_anim.py, tests/test_event_bus.py]
tech_stack:
  added: []
  patterns: [dataclass-frozen-slots, module-level-singleton, rules-list-evaluator, check-then-increment-tick]
key_files:
  created:
    - src/anim/__init__.py
    - src/anim/event_bus.py
    - src/anim/anim_clip.py
    - src/anim/anim_player.py
    - src/anim/state_machine.py
    - src/anim/player_anim.py
    - tests/test_anim.py
    - tests/test_event_bus.py
  modified: []
decisions:
  - "AnimPlayer uses check-then-increment tick model: frame persists for full duration before advancing, matching v1.3 pyxel.frame_count // N semantics"
metrics:
  duration: 369s
  completed: 2026-04-12T04:40:42Z
  tasks: 2
  files: 8
---

# Phase 26 Plan 01: Event Bus + Animation Package Skeleton Summary

Standalone `src/anim/` package with 6 files (5 source + `__init__.py`) implementing the pub-sub event bus, AnimClip frozen dataclass, AnimPlayer tick-driven frame counter, AnimFSM rules-list evaluator, and PlayerAnimDriver wiring with v1.3 frame parity for all 11 player states.

## What Was Done

### Task 1: event_bus + anim_clip + anim_player (TDD)

Created the foundation modules:

- **`src/anim/__init__.py`** -- empty package marker
- **`src/anim/event_bus.py`** -- module-level singleton with `subscribe()`, `emit()`, `reset()` per D-13a. No class wrapper, synchronous dispatch.
- **`src/anim/anim_clip.py`** -- `@dataclass(frozen=True, slots=True)` with frames/durations/loop/events fields. `__post_init__` validates length match. `events` dict reserved for Phase 31 ANIM-04.
- **`src/anim/anim_player.py`** -- Frame ticker with `set_clip()` (D-07 reset), `tick()` (check-then-increment), `current_u()`. `loop=False` holds on last frame. No pyxel import.

Tests: 4 in `test_event_bus.py`, 6 in `test_anim.py`.

### Task 2: state_machine + player_anim (TDD)

Created the decision and wiring modules:

- **`src/anim/state_machine.py`** -- `AnimFSM` class with construction-time clip_id validation. `current_frame_u(driver)` walks rules first-match, triggers D-07 set_clip on clip change, ticks, returns u offset. `RuntimeError` on missing fallback (unreachable per D-06).
- **`src/anim/player_anim.py`** -- `PlayerAnimDriver` slotted dataclass (4 fields per D-01), `PLAYER_CLIPS` dict (idle/run/jump), `PLAYER_RULES` list (3 rules + D-06 fallback), `build_player_fsm()` factory. All sprite offsets and durations use named constants.

Tests: 10 new in `test_anim.py` (FSM validation, first-match, clip-change reset, driver slots, build factory, 4 state parity, 6 fallback states).

## Verification Results

- Full package import: `from src.anim import event_bus, anim_clip, anim_player, state_machine, player_anim` -- PASS
- Test suite: `python -m pytest tests/test_anim.py tests/test_event_bus.py -x -q` -- 20 passed in 0.08s
- No pyxel imports: `grep -rn "^import pyxel\|^from pyxel" src/anim/` -- zero matches
- No magic numbers: all literals use named constants (IDLE_U, RUN_FRAME_A_U, RUN_FRAME_B_U, JUMP_U, STATIC_CLIP_DURATION_TICKS, RUN_TOGGLE_DURATION_TICKS)
- v1.3 RUNNING parity: 12 ticks of RUN_FRAME_A_U (16) then 12 of RUN_FRAME_B_U (32) -- verified
- JUMPING/FALLING parity: constant JUMP_U (32) -- verified
- IDLE parity: constant IDLE_U (0) -- verified
- Fallback states (WALL_SLIDING, DIVING, RAMMING, DASHING, BOOSTING, CHARGING_SHOT): all render IDLE_U -- verified

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] AnimPlayer tick model corrected to check-then-increment**
- **Found during:** Task 1 GREEN phase
- **Issue:** The plan's code example used increment-then-check (`self._clip_ticks += 1` first, then `while >= duration`), which causes frames to advance one tick early. With `durations=[2,2]`, this produces `[0, 16, 16, 0]` instead of the plan-specified `[0, 0, 16, 16]`.
- **Fix:** Changed to check-then-increment: the duration threshold check runs BEFORE the counter increment, so frames persist for their full duration count before advancing. This matches v1.3 `pyxel.frame_count // 12` semantics where frame 0 shows for ticks 0-11.
- **Files modified:** `src/anim/anim_player.py`
- **Commit:** 425965c

## Decisions Made

1. **Check-then-increment tick model**: AnimPlayer checks if the accumulated ticks have reached the current frame's duration BEFORE incrementing the tick counter. This means a frame with `duration=N` is displayed for exactly N calls to `tick()`, matching v1.3's integer-division-based frame selection.

## Known Stubs

None -- all modules are fully functional within their Phase 26 scope. The `events` field on `AnimClip` is an intentional Phase 31 reservation, not a stub.

## Commits

| Task | Type | Hash | Description |
|------|------|------|-------------|
| 1 RED | test | 91777fc | add failing anim_clip/anim_player/event_bus tests |
| 1 GREEN | feat | 425965c | implement event_bus + anim_clip + anim_player modules |
| 2 RED | test | a6b106a | add failing AnimFSM + player parity tests |
| 2 GREEN | feat | d58acec | implement AnimFSM + player_anim module |

## Self-Check: PASSED

- All 8 created files exist on disk
- All 4 commit hashes found in git log
- 20/20 tests pass in 0.08s
