# Phase 08: New Fusion Abilities - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-28
**Phase:** 08-new-fusion-abilities
**Areas discussed:** Slime Ram activation & feel, Directional Slime Hold, Charge Shot mechanics, Input mapping & conflicts, Basic dash behavior, Slime recall flow, Ram gating, Drill retcon, Secondary input mapping

---

## Core Design Pattern

User proposed "base ability + fusion enhancement" pattern: every ability has a solo form that becomes powered up in fused state. Inspired by R-Type Force pod attach/detach dynamic.

**User's choice:** Base actions augmented by slime abilities — dash alone = basic dash, dash while fused = slime ram. Pattern applies to all abilities.

---

## Mana Shield (Fusion Defense)

| Option | Description | Selected |
|--------|-------------|----------|
| Juice absorbs first | All damage drains juice instead of HP while fused. Protoss shields. | ✓ |
| Juice reduces damage | Half damage to juice, half to HP. Subtler advantage. | |
| Shield HP layer | Separate shield bar based on juice. Halo energy shields. | |

**User's choice:** Juice absorbs first
**Notes:** "This should work like Protoss force field."

## Juice Empty While Fused

| Option | Description | Selected |
|--------|-------------|----------|
| Forced unfuse + stagger | Slime ejects, player stunned ~20 frames. | |
| Forced unfuse, no penalty | Slime detaches, normal invuln. | |
| Slime dissipates | Slime gone, cooldown to reform at full size. | ✓ |

**User's choice:** Slime dissipates
**Notes:** "Slime will reform at full size after the cooldown. Much like burnout in SF6."

## Slime Ram Feel

| Option | Description | Selected |
|--------|-------------|----------|
| Shinespark-style launch | Build speed, press dash to launch. High speed, invincible, directional. | ✓ |
| Instant burst dash | Immediate forward dash, fixed distance. Mega Man X style. | |
| Momentum carry | Dash inherits current speed. Physics-integrated. | |

**User's choice:** Shinespark-style launch
**Notes:** "Similar to Crystal Dash in Hollow Knight. We can adjust the amount of setup needed or it may get boost from max juice cap."

## Charge Shot Mechanic

| Option | Description | Selected |
|--------|-------------|----------|
| Hold Z to charge | Hold = charge meter fills, release = fire. Mega Man style. | ✓ |
| Rapid-fire while fused | Faster/stronger tap spit, no charging. | |
| Auto-charge on fuse | Fusing starts passive charge, Z fires at current level. | |

**User's choice:** Hold Z to charge
**Notes:** "Max charge to fling the slime in its entirety for maximum damage and tactically place unfused slime to the destination."

## Fusion Activation Method

| Option | Description | Selected |
|--------|-------------|----------|
| Toggle fuse (button press) | Convenient, no cost to enter. | |
| Charge-to-fuse (100% juice) | Earn the power state. Super Metroid feel. | ✓ |

**User's choice:** Charge-to-fuse
**Notes:** User and Claude agreed charge-to-fuse creates better tension and risk/reward. "It's the better game."

## Control Scheme

| Option | Description | Selected |
|--------|-------------|----------|
| Super Metroid (hold Z = charge+fuse) | Tap Z = spit, hold Z = recall + charge, fuse at 100%. One button for offensive loop. | ✓ |
| R-Type (X=call, Z=shoot) | Separate call and shoot buttons. More explicit. | |

**User's choice:** Super Metroid style
**Notes:** Frees up X button entirely for Phase 9.

## Charge Shot Power Scaling

| Option | Description | Selected |
|--------|-------------|----------|
| Juice = power, always flings | More juice = bigger shot. Power scales. | |
| All-or-nothing full power | Always max power, dumps all juice. Every shot is the big one. | ✓ |

**User's choice:** All-or-nothing
**Notes:** "If it flings and unfuses the slime this is the only way to handle."

## Ram Block Interaction

| Option | Description | Selected |
|--------|-------------|----------|
| Juice-powered penetration | Plows through CRACKED_H as long as juice remains. ~15 juice per block. | ✓ |
| Fixed distance, flat cost | Fixed ~4 tile distance, 50 juice flat. | |

**User's choice:** Juice-powered penetration
**Notes:** "This will allow juice gating."

## Basic Dash (Solo V)

| Option | Description | Selected |
|--------|-------------|----------|
| Short combat dodge | ~2 tile burst, i-frames, short cooldown. Celeste style. | ✓ |
| Momentum dash | Speed added to velocity. Hollow Knight style. | |
| Directional dash | 8-way fixed distance. Celeste with full direction. | |

**User's choice:** Short combat dodge

## Slime Recall

| Option | Description | Selected |
|--------|-------------|----------|
| Instant teleport | Snap to player, no travel. | |
| Quick zip/slingshot | Zips at high speed, ~4-6 frames. Rubber-band feel. | ✓ |
| Slime bounces to player | Bouncy hop-path, ~10-15 frames. Charming. | |

**User's choice:** Quick zip/slingshot

## Slime Directional Positioning

User proposed: tap vs hold input duration on movement keys. Quick tap (< ~4-6 frames) = reposition slime to take cover. Hold = normal walk. No extra button needed. Slime moves to cover the opposite side — player faces right, slime goes left for firing position.

## Drill Dive Retcon

| Option | Description | Selected |
|--------|-------------|----------|
| Unify under V, retcon drill | V = all burst movement. DOWN+V = drill. Earned from Mole Boss. | ✓ |
| Keep drill on SPACE, add dash on V | No v1.0 changes. Two separate button families. | |
| Decide in planning | Let planner evaluate refactor cost. | |

**User's choice:** Unify under V, retcon drill
**Notes:** "Should we introduce normal dash first then drill as vertical variant of the dash? That seems more logical to me. Perhaps drill is earned from the mole boss fight."

## Secondary Input Mapping

User requested WASD+JK+Space as secondary controls based on player feedback. No gray area — straightforward alias mapping.

---

## Claude's Discretion

- Specific frame timings for dash i-frames, cooldowns, and input tap threshold (approximate values given, tunable)
- Slime recall visual effect (arc/trail)
- Charge visual feedback (pulsing, glow stages)
- Ram speed and acceleration curve
- Juice cost exact values (approximates given: ~15 per block, ~20 per hit absorbed)

## Deferred Ideas

- X button for Phase 9 defensive abilities (Bubble Shield, Yoshi Jump, Reform Block)
- Juice capacity upgrades gating deeper CRACKED_H walls (Phase 11 SYS-04)
