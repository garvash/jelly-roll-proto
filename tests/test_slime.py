import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock pyxel before importing classes that use it
sys.modules['pyxel'] = MagicMock()

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
    
    # Fill history to reach SLIME_FOLLOW_DELAY
    for i in range(SLIME_FOLLOW_DELAY + 1):
        slime.update(player_x, player_y, player_facing_right)
    
    # After delay, target_x should be player_x + offset_x (-8 for facing_right=True)
    expected_target_x = player_x - 8
    expected_target_y = player_y
    
    # Slime should have moved towards target (lerp)
    assert slime.x > 0
    assert slime.y > 0
    assert slime.target_x == expected_target_x
    assert slime.target_y == expected_target_y

def test_slime_juice_regeneration():
    slime = Slime(0, 0)
    slime.juice = 50.0
    slime.update(0, 0, True)
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
    
    # Mock pyxel.btn and pyxel.btnp for activation
    import pyxel
    def mock_btn(key):
        if key == pyxel.KEY_DOWN: return True
        return False
        
    def mock_btnp(key):
        if key == pyxel.KEY_X: return True
        return False

    with patch('pyxel.btn', side_effect=mock_btn), \
         patch('pyxel.btnp', side_effect=mock_btnp):
        
        # Player in air
        player.is_grounded = False
        
        player.handle_input(slime)
        
        assert player.state == "DIVING"
        assert player.is_fused == True
        assert slime.juice == JUICE_MAX - DRILL_ACTIVATION_COST

def test_slime_reform_logic():
    slime = Slime(0, 0)
    player_x, player_y = 200, 200 # Far away
    player_facing_right = True
    
    slime.update(player_x, player_y, player_facing_right)
    
    # Should have reformed (teleported)
    assert slime.x == player_x - SLIME_REFORM_DIST
    assert slime.y == player_y
    assert len(slime.history) == 0
