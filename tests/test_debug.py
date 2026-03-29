"""Tests for debug god-mode toggles (D-08 through D-10)."""
import os
from unittest.mock import MagicMock, patch


def test_god_abilities_defaults_false():
    """debug.god_abilities defaults to False."""
    import src.core.debug as debug
    # Reset to module defaults (in case prior test toggled)
    debug.god_abilities = False
    assert debug.god_abilities is False


def test_god_invincible_defaults_false():
    """debug.god_invincible defaults to False."""
    import src.core.debug as debug
    debug.god_invincible = False
    assert debug.god_invincible is False


def test_god_infinite_juice_defaults_false():
    """debug.god_infinite_juice defaults to False."""
    import src.core.debug as debug
    debug.god_infinite_juice = False
    assert debug.god_infinite_juice is False


def test_player_abilities_default_false():
    """Player.__init__ creates player with abilities defaulting to False."""
    with patch("src.entities.player.input_manager"):
        from src.entities.player import Player
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        level_map.check_hazard.return_value = False
        p = Player(50, 50, level_map)
        assert p.has_shield is False
        assert p.has_dash is False
        assert p.has_boost is False
        assert p.has_shield_t2 is False


def test_constants_no_debug_all_abilities():
    """constants.py source does NOT contain DEBUG_ALL_ABILITIES."""
    constants_path = os.path.join(os.path.dirname(__file__), "..", "src", "core", "constants.py")
    with open(constants_path) as f:
        source = f.read()
    assert "DEBUG_ALL_ABILITIES" not in source
