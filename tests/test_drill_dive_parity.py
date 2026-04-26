"""Phase 32 Wave 0 — RED tests for DrillDive behavioral parity (v1.3 contract).

Per VALIDATION.md Wave 0 Requirements + RESEARCH § Validation Architecture
(lines 762-805). DrillDive is the v1.3-equivalent ability moved out of
Player.apply_diving_physics into src.fusion.drill_dive (Plan 05). These tests
pin its behavior so the refactor can't drift parity.

State on Wave 0:
- Module-level `pytest.importorskip("src.fusion.drill_dive")` skips until Plan 05.

Coverage (FUS-05 — drill behavioral parity):
- activation cost (DRILL_ACTIVATION_COST = 5.0)
- impact exit + impact cost (DRILL_IMPACT_COST = 20.0) on solid landing
- soft block refund (+DRILL_BLOCK_REFUND = 15.0); drill_block_break(tx,ty)
- CRACKED_V cost (DRILL_CRACKED_V_COST = 20.0; no refund)
- juice→0 dissipate request_exit signal
- velocity clamp dy = DRILL_SPEED with dx = ±DRILL_DRIFT_SPEED on L/R
"""
import sys
import types

# Mock pyxel before any game imports.
if "pyxel" not in sys.modules:
    mock_pyxel = types.ModuleType("pyxel")
    mock_pyxel.KEY_LEFT = 0
    mock_pyxel.KEY_RIGHT = 1
    mock_pyxel.KEY_UP = 2
    mock_pyxel.KEY_DOWN = 3
    mock_pyxel.KEY_SPACE = 4
    mock_pyxel.KEY_Z = 5
    mock_pyxel.KEY_J = 6
    mock_pyxel.KEY_V = 7
    mock_pyxel.KEY_K = 8
    mock_pyxel.KEY_A = 9
    mock_pyxel.KEY_D = 10
    mock_pyxel.KEY_W = 11
    mock_pyxel.KEY_S = 12
    mock_pyxel.frame_count = 0
    mock_pyxel.btn = lambda k: False
    mock_pyxel.btnp = lambda k, **kw: False
    mock_pyxel.btnr = lambda k: False
    mock_pyxel.blt = lambda *a, **kw: None
    mock_pyxel.rect = lambda *a, **kw: None
    mock_pyxel.pset = lambda *a, **kw: None
    sys.modules["pyxel"] = mock_pyxel

import pytest

# Per-test importorskip pattern: keeps test list visible to `pytest --co` while
# skipping each test at runtime until Plan 05 ships `src.fusion.drill_dive` and
# `src.fusion.protocol`.
def _require_drill_modules():
    pytest.importorskip("src.fusion.protocol")
    pytest.importorskip("src.fusion.drill_dive")


from unittest.mock import MagicMock

from src.anim import event_bus
from src.core import tuning


# CRACKED_V tile-type sentinel — sourced from src.entities.player to avoid drift.
INTGRID_CRACKED_V_VALUE = 12  # Mirrors src/entities/player.py:10 (verified)


class MockLevelMap:
    """Mutable mock level. Tests override methods by reassignment."""

    def __init__(self):
        self._destructibles = {}
        self._collisions = {}

    def check_collision(self, x, y, w, h):
        return False

    def check_hazard(self, x, y, w, h):
        return False

    def get_destructible_at(self, x, y, w, h):
        return None


def make_player_and_slime(px=50, py=50, sx=100, sy=50):
    """Build (player, slime, level_map) for ability-level unit tests.

    Player.game = None default; tests that need is_fused True latch via
    a mock manager attached to player.game.fusion_manager.
    """
    from src.entities.player import Player
    from src.entities.slime import Slime

    level_map = MockLevelMap()
    player = Player(px, py, level_map)
    slime = Slime(sx, sy)
    return player, slime, level_map


def _stub_input_manager(left=False, right=False, down=False, jump=False):
    im = MagicMock()
    btn_map = {"left": left, "right": right, "down": down, "jump": jump, "spit": False, "up": False}
    im.btn = lambda name: btn_map.get(name, False)
    im.btnp = lambda name: False
    im.btnr = lambda name: False
    im.was_tap = lambda name: False
    im.hold_frames = lambda name: 0
    return im


# --- Activation cost --------------------------------------------------------


def test_activation_cost():
    """DrillDive.on_enter consumes DRILL_ACTIVATION_COST (5.0) juice."""
    _require_drill_modules()
    from src.fusion.drill_dive import DrillDive

    player, _, _ = make_player_and_slime()
    slime = MagicMock()
    slime.juice = 200.0
    slime.max_juice = 200.0
    slime.consume = MagicMock()
    slime.refill = MagicMock()

    DrillDive().on_enter(player, slime, context={})

    slime.consume.assert_any_call(tuning.DRILL_ACTIVATION_COST)


