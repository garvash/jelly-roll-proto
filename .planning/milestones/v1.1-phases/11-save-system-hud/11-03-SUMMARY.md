---
phase: 11-save-system-hud
plan: 03
subsystem: hud-pause
tags: [pyxel, minimap, pause-screen, hud, tdd]

requires:
  - phase: 11-save-system-hud
    provides: SaveManager, SavePoint, game state machine from Plans 01+02
provides:
  - "Mini-map HUD element with room classification and color coding"
  - "Full pause screen with macro-map, stats, ability row, and menu"
  - "Room type classification from LDtk entities (save/boss/normal)"
  - "D-18 verification: close_gates uses VIEWPORT_W/VIEWPORT_H constants"
affects: []

tech-stack:
  added: []
  patterns: [module-level-testable-functions, getattr-forward-compat]

key-files:
  created:
    - tests/test_minimap.py
  modified:
    - main.py

key-decisions:
  - "Mini-map helper functions (classify_room_types, compute_map_rects, get_room_color) at module level for testability"
  - "Juice bar uses self.slime.max_juice instead of JUICE_MAX constant to reflect upgraded capacity"
  - "SYS-04 gap documented: ENERGY=0 MISSILE=0 in LDtk world -- needs manual LDtk editor placement"

patterns-established:
  - "Module-level helper functions for testable game subsystems"
  - "Uniform scaling with min(scale_x, scale_y) for proportional map rendering"

requirements-completed: [SYS-02, SYS-03]

duration: 3min
completed: 2026-03-30
---

# Phase 11 Plan 03: HUD Mini-Map and Pause Screen Summary

**Mini-map with room classification and color coding in HUD strip, full pause screen with macro-map, stats, ability icons, and Resume/Save/Quit menu**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-30T15:45:10Z
- **Completed:** 2026-03-30T15:48:31Z
- **Tasks:** 2 of 3 (Task 3 is human-verify checkpoint)
- **Files modified:** 2

## Accomplishments
- Mini-map renders in HUD strip between HP pips and juice bar with white border
- Room types classified from LDtk entities: save rooms green (11), boss rooms red (8), current room blinks white/black (15-frame cycle), visited normal rooms gray (5)
- Variable room sizes render proportionally (tall shafts appear taller than standard rooms)
- Full pause screen overlay with macro-map (120x60), HP/JUICE stats, ability abbreviations (DSH/SHD/BST/RAM/CHG), and RESUME/SAVE/QUIT menu
- Save option only appears in pause menu when player is near a save point
- D-18 verified: close_gates uses VIEWPORT_W/VIEWPORT_H constants (Phase 14 fix confirmed)
- Juice bar now uses self.slime.max_juice (reflects upgraded capacity) instead of JUICE_MAX constant
- 11 new tests for room classification, rect computation, color logic, and visited filtering

## Task Commits

Each task was committed atomically:

1. **Task 1: Mini-map + room type classification + map rendering helper** (TDD)
   - `6c0eca5` (test) - Failing tests for mini-map classification, rect computation, and color logic
   - `ddd9525` (feat) - Implement mini-map with room classification, color coding, and HUD integration
2. **Task 2: Full pause screen + D-18 verification + SYS-04 verification** - `31f1289` (feat)
3. **Task 3: Visual playtest verification** - PENDING (checkpoint:human-verify)

## Files Created/Modified
- `main.py` - Added classify_room_types(), compute_map_rects(), get_room_color() module-level functions; _draw_minimap() method; full _update_pause() and _draw_pause_overlay(); mini-map in _draw_hud(); juice bar fix
- `tests/test_minimap.py` - 11 tests: TestClassifyRoomTypes (3), TestComputeMapRects (2), TestMapColors (5), TestVisitedFilter (1)

## Decisions Made
- Mini-map helper functions placed at module level (not inside Game class) for direct test importability
- SYS-04 gap: ENERGY and MISSILE entities not yet placed in LDtk world (count = 0 each); this requires manual LDtk editor work and cannot be done programmatically
- D-18 verified as already fixed: close_gates uses VIEWPORT_W // TILE_SIZE and VIEWPORT_H // TILE_SIZE

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results
- D-18: close_gates at map.py:184 uses `VIEWPORT_W // TILE_SIZE` and `VIEWPORT_H // TILE_SIZE` -- no hardcoded `+ 16`
- SYS-04: ENERGY count = 0, MISSILE count = 0 in assets/cave/simplified/ -- gap noted, requires LDtk placement

## Known Stubs
None - all functionality is fully wired with real logic. The pause screen ability row uses `getattr(self.player, 'has_dash', False)` which is forward-compatible with ability pickups that may not exist yet on the Player class.

## Pending Checkpoint
Task 3 is a `checkpoint:human-verify` gate requiring visual playtest of all Phase 11 features (title screen, save points, mini-map, pause screen, death animation, capacity upgrades).

## Self-Check: PASSED
