# Pitfalls Research

**Domain:** Metroidvania Development (Pyxel)
**Researched:** 2025-03-12
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Soft-Locking via Destruction

**What goes wrong:**
Player drills through a "soft" block floor into a pit, but lacks the ability (juice or height) to jump back out, and there's no way to progress.

**Why it happens:**
Destructive traversal allows players to modify the level in ways the designer didn't intend.

**How to avoid:**
1. Design "One-way" drops with clear exits.
2. Implement a "Reset Room" or "Respawn at last solid ground" mechanic.
3. Use regenerating blocks for critical path traversal.

**Warning signs:**
Testers getting stuck and having to restart the script.

**Phase to address:**
Phase 2 (Level Design & DRILL-02).

---

### Pitfall 2: The "Floaty" Platformer Feel

**What goes wrong:**
Jump height is fixed, gravity is too low, and movement lacks friction. The game feels "slippery" or unresponsive.

**Why it happens:**
Relying on simple `y += velocity` without implementing variable jump height (holding button longer) or coyote time (jump after leaving ledge).

**How to avoid:**
1. Implement variable jump height.
2. Add "Coyote Time" (3-5 frames of grace).
3. Use gravity scaling (falling faster than rising).

**Warning signs:**
Movement feels frustrating; hard to land on small platforms.

**Phase to address:**
Phase 1 (Core Movement MOV-01).

---

### Pitfall 3: Pyxel Collision "Tunneling"

**What goes wrong:**
The Drill moves so fast it passes through a thin wall or block without triggering a collision.

**Why it happens:**
In one frame, the position goes from `x=10` to `x=20`, skipping the wall at `x=15`.

**How to avoid:**
1. Limit maximum velocity.
2. Use "Sub-stepping" (check for collisions at multiple points along the velocity vector).
3. Ensure destructible blocks are at least as thick as the maximum per-frame travel distance.

**Warning signs:**
Player occasionally "glitches" through walls during a Drill Dive.

**Phase to address:**
Phase 2 (DRILL-01).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hard-coded Tile IDs | Faster to write `if tile == 17`. | Hard to change tileset later. | Never; use a `Map` class constants. |
| Global Variables for Juice | Easy to access from anywhere. | Hard to track state changes or add multi-slime support. | Only in the first hour of prototyping. |
| Neglecting `pyxel edit` | Writing code to draw every line/pixel. | Immense time waste for assets. | Never; use the built-in asset editor. |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Slime Following | Direct `slime.x = player.x`. | Slime feels like a rigid attachment. Use a lerp or breadcrumb trail for "organic" feel. |
| HUD Rendering | Not accounting for camera offset. | HUD moves with the player and disappears. Draw HUD using absolute coordinates *after* resetting camera. |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Excessive Print Loops | Frame rate drops to 10 FPS. | Remove all `print()` calls in the `update` or `draw` loops. | Immediately in Pyxel. |
| Iterating All Tiles | Stutter when entering new rooms. | Only check collision for tiles within the entity's bounding box. | At map sizes > 128x128. |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No Juice Feedback | Player tries to drill, nothing happens, feels like a bug. | Slime should flash red or emit a "puff" sound when out of juice. |
| Screen Shake Overuse | Physical discomfort/headache. | Keep shake subtle and linked only to high-impact events (Drilling/Boss hit). |
| Poor Signposting | Player wanders for 10 minutes without finding the Drill. | Use lighting (light tiles) to guide the player toward the first upgrade. |

## "Looks Done But Isn't" Checklist

- [ ] **Jump:** Often missing jump buffering — verify player can jump if button pressed 3 frames *before* landing.
- [ ] **Wall Slide:** Often missing "sticky" feel — verify the player doesn't instantly fall when touching a wall.
- [ ] **Drill:** Often missing "hit stop" — verify the game pauses for 1 frame when a block is destroyed for "crunch."

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Slippery Movement | MEDIUM | Refactor physics to use acceleration/friction instead of direct velocity setting. |
| Map Corruption | HIGH | Keep git backups of `.pyxres` files; Pyxel's binary format can be fragile if interrupted. |

---
*Pitfalls research for: Slime-Drill Metroidvania*
*Researched: 2025-03-12*
