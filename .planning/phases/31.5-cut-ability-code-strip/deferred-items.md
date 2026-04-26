---
phase: 31.5-cut-ability-code-strip
created: 2026-04-26
discovered_during: Plan 05 (acceptance) Gate 4 (full pytest)
---

# Phase 31.5: Deferred Items

Per SCOPE BOUNDARY: only auto-fix issues DIRECTLY caused by the current
plan's changes. Pre-existing failures in unrelated files are out of scope
and logged here for future cleanup.

---

## Pre-existing pytest failures (10 tests) -- NOT caused by Phase 31.5

**Confirmed pre-existing on base commit `c3d276f` (run before any Plan 05
edits): identical 17-failure baseline. After Plan 05 fixed the 7 sympathetic
strip regressions, 10 remain — all unrelated to the cut-ability strip.**

### Group A: tuning baseline mismatch (5 failures) — Phase 29 era

| Test | Expected (v1.3) | Actual (live schema, post-Phase-29) |
|------|-----------------|--------------------------------------|
| `test_tuning.py::test_pep562_flat_access` | GRAVITY = 0.0875 | 0.13 |
| `test_tuning.py::test_set_value_visibility` | baseline GRAVITY = 0.0875 | 0.13 |
| `test_tuning.py::test_baseline_reset_single_key` | reset to 0.0875 | 0.13 |
| `test_tuning.py::test_baseline_reset_all` | reset to 0.0875 / -3.25 | 0.13 / -4.0 |
| `test_tuning.py::test_bake_derived_determinism` | max_height_tiles = 3 | 4 |

**Root cause:** The Phase 29 (player-movement-feel-pass) updated
`assets/physics-schema.json` with new v2.0 baseline tuning values, but
`tests/test_tuning.py` still asserts against the v1.3 EXPECTED_* constants
(lines 30-34). These tests need their EXPECTED_* constants updated to match
the live schema baseline OR the test fixture needs to load a v1.3 fixture
schema for these specific assertions.

**Why deferred:** Out of scope per SCOPE BOUNDARY — pre-existing on base
commit, unrelated to Phase 31.5 cut-ability strip. Belongs in a Phase 29
cleanup or a dedicated test-baseline-refresh task.

### Group B: physics archive expectations (3 failures) — Phase 22/29 era

| Test | Reason |
|------|--------|
| `test_phase22.py::test_physics_constants_unchanged` | Phase 22 archived constants vs live schema mismatch |
| `test_phase22.py::test_physics_schema_updated` | Phase 22 schema version expectations stale |
| `test_physics.py::test_walk_logic` | walk-speed expects 1.9 baseline, gets 1.7999... (rounding from new accel/friction) |

**Why deferred:** Out of scope. These tests assert Phase 22-era physics
behavior that was superseded by Phase 29's feel pass. No Phase 31.5
relevance.

### Group C: test infrastructure / asset format (2 failures)

| Test | Reason |
|------|--------|
| `test_sprite_assets.py::test_palette_compliance` | `pyxel.images[1].pget()` returns MagicMock (test infrastructure issue — Pyxel needs real init for pget(), but conftest mocks at module load) |
| `test_ldtk_migration.py::test_tileset_relpath_cavern` | LDtk file no longer has tileset uid=64 (asset format change) |

**Why deferred:** Out of scope. These are test infrastructure / asset
format issues unrelated to the cut-ability strip.

---

## Stale assertions in animation defensive tests (low priority)

`tests/test_anim.py` and `tests/test_anim_hitbox.py` reference state
strings RAMMING / DASHING / BOOSTING / CHARGING_SHOT in defensive
fallback tests. The tests still **PASS** (Python's setattr lets them set
arbitrary state strings on a Player; the fallback rule applies). The
strings are dead vocabulary post-strip but the tests are functionally
correct as defensive coverage.

**Why deferred:** Tests pass; cleanup is hygiene-only. Future cleanup
can drop the cut-state strings from the fallback tuples once the broader
animation suite is overhauled.

---

## Sign-off

These items are not blockers for Phase 32 unblock. They are cataloged
here to prevent re-discovery in future executions. Address in a
dedicated maintenance plan when convenient.
