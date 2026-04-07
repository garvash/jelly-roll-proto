# Jelly Roll Proto

A sideview exploration platformer (Metroidvania) built in Pyxel. This project serves as a rapid prototype for a full game to be developed in Godot or Unity, focusing on the "dual-hero" fusion mechanic between a player character and a companion slime.

## Core Value

The primary goal is to prototype the **satisfying "fusion" loop**: using a companion slime to power a destructive "Drill Dive" that enables both exploration (breaking paths) and combat (finishing bosses).

## Current State

Shipped **v1.2 Unified Schema & Tilemap Rendering** (2026-04-07). Three milestones complete. Next milestone not yet planned.

## Current State

Shipped **v1.2 Unified Schema & Tilemap Rendering** (2026-04-07). Three milestones complete. Unified schema drives both game and converter, LDtk autoLayerTiles render terrain with visual variation, multi-layer parallax pipeline operational.

- **v1.0** (2026-03-28): Vertical slice — Celeste-style platforming, slime companion, Drill Dive fusion, Giant Mole boss, kick mechanic, collectibles, enemy encounters. Core gameplay loop validated.
- **v1.1** (2026-04-01): World expansion — Macro-Map with room persistence, 6 fusion abilities (Ram, Hold, Charge Shot, Bubble Shield, Slime Boost, CRACKED_V gating), save/checkpoint system, 320x180 display with 2x sprite scale, PNG spritesheet pipeline, event-gated door system, LDtk entity/door integration (entity-schema v0.4.0), full tech debt cleanup.
- **v1.2** (2026-04-07): Unified schema & tilemap rendering — entity-schema.json v1.0.0 with biomes section, schema.py lookup module, autoLayerTiles parsing (18,094 tiles, 32 variants), multi-layer parallax pipeline, collision/visual separation. Infrastructure ready for multi-biome.

## Vision

- **Dual-Hero Dynamic:** An independent pet slime that follows the player and fuses with them to grant special abilities.
- **Destructive Exploration:** Using the "Drill Dive" to carve paths through "soft" ground in an interconnected cavern.
- **Tactical Combat:** Managing "slime juice" to fire projectiles and timing the "Drill Dive" to exploit boss weaknesses.
- **Retro Aesthetic:** A dark, moody, and cramped cavern atmosphere using Pyxel's limited color palette.

## Project Context

- **Platform:** Pyxel (Python-based retro engine).
- **Codebase:** ~83K LOC Python (includes generated assets).
- **Future Path:** Transition to Godot or Unity for the full-scale production.

## Requirements

### Validated

- ✓ MOV-01: Classic platforming (Walk, Jump, Wall Slide) — v1.0
- ✓ MOV-02: Grounded and airborne Dash — v1.0 (later replaced by Kick)
- ✓ MOV-03: Core physics stability and kick mechanic — v1.0
- ✓ SLM-01: Companion slime with independent follow — v1.0
- ✓ SLM-02: Slime juice resource system — v1.0
- ✓ SLM-03: Slime Spit projectile combat — v1.0
- ✓ DRILL-01: Drill Dive fusion ability — v1.0
- ✓ DRILL-02: Destructive traversal — v1.0
- ✓ ENV-01: Cavern biome with hazards — v1.0
- ✓ BOSS-01: Giant Mole boss — v1.0
- ✓ PROG-01: Linear progression flow — v1.0
- ✓ HLT-01: Player health system (3 HP) — v1.0
- ✓ ENM-01: Snail and Bat enemies — v1.0
- ✓ INT-01: Kick, switches, and collectibles — v1.0
- ✓ MAP-01: 5x5 room switching and macro-map — v1.1
- ✓ MAP-02: Room layouts via pml-to-ldtk pipeline with event-gated doors — v1.1
- ✓ MAP-03: State persistence across rooms — v1.1
- ✓ MAP-04: Biome-specific tile identification — v1.1
- ✓ ABL-01: Slime Ram fusion with horizontal gating — v1.1
- ✓ ABL-02: CRACKED_V vertical gating (Drill Dive + Slime Boost) — v1.1
- ✓ ABL-03: Directional Slime Hold — v1.1
- ✓ ABL-04: Charge Slime Shot — v1.1
- ✓ ABL-05: Bubble Shield — v1.1
- ✓ ABL-06: Yoshi-style Double Jump — v1.1
- ✓ SYS-01: Save Rooms/Checkpoints with JSON persistence — v1.1
- ✓ SYS-02: Mini-map HUD bar — v1.1
- ✓ SYS-03: Pause Screen with Macro-Map view — v1.1
- ✓ SYS-04: Heart Containers and Juice Capacity upgrades — v1.1
- ✓ SCHEMA-01: Unified schema file for tile and entity definitions — v1.2 Phase 17
- ✓ SCHEMA-02: Schema-driven IntGrid value mapping (replace hardcoded constants) — v1.2 Phase 18
- ✓ SCHEMA-03: pml-to-ldtk converter reads tile/entity definitions from shared schema — v1.2 Phase 18
- ✓ SCHEMA-04: Schema supports per-biome tileset sections — v1.2 Phase 17
- ✓ TILE-01: Load autoLayerTiles from LDtk simplified export — v1.2 Phase 19
- ✓ TILE-02: Render terrain with visual variation (edges, corners) via tilemap — v1.2 Phase 19
- ✓ TILE-03: Tiles render as defined (flip flags deferred, all tiles f=0) — v1.2 Phase 19
- ✓ TILE-04: Collision (IntGrid) independent from visual rendering (autoLayerTiles) — v1.2 Phase 19
- ✓ TILE-05: Schema defines tilemap layers with z-order and parallax scroll rate — v1.2 Phase 17
- ✓ TILE-06: Multi-layer parallax rendering at independent scroll rates — v1.2 Phase 19

