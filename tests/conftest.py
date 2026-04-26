"""Phase 26 shared pytest fixtures (extended in Phase 32 with FusionManager helpers).

- pyxel MagicMock installed at module load so src.entities.player is importable
  in a headless harness (pattern from test suites that need pyxel mocked).
- Autouse event_bus.reset() keeps test cases hermetic (Pitfall 1 guard).
- mock_level / mock_slime shared fixtures for gameplay integration tests.
- Phase 32: `make_game_with_fusion` fixture wires a real FusionManager +
  ChargeController inside a MagicMock game. importorskip-guarded so it skips
  cleanly until Plan 04 ships `src.fusion.manager`.
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


@pytest.fixture
def make_game_with_fusion():
    """Phase 32 helper. Returns a factory building a MagicMock game with real
    FusionManager + ChargeController instances attached. Skipped until Plan 04
    ships `src.fusion.manager` (importorskip-guarded).

    Usage::

        def test_something(make_game_with_fusion, mock_slime):
            game = make_game_with_fusion()
            game.fusion_manager.latch_fuse(mock_slime)
            ...
    """
    pytest.importorskip("src.fusion.manager")
    pytest.importorskip("src.fusion.drill_dive")
    pytest.importorskip("src.fusion.pogo")

    from src.fusion.manager import FusionManager
    from src.fusion.charge_controller import ChargeController
    from src.fusion.drill_dive import DrillDive
    from src.fusion.pogo import Pogo

    def _factory():
        game = MagicMock()
        game.fusion_manager = FusionManager(
            abilities={"drill_dive": DrillDive(), "pogo": Pogo()}
        )
        game.charge_controller = ChargeController(fusion_manager=game.fusion_manager)
        return game

    return _factory
