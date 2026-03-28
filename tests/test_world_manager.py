import pytest
from unittest.mock import MagicMock
import sys

# Mock pyxel to allow imports that transitively reference it
sys.modules["pyxel"] = MagicMock()

from src.level.world import LevelBounds, WorldManager
from src.core.constants import VIEWPORT_W, VIEWPORT_H


# --- LevelBounds Tests ---

class TestLevelBounds:
    def test_contains_inside(self):
        lb = LevelBounds("room_a", 0, 0, VIEWPORT_W, VIEWPORT_H)
        assert lb.contains(64, 64) is True

    def test_contains_origin(self):
        lb = LevelBounds("room_a", 0, 0, VIEWPORT_W, VIEWPORT_H)
        assert lb.contains(0, 0) is True

    def test_contains_just_outside_right(self):
        lb = LevelBounds("room_a", 0, 0, VIEWPORT_W, VIEWPORT_H)
        assert lb.contains(VIEWPORT_W, 64) is False

    def test_contains_just_outside_bottom(self):
        lb = LevelBounds("room_a", 0, 0, VIEWPORT_W, VIEWPORT_H)
        assert lb.contains(64, VIEWPORT_H) is False

    def test_contains_offset_room(self):
        lb = LevelBounds("room_b", VIEWPORT_W, 256, VIEWPORT_W, VIEWPORT_H)
        assert lb.contains(VIEWPORT_W + 2, 260) is True
        assert lb.contains(100, 260) is False

    def test_stores_attributes(self):
        lb = LevelBounds("test", 10, 20, 30, 40)
        assert lb.id == "test"
        assert lb.x == 10
        assert lb.y == 20
        assert lb.w == 30
        assert lb.h == 40


# --- WorldManager.detect_level Tests ---

class TestDetectLevel:
    @pytest.fixture
    def world(self):
        levels = [
            LevelBounds("room_0_0", 0, 0, VIEWPORT_W, VIEWPORT_H),
            LevelBounds("room_1_0", VIEWPORT_W, 0, VIEWPORT_W, VIEWPORT_H),
            LevelBounds("room_0_1", 0, VIEWPORT_H, VIEWPORT_W, VIEWPORT_H),
            LevelBounds("room_1_1", VIEWPORT_W, VIEWPORT_H, VIEWPORT_W * 2, VIEWPORT_H),  # Double-wide room
        ]
        return WorldManager(levels)

    def test_detect_top_left(self, world):
        level = world.detect_level(10, 10)
        assert level is not None
        assert level.id == "room_0_0"

    def test_detect_top_right(self, world):
        level = world.detect_level(VIEWPORT_W + 50, 50)
        assert level is not None
        assert level.id == "room_1_0"

    def test_detect_bottom_left(self, world):
        level = world.detect_level(64, VIEWPORT_H + 20)
        assert level is not None
        assert level.id == "room_0_1"

    def test_detect_double_wide(self, world):
        level = world.detect_level(VIEWPORT_W + 100, VIEWPORT_H + 10)
        assert level is not None
        assert level.id == "room_1_1"

    def test_detect_out_of_bounds(self, world):
        level = world.detect_level(9999, 9999)
        assert level is None

    def test_detect_updates_current_level(self, world):
        assert world.current_level is None
        world.detect_level(64, 64)
        assert world.current_level.id == "room_0_0"

    def test_detect_boundary_edge(self, world):
        """Player at exact boundary should be in room_1_0."""
        level = world.detect_level(VIEWPORT_W, 0)
        assert level.id == "room_1_0"


# --- WorldManager.get_camera_clamped Tests ---

class TestCameraClamping:
    @pytest.fixture
    def world_standard(self):
        """World with standard VIEWPORT_W x VIEWPORT_H rooms."""
        levels = [
            LevelBounds("room_0_0", 0, 0, VIEWPORT_W, VIEWPORT_H),
            LevelBounds("room_1_0", VIEWPORT_W, 0, VIEWPORT_W, VIEWPORT_H),
        ]
        wm = WorldManager(levels)
        return wm

    @pytest.fixture
    def world_large(self):
        """World with a large room (2*VIEWPORT_W x VIEWPORT_H) for scrolling tests."""
        levels = [
            LevelBounds("big_room", 0, 0, VIEWPORT_W * 2, VIEWPORT_H),
        ]
        wm = WorldManager(levels)
        return wm

    def test_standard_room_camera_locked(self, world_standard):
        """In a standard room, camera is always locked to (0,0)."""
        world_standard.detect_level(64, 64)
        cx, cy = world_standard.get_camera_clamped(64, 64)
        assert cx == 0
        assert cy == 0

    def test_standard_room_camera_locked_any_position(self, world_standard):
        """Camera stays at room origin regardless of player pos in standard room."""
        world_standard.detect_level(10, 10)
        cx, cy = world_standard.get_camera_clamped(10, 10)
        assert cx == 0
        assert cy == 0

        world_standard.detect_level(VIEWPORT_W - 8, VIEWPORT_H - 8)
        cx, cy = world_standard.get_camera_clamped(VIEWPORT_W - 8, VIEWPORT_H - 8)
        assert cx == 0
        assert cy == 0

    def test_second_room_camera_locked(self, world_standard):
        """Second room at (VIEWPORT_W, 0) should lock camera to (VIEWPORT_W, 0)."""
        world_standard.detect_level(VIEWPORT_W + 50, 64)
        cx, cy = world_standard.get_camera_clamped(VIEWPORT_W + 50, 64)
        assert cx == VIEWPORT_W
        assert cy == 0

    def test_large_room_scrolls_x(self, world_large):
        """In a double-wide room, camera scrolls horizontally."""
        world_large.detect_level(VIEWPORT_W + 100, 64)
        cx, cy = world_large.get_camera_clamped(VIEWPORT_W + 100, 64)
        # cam_x = max(0, min(420-160, 640-320)) = max(0, min(260, 320)) = 260
        assert cx == VIEWPORT_W + 100 - VIEWPORT_W // 2
        assert cy == 0

    def test_large_room_clamps_left(self, world_large):
        """Camera clamps to left edge in large room."""
        world_large.detect_level(10, 64)
        cx, cy = world_large.get_camera_clamped(10, 64)
        assert cx == 0
        assert cy == 0

    def test_large_room_player_center(self, world_large):
        """Player at center of large room gets centered camera."""
        world_large.detect_level(VIEWPORT_W, 64)
        cx, cy = world_large.get_camera_clamped(VIEWPORT_W, 64)
        # cam_x = max(0, min(320-160, 320)) = max(0, min(160, 320)) = 160
        assert cx == VIEWPORT_W // 2
        assert cy == 0

    def test_fallback_no_level(self):
        """With no current level, falls back to grid snapping."""
        wm = WorldManager([])
        cx, cy = wm.get_camera_clamped(500, 300)
        assert cx == int(500 // VIEWPORT_W) * VIEWPORT_W
        assert cy == int(300 // VIEWPORT_H) * VIEWPORT_H

    def test_camera_never_negative(self, world_standard):
        """Camera coords never go below the level origin."""
        world_standard.detect_level(0, 0)
        cx, cy = world_standard.get_camera_clamped(-10, -10)
        assert cx >= 0
        assert cy >= 0

    def test_camera_never_exceeds_bounds(self, world_standard):
        """Camera should not exceed level bounds."""
        world_standard.detect_level(64, 64)
        cx, cy = world_standard.get_camera_clamped(500, 500)
        # standard room size == viewport size, so max cam = (0, 0)
        assert cx == 0
        assert cy == 0
