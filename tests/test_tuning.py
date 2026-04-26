"""Phase 24 Plan 05 — Unit tests for the tuning loader, mutation API, baseline,
name-uniqueness invariant, derived-value bake, and the constants.py compat shim.

These tests are the quality gate for Phase 24:

* ``test_set_value_visibility`` is the FND-04 (revised) acceptance criterion —
  in-process mutation must be visible to subsequent reads.
* ``test_bake_derived_determinism`` is the FND-06 smoke test — baking against
  the v1.3 baseline must reproduce the hand-baked
  ``derived.jump.max_height_tiles`` / ``max_width_tiles`` values.
* ``test_compat_shim_smoke`` is the FND-03 safety net — the 12 legacy caller
  modules must import cleanly through ``src.core.constants``.
* ``test_name_uniqueness_raises`` enforces D-15 at load time.
* ``test_baseline_reset_*`` enforces D-04.
* ``test_hazard_drain_rates_int_keys`` guards the Plan 04 JSON int-key
  impedance fix.

All 11 tests must pass under ``python -m pytest tests/test_tuning.py -q``.
"""

import importlib
import json
from pathlib import Path

import pytest

from src.core import tuning

# --- v1.3 baseline expected values (D-12; no magic numbers per project memory) --
EXPECTED_GRAVITY = 0.0875
EXPECTED_JUMP_FORCE = -3.25
EXPECTED_MAX_WALK_SPEED = 1.25
EXPECTED_MAX_HEIGHT_TILES = 3  # v1.3 hand-baked per D-12 / FND-06
EXPECTED_MAX_WIDTH_TILES = 5   # v1.3 hand-baked per D-12 / FND-06
EXPECTED_SAVE_FILE = "save.json"
EXPECTED_HAZARD_DRAIN_SLOW = 0.25   # HAZARD_DRAIN_RATES[6]
EXPECTED_HAZARD_DRAIN_MEDIUM = 0.75  # HAZARD_DRAIN_RATES[7]
EXPECTED_HAZARD_DRAIN_FAST = 1.5    # HAZARD_DRAIN_RATES[8]
EXPECTED_HAZARD_KEY_SLOW = 6
EXPECTED_HAZARD_KEY_MEDIUM = 7
EXPECTED_HAZARD_KEY_FAST = 8
MIN_FLAT_LEAVES = 50  # covers all ~60 constants.py leaves (actual: 87)
MUTATED_GRAVITY_A = 0.123
MUTATED_GRAVITY_B = 0.5
MUTATED_GRAVITY_C = 0.111
MUTATED_JUMP_FORCE = -5.0
ROUND_TRIP_GRAVITY_FROM_BAD_SCHEMA_A = 0.1
ROUND_TRIP_GRAVITY_FROM_BAD_SCHEMA_B = 0.2

# --- Legacy callers covered by FND-03 compat-shim smoke test ------------------
LEGACY_CALLERS = [
    "src.entities.boss",
    "src.entities.slime",
    "src.entities.enemies",
    "src.entities.effects",
    "src.entities.player",
    "src.entities.save_point",
    "src.entities.items",
    "src.entities.projectile",
    "src.level.map",
    "src.level.world",
    "src.core.save_manager",
    "src.core.sprite_utils",
]


@pytest.fixture(autouse=True)
def _reload_tuning():
    """Ensure every test starts with a pristine baseline.

    ``tuning.load()`` is idempotent and re-reads the on-disk schema, re-taking
    the baseline. We also ``reset()`` afterward in case a test mutated values
    without cleaning up (T-24-19 mitigation).
    """
    tuning.load()
    yield
    tuning.load()  # defensive: some tests swap the schema path
    tuning.reset()


# 1. --------------------------------------------------------------------------
def test_load_round_trip():
    """Loader reads assets/physics-schema.json and populates _model/_baseline."""
    schema_path = Path("assets/physics-schema.json")
    with open(schema_path, encoding="utf-8") as f:
        raw = json.load(f)

    assert tuning._model["movement"]["GRAVITY"] == raw["tuning"]["movement"]["GRAVITY"]
    assert len(tuning.__all__) > MIN_FLAT_LEAVES
    # D-04: baseline is a deepcopy, not an alias to _model.
    assert tuning._baseline is not tuning._model


# 2. --------------------------------------------------------------------------
def test_pep562_flat_access():
    """PEP 562 __getattr__ exposes every flat leaf at the module level.

    Plan 31.5-05 dropped the `assert tuning.RAM_INVINCIBLE is True` line;
    the `slime_ram` tuning group was deleted in Plan 03 per CONTEXT D-01,
    so the key now raises AttributeError instead. Surviving assertions
    cover the v1.3 baseline values + the missing-key error path.
    """
    assert tuning.GRAVITY == EXPECTED_GRAVITY
    assert tuning.JUMP_FORCE == EXPECTED_JUMP_FORCE
    assert tuning.MAX_WALK_SPEED == EXPECTED_MAX_WALK_SPEED
    assert tuning.SAVE_FILE == EXPECTED_SAVE_FILE
    # Exercises the __getattr__ raise path (W-2).
    with pytest.raises(AttributeError, match="NOT_A_KEY"):
        tuning.NOT_A_KEY  # noqa: B018 — intentional attribute lookup


