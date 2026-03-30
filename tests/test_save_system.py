"""Tests for the save system: SaveManager persistence and capacity constants."""
import json
import os
import pytest
from types import SimpleNamespace

from src.core.constants import MAX_HP_CAP, MAX_JUICE_CAP, SAVE_FILE
from src.core.save_manager import SaveManager


def _make_game(tmp_path):
    """Create a mock game object matching real Game structure."""
    player = SimpleNamespace(
        max_hp=3,
        hp=2,  # Current HP should NOT be saved (D-04)
        has_drill=True,
        has_dash=False,
        has_shield=False,
        has_shield_t2=False,
        has_boost=False,
    )
    slime = SimpleNamespace(
        max_juice=200.0,
        juice=150.0,  # Current juice should NOT be saved
    )
    current_level = SimpleNamespace(id="Level_3")
    world = SimpleNamespace(
        collected_iids={"iid-aaa", "iid-bbb"},
        current_level=current_level,
    )
    game = SimpleNamespace(
        player=player,
        slime=slime,
        world=world,
        event_flags={"boss_defeated": True, "switch_1": False},
        rooms_visited={"Level_0", "Level_1", "Level_3"},
    )
    return game


@pytest.fixture
def save_dir(tmp_path, monkeypatch):
    """Redirect SaveManager to use tmp_path for save file."""
    monkeypatch.setattr(
        SaveManager, "_get_save_path",
        staticmethod(lambda: str(tmp_path / SAVE_FILE)),
    )
    return tmp_path


class TestSaveManager:
    def test_save_creates_file(self, save_dir):
        game = _make_game(save_dir)
        SaveManager.save(game)
        assert os.path.exists(save_dir / SAVE_FILE)

    def test_load_returns_dict(self, save_dir):
        game = _make_game(save_dir)
        SaveManager.save(game)
        data = SaveManager.load()
        assert isinstance(data, dict)
        assert "version" in data

    def test_load_missing_returns_none(self, save_dir):
        assert SaveManager.load() is None

    def test_exists_true_false(self, save_dir):
        assert SaveManager.exists() is False
        game = _make_game(save_dir)
        SaveManager.save(game)
        assert SaveManager.exists() is True

    def test_delete_removes_file(self, save_dir):
        game = _make_game(save_dir)
        SaveManager.save(game)
        assert SaveManager.exists() is True
        SaveManager.delete()
        assert SaveManager.exists() is False

    def test_delete_missing_no_error(self, save_dir):
        # Should not raise when file doesn't exist
        SaveManager.delete()


class TestSaveRoundTrip:
    def test_roundtrip_preserves_all_fields(self, save_dir):
        game = _make_game(save_dir)
        SaveManager.save(game)
        data = SaveManager.load()

        assert data["version"] == 1
        assert data["player"]["max_hp"] == 3
        assert data["player"]["has_drill"] is True
        assert data["player"]["has_dash"] is False
        assert data["player"]["has_shield"] is False
        assert data["player"]["has_shield_t2"] is False
        assert data["player"]["has_boost"] is False
        assert data["slime"]["max_juice"] == 200.0
        assert data["event_flags"]["boss_defeated"] is True
        assert data["save_room_id"] == "Level_3"

    def test_sets_serialized_as_lists(self, save_dir):
        game = _make_game(save_dir)
        SaveManager.save(game)
        data = SaveManager.load()

        # JSON serializes sets as lists
        assert isinstance(data["world"]["collected_iids"], list)
        assert set(data["world"]["collected_iids"]) == {"iid-aaa", "iid-bbb"}
        assert isinstance(data["visited_rooms"], list)
        assert set(data["visited_rooms"]) == {"Level_0", "Level_1", "Level_3"}

    def test_hp_not_saved_only_max_hp(self, save_dir):
        game = _make_game(save_dir)
        SaveManager.save(game)
        data = SaveManager.load()

        # Only max_hp saved, not current hp (D-04: respawn at full)
        assert "max_hp" in data["player"]
        assert "hp" not in data["player"]

        # Only max_juice saved, not current juice
        assert "max_juice" in data["slime"]
        assert "juice" not in data["slime"]


class TestCapacityCaps:
    def test_max_hp_cap_constant_is_5(self):
        assert MAX_HP_CAP == 5

    def test_max_juice_cap_constant_is_300(self):
        assert MAX_JUICE_CAP == 300.0
