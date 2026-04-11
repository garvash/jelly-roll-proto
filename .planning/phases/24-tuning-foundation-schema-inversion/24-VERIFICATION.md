---
phase: 24-tuning-foundation-schema-inversion
verified: 2026-04-11T00:00:00Z
status: human_needed
score: 3/4 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Boot the game and spot-check v1.3 parity: walk speed, jump height, gravity, drill, and ram"
    expected: "All behaviors match v1.3 frame-for-frame (no numeric drift; timings identical). Specifically: walk speed feels 1.25px/f, jump peak reaches ~3 tiles, gravity falls at ~0.0875px/f^2 ascending / ~0.1575 descending, drill dive dives at ~2.0px/f, ram moves at ~2.5px/f."
    why_human: "Frame-for-frame gameplay parity cannot be verified programmatically without a recorded playthrough fixture; current unit tests only confirm the numeric *values* flow from schema to _model, not that the full runtime loop (pyxel update/draw) produces v1.3-identical behaviour"
deferred:
  - truth: "bake_derived() computed max_width_px = 84 drifts from schema-authored 89 (both floor to max_width_tiles = 5 so functional parity holds)"
    addressed_in: "Phase 36"
    evidence: "Phase 36 goal: 'Preset Bake + Regression Check — Lock shipping preset, regression playthrough against v1.0-v1.3'. Plan 24-03 SUMMARY explicitly defers formula reconciliation to Phase 36's preset-bake."
---

# Phase 24: Tuning Foundation (Schema Inversion) Verification Report

**Phase Goal:** Promote `physics-schema.json` to the single source of truth, with a loader that exposes a mutation API (`set_value`/`save`/`reset`/`bake_derived`) and a compat shim that keeps existing `constants.py` call sites working. Game boots with values identical to v1.3.

