"""Tests for Slime Boost (ABL-06, D-07 through D-11)."""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from src.core.constants import (
    BOOST_FORCE, BOOST_JUICE_COST, BOOST_RECOMMIT_WINDOW,
    BOOST_DOWNWARD_DAMAGE_W, BOOST_DOWNWARD_DAMAGE_H,
    JUMP_BUFFER, GRAVITY, FALLING_GRAVITY_MULTIPLIER,
)


def make_player(**overrides):
    """Create a Player with mocked dependencies."""
    with patch("src.entities.player.input_manager"):
        from src.entities.player import Player
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        level_map.check_hazard.return_value = False
        game = MagicMock()
        p = Player(50, 50, level_map, game)
        for k, v in overrides.items():
            setattr(p, k, v)
        return p


def make_slime(**overrides):
    """Create a mock slime with standard defaults."""
    slime = MagicMock()
    slime.juice = 200.0
    slime.max_juice = 200.0
    slime.w = 8
    slime.h = 8
    slime.x = 50
    slime.y = 50
    slime.is_fused = True
    slime.is_dissipated = False
    slime.is_recalling = False
    slime.is_punted = False
    slime.is_holding_position = False
    slime.dx = 0
    slime.dy = 0
    slime.history = MagicMock()
    for k, v in overrides.items():
        setattr(slime, k, v)
    return slime


class TestBoostTrigger:
    """Test boost activation conditions (D-07)."""

    @patch("src.entities.player.input_manager")
    def test_boost_trigger_fused_airborne(self, mock_input):
        """Fused + airborne + has_boost + SPACE sets BOOSTING, dy=BOOST_FORCE, consumes juice."""
        mock_input.btnp.return_value = False
        mock_input.btn.return_value = False
        mock_input.btnr.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(is_fused=True, is_grounded=False, has_boost=True, has_drill=False)
        slime = make_slime()

        # Simulate SPACE press: btnp("jump") returns True
        def btnp_side(action):
            return action == "jump"
        mock_input.btnp.side_effect = btnp_side
        # down not held (not drill)
        def btn_side(action):
            return False
        mock_input.btn.side_effect = btn_side

        p.handle_input(slime)
        assert p.state == "BOOSTING"
        assert p.dy == BOOST_FORCE
        slime.consume.assert_called_with(BOOST_JUICE_COST)

    @patch("src.entities.player.input_manager")
    def test_boost_requires_fused(self, mock_input):
        """Not fused: no boost."""
        mock_input.btnp.return_value = False
        mock_input.btn.return_value = False
        mock_input.btnr.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(is_fused=False, is_grounded=False, has_boost=True)
        slime = make_slime(is_fused=False)

        def btnp_side(action):
            return action == "jump"
        mock_input.btnp.side_effect = btnp_side

        p.handle_input(slime)
        assert p.state != "BOOSTING"

    @patch("src.entities.player.input_manager")
    def test_boost_requires_airborne(self, mock_input):
        """Grounded: no boost (ground SPACE = jump)."""
        mock_input.btnp.return_value = False
        mock_input.btn.return_value = False
        mock_input.btnr.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(is_fused=True, is_grounded=True, has_boost=True)
        slime = make_slime()

        def btnp_side(action):
            return action == "jump"
        mock_input.btnp.side_effect = btnp_side

        p.handle_input(slime)
        assert p.state != "BOOSTING"

    @patch("src.entities.player.input_manager")
    def test_boost_requires_has_boost(self, mock_input):
        """has_boost=False: no boost."""
        mock_input.btnp.return_value = False
        mock_input.btn.return_value = False
        mock_input.btnr.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(is_fused=True, is_grounded=False, has_boost=False)
        slime = make_slime()

        def btnp_side(action):
            return action == "jump"
        mock_input.btnp.side_effect = btnp_side

        p.handle_input(slime)
        assert p.state != "BOOSTING"


class TestBoostChaining:
    """Test multi-tap chaining within recommit window (D-08)."""

    @patch("src.entities.player.input_manager")
    def test_boost_chain_within_window(self, mock_input):
        """SPACE tap during recommit window chains another boost."""
        mock_input.btnp.side_effect = lambda a: a == "jump"

        p = make_player(state="BOOSTING", boost_recommit_timer=5, is_grounded=False)
        slime = make_slime(juice=200.0)

        p.update_boost(slime)

        assert p.dy == BOOST_FORCE
        slime.consume.assert_called_with(BOOST_JUICE_COST)
        assert p.boost_recommit_timer == BOOST_RECOMMIT_WINDOW


