import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock pyxel
mock_pyxel = MagicMock()
sys.modules["pyxel"] = mock_pyxel

from src.entities.player import Player
from src.level.map import LevelMap
from src.entities.slime import Slime

class TestDestruction(unittest.TestCase):
    def setUp(self):
        mock_pyxel.reset_mock()
        self.level_map = LevelMap(0)
        self.player = Player(0, 0, self.level_map)
        self.slime = Slime(0, 10)
        
        # Mock tilemap
        self.mock_tm = MagicMock()
        mock_pyxel.tilemaps.__getitem__.return_value = self.mock_tm

    def test_block_destruction_and_refund(self):
        T_EMPTY = (0, 0)
        T_DESTRUCTIBLE = (2, 1)
        DRILL_BLOCK_REFUND = 15.0

        with patch('src.level.map.TILE_EMPTY', T_EMPTY), \
             patch('src.level.map.TILE_DESTRUCTIBLE', T_DESTRUCTIBLE), \
             patch('src.entities.player.TILE_EMPTY', T_EMPTY), \
             patch('src.entities.player.TILE_DESTRUCTIBLE', T_DESTRUCTIBLE), \
             patch('src.entities.player.DRILL_BLOCK_REFUND', DRILL_BLOCK_REFUND):
            
            self.player.x = 0
            self.player.y = 4
            self.player.state = "DIVING"
            self.player.dy = 4
            
            # Use T_DESTRUCTIBLE and T_EMPTY (local names)
            self.mock_tm.pget.side_effect = lambda tx, ty: T_DESTRUCTIBLE if tx == 0 and ty == 1 else T_EMPTY
            
            initial_juice = 50.0
            self.slime.juice = initial_juice
            self.player.move_and_collide(self.slime)
            
            self.mock_tm.pset.assert_called_with(0, 1, T_EMPTY)
            self.assertEqual(self.slime.juice, initial_juice + DRILL_BLOCK_REFUND)
            self.assertEqual(self.player.state, "DIVING")

    def test_solid_collision_stops_drill(self):
        T_EMPTY = (0, 0)
        T_SOLID = (0, 1)
        DRILL_IMPACT_COST = 20.0

        with patch('src.level.map.TILE_EMPTY', T_EMPTY), \
             patch('src.level.map.TILE_SOLID', T_SOLID), \
             patch('src.entities.player.TILE_EMPTY', T_EMPTY), \
             patch('src.entities.player.TILE_SOLID', T_SOLID), \
             patch('src.entities.player.DRILL_IMPACT_COST', DRILL_IMPACT_COST):
            
            self.player.x = 0
            self.player.y = 4
            self.player.state = "DIVING"
            self.player.dy = 4
            
            # Use T_SOLID and T_EMPTY (local names)
            self.mock_tm.pget.side_effect = lambda tx, ty: T_SOLID if tx == 0 and ty == 1 else T_EMPTY
            
            initial_juice = 50.0
            self.slime.juice = initial_juice
            self.player.move_and_collide(self.slime)
            
            self.assertEqual(self.player.state, "IDLE")
            self.assertEqual(self.slime.juice, initial_juice - DRILL_IMPACT_COST)

if __name__ == "__main__":
    unittest.main()
