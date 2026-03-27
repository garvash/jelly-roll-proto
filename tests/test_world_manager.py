import pytest
from unittest.mock import MagicMock
import sys

# Mock pyxel to allow imports that transitively reference it
sys.modules["pyxel"] = MagicMock()

from src.level.world import LevelBounds, WorldManager


# --- LevelBounds Tests ---

class TestLevelBounds:
    def test_contains_inside(self):
        lb = LevelBounds("room_a", 0, 0, 128, 128)
        assert lb.contains(64, 64) is True

    def test_contains_origin(self):
        lb = LevelBounds("room_a", 0, 0, 128, 128)
        assert lb.contains(0, 0) is True

    def test_contains_just_outside_right(self):
        lb = LevelBounds("room_a", 0, 0, 128, 128)
        assert lb.contains(128, 64) is False

    def test_contains_just_outside_bottom(self):
        lb = LevelBounds("room_a", 0, 0, 128, 128)
        assert lb.contains(64, 128) is False

    def test_contains_offset_room(self):
        lb = LevelBounds("room_b", 128, 256, 128, 128)
        assert lb.contains(130, 260) is True
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
            LevelBounds("room_0_0", 0, 0, 128, 128),
            LevelBounds("room_1_0", 128, 0, 128, 128),
            LevelBounds("room_0_1", 0, 128, 128, 128),
            LevelBounds("room_1_1", 128, 128, 256, 128),  # Double-wide room
        ]
        return WorldManager(levels)

    def test_detect_top_left(self, world):
        level = world.detect_level(10, 10)
        assert level is not None
        assert level.id == "room_0_0"

    def test_detect_top_right(self, world):
        level = world.detect_level(200, 50)
        assert level is not None
        assert level.id == "room_1_0"

    def test_detect_bottom_left(self, world):
        level = world.detect_level(64, 200)
        assert level is not None
        assert level.id == "room_0_1"

    def test_detect_double_wide(self, world):
        level = world.detect_level(300, 192)
        assert level is not None
        assert level.id == "room_1_1"

    def test_detect_out_of_bounds(self, world):
        level = world.detect_level(999, 999)
        assert level is None

    def test_detect_updates_current_level(self, world):
        assert world.current_level is None
        world.detect_level(64, 64)
        assert world.current_level.id == "room_0_0"

    def test_detect_boundary_edge(self, world):
        """Player at exact boundary (128, 0) should be in room_1_0."""
        level = world.detect_level(128, 0)
        assert level.id == "room_1_0"


# --- WorldManager.get_camera_clamped Tests ---

class TestCameraClamping:
    @pytest.fixture
    def world_standard(self):
        """World with standard 128x128 rooms."""
        levels = [
            LevelBounds("room_0_0", 0, 0, 128, 128),
            LevelBounds("room_1_0", 128, 0, 128, 128),
        ]
        wm = WorldManager(levels)
        return wm

    @pytest.fixture
    def world_large(self):
        """World with a large room (256x128) for scrolling tests."""
        levels = [
            LevelBounds("big_room", 0, 0, 256, 128),
        ]
        wm = WorldManager(levels)
        return wm

    def test_standard_room_camera_locked(self, world_standard):
        """In a 128x128 room, camera is always locked to (0,0)."""
        world_standard.detect_level(64, 64)
        cx, cy = world_standard.get_camera_clamped(64, 64)
        assert cx == 0
        assert cy == 0

    def test_standard_room_camera_locked_any_position(self, world_standard):
        """Camera stays at room origin regardless of player pos in 128x128."""
        world_standard.detect_level(10, 10)
        cx, cy = world_standard.get_camera_clamped(10, 10)
        assert cx == 0
        assert cy == 0

        world_standard.detect_level(120, 120)
        cx, cy = world_standard.get_camera_clamped(120, 120)
        assert cx == 0
        assert cy == 0

    def test_second_room_camera_locked(self, world_standard):
        """Second room at (128, 0) should lock camera to (128, 0)."""
        world_standard.detect_level(200, 64)
        cx, cy = world_standard.get_camera_clamped(200, 64)
        assert cx == 128
        assert cy == 0

    def test_large_room_scrolls_x(self, world_large):
        """In a 256x128 room, camera scrolls horizontally."""
        world_large.detect_level(200, 64)
        cx, cy = world_large.get_camera_clamped(200, 64)
        # cam_x = max(0, min(200-64, 256-128)) = max(0, min(136, 128)) = 128
        assert cx == 128
        assert cy == 0

    def test_large_room_clamps_left(self, world_large):
        """Camera clamps to left edge in large room."""
        world_large.detect_level(10, 64)
        cx, cy = world_large.get_camera_clamped(10, 64)
        assert cx == 0
        assert cy == 0

    def test_large_room_player_center(self, world_large):
        """Player at center of large room gets centered camera."""
        world_large.detect_level(128, 64)
        cx, cy = world_large.get_camera_clamped(128, 64)
        # cam_x = max(0, min(128-64, 128)) = max(0, min(64, 128)) = 64
        assert cx == 64
        assert cy == 0

    def test_fallback_no_level(self):
        """With no current level, falls back to grid snapping."""
        wm = WorldManager([])
        cx, cy = wm.get_camera_clamped(300, 200)
        assert cx == 256  # int(300 // 128) * 128
        assert cy == 128  # int(200 // 128) * 128

    def test_camera_never_negative(self, world_standard):
        """Camera coords never go below the level origin."""
        world_standard.detect_level(0, 0)
        cx, cy = world_standard.get_camera_clamped(-10, -10)
        assert cx >= 0
        assert cy >= 0

    def test_camera_never_exceeds_bounds(self, world_standard):
        """Camera should not exceed (level.x + level.w - 128)."""
        world_standard.detect_level(64, 64)
        cx, cy = world_standard.get_camera_clamped(200, 200)
        # level is 0,0,128,128 so max cam = (0, 0)
        assert cx == 0
        assert cy == 0
