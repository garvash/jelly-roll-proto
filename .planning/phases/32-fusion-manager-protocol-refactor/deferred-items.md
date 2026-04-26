# Phase 32 Deferred Items

Pre-existing test failures observed during plan executions but out-of-scope per the executor scope boundary rule (issues NOT caused by the current task's changes).

## Pre-existing baseline failures (verified on base commit `3d51851`)

These tests fail on the Phase 32 base commit (`3d51851`, the `worktree-agent-a99c111cf96887134` branch root) BEFORE any plan code lands. They are unrelated to the fusion-package work.

- `tests/test_phase22.py::test_physics_constants_unchanged`
- `tests/test_phase22.py::test_physics_schema_updated`
- `tests/test_physics.py::test_walk_logic` — `assert 1.7999999999999996 == 1.9`
- `tests/test_sprite_assets.py::test_palette_compliance`
- `tests/test_tuning.py::test_pep562_flat_access` — `assert 0.13 == 0.0875`
- `tests/test_tuning.py::test_set_value_visibility`
- `tests/test_tuning.py::test_baseline_reset_single_key` — `assert 0.13 == 0.0875`
- `tests/test_tuning.py::test_baseline_reset_all` — `assert 0.13 == 0.0875`
- `tests/test_tuning.py::test_bake_derived_determinism` — `assert 4 == 3`

These appear related to physics/tuning preset values that diverged from the test expectations, likely from Phase 29 / Phase 31 / Phase 31.5 tuning changes. They predate Phase 32 and require their own dedicated triage pass — out of scope for fusion refactor plans.

**First observed during:** Plan 32-02 GREEN phase regression check (2026-04-26).
