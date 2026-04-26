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
    """Player.__init__ creates player with surviving ability flags defaulting to False.

    Updated in Plan 31.5-05 (sympathetic regression sweep per RESEARCH Risk 5):
    has_dash / has_shield / has_shield_t2 / has_boost flags were stripped from
    Player.__init__ in Plan 01 sub-step 6 per CONTEXT D-17. The surviving
    ability flag is has_drill (drill is the sole fusion item in v2.0 per
    FUSION-DESIGN.md). This test now asserts has_drill defaults to False.
    """
    with patch("src.entities.player.input_manager"):
        from src.entities.player import Player
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        level_map.check_hazard.return_value = False
        p = Player(50, 50, level_map)
        assert p.has_drill is False


def test_constants_no_debug_all_abilities():
    """constants.py source does NOT contain DEBUG_ALL_ABILITIES."""
    constants_path = os.path.join(os.path.dirname(__file__), "..", "src", "core", "constants.py")
    with open(constants_path) as f:
        source = f.read()
    assert "DEBUG_ALL_ABILITIES" not in source
