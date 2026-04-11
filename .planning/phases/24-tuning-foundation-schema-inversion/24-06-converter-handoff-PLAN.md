---
phase: 24-tuning-foundation-schema-inversion
plan: 06
type: execute
wave: 4
depends_on: [24-02]
files_modified:
  - CONVERTER-HANDOFF.md
autonomous: false
requirements:
  - FND-06
tags: [docs, converter-contract, handoff, human-verify]
must_haves:
  truths:
    - "CONVERTER-HANDOFF.md documents the v0.2.0 → v0.3.0 physics-schema.json layout change"
    - "An old-path → new-path migration table shows every v0.2.0 top-level key moving under derived.*"
    - "The doc explains that tuning.* is game-facing raw inputs, derived.* is the converter contract"
    - "The doc explains derived.* on disk may lag tuning.* between Phase 24 and Phase 36 (D-11 — acceptable staleness)"
    - "The doc flags the name-uniqueness invariant (D-15) for any future converter-side schema extension"
    - "The doc is committed before the plan closes"
  artifacts:
    - path: "CONVERTER-HANDOFF.md"
      provides: "Updated converter contract reflecting v0.3.0 layout"
      contains: "v0.3.0"
  key_links:
    - from: "CONVERTER-HANDOFF.md"
      to: "assets/physics-schema.json v0.3.0"
      via: "migration table from old top-level paths to derived.* paths"
      pattern: "derived\\."
---

<objective>
Update `CONVERTER-HANDOFF.md` so the external pml-to-ldtk converter team has a clean migration path from reading v0.2.0's top-level blocks (player, jump, fall, clearance, placement_rules, source_constants) to reading v0.3.0's `derived.*` and `tuning.*` blocks.

Purpose: This is FND-06. The pml-to-ldtk converter is NOT in this repo — the handoff doc is the only deliverable the external team consumes, and Phase 23's handoff doc is currently written against v0.2.0. If this plan doesn't run, the v2.0 ship in Phase 36 hits a broken contract.

Output: CONVERTER-HANDOFF.md with a new "v2.0 Schema Inversion (v0.3.0)" section that includes an old-path → new-path migration table, the tuning/derived split explanation, and the staleness note (D-11).

