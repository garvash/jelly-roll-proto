import pytest
from unittest.mock import MagicMock, patch
import sys

# Ensure pyxel is mocked consistently
if 'pyxel' not in sys.modules:
    mock_pyxel = MagicMock()
    sys.modules['pyxel'] = mock_pyxel
else:
    mock_pyxel = sys.modules['pyxel']

from src.level.map import LevelMap
from src.core.constants import TILE_SIZE, TILE_SOLID, TILE_HAZARD, TILE_DESTRUCTIBLE, TILE_EMPTY

def test_tile_identification():
    level_map = LevelMap(0)
    
    # Mock tilemap(0).pget
    mock_tilemap = MagicMock()
    # Reset any existing mock behavior for pyxel.tilemaps
    mock_pyxel.tilemaps.__getitem__.return_value = mock_tilemap
    
    # Setup mock data:
    # tx=0 -> Empty
    # tx=1 -> Solid
    # tx=2 -> Hazard
    # tx=3 -> Destructible
    
    def mock_pget(tx, ty):
        if tx == 0: return TILE_EMPTY
        if tx == 1: return TILE_SOLID
        if tx == 2: return TILE_HAZARD
        if tx == 3: return TILE_DESTRUCTIBLE
        return TILE_EMPTY

    mock_tilemap.pget.side_effect = mock_pget
    
    # is_solid should return True for both TILE_SOLID and TILE_DESTRUCTIBLE
    assert level_map.is_solid(1, 0) == True
    assert level_map.is_solid(3, 0) == True
    assert level_map.is_solid(0, 0) == False
    assert level_map.is_solid(2, 0) == False
    
    assert level_map.is_hazard(2, 0) == True
    assert level_map.is_hazard(1, 0) == False
    
    assert level_map.is_destructible(3, 0) == True
    assert level_map.is_destructible(1, 0) == False

def test_check_hazard():
    level_map = LevelMap(0)
    mock_tilemap = MagicMock()
    mock_pyxel.tilemaps.__getitem__.return_value = mock_tilemap
    
    def mock_pget(tx, ty):
        if tx == 2: return TILE_HAZARD
        return TILE_EMPTY
        
    mock_tilemap.pget.side_effect = mock_pget
    
    # Hazard at tx=2 (x=16 to 23)
    # Overlaps at x=15 (tiles 1 and 2)
    assert level_map.check_hazard(15, 0, 8, 8) == True
    # Doesn't overlap at x=0 (tile 0) or x=24 (tile 3)
    assert level_map.check_hazard(0, 0, 8, 8) == False
    assert level_map.check_hazard(24, 0, 8, 8) == False

def test_get_destructible_at():
    level_map = LevelMap(0)
    mock_tilemap = MagicMock()
    mock_pyxel.tilemaps.__getitem__.return_value = mock_tilemap
    
    # Place destructible at (3, 1) -> x=24..31, y=8..15
    def mock_pget(tx, ty):
        if tx == 3 and ty == 1: return TILE_DESTRUCTIBLE
        return TILE_EMPTY
        
    mock_tilemap.pget.side_effect = mock_pget
    
    # Overlaps (x=20..27, y=10..17) - hits (3, 1)
    assert level_map.get_destructible_at(20, 10, 8, 8) == (3, 1)
    # Doesn't overlap
    assert level_map.get_destructible_at(0, 0, 8, 8) == None
