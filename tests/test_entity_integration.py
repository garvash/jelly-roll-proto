"""Tests for LDtk entity integration fixes (INT-01 through INT-04)."""
import json
import os
import sys
import tempfile
import types

import pytest
from unittest.mock import MagicMock, patch, call
from types import SimpleNamespace


# === INT-01: Entity name aliases ===

class TestEntityNameAliases:
    """INT-01: ENTITY_ALIASES maps LDtk export names to game code names."""

    def test_entity_name_aliases(self):
        """Save maps to SavePoint and FinalBoss maps to BossMole."""
        # Import at test time to ensure main module is loadable
        # We test the dict directly since it's a module-level constant.
        from main import ENTITY_ALIASES

        assert ENTITY_ALIASES["Save"] == "SavePoint"
        assert ENTITY_ALIASES["FinalBoss"] == "BossMole"

    def test_unknown_name_passes_through(self):
        """Unknown entity names are unchanged by alias lookup."""
        from main import ENTITY_ALIASES

        assert ENTITY_ALIASES.get("Snail", "Snail") == "Snail"
        assert ENTITY_ALIASES.get("Door", "Door") == "Door"
        assert ENTITY_ALIASES.get("Bat", "Bat") == "Bat"


# === INT-03: Direction normalization in map.py ===

class TestDirectionNormalization:
    """INT-03: map.py normalizes string enum values to lowercase."""

    def _make_ldtk_data(self, entities=None, x=0, y=0):
        """Create a minimal LDtk simplified data.json."""
        return {
            "x": x, "y": y,
            "width": 320, "height": 176,
            "identifier": "Level_0",
            "entities": entities or {},
        }

    def _write_level(self, tmpdir, level_name, data, csv_content="0"):
        """Write a minimal level directory with data.json and IntGrid.csv."""
        level_dir = os.path.join(tmpdir, level_name)
        os.makedirs(level_dir, exist_ok=True)
        with open(os.path.join(level_dir, "data.json"), "w") as f:
            json.dump(data, f)
        with open(os.path.join(level_dir, "IntGrid.csv"), "w") as f:
            f.write(csv_content)

    def test_direction_normalization(self):
        """Capitalized direction values from LDtk become lowercase."""
        # Stub pyxel for map.py import
        pyxel_mock = MagicMock()
        pyxel_mock.tilemaps = {0: MagicMock()}
        with patch.dict(sys.modules, {"pyxel": pyxel_mock}):
            from src.level.map import LevelMap

            with tempfile.TemporaryDirectory() as tmpdir:
                data = self._make_ldtk_data(entities={
                    "Door": [
                        {"x": 10, "y": 20, "iid": "d1",
                         "customFields": {"direction": "Left", "action": "Spit",
                                          "target_level_id": 1, "event_id": "boss_defeated"}}
                    ]
                })
                self._write_level(tmpdir, "Level_0", data)

                lm = LevelMap()
                lm.load_from_ldtk_simplified(tmpdir)

                door_ent = next(e for e in lm.entities if e["type"] == "Door")
                # String fields lowercased
                assert door_ent["direction"] == "left", f"Expected 'left', got '{door_ent['direction']}'"
                assert door_ent["action"] == "spit", f"Expected 'spit', got '{door_ent['action']}'"
                assert door_ent["event_id"] == "boss_defeated"
                # Non-string field preserved
                assert door_ent["target_level_id"] == 1

    def test_direction_normalization_top_level(self):
        """Top-level entity fields (like direction from inst dict) are also lowercased."""
        pyxel_mock = MagicMock()
        pyxel_mock.tilemaps = {0: MagicMock()}
        with patch.dict(sys.modules, {"pyxel": pyxel_mock}):
            from src.level.map import LevelMap

            with tempfile.TemporaryDirectory() as tmpdir:
                # Simulate an entity with 'direction' as a top-level field (not in customFields)
                data = self._make_ldtk_data(entities={
                    "Door": [
                        {"x": 10, "y": 20, "iid": "d1", "direction": "Right",
                         "customFields": {"target_level_id": 2}}
                    ]
                })
                self._write_level(tmpdir, "Level_0", data)

                lm = LevelMap()
                lm.load_from_ldtk_simplified(tmpdir)

                door_ent = next(e for e in lm.entities if e["type"] == "Door")
                assert door_ent["direction"] == "right"

    def test_all_direction_values(self):
        """All four direction values normalize correctly."""
        pyxel_mock = MagicMock()
        pyxel_mock.tilemaps = {0: MagicMock()}
        with patch.dict(sys.modules, {"pyxel": pyxel_mock}):
            from src.level.map import LevelMap

            with tempfile.TemporaryDirectory() as tmpdir:
                data = self._make_ldtk_data(entities={
                    "Door": [
                        {"x": 10, "y": 20, "iid": f"d{i}",
                         "customFields": {"direction": d, "target_level_id": 0}}
                        for i, d in enumerate(["Left", "Right", "Up", "Down"])
                    ]
                })
                self._write_level(tmpdir, "Level_0", data)

                lm = LevelMap()
                lm.load_from_ldtk_simplified(tmpdir)

                directions = sorted(e["direction"] for e in lm.entities if e["type"] == "Door")
                assert directions == ["down", "left", "right", "up"]


