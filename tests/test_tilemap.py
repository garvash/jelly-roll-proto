"""Tests for autoLayerTiles parsing and tilemap rendering (TILE-01 through TILE-04).

Phase 19, Plan 01: Verify that LDtk autoLayerTiles are parsed into pyxel.tilemaps[0]
with correct world-space coordinates, flip flag warnings, transparency skipping,
and collision/visual separation.
"""
import json
import os
import tempfile
import unittest.mock

import pytest

# Resolve project root relative to this test file (tests/ -> project root).
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _make_ldtk_data(levels):
    """Build a minimal LDtk JSON structure matching output.ldtk format.

    Args:
        levels: list of dicts, each with keys:
            identifier, worldX, worldY, pxWid, pxHei, autoLayerTiles
    Returns:
        dict matching top-level output.ldtk structure.
    """
    result_levels = []
    for lv in levels:
        result_levels.append({
            "identifier": lv.get("identifier", "Level_0"),
            "worldX": lv.get("worldX", 0),
            "worldY": lv.get("worldY", 0),
            "pxWid": lv.get("pxWid", 320),
            "pxHei": lv.get("pxHei", 176),
            "layerInstances": [
                {
                    "__identifier": "IntGrid",
                    "__type": "IntGrid",
                    "__gridSize": 16,
                    "autoLayerTiles": lv.get("autoLayerTiles", []),
                }
            ],
        })
    return {"levels": result_levels}


def _make_tile(px_x, px_y, src_x, src_y, f=0, a=1):
    """Create a single autoLayerTile entry."""
    return {"px": [px_x, px_y], "src": [src_x, src_y], "f": f, "t": 0, "d": [0, 0], "a": a}


