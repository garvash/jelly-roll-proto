"""Tests for basic dash mechanic (D-15)."""
import unittest
from unittest.mock import MagicMock, patch
from src.entities.player import Player
from src.core.constants import DASH_SPEED, DASH_DURATION, DASH_COOLDOWN, DASH_IFRAMES


class MockLevelMap:
    def check_collision(self, x, y, w, h):
        return False
    def check_hazard(self, x, y, w, h):
        return False
    def get_destructible_at(self, x, y, w, h):
        return None
    def is_switch(self, tx, ty):
        return False


class TestDash(unittest.TestCase):
    def setUp(self):
        self.level_map = MockLevelMap()
        self.player = Player(50, 50, self.level_map)
        self.player.has_dash = True
        self.player.is_grounded = True

    def test_dash_sets_state(self):
        """start_dash() sets state to DASHING and timer to DASH_DURATION."""
        self.player.start_dash()
        self.assertEqual(self.player.state, "DASHING")
        self.assertEqual(self.player.dash_timer, DASH_DURATION)

    def test_dash_grants_iframes(self):
        """start_dash() grants at least DASH_IFRAMES of invulnerability."""
        self.player.start_dash()
        self.assertGreaterEqual(self.player.invuln_timer, DASH_IFRAMES)

    def test_dash_direction_right(self):
        """Dash direction matches facing_right = True."""
        self.player.facing_right = True
        self.player.start_dash()
        self.assertEqual(self.player.dash_dx, DASH_SPEED)

    def test_dash_direction_left(self):
        """Dash direction matches facing_right = False."""
        self.player.facing_right = False
        self.player.start_dash()
        self.assertEqual(self.player.dash_dx, -DASH_SPEED)

    def test_dash_cooldown(self):
        """start_dash() sets cooldown to DASH_COOLDOWN."""
        self.player.start_dash()
        self.assertEqual(self.player.dash_cooldown, DASH_COOLDOWN)

    def test_air_dash_once(self):
        """Air dash marks dash_air_used; second air dash is blocked."""
        self.player.is_grounded = False
        self.player.start_dash()
        self.assertTrue(self.player.dash_air_used)
        self.assertEqual(self.player.state, "DASHING")

        # Simulate dash ending
        self.player.dash_timer = 0
        self.player.state = "FALLING"
        self.player.dash_cooldown = 0

        # Second air dash should be blocked by handle_input logic
        # (dash_air_used is True, so the elif branch hits pass)
        with patch("src.entities.player.input_manager") as m_input:
            m_input.btnp.side_effect = lambda action, **kw: action == "dash"
            m_input.btn.return_value = False
            m_input.btnr.return_value = False
            from src.entities.slime import Slime
            slime = Slime(50, 50)
            self.player.handle_input(slime)
        # State should NOT be DASHING (air dash already used)
        self.assertNotEqual(self.player.state, "DASHING")

    def test_air_dash_resets_on_ground(self):
        """dash_air_used resets to False when player lands."""
        self.player.dash_air_used = True
        # Simulate floor collision: set dy >= 0 and make collision return True
        self.player.dy = 1.0
        self.player.y = 48.0  # Position near a tile boundary
        mock_map = MagicMock()
        # First call: horizontal hazard check -> False
        # Second call: horizontal collision -> False
        # Third call: vertical hazard check -> False
        # Fourth call: vertical collision -> True (floor)
        # Fifth call: grounding check (look 1px down) -> True
        mock_map.check_hazard.return_value = False
        mock_map.check_collision.side_effect = [False, False, True]
        mock_map.get_destructible_at.return_value = None
        self.player.level_map = mock_map
        self.player.move_and_collide()
        self.assertFalse(self.player.dash_air_used)

    def test_apply_dash_physics(self):
        """Dash physics sets dx to dash_dx and dy to 0."""
        self.player.start_dash()
        self.player.dy = 5.0  # Simulate falling
        self.player.apply_dash_physics()
        self.assertEqual(self.player.dx, self.player.dash_dx)
        self.assertEqual(self.player.dy, 0)

    def test_dash_timer_ends_state(self):
        """When dash_timer reaches 0, state transitions out of DASHING."""
        self.player.start_dash()
        self.assertEqual(self.player.state, "DASHING")
        # Simulate timer ticking down
        self.player.dash_timer = 1
        with patch("src.entities.player.input_manager") as m_input:
            m_input.btnp.return_value = False
            m_input.btn.return_value = False
            m_input.btnr.return_value = False
            self.player.update_timers()
        self.assertNotEqual(self.player.state, "DASHING")


if __name__ == "__main__":
    unittest.main()
