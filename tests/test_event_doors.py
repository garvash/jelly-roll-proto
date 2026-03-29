"""Tests for event-gated door system (D-01 through D-06)."""
import sys
import types

# Stub pyxel so map_entities can import without the real engine
pyxel_stub = types.ModuleType("pyxel")
sys.modules["pyxel"] = pyxel_stub

from src.entities.map_entities import Door


class TestEventDoorStartsClosed:
    """Test 1: Door with action='event', event_id='boss_defeated' starts closed."""

    def test_event_door_starts_closed(self):
        door = Door(0, 0, action="event", event_id="boss_defeated")
        assert door.is_open is False
        assert door.action == "event"
        assert door.event_id == "boss_defeated"


class TestEventDoorOpensOnFlag:
    """Test 2: check_event_open with matching True flag opens door."""

    def test_opens_when_flag_set(self):
        door = Door(0, 0, action="event", event_id="boss_defeated")
        door.check_event_open({"boss_defeated": True})
        assert door.is_open is True


class TestEventDoorStaysClosedOnFalse:
    """Test 3: check_event_open with flag=False keeps door closed."""

    def test_stays_closed_when_flag_false(self):
        door = Door(0, 0, action="event", event_id="boss_defeated")
        door.check_event_open({"boss_defeated": False})
        assert door.is_open is False


class TestEventDoorStaysClosedOnMissing:
    """Test 4: check_event_open with empty dict keeps door closed."""

    def test_stays_closed_when_flag_missing(self):
        door = Door(0, 0, action="event", event_id="boss_defeated")
        door.check_event_open({})
        assert door.is_open is False


class TestNonEventDoorIgnoresCheck:
    """Test 5: Door with action='spit' ignores check_event_open."""

    def test_spit_door_ignores_event_check(self):
        door = Door(0, 0, action="spit", event_id=None)
        door.check_event_open({"boss_defeated": True})
        assert door.is_open is False


class TestNullActionDoorIgnoresCheck:
    """Test 6: Door with action=None ignores check_event_open."""

    def test_null_action_ignores_event_check(self):
        door = Door(0, 0, action=None, event_id=None)
        door.check_event_open({"boss_defeated": True})
        assert door.is_open is False
