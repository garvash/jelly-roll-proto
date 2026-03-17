import pytest
from unittest.mock import MagicMock, patch
import sys
from src.core.constants import TILE_EMPTY, TILE_SOLID, TILE_HAZARD, TILE_DESTRUCTIBLE, TILE_GATE

def test_tile_identification():
    # Mock pyxel locally for this test
    mock_pyxel = MagicMock()
    
    with patch('src.level.map.pyxel', mock_pyxel):
        from src.level.map import LevelMap
        
        level_map = LevelMap(0)
        
        # Populate collision data directly
        level_map.collision_data[(0, 0)] = TILE_EMPTY
        level_map.collision_data[(1, 0)] = TILE_SOLID
        level_map.collision_data[(2, 0)] = TILE_HAZARD
        level_map.collision_data[(3, 0)] = TILE_DESTRUCTIBLE
        
        # is_solid should return True for TILE_SOLID, TILE_DESTRUCTIBLE, and TILE_GATE
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
        level_map.collision_data[(2, 0)] = TILE_HAZARD
        
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
        level_map.collision_data[(3, 1)] = TILE_DESTRUCTIBLE
        
        # Overlaps (x=20..27, y=10..17) - hits (3, 1)
        assert level_map.get_destructible_at(20, 10, 8, 8) == (3, 1)
        # Doesn't overlap
        assert level_map.get_destructible_at(0, 0, 8, 8) == None
