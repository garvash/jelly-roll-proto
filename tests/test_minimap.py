"""Tests for mini-map room classification, cell-based rect computation, and color logic."""
import pytest
from types import SimpleNamespace
from src.core.constants import VIEWPORT_W, VIEWPORT_H


def make_levels():
    return [
        SimpleNamespace(id="Level_0", x=0, y=0, w=320, h=176),
        SimpleNamespace(id="Level_1", x=320, y=0, w=320, h=528),
        SimpleNamespace(id="Level_2", x=640, y=176, w=320, h=352),
        SimpleNamespace(id="Level_3", x=960, y=176, w=320, h=176),
        SimpleNamespace(id="Level_4", x=960, y=352, w=320, h=176),
    ]


from main import classify_room_types, compute_map_rects, get_room_color


class TestClassifyRoomTypes:
    def test_save_room_detected(self):
        entities = [{"type": "SavePoint", "x": 100, "y": 50}]
        levels = [SimpleNamespace(id="Level_0", x=0, y=0, w=320, h=176)]
        result = classify_room_types(levels, entities)
        assert result["Level_0"] == "save"

    def test_boss_room_detected(self):
        entities = [{"type": "BossMole", "x": 1000, "y": 200}]
        levels = [SimpleNamespace(id="Level_3", x=960, y=176, w=320, h=176)]
        result = classify_room_types(levels, entities)
        assert result["Level_3"] == "boss"

    def test_normal_room_default(self):
        entities = []
        levels = [SimpleNamespace(id="Level_0", x=0, y=0, w=320, h=176)]
        result = classify_room_types(levels, entities)
        assert result["Level_0"] == "normal"


class TestComputeMapRects:
    def test_tall_level_produces_multiple_cells(self):
        """Level_1 (528h = 3 viewports) should produce 3 cells when all visited."""
        levels = make_levels()
        # Visit all 3 cells of Level_1
        visited = {(320, 0), (320, 176), (320, 352)}
        rects = compute_map_rects(levels, max_w=60, max_h=12, visited=visited)
        assert len(rects) == 3

    def test_single_cell_per_standard_room(self):
        """Standard room (320x176) produces 1 cell."""
        levels = make_levels()
        visited = {(0, 0)}
        rects = compute_map_rects(levels, max_w=60, max_h=12, visited=visited)
        assert len(rects) == 1

    def test_fits_within_bounds(self):
        levels = make_levels()
        rects = compute_map_rects(levels, max_w=60, max_h=12)
        for rx, ry, rw, rh, _ in rects:
            assert rx >= 0 and ry >= 0


class TestMapColors:
    def test_current_cell_white(self):
        assert get_room_color((0, 0), (0, 0), {}, frame=0) == 7

    def test_current_cell_blinks_off(self):
        assert get_room_color((0, 0), (0, 0), {}, frame=20) == 0

    def test_visited_cell_gray(self):
        assert get_room_color((320, 0), (0, 0), {}, frame=0) == 5


class TestVisitedFilter:
    def test_only_visited_cells_shown(self):
        levels = make_levels()
        visited = {(0, 0), (320, 0)}
        rects = compute_map_rects(levels, max_w=60, max_h=12, visited=visited)
        keys = [r[4] for r in rects]
        assert (0, 0) in keys
        assert (320, 0) in keys
        assert (640, 176) not in keys
