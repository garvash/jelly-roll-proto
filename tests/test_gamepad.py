"""Verify gamepad controller support via _ACTION_MAP (D-04, D-05)."""
import unittest


class TestGamepadMapping(unittest.TestCase):
    """All 7 game actions must have gamepad bindings via source inspection."""

    def setUp(self):
        with open("src/core/input.py") as f:
            self.source = f.read()

    def test_dpad_left(self):
        self.assertIn("GAMEPAD1_BUTTON_DPAD_LEFT", self.source)

    def test_dpad_right(self):
        self.assertIn("GAMEPAD1_BUTTON_DPAD_RIGHT", self.source)

    def test_dpad_up(self):
        self.assertIn("GAMEPAD1_BUTTON_DPAD_UP", self.source)

    def test_dpad_down(self):
        self.assertIn("GAMEPAD1_BUTTON_DPAD_DOWN", self.source)

    def test_button_a_jump(self):
        """A (bottom) = Jump per D-04."""
        # GAMEPAD1_BUTTON_A should be in the "jump" line
        for line in self.source.split('\n'):
            if '"jump"' in line:
                self.assertIn("GAMEPAD1_BUTTON_A", line)
                return
        self.fail("No 'jump' action found in _ACTION_MAP")

    def test_button_b_spit(self):
        """B (right) = Spit per D-04."""
        for line in self.source.split('\n'):
            if '"spit"' in line:
                self.assertIn("GAMEPAD1_BUTTON_B", line)
                return
        self.fail("No 'spit' action found in _ACTION_MAP")

    def test_button_x_dash(self):
        """X (left) = Dash per D-04."""
        for line in self.source.split('\n'):
            if '"dash"' in line:
                self.assertIn("GAMEPAD1_BUTTON_X", line)
                return
        self.fail("No 'dash' action found in _ACTION_MAP")

    def test_keyboard_keys_preserved(self):
        """Existing keyboard bindings unchanged."""
        self.assertIn("KEY_LEFT", self.source)
        self.assertIn("KEY_A", self.source)
        self.assertIn("KEY_SPACE", self.source)
        self.assertIn("KEY_Z", self.source)
        self.assertIn("KEY_J", self.source)
        self.assertIn("KEY_V", self.source)
        self.assertIn("KEY_K", self.source)

    def test_nine_gamepad_bindings(self):
        """All 9 actions have exactly one gamepad constant each."""
        count = self.source.count("GAMEPAD1")
        self.assertEqual(count, 9, f"Expected 9 GAMEPAD1 references, found {count}")


if __name__ == "__main__":
    unittest.main()
