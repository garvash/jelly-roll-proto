---
phase: 25
plan: 02
type: execute
wave: 2
depends_on:
  - 25-01
files_modified:
  - tests/test_tuning_livereach.py
autonomous: true
requirements:
  - FND-05
must_haves:
  truths:
    - "Running `tuning.set_value('GRAVITY', 10 * baseline)` between two `player.update()` calls produces a visibly different physics effect on the second call"
    - "The same proof holds for JUMP_FORCE, MAX_WALK_SPEED, and WALK_FRICTION (at minimum)"
    - "Tests are hermetic: each test starts from `tuning.reset()` baseline and cannot leak state to the next test"
    - "The test file runs under `pytest tests/test_tuning_livereach.py -q` and exits 0"
  artifacts:
    - path: "tests/test_tuning_livereach.py"
      provides: "Automated proof that Phase 25's use-site migration reaches gameplay (FND-05 acceptance artifact #1 per 25-CONTEXT D-04.1)"
      contains: "def test_livereach_gravity"
  key_links:
    - from: "tests/test_tuning_livereach.py"
      to: "src.entities.player.Player"
      via: "Player instantiation + player.update() driven per test (steal harness from tests/test_physics.py)"
      pattern: "Player\\(.*\\)"
    - from: "tests/test_tuning_livereach.py"
      to: "src.core.tuning.set_value / reset"
      via: "autouse pytest fixture calling tuning.reset() in teardown (D-04a)"
      pattern: "tuning\\.reset\\(\\)"
---

<objective>
Create `tests/test_tuning_livereach.py` — the automated proof that Phase 25's use-site migration actually reaches gameplay. Per 25-CONTEXT D-04.1, for each of `GRAVITY`, `JUMP_FORCE`, `MAX_WALK_SPEED`, and `WALK_FRICTION`, the test must: (a) instantiate a Player, (b) drive one `player.update()` and snapshot the physics effect, (c) call `tuning.set_value(KEY, 10 * baseline)`, (d) drive another `player.update()`, (e) assert the effect changed in the expected direction. This is the hermetic automated proof of Phase 25 success criterion #2 (from ROADMAP: "Editing a movement value in physics-schema.json changes player behavior on the very next frame").

Purpose: Plan 01 migrates player.py mechanically. Mechanical rename preserves baseline by construction but does NOT by itself prove that `set_value` reaches use sites. This test is the load-bearing automated artifact that closes FND-05. It must depend on Plan 01 (player.py migrated) being committed — otherwise the legacy wildcard binding still shadows `tuning.set_value()` and the test would be a green false positive.

Output: `tests/test_tuning_livereach.py` with at minimum 4 test functions covering GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, and WALK_FRICTION, using an autouse `tuning.reset()` teardown fixture, reusing the Player instantiation harness style from `tests/test_physics.py`.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/25-call-site-migration-constants-tuning/25-CONTEXT.md
@src/core/tuning.py
@src/entities/player.py
@tests/test_physics.py
@tests/test_tuning.py

<interfaces>
<!-- Player instantiation harness pattern (steal from tests/test_physics.py) -->
```python
import pytest
from unittest.mock import MagicMock, patch
import sys

# Pyxel must be mocked globally for import to succeed in a headless test.
mock_pyxel = MagicMock()
sys.modules["pyxel"] = mock_pyxel

from src.entities.player import Player
from src.core import tuning

@pytest.fixture
def mock_level():
    level = MagicMock()
    level.check_collision.return_value = False
    level.check_hazard.return_value = False
    level.is_switch.return_value = False
    return level

@pytest.fixture
def mock_slime():
    slime = MagicMock()
    slime.x = 100; slime.y = 100; slime.w = 8; slime.h = 8
    slime.juice = 100
    return slime
```

