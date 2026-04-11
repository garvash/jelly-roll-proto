# Architecture Patterns: Milestone v1.1

**Project:** Jelly-Roll
**Researched:** 2026-03-12

## Recommended Architecture

### Macro-Map Structure (The Z-Spiral)
The 5x5 grid follows a **Z-Spiral** traversal.
- **[0,0] to [0,2]:** Intro.
- **[2,2]:** Central Hub.
- **[4,4]:** Boss Room.

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| LevelMap | Tilemap data, collision, LDtk loading. | Game, Player |
| Game | Camera snapping, room-based entity spawning. | All entities |
| Persistence | JSON Save/Load. | Game State |
| HUD | Mini-map rendering and resource bars. | Game, Player, Slime |

### Data Flow
1. **Player Position** triggers **Camera Snap** (128x128 increments).
2. **Camera Snap** updates `current_room_coords`.
3. **Room Entry** spawns entities if `(coords) NOT in rooms_visited` (for items/one-time events) or refreshes enemies.

## Patterns to Follow

### Pattern 1: Position History Buffer (Gradius Option)
Record player `(x, y)` in a list. Slime (when not fused) follows `history[offset]`.
```python
def update_history(self):
    self.history.insert(0, (self.x, self.y))
    if len(self.history) > 100:
        self.history.pop()
```

### Pattern 2: Tap-Hold Input Buffering
Differentiate between a quick tap (Spit) and a long hold (Charge Shot).
```python
if pyxel.btn(pyxel.KEY_SPACE):
    self.charge_timer += 1
elif pyxel.btnr(pyxel.KEY_SPACE):
    if self.charge_timer > 15:
        self.fire_charge_shot()
    else:
        self.fire_spit()
    self.charge_timer = 0
```

## Anti-Patterns to Avoid

### Hard-Coded Room Transitions
Avoid `if x > 128: x = 0; room += 1`.
Instead, use **Camera Snapping**: `cam_x = (player.x // 128) * 128`. This makes the 5x5 grid dynamic and uniform.

## Sources
- Game Programming Patterns (Position History).
- Metroidvania Architecture (Gating and Hubs).
