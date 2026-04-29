"""Phase 32 Wave 0 — RED tests for FusionManager + ChargeController FSM behaviors.

Per VALIDATION.md Wave 0 Requirements + RESEARCH § Validation Architecture
(lines 762-805). These tests authored against the FusionAbility / FusionManager
public API specified in CONTEXT (D-09, D-12, D-15, D-17) and the Wave-2/4 plan
skeletons.

State on Wave 0:
- All tests SKIP cleanly until Plan 04 ships `src.fusion.manager` (importorskip
  at module top).
- `test_no_mid_drill_cancel` adds a SECOND skip layer (source-introspection on
  Player.handle_input) that survives the wave-2-to-wave-4 window where
  `src.fusion.manager` exists but `Player.handle_input` still has the mid-drill
  cancel block. It flips GREEN automatically when Plan 06 deletes that block.

Coverage:
- FUS-04 / FUS-05: 100% juice gate, fuse_start latch position, free-cancel,
  no-mid-drill-cancel guard.
"""
import sys
import types

# Mock pyxel before any game imports (matches tests/test_fusion.py:5-27 idiom).
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

# Per-test importorskip pattern (NOT module-level): keeps test list visible to
# `pytest --co` while skipping each test at runtime until Plan 04/05 ships
# `src.fusion.manager` / `src.fusion.charge_controller` / `src.fusion.drill_dive`.
# Centralized so each test body can call `_require_fusion_modules()` once.
def _require_fusion_modules():
    pytest.importorskip("src.fusion.manager")
    pytest.importorskip("src.fusion.charge_controller")
    pytest.importorskip("src.fusion.drill_dive")


from unittest.mock import MagicMock

from src.anim import event_bus
from src.core import tuning


class MockLevelMap:
    """Minimal level map mirroring tests/test_fusion.py:35-41."""

    def check_collision(self, x, y, w, h):
        return False

    def check_hazard(self, x, y, w, h):
        return False

    def get_destructible_at(self, x, y, w, h):
        return None


