"""Tests for Charge Shot Windup (gap fix: CHARGING_SHOT state with visual absorption)."""
import pytest
from unittest.mock import MagicMock, patch, call
from src.core.constants import CHARGE_WINDUP_DURATION


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


class TestChargeShotWindupEntry:
    """Test 1: Releasing Z while fused sets state to CHARGING_SHOT (not instant fire)."""

    @patch("src.entities.player.input_manager")
    def test_z_release_enters_charging_state(self, mock_input):
        """Releasing Z while fused sets state to CHARGING_SHOT."""
        mock_input.btnr.return_value = False
        mock_input.btnp.return_value = False
        mock_input.btn.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(is_fused=True, facing_right=True)
        slime = make_slime()

        # Simulate Z release while fused
        def btnr_side(key):
            if key == "spit":
                return True
            return False
        mock_input.btnr.side_effect = btnr_side

        p.handle_input(slime)

        assert p.state == "CHARGING_SHOT"
        assert p.charge_windup_timer == CHARGE_WINDUP_DURATION

    @patch("src.entities.player.input_manager")
    def test_z_release_does_not_instant_fire(self, mock_input):
        """Z release while fused should NOT call fire_charge_shot immediately."""
        mock_input.btnr.return_value = False
        mock_input.btnp.return_value = False
        mock_input.btn.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(is_fused=True, facing_right=True)
        slime = make_slime()

        def btnr_side(key):
            if key == "spit":
                return True
            return False
        mock_input.btnr.side_effect = btnr_side

        with patch.object(p, 'fire_charge_shot') as mock_fire:
            p.handle_input(slime)
            mock_fire.assert_not_called()


class TestChargeShotWindupTimer:
    """Test 2: While in CHARGING_SHOT, charge_windup_timer decrements each frame."""

    @patch("src.entities.player.input_manager")
    def test_timer_decrements(self, mock_input):
        """charge_windup_timer decrements each frame in CHARGING_SHOT."""
        p = make_player(is_fused=True, state="CHARGING_SHOT")
        p.charge_windup_timer = CHARGE_WINDUP_DURATION
        slime = make_slime()

        p.update_charge_shot(slime)

        assert p.charge_windup_timer == CHARGE_WINDUP_DURATION - 1


class TestChargeShotFires:
    """Test 3: When charge_windup_timer reaches 0, fire_charge_shot is called."""

    @patch("src.entities.player.input_manager")
    def test_fires_at_zero(self, mock_input):
        """fire_charge_shot is called when timer hits 0."""
        p = make_player(is_fused=True, state="CHARGING_SHOT")
        p.charge_windup_timer = 1  # Will reach 0 after one tick
        slime = make_slime()

        with patch.object(p, 'fire_charge_shot') as mock_fire:
            p.update_charge_shot(slime)
            mock_fire.assert_called_once_with(slime)

    @patch("src.entities.player.input_manager")
    def test_state_exits_after_fire(self, mock_input):
        """State exits CHARGING_SHOT after fire."""
        p = make_player(is_fused=True, is_grounded=True, state="CHARGING_SHOT")
        p.charge_windup_timer = 1
        slime = make_slime()

        p.update_charge_shot(slime)

        assert p.state != "CHARGING_SHOT"


class TestChargeShotMovementLock:
    """Test 4: During CHARGING_SHOT, player cannot move horizontally."""

    @patch("src.entities.player.input_manager")
    def test_no_horizontal_movement(self, mock_input):
        """Player horizontal movement is locked during CHARGING_SHOT."""
        mock_input.btnr.return_value = False
        mock_input.btnp.return_value = False
        mock_input.btn.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(is_fused=True, state="CHARGING_SHOT")
        p.charge_windup_timer = 10
        slime = make_slime()

        p.update_charge_shot(slime)

        assert p.dx == 0


class TestSlimeAbsorption:
    """Test 5: slime.is_being_absorbed is True during CHARGING_SHOT, False otherwise."""

    @patch("src.entities.player.input_manager")
    def test_absorption_set_on_entry(self, mock_input):
        """is_being_absorbed is set to True when entering CHARGING_SHOT."""
        mock_input.btnr.return_value = False
        mock_input.btnp.return_value = False
        mock_input.btn.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(is_fused=True, facing_right=True)
        slime = make_slime(is_being_absorbed=False)

        def btnr_side(key):
            if key == "spit":
                return True
            return False
        mock_input.btnr.side_effect = btnr_side

        p.handle_input(slime)

        assert slime.is_being_absorbed is True

    @patch("src.entities.player.input_manager")
    def test_absorption_cleared_after_fire(self, mock_input):
        """is_being_absorbed is set to False when windup completes."""
        p = make_player(is_fused=True, state="CHARGING_SHOT")
        p.charge_windup_timer = 1
        slime = make_slime(is_being_absorbed=True)

        p.update_charge_shot(slime)

        assert slime.is_being_absorbed is False
