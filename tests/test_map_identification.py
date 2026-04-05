import pytest
from unittest.mock import MagicMock, patch
import sys
from src.core.constants import TILE_EMPTY
from src.core import schema

# IntGrid values for collision_data (from entity-schema.json)
INTGRID_SOLID = 1
INTGRID_HAZARD = 2
INTGRID_DESTRUCTIBLE = 3


@pytest.fixture(autouse=True)
def init_schema():
    """Initialize schema before each test so map.py behavior caches work."""
    schema.init("assets/entity-schema.json")


def test_tile_identification():
    # Mock pyxel locally for this test
    mock_pyxel = MagicMock()

    with patch('src.level.map.pyxel', mock_pyxel):
        from src.level.map import LevelMap

        level_map = LevelMap(0)

        # Populate collision data with IntGrid ints
        level_map.collision_data[(0, 0)] = 0  # empty (not in any behavior set)
        level_map.collision_data[(1, 0)] = INTGRID_SOLID
        level_map.collision_data[(2, 0)] = INTGRID_HAZARD
        level_map.collision_data[(3, 0)] = INTGRID_DESTRUCTIBLE

        # is_solid should return True for INTGRID_SOLID and INTGRID_DESTRUCTIBLE
        assert level_map.is_solid(1, 0) == True
        assert level_map.is_solid(3, 0) == True
        assert level_map.is_solid(0, 0) == False
        assert level_map.is_solid(2, 0) == False

        assert level_map.is_hazard(2, 0) == True
        assert level_map.is_hazard(1, 0) == False

        assert level_map.is_destructible(3, 0) == True
        assert level_map.is_destructible(1, 0) == False

def test_check_hazard():
    mock_pyxel = MagicMock()
    with patch('src.level.map.pyxel', mock_pyxel):
        from src.level.map import LevelMap

        level_map = LevelMap(0)

        # Hazard at tx=2 (x=16 to 23)
        level_map.collision_data[(2, 0)] = INTGRID_HAZARD

        # Hazard at tx=2 (x=16 to 23)
        # Overlaps at x=15 (tiles 1 and 2)
        assert level_map.check_hazard(15, 0, 8, 8) == True
        # Doesn't overlap at x=0 (tile 0) or x=24 (tile 3)
        assert level_map.check_hazard(0, 0, 8, 8) == False
        assert level_map.check_hazard(24, 0, 8, 8) == False

def test_get_destructible_at():
    mock_pyxel = MagicMock()
    with patch('src.level.map.pyxel', mock_pyxel):
        from src.level.map import LevelMap

        level_map = LevelMap(0)

        # Place destructible at (3, 1) -> x=24..31, y=8..15
        level_map.collision_data[(3, 1)] = INTGRID_DESTRUCTIBLE

        # Overlaps (x=20..27, y=10..17) - hits (3, 1)
        assert level_map.get_destructible_at(20, 10, 8, 8) == (3, 1)
        # Doesn't overlap
        assert level_map.get_destructible_at(0, 0, 8, 8) == None
