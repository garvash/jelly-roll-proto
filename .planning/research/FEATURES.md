# Feature Landscape: Milestone v1.1

**Project:** Jelly-Roll
**Researched:** 2026-03-12

## Table Stakes

Features expected in a "Metroidvania" style expansion.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| 5x5 World | Standard map size for prototypes. | Medium | Requires camera logic and room-based spawning. |
| Save Rooms | Essential for persistence. | Low | Simple JSON serialization. |
| HUD Mini-map | Navigation aid for multi-room maps. | Medium | Requires tracking `rooms_visited`. |

## Differentiators

Unique "Fusion" and "Option" mechanics.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Slime Ram | Forward momentum + combat utility. | Medium | 8-way vs 1-way (Slime Ram is 1-way forward dash). |
| Nitro-Ejection | Vertical freedom at a cost. | Medium | Infinite jump using "Juice" resource. |
| Charge Shot | Rewarding patience and timing. | Low | Tap-Hold logic in input handling. |
| Bubble Shield | Defensive resource sink. | Low | Area protection while draining Slime meter. |

## Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Procedural Gen | High risk, breaks Z-Spiral logic. | Hand-crafted 5x5 LDtk world. |
| Complex XP System | Adds bloat to a 15-min proto. | Health/Juice "Tanks" for upgrades. |

## Feature Dependencies

```
Drill Dive → Slime Ram (Sequence Break protection)
Slime Ram → BossMole (Reach the Deep)
BossMole → Nitro-Ejection (The Escape)
```

## MVP Recommendation
Prioritize **Slime Ram** and the **5x5 Grid**, as they define the core exploration loop. **Nitro-Ejection** should be the "reward" for finishing the boss.

## Sources
- "Gradius Option" mechanics research.
- Metroidvania level design patterns (S-Curve/Z-Spiral).
