# Milestones - Jelly Roll Proto

## v1.3 16x16 Tile Migration (Shipped: 2026-04-09)

**Phases:** 4 (20-23) | **Plans:** 7 | **Tasks:** 15 | **Timeline:** 2026-04-08 to 2026-04-09 (2 days)
**Stats:** 146 files changed, +11,483 / -20,375 lines

**Key accomplishments:**

1. TILE_SIZE=16 throughout codebase — SPRITE_SCALE indirection completely removed, all derived constants updated
2. entity-schema.json bumped to v2.0.0 with grid_size=16, rooms now 20x11 tiles (320x176px unchanged)
3. LDtk project reconfigured for 16x16 grid — tileset, autoLayerTiles, and entity layers all migrated
4. All entity collision boxes aligned to 16x16 visuals (player 10x14, enemies 16x16, boss 24x28)
5. physics-schema.json v0.2.0 with tile-unit values halved (same pixel distances, new tile scale)
6. CONVERTER-HANDOFF.md documenting all breaking changes for the pml-to-ldtk converter maintainer

**Delivered:** Complete 16x16 tile migration eliminating the 8x8 collision / 16x16 visual split. Same pixel dimensions, simpler math, cleaner code. Converter handoff enables external tool update.

**Archive:** [v1.3-ROADMAP.md](milestones/v1.3-ROADMAP.md) | [v1.3-REQUIREMENTS.md](milestones/v1.3-REQUIREMENTS.md)

---

## v1.2 Unified Schema & Tilemap Rendering (Shipped: 2026-04-07)

**Phases:** 3 (17-19) | **Plans:** 6 | **Tasks:** 10 | **Timeline:** 2026-04-05 to 2026-04-07 (3 days)
**Stats:** 16 files changed, +884 / -175 lines

**Key accomplishments:**

1. Unified entity-schema.json v1.0.0 with biomes section covering tile definitions, entity definitions, and layer definitions in one file
2. Schema.py module with 9 public lookup functions replacing all hardcoded TILE_* constants
3. Game and pml-to-ldtk converter both consume tile/entity definitions from the shared schema
4. Parsed 18,094 autoLayerTiles from LDtk with 32 unique tile variants for terrain edge/corner/inner visuals
5. Multi-layer parallax rendering pipeline with z-ordered layers at independent scroll rates
6. Clean collision/visual separation — IntGrid for physics, autoLayerTiles for visuals

**Delivered:** Unified schema drives both game and converter, LDtk terrain renders with proper visual variation, and multi-layer parallax pipeline is operational. Infrastructure ready for multi-biome support.

**Archive:** [v1.2-ROADMAP.md](milestones/v1.2-ROADMAP.md) | [v1.2-REQUIREMENTS.md](milestones/v1.2-REQUIREMENTS.md)

---

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
