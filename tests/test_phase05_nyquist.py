import pytest
from unittest.mock import MagicMock, patch
import sys
from src.core.constants import PLAYER_MAX_HP, INVULN_DURATION

# Mock pyxel locally
mock_pyxel = MagicMock()
sys.modules['pyxel'] = mock_pyxel

def test_input_ignored_during_knockback():
    mock_pyxel.btn.return_value = True # Holding right
    
    with patch('src.entities.player.pyxel', mock_pyxel):
        from src.entities.player import Player
        from src.entities.slime import Slime
        
        player = Player(100, 100, MagicMock())
        slime = Slime(100, 100)
        
        # Trigger knockback (sets timer to 10)
        player.take_damage(1, source_x=110)
        assert player.knockback_timer == 10
        initial_x = player.x
        
        # Update should ignore move input (btn) but still apply physics
        player.update(slime)
        
        # dx should be positive (moving away from source_x=110)
        # but the WALK_ACCEL should NOT have been added.
        # Knockback force is 2.0. Friction is 0.6.
        # 2.0 - 0.6 = 1.4? No, friction is applied in handle_input which is skipped.
        # Wait, apply_physics is called after handle_input.
        
        # Actually, if handle_input is skipped, dx remains at knockback value.
        assert player.dx == -2.0 # Knockback away from 110
        
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
    player.w = 8
    player.h = 8
    
    level_map = MagicMock()
    bat.update(player, level_map)
    assert bat.state == "HANGING"
    
    player.x = 110 # Close
    bat.update(player, level_map)
    assert bat.state == "DIVING"

def test_room_spawn_update():
    # Use real main.Game to test integration
    with patch('pyxel.init'), patch('pyxel.load'), patch('pyxel.run'):
        from main import Game
        game = Game()
        game.level_map = MagicMock()
        game.level_map.find_tile.return_value = None
        
        # Initial spawn
        assert game.room_spawn_x == game.player.x
        assert game.room_spawn_y == game.player.y
        
        # Move to next room (must exceed VIEWPORT_W=320)
        from src.core.constants import VIEWPORT_W
        game.player.x = VIEWPORT_W + 50  # Room (320, 0)
        game.update()

        assert game.cam_x == VIEWPORT_W
        assert game.room_spawn_x == VIEWPORT_W + 50
        assert game.room_spawn_y == pytest.approx(game.player.y, abs=0.5)