# 3. --------------------------------------------------------------------------
def test_set_value_visibility():
    """FND-04 (revised): set_value() mutations are visible to subsequent reads.

    This test IS the FND-04 revised acceptance criterion.
    """
    tuning.set_value("GRAVITY", MUTATED_GRAVITY_A)
    assert tuning.GRAVITY == MUTATED_GRAVITY_A
    # Baseline is untouched (D-04).
    assert tuning.get_baseline("GRAVITY") == EXPECTED_GRAVITY
    # Group index is queryable for panel tab placement (D-14).
    assert tuning.get_group("GRAVITY") == "movement"


# 4. --------------------------------------------------------------------------
def test_baseline_reset_single_key():
    """reset(key) restores a single leaf from _baseline (D-04)."""
    tuning.set_value("GRAVITY", MUTATED_GRAVITY_B)
    tuning.reset("GRAVITY")
    assert tuning.GRAVITY == EXPECTED_GRAVITY


# 5. --------------------------------------------------------------------------
def test_baseline_reset_all():
    """reset() with no argument restores every leaf from _baseline (D-04)."""
    tuning.set_value("GRAVITY", MUTATED_GRAVITY_B)
    tuning.set_value("JUMP_FORCE", MUTATED_JUMP_FORCE)
    tuning.reset()
    assert tuning.GRAVITY == EXPECTED_GRAVITY
    assert tuning.JUMP_FORCE == EXPECTED_JUMP_FORCE


# 6. --------------------------------------------------------------------------
def test_set_value_unknown_key_raises():
    """set_value() rejects arbitrary keys (D-15 / T-24-10)."""
    with pytest.raises(KeyError):
        tuning.set_value("NOT_A_KEY", 1)


# 7. --------------------------------------------------------------------------
def test_name_uniqueness_raises(tmp_path):
    """D-15: duplicate flat leaf across groups raises at load time."""
    bad = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "conflict",
        "description": "intentional duplicate for name-uniqueness test",
        "version": "0.3.0",
        "updated": "test",
        "fps": 60,
        "tile_size": 16,
        "tuning": {
            "movement": {"GRAVITY": ROUND_TRIP_GRAVITY_FROM_BAD_SCHEMA_A},
            "slime_juice": {"GRAVITY": ROUND_TRIP_GRAVITY_FROM_BAD_SCHEMA_B},  # duplicate leaf
        },
        "derived": {},
    }
    bad_path = tmp_path / "bad-schema.json"
    bad_path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate tuning leaf"):
        tuning.load(schema_path=bad_path)
    tuning.load()  # restore real schema for subsequent tests


# 8. --------------------------------------------------------------------------
def test_bake_derived_determinism():
    """FND-06: bake_derived() against v1.3 baseline reproduces hand-baked tiles.

    This test IS the FND-06 smoke test.
    """
    tuning.reset()
    tuning.bake_derived()
    assert tuning._raw["derived"]["jump"]["max_height_tiles"] == EXPECTED_MAX_HEIGHT_TILES
    assert tuning._raw["derived"]["jump"]["max_width_tiles"] == EXPECTED_MAX_WIDTH_TILES


# 9. --------------------------------------------------------------------------
def test_atomic_save_round_trip(tmp_path):
    """save() + load() round-trips a mutated value; reload takes a fresh baseline (D-05)."""
    target = tmp_path / "round-trip-schema.json"
    # Seed target with a copy of the real schema so the loader version check passes.
    real = Path("assets/physics-schema.json").read_text(encoding="utf-8")
    target.write_text(real, encoding="utf-8")

    tuning.load(schema_path=target)
    tuning.set_value("GRAVITY", MUTATED_GRAVITY_C)
    tuning.save(schema_path=target)

    assert target.exists()

    tuning.load(schema_path=target)
    assert tuning.GRAVITY == MUTATED_GRAVITY_C
    # D-05: restart = fresh baseline.
    assert tuning.get_baseline("GRAVITY") == MUTATED_GRAVITY_C

    tuning.load()  # restore real schema path


# 10. -------------------------------------------------------------------------
def test_compat_shim_smoke():
    """FND-03 safety net: all 12 legacy caller modules import cleanly.

    This is a module-import smoke test, not a runtime test — we do NOT
    instantiate any game objects. If a module has a side-effectful top-level
    block that crashes (e.g. requires ``pyxel.init()``), the AssertionError
    names the offending module so the executor can triage without silently
    skipping (T-24-20 mitigation).
    """
    for mod in LEGACY_CALLERS:
        try:
            importlib.import_module(mod)
        except Exception as exc:  # noqa: BLE001 — re-raised as AssertionError with context
            raise AssertionError(
                f"compat shim smoke test: failed to import {mod!r} "
                f"({type(exc).__name__}: {exc})"
            ) from exc


# 11. -------------------------------------------------------------------------
def test_hazard_drain_rates_int_keys():
    """Plan 04 fix-up: HAZARD_DRAIN_RATES is indexed with int keys, not strings.

    JSON serialization stringifies the dict's int keys; the compat shim
    rebuilds it with int keys so legacy callers can index with IntGrid IDs.
    """
    from src.core.constants import HAZARD_DRAIN_RATES

    assert HAZARD_DRAIN_RATES[EXPECTED_HAZARD_KEY_SLOW] == EXPECTED_HAZARD_DRAIN_SLOW
    assert HAZARD_DRAIN_RATES[EXPECTED_HAZARD_KEY_MEDIUM] == EXPECTED_HAZARD_DRAIN_MEDIUM
    assert HAZARD_DRAIN_RATES[EXPECTED_HAZARD_KEY_FAST] == EXPECTED_HAZARD_DRAIN_FAST
