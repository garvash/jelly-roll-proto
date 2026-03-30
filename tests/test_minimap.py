"""Tests for mini-map room classification, rect computation, and color logic."""
import pytest
from types import SimpleNamespace


# Test helper: create mock levels matching real LDtk layout
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
    def test_proportional_heights(self):
        levels = make_levels()
        rects = compute_map_rects(levels, max_w=60, max_h=12)
        # Level_1 (528h) should be ~3x height of Level_0 (176h)
        r0 = next(r for r in rects if r[4] == "Level_0")
        r1 = next(r for r in rects if r[4] == "Level_1")
        assert r1[3] > r0[3] * 2  # At least 2x taller

    def test_fits_within_bounds(self):
        levels = make_levels()
        rects = compute_map_rects(levels, max_w=60, max_h=12)
        for rx, ry, rw, rh, _ in rects:
            assert rx >= 0 and ry >= 0
            assert rx + rw <= 60
            assert ry + rh <= 12


class TestMapColors:
    def test_current_room_white(self):
        assert get_room_color("Level_0", "Level_0", {"Level_0": "normal"}, frame=0) == 7

    def test_current_room_blinks_off(self):
        assert get_room_color("Level_0", "Level_0", {"Level_0": "normal"}, frame=20) == 0

    def test_save_room_green(self):
        assert get_room_color("Level_0", "Level_1", {"Level_0": "save"}, frame=0) == 11

    def test_boss_room_red(self):
        assert get_room_color("Level_3", "Level_1", {"Level_3": "boss"}, frame=0) == 8

    def test_normal_visited_gray(self):
        assert get_room_color("Level_2", "Level_0", {"Level_2": "normal"}, frame=0) == 5


class TestVisitedFilter:
    def test_only_visited_rooms_shown(self):
        levels = make_levels()
        visited = {"Level_0", "Level_1"}
        rects = compute_map_rects(levels, max_w=60, max_h=12, visited=visited)
        ids = [r[4] for r in rects]
        assert "Level_0" in ids
        assert "Level_1" in ids
        assert "Level_2" not in ids
