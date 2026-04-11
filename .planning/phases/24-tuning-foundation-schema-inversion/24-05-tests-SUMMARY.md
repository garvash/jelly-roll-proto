---
phase: 24
plan: 05
subsystem: tests
tags: [tests, pytest, loader, baseline, compat-shim, smoke, fnd-02, fnd-04, fnd-06]
dependency_graph:
  requires:
    - "24-02 (assets/physics-schema.json v0.3.0)"
    - "24-03 (src/core/tuning.py loader + mutation API)"
    - "24-04 (src/core/constants.py compat shim)"
  provides:
    - "tests/test_tuning.py — 11-test unit + smoke suite locking in FND-02 / FND-04 revised / FND-06 / FND-03 safety net"
    - "HAZARD_DRAIN_RATES int-key regression guard"
  affects:
    - "tests/test_tuning.py (new)"
tech_stack:
  added: []
  patterns:
    - "pytest autouse fixture for pristine-baseline isolation"
    - "tmp_path fixture for filesystem-isolated round-trip + duplicate-leaf tests"
    - "Module-import smoke test loop (importlib.import_module) with try/except re-raise as AssertionError naming the offending module"
    - "Named-constant discipline: all numeric literals hoisted to module-level EXPECTED_* / MUTATED_* constants (per project memory 'Avoid magic numbers')"
key_files:
  created:
    - "tests/test_tuning.py"
  modified: []
decisions:
  - "Suite size: 11 tests exactly — the executor's acceptance greps pin the names, so no added/removed/parametrized tests (plan explicitly forbids scope creep)"
  - "autouse fixture calls tuning.load() at setup AND a defensive tuning.load() + tuning.reset() at teardown so tests that swap the schema path (test_name_uniqueness_raises, test_atomic_save_round_trip) leave the real schema loaded for the next test regardless of pytest collection order"
  - "Did NOT mock pyxel for the compat-shim smoke test — pyxel is installed as a real package in .venv/ and all 12 legacy callers import cleanly against it (verified). Mocking would hide real import-time regressions"
  - "Used module-level EXPECTED_HAZARD_KEY_{SLOW,MEDIUM,FAST} constants (6/7/8) to avoid magic numbers in the int-key regression test per the 'Avoid magic numbers' project memory"
  - "test_compat_shim_smoke wraps each import in try/except and re-raises as AssertionError with the module name (T-24-20 mitigation) rather than letting a raw ImportError escape — named context is load-bearing for triage"
metrics:
  duration_seconds: 220
  completed: 2026-04-11
  tasks: 1
  files_changed: 1
requirements_completed:
  - FND-02
  - FND-04
  - FND-06
---

# Phase 24 Plan 05: Tests Summary

**One-liner:** Eleven-test pytest suite in `tests/test_tuning.py` (235 lines) that locks in the Phase 24 loader API, mutation visibility (FND-04 revised), baseline reset (D-04), name-uniqueness invariant (D-15), bake_derived determinism (FND-06), atomic save round-trip (D-03/D-05), and the 12-caller compat-shim smoke test (FND-03), with HAZARD_DRAIN_RATES int-key regression guarded — all 11 tests green in 0.17s.

## What Changed

### tests/test_tuning.py (Task 1) — new, 235 lines

**Test file layout** (top-down):

1. **Module docstring** — names each gate test and cites the requirement it guards (FND-02, FND-04 revised, FND-06, FND-03, D-15, D-04).
2. **Imports** — `importlib`, `json`, `pathlib.Path`, `pytest`, `from src.core import tuning`.
3. **Named constants block** — 17 module-level constants covering every literal value the tests reference:
   - `EXPECTED_GRAVITY=0.0875`, `EXPECTED_JUMP_FORCE=-3.25`, `EXPECTED_MAX_WALK_SPEED=1.25`, `EXPECTED_SAVE_FILE='save.json'`
   - `EXPECTED_MAX_HEIGHT_TILES=3`, `EXPECTED_MAX_WIDTH_TILES=5` (v1.3 hand-baked per D-12 / FND-06)
   - `EXPECTED_HAZARD_DRAIN_SLOW=0.25`, `_MEDIUM=0.75`, `_FAST=1.5`; `EXPECTED_HAZARD_KEY_SLOW=6`, `_MEDIUM=7`, `_FAST=8`
   - `MIN_FLAT_LEAVES=50` (acceptance lower bound; actual loaded count is 87)
   - `MUTATED_GRAVITY_A=0.123`, `_B=0.5`, `_C=0.111`; `MUTATED_JUMP_FORCE=-5.0`
   - `ROUND_TRIP_GRAVITY_FROM_BAD_SCHEMA_A=0.1`, `_B=0.2` (the two conflicting values in test_name_uniqueness_raises)
