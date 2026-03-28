"""Tests for charge shot recoil (D-17): upward impulse on fire."""
import pytest
from unittest.mock import MagicMock, patch
from src.core.constants import CHARGE_RECOIL_FORCE


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
    slime.is_fused = True
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


class TestChargeRecoil:
    def test_charge_shot_applies_recoil(self):
        """Charge shot sets player.dy to CHARGE_RECOIL_FORCE after firing."""
        p = make_player(is_fused=True, facing_right=True, dy=0)
        slime = make_slime(juice=200.0)
        p.fire_charge_shot(slime)
        assert p.dy == CHARGE_RECOIL_FORCE

    def test_recoil_value_is_negative(self):
        """CHARGE_RECOIL_FORCE must be negative (upward impulse)."""
        assert CHARGE_RECOIL_FORCE < 0
