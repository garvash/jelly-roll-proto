"""Regression tests for Phase 21 LDtk 8px-to-16px migration output (D-25).

These tests validate that the migrated output.ldtk and simplified exports
maintain correct structure and 16px alignment. They load actual migrated
files (not mocks) to catch regressions if the migration script is re-run
or the LDtk project is regenerated.
"""
import json
import os

import pytest

# Resolve project root relative to this test file (tests/ -> project root).
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OUTPUT_LDTK = os.path.join(_PROJECT_ROOT, "assets", "output.ldtk")
_SIMPLIFIED_DIR = os.path.join(_PROJECT_ROOT, "assets", "output", "simplified")
_LEVEL_0_CSV = os.path.join(_SIMPLIFIED_DIR, "Level_0", "IntGrid.csv")

# Grid constants
_EXPECTED_GRID = 16
_STANDARD_ROOM_COLS = 20  # 320px / 16px
_STANDARD_ROOM_ROWS = 11  # 176px / 16px


@pytest.fixture(scope="module")
def ldtk_data():
    """Load and cache output.ldtk for all tests in this module."""
    with open(_OUTPUT_LDTK, "r", encoding="utf-8") as f:
        return json.load(f)


def test_ldtk_default_grid_size_is_16(ldtk_data):
    """output.ldtk defaultGridSize must be 16 after migration (LDTK-02)."""
    assert ldtk_data["defaultGridSize"] == _EXPECTED_GRID, (
        f"defaultGridSize is {ldtk_data['defaultGridSize']}, expected {_EXPECTED_GRID}"
    )


def test_intgrid_csv_dimensions_20x11():
    """Level_0 IntGrid.csv must be 20 columns x 11 rows after downsampling (LDTK-02)."""
    with open(_LEVEL_0_CSV, "r") as f:
        rows = [line.strip() for line in f if line.strip()]

    assert len(rows) == _STANDARD_ROOM_ROWS, (
        f"IntGrid.csv has {len(rows)} rows, expected {_STANDARD_ROOM_ROWS}"
    )

    for i, row in enumerate(rows):
        values = [v for v in row.split(",") if v.strip() != ""]
        assert len(values) == _STANDARD_ROOM_COLS, (
            f"IntGrid.csv row {i} has {len(values)} values, expected {_STANDARD_ROOM_COLS}"
        )


def test_autotile_src_coords_16px_aligned(ldtk_data):
    """All autoLayerTile src coords in Level_0 must be multiples of 16 (LDTK-03).

    Since the tileset was upscaled 2x (8px -> 16px tiles), all src coordinates
    should be even multiples of the new tile size.
    """
    level_0 = ldtk_data["levels"][0]
    for layer in level_0.get("layerInstances", []):
        tiles = layer.get("autoLayerTiles", [])
        if not tiles:
            continue
        for tile in tiles:
            src_x, src_y = tile["src"]
            assert src_x % _EXPECTED_GRID == 0, (
                f"autoLayerTile src[0]={src_x} not aligned to {_EXPECTED_GRID}px "
                f"(px={tile['px']})"
            )
            assert src_y % _EXPECTED_GRID == 0, (
                f"autoLayerTile src[1]={src_y} not aligned to {_EXPECTED_GRID}px "
                f"(px={tile['px']})"
            )


def test_entity_positions_16px_snapped(ldtk_data):
    """All entity px values in Level_0 must be multiples of 16 (D-13, D-14)."""
    level_0 = ldtk_data["levels"][0]
    for layer in level_0.get("layerInstances", []):
        for entity in layer.get("entityInstances", []):
            px = entity.get("px", [])
            if len(px) < 2:
                continue
            ident = entity.get("__identifier", "unknown")
            assert px[0] % _EXPECTED_GRID == 0, (
                f"Entity {ident} px[0]={px[0]} not snapped to {_EXPECTED_GRID}px"
            )
            assert px[1] % _EXPECTED_GRID == 0, (
                f"Entity {ident} px[1]={px[1]} not snapped to {_EXPECTED_GRID}px"
            )


def test_tileset_relpath_cavern(ldtk_data):
    """Tileset uid=64 must have relPath 'tilesets/cavern.png' (LDTK-04)."""
    tilesets = ldtk_data.get("defs", {}).get("tilesets", [])
    ts_64 = None
    for ts in tilesets:
        if ts.get("uid") == 64:
            ts_64 = ts
            break
    assert ts_64 is not None, "Tileset uid=64 not found in defs.tilesets"
    assert ts_64["relPath"] == "tilesets/cavern.png", (
        f"Tileset uid=64 relPath is '{ts_64['relPath']}', "
        f"expected 'tilesets/cavern.png'"
    )
    assert ts_64["tileGridSize"] == _EXPECTED_GRID, (
        f"Tileset uid=64 tileGridSize is {ts_64['tileGridSize']}, "
        f"expected {_EXPECTED_GRID}"
    )


def test_layer_grid_sizes_are_16(ldtk_data):
    """All layer definitions must have gridSize=16 (LDTK-02)."""
    layers = ldtk_data.get("defs", {}).get("layers", [])
    for layer in layers:
        grid = layer.get("gridSize")
        ident = layer.get("identifier", "unknown")
        assert grid == _EXPECTED_GRID, (
            f"Layer '{ident}' gridSize is {grid}, expected {_EXPECTED_GRID}"
        )


def test_autotile_px_positions_16px_aligned(ldtk_data):
    """All surviving autoLayerTile px positions must be 16px-aligned (filtered)."""
    level_0 = ldtk_data["levels"][0]
    for layer in level_0.get("layerInstances", []):
        tiles = layer.get("autoLayerTiles", [])
        for tile in tiles:
            px_x, px_y = tile["px"]
            assert px_x % _EXPECTED_GRID == 0, (
                f"autoLayerTile px[0]={px_x} not aligned to {_EXPECTED_GRID}px"
            )
            assert px_y % _EXPECTED_GRID == 0, (
                f"autoLayerTile px[1]={px_y} not aligned to {_EXPECTED_GRID}px"
            )
