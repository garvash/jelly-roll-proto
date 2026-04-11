---
phase: 24-tuning-foundation-schema-inversion
reviewed: 2026-04-11T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - src/core/tuning.py
  - src/core/constants.py
  - tests/test_tuning.py
  - assets/physics-schema.json
findings:
  critical: 0
  warning: 3
  info: 5
  total: 8
status: issues_found
---

# Phase 24: Code Review Report

**Reviewed:** 2026-04-11
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Phase 24 performs a clean source-of-truth inversion: `assets/physics-schema.json`
is now canonical, `src/core/tuning.py` is a small, well-documented PEP 562
loader with an explicit mutation/save/bake API, and `src/core/constants.py`
collapses to a 27-line compat shim. The design is internally consistent with
the documented D-01 through D-18 decisions, and the 11 unit tests cover the
FND-03/04/06 acceptance criteria, D-04 baseline semantics, D-15 name uniqueness,
and the HAZARD_DRAIN_RATES int-key fix-up.

No security issues, no hardcoded secrets, no dangerous function usage, and no
debug artifacts. Atomic save uses the correct temp-file + fsync + os.replace
idiom. Tests avoid magic numbers per the project-memory rule.

Three warnings relate to mutation-API robustness and semantic sharp edges
(stale derived values after reset, missing sentinel checks in the mutation
path, a lenient schema-version check). Five info items flag minor API
ergonomics and schema duplication.

## Warnings

### WR-01: `reset(None)` leaves stale `derived.*` in `_raw`, so a following `save()` serialises baked values that no longer match the restored tuning

**File:** `src/core/tuning.py:142-156`
**Issue:** Full reset rebinds `_raw["tuning"] = copy.deepcopy(_baseline)` and
re-points `_model`, but never touches `_raw["derived"]`. If an operator runs
`bake_derived()` -> `reset()` -> `save()`, the on-disk schema will end up with
`tuning.*` at the baseline values while `derived.jump.max_height_tiles` (etc.)
still reflects the post-bake numbers from the previous mutation session. The
converter then reads internally inconsistent derived values.

This is not caught by any test because `test_bake_derived_determinism` calls
`reset()` *before* `bake_derived()`, not after, and `test_atomic_save_round_trip`
never bakes.

**Fix:** Either snapshot `_raw["derived"]` alongside `_baseline` at load time
and restore it here, or document explicitly that `reset()` does not revert
derived values and require callers to re-bake before saving. Minimal code
change:
```python
# in load():
global _derived_baseline
_derived_baseline = copy.deepcopy(_raw.get("derived", {}))

# in reset(key=None) full-reset branch:
_raw["tuning"] = copy.deepcopy(_baseline)
_raw["derived"] = copy.deepcopy(_derived_baseline)
_model = _raw["tuning"]
```

### WR-02: `set_value`, `reset`, `save`, and `bake_derived` do not guard against `_model is None`, producing a confusing `TypeError` if ever called pre-load

**File:** `src/core/tuning.py:130-162, 165-184, 227-262`
**Issue:** `__getattr__` correctly raises
`RuntimeError("tuning.load() has not been called")` when `_model is None`,
but none of the mutation or persistence functions do. In normal operation
this is unreachable because `load()` runs eagerly at import (line 284), but
a test that monkey-patches `_model = None`, or a future refactor that drops
the eager load, will get an opaque `TypeError: 'NoneType' object is not
subscriptable` from `_model[_flat_index[key]]` instead of the intended
lifecycle error.

**Fix:** Hoist the sentinel check into a small helper and reuse it:
```python
def _require_loaded() -> None:
    if _model is None:
        raise RuntimeError("tuning.load() has not been called")

def set_value(key: str, value) -> None:
    _require_loaded()
    if key not in _flat_index:
        raise KeyError(f"unknown tuning key {key!r} (not in _flat_index)")
    _model[_flat_index[key]][key] = value
```
Apply the same call at the top of `reset`, `save`, `bake_derived`,
`get_group`, and `get_baseline`.

### WR-03: `_euler_jump_airtime` will infinite-loop if `gravity <= 0` or `fall_mult <= 0`

**File:** `src/core/tuning.py:206-224`
**Issue:** The ascent loop terminates only when `vy >= 0`, reached by
`vy += gravity`. If a panel edit (or a corrupt schema) sets `GRAVITY = 0`
or negative, the ascent loop never exits. The descent loop has the same
failure mode if `gravity * fall_mult <= 0`. Because `bake_derived` is a
CLI-invoked operation (`python -m src.core.tuning bake`), a bad tuning
value would hang the CLI without any feedback.

The existing D-15 / set_value key-validation guards against typos, but
there is no value-range validation and the schema has no JSON Schema
`minimum` constraint on `GRAVITY`.

