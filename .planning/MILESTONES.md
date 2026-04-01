# Milestones - Jelly Roll Proto

## v1.1 World Expansion & New Abilities (Shipped: 2026-04-01)

**Phases:** 10 (7-16) | **Plans:** 30 | **Tasks:** 52 | **Timeline:** 2026-03-27 to 2026-04-01 (6 days)
**Stats:** 221 commits, 367 files changed, +54,921 / -2,497 lines

**Key accomplishments:**

1. Macro-Map with 5x5 room grid, camera snapping, and room state persistence
2. 6 fusion abilities: Slime Ram, Directional Hold, Charge Shot, Bubble Shield, Slime Boost, CRACKED_V gating
3. Save/checkpoint system with JSON persistence, title/pause/death screens, mini-map HUD
4. 320x180 display expansion with 2x sprite scale and PNG spritesheet pipeline (Aseprite workflow)
5. Event-gated door system replacing hardcoded tile ID 4 boss gates
6. LDtk entity/door integration fixes (aliases, flat customFields, direction normalization, 3 new entity stubs)

**Delivered:** Full world expansion with interconnected rooms, 6 fusion abilities for gated exploration, save system, 320x180 display with PNG sprites, and complete integration/tech debt cleanup.

**Archive:** [v1.1-ROADMAP.md](milestones/v1.1-ROADMAP.md) | [v1.1-REQUIREMENTS.md](milestones/v1.1-REQUIREMENTS.md) | [v1.1-MILESTONE-AUDIT.md](milestones/v1.1-MILESTONE-AUDIT.md)

---

## v1.0 Vertical Slice (Shipped: 2026-03-28)

**Phases:** 6 (1-6) | **Plans:** 14 | **Timeline:** 2026-03-12 to 2026-03-22 (11 days)

**Key accomplishments:**

1. Celeste-style platforming with walk, jump, wall slide, and kick mechanics
2. Independent slime companion with juice resource system and shadow follow logic
3. Drill Dive fusion ability for destructive traversal through soft blocks
4. Giant Mole boss with spit-stun-drill combat loop
5. Cavern biome with hazards, destructible blocks, and collectible items
6. 3 HP health system with Snail and Bat enemies

**Delivered:** A playable vertical slice demonstrating the dual-hero fusion mechanic in a single cavern biome with one boss, proving the core gameplay loop works.

**Archive:** [v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md) | [v1.0-REQUIREMENTS.md](milestones/v1.0-REQUIREMENTS.md) | [v1.0-MILESTONE-AUDIT.md](milestones/v1.0-MILESTONE-AUDIT.md)
