---
phase: 25
plan: 02
subsystem: tuning-test-infrastructure
tags: [test, livereach, FND-05, acceptance-artifact]
requires:
  - src/core/tuning.py (Phase 24 — set_value / reset / get_baseline API)
  - src/entities/player.py (Phase 25 Plan 01 — migrated to tuning.X use sites)
provides:
  - tests/test_tuning_livereach.py (FND-05 acceptance artifact #1)
affects:
  - Future Phase 28 panel work can rely on a regression net that catches
    reintroduction of import-time caching in player.py
tech_stack:
  added: []
  patterns:
    - "autouse pytest fixture calling tuning.reset() in teardown (D-04a)"
    - "pyxel globally mocked via sys.modules pre-import (steal from test_physics.py)"
    - "per-test patch('src.entities.player.input_manager') to drive input state"
key_files:
  created:
    - tests/test_tuning_livereach.py
  modified: []
decisions:
  - "Used LIVEREACH_MULTIPLIER=10.0 for all four tests — large enough to be visible above float noise, small enough to avoid overflow or collision-probe side effects"
  - "Autouse teardown fixture runs tuning.reset() (whole-model) after every test — D-04a hermetic requirement"
  - "GRAVITY test uses strict dy_mutated==pytest.approx(dy_baseline*10, rel=1e-6) — catches any partial-miss in the apply_physics() migration"
  - "JUMP_FORCE test asserts delta relationship (dy_mutated - dy_baseline == 9*baseline_jump) instead of raw equality — the one-frame gravity tick cancels cleanly in the difference"
  - "MAX_WALK_SPEED test runs 16 frames to saturate baseline cleanly (10-frame saturation at baseline) then compares dx > baseline_cap — does not try to reach mutated saturation (would need 100 frames)"
  - "WALK_FRICTION test uses FRICTION_START_DX=1.0 so the 10x mutation (1.5) triggers the max(0, ...) clamp-to-zero branch, and asserts dx_mutated==pytest.approx(0.0, abs=1e-6)"
  - "Did NOT import anything from src.core.constants — referencing the shim in a Phase 25 acceptance test would be self-defeating"
  - "Named constants for every numeric literal per project memory (LIVEREACH_MULTIPLIER, WALK_SATURATION_FRAMES, FRICTION_START_DX, APPROX_REL)"
metrics:
  duration: ~12min
  completed: 2026-04-12
  tests_added: 4
  keys_covered: 4
  lines_added: 308
  sanity_check_nop_result: "all 4 tests fail when tuning.set_value calls are NOPed (proves not a green false positive)"
requirements:
  - FND-05
---

# Phase 25 Plan 02: Livereach Test Summary

**One-liner:** Added `tests/test_tuning_livereach.py` with four hermetic tests (GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, WALK_FRICTION) proving that `tuning.set_value()` mutations reach `Player` physics on the very next frame — the FND-05 acceptance artifact that closes Phase 25's "changes physics on the next frame" success criterion.

## Keys Covered (4)

Per 25-CONTEXT D-04.1 the minimum bar was GRAVITY / JUMP_FORCE / MAX_WALK_SPEED / WALK_FRICTION. All four are covered, one test function per key, with the naming pattern `test_livereach_<key_lowercase>` for grep-friendliness.

| Key             | Use site driven                           | Assertion                                                                        |
| --------------- | ----------------------------------------- | -------------------------------------------------------------------------------- |
| GRAVITY         | `apply_physics()` falling branch          | `dy_mutated == pytest.approx(dy_baseline * 10, rel=1e-6)` (strict 10x)           |
| JUMP_FORCE      | `handle_input()` jump branch              | `dy_mutated - dy_baseline == pytest.approx(9 * baseline_jump, rel=1e-6)`         |
| MAX_WALK_SPEED  | `handle_input()` horizontal clamp         | `dx_mutated > dx_baseline` after 16 frames of walk input                         |
| WALK_FRICTION   | `handle_input()` friction branch          | `dx_mutated == pytest.approx(0.0, abs=1e-6)` (10x friction clamps to zero)       |

Each test is structured as Phase A (baseline) → `tuning.set_value(KEY, 10 * baseline)` → Phase B (mutated), with a fresh `Player` instance per phase so no cached state leaks across the mutation boundary.

## Hermetic Fixture (D-04a)

Single autouse fixture at module scope:

```python
@pytest.fixture(autouse=True)
def _tuning_reset_after_each_test():
    yield
    tuning.reset()
```

`tuning.reset()` with no argument restores the whole `_model` from `_baseline` via a deepcopy rebind, so the next test starts at v1.3 baseline regardless of what the previous test mutated. Confirmed no cross-test contamination: after this file the full `pytest -q` suite ran 367 passed, 3 skipped (was 363 passed, 3 skipped before this plan — exactly +4 for the new tests, zero regressions in the other 26 test files that still import from the compat shim).

## Floating-Point Tolerance Choices

- `APPROX_REL = 1e-6` — used for strict equality checks (gravity, jump delta, walk friction residual). Tight enough to catch any accidental truncation or single-precision drift, loose enough to absorb standard double-precision roundoff.
- `pytest.approx(0.0, abs=1e-6)` — used for the friction clamp-to-zero check. Relative tolerance is unsafe against zero; absolute `1e-6` is the documented pytest idiom for "this should be zero, modulo roundoff".
- MAX_WALK_SPEED test uses strict `>` rather than an `approx` equality, because the mutated run does not saturate in 16 frames (would need ~100) — only the direction-of-change is load-bearing.

## Sanity Check (Plan verification step 4)

Performed inline: temporarily NOPed every `tuning.set_value(...)` line in the test file (re-routed to a `pass` statement) and re-ran the suite. Result:

```
4 failed in 0.23s
FAILED tests/test_tuning_livereach.py::test_livereach_gravity
FAILED tests/test_tuning_livereach.py::test_livereach_jump_force
FAILED tests/test_tuning_livereach.py::test_livereach_max_walk_speed
FAILED tests/test_tuning_livereach.py::test_livereach_walk_friction
```

All 4 tests failed (e.g. WALK_FRICTION: `dx_baseline=0.85, dx_mutated=0.85` — identical because the mutation never happened). File then reverted to the committed version and re-run: `4 passed in 0.11s`. This proves the tests genuinely depend on `set_value` reaching gameplay — they are **not** green false positives.

## Verification

| Command                                     | Result                          |
| -------------------------------------------- | ------------------------------- |
| `pytest tests/test_tuning_livereach.py -q`   | **4 passed in 0.15s**           |
| `pytest tests/test_tuning.py -q`             | **11 passed in 0.27s** (Phase 24 green) |
| `pytest -q` (full suite)                     | **367 passed, 3 skipped in 42.32s** (+4 vs baseline) |
| Sanity NOP of `set_value` calls              | 4 failed (as designed)          |
| Revert NOP → re-run                          | 4 passed                        |

## Acceptance Criteria (all pass)

- `tests/test_tuning_livereach.py` exists
- `test_livereach_gravity` / `test_livereach_jump_force` / `test_livereach_max_walk_speed` / `test_livereach_walk_friction` — one each
- `tuning.reset()` present (in the autouse fixture)
- `tuning.set_value` present 4× (one call per test; 9 total matches including docstring references)
- `from src.core.constants` — **zero** occurrences (the test deliberately does not touch the shim)
- `autouse=True` fixture present (single `_tuning_reset_after_each_test` fixture)
- `pytest tests/test_tuning_livereach.py -q` exits 0 with 4 passed
- `pytest -q` (full suite) exits 0 (no contamination from the new fixture)
- `pytest tests/test_tuning.py -q` exits 0 (Phase 24 untouched)

## Deviations from Plan

None. The plan executed exactly as written in a single task. The only noteworthy implementation choice that wasn't prescribed was assigning `slime.max_juice`, `slime.is_dissipated`, and `slime.is_recalling` on the `mock_slime` fixture — these are needed because `update_shield()` / `handle_input()` read them on the slime; they were not in the copied harness block from `test_physics.py` because that file's tests don't drive `player.update()` end-to-end. Added defensively to keep the harness hermetic.

Also set `mock_level.get_zone_hazard_type.return_value = None` on the level mock so `update_shield()` stays in the dormant (no-hazard) branch — `MagicMock`'s default truthy return would otherwise activate the shield logic and contaminate `dy`/`dx` measurements. This is a harness hygiene fix, not a deviation from the plan's intent.

## Self-Check: PASSED

- FOUND: C:\Github\jelly-roll-proto\.claude\worktrees\agent-a0ff28be\tests\test_tuning_livereach.py
- FOUND: C:\Github\jelly-roll-proto\.claude\worktrees\agent-a0ff28be\.planning\phases\25-call-site-migration-constants-tuning\25-02-SUMMARY.md (this file)
- FOUND commit: 174c9a9 (test(25-02): add livereach tests proving tuning mutations reach gameplay)