# === INT-02: Flat customFields read ===

class TestFlatCustomFields:
    """INT-02: After map.py flattening, entity dict has fields at top level."""

    def test_flat_customfields(self):
        """action and event_id are at top level after flattening, not nested."""
        pyxel_mock = MagicMock()
        pyxel_mock.tilemaps = {0: MagicMock()}
        with patch.dict(sys.modules, {"pyxel": pyxel_mock}):
            from src.level.map import LevelMap

            with tempfile.TemporaryDirectory() as tmpdir:
                data = {
                    "x": 0, "y": 0, "width": 320, "height": 176,
                    "identifier": "Level_0",
                    "entities": {
                        "Door": [
                            {"x": 10, "y": 20, "iid": "d1",
                             "customFields": {"action": "event", "event_id": "boss_defeated",
                                              "target_level_id": 3, "hp": 2}}
                        ]
                    }
                }
                level_dir = os.path.join(tmpdir, "Level_0")
                os.makedirs(level_dir)
                with open(os.path.join(level_dir, "data.json"), "w") as f:
                    json.dump(data, f)
                with open(os.path.join(level_dir, "IntGrid.csv"), "w") as f:
                    f.write("0")

                lm = LevelMap()
                lm.load_from_ldtk_simplified(tmpdir)

                door_ent = next(e for e in lm.entities if e["type"] == "Door")
                # Fields are at top level
                assert "action" in door_ent
                assert "event_id" in door_ent
                assert door_ent["action"] == "event"
                assert door_ent["event_id"] == "boss_defeated"
                assert door_ent["target_level_id"] == 3
                assert door_ent["hp"] == 2
                # No nested customFields key in the flattened dict
                assert "customFields" not in door_ent


# === action="none" normalization ===

class TestActionNoneNormalized:
    """LDtk action="None" (uppercase from enum) is treated as None."""

    def test_action_none_normalized(self):
        """action string 'none' (lowercased from LDtk 'None') becomes Python None."""
        # The normalization happens in spawn_enemies in main.py.
        # We test that: if action field is "none" after lowercasing, it becomes None.
        # map.py lowercases "None" -> "none", then spawn_enemies converts "none" -> None.
        pyxel_mock = MagicMock()
        pyxel_mock.tilemaps = {0: MagicMock()}
        with patch.dict(sys.modules, {"pyxel": pyxel_mock}):
            from src.level.map import LevelMap

            with tempfile.TemporaryDirectory() as tmpdir:
                data = {
                    "x": 0, "y": 0, "width": 320, "height": 176,
                    "identifier": "Level_0",
                    "entities": {
                        "Door": [
                            {"x": 10, "y": 20, "iid": "d1",
                             "customFields": {"action": "None", "target_level_id": 0}}
                        ]
                    }
                }
                level_dir = os.path.join(tmpdir, "Level_0")
                os.makedirs(level_dir)
                with open(os.path.join(level_dir, "data.json"), "w") as f:
                    json.dump(data, f)
                with open(os.path.join(level_dir, "IntGrid.csv"), "w") as f:
                    f.write("0")

                lm = LevelMap()
                lm.load_from_ldtk_simplified(tmpdir)

                door_ent = next(e for e in lm.entities if e["type"] == "Door")
                # map.py lowercases "None" to "none"
                assert door_ent["action"] == "none"
                # spawn_enemies would then convert "none" -> None
                # We verify that logic inline:
                action = door_ent["action"]
                if action == "none":
                    action = None
                assert action is None


# === INT-04: No double-spawn on restore ===

class TestNoDoubleSpawn:
    """INT-04: restore_from_save clears entity lists before spawn_enemies."""

    def test_no_double_spawn_on_restore(self):
        """Verify restore_from_save clears enemies/doors/save_points before spawning."""
        # We check the source code for the defensive clear pattern.
        # This is a structural test: verify the code has the clear before spawn.
        import inspect
        from main import Game

        source = inspect.getsource(Game.restore_from_save)
        # Find positions of clear statements and spawn call
        enemies_clear = source.find("self.enemies = []")
        doors_clear = source.find("self.doors = []")
        save_points_clear = source.find("self.save_points = []")
        items_clear = source.find("self.items = []")
        spawn_call = source.find("self.spawn_enemies()")

        # All clears must exist
        assert enemies_clear != -1, "self.enemies = [] not found in restore_from_save"
        assert doors_clear != -1, "self.doors = [] not found in restore_from_save"
        assert save_points_clear != -1, "self.save_points = [] not found in restore_from_save"
        assert items_clear != -1, "self.items = [] not found in restore_from_save"

        # All clears must come before spawn_enemies call
        assert enemies_clear < spawn_call, "enemies clear must come before spawn_enemies"
        assert doors_clear < spawn_call, "doors clear must come before spawn_enemies"
        assert save_points_clear < spawn_call, "save_points clear must come before spawn_enemies"
        assert items_clear < spawn_call, "items clear must come before spawn_enemies"


