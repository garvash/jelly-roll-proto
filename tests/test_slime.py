import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock pyxel before importing classes that use it
mock_pyxel = MagicMock()
sys.modules['pyxel'] = mock_pyxel
mock_pyxel.btn.return_value = False
mock_pyxel.btnp.return_value = False

from src.entities.slime import Slime
from src.entities.player import Player
from src.core.constants import *

class MockLevelMap:
    def check_collision(self, x, y, w, h):
        return False

def test_slime_initialization():
    slime = Slime(10, 10)
    assert slime.x == 10
    assert slime.y == 10
    assert slime.juice == JUICE_MAX
    assert not slime.is_fused

def test_slime_follow_logic():
    slime = Slime(0, 0)
    player_x, player_y = 100, 100
    player_facing_right = True
    
    level_map = MagicMock()
    level_map.check_collision.return_value = False
    # Fill history to reach SLIME_FOLLOW_DELAY
    for i in range(SLIME_FOLLOW_DELAY + 1):
        slime.update(player_x, player_y, player_facing_right, level_map)
    # Slime should have moved towards target (in front of player)
    assert slime.x > 0
    assert slime.y > 0
    # Target is raw player position; front offset applied separately via lerp
    assert slime.target_x == player_x
    assert slime.target_y == player_y

def test_slime_juice_regeneration():
    slime = Slime(0, 0)
    slime.juice = 50.0
    level_map = MagicMock()
    slime.update(0, 0, True, level_map)
    assert slime.juice == 50.0 + JUICE_REGEN_RATE

def test_slime_scaling():
    slime = Slime(0, 0)
    
    slime.juice = JUICE_MAX
    assert slime.scale == 1.0
    
    slime.juice = 0
    assert slime.scale == JUICE_MIN_SCALE
    
    slime.juice = JUICE_MAX / 2
    expected_scale = JUICE_MIN_SCALE + (1.0 - JUICE_MIN_SCALE) * 0.5
    assert slime.scale == expected_scale

def test_drill_dive_activation():
    level_map = MockLevelMap()
    player = Player(10, 10, level_map)
    slime = Slime(10, 10)

    # Mock input_manager instead of raw pyxel (player.py now uses input abstraction)
    with patch("src.entities.player.input_manager") as m_input:
        m_input.btn.side_effect = lambda action: action == "down"
        m_input.btnp.side_effect = lambda action, **kw: action == "jump"
        m_input.btnr.return_value = False
        m_input.was_tap.return_value = False
        m_input.hold_frames.return_value = 0

        # Player in air
        player.is_grounded = False
        player.has_drill = True

        # In actual game, update_timers might consume btnp,
        # but here we ensure handle_input sees it.
        player.handle_input(slime)

        assert player.state == "DIVING"
        assert player.is_fused == True
        assert slime.juice == JUICE_MAX - DRILL_ACTIVATION_COST

def test_slime_reform_logic():
    slime = Slime(0, 0)
    player_x, player_y = 200, 200 # Far away
    player_facing_right = True
    
    level_map = MagicMock()
    level_map.check_collision.return_value = False
    slime.update(player_x, player_y, player_facing_right, level_map)
    
    # Should have reformed (teleported)
    # Reform still uses offset to keep slime behind player on teleport
    assert slime.x == player_x - SLIME_REFORM_DIST
    assert slime.y == player_y
    assert len(slime.history) == 0
