"""Tests for the fusion system: recall, fuse/unfuse, mana shield, dissipation (D-01 through D-05).

Phase 32 Wave 0 migration: deprecated Player fuse/unfuse callsites moved to
`game.fusion_manager.latch_fuse(slime)` / `game.fusion_manager.force_exit(player, slime, reason)`
per CONTEXT D-13 (Player methods deleted, no shim) and Plan 04 final
`force_exit(player, slime, reason)` signature.

Tests SKIP cleanly until Plan 04 ships `src.fusion.manager` (per-test importorskip
guard). After Plan 04 + Plan 06 land they GREEN automatically.
"""
import sys
import types

# Mock pyxel before any game imports.
# Phase 32 fix (Rule 3 — blocking pre-existing issue): use setdefault so we
# don't overwrite the conftest.py MagicMock pyxel install when test_fusion is
# collected after a test that already imported via the MagicMock path. The
# previous unconditional `sys.modules["pyxel"] = mock_pyxel` broke later
# imports that referenced attributes not in this partial mock (e.g.
# `pyxel.GAMEPAD1_BUTTON_DPAD_LEFT` from src/core/input.py).
if "pyxel" not in sys.modules or not hasattr(sys.modules["pyxel"], "GAMEPAD1_BUTTON_DPAD_LEFT"):
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
    sys.modules.setdefault("pyxel", mock_pyxel)

import pytest
from unittest.mock import MagicMock

from src.core.constants import (
    RECALL_SPEED, RECALL_OVERLAP_DIST, MANA_SHIELD_COST,
    SLIME_DISSIPATE_COOLDOWN, INVULN_DURATION, JUICE_MAX
)


# Per-test importorskip pattern: keeps test list visible to `pytest --co` while
# skipping each test at runtime until Plan 04 ships `src.fusion.manager`.
def _require_fusion_modules():
    pytest.importorskip("src.fusion.manager")
    pytest.importorskip("src.fusion.drill_dive")
    pytest.importorskip("src.fusion.pogo")


class MockLevelMap:
    def check_collision(self, x, y, w, h):
        return False
    def check_hazard(self, x, y, w, h):
        return False
    def get_destructible_at(self, x, y, w, h):
        return None


def make_game_player_slime(px=50, py=50, sx=100, sy=50):
    """Phase 32 Wave 0 migration. Returns (game, player, slime, level_map).

    Player.game is set so the @property is_fused (D-14a) resolves through
    the manager. game.fusion_manager + game.charge_controller are real
    instances (not MagicMock) so latch_fuse / force_exit run real code —
    the unit-vs-integration line is fuzzy here intentionally; we want
    regression depth on the new manager.
    """
    from src.fusion.manager import FusionManager
    from src.fusion.charge_controller import ChargeController
    from src.fusion.drill_dive import DrillDive
    from src.fusion.pogo import Pogo
    from src.entities.player import Player
    from src.entities.slime import Slime

    level_map = MockLevelMap()
    game = MagicMock()
    game.fusion_manager = FusionManager(
        abilities={"drill_dive": DrillDive(), "pogo": Pogo()}
    )
    game.charge_controller = ChargeController(fusion_manager=game.fusion_manager)
    player = Player(px, py, level_map)
    player.game = game
    slime = Slime(sx, sy)
    return game, player, slime, level_map


def test_fuse_sets_both_flags():
    """latch_fuse(slime) sets player.is_fused=True AND slime.is_fused=True."""
    _require_fusion_modules()
    game, player, slime, _ = make_game_player_slime()
    assert not player.is_fused
    assert not slime.is_fused
    game.fusion_manager.latch_fuse(slime)
    assert player.is_fused
    assert slime.is_fused


def test_unfuse_clears_both_flags():
    """force_exit(player, slime, 'test_unfuse') sets both is_fused flags to False (D-15)."""
    _require_fusion_modules()
    game, player, slime, _ = make_game_player_slime()
    game.fusion_manager.latch_fuse(slime)
    assert player.is_fused and slime.is_fused
    game.fusion_manager.force_exit(player, slime, "test_unfuse")
    assert not player.is_fused
    assert not slime.is_fused


