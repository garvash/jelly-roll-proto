# Slime Drill Proto

A sideview exploration platformer (Metroidvania) built in Pyxel. This project serves as a rapid prototype for a full game to be developed in Godot or Unity, focusing on the "dual-hero" fusion mechanic between a player character and a companion slime.

## Core Value

The primary goal is to prototype the **satisfying "fusion" loop**: using a companion slime to power a destructive "Drill Dive" that enables both exploration (breaking paths) and combat (finishing bosses).

## Vision

- **Dual-Hero Dynamic:** An independent pet slime that follows the player and fuses with them to grant special abilities.
- **Destructive Exploration:** Using the "Drill Dive" to carve paths through "soft" ground in an interconnected cavern.
- **Tactical Combat:** Managing "slime juice" to fire projectiles and timing the "Drill Dive" to exploit boss weaknesses.
- **Retro Aesthetic:** A dark, moody, and cramped cavern atmosphere using Pyxel's limited color palette.

## Project Context

- **Platform:** Pyxel (Python-based retro engine).
- **Milestone 1 Goal:** Create a vertical slice with one biome, one boss, and one core ability.
- **Future Path:** Transition to Godot or Unity for the full-scale production.

## Requirements

### Active

- [ ] **SLM-01**: Companion slime that follows the player independently.
- [ ] **SLM-02**: Slime juice resource system (recharging, dictates ability size/duration).
- [ ] **SLM-03**: Slime Spit (Projectile) combat. Projectile count scales with slime size.
- [ ] **DRILL-01**: Drill Dive fusion ability (Down + Air) with guided steering.
- [ ] **DRILL-02**: Destructive traversal (breaking "soft" blocks with the drill).
- [ ] **ENV-01**: Dark & Moody cavern biome with interconnected rooms.
- [ ] **BOSS-01**: Giant Mole boss with Dig/Pop-up phases and "Slime-to-Drill" vulnerability loop.
- [ ] **PROG-01**: Linear progression flow (Start -> Find Drill -> Fight Boss -> Exit).

## Validated

- [x] **MOV-01**: Classic platforming (Walk, Jump, Wall Slide). (2026-03-12)
- [x] **MOV-02**: Grounded and airborne Dash. (2026-03-12)

### Out of Scope

- **Metroidvania Map Screen:** Not needed for a 1-biome prototype.
- **Inventory System:** All upgrades are mechanical/physical (slime size).
- **Multiple Biomes:** Focus on the Cavern first.
- **Complex NPC Dialog:** Keep the focus on mechanics.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pyxel Engine | Fast prototyping of retro-style mechanics. | — Pending |
| Dual-Hero Fusion | Creates a unique resource-management layer to platforming. | — Pending |
| Per-Block Consumption | Rewards precision and efficiency in drilling. | — Pending |
| Dissipating Slime | Adds a high-stakes "vulnerability" state when juice is empty. | — Pending |

---
*Last updated: 2026-03-12 after initialization*
