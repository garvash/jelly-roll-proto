---
phase: 09-defensive-mechanics
plan: 01
subsystem: gameplay
tags: [pyxel, tile-system, input-remap, charge-recoil, zone-hazard, entity-schema]

# Dependency graph
requires:
  - phase: 08-new-fusion-abilities
    provides: input abstraction, fusion system, charge shot, slime ram
provides:
  - Zone hazard tile constants and LevelMap detection (TILE_WATER/ACID/LAVA)
  - HAZARD_DRAIN_RATES dict for drain-per-frame lookups
  - get_zone_hazard_type() AABB method on LevelMap
  - Drill dive remapped to DOWN+SPACE (D-12)
  - V button is purely horizontal (dash/ram only)
  - CHARGE_RECOIL_FORCE upward impulse on charge shot
  - Shield/Boost/ShieldT2 item pickup collection
  - Player flags (has_shield, has_boost, has_shield_t2, shield_active, etc.)
  - Entity schema IntGrid 6-8 and ShieldPickup/BoostPickup/ShieldT2 entities
  - BOOST constants (force, cost, recommit window, damage hitbox)
affects: [09-02-bubble-shield, 09-03-slime-boost, pml-to-ldtk-converter]

# Tech tracking
tech-stack:
  added: []
  patterns: [zone-hazard-passable-tiles, input-remap-axis-consistency, charge-recoil-bomb-climb]

key-files:
  created:
    - tests/test_input_remap.py
    - tests/test_charge_recoil.py
    - tests/test_hazard_zones.py
  modified:
    - src/core/constants.py
    - src/level/map.py
    - src/entities/items.py
    - src/entities/player.py
    - assets/entity-schema.json
    - tests/test_drill_retcon.py
    - tests/test_slime.py

key-decisions:
  - "Drill dive remapped to DOWN+SPACE per D-12 for axis consistency (vertical=SPACE, horizontal=V)"
  - "Zone hazard tiles are passable (NOT solid) -- player walks through them with juice drain"
  - "ABL-07 (Reform Block) removed from scope per D-21 -- no code changes needed"

patterns-established:
  - "Zone hazard tiles: HAZARD_DRAIN_RATES dict maps tile type to drain rate for uniform lookup"
  - "Boost placeholder: SPACE+fused+airborne reserved in handle_input for Plan 03 implementation"

requirements-completed: [ABL-05, ABL-06, ABL-07]

# Metrics
duration: 5min
completed: 2026-03-28
---

# Phase 9 Plan 01: Defensive Mechanics Infrastructure Summary

**Zone hazard tiles (water/acid/lava) with drain rates, drill dive remapped to DOWN+SPACE, charge shot recoil impulse, and shield/boost item pickups**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-28T09:28:14Z
- **Completed:** 2026-03-28T09:33:30Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments
- Added TILE_WATER/ACID/LAVA zone hazard tiles with configurable drain rates and LevelMap AABB detection
- Remapped drill dive from DOWN+V to DOWN+SPACE for axis consistency (vertical=SPACE, horizontal=V)
- Added charge shot recoil (CHARGE_RECOIL_FORCE = -2.5) enabling bomb-climb exploit
- Added SHIELD_PICKUP, BOOST_PICKUP, SHIELD_T2 item collection and player ability flags
- Updated entity-schema.json with IntGrid 6-8 zone hazards and three new pickup entities

## Task Commits

Each task was committed atomically:

1. **Task 1: Zone hazard constants, map detection, item pickups, entity schema** - `860bcee` (feat)
2. **Task 2 RED: Failing tests for input remap, charge recoil, hazard zones** - `b652141` (test)
3. **Task 2 GREEN: Input remap + charge shot recoil implementation** - `580e005` (feat)

## Files Created/Modified
- `src/core/constants.py` - Added zone hazard tiles, drain rates, shield/boost/recoil constants
- `src/level/map.py` - Added TILE_WATER/ACID/LAVA to val_to_tile, get_zone_hazard_type() method
- `src/entities/items.py` - Added SHIELD_PICKUP, BOOST_PICKUP, SHIELD_T2 collection and draw
- `src/entities/player.py` - Added Phase 9 flags, remapped drill to DOWN+SPACE, charge recoil
- `assets/entity-schema.json` - IntGrid 6-8 zone hazards, ShieldPickup/BoostPickup/ShieldT2 entities
- `tests/test_input_remap.py` - 5 tests for DOWN+SPACE drill and V for dash/ram
- `tests/test_charge_recoil.py` - 2 tests for charge shot recoil impulse
- `tests/test_hazard_zones.py` - 5 tests for zone detection and passability
- `tests/test_drill_retcon.py` - Updated to expect jump button for drill activation
- `tests/test_slime.py` - Updated drill dive test to use jump button

## Decisions Made
- Drill dive remapped to DOWN+SPACE per D-12 for axis consistency (vertical actions on SPACE, horizontal on V)
- Zone hazard tiles are passable (not in is_solid tuple) -- player walks through them freely
- ABL-07 (Reform Block) documented as removed per D-21 -- no code changes needed, just schema note

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated existing drill tests for input remap**
- **Found during:** Task 2
- **Issue:** test_slime.py::test_drill_dive_activation and test_drill_retcon.py tested drill on "dash" button
- **Fix:** Updated to expect "jump" button per D-12 remap
- **Files modified:** tests/test_slime.py, tests/test_drill_retcon.py
- **Committed in:** 580e005

---

**Total deviations:** 1 auto-fixed (1 bug fix for outdated tests)
**Impact on plan:** Essential fix to align existing tests with D-12 remap. No scope creep.

## Issues Encountered
- Pre-existing test failures in test_phase05_gaps.py and test_phase05_nyquist.py (rooms_visited uses string IDs vs tuple coordinates, camera update timing). Not caused by this plan. Logged as out-of-scope.

## User Setup Required
None - no external service configuration required.

## Known Stubs
- Boost activation placeholder in player.py handle_input (`pass` comment) -- Plan 03 will implement
- Shield/Boost/ShieldT2 draw sprites use placeholder coordinates (32,0), (40,0), (48,0) -- art pass needed

## Next Phase Readiness
- Zone hazard infrastructure ready for Plan 02 (Bubble Shield) and Plan 03 (Slime Boost)
- All constants, flags, and detection methods in place for parallel plan execution
- Entity schema updated for pml-to-ldtk converter compatibility

---
*Phase: 09-defensive-mechanics*
*Completed: 2026-03-28*
