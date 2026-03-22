# Phase 07 Research: Macro-Map & Room Persistence

## Overview
Phase 07 transforms the prototype from a series of disconnected rooms into a cohesive 5x5 Metroidvania world. This requires a robust system for handling level boundaries, smooth camera transitions, and state persistence for both permanent upgrades and regenerative environment hazards.

## 1. Macro-Map Architecture (5x5 Z-Spiral)
The world is comprised of a 5x5 grid of 128x128 pixel rooms (16x16 tiles), totaling a 640x640 pixel world space.

### WorldManager Responsibilities
- **Level Registry**: Store a list of `LevelBounds` objects parsed from LDtk `data.json` files.
- **Level Detection**: Determine which level the player's center-point is currently occupying.
- **Entity Lifecycle**: Manage spawning and despawning of enemies and items when a level boundary is crossed.
- **Global State**: Track collected items (Energy Tanks, Missile Tanks, Upgrades) by their unique LDtk `iid`.

### Data Structure: LevelBounds
```python
class LevelBounds:
    def __init__(self, data_json):
        self.id = data_json["identifier"]
        self.x = data_json["x"]
        self.y = data_json["y"]
        self.w = data_json["width"]
        self.h = data_json["height"]
```

## 2. Metroid-Style Camera & Transitions

### Camera Clamping
The camera should follow the player but stay strictly within the current level's bounds. This allows for rooms larger than 128x128 (e.g., vertical shafts or long corridors) while maintaining the "snapped" feel for single-screen rooms.

**Logic:**
```python
cam_x = clamp(player.x - 60, level.x, level.x + level.w - 128)
cam_y = clamp(player.y - 60, level.y, level.y + level.h - 128)
```

### Freeze-and-Slide Transition
When the player crosses into a new level, the game enters a `TRANSITIONING` state.

1.  **Freeze**: Pause all entity updates (Player, Enemies, Slime).
2.  **Calculate**: Determine the target camera position in the new room.
3.  **Slide**: Linearly interpolate (LERP) the camera position over ~15-30 frames.
4.  **Reposition**: Move the player ~8-12 pixels into the new room to avoid boundary jitter.
5.  **Resume**: Spawn entities for the new room and return to `PLAYING` state.

## 3. Room Persistence System

### Permanent Items (Global)
- Tracked via a `set` of `iid` strings in `WorldManager`.
- Collected items are never spawned again, even after `reset()` or room re-entry.

### Regenerative Blocks (Juice Gates)
- **Local Persistence**: When a destructible block is broken, it is added to a `broken_blocks` dictionary in `WorldManager`.
- **Timed Regeneration**: Each entry in `broken_blocks` has a timer (e.g., 150 frames / 5 seconds).
- **Update Loop**: `WorldManager` decrements timers every frame. When a timer hits 0, the block is restored in `LevelMap.collision_data` and the Pyxel tilemap.
- **Entry Reset**: Per requirements, entering a new room immediately clears all active regeneration timers and restores all blocks in that room to ensure no soft-locks.

## 4. Technical Challenges & Solutions

| Challenge | Solution |
| :--- | :--- |
| **Z-Spiral Mapping** | Manually place 25 levels in LDtk forming the spiral. Use absolute coordinates for all logic. |
| **Door Entities** | Use specialized Entity types in LDtk. Doors check for player `kick` or `projectile` collision to toggle state. |
| **Memory Management** | Only spawn entities for the *active* room and its immediate neighbors (optional) to keep object counts low. |

## 5. Validation Architecture

### Automated Verification
- **Level Boundary Test**: Mock player movement across level edges and assert `WorldManager.current_level` updates correctly.
- **Camera Clamp Test**: Verify camera coordinates never exceed `current_level` bounds for various player positions.
- **Persistence Test**: 
    1. Collect an item. 
    2. Exit room. 
    3. Re-enter room. 
    4. Assert item is not present.
- **Regen Timer Test**: Break a block, wait $N$ frames, assert block is restored.

### Visual Regression (MCP Pyxel)
- **Transition Verification**: Use `capture_frames` during a transition to ensure the slide is smooth and the player ends up in the correct relative position.
- **Boundary Clamping**: Capture screens at level corners to verify no "out-of-bounds" black space is visible.

### Manual Success Criteria
- [ ] Player can traverse from [0,0] to [4,4] and back.
- [ ] Items collected in the "Deep" stay collected.
- [ ] "Juice Gates" (timed blocks) function correctly, requiring rapid destruction.
