---
phase: 24-tuning-foundation-schema-inversion
plan: 05
type: execute
wave: 4
depends_on: [24-04]
files_modified:
  - tests/test_tuning.py
autonomous: true
requirements:
  - FND-02
  - FND-04
  - FND-06
tags: [tests, pytest, loader, baseline, compat-shim, smoke]
must_haves:
  truths:
    - "tests/test_tuning.py exists and every test passes under pytest"
    - "test_load_round_trip proves schema → loader → save → re-load preserves all values"
    - "test_set_value_visibility proves FND-04 revised: in-process mutation is visible to subsequent reads"
    - "test_baseline_reset proves reset() restores _model from _baseline"
    - "test_name_uniqueness_raises proves D-15 invariant is enforced at load time"
    - "test_bake_derived_determinism proves FND-06: v1.3 baseline → bake_derived → matches current derived.jump values (max_height_tiles=3, max_width_tiles=5)"
    - "test_compat_shim_smoke proves all 12 legacy caller files import cleanly"
    - "test_set_value_unknown_key_raises proves D-15 rejects arbitrary keys"
    - "test_atomic_save_round_trip proves save() + load() is value-stable"
  artifacts:
    - path: "tests/test_tuning.py"
      provides: "Unit + smoke test coverage for Phase 24 loader, mutation API, and compat shim"
      min_lines: 150
      contains: "def test_set_value_visibility"
  key_links:
    - from: "tests/test_tuning.py::test_bake_derived_determinism"
      to: "src/core/tuning.py bake_derived()"
      via: "reset to baseline → bake → assert derived.jump.max_height_tiles == 3"
      pattern: "max_height_tiles.*3"
    - from: "tests/test_tuning.py::test_compat_shim_smoke"
      to: "the 12 legacy caller files"
      via: "importlib.import_module in a loop"
      pattern: "src\\.entities\\.player"
---

<objective>
Write `tests/test_tuning.py` with the full Phase 24 test set covering the loader, mutation API, baseline, name-uniqueness invariant, bake_derived determinism, and the compat shim's legacy-caller smoke test.

Purpose: Lock in FND-02, FND-04 (revised), and FND-06 with pytest. The set_value visibility test IS the FND-04 acceptance criterion; the bake_derived determinism test IS the FND-06 smoke test; the compat shim loop IS the FND-03 safety net. If these tests pass, Phase 24 is verifiable.

Output: `tests/test_tuning.py` with ≥9 named tests, all green under `pytest tests/test_tuning.py -q`.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@src/core/tuning.py
@src/core/constants.py
@assets/physics-schema.json
@.planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md

<interfaces>
<!-- Pytest layout. All tests are in a single file because the loader is a single module. -->

File: tests/test_tuning.py

Imports (top of file):
  import copy
  import importlib
  import json
  import os
  import tempfile
  from pathlib import Path
  import pytest
  from src.core import tuning

Fixtures:
  @pytest.fixture(autouse=True)
  def _reload_tuning():
      """Ensure every test starts with a pristine baseline. tuning.load() is idempotent
      and re-reads the on-disk schema, re-taking the baseline. We also reset() afterward
      in case a test mutated values without cleaning up."""
      tuning.load()
      yield
      tuning.reset()

