---
phase: 08-new-fusion-abilities
plan: 05
subsystem: player-slime-mechanics
tags: [bugfix, uat-gap-closure, tdd]
dependency_graph:
  requires: [08-04]
  provides: [reposition-follow-fix, ram-wall-snap]
  affects: [player.py, slime.py]
tech_stack:
  added: []
  patterns: [save-direction-before-state-change, reposition-vs-hold-position-separation]
key_files:
  created:
    - tests/test_tap_reposition.py
  modified:
    - src/entities/slime.py
    - src/entities/player.py
    - tests/test_ram.py
decisions:
  - "Separated reposition() from hold_position() rather than adding a flag parameter, keeping each method single-purpose"
  - "Saved movement direction as local variable before end_ram rather than changing end_ram signature"
metrics:
  duration: 225s
  completed: 2026-03-28T10:51:00Z
  tasks: 2
  tests_added: 10
  tests_total: 20
---

# Phase 08 Plan 05: UAT Gap Closure (Reposition Follow + Ram Wall Embed) Summary

Fixed two UAT-reported bugs: tap reposition killing slime follow behavior, and ram embedding player inside walls. Both fixes use TDD with 10 new tests.

## What Was Done

### Task 1: Fix tap reposition -- add Slime.reposition() (1465c3a)
- Added `Slime.reposition()` method that moves slime to a new position without setting `is_holding_position = True`
- Rewired `Player.handle_input()` tap LEFT/RIGHT path from `slime.hold_position()` to `slime.reposition()`
- `hold_position()` preserved for future long-hold mechanics
- 8 new tests in `tests/test_tap_reposition.py` verify: follow state preserved, position changes, history cleared, velocity zeroed, punt cleared

### Task 2: Fix ram wall embed -- save dx before end_ram (9306d74)
- Root cause: `end_ram()` zeroed `self.dx` before snap-to-surface code checked direction
- Fix: save `move_direction = self.dx` before any ram logic, use saved value for snap calculation
- 2 new tests in `tests/test_ram.py` verify right and left ram snap to wall surface
- All 12 existing ram tests continue to pass

## Deviations from Plan

None - plan executed exactly as written.

## Verification

- `python -m pytest tests/test_tap_reposition.py tests/test_ram.py -x -v` -- 20/20 passed
- `python -m pytest tests/test_slime_hold.py -x -v` -- 6/6 passed (existing hold tests unbroken)

## Known Stubs

None.

## Self-Check: PASSED
