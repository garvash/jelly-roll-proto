import pytest
from unittest.mock import MagicMock
from src.entities.enemies import Snail, Bat
from src.entities.player import Player

def test_snail_turn_at_wall():
    level_map = MagicMock()
    # Mock collision at x=10+0.5=10.5
    def mock_collision(x, y, w, h):
        return x > 10
    level_map.check_collision = mock_collision
    
    snail = Snail(10, 10)
    snail.dx = 0.5
    
    player = MagicMock()
    player.x = 0
    player.y = 0
    player.w = 10
    player.h = 14
    
    snail.update(player, level_map)
    
    assert snail.dx == -0.5
    assert snail.facing_right == False

def test_snail_turn_at_ledge():
    level_map = MagicMock()
    # Mock ground only at current position, not ahead
    def mock_collision(x, y, w, h):
        if y > 10: # Ground check
            return x < 11
        return False
    level_map.check_collision = mock_collision
    
    snail = Snail(10, 10)
    snail.dx = 0.5
    
    player = MagicMock()
    player.x = 0
    player.y = 0
    player.w = 10
    player.h = 14
    
    snail.update(player, level_map)
    
    assert snail.dx == -0.5

def test_bat_dive_logic():
    level_map = MagicMock()
    level_map.check_collision.return_value = False
    
    bat = Bat(100, 10)
    player = MagicMock()
    player.x = 110 # Close horizontally
    player.y = 50  # Below bat
    player.w = 10
    player.h = 14
    
    bat.update(player, level_map)
    assert bat.state == "DIVING"
    
    bat.update(player, level_map)
    assert bat.y > 10 # Moving down

def test_enemy_death():
    snail = Snail(10, 10)
    snail.take_damage()
    assert snail.is_alive == False
