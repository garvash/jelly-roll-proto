---
phase: "07"
plan: "01"
subsystem: level-management
tags: [world-manager, camera-clamping, room-detection, ldtk]
dependency_graph:
  requires: []
  provides: [WorldManager, LevelBounds, camera-clamping]
  affects: [main-game-loop, map-loading]
tech_stack:
  added: []
  patterns: [coordinate-based-room-detection, clamp-within-bounds]
key_files:
  created:
    - src/level/world.py
    - tests/test_world_manager.py
  modified:
    - src/level/map.py
    - main.py
decisions:
  - "Camera clamping uses player position (not center) for targeting, with level bounds as hard constraints"
  - "rooms_visited keyed by level identifier string instead of pixel coordinate tuples"
  - "Fallback to legacy 128x128 grid snapping when no LevelBounds detected"
metrics:
  duration: "3m 27s"
  completed: "2026-03-27"
  tasks_completed: 4
  tasks_total: 4
  tests_added: 22
  tests_passing: 22
---

# Phase 07 Plan 01: WorldManager Refactor & Camera Clamping Summary

WorldManager with LevelBounds-based room detection and camera clamping, replacing hardcoded 128x128 grid snapping to support variable-size rooms in the 5x5 macro-map.

## Tasks Completed

| Task | Description | Commit | Key Files |
|------|-------------|--------|-----------|
| 07-01-01 | Create WorldManager and LevelBounds classes | d1dd1fd | src/level/world.py |
| 07-01-02 | Store LevelBounds metadata during LDtk loading | 62b87f3 | src/level/map.py |
| 07-01-03 | Integrate WorldManager into Game loop | 4d6dd66 | main.py |
| 07-01-04 | Unit tests for detect_level and camera clamping | 0cc12d0 | tests/test_world_manager.py |

## Implementation Details

### WorldManager (src/level/world.py)
- `LevelBounds` class stores id, x, y, w, h with a `contains()` point-in-rect check
- `WorldManager.detect_level(x, y)` iterates levels to find the one containing the player center; updates `current_level`
- `WorldManager.get_camera_clamped(px, py)` centers camera on player then clamps to level bounds, preventing out-of-bounds rendering

### LevelMap Integration (src/level/map.py)
- Added `self.levels` dict populated during `load_from_ldtk_simplified()` from each level's `data.json` (identifier, x, y, width, height)
- `get_level_bounds_list()` exposes collection for WorldManager initialization

### Game Loop Integration (main.py)
- WorldManager initialized after map load in `Game.reset()`
- Room transitions now use `detect_level()` with player center-point instead of integer division grid snapping
- Camera updated via `get_camera_clamped()` every frame
- `rooms_visited` keyed by level id string for correctness across variable-size rooms

## Decisions Made

1. **Player position for camera target**: Using `player.x, player.y` (top-left) for camera centering, with `player center` only for room detection. This keeps camera behavior consistent with the player's visual anchor.
2. **Level id as room key**: Switched from `(cam_x, cam_y)` tuples to `level.id` strings for `rooms_visited`, which is more robust for rooms that aren't on the 128-grid.
3. **Graceful fallback**: When no LevelBounds are loaded (e.g., legacy maps), camera falls back to the original grid-snapping behavior.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None - all functionality is fully wired.

## Verification

- 22 unit tests passing in `tests/test_world_manager.py`
- Covers: LevelBounds containment, detect_level for multi-room grids, camera clamping for standard/large rooms, boundary edges, fallback behavior

## Self-Check: PASSED
