import pytest
from unittest.mock import MagicMock, patch
import sys

# We still need to mock pyxel globally to allow the import to succeed
mock_pyxel = MagicMock()
sys.modules["pyxel"] = mock_pyxel

from src.entities.player import Player
from src.core.constants import *

# Define key constants for the mock
KEY_RIGHT = 3
KEY_LEFT = 2
KEY_SPACE = 32
KEY_DOWN = 1
KEY_UP = 0

@pytest.fixture
def mock_level():
    level = MagicMock()
    level.check_collision.return_value = False
    level.check_hazard.return_value = False
    level.is_switch.return_value = False
    return level

@pytest.fixture
def mock_slime():
    slime = MagicMock()
    slime.x = 100
    slime.y = 100
    slime.w = 8
    slime.h = 8
    slime.juice = 100
    return slime

def test_walk_logic(mock_level, mock_slime):
    player = Player(0, 0, mock_level)
    
    # Patch pyxel INSIDE the player module
    with patch("src.entities.player.pyxel") as m_pyxel:
        m_pyxel.KEY_RIGHT = KEY_RIGHT
        m_pyxel.KEY_LEFT = KEY_LEFT
        m_pyxel.KEY_SPACE = KEY_SPACE
        m_pyxel.btn.side_effect = lambda key: key == KEY_RIGHT
        m_pyxel.btnp.return_value = False
        m_pyxel.btnr.return_value = False
        
        player.handle_input(mock_slime)
        assert player.dx == WALK_ACCEL
        player.handle_input(mock_slime)
        assert player.dx == WALK_ACCEL * 2
        
        # Cap speed
        for _ in range(10):
            player.handle_input(mock_slime)
        assert player.dx == MAX_WALK_SPEED

    # Test Friction
    with patch("src.entities.player.pyxel") as m_pyxel:
        m_pyxel.btn.return_value = False
        m_pyxel.btnp.return_value = False
        m_pyxel.btnr.return_value = False
        # Current dx is MAX_WALK_SPEED
        player.handle_input(mock_slime)
        assert player.dx == MAX_WALK_SPEED - WALK_FRICTION
        
        # Stop eventually
        for _ in range(10):
            player.handle_input(mock_slime)
        assert player.dx == 0

def test_jump_logic(mock_level, mock_slime):
    player = Player(0, 0, mock_level)
    player.is_grounded = True
    
    with patch("src.entities.player.pyxel") as m_pyxel:
        m_pyxel.KEY_SPACE = KEY_SPACE
        m_pyxel.btnp.side_effect = lambda key: key == KEY_SPACE
        m_pyxel.btn.return_value = False
        m_pyxel.btnr.return_value = False
        
        player.update_timers()
        player.handle_input(mock_slime)
        assert player.dy == JUMP_FORCE
        assert player.is_grounded == False

    # Test Gravity
    player.dy = -2.0
    player.is_grounded = False
    player.apply_physics()
    assert player.dy == -2.0 + GRAVITY

def test_wall_logic(mock_level, mock_slime):
    player = Player(10, 10, mock_level)
    player.is_grounded = False
    player.dy = 1.0 # Falling
    
    def collision_side_effect(x, y, w, h):
        if x >= 10 + 8: # Right side of player at 10,10 with w=8
            return True
        return False
    
    mock_level.check_collision.side_effect = collision_side_effect
    
    with patch("src.entities.player.pyxel") as m_pyxel:
        m_pyxel.KEY_RIGHT = KEY_RIGHT
        m_pyxel.btn.side_effect = lambda key: key == KEY_RIGHT
        m_pyxel.btnp.return_value = False
        m_pyxel.btnr.return_value = False
        
        player.handle_input(mock_slime)
        assert player.is_wall_sliding == True
        
        player.apply_physics()
        assert player.dy == 1.0 + (GRAVITY * WALL_SLIDE_FRICTION)
        
    # Wall Jump
    player.jump_buffer_timer = 1
    with patch("src.entities.player.pyxel") as m_pyxel:
        m_pyxel.KEY_RIGHT = KEY_RIGHT
        m_pyxel.btn.side_effect = lambda key: key == KEY_RIGHT
        m_pyxel.btnp.return_value = False
        m_pyxel.btnr.return_value = False
        
        player.handle_input(mock_slime)
        assert player.dx == -WALL_JUMP_X_IMPULSE
        assert player.dy == WALL_JUMP_Y_FORCE
