# Phase 32 Deferred Items

Pre-existing test failures observed during plan executions but out-of-scope per the executor SCOPE BOUNDARY rule (issues NOT caused by the current task's changes). These tests fail on the Phase 32 base commit (`3d51851`) BEFORE any plan code lands and require their own dedicated triage pass — they are unrelated to FUS-04 / FUS-05 / FUS-07 scope.

## Pre-existing baseline failures (verified on base commit `3d51851`)

- `tests/test_phase22.py::test_physics_constants_unchanged`
- `tests/test_phase22.py::test_physics_schema_updated`
- `tests/test_physics.py::test_walk_logic` — `assert 1.7999999999999996 == 1.9` (floating-point drift)
- `tests/test_sprite_assets.py::test_palette_compliance` — palette assertion
- `tests/test_tuning.py::test_pep562_flat_access` — `assert 0.13 == 0.0875`
- `tests/test_tuning.py::test_set_value_visibility`
- `tests/test_tuning.py::test_baseline_reset_single_key` — `assert 0.13 == 0.0875`
- `tests/test_tuning.py::test_baseline_reset_all` — `assert 0.13 == 0.0875`
- `tests/test_tuning.py::test_bake_derived_determinism` — `assert 4 == 3`
- `tests/test_ldtk_migration.py::test_tileset_relpath_cavern` — `Tileset uid=64 not found in defs.tilesets`

These appear related to physics/tuning preset values that diverged from the test expectations, likely from Phase 29 / Phase 31 / Phase 31.5 tuning changes. They should be addressed in a dedicated tech-debt phase or by the appropriate domain owner.

**First observed:** Plan 32-02 GREEN phase regression check; identical failures verified during Plan 32-01 execution via `git stash` of plan changes (2026-04-26).

## Pre-Plan-06 expected failures (activated by Plan 05 import threshold)

Wave 0 wrote `tests/test_fusion.py` test bodies that depend on `Player.is_fused` being a `@property` that reads through `game.fusion_manager.is_fused` (D-14a). Plan 06 owns that change (per VALIDATION row 32-06-01). Until Plan 06 ships, the following tests fail with `assert False` on `player.is_fused` / `assert 2 == 3` on `player.hp`:

- `tests/test_fusion.py::test_fuse_sets_both_flags`
- `tests/test_fusion.py::test_unfuse_clears_both_flags`
- `tests/test_fusion.py::test_mana_shield_consumes_juice`
- `tests/test_fusion.py::test_mana_shield_dissipates_on_empty`

These tests SKIPPED through Plan 04 because the test file's `importorskip("src.fusion.drill_dive")` / `importorskip("src.fusion.pogo")` gate had not yet been satisfied. Plan 05 ships those modules and the tests now collect and run — but the underlying Player wiring (D-14a `@property`) is Plan 06 scope. They will turn GREEN automatically when Plan 06 lands.

**First observed:** Plan 32-05 full regression run after Task 2 GREEN (2026-04-26).
