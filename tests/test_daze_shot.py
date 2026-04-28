"""Phase 33 FUS-06 D-17 — daze-shot fused-branch tests.

RED until Wave 2 modifies src/entities/player.py:197 to remove the
`not self.is_fused` gate and add the SLIME_DAZE_COST consume + daze_fire emit.

The fused-branch contract (D-17):
- When the player is fused and Z-tap fires (was_tap("spit")), the fused
  branch fires a projectile, consumes tuning.SLIME_DAZE_COST juice, and
  emits a "daze_fire" event.
- Cancel-spam guard (Pitfall 4): if mock_slime.juice < tuning.SLIME_DAZE_COST,
  no projectile fires, no juice is consumed, no event emits.
"""
import pytest
from unittest.mock import MagicMock, patch

# Wave 2 dep: until make_game_with_fusion fixture's importorskip succeeds,
# this module would still be importable, but the tests rely on the fixture
# (which itself importorskip's src.fusion.manager + drill_dive + pogo).
# Adding an explicit module-level guard documents the dependency chain.
pytest.importorskip("src.fusion.manager", reason="Wave 2 dep — fused-branch FSM")

from src.anim import event_bus
import src.core.input as input_manager
from src.core import tuning


def _btn_map_factory(**overrides):
    mapping = {"left": False, "right": False, "up": False, "down": False,
               "jump": False, "spit": False}
    mapping.update(overrides)
    return lambda name: mapping.get(name, False)


# --- Test 1: fused Z-tap fires daze ----------------------------------------


def test_fused_tap_fires_daze(mock_level, mock_slime, make_game_with_fusion):
    """D-17: fused player Z-tap fires projectile + consumes SLIME_DAZE_COST
    + emits daze_fire event."""
    captured = []
    event_bus.subscribe("daze_fire", lambda **kw: captured.append(kw))
    from src.entities.player import Player
    game = make_game_with_fusion()
    # Empty enemy/mole/world so handle_input's auto-aim block is a no-op
    # (the MagicMock default would yield MagicMocks with non-comparable .x/.y).
    game.mole = None
    game.enemies = []
    game.projectiles = []
    game.world.current_level = None
    p = Player(100, 100, mock_level, game=game)
    p.is_grounded = True
    game.fusion_manager.latch_fuse(mock_slime)
    assert p.is_fused
    mock_slime.juice = tuning.SLIME_DAZE_COST + 10
    initial_juice = mock_slime.juice
    # Wire consume() to actually decrement juice (mock_slime is a MagicMock;
    # default consume is a no-op MagicMock that wouldn't move .juice). We need
    # real decrement to validate the SLIME_DAZE_COST exact-cost contract.
    def _consume(amount):
        mock_slime.juice = max(0.0, mock_slime.juice - amount)
    mock_slime.consume = _consume
    with patch.object(input_manager, "btn", side_effect=_btn_map_factory()), \
         patch.object(input_manager, "btnp", side_effect=_btn_map_factory()), \
         patch.object(input_manager, "btnr", side_effect=_btn_map_factory()), \
         patch.object(input_manager, "was_tap", return_value=True), \
         patch.object(input_manager, "hold_frames", return_value=0):
        p.handle_input(mock_slime)
    # W#1 closure: fused branch consumes EXACTLY SLIME_DAZE_COST (no SPIT_COST double-charge).
    assert mock_slime.juice == initial_juice - tuning.SLIME_DAZE_COST
    assert len(captured) >= 1


# --- Test 2: fused Z-tap with low juice does NOT fire ----------------------


def test_daze_blocked_on_low_juice(mock_level, mock_slime, make_game_with_fusion):
    """D-17 Pitfall 4 cancel-spam guard: fused player with juice <
    SLIME_DAZE_COST does NOT fire and does NOT consume juice."""
    captured = []
    event_bus.subscribe("daze_fire", lambda **kw: captured.append(kw))
    from src.entities.player import Player
    game = make_game_with_fusion()
    # Empty enemy/mole/world so handle_input's auto-aim block is a no-op.
    game.mole = None
    game.enemies = []
    game.projectiles = []
    game.world.current_level = None
    p = Player(100, 100, mock_level, game=game)
    p.is_grounded = True
    game.fusion_manager.latch_fuse(mock_slime)
    # Juice intentionally below SLIME_DAZE_COST
    mock_slime.juice = max(0.0, tuning.SLIME_DAZE_COST - 1)
    initial_juice = mock_slime.juice
    with patch.object(input_manager, "was_tap", return_value=True), \
         patch.object(input_manager, "btn", side_effect=_btn_map_factory()), \
         patch.object(input_manager, "btnp", side_effect=_btn_map_factory()), \
         patch.object(input_manager, "btnr", side_effect=_btn_map_factory()), \
         patch.object(input_manager, "hold_frames", return_value=0):
        p.handle_input(mock_slime)
    assert mock_slime.juice == initial_juice  # unchanged
    assert len(captured) == 0