4. **`LEGACY_CALLERS`** — 12-element list consumed by `test_compat_shim_smoke`.
5. **`_reload_tuning` autouse fixture** — `tuning.load()` at setup; `tuning.load()` + `tuning.reset()` at teardown. The defensive teardown reload handles tests that swap `_schema_path` (test_name_uniqueness_raises, test_atomic_save_round_trip) so the next test always starts reading the real `assets/physics-schema.json`.
6. **The 11 tests** — in the plan's locked order:

| # | Test name | What it pins |
| - | --------- | ------------- |
| 1 | `test_load_round_trip` | Loader reads the real schema; `__all__` ≥ 50 leaves; `_baseline is not _model` (deepcopy, not alias). |
| 2 | `test_pep562_flat_access` | `tuning.GRAVITY`, `JUMP_FORCE`, `MAX_WALK_SPEED`, `RAM_INVINCIBLE is True`, `SAVE_FILE`; unknown attr raises `AttributeError` matching `"NOT_A_KEY"`. |
| 3 | **`test_set_value_visibility`** (FND-04 revised gate) | `set_value('GRAVITY', 0.123)` → `tuning.GRAVITY == 0.123`; `get_baseline('GRAVITY') == 0.0875`; `get_group('GRAVITY') == 'movement'`. |
| 4 | `test_baseline_reset_single_key` | `reset('GRAVITY')` restores one leaf (D-04). |
| 5 | `test_baseline_reset_all` | `reset()` restores every leaf (D-04). |
| 6 | `test_set_value_unknown_key_raises` | `KeyError` on `set_value('NOT_A_KEY', 1)` (D-15 / T-24-10). |
| 7 | `test_name_uniqueness_raises` | Synthetic schema with `movement.GRAVITY` + `slime_juice.GRAVITY` collision; `tuning.load(schema_path=tmp_path/...)` raises `ValueError` matching `"Duplicate tuning leaf"` (D-15). Restores real schema afterward. |
| 8 | **`test_bake_derived_determinism`** (FND-06 gate) | `reset()` + `bake_derived()` → `max_height_tiles == 3`, `max_width_tiles == 5`. |
| 9 | `test_atomic_save_round_trip` | Seeds `tmp_path/round-trip-schema.json` with a copy of the real schema, mutates `GRAVITY`, `save()`, reloads, asserts new value AND that `get_baseline('GRAVITY') == 0.111` (D-05: reload takes a fresh baseline). |
| 10 | **`test_compat_shim_smoke`** (FND-03 gate) | `importlib.import_module` over all 12 legacy caller paths. `try/except` re-raises as `AssertionError` naming the offending module (T-24-20 mitigation, no silent skips). |
| 11 | `test_hazard_drain_rates_int_keys` | `from src.core.constants import HAZARD_DRAIN_RATES`; asserts `[6]==0.25`, `[7]==0.75`, `[8]==1.5` (Plan 04 JSON int-key fix-up regression guard). |