<!-- tuning.py mutation + reset API -->
```python
tuning.set_value('GRAVITY', 0.875)   # 10× baseline 0.0875
tuning.reset()                       # restores _model from _baseline (whole schema)
tuning.reset('GRAVITY')              # restores a single key
# D-04a: the fixture must call tuning.reset() (no key) in teardown for hermetic tests.
```

<!-- Existing test_tuning.py baseline constants (reuse for sanity checks) -->
```python
EXPECTED_GRAVITY = 0.0875
EXPECTED_JUMP_FORCE = -3.25
EXPECTED_MAX_WALK_SPEED = 1.25
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Write tests/test_tuning_livereach.py with four livereach tests and a reset fixture</name>
  <files>tests/test_tuning_livereach.py</files>
  <read_first>
    - tests/test_physics.py (copy the Pyxel mock + Player harness verbatim — mock_level fixture, mock_slime fixture, the `sys.modules["pyxel"] = mock_pyxel` dance)
    - tests/test_tuning.py (copy the `EXPECTED_GRAVITY` / `EXPECTED_JUMP_FORCE` / `EXPECTED_MAX_WALK_SPEED` baseline values — no magic numbers per project memory)
    - src/core/tuning.py (understand set_value + reset semantics; reset() with no key restores the whole model)
    - src/entities/player.py (AFTER Plan 01 has landed — verify that `tuning.GRAVITY` etc. are the actual live reads in update/apply_gravity/move/jump; the test is only meaningful if player.py is already migrated)
    - .planning/phases/25-call-site-migration-constants-tuning/25-CONTEXT.md §D-04 and §D-04a
  </read_first>
  <action>
Create `tests/test_tuning_livereach.py` with the following shape. Use Write tool (new file).

**Imports + Pyxel mock block** — verbatim from tests/test_physics.py lines 1–10:
```python
"""Phase 25 livereach tests — FND-05 acceptance artifact #1.

For each of GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, WALK_FRICTION, this suite
proves that a `tuning.set_value` call between two `player.update()` calls
changes the physics effect on the second update. This is the automated
proof that Phase 25's use-site migration reaches gameplay (25-CONTEXT D-04.1).

Hermetic via autouse `tuning.reset()` teardown (D-04a) — every test starts
and ends at the v1.3 baseline.
"""
import pytest
from unittest.mock import MagicMock, patch
import sys

mock_pyxel = MagicMock()
sys.modules["pyxel"] = mock_pyxel

from src.entities.player import Player
from src.core import tuning
```

**Baseline constants** — use named constants (project memory: no magic numbers). Re-derive each from `tuning.get_baseline()` so the test never drifts when v1.3 values move:
```python
# Multiplier for the livereach proof — big enough that a 10× change in
# GRAVITY produces a visibly different dy after one frame, without running
# the risk of overflow or Player collision-probe side effects.
LIVEREACH_MULTIPLIER = 10.0
FRICTION_MULTIPLIER = 10.0
# Single-frame simulation — one update() call per phase of the test.
SINGLE_FRAME = 1
```

**Autouse teardown fixture (D-04a):**
```python
@pytest.fixture(autouse=True)
def _tuning_reset_after_each_test():
    """Restore the full tuning baseline after every test so mutations do not
    leak between test functions (D-04a)."""
    yield
    tuning.reset()
```

**Player harness fixtures** — copy from tests/test_physics.py lines 19–35 (`mock_level`, `mock_slime`):
```python
@pytest.fixture
def mock_level():
    level = MagicMock()
    level.check_collision.return_value = False
    level.check_hazard.return_value = False
    level.is_switch.return_value = False
    return level

@pytest.fixture
def mock_slime():
    slime = MagicMock()
    slime.x = 100; slime.y = 100
    slime.w = 8; slime.h = 8
    slime.juice = 100
    return slime
```

**Helper — build a Player at rest with input patched to neutral:**
```python
def _fresh_player(level):
    """Instantiate a Player at (0,0) with no grounded contact. The tests
    patch input_manager separately per test so each one can drive the
    exact input state it needs."""
    return Player(0, 0, level)