Tests to include (exact names — executor MUST use these; the acceptance criteria pin them):

  1. test_load_round_trip
     - Reads assets/physics-schema.json directly with json.load
     - Asserts tuning._model['movement']['GRAVITY'] == raw['tuning']['movement']['GRAVITY']
     - Asserts len(tuning.__all__) > 50 (covers all ~60 constants.py leaves)
     - Asserts tuning._baseline is not tuning._model (deepcopy, not alias)

  2. test_pep562_flat_access
     - Asserts tuning.GRAVITY == 0.0875
     - Asserts tuning.JUMP_FORCE == -3.25
     - Asserts tuning.MAX_WALK_SPEED == 1.25
     - Asserts tuning.RAM_INVINCIBLE is True
     - Asserts tuning.SAVE_FILE == 'save.json'
     - Asserts getattr(tuning, 'NOT_A_KEY', None) is None  (AttributeError path returns sentinel)

  3. test_set_value_visibility   # <-- THIS IS FND-04 (revised)
     - tuning.set_value('GRAVITY', 0.123)
     - Asserts tuning.GRAVITY == 0.123
     - Asserts tuning.get_baseline('GRAVITY') == 0.0875   (baseline untouched)
     - Asserts tuning.get_group('GRAVITY') == 'movement'

  4. test_baseline_reset_single_key
     - tuning.set_value('GRAVITY', 0.5)
     - tuning.reset('GRAVITY')
     - Asserts tuning.GRAVITY == 0.0875

  5. test_baseline_reset_all
     - tuning.set_value('GRAVITY', 0.5)
     - tuning.set_value('JUMP_FORCE', -5.0)
     - tuning.reset()
     - Asserts tuning.GRAVITY == 0.0875
     - Asserts tuning.JUMP_FORCE == -3.25

  6. test_set_value_unknown_key_raises
     - pytest.raises(KeyError): tuning.set_value('NOT_A_KEY', 1)

  7. test_name_uniqueness_raises
     - Writes a temp schema file containing two groups that both define 'GRAVITY'
     - Calls tuning.load(schema_path=<temp path>)
     - pytest.raises(ValueError, match="Duplicate tuning leaf"): ...
     - Finally calls tuning.load() (no arg) to restore real schema for subsequent tests

  8. test_bake_derived_determinism   # <-- THIS IS FND-06
     - tuning.reset()
     - tuning.bake_derived()
     - Asserts tuning._raw['derived']['jump']['max_height_tiles'] == 3
     - Asserts tuning._raw['derived']['jump']['max_width_tiles'] == 5
     - (These are the v1.3-hand-baked values per D-12; any drift means bake_derived is broken
       or constants.py values drifted from v1.3 baseline — both are phase-failing conditions.)

  9. test_atomic_save_round_trip
     - Creates a tempfile target path
     - tuning.set_value('GRAVITY', 0.111)
     - tuning.save(schema_path=<temp path>)
     - Asserts the temp path exists
     - Reloads: tuning.load(schema_path=<temp path>)
     - Asserts tuning.GRAVITY == 0.111
     - Asserts tuning.get_baseline('GRAVITY') == 0.111  (reload takes a new baseline — D-05)
     - Finally tuning.load() to restore real schema

 10. test_compat_shim_smoke   # <-- THIS IS FND-03 safety net
     - Loops over all 12 legacy caller module paths:
         'src.entities.boss',
         'src.entities.slime',
         'src.entities.enemies',
         'src.entities.effects',
         'src.entities.player',
         'src.entities.save_point',
         'src.entities.items',
         'src.entities.projectile',
         'src.level.map',
         'src.level.world',
         'src.core.save_manager',
         'src.core.sprite_utils',
     - importlib.import_module(each)
     - No exception means the shim is working. (We do NOT instantiate any game objects — this is
       a module-import smoke test, not a runtime test. Runtime parity is the next executor's job
       via a manual boot-and-play spot-check during the human-verify phase of execute.)

 11. test_hazard_drain_rates_int_keys   # <-- catches the Plan 04 HAZARD_DRAIN_RATES JSON impedance bug
     - from src.core.constants import HAZARD_DRAIN_RATES
     - Asserts HAZARD_DRAIN_RATES[6] == 0.25   (int key, not "6" string)
     - Asserts HAZARD_DRAIN_RATES[7] == 0.75
     - Asserts HAZARD_DRAIN_RATES[8] == 1.5