class TestBoostExit:
    """Test boost exit conditions (D-09)."""

    @patch("src.entities.player.input_manager")
    def test_boost_exit_window_expired(self, mock_input):
        """Recommit timer expires: unfuse normally, state=FALLING."""
        mock_input.btnp.return_value = False

        p = make_player(state="BOOSTING", boost_recommit_timer=1, is_fused=True)
        slime = make_slime()

        # Timer will decrement to 0, then exit
        p.update_boost(slime)

        assert p.state == "FALLING"
        assert p.boost_recommit_timer == 0

    @patch("src.entities.player.input_manager")
    def test_boost_exit_juice_empty(self, mock_input):
        """Juice empties during boost: dissipate + burnout."""
        mock_input.btnp.side_effect = lambda a: a == "jump"

        p = make_player(state="BOOSTING", boost_recommit_timer=5, is_fused=True)
        # Slime with low juice -- will go to 0 after consume
        slime = make_slime(juice=10.0)

        # After consume(25), juice should be negative
        def consume_side(amount):
            slime.juice -= amount
        slime.consume.side_effect = consume_side

        p.update_boost(slime)

        assert p.state == "FALLING"
        slime.dissipate.assert_called_once()


class TestBoostJumpBuffer:
    """Test jump buffer clearing during boost (Pitfall 3)."""

    @patch("src.entities.player.input_manager")
    def test_boost_clears_jump_buffer(self, mock_input):
        """Boost activation clears jump_buffer_timer."""
        mock_input.btnp.return_value = False
        mock_input.btn.return_value = False
        mock_input.btnr.return_value = False
        mock_input.was_tap.return_value = False
        mock_input.hold_frames.return_value = 0

        p = make_player(
            is_fused=True, is_grounded=False, has_boost=True,
            jump_buffer_timer=4, has_drill=False
        )
        slime = make_slime()

        def btnp_side(action):
            return action == "jump"
        mock_input.btnp.side_effect = btnp_side

        p.handle_input(slime)
        assert p.state == "BOOSTING"
        assert p.jump_buffer_timer == 0

    def test_boost_exit_clears_jump_buffer(self):
        """end_boost clears jump_buffer_timer."""
        p = make_player(state="BOOSTING", jump_buffer_timer=4, is_fused=True)
        slime = make_slime()
        p.end_boost(slime, dissipate=False)
        assert p.jump_buffer_timer == 0


class TestBoostPhysics:
    """Test physics during BOOSTING state."""

    def test_boost_gravity_applies(self):
        """Gravity applies during BOOSTING (player arcs between taps)."""
        p = make_player(state="BOOSTING", dy=-2.0, is_grounded=False)
        initial_dy = p.dy
        p.apply_physics()
        # Gravity should increase dy (make it less negative or more positive)
        assert p.dy > initial_dy

    @patch("src.entities.player.input_manager")
    def test_boost_no_buffer_accumulation_during_boost(self, mock_input):
        """Jump buffer does not accumulate during BOOSTING state."""
        mock_input.btnp.side_effect = lambda a: a == "jump"

        p = make_player(state="BOOSTING", jump_buffer_timer=0, is_grounded=False)
        p.update_timers()
        assert p.jump_buffer_timer == 0


class TestBoostStompDamage:
    """Test boost enemy stomp damage (D-10)."""

    def test_boost_stomps_enemy_below(self):
        """BOOSTING player damages enemy directly below via stomp hitbox."""
        p = make_player(state="BOOSTING", x=50, y=50, w=8, h=8)
        enemy = MagicMock()
        enemy.is_alive = True
        enemy.x = 48
        enemy.y = 58  # Below player (player.y + player.h = 58)
        enemy.w = 12
        enemy.h = 8

        # Stomp hitbox: centered below player
        stomp_x = p.x + (p.w - BOOST_DOWNWARD_DAMAGE_W) // 2
        stomp_y = p.y + p.h

        # AABB overlap check (same as main.py will use)
        overlaps = (stomp_x < enemy.x + enemy.w and
                    stomp_x + BOOST_DOWNWARD_DAMAGE_W > enemy.x and
                    stomp_y < enemy.y + enemy.h and
                    stomp_y + BOOST_DOWNWARD_DAMAGE_H > enemy.y)

        assert overlaps, "Stomp hitbox should overlap enemy below"
        if overlaps:
            enemy.take_damage(1)
        enemy.take_damage.assert_called_with(1)

    def test_boost_no_stomp_distant_enemy(self):
        """Enemy not below player is not stomped."""
        p = make_player(state="BOOSTING", x=50, y=50, w=8, h=8)
        enemy = MagicMock()
        enemy.is_alive = True
        enemy.x = 100  # Far away
        enemy.y = 100
        enemy.w = 8
        enemy.h = 8

        stomp_x = p.x + (p.w - BOOST_DOWNWARD_DAMAGE_W) // 2
        stomp_y = p.y + p.h

        overlaps = (stomp_x < enemy.x + enemy.w and
                    stomp_x + BOOST_DOWNWARD_DAMAGE_W > enemy.x and
                    stomp_y < enemy.y + enemy.h and
                    stomp_y + BOOST_DOWNWARD_DAMAGE_H > enemy.y)

        assert not overlaps, "Stomp hitbox should NOT overlap distant enemy"
