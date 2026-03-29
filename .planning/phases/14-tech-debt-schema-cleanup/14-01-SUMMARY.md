---
phase: 14-tech-debt-schema-cleanup
plan: 01
subsystem: gameplay
tags: [event-flags, doors, entity-schema, gate-system]

# Dependency graph
requires:
  - phase: 13-sprite-scale-png-spritesheets
    provides: PNG spritesheet pipeline and entity-schema.json v0.2.0
provides:
  - Event-gated door system (action="event" + event_id field)
  - event_flags dict in main.py for game-state-driven door behavior
  - Fixed close_gates legacy scan using viewport-derived tile counts
affects: [14-02, 14-03, map-design, boss-encounters]

# Tech tracking
tech-stack:
  added: []
  patterns: [event-flag-driven entity behavior, schema-first entity extension]

key-files:
  created: [tests/test_event_doors.py]
  modified: [assets/entity-schema.json, src/entities/map_entities.py, main.py, src/level/map.py]

key-decisions:
  - "event_flags is a separate dict from game_state string to avoid type conflicts"
  - "Event doors check flags on every room entry for consistent gate state"

patterns-established:
  - "Event flag pattern: entities check a shared event_flags dict for state-driven behavior"
  - "Schema-first extension: add fields to entity-schema.json before code implementation"

requirements-completed: [MAP-02]

# Metrics
duration: 2min
completed: 2026-03-30
---

# Phase 14 Plan 01: Event-Gated Door System Summary

**Event-gated door system replacing hardcoded tile ID 4 boss gates with flexible event_flags dict, plus close_gates viewport scan fix**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-30T05:28:16Z
- **Completed:** 2026-03-30T05:30:42Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Door entity schema extended with action="event" enum value and event_id string field
- Door class gains check_event_open method for event-flag-driven opening behavior
- Boss death now sets event_flags["boss_defeated"] = True; doors re-check on every room entry
- close_gates legacy scan fixed from hardcoded 16x16 to viewport-derived 40x22 tile range
- 6 passing tests for event door open/close behavior

## Task Commits

Each task was committed atomically:

1. **Task 1: Entity schema update + Door class event support + event door tests** - `ae72f47` (feat, TDD)
2. **Task 2: main.py event_flags integration + close_gates legacy scan fix** - `e8451e4` (feat)

## Files Created/Modified
- `assets/entity-schema.json` - Added "event" to Door action enum, added event_id field
- `src/entities/map_entities.py` - Extended Door.__init__ with action/event_id params, added check_event_open method
- `tests/test_event_doors.py` - 6 tests covering event door open/close/ignore behavior
- `main.py` - Added event_flags dict, boss death flag, Door instantiation with action/event_id, room entry event check
- `src/level/map.py` - Fixed close_gates legacy scan to use tiles_w/tiles_h instead of hardcoded 16

## Decisions Made
- event_flags kept as separate dict from game_state string ("PLAYING"/"WON") to avoid type conflicts
- Event doors check flags on every room entry (D-04) for consistent gate state across room transitions

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Event-gated door system ready for map designers to place action="event" doors in LDtk
- event_flags dict extensible for future game events beyond boss_defeated
- Plan 14-02 and 14-03 can proceed with schema cleanup confidence

## Self-Check: PASSED

- All 5 key files verified present on disk
- Commits ae72f47 and e8451e4 verified in git log
- 214 tests pass, 3 skipped, 0 failures

---
*Phase: 14-tech-debt-schema-cleanup*
*Completed: 2026-03-30*
