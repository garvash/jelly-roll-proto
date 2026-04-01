"""Tests for Charge Shot instant fire (release Z while fused)."""
import pytest
from unittest.mock import MagicMock, patch


def make_player(**overrides):
    """Create a Player with mocked dependencies."""
    with patch("src.entities.player.input_manager"):
        from src.entities.player import Player
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        level_map.check_hazard.return_value = False
        level_map.get_zone_hazard_type.return_value = None
        game = MagicMock()
        game.projectiles = []
        p = Player(50, 50, level_map, game)
        for k, v in overrides.items():
            setattr(p, k, v)
        return p


def make_slime(**overrides):
    """Create a mock slime with standard defaults."""
    slime = MagicMock()
    slime.juice = 200.0
    slime.max_juice = 200.0
    slime.w = 8
    slime.h = 8
    slime.x = 50
    slime.y = 50
    slime.is_fused = True
    slime.is_dissipated = False
    slime.is_recalling = False
    slime.is_punted = False
    slime.is_holding_position = False
    slime.is_being_absorbed = False
    slime.dx = 0
    slime.dy = 0
    slime.history = MagicMock()
    for k, v in overrides.items():
        setattr(slime, k, v)
    return slime


class TestChargeShotInstantFire:
    """Release Z while fused fires charge shot immediately."""

    @patch("src.entities.player.input_manager")
    def test_z_release_fires_immediately(self, mock_input):
        """Releasing Z while fused calls fire_charge_shot."""
        mock_input.btnr.return_value = False
        mock_input.btnp.return_value = False
        mock_input.btn.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(is_fused=True, facing_right=True)
        slime = make_slime()

        def btnr_side(key):
            return key == "spit"
        mock_input.btnr.side_effect = btnr_side

        with patch.object(p, 'fire_charge_shot') as mock_fire:
            p.handle_input(slime)
            mock_fire.assert_called_once_with(slime)

    @patch("src.entities.player.input_manager")
    def test_state_exits_fused_after_fire(self, mock_input):
        """State is IDLE or FALLING after charge shot, not CHARGING_SHOT."""
        mock_input.btnr.return_value = False
        mock_input.btnp.return_value = False
        mock_input.btn.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(is_fused=True, is_grounded=True, facing_right=True)
        slime = make_slime()

        def btnr_side(key):
            return key == "spit"
        mock_input.btnr.side_effect = btnr_side

        p.handle_input(slime)

        assert p.state in ("IDLE", "FALLING")

    @patch("src.entities.player.input_manager")
    def test_slime_dissipates_after_fire(self, mock_input):
        """Slime dissipates as cost of charge shot."""
        mock_input.btnr.return_value = False
        mock_input.btnp.return_value = False
        mock_input.btn.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(is_fused=True, facing_right=True)
        slime = make_slime()

        def btnr_side(key):
            return key == "spit"
        mock_input.btnr.side_effect = btnr_side

        p.handle_input(slime)

        slime.dissipate.assert_called_once()