**What the test file deliberately does NOT do** (per plan's explicit forbidden list):

- No `@pytest.mark.parametrize` — keeps the grep-based acceptance checks simple.
- No pyxel-window integration tests — unit-test file only.
- No monkeypatching of anything inside `tuning.py` — every test exercises the real loader against the real schema.
- No modifications to `tests/conftest.py` or any other test file (there is no `conftest.py`; verified via `ls tests/conftest.py`).
- No tests beyond the 11 locked names.

## Tasks Completed

| Task | Name                                                        | Commit  | Files                  |
| ---- | ----------------------------------------------------------- | ------- | ---------------------- |
| 1    | Write tests/test_tuning.py with 11 locked tests             | 6ac4554 | tests/test_tuning.py   |

## Verification

All plan acceptance criteria executed in-session:

```
test -f tests/test_tuning.py                                              OK
wc -l tests/test_tuning.py (235 >= 150)                                   OK
grep "def test_load_round_trip" tests/test_tuning.py                      OK
grep "def test_pep562_flat_access" tests/test_tuning.py                   OK
grep "def test_set_value_visibility" tests/test_tuning.py                 OK
grep "def test_baseline_reset_single_key" tests/test_tuning.py            OK
grep "def test_baseline_reset_all" tests/test_tuning.py                   OK
grep "def test_set_value_unknown_key_raises" tests/test_tuning.py         OK
grep "def test_name_uniqueness_raises" tests/test_tuning.py               OK
grep "def test_bake_derived_determinism" tests/test_tuning.py             OK
grep "def test_atomic_save_round_trip" tests/test_tuning.py               OK
grep "def test_compat_shim_smoke" tests/test_tuning.py                    OK
grep "def test_hazard_drain_rates_int_keys" tests/test_tuning.py          OK
python -m pytest tests/test_tuning.py -q                                  11 passed in 0.17s
python -m pytest tests/test_tuning.py::test_set_value_visibility -q       1 passed  (FND-04 gate)
python -m pytest tests/test_tuning.py::test_bake_derived_determinism -q   1 passed  (FND-06 gate)
python -m pytest tests/test_tuning.py::test_compat_shim_smoke -q          1 passed  (FND-03 gate)
```

**All 12 legacy callers imported cleanly** under the real (installed) pyxel package — no mock needed. Verified out-of-test with a one-liner loop before writing the suite, and again inside `test_compat_shim_smoke` during the pytest run. Zero side-effect crashes at import time.

**No schema or source-code drift:** `git status --short` after the Task 1 commit shows only the new `tests/test_tuning.py`. `assets/physics-schema.json`, `src/core/tuning.py`, and `src/core/constants.py` are byte-identical to their pre-plan state — the `tmp_path` fixture successfully isolated the round-trip and duplicate-leaf tests from the real asset.

## Deviations from Plan

None. The plan gave the 11 test names, fixture, and key code blocks explicitly; the suite implements them verbatim with the following planner-permitted clarifications:

- **Autouse fixture has a defensive reload in teardown.** The plan specified `tuning.load()` at setup and `tuning.reset()` at teardown. I added a `tuning.load()` before the `tuning.reset()` in teardown because `test_name_uniqueness_raises` and `test_atomic_save_round_trip` both bind `_schema_path` to a `tmp_path` temp file; without the reload, the next test in the suite would start against a now-deleted temp schema. Both swap-tests also call `tuning.load()` at their own tail as the plan requires — the teardown reload is pure belt-and-suspenders. This is within the spirit of the plan ("every test starts with a pristine baseline") and does not change test behavior in the happy path.

- **`EXPECTED_HAZARD_KEY_*` constants added.** The plan's `test_hazard_drain_rates_int_keys` pseudo-code literal-indexed `HAZARD_DRAIN_RATES[6]`, `[7]`, `[8]`. The project memory `feedback_magic_numbers.md` says "use named constants or comments for all numeric literals," so I hoisted the three int keys to module-level `EXPECTED_HAZARD_KEY_{SLOW,MEDIUM,FAST}` constants alongside the existing value constants. Intent is identical; no test behavior change.

No Rule 1 bugs, no Rule 2 missing critical functionality, no Rule 3 blockers, no Rule 4 architectural escalations. No bugs were discovered in `tuning.py`, `constants.py`, or `physics-schema.json` during test-writing — the Wave 2/3/4 deliverables are solid and every gate test passed on the first run.

## Auth Gates Hit

None.

## Deferred Issues

None.

## Known Stubs

None. Every test exercises real module state and real disk I/O (through `tmp_path`); nothing is mocked or stubbed.

## Threat Flags

None introduced. All threat-model mitigations from the plan's `<threat_model>` are implemented:

- **T-24-18** (test writes clobbering real `physics-schema.json`) — `test_atomic_save_round_trip` and `test_name_uniqueness_raises` both use pytest's `tmp_path` fixture. The real `assets/physics-schema.json` is never a save target. Each test calls `tuning.load()` at its tail to restore the default path, and the autouse teardown adds a defensive reload. Verified: `git status --short assets/physics-schema.json` is empty after the full pytest run.
- **T-24-19** (test pollution across ordering) — autouse `_reload_tuning` fixture. Every test sees a pristine baseline regardless of collection order.
- **T-24-20** (compat-shim smoke test crashing on pyxel side effects) — `test_compat_shim_smoke` wraps each `importlib.import_module` in try/except and re-raises as `AssertionError` naming the offending module. No silent skips. In practice, none of the 12 callers have pyxel-init side effects at import time (verified), so the raise path is pure defense-in-depth.

## Self-Check: PASSED

- `tests/test_tuning.py` — present, 235 lines, all 11 locked test names grep-verified
- `python -m pytest tests/test_tuning.py -q` — 11 passed in 0.17s (zero failures, zero skips, zero warnings)
- Three gate tests runnable in isolation:
  - `tests/test_tuning.py::test_set_value_visibility` — passed (FND-04 revised)
  - `tests/test_tuning.py::test_bake_derived_determinism` — passed (FND-06)
  - `tests/test_tuning.py::test_compat_shim_smoke` — passed (FND-03 safety net across all 12 callers)
- Commit `6ac4554` — found in `git log --oneline` (`test(24-05): add tuning loader + compat shim test suite`)
- Worktree rebased to `8faa4729` (per worktree_branch_check) before any edits — verified via `git merge-base --is-ancestor` (and `git reset --hard` executed because the worktree started on a descendant branch)
- `git status --short tests/test_tuning.py assets/physics-schema.json src/core/tuning.py src/core/constants.py` after the final commit shows only `tests/test_tuning.py` as the intended new file; no unintended modifications to schema or source code
- No `conftest.py` created or modified (verified by `ls tests/conftest.py` → not found, both before and after)
