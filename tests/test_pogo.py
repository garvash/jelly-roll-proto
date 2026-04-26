"""Phase 32 Wave 0 — RED tests for Pogo (unfused DOWN+SPACE ability).

Per VALIDATION.md Wave 0 Requirements + RESEARCH § Validation Architecture
(lines 762-805). Pogo is the unfused branch of the DOWN+SPACE input dispatch
(D-17). Constants are HARDCODED in src.fusion.pogo per CONTEXT D-18 (NOT in
tuning.py — pogo is a permanent unfused option, not a tuning surface).

State on Wave 0:
- Module-level `pytest.importorskip("src.fusion.pogo")` skips until Plan 05.

Coverage (FUS-04 / FUS-05):
- Activation gate: airborne unfused (no juice gate per D-20).
- Constants exist in src.fusion.pogo (NOT in tuning) per D-18.
- No juice cost on activation/tick (D-20 — pogo is free).
"""
import sys
import types

# Mock pyxel before any game imports.
if "pyxel" not in sys.modules:
    mock_pyxel = types.ModuleType("pyxel")
    mock_pyxel.KEY_LEFT = 0
    mock_pyxel.KEY_RIGHT = 1
    mock_pyxel.KEY_UP = 2
    mock_pyxel.KEY_DOWN = 3
    mock_pyxel.KEY_SPACE = 4
    mock_pyxel.KEY_Z = 5
    mock_pyxel.KEY_J = 6
    mock_pyxel.KEY_V = 7
    mock_pyxel.KEY_K = 8
    mock_pyxel.KEY_A = 9
    mock_pyxel.KEY_D = 10
    mock_pyxel.KEY_W = 11
    mock_pyxel.KEY_S = 12
    mock_pyxel.frame_count = 0
    mock_pyxel.btn = lambda k: False
    mock_pyxel.btnp = lambda k, **kw: False
    mock_pyxel.btnr = lambda k: False
    mock_pyxel.blt = lambda *a, **kw: None
    mock_pyxel.rect = lambda *a, **kw: None
    mock_pyxel.pset = lambda *a, **kw: None
    sys.modules["pyxel"] = mock_pyxel

import pytest

# Per-test importorskip pattern: keeps test list visible to `pytest --co` while
# skipping each test at runtime until Plan 05 ships `src.fusion.pogo`.
def _require_pogo_module():
    pytest.importorskip("src.fusion.pogo")


from unittest.mock import MagicMock

from src.core import tuning


class MockLevelMap:
    def check_collision(self, x, y, w, h):
        return False

    def check_hazard(self, x, y, w, h):
        return False

    def get_destructible_at(self, x, y, w, h):
        return None


def make_player_and_slime(px=50, py=50, sx=100, sy=50):
    from src.entities.player import Player
    from src.entities.slime import Slime

    level_map = MockLevelMap()
    player = Player(px, py, level_map)
    slime = Slime(sx, sy)
    return player, slime, level_map


# --- Activation gate (airborne, unfused, no juice gate) --------------------


def test_pogo_activates_unfused():
    """Pogo.can_activate returns True for airborne unfused player.

    Per D-17: Pogo is the unfused branch of DOWN+SPACE airborne dispatch.
    Per D-20: Pogo has NO juice gate (free, even with empty slime).
    """
    _require_pogo_module()
    from src.fusion.pogo import Pogo

    player, _, _ = make_player_and_slime()
    player.is_grounded = False  # airborne precondition
    # Player.is_fused is False by default (no fusion_manager attached).

    slime = MagicMock()
    slime.juice = 0.0  # Empty — must NOT block pogo (no juice gate per D-20)
    slime.max_juice = 200.0
    slime.is_fused = False

    assert Pogo().can_activate(player, slime) is True, (
        "Pogo.can_activate must return True for airborne unfused player even with empty juice"
    )


# --- Constants present, hardcoded (NOT in tuning) ---------------------------


def test_pogo_constants_hardcoded():
    """POGO_BOUNCE_VELOCITY / POGO_COOLDOWN_FRAMES / POGO_DAMAGE exist as
    module-level constants in src.fusion.pogo (D-18: hardcoded, NOT in tuning)."""
    _require_pogo_module()
    from src.fusion import pogo as pogo_module

    # All three constants must exist on the module.
    assert hasattr(pogo_module, "POGO_BOUNCE_VELOCITY"), (
        "src.fusion.pogo must define POGO_BOUNCE_VELOCITY"
    )
    assert hasattr(pogo_module, "POGO_COOLDOWN_FRAMES"), (
        "src.fusion.pogo must define POGO_COOLDOWN_FRAMES"
    )
    assert hasattr(pogo_module, "POGO_DAMAGE"), (
        "src.fusion.pogo must define POGO_DAMAGE"
    )

    # All must be numeric (int or float).
    assert isinstance(pogo_module.POGO_BOUNCE_VELOCITY, (int, float))
    assert isinstance(pogo_module.POGO_COOLDOWN_FRAMES, (int, float))
    assert isinstance(pogo_module.POGO_DAMAGE, (int, float))

    # D-18: NOT in tuning.* (pogo is hardcoded, not a tuning surface).
    assert not hasattr(tuning, "POGO_BOUNCE_VELOCITY"), (
        "POGO_BOUNCE_VELOCITY must NOT live in tuning.* (D-18: hardcoded only)"
    )
    assert not hasattr(tuning, "POGO_COOLDOWN_FRAMES"), (
        "POGO_COOLDOWN_FRAMES must NOT live in tuning.* (D-18: hardcoded only)"
    )
    assert not hasattr(tuning, "POGO_DAMAGE"), (
        "POGO_DAMAGE must NOT live in tuning.* (D-18: hardcoded only)"
    )


# --- No juice cost ---------------------------------------------------------


def test_pogo_no_juice_cost():
    """Pogo.on_enter and Pogo.on_tick must NEVER call slime.consume (D-20: free)."""
    _require_pogo_module()
    from src.fusion.pogo import Pogo

    player, _, _ = make_player_and_slime()
    slime = MagicMock()
    slime.juice = 100.0
    slime.max_juice = 200.0
    slime.consume = MagicMock()
    slime.refill = MagicMock()

    pogo = Pogo()
    pogo.on_enter(player, slime, context={})
    DT_DEFAULT = 1.0  # named constant — single-frame dispatch
    pogo.on_tick(player, slime, DT_DEFAULT)

    slime.consume.assert_not_called()
