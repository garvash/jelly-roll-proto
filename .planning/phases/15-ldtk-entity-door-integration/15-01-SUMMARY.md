---
phase: 15-ldtk-entity-door-integration
plan: 01
subsystem: level-loading
tags: [ldtk, entity-pipeline, map-parsing, integration-fix]

# Dependency graph
requires:
  - phase: 11-save-hud
    provides: "Door, SavePoint, restore_from_save, classify_room_types"
provides:
  - "Entity alias resolution (ENTITY_ALIASES) for LDtk name mismatches"
  - "Lowercase string normalization for all LDtk custom field values"
  - "Flat customFields read for Door action/event_id"
  - "Defensive entity list clear in restore_from_save"
affects: [15-02, entity-pipeline, door-system, save-system]

# Tech tracking
tech-stack:
  added: []
  patterns: ["ENTITY_ALIASES dict for LDtk name mapping", "isinstance(val, str) + val.lower() at parse time"]

key-files:
  created: [tests/test_entity_integration.py]
  modified: [src/level/map.py, main.py]

key-decisions:
  - "Normalize ALL string fields to lowercase at parse time in map.py, not just direction"
  - "Use module-level ENTITY_ALIASES dict rather than inline checks for extensibility"
  - "Apply alias resolution in all five entity type check sites (spawn_enemies, classify_room_types, check_boss_trigger, restore_from_save)"

patterns-established:
  - "ENTITY_ALIASES pattern: centralized alias dict for LDtk export name mismatches"
  - "Parse-time normalization: all string enum values lowercased in map.py before game code sees them"

requirements-completed: [INT-01, INT-02, INT-03, INT-04]

# Metrics
duration: 5min
completed: 2026-04-01
---

# Phase 15 Plan 01: LDtk Entity Integration Fixes Summary

**Entity alias resolution, direction normalization, flat customFields read, and double-spawn guard fix four LDtk-to-game pipeline bugs**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-01T14:46:54Z
- **Completed:** 2026-04-01T14:51:39Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Fixed entity name mismatches: ENTITY_ALIASES maps Save->SavePoint, FinalBoss->BossMole (INT-01)
- Fixed Door customFields: reads action/event_id from flat entity dict instead of non-existent nested dict (INT-02)
- Fixed direction capitalization: all string enum values lowercased at parse time in map.py (INT-03)
- Fixed double-spawn on restore: defensive clear of entity lists before spawn_enemies in restore_from_save (INT-04)
- Added 10 unit tests covering all four bug fixes

## Task Commits

Each task was committed atomically:

1. **Task 1: Direction normalization + entity alias + customFields + double-spawn fixes** - `6840187` (feat)
2. **Task 2: Unit tests for INT-01 through INT-04** - `3ee68a3` (test)

## Files Created/Modified
- `src/level/map.py` - Added isinstance(val, str) + val.lower() in both customFields and top-level field loops
- `main.py` - Added ENTITY_ALIASES dict, alias resolution in 5 sites, flat Door field reads, action="none" normalization, defensive entity list clears in restore_from_save
- `tests/test_entity_integration.py` - 10 unit tests covering entity aliases, direction normalization, flat customFields, action none normalization, double-spawn guard, classify_room_types with aliases

## Decisions Made
- Applied alias resolution in `restore_from_save` SavePoint check (line 888) in addition to the three sites specified in the plan -- this was a Rule 2 auto-fix since the site was missed in the plan but uses the same pattern.
- Wrote 10 tests (exceeding the plan's 7) by adding tests for all direction values, top-level direction normalization, canonical name passthrough, and unknown name passthrough.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added alias resolution in restore_from_save SavePoint lookup**
- **Found during:** Task 1 (entity alias fixes)
- **Issue:** restore_from_save checks `ent["type"] == "SavePoint"` at line 888 but the plan only listed spawn_enemies, classify_room_types, and check_boss_trigger as alias sites
- **Fix:** Changed to `ENTITY_ALIASES.get(ent["type"], ent["type"]) == "SavePoint"`
- **Files modified:** main.py
- **Verification:** Tests pass, structural consistency with other alias sites
- **Committed in:** 6840187 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 2 - missing critical)
**Impact on plan:** Essential for correctness -- without this fix, a "Save" entity would not be found during restore teleport.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - all fixes are complete with no placeholder code.

## Next Phase Readiness
- Entity pipeline from LDtk export through spawn code is now correct
- Plan 15-02 can proceed with any remaining integration work
- Full test suite passes (298 passed, 3 skipped)

---
*Phase: 15-ldtk-entity-door-integration*
*Completed: 2026-04-01*