Total: 11 named tests. If the executor reorders or renames any, the grep-based acceptance checks fail.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Write tests/test_tuning.py with 11 locked tests</name>
  <files>tests/test_tuning.py</files>
  <read_first>
    - src/core/tuning.py (so you're testing the real API surface from Plan 03)
    - src/core/constants.py (compat shim from Plan 04)
    - assets/physics-schema.json (current v0.3.0 — test expectations depend on its values)
    - .planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md (§decisions D-04, D-05, D-12, D-15, D-17)
    - tests/test_physics.py (one existing test file — skim to match pytest style and path conventions)
  </read_first>
  <action>
    Create `tests/test_tuning.py`. Use the Write tool.

    Follow the test list in <interfaces> exactly — 11 tests with the listed names. Pytest style (no unittest.TestCase; just module-level `def test_<name>():` functions).

    Key implementation notes:

    - **Autouse fixture `_reload_tuning`**: call `tuning.load()` (no arg, reads default path) at setup and `tuning.reset()` at teardown, so each test sees a pristine baseline regardless of order.

    - **test_name_uniqueness_raises**: build the conflict schema dynamically:

        def test_name_uniqueness_raises(tmp_path):
            bad = {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "title": "conflict",
                "description": "intentional duplicate for name-uniqueness test",
                "version": "0.3.0",
                "updated": "test",
                "fps": 60,
                "tile_size": 16,
                "tuning": {
                    "movement": {"GRAVITY": 0.1},
                    "slime_juice": {"GRAVITY": 0.2},  # duplicate leaf
                },
                "derived": {}
            }
            bad_path = tmp_path / "bad-schema.json"
            bad_path.write_text(json.dumps(bad))
            with pytest.raises(ValueError, match="Duplicate tuning leaf"):
                tuning.load(schema_path=bad_path)
            tuning.load()  # restore real schema for subsequent tests

    - **test_atomic_save_round_trip** (tmp_path fixture):

        def test_atomic_save_round_trip(tmp_path):
            target = tmp_path / "round-trip-schema.json"
            # Seed target with a copy of the real schema so Plan 03's version check passes on reload
            real = Path("assets/physics-schema.json").read_text(encoding="utf-8")
            target.write_text(real, encoding="utf-8")
            tuning.load(schema_path=target)
            tuning.set_value("GRAVITY", 0.111)
            tuning.save(schema_path=target)
            assert target.exists()
            tuning.load(schema_path=target)
            assert tuning.GRAVITY == 0.111
            assert tuning.get_baseline("GRAVITY") == 0.111  # D-05: restart = fresh baseline
            tuning.load()  # restore real path

    - **test_compat_shim_smoke**:

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

        def test_compat_shim_smoke():
            for mod in LEGACY_CALLERS:
                importlib.import_module(mod)   # raises on failure; bare call is the assertion

      If any of the 12 modules have a side-effectful top-level block that requires a pyxel
      window (which boss.py may or may not have), wrap each import in a try/except ImportError
      → re-raise AS AssertionError with the module name — DO NOT silently skip. If a side effect
      like `pyxel.init()` crashes at import, that's a pre-existing Phase 24-adjacent bug; report
      it in the task output and flag it for the executor. Do not try to fix it in this plan.

    - Use module-level constants for the 12 legacy callers and the expected v1.3 values
      (no magic numbers, per the memory note "Avoid magic numbers"):
          EXPECTED_GRAVITY = 0.0875
          EXPECTED_JUMP_FORCE = -3.25
          EXPECTED_MAX_HEIGHT_TILES = 3  # v1.3 hand-baked per D-12
          EXPECTED_MAX_WIDTH_TILES = 5   # v1.3 hand-baked per D-12

    Do NOT:
    - parametrize tests (keeps grep-based acceptance checks simple)
    - add integration tests that run pyxel — this is a unit-test file
    - mock anything in tuning.py — tests exercise the real loader against the real schema
    - modify tests/conftest.py or any other test file
    - add tests beyond the 11 listed (scope creep)
  </action>
  <verify>
    <automated>python -m pytest tests/test_tuning.py -q</automated>
  </verify>
  <acceptance_criteria>
    - `test -f tests/test_tuning.py` exits 0
    - `grep -q "def test_load_round_trip" tests/test_tuning.py` exits 0
    - `grep -q "def test_pep562_flat_access" tests/test_tuning.py` exits 0
    - `grep -q "def test_set_value_visibility" tests/test_tuning.py` exits 0
    - `grep -q "def test_baseline_reset_single_key" tests/test_tuning.py` exits 0
    - `grep -q "def test_baseline_reset_all" tests/test_tuning.py` exits 0
    - `grep -q "def test_set_value_unknown_key_raises" tests/test_tuning.py` exits 0
    - `grep -q "def test_name_uniqueness_raises" tests/test_tuning.py` exits 0
    - `grep -q "def test_bake_derived_determinism" tests/test_tuning.py` exits 0
    - `grep -q "def test_atomic_save_round_trip" tests/test_tuning.py` exits 0
    - `grep -q "def test_compat_shim_smoke" tests/test_tuning.py` exits 0
    - `grep -q "def test_hazard_drain_rates_int_keys" tests/test_tuning.py` exits 0
    - `python -m pytest tests/test_tuning.py -q` exits 0 with all 11 tests passing
    - `python -m pytest tests/test_tuning.py::test_set_value_visibility -q` exits 0 (FND-04 revised acceptance)
    - `python -m pytest tests/test_tuning.py::test_bake_derived_determinism -q` exits 0 (FND-06 acceptance)
    - `python -m pytest tests/test_tuning.py::test_compat_shim_smoke -q` exits 0 (12-caller smoke test)
  </acceptance_criteria>
  <done>tests/test_tuning.py exists with exactly the 11 named tests; pytest green on the whole file; the three gate tests (test_set_value_visibility, test_bake_derived_determinism, test_compat_shim_smoke) individually green; no tests skipped.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| test runner → filesystem | Tests write temp files for save-round-trip and name-uniqueness schemas |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-24-18 | Tampering | test writes clobbering real physics-schema.json | mitigate | test_atomic_save_round_trip and test_name_uniqueness_raises both use pytest's `tmp_path` fixture (isolated temp dir); real assets/physics-schema.json is never a save target; each test calls `tuning.load()` after to restore the default path |
| T-24-19 | Denial of Service | test pollution across ordering | mitigate | autouse `_reload_tuning` fixture calls load() at setup and reset() at teardown — every test sees a pristine baseline regardless of order |
| T-24-20 | Tampering | compat-shim smoke test crashing on pyxel-init side effects | mitigate | Test wraps each import in a try/except → raises AssertionError with module name; planner explicitly instructs executor NOT to fix any discovered side effect, just report it (scope discipline) |
</threat_model>

<verification>
- `pytest tests/test_tuning.py -q` all green
- The 11 named tests all exist (grep-verified)
- FND-04 revised, FND-06, and FND-03 smoke test are each runnable in isolation
- No tests modify assets/physics-schema.json on disk
</verification>

<success_criteria>
- 11 named tests, all green
- FND-02/FND-04/FND-06 each have at least one dedicated passing test
- D-15 name-uniqueness raise path is exercised
- D-17 known limitation is implicitly accepted (no test asserts legacy callers see runtime mutations)
- HAZARD_DRAIN_RATES int-key regression is guarded
</success_criteria>

<output>
After completion, create `.planning/phases/24-tuning-foundation-schema-inversion/24-05-SUMMARY.md`
</output>
