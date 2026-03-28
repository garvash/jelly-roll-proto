"""Tests for tap reposition fix: slime.reposition() must NOT set is_holding_position (UAT gap 2)."""
import pytest
from unittest.mock import MagicMock, patch
from src.core.constants import TILE_SIZE, HOLD_TAP_THRESHOLD


def make_slime(**overrides):
    """Create a real Slime instance for testing reposition behavior."""
    from src.entities.slime import Slime
    s = Slime(50, 50)
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


def make_level_map(collision=False, ground_at_dy=0):
    """Create a mock level_map. ground_at_dy: how many tiles down to find ground (0=immediate)."""
    lm = MagicMock()

    def check_collision(x, y, w, h):
        # Candidate position is never solid (air), but ground check returns True
        # This simulates: candidate tile is open, ground is 0 tiles below
        if h == 1:
            # Ground scan check (checking 1px tall strip below candidate)
            return True
        return collision

    lm.check_collision.side_effect = check_collision
    lm.check_hazard.return_value = False
    return lm


class TestRepositionFollowState:
    def test_reposition_keeps_is_holding_position_false(self):
        """After reposition(), is_holding_position must remain False."""
        slime = make_slime()
        lm = make_level_map()
        slime.reposition(1, 50, 50, lm)
        assert slime.is_holding_position is False

    def test_reposition_changes_position(self):
        """After reposition(), slime.x must differ from starting position."""
        slime = make_slime(x=50, y=50)
        lm = make_level_map()
        slime.reposition(1, 50, 50, lm)
        assert slime.x != 50, "Slime position should change after reposition"

    def test_reposition_clears_history(self):
        """After reposition(), slime.history is cleared for fresh follow."""
        slime = make_slime()
        slime.history.append((40, 40))
        slime.history.append((42, 42))
        lm = make_level_map()
        slime.reposition(1, 50, 50, lm)
        assert len(slime.history) == 0

    def test_reposition_clears_velocity(self):
        """After reposition(), dx and dy are zeroed."""
        slime = make_slime(dx=3.0, dy=2.0)
        lm = make_level_map()
        slime.reposition(1, 50, 50, lm)
        assert slime.dx == 0
        assert slime.dy == 0

    def test_reposition_clears_punted(self):
        """After reposition(), is_punted is False."""
        slime = make_slime(is_punted=True)
        lm = make_level_map()
        slime.reposition(1, 50, 50, lm)
        assert slime.is_punted is False

    def test_reposition_left_changes_position(self):
        """Reposition with direction=-1 moves slime left of player."""
        slime = make_slime(x=50, y=50)
        lm = make_level_map()
        slime.reposition(-1, 50, 50, lm)
        assert slime.x < 50, "Slime should move left of player position"


class TestPlayerCallsReposition:
    @patch("src.entities.player.input_manager")
    def test_tap_left_calls_reposition_not_hold(self, mock_input):
        """Player.handle_input tap LEFT calls slime.reposition, not slime.hold_position."""
        from src.entities.player import Player
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        level_map.check_hazard.return_value = False
        game = MagicMock()
        p = Player(50, 50, level_map, game)
        p.is_fused = False
        p.knockback_timer = 0

        slime = MagicMock()
        slime.is_dissipated = False
        slime.is_fused = False
        slime.is_recalling = False
        slime.juice = 200
        slime.max_juice = 200

        mock_input.was_tap.return_value = False
        # Simulate tap left
        def was_tap_side(action, threshold):
            return action == "left"
        mock_input.was_tap.side_effect = was_tap_side
        mock_input.btn.return_value = False
        mock_input.btnp.return_value = False
        mock_input.btnr.return_value = False
        mock_input.hold_frames.return_value = 0

        p.handle_input(slime)

        slime.reposition.assert_called_once()
        slime.hold_position.assert_not_called()

    @patch("src.entities.player.input_manager")
    def test_tap_right_calls_reposition_not_hold(self, mock_input):
        """Player.handle_input tap RIGHT calls slime.reposition, not slime.hold_position."""
        from src.entities.player import Player
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        level_map.check_hazard.return_value = False
        game = MagicMock()
        p = Player(50, 50, level_map, game)
        p.is_fused = False
        p.knockback_timer = 0

        slime = MagicMock()
        slime.is_dissipated = False
        slime.is_fused = False
        slime.is_recalling = False
        slime.juice = 200
        slime.max_juice = 200

        def was_tap_side(action, threshold):
            return action == "right"
        mock_input.was_tap.side_effect = was_tap_side
        mock_input.btn.return_value = False
        mock_input.btnp.return_value = False
        mock_input.btnr.return_value = False
        mock_input.hold_frames.return_value = 0

        p.handle_input(slime)

        slime.reposition.assert_called_once()
        slime.hold_position.assert_not_called()
