# Phase 06: Physics Refinement & Test Gaps - Research

**Researched:** 2026-03-18
**Domain:** Physics, Technical Debt, & Polish
**Confidence:** HIGH

## Summary
Phase 06 addresses critical polish issues identified in the prototype: the "floaty" and bug-prone slime companion physics, projectile collision edge cases, and missing visual feedback for enemy destruction. It also resolves technical debt by implementing the Celeste-style physics test suite that was stubbed in Phase 01 and re-organizing Phase 04 artifacts that were nested in Phase 03.

**Primary recommendation:** Transition slime movement from Lerp-based to a weighted Physics-based follow to match the player's "weight" and implement a "stuck-prevention" check for projectiles and companions.

<user_constraints>
## User Constraints

### Locked Decisions
- **Fix Slime Lodging:** Slime getting stuck in walls must be resolved (likely an AABB snap issue).
- **Physics Alignment:** Slime movement should feel less "floaty" and more consistent with the heroine's physics rules.
- **Destruction Polish:** Add explosion animations and particles for enemy destruction.
- **Juice Mechanics:** Enhance slime juice stains to stick to walls and linger (lingering is implemented, but wall-sticking needs verification).
- **Phase Split:** Move Phase 04 artifacts (Boss/Progression) out of the Phase 03 directory.
- **Test Completion:** Implement automated tests for core physics (Walk, Jump, Wall Slide).

### Claude's Discretion
- **Destruction Implementation:** Recommendation to use a simple particle pool or short-lived FSM-based effect entities.
- **Follow Logic:** Recommendation to use "History-based Target with Physics-based Movement" for the slime.

### Deferred Ideas
- LDtk map support (Researched but recommended for Phase 07 or 08 as it's a large structural change).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PHY-01 | Fix Slime wall lodging | Identified snap-to-floor/wall logic gaps in `Slime.update`. |
| PHY-02 | Refine Slime floatiness | History-lerp approach causes floatiness; needs acceleration/friction. |
| PHY-03 | Fix Projectile point-blank collision | Grace timer in `projectile.py` (2 frames) is insufficient for some spawn offsets. |
| VIS-01 | Enemy destruction animation | Implementation of an `Effect` or `Particle` class with Pyxel `blt` animations. |
| TST-01 | Implement Phase 01 Physics Tests | Use `unittest.mock` to simulate `LevelMap` and `pyxel` state for `test_physics.py`. |
| ORG-01 | Phase 04 Directory Split | File system relocation of 04-*.md files from 03/ to 04/. |
</phase_requirements>

## Standard Stack

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pyxel | 1.9.x | Game Engine | Current project engine. |
| pytest | Latest | Testing | Project standard for automated validation. |
| unittest.mock | Built-in | Mocking | Necessary for testing logic dependent on Pyxel's C-level globals. |

## Architecture Patterns

### Particle/Effect System
Use a simple list-based manager in `Game` (e.g., `self.effects = []`).
- **Effect Entity:** Short lifetime, specific `(u, v)` animation frames, no collision logic.

### Improved Slime Follow
- **What:** Maintain the `history` queue for *target* coordinates but use the standard `move_and_collide` logic even in follow mode, instead of simple Lerping.
- **Why:** Ensures the slime obeys the same gravity and collision rules as the player, removing the "floaty" feel.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Collision Geometry | Don't use complex SAT | AABB + Tile lookup | Pyxel's tile-based nature makes AABB efficient and sufficient. |
| Tweening Libs | Don't import extras | Linear interpolation / Accel | Simple enough to implement manually in Pyxel. |

## Common Pitfalls

### Pitfall 1: Projectile "Teleporting" through Walls
**What goes wrong:** At high speeds, projectiles move more than their width per frame, skipping wall checks.
**How to avoid:** Use sub-stepping or ensure `PROJECTILE_SPEED` is less than `TILE_SIZE` (currently 4.0 vs 8.0, so it's safe for now).

### Pitfall 2: Slime "Jitter" in Walls
**What goes wrong:** History target is inside a wall, Lerp tries to pull it in, `check_collision` stops it, causing a 1px jitter.
**How to avoid:** Ensure `target_x/y` is valid or use `move_and_collide` which handles snapping to tile edges.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | none |
| Quick run command | `pytest tests/test_physics.py` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command |
|--------|----------|-----------|-------------------|
| TST-01 | Physics: Walk | Unit | `pytest tests/test_physics.py::test_walk_logic` |
| TST-01 | Physics: Jump | Unit | `pytest tests/test_physics.py::test_jump_logic` |
| PHY-01 | Slime Collision | Integration | `pytest tests/test_slime.py` |

## Metadata
**Confidence:** HIGH
**Research date:** 2026-03-18
**Valid until:** 2026-04-18
