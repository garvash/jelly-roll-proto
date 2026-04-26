---
phase: 32-fusion-manager-protocol-refactor
plan: 03
subsystem: save
tags: [save, versioning, json, exception, fus-07, wave-1]

# Dependency graph
requires:
  - phase: 32-fusion-manager-protocol-refactor
    provides: "Plan 01 (Wave 0) authors TestSaveVersionRejection class + migrates roundtrip assertions to save_version: 2 — REQUIRED for tests/test_save_system.py to GREEN under Plan 03 changes"
provides:
  - "CURRENT_SAVE_VERSION = 2 module-level constant in src/core/save_manager.py (D-23)"
  - "SaveVersionMismatchError(found, expected) exception class with preserved-on-disk semantics (D-24)"
  - "save() writes save_version key (was version: 1) — D-21 rename"
  - "load() rejects mismatched saves with hard-fail; missing-file path unchanged returns None (Pitfall 8)"
affects: [32-06-PLAN.md (main.py callsites surface user-facing message + try/except wrap)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Typed exception over result-dict for save-version rejection (RESEARCH § Save-Version Rejection Mechanism, lines 408-483 — chosen because main.py:1249 has an `if data:` truthiness guard that would silently misroute on a dict-with-error)"
    - "Order-of-operations: existence check → parse → version check (Pitfall 8) — preserves return None for missing-file case while still hard-failing on version mismatch"
    - "data.get(key) over data[key] for unknown-schema input — surfaces missing field as found=None instead of KeyError (T-32-03-01 mitigation)"

key-files:
  created: []
  modified:
    - "src/core/save_manager.py — +38/-5 lines; adds module docstring update, CURRENT_SAVE_VERSION constant, SaveVersionMismatchError class, version-check in load(), field rename in save()"

key-decisions:
  - "Typed exception (SaveVersionMismatchError) chosen over result-dict return per RESEARCH § Save-Version Rejection Mechanism — typed exception is the only mechanism that survives the existing main.py:1249 `if data:` truthiness guard without silent misrouting"
  - "Order: existence → parse → version (Pitfall 8) — missing-file returns None unchanged; missing-key (v1.3 saves) surfaces as found=None via data.get not subscript"
  - "No silent migration (D-24) — v1.3 saves are rejected with file preserved on disk; user gets a 'New game required' message in Plan 06"
  - "T-32-03-02 string-vs-int defense: Strict `!= CURRENT_SAVE_VERSION` (int comparison) — string '2' falls through to rejection, which is the safe path (rejection IS the design, not an edge case)"

patterns-established:
  - "Versioned save schema with hard-fail rejection — caller surfaces UX, library raises typed exception"
  - "Schema-version constants live next to their I/O code, not in tuning (D-23 — single source of truth, increment on breaking change)"

requirements-completed: [FUS-07]

# Metrics
duration: ~10min
completed: 2026-04-26
---

# Phase 32 Plan 03: Save Format v2 Summary

**Save format bumped to `save_version: 2` with typed SaveVersionMismatchError rejection in SaveManager.load(); v1.3 saves rejected on disk-preserved (D-24).**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-04-26T12:25:00Z
- **Completed:** 2026-04-26T12:32:26Z
- **Tasks:** 1 of 1
- **Files modified:** 1

## Accomplishments

- Module-level `CURRENT_SAVE_VERSION = 2` constant added (D-23 — single source of truth)
- `SaveVersionMismatchError` exception class with `found` + `expected` attributes; preserved-on-disk semantics in docstring
- `save()` writes `"save_version": CURRENT_SAVE_VERSION` instead of `"version": 1` (D-21)
- `load()` injection: existence → parse → version-check (Pitfall 8 order); raises `SaveVersionMismatchError(found, expected)` on mismatch with file preserved on disk (D-24)
- Module docstring updated with FUS-07 + D-21..D-24 references
- Threat-model mitigations active: T-32-03-01 (KeyError on missing key — `.get` returns None) and T-32-03-02 (string `"2"` vs int `2` — strict inequality forces rejection path)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add CURRENT_SAVE_VERSION constant + SaveVersionMismatchError class to src/core/save_manager.py** — `985ab97` (feat)

_Note: This plan is single-task. No separate test commit because Plan 01 (Wave 0) authors the test contract per phase plan; Plan 03 is the production-code half of the TDD pair. See "Cross-Plan TDD Coordination" below._

## Files Created/Modified

- `src/core/save_manager.py` — Save persistence layer; adds CURRENT_SAVE_VERSION + SaveVersionMismatchError + version-check + field rename. Other methods (`exists()`, `delete()`, `_get_save_path()`) unchanged per plan instruction.

## Decisions Made

- **Typed exception over result-dict** (RESEARCH § Save-Version Rejection Mechanism, lines 408-483): A `SaveVersionMismatchError` exception cleanly bypasses the existing `if data:` truthiness guard at main.py:1249, whereas a result-dict would silently misroute (a non-empty dict is truthy and would make main.py treat the error as a successful load).
- **Order: existence → parse → version** (Pitfall 8): Missing file MUST short-circuit return None before any JSON parse; otherwise we'd raise on a fresh install. Existing `if not os.path.exists(path): return None` block kept FIRST.
- **`data.get("save_version")` not `data["save_version"]`** (T-32-03-01): v1.3 saves don't have the key at all; subscript would raise `KeyError` (a DoS surface per STRIDE). `.get(key)` returns None, which falls through to `!= CURRENT_SAVE_VERSION` and surfaces cleanly via `SaveVersionMismatchError(found=None, ...)`.
- **`f"...{found}..."` in `__init__`**: Exception message lives in `__init__` so callers can `except SaveVersionMismatchError as e` and access `e.found` / `e.expected` for UX surfacing — Plan 06 will use these in main.py.
- **No magic numbers**: Literal `2` appears ONLY at `CURRENT_SAVE_VERSION = 2`. The save payload uses `CURRENT_SAVE_VERSION`, the version-check uses `CURRENT_SAVE_VERSION`, and the exception's `expected` parameter receives `CURRENT_SAVE_VERSION`. Per project MEMORY no-magic-numbers rule.

## Deviations from Plan

None — plan executed exactly as written. All `<acceptance_criteria>` grep checks pass:

| Acceptance check | Result |
|------------------|--------|
| `^CURRENT_SAVE_VERSION = 2$` | 1 match |
| `class SaveVersionMismatchError` | 1 match |
| `"save_version": CURRENT_SAVE_VERSION` | 1 match |
| `"version": 1` (old field gone) | 0 matches |
| `raise SaveVersionMismatchError` | 1 match |
| `data.get("save_version")` | 1 match |
| Module imports cleanly | OK |
| Inline-Python verify (v1 reject + file-preserved) | PASS |

Final file size: 103 lines (plan estimated 80-95; the slightly larger size comes from richer `load()` and module docstrings, both informational only — no behavior delta).

## Cross-Plan TDD Coordination

Plan 03 is the production-code half of a TDD pair where Plan 01 (Wave 0) is the test-authoring half. They run in parallel waves and merge after both complete. Per Plan 01 § Task 2 the following test-side changes belong to Plan 01, NOT Plan 03:

- `tests/test_save_system.py` line 58: `assert "version" in data` → `assert "save_version" in data`
- `tests/test_save_system.py` line 87: `assert data["version"] == 1` → `assert data["save_version"] == CURRENT_SAVE_VERSION`
- `tests/test_save_system.py`: new `TestSaveVersionRejection` class with 3 tests covering v1 rejection + file-preservation semantics

**Implication for this worktree:** Running `python -m pytest tests/test_save_system.py` against the standalone Plan 03 worktree (without Plan 01 merged) FAILS at `TestSaveManager::test_load_returns_dict` (asserts `"version" in data`) — this is expected and resolves at merge. Verification was performed via the inline Python script in the plan's `<verify>` block, which is self-contained and does not depend on Plan 01:

```
OK: v1 save rejected with found=None
OK: file preserved
```

The Plan 03 acceptance criterion `python -m pytest tests/test_save_system.py -x -q exits 0` is contingent on Plan 01 being merged first. Phase-level orchestrator owns the merge ordering.

## Threat Model Verdict

| Threat | Disposition | Status post-Plan 03 |
|--------|-------------|---------------------|
| T-32-03-01 (DoS via KeyError on missing save_version key) | mitigate | MITIGATED — `data.get("save_version")` returns None for v1.3 saves; surfaces as `found=None`, no KeyError |
| T-32-03-02 (Tampering: save_version as string '2') | mitigate | MITIGATED — strict `!= 2` comparison; string `'2' != 2` evaluates True → falls through to rejection (the safe path) |
| T-32-03-03 (DoS: malformed JSON triggers JSONDecodeError) | accept | ACCEPTED with rationale per RESEARCH § Threat Model Surface (line 834) — same pre/post Plan 03; out-of-scope for prototype, flagged for Phase 35+ hygiene |
| T-32-03-04 (Path traversal via user-supplied filename) | n/a | N/A — `_get_save_path()` resolves to fixed `tuning.SAVE_FILE`, no user input controls filename |
| T-32-03-05 (Code execution via JSON payload) | n/a | N/A — `json.load` parses to primitives only, no eval |
| T-32-03-06 (Tampering on shared filesystem) | accept | ACCEPTED — single-user local prototype scope; HMAC signing deferred post-prototype |

**Block-on threshold:** HIGH. None of T-32-03-01..06 unmitigated above HIGH. Gate passes.

## Issues Encountered

None — single-pass surgical edit per plan recipe. No iteration, no debugging.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 06 (main.py callsite migration) can now wrap `SaveManager.load()` with `try/except SaveVersionMismatchError` at main.py:1197 and main.py:1249 to surface a user-facing "New game required" message. The `e.found` / `e.expected` attributes are available for log/telemetry purposes.
- Plan 04 (FusionManager) does not depend on this plan; runs in parallel.
- Plan 01 test migration must merge BEFORE this worktree to keep `pytest tests/test_save_system.py` green at trunk.

## Self-Check: PASSED

**Created files:** none

**Modified files:**
- FOUND: `src/core/save_manager.py` (verified 103 lines, contains CURRENT_SAVE_VERSION + SaveVersionMismatchError + save_version field + raise + data.get pattern)

**Commits:**
- FOUND: `985ab97` — `feat(32-03): add save_version=2 + SaveVersionMismatchError to SaveManager (FUS-07)`

**Inline verifications:**
- v1 save rejection with `found=None`: PASS
- File preserved on disk after rejection: PASS
- Module imports cleanly: PASS
- `CURRENT_SAVE_VERSION == 2` constant exposed at module level: PASS

---
*Phase: 32-fusion-manager-protocol-refactor*
*Completed: 2026-04-26*
