# Phase 30: Fusion Lifecycle Design Doc - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-19
**Phase:** 30-fusion-lifecycle-design-doc
**Areas discussed:** Scope pivot, Base verb (pogo dive), Fusion input model, Juice economy, Fusion FSM, Empty-state behavior, Cut abilities, Baseline capture, Design doc structure, Doc lock, Acceptance checks

---

## Scope pivot — one fusion, not six

The user surfaced that the prototype is 1 biome and does not have all unlockable abilities. Phase 30's ROADMAP entry assumed one-page contracts for ABL-01..06, but the user's intent is to design **one** fusion mechanic that feels natural to the player's game feel.

| Option | Description | Selected |
|--------|-------------|----------|
| Document all 6 as regression targets | Original ROADMAP intent — preserve v1.1 abilities | |
| Document 1 fusion (Drill Dive) | Prototype-focused; cut the others | ✓ |
| Document 2 (drill + ram) | Symmetric gate-breaking pair | |

**User's choice:** Drill Dive (fusion) + Pogo Dive (unfused baseline, Shovel Knight-style). Same input verb (DOWN+V air), fusion upgrades outcome.

---

## Pogo bounce trigger

| Option | Description | Selected |
|--------|-------------|----------|
| Bounce on any solid (Shovel Knight pure) | Pogo bounces on everything | |
| Bounce only on enemies / breakables | Pure ground just lands | ✓ |
| Bounce on enemies, pass-through on soft/cracked | Explicit "need fusion to break" signal | |

**User's choice:** enemies/breakables only.

---

## Drill bounce behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Pure plunge (no bounce) | Drill is commitment | ✓ |
| Plunges soft/cracked, bounces on solid | Hybrid with pogo | |
| Drill ends with pogo on landing | Reward drill-into-floor | |

**User's choice:** pure plunge.

---

## Pogo cost

| Option | Description | Selected |
|--------|-------------|----------|
| Free — always available | Baseline verb, juice reserved for fusion | ✓ |
| Costs juice (small per bounce) | Pulls juice onto unfused play | |

**User's choice:** free.

---

## Recall release behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Release = slime freezes at position | Free positioning (ABL-03 reuse) | |
| Release = slime returns to follow | Clean for now | ✓ |

**User's choice:** return to follow. **Rationale captured:** "Z is shoot button — freezing would make slime shot feel unresponsive." Recall release preserves spit tap responsiveness.

---

## Docked state

| Option | Description | Selected |
|--------|-------------|----------|
| Distinct state between RECALL and WINDUP | More explicit FSM | |
| Collapses into WINDUP frame 0 | Simpler FSM | ✓ |

**User's choice:** fold docked into windup frame 0.

---

## Windup cancel

| Option | Description | Selected |
|--------|-------------|----------|
| Free cancel, no penalty | Forgiving for prototype | ✓ |
| Pop-out dazed | Punishes misinputs | |
| No cancel | Commits on windup start | |

**User's choice:** free cancel.

---

## Fused state model (continuous vs latched)

| Option | Description | Selected |
|--------|-------------|----------|
| Continuous (hold Z to stay fused) | Drill input = Z + DOWN + V (3-input combo) | |
| Latched (windup latches, Z free) | Drill input = DOWN + V only | ✓ |

**User's choice:** latched. Drill retains 2-input cleanliness; fused becomes a real state with its own identity.

---

## Fused projectile — needed for boss daze?

Originally Claude proposed cutting fused projectile entirely. User pushed back: "fused projectile is needed for shoot to daze the boss for drill dive."

**Resolution:** Restored fused daze shot as core to the boss loop. Mechanically same projectile as unfused spit, visually and behaviorally upgraded (more damage, daze effect, juice cost).

| Option | Description | Selected |
|--------|-------------|----------|
| Mechanically identical, visually upgraded | Reuses spit impl, adds daze layer | ✓ |
| Truly different projectile | Piercing / arc'd / slime-as-projectile | |

**User's choice:** same projectile upgraded. Phase 33 tunes both.

