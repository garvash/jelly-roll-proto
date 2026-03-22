# Jelly Roll Proto

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

### Validated

- [x] **MOV-01**: Classic platforming (Walk, Jump, Wall Slide). (2026-03-12)
- [x] **MOV-02**: Grounded and airborne Dash. (Note: Dash was later removed/replaced by Kick in core gameplay). (2026-03-12)
- [x] **SLM-01**: Companion slime that follows the player independently. (2026-03-13)
- [x] **SLM-02**: Slime juice resource system (recharging, dictates ability size/duration). (2026-03-13)
- [x] **SLM-03**: Slime Spit (Projectile) combat. Projectile count scales with slime size. (2026-03-14)
- [x] **DRILL-01**: Drill Dive fusion ability (Down + Air) with guided steering. (2026-03-13)
- [x] **DRILL-02**: Destructive traversal (breaking "soft" blocks with the drill). (2026-03-14)
- [x] **ENV-01**: Dark & Moody cavern biome with interconnected rooms. (2026-03-14)
- [x] **BOSS-01**: Giant Mole boss with Dig/Pop-up phases and "Slime-to-Drill" vulnerability loop. (2026-03-14)
- [x] **PROG-01**: Linear progression flow (Start -> Find Drill -> Fight Boss -> Exit). (2026-03-14)
- [x] **HLT-01**: Player health system (3 HP) with hearts UI and invulnerability. (2026-03-14)
- [x] **ENM-01**: Snail and Bat enemies with platform-aware and diving AI. (2026-03-14)
- [x] **INT-01**: Kick mechanic, switches, and item collectibles (Energy/Missile Tanks). (2026-03-15)

## Current Milestone: v1.1 World Expansion & New Abilities

**Goal:** Expand the prototype into a cohesive 5x5 micro-world with deep fusion mechanics and a complete Metroidvania gameplay loop.

**Target features:**
- **Macro-Map Expansion:** 5x5 Z-Spiral world layout with specific biomes (Awakening, Hammer, Chisel, Mole Nest).
- **New Fusion Abilities:** Slime Ram (Forward Dash) and Nitro-Ejection (Infinite Jump).
- **Enhanced Slime Control:** Directional Tap-Hold, Charge Shot, and Reform (terrain filling).
- **Defensive Mechanics:** Bubble Shield and Yoshi-style Double Jump.
- **World Persistence:** Save Rooms and Checkpoints.
- **HUD & UI:** Mini-map bar, expanded screen size, and Pause Map.

### Active

- [ ] **MAP-01**: Implement 5x5 room switching and macro-map topology.
- [ ] **MOV-04**: Fusion Dash / Slime Ram (Barrel Roll) mechanic.
- [ ] **SLM-04**: Directional tap-to-hold and Charge Shot logic.
- [ ] **DEF-01**: Bubble Shield and Yoshi Double Jump.
- [ ] **SYS-01**: Save/Checkpoint system.
- [ ] **UI-02**: HUD expansion with Mini-map and Pause screen.

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
*Last updated: 2026-03-20*
