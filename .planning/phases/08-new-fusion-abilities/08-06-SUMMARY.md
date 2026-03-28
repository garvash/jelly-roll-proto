---
phase: 08-new-fusion-abilities
plan: 06
subsystem: gameplay
tags: [pyxel, charge-shot, windup, state-machine, slime-absorption]

requires:
  - phase: 08-04
    provides: "Charge shot fire_charge_shot() and ChargeProjectile"
provides:
  - "CHARGING_SHOT state with 20-frame windup before charge shot fires"
  - "Slime is_being_absorbed flag for visual feedback during windup"
  - "Input lockout during charge windup"
affects: [gameplay-tuning, visual-polish]

tech-stack:
  added: []
  patterns: ["TDD state machine extension: add state to dispatch, guard, and input handler"]

key-files:
  created:
    - tests/test_charge_shot_windup.py
  modified:
    - src/core/constants.py
    - src/entities/player.py
    - src/entities/slime.py

key-decisions:
  - "CHARGE_WINDUP_DURATION set to 20 frames (~0.33s) for game feel without being sluggish"
  - "D-18 honored: windup is purely cosmetic, always fires at max power"

patterns-established:
  - "Charge shot windup: state entry on Z release, timer countdown, then fire"

requirements-completed: [ABL-04]

duration: 4min
completed: 2026-03-28
---

# Phase 08 Plan 06: Charge Shot Windup Summary

**CHARGING_SHOT state with 20-frame visual windup and slime absorption before charge shot fires (UAT gap 3 fix)**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-28T10:47:57Z
- **Completed:** 2026-03-28T10:52:15Z
- **Tasks:** 1
- **Files modified:** 4

## Accomplishments
- Z release while fused now enters CHARGING_SHOT state with 20-frame windup instead of instant fire
- Slime shows pulsing shrink absorption visual during windup (is_being_absorbed flag)
- Player input locked and movement zeroed during windup
- fire_charge_shot() called only after timer reaches 0 -- logic itself unchanged
- All 8 new tests pass; no regressions in related tests (67 related tests pass)

## Task Commits

Each task was committed atomically:

1. **Task 1 (RED): Add failing tests for charge shot windup** - `b36f3cb` (test)
2. **Task 1 (GREEN): Implement CHARGING_SHOT state with windup and slime absorption** - `85da43b` (feat)

## Files Created/Modified
- `tests/test_charge_shot_windup.py` - 8 tests covering state entry, timer decrement, fire trigger, movement lock, slime absorption
- `src/core/constants.py` - Added CHARGE_WINDUP_DURATION = 20
- `src/entities/player.py` - Added CHARGING_SHOT state, charge_windup_timer, update_charge_shot(), input lockout
- `src/entities/slime.py` - Added is_being_absorbed flag, pulsing shrink draw mode, cleared in reform()/dissipate()

## Decisions Made
- CHARGE_WINDUP_DURATION = 20 frames (~0.33s at 60fps): short enough to feel responsive, long enough for visual feedback
- D-18 strictly honored: no charge levels, no variable power, windup is purely for game feel
- Input fully locked during windup (early return in handle_input) to prevent movement or state changes

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Pre-existing test failure in test_bubble_shield.py::TestShieldDrain::test_water_drain_rate caused by DEBUG_ALL_ABILITIES=True setting has_shield_t2=True which reduces water drain to 0 -- not related to this plan's changes
- Pre-existing test failures in test_phase05_gaps.py and test_phase05_nyquist.py due to room tracking changes -- not related

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Charge shot now has proper game feel with windup animation
- UAT gap 3 (charge shot fires instantly with no feedback) is closed
- Ready for further visual polish or tuning of CHARGE_WINDUP_DURATION if needed

---
*Phase: 08-new-fusion-abilities*
*Completed: 2026-03-28*
