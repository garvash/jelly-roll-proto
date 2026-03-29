import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock pyxel to avoid issues with display/initialization during tests
mock_pyxel = MagicMock()

# Define common constants to avoid issues if code expects specific values
mock_pyxel.KEY_LEFT = 1
mock_pyxel.KEY_RIGHT = 2
mock_pyxel.KEY_UP = 3
mock_pyxel.KEY_DOWN = 4
mock_pyxel.KEY_SPACE = 5
mock_pyxel.KEY_X = 6
mock_pyxel.KEY_Z = 7
mock_pyxel.KEY_Q = 8
mock_pyxel.KEY_R = 9
mock_pyxel.frame_count = 0

# Default return values for input functions
mock_pyxel.btn.return_value = False
mock_pyxel.btnp.return_value = False
mock_pyxel.btnr.return_value = False

sys.modules["pyxel"] = mock_pyxel

# Also force update modules that might have already imported the real pyxel
import src.entities.enemies
import src.entities.player
import src.entities.projectile
import src.entities.slime
import src.level.map
import main

src.entities.enemies.pyxel = mock_pyxel
src.entities.player.pyxel = mock_pyxel
src.entities.projectile.pyxel = mock_pyxel
src.entities.slime.pyxel = mock_pyxel
src.level.map.pyxel = mock_pyxel
main.pyxel = mock_pyxel

# Also mock the input abstraction layer used by player.py
import src.core.input as _input_mod
_input_mod.pyxel = mock_pyxel

from src.entities.enemies import Snail, Bat
from src.entities.player import Player
from src.entities.projectile import Projectile
from src.entities.slime import Slime
from main import Game
from src.core.constants import VIEWPORT_W, VIEWPORT_H

def test_bat_returning_state():
    level_map = MagicMock()
    level_map.check_collision.return_value = False
    
    # Bat starts at y=10
    bat = Bat(100, 10)
    player = MagicMock()
    player.x = 110
    player.y = 50
    player.w = 8
    player.h = 8
    
    # Trigger DIVING
    bat.update(player, level_map)
    assert bat.state == "DIVING"
    
    # Trigger RETURNING by going past depth limit
    bat.y = 111 # 111 > 10 + 100 is true
    bat.update(player, level_map)
    # During this update, y increases by 3 (to 114) and THEN state becomes RETURNING
    assert bat.state == "RETURNING"
    last_y = bat.y
    
    # Verify it moves UP towards start_y
    bat.update(player, level_map)
    assert bat.y < last_y
    
    # Verify it returns to HANGING when reached start_y
    bat.y = 10.5
    bat.update(player, level_map)
    # 10.5 > 10, so it does 10.5 - 1.5 = 9.0
    assert bat.y == 9.0
    bat.update(player, level_map)
    # 9.0 > 10 is false, so it snaps to start_y and becomes HANGING
    assert bat.y == 10
    assert bat.state == "HANGING"

def test_spawning_logic():
    # Mock pyxel methods called in Game.__init__
    with patch('pyxel.init'), patch('pyxel.load'), patch('pyxel.run'):
        game = Game()
        game.level_map = MagicMock()
        game.level_map.find_tile.return_value = None # Fix unpacking error
        game.cam_x = 0
        game.cam_y = 0
        
        # Mock a Snail at (8, 8) and a Bat at (16, 16)
        def mock_get_tile(tx, ty):
            if tx == 1 and ty == 1: return (0, 2) # Snail
            if tx == 2 and ty == 2: return (0, 3) # Bat
            return (0, 0)
        
        game.level_map.get_tile.side_effect = mock_get_tile
        
        game.spawn_enemies()
        
        # Check if enemies were added
        assert len(game.enemies) == 2
        assert isinstance(game.enemies[0], Snail)
        assert game.enemies[0].x == 8
        assert game.enemies[0].y == 8
        assert isinstance(game.enemies[1], Bat)
        assert game.enemies[1].x == 16
        assert game.enemies[1].y == 16
        
        # Verify tiles were removed
        assert game.level_map.remove_tile.call_count == 2
        game.level_map.remove_tile.assert_any_call(1, 1)
        game.level_map.remove_tile.assert_any_call(2, 2)

