# Phase 33 Deferred Items

Out-of-scope discoveries logged during plan execution. These are pre-existing
failures in the base commit (`5c3b78179f2a36f1705664f664e698d3aade5820`) and
NOT caused by any Phase 33 work. Verified by `git stash` + re-run on clean tree.

## Pre-existing test failures (not regressions)

Discovered during Plan 06 Task 1 GREEN-phase verification (2026-04-29).
None of these touch `src/core/debug.py`, `main.py:Game.update` warp consumer,
or any file modified by Plan 06.

| Test                                                       | Likely Owner             | Notes                                                                 |
| ---------------------------------------------------------- | ------------------------ | --------------------------------------------------------------------- |
| `tests/test_ldtk_migration.py::test_tileset_relpath_cavern` | LDtk asset pipeline      | `tilesets uid=64` not present in current world JSON; pipeline drift   |
| `tests/test_phase22.py::test_physics_constants_unchanged`   | Phase 29 movement retune | Asserts pre-Phase-29 v1.3 values; superseded by v2.0-default preset   |
| `tests/test_phase22.py::test_physics_schema_updated`        | Phase 29 schema delta    | Same — schema seed values changed in Phase 29, test not updated       |
| `tests/test_physics.py::test_walk_logic`                    | Phase 29 walk speed      | Asserts MAX_WALK_SPEED == 1.9 but current preset has 1.7999... drift  |
| `tests/test_sprite_assets.py::test_palette_compliance`      | Phase 31 art pipeline    | Sprite palette violation; Phase 31 cell additions or art swap         |
| `tests/test_tuning.py::test_pep562_flat_access`             | Phase 29 tuning seeds    | GRAVITY default mismatch (0.13 vs 0.0875); seed updated, test stale   |
| `tests/test_tuning.py::test_set_value_visibility`           | Phase 29 tuning seeds    | Same root cause                                                       |
| `tests/test_tuning.py::test_baseline_reset_single_key`      | Phase 29 tuning seeds    | Same root cause                                                       |
| `tests/test_tuning.py::test_baseline_reset_all`             | Phase 29 tuning seeds    | Same root cause                                                       |
| `tests/test_tuning.py::test_bake_derived_determinism`       | Phase 29 derived bakes   | `derived.jump.max_height_tiles` changed from 3 to 4 post-Phase-29     |

## Verification

Confirmed pre-existing by:
```bash
git stash
python -m pytest tests/test_phase22.py tests/test_physics.py \
                 tests/test_sprite_assets.py tests/test_tuning.py \
                 tests/test_ldtk_migration.py::test_tileset_relpath_cavern -q
# Result: identical 10 failures
git stash pop
```

Phase 33 Plan 06 Task 1 only modifies `src/core/debug.py` + `main.py:Game.update`.
The `tests/test_debug.py` suite (extended with 8 new Phase 33 cases) is GREEN
post-implementation: `14 passed in 0.06s`.

These failures should be addressed in a dedicated test-update plan (Phase 36
final preset bake, or a stand-alone test-debt phase). Not blocking Phase 33.
