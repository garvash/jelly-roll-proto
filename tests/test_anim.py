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
