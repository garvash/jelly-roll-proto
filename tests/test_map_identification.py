import pytest
from unittest.mock import MagicMock, patch
import sys

# Ensure pyxel is mocked consistently
mock_pyxel = MagicMock()
sys.modules['pyxel'] = mock_pyxel

from src.level.map import LevelMap
import src.level.map
import src.core.constants

def test_tile_identification():
    # Define constants locally for comparison
    T_EMPTY = (0, 0)
    T_SOLID = (0, 1)
    T_HAZARD = (1, 1)
    T_DESTRUCTIBLE = (2, 1)
    T_GATE = (3, 1)

    # Patch them everywhere they might be used
    with patch('src.level.map.TILE_EMPTY', T_EMPTY), \
         patch('src.level.map.TILE_SOLID', T_SOLID), \
         patch('src.level.map.TILE_HAZARD', T_HAZARD), \
         patch('src.level.map.TILE_DESTRUCTIBLE', T_DESTRUCTIBLE), \
         patch('src.level.map.TILE_GATE', T_GATE):
        
        mock_tilemap = MagicMock()
        mock_pyxel.tilemaps.__getitem__.return_value = mock_tilemap
        
        level_map = LevelMap(0)
        
        def mock_pget(tx, ty):
            if tx == 0: return T_EMPTY
            if tx == 1: return T_SOLID
            if tx == 2: return T_HAZARD
            if tx == 3: return T_DESTRUCTIBLE
            return T_EMPTY

        mock_tilemap.pget.side_effect = mock_pget
        
        # Check values directly to be sure
        import src.level.map
        # print(f"TEST DEBUG: map.TILE_SOLID={src.level.map.TILE_SOLID}")
        
        # is_solid should return True for both T_SOLID and T_DESTRUCTIBLE
        assert level_map.is_solid(1, 0) == True
        assert level_map.is_solid(3, 0) == True
        assert level_map.is_solid(0, 0) == False
        assert level_map.is_solid(2, 0) == False
        
        assert level_map.is_hazard(2, 0) == True
        assert level_map.is_hazard(1, 0) == False
        
        assert level_map.is_destructible(3, 0) == True
        assert level_map.is_destructible(1, 0) == False

def test_check_hazard():
    T_EMPTY = (0, 0)
    T_HAZARD = (1, 1)
    
    with patch('src.level.map.TILE_EMPTY', T_EMPTY), \
         patch('src.level.map.TILE_HAZARD', T_HAZARD):
        
        mock_tilemap = MagicMock()
        mock_pyxel.tilemaps.__getitem__.return_value = mock_tilemap
        
        level_map = LevelMap(0)
        
        def mock_pget(tx, ty):
            if tx == 2: return T_HAZARD
            return T_EMPTY
            
        mock_tilemap.pget.side_effect = mock_pget
        
        # Hazard at tx=2 (x=16 to 23)
        # Overlaps at x=15 (tiles 1 and 2)
        assert level_map.check_hazard(15, 0, 8, 8) == True
        # Doesn't overlap at x=0 (tile 0) or x=24 (tile 3)
        assert level_map.check_hazard(0, 0, 8, 8) == False
        assert level_map.check_hazard(24, 0, 8, 8) == False

def test_get_destructible_at():
    T_EMPTY = (0, 0)
    T_DESTRUCTIBLE = (2, 1)
    
    with patch('src.level.map.TILE_EMPTY', T_EMPTY), \
         patch('src.level.map.TILE_DESTRUCTIBLE', T_DESTRUCTIBLE):
        
        mock_tilemap = MagicMock()
        mock_pyxel.tilemaps.__getitem__.return_value = mock_tilemap
        
        level_map = LevelMap(0)
        
        # Place destructible at (3, 1) -> x=24..31, y=8..15
        def mock_pget(tx, ty):
            if tx == 3 and ty == 1: return T_DESTRUCTIBLE
            return T_EMPTY
            
        mock_tilemap.pget.side_effect = mock_pget
        
        # Overlaps (x=20..27, y=10..17) - hits (3, 1)
        assert level_map.get_destructible_at(20, 10, 8, 8) == (3, 1)
        # Doesn't overlap
        assert level_map.get_destructible_at(0, 0, 8, 8) == None
