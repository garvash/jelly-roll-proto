"""Phase 25 livereach tests — FND-05 acceptance artifact #1.

For each of GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, WALK_FRICTION, this suite
proves that a ``tuning.set_value`` call between two ``player.update()`` calls
changes the physics effect on the second update. This is the automated
proof that Phase 25's use-site migration reaches gameplay (25-CONTEXT D-04.1).

Hermetic via autouse ``tuning.reset()`` teardown (D-04a) — every test starts
and ends at the v1.3 baseline.
"""
import math
import pytest
from unittest.mock import MagicMock, patch
import sys

# Pyxel must be mocked globally for ``src.entities.player`` to import in a
# headless test harness. Pattern stolen verbatim from ``tests/test_physics.py``.
mock_pyxel = MagicMock()
sys.modules["pyxel"] = mock_pyxel

from src.entities.player import Player  # noqa: E402 — after pyxel mock
from src.core import tuning  # noqa: E402 — after pyxel mock

# --- Named constants (project memory: no magic numbers) ---------------------
# 10x multiplier is big enough that a single-frame change in GRAVITY or
# JUMP_FORCE is visible above floating-point noise, and WALK_ACCEL accumulator
# still saturates cleanly in ~10 frames at the mutated MAX_WALK_SPEED.
LIVEREACH_MULTIPLIER = 10.0

# Number of frames to drive the walk-saturation tests. At baseline,
# MAX_WALK_SPEED / WALK_ACCEL = 1.25 / 0.125 = 10, so 16 frames saturates
# baseline with headroom. At the mutated cap (12.5), 16 * 0.125 = 2.0 < 12.5,
# so we must run long enough for the mutated run to exceed baseline without
# forcing full saturation (which would take 100 frames). The assertion only
# requires dx_mutated > dx_baseline, which is true from frame 11 onward.
WALK_SATURATION_FRAMES = 16

# Non-zero starting dx for the WALK_FRICTION test. Must be strictly positive
# and small enough that 10 * WALK_FRICTION (the mutated decel) does not
# over-shoot zero on the first frame at baseline, so both runs stay in the
# "friction > 0" branch of handle_input.
FRICTION_START_DX = 1.0

# Floating-point tolerance for direction-of-change assertions. The tests do
# not re-derive physics integration; they only check sign + monotonicity, so
# a loose rel tolerance is sufficient.
APPROX_REL = 1e-6


# --- Autouse teardown fixture (D-04a) ---------------------------------------
@pytest.fixture(autouse=True)
def _tuning_reset_after_each_test():
    """Restore the full tuning baseline after every test so mutations do not
    leak between test functions (25-CONTEXT D-04a)."""
    yield
    tuning.reset()


# --- Player harness fixtures (copied from tests/test_physics.py) ------------
@pytest.fixture
def mock_level():
    level = MagicMock()
    level.check_collision.return_value = False
    level.check_hazard.return_value = False
    level.is_switch.return_value = False
    # update_shield() queries this; returning None keeps the shield branch
    # dormant so the test measures only pure physics.
    level.get_zone_hazard_type.return_value = None
    return level


@pytest.fixture
def mock_slime():
    slime = MagicMock()
    slime.x = 100
    slime.y = 100
    slime.w = 8
    slime.h = 8
    slime.juice = 100
    slime.max_juice = 100
    slime.is_dissipated = False
    slime.is_recalling = False
    return slime


def _fresh_player(level):
    """Instantiate a Player at (0, 0) with no level-map contact.

    Tests patch ``src.entities.player.input_manager`` per-call to drive the
    exact input state they need.
    """
    return Player(0, 0, level)


def _neutral_input(m_input):
    """Configure a patched input_manager mock to report all buttons released."""
    m_input.btn.return_value = False
    m_input.btnp.return_value = False
    m_input.btnr.return_value = False
    m_input.was_tap.return_value = False
    m_input.hold_frames.return_value = 0