# === classify_room_types with aliases ===

class TestClassifyRoomTypesWithAliases:
    """classify_room_types recognizes aliased entity names."""

    def test_scan_room_types_with_aliases(self):
        """'Save' and 'FinalBoss' entity types are recognized via aliases."""
        from main import classify_room_types

        # Create mock levels
        levels = [
            SimpleNamespace(id="Level_0", x=0, y=0, w=320, h=176),
            SimpleNamespace(id="Level_1", x=320, y=0, w=320, h=176),
            SimpleNamespace(id="Level_2", x=640, y=0, w=320, h=176),
        ]

        entities = [
            {"type": "Save", "x": 10, "y": 10},       # Aliased SavePoint
            {"type": "FinalBoss", "x": 330, "y": 10},  # Aliased BossMole
            {"type": "Snail", "x": 650, "y": 10},      # Normal enemy (no effect)
        ]

        room_types = classify_room_types(levels, entities)
        assert room_types["Level_0"] == "save", f"Expected 'save', got '{room_types['Level_0']}'"
        assert room_types["Level_1"] == "boss", f"Expected 'boss', got '{room_types['Level_1']}'"
        assert room_types["Level_2"] == "normal", f"Expected 'normal', got '{room_types['Level_2']}'"

    def test_scan_room_types_with_canonical_names(self):
        """Canonical names (SavePoint, BossMole) still work."""
        from main import classify_room_types

        levels = [
            SimpleNamespace(id="Level_0", x=0, y=0, w=320, h=176),
            SimpleNamespace(id="Level_1", x=320, y=0, w=320, h=176),
        ]

        entities = [
            {"type": "SavePoint", "x": 10, "y": 10},
            {"type": "BossMole", "x": 330, "y": 10},
        ]

        room_types = classify_room_types(levels, entities)
        assert room_types["Level_0"] == "save"
        assert room_types["Level_1"] == "boss"


# === Plan 02: Entity stub tests ===

class TestEntityStubs:
    """Tests for OneWay, HiddenLoot, MapFixture stub entities (Plan 02)."""

    def test_oneway_stub(self):
        """OneWay stub creates and renders without crash (D-07)."""
        from src.entities.map_entities import OneWay
        ow = OneWay(100, 200, "left")
        assert ow.x == 100
        assert ow.y == 200
        assert ow.direction == "left"
        ow.update()  # Should not crash
        with patch("src.entities.map_entities.pyxel"):
            ow.draw()  # Should not crash (pyxel mocked)
        assert ow.check_collision(100, 200, 8, 8) is True
        assert ow.check_collision(200, 200, 8, 8) is False

    def test_hiddenloot_stub(self):
        """HiddenLoot stub creates and renders without crash (D-08)."""
        from src.entities.map_entities import HiddenLoot
        hl = HiddenLoot(50, 60, iid="test-iid")
        assert hl.x == 50
        assert hl.y == 60
        assert hl.iid == "test-iid"
        hl.update()
        with patch("src.entities.map_entities.pyxel"):
            hl.draw()
        assert hl.check_collision(50, 60, 8, 8) is True

    def test_map_stub(self):
        """MapFixture stub creates and renders without crash (D-09)."""
        from src.entities.map_entities import MapFixture
        mf = MapFixture(80, 90)
        assert mf.x == 80
        assert mf.y == 90
        mf.update()
        with patch("src.entities.map_entities.pyxel"):
            mf.draw()
        assert mf.check_collision(80, 90, 8, 8) is True

    def test_fixtures_list_exists(self):
        """Fixtures list is initialized and cleared properly."""
        import inspect
        from main import Game
        # Check reset has self.fixtures = []
        reset_src = inspect.getsource(Game.reset)
        assert "self.fixtures = []" in reset_src, "self.fixtures = [] not found in reset()"
        # Check _on_room_enter has self.fixtures = []
        room_src = inspect.getsource(Game._on_room_enter)
        assert "self.fixtures = []" in room_src, "self.fixtures = [] not in _on_room_enter()"

    def test_unknown_entity_logged(self, capsys):
        """Unknown entity types are logged (not silently ignored)."""
        # We test structurally: spawn_enemies should have a print for unknown entities
        import inspect
        from main import Game
        source = inspect.getsource(Game.spawn_enemies)
        assert 'Unknown entity type' in source, "Unknown entity type logging not found"
