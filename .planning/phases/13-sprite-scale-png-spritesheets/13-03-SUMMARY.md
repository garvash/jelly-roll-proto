---
phase: 13-sprite-scale-png-spritesheets
plan: 03
subsystem: rendering
tags: [pyxel, sprites, draw_sprite, entity-schema, bottom-center-anchor]

requires:
  - phase: 13-02
    provides: sprite_utils.py draw_sprite helper and SPRITE_SIZE/BOSS_SPRITE_SIZE constants
provides:
  - All entity draw methods use draw_sprite helper at 16x16 visual (32x32 boss)
  - entity-schema.json v0.2.0 with sprite metadata for map converter
  - sprite_utils.py with draw_sprite and load_sprite_tags (created as dependency)
affects: [map-converter, future-art-pipeline, entity-rendering]

tech-stack:
  added: [sprite_utils.py]
  patterns: [bottom-center-anchor-drawing, draw_sprite-helper-pattern, bank-1-sprite-layout]

key-files:
  created:
    - src/core/sprite_utils.py
  modified:
    - src/core/constants.py
    - src/entities/player.py
    - src/entities/slime.py
    - src/entities/enemies.py
    - src/entities/boss.py
    - src/entities/items.py
    - src/entities/projectile.py
    - src/entities/effects.py
    - assets/entity-schema.json

key-decisions:
  - "Created sprite_utils.py inline (Rule 3 deviation) since plan 13-02 dependency not yet in worktree"
  - "Items DRILL type mapped to frame 2 (same as DASH_PICKUP) since drill item predates new item system"
  - "Slime dissipation path simplified to use draw_sprite scale parameter directly"

patterns-established:
  - "draw_sprite helper: all entity sprites go through draw_sprite() for consistent bottom-center anchoring"
  - "Bank 1 layout: player=y0, slime=y16, snail=y32, bat=y48, items=y64, projectiles=y80, effects=y96, boss=y128"

requirements-completed: [D-01, D-02, D-03, D-04, D-12, D-14, D-17, D-20, D-21, D-24, D-25]

duration: 5min
completed: 2026-03-29
---

# Phase 13 Plan 03: Entity Draw Migration Summary

**All 13 entity draw sites across 7 files migrated to draw_sprite helper with 16x16 visual sprites (32x32 boss), plus entity-schema.json sprite metadata for map converter**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-29T09:59:57Z
- **Completed:** 2026-03-29T10:05:10Z
- **Tasks:** 2 of 3 (Task 3 is human-verify checkpoint)
- **Files modified:** 10

## Accomplishments
- Migrated all entity draw methods from raw pyxel.blt() to draw_sprite helper with bottom-center anchoring
- All standard entities render at 16x16 visual size, boss at 32x32, collision boxes unchanged
- Items fully moved to bank 1 (removed bank 0 entity sprite references)
- Slime juice-depletion scale effect preserved via draw_sprite scale parameter
- entity-schema.json extended with sprite metadata (sheet, frame_size) for all entities
- Schema version bumped to 0.2.0

## Task Commits

Each task was committed atomically:

1. **Task 1: Update all entity draw methods to use draw_sprite at 16x16** - `05bea90` (feat)
2. **Task 2: Add sprite metadata to entity-schema.json** - `aad6201` (feat)
3. **Task 3: Visual verification of sprite rendering** - CHECKPOINT (awaiting human verification)

## Files Created/Modified
- `src/core/sprite_utils.py` - draw_sprite helper with bottom-center anchor offset + load_sprite_tags for Aseprite JSON
- `src/core/constants.py` - Added SPRITE_SCALE, SPRITE_SIZE, BOSS_SPRITE_SIZE constants
- `src/entities/player.py` - Player draw via draw_sprite, 16px stride animation frames
- `src/entities/slime.py` - Slime draw with fused/regular/scale paths via draw_sprite
- `src/entities/enemies.py` - Snail (y=32) and Bat (y=48) draw via draw_sprite
- `src/entities/boss.py` - Mole (y=128, 32x32) and Rock (y=80, 16x16) via draw_sprite
- `src/entities/items.py` - All items on bank 1 y=64, ITEM_FRAMES dict lookup
- `src/entities/projectile.py` - Spit at y=80 via draw_sprite
- `src/entities/effects.py` - Explosion at y=96, 16px stride via draw_sprite
- `assets/entity-schema.json` - v0.2.0 with sprite metadata for all entities

## Decisions Made
- Created sprite_utils.py and sprite constants inline since plan 13-02 not yet merged to this worktree (Rule 3 blocking dependency)
- Mapped DRILL item type to frame index 2 alongside DASH_PICKUP (legacy compatibility)
- Simplified slime dissipation path to remove manual offset math, relying on draw_sprite scale parameter

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Created sprite_utils.py and sprite constants as dependencies**
- **Found during:** Task 1 (entity draw migration)
- **Issue:** Plan 13-02 dependency (sprite_utils.py, SPRITE_SIZE, BOSS_SPRITE_SIZE) not present in worktree
- **Fix:** Created src/core/sprite_utils.py with draw_sprite and load_sprite_tags; added SPRITE_SCALE/SPRITE_SIZE/BOSS_SPRITE_SIZE to constants.py
- **Files modified:** src/core/sprite_utils.py (created), src/core/constants.py
- **Verification:** All 7 entity files import and use draw_sprite successfully
- **Committed in:** 05bea90 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Essential dependency creation. No scope creep. If plan 13-02 merges later, these files will need reconciliation.

## Issues Encountered
- entity-schema.json had a "description" key at top level of "entities" object that caused verification script iteration to fail on non-dict values. Adjusted verification to skip non-dict entries.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All entity draw sites migrated; awaiting human visual verification (Task 3 checkpoint)
- After verification, sprite rendering pipeline is complete for the prototype
- Future art pipeline: replace auto-upscaled PNGs with hand-drawn 16x16 Aseprite sprites

---
*Phase: 13-sprite-scale-png-spritesheets*
*Completed: 2026-03-29*
