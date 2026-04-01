---
phase: 15-ldtk-entity-door-integration
plan: 02
subsystem: entity-pipeline
tags: [ldtk, entity-stubs, schema, map-entities, spawn-wiring]

# Dependency graph
requires:
  - phase: 15-ldtk-entity-door-integration
    plan: 01
    provides: "Entity alias resolution, direction normalization, flat customFields, double-spawn guard"
provides:
  - "OneWay, HiddenLoot, MapFixture stub entity classes"
  - "entity-schema.json v0.4.0 with three new entity definitions"
  - "Spawn wiring for OneWay, HiddenLoot, Map entities in main.py"
  - "Fixtures lifecycle management (reset, room-enter, restore-from-save)"
  - "Unknown entity type logging for debugging"
affects: [entity-pipeline, ldtk-converter, future-oneway-phase, future-hiddenloot-phase]

# Tech tracking
tech-stack:
  added: []
  patterns: ["self.fixtures list for non-interactive entity stubs", "Unknown entity type console logging"]

key-files:
  created: []
  modified: [src/entities/map_entities.py, assets/entity-schema.json, main.py, tests/test_entity_integration.py]

key-decisions:
  - "Named Map entity class as MapFixture to avoid shadowing Python builtin map()"
  - "Used self.fixtures list separate from enemies/items/doors for stub entities that have no game logic yet"
  - "Added unknown entity type logging with PlayerStart exclusion since PlayerStart is handled outside spawn_enemies"

patterns-established:
  - "fixtures list pattern: stub entities with update/draw/check_collision but no game behavior"
  - "Unknown entity logging: catch-all else clause in spawn_enemies for debugging"

requirements-completed: [INT-01, INT-02, INT-03, INT-04]

# Metrics
duration: 5min
completed: 2026-04-01
status: partial-checkpoint-pending
---

# Phase 15 Plan 02: Entity Stubs + Schema v0.4.0 Summary

**Three LDtk entity stubs (OneWay, HiddenLoot, MapFixture) with schema v0.4.0, spawn wiring, fixture lifecycle, and unknown entity logging**

## Status: PARTIAL (Checkpoint Pending)

Task 1 (auto) is complete. Task 2 (checkpoint:human-verify) requires manual E2E playtest verification.

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-01T14:55:02Z
- **Completed:** 2026-04-01 (Task 1 only)
- **Tasks:** 1/2 (Task 2 is human-verify checkpoint)
- **Files modified:** 4

## Accomplishments
- Added three stub entity classes (OneWay, HiddenLoot, MapFixture) to map_entities.py with init/update/draw/check_collision
- Bumped entity-schema.json from v0.3.0 to v0.4.0 with OneWay, HiddenLoot, Map entity definitions
- Wired spawn cases in main.py spawn_enemies for all three new entity types
- Added self.fixtures lifecycle management in reset(), _on_room_enter(), restore_from_save()
- Added fixture update/draw loops in main update/draw methods
- Added unknown entity type console logging (excludes PlayerStart)
- All 15 entity integration tests pass, full suite 303 passed (3 skipped)

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: Failing tests for entity stubs** - `1facecc` (test)
2. **Task 1 GREEN: Entity stubs + schema v0.4.0 + spawn wiring** - `2a738f1` (feat)

_Task 2 (human-verify playtest) is pending checkpoint approval._

## Files Created/Modified
- `src/entities/map_entities.py` - Added OneWay, HiddenLoot, MapFixture stub classes with placeholder rect rendering
- `assets/entity-schema.json` - Bumped to v0.4.0, added OneWay, HiddenLoot, Map entity definitions
- `main.py` - Added imports, spawn wiring, fixtures lifecycle (reset/room-enter/restore), update/draw loops, unknown entity logging
- `tests/test_entity_integration.py` - Added 5 new tests for stubs, fixtures, and unknown entity logging

## Decisions Made
- Named the Map entity class `MapFixture` to avoid shadowing Python's builtin `map()` function
- Used a separate `self.fixtures` list rather than adding stubs to `self.enemies` or `self.items`, since fixtures have no game behavior yet
- Added `PlayerStart` exclusion to unknown entity logging since PlayerStart is handled separately before the entity type dispatch chain

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Pyxel not initialized error in tests when calling draw() on stubs -- resolved by mocking `src.entities.map_entities.pyxel` in test context

## Known Stubs

| File | Class | Status |
|------|-------|--------|
| src/entities/map_entities.py | OneWay | Stub - placeholder rectb rendering, no collision behavior |
| src/entities/map_entities.py | HiddenLoot | Stub - placeholder rectb rendering, no reveal mechanic |
| src/entities/map_entities.py | MapFixture | Stub - placeholder rectb rendering, no interaction |

These stubs are intentional per the plan. They prevent crashes when LDtk data contains these entity types. Full behavior will be implemented in future phases.

## User Setup Required
None - no external service configuration required.

## Checkpoint Pending

Task 2 requires manual E2E playtest verification:
1. Save->Die->Reload flow
2. Room transitions with doors
3. Boss room trigger
4. Event-gated doors
5. New entity stub rendering

## Next Phase Readiness
- Entity pipeline from LDtk export is now complete for all known entity types
- All entity types in entity-schema.json have corresponding spawn handling
- Unknown entity types are logged for debugging
- Awaiting human playtest verification (Task 2 checkpoint)

---
*Phase: 15-ldtk-entity-door-integration*
*Completed: 2026-04-01 (partial - checkpoint pending)*
