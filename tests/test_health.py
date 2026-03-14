import pytest
from unittest.mock import MagicMock
from src.entities.player import Player
from src.core.constants import PLAYER_MAX_HP, INVULN_DURATION

def test_player_take_damage():
    player = Player(10, 10, MagicMock())
    
    # Take 1 damage
    success = player.take_damage(1)
    
    assert success == True
    assert player.hp == PLAYER_MAX_HP - 1
    assert player.invuln_timer == INVULN_DURATION

def test_player_invulnerability():
    player = Player(10, 10, MagicMock())
    
    # First hit
    player.take_damage(1)
    initial_hp = player.hp
    
    # Second hit immediately should fail and not reduce HP
    success = player.take_damage(1)
    
    assert success == False
    assert player.hp == initial_hp

def test_player_knockback():
    player = Player(10, 10, MagicMock())
    # source is to the right
    player.take_damage(1, source_x=20)
    
    # Should move left and up
    assert player.dx < 0
    assert player.dy < 0
    assert player.knockback_timer > 0

def test_player_death():
    player = Player(10, 10, MagicMock())
    
    # Take damage equal to max HP (resetting invuln between)
    for _ in range(PLAYER_MAX_HP):
        player.take_damage(1)
        player.invuln_timer = 0
        
    assert player.hp == 0
    assert player.is_alive == False
