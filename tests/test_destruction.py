import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock pyxel before importing classes that use it
mock_pyxel = MagicMock()
sys.modules["pyxel"] = mock_pyxel

from src.entities.player import Player
from src.level.map import LevelMap
from src.entities.slime import Slime
from src.core.constants import TILE_DESTRUCTIBLE, TILE_EMPTY, JUICE_MAX, DRILL_BLOCK_REFUND

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
        # Set up a destructible tile at (0, 1) - directly below player at (0, 0)
        # Player is 8x8, so (0, 8) in pixels is (0, 1) in tiles
        self.player.y = 0
        self.player.state = "DIVING"
        self.player.dy = 4
        
        # Mock pget to return TILE_DESTRUCTIBLE for the tile below
        self.mock_tm.pget.side_effect = lambda tx, ty: TILE_DESTRUCTIBLE if tx == 0 and ty == 1 else TILE_EMPTY
        
        initial_juice = 50.0
        self.slime.juice = initial_juice
        
        # One move step should hit the tile
        self.player.move_and_collide(self.slime)
        
        # Verify tile removal was called
        self.mock_tm.pset.assert_called_with(0, 1, TILE_EMPTY)
        
        # Verify juice refund (DRILL_BLOCK_REFUND = 15.0)
        self.assertEqual(self.slime.juice, initial_juice + DRILL_BLOCK_REFUND)
        
        # Verify state is still DIVING (should continue through)
        self.assertEqual(self.player.state, "DIVING")

    def test_solid_collision_stops_drill(self):
        from src.core.constants import TILE_SOLID, DRILL_IMPACT_COST
        
        self.player.y = 0
        self.player.state = "DIVING"
        self.player.dy = 4
        
        # Mock pget to return TILE_SOLID
        self.mock_tm.pget.side_effect = lambda tx, ty: TILE_SOLID if tx == 0 and ty == 1 else TILE_EMPTY
        
        initial_juice = 50.0
        self.slime.juice = initial_juice
        
        self.player.move_and_collide(self.slime)
        
        # Verify state changed to IDLE
        self.assertEqual(self.player.state, "IDLE")
        
        # Verify juice impact cost (DRILL_IMPACT_COST = 20.0)
        self.assertEqual(self.slime.juice, initial_juice - DRILL_IMPACT_COST)

if __name__ == "__main__":
    unittest.main()