```

**Test 1 — GRAVITY livereach (per D-04.1 acceptance bar):**
```python
def test_livereach_gravity(mock_level, mock_slime):
    """tuning.set_value('GRAVITY', 10x baseline) must change the dy applied
    during apply_gravity() on the next update()."""
    baseline_gravity = tuning.get_baseline('GRAVITY')

    # Phase A: baseline gravity, one frame of falling from rest.
    player_a = _fresh_player(mock_level)
    player_a.is_grounded = False
    player_a.state = "FALLING"
    player_a.dy = 0.0
    with patch("src.entities.player.input_manager") as m_input:
        m_input.btn.return_value = False
        m_input.btnp.return_value = False
        m_input.btnr.return_value = False
        player_a.update(mock_slime)
    dy_baseline = player_a.dy

    # Phase B: 10x gravity, one frame of falling from rest.
    tuning.set_value('GRAVITY', baseline_gravity * LIVEREACH_MULTIPLIER)
    player_b = _fresh_player(mock_level)
    player_b.is_grounded = False
    player_b.state = "FALLING"
    player_b.dy = 0.0
    with patch("src.entities.player.input_manager") as m_input:
        m_input.btn.return_value = False
        m_input.btnp.return_value = False
        m_input.btnr.return_value = False
        player_b.update(mock_slime)
    dy_mutated = player_b.dy

    # The 10x-gravity player must have a strictly greater dy after one frame.
    assert dy_mutated > dy_baseline, (
        f"GRAVITY livereach failed: dy_baseline={dy_baseline}, "
        f"dy_mutated={dy_mutated}. If these are equal, player.py is still "
        f"caching GRAVITY at import time — Phase 25 Plan 01 did not migrate "
        f"the use site correctly."
    )