def _write_ldtk_temp(data):
    """Write LDtk data to a temp file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".ldtk", dir=_PROJECT_ROOT)
    with os.fdopen(fd, "w") as f:
        json.dump(data, f)
    return path


@unittest.mock.patch("src.level.map.pyxel")
def test_autotiles_parsed(mock_pyxel):
    """load_autotiles_from_ldtk returns the total count of tiles loaded (TILE-01)."""
    from src.level.map import LevelMap

    tiles_lv0 = [_make_tile(0, 0, 8, 8), _make_tile(8, 0, 16, 8), _make_tile(16, 0, 24, 8)]
    tiles_lv1 = [_make_tile(0, 0, 8, 8), _make_tile(8, 0, 16, 8), _make_tile(16, 0, 24, 8)]
    data = _make_ldtk_data([
        {"identifier": "Level_0", "worldX": 0, "worldY": 0, "autoLayerTiles": tiles_lv0},
        {"identifier": "Level_1", "worldX": 320, "worldY": 0, "autoLayerTiles": tiles_lv1},
    ])
    path = _write_ldtk_temp(data)
    try:
        lm = LevelMap()
        count = lm.load_autotiles_from_ldtk(path)
        assert count == 6, f"Expected 6 tiles loaded, got {count}"
    finally:
        os.unlink(path)


@unittest.mock.patch("src.level.map.pyxel")
def test_autotiles_on_tilemap(mock_pyxel):
    """After loading, pset writes 2x2 block of 8px cells for each 16px tile (TILE-02).

    Tile at px=[16,0] src=[32,16] -> 16px coords tx=1, ty=0, u=2, v=1.
    In 8px tilemap cells: top-left (2,0)=(4,2), top-right (3,0)=(5,2),
    bottom-left (2,1)=(4,3), bottom-right (3,1)=(5,3).
    """
    from src.level.map import LevelMap

    data = _make_ldtk_data([
        {"identifier": "Level_0", "worldX": 0, "worldY": 0,
         "autoLayerTiles": [_make_tile(16, 0, 32, 16)]},
    ])
    path = _write_ldtk_temp(data)
    try:
        lm = LevelMap()
        lm.load_autotiles_from_ldtk(path)
        pset_calls = mock_pyxel.tilemaps.__getitem__().pset.call_args_list
        # 16px tile (u=2, v=1) at (tx=1, ty=0) -> 8px cells:
        expected_cells = [
            (2, 0, (4, 2)),   # top-left
            (3, 0, (5, 2)),   # top-right
            (2, 1, (4, 3)),   # bottom-left
            (3, 1, (5, 3)),   # bottom-right
        ]
        for cell in expected_cells:
            found = any(args == cell for args, _ in pset_calls)
            assert found, (
                f"Expected pset{cell} in 2x2 block but got calls: {pset_calls}"
            )
    finally:
        os.unlink(path)


@unittest.mock.patch("src.level.map.pyxel")
def test_tile_with_flip_flag_still_loads(mock_pyxel):
    """Tiles with flip flags load without error — LDtk tileset has no flips (TILE-03)."""
    from src.level.map import LevelMap

    data = _make_ldtk_data([
        {"identifier": "Level_0", "worldX": 0, "worldY": 0,
         "autoLayerTiles": [_make_tile(0, 0, 8, 8, f=1)]},
    ])
    path = _write_ldtk_temp(data)
    try:
        lm = LevelMap()
        count = lm.load_autotiles_from_ldtk(path)
        assert count == 1
    finally:
        os.unlink(path)


@unittest.mock.patch("src.level.map.pyxel")
def test_no_flip_warning_when_zero(mock_pyxel, capsys):
    """No warning when flip flag is 0."""
    from src.level.map import LevelMap

    data = _make_ldtk_data([
        {"identifier": "Level_0", "worldX": 0, "worldY": 0,
         "autoLayerTiles": [_make_tile(0, 0, 8, 8, f=0)]},
    ])
    path = _write_ldtk_temp(data)
    try:
        lm = LevelMap()
        lm.load_autotiles_from_ldtk(path)
        captured = capsys.readouterr()
        assert "flip" not in captured.out.lower(), (
            f"Unexpected flip warning in output: {captured.out!r}"
        )
    finally:
        os.unlink(path)


@unittest.mock.patch("src.level.map.pyxel")
def test_collision_visual_separation(mock_pyxel):
    """After loading autotiles, collision_data values remain IntGrid ints (TILE-04)."""
    from src.level.map import LevelMap

    lm = LevelMap()
    # Simulate collision data as if load_from_ldtk_simplified had run
    lm.collision_data = {(0, 0): 1, (1, 0): 3, (2, 0): 2}

    data = _make_ldtk_data([
        {"identifier": "Level_0", "worldX": 0, "worldY": 0,
         "autoLayerTiles": [
             _make_tile(0, 0, 8, 8),
             _make_tile(8, 0, 16, 16),
             _make_tile(16, 0, 24, 8),
         ]},
    ])
    path = _write_ldtk_temp(data)
    try:
        lm.load_autotiles_from_ldtk(path)
        # collision_data must still contain ints, not tuples
        for key, val in lm.collision_data.items():
            assert isinstance(val, int), (
                f"collision_data[{key}] is {type(val).__name__} ({val}), expected int"
            )
    finally:
        os.unlink(path)


@unittest.mock.patch("src.level.map.pyxel")
def test_skip_transparent_tiles(mock_pyxel):
    """Tiles with a=0 are skipped; only a=1 tiles are loaded (TILE-03)."""
    from src.level.map import LevelMap

    data = _make_ldtk_data([
        {"identifier": "Level_0", "worldX": 0, "worldY": 0,
         "autoLayerTiles": [
             _make_tile(0, 0, 8, 8, a=0),  # transparent -- skip
             _make_tile(8, 0, 16, 8, a=1),  # opaque -- load
         ]},
    ])
    path = _write_ldtk_temp(data)
    try:
        lm = LevelMap()
        count = lm.load_autotiles_from_ldtk(path)
        assert count == 1, f"Expected 1 tile loaded (skipping a=0), got {count}"
    finally:
        os.unlink(path)


@unittest.mock.patch("src.level.map.pyxel")
def test_origin_normalization(mock_pyxel):
    """Two levels with negative worldY produce correct tile offsets (origin snap).

    Level A: worldX=0, worldY=-176 -> after normalization, world_y=0
    Level B: worldX=320, worldY=0 -> after normalization, world_y=176

    Tile at px=[0,0] in Level A should map to ty=0 (not negative).
    Tile at px=[0,0] in Level B should map to ty=11 (176 / 16 = 11).
    """
    from src.level.map import LevelMap

    data = _make_ldtk_data([
        {"identifier": "Level_A", "worldX": 0, "worldY": -176,
         "autoLayerTiles": [_make_tile(0, 0, 16, 16)]},
        {"identifier": "Level_B", "worldX": 320, "worldY": 0,
         "autoLayerTiles": [_make_tile(0, 0, 32, 32)]},
    ])
    path = _write_ldtk_temp(data)
    try:
        lm = LevelMap()
        lm.load_autotiles_from_ldtk(path)
        pset_calls = mock_pyxel.tilemaps.__getitem__().pset.call_args_list
        # Level A tile: 16px coords tx=0, ty=0, u=1, v=1
        # 8px top-left cell: (0, 0, (2, 2))
        found_a = any(args == (0, 0, (2, 2)) for args, _ in pset_calls)
        # Level B tile: 16px coords tx=20, ty=11, u=2, v=2
        # 8px top-left cell: (40, 22, (4, 4))
        found_b = any(args == (40, 22, (4, 4)) for args, _ in pset_calls)
        assert found_a, (
            f"Level A tile expected 8px pset(0, 0, (2, 2)), got: {pset_calls}"
        )
        assert found_b, (
            f"Level B tile expected 8px pset(40, 22, (4, 4)), got: {pset_calls}"
        )
    finally:
        os.unlink(path)