def test_unfuse_with_dissipate():
    """force_exit(player, slime, 'juice_empty') triggers slime.dissipate() (D-07)."""
    _require_fusion_modules()
    game, player, slime, _ = make_game_player_slime()
    game.fusion_manager.latch_fuse(slime)
    game.fusion_manager.force_exit(player, slime, "juice_empty")
    assert not player.is_fused
    assert not slime.is_fused
    assert slime.is_dissipated
    assert slime.dissipate_timer == SLIME_DISSIPATE_COOLDOWN


def test_mana_shield_consumes_juice():
    """Fused damage consumes juice, not HP (D-04).

    take_damage routes through game.fusion_manager.apply_fused_damage
    after Plan 06 wires the mana shield path.
    """
    _require_fusion_modules()
    game, player, slime, _ = make_game_player_slime()
    game.fusion_manager.latch_fuse(slime)
    slime.juice = JUICE_MAX  # Full juice
    initial_hp = player.hp
    initial_juice = slime.juice

    result = player.take_damage(1, source_x=60, slime=slime)

    assert result is True
    assert player.hp == initial_hp  # HP unchanged
    assert slime.juice == initial_juice - MANA_SHIELD_COST
    assert player.invuln_timer == INVULN_DURATION


def test_mana_shield_dissipates_on_empty():
    """Fused with juice < MANA_SHIELD_COST: take_damage -> slime dissipates (D-05)."""
    _require_fusion_modules()
    game, player, slime, _ = make_game_player_slime()
    game.fusion_manager.latch_fuse(slime)
    # Set juice just barely enough to be consumed but will hit 0
    slime.juice = MANA_SHIELD_COST - 5  # Will be consumed to 0

    result = player.take_damage(1, source_x=60, slime=slime)

    assert result is True
    assert player.hp == player.max_hp  # HP unchanged (mana shield absorbed)
    assert slime.juice == 0
    assert slime.is_dissipated
    assert not player.is_fused


def test_recall_moves_toward_player():
    """Slime at (100, 50), player at (50, 50): update_recall moves slime closer."""
    _require_fusion_modules()
    _, _, slime, _ = make_game_player_slime(sx=100, sy=50)
    slime.recall(50, 50)
    assert slime.is_recalling

    initial_x = slime.x
    slime.update_recall(50, 50)
    assert slime.x < initial_x  # Moved left toward player


def test_recall_arrives_triggers_overlap():
    """Slime within RECALL_OVERLAP_DIST of player -> update_recall returns True."""
    _require_fusion_modules()
    _, _, slime, _ = make_game_player_slime(sx=52, sy=50)  # Very close
    slime.recall(50, 50)

    arrived = slime.update_recall(50, 50)
    assert arrived is True
    assert not slime.is_recalling


def test_dissipate_timer_countdown():
    """dissipate() sets timer, ticks down to 0, then reforms at full juice."""
    _require_fusion_modules()
    _, player, slime, lm = make_game_player_slime()
    slime.dissipate()
    assert slime.is_dissipated
    assert slime.dissipate_timer == SLIME_DISSIPATE_COOLDOWN

    # Tick down almost completely
    for _ in range(SLIME_DISSIPATE_COOLDOWN - 1):
        reformed = slime.update_dissipation(player.x, player.y, True, lm)
        assert not reformed
        assert slime.is_dissipated

    # Final tick triggers reform
    reformed = slime.update_dissipation(player.x, player.y, True, lm)
    assert reformed is True
    assert not slime.is_dissipated
    assert slime.juice == slime.max_juice


def test_fuse_clears_recall_state():
    """latch_fuse() should clear slime.is_recalling.

    Plan 31.5-05 dropped is_holding_position assertion (Hold state stripped).
    Phase 32 (D-14a): dropped `not player.is_charging_recall` assertion —
    is_charging_recall is removed from Player (RESEARCH FUS-04 grep gate).
    The clear-recall behavior now lives in FusionManager.latch_fuse per
    Plan 04 (sets `slime.is_recalling = False`).
    """
    _require_fusion_modules()
    game, _, slime, _ = make_game_player_slime()
    slime.is_recalling = True
    game.fusion_manager.latch_fuse(slime)
    assert not slime.is_recalling


def test_normal_damage_when_not_fused():
    """Without fusion, take_damage reduces HP normally."""
    _require_fusion_modules()
    _, player, slime, _ = make_game_player_slime()
    initial_hp = player.hp
    player.take_damage(1, source_x=60, slime=slime)
    assert player.hp == initial_hp - 1
