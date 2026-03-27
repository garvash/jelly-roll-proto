---
phase: "07"
plan: "02"
subsystem: transitions-persistence
tags: [room-transitions, item-persistence, block-regen, doors, goo-mold]
dependency_graph:
  requires: [WorldManager, LevelBounds, camera-clamping]
  provides: [freeze-slide-transition, item-persistence, block-regen, door-entity, biome-gates]
  affects: [main-game-loop, map-loading, player-collision]
tech_stack:
  added: []
  patterns: [ease-out-quadratic-lerp, iid-based-persistence, timer-based-regen]
key_files:
  created:
    - src/entities/map_entities.py
    - tests/test_persistence.py
  modified:
    - src/level/world.py
    - src/level/map.py
    - src/core/constants.py
    - src/entities/items.py
    - src/entities/player.py
    - main.py
decisions:
  - "24-frame ease-out quadratic LERP for transition slide (~0.4s at 60fps)"
  - "Item persistence keyed by LDtk iid field from entity instances"
  - "Block regen timer at 300 frames (5 seconds); all blocks reset on room entry"
  - "Goo-Mold, Cracked-H, Cracked-V mapped to IntGrid values 10, 11, 12"
metrics:
  duration: "6m 24s"
  completed: "2026-03-27"
  tasks_completed: 6
  tasks_total: 6
  tests_added: 18
  tests_passing: 18
---

# Phase 07 Plan 02: Metroid Transitions & State Persistence Summary

Freeze-and-slide room transitions with ease-out LERP, permanent item collection via LDtk iid tracking, timed block regeneration with room-entry reset, and biome-specific gate tile types (Goo-Mold, cracked blocks).

## Tasks Completed

| Task | Description | Commit | Key Files |
|------|-------------|--------|-----------|
| 07-02-01 | Transition state machine and camera sliding | 3e97cab | src/level/world.py, main.py |
| 07-02-02 | Door entity with kick/spit interaction | 01d7634 | src/entities/map_entities.py, main.py |
| 07-02-03 | Item persistence using LDtk instance IDs | 2b712fe | src/entities/items.py, src/level/map.py, main.py |
| 07-02-04 | Destructible block timed regeneration | 972237b | src/level/map.py, src/entities/player.py, main.py |
| 07-02-05 | Biome-specific gate tiles (Goo-Mold, cracked) | bef4f1c | src/core/constants.py, src/level/map.py |
| 07-02-06 | Unit tests for persistence system | 83b6a11 | tests/test_persistence.py |

## Implementation Details

### Transition System (src/level/world.py)
- `WorldManager.STATE_PLAYING` / `STATE_TRANSITIONING` state machine
- `trigger_transition()` computes target camera from level bounds, initializes LERP
- `update_transition()` runs ease-out quadratic interpolation over 24 frames
- Gameplay frozen during transition (early return in `Game.update()`)
- Player nudged into target room to prevent re-triggering

### Door Entity (src/entities/map_entities.py)
- `Door` class: closed by default, opens on Player Kick or Slime Spit hit
- Open doors trigger `WorldManager.trigger_transition` on player collision
- `target_level_id` links door to destination room
- Doors cleared on room transition, re-spawned from entities

### Item Persistence (WorldManager + items.py)
- `Item` accepts `iid` parameter (LDtk instance ID)
- `WorldManager.collected_iids` set tracks permanently collected items
- `spawn_enemies` skips entities whose iid is in collected_iids
- Items marked collected on pickup via `WorldManager.collect_item()`
- LDtk entity loader now captures `iid` and custom fields from data.json

### Block Regeneration (WorldManager)
- `broken_blocks` dict: (tx, ty) -> {timer, tile_data}
- `update_block_regen()` ticks timers each frame, restores via `LevelMap.restore_tile()`
- `reset_blocks_for_room()` instantly restores all blocks on room entry (anti soft-lock)
- Default regen timer: 300 frames (5 seconds at 60fps)
- `LevelMap.restore_tile()` re-adds to both collision_data and visual tilemap

### Biome Gates (constants.py + map.py)
- `TILE_GOO_MOLD` (IntGrid 10): Negative Space blocks
- `TILE_CRACKED_H` (IntGrid 11): Horizontal cracked blocks (ABL-01)
- `TILE_CRACKED_V` (IntGrid 12): Vertical cracked blocks (ABL-02)
- All three treated as solid for collision and destructible for drill

## Decisions Made

1. **24-frame ease-out LERP**: Chosen for smooth deceleration matching Metroid-style camera slides. About 0.4 seconds at 60fps.
2. **IID-based persistence**: Using LDtk's native instance IDs rather than coordinate-based keys for robustness across level edits.
3. **Room-entry block reset**: All broken blocks reset immediately on room entry, preventing soft-locks from over-drilling.
4. **IntGrid mapping 10-12**: Reserved IntGrid values 10+ for biome-specific tiles to avoid conflicts with existing 1-5 mapping.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None - all functionality is fully wired.

## Verification

- 18 unit tests passing in `tests/test_persistence.py`
- Covers: item persistence (5 tests), block regen timers and room reset (7 tests), transition state machine (6 tests)

## Self-Check: PASSED
