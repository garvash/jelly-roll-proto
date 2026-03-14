# Roadmap - Slime Drill Proto

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
