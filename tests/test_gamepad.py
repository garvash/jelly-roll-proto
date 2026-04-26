"""Verify gamepad controller support via _ACTION_MAP (D-04, D-05).

Updated in Plan 31.5-05 (sympathetic regression sweep per RESEARCH Risk 5):
the `dash` action was stripped from _ACTION_MAP in Plan 04 per CONTEXT D-04;
the `KEY_V` / `KEY_K` / `GAMEPAD1_BUTTON_X` bindings vanished with it.
Surviving action set is 8 (left, right, up, down, jump, spit, pause, confirm).
V is dead in v2.0 per FUSION-DESIGN.md Input Model.
"""
import unittest


class TestGamepadMapping(unittest.TestCase):
    """All 8 surviving game actions have gamepad bindings via source inspection."""

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

    # test_button_x_dash deleted in Plan 31.5-05: the `dash` action was
    # stripped from _ACTION_MAP per CONTEXT D-04. V button is dead in v2.0.

    def test_keyboard_keys_preserved(self):
        """Surviving keyboard bindings present (KEY_V / KEY_K removed with dash strip)."""
        self.assertIn("KEY_LEFT", self.source)
        self.assertIn("KEY_A", self.source)
        self.assertIn("KEY_SPACE", self.source)
        self.assertIn("KEY_Z", self.source)
        self.assertIn("KEY_J", self.source)

    def test_eight_gamepad_bindings(self):
        """All 8 surviving actions have exactly one gamepad constant each.

        Down from 9 pre-Phase-31.5: GAMEPAD1_BUTTON_X (dash) stripped.
        """
        count = self.source.count("GAMEPAD1")
        self.assertEqual(count, 8, f"Expected 8 GAMEPAD1 references, found {count}")


if __name__ == "__main__":
    unittest.main()
