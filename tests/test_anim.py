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


def test_jumping_stationary_parity():
    """Phase 31 D-01 Metroid split: JUMPING with vx_sign=0 picks jump_stationary
    (U=96) instead of the v1.3 JUMP_U=32. Single-frame static clip, so 48 ticks
    of output are all JUMP_STATIONARY_U."""
    from src.anim.player_anim import JUMP_STATIONARY_U
    fsm = build_player_fsm()
    driver = PlayerAnimDriver(state="JUMPING", is_grounded=False, vx_sign=0)
    outputs = [fsm.current_frame_u(driver) for _ in range(48)]
    assert all(u == JUMP_STATIONARY_U for u in outputs)


def test_falling_parity():
    """FALLING with vx_sign=0 (no horizontal motion) holds the stationary jump
    pose so the airborne arc reads as a single jump from launch to landing.
    Phase 32.1: the prior contract ("FALLING always shows JUMP_U") was replaced
    when the walking-jump spin was extended to play through the entire
    airborne arc — see test_jumping_running_spans_airborne_arc."""
    from src.anim.player_anim import JUMP_STATIONARY_U
    fsm = build_player_fsm()
    driver = PlayerAnimDriver(state="FALLING", is_grounded=False, vx_sign=0)
    outputs = [fsm.current_frame_u(driver) for _ in range(48)]
    assert all(u == JUMP_STATIONARY_U for u in outputs)


def test_jumping_running_spans_airborne_arc():
    """Walking-jump spin plays through both JUMPING (ascent) and FALLING
    (descent) — until the player lands. Phase 32.1 user-reported regression:
    spin disengaged mid-flight when state flipped to FALLING."""
    from src.anim.player_anim import JUMP_SPIN_FRAMES_U
    fsm = build_player_fsm()
    seen = set()
    for state in ("JUMPING", "FALLING"):
        d = PlayerAnimDriver(state=state, is_grounded=False, vx_sign=1)
        for _ in range(40):
            seen.add(fsm.current_frame_u(d))
    assert seen == set(JUMP_SPIN_FRAMES_U), (
        f"walking-jump spin must play across JUMPING+FALLING; saw {seen}"
    )


def test_idle_parity():
    fsm = build_player_fsm()
    driver = PlayerAnimDriver(state="IDLE")
    outputs = [fsm.current_frame_u(driver) for _ in range(48)]
    assert all(u == IDLE_U for u in outputs)