# --- Impact exit on solid landing ------------------------------------------


def test_impact_exit():
    """Solid-terrain landing during on_tick yields TickResult(request_exit=True,
    exit_reason='solid_landing'). on_exit consumes DRILL_IMPACT_COST and emits
    drill_impact + drill_end (D-12; emit lives in DrillDive.on_exit per
    32-05-PLAN.md Task 1 narrative)."""
    _require_drill_modules()
    from src.fusion.drill_dive import DrillDive

    player, _, level_map = make_player_and_slime()
    slime = MagicMock()
    slime.juice = 100.0
    slime.max_juice = 200.0
    slime.consume = MagicMock()
    slime.refill = MagicMock()

    drill = DrillDive()
    drill.on_enter(player, slime, context={})

    # Mock solid floor below player after vertical move.
    def solid_below(x, y, w, h):
        return y > player.y

    level_map.check_collision = solid_below

    captured_impact = []
    captured_end = []
    event_bus.subscribe("drill_impact", lambda **kw: captured_impact.append(kw))
    event_bus.subscribe("drill_end", lambda **kw: captured_end.append(kw))

    DT_DEFAULT = 1.0  # single-frame dispatch
    result = drill.on_tick(player, slime, DT_DEFAULT)

    assert result.request_exit is True, (
        "TickResult.request_exit must be True on solid landing"
    )
    assert result.exit_reason == "solid_landing", (
        f"exit_reason must be 'solid_landing', got {result.exit_reason!r}"
    )

    # on_exit performs the cost + emit (per Plan 05 Task 1 — emit in on_exit).
    drill.on_exit(player, slime, "solid_landing")
    slime.consume.assert_any_call(tuning.DRILL_IMPACT_COST)
    assert len(captured_impact) >= 1, "drill_impact must emit on solid landing"
    assert len(captured_end) >= 1, "drill_end must emit on every drill exit"


# --- Soft block refund ------------------------------------------------------


def test_soft_block_refund():
    """Mid-tick destructible-tile (soft) break: refunds DRILL_BLOCK_REFUND (15.0)
    and emits drill_block_break(tx=tx, ty=ty). Drill continues (request_exit=False).

    Event kwargs must match the existing emit signature CHAR-FOR-CHAR
    (RESEARCH Pitfall 1, source: src/entities/player.py:482)."""
    _require_drill_modules()
    from src.fusion.drill_dive import DrillDive

    player, _, level_map = make_player_and_slime()
    slime = MagicMock()
    slime.juice = 100.0
    slime.max_juice = 200.0
    slime.consume = MagicMock()
    slime.refill = MagicMock()

    drill = DrillDive()
    drill.on_enter(player, slime, context={})

    # Soft tile (no tile_type / generic destructible) at coords (5, 7).
    SOFT_TX = 5
    SOFT_TY = 7

    def get_dest(x, y, w, h):
        return (SOFT_TX, SOFT_TY, None)

    level_map.get_destructible_at = get_dest
    # No solid collision so drill continues.
    level_map.check_collision = lambda x, y, w, h: False

    captured = []
    event_bus.subscribe("drill_block_break", lambda **kw: captured.append(kw))

    DT_DEFAULT = 1.0
    result = drill.on_tick(player, slime, DT_DEFAULT)

    slime.refill.assert_any_call(tuning.DRILL_BLOCK_REFUND)
    assert result.request_exit is False, "drill must continue after soft block break"
    assert len(captured) >= 1, "drill_block_break must emit per soft tile break"
    # Match existing emit signature exactly (Pitfall 1 — char-for-char).
    assert captured[0] == {"tx": SOFT_TX, "ty": SOFT_TY}, (
        f"drill_block_break kwargs must equal {{'tx': {SOFT_TX}, 'ty': {SOFT_TY}}}, "
        f"got {captured[0]}"
    )


# --- CRACKED_V cost (no refund) --------------------------------------------


