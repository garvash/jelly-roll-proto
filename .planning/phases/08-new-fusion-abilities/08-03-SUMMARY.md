---
phase: 08-new-fusion-abilities
plan: 03
subsystem: fusion-mechanics
tags: [fusion, recall, mana-shield, dissipation, directional-hold, slime]

requires:
  - phase: 08-new-fusion-abilities
    plan: 02
    provides: Basic dash, kick removal, drill retcon to DOWN+V, input abstraction
provides:
  - Fusion system core (recall, fuse/unfuse, mana shield, dissipation cycle)
  - Directional slime hold (tap LEFT/RIGHT to reposition companion)
  - Spit-on-release for clean Z button separation from recall hold
affects: [08-04, player, slime, combat, enemies, boss]

tech-stack:
  added: []
  patterns: [fuse-unfuse-atomic-pair, mana-shield-damage-absorb, recall-zip-movement]

key-files:
  created: [tests/test_fusion.py, tests/test_slime_hold.py]
  modified: [src/core/constants.py, src/entities/slime.py, src/entities/player.py, src/entities/enemies.py, src/entities/boss.py, main.py, tests/test_slime.py]

key-decisions:
  - "fuse/unfuse are single-point-of-truth methods (Pitfall 3): only fuse() sets is_fused=True, only unfuse() clears it"
  - "Mana shield absorbs all damage while fused at MANA_SHIELD_COST per hit; juice empty triggers dissipation"
  - "Spit fires on Z release (was_tap) for clean separation from hold-to-recall (Pitfall 2)"
  - "Enemy/boss take_damage calls now pass slime for mana shield to work on contact damage"

patterns-established:
  - "Fusion state pair: always use player.fuse(slime)/unfuse(slime) instead of bare is_fused assignments"
  - "Slime state hierarchy: dissipated > recalling > fused > holding > punted > following"
  - "Enemy slime passthrough: enemies pass slime=slime to player.take_damage for mana shield"

requirements-completed: [ABL-03]

duration: 7min
completed: 2026-03-28
---

# Phase 08 Plan 03: Fusion System Core and Directional Slime Hold Summary

**Recall-to-fuse cycle with mana shield damage absorption, dissipation cooldown, and tap-to-reposition companion slime**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-28T06:19:43Z
- **Completed:** 2026-03-28T06:27:00Z
- **Tasks:** 1/1
- **Files modified:** 9

## Accomplishments
- Implemented full fusion cycle: hold Z to recall slime, auto-fuse at max juice, mana shield absorbs hits, dissipation on juice empty with cooldown reform
- Added directional slime hold: tap LEFT/RIGHT repositions slime, hold walks normally (ABL-03)
- Created fuse/unfuse as atomic operations ensuring player and slime state always sync (Pitfall 3)
- Updated all enemy/boss damage paths to pass slime for mana shield compatibility
- 16 new tests across 2 test files covering fusion and directional hold mechanics

## Task Commits

Each task was committed atomically:

1. **Task 1: Add fusion constants, recall, fuse/unfuse, mana shield, dissipation, and directional hold** - `f3618b3` (feat)

## Files Created/Modified
- `src/core/constants.py` - Added RECALL_SPEED, MANA_SHIELD_COST, SLIME_DISSIPATE_COOLDOWN, SPIT_HOLD_THRESHOLD, HOLD_TAP_THRESHOLD, RECALL_TRAIL_COLOR
- `src/entities/slime.py` - Added recall(), update_recall(), dissipate(), update_dissipation(), hold_position(), recall trail drawing, dissipated/holding states
- `src/entities/player.py` - Added fuse()/unfuse() methods, mana shield in take_damage, recall charging logic, directional hold input, spit-on-release pattern
- `src/entities/enemies.py` - Updated Snail/Bat update() and take_damage calls to pass slime
- `src/entities/boss.py` - Updated BossRock/Mole update() and take_damage calls to pass slime
- `main.py` - Updated enemy/boss update calls to pass slime=self.slime
- `tests/test_fusion.py` - 10 tests: fuse/unfuse flags, mana shield, recall movement, dissipation timer
- `tests/test_slime_hold.py` - 6 tests: hold position, direction, punt cancel, hold persistence, reform distance
- `tests/test_slime.py` - Fixed drill dive test to mock was_tap and hold_frames for new input pattern

## Decisions Made
- fuse/unfuse as atomic pair operations: ensures player.is_fused and slime.is_fused are always synchronized
- Mana shield absorbs all damage while fused at 20 juice per hit; no HP loss
- Spit fires on Z release (was_tap pattern) to avoid accidental spit during recall hold
- Enemy/boss callers updated to pass slime through for mana shield to work on all contact damage
- Bare self.is_fused=False kept only as fallback in take_damage when slime is None (backward compat)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Updated enemy/boss take_damage to pass slime**
- **Found during:** Task 1
- **Issue:** Enemies and boss call player.take_damage() without slime parameter, so mana shield would never activate for contact damage
- **Fix:** Added slime parameter to Enemy.update(), Snail.update(), Bat.update(), BossRock.update(), Mole.update() and their take_damage calls; updated main.py callers
- **Files modified:** src/entities/enemies.py, src/entities/boss.py, main.py
- **Verification:** All 113 tests pass (excluding 2 pre-existing failures)
- **Committed in:** f3618b3

**2. [Rule 3 - Blocking] Fixed test_slime.py drill dive activation test mock**
- **Found during:** Task 1 (test verification)
- **Issue:** test_drill_dive_activation didn't mock was_tap/hold_frames, causing truthy MagicMock to trigger spit code and consume extra juice
- **Fix:** Added was_tap.return_value=False and hold_frames.return_value=0 to mock
- **Files modified:** tests/test_slime.py
- **Verification:** test_drill_dive_activation passes with correct juice value
- **Committed in:** f3618b3

---

**Total deviations:** 2 auto-fixed (1 missing critical, 1 blocking)
**Impact on plan:** Both fixes necessary for correct mana shield behavior and test suite integrity. No scope creep.

## Known Stubs
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Fusion system fully operational for Plan 04 to build Ram and Charge Shot abilities on top
- fuse/unfuse pattern established for any future fused ability to use
- Directional hold ready for slime positioning strategy in combat/exploration

---
*Phase: 08-new-fusion-abilities*
*Completed: 2026-03-28*
