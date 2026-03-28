"""Tests for directional slime hold (ABL-03, D-19 through D-21)."""
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

from src.core.constants import SLIME_MAX_DIST, TILE_SIZE


class MockLevelMap:
    """Level map with a floor at y=56 (row 7) for ground detection."""
    def check_collision(self, x, y, w, h):
        # Floor at y=56 (tile row 7)
        if y + h > 56:
            return True
        return False

    def check_hazard(self, x, y, w, h):
        return False


class OpenLevelMap:
    """Level map with no collisions (open space)."""
    def check_collision(self, x, y, w, h):
        return False

    def check_hazard(self, x, y, w, h):
        return False


def make_slime(x=50, y=48):
    from src.entities.slime import Slime
    slime = Slime(x, y)
    return slime


def test_hold_position_sets_flag():
    """hold_position() sets is_holding_position=True."""
    slime = make_slime()
    level_map = MockLevelMap()
    slime.hold_position(1, 50, 48, level_map)
    assert slime.is_holding_position is True


def test_hold_position_right():
    """hold_position(1, ...) places slime to the right of player."""
    slime = make_slime(x=50, y=48)
    level_map = MockLevelMap()
    px = 50
    slime.hold_position(1, px, 48, level_map)
    assert slime.x > px


def test_hold_position_left():
    """hold_position(-1, ...) places slime to the left of player."""
    slime = make_slime(x=50, y=48)
    level_map = MockLevelMap()
    px = 50
    slime.hold_position(-1, px, 48, level_map)
    assert slime.x < px


def test_hold_position_cancels_punt():
    """hold_position() clears is_punted state."""
    slime = make_slime()
    level_map = MockLevelMap()
    slime.is_punted = True
    slime.hold_position(1, 50, 48, level_map)
    assert slime.is_punted is False
    assert slime.is_holding_position is True


def test_holding_slime_doesnt_follow():
    """When is_holding_position=True, slime stays at hold position during update."""
    slime = make_slime(x=80, y=48)
    level_map = MockLevelMap()
    slime.is_holding_position = True
    hold_x = slime.x

    # Update with player far away (but not too far to trigger reform)
    slime.update(50, 48, True, level_map, is_fused=False)

    # Slime should stay near hold position (gravity may shift y slightly)
    assert abs(slime.x - hold_x) < 1  # x unchanged


def test_holding_slime_reforms_when_too_far():
    """Holding slime reforms if distance to player exceeds SLIME_MAX_DIST."""
    slime = make_slime(x=200, y=48)
    level_map = OpenLevelMap()
    slime.is_holding_position = True

    # Player at x=0, slime at x=200, distance > SLIME_MAX_DIST (100)
    slime.update(0, 48, True, level_map, is_fused=False)

    assert not slime.is_holding_position  # Reset after reform
