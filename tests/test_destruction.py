import unittest
from unittest.mock import MagicMock, patch
import sys
from src.core.constants import TILE_EMPTY, TILE_SOLID, TILE_DESTRUCTIBLE, DRILL_BLOCK_REFUND, DRILL_IMPACT_COST

class TestDestruction(unittest.TestCase):
    def setUp(self):
        # Local mock to avoid global pollution
        self.mock_pyxel = MagicMock()
        
    def test_block_destruction_and_refund(self):
        with patch('src.level.map.pyxel', self.mock_pyxel), \
             patch('src.entities.player.pyxel', self.mock_pyxel), \
             patch('src.entities.slime.pyxel', self.mock_pyxel):
            
            from src.level.map import LevelMap
            from src.entities.player import Player
            from src.entities.slime import Slime
            
            level_map = LevelMap(0)
            player = Player(0, 4, level_map)
            slime = Slime(0, 10)
            
            # Mock tilemap for the visual side
            mock_tm = MagicMock()
            self.mock_pyxel.tilemaps.__getitem__.return_value = mock_tm
            
            player.state = "DIVING"
            player.dy = 4
            
            # Setup collision data
            level_map.collision_data[(0, 1)] = TILE_DESTRUCTIBLE
            
            initial_juice = 50.0
            slime.juice = initial_juice
            player.move_and_collide(slime)
            
            # Should have removed from collision data
            self.assertNotIn((0, 1), level_map.collision_data)
            # Should have called pset on tilemap for visual removal
            mock_tm.pset.assert_called_with(0, 1, TILE_EMPTY)
            
            self.assertEqual(slime.juice, initial_juice + DRILL_BLOCK_REFUND)
            self.assertEqual(player.state, "DIVING")

    def test_solid_collision_stops_drill(self):
        with patch('src.level.map.pyxel', self.mock_pyxel), \
             patch('src.entities.player.pyxel', self.mock_pyxel), \
             patch('src.entities.slime.pyxel', self.mock_pyxel):
            
            from src.level.map import LevelMap
            from src.entities.player import Player
            from src.entities.slime import Slime
            
            level_map = LevelMap(0)
            player = Player(0, 4, level_map)
            slime = Slime(0, 10)
            
            # Mock tilemap
            mock_tm = MagicMock()
            self.mock_pyxel.tilemaps.__getitem__.return_value = mock_tm
            
            player.state = "DIVING"
            player.dy = 4
            
            # Setup collision data
            level_map.collision_data[(0, 1)] = TILE_SOLID
            
            initial_juice = 50.0
            slime.juice = initial_juice
            player.move_and_collide(slime)
            
            self.assertEqual(player.state, "IDLE")
            self.assertEqual(slime.juice, initial_juice - DRILL_IMPACT_COST)

if __name__ == "__main__":
    unittest.main()
