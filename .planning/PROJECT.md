# Jelly Roll Proto

A sideview exploration platformer (Metroidvania) built in Pyxel. This project serves as a rapid prototype for a full game to be developed in Godot or Unity, focusing on the "dual-hero" fusion mechanic between a player character and a companion slime.

## Core Value

The primary goal is to prototype the **satisfying "fusion" loop**: using a companion slime to power a destructive "Drill Dive" that enables both exploration (breaking paths) and combat (finishing bosses).

## Current State

Shipped **v1.0 Vertical Slice** (2026-03-28): A playable cavern biome with Celeste-style platforming, slime companion with juice resource, Drill Dive fusion, Giant Mole boss, kick mechanic, collectibles, and enemy encounters. The core gameplay loop (explore, drill, fight) is validated.

**v1.1 World Expansion** nearing completion — Phases 7-10, 12-15 complete. Macro-Map, 6 fusion abilities (Ram, Hold, Charge Shot, Bubble Shield, Slime Boost, CRACKED_V gating), 320x180 display with 2x sprite scale, PNG spritesheet pipeline, event-gated door system, full tech debt cleanup, and LDtk entity/door integration fixes (entity aliases, flat customFields, direction normalization, 3 new entity stubs at schema v0.4.0). Phase 16 (housekeeping/verification) remains.

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

### Active (v1.1)

- [ ] MOV-04: Fusion Dash / Slime Ram (Barrel Roll) mechanic
- [ ] SLM-04: Directional tap-to-hold and Charge Shot logic
- [ ] DEF-01: Bubble Shield and Yoshi Double Jump
- [ ] SYS-01: Save/Checkpoint system
- [ ] UI-02: HUD expansion with Mini-map and Pause screen

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

## Constraints

- Pyxel 128x128 pixel screen (expandable to 256x256)
- 16-color palette
- Prototype scope — validate mechanics, not production-quality art

---
*Last updated: 2026-04-01 after Phase 15 (LDtk entity/door integration)*