def make_game_player_slime(px=50, py=50, sx=100, sy=50):
    """Return (game, player, slime, level_map) with real FusionManager + ChargeController.

    Phase 32 Wave 0 helper. Player.game is set so the @property is_fused (D-14a)
    resolves through the manager.
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


# --- FUS-05: 100% juice gate -----------------------------------------------


def test_drill_requires_full_juice():
    """100% gate: drill_dive.can_activate returns False when juice < max, True at max."""
    _require_fusion_modules()
    from src.fusion.drill_dive import DrillDive

    drill = DrillDive()
    game, player, slime, _ = make_game_player_slime()

    # Make the airborne + has_drill + dist preconditions trivially true via mocks
    # so the only failing precondition is juice < max.
    player.is_grounded = False
    player.has_drill = True
    # game.fusion_manager.is_fused must be True for drill activation per D-17.
    game.fusion_manager.latch_fuse(slime)

    slime.juice = slime.max_juice - 0.1  # 99% — below the 100% gate
    assert drill.can_activate(player, slime) is False, (
        "DrillDive.can_activate must return False when juice < max_juice (100% gate)"
    )

    slime.juice = slime.max_juice  # 100% — gate satisfied
    assert drill.can_activate(player, slime) is True, (
        "DrillDive.can_activate must return True when juice == max_juice"
    )


# --- FUS-05: fuse_start latch position --------------------------------------


def test_fuse_start_emits_at_latch():
    """fuse_start fires at WINDUP→FUSED 200% latch, NOT at WINDUP begin.

    Subscribes to fuse_start, runs ChargeController state through RECALL → WINDUP
    and asserts NO emit at WINDUP entry. Steps until WINDUP→FUSED latch
    (second-pass 100→200% reached). Asserts exactly one fuse_start was captured.
    """
    _require_fusion_modules()
    captured = []
    event_bus.subscribe("fuse_start", lambda **kw: captured.append(kw))

    game, player, slime, _ = make_game_player_slime(px=50, py=50, sx=52, sy=50)
    # Slime starts within RECALL_OVERLAP_DIST so RECALL completes immediately.
    slime.juice = slime.max_juice  # 100% so WINDUP can begin on dock

    # Step 1: drive ChargeController through IDLE → RECALL → WINDUP.
    # Use a mock input_manager that holds Z (spit) for the entire fuse sequence.
    input_manager = MagicMock()
    input_manager.btn = lambda name: name == "spit"
    input_manager.btnp = lambda name: False
    input_manager.btnr = lambda name: False
    input_manager.was_tap = lambda name: False
    input_manager.hold_frames = lambda name: 0

    # Drive enough frames to reach WINDUP entry. After at most a few frames the
    # slime is overlapping and WINDUP begins. Fuse_start must NOT yet have emitted.
    MAX_RECALL_FRAMES = 10  # named constant — overlap is immediate but safe upper bound
    for _ in range(MAX_RECALL_FRAMES):
        game.charge_controller.handle_z_input(player, slime, input_manager)
        if game.charge_controller._state == "WINDUP":
            break
    assert game.charge_controller._state == "WINDUP", (
        "ChargeController should reach WINDUP within MAX_RECALL_FRAMES with full juice + docked"
    )
    assert len(captured) == 0, (
        f"fuse_start must NOT emit at WINDUP entry, got {len(captured)} emit(s)"
    )

    # Step 2: drive WINDUP frames until FUSED latch.
    MAX_WINDUP_FRAMES = 120  # ~2s safety margin against the ~30f spec
    for _ in range(MAX_WINDUP_FRAMES):
        game.charge_controller.handle_z_input(player, slime, input_manager)
        if game.fusion_manager.is_fused:
            break
    assert game.fusion_manager.is_fused is True, (
        "FusionManager.is_fused should be True after WINDUP completes"
    )
    assert len(captured) == 1, (
        f"fuse_start must emit exactly once at the latch, got {len(captured)}"
    )


def test_fuse_charging_emits_at_windup_entry():
    """fuse_charging fires once at the moment ChargeController enters WINDUP.

    The convergence + blob buildup animation needs to play DURING the 30-frame
    second-pass charge, not only at the latch climax. This test asserts that
    fuse_charging emits exactly once at IDLE→RECALL→WINDUP transition (not
    again per-frame, and not at the FUSED latch).
    """
    _require_fusion_modules()
    captured = []
    event_bus.subscribe("fuse_charging", lambda **kw: captured.append(kw))

    game, player, slime, _ = make_game_player_slime(px=50, py=50, sx=52, sy=50)
    slime.juice = slime.max_juice

    input_manager = MagicMock()
    input_manager.btn = lambda name: name == "spit"
    input_manager.btnp = lambda name: False
    input_manager.btnr = lambda name: False
    input_manager.was_tap = lambda name: False
    input_manager.hold_frames = lambda name: 0

    MAX_RECALL_FRAMES = 10
    for _ in range(MAX_RECALL_FRAMES):
        game.charge_controller.handle_z_input(player, slime, input_manager)
        if game.charge_controller._state == "WINDUP":
            break
    assert game.charge_controller._state == "WINDUP"
    assert len(captured) == 1, (
        f"fuse_charging must emit exactly once at WINDUP entry, got {len(captured)}"
    )

    # Run the rest of WINDUP through the latch — emit count must NOT increase.
    MAX_WINDUP_FRAMES = 120
    for _ in range(MAX_WINDUP_FRAMES):
        game.charge_controller.handle_z_input(player, slime, input_manager)
        if game.fusion_manager.is_fused:
            break
    assert game.fusion_manager.is_fused is True
    assert len(captured) == 1, (
        f"fuse_charging must NOT re-emit during WINDUP frames or at the latch, "
        f"got {len(captured)} total emit(s)"
    )


# --- FUS-05: free-cancel during WINDUP --------------------------------------


def test_windup_release_free_cancel():
    """Releasing Z during WINDUP returns ChargeController to IDLE without juice loss.

    Per FUSION-DESIGN § Juice Economy + CONTEXT D-23c: WINDUP IS the cancel
    window. Releasing Z mid-WINDUP returns to IDLE with juice unchanged and no
    fuse_start emit.
    """
    _require_fusion_modules()
    captured = []
    event_bus.subscribe("fuse_start", lambda **kw: captured.append(kw))

    game, player, slime, _ = make_game_player_slime(px=50, py=50, sx=52, sy=50)
    slime.juice = slime.max_juice
    initial_juice = slime.juice

    # Step into WINDUP with Z held.
    held_input = MagicMock()
    held_input.btn = lambda name: name == "spit"
    held_input.btnp = lambda name: False
    held_input.btnr = lambda name: False
    held_input.was_tap = lambda name: False
    held_input.hold_frames = lambda name: 0
    MAX_RECALL_FRAMES = 10
    for _ in range(MAX_RECALL_FRAMES):
        game.charge_controller.handle_z_input(player, slime, held_input)
        if game.charge_controller._state == "WINDUP":
            break
    assert game.charge_controller._state == "WINDUP", (
        "ChargeController should reach WINDUP before testing cancel"
    )

    # Now release Z mid-WINDUP. Single frame of btnr("spit") -> True.
    release_input = MagicMock()
    release_input.btn = lambda name: False
    release_input.btnp = lambda name: False
    release_input.btnr = lambda name: name == "spit"
    release_input.was_tap = lambda name: False
    release_input.hold_frames = lambda name: 0
    game.charge_controller.handle_z_input(player, slime, release_input)

    assert game.charge_controller._state == "IDLE", (
        "ChargeController should return to IDLE on Z release during WINDUP"
    )
    assert slime.juice == initial_juice, (
        f"juice must be unchanged on free-cancel, got {slime.juice} (expected {initial_juice})"
    )
    assert len(captured) == 0, (
        f"fuse_start must NOT emit on free-cancel, got {len(captured)} emit(s)"
    )
    assert game.fusion_manager.is_fused is False, (
        "FusionManager must NOT be fused after free-cancel"
    )


# --- FUS-04 / FUS-05: no mid-drill cancel ------------------------------------


def test_no_mid_drill_cancel():
    """Pressing SPACE during a drill must NOT cancel — drill is committed (D-08).

    Two-layer skip guard:
    - Module-level pytest.importorskip("src.fusion.manager") skips until Plan 04.
    - Body-level source-introspection guard skips until Plan 06 deletes the
      mid-drill jump-cancel block in Player.handle_input.

    Without the body-level guard, this test would import successfully after
    Plan 04 ships but FAIL RED in the wave-2-to-wave-4 window because
    Player.handle_input still has the cancel branch.
    """
    _require_fusion_modules()
    import inspect

    from src.entities.player import Player
    from src.fusion.drill_dive import DrillDive

    # Body-level guard: skip until Plan 06 strips the mid-drill cancel branch.
    src = inspect.getsource(Player.handle_input)
    if 'btnp("jump")' in src and 'state == "DIVING"' in src:
        pytest.skip(
            "Plan 06 (mid-drill cancel deletion) not yet shipped — guard re-checks each run"
        )

    # Real test body — runs only after Plan 06.
    captured_fuse_end = []
    event_bus.subscribe("fuse_end", lambda **kw: captured_fuse_end.append(kw))

    game, player, slime, _ = make_game_player_slime()
    player.is_grounded = False
    player.has_drill = True
    slime.juice = slime.max_juice

    # Latch into FUSED + activate drill.
    game.fusion_manager.latch_fuse(slime)
    drill = DrillDive()
    drill.on_enter(player, slime, context={})
    # Manager owns active ability; for the test we manually attach to mirror tick().
    game.fusion_manager._active = drill
    player.state = "DIVING"

    # Simulate one frame of input_manager.btnp("jump") returning True.
    jump_input = MagicMock()
    jump_input.btn = lambda name: False
    jump_input.btnp = lambda name: name == "jump"
    jump_input.btnr = lambda name: False
    jump_input.was_tap = lambda name: False
    jump_input.hold_frames = lambda name: 0

    # Drive a tick — drill must NOT exit and player must stay DIVING.
    DT_DEFAULT = 1.0  # named constant — single-frame dispatch
    game.fusion_manager.tick(player, slime, DT_DEFAULT)

    assert game.fusion_manager.is_fused is True, (
        "FusionManager.is_fused must remain True after jump press during drill"
    )
    assert game.fusion_manager._active is drill, (
        "Active ability must still be DrillDive (no cancel)"
    )
    assert player.state == "DIVING", (
        f"Player.state must remain DIVING, got {player.state}"
    )
    assert len(captured_fuse_end) == 0, (
        f"fuse_end must NOT emit on jump press during drill, got {len(captured_fuse_end)}"
    )


# --- Fused-idle juice-drain unfuse (regression: stuck fused at 0 juice) -----


def test_fused_idle_zero_juice_force_exits():
    """When fused with no active ability and juice drains to 0 (e.g., daze-shot
    spam), FusionManager.tick must force_exit('juice_empty').

    Regression: without this check, the player got stuck fused at 0 juice —
    drill needs 100% juice (D-15 gate), daze fire needs SLIME_DAZE_COST, pogo
    requires unfused, so no input could recover. tick() previously returned
    early on `_active is None` without observing juice.
    """
    _require_fusion_modules()
    captured_fuse_end = []
    event_bus.subscribe("fuse_end", lambda **kw: captured_fuse_end.append(kw))

    game, player, slime, _ = make_game_player_slime()
    game.fusion_manager.latch_fuse(slime)
    assert game.fusion_manager.is_fused is True
    assert game.fusion_manager._active is None  # fused-idle (no drill, no pogo)

    slime.juice = 0  # simulate post-daze-fire drain

    DT_DEFAULT = 1.0
    game.fusion_manager.tick(player, slime, DT_DEFAULT)

    assert game.fusion_manager.is_fused is False, (
        "fused-idle + juice <= 0 must force_exit; player stuck otherwise"
    )
    assert slime.is_fused is False, (
        "slime.is_fused must mirror manager.is_fused (Pitfall 4)"
    )
    assert len(captured_fuse_end) == 1, (
        f"fuse_end must emit once on juice_empty force_exit, got {len(captured_fuse_end)}"
    )
