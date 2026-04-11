---
phase: 24-tuning-foundation-schema-inversion
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/REQUIREMENTS.md
  - .planning/ROADMAP.md
autonomous: true
requirements:
  - FND-04
tags: [docs, requirements, roadmap, blocking]
must_haves:
  truths:
    - "REQUIREMENTS.md FND-04 no longer mentions hot-reload / mtime watcher"
    - "REQUIREMENTS.md FND-04 references tuning.set_value() visibility as the acceptance condition"
    - "ROADMAP.md Phase 24 success criterion #2 no longer mentions text-editor editing"
    - "ROADMAP.md Phase 24 success criterion #2 references the set_value visibility test"
  artifacts:
    - path: ".planning/REQUIREMENTS.md"
      provides: "FND-04 revised wording (set_value visibility, not hot-reload)"
      contains: "set_value"
    - path: ".planning/ROADMAP.md"
      provides: "Phase 24 success criterion #2 revised to match FND-04"
      contains: "set_value"
  key_links:
    - from: ".planning/REQUIREMENTS.md FND-04"
      to: ".planning/ROADMAP.md Phase 24 success criterion #2"
      via: "identical set_value visibility test phrasing"
      pattern: "set_value"
---

<objective>
Revise the two planning-doc placeholders that still encode the dropped hot-reload requirement BEFORE any code task runs, so downstream verification reads the correct acceptance targets.

Purpose: CONTEXT.md §requirement_changes explicitly drops FND-04 (file-watcher hot-reload) and replaces it with a set_value() in-process visibility test. If REQUIREMENTS.md and ROADMAP.md still encode the old wording when Plans 02-06 run, the verifier will check the wrong criteria and either fail correct work or pass wrong work. This plan MUST run and commit before any other Phase 24 plan.

