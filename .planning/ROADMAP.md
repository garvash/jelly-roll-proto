# Roadmap - Jelly Roll Proto

## Phase 1: Core Movement & Physics
**Goal:** Deliver a player character with high-quality, responsive platforming physics (Celeste-style) including Walk, Jump, Wall Slide, and Dash.
- [x] **MOV-01**: Classic platforming (Walk, Jump, Wall Slide).
- [x] **MOV-02**: Grounded and airborne Dash.

## Phase 2: Slime Companion & Fusion
**Goal:** Implement the independent slime companion, the "Juice" resource system, and the core "Slime-Drill" fusion (Drill Dive).
**Plans:** 4 plans
- [x] 02-01-PLAN.md — Core Slime Entity & Follow Logic (SLM-01)
- [x] 02-02-PLAN.md — Juice Resource & Scaling (SLM-02)
- [x] 02-03-PLAN.md — Drill Dive Mechanic & Fusion FSM (DRILL-01)
- [x] 02-04-PLAN.md — Verification & Final Polish
- [x] **SLM-01**: Companion slime that follows the player independently.
- [x] **SLM-02**: Slime juice resource system.
- [x] **DRILL-01**: Drill Dive fusion ability (Down + Air) with guided steering.

## Phase 3: Destructive World & Boss
**Goal:** Create the cavern biome with destructible blocks and the Mole boss to validate the "Exploration" and "Combat" loops.
- [x] **ENV-01**: Dark & Moody cavern biome with interconnected rooms and hazard spikes.
- [x] **DRILL-02**: Destructive traversal (breaking "soft" blocks) with hit-stop and screen-shake feedback.
- [x] **BOSS-01**: Giant Mole boss with Dig/Pop-up phases.
- [x] **PROG-01**: Linear progression flow (Start -> Boss -> Exit).

## Phase 4: Level Interactivity & Items
**Goal:** Expand the gameplay with more interactive level elements and collectibles.
- [x] **INT-01**: Kick mechanic, switches, and item collectibles (Energy/Missile Tanks). (2026-03-15)
- [x] **MOV-03**: Core physics stability and removal of dash in favor of kick. (2026-03-15)

## Phase 5: New Enemies & Player Health
**Goal:** Implement a player health system and populate the cavern with Snail and Bat enemies.
- [x] **HLT-01**: Player health system (3 HP) with hearts UI and invulnerability. (2026-03-14)
- [x] **ENM-01**: Snail and Bat enemies with platform-aware and diving AI. (2026-03-14)

## Phase 7: Macro-Map & Room Persistence
**Goal:** Deliver a 5x5 Metroidvania world system with level-clamped camera, freeze-and-slide transitions, and state persistence.
**Plans:** 2/2 complete
- [x] 07-01-PLAN.md -- WorldManager Refactor & Camera Clamping (2026-03-27)
- [x] 07-02-PLAN.md -- Metroid Transitions & State Persistence (2026-03-27)
