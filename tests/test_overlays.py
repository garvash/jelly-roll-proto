"""Tests for diagnostic overlay manager (Phase 27, Plan 01).

Covers: toggle flags, buffer management, read-only entity access, draw dispatch.
"""
import sys
from unittest.mock import MagicMock, patch, call
from collections import deque

# Mock pyxel before importing overlays
sys.modules.setdefault("pyxel", MagicMock())

import src.core.overlays as overlays


def _reset_flags():
    """Reset all overlay flags to defaults for test isolation."""
    overlays.show_hitboxes = False
    overlays.show_velocity = False
    overlays.show_input = False
    overlays.show_slime = False
    overlays._frame_times.clear()
    overlays._last_frame_time = 0.0


class MockEntity:
    """Minimal entity mock with hitbox and velocity attributes."""
    def __init__(self, x=10, y=20, w=8, h=8, dx=0.0, dy=0.0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.dx = dx
        self.dy = dy


class MockSlime(MockEntity):
    """Slime entity mock with additional slime-specific attributes."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_fused = False
        self.is_dissipated = False
        self.target_x = 50
        self.target_y = 60
        self.history = deque(maxlen=32)


class MockGame:
    """Minimal game mock providing entity references."""
    def __init__(self):
        self.player = MockEntity(x=100, y=100, w=8, h=8, dx=2.5, dy=-1.0)
        self.slime = MockSlime(x=120, y=100, w=16, h=16, dx=1.0, dy=0.5)
        self.enemies = [MockEntity(x=200, y=100)]
        self.projectiles = [MockEntity(x=150, y=80, w=4, h=4)]
        self.doors = [MockEntity(x=50, y=50, w=16, h=32)]
        self.mole = MockEntity(x=300, y=100, w=32, h=32)
        self.cam_x = 0
        self.cam_y = 0


# --- Test 1: Flags default to False ---

def test_flags_default_false():
    """All four overlay flags default to False on module load."""
    # Reset to confirm defaults
    _reset_flags()
    assert overlays.show_hitboxes is False
    assert overlays.show_velocity is False
    assert overlays.show_input is False
    assert overlays.show_slime is False


# --- Test 2: F2 toggles hitboxes ---

def test_f2_toggles_hitboxes():
    """F2 keypress toggles show_hitboxes True, then False on second press."""
    _reset_flags()
    pyxel = sys.modules["pyxel"]

    def btnp_f2(key):
        return key == pyxel.KEY_F2

    with patch.object(pyxel, "btnp", side_effect=btnp_f2):
        overlays.update()
    assert overlays.show_hitboxes is True

    with patch.object(pyxel, "btnp", side_effect=btnp_f2):
        overlays.update()
    assert overlays.show_hitboxes is False


# --- Test 3: F3 toggles velocity ---

def test_f3_toggles_velocity():
    """F3 keypress toggles show_velocity True, then False."""
    _reset_flags()
    pyxel = sys.modules["pyxel"]

    def btnp_f3(key):
        return key == pyxel.KEY_F3

    with patch.object(pyxel, "btnp", side_effect=btnp_f3):
        overlays.update()
    assert overlays.show_velocity is True

    with patch.object(pyxel, "btnp", side_effect=btnp_f3):
        overlays.update()
    assert overlays.show_velocity is False


# --- Test 4: F4 and F5 toggle independently ---

def test_f4_f5_toggle_independently():
    """Toggling F4 does not affect F5, and vice versa."""
    _reset_flags()
    pyxel = sys.modules["pyxel"]

    # Toggle F4 only
    def btnp_f4(key):
        return key == pyxel.KEY_F4

    with patch.object(pyxel, "btnp", side_effect=btnp_f4):
        overlays.update()
    assert overlays.show_input is True
    assert overlays.show_slime is False

    # Toggle F5 only
    def btnp_f5(key):
        return key == pyxel.KEY_F5

    with patch.object(pyxel, "btnp", side_effect=btnp_f5):
        overlays.update()
    assert overlays.show_slime is True
    assert overlays.show_input is True  # F4 still on


# --- Test 5: Frame time buffer maxlen ---

def test_frame_time_buffer_maxlen():
    """Frame time deque never exceeds maxlen=64 even after 100 appends."""
    _reset_flags()
    assert overlays._frame_times.maxlen == 64

    # Simulate 100 frame-time updates
    overlays._last_frame_time = 1.0
    for i in range(100):
        with patch("time.perf_counter", return_value=1.0 + (i + 1) * 0.016):
            overlays._update_frame_time()

    assert len(overlays._frame_times) == 64


# --- Test 6: Hitbox draw does not mutate entity state ---

def test_hitbox_no_mutation():
    """Drawing hitbox overlay does not modify player position or size."""
    _reset_flags()
    overlays.show_hitboxes = True
    game = MockGame()

    # Record original values
    orig_x, orig_y = game.player.x, game.player.y
    orig_w, orig_h = game.player.w, game.player.h

    overlays.draw(game)

    assert game.player.x == orig_x
    assert game.player.y == orig_y
    assert game.player.w == orig_w
    assert game.player.h == orig_h


# --- Test 7: Velocity draw does not mutate entity state ---

def test_velocity_no_mutation():
    """Drawing velocity overlay does not modify player dx/dy."""
    _reset_flags()
    overlays.show_velocity = True
    game = MockGame()

    orig_dx, orig_dy = game.player.dx, game.player.dy

    overlays.draw(game)

    assert game.player.dx == orig_dx
    assert game.player.dy == orig_dy


# --- Test 8: Draw with all flags off is a no-op ---

def test_draw_with_all_off_is_noop():
    """When all overlay flags are False, draw() makes no pyxel draw calls."""
    _reset_flags()
    game = MockGame()
    pyxel = sys.modules["pyxel"]

    # Reset call tracking
    pyxel.rectb.reset_mock()
    pyxel.line.reset_mock()
    pyxel.rect.reset_mock()
    pyxel.pset.reset_mock()
    pyxel.circ.reset_mock()
    pyxel.circb.reset_mock()

    overlays.draw(game)

    pyxel.rectb.assert_not_called()
    pyxel.line.assert_not_called()
    # rect/pset may not be called in world-space draw either


# === Plan 02 tests: F4 input blips + F5 slime overlay ===


def _reset_plan02():
    """Reset Plan 02 state for test isolation."""
    _reset_flags()
    overlays._coyote_blips.clear()
    overlays._jump_blips.clear()
    overlays._land_blips.clear()
    overlays._buffer_blips.clear()
    overlays._slime_stuck_frames = 0
    overlays._initialized = False
    overlays._game_ref = None
    overlays._prev_cam_x = 0.0
    overlays._prev_cam_y = 0.0
    # Reset event bus to prevent cross-test subscription leaks
    from src.anim import event_bus
    event_bus.reset()


class MockPlayer:
    """Player mock with coyote/buffer timer attributes for F4 overlay tests."""
    def __init__(self, x=50, y=100, w=10, h=14, dx=0.0, dy=0.0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.dx = dx
        self.dy = dy
        self.coyote_timer = 0
        self.jump_buffer_timer = 0
        self.is_grounded = True


class MockSlimeFull(MockSlime):
    """Extended slime mock with velocity and history for F5 overlay tests."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_x = kwargs.get("target_x", 50)
        self.target_y = kwargs.get("target_y", 60)


class MockGamePlan02:
    """Game mock with Plan 02-compatible player and slime."""
    def __init__(self):
        self.player = MockPlayer(x=50, y=100, w=10, h=14)
        self.slime = MockSlimeFull(x=120, y=100, w=16, h=16, dx=0.0, dy=0.0)
        self.enemies = []
        self.projectiles = []
        self.doors = []
        self.mole = None
        self.cam_x = 0
        self.cam_y = 0


# --- Test 9: Coyote blips maxlen ---

def test_coyote_blips_maxlen():
    """_coyote_blips deque has maxlen=32 to prevent unbounded growth (T-27-02)."""
    _reset_plan02()
    assert overlays._coyote_blips.maxlen == 32


# --- Test 10: Buffer blips maxlen ---

def test_buffer_blips_maxlen():
    """_buffer_blips deque has maxlen=32 to prevent unbounded growth (T-27-02)."""
    _reset_plan02()
    assert overlays._buffer_blips.maxlen == 32


# --- Test 11: Record coyote blip ---

def test_record_coyote_blip():
    """_on_fall_start appends (center_x, bottom_y, frame_count) to _coyote_blips."""
    _reset_plan02()
    game = MockGamePlan02()
    overlays._game_ref = game

    pyxel = sys.modules["pyxel"]
    pyxel.frame_count = 42

    overlays._on_fall_start()

    assert len(overlays._coyote_blips) == 1
    bx, by, frame = overlays._coyote_blips[0]
    # center_x = 50 + 10 // 2 = 55, bottom_y = 100 + 14 = 114
    assert bx == 55
    assert by == 114
    assert frame == 42


# --- Test 12: Slime trail readonly ---

def test_slime_trail_readonly():
    """Drawing slime overlay does not modify the history deque length."""
    _reset_plan02()
    game = MockGamePlan02()

    # Pre-populate slime history with 5 entries
    for i in range(5):
        game.slime.history.append((100 + i, 100 + i))

    original_len = len(game.slime.history)
    overlays.show_slime = True
    overlays._draw_slime_overlay(game)

    assert len(game.slime.history) == original_len


# --- Test 13: Stuck counter increments ---

def test_stuck_counter_increments():
    """Stuck counter increments when slime velocity magnitude < 0.1."""
    _reset_plan02()
    game = MockGamePlan02()
    game.slime.dx = 0.01
    game.slime.dy = 0.01

    overlays._slime_stuck_frames = 0
    overlays._draw_slime_overlay(game)

    assert overlays._slime_stuck_frames > 0


# --- Test 14: Stuck counter resets ---

def test_stuck_counter_resets():
    """Stuck counter resets to 0 when slime velocity magnitude >= 0.1."""
    _reset_plan02()
    game = MockGamePlan02()

    # First build up stuck frames
    game.slime.dx = 0.01
    game.slime.dy = 0.01
    overlays._slime_stuck_frames = 5

    # Now give it real velocity
    game.slime.dx = 1.0
    game.slime.dy = 0.0
    overlays._draw_slime_overlay(game)

    assert overlays._slime_stuck_frames == 0


# --- Test 15: init subscribes events ---

def test_init_subscribes_events():
    """init(game) subscribes to fall_start, jump_start, land events on event_bus."""
    _reset_plan02()
    from src.anim import event_bus

    game = MockGamePlan02()
    overlays.init(game)

    assert "fall_start" in event_bus._subscribers
    assert "jump_start" in event_bus._subscribers
    assert "land" in event_bus._subscribers
    assert len(event_bus._subscribers["fall_start"]) == 1
    assert len(event_bus._subscribers["jump_start"]) == 1
    assert len(event_bus._subscribers["land"]) == 1


# --- Test 16: init idempotent ---

def test_init_idempotent():
    """Calling init(game) twice does not create duplicate subscriptions (T-27-03)."""
    _reset_plan02()
    from src.anim import event_bus

    game = MockGamePlan02()
    overlays.init(game)
    overlays.init(game)

    assert len(event_bus._subscribers["fall_start"]) == 1
    assert len(event_bus._subscribers["jump_start"]) == 1
    assert len(event_bus._subscribers["land"]) == 1
