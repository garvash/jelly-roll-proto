"""Phase 26 ANIM-02 event bus primitives. Plan 01 -- module tests only;
gameplay emit sites are covered by plan 03."""

import pytest
from src.anim import event_bus


@pytest.fixture(autouse=True)
def _reset_bus():
    """Mirror of tests/test_tuning_livereach.py:51-56 reset pattern."""
    event_bus.reset()
    yield
    event_bus.reset()


def test_subscribe_emit_roundtrip():
    received = []
    event_bus.subscribe("x", lambda k=None: received.append(k))
    event_bus.emit("x", k=1)
    assert received == [1]


def test_emit_with_no_subscribers_is_noop():
    # Should not raise.
    event_bus.emit("nonexistent_event", data=42)


def test_multiple_subscribers_called_in_order():
    order = []
    event_bus.subscribe("evt", lambda: order.append("first"))
    event_bus.subscribe("evt", lambda: order.append("second"))
    event_bus.emit("evt")
    assert order == ["first", "second"]


def test_reset_clears_subscribers():
    called = []
    event_bus.subscribe("x", lambda: called.append(True))
    event_bus.reset()
    event_bus.emit("x")
    assert called == []