# --- Test 3: daze stun applies on Snail contact via main.py loop -----------


def test_daze_stun_applies_on_snail_contact(mock_level):
    """Phase 33 D-17 / Blocker #2 closure: daze-flagged projectile
    intersecting an alive Snail sets snail.stun_timer and consumes the
    projectile via main.py's per-frame contact-scan helper.

    Calls main.apply_daze_stun_contacts directly (planner-discretion per
    Plan 04 Task 3 — extracts the scan into a module-level helper to
    avoid pulling pyxel.init via Game()).

    Plan 03 Task 1 adds Enemy.stun_timer; this worktree may execute in
    parallel against a base that does not yet have it, so the test
    setattr's stun_timer=0 defensively. Once Plan 03 merges, the setattr
    is a no-op (the attribute is already 0 by default).
    """
    from src.entities.projectile import Projectile, STUN_DURATION_FRAMES
    from src.entities.enemies import Snail
    from main import apply_daze_stun_contacts

    snail = Snail(50, 50)
    # Defensive: Plan 03 Task 1 adds Enemy.stun_timer (this attribute on the
    # Enemy base class). Set it explicitly so the test passes regardless of
    # parallel-wave merge order. After Plan 03 merges, this setattr is
    # idempotent (sets the already-zero default to zero).
    if not hasattr(snail, "stun_timer"):
        snail.stun_timer = 0
    assert snail.stun_timer == 0

    # Direct daze-flagged projectile at snail's position (overlaps AABB)
    proj = Projectile(50, 50, 1, 0, mock_level)
    proj.applies_daze_stun = True

    apply_daze_stun_contacts([proj], [snail])

    assert snail.stun_timer == STUN_DURATION_FRAMES, (
        f"Expected stun_timer={STUN_DURATION_FRAMES}, got {snail.stun_timer}"
    )
    assert proj.is_active is False, (
        "Daze-flagged projectile must be consumed on enemy contact"
    )


# --- Test 4: Boss contact does NOT raise (W#6 closure regression) ----------


def test_daze_projectile_boss_contact_does_not_raise(mock_level):
    """Phase 33 D-17 / W#6 closure: a daze-flagged projectile contacting
    the Boss (Mole.update_emerging at boss.py:106-111) must NOT raise.
    Boss has no stun_timer field; the existing boss code reads
    proj.x/y/w/h/is_active only and never touches applies_daze_stun.
    This test is the regression contract that lets us safely DROP
    boss.py from files_modified."""
    from src.entities.projectile import Projectile
    from src.entities.boss import Mole

    # Construct daze-flagged projectile at Mole's spawn position
    proj = Projectile(100, 100, 1, 0, mock_level)
    proj.applies_daze_stun = True

    mole = Mole(100, 100, mock_level)
    mole.state = "EMERGING"
    mole.state_timer = 30  # avoid rock-throw frames (20, 60)

    player_stub = MagicMock()
    player_stub.x = 200
    player_stub.y = 200
    player_stub.w = 8
    player_stub.h = 16

    # Must not raise — even though projectile has applies_daze_stun set,
    # Mole.update_emerging only reads p.x/y/w/h/is_active.
    try:
        mole.update_emerging([proj], player_stub, slime=None)
    except Exception as e:
        pytest.fail(f"Boss contact with daze-flagged projectile raised: {e!r}")

    # Boss should have transitioned to VULNERABLE (existing boss behavior
    # unaffected by the daze flag) — the projectile contact still works.
    assert mole.state == "VULNERABLE", (
        f"Boss must transition to VULNERABLE on projectile hit "
        f"regardless of daze flag; got {mole.state}"
    )
    assert proj.is_active is False, "Boss code consumes projectile via is_active=False"
