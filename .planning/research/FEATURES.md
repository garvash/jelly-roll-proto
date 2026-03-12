# Feature Research

**Domain:** Metroidvania Prototype (Slime-Drill)
**Researched:** 2025-03-12
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Tight Movement | Metroidvanias live/die by platforming feel. | MEDIUM | Needs custom physics (gravity, friction, air control). |
| Ability Gates | Fundamental loop of the genre. | LOW | "Soft" blocks that require the Drill ability to break. |
| Interconnectivity | Exploration must feel non-linear. | HIGH | Level design must wrap around (shortcuts/loops). |
| Combat Feedback | Hitting/Getting hit must feel visceral. | LOW | Screenshake, freeze-frames (hitstop), knockback. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Slime Fusion | Unique resource-management mechanic. | MEDIUM | Slime must follow player and "attach" for the Drill Dive. |
| Drill Navigation | Moving *through* geometry. | HIGH | Transforming "solid" tiles into "passable" air via destruction. |
| Resource Juice | Strategic depth to traversal/combat. | MEDIUM | Slime "shrinks" as you use Spit/Drill; refill by standing still or eating. |
| Slime Spit | Scaling projectile attack. | LOW | Number of projectiles scales with Slime's size (Juice level). |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Procedural Levels | Infinite replayability. | Breaks Metroidvania flow. | Hand-crafted "Metroid-style" rooms with intentional secrets. |
| RPG Stats/XP | Sense of growth. | Bloats the prototype; hard to balance. | Growth via physical Slime size/juice capacity upgrades. |
| Full Map Screen | Navigation ease. | Hard to implement in Pyxel for a 1-biome proto. | Strong environmental signposting (lighting/colors). |

## Feature Dependencies

```
[Movement (MOV-01)]
    └──requires──> [Collision System]
                       └──requires──> [Tilemap Layering]

[Drill Dive (DRILL-01)] ──requires──> [Slime Juice (SLM-02)]

[Destruction (DRILL-02)] ──enhances──> [Movement (MOV-01)]

[Drill Dive (DRILL-01)] ──conflicts──> [Slime Spit (SLM-03)] (Cannot spit while drilling)
```

### Dependency Notes

- **Drill Dive requires Slime Juice:** The ability is powered by the Slime's mass. No juice = no drill.
- **Destruction enhances Movement:** Breaking blocks creates new, faster shortcuts through the environment.
- **Drill conflicts with Spit:** Using juice for one prevents using it for the other, creating a tactical choice (Attack vs. Traversal).

## MVP Definition

### Launch With (v1 - "The Slice")

Minimum viable product — what's needed to validate the concept.

- [ ] **Tight Physics** — Feel is everything.
- [ ] **Slime Follow** — The companion dynamic must be established early.
- [ ] **Drill Fusion** — The core "hook" of the game.
- [ ] **Soft Blocks** — Validating the destructive exploration loop.
- [ ] **One Boss** — Proving the combat viability of the Drill mechanic.

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] **Juice Scaling** — Make the Slime visibly grow/shrink.
- [ ] **Parallax Layers** — Enhance the "Moody Cavern" atmosphere.
- [ ] **Save Points** — Necessary for a 15-minute slice.

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Multiple Biomes** — Expand the world.
- [ ] **New Slime Types** — Different fusions (e.g., Slime Hook).

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Movement Feel | CRITICAL | HIGH | P1 |
| Drill Traversal | HIGH | HIGH | P1 |
| Slime Follower | HIGH | MEDIUM | P1 |
| Slime Spit | MEDIUM | LOW | P2 |
| Boss Fight | HIGH | MEDIUM | P1 |
| HUD/Juice Bar | MEDIUM | LOW | P2 |

**Priority key:**
- P1: Must have for launch (The Vertical Slice)
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Animal Well | Hollow Knight | Our Approach |
|---------|--------------|--------------|--------------|
| Traversal | Tools (Yoyo/Bubble) | Dash/Wings | **Slime Fusion Drill** |
| Companion | Minimal | None | **Central Mechanic (Pet)** |
| Environment | Non-destructive | Static | **Destructive (Carving Paths)** |

## Sources

- [GDC: Level Design in Metroidvanias](https://www.gdcvault.com/) — Reference for gating mechanics.
- [Animal Well Research] — Inspiration for mechanical tool-based progression.
- [Hollow Knight Physics Analysis] — Standards for platformer responsiveness.

---
*Feature research for: Slime-Drill Metroidvania*
*Researched: 2025-03-12*
