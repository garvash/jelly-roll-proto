"""Drill-dive block destruction + solid collision integration tests.

Phase 32 D-10 / Plan 06 migration: drill block-break + impact logic moved
from Player.move_and_collide to src/fusion/drill_dive.py::on_tick + on_exit.
Tests now drive the new code path via drill_dive directly. Detailed parity
assertions live in tests/test_drill_dive_parity.py; this file retains the
LevelMap-integration smoke that previously exercised the player.py path.
"""
import unittest
from unittest.mock import MagicMock, patch
import sys
from src.core.constants import TILE_EMPTY, DRILL_BLOCK_REFUND, DRILL_IMPACT_COST
from src.core import schema

# IntGrid values for collision_data (from entity-schema.json)
INTGRID_SOLID = 1
INTGRID_DESTRUCTIBLE = 3


class TestDestruction(unittest.TestCase):
    def setUp(self):
        # Local mock to avoid global pollution
        self.mock_pyxel = MagicMock()
        # Initialize schema so map.py behavior caches work
        schema.init("assets/entity-schema.json")

    def test_block_destruction_and_refund(self):
        with patch('src.level.map.pyxel', self.mock_pyxel), \
             patch('src.entities.player.pyxel', self.mock_pyxel), \
             patch('src.entities.slime.pyxel', self.mock_pyxel):

            from src.level.map import LevelMap
            from src.entities.player import Player
            from src.entities.slime import Slime
            from src.fusion.drill_dive import DrillDive

            level_map = LevelMap(0)
            player = Player(0, 4, level_map)
            slime = Slime(0, 10)

            # Mock tilemap for the visual side
            mock_tm = MagicMock()
            self.mock_pyxel.tilemaps.__getitem__.return_value = mock_tm

            player.state = "DIVING"
            player.dy = 4

            # Setup collision data with IntGrid int
            level_map.collision_data[(0, 1)] = INTGRID_DESTRUCTIBLE

            initial_juice = 50.0
            slime.juice = initial_juice
            # Phase 32 Plan 06: drill block-break runs in drill_dive.on_tick.
            DrillDive().on_tick(player, slime, dt=1.0)

            # Should have removed from collision data
            self.assertNotIn((0, 1), level_map.collision_data)
            # Should have called pset on tilemap for visual removal
            # _pset_tile writes a 2x2 block of 8px cells for each 16px tile
            # Tile (0,1) -> cells (0,2)-(1,3), TILE_EMPTY (15,15) -> 8px UVs (30,30)-(31,31)
            mock_tm.pset.assert_any_call(0, 2, (30, 30))
            mock_tm.pset.assert_any_call(1, 2, (31, 30))
            mock_tm.pset.assert_any_call(0, 3, (30, 31))
            mock_tm.pset.assert_any_call(1, 3, (31, 31))

            self.assertEqual(slime.juice, initial_juice + DRILL_BLOCK_REFUND)
            # drill continues — on_tick returns TickResult(request_exit=False)
            # for soft blocks. Player.state stays "DIVING" (mirror retained
            # per Plan 05 Open Q #1).

    def test_solid_collision_stops_drill(self):
        with patch('src.level.map.pyxel', self.mock_pyxel), \
             patch('src.entities.player.pyxel', self.mock_pyxel), \
             patch('src.entities.slime.pyxel', self.mock_pyxel):

            from src.level.map import LevelMap
            from src.entities.player import Player
            from src.entities.slime import Slime
            from src.fusion.drill_dive import DrillDive

            level_map = LevelMap(0)
            player = Player(0, 4, level_map)
            slime = Slime(0, 10)

            # Mock tilemap
            mock_tm = MagicMock()
            self.mock_pyxel.tilemaps.__getitem__.return_value = mock_tm

            player.state = "DIVING"
            player.dy = 4

            # Setup collision data with IntGrid int
            level_map.collision_data[(0, 1)] = INTGRID_SOLID

            initial_juice = 50.0
            slime.juice = initial_juice
            # Phase 32 Plan 06: drill_dive.on_tick detects solid below + requests
            # exit; on_exit pays DRILL_IMPACT_COST and writes player.state="IDLE".
            drill = DrillDive()
            result = drill.on_tick(player, slime, dt=1.0)
            self.assertTrue(result.request_exit)
            self.assertEqual(result.exit_reason, "solid_landing")
            drill.on_exit(player, slime, "solid_landing")

            self.assertEqual(player.state, "IDLE")
            self.assertEqual(slime.juice, initial_juice - DRILL_IMPACT_COST)

if __name__ == "__main__":
    unittest.main()
