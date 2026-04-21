"""Phase 26 ANIM-01/02 animation module unit tests. Plan 01 -- AnimClip,
AnimPlayer, and event_bus primitives. Plan 02 -- Player-instance wiring."""

import sys
from unittest.mock import MagicMock

# Pyxel mock must be installed before any src.entities imports (matches
# test_physics.py pattern).
mock_pyxel = MagicMock()
sys.modules["pyxel"] = mock_pyxel

import pytest
from src.anim.anim_clip import AnimClip
from src.anim.anim_player import AnimPlayer


# ---------------------------------------------------------------------------
# AnimClip tests
# ---------------------------------------------------------------------------

def test_clip_constructs_with_defaults():
    clip = AnimClip(frames=[0, 16], durations=[10, 10])
    assert clip.loop is True
    assert clip.events == {}


def test_clip_length_mismatch():
    with pytest.raises(ValueError):
        AnimClip(frames=[0, 16], durations=[10])


# ---------------------------------------------------------------------------
# AnimPlayer tests
# ---------------------------------------------------------------------------

def test_player_tick_advances_frame():
    clip = AnimClip(frames=[0, 16], durations=[2, 2])
    player = AnimPlayer(clip)
    # tick-then-read: first tick moves counter to 1, still on frame 0
    results = []
    for _ in range(4):
        player.tick()
        results.append(player.current_u())
    assert results == [0, 0, 16, 16]


def test_player_loops_by_default():
    clip = AnimClip(frames=[0, 16], durations=[2, 2])
    player = AnimPlayer(clip)
    for _ in range(4):
        player.tick()
    # tick 5 wraps back to frame 0
    player.tick()
    assert player.current_u() == 0


def test_clip_change_resets_counter():
    clip = AnimClip(frames=[0, 16], durations=[2, 2])
    player = AnimPlayer(clip)
    player.tick()
    player.tick()  # now on frame index 1
    player.set_clip(clip)  # D-07 reset
    assert player.current_u() == 0  # frames[0]
    # One tick should NOT advance past frame 0 (counter restarted)
    player.tick()
    assert player.current_u() == 0


def test_non_looping_clip_holds():
    clip = AnimClip(frames=[0, 16], durations=[2, 2], loop=False)
    player = AnimPlayer(clip)
    for _ in range(10):
        player.tick()
    assert player.current_u() == 16  # held on last frame


# ---------------------------------------------------------------------------
# AnimFSM tests
# ---------------------------------------------------------------------------

from src.anim.state_machine import AnimFSM
from src.anim.player_anim import (
    PlayerAnimDriver, build_player_fsm,
    IDLE_U, RUN_FRAME_A_U, RUN_FRAME_B_U, JUMP_U,
    RUN_TOGGLE_DURATION_TICKS,
)


def test_fsm_raises_on_missing_clip():
    with pytest.raises(ValueError, match="nope"):
        AnimFSM(rules=[(lambda d: True, "nope")], clips={})


def test_fsm_walks_rules_first_match_wins():
    clip_a = AnimClip(frames=[100], durations=[1])
    clip_b = AnimClip(frames=[200], durations=[1])
    clip_c = AnimClip(frames=[300], durations=[1])
    fsm = AnimFSM(
        rules=[
            (lambda d: True, "a"),
            (lambda d: True, "b"),
            (lambda d: True, "c"),
        ],
        clips={"a": clip_a, "b": clip_b, "c": clip_c},
    )
    assert fsm.current_frame_u(None) == 100  # first rule wins


def test_fsm_resets_counter_on_clip_change():
    clip_a = AnimClip(frames=[10, 20], durations=[2, 2])
    clip_b = AnimClip(frames=[30, 40], durations=[2, 2])
    driver = PlayerAnimDriver(state="RUNNING")
    fsm = AnimFSM(
        rules=[
            (lambda d: d.state == "RUNNING", "a"),
            (lambda d: True, "b"),
        ],
        clips={"a": clip_a, "b": clip_b},
    )
    # Drive a few ticks in state A
    fsm.current_frame_u(driver)
    fsm.current_frame_u(driver)
    # Switch to state B -- should reset to first frame of clip_b
    driver.state = "IDLE"
    result = fsm.current_frame_u(driver)
    assert result == 30  # first frame of clip_b (fresh start)


def test_driver_single_instance():
    d = PlayerAnimDriver()
    assert hasattr(d, "__slots__")
    d.state = "RUNNING"  # mutation works
    with pytest.raises(AttributeError):
        d.nonexistent = 1  # type: ignore[attr-defined]


