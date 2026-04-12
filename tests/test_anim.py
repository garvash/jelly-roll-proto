"""Phase 26 ANIM-01 animation module unit tests. Plan 01 -- AnimClip,
AnimPlayer, and event_bus primitives. Task 2 extends with AnimFSM + parity."""

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
    outputs = [fsm.current_frame_u(driver) for _ in range(48)]
    expected = (
        [RUN_FRAME_A_U] * RUN_TOGGLE_DURATION_TICKS
        + [RUN_FRAME_B_U] * RUN_TOGGLE_DURATION_TICKS
        + [RUN_FRAME_A_U] * RUN_TOGGLE_DURATION_TICKS
        + [RUN_FRAME_B_U] * RUN_TOGGLE_DURATION_TICKS
    )
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
