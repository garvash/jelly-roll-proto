---
phase: 30-fusion-lifecycle-design-doc
plan: 01
subsystem: design-doc
tags:
  - design-doc
  - fusion
  - drill-dive
  - locked-contract
  - scope-pivot
dependency_graph:
  requires:
    - Phase 24 (tuning loader — v1.3 baseline values cited from _v1.3-reference.json)
    - Phase 26 (event bus — naming convention + existing fuse_start/fuse_end/drill_impact)
    - Phase 29 (v1.3-reference.json frozen baseline — authoritative drill values)
  provides:
    - ".planning/FUSION-DESIGN.md — LOCKED design contract at SHA e6263693dc7d3baee2cefc4bea757610bfe6b51e"
    - "FUS-01 / FUS-02 / FUS-03 inline requirement definitions"
    - "Drill-dive v1.3 regression contract (values + three exit conditions)"
    - "Five-state FSM: IDLE -> RECALL -> WINDUP -> FUSED -> EXIT with Mermaid + ASCII rendering"
    - "Second-pass charge (100->200%) commitment ritual with three-layer anti-accidental-fuse defense"
    - "Cut-ability list (5 abilities) + code-strip phase hard-gate flag"
    - "Acceptance checklist for Phase 32 behavioral verification"
  affects:
    - "Phase 32 — hard-gated on locked_commit SHA; scope narrowed to single drill_dive module"
    - "Phase 33 — scope narrowed to drill-only feel pass; reads drill-dive contract as tuning target"
    - "Phase 31 — subscribes to new events (drill_start, drill_block_break, drill_end, manual_unfuse_start)"
    - "Pre-Phase-32 code-strip phase (TBD number via /gsd-insert-phase) — removes cut-ability code"
tech_stack:
  added:
    - YAML frontmatter lock mechanism (status/locked_at/locked_commit)
    - Mermaid stateDiagram-v2 inline rendering (GitHub/Obsidian/VS Code native)
  patterns:
    - Two-commit lock dance (doc-write commit -> lock commit; locked_commit points at doc-write SHA)
    - Inline bold-ID requirement definitions mirroring v1.1-REQUIREMENTS.md convention
    - Code-archaeology-with-citations (every concrete value names its source file:line)
key_files:
  created:
    - .planning/FUSION-DESIGN.md
    - .planning/phases/30-fusion-lifecycle-design-doc/30-01-SUMMARY.md
  modified:
    - .planning/ROADMAP.md
