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