def test_duplication_prevention():
    from src.level.world import LevelBounds, WorldManager
    with patch('pyxel.init'), patch('pyxel.load'), patch('pyxel.run'):
        game = Game()
        game.level_map = MagicMock()
        game.level_map.get_tile.return_value = (0, 0)
        game.level_map.find_tile.return_value = None # Fix unpacking error
        # Set up two adjacent rooms
        game.world = WorldManager([
            LevelBounds("room_0", 0, 0, VIEWPORT_W, VIEWPORT_H),
            LevelBounds("room_1", VIEWPORT_W, 0, VIEWPORT_W, VIEWPORT_H),
        ])
        game.world.detect_level(10, 10)
        game.cam_x, game.cam_y = 0, 0
        game.rooms_visited = {"room_0"}
        game.player.x = 10
        game.player.y = 10

        # First visit already recorded
        game.update()
        assert "room_0" in game.rooms_visited

        # Manually clear enemies to see if they respawn
        game.enemies = []

        # Second update in same room
        game.update()

        # Let's mock spawn_enemies to see if it's called
        with patch.object(Game, 'spawn_enemies') as mock_spawn:
            # Move player to next room
            game.player.x = VIEWPORT_W + 50
            game.update()
            # Advance transition to completion
            for _ in range(60):
                game.update()
            assert game.cam_x == VIEWPORT_W
            assert mock_spawn.call_count == 1

            game.update() # Still in room_1
            assert mock_spawn.call_count == 1 # Still 1

def test_combat_projectile_collision():
    with patch('pyxel.init'), patch('pyxel.load'), patch('pyxel.run'):
        game = Game()
        game.level_map = MagicMock() # Correctly replace level_map
        game.level_map.find_tile.return_value = None
        game.level_map.check_collision.return_value = False
        game.level_map.check_hazard.return_value = False
        enemy = Snail(100, 100)
        game.enemies = [enemy]
        
        # Create a projectile colliding with enemy
        proj = Projectile(100, 100, 1, 0, game.level_map)
        game.projectiles = [proj]
        
        # Trigger combat collision logic in update
        for e in game.enemies:
            for p in game.projectiles:
                if p.is_active and e.check_collision(p.x, p.y, p.w, p.h):
                    e.take_damage()
                    p.is_active = False
        
        assert enemy.hp == 0
        assert enemy.is_alive == False
        assert proj.is_active == False

def test_combat_drill_collision():
    with patch('pyxel.init'), patch('pyxel.load'), patch('pyxel.run'):
        game = Game()
        game.level_map = MagicMock() # Correctly replace level_map
        game.level_map.find_tile.return_value = None
        enemy = Snail(100, 100)
        game.enemies = [enemy]
        game.player.state = "DIVING"
        game.player.x = 100
        game.player.y = 100
        game.player.w = 8
        game.player.h = 8
        game.slime.juice = 50
        
        # Combat loop from Game.update
        for e in game.enemies:
            if game.player.state == "DIVING" and e.check_collision(game.player.x, game.player.y, game.player.w, game.player.h):
                e.take_damage()
                game.slime.refill(10)
                game.player.on_block_break()
        
        assert enemy.hp == 0
        assert enemy.is_alive == False
        assert game.slime.juice == 60

def test_player_contact_damage():
    level_map = MagicMock()
    level_map.check_collision.return_value = False
    
    snail = Snail(10, 10)
    player = MagicMock()
    player.x = 12
    player.y = 12
    player.w = 8
    player.h = 8
    
    snail.update(player, level_map)
    
    # Verify player.take_damage was called
    player.take_damage.assert_called_once()
    # Arg 1 is amount, Arg 2 is source_x
    args, kwargs = player.take_damage.call_args
    assert args[0] == 1
    assert args[1] == snail.x + snail.w / 2