---

## Juice gate for fusion

Claude initially proposed 25% hard gate or no gate. User reframed: "I was thinking 100% gate. This will make the juice gating obvious. 'Oh I need 1 more juice for this puzzle' moment. Holding down slime button without moving will give you faster juice recovery if slime is active."

**Resolution:** 100% gate with accelerated regen ritual. Juice bar becomes a binary readiness meter.

---

## Accelerated regen conditions

| Option | Description | Selected |
|--------|-------------|----------|
| Slime active + docked at player | Matches held-Z ritual | ✓ |
| Slime active, anywhere in room | Less spatial commitment | |
| Slime active + player stationary | Harshest, safe-spot feel | |

**User's choice:** active + docked. Player's held-Z is the ritual input.

---

## Empty juice while fused

| Option | Description | Selected |
|--------|-------------|----------|
| Dissipate with cooldown (v1.1 behavior) | Real stakes around fusion spending | ✓ |
| Dissipate, returns quickly | Softer | |
| Slime ejects unharmed | Zero-risk fusion | |

**User's choice:** v1.1 dissipate + cooldown preserved.

---

## Cut abilities fate

| Option | Description | Selected |
|--------|-------------|----------|
| Scope out + follow-up phase strips code | Clean codebase matches clean design | ✓ |
| Scope out + leave code dormant | Simplest, but Phase 32 still deals with them | |
| Scope out + strip in Phase 32 | Loads Phase 32 | |

**User's choice:** scope out in Phase 30 design, strip code in a new follow-up phase inserted between 30 and 32.

---

## Baseline capture method

| Option | Description | Selected |
|--------|-------------|----------|
| Code archaeology + written spec | Read player.py, extract to spec | ✓ |
| Code archaeology + gameplay recordings | Frame-by-frame diff needs infra | |
| Behavioral checklist only | No frame counts | |

**User's choice:** code archaeology + written spec.

---

## Design doc scope

| Option | Description | Selected |
|--------|-------------|----------|
| Single comprehensive doc | One FUSION-DESIGN.md | ✓ |
| Split design doc + drill contract file | More structure | |
| Design doc + living FSM diagram | Separate diagram artifact | |

**User's choice:** single file.

---

## Doc lock mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Frontmatter flag + commit hash | YAML status/locked_at/locked_commit | ✓ |
| Git tag (v2.0-fusion-design-locked) | Heavier ceremony | |
| Commit message + status line only | Honor system | |

**User's choice:** frontmatter + commit hash.

---

## Acceptance checks form

| Option | Description | Selected |
|--------|-------------|----------|
| Behavioral checklist | Phase 32 verifies by inspection + smoke test | ✓ |
| Playable test scenario + checklist | Author specific LDtk level/inputs | |
| Automated regression test stubs | pytest stubs filled in by Phase 32 | |

**User's choice:** behavioral checklist.

---

## Claude's Discretion

- Exact frame thresholds (tap-vs-hold, windup duration, unfuse windup)
- Exact juice costs (spit, daze shot, per-block drill) — carried from v1.3; Phase 33 retunes
- Whether manual unfuse mid-drill is allowed — default on, Phase 33 may disable
- Daze-on-hit effect duration and stun behavior
- CRACKED_V gating handling under single-fusion model (confirm via archaeology)
- FSM diagram format (ASCII vs Mermaid) — author's choice
- Scope pivot rationale framing in the doc itself

---

## Deferred Ideas

- **NEW PHASE** needed between 30 and 32 to strip cut-ability code (ram/hold/charge_shot/bubble_shield/boost from player.py + slime.py + physics-schema.json groups)
- Phase 32 scope shrinks to single-ability refactor
- Phase 33 scope shrinks to drill-only feel pass
- Daze projectile distinctness — may differentiate post-prototype if playtest shows same-as-spit isn't felt
- Post-prototype ability re-evaluation at Godot/Unity transition
- FUS-01/02/03 defined inline in FUSION-DESIGN.md (no v2.0 REQUIREMENTS.md exists)