This plan includes a checkpoint:human-verify step because the doc change is a contract-surface for humans on another team — the user should skim the migration table before committing.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CONVERTER-HANDOFF.md
@assets/physics-schema.json
@.planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Append v0.3.0 migration section to CONVERTER-HANDOFF.md</name>
  <files>CONVERTER-HANDOFF.md</files>
  <read_first>
    - CONVERTER-HANDOFF.md (current doc, written for v0.2.0 — you are appending, not rewriting)
    - assets/physics-schema.json (v0.3.0 — the new layout, so the migration table is accurate)
    - .planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md (§decisions D-06..D-11)
  </read_first>
  <action>
    Open CONVERTER-HANDOFF.md. DO NOT rewrite existing Sections 1-4 (v1.3 migration content — those stay as the v1.3 historical record). APPEND a new top-level section after Section 4:

    # Section 5: v2.0 Schema Inversion (physics-schema.json v0.2.0 → v0.3.0)

    Then write the following content verbatim (adjust only line wrapping if needed — markdown tables can't wrap mid-row):

    ```markdown
    **Date:** 2026-04-11
    **Scope:** Phase 24 of the v2.0 milestone
    **Schema version:** `physics-schema.json` v0.2.0 → v0.3.0 (BREAKING LAYOUT)

    ## TL;DR

    The game now treats `physics-schema.json` as the single source of truth for tuning values. The file has been restructured into two sibling top-level blocks:

    - **`tuning.*`** — raw game inputs (GRAVITY, JUMP_FORCE, every named constant from `src/core/constants.py`), grouped by system. The running game reads these directly.
    - **`derived.*`** — converter-facing values (jump max height, clearance rules, placement caps) computed from `tuning.*` via Euler integration. **This is what the pml-to-ldtk converter should read.** It is the same content you read in v0.2.0 — the fields moved one level deeper and nothing was renamed.

    **What you must change on the converter side:** prefix every old top-level path with `derived.`. That's it. No field renames, no unit changes, no value drift. A gap that was `5` tiles wide in v0.2.0 is still `5` tiles wide in v0.3.0.

    **What is new:** `source_constants` is deleted. Its six scalar values moved into `tuning.movement.*` and `tuning.tile.*` alongside the rest of the game constants.

    ## Migration Table (v0.2.0 → v0.3.0)

    | Old path (v0.2.0)                                  | New path (v0.3.0)                                  | Changed?          |
    |----------------------------------------------------|----------------------------------------------------|-------------------|
    | `$schema`                                          | `$schema`                                          | unchanged         |
    | `title`                                            | `title`                                            | unchanged         |
    | `description`                                      | `description`                                      | updated wording   |
    | `version`                                          | `version`                                          | `0.2.0` → `0.3.0` |
    | `updated`                                          | `updated`                                          | unchanged         |
    | `tile_size`                                        | `tile_size`                                        | unchanged (16)    |
    | `fps`                                              | `fps`                                              | unchanged (60)    |
    | `player.*`                                         | `derived.player.*`                                 | moved, unchanged  |
    | `jump.*`                                           | `derived.jump.*`                                   | moved, unchanged  |
    | `fall.*`                                           | `derived.fall.*`                                   | moved, unchanged  |
    | `clearance.*`                                      | `derived.clearance.*`                              | moved, unchanged  |
    | `placement_rules.*`                                | `derived.placement_rules.*`                        | moved, unchanged  |
    | `source_constants.GRAVITY`                         | `tuning.movement.GRAVITY`                          | moved             |
    | `source_constants.JUMP_FORCE`                      | `tuning.movement.JUMP_FORCE`                       | moved             |
    | `source_constants.MAX_WALK_SPEED`                  | `tuning.movement.MAX_WALK_SPEED`                   | moved             |
    | `source_constants.MAX_FALL_SPEED`                  | `tuning.movement.MAX_FALL_SPEED`                   | moved             |
    | `source_constants.FALLING_GRAVITY_MULTIPLIER`      | `tuning.movement.FALLING_GRAVITY_MULTIPLIER`       | moved             |
    | `source_constants.TILE_SIZE`                       | `tuning.tile.TILE_SIZE`                            | moved             |
    | `source_constants` (block)                         | (deleted — values moved into `tuning.*`)           | **DELETED**       |

    ## What is `tuning.*`? (for context)

    `tuning.*` is the game's read surface. It holds ~60 named constants grouped into ~22 sections that mirror the comment headers of `src/core/constants.py`:

    - `tuning.tile`, `tuning.display`, `tuning.sprite`
    - `tuning.hazards`, `tuning.movement`, `tuning.forgiving`, `tuning.wall`
    - `tuning.slime_follow`, `tuning.slime_juice`, `tuning.projectile`
    - `tuning.drill`, `tuning.juice_effects`, `tuning.health`, `tuning.dash`
    - `tuning.fusion`, `tuning.slime_ram`, `tuning.charge_shot`, `tuning.boost`
    - `tuning.gates`, `tuning.save`, `tuning.death`, `tuning.save_point`

    The converter does not need to read `tuning.*`. Everything the converter needs is in `derived.*`. `tuning.*` is documented here only so you know what the game actually reads from the file.

    ### Name-uniqueness invariant

    Every leaf key under `tuning.*` is globally unique across groups. The game's loader raises at boot if two groups ever contain the same leaf. If a future schema extension wants to add a new key, it must not collide with an existing name. This matters to the converter only if you ever decide to write keys back into `tuning.*` — don't create duplicates.

    ## Staleness window for `derived.*` (Phase 24 → Phase 36)

    Between now (Phase 24) and the v2.0 ship (Phase 36), `derived.*` on disk may lag `tuning.*`. This is intentional: during the v2.0 feel passes, the developer will be dragging sliders that mutate `tuning.*` in memory via a live panel, but the panel will not automatically re-bake `derived.*` on every slider drag — that would rewrite the converter contract dozens of times per minute.

    Instead, `derived.*` is rebaked on demand via:

    ```
    python -m src.core.tuning bake
    ```

    which recomputes the `derived.jump.*` fields (the only algorithmically computed subblock) from the current `tuning.*` values via the same Euler integration the game uses, and writes the result back to `physics-schema.json`.

    **What this means for the converter team:** if you pull a WIP commit during v2.0 development, `derived.*` might be stale relative to what the game actually runs. This is normal. Wait for the v2.0 Phase 36 "shipping bake" commit (or run the bake command yourself) before taking a hard dependency on specific `derived.*` values. For pre-Phase-36 smoke testing, the v0.3.0 initial commit is a known-good bake against v1.3 baseline values.

    ## Section 4 deltas (LDtk output format)

    No changes to the LDtk output format in this phase. Section 3 of this document (v1.3 LDtk output format changes) still applies unchanged. The v2.0 schema inversion is a contract-surface change only — `.ldtk` file output is byte-identical.
    ```

    After appending, make sure the file still parses as valid markdown (no stray backticks, table pipes aligned, etc.).

    Do NOT:
    - rewrite or delete any content from existing Sections 1-4
    - change the document's existing header structure or table of contents
    - touch any other file
    - add migration instructions for tuning.* keys the converter doesn't actually read (scope creep — the converter reads derived.*, so the migration table only needs to show derived.* paths plus the handful of source_constants leaves that moved)
  </action>
  <verify>
    <automated>grep -q "v0.3.0" CONVERTER-HANDOFF.md && grep -q "derived.jump" CONVERTER-HANDOFF.md && grep -q "Section 5" CONVERTER-HANDOFF.md</automated>
  </verify>
  <acceptance_criteria>
    - `grep -q "v0.3.0" CONVERTER-HANDOFF.md` exits 0
    - `grep -q "Section 5" CONVERTER-HANDOFF.md` exits 0
    - `grep -q "derived.jump" CONVERTER-HANDOFF.md` exits 0
    - `grep -q "derived.player" CONVERTER-HANDOFF.md` exits 0
    - `grep -q "derived.placement_rules" CONVERTER-HANDOFF.md` exits 0
    - `grep -q "tuning.movement.GRAVITY" CONVERTER-HANDOFF.md` exits 0
    - `grep -q "source_constants" CONVERTER-HANDOFF.md` exits 0 (still referenced — as the deleted block)
    - `grep -q "python -m src.core.tuning bake" CONVERTER-HANDOFF.md` exits 0 (bake command documented)
    - `grep -q "name-uniqueness" CONVERTER-HANDOFF.md` exits 0 (D-15 flagged for converter team)
    - `grep -q "Section 1" CONVERTER-HANDOFF.md` exits 0 (Section 1-4 still present — append, not rewrite)
    - `grep -q "v1.3 Migration Handoff" CONVERTER-HANDOFF.md` exits 0 (original v1.3 header untouched)
  </acceptance_criteria>
  <done>CONVERTER-HANDOFF.md has a new Section 5 documenting the v0.3.0 layout change with an old-path → new-path table, a tuning/derived explanation, the bake-command staleness note, and the name-uniqueness invariant; Sections 1-4 are byte-identical to pre-plan state.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: Human-verify the CONVERTER-HANDOFF.md Section 5 migration table</name>
  <files>CONVERTER-HANDOFF.md</files>
  <read_first>
    - CONVERTER-HANDOFF.md (the file just updated in Task 1)
    - assets/physics-schema.json (ground truth to spot-check migration table rows against)
  </read_first>
  <what-built>A new Section 5 of CONVERTER-HANDOFF.md containing a v0.2.0 → v0.3.0 migration table, a tuning/derived explanation, the `python -m src.core.tuning bake` command documentation, and the derived.* staleness note (D-11).</what-built>
  <action>
    This is a human-verify checkpoint. The executor has already written Section 5 in Task 1; this task asks the user to skim it before the plan commits. The executor should:

    1. Print the file path to the user: `CONVERTER-HANDOFF.md`
    2. Suggest the spot-check steps below (these are the same as <how-to-verify>)
    3. Wait for the user to type "approved" or describe corrections
    4. If corrections are requested, make them and loop back to step 1
    5. If approved, exit the checkpoint and let execute-plan commit

    No code or file writes happen in this task unless the user requests corrections.
  </action>
  <how-to-verify>
    1. Open `CONVERTER-HANDOFF.md` and scroll to the end — you should see "# Section 5: v2.0 Schema Inversion (physics-schema.json v0.2.0 → v0.3.0)".
    2. Read the migration table and spot-check three rows against `assets/physics-schema.json`:
       - `jump.max_height_tiles` — should now be at `derived.jump.max_height_tiles` (open the JSON and confirm it's 3).
       - `source_constants.GRAVITY` — should now be at `tuning.movement.GRAVITY` (open the JSON and confirm it's 0.0875).
       - `placement_rules.max_gap_horizontal` — should now be at `derived.placement_rules.max_gap_horizontal.value_tiles` (open the JSON and confirm it's 5).
    3. Confirm the staleness note accurately describes what you want the converter team to expect (pre-Phase-36 commits may have stale derived.*, re-bake with the CLI command).
    4. Confirm nothing in Sections 1-4 was accidentally clobbered — the top of the file should still read "# v1.3 Migration Handoff: 16x16 Tile Migration".

    Time box: 3-5 minutes. This is a doc review, not a deep audit.
  </how-to-verify>
  <verify>
    <automated>grep -q "Section 5" CONVERTER-HANDOFF.md && grep -q "v1.3 Migration Handoff" CONVERTER-HANDOFF.md</automated>
  </verify>
  <acceptance_criteria>
    - User types "approved" or equivalent affirmative
    - If user requests changes, executor makes them and re-presents before accepting approval
    - `grep -q "Section 5" CONVERTER-HANDOFF.md` exits 0 (content still present after any corrections)
    - `grep -q "v1.3 Migration Handoff" CONVERTER-HANDOFF.md` exits 0 (original content still intact)
  </acceptance_criteria>
  <done>User has reviewed Section 5 and typed "approved" (or requested changes were made and re-approved); CONVERTER-HANDOFF.md is ready to commit with the v0.3.0 migration content.</done>
  <resume-signal>Type "approved" to continue, or describe any corrections needed (e.g. "row X shows wrong path", "staleness note is confusing", "need to add a link to the bake CLI").</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| this repo → external pml-to-ldtk team | The handoff doc is the only contract surface; if it's wrong or stale, the v2.0 ship hits a broken converter |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-24-21 | Repudiation | future "why did the converter break" debate | mitigate | Explicit old → new migration table with every path called out row-by-row leaves no ambiguity about what changed |
| T-24-22 | Tampering | accidental wipe of v1.3 Section 1-4 content | mitigate | Acceptance criteria grep for "Section 1" and "v1.3 Migration Handoff" presence; checkpoint:human-verify asks the user to confirm Sections 1-4 are intact |
| T-24-23 | Information Disclosure | n/a | accept | Handoff doc is in-repo and contains no secrets |
</threat_model>

<verification>
- Section 5 present with v0.3.0 migration table
- `tuning.movement.GRAVITY`, `derived.jump`, `derived.placement_rules` all mentioned
- Bake CLI documented
- Name-uniqueness invariant flagged
- Sections 1-4 untouched (grep for "Section 1" and "v1.3 Migration Handoff" still match)
- Human-verify step approved
</verification>

<success_criteria>
- CONVERTER-HANDOFF.md has a complete Section 5 documenting the v0.3.0 contract shift
- The converter team has a 1-row-per-path migration table (no "figure it out yourself")
- Staleness expectations (D-11) are explicit
- D-15 name-uniqueness is flagged as an invariant the converter team must respect if they ever extend tuning.*
- Old content is preserved
</success_criteria>

<output>
After completion, create `.planning/phases/24-tuning-foundation-schema-inversion/24-06-SUMMARY.md`
</output>