def test_fallback_states_parity():
    """D-06 fallback: unrecognized states render as IDLE.

    Phase 31: DIVING is no longer a fallback (it picks drill_spin per D-05).
    Other non-animated states still fall through to idle.
    """
    fallback_states = (
        "WALL_SLIDING", "RAMMING",
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
    """Phase 31 D-01 Metroid split: JUMPING with default dx=0 (vx_sign=0)
    picks jump_stationary. JUMP_STATIONARY_U replaces the v1.3 JUMP_U."""
    from src.anim.player_anim import JUMP_STATIONARY_U
    p = Player(0, 0, mock_level)
    p.state = "JUMPING"
    p._update_anim_driver()
    outputs = [p._anim.current_frame_u(p._anim_driver) for _ in range(12)]
    assert all(u == JUMP_STATIONARY_U for u in outputs)


def test_player_draw_u_falling_parity(mock_level):
    """FALLING with no horizontal motion (default dx=0 → vx_sign=0) holds the
    stationary jump pose. Phase 32.1: airborne contract no longer maps FALLING
    to a single static JUMP_U — it spans the airborne arc per vx_sign."""
    from src.anim.player_anim import JUMP_STATIONARY_U
    p = Player(0, 0, mock_level)
    p.state = "FALLING"
    p._update_anim_driver()
    outputs = [p._anim.current_frame_u(p._anim_driver) for _ in range(12)]
    assert all(u == JUMP_STATIONARY_U for u in outputs)


def test_player_draw_u_idle_parity(mock_level):
    """IDLE must always produce IDLE_U."""
    p = Player(0, 0, mock_level)
    p.state = "IDLE"
    p._update_anim_driver()
    outputs = [p._anim.current_frame_u(p._anim_driver) for _ in range(12)]
    assert all(u == IDLE_U for u in outputs)


def test_player_draw_u_fallback_parity(mock_level):
    """D-06 fallback: non-animated states produce IDLE_U.

    Phase 31 removes DIVING from the fallback set (it now picks drill_spin).
    """
    fallback_states = (
        "WALL_SLIDING", "RAMMING",
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


# ---------------------------------------------------------------------------
# Phase 31 Plan 01 Task 2: extended PlayerAnimDriver + named constants
# ---------------------------------------------------------------------------

def test_driver_defaults_phase31_fields():
    from src.anim.player_anim import PlayerAnimDriver
    d = PlayerAnimDriver()
    assert d.vx_sign == 0
    assert d.prev_facing == 1
    assert d.skid_ticks == 0
    assert d.land_ticks == 0
    assert d.crouch_ticks == 0


def test_driver_accepts_all_fields_kwarg():
    from src.anim.player_anim import PlayerAnimDriver
    d = PlayerAnimDriver(
        state="JUMPING", is_grounded=False, facing=-1, vy_sign=-1,
        vx_sign=1, prev_facing=-1, skid_ticks=3, land_ticks=4, crouch_ticks=2,
    )
    assert d.vx_sign == 1
    assert d.prev_facing == -1
    assert d.skid_ticks == 3
    assert d.land_ticks == 4
    assert d.crouch_ticks == 2


def test_phase31_named_constants_exist():
    import src.anim.player_anim as pa
    for name in [
        "LAND_SQUASH_FRAMES", "TURN_SKID_FRAMES", "JUMP_CROUCH_FRAMES",
        "DRILL_RECOIL_PAUSE_FRAMES",
        "LAND_SQUASH_U", "TURN_SKID_U", "JUMP_CROUCH_U",
        "JUMP_STATIONARY_U", "JUMP_RUNNING_U",
        "DRILL_SPIN_FRAME_0_U", "DRILL_SPIN_FRAME_1_U",
        "DRILL_SPIN_FRAME_2_U", "DRILL_SPIN_FRAME_3_U",
    ]:
        assert hasattr(pa, name), f"missing constant {name}"
        assert isinstance(getattr(pa, name), int), f"{name} must be int"


def test_phase31_u_offsets_stride_16():
    import src.anim.player_anim as pa
    for name in [
        "LAND_SQUASH_U", "TURN_SKID_U", "JUMP_CROUCH_U",
        "JUMP_STATIONARY_U", "JUMP_RUNNING_U",
        "DRILL_SPIN_FRAME_0_U", "DRILL_SPIN_FRAME_1_U",
        "DRILL_SPIN_FRAME_2_U", "DRILL_SPIN_FRAME_3_U",
    ]:
        u = getattr(pa, name)
        assert u % 16 == 0, f"{name}={u} not aligned to 16 px stride"


# ---------------------------------------------------------------------------
# Phase 31 Plan 05 Task 2: build_player_fsm reads from tuning.anim
# ---------------------------------------------------------------------------

def test_build_player_fsm_reads_from_tuning_anim():
    from src.core import tuning
    from src.anim.player_anim import build_player_fsm
    tuning.load_anim()
    build_player_fsm()  # constructed; AnimFSM ctor would raise if a rule clip_id were missing
    assert tuning.anim.player.clips["run"].frames == [16, 32]
    assert tuning.anim.player.clips["run"].durations == [6, 6]


def test_build_player_fsm_picks_up_new_durations_on_rebuild():
    from src.core import tuning
    from src.anim.player_anim import build_player_fsm, PlayerAnimDriver, STATE_RUNNING
    tuning.load_anim()
    original = tuning.anim.player.clips["run"].durations[0]
    tuning.set_anim_value("ANIM_PLAYER_RUN_DURATION_0", 1)
    fsm = build_player_fsm()
    d = PlayerAnimDriver(state=STATE_RUNNING)
    us = set()
    for _ in range(4):
        us.add(fsm.current_frame_u(d))
    assert len(us) == 2  # both 16 and 32 appear within 4 ticks
    tuning.set_anim_value("ANIM_PLAYER_RUN_DURATION_0", original)


# ---------------------------------------------------------------------------
# Phase 31 Plan 05 Task 3: ANIM panel tab + reload_anim_schema
# ---------------------------------------------------------------------------

def test_panel_anim_tab_exists():
    from src.ui import panel
    tab_names = [td[0] for td in panel.TAB_DEFS]
    assert "Anim" in tab_names, f"Expected 'Anim' tab in {tab_names}"


def test_panel_reload_anim_schema_rebinds_fsm(mock_level):
    from src.core import tuning
    from src.anim.player_anim import build_player_fsm
    from src.ui import panel
    tuning.load_anim()
    fsm_before = build_player_fsm()
    reload_fn = getattr(panel, "reload_anim_schema", None)
    assert reload_fn is not None, "panel.reload_anim_schema(player) must exist"
    class FakePlayer:
        def __init__(self):
            self._anim = fsm_before
    p = FakePlayer()
    reload_fn(p)
    assert p._anim is not fsm_before


# ---------------------------------------------------------------------------
# Phase 31 Plan 02 Task 1: 6 new PLAYER_CLIPS + reordered PLAYER_RULES
# ---------------------------------------------------------------------------

def test_metroid_jump_split():
    """Walking jump now uses the 8-frame spin starting at JUMP_SPIN_FRAMES_U[0];
    the running-jump variants land on the spin's first frame on the initial tick."""
    from src.anim.player_anim import (
        build_player_fsm, PlayerAnimDriver,
        STATE_JUMPING, JUMP_STATIONARY_U, JUMP_SPIN_FRAMES_U,
    )
    fsm = build_player_fsm()
    d_stationary = PlayerAnimDriver(state=STATE_JUMPING, is_grounded=False, vx_sign=0)
    assert fsm.current_frame_u(d_stationary) == JUMP_STATIONARY_U
    fsm2 = build_player_fsm()
    d_running_right = PlayerAnimDriver(state=STATE_JUMPING, is_grounded=False, vx_sign=1)
    assert fsm2.current_frame_u(d_running_right) == JUMP_SPIN_FRAMES_U[0]
    fsm3 = build_player_fsm()
    d_running_left = PlayerAnimDriver(state=STATE_JUMPING, is_grounded=False, vx_sign=-1)
    assert fsm3.current_frame_u(d_running_left) == JUMP_SPIN_FRAMES_U[0]


def test_land_squash_rule_fires():
    from src.anim.player_anim import (
        build_player_fsm, PlayerAnimDriver,
        STATE_IDLE, LAND_SQUASH_U, IDLE_U,
    )
    fsm = build_player_fsm()
    d = PlayerAnimDriver(state=STATE_IDLE, is_grounded=True, land_ticks=3)
    assert fsm.current_frame_u(d) == LAND_SQUASH_U
    fsm2 = build_player_fsm()
    d2 = PlayerAnimDriver(state=STATE_IDLE, is_grounded=True, land_ticks=0)
    assert fsm2.current_frame_u(d2) == IDLE_U


def test_turn_skid_rule_fires():
    from src.anim.player_anim import (
        build_player_fsm, PlayerAnimDriver,
        STATE_RUNNING, TURN_SKID_U,
    )
    fsm = build_player_fsm()
    d = PlayerAnimDriver(state=STATE_RUNNING, is_grounded=True, skid_ticks=2, vx_sign=1)
    assert fsm.current_frame_u(d) == TURN_SKID_U


def test_jump_crouch_rule_takes_priority():
    from src.anim.player_anim import (
        build_player_fsm, PlayerAnimDriver,
        STATE_JUMPING, JUMP_CROUCH_U,
    )
    fsm = build_player_fsm()
    d = PlayerAnimDriver(state=STATE_JUMPING, is_grounded=False, crouch_ticks=1, vx_sign=0)
    assert fsm.current_frame_u(d) == JUMP_CROUCH_U


def test_drill_spin_cycles_eight_frames():
    """Phase 32.1: drill_spin reuses the 8-frame jump-spin sprite range as a
    placeholder (sprite indices 4..11; U=64..176)."""
    from src.anim.player_anim import (
        build_player_fsm, PlayerAnimDriver,
        STATE_DIVING, JUMP_SPIN_FRAMES_U,
    )
    fsm = build_player_fsm()
    d = PlayerAnimDriver(state=STATE_DIVING, is_grounded=False)
    seen = set()
    for _ in range(80):
        seen.add(fsm.current_frame_u(d))
    assert seen == set(JUMP_SPIN_FRAMES_U), (
        f"drill_spin did not cycle all 8 frames; saw {seen}"
    )


def test_land_squash_clip_non_looping_holds_idle():
    from src.anim.player_anim import PLAYER_CLIPS, LAND_SQUASH_U, IDLE_U, LAND_SQUASH_FRAMES
    clip = PLAYER_CLIPS["land_squash"]
    assert clip.frames == [LAND_SQUASH_U, IDLE_U]
    assert clip.loop is False
    assert clip.durations[0] == LAND_SQUASH_FRAMES - 1
    assert clip.durations[1] == 1


def test_jump_crouch_clip_non_looping():
    from src.anim.player_anim import PLAYER_CLIPS
    clip = PLAYER_CLIPS["jump_crouch"]
    assert clip.loop is False


# ---------------------------------------------------------------------------
# Phase 31 Plan 02 Task 2: extended _update_anim_driver + subscribers + bridge
# ---------------------------------------------------------------------------

def test_update_anim_driver_computes_vx_sign(mock_level):
    from src.entities.player import Player
    p = Player(0, 0, mock_level)
    p.dx = -2.0
    p._update_anim_driver()
    assert p._anim_driver.vx_sign == -1
    p.dx = 0.0
    p._update_anim_driver()
    assert p._anim_driver.vx_sign == 0
    p.dx = 3.0
    p._update_anim_driver()
    assert p._anim_driver.vx_sign == 1


def test_update_anim_driver_snapshots_prev_facing(mock_level):
    from src.entities.player import Player
    from src.anim.player_anim import TURN_SKID_FRAMES
    p = Player(0, 0, mock_level)
    p.facing_right = True
    p.is_grounded = True
    p._update_anim_driver()
    assert p._anim_driver.facing == 1
    # Flip facing; prev_facing MUST show OLD value (+1), not new (-1)
    p.facing_right = False
    p._update_anim_driver()
    assert p._anim_driver.prev_facing == 1, (
        "prev_facing must snapshot BEFORE facing overwrite (Pitfall 1)"
    )
    assert p._anim_driver.facing == -1
    # Edge detected while grounded -> skid_ticks armed (minus 1 for same-frame decrement)
    assert p._anim_driver.skid_ticks == TURN_SKID_FRAMES - 1


def test_update_anim_driver_decrements_counters(mock_level):
    from src.entities.player import Player
    p = Player(0, 0, mock_level)
    p._anim_driver.skid_ticks = 3
    p._anim_driver.land_ticks = 2
    p._anim_driver.crouch_ticks = 1
    p.facing_right = True  # no edge flip
    p._update_anim_driver()
    assert p._anim_driver.skid_ticks == 2
    assert p._anim_driver.land_ticks == 1
    assert p._anim_driver.crouch_ticks == 0
    # At 0, no underflow
    p._update_anim_driver()
    assert p._anim_driver.skid_ticks == 1
    assert p._anim_driver.land_ticks == 0
    assert p._anim_driver.crouch_ticks == 0


def test_land_event_arms_land_ticks(mock_level):
    """Game-level subscriber sets driver.land_ticks on 'land' emit.

    The subscribe call lives in Game.__init__ (main.py) post-WR-01 fix
    -- this test mimics that wiring with a fake game-ref to keep the
    contract under test without booting the full Game.
    """
    from src.entities.player import Player
    from src.anim import event_bus
    from src.anim.player_anim import LAND_SQUASH_FRAMES
    p = Player(0, 0, mock_level)
    p._anim_driver.land_ticks = 0

    class FakeGame:
        player = p
    fake = FakeGame()

    def _on_land(**kw):
        fake.player._anim_driver.land_ticks = LAND_SQUASH_FRAMES
    event_bus.subscribe("land", _on_land)
    event_bus.emit("land")
    assert p._anim_driver.land_ticks == LAND_SQUASH_FRAMES


def test_jump_start_event_arms_crouch_ticks(mock_level):
    """Game-level subscriber sets driver.crouch_ticks on 'jump_start' emit.

    The subscribe call lives in Game.__init__ (main.py) post-WR-01 fix.
    """
    from src.entities.player import Player
    from src.anim import event_bus
    from src.anim.player_anim import JUMP_CROUCH_FRAMES
    p = Player(0, 0, mock_level)
    p._anim_driver.crouch_ticks = 0

    class FakeGame:
        player = p
    fake = FakeGame()

    def _on_jump_start(**kw):
        fake.player._anim_driver.crouch_ticks = JUMP_CROUCH_FRAMES
    event_bus.subscribe("jump_start", _on_jump_start)
    event_bus.emit("jump_start")
    assert p._anim_driver.crouch_ticks == JUMP_CROUCH_FRAMES


def test_drill_block_break_bridge_emits(mock_level):
    """Phase 31 provisional bridge: drill DIVING block-break emits
    drill_block_break. Phase 32 will relocate this; the bridge is
    intentionally removable."""
    from src.anim import event_bus
    captured = []
    def _sub(**kw):
        captured.append(kw)
    event_bus.subscribe("drill_block_break", _sub)
    event_bus.emit("drill_block_break", tx=5, ty=7)
    assert captured == [{"tx": 5, "ty": 7}]