def test_build_player_fsm_returns_animfsm():
    assert isinstance(build_player_fsm(), AnimFSM)


# ---------------------------------------------------------------------------
# v1.3 parity tests
# ---------------------------------------------------------------------------

def test_running_parity():
    fsm = build_player_fsm()
    driver = PlayerAnimDriver(state="RUNNING")
    # 48 ticks = 8 half-cycles at 6 ticks each
    outputs = [fsm.current_frame_u(driver) for _ in range(48)]
    cycle = [RUN_FRAME_A_U] * RUN_TOGGLE_DURATION_TICKS + [RUN_FRAME_B_U] * RUN_TOGGLE_DURATION_TICKS
    expected = cycle * (48 // (RUN_TOGGLE_DURATION_TICKS * 2))
    assert outputs == expected


def test_jumping_parity():
    fsm = build_player_fsm()
    driver = PlayerAnimDriver(state="JUMPING")
    outputs = [fsm.current_frame_u(driver) for _ in range(48)]
    assert all(u == JUMP_U for u in outputs)


def test_falling_parity():
    fsm = build_player_fsm()
    driver = PlayerAnimDriver(state="FALLING")
    outputs = [fsm.current_frame_u(driver) for _ in range(48)]
    assert all(u == JUMP_U for u in outputs)


def test_idle_parity():
    fsm = build_player_fsm()
    driver = PlayerAnimDriver(state="IDLE")
    outputs = [fsm.current_frame_u(driver) for _ in range(48)]
    assert all(u == IDLE_U for u in outputs)


def test_fallback_states_parity():
    """D-06 fallback: unrecognized states render as IDLE."""
    fallback_states = (
        "WALL_SLIDING", "DIVING", "RAMMING",
        "DASHING", "BOOSTING", "CHARGING_SHOT",
    )
    for state_name in fallback_states:
        fsm = build_player_fsm()  # fresh FSM per state
        driver = PlayerAnimDriver(state=state_name)
        outputs = [fsm.current_frame_u(driver) for _ in range(24)]
        assert all(u == IDLE_U for u in outputs), (
            f"State {state_name} should fall back to IDLE_U={IDLE_U}"
        )


# ---------------------------------------------------------------------------
# Plan 26-02: Player-instance-level parity tests
# ---------------------------------------------------------------------------

from src.entities.player import Player
from src.core.constants import *


@pytest.fixture
def mock_level():
    level = MagicMock()
    level.check_collision.return_value = False
    level.check_hazard.return_value = False
    level.is_switch.return_value = False
    return level


@pytest.fixture
def mock_slime():
    slime = MagicMock()
    slime.x = 100
    slime.y = 100
    slime.w = 8
    slime.h = 8
    slime.juice = 100
    return slime


def test_player_init_constructs_driver_and_fsm(mock_level):
    """Player.__init__ must create _anim_driver and _anim."""
    p = Player(0, 0, mock_level)
    assert hasattr(p, "_anim_driver"), "Player missing _anim_driver"
    assert hasattr(p, "_anim"), "Player missing _anim"
    assert isinstance(p._anim_driver, PlayerAnimDriver)


def test_player_driver_is_single_instance(mock_level):
    """D-16: driver is mutated in place, never reassigned."""
    p = Player(0, 0, mock_level)
    id_before = id(p._anim_driver)
    p._update_anim_driver()
    assert id(p._anim_driver) == id_before


def test_player_update_anim_driver_reflects_state(mock_level):
    """_update_anim_driver() must copy player fields into driver."""
    p = Player(0, 0, mock_level)
    p.state = "RUNNING"
    p.facing_right = False
    p.dy = -2.5
    p.is_grounded = False
    p._update_anim_driver()
    assert p._anim_driver.state == "RUNNING"
    assert p._anim_driver.facing == -1
    assert p._anim_driver.vy_sign == -1
    assert p._anim_driver.is_grounded is False


def test_player_draw_u_running_parity(mock_level):
    """RUNNING over 12 ticks must match v1.3: 6x RUN_FRAME_A then 6x RUN_FRAME_B."""
    p = Player(0, 0, mock_level)
    p.state = "RUNNING"
    p._update_anim_driver()
    outputs = []
    for _ in range(12):
        outputs.append(p._anim.current_frame_u(p._anim_driver))
    expected = [RUN_FRAME_A_U] * 6 + [RUN_FRAME_B_U] * 6
    assert outputs == expected


def test_player_draw_u_jumping_parity(mock_level):
    """JUMPING must always produce JUMP_U."""
    p = Player(0, 0, mock_level)
    p.state = "JUMPING"
    p._update_anim_driver()
    outputs = [p._anim.current_frame_u(p._anim_driver) for _ in range(12)]
    assert all(u == JUMP_U for u in outputs)


def test_player_draw_u_falling_parity(mock_level):
    """FALLING must always produce JUMP_U."""
    p = Player(0, 0, mock_level)
    p.state = "FALLING"
    p._update_anim_driver()
    outputs = [p._anim.current_frame_u(p._anim_driver) for _ in range(12)]
    assert all(u == JUMP_U for u in outputs)


def test_player_draw_u_idle_parity(mock_level):
    """IDLE must always produce IDLE_U."""
    p = Player(0, 0, mock_level)
    p.state = "IDLE"
    p._update_anim_driver()
    outputs = [p._anim.current_frame_u(p._anim_driver) for _ in range(12)]
    assert all(u == IDLE_U for u in outputs)


def test_player_draw_u_fallback_parity(mock_level):
    """D-06 fallback: all non-animated states produce IDLE_U."""
    fallback_states = (
        "WALL_SLIDING", "DIVING", "RAMMING",
        "DASHING", "BOOSTING", "CHARGING_SHOT",
    )
    for state_name in fallback_states:
        p = Player(0, 0, mock_level)
        p.state = state_name
        p._update_anim_driver()
        outputs = [p._anim.current_frame_u(p._anim_driver) for _ in range(12)]
        assert all(u == IDLE_U for u in outputs), (
            f"State {state_name} should fall back to IDLE_U={IDLE_U}"
        )


# ---------------------------------------------------------------------------
# Phase 31 Plan 01 Task 1: AnimPlayer.pause_for + AnimFSM.pause_for
# ---------------------------------------------------------------------------

def test_pause_for_freezes_ticks():
    from src.anim.anim_player import AnimPlayer
    from src.anim.anim_clip import AnimClip
    clip = AnimClip(frames=[0, 16], durations=[2, 2])
    player = AnimPlayer(clip)
    player.pause_for(3)
    frames_during_pause = []
    for _ in range(3):
        player.tick()
        frames_during_pause.append(player.current_u())
    assert frames_during_pause == [0, 0, 0]
    # Resume: pause is a pure freeze. Clip ticks stay at 0, so frame 0 shows
    # for its full 2-tick duration (resume ticks 1-2), advancing on resume tick 3.
    player.tick()
    assert player.current_u() == 0
    player.tick()
    assert player.current_u() == 0
    player.tick()
    assert player.current_u() == 16


def test_pause_for_additive():
    from src.anim.anim_player import AnimPlayer
    from src.anim.anim_clip import AnimClip
    clip = AnimClip(frames=[0, 16], durations=[1, 1])
    player = AnimPlayer(clip)
    player.pause_for(2)
    player.pause_for(2)  # additive, not overwrite (RESEARCH A2)
    for _ in range(4):
        player.tick()
        assert player.current_u() == 0
    # Resume: durations=[1,1]. Resume tick 1 shows frame 0 (clip_ticks 0->1),
    # resume tick 2 advances to frame 16.
    player.tick()
    assert player.current_u() == 0
    player.tick()
    assert player.current_u() == 16


def test_pause_for_cleared_on_set_clip():
    from src.anim.anim_player import AnimPlayer
    from src.anim.anim_clip import AnimClip
    clip_a = AnimClip(frames=[0], durations=[1])
    clip_b = AnimClip(frames=[16, 32], durations=[1, 1])
    player = AnimPlayer(clip_a)
    player.pause_for(10)
    player.set_clip(clip_b)
    player.tick()
    assert player.current_u() == 16
    player.tick()
    assert player.current_u() == 32


def test_anim_fsm_pause_for_forwards():
    from src.anim.state_machine import AnimFSM
    from src.anim.anim_clip import AnimClip
    clip = AnimClip(frames=[0, 16], durations=[2, 2])
    fsm = AnimFSM(rules=[(lambda d: True, "c")], clips={"c": clip})
    dr = MagicMock()
    # Prime the FSM so set_clip runs once
    fsm.current_frame_u(dr)
    fsm.pause_for(3)
    outputs = [fsm.current_frame_u(dr) for _ in range(3)]
    assert outputs == [0, 0, 0]
