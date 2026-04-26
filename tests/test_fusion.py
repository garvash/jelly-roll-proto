"""Tests for the fusion system: recall, fuse/unfuse, mana shield, dissipation (D-01 through D-05)."""
import sys
import types

# Mock pyxel before any game imports
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

from src.core.constants import (
    RECALL_SPEED, RECALL_OVERLAP_DIST, MANA_SHIELD_COST,
    SLIME_DISSIPATE_COOLDOWN, INVULN_DURATION, JUICE_MAX
)


class MockLevelMap:
    def check_collision(self, x, y, w, h):
        return False
    def check_hazard(self, x, y, w, h):
        return False
    def get_destructible_at(self, x, y, w, h):
        return None


def make_player_and_slime(px=50, py=50, sx=100, sy=50):
    from src.entities.player import Player
    from src.entities.slime import Slime
    level_map = MockLevelMap()
    player = Player(px, py, level_map)
    slime = Slime(sx, sy)
    return player, slime, level_map


def test_fuse_sets_both_flags():
    """fuse(slime) sets player.is_fused=True AND slime.is_fused=True."""
    player, slime, _ = make_player_and_slime()
    assert not player.is_fused
    assert not slime.is_fused
    player.fuse(slime)
    assert player.is_fused
    assert slime.is_fused


def test_unfuse_clears_both_flags():
    """unfuse(slime) sets both to False."""
    player, slime, _ = make_player_and_slime()
    player.fuse(slime)
    assert player.is_fused and slime.is_fused
    player.unfuse(slime)
    assert not player.is_fused
    assert not slime.is_fused


def test_unfuse_with_dissipate():
    """unfuse(slime, dissipate=True) calls slime.dissipate()."""
    player, slime, _ = make_player_and_slime()
    player.fuse(slime)
    player.unfuse(slime, dissipate=True)
    assert not player.is_fused
    assert not slime.is_fused
    assert slime.is_dissipated
    assert slime.dissipate_timer == SLIME_DISSIPATE_COOLDOWN


def test_mana_shield_consumes_juice():
    """Fused damage consumes juice, not HP (D-04)."""
    player, slime, _ = make_player_and_slime()
    player.fuse(slime)
    slime.juice = JUICE_MAX  # Full juice
    initial_hp = player.hp
    initial_juice = slime.juice

    result = player.take_damage(1, source_x=60, slime=slime)

    assert result is True
    assert player.hp == initial_hp  # HP unchanged
    assert slime.juice == initial_juice - MANA_SHIELD_COST
    assert player.invuln_timer == INVULN_DURATION


def test_mana_shield_dissipates_on_empty():
    """Fused with juice < MANA_SHIELD_COST: take_damage -> slime dissipates (D-05)."""
    player, slime, _ = make_player_and_slime()
    player.fuse(slime)
    # Set juice just barely enough to be consumed but will hit 0
    slime.juice = MANA_SHIELD_COST - 5  # Will be consumed to 0

    result = player.take_damage(1, source_x=60, slime=slime)

    assert result is True
    assert player.hp == player.max_hp  # HP unchanged (mana shield absorbed)
    assert slime.juice == 0
    assert slime.is_dissipated
    assert not player.is_fused


def test_recall_moves_toward_player():
    """Slime at (100, 50), player at (50, 50): update_recall moves slime closer."""
    _, slime, _ = make_player_and_slime(sx=100, sy=50)
    slime.recall(50, 50)
    assert slime.is_recalling

    initial_x = slime.x
    slime.update_recall(50, 50)
    assert slime.x < initial_x  # Moved left toward player


def test_recall_arrives_triggers_overlap():
    """Slime within RECALL_OVERLAP_DIST of player -> update_recall returns True."""
    _, slime, _ = make_player_and_slime(sx=52, sy=50)  # Very close
    slime.recall(50, 50)

    arrived = slime.update_recall(50, 50)
    assert arrived is True
    assert not slime.is_recalling


def test_dissipate_timer_countdown():
    """dissipate() sets timer, ticks down to 0, then reforms at full juice."""
    player, slime, lm = make_player_and_slime()
    slime.dissipate()
    assert slime.is_dissipated
    assert slime.dissipate_timer == SLIME_DISSIPATE_COOLDOWN

    # Tick down almost completely
    for _ in range(SLIME_DISSIPATE_COOLDOWN - 1):
        reformed = slime.update_dissipation(player.x, player.y, True, lm)
        assert not reformed
        assert slime.is_dissipated

    # Final tick triggers reform
    reformed = slime.update_dissipation(player.x, player.y, True, lm)
    assert reformed is True
    assert not slime.is_dissipated
    assert slime.juice == slime.max_juice


def test_fuse_clears_recall_state():
    """fuse() should clear is_recalling.

    Plan 31.5-05: dropped is_holding_position assertion (Hold state stripped
    from Slime in Plan 02 per CONTEXT D-06; the attribute no longer exists
    on Slime and fuse() no longer references it).
    """
    player, slime, _ = make_player_and_slime()
    slime.is_recalling = True
    player.fuse(slime)
    assert not slime.is_recalling
    assert not player.is_charging_recall


def test_normal_damage_when_not_fused():
    """Without fusion, take_damage reduces HP normally."""
    player, slime, _ = make_player_and_slime()
    initial_hp = player.hp
    player.take_damage(1, source_x=60, slime=slime)
    assert player.hp == initial_hp - 1
