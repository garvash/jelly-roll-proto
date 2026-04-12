"""Phase 26 ANIM-02 pub-sub dispatcher. Module-level singleton per D-13a.

Every subscriber is called synchronously on the emitting frame. Pyxel is
single-threaded by design, so emit walking the subscriber list inline is
safe. Tests call reset() in an autouse fixture to prevent cross-test
contamination (inherited from Phase 24/25's tuning.reset() pattern).
"""
from typing import Callable

_subscribers: dict[str, list[Callable[..., None]]] = {}


def subscribe(event_name: str, callback: Callable[..., None]) -> None:
    _subscribers.setdefault(event_name, []).append(callback)


def emit(event_name: str, **kwargs) -> None:
    for cb in _subscribers.get(event_name, ()):
        cb(**kwargs)


def reset() -> None:
    """Clear all subscribers. Pytest fixtures call this between tests."""
    _subscribers.clear()
