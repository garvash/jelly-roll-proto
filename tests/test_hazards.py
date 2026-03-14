import pytest
from unittest.mock import MagicMock
from src.entities.player import Player
from src.core.constants import PLAYER_MAX_HP

def test_player_damage_on_hazard():
    level_map = MagicMock()
    level_map.check_hazard.return_value = True
    level_map.check_collision.return_value = False
    
    game = MagicMock()
    game.room_spawn_x = 40
    game.room_spawn_y = 40
    
    player = Player(10, 10, level_map, game)
    
    # Take damage from hazard
    player.move_and_collide()
    
    # Expect HP reduction and teleport to room spawn
    assert player.hp == PLAYER_MAX_HP - 1
    assert player.x == 40
    assert player.y == 40
    assert player.is_alive == True

def test_player_death_on_repeated_hazard():
    level_map = MagicMock()
    level_map.check_hazard.return_value = True
    level_map.check_collision.return_value = False
    
    game = MagicMock()
    game.room_spawn_x = 40
    game.room_spawn_y = 40
    
    player = Player(10, 10, level_map, game)
    
    # Take damage 3 times
    for _ in range(PLAYER_MAX_HP):
        player.move_and_collide()
        # Reset invuln to allow next hit (since move_and_collide triggers it)
        player.invuln_timer = 0
    
    assert player.hp <= 0
    assert player.is_alive == False
