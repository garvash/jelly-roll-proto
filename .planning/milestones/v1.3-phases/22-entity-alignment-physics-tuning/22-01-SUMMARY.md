---
phase: 22-entity-alignment-physics-tuning
plan: 01
subsystem: entities
tags: [collision, hitbox, physics, tile-migration, pyxel]

# Dependency graph
requires:
  - phase: 21-tileset-ldtk-pipeline
    provides: 16x16 tile grid and LDtk project migrated to 16px
provides:
  - Entity collision boxes aligned to 16x16 visual sprites
  - Legacy spawn path using TILE_SIZE constant
  - Boss offset math using self.w//2 and self.h//2
  - Regression test scaffold for all entity hitbox sizes
affects: [22-02-PLAN, 23-converter-handoff]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Entity hitboxes derived from visual sprite size, not hardcoded"
    - "Boss spawn offsets use self.w//2, self.h//2 instead of magic numbers"
    - "Legacy tile-scan spawn path uses TILE_SIZE constant"

key-files:
  created:
    - tests/test_phase22.py
  modified:
    - src/entities/enemies.py
    - src/entities/slime.py
    - src/entities/boss.py
    - src/entities/effects.py
    - main.py
    - tests/test_enemies.py
    - tests/test_boss.py
    - tests/test_phase05_gaps.py
    - tests/test_phase05_nyquist.py

key-decisions:
  - "Player hitbox 10x14 unchanged per D-01"
  - "Door dimensions 8x32/32x8 unchanged per D-02"
  - "Spit projectile 4x4 unchanged per RESEARCH pitfall 1"
  - "14 pre-existing test failures documented as deferred (from Phase 20/21)"

patterns-established:
  - "Boss offsets use self.w//2, self.h//2 not magic numbers"
  - "Spawn coordinate math uses TILE_SIZE constant not literal 8"

requirements-completed: [ENT-01, ENT-02, ENT-03, ENT-04, ENT-05]

# Metrics
duration: 11min
completed: 2026-04-08
---

# Phase 22 Plan 01: Entity Alignment Summary

**All entity collision boxes updated to match 16x16 visual sprites with legacy spawn path using TILE_SIZE constant**

## Performance

- **Duration:** 11 min
- **Started:** 2026-04-08T12:55:59Z
- **Completed:** 2026-04-08T13:06:58Z
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments
- Enemy base class default hitbox changed from 8x8 to 16x16, propagating to Snail and Bat
- Slime, BossRock collision boxes updated to 16x16; Mole updated to 24x28
- Boss hardcoded offset values replaced with self.w//2 and self.h//2
- Effect draw call uses 16x16 collision size instead of 8x8
- Legacy tile-scan spawn path in main.py uses TILE_SIZE constant (zero remaining hardcoded * 8)
- 13 regression tests created; 12 pass, 1 (physics schema) deferred to Plan 02
- Existing tests updated for new entity sizes, improving pass rate by 8 tests

## Task Commits

Each task was committed atomically:

1. **Task 1: Create phase 22 test scaffold** - `546b1aa` (test) - TDD RED: 13 tests, 5 pass/8 fail
2. **Task 2: Update entity hitboxes and fix legacy spawn path** - `23012a5` (feat) - TDD GREEN: 12 pass/1 deferred
3. **Task 3: Fix existing tests for new entity sizes** - `820a533` (fix) - Updated 4 test files

## Files Created/Modified
- `tests/test_phase22.py` - 13 regression tests for all entity hitbox sizes
- `src/entities/enemies.py` - Enemy base default w=16, h=16
- `src/entities/slime.py` - Slime collision 16x16
- `src/entities/boss.py` - Mole 24x28, BossRock 16x16, centered spawn offsets
- `src/entities/effects.py` - Effect draw uses 16x16 collision args
- `main.py` - Legacy spawn path uses TILE_SIZE, added TILE_SIZE import
- `tests/test_enemies.py` - Mock player dimensions 10x14
- `tests/test_boss.py` - Mock player dimensions 10x14
- `tests/test_phase05_gaps.py` - Bat start_y, spawn coords, player dimensions
- `tests/test_phase05_nyquist.py` - Player dimensions 10x14

## Decisions Made
- Player hitbox 10x14 unchanged (per D-01)
- Door dimensions 8x32/32x8 unchanged (per D-02)
- Spit projectile stays 4x4 (per RESEARCH pitfall 1)
- 14 pre-existing test failures from Phase 20/21 documented as deferred items

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- 14 pre-existing test failures discovered from Phase 20/21 tile migration. These are documented in deferred-items.md and do not affect this plan's goals.

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - all functionality is wired and operational.

## Next Phase Readiness
- Entity hitboxes aligned to 16x16 visuals
- Ready for Plan 02 (physics-schema.json recalculation and remaining test fixes)
- test_physics_schema_updated will pass once Plan 02 updates the schema

---
*Phase: 22-entity-alignment-physics-tuning*
*Completed: 2026-04-08*