# --- Test 1: GRAVITY livereach (D-04.1 acceptance bar) ----------------------
def test_livereach_gravity(mock_level, mock_slime):
    """``tuning.set_value('GRAVITY', 10x baseline)`` must change the dy
    applied during ``apply_physics()`` on the next ``update()``."""
    baseline_gravity = tuning.get_baseline("GRAVITY")

    # --- Phase A: baseline gravity, one frame of falling from rest. --------
    player_a = _fresh_player(mock_level)
    player_a.is_grounded = False
    player_a.state = "FALLING"
    player_a.dy = 0.0
    with patch("src.entities.player.input_manager") as m_input:
        _neutral_input(m_input)
        player_a.update(mock_slime)
    dy_baseline = player_a.dy

    # --- Phase B: 10x gravity, one frame of falling from rest. -------------
    tuning.set_value("GRAVITY", baseline_gravity * LIVEREACH_MULTIPLIER)
    player_b = _fresh_player(mock_level)
    player_b.is_grounded = False
    player_b.state = "FALLING"
    player_b.dy = 0.0
    with patch("src.entities.player.input_manager") as m_input:
        _neutral_input(m_input)
        player_b.update(mock_slime)
    dy_mutated = player_b.dy

    assert dy_mutated > dy_baseline, (
        f"GRAVITY livereach failed: dy_baseline={dy_baseline}, "
        f"dy_mutated={dy_mutated}. If these are equal, player.py is still "
        f"caching GRAVITY at import time — Phase 25 Plan 01 did not migrate "
        f"the use site correctly."
    )
    # The 10x mutated gravity should accelerate ~10x faster in one frame.
    assert dy_mutated == pytest.approx(
        dy_baseline * LIVEREACH_MULTIPLIER, rel=APPROX_REL
    )


# --- Test 2: JUMP_FORCE livereach -------------------------------------------
def test_livereach_jump_force(mock_level, mock_slime):
    """``tuning.set_value('JUMP_FORCE', 10x baseline)`` must change the dy
    set by the jump branch of ``handle_input()`` on the next frame.

    JUMP_FORCE is negative (up = -y in pyxel), so "stronger jump" means
    "more negative dy".
    """
    baseline_jump = tuning.get_baseline("JUMP_FORCE")

    def _fire_jump(m_input):
        # btnp("jump") must fire true for update_timers() to load the buffer,
        # then handle_input() consumes the buffer + coyote_timer. Neutral for
        # all other actions.
        m_input.btnp.side_effect = lambda action, **kw: action == "jump"
        m_input.btn.return_value = False
        m_input.btnr.return_value = False
        m_input.was_tap.return_value = False
        m_input.hold_frames.return_value = 0

    # --- Phase A: baseline JUMP_FORCE, one frame with jump input. ----------
    player_a = _fresh_player(mock_level)
    player_a.is_grounded = True  # coyote_timer will be set to COYOTE_TIME
    player_a.state = "IDLE"
    player_a.dy = 0.0
    with patch("src.entities.player.input_manager") as m_input:
        _fire_jump(m_input)
        player_a.update(mock_slime)
    # handle_input() sets dy = JUMP_FORCE, then apply_physics() adds GRAVITY
    # (since is_grounded was flipped to False by the jump). Both branches
    # scale with the mutation target since only JUMP_FORCE changes between
    # phase A and phase B.
    dy_baseline = player_a.dy

    # --- Phase B: 10x JUMP_FORCE, one frame with jump input. ---------------
    tuning.set_value("JUMP_FORCE", baseline_jump * LIVEREACH_MULTIPLIER)
    player_b = _fresh_player(mock_level)
    player_b.is_grounded = True
    player_b.state = "IDLE"
    player_b.dy = 0.0
    with patch("src.entities.player.input_manager") as m_input:
        _fire_jump(m_input)
        player_b.update(mock_slime)
    dy_mutated = player_b.dy

    # "Stronger jump" = "more negative dy". Assert strict inequality in the
    # up direction, and a 10x magnitude relationship (modulo the one-frame
    # gravity tick which is identical in both runs and cancels out in the
    # difference).
    assert dy_mutated < dy_baseline, (
        f"JUMP_FORCE livereach failed: dy_baseline={dy_baseline}, "
        f"dy_mutated={dy_mutated}. Expected dy_mutated strictly more "
        f"negative. If equal, player.py is still caching JUMP_FORCE at "
        f"import time."
    )
    # Both runs add the same one-frame gravity tick, so the difference
    # (dy_mutated - dy_baseline) == 9 * JUMP_FORCE_baseline (since mutated
    # == 10 * baseline, delta == 9 * baseline).
    expected_delta = (LIVEREACH_MULTIPLIER - 1.0) * baseline_jump
    assert (dy_mutated - dy_baseline) == pytest.approx(
        expected_delta, rel=APPROX_REL
    )


