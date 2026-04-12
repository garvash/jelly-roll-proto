---
phase: 26-event-bus-animation-fsm-skeleton
plan: 02
subsystem: animation
tags: [anim, fsm, player-wiring, parity, tdd]
dependency_graph:
  requires: [src/anim/player_anim.py, src/anim/state_machine.py, src/anim/anim_clip.py, src/anim/anim_player.py]
  provides: [Player._anim, Player._anim_driver, Player._update_anim_driver]
  affects: [src/entities/player.py, tests/test_anim.py, src/anim/player_anim.py]
tech_stack:
  added: []
  patterns: [driver-fed-fsm, in-place-mutation-D16, last-call-D14]
key_files:
  created: []
  modified:
    - src/entities/player.py
    - src/anim/player_anim.py
    - tests/test_anim.py
decisions:
  - "RUN_TOGGLE_DURATION_TICKS corrected from 12 to 6 to match actual player.py hardcoded formula (// 6 not // 12)"
metrics:
  duration: 361s
  completed: 2026-04-12T05:11:55Z
  tasks: 1
  files: 3
---

# Phase 26 Plan 02: Wire Player to AnimFSM Summary

Replaced hardcoded sprite frame toggle in Player.draw() with AnimFSM.current_frame_u() lookup, wiring the Reanimator-style driver architecture from plan 26-01 into the live player entity with frame-for-frame v1.3 parity (6-tick run toggle).

## What Was Done

### Task 1: Wire Player.__init__, _update_anim_driver(), update() end, and draw() (TDD)

**RED commit** (`7f63711`): Added 8 failing Player-instance-level tests to tests/test_anim.py:
- `test_player_init_constructs_driver_and_fsm` -- verifies _anim_driver and _anim attrs exist
- `test_player_driver_is_single_instance` -- D-16: id() unchanged after mutation
- `test_player_update_anim_driver_reflects_state` -- state/facing/vy_sign/is_grounded reflect player fields
- `test_player_draw_u_running_parity` -- 6x RUN_FRAME_A + 6x RUN_FRAME_B (v1.3 match)
- `test_player_draw_u_jumping_parity` -- constant JUMP_U
- `test_player_draw_u_falling_parity` -- constant JUMP_U
- `test_player_draw_u_idle_parity` -- constant IDLE_U
- `test_player_draw_u_fallback_parity` -- 6 fallback states all produce IDLE_U (D-06)

Also added pyxel mock harness (sys.modules["pyxel"] = MagicMock()) at file top and mock_level/mock_slime fixtures.

**GREEN commit** (`1ac619b`): Implemented all 5 steps in player.py:
1. Import: `from src.anim.player_anim import PlayerAnimDriver, build_player_fsm`
2. __init__: `self._anim_driver = PlayerAnimDriver()` + `self._anim = build_player_fsm()`
3. New method `_update_anim_driver()` mutates driver in place (D-16) with state, is_grounded, facing, vy_sign
4. update() ends with `self._update_anim_driver()` after `self.update_state()` (D-14)
5. draw() replaced 7-line hardcoded block with single `u = self._anim.current_frame_u(self._anim_driver)`

Player.py diff: +14 lines, -7 lines (net +7). Total lines: 817.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] RUN_TOGGLE_DURATION_TICKS parity mismatch**
- **Found during:** Task 1 GREEN phase
- **Issue:** Plan 26-01 set `RUN_TOGGLE_DURATION_TICKS = 12` in player_anim.py, referencing `// 12` in the comment. However, the actual hardcoded formula in player.py is `pyxel.frame_count // 6 % 2`, meaning 6 frames per sprite frame, not 12.
- **Fix:** Changed constant from 12 to 6 in src/anim/player_anim.py. Updated comment to reference `// 6`. Updated existing test_running_parity to handle the new cycle length correctly (48 ticks = 8 half-cycles at 6 ticks each).
- **Files modified:** src/anim/player_anim.py, tests/test_anim.py
- **Commit:** 1ac619b

## Verification Results

All acceptance criteria passed:
- Hardcoded `u = 16 + (pyxel.frame_count // 6 % 2) * 16` line removed from player.py
- Hardcoded `u = 32 # Use run1` jump/fall literal removed from player.py
- `self._anim.current_frame_u` appears 1 time in player.py (draw)
- `_update_anim_driver` appears 2 times in player.py (definition + call site)
- `from src.anim.player_anim import` appears 1 time in player.py
- `self._anim_driver` appears 4 times in player.py (init + method body fields + draw arg)
- D-14 grep confirms `_update_anim_driver` immediately follows `update_state()`
- All 24 anim tests pass (16 from 26-01 + 8 new from 26-02)
- Full test suite: 331 passed, 3 skipped, 0 failed

## Notes for Downstream Plans

- Plan 26-03 now owns adding event_bus.emit() calls and must NOT modify the animation path established here
- `self.dy` is the correct field name for vertical velocity (matches D-03 formula)
- The `SPRITE_SIZE` constant in the draw_sprite call comes from `src.core.constants` (star import), not from tuning -- unchanged from pre-Phase-26

## Self-Check: PASSED
