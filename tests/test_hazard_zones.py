"""Tests for zone hazard tile system (D-14): water, acid, lava passable zones."""
import pytest
from unittest.mock import MagicMock, patch
from src.core.constants import (
    TILE_WATER, TILE_ACID, TILE_LAVA, TILE_SOLID,
    HAZARD_DRAIN_RATES, TILE_SIZE
)


def make_level_map(**collision_tiles):
    """Create a LevelMap with mocked pyxel, using provided collision data.

    Args:
        **collision_tiles: keyword args ignored, pass collision_data directly.
    """
    with patch("src.level.map.pyxel"):
        from src.level.map import LevelMap
        lm = LevelMap()
        return lm


class TestGetZoneHazardType:
    def test_returns_water(self):
        """get_zone_hazard_type returns TILE_WATER when overlapping water tile."""
        lm = make_level_map()
        lm.collision_data = {(5, 5): TILE_WATER}
        result = lm.get_zone_hazard_type(40, 40, 8, 8)  # x=40 -> tx=5
        assert result == TILE_WATER

    def test_returns_none_for_empty(self):
        """get_zone_hazard_type returns None when no zone hazard tiles."""
        lm = make_level_map()
        lm.collision_data = {}
        result = lm.get_zone_hazard_type(40, 40, 8, 8)
        assert result is None

    def test_returns_worst_drain(self):
        """get_zone_hazard_type returns highest drain tile when overlapping multiple."""
        lm = make_level_map()
        lm.collision_data = {
            (5, 5): TILE_WATER,
            (5, 6): TILE_LAVA,
        }
        # AABB covers both tiles (y=40 to y+16-1=55 -> ty=5 to ty=6)
        result = lm.get_zone_hazard_type(40, 40, 8, 16)
        assert result == TILE_LAVA

    def test_zone_tiles_not_solid(self):
        """Zone hazard tiles must NOT be solid (player passes through them)."""
        lm = make_level_map()
        lm.collision_data = {(5, 5): TILE_WATER}
        assert lm.is_solid(5, 5) is False

        lm.collision_data = {(5, 5): TILE_ACID}
        assert lm.is_solid(5, 5) is False

        lm.collision_data = {(5, 5): TILE_LAVA}
        assert lm.is_solid(5, 5) is False

    def test_zone_tiles_in_val_to_tile_mapping(self):
        """Verify val_to_tile maps IntGrid 6->WATER, 7->ACID, 8->LAVA."""
        # Read the source to check the mapping is correct
        with open("src/level/map.py") as f:
            source = f.read()
        assert "6: TILE_WATER" in source
        assert "7: TILE_ACID" in source
        assert "8: TILE_LAVA" in source
