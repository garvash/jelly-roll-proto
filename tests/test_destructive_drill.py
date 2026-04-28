"""Phase 33 FUS-06 D-03/D-04/D-05 — destructive-drill enemy-interaction tests.

RED until Wave 2 ships src/fusion/drill_dive.py changes:
  - DRILL_DAMAGE module-level constant (= 1 per D-04)
  - on_tick AABB scan over player.game.enemies that:
    * calls enemy.take_damage(DRILL_DAMAGE) on intersecting alive enemies
    * drains tuning.DRILL_ENEMY_COST per enemy hit
    * emits "drill_enemy_hit" event with x/y kwargs
    * returns TickResult(request_exit=False) — drill CONTINUES (D-03)

The Wave 1 schema migration adds tuning.DRILL_ENEMY_COST (= 15.0). Until
Wave 1 lands, the import fails and `pytest.importorskip` skips collection of
this module entirely (per Phase 32 pattern in test_drill_dive_parity.py).
"""
import sys
import types

# Mock pyxel before any game imports (verbatim from test_drill_dive_parity.py:19-46).
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

# Module-level guard — Wave 2 ships DRILL_DAMAGE; until then this skip keeps
# pytest collection clean while still exposing the test names.
pytest.importorskip("src.fusion.drill_dive", reason="Wave 2 will add DRILL_DAMAGE constant")

from unittest.mock import MagicMock

from src.anim import event_bus
from src.core import tuning


# Phase 33 D-05 named constants (project memory: no magic numbers).
EXPECTED_KILLS_BEFORE_EXIT = 5
STARTING_JUICE = 30.0
ENEMY_HP_DEFAULT = 1
ENEMY_W = 16
ENEMY_H = 16
PLAYER_X = 50
PLAYER_Y = 50
HIGH_JUICE = 200.0  # plenty for cost drain


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


def make_player_and_slime(px=PLAYER_X, py=PLAYER_Y, sx=100, sy=PLAYER_Y):
    """Build (player, slime, level_map) for ability-level unit tests."""
    from src.entities.player import Player
    from src.entities.slime import Slime

    level_map = MockLevelMap()
    player = Player(px, py, level_map)
    slime = Slime(sx, sy)
    return player, slime, level_map


def _make_alive_enemy(x, y, w=ENEMY_W, h=ENEMY_H, hp=ENEMY_HP_DEFAULT):
    """Build a MagicMock enemy with x/y/w/h/hp/is_alive/take_damage."""
    enemy = MagicMock()
    enemy.x = x
    enemy.y = y
    enemy.w = w
    enemy.h = h
    enemy.hp = hp
    enemy.is_alive = True
    enemy.take_damage = MagicMock()
    return enemy


# --- Test 1: drill hits intersecting enemy and continues -------------------


def test_drill_hits_enemy_and_continues():
    """D-03 + D-04 + D-05: drill on_tick deals DRILL_DAMAGE to intersecting
    enemy, drains DRILL_ENEMY_COST juice, emits drill_enemy_hit, continues
    drilling (no request_exit, no state change).
    """
    from src.fusion.drill_dive import DrillDive, DRILL_DAMAGE

    captured = []
    event_bus.subscribe("drill_enemy_hit", lambda **kw: captured.append(kw))

    player, slime, _ = make_player_and_slime(px=PLAYER_X, py=PLAYER_Y)
    enemy = _make_alive_enemy(x=PLAYER_X, y=PLAYER_Y)
    player.game = MagicMock()
    player.game.enemies = [enemy]
    slime.juice = HIGH_JUICE

    drill = DrillDive()
    result = drill.on_tick(player, slime, dt=1.0)

    enemy.take_damage.assert_called_once_with(DRILL_DAMAGE)
    assert slime.juice == HIGH_JUICE - tuning.DRILL_ENEMY_COST
    assert len(captured) == 1
    assert result.request_exit is False  # CONTINUES — no exit


# --- Test 2: drill hits two enemies on same frame --------------------------


