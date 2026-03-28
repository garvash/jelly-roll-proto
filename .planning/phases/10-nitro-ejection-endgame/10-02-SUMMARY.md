---
phase: 10-nitro-ejection-endgame
plan: 02
subsystem: input
tags: [gamepad, input, controller, pyxel]
dependency_graph:
  requires: []
  provides: [gamepad-input-support]
  affects: [all-abilities, movement, combat]
tech_stack:
  added: []
  patterns: [action-map-extension]
key_files:
  created:
    - tests/test_gamepad.py
  modified:
    - src/core/input.py
decisions:
  - id: D-04
    summary: "Standard platformer button layout: A=Jump, B=Spit, X=Dash, D-pad=movement"
  - id: D-05
    summary: "Extend existing _ACTION_MAP with GAMEPAD1_BUTTON_* constants -- no new code patterns"
metrics:
  duration: "2 minutes"
  completed: "2026-03-28"
---

# Phase 10 Plan 02: Gamepad Controller Support Summary

Gamepad controller support via Pyxel GAMEPAD1_* constants appended to _ACTION_MAP action lists, enabling all 7 game actions on standard gamepad with D-pad and face buttons.

## What Was Done

### Task 1: Add gamepad constants to _ACTION_MAP (TDD)

**RED phase:** Created `tests/test_gamepad.py` with 9 tests verifying all 7 gamepad bindings exist in _ACTION_MAP and keyboard bindings are preserved. Used source-file inspection pattern to avoid Pyxel runtime dependency in tests.

**GREEN phase:** Extended `_ACTION_MAP` in `src/core/input.py` to append one GAMEPAD1_* constant to each action's key list:
- left/right/up/down -> GAMEPAD1_BUTTON_DPAD_LEFT/RIGHT/UP/DOWN
- jump -> GAMEPAD1_BUTTON_A (bottom face button)
- spit -> GAMEPAD1_BUTTON_B (right face button)
- dash -> GAMEPAD1_BUTTON_X (left face button)

No other changes needed -- Pyxel treats gamepad constants identically to keyboard keys through btn/btnp/btnr, so the entire input abstraction layer works with gamepad automatically.

## Commits

| Commit | Type | Description |
|--------|------|-------------|
| 57b44e3 | test | Add failing tests for gamepad button mapping |
| d3b3e56 | feat | Gamepad controller support via _ACTION_MAP (D-04, D-05) |

## Verification

- `python -m pytest tests/test_gamepad.py -x -v` -- 9/9 passed
- `python -m pytest tests/test_input.py -x -q` -- 10/10 passed
- `grep -c "GAMEPAD1" src/core/input.py` -- 7 (one per action)

## Deviations from Plan

None -- plan executed exactly as written.

## Known Stubs

None.

## Self-Check: PASSED

- FOUND: tests/test_gamepad.py
- FOUND: src/core/input.py
- FOUND: 10-02-SUMMARY.md
- FOUND: commit 57b44e3 (test)
- FOUND: commit d3b3e56 (feat)
