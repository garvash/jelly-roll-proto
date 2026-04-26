# Phase 32 Deferred Items

Pre-existing test failures discovered during Plan 01 execution (Wave 0). These are out of scope per the SCOPE BOUNDARY rule (NOT directly caused by Plan 01 test scaffolding). They were observed identically on the Plan 01 baseline before any test changes.

## Pre-Plan-32 baseline failures (do NOT block Plan 01 sign-off)

- `tests/test_physics.py::test_walk_logic` — `assert 1.7999999999999996 == 1.9` (floating-point drift; pre-Phase-32)
- `tests/test_sprite_assets.py::test_palette_compliance` — palette assertion (pre-Phase-32)
- `tests/test_tuning.py::test_pep562_flat_access` — `assert 0.13 == 0.0875` (tuning baseline mismatch; pre-Phase-32)
- `tests/test_tuning.py::test_set_value_visibility` — assertion mismatch (pre-Phase-32)
- `tests/test_tuning.py::test_baseline_reset_single_key` — `assert 0.13 == 0.0875` (pre-Phase-32)
- `tests/test_tuning.py::test_baseline_reset_all` — `assert 0.13 == 0.0875` (pre-Phase-32)
- `tests/test_tuning.py::test_bake_derived_determinism` — `assert 4 == 3` (pre-Phase-32)
- `tests/test_ldtk_migration.py::test_tileset_relpath_cavern` — `Tileset uid=64 not found in defs.tilesets` (pre-Phase-32)

Source: identical failures occur on `git stash` of Plan 01 changes (verified during Plan 01 execution).

These should be addressed in a dedicated tech-debt phase or by the appropriate domain owner — they are not part of FUS-04 / FUS-05 / FUS-07 scope.
