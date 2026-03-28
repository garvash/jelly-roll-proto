# Phase 10: Nitro-Ejection & Endgame - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-28
**Phase:** 10-nitro-ejection-endgame
**Areas discussed:** Nitro-Ejection identity, CRACKED_V interaction, Gamepad support, Ability tuning, Goo-Mold cleanup, VFX scope

---

## Nitro-Ejection Identity (Pre-Discussion Clarification)

**User clarification:** "I have never mentioned anything about nitro-ejection. What does the document say? Infinite jump comes from the infinite juice upgrade in late game."

**Follow-up clarification:** "The 5x5 map approach is outdated and should be disregarded, the direct LDtk map design can scale from small single biome map to a massive 10 biome world. This is the most versatile way to prototype."

**Further clarification:** "Infinite juice is basically collecting all juice cap and hitting something like 255 will make the game treat as infinite and not a separate powerup."

**Outcome:** "Nitro-Ejection" from 5x5mapdesign.txt is an outdated concept. The "Infinite Jump" is emergent from Juice Capacity upgrades (SYS-04) reaching ~255 max juice. No separate ability needed. Phase 10 scope redefined to focus on CRACKED_V breaking, gamepad support, and ability tuning.

---

## CRACKED_V Block Breaking

| Option | Description | Selected |
|--------|-------------|----------|
| Break on contact | Drill Dive breaks CRACKED_V on downward contact, same as soft blocks | ✓ |
| Require fused drill | Only fused Drill Dive breaks CRACKED_V, unfused bounces off | |
| Multi-hit durability | 2+ hits to break, adds puzzle element | |

**User's choice:** Break on contact (Recommended)

| Option | Description | Selected |
|--------|-------------|----------|
| Break on upward contact | Boost breaks CRACKED_V above on contact during flight | ✓ |
| Only sustained flight | Must chain 2+ Boost taps for enough momentum | |
| You decide | Claude picks based on collision patterns | |

**User's choice:** Break on upward contact (Recommended)
**Notes:** Symmetrical vertical traversal — Drill down, Boost up.

---

## Gamepad Support

| Option | Description | Selected |
|--------|-------------|----------|
| Standard platformer | D-pad=movement, A=jump, B=spit, X=dash. Celeste/Hollow Knight convention. | ✓ |
| Metroid Dread style | D-pad=movement, B=jump, Y=spit, X=dash. GBA Metroid feel. | |
| You decide | Claude picks sensible default | |

**User's choice:** Standard platformer (Recommended)
**Notes:** Y, Start, Shoulders, Triggers reserved for future use.

---

## Ability Tuning Scope

| Option | Description | Selected |
|--------|-------------|----------|
| All 6 abilities | Full pass across Dash, Ram, Drill, Charge Shot, Shield, Boost | ✓ |
| Goo-Mold breaking | Define which ability breaks goo-mold | |
| Edge cases & bugs | Focus on known rough edges and state transitions | ✓ |
| Visual/audio feedback | Screen shake, particles, sound cues | ✓ |

**User's choice:** All 6 abilities + Edge cases & bugs + Visual/audio feedback (multi-select)
**Notes:** Goo-Mold is remnants from the past "reform blocks" misinterpretation. Remove or rename for future use.

---

## Goo-Mold Tile Cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| Remove entirely | Delete from constants, map, entity schema | ✓ |
| Rename to TILE_RESERVED | Keep IntGrid slot, generic placeholder | |
| Keep as-is | Leave defined but unused | |

**User's choice:** Remove entirely (Recommended)
**Notes:** No LDtk maps use it. Can re-add a new block type later with fresh design.

---

## VFX Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal | Screen shake + pixel particles, no audio. Pyxel built-in drawing. | ✓ |
| Full juice | Screen shake + particles + Pyxel sound effects | |
| You decide | Claude determines per ability | |

**User's choice:** Minimal (Recommended)
**Notes:** No audio this phase. Pyxel audio can be a separate pass.

---

## Claude's Discretion

- Specific tuning constant values
- Exact VFX implementation details
- Order of ability tuning
- Edge case prioritization

## Deferred Ideas

- Infinite juice threshold logic — implement with SYS-04 in Phase 11
- Pyxel audio/SFX — separate pass after visual feedback
- New block type for freed IntGrid slot 10
- 5x5mapdesign.txt archival/removal
