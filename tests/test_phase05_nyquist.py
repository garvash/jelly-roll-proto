import pytest
from unittest.mock import MagicMock, patch
import sys
from src.core.constants import PLAYER_MAX_HP, INVULN_DURATION, VIEWPORT_W, VIEWPORT_H

# Mock pyxel locally
mock_pyxel = MagicMock()
sys.modules['pyxel'] = mock_pyxel

def test_input_ignored_during_knockback():
    mock_pyxel.btn.return_value = True # Holding right

    with patch('src.entities.player.input_manager') as m_input:
        m_input.btn.return_value = True  # Holding right
        m_input.btnp.return_value = False
        m_input.btnr.return_value = False

        from src.entities.player import Player
        from src.entities.slime import Slime

        player = Player(100, 100, MagicMock())
        slime = Slime(100, 100)

        # Trigger knockback (sets timer to 10)
        player.take_damage(1, source_x=110)
        assert player.knockback_timer == 10

        # Update should ignore move input (btn) but still apply physics
        player.update(slime)

        # If handle_input is skipped, dx remains at knockback value.
        assert player.dx == -1.0  # Knockback away from 110 (KNOCKBACK_FORCE_X=1.0)
        
def test_invuln_timer_decreases():
    player_mock_pyxel = MagicMock()
    with patch('src.entities.player.pyxel', player_mock_pyxel):
        from src.entities.player import Player
        player = Player(100, 100, MagicMock())
        player.take_damage(1)
        assert player.invuln_timer == INVULN_DURATION
        
        player.update_timers()
        assert player.invuln_timer == INVULN_DURATION - 1

def test_bat_range_limit():
    from src.entities.enemies import Bat
    bat = Bat(100, 100)
    player = MagicMock()
    player.x = 250 # Far away (limit is 80)
    player.y = 150
    player.w = 10
    player.h = 14
    
    level_map = MagicMock()
    bat.update(player, level_map)
    assert bat.state == "HANGING"
    
    player.x = 110 # Close
    bat.update(player, level_map)
    assert bat.state == "DIVING"

def test_room_spawn_update():
    # Use real main.Game to test integration
    from src.level.world import LevelBounds, WorldManager
    with patch('pyxel.init'), patch('pyxel.load'), patch('pyxel.run'), \
         patch('src.entities.player.input_manager') as m_input:
        m_input.btn.return_value = False
        m_input.btnp.return_value = False
        m_input.btnr.return_value = False

        from main import Game
        with patch.object(Game, 'spawn_enemies'):
            game = Game()
        game.game_state = "PLAYING"  # Skip title screen for gameplay test
        game.level_map = MagicMock()
        game.level_map.find_tile.return_value = None
        game.level_map.entities = []
        # Set up two adjacent rooms so room transition can fire
        game.world = WorldManager([
            LevelBounds("room_0", 0, 0, VIEWPORT_W, VIEWPORT_H),
            LevelBounds("room_1", VIEWPORT_W, 0, VIEWPORT_W, VIEWPORT_H),
        ])
        # Place player inside room_0 and sync spawn position
        game.player.x = 50
        game.player.y = 50
        game.room_spawn_x = 50
        game.room_spawn_y = 50
        game.world.detect_level(50, 50)
        game.cam_x, game.cam_y = 0, 0

        # Initial spawn
        assert game.room_spawn_x == game.player.x
        assert game.room_spawn_y == game.player.y

        # Move to next room — put player well inside room_1
        game.player.x = VIEWPORT_W + 50
        game.update()

        # After transition trigger, cam updates via transition system
        # Advance transition frames to complete the slide
        for _ in range(60):
            game.update()

        assert game.cam_x == VIEWPORT_W
        assert game.room_spawn_x == VIEWPORT_W + 50