**Fix:** Add a precondition check at the top of `bake_derived`:
```python
if gravity <= 0:
    raise ValueError(f"bake_derived: GRAVITY must be > 0, got {gravity}")
if fall_mult <= 0:
    raise ValueError(
        f"bake_derived: FALLING_GRAVITY_MULTIPLIER must be > 0, got {fall_mult}"
    )
if jump_force >= 0:
    raise ValueError(
        f"bake_derived: JUMP_FORCE must be negative (upward), got {jump_force}"
    )
```
Or, defensively, bound the simulation with a frame cap (e.g. `1 << 16`)
and raise if exceeded.

## Info

### IN-01: `_SUPPORTED_SCHEMA_MAJOR = "0.3"` + `startswith` accepts `"0.30.0"` as a match

**File:** `src/core/tuning.py:46, 67`
**Issue:** `"0.30.0".startswith("0.3")` evaluates to `True`, so a future
bump to a real 0.30 series would silently pass the v0.3.x gate. This is
unlikely to happen but is a classic prefix-matching trap and the docstring
explicitly frames the check as "0.3.x".
**Fix:** `version.startswith(_SUPPORTED_SCHEMA_MAJOR + ".")` (i.e. compare
against `"0.3."`), or parse the version with `packaging.version.Version`
and compare major/minor numerically.

### IN-02: Redundant tile size / FPS between schema top-level and `tuning.tile`

**File:** `assets/physics-schema.json:6-11`
**Issue:** The schema declares `"fps": 60` and `"tile_size": 16` at the top
level (read by the converter) and also `tuning.tile.TILE_SIZE: 16` (read by
the game). Nothing enforces agreement; an operator tuning `TILE_SIZE` via
the Phase 28 panel would leave the top-level `tile_size` stale, and
`bake_derived` uses only the tuning-side value. Same for `fps` (no
corresponding `tuning.*` entry today).
**Fix:** Either drop the top-level duplicates and have the converter read
`tuning.tile.TILE_SIZE`, or add a load-time cross-check:
```python
if _raw.get("tile_size") != _model["tile"]["TILE_SIZE"]:
    raise ValueError("schema top-level tile_size != tuning.tile.TILE_SIZE")
```

### IN-03: `HAZARD_DRAIN_SLOW/MEDIUM/FAST` scalars duplicate values inside `HAZARD_DRAIN_RATES`

**File:** `assets/physics-schema.json:27-30`
**Issue:** `hazards` exposes both three named scalars (`HAZARD_DRAIN_SLOW=0.25`,
`HAZARD_DRAIN_MEDIUM=0.75`, `HAZARD_DRAIN_FAST=1.5`) and the lookup dict
`HAZARD_DRAIN_RATES: {"6": 0.25, "7": 0.75, "8": 1.5}` with the same values.
A panel edit to one will not propagate to the other, and the compat shim's
int-key rebuild runs only once at import time, so later mutations of
`HAZARD_DRAIN_RATES` on `tuning` will not be reflected in
`constants.HAZARD_DRAIN_RATES` either.
**Fix:** Pick one representation. If the IntGrid-id dict is canonical,
remove the three named scalars; if the named scalars are canonical, compute
the dict in the compat shim (or in `bake_derived`) from them.

### IN-04: Schema-version error message is stale-to-a-specific-prior-version

**File:** `src/core/tuning.py:68-72`
**Issue:** The error message hard-codes "Likely a stale v0.2.0 schema that
was never migrated to the v0.3.0 tuning.* layout." That was true during the
Phase 24 migration but will be misleading the next time the schema majors,
since a v0.4.x schema will also hit this branch.
**Fix:** Drop the version-specific hint, or parameterise it:
```python
raise ValueError(
    f"Unsupported physics-schema version {version!r} at {path}; "
    f"loader supports {_SUPPORTED_SCHEMA_MAJOR}.x only."
)
```

### IN-05: `HAZARD_DRAIN_RATES` rebuild in the compat shim mutates a module-global at import time without guarding non-string keys

**File:** `src/core/constants.py:26`
**Issue:** `{int(k): v for k, v in _tuning.HAZARD_DRAIN_RATES.items()}` will
raise `ValueError` if any key is non-numeric (e.g. a future migration adds
a named hazard). There is no test that exercises a corrupt-key path; the
existing `test_hazard_drain_rates_int_keys` only asserts the happy path.
**Fix:** Either tighten the schema to enforce digit-only keys, or make the
rebuild defensive:
```python
HAZARD_DRAIN_RATES = {
    int(k) if k.isdigit() else k: v
    for k, v in _tuning.HAZARD_DRAIN_RATES.items()
}
```
Low priority; flagged because it is the one location in the compat shim
that diverges from pure re-export.

---

_Reviewed: 2026-04-11_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
