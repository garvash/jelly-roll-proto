# Phase 02: Slime Companion & Fusion - Research

**Date:** 2026-03-12
**Status:** Complete

## <user_constraints>
### Locked Decisions
- **Physics Leash:** The slime follows the player using physics-based leash logic. Trails behind and switches sides intelligently.
- **Dissipation/Reform:** Reform near player if distance exceeds threshold.
- **Visual Scaling:** Scales from 8x8 (100% juice) to 2x2 (0% juice).
- **Juice Regeneration:** Passive auto-replenish when not fused.
- **Drill Dive:** Triggered by Down + Dash (X) in air. High-speed downward dive with vertical priority.
- **Impact Cost:** Juice consumed "per hit" on surface/entity impact.

### Claude's Discretion
- **Fusion Visuals:** Drill attachment sprite implementation.
- **Celeste-style Snappiness:** Maintain weighted feel.

### Deferred Ideas (OUT OF SCOPE)
- SLM-03 (Slime Spit)
- DRILL-02 (Destructive traversal)
</user_constraints>

## Standard Stack
### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pyxel | 2.8.2 | Engine | Native scaling support in 2.x via `blt(..., scale=f)`. |

## Architecture Patterns

### Slime Follow Pattern (Position History)
Store a queue of the player's last 10 positions. The slime targets a position at index 5-8 of the queue.
```python
# Pseudo-code logic
self.history.append((player.x, player.y))
if len(self.history) > 10:
    self.history.pop(0)
target = self.history[0]
self.x += (target[0] - self.x) * 0.2
```

### Drill Dive FSM State
```python
# src/entities/player.py
if self.state == "DIVING":
    self.dy = DRILL_SPEED
    self.dx *= DRILL_DRIFT_MULTS
    if self.level_map.check_collision(self.x, self.y + 1, ...):
        self.on_impact() # Consumes juice
```

## Don't Hand-Roll
| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Sprite Scaling | Manual pixel loop | `pyxel.blt(..., scale=s)` | Native, hardware-accelerated (internal). |

## Common Pitfalls
- **Leash Snapping:** Slime "teleporting" look. Solution: Use `lerp` for smooth position transitions even during reform.
- **Juice Zero State:** Forgetting to disable the dive move at 0 juice.

## Validation Architecture
- **Framework:** Pytest (existing in `tests/`)
- **REQ-SLM-01:** Test slime distance from player after N frames of movement.
- **REQ-SLM-02:** Test `Slime.scale` property matches `juice` level.
- **REQ-DRILL-01:** Verify `player.state == "DIVING"` and `dy > MAX_FALL_SPEED`.