**Verified:** 2026-04-11
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (from ROADMAP.md Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Game boots from `physics-schema.json` values and plays identically to v1.3 (spot-check: walk speed, jump height, gravity, drill, ram all match frame-for-frame) | ? UNCERTAIN | Numeric values verified (all 87 leaves flow schema → tuning._model → constants.py shim without drift); `python -c "import main"` succeeds; 11/11 test_tuning.py tests pass; full suite 356 passed / 3 skipped (only unrelated pre-existing ldtk test fails). Frame-for-frame gameplay parity requires human play-through. |
| 2 | Calling `tuning.set_value(key, value)` makes the new value visible to subsequent `getattr(tuning, key)` reads in the same process (verified by `tests/test_tuning.py::test_set_value_visibility`) | VERIFIED | `python -m pytest tests/test_tuning.py::test_set_value_visibility -q` passes. Live spot-check: `set_value('GRAVITY', 0.09)` → `tuning.GRAVITY == 0.09`; `get_baseline('GRAVITY') == 0.0875`; `reset('GRAVITY')` restores to 0.0875. |
| 3 | Every existing `from src.core.constants import X` call site still imports successfully (compat shim verified by `python -c "import src.core.constants"`) | VERIFIED | `python -c "import src.core.constants"` exits 0. All 12 legacy callers (boss/slime/enemies/effects/player/save_point/items/projectile/map/world/save_manager/sprite_utils) imported cleanly in one session. `test_compat_shim_smoke` passes. |
| 4 | pml-to-ldtk converter smoke test passes against the restructured schema; CONVERTER-HANDOFF.md reflects the new `tuning.*` / `derived.*` layout | VERIFIED | CONVERTER-HANDOFF.md has Section 5 at line 112 with migration table, `derived.jump`, `tuning.movement.GRAVITY`, `python -m src.core.tuning bake` CLI, `Name-uniqueness invariant`, and the staleness note (D-11); Sections 1-4 (v1.3 history) intact at line 1. Schema round-trips cleanly via bake CLI; 22 tuning groups, 5 derived keys, all D-06 top-level keys present in correct order. |

**Score:** 3/4 truths verified (1 requires human spot-check)

### Deferred Items

| # | Item | Addressed In | Evidence |
|---|------|--------------|----------|
| 1 | bake_derived().max_width_px computes 84, schema authored 89 — both floor to max_width_tiles=5 so functional parity holds, but formula reconciliation is pending | Phase 36 | ROADMAP Phase 36: "Milestone Cap — Preset Bake + Regression Check — Lock shipping preset, regression playthrough against v1.0-v1.3, CONVERTER-HANDOFF.md final". Plan 24-03 SUMMARY §Deviations explicitly defers the fix to the Phase 36 preset-bake reconciliation. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `assets/physics-schema.json` | v0.3.0 with tuning.* (22 groups, 87 unique leaves) + derived.* (5 blocks); source_constants deleted | VERIFIED | version="0.3.0"; 9 top-level keys in D-06 order; 22 tuning groups; 87 unique flat leaves; derived has {player, jump, fall, clearance, placement_rules}; GRAVITY=0.0875, JUMP_FORCE=-3.25, max_height_tiles=3, max_width_tiles=5 |
| `src/core/tuning.py` | Loader + mutation API + PEP 562 + atomic save + bake CLI | VERIFIED | 297 lines. load/set_value/save/reset/get_baseline/get_group/bake_derived/__getattr__ all present and behave per spec. `os.replace` atomic save; "Duplicate tuning leaf" D-15 raise; no mtime/watchdog/FileSystemEvent references. CLI `python -m src.core.tuning bake` works. |
| `src/core/constants.py` | <40-line compat shim re-exporting tuning.*, with HAZARD_DRAIN_RATES int-key fix-up | VERIFIED | 27 lines. Contains `from src.core.tuning import *`, `from src.core import tuning as _tuning`, and `HAZARD_DRAIN_RATES = {int(k): v for k, v in _tuning.HAZARD_DRAIN_RATES.items()}`. No scalar redefinitions. All 12 legacy callers import cleanly through it. |
| `tests/test_tuning.py` | ≥11 named tests covering load/set_value/reset/uniqueness/bake/save/compat-shim | VERIFIED | 236 lines, exactly 11 tests with required names. `python -m pytest tests/test_tuning.py -q` → 11 passed in 0.12s. Three FND-gate tests pass individually in isolation. |
| `CONVERTER-HANDOFF.md` | New Section 5 with v0.2.0 → v0.3.0 migration table; Sections 1-4 preserved | VERIFIED | 186 lines. Section 5 at line 112 contains migration table, tuning/derived explanation, bake CLI, name-uniqueness invariant, staleness note. Line 1 still "# v1.3 Migration Handoff: 16x16 Tile Migration" (Sections 1-4 preserved). |
| `.planning/REQUIREMENTS.md` | FND-04 revised to set_value visibility wording | VERIFIED | Line 16: "FND-04: Mutations via `tuning.set_value()` are visible to subsequent reads in the same process (verified via unit test). File-watch hot-reload is not implemented..." FND-01/02/03/05/06 unchanged. Traceability row FND-04 → Phase 24 preserved. |
| `.planning/ROADMAP.md` | Phase 24 goal/success-criterion #2 revised | VERIFIED | Goal line 81: "loader that exposes a mutation API (`set_value`/`save`/`reset`/`bake_derived`)". Criterion #2 line 86 references `tests/test_tuning.py::test_set_value_visibility`. Phase one-liner line 64 says "mutation API, compat shim, and converter handoff update". |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `tuning.GRAVITY` flat access | `_model['movement']['GRAVITY']` | PEP 562 `__getattr__` + `_flat_index` | WIRED | Live test: `tuning.GRAVITY` returns 0.0875. `_flat_index['GRAVITY'] == 'movement'`. |
| `set_value('GRAVITY', x)` mutation | subsequent `tuning.GRAVITY` read | `_model[_flat_index[key]][key] = value` | WIRED | `test_set_value_visibility` passes; live spot-check confirms 0.09 round-trip with `get_baseline` returning untouched 0.0875. |
| `src.core.constants.GRAVITY` import | `src.core.tuning.GRAVITY` | `from src.core.tuning import *` wildcard + `__all__` sort | WIRED | `python -c "from src.core.constants import GRAVITY; print(GRAVITY)"` → 0.0875. 12/12 legacy callers import cleanly. |
| `constants.HAZARD_DRAIN_RATES[6]` (int key) | `tuning.HAZARD_DRAIN_RATES["6"]` (str key) | post-import dict comprehension rebuild | WIRED | Live test: `constants.HAZARD_DRAIN_RATES[6] == 0.25`. `test_hazard_drain_rates_int_keys` passes. |
| `bake_derived()` | `_raw['derived']['jump']` numeric fields | Euler integration over `_model['movement']` values | WIRED (with drift) | `test_bake_derived_determinism` passes: max_height_tiles=3, max_width_tiles=5 match schema. Underlying max_width_px drifts 84 vs 89 (deferred to Phase 36). |
| `save()` | `physics-schema.json` | `os.replace` after temp-file + fsync | WIRED | `os.replace` grep match; CLI `python -m src.core.tuning bake` wrote and restored schema; `test_atomic_save_round_trip` passes. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Tuning loader module imports | `python -c "from src.core import tuning; assert tuning.GRAVITY == 0.0875"` | GRAVITY=0.0875 | PASS |
| Set/get/reset round-trip | `python -c "... set_value(0.09); assert 0.09; reset; assert 0.0875"` | All asserts pass | PASS |
| Compat shim import | `python -c "import src.core.constants"` | exits 0 | PASS |
| All 12 legacy callers import | single `import ...` statement on 12 modules | all succeed | PASS |
| Main entry-point imports | `python -c "import main"` | main imports OK | PASS |
| Unit tests (Phase 24) | `python -m pytest tests/test_tuning.py -q` | 11 passed in 0.12s | PASS |
| FND-gate tests individually | `pytest test_set_value_visibility test_bake_derived_determinism test_compat_shim_smoke` | 3 passed | PASS |
| Full test suite (ex. pre-existing ldtk failure) | `python -m pytest -q --ignore=tests/test_ldtk_migration.py` | 356 passed, 3 skipped | PASS |
| Bake CLI round-trip | `python -m src.core.tuning bake` | "baked derived.* and saved to ..." then `git checkout` restored to 89 | PASS |
| Schema parseable + shape invariants | `python -c "import json; ... version=='0.3.0'; 22 groups; 87 unique leaves"` | all asserts pass | PASS |
| Duplicate flat-key rejected at load | `test_name_uniqueness_raises` synthetic schema | ValueError "Duplicate tuning leaf" raised | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FND-01 | 24-02 | `physics-schema.json` promoted to source of truth; restructured into `tuning.*` + `derived.*`; game boots with v1.3-identical values | SATISFIED (partial: human gameplay check pending) | Schema verified v0.3.0 with 22 tuning groups (87 unique leaves) and 5 derived blocks, all numeric values match v1.3. The "boots with values identical to v1.3" partial-human gate is tied to Success Criterion 1. |
| FND-02 | 24-03 | `src/core/tuning.py` loads schema, exposes values via PEP 562 `__getattr__`, supports `set_value()` in-memory mutation, atomic disk writes | SATISFIED | tuning.py 297 lines with all API; tests 1-9 in test_tuning.py pass; `os.replace` atomic save verified. |
| FND-03 | 24-04 | `src/core/constants.py` rewritten as passthrough compat shim | SATISFIED | constants.py 27 lines; wildcard re-export + HAZARD_DRAIN_RATES fix-up. All 12 legacy callers import cleanly. `test_compat_shim_smoke` passes. |
| FND-04 | 24-01, 24-05 | Mutations via `tuning.set_value()` visible to subsequent reads in-process (unit-test verified); file-watch hot-reload NOT implemented | SATISFIED | Revised wording present in REQUIREMENTS.md and ROADMAP.md. `test_set_value_visibility` passes (the named acceptance test). No mtime/watchdog/FileSystemEvent in tuning.py. |
| FND-06 | 24-05, 24-06 | Converter contract smoke test verifies restructured schema parseable; CONVERTER-HANDOFF.md updated | SATISFIED | CONVERTER-HANDOFF.md Section 5 appended with migration table and bake CLI. `test_bake_derived_determinism` passes (max_height_tiles=3, max_width_tiles=5 against v1.3 baseline — formal smoke test). |

No orphaned requirements for Phase 24.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/core/tuning.py` | 142-156 | `reset(None)` rebinds `_raw['tuning']` but does not reset `_raw['derived']` — bake→reset→save sequence would serialise mismatched derived | Warning | WR-01 from 24-REVIEW.md. Advisory; not triggered by any current call site; Phase 28 panel will use this path. |
| `src/core/tuning.py` | 130-162, 165-184, 227-262 | `set_value`/`reset`/`save`/`bake_derived` do not guard `_model is None` | Warning | WR-02 from 24-REVIEW.md. Advisory; unreachable in normal flow due to eager auto-load at line 284. |
| `src/core/tuning.py` | 206-224 | `_euler_jump_airtime` can infinite-loop if GRAVITY <= 0 or fall_mult <= 0 | Warning | WR-03 from 24-REVIEW.md. Advisory; would require a corrupt-value schema or bad panel edit to trigger. |
| `src/core/tuning.py` | 46, 67 | `_SUPPORTED_SCHEMA_MAJOR = "0.3"` + startswith accepts `0.30.x` | Info | IN-01 advisory. |
| `assets/physics-schema.json` | 6-11 vs 11-12 | Top-level `tile_size=16` and `fps=60` duplicate `tuning.tile.TILE_SIZE` / no `fps` counterpart | Info | IN-02 advisory; cross-check would catch drift. |
| `assets/physics-schema.json` | 27-30 | `HAZARD_DRAIN_SLOW/MEDIUM/FAST` scalars duplicate `HAZARD_DRAIN_RATES` dict values | Info | IN-03 advisory; panel edit to one would not propagate. |
| `src/core/tuning.py` | 68-72 | Error message hard-codes "Likely a stale v0.2.0 schema" hint | Info | IN-04 advisory. |
| `src/core/constants.py` | 26 | `HAZARD_DRAIN_RATES` dict-comprehension would raise on non-digit keys | Info | IN-05 advisory. |

All 8 findings are advisory (0 critical / 3 warning / 5 info) per 24-REVIEW.md. None block goal achievement.

### Human Verification Required

### 1. v1.3 Frame-for-Frame Parity Spot-Check

**Test:** Boot the game from the current HEAD (`python main.py`). Play through a short segment that exercises the core movement verbs — run, jump, wall jump, drill dive, ram, charge shot. Compare "feel" to an v1.3 reference build.

**Expected:**
- Walk speed caps at ~1.25 px/frame (crosses a 5-tile gap in ~64 frames)
- Jump peak reaches 3 tiles above take-off
- Fall acceleration visibly asymmetric (snappier descent than ascent)
- Drill dive descends at ~2.0 px/frame
- Ram crosses the screen at ~2.5 px/frame
- Charge shot windup frames feel unchanged
- No visual/audio/input regressions vs v1.3

**Why human:** Frame-for-frame gameplay parity is tactile and cannot be verified by unit tests without a recorded-input fixture, which Phase 24 did not produce. The numeric values are proven to flow correctly from schema to runtime (all tests pass; 356/356 non-ldtk tests pass), but "identical play feel" requires a pyxel window and a controller.

### Gaps Summary

No blocker gaps. All plan-level artifacts exist, are substantive, are wired, and data flows from schema → loader → compat shim → 12 legacy callers without drift. The only outstanding item is ROADMAP Success Criterion #1's "plays identically to v1.3 frame-for-frame" tactile gate, which is inherently a human check.

One deferred item: `bake_derived().max_width_px` computes 84 where the schema authors 89. Both floor to `max_width_tiles = 5`, so all automated tests and the FND-06 smoke test pass, and the phase's functional parity is intact. Plan 24-03 SUMMARY documents this as a Rule-4 architectural observation reserved for Phase 36's preset-bake reconciliation.

Cross-phase regressions introduced by Phase 24 (test_cracked_v, test_phase22, test_sprite_scale) were repaired in commit `4c13c56` (verified in `git log`). The unrelated pre-existing failure `test_ldtk_migration::test_tileset_relpath_cavern` remains and is correctly identified in the prompt as out-of-scope.

---

_Verified: 2026-04-11_
_Verifier: Claude (gsd-verifier)_
