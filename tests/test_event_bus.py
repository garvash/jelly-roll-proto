"""Phase 26 ANIM-02 event bus tests.

Plan 01 -- module primitives (subscribe/emit/reset).
Plan 03 -- gameplay integration tests (17 per-event + 3 pitfall guards).

conftest.py provides autouse _reset_event_bus fixture and pyxel mock.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.anim import event_bus
from src.entities.player import Player
import src.core.input as input_manager


# ---- Plan 26-01 primitives (unchanged) ----

def test_subscribe_emit_roundtrip():
    received = []
    event_bus.subscribe("x", lambda k=None: received.append(k))
    event_bus.emit("x", k=1)
    assert received == [1]


def test_emit_with_no_subscribers_is_noop():
    # Should not raise.
    event_bus.emit("nonexistent_event", data=42)


def test_multiple_subscribers_called_in_order():
    order = []
    event_bus.subscribe("evt", lambda: order.append("first"))
    event_bus.subscribe("evt", lambda: order.append("second"))
    event_bus.emit("evt")
    assert order == ["first", "second"]


def test_reset_clears_subscribers():
    called = []
    event_bus.subscribe("x", lambda: called.append(True))
    event_bus.reset()
    event_bus.emit("x")
    assert called == []


# ---- Plan 26-03: 17 integration tests (one per ANIM-02 event) ----

def _make_player(mock_level):
    """Create a Player for integration tests with sensible defaults."""
    p = Player(100, 100, mock_level)
    p.is_grounded = True
    p.is_alive = True
    p.hp = 10
    p.max_hp = 10
    return p


def _btn_map(**overrides):
    """Return a function simulating input_manager.btn() calls."""
    mapping = {
        "left": False, "right": False, "up": False, "down": False,
        "jump": False, "spit": False, "dash": False,
    }
    mapping.update(overrides)
    return lambda name: mapping.get(name, False)


def _btnp_map(**overrides):
    """Return a function simulating input_manager.btnp() calls."""
    mapping = {
        "left": False, "right": False, "up": False, "down": False,
        "jump": False, "spit": False, "dash": False,
    }
    mapping.update(overrides)
    return lambda name: mapping.get(name, False)


def _btnr_map(**overrides):
    """Return a function simulating input_manager.btnr() calls."""
    mapping = {
        "left": False, "right": False, "up": False, "down": False,
        "jump": False, "spit": False, "dash": False,
    }
    mapping.update(overrides)
    return lambda name: mapping.get(name, False)


# 1. direction_change
def test_direction_change_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("direction_change", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.facing_right = True
    # Press left to flip facing
    with patch.object(input_manager, "btn", side_effect=_btn_map(left=True)), \
         patch.object(input_manager, "btnp", side_effect=_btnp_map()), \
         patch.object(input_manager, "btnr", side_effect=_btnr_map()), \
         patch.object(input_manager, "was_tap", return_value=False), \
         patch.object(input_manager, "hold_frames", return_value=0):
        p.handle_input(mock_slime)
    assert len(captured) >= 1, "direction_change should emit when facing flips"


# 2. jump_start
def test_jump_start_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("jump_start", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.is_grounded = True
    p.coyote_timer = 99
    p.jump_buffer_timer = 99
    p.state = "IDLE"
    with patch.object(input_manager, "btn", side_effect=_btn_map()), \
         patch.object(input_manager, "btnp", side_effect=_btnp_map()), \
         patch.object(input_manager, "btnr", side_effect=_btnr_map()), \
         patch.object(input_manager, "was_tap", return_value=False), \
         patch.object(input_manager, "hold_frames", return_value=0):
        p.handle_input(mock_slime)
    assert len(captured) >= 1, "jump_start should emit when buffered jump executes"


# 3. jump_released
def test_jump_released_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("jump_released", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.dy = -3.0
    p.state = "JUMPING"
    with patch.object(input_manager, "btn", side_effect=_btn_map()), \
         patch.object(input_manager, "btnp", side_effect=_btnp_map()), \
         patch.object(input_manager, "btnr", side_effect=_btnr_map(jump=True)), \
         patch.object(input_manager, "was_tap", return_value=False), \
         patch.object(input_manager, "hold_frames", return_value=0):
        p.handle_input(mock_slime)
    assert len(captured) >= 1, "jump_released should emit on jump button release"


# 4. fall_start
def test_fall_start_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("fall_start", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.is_grounded = False
    p.dy = -0.1  # Ascending, just about to cross zero
    # Drive apply_physics twice so gravity flips dy positive
    p.apply_physics()
    p.apply_physics()
    assert p.dy > 0, "dy should be positive after two physics frames"
    assert len(captured) >= 1, "fall_start should emit when dy crosses from <=0 to >0 while airborne"


# 5. land
def test_land_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("land", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.is_grounded = False
    p.dy = 2.0  # Falling

    # Mock collision: floor at a specific position
    def mock_check_collision(x, y, w, h):
        # Return True when checking the floor position (after vertical move)
        if y > 100:
            return True
        return False

    mock_level.check_collision.side_effect = mock_check_collision
    mock_level.check_hazard.return_value = False
    p.move_and_collide(mock_slime)
    assert len(captured) >= 1, "land should emit when player transitions from airborne to grounded"


# 6. wall_touch
def test_wall_touch_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("wall_touch", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.is_grounded = False
    p.dy = 2.0  # Must be falling for wall slide
    p.is_wall_sliding = False

    # Mock: left wall present
    def mock_collision(x, y, w, h):
        # Wall on left side: check_collision(self.x - 1, ...) returns True
        if w == 1 and x < p.x:
            return True
        return False

    mock_level.check_collision.side_effect = mock_collision
    mock_level.check_hazard.return_value = False
    with patch.object(input_manager, "btn", side_effect=_btn_map(left=True)), \
         patch.object(input_manager, "btnp", side_effect=_btnp_map()), \
         patch.object(input_manager, "btnr", side_effect=_btnr_map()), \
         patch.object(input_manager, "was_tap", return_value=False), \
         patch.object(input_manager, "hold_frames", return_value=0):
        p.handle_input(mock_slime)
    assert len(captured) >= 1, "wall_touch should emit on wall slide start"


# 7. wall_jump
def test_wall_jump_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("wall_jump", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.is_grounded = False
    p.dy = 2.0
    p.is_wall_sliding = True
    p.wall_dir = -1
    p.coyote_timer = 0
    p.jump_buffer_timer = 99  # Buffered jump

    # Mock: on_left_wall = True (1px probe left of player)
    def mock_collision(x, y, w, h):
        if w == 1 and x < p.x:
            return True
        return False

    mock_level.check_collision.side_effect = mock_collision
    with patch.object(input_manager, "btn", side_effect=_btn_map(left=True)), \
         patch.object(input_manager, "btnp", side_effect=_btnp_map()), \
         patch.object(input_manager, "btnr", side_effect=_btnr_map()), \
         patch.object(input_manager, "was_tap", return_value=False), \
         patch.object(input_manager, "hold_frames", return_value=0):
        p.handle_input(mock_slime)
    assert len(captured) >= 1, "wall_jump should emit on wall jump"


# 8. drill_impact [FUSION]
def test_drill_impact_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("drill_impact", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.state = "DIVING"
    p.is_fused = True
    p.dy = 5.0  # Falling while diving
    mock_slime.juice = 50

    # Mock: vertical collision (floor hit during dive, no destructible tile)
    def mock_collision(x, y, w, h):
        if y > 100:
            return True
        return False

    mock_level.check_collision.side_effect = mock_collision
    mock_level.check_hazard.return_value = False
    mock_level.get_destructible_at.return_value = None
    p.move_and_collide(mock_slime)
    assert len(captured) >= 1, "drill_impact should emit on drill dive floor impact"


# 9. fuse_start [FUSION]
def test_fuse_start_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("fuse_start", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.fuse(mock_slime)
    assert len(captured) >= 1, "fuse_start should emit when player fuses"


# 10. fuse_end [FUSION]
def test_fuse_end_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("fuse_end", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.fuse(mock_slime)
    event_bus.reset()  # Clear fuse_start captures
    captured.clear()
    event_bus.subscribe("fuse_end", lambda **kw: captured.append(kw))
    p.unfuse(mock_slime)
    assert len(captured) >= 1, "fuse_end should emit when player unfuses"


# 11. ram_start [FUSION]
def test_ram_start_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("ram_start", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.is_fused = True
    with patch.object(input_manager, "btn", side_effect=_btn_map()):
        p.start_ram(mock_slime)
    assert len(captured) >= 1, "ram_start should emit on ram activation"


# 12. ram_impact [FUSION] -- on cracked-H break only
def test_ram_impact_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("ram_impact", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.state = "RAMMING"
    p.is_fused = True
    p.dx = 3.0
    p.ram_dx = 3.0
    p.ram_dy = 0
    p.invuln_timer = 9999
    mock_slime.juice = 50

    # Set up game mock for ram break
    game_mock = MagicMock()
    game_mock.shake_timer = 0
    p.game = game_mock

    # Mock: horizontal collision with cracked-H tile
    call_count = [0]
    def mock_collision(x, y, w, h):
        call_count[0] += 1
        # After horizontal move (first collision check), return True
        if call_count[0] == 1:
            return True
        return False

    mock_level.check_collision.side_effect = mock_collision
    mock_level.check_hazard.return_value = False
    mock_level.get_cracked_h_at.return_value = (5, 5)  # Cracked tile found
    p.move_and_collide(mock_slime)
    assert len(captured) >= 1, "ram_impact should emit on cracked-H break"


# 13a. boost_tap [FUSION] -- site A: start_boost
def test_boost_tap_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("boost_tap", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.is_fused = True
    p.is_grounded = False
    p.has_boost = True
    mock_slime.juice = 50
    p.start_boost(mock_slime)
    assert len(captured) >= 1, "boost_tap should emit from start_boost (site A)"


# 13b. boost_tap [FUSION] -- site B: update_boost chain tap
def test_boost_tap_chain_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("boost_tap", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.state = "BOOSTING"
    p.is_fused = True
    p.boost_recommit_timer = 10
    mock_slime.juice = 50
    # Simulate chain tap: jump button pressed
    with patch.object(input_manager, "btnp", side_effect=_btnp_map(jump=True)):
        p.update_boost(mock_slime)
    assert len(captured) >= 1, "boost_tap should emit from update_boost chain tap (site B)"


# 14. charge_shot_fire [FUSION]
def test_charge_shot_fire_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("charge_shot_fire", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.is_fused = True
    p.facing_right = True
    mock_slime.juice = 50
    # Set up game mock
    game_mock = MagicMock()
    game_mock.projectiles = []
    game_mock.particles = []
    p.game = game_mock
    p.fire_charge_shot(mock_slime)
    assert len(captured) >= 1, "charge_shot_fire should emit on charge shot"


# 15. spit
def test_spit_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("spit", lambda **kw: captured.append(kw))
    from src.entities.slime import Slime
    s = Slime(100, 100)
    s.juice = 100
    result = s.spit(1, 0, mock_level)
    assert len(captured) >= 1, "spit should emit on successful spit"


# 16. damaged
def test_damaged_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("damaged", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.is_alive = True
    p.invuln_timer = 0
    p.hp = 10
    p.is_fused = False
    p.take_damage(1)
    assert len(captured) >= 1, "damaged should emit on real HP damage"


# 17. death
def test_death_emits_from_gameplay(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("death", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.is_alive = True
    p.die()
    assert len(captured) >= 1, "death should emit on player death"


# ---- Plan 26-03: 3 Pitfall exactly-once guards ----

# Pitfall 3: direction_change only on flip, not every frame
def test_direction_change_only_on_flip(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("direction_change", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.facing_right = True

    # Hold RIGHT for 10 frames (no flip) -- should NOT emit
    for _ in range(10):
        with patch.object(input_manager, "btn", side_effect=_btn_map(right=True)), \
             patch.object(input_manager, "btnp", side_effect=_btnp_map()), \
             patch.object(input_manager, "btnr", side_effect=_btnr_map()), \
             patch.object(input_manager, "was_tap", return_value=False), \
             patch.object(input_manager, "hold_frames", return_value=0):
            p.handle_input(mock_slime)
    assert len(captured) == 0, "direction_change should NOT emit when facing stays the same"

    # Now flip to LEFT for 10 frames -- should emit exactly once
    for _ in range(10):
        with patch.object(input_manager, "btn", side_effect=_btn_map(left=True)), \
             patch.object(input_manager, "btnp", side_effect=_btnp_map()), \
             patch.object(input_manager, "btnr", side_effect=_btnr_map()), \
             patch.object(input_manager, "was_tap", return_value=False), \
             patch.object(input_manager, "hold_frames", return_value=0):
            p.handle_input(mock_slime)
    assert len(captured) == 1, f"direction_change should emit exactly once on flip, got {len(captured)}"


# Pitfall 5: land only on touchdown, not every grounded frame
def test_land_only_on_touchdown(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("land", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.is_grounded = False
    p.dy = 2.0

    # Land: collision on first frame
    def mock_collision(x, y, w, h):
        if y > 100:
            return True
        return False

    mock_level.check_collision.side_effect = mock_collision
    mock_level.check_hazard.return_value = False
    p.move_and_collide(mock_slime)
    assert len(captured) == 1, "land should emit exactly once on touchdown"

    # Drive 10 more frames where player is already grounded
    for _ in range(10):
        p.dy = 0
        p.move_and_collide(mock_slime)
    assert len(captured) == 1, f"land should not re-emit while staying grounded, got {len(captured)}"


# Pitfall 4: fall_start only on transition, not every falling frame
def test_fall_start_only_on_transition(mock_level, mock_slime):
    captured = []
    event_bus.subscribe("fall_start", lambda **kw: captured.append(kw))
    p = _make_player(mock_level)
    p.is_grounded = False
    p.dy = -0.1  # Just barely ascending

    # Drive 10 frames of physics -- gravity should flip dy and hold it positive
    for _ in range(10):
        p.apply_physics()
    assert p.dy > 0, "dy should be positive after several physics frames"
    assert len(captured) == 1, f"fall_start should emit exactly once on dy transition, got {len(captured)}"
