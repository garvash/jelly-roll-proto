"""Phase 26 shared pytest fixtures.

- pyxel MagicMock installed at module load so src.entities.player is importable
  in a headless harness (pattern from test suites that need pyxel mocked).
- Autouse event_bus.reset() keeps test cases hermetic (Pitfall 1 guard).
- mock_level / mock_slime shared fixtures for gameplay integration tests.
"""
import sys
from unittest.mock import MagicMock

# Pyxel must be mocked BEFORE any src.entities.player import anywhere in the
# test suite (or any test file that does `from src.entities.player import Player`).
sys.modules.setdefault("pyxel", MagicMock())

import pytest
from src.anim import event_bus


@pytest.fixture(autouse=True)
def _reset_event_bus():
    """Clear the module-level event bus between tests (Pitfall 1)."""
    event_bus.reset()
    yield
    event_bus.reset()


@pytest.fixture
def mock_level():
    level = MagicMock()
    level.check_collision.return_value = False
    level.check_hazard.return_value = False
    level.is_switch.return_value = False
    level.get_zone_hazard_type.return_value = None
    level.get_destructible_at.return_value = None
    level.get_cracked_h_at.return_value = None
    level.get_cracked_v_at.return_value = None
    return level


@pytest.fixture
def mock_slime():
    slime = MagicMock()
    slime.x = 100
    slime.y = 100
    slime.w = 8
    slime.h = 8
    slime.juice = 100
    slime.max_juice = 100
    slime.is_alive = True
    slime.is_fused = False
    slime.is_recalling = False
    slime.is_holding_position = False
    slime.is_dissipated = False
    slime.is_being_absorbed = False
    return slime