Output: REQUIREMENTS.md FND-04 rewritten, ROADMAP.md Phase 24 success criterion #2 rewritten, both committed.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/REQUIREMENTS.md
@.planning/ROADMAP.md
@.planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Revise FND-04 in REQUIREMENTS.md [BLOCKING]</name>
  <files>.planning/REQUIREMENTS.md</files>
  <read_first>
    - .planning/REQUIREMENTS.md (current FND-04 wording is on or near line 16)
    - .planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md (§requirement_changes — the replacement wording is dictated here)
  </read_first>
  <action>
    Open .planning/REQUIREMENTS.md.

    REPLACE the FND-04 line (currently reads exactly):

    > - [ ] **FND-04**: Hot-reload works — external file edits (git pull, text editor save) are detected and applied within one frame via mtime check in game loop.

    WITH the replacement wording from CONTEXT.md §requirement_changes, verbatim:

    > - [ ] **FND-04**: Mutations via `tuning.set_value()` are visible to subsequent reads in the same process (verified via unit test). File-watch hot-reload is not implemented — the live-tuning panel (Phase 28) is the only editing interface. The git-pull workflow is "restart the game."

    Leave FND-01, FND-02, FND-03, FND-05, FND-06 UNCHANGED. Do NOT renumber. Do NOT touch the Traceability table or Coverage-by-Phase table (FND-04 is still a Phase 24 requirement, just with new wording).

    The phrase "hot-reload", "mtime", "text editor", "one frame" MUST NOT appear anywhere in the FND-04 bullet after this edit. The phrase "set_value" MUST appear in the FND-04 bullet after this edit.
  </action>
  <verify>
    <automated>grep -c "FND-04.*set_value" .planning/REQUIREMENTS.md</automated>
  </verify>
  <acceptance_criteria>
    - `grep -q "FND-04.*set_value" .planning/REQUIREMENTS.md` exits 0
    - `grep -E "FND-04.*(mtime|hot-reload|text editor)" .planning/REQUIREMENTS.md` returns NO matches (exit 1)
    - `grep -q "^- \[ \] \*\*FND-01\*\*" .planning/REQUIREMENTS.md` exits 0 (FND-01 untouched)
    - `grep -q "^- \[ \] \*\*FND-05\*\*" .planning/REQUIREMENTS.md` exits 0 (FND-05 untouched)
    - `grep -q "^- \[ \] \*\*FND-06\*\*" .planning/REQUIREMENTS.md` exits 0 (FND-06 untouched)
    - `grep -q "| FND-04 | Phase 24" .planning/REQUIREMENTS.md` exits 0 (traceability row still present)
  </acceptance_criteria>
  <done>FND-04 wording replaced verbatim with CONTEXT.md §requirement_changes text; no hot-reload/mtime/text-editor phrasing remains in FND-04; other FND entries and traceability tables are byte-identical.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Revise ROADMAP.md Phase 24 success criterion #2 [BLOCKING]</name>
  <files>.planning/ROADMAP.md</files>
  <read_first>
    - .planning/ROADMAP.md (Phase 24 block starts at "### Phase 24: Tuning Foundation (Schema Inversion)" ~line 80)
    - .planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md (§requirement_changes)
  </read_first>
  <action>
    Open .planning/ROADMAP.md.

    Locate the "### Phase 24: Tuning Foundation (Schema Inversion)" block. Under "**Success Criteria** (what must be TRUE):", REPLACE bullet #2, which currently reads:

    > 2. Editing `physics-schema.json` in a text editor while the game is running causes the edited value to take effect within one frame without a restart

    WITH:

    > 2. Calling `tuning.set_value(key, value)` makes the new value visible to subsequent `getattr(tuning, key)` reads in the same process (verified by `tests/test_tuning.py::test_set_value_visibility`). File-watcher hot-reload is explicitly not implemented — the live-tuning panel (Phase 28) is the only editing interface.

    Also UPDATE the Phase 24 **Goal** line, which currently reads:

    > **Goal**: Promote `physics-schema.json` to the single source of truth, with a loader that hot-reloads external edits and a compat shim that keeps existing `constants.py` call sites working. Game boots with values identical to v1.3.

    TO (remove "hot-reloads external edits"):

    > **Goal**: Promote `physics-schema.json` to the single source of truth, with a loader that exposes a mutation API (`set_value`/`save`/`reset`/`bake_derived`) and a compat shim that keeps existing `constants.py` call sites working. Game boots with values identical to v1.3.

    Also UPDATE the Phase 24 one-line entry in the v2.0 phase list, which currently reads:

    > - [ ] **Phase 24: Tuning Foundation (Schema Inversion)** — Promote `physics-schema.json` to source of truth with loader, hot-reload, compat shim, and converter smoke test

    TO:

    > - [ ] **Phase 24: Tuning Foundation (Schema Inversion)** — Promote `physics-schema.json` to source of truth with loader, mutation API, compat shim, and converter handoff update

    Leave criteria #1, #3, #4 UNCHANGED. Leave all other phases UNCHANGED. Do NOT touch the Progress table at the bottom.
  </action>
  <verify>
    <automated>grep -c "set_value" .planning/ROADMAP.md</automated>
  </verify>
  <acceptance_criteria>
    - `grep -q "tuning.set_value" .planning/ROADMAP.md` exits 0
    - `grep -q "test_set_value_visibility" .planning/ROADMAP.md` exits 0
    - `grep -E "Editing .physics-schema.json. in a text editor" .planning/ROADMAP.md` returns NO matches (exit 1)
    - `grep -q "hot-reloads external edits" .planning/ROADMAP.md` exits 1 (phrase removed)
    - `grep -q "Phase 25: Call-Site Migration" .planning/ROADMAP.md` exits 0 (other phases untouched)
    - `grep -q "mutation API" .planning/ROADMAP.md` exits 0 (Phase 24 goal line updated)
  </acceptance_criteria>
  <done>ROADMAP.md Phase 24 Goal line, the v2.0 phase-list one-liner, and success criterion #2 all updated to match the FND-04 revision; success criteria #1/#3/#4 byte-identical; no other phase blocks mutated.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| planner → executor | Stale requirement wording could drive wrong verification |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-24-01 | Tampering | .planning/REQUIREMENTS.md | mitigate | Grep-based acceptance criteria pin exact strings ("set_value" present, "mtime"/"hot-reload" absent) so an accidental revert or partial edit fails the task |
| T-24-02 | Tampering | .planning/ROADMAP.md | mitigate | Same: pin both the added and removed substrings; also verify unrelated phase blocks remain present |
| T-24-03 | Information Disclosure | n/a | accept | Docs are already in-repo and public; no secret content is touched |
</threat_model>

<verification>
After both tasks:
- `grep -q "set_value" .planning/REQUIREMENTS.md .planning/ROADMAP.md` exits 0
- `grep -E "(mtime|hot-reloads external)" .planning/REQUIREMENTS.md .planning/ROADMAP.md` returns no matches
- `git diff --stat .planning/REQUIREMENTS.md .planning/ROADMAP.md` shows exactly these two files changed
</verification>

<success_criteria>
- FND-04 in REQUIREMENTS.md reads the CONTEXT.md §requirement_changes replacement verbatim
- ROADMAP.md Phase 24 success criterion #2 references `test_set_value_visibility`
- ROADMAP.md Phase 24 Goal line no longer says "hot-reloads external edits"
- No other REQ-IDs or phase blocks were touched
- Both files committed so later plans read the revised acceptance targets
</success_criteria>

<output>
After completion, create `.planning/phases/24-tuning-foundation-schema-inversion/24-01-SUMMARY.md`
</output>
