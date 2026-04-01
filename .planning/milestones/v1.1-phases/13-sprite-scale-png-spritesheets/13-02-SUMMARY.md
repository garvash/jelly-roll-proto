---
phase: 13-sprite-scale-png-spritesheets
plan: "02"
subsystem: asset-pipeline
tags: [sprites, png, constants, draw-helper, sprite-scale]
dependency_graph:
  requires:
    - phase: 13-01
      provides: PNG spritesheets + JSON sidecars in assets/sprites/
  provides:
    - SPRITE_SCALE=2, SPRITE_SIZE=16, BOSS_SPRITE_SIZE=32 constants
    - draw_sprite() bottom-center anchor helper function
    - load_sprite_tags() JSON sidecar parser
    - PNG-based sprite loading manifest in main.py
  affects: [13-03 entity draw migration]
tech_stack:
  added: []
  patterns: [bottom-center anchor offset, PNG manifest loading, JSON sidecar tag parsing]
key_files:
  created:
    - src/core/sprite_utils.py
    - tests/test_sprite_scale.py
  modified:
    - src/core/constants.py
    - main.py
key_decisions:
  - "Comment referencing pyxres removed from main.py to satisfy zero-reference verification"
patterns_established:
  - "draw_sprite(x, y, coll_w, coll_h, bank, u, v, visual_w, visual_h, facing_right) for all entity draw calls"
  - "SPRITE_MANIFEST dict maps entity names to (bank, x, y, path) for PNG loading"
requirements_completed: [D-09, D-11, D-12, D-13, D-14, D-15, D-16, D-23]
duration: 3m 25s
completed: 2026-03-29
---

# Phase 13 Plan 02: Sprite Constants, Draw Helper & PNG Loading Pipeline Summary

**SPRITE_SCALE=2 constants, draw_sprite() bottom-center anchor helper, and PNG manifest loading replacing pyxres in main.py**

## Performance

- **Duration:** 3m 25s
- **Started:** 2026-03-29T09:52:48Z
- **Completed:** 2026-03-29T09:56:13Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments
- SPRITE_SCALE=2, SPRITE_SIZE=16, BOSS_SPRITE_SIZE=32 constants added to constants.py
- draw_sprite() helper with bottom-center anchor offset and optional scale parameter created in sprite_utils.py
- main.py pyxres loading fully replaced with PNG manifest loading (SPRITE_MANIFEST dict, _load_sprites method)
- Explosion sprite injection code removed from reset() (baked into effects.png by plan 01)
- JSON sidecar tags loaded at startup for forward Aseprite pipeline compatibility
- 5 TDD tests covering constants and draw offset math all passing

## Task Commits

Each task was committed atomically:

1. **Task 0: Create test stubs for sprite constants and draw_sprite math** - `4d3590e` (test - TDD RED)
2. **Task 1: Add sprite constants to constants.py and create sprite_utils.py** - `315f548` (feat - TDD GREEN)
3. **Task 2: Replace pyxres loading with PNG manifest in main.py** - `3919683` (feat)

## Files Created/Modified
- `src/core/constants.py` - Added SPRITE_SCALE, SPRITE_SIZE, BOSS_SPRITE_SIZE constants
- `src/core/sprite_utils.py` - New file: draw_sprite() helper + load_sprite_tags() parser
- `main.py` - SPRITE_MANIFEST dict, _load_sprites(), sprite_tags loading, removed pyxres dependency
- `tests/test_sprite_scale.py` - 5 tests for constants and draw offset math

## Decisions Made
None - followed plan as specified.

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
None.

## Known Stubs
None -- all outputs are fully functional.

## Next Phase Readiness
- draw_sprite() helper ready for Plan 03 to migrate all 13 entity draw sites
- SPRITE_MANIFEST provides bank layout coordinates for entity draw updates
- sprite_tags dict available on Game instance for future tag-based frame selection

---
*Phase: 13-sprite-scale-png-spritesheets*
*Completed: 2026-03-29*
