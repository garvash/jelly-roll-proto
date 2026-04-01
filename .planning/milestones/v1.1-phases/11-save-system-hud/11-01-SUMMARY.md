---
phase: 11-save-system-hud
plan: 01
subsystem: persistence
tags: [json, save-system, entity, pyxel, tdd]

requires:
  - phase: none
    provides: standalone save infrastructure
provides:
  - "SaveManager class with save/load/exists/delete static methods"
  - "SavePoint entity with proximity detection and prompt state"
  - "Entity-schema.json SavePoint definition for LDtk pipeline"
  - "Save system constants (caps, timers, filename)"
affects: [11-02-game-loop-wiring, 11-03-hud-pause-menu]

tech-stack:
  added: []
  patterns: [static-manager-class, getattr-forward-compat, tmp-path-monkeypatch-testing]

key-files:
  created:
    - src/core/save_manager.py
    - src/entities/save_point.py
    - tests/test_save_system.py
  modified:
    - src/core/constants.py
    - assets/entity-schema.json

key-decisions:
  - "Used getattr with defaults for ability flags (has_dash, has_shield, etc.) since player.py only has has_drill currently"
  - "Save only max_hp/max_juice not current values per D-04 respawn-at-full rule"
  - "Project-root-relative path resolution for save file via os.path.dirname chain"

patterns-established:
  - "SaveManager static pattern: all methods are @staticmethod with _get_save_path() helper"
  - "Monkeypatch _get_save_path for test isolation using tmp_path"

requirements-completed: [SYS-01, SYS-04]

duration: 3min
completed: 2026-03-30
---

# Phase 11 Plan 01: Save System Infrastructure Summary

**SaveManager with JSON round-trip persistence, SavePoint entity with AABB proximity and pulse animation, capacity cap constants**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-30T15:20:07Z
- **Completed:** 2026-03-30T15:23:07Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- SaveManager with save/load/exists/delete methods serializing player abilities, capacity, collected items, event flags, and room state to JSON
- SavePoint entity with AABB proximity detection, yellow/orange pulse animation, and SAVE?/SAVED! prompt states
- Entity-schema.json updated with SavePoint definition for pml-to-ldtk converter pipeline
- 16 tests covering round-trip persistence, capacity caps, and proximity detection

## Task Commits

Each task was committed atomically:

1. **Task 1: SaveManager module + constants + tests** (TDD)
   - `6e112a7` (test) - Failing tests for SaveManager and capacity caps
   - `33bd221` (feat) - Implement SaveManager with JSON persistence and save constants
2. **Task 2: SavePoint entity + entity-schema update** - `7c1b78b` (feat)

## Files Created/Modified
- `src/core/save_manager.py` - SaveManager class with save/load/exists/delete static methods
- `src/core/constants.py` - Added MAX_HP_CAP, MAX_JUICE_CAP, SAVE_FILE, death/pulse timer constants
- `src/entities/save_point.py` - SavePoint entity with proximity check, pulse animation, prompt states
- `assets/entity-schema.json` - Added SavePoint entity definition for LDtk pipeline
- `tests/test_save_system.py` - 16 tests: SaveManager ops, round-trip, caps, SavePoint proximity

## Decisions Made
- Used `getattr(player, "has_dash", False)` for ability flags not yet on Player class (has_dash, has_shield, has_shield_t2, has_boost) - forward compatible with future phases
- Save only max_hp/max_juice (not current values) per D-04 design decision: player respawns at full

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Player missing ability flags referenced in plan**
- **Found during:** Task 1 (SaveManager implementation)
- **Issue:** Plan referenced player.has_dash, has_shield, has_shield_t2, has_boost but only has_drill exists
- **Fix:** Used getattr with False defaults so SaveManager works with current and future player code
- **Files modified:** src/core/save_manager.py
- **Verification:** All round-trip tests pass; fields serialize correctly
- **Committed in:** 33bd221

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Forward-compatible fix. No scope creep.

## Issues Encountered
- entity-schema.json was not present in worktree (only in main repo); copied it in before modification

## Known Stubs
None - all functionality is fully wired with real logic.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- SaveManager and SavePoint ready for Plan 02 to wire into game loop
- Constants ready for Plan 03 HUD/pause menu implementation
- Entity schema ready for LDtk map authors to place SavePoint entities

## Self-Check: PASSED

All 5 files found. All 3 commits verified.

---
*Phase: 11-save-system-hud*
*Completed: 2026-03-30*
