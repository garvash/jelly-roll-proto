---
phase: 22-entity-alignment-physics-tuning
plan: 02
subsystem: physics
tags: [physics-schema, tile-migration, 16px, converter-contract]

# Dependency graph
requires:
  - phase: 20-grid-constants-schema-metadata
    provides: "TILE_SIZE=16 in constants.py"
provides:
  - "physics-schema.json v0.2.0 with 16px tile-unit values"
  - "Correct player hitbox_px [10, 14] in schema"
  - "Converter-ready gap/clearance values for 16px grid"
affects: [23-converter-handoff, pml-to-ldtk-converter]

# Tech tracking
tech-stack:
  added: []
  patterns: ["physics-schema versioning for breaking tile-size changes"]

key-files:
  created: []
  modified: ["assets/physics-schema.json"]

key-decisions:
  - "Version bump 0.1.0 -> 0.2.0 signals breaking change to converter"
  - "Player hitbox_px corrected to [10, 14] (was incorrectly [8, 8] in v0.1.0)"

patterns-established:
  - "Physics schema tile-unit values derived by dividing px by tile_size"

requirements-completed: [PHYS-01, PHYS-02, PHYS-03]

# Metrics
duration: 1min
completed: 2026-04-08
---

# Phase 22 Plan 02: Physics Schema 16px Recalculation Summary

**physics-schema.json v0.2.0 with all tile-unit values recalculated for 16px base and corrected player hitbox**

## Performance

- **Duration:** 1 min
- **Started:** 2026-04-08T12:55:45Z
- **Completed:** 2026-04-08T12:56:32Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Recalculated all tile-unit values in physics-schema.json for TILE_SIZE=16 (values halved from 8px base)
- Corrected player hitbox_px from [8, 8] to [10, 14] (actual collision dimensions)
- Updated clearance to 1 tile (player fits in 16px tile, was 2 tiles at 8px)
- Physics constants (GRAVITY, JUMP_FORCE, etc.) preserved unchanged per D-03

## Task Commits

Each task was committed atomically:

1. **Task 1: Recalculate physics-schema.json for 16px tile base** - `09acd36` (feat)

**Plan metadata:** (pending)

## Files Created/Modified
- `assets/physics-schema.json` - Updated from v0.1.0 to v0.2.0 with 16px tile-unit values

## Decisions Made
- Version bump 0.1.0 -> 0.2.0 signals breaking change to converter consumers
- Corrected player hitbox_px to [10, 14] -- the old [8, 8] was incorrect even at 8px scale

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- test_phase22.py does not exist yet (created by Plan 01 which runs in parallel) -- not a blocker, verification done via inline Python assertions

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- physics-schema.json is ready for Phase 23 converter handoff documentation
- All entity alignment (Plan 01) and physics schema (Plan 02) changes are complete

---
*Phase: 22-entity-alignment-physics-tuning*
*Completed: 2026-04-08*
