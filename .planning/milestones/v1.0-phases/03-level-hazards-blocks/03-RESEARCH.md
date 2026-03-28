# Phase 03: Level Hazards & Blocks - Research

**Date:** 2026-03-12
**Status:** Complete

## <user_constraints>
### Locked Decisions
- **Destructible Blocks:** Certain tile types removed when player impacts in `DIVING` state.
- **Juice Refund:** Small amount of juice returned on block destruction.
- **Impact Feedback:** Screen shake and hit-stop (stall) on block break.
- **Spikes & Hazards:** Tiles causing instant death/reset.
- **Collision Detection:** Expand `Player.move_and_collide` for hazard tiles.

### Claude's Discretion
- **Hit-Stop Duration:** 2-3 frames suggested.
- **Screen Shake Intensity:** Subtle (±2px).

### Deferred Ideas (OUT OF SCOPE)
- **BOSS-01 (Mole Boss):** Combat mechanics deferred.
</user_constraints>

## Standard Stack
### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pyxel | 2.8.2 | Engine | Native `tilemap.pget` and `camera()` for screen shake. |

## Architecture Patterns

### Pattern: Tile Lookup Strategy
Use `tilemap.pget(tx, ty)` for coordinate-based lookups and `tilemap.set(tx, ty, (0, 0))` for removal.
Divide world position by `TILE_SIZE` (8) to get tile coordinates.

### Hit-Stop Implementation
```python
# In main.py Game.update
if self.hit_stop_frames > 0:
    self.hit_stop_frames -= 1
    return
```

### Screen Shake Implementation
```python
# In main.py Game.draw
if self.shake_timer > 0:
    pyxel.camera(pyxel.rndi(-2, 2), pyxel.rndi(-2, 2))
    self.shake_timer -= 1
else:
    pyxel.camera(0, 0)
```

## Don't Hand-Roll
| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Screen Shake | Manual sprite offsets | `pyxel.camera()` | Global, handles all drawing. |
| Tile Identification | Pixel color checks | `tilemap.pget()` | Returns (u, v) tile tuples. |

## Common Pitfalls
- **Coordinate Mismatch:** Forgetting to divide by 8 for tilemap lookups.
- **Collision Overlap:** Checking for spikes *after* moving can result in death before the "hit" frame is rendered.

## Validation Architecture
- **Framework:** Pytest
- **REQ-ENV-01:** Test `player.is_alive == False` after touching spike tile.
- **REQ-DRILL-02:** Test `tilemap.pget(tx, ty) == (0, 0)` after drill impact.
