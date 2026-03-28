---
phase: 08-new-fusion-abilities
plan: 02
subsystem: player-mechanics
tags: [dash, kick-removal, drill-retcon, controls, entity-schema]

requires:
  - phase: 08-new-fusion-abilities
    plan: 01
    provides: Input abstraction module (src/core/input.py)
provides:
  - Basic dash mechanic (DASHING state, start_dash, apply_dash_physics)
  - Kick mechanic fully removed from codebase
  - Drill Dive retconned to DOWN+V activation
  - DashPickup item type replacing DRILL
affects: [08-03, 08-04, player, items, entity-schema, controls]

tech-stack:
  added: []
  patterns: [state-machine-extension, item-type-rename]

key-files:
  created: [tests/test_dash.py, tests/test_kick_removal.py, tests/test_drill_retcon.py]
  modified: [src/entities/player.py, src/core/constants.py, main.py, src/entities/items.py, assets/entity-schema.json, tests/test_slime.py]

key-decisions:
  - "V button is the movement ability button: V=dash (unfused), DOWN+V=drill dive (D-07, D-22)"
  - "Basic dash is gated behind DashPickup item (has_dash flag), separate from drill (has_drill)"
  - "One air dash per airborne, resets on landing via move_and_collide floor snap"
  - "Dash freezes vertical movement (dy=0) for clean horizontal burst"

patterns-established:
  - "State machine extension: add state branch in update(), guard in update_state(), timer in update_timers()"
  - "Item-gated abilities: has_dash/has_drill pattern for pickup-locked mechanics"

requirements-completed: []

duration: 5min
completed: 2026-03-28
---

# Phase 08 Plan 02: Kick Removal, Drill Retcon, and Basic Dash Summary

**Removed kick mechanic, retconned Drill Dive to DOWN+V, replaced DRILL with DashPickup, implemented basic dash with i-frames and air dash**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-28T06:11:08Z
- **Completed:** 2026-03-28T06:16:07Z
- **Tasks:** 3/3
- **Files modified:** 9

## Accomplishments
- Fully removed kick mechanic: kick_timer, kick() method, KICK_DURATION, SLIME_PUNT_SPEED, and kick-opens-door logic all deleted
- Retconned Drill Dive activation from DOWN+SPACE to DOWN+V (dash button) per D-22
- Implemented basic dash: 8-frame burst at 4.0 px/frame, 8-frame i-frames, 20-frame cooldown, one air dash per airborne
- Replaced DRILL item type with DASH_PICKUP throughout items.py, main.py, and entity-schema.json
- Created 22 new test methods across 3 test files covering dash, kick removal, and drill retcon

## Task Commits

1. **Task 1: Remove kick mechanic and retcon drill dive activation** - `6498e50` (feat)
2. **Task 2: Implement basic dash state and movement** - `9443ccb` (feat)
3. **Task 3: Replace DRILL item with DashPickup and update entity schema** - `cdd05ee` (feat)

## Files Created/Modified
- `src/core/constants.py` - Removed KICK_DURATION/SLIME_PUNT_SPEED, added DASH_SPEED/DASH_DURATION/DASH_IFRAMES/DASH_COOLDOWN
- `src/entities/player.py` - Removed kick, added dash state machine (start_dash, apply_dash_physics, DASHING state)
- `main.py` - Removed kick-opens-door, renamed Drill entity spawn to DashPickup
- `src/entities/items.py` - DRILL -> DASH_PICKUP, has_drill -> has_dash
- `assets/entity-schema.json` - Drill entity renamed to DashPickup
- `tests/test_dash.py` - 9 tests for dash mechanics
- `tests/test_kick_removal.py` - 4 tests verifying kick is fully removed
- `tests/test_drill_retcon.py` - 5 tests verifying drill retcon and DashPickup
- `tests/test_slime.py` - Updated drill dive test to use dash button

## Decisions Made
- V button unified as movement ability button: V=dash unfused, DOWN+V=drill dive
- Basic dash gated behind DashPickup item (has_dash flag), separate from drill ability (has_drill)
- One air dash per airborne, resets on landing
- Dash freezes vertical movement (dy=0) for clean horizontal burst feel

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Updated test_slime.py drill dive activation test**
- **Found during:** Task 1 (test verification)
- **Issue:** test_drill_dive_activation used btnp("jump") for drill activation, which was retconned to btnp("dash")
- **Fix:** Changed mock side_effect from "jump" to "dash" in test_slime.py
- **Files modified:** tests/test_slime.py
- **Commit:** 6498e50

**Total deviations:** 1 auto-fixed (blocking)
**Impact on plan:** Necessary fix for test correctness after D-22 retcon.

## Known Stubs
None.

## User Setup Required
None.

## Next Phase Readiness
- Plan 03 can build charge-to-fuse on top of the V button infrastructure
- Plan 04 can build Slime Ram using the same state machine pattern established here
- DashPickup entity schema shared with pml-to-ldtk converter (entity-schema.json updated)

---
*Phase: 08-new-fusion-abilities*
*Completed: 2026-03-28*
