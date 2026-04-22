"""Phase 31 ANIM-07 hitbox-independence hard gate.

D-20: unit test driving Player through every clip, asserting (w, h) unchanged.
D-21: player-only scope.
D-22: hard gate -- runs in default pytest invocation, blocks commit on breach.
D-23: coverage = state x vx_sign x vy_sign x facing matrix.

This test encodes the architecture's worst-case failure mode as an
automatic fail-loud trip wire: if any animation state read mutates
`player.w` or `player.h`, gameplay and visuals diverge silently. The
Reanimator-style driver/picker split exists specifically to keep this
from happening; this test enforces the invariant mechanically.
"""
import sys
from unittest.mock import MagicMock

# conftest.py already does sys.modules.setdefault("pyxel", MagicMock()) but
# we re-apply here defensively for any isolated test run.
sys.modules.setdefault("pyxel", MagicMock())

import pytest
from src.entities.player import Player
from src.anim import event_bus
from src.anim.player_anim import (
    STATE_IDLE, STATE_RUNNING, STATE_JUMPING, STATE_FALLING, STATE_DIVING,
    LAND_SQUASH_FRAMES, JUMP_CROUCH_FRAMES,
)


# --- Matrix dimensions (D-23) -----------------------------------------
# 11 states: include every state string the Player.state can take,
# matching the full v1.3 + v2.0 state machine vocabulary.
HITBOX_STATES = (
    STATE_IDLE, STATE_RUNNING, STATE_JUMPING, STATE_FALLING, STATE_DIVING,
    # Defensive: other state strings the Player.state may take in v1.3/v2.0.
    # Even if no rule fires for them today, future rule additions must not
    # cause w/h mutation. The fallback 'idle' rule will pick them up.
    "WALL_SLIDING", "DASHING", "RAMMING", "BOOSTING", "CHARGING_SHOT", "DEAD",
)
VX_SIGNS = (-1, 0, 1)
VY_SIGNS = (-1, 0, 1)
FACINGS = (True, False)

# Ticks per combo must exceed the longest clip.
# drill_spin: 4 frames x 2 ticks = 8. land_squash: 2 frames x (3+1) = 4.
# 60 gives us 7+ full loops of the longest clip.
TICKS_PER_COMBO = 60


def test_hitbox_invariant_across_matrix(mock_level):
    """ANIM-07 D-20/D-23 hard gate: state x vx_sign x vy_sign x facing matrix.

    For each combination, snapshot (w, h) at Player construction, drive
    the anim driver, tick the FSM 60 times, and assert (w, h) is unchanged.
    """
    failures = []
    for state in HITBOX_STATES:
        for vxs in VX_SIGNS:
            for vys in VY_SIGNS:
                for facing in FACINGS:
                    p = Player(0, 0, mock_level)
                    initial_w, initial_h = p.w, p.h
                    p.state = state
                    # Non-zero dx/dy drives the intended vx_sign/vy_sign
                    p.dx = float(vxs) * 2.0
                    p.dy = float(vys) * 2.0
                    p.facing_right = facing
                    p._update_anim_driver()
                    for _ in range(TICKS_PER_COMBO):
                        p._anim.current_frame_u(p._anim_driver)
                    if p.w != initial_w or p.h != initial_h:
                        failures.append(
                            f"state={state!r} vx={vxs} vy={vys} facing={facing}: "
                            f"w {initial_w}->{p.w}, h {initial_h}->{p.h}"
                        )
    assert not failures, (
        "ANIM-07 hitbox-independence invariant breached!\n"
        "The animation layer must NEVER mutate player.w or player.h.\n"
        "Failures:\n  - " + "\n  - ".join(failures)
    )


def test_hitbox_invariant_with_land_event(mock_level):
    """Land event arms land_ticks -> land_squash clip runs. Must not mutate w/h."""
    p = Player(0, 0, mock_level)
    initial_w, initial_h = p.w, p.h
    p.is_grounded = True
    p.state = STATE_IDLE
    p._update_anim_driver()
    event_bus.emit("land")
    # Tick through the full land_squash clip lifetime
    for _ in range(LAND_SQUASH_FRAMES + 5):
        p._update_anim_driver()
        p._anim.current_frame_u(p._anim_driver)
    assert p.w == initial_w, f"land_squash mutated w: {initial_w} -> {p.w}"
    assert p.h == initial_h, f"land_squash mutated h: {initial_h} -> {p.h}"


def test_hitbox_invariant_with_jump_start_event(mock_level):
    """jump_start arms crouch_ticks -> jump_crouch clip runs. Must not mutate w/h."""
    p = Player(0, 0, mock_level)
    initial_w, initial_h = p.w, p.h
    p.state = STATE_JUMPING
    p.is_grounded = False
    p._update_anim_driver()
    event_bus.emit("jump_start")
    for _ in range(JUMP_CROUCH_FRAMES + 5):
        p._update_anim_driver()
        p._anim.current_frame_u(p._anim_driver)
    assert p.w == initial_w, f"jump_crouch mutated w: {initial_w} -> {p.w}"
    assert p.h == initial_h, f"jump_crouch mutated h: {initial_h} -> {p.h}"


def test_hitbox_invariant_with_drill_block_break_pause(mock_level):
    """drill_block_break causes AnimFSM.pause_for -- must not mutate w/h."""
    p = Player(0, 0, mock_level)
    initial_w, initial_h = p.w, p.h
    p.state = STATE_DIVING
    p.is_grounded = False
    p._update_anim_driver()
    # Trigger the animation pause path directly (the subscriber lives in
    # main.py's Game class and isn't trivially testable without a full harness).
    p._anim.pause_for(3)
    for _ in range(10):
        p._anim.current_frame_u(p._anim_driver)
    assert p.w == initial_w, f"pause_for mutated w: {initial_w} -> {p.w}"
    assert p.h == initial_h, f"pause_for mutated h: {initial_h} -> {p.h}"


def test_hitbox_invariant_on_facing_edge_skid(mock_level):
    """Facing flip arms skid_ticks -> turn_skid clip runs. Must not mutate w/h."""
    p = Player(0, 0, mock_level)
    initial_w, initial_h = p.w, p.h
    p.facing_right = True
    p.is_grounded = True
    p.state = STATE_RUNNING
    p.dx = 2.0
    p._update_anim_driver()
    # Flip facing to trigger edge
    p.facing_right = False
    p.dx = -2.0
    p._update_anim_driver()
    for _ in range(10):
        p._update_anim_driver()
        p._anim.current_frame_u(p._anim_driver)
    assert p.w == initial_w, f"turn_skid mutated w: {initial_w} -> {p.w}"
    assert p.h == initial_h, f"turn_skid mutated h: {initial_h} -> {p.h}"
