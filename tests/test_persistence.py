"""Tests for state persistence: item collection tracking and block regeneration."""
import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock pyxel to allow imports that transitively reference it
sys.modules["pyxel"] = MagicMock()

from src.level.world import LevelBounds, WorldManager
from src.core.constants import TILE_DESTRUCTIBLE, TILE_CRACKED_H, TILE_GOO_MOLD


# --- Item Persistence Tests ---

class TestItemPersistence:
    def test_item_not_collected_by_default(self):
        wm = WorldManager()
        assert wm.is_item_collected("item-abc-123") is False

    def test_collect_item_marks_as_collected(self):
        wm = WorldManager()
        wm.collect_item("item-abc-123")
        assert wm.is_item_collected("item-abc-123") is True

    def test_different_items_tracked_independently(self):
        wm = WorldManager()
        wm.collect_item("energy-1")
        assert wm.is_item_collected("energy-1") is True
        assert wm.is_item_collected("energy-2") is False

    def test_collect_same_item_twice_is_idempotent(self):
        wm = WorldManager()
        wm.collect_item("drill-1")
        wm.collect_item("drill-1")
        assert wm.is_item_collected("drill-1") is True
        assert len(wm.collected_iids) == 1

    def test_multiple_items_collected(self):
        wm = WorldManager()
        wm.collect_item("a")
        wm.collect_item("b")
        wm.collect_item("c")
        assert len(wm.collected_iids) == 3
        assert wm.is_item_collected("a")
        assert wm.is_item_collected("b")
        assert wm.is_item_collected("c")


# --- Block Regeneration Tests ---

class TestBlockRegeneration:
    def _make_mock_level_map(self):
        """Create a mock LevelMap for testing tile restoration."""
        mock = MagicMock()
        mock.restore_tile = MagicMock()
        return mock

    def test_break_block_registers_timer(self):
        wm = WorldManager()
        wm.break_block(5, 10, TILE_DESTRUCTIBLE)
        assert (5, 10) in wm.broken_blocks
        assert wm.broken_blocks[(5, 10)]["timer"] == wm.block_regen_frames
        assert wm.broken_blocks[(5, 10)]["tile_data"] == TILE_DESTRUCTIBLE

    def test_regen_timer_ticks_down(self):
        wm = WorldManager()
        mock_map = self._make_mock_level_map()
        wm.break_block(3, 4, TILE_DESTRUCTIBLE)

        wm.update_block_regen(mock_map)
        assert wm.broken_blocks[(3, 4)]["timer"] == wm.block_regen_frames - 1
        mock_map.restore_tile.assert_not_called()

    def test_block_restores_after_full_timer(self):
        wm = WorldManager()
        mock_map = self._make_mock_level_map()
        wm.break_block(1, 2, TILE_DESTRUCTIBLE)

        # Tick down to 1 frame remaining
        for _ in range(wm.block_regen_frames - 1):
            wm.update_block_regen(mock_map)
        assert (1, 2) in wm.broken_blocks

        # Final tick - should restore
        wm.update_block_regen(mock_map)
        assert (1, 2) not in wm.broken_blocks
        mock_map.restore_tile.assert_called_once_with(1, 2, TILE_DESTRUCTIBLE)

    def test_multiple_blocks_regen_independently(self):
        wm = WorldManager()
        mock_map = self._make_mock_level_map()
        wm.break_block(0, 0, TILE_DESTRUCTIBLE)

        # Tick 100 frames
        for _ in range(100):
            wm.update_block_regen(mock_map)

        # Break another block
        wm.break_block(5, 5, TILE_CRACKED_H)

        # First block should have its timer at regen_frames - 100
        assert wm.broken_blocks[(0, 0)]["timer"] == wm.block_regen_frames - 100
        assert wm.broken_blocks[(5, 5)]["timer"] == wm.block_regen_frames

    def test_reset_blocks_for_room_restores_all(self):
        wm = WorldManager()
        mock_map = self._make_mock_level_map()

        wm.break_block(1, 1, TILE_DESTRUCTIBLE)
        wm.break_block(2, 2, TILE_CRACKED_H)
        wm.break_block(3, 3, TILE_GOO_MOLD)

        wm.reset_blocks_for_room(mock_map)

        assert len(wm.broken_blocks) == 0
        assert mock_map.restore_tile.call_count == 3

    def test_reset_blocks_passes_correct_tile_data(self):
        wm = WorldManager()
        mock_map = self._make_mock_level_map()

        wm.break_block(10, 20, TILE_GOO_MOLD)
        wm.reset_blocks_for_room(mock_map)

        mock_map.restore_tile.assert_called_once_with(10, 20, TILE_GOO_MOLD)

    def test_no_blocks_to_reset(self):
        wm = WorldManager()
        mock_map = self._make_mock_level_map()
        # Should not raise
        wm.reset_blocks_for_room(mock_map)
        assert mock_map.restore_tile.call_count == 0


# --- Transition State Tests ---

class TestTransitionState:
    def test_initial_state_is_playing(self):
        wm = WorldManager()
        assert wm.state == WorldManager.STATE_PLAYING
        assert not wm.is_transitioning()

    def test_trigger_transition_changes_state(self):
        target = LevelBounds("room_b", 128, 0, 128, 128)
        wm = WorldManager([LevelBounds("room_a", 0, 0, 128, 128), target])
        wm.current_level = wm.levels[0]

        wm.trigger_transition(target, 0, 0)
        assert wm.state == WorldManager.STATE_TRANSITIONING
        assert wm.is_transitioning()

    def test_transition_completes_after_frames(self):
        target = LevelBounds("room_b", 128, 0, 128, 128)
        wm = WorldManager([LevelBounds("room_a", 0, 0, 128, 128), target])
        wm.current_level = wm.levels[0]

        wm.trigger_transition(target, 0, 0)

        for _ in range(WorldManager.TRANSITION_FRAMES):
            cam = wm.update_transition()

        assert wm.state == WorldManager.STATE_PLAYING
        assert not wm.is_transitioning()
        assert wm.current_level is target

    def test_transition_camera_interpolates(self):
        target = LevelBounds("room_b", 128, 0, 128, 128)
        wm = WorldManager([LevelBounds("room_a", 0, 0, 128, 128), target])
        wm.current_level = wm.levels[0]

        wm.trigger_transition(target, 0, 0)

        # First frame should not be at destination yet
        cam = wm.update_transition()
        assert cam[0] >= 0  # Moving towards 128
        assert cam[0] < 128  # Not there yet

    def test_transition_ends_at_target_camera(self):
        target = LevelBounds("room_b", 128, 0, 128, 128)
        wm = WorldManager([LevelBounds("room_a", 0, 0, 128, 128), target])
        wm.current_level = wm.levels[0]

        wm.trigger_transition(target, 0, 0)

        cam = None
        for _ in range(WorldManager.TRANSITION_FRAMES):
            cam = wm.update_transition()

        assert cam == (128, 0)

    def test_double_trigger_ignored(self):
        target = LevelBounds("room_b", 128, 0, 128, 128)
        wm = WorldManager([LevelBounds("room_a", 0, 0, 128, 128), target])
        wm.current_level = wm.levels[0]

        wm.trigger_transition(target, 0, 0)
        # Second trigger during transition should be ignored
        wm.trigger_transition(LevelBounds("room_c", 256, 0, 128, 128), 0, 0)
        assert wm.transition_target_level is target
