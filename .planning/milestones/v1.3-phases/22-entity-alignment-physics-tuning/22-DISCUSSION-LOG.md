# Phase 22: Entity Alignment & Physics Tuning - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-08
**Phase:** 22-entity-alignment-physics-tuning
**Areas discussed:** Player hitbox, Door dimensions, Physics retuning, Boss collision

---

## Player Hitbox Final Size

| Option | Description | Selected |
|--------|-------------|----------|
| 16x16 | Matches visual exactly, eliminates draw_sprite offset, tight 1-tile gaps | |
| 12x14 | Slightly smaller than visual, 2px grace each side | |
| Keep 10x14 | Current from P21, most forgiving, visible side overhang | Yes |

**User's choice:** Keep 10x14
**Notes:** "for now it felt good" — tested during Phase 21 visual verification

---

## Door Dimensions

| Option | Description | Selected |
|--------|-------------|----------|
| 16x16 | One tile, simpler, square | |
| 16x32 / 32x16 | Scale proportionally from old sizes | |
| Keep current (8x32 / 32x8) | Work as trigger zones regardless of tile size | Yes |

**User's choice:** Keep current sizes
**Notes:** "we can think about it later when we are replacing the visuals for them"

---

## Physics Retuning

| Option | Description | Selected |
|--------|-------------|----------|
| Just update schema math | Recalculate tile-unit values for 16px, no gameplay changes | Yes |
| Retune physics | Increase jump/speed for bigger tiles | |
| Update + playtest | Update math, then adjust if passages feel constrained | |

**User's choice:** Just update the schema math
**Notes:** "we already adjusted the physics for the screen size. the tiles are visual representation of the world."

---

## Boss Collision vs Visual

| Option | Description | Selected |
|--------|-------------|----------|
| 32x32 | Matches visual, 2x2 tiles, harder to dodge | |
| 24x28 | Proportional to player approach, some grace pixels | Yes |
| Keep 16x16 | One tile hitbox, easy to dodge, big overhang | |

**User's choice:** 24x28
**Notes:** "let's try 2 and see" — same proportional overhang as player

---

## Claude's Discretion

- Slime base hitbox and scaling behavior
- Enemy spawn position adjustments after hitbox changes

## Deferred Ideas

- Door visual replacement and dimension rethink (future phase)
