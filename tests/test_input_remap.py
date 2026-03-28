"""Tests for input remap: drill dive on DOWN+SPACE, V for dash/ram only (D-12)."""
import pytest
from unittest.mock import MagicMock, patch
from src.core.constants import (
    JUMP_FORCE, COYOTE_TIME, JUMP_BUFFER, SLIME_MAX_DIST,
    DRILL_SPEED, DASH_SPEED
)


def make_player(**overrides):
    """Create a Player with mocked dependencies."""
    with patch("src.entities.player.input_manager"):
        from src.entities.player import Player
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        level_map.check_hazard.return_value = False
        game = MagicMock()
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
    slime.is_fused = False
    slime.is_dissipated = False
    slime.is_recalling = False
    slime.is_punted = False
    slime.is_holding_position = False
    slime.dx = 0
    slime.dy = 0
    slime.history = MagicMock()
    for k, v in overrides.items():
        setattr(slime, k, v)
    return slime


class TestDrillDiveOnDownSpace:
    @patch("src.entities.player.input_manager")
    def test_drill_dive_on_down_space(self, mock_input):
        """DOWN+SPACE while airborne with drill and juice triggers DIVING state."""
        mock_input.btnp.side_effect = lambda a: a == "jump"
        mock_input.btn.side_effect = lambda a: a == "down"
        mock_input.btnr.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(has_drill=True, is_grounded=False, state="FALLING")
        slime = make_slime(juice=200.0, x=50, y=50)  # Close to player
        p.handle_input(slime)
        assert p.state == "DIVING"

    @patch("src.entities.player.input_manager")
    def test_dash_button_no_drill_dive(self, mock_input):
        """V (dash button) with DOWN held should NOT trigger drill dive."""
        mock_input.btnp.side_effect = lambda a: a == "dash"
        mock_input.btn.side_effect = lambda a: a == "down"
        mock_input.btnr.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(has_drill=True, is_grounded=False, has_dash=False,
                        is_fused=False, state="FALLING")
        slime = make_slime(juice=200.0, x=50, y=50)
        p.handle_input(slime)
        assert p.state != "DIVING"

    @patch("src.entities.player.input_manager")
    def test_v_still_triggers_ram_when_fused(self, mock_input):
        """V while fused should trigger Slime Ram."""
        mock_input.btnp.side_effect = lambda a: a == "dash"
        mock_input.btn.return_value = False
        mock_input.btnr.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(is_fused=True, facing_right=True, state="IDLE")
        slime = make_slime(is_fused=True, juice=200.0)
        p.handle_input(slime)
        assert p.state == "RAMMING"

    @patch("src.entities.player.input_manager")
    def test_v_still_triggers_dash_when_unfused(self, mock_input):
        """V while unfused with has_dash should trigger basic dash."""
        mock_input.btnp.side_effect = lambda a: a == "dash"
        mock_input.btn.return_value = False
        mock_input.btnr.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(is_fused=False, has_dash=True, dash_cooldown=0,
                        facing_right=True, state="IDLE")
        slime = make_slime(is_fused=False, juice=200.0)
        p.handle_input(slime)
        assert p.state == "DASHING"

    @patch("src.entities.player.input_manager")
    def test_ground_jump_still_works_after_remap(self, mock_input):
        """Ground jump via buffer still works after drill remap to SPACE."""
        mock_input.btnp.return_value = False
        mock_input.btn.return_value = False
        mock_input.btnr.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(is_grounded=True, coyote_timer=COYOTE_TIME,
                        jump_buffer_timer=JUMP_BUFFER, state="IDLE")
        slime = make_slime()
        p.handle_input(slime)
        assert p.dy == JUMP_FORCE
