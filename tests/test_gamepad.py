"""Verify gamepad controller support via _ACTION_MAP (D-04, D-05)."""
import sys
from unittest.mock import MagicMock

import pytest

# Mock pyxel before importing input module
mock_pyxel = MagicMock()
# Keyboard constants (must match test_input.py mock values)
mock_pyxel.KEY_LEFT = 0
mock_pyxel.KEY_A = 1
mock_pyxel.KEY_RIGHT = 2
mock_pyxel.KEY_D = 3
mock_pyxel.KEY_UP = 4
mock_pyxel.KEY_W = 5
mock_pyxel.KEY_DOWN = 6
mock_pyxel.KEY_S = 7
mock_pyxel.KEY_SPACE = 8
mock_pyxel.KEY_Z = 9
mock_pyxel.KEY_J = 10
mock_pyxel.KEY_V = 11
mock_pyxel.KEY_K = 12
# Gamepad constants
mock_pyxel.GAMEPAD1_BUTTON_DPAD_LEFT = 100
mock_pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT = 101
mock_pyxel.GAMEPAD1_BUTTON_DPAD_UP = 102
mock_pyxel.GAMEPAD1_BUTTON_DPAD_DOWN = 103
mock_pyxel.GAMEPAD1_BUTTON_A = 104
mock_pyxel.GAMEPAD1_BUTTON_B = 105
mock_pyxel.GAMEPAD1_BUTTON_X = 106

sys.modules["pyxel"] = mock_pyxel

from src.core.input import _ACTION_MAP  # noqa: E402


class TestGamepadMapping:
    """All 7 game actions must have gamepad bindings."""

    def test_dpad_left(self):
        assert mock_pyxel.GAMEPAD1_BUTTON_DPAD_LEFT in _ACTION_MAP["left"]

    def test_dpad_right(self):
        assert mock_pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT in _ACTION_MAP["right"]

    def test_dpad_up(self):
        assert mock_pyxel.GAMEPAD1_BUTTON_DPAD_UP in _ACTION_MAP["up"]

    def test_dpad_down(self):
        assert mock_pyxel.GAMEPAD1_BUTTON_DPAD_DOWN in _ACTION_MAP["down"]

    def test_button_a_jump(self):
        """A (bottom) = Jump per D-04."""
        assert mock_pyxel.GAMEPAD1_BUTTON_A in _ACTION_MAP["jump"]

    def test_button_b_spit(self):
        """B (right) = Spit per D-04."""
        assert mock_pyxel.GAMEPAD1_BUTTON_B in _ACTION_MAP["spit"]

    def test_button_x_dash(self):
        """X (left) = Dash per D-04."""
        assert mock_pyxel.GAMEPAD1_BUTTON_X in _ACTION_MAP["dash"]


class TestKeyboardPreserved:
    """Existing keyboard bindings must remain unchanged."""

    def test_left_keys(self):
        assert mock_pyxel.KEY_LEFT in _ACTION_MAP["left"]
        assert mock_pyxel.KEY_A in _ACTION_MAP["left"]

    def test_right_keys(self):
        assert mock_pyxel.KEY_RIGHT in _ACTION_MAP["right"]
        assert mock_pyxel.KEY_D in _ACTION_MAP["right"]

    def test_up_keys(self):
        assert mock_pyxel.KEY_UP in _ACTION_MAP["up"]
        assert mock_pyxel.KEY_W in _ACTION_MAP["up"]

    def test_down_keys(self):
        assert mock_pyxel.KEY_DOWN in _ACTION_MAP["down"]
        assert mock_pyxel.KEY_S in _ACTION_MAP["down"]

    def test_jump_key(self):
        assert mock_pyxel.KEY_SPACE in _ACTION_MAP["jump"]

    def test_spit_keys(self):
        assert mock_pyxel.KEY_Z in _ACTION_MAP["spit"]
        assert mock_pyxel.KEY_J in _ACTION_MAP["spit"]

    def test_dash_keys(self):
        assert mock_pyxel.KEY_V in _ACTION_MAP["dash"]
        assert mock_pyxel.KEY_K in _ACTION_MAP["dash"]
