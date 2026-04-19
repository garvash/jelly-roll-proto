---
status: LOCKED
locked_at: 2026-04-19
locked_commit: TBD
---

# Fusion Lifecycle Design (v2.0 prototype)

This document is the **LOCKED design contract** for v2.0 fusion behavior. It is the single source of truth that downstream phases are built against:

- **Phase 32 (Fusion Manager + Protocol Refactor)** is HARD-GATED on the SHA in this doc's frontmatter. The refactor verifies `locked_commit` against git history before writing its PLAN, then builds against this spec — not against live `player.py` drift, not against memory, not against the pre-pivot ROADMAP.
- **Phase 33 (Per-Ability Feel Pass)** reads the Drill-Dive Contract section (§ Drill-Dive Contract, FUS-03) as its tuning target. Phase 33 may retune values live; it may NOT change behavioral invariants without re-locking this doc.
- **Phase 31 (Animation + Particle Bank)** subscribes to the event-bus events enumerated in § Fusion FSM (`drill_start`, `drill_block_break`, `drill_end`, `manual_unfuse_start`) plus the existing `fuse_start` / `fuse_end`. Events are anim side-channel hooks; they do not drive gameplay state.

**Scope pivot — one fusion, not six.** The v2.0 prototype ships **exactly one fusion mechanic: Drill Dive**. The five other v1.1 fusion abilities (Slime Ram, Directional Hold, Charge Shot, Bubble Shield, Slime Boost) are **cut from the prototype** — enumerated later in § Cut Abilities, out of prototype scope, revisit post-prototype. This is per D-01 / D-02 / D-29 of `.planning/phases/30-fusion-lifecycle-design-doc/30-CONTEXT.md`.

The prototype combat fantasy is **shoot to daze the boss → drill to finish** (per D-03). This doc defines the input model, FSM, juice economy, and drill contract that make that loop feel natural.

## Requirements (defined in this document)

Per D-32, the `FUS-XX` requirement IDs referenced in `.planning/ROADMAP.md` are defined inline here (no separate REQUIREMENTS file exists for v2.0). Each ID traces to a named section heading below, so downstream plans can link to a specific anchor.

- **FUS-01**: Fusion lifecycle FSM defines `IDLE → RECALL → WINDUP → FUSED → EXIT` with activation input, 100% juice gate at WINDUP entry, cancel/release rules at each phase, and auto/manual EXIT paths. Under the "200% charge" mental model (D-23a), WINDUP is the visible second-pass fill from 100→200% of the juice bar; imminent-fusion telegraph at ≥90% (D-23b); ~30-frame cancel window at base (D-23c). See [§ Fusion FSM](#fusion-fsm) and [§ Juice Economy](#juice-economy).
- **FUS-02**: Unified input model. Z is the slime/fusion button (tap = spit/daze, hold = recall/fuse/manual-unfuse); DOWN+V in air is the dive verb (pogo unfused, drill fused); tap/hold disambiguation uses a ~8-frame threshold (tuned in Phase 33 — current v1.3 code uses `SPIT_HOLD_THRESHOLD = 16` frames). See [§ Input Model](#input-model).
- **FUS-03**: Drill-dive v1.3 regression contract. Documented velocity, per-block juice cost, CRACKED_V handling, and entry/exit conditions serve as Phase 32's parity target — verified by inspection and smoke test, no pytest required (per D-28). See [§ Drill-Dive Contract](#drill-dive-contract).

## Scope Pivot Rationale

**Per D-01**: the prototype ships **ONE** fusion mechanic: **Drill Dive**. The five other v1.1 fusion abilities — Slime Ram, Directional Hold, Charge Shot, Bubble Shield, Slime Boost — are **cut from the prototype**. They are NOT deleted from design thinking; they are out of prototype scope, revisit post-prototype (see [§ Cut Abilities](#cut-abilities) for one-line rationale per ability, per D-02).

**Why cut?** The five abilities shipped in v1.1 as *expansion-era* content — they validated the fusion-verb space, but each one added a partner-compound in a six-ability matrix that no longer pays for itself in a **feel-first prototype**. The cuts are prototype focus, not rejection. Post-prototype transition to Godot/Unity (the natural re-evaluation point per 30-CONTEXT.md Deferred Ideas) is when the full six-ability palette may return.

**Per D-03**: the prototype's fusion loop is **"shoot to daze the boss → drill to finish."** This is the combat fantasy that `.planning/PROJECT.md` already names ("using a companion slime to power a destructive Drill Dive that enables both exploration and combat"). The whole input model (Z = slime/fusion button; DOWN+V = dive verb, pogo unfused / drill fused) exists to make that two-step loop read as **natural, readable, and committed** — not as "pick one of six fusion flavors from a menu."

**Per D-02 — Code-strip follow-up.** The cut-ability code still exists in the tree today:
- `src/entities/player.py` — `start_ram()` / `apply_ram_physics()` / `end_ram()`, `bubble shield` logic, `charge_shot_*`, `start_boost` / `end_boost`, `has_shield` / `has_boost` flags, `ram_dx` / `ram_dy` state.
- `src/entities/slime.py` — any shield/charge-shot/boost hooks.
- `assets/physics-schema.json` — tuning groups `ram`, `charge_shot`, `boost`, `bubble_shield`.
- `.planning/ROADMAP.md` references to six-ability refactor (being updated by this plan's Task 8).

A **separate cut-ability-code-strip phase** must run between Phase 30 (this doc) and Phase 32 (fusion refactor) to remove that code. It's tracked as a Deferred Idea in `30-CONTEXT.md` ("NEW PHASE NEEDED — cut-ability code strip"). This plan's Task 8 adds a pointer note to ROADMAP.md; inserting the actual phase happens via `/gsd-insert-phase` after Phase 30 closes. The code-strip phase is a **HARD GATE** before Phase 32 begins — Phase 32 must not start until cut-ability code is out of the tree, to prevent the refactor from accidentally preserving dead code in the new `src/fusion/` package.

**Per D-29**: this is a *single comprehensive file*. No separate contract files. No separate FSM diagram artifact. All seven content sections (Input Model, Fusion FSM, Juice Economy, Drill-Dive Contract, Cut Abilities, Acceptance Checklist, Lock Protocol) live inline below.