### Active

(No active requirements — v1.2 milestone complete)

### Out of Scope

- Mobile app — web-first approach
- Complex NPC Dialog — keep focus on mechanics
- Multiple Biomes — focus on Cavern first
- Inventory System — all upgrades are mechanical/physical (slime size)
- Dynamic lighting — stick to Pyxel's palette

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pyxel Engine | Fast prototyping of retro-style mechanics | ✓ Good — enabled 11-day v1.0 delivery |
| Dual-Hero Fusion | Creates unique resource-management layer to platforming | ✓ Good — core loop feels satisfying |
| Per-Block Consumption | Rewards precision and efficiency in drilling | ✓ Good — validated in v1.0 |
| Dissipating Slime | Adds high-stakes "vulnerability" state when juice is empty | ✓ Good — creates tension |
| Dash removed for Kick | Kick provides more interesting combat/puzzle interactions | ✓ Good — better gameplay variety |
| Physics-based slime follow | Replaced lerp with acceleration/friction for weight | ✓ Good — feels more natural |
| Room-entry block reset | Prevents soft-locks from permanent destruction | ✓ Good — pragmatic for prototype |
| IID-based item persistence | LDtk instance IDs for permanent item tracking | ✓ Good — clean integration |
| 24-frame ease-out LERP transitions | Smooth camera slide between rooms | ✓ Good — feels polished |
| V button unified (D-07/D-10/D-22) | V=dash unfused, DOWN+V=drill dive; kick removed | ✓ Good — cleaner input model |
| Charge-to-fuse system | Hold fuse button to initiate fusion abilities | ✓ Good — unifies ability activation |
| Mana shield pattern | Fused damage drains juice instead of HP | ✓ Good — rewards staying fused |
| Event-gated doors | "event" action + event_id replaces tile ID 4 boss gates | ✓ Good — flexible gating |
| ABL-07 removed (D-21) | Reform Block cut — terrain fill too niche for prototype | ✓ Good — reduced scope |
| 320x180 display | Super Metroid-style layout with 16px HUD strip | ✓ Good — better readability |
| PNG spritesheet pipeline | Aseprite → PNG replacing Pyxel image banks | ✓ Good — standard workflow |
| Entity-schema v0.4.0 | Shared JSON schema between code and pml-to-ldtk converter | ✓ Good — single source of truth |
| Entity-schema v1.0.0 biomes section | Unify tile, entity, and layer definitions in one schema | ✓ Good — eliminates hardcoded constants, biome-ready |
| Full LDtk project file for autoLayerTiles | Parse output.ldtk directly instead of simplified export | ✓ Good — 18,094 tiles with correct coordinates |
| TILE-03 flip flags deferred | All 18,094 tiles have f=0, no flip rendering needed yet | ✓ Good — avoids Pyxel limitation workaround |

## Constraints

- Pyxel 320x180 display (320x176 game viewport + 16px HUD strip)
- 16-color palette
- Prototype scope — validate mechanics, not production-quality art
- ~83K LOC Python codebase

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-07 after v1.2 milestone*
