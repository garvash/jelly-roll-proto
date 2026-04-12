"""Tests for zone hazard tile system (D-14): water, acid, lava passable zones."""
import pytest
from unittest.mock import MagicMock, patch
from src.core.constants import (
    HAZARD_DRAIN_RATES, TILE_SIZE
)
from src.core import schema

# IntGrid values for collision_data (from entity-schema.json)
INTGRID_WATER = 6   # IntGrid value for water
INTGRID_ACID = 7    # IntGrid value for acid
INTGRID_LAVA = 8    # IntGrid value for lava
INTGRID_SOLID = 1   # IntGrid value for solid


@pytest.fixture(autouse=True)
def init_schema():
    """Initialize schema before each test so map.py behavior caches work."""
    schema.init("assets/entity-schema.json")


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
        """get_zone_hazard_type returns INTGRID_WATER when overlapping water tile."""
        lm = make_level_map()
        lm.collision_data = {(5, 5): INTGRID_WATER}
        result = lm.get_zone_hazard_type(80, 80, 8, 8)  # x=80 -> tx=5 (80//16)
        assert result == INTGRID_WATER

    def test_returns_none_for_empty(self):
        """get_zone_hazard_type returns None when no zone hazard tiles."""
        lm = make_level_map()
        lm.collision_data = {}
        result = lm.get_zone_hazard_type(80, 80, 8, 8)
        assert result is None

    def test_returns_worst_drain(self):
        """get_zone_hazard_type returns highest drain tile when overlapping multiple."""
        lm = make_level_map()
        lm.collision_data = {
            (5, 5): INTGRID_WATER,
            (5, 6): INTGRID_LAVA,
        }
        # AABB covers both tiles (y=80 to y+32-1=111 -> ty=5 to ty=6)
        result = lm.get_zone_hazard_type(80, 80, 8, 32)
        assert result == INTGRID_LAVA

    def test_zone_tiles_not_solid(self):
        """Zone hazard tiles must NOT be solid (player passes through them)."""
        lm = make_level_map()
        lm.collision_data = {(5, 5): INTGRID_WATER}
        assert lm.is_solid(5, 5) is False

        lm.collision_data = {(5, 5): INTGRID_ACID}
        assert lm.is_solid(5, 5) is False

        lm.collision_data = {(5, 5): INTGRID_LAVA}
        assert lm.is_solid(5, 5) is False

    def test_zone_hazard_drain_rates_use_int_keys(self):
        """Verify HAZARD_DRAIN_RATES uses IntGrid int keys (6, 7, 8)."""
        assert 6 in HAZARD_DRAIN_RATES, "HAZARD_DRAIN_RATES missing IntGrid key 6 (water)"
        assert 7 in HAZARD_DRAIN_RATES, "HAZARD_DRAIN_RATES missing IntGrid key 7 (acid)"
        assert 8 in HAZARD_DRAIN_RATES, "HAZARD_DRAIN_RATES missing IntGrid key 8 (lava)"