def test_drill_hits_two_enemies_same_frame():
    """Two intersecting enemies in one frame: both take damage, juice drains
    twice, drill_enemy_hit emits twice, drill continues."""
    from src.fusion.drill_dive import DrillDive, DRILL_DAMAGE

    captured = []
    event_bus.subscribe("drill_enemy_hit", lambda **kw: captured.append(kw))

    player, slime, _ = make_player_and_slime(px=PLAYER_X, py=PLAYER_Y)
    enemy_a = _make_alive_enemy(x=PLAYER_X, y=PLAYER_Y)
    enemy_b = _make_alive_enemy(x=PLAYER_X + 4, y=PLAYER_Y + 4)
    player.game = MagicMock()
    player.game.enemies = [enemy_a, enemy_b]
    slime.juice = HIGH_JUICE

    drill = DrillDive()
    result = drill.on_tick(player, slime, dt=1.0)

    enemy_a.take_damage.assert_called_once_with(DRILL_DAMAGE)
    enemy_b.take_damage.assert_called_once_with(DRILL_DAMAGE)
    assert slime.juice == HIGH_JUICE - (2 * tuning.DRILL_ENEMY_COST)
    assert len(captured) == 2
    assert result.request_exit is False


# --- Test 3: enemy contact does NOT trigger solid_landing exit -------------


def test_drill_enemy_contact_does_not_request_exit():
    """D-03 continue-through invariant: enemy AABB intersection must NOT
    produce a TickResult with request_exit=True or exit_reason='solid_landing'.
    Drill is invulnerable to enemies via offense (D-03), not via i-frames."""
    from src.fusion.drill_dive import DrillDive

    player, slime, _ = make_player_and_slime(px=PLAYER_X, py=PLAYER_Y)
    enemy = _make_alive_enemy(x=PLAYER_X, y=PLAYER_Y)
    player.game = MagicMock()
    player.game.enemies = [enemy]
    slime.juice = HIGH_JUICE

    drill = DrillDive()
    result = drill.on_tick(player, slime, dt=1.0)

    assert result.request_exit is False
    assert getattr(result, "exit_reason", None) != "solid_landing"


# --- Test 4: 5 enemies + low juice — all hit, then Exit-(b) on next call ---


def test_drill_juice_starvation_after_kill_chain():
    """D-05 Exit-(b): with juice=30 and DRILL_ENEMY_COST=15 (Wave 1 schema-seed),
    a 5-enemy stack should ALL take damage on the same frame (option (a) clamp
    ordering per RESEARCH Pitfall 2 recommendation), juice clamps to 0, and
    Exit-(b) (juice→0 dissipate) fires on the NEXT call to on_tick.

    Per RESEARCH Pitfall 2: the scan damages all intersecting enemies first,
    THEN reads slime.juice and signals exit. So 30 juice / 15 cost = 2 hits
    paid normally; the remaining 3 hits clamp juice to 0 but still register
    take_damage (option (a)). The dissipate Exit-(b) fires next frame.
    """
    from src.fusion.drill_dive import DrillDive, DRILL_DAMAGE

    captured = []
    event_bus.subscribe("drill_enemy_hit", lambda **kw: captured.append(kw))

    player, slime, _ = make_player_and_slime(px=PLAYER_X, py=PLAYER_Y)
    enemies = [_make_alive_enemy(x=PLAYER_X + (i * 2), y=PLAYER_Y)
               for i in range(EXPECTED_KILLS_BEFORE_EXIT)]
    player.game = MagicMock()
    player.game.enemies = enemies
    slime.juice = STARTING_JUICE  # 30 — enough for 2 full cost drains

    drill = DrillDive()
    first_result = drill.on_tick(player, slime, dt=1.0)

    # All 5 enemies take damage on the same frame (option (a)).
    for enemy in enemies:
        enemy.take_damage.assert_called_once_with(DRILL_DAMAGE)
    # Juice clamps to 0 (negative not allowed).
    assert slime.juice == 0.0
    assert len(captured) == EXPECTED_KILLS_BEFORE_EXIT
    # First call still continues — Exit-(b) is signalled on the NEXT call.
    assert first_result.request_exit is False

    # Next call: juice is empty — drill requests dissipate exit.
    second_result = drill.on_tick(player, slime, dt=1.0)
    assert second_result.request_exit is True
