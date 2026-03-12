# Project Research Summary

**Project:** Slime-Drill Metroidvania Prototype
**Domain:** Retro Indie Platformer (Pyxel)
**Researched:** 2025-03-12
**Confidence:** HIGH

## Executive Summary

The "Slime-Drill" prototype is a sideview Metroidvania focused on a unique "Fusion" mechanic between a player character and a companion slime. Research indicates that Pyxel is the ideal engine for this 1-biome vertical slice due to its constraints, which mirror the intended retro aesthetic and allow for rapid mechanical iteration. Experts building in this domain prioritize "feel" (physics/responsiveness) and "gating" (ability-based progression) above all else.

The recommended approach involves a three-phase development cycle focusing first on tight platforming physics, followed by the Slime-Drill fusion logic, and concluding with a hand-crafted level that validates the "Destructive Exploration" loop. The primary risk is "soft-locking" players through map destruction, which must be mitigated via regenerating blocks or robust room-reset mechanics.

## Key Findings

### Recommended Stack

We will use **Python 3.11+** with the **Pyxel 2.1+** engine. **uv** will manage dependencies to ensure a reproducible environment. The built-in Pyxel Editor will be the primary tool for sprite and tilemap creation, supplemented by Aseprite for complex animations.

**Core technologies:**
- **Python 3.11:** Provides the performance overhead needed for entity-heavy logic in a retro engine.
- **Pyxel:** Fixed 16-color palette and low resolution enforce the "Moody Cavern" aesthetic.
- **uv:** Ensures fast, consistent environment setup for developers and testers.

### Expected Features

The prototype must deliver standard Metroidvania "Table Stakes" while proving the "Slime-Drill" differentiator.

**Must have (table stakes):**
- **Tight Movement:** Variable jump height, coyote time, and responsive air control.
- **Ability Gates:** "Soft" blocks that can only be bypassed using the Drill.

**Should have (competitive):**
- **Slime Fusion:** The core "hook" where the companion transforms into a drill.
- **Destructive Navigation:** Carving new paths through the environment.

**Defer (v2+):**
- **Map Screen:** Not needed for a single-biome prototype; focus on environmental signposting.

### Architecture Approach

A decoupled **Entity-Component-System (ECS)** lite approach is recommended, separating `Player`, `Slime`, and `Level` logic into distinct modules.

**Major components:**
1. **Player Entity:** Manages the Finite State Machine (IDLE, RUN, JUMP, DRILL).
2. **Slime Entity:** Handles independent "Leash" AI and the "Juice" resource system.
3. **Level Manager:** Coordinates tile-based collision and the "Destructible Block" dictionary.

### Critical Pitfalls

1. **Soft-Locking:** Avoid by designing levels with "Reset" points or regenerating "soft" tiles.
2. **"Floaty" Physics:** Mitigate by implementing gravity scaling and jump buffering early.
3. **Collision Tunneling:** Prevent by limiting max velocity and using sub-stepping for the Drill Dive.

## Implications for Roadmap

Based on research, the suggested phase structure is:

### Phase 1: Core Movement & Physics
**Rationale:** Platformers succeed or fail based on "feel." This must be validated before adding complex mechanics.
**Delivers:** Player character with Walk, Jump, Wall Slide, and Dash (MOV-01/02).
**Addresses:** Tight Movement (Table Stakes).
**Avoids:** Floaty Platformer Feel (Pitfall 2).

### Phase 2: Slime Companion & Fusion
**Rationale:** The "Slime-Drill" fusion is the project's Core Value. It requires Phase 1 physics to be stable.
**Delivers:** Independent Slime AI, Juice system, and the Drill Dive ability (SLM-01/02, DRILL-01).
**Uses:** FSM Pattern for Fusion states.
**Implements:** Slime Entity & Juice State Management.

### Phase 3: Destructive World & Boss
**Rationale:** Validates the "Exploration" and "Combat" loops using the mechanics from Phase 2.
**Delivers:** Cavern biome with destructible blocks and the Mole Boss (ENV-01, DRILL-02, BOSS-01).
**Addresses:** Destructive Navigation (Differentiator).
**Avoids:** Soft-Locking via Destruction (Pitfall 1).

### Phase Ordering Rationale

- **Physics First:** Ensures the foundation is solid before layering on the Slime/Drill logic.
- **Mechanics before Level:** Prevents having to redesign the level if the Drill speed or Slime size changes.
- **Pitfall Mitigation:** Each phase includes specific checks (Coyote time in P1, Sub-stepping in P2, Room-reset in P3) to address researched risks.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (Slime AI):** Needs specific investigation into "Leash" algorithms to ensure the slime doesn't get stuck on corners.
- **Phase 3 (Mole Boss):** Needs state-machine research for the "Dig/Pop-up" phases to ensure the vulnerability window is fair.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Movement):** Well-documented "Celeste-style" physics patterns are readily available.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Pyxel is the industry standard for Python-based retro prototypes. |
| Features | HIGH | Clear differentiation from genre giants (Hollow Knight/Animal Well). |
| Architecture | MEDIUM | Python performance with destructible maps needs empirical testing. |
| Pitfalls | HIGH | Metroidvania pitfalls are well-documented by the indie community. |

**Overall confidence:** HIGH

### Gaps to Address

- **Slime Pathfinding:** Researching simple A* vs. Breadcrumb following for the companion.
- **Block Regeneration:** Determining if blocks should respawn on room-reentry or after a timer.

## Sources

### Primary (HIGH confidence)
- [Pyxel Official Docs](https://github.com/kitao/pyxel) — Feature verification.
- [GDC: Designing for Exploration](https://www.gdcvault.com/) — Metroidvania gating standards.

### Secondary (MEDIUM confidence)
- [Celeste Physics Analysis](https://celestegame.github.io/celeste-physics.html) — Movement standards.
- [Indie Game Decon: Destruction Mechanics] — Strategy for tile-based carving.

---
*Research completed: 2025-03-12*
*Ready for roadmap: yes*