# --- Test 3: MAX_WALK_SPEED livereach ---------------------------------------
def test_livereach_max_walk_speed(mock_level, mock_slime):
    """``tuning.set_value('MAX_WALK_SPEED', 10x baseline)`` must change the
    clamp applied in ``handle_input()`` so the walk velocity grows past the
    old cap on the next frame."""
    baseline_cap = tuning.get_baseline("MAX_WALK_SPEED")

    def _walk_right(m_input):
        m_input.btn.side_effect = lambda action: action == "right"
        m_input.btnp.return_value = False
        m_input.btnr.return_value = False
        m_input.was_tap.return_value = False
        m_input.hold_frames.return_value = 0

    # --- Phase A: baseline cap, drive walk for enough frames to saturate. --
    player_a = _fresh_player(mock_level)
    player_a.is_grounded = True
    player_a.state = "IDLE"
    player_a.dx = 0.0
    with patch("src.entities.player.input_manager") as m_input:
        _walk_right(m_input)
        for _ in range(WALK_SATURATION_FRAMES):
            player_a.update(mock_slime)
    dx_baseline = player_a.dx

    # Sanity: baseline run must have saturated exactly at the baseline cap.
    assert dx_baseline == pytest.approx(baseline_cap, rel=APPROX_REL), (
        f"Baseline walk did not saturate: dx_baseline={dx_baseline}, "
        f"expected {baseline_cap}. Harness bug."
    )

    # --- Phase B: 10x cap, drive walk for the same frame count. ------------
    tuning.set_value("MAX_WALK_SPEED", baseline_cap * LIVEREACH_MULTIPLIER)
    player_b = _fresh_player(mock_level)
    player_b.is_grounded = True
    player_b.state = "IDLE"
    player_b.dx = 0.0
    with patch("src.entities.player.input_manager") as m_input:
        _walk_right(m_input)
        for _ in range(WALK_SATURATION_FRAMES):
            player_b.update(mock_slime)
    dx_mutated = player_b.dx

    # The mutated cap is now 12.5, well above the baseline cap of 1.25, so
    # the mutated run must have grown past the old cap. Exact equality to
    # ``WALK_SATURATION_FRAMES * WALK_ACCEL`` would require no saturation,
    # but the assertion here is the direction-of-change one.
    assert dx_mutated > dx_baseline, (
        f"MAX_WALK_SPEED livereach failed: dx_baseline={dx_baseline}, "
        f"dx_mutated={dx_mutated}. Expected dx_mutated > old cap. If equal, "
        f"player.py is still caching MAX_WALK_SPEED at import time."
    )


# --- Test 4: WALK_FRICTION livereach ----------------------------------------
def test_livereach_walk_friction(mock_level, mock_slime):
    """``tuning.set_value('WALK_FRICTION', 10x baseline)`` must change the
    decel applied in the friction branch of ``handle_input()`` so a coasting
    player decelerates faster on the next frame."""
    baseline_friction = tuning.get_baseline("WALK_FRICTION")

    # --- Phase A: baseline friction, one frame of coast from FRICTION_START_DX.
    player_a = _fresh_player(mock_level)
    player_a.is_grounded = True
    player_a.state = "IDLE"
    player_a.dx = FRICTION_START_DX
    with patch("src.entities.player.input_manager") as m_input:
        _neutral_input(m_input)
        player_a.update(mock_slime)
    dx_baseline = player_a.dx

    # Sanity: baseline friction should subtract exactly WALK_FRICTION.
    assert dx_baseline == pytest.approx(
        FRICTION_START_DX - baseline_friction, rel=APPROX_REL
    ), (
        f"Baseline friction did not subtract WALK_FRICTION cleanly: "
        f"dx_baseline={dx_baseline}. Harness bug."
    )

    # --- Phase B: 10x friction, one frame of coast from FRICTION_START_DX. -
    tuning.set_value("WALK_FRICTION", baseline_friction * LIVEREACH_MULTIPLIER)
    player_b = _fresh_player(mock_level)
    player_b.is_grounded = True
    player_b.state = "IDLE"
    player_b.dx = FRICTION_START_DX
    with patch("src.entities.player.input_manager") as m_input:
        _neutral_input(m_input)
        player_b.update(mock_slime)
    dx_mutated = player_b.dx

    # Stronger friction = smaller abs(dx) after one frame. Still positive
    # because 10 * baseline_friction (1.5) < FRICTION_START_DX (1.0)? No —
    # 1.5 > 1.0 so the clamp-to-zero branch triggers. Either way, the
    # mutated run must be strictly less than the baseline run's dx.
    assert dx_mutated < dx_baseline, (
        f"WALK_FRICTION livereach failed: dx_baseline={dx_baseline}, "
        f"dx_mutated={dx_mutated}. Expected dx_mutated strictly smaller. "
        f"If equal, player.py is still caching WALK_FRICTION at import time."
    )
    # At 10x friction (1.5), max(0, 1.0 - 1.5) = 0, so the mutated dx
    # should clamp exactly to 0.
    assert dx_mutated == pytest.approx(0.0, abs=APPROX_REL)