decisions:
  - i-frames=NONE preserved from v1.3 (Open-Q #1 resolution; Phase 33 may revisit)
  - FUS-02 activation button = V (dash action); Phase 32 remaps from current jump/SPACE routing
  - manual_unfuse_start event fires at WINDUP-begin (earliest anim signal)
  - Free-cancel symmetric at both WINDUP and UNFUSE_WINDUP (Open-Q #4)
  - Accelerated regen draft = 2x passive (1.0 juice/frame); Phase 33 tunes
  - Mermaid + ASCII fallback for FSM diagram (D-30 permits either; ship both)
  - Doc-write commit also folds ROADMAP scope-pivot (one commit, two files)
metrics:
  duration_minutes: 14
  tasks_completed: 8
  files_created: 2
  files_modified: 1
  completed_date: 2026-04-19
---

# Phase 30 Plan 01: Fusion Lifecycle Design Doc Summary

**One-liner:** Authored and locked `.planning/FUSION-DESIGN.md` — the design contract narrowing the prototype to one fusion mechanic (Drill Dive), defining the `IDLE → RECALL → WINDUP → FUSED → EXIT` FSM under a 100%-gated juice-as-mana economy with a second-pass (100→200%) commitment ritual — sealed via YAML frontmatter lock at git SHA `e6263693dc7d3baee2cefc4bea757610bfe6b51e`, with ROADMAP.md scope-pivot folded into the same lock dance.

## Context

Phase 32 (Fusion Manager + Protocol Refactor) and Phase 33 (Per-Ability Feel Pass) are **hard-gated** on this doc being locked — without a written, SHA-pinned contract, they would be building against vibes. Phase 30 is design-only (no code), producing exactly one deliverable (`FUSION-DESIGN.md`) plus a scope-pivot update to ROADMAP.md that propagates the "one fusion, not six" decision into downstream phase goals.

The `30-CONTEXT.md` locked-decisions set (D-01..D-32) encoded the user's scope pivot and FSM design choices; the plan's job was to **render those decisions as a single comprehensive locked file** with inline citations to v1.3 baseline values, a Mermaid state diagram + ASCII fallback, and a two-commit lock dance that pins the content to a specific git SHA for downstream verification.

## What Was Built

Single locked markdown file at `.planning/FUSION-DESIGN.md` (480 lines, 7 content sections + YAML frontmatter lock) plus targeted ROADMAP.md updates. Content sections, written in the order mandated by Pitfall 6 of `30-RESEARCH.md` (Input Model before FSM):

1. **Frontmatter** (`status: LOCKED`, `locked_at: 2026-04-19`, `locked_commit: e6263693...`).
2. **Summary + FUS-01/02/03 inline requirement definitions** with section anchors (follows `v1.1-REQUIREMENTS.md` bold-ID precedent per D-32).
3. **§ Scope Pivot Rationale** — one-fusion-not-six per D-01/D-02/D-03 with code-strip follow-up note.
4. **§ Input Model** (FUS-02) — Z semantics (tap = spit/daze, hold = recall/fuse/unfuse) and V semantics (DOWN+V: pogo unfused, drill fused). Quantified tap/hold threshold (~8 frames target; v1.3 uses 16). Implementation remap note (Phase 32 re-routes drill from `jump`/SPACE to `dash`/V per PROJECT.md canonical).
5. **§ Fusion FSM** (FUS-01 FSM side) — five-state machine with Mermaid `stateDiagram-v2` block AND ASCII table fallback (D-30 permits either; this doc ships both for Mermaid rendering parity and grep-based verification). State-by-state rules cite named constants (`RECALL_SPEED=4.0`, `RECALL_OVERLAP_DIST=4`, `MANA_SHIELD_COST=20.0`, `SLIME_DISSIPATE_COOLDOWN=240`). Event emissions subsection enumerates existing events (`fuse_start`, `fuse_end`) and four NEW events (`drill_start`, `drill_block_break`, `drill_end`, `manual_unfuse_start`) flagged as anim side-channel hooks per MEMORY's Reanimator-style constraint.
6. **§ Juice Economy** (FUS-01 economy side) — 100% gate framing as formalization of existing charge-to-fuse behavior (NOT invention — per Pitfall 2). Second-pass charge model (100→200% overlay = WINDUP = ~30f cancel window per D-23c). Three-layer anti-accidental-fuse defense: visible bar phase + imminent-fusion telegraph at ≥90% per D-23b + free-cancel per D-23. Accelerated regen at 2× passive (draft per Open-Q #5). v1.3 values table cites `_v1.3-reference.json`.
7. **§ Drill-Dive Contract** (FUS-03) — activation, physics, block-break, and three exit condition tables, each with file:line citations to `_v1.3-reference.json` and `src/entities/player.py:443-802`. i-frames=NONE preserved from v1.3 (Open-Q #1). Block-gate hierarchy tie-in: drill opens CRACKED_V only. Phase 32 preserve/change/may-tune table delimits refactor scope.
8. **§ Cut Abilities** — one-line rationale each (per D-02 + Pitfall 5) for Slime Ram, Directional Hold, Charge Shot, Bubble Shield, Slime Boost. Code-strip phase requirement flagged with specific file/symbol list. Post-prototype revisit framing.
9. **§ Acceptance Checklist** — behavioral contract Phase 32 must satisfy by inspection + smoke test (no pytest per D-28). Uses markdown checkbox syntax per `29-FEEL-TARGETS.md` precedent. Input / FSM / Drill / out-of-scope sub-checklists. Three-run smoke test exercising each drill exit condition.
10. **§ Lock Protocol** — `locked_commit` semantics (points at doc-write commit, NOT the lock commit). Two-commit dance workflow. Re-lock policy requiring user approval. Downstream verification contract (Phase 32 `depends_on_sha`, Phase 33 value-reading, Phase 31 event-subscription).

**ROADMAP.md scope pivot** (folded into the doc-write commit per plan design):
- Phase 30 Goal narrowed to single-fusion; Success Criteria updated to reference drill-dive contract (not six abilities); Plans count set to 1; code-strip follow-up note appended as indented callout.
- Phase 32 Goal: `drill_dive` single module (not six); cut-ability code-strip phase added to Depends-on; Success Criteria updated to reference FUS-03 contract rather than ABL-01..06.
- Phase 33 Goal: drill-only feel pass; Success Criteria updated to drill-identity goals; windup/WINDUP/accelerated-regen tuning targets enumerated.
- Progress table row for Phase 30: `0/TBD` → `0/1 | In progress`.

## Key Decisions Made While Writing

The plan's `<draft_decisions>` block front-loaded the resolutions of the five Open Questions raised in `30-RESEARCH.md`. All five were adopted as written:

1. **Drill i-frames = NONE** (Open-Q #1) — preserve v1.3 behavior. Drill-dive contract documents this as a regression target with flag for Phase 33 to revisit if playtest demands.
2. **FUS-02 activation button = V (`dash` action)** (Open-Q #2) — matches PROJECT.md canonical ("V=dash unfused, DOWN+V=drill dive"). Phase 32 remaps from current code's `jump`/SPACE routing. Documented as implementation detail, not design change.
3. **`manual_unfuse_start` fires at WINDUP-begin** (Open-Q #3) — earliest anim signal; mirrors `fuse_start` at fuse-windup-begin. Existing `fuse_end` still fires at actual unfuse moment.
4. **Free-cancel symmetric at both WINDUP and UNFUSE_WINDUP** (Open-Q #4) — D-23 symmetric. Release during any windup = abort (stay-or-return to prior state; no cost). Flagged for Phase 33 playtest validation.
5. **Accelerated regen multiplier draft = 2× passive** (Open-Q #5) — 1.0 juice/frame = 60/sec (full refill in ~3.33s from 0). Labeled as draft with "Phase 33 tunes" note; not binding.

Additional decision made during execution: **Mermaid stateDiagram-v2 chosen for FSM diagram with ASCII table fallback immediately after** — per Pattern 3 of `30-RESEARCH.md` and D-30's "either format permitted" ruling. Ships both because Mermaid renders as a picture in GitHub/Obsidian/VS Code preview (legibility win) AND the ASCII table makes grep-based content verification robust (guarantees state names match the FSM literally, not via inference from a rendered diagram).

## Lock Artifact

- **Doc-write commit SHA (what was locked):** `e6263693dc7d3baee2cefc4bea757610bfe6b51e`
- **Lock commit SHA (frontmatter amendment that populated `locked_commit`):** `a27dc31c454cb60eff8696d55b5a195a6af46b79`
- `locked_commit` in FUSION-DESIGN.md frontmatter points at the doc-write SHA (what was locked), NOT the lock-commit SHA (when the lock was applied) — invariant per § Lock Protocol.
- `git log -2 --oneline -- .planning/FUSION-DESIGN.md` shows exactly the lock commit + the last content-writing commit (Task 7's `4c40149`), confirming the two-commit dance visible in git history.
- `git cat-file -p e6263693...` resolves cleanly — SHA exists in history.

## Commits (this plan)

| Task | Name                                                                     | Commit    |
| ---- | ------------------------------------------------------------------------ | --------- |
| 1    | Frontmatter + summary + scope-pivot section                              | `2b0da5e` |
| 2    | § Input Model section (FUS-02)                                           | `2811a91` |
| 3    | § Fusion FSM section with Mermaid + ASCII fallback (FUS-01 FSM side)     | `c6009ab` |
| 4    | § Juice Economy section — 100% gate + accelerated regen (FUS-01 economy) | `553de1c` |
| 5    | § Drill-Dive Contract section — v1.3 values + 3 exit conditions (FUS-03) | `562b18c` |
| 6    | § Cut Abilities section — one-line rationale per ability                 | `ad524e9` |
| 7    | § Acceptance Checklist + § Lock Protocol sections                        | `4c40149` |
| 8a   | Doc-write commit (ROADMAP scope-pivot; initiates lock dance)             | `e626369` |
| 8b   | Lock commit (amends frontmatter `locked_commit` TBD → doc-write SHA)     | `a27dc31` |

## Deviations from Plan

**None substantive.** Plan executed as written. Minor interpretation call on Task 8 Step 3:

**Interpretation note (Task 8 Step 3):** The plan's Step 3 says to "stage `.planning/FUSION-DESIGN.md` AND `.planning/ROADMAP.md` and commit" for the doc-write commit. Because Tasks 1-7 are per-task-committed (per gsd executor protocol + `type="auto"` + autonomous), FUSION-DESIGN.md content was already committed across Tasks 1-7 by the time Task 8 ran. The doc-write commit therefore contains only the ROADMAP pivot. The lock commit (Step 6) then amends FUSION-DESIGN.md frontmatter as intended. Net effect matches plan intent: `locked_commit` is a real SHA that resolves in git history, the two-commit dance produces distinct doc-write and lock commits, and `git log -2 -- .planning/FUSION-DESIGN.md` shows exactly two commits touching that specific file (the lock commit + Task 7's final-content commit). All plan acceptance criteria met.

## Verification Results

All 18 VALIDATION.md Per-Task Verification Map checks PASS against the final doc:

- `test -f .planning/FUSION-DESIGN.md` ✓
- `status: LOCKED` in frontmatter ✓
- `locked_at: 2026-04-19` matches YYYY-MM-DD ✓
- `locked_commit: e6263693dc7d3baee2cefc4bea757610bfe6b51e` matches `[0-9a-f]{7,40}$` (40-char hex SHA, not TBD) ✓
- `## Fusion FSM` section present ✓
- All five FSM states (IDLE, RECALL, WINDUP, FUSED, EXIT) appear as standalone words ✓
- `100%` juice-gate rule present ✓
- `200%` second-pass charge present ✓
- `second-pass` concept named ✓
- Imminent-fusion telegraph (`90%`, `pulse`/`flash`) present ✓
- `~30 frame` cancel-window quantified ✓
- Z tap/hold + DOWN+V input semantics (≥3 matches) ✓
- Tap/hold threshold quantified (`~8 frames` target) ✓
- `## Drill-Dive Contract` section present ✓
- `DRILL_SPEED`, `DRILL_IMPACT_COST`, `DRILL_ACTIVATION_COST`, `DRILL_BLOCK_REFUND`, `DRILL_CRACKED_V_COST`, `DRILL_DRIFT_SPEED` all named with values ✓
- `CRACKED_V` handling documented ✓
- Three exit conditions (solid, juice=0, cancel) identifiable by grep ✓
- All three FUS-01/02/03 IDs defined as bold anchors ✓
- All five cut abilities named verbatim (Slime Ram, Directional Hold, Charge Shot, Bubble Shield, Slime Boost) ✓
- `## Acceptance Checklist` section present ✓

## Next Steps

1. **User reviews the locked doc** in GitHub/Obsidian/VS Code preview. Per VALIDATION.md Manual-Only Verifications table, user sign-off on the locked design is a phase-gate requirement.
2. **Run `/gsd-insert-phase`** to create the cut-ability code-strip phase between Phase 30 and Phase 32. This is the hard-gate dependency Phase 32 needs — without it, Phase 32's refactor would accidentally preserve dead cut-ability code in the new `src/fusion/` package.
3. **Phase 32 planner** reads `locked_commit` from this doc's frontmatter, verifies via `git cat-file -p e6263693...`, and writes its PLAN referencing `depends_on_doc: FUSION-DESIGN.md` with `depends_on_sha: e6263693dc7d3baee2cefc4bea757610bfe6b51e`.
4. **Phase 33 planner** reads `drill-dive-contract` anchor values (`DRILL_SPEED=2.0`, `DRILL_IMPACT_COST=20.0`, etc.) as the tuning baseline; retunes live via the F1 panel.

## Self-Check

**File-existence checks:**
- `.planning/FUSION-DESIGN.md` — FOUND
- `.planning/phases/30-fusion-lifecycle-design-doc/30-01-SUMMARY.md` — FOUND (this file)
- `.planning/ROADMAP.md` modified — FOUND (scope pivot applied)

**Commit-existence checks (all 9 commits):**
- `2b0da5e` — FOUND
- `2811a91` — FOUND
- `c6009ab` — FOUND
- `553de1c` — FOUND
- `562b18c` — FOUND
- `ad524e9` — FOUND
- `4c40149` — FOUND
- `e626369` — FOUND (doc-write SHA matches `locked_commit` in frontmatter)
- `a27dc31` — FOUND (lock commit; amends frontmatter)

## Self-Check: PASSED
