# Domain Pitfalls: Milestone v1.1

**Project:** Jelly-Roll
**Researched:** 2026-03-12

## Critical Pitfalls

### Pitfall 1: Tilemap Overwrite (Destruction)
**What goes wrong:** Player breaks blocks in one room, but they "respawn" or the wrong tiles are removed because tilemap coordinates were relative, not absolute.
**Prevention:** Always use **World Coordinates** for `tilemap.pset`. 128x128 rooms in a 5x5 grid = 0 to 640 pixels (0 to 80 tiles).

### Pitfall 2: Entity Spam (Memory)
**What goes wrong:** Spawning all 25 rooms' worth of enemies at startup.
**Prevention:** Use **Room-Based Spawning**. Only instantiate entities when the camera enters their room. Despawn or deactivate off-screen enemies.

### Pitfall 3: Sequence Breaking (The Z-Spiral)
**What goes wrong:** Player reaches the boss room [4,4] early by clipping through walls or using unintended dash physics.
**Prevention:** Use **Logic Gating** (IntGrid markers) that require specific abilities (Drill Dive, Slime Ram). Test collision with high-velocity dashes (Slime Ram).

## Moderate Pitfalls

### Pitfall 1: Mini-map Scaling
**What goes wrong:** Mini-map takes up too much screen space on a 128x128 display.
**Prevention:** Use a 1-pixel per room or 2x2 pixels per room representation. Toggle with a key (e.g., TAB) instead of always-on.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| 5x5 World | Camera lag/jitter during snapping. | Snap immediately or use a very fast lerp (0.2s). |
| Slime Ram | Passing through 1-tile walls. | Check collision at multiple points along the dash path. |
| Persistence | Corrupted JSON if game crashes mid-save. | Save to a temporary file then rename. |

## Sources
- Pyxel community forums (Memory/Performance).
- Action-Platformer development post-mortems.
