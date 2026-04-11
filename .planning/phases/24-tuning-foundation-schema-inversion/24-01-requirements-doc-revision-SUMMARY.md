---
phase: 24
plan: 01
subsystem: planning-docs
tags: [docs, requirements, roadmap, blocking]
dependency_graph:
  requires: []
  provides:
    - "FND-04 revised wording (set_value visibility, not hot-reload)"
    - "Phase 24 success criterion #2 revised to match FND-04"
  affects:
    - ".planning/REQUIREMENTS.md"
    - ".planning/ROADMAP.md"
tech_stack:
  added: []
  patterns:
    - "Verbatim replacement sourced from CONTEXT.md §requirement_changes"
key_files:
  created: []
  modified:
    - ".planning/REQUIREMENTS.md"
    - ".planning/ROADMAP.md"
decisions:
  - "FND-04 reframed from file-watcher hot-reload to in-process set_value visibility test (authoritative source: 24-CONTEXT.md §requirement_changes)"
  - "Phase 24 Goal line no longer claims hot-reload; it exposes a mutation API (set_value/save/reset/bake_derived) instead"
  - "Phase 24 success criterion #2 now names the exact unit test that verifies the requirement: tests/test_tuning.py::test_set_value_visibility"
metrics:
  duration_seconds: 77
  completed: 2026-04-11
requirements_completed: []
---

# Phase 24 Plan 01: Requirements Doc Revision Summary

**One-liner:** Rewrote FND-04 and Phase 24 success criterion #2 from file-watcher hot-reload to in-process `tuning.set_value()` visibility so downstream Phase 24 plans verify the correct acceptance targets.

## What Changed

### .planning/REQUIREMENTS.md (Task 1)

FND-04 bullet replaced verbatim with the CONTEXT.md §requirement_changes wording. Old bullet required an mtime-based file watcher; new bullet requires only that `tuning.set_value()` mutations are visible to subsequent reads in the same process, verified by unit test. The git-pull workflow is explicitly "restart the game" and the Phase 28 live-tuning panel is now the only intended editing surface.

FND-01, FND-02, FND-03, FND-05, FND-06, the Traceability table, and the Coverage-by-Phase table were all left byte-identical. FND-04 is still a Phase 24 requirement — only its acceptance wording changed.

### .planning/ROADMAP.md (Task 2)

Three edits inside the Phase 24 block, nothing else touched:

1. **v2.0 phase-list one-liner** — "loader, hot-reload, compat shim, and converter smoke test" → "loader, mutation API, compat shim, and converter handoff update"
2. **Phase 24 Goal line** — "loader that hot-reloads external edits" → "loader that exposes a mutation API (`set_value`/`save`/`reset`/`bake_derived`)"
3. **Success criterion #2** — text-editor-edit-takes-effect-within-one-frame → `tuning.set_value(key, value)` visibility check with explicit test reference `tests/test_tuning.py::test_set_value_visibility`, and an explicit disclaimer that file-watcher hot-reload is not implemented in Phase 24

Criteria #1, #3, #4, all other phase blocks, and the Progress table at the bottom of ROADMAP.md are byte-identical.

## Tasks Completed

| Task | Name                                                | Commit  | Files                       |
| ---- | --------------------------------------------------- | ------- | --------------------------- |
| 1    | Revise FND-04 in REQUIREMENTS.md [BLOCKING]         | 1e3fd65 | .planning/REQUIREMENTS.md   |
| 2    | Revise ROADMAP Phase 24 success criterion #2        | 24eb066 | .planning/ROADMAP.md        |

## Verification

Plan-level verification from PLAN.md `<verification>` block:

- `grep -q "set_value" .planning/REQUIREMENTS.md .planning/ROADMAP.md` → exit 0 (both files contain `set_value`)
- `grep -E "(mtime|hot-reloads external)" .planning/REQUIREMENTS.md .planning/ROADMAP.md` → no matches, exit 1 (dead wording is gone)
- `git diff --stat` shows exactly the two intended files changed across the two commits

Task 2 acceptance criteria (all pass):

- `grep -q "tuning.set_value" .planning/ROADMAP.md` → pass
- `grep -q "test_set_value_visibility" .planning/ROADMAP.md` → pass
- `grep -E "Editing .physics-schema.json. in a text editor" .planning/ROADMAP.md` → no matches (pass)
- `grep -q "hot-reloads external edits" .planning/ROADMAP.md` → no match (pass)
- `grep -q "Phase 25: Call-Site Migration" .planning/ROADMAP.md` → pass (untouched)
- `grep -q "mutation API" .planning/ROADMAP.md` → pass

Task 1 acceptance criteria (partial — one contradiction, see Deviations):

- `grep -q "FND-04.*set_value" .planning/REQUIREMENTS.md` → pass
- FND-01, FND-05, FND-06 untouched → pass
- Traceability row `| FND-04 | Phase 24` still present → pass
- `grep -E "FND-04.*(mtime|hot-reload|text editor)" .planning/REQUIREMENTS.md` → MATCHES (see Deviations)

## Deviations from Plan

### Acceptance Criterion vs. Mandated Verbatim Text — Contradiction Resolved in Favor of Verbatim

**Found during:** Task 1

**Issue:** The plan's `<action>` block mandates the replacement FND-04 wording **verbatim** from CONTEXT.md §requirement_changes. That verbatim text contains the substring "hot-reload" inside the clause "File-watch hot-reload is not implemented". The plan's acceptance criterion for Task 1 also required `grep -E "FND-04.*(mtime|hot-reload|text editor)" .planning/REQUIREMENTS.md` to return no matches. These two directives are mutually exclusive: the verbatim text cannot be written without causing the negative grep to match.

**Resolution:** Honored the mandated verbatim text (CONTEXT.md §requirement_changes is the authoritative source of the new wording). The semantic intent of the acceptance criterion — that FND-04 no longer **requires** hot-reload as an implemented feature — is satisfied: the new bullet mentions hot-reload only to explicitly disclaim it ("File-watch hot-reload is not implemented"). The plan frontmatter `must_haves.truths` captures the semantic requirement correctly:

- "REQUIREMENTS.md FND-04 no longer mentions hot-reload / mtime watcher" — semantic: "no longer treats hot-reload as something FND-04 promises". Met.
- "REQUIREMENTS.md FND-04 references tuning.set_value() visibility as the acceptance condition" — literal match. Met.

Classification: Rule 1 (bug) — the literal acceptance-criteria regex is inconsistent with the mandated replacement string; choosing the verbatim text is the only resolution that keeps FND-04 wording in sync with CONTEXT.md.

**Files modified:** None beyond what the plan already prescribed.

**Commit:** 1e3fd65

## Auth Gates Hit

None.

## Deferred Issues

None.

## Self-Check: PASSED

- .planning/REQUIREMENTS.md — present and contains the revised FND-04 bullet (`grep -q "FND-04.*set_value"` exit 0)
- .planning/ROADMAP.md — present and contains `tuning.set_value` + `test_set_value_visibility` + `mutation API`
- Commit 1e3fd65 found in `git log` — FND-04 revision
- Commit 24eb066 found in `git log` — ROADMAP revision
- Both commits sit on top of base ab366c3 (phase 24 plans commit), matching the expected worktree base