def test_cracked_v_cost():
    """CRACKED_V tile during drill: consumes DRILL_CRACKED_V_COST (20.0) juice;
    no refund (gate block, ABL-02). Drill continues."""
    _require_drill_modules()
    from src.fusion.drill_dive import DrillDive

    player, _, level_map = make_player_and_slime()
    slime = MagicMock()
    slime.juice = 100.0
    slime.max_juice = 200.0
    slime.consume = MagicMock()
    slime.refill = MagicMock()

    drill = DrillDive()
    drill.on_enter(player, slime, context={})
    # Reset consume tracker so we don't conflate activation cost.
    slime.consume.reset_mock()
    slime.refill.reset_mock()

    CRACKED_TX = 3
    CRACKED_TY = 4

    def get_dest_cracked_v(x, y, w, h):
        return (CRACKED_TX, CRACKED_TY, INTGRID_CRACKED_V_VALUE)

    level_map.get_destructible_at = get_dest_cracked_v
    level_map.check_collision = lambda x, y, w, h: False

    DT_DEFAULT = 1.0
    drill.on_tick(player, slime, DT_DEFAULT)

    slime.consume.assert_any_call(tuning.DRILL_CRACKED_V_COST)
    # CRACKED_V must NOT trigger the soft-block refund branch.
    for call in slime.refill.call_args_list:
        args, kwargs = call
        if args and args[0] == tuning.DRILL_BLOCK_REFUND:
            raise AssertionError(
                "CRACKED_V tile must NOT trigger DRILL_BLOCK_REFUND (gate-block, no refund)"
            )


# --- Juice empty dissipate signal -------------------------------------------


def test_juice_empty_dissipate():
    """slime.juice = 0 during drill on_tick yields TickResult(request_exit=True,
    exit_reason='juice_empty'). FusionManager owns the slime.dissipate() call;
    here we only verify the request signal."""
    _require_drill_modules()
    from src.fusion.drill_dive import DrillDive

    player, _, level_map = make_player_and_slime()
    slime = MagicMock()
    slime.juice = 0.0  # Empty on tick entry
    slime.max_juice = 200.0
    slime.consume = MagicMock()
    slime.refill = MagicMock()

    drill = DrillDive()
    # Bypass on_enter (which costs activation) — we want to test mid-drill empty.
    drill.on_enter(player, slime, context={})
    slime.juice = 0.0  # Re-set after activation cost

    level_map.check_collision = lambda x, y, w, h: False
    level_map.get_destructible_at = lambda x, y, w, h: None

    DT_DEFAULT = 1.0
    result = drill.on_tick(player, slime, DT_DEFAULT)

    assert result.request_exit is True, "drill must request exit when juice is 0"
    assert result.exit_reason == "juice_empty", (
        f"exit_reason must be 'juice_empty', got {result.exit_reason!r}"
    )


# --- Velocity clamp ---------------------------------------------------------


def test_drill_velocity_clamp():
    """Post on_enter, on_tick returns TickResult with dy=DRILL_SPEED (2.0).
    With input_manager.btn('left') True → dx = -DRILL_DRIFT_SPEED (-0.5);
    with btn('right') True → dx = +DRILL_DRIFT_SPEED (0.5);
    with neither L nor R → dx = 0.

    NOTE: DrillDive consults input_manager via the module-level src.core.input
    import inside on_tick (planner choice — see Plan 05). This test patches
    src.core.input directly so the ability sees our mock primitives.
    """
    _require_drill_modules()
    from unittest.mock import patch

    from src.fusion.drill_dive import DrillDive

    player, _, level_map = make_player_and_slime()
    slime = MagicMock()
    slime.juice = 100.0
    slime.max_juice = 200.0
    slime.consume = MagicMock()
    slime.refill = MagicMock()

    drill = DrillDive()
    drill.on_enter(player, slime, context={})

    level_map.check_collision = lambda x, y, w, h: False
    level_map.get_destructible_at = lambda x, y, w, h: None

    DT_DEFAULT = 1.0

    # No L/R held → dx = 0.
    with patch("src.core.input.btn", side_effect=lambda name: False):
        result = drill.on_tick(player, slime, DT_DEFAULT)
    assert result.dy == tuning.DRILL_SPEED, (
        f"dy must equal DRILL_SPEED ({tuning.DRILL_SPEED}), got {result.dy}"
    )
    assert result.dx == 0, f"dx must be 0 with no L/R held, got {result.dx}"

    # Left held → dx = -DRILL_DRIFT_SPEED.
    with patch("src.core.input.btn", side_effect=lambda name: name == "left"):
        result = drill.on_tick(player, slime, DT_DEFAULT)
    assert result.dx == -tuning.DRILL_DRIFT_SPEED, (
        f"dx must equal -DRILL_DRIFT_SPEED ({-tuning.DRILL_DRIFT_SPEED}), got {result.dx}"
    )

    # Right held → dx = +DRILL_DRIFT_SPEED.
    with patch("src.core.input.btn", side_effect=lambda name: name == "right"):
        result = drill.on_tick(player, slime, DT_DEFAULT)
    assert result.dx == tuning.DRILL_DRIFT_SPEED, (
        f"dx must equal +DRILL_DRIFT_SPEED ({tuning.DRILL_DRIFT_SPEED}), got {result.dx}"
    )