```

**Test 2 — JUMP_FORCE livereach:** same shape, but the test must drive a jump input. Use `m_input.btnp.side_effect = lambda a: a == "jump"` to fire a jump on frame 1; snapshot `player.dy` immediately after the jump is applied (it should equal `tuning.JUMP_FORCE`). Assert: `dy_mutated == 10 * dy_baseline` (or as close as integer pyxel inputs allow; use a tolerance of `1e-6` via `pytest.approx`). Note that JUMP_FORCE is negative — "larger" in the jump-stronger direction means "more negative."

**Test 3 — MAX_WALK_SPEED livereach:** drive a right-walk input across several frames (at least `ceil(MAX_WALK_SPEED / WALK_ACCEL) + 1` so velocity saturates at the cap). Snapshot `player.dx` at saturation. Mutate via `tuning.set_value('MAX_WALK_SPEED', 10 * baseline)`, re-run, assert `dx_mutated > dx_baseline`. Implementation note: the walk clamp in player.py reads `tuning.MAX_WALK_SPEED` — if it does not, test will fail and Plan 01 was incomplete.

**Test 4 — WALK_FRICTION livereach:** give Player a nonzero `player.dx` and NO input (friction branch). After one update, `player.dx` should be closer to 0 by exactly `tuning.WALK_FRICTION`. Mutate friction to 10x, reset player, reapply, assert the mutated player decelerates faster (strictly smaller `abs(player.dx)` after one frame).

**Cross-cutting implementation notes:**

- Every test MUST create a fresh `Player` instance per phase (A and B). Do not reuse one Player across a set_value call — the mechanical rename means `tuning.X` reads are live, but the Player's own cached state (`player.dy`, `player.x`) from phase A would contaminate phase B.
- Every test MUST patch `src.entities.player.input_manager` for the duration of the update() call (D-01a from 24-CONTEXT's test idioms — input is the only external dependency other than tuning and level).
- Never assert on exact float equality for the mutated branch; use `>`, `<`, or `pytest.approx(rel=1e-6)`. The point is to prove the sign and direction of change, not to re-derive v1.3 physics integration.
- Do NOT import anything from `src.core.constants`. The test's entire point is that use-site migration works without the shim; referencing the shim in a Phase 25 acceptance test would be self-defeating.
- Do NOT touch `tests/test_physics.py`, `tests/test_tuning.py`, or any of the other 27 tests/test_*.py files — they are deliberately left on the shim per D-02b.
- Naming: use `test_livereach_<key_lowercase>` for each test function so the pattern is grep-friendly.

After writing, run: `pytest tests/test_tuning_livereach.py -q`. Expected: 4 passed. Then run the full suite `pytest -q` to confirm the new test file does not contaminate the others (the autouse reset fixture should prevent any leakage).
  </action>
  <verify>
    <automated>pytest tests/test_tuning_livereach.py -q</automated>
  </verify>
  <acceptance_criteria>
    - File `tests/test_tuning_livereach.py` exists
    - `grep -c "def test_livereach_gravity" tests/test_tuning_livereach.py` returns 1
    - `grep -c "def test_livereach_jump_force" tests/test_tuning_livereach.py` returns 1
    - `grep -c "def test_livereach_max_walk_speed" tests/test_tuning_livereach.py` returns 1
    - `grep -c "def test_livereach_walk_friction" tests/test_tuning_livereach.py` returns 1
    - `grep -c "tuning.reset()" tests/test_tuning_livereach.py` returns at least 1 (the autouse fixture)
    - `grep -c "tuning.set_value" tests/test_tuning_livereach.py` returns at least 4 (one per test)
    - `grep -c "from src.core.constants" tests/test_tuning_livereach.py` returns 0 (never touch the shim in this file)
    - `grep -c "autouse=True" tests/test_tuning_livereach.py` returns 1 (the reset fixture)
    - `pytest tests/test_tuning_livereach.py -q` exits 0 with 4 passed (or more if executor adds extra tests)
    - `pytest -q` (full suite) exits 0 — the autouse reset must not contaminate other test files
    - `pytest tests/test_tuning.py -q` exits 0 (Phase 24's tests unchanged)
  </acceptance_criteria>
  <done>
    A hermetic livereach test file exists at `tests/test_tuning_livereach.py`, covers GRAVITY / JUMP_FORCE / MAX_WALK_SPEED / WALK_FRICTION per 25-CONTEXT D-04.1, uses an autouse `tuning.reset()` fixture per D-04a, passes, and proves that Plan 01's use-site migration reaches gameplay. The full pytest suite remains green.
  </done>
</task>

</tasks>

<verification>
Run in order:
1. `pytest tests/test_tuning_livereach.py -q` — the new file must pass all 4 tests
2. `pytest tests/test_tuning.py -q` — Phase 24's tests unchanged, still green
3. `pytest -q` — full suite green (no cross-test contamination from the new fixture)
4. Sanity check: swap the new file's `tuning.set_value(KEY, ...)` line for a no-op comment and confirm the tests FAIL — this proves the test actually depends on the set_value call reaching gameplay. (This is a manual sanity check; revert the edit before committing.)
</verification>

<success_criteria>
- `tests/test_tuning_livereach.py` covers at minimum GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, WALK_FRICTION
- Each test uses the reset fixture and is hermetic
- `pytest tests/test_tuning_livereach.py -q` exits 0
- `pytest -q` (full suite) exits 0
- No import from `src.core.constants` in the new file
- No modifications to existing test files or other source files
</success_criteria>

<output>
After completion, create `.planning/phases/25-call-site-migration-constants-tuning/25-02-SUMMARY.md` noting:
- Which four tuning keys were covered
- Confirmation that the autouse reset fixture keeps tests hermetic
- Confirmation that the full `pytest -q` suite stayed green
- Any floating-point tolerance choices made (e.g., pytest.approx rel values)
</output>
