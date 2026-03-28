import pytest
from unittest.mock import MagicMock
import sys

# Mock pyxel globally before importing input module
mock_pyxel = MagicMock()
# Define key constants that _ACTION_MAP references at import time
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
sys.modules["pyxel"] = mock_pyxel

import src.core.input as input_manager


@pytest.fixture(autouse=True)
def reset_state():
    """Reset input module state and mock before each test."""
    # Ensure input_manager uses THIS test file's mock (not one from another test)
    import src.core.input as _inp
    _inp.pyxel = mock_pyxel
    # Rebuild _ACTION_MAP with this mock's key constants
    _inp._ACTION_MAP = {
        "left":   [mock_pyxel.KEY_LEFT, mock_pyxel.KEY_A],
        "right":  [mock_pyxel.KEY_RIGHT, mock_pyxel.KEY_D],
        "up":     [mock_pyxel.KEY_UP, mock_pyxel.KEY_W],
        "down":   [mock_pyxel.KEY_DOWN, mock_pyxel.KEY_S],
        "jump":   [mock_pyxel.KEY_SPACE],
        "spit":   [mock_pyxel.KEY_Z, mock_pyxel.KEY_J],
        "dash":   [mock_pyxel.KEY_V, mock_pyxel.KEY_K],
    }
    input_manager._hold_frames.clear()
    input_manager._prev_hold_frames.clear()
    mock_pyxel.btn.reset_mock()
    mock_pyxel.btnp.reset_mock()
    mock_pyxel.btnr.reset_mock()
    mock_pyxel.btn.side_effect = None
    mock_pyxel.btnp.side_effect = None
    mock_pyxel.btnr.side_effect = None
    mock_pyxel.btn.return_value = False
    mock_pyxel.btnp.return_value = False
    mock_pyxel.btnr.return_value = False
    yield


def test_btn_primary_key():
    """Primary key (KEY_LEFT) triggers btn('left')."""
    mock_pyxel.btn.side_effect = lambda k: k == mock_pyxel.KEY_LEFT
    assert input_manager.btn("left") is True


def test_btn_secondary_key():
    """Secondary key (KEY_A) also triggers btn('left')."""
    mock_pyxel.btn.side_effect = lambda k: k == mock_pyxel.KEY_A
    assert input_manager.btn("left") is True


def test_btnp_primary():
    """Primary key (KEY_Z) triggers btnp('spit')."""
    mock_pyxel.btnp.side_effect = lambda k, **kw: k == mock_pyxel.KEY_Z
    assert input_manager.btnp("spit") is True


def test_btnp_secondary():
    """Secondary key (KEY_J) triggers btnp('spit')."""
    mock_pyxel.btnp.side_effect = lambda k, **kw: k == mock_pyxel.KEY_J
    assert input_manager.btnp("spit") is True


def test_btnr_primary():
    """Primary key (KEY_SPACE) triggers btnr('jump')."""
    mock_pyxel.btnr.side_effect = lambda k: k == mock_pyxel.KEY_SPACE
    assert input_manager.btnr("jump") is True


def test_hold_frames_increments():
    """hold_frames increments each frame while the key is held."""
    mock_pyxel.btn.side_effect = lambda k: k == mock_pyxel.KEY_LEFT
    for i in range(5):
        input_manager.update()
        assert input_manager.hold_frames("left") == i + 1


def test_hold_frames_resets_on_release():
    """hold_frames resets to 0 when key is released."""
    # Hold for 3 frames
    mock_pyxel.btn.side_effect = lambda k: k == mock_pyxel.KEY_LEFT
    for _ in range(3):
        input_manager.update()
    assert input_manager.hold_frames("left") == 3

    # Release
    mock_pyxel.btn.return_value = False
    mock_pyxel.btn.side_effect = None
    input_manager.update()
    assert input_manager.hold_frames("left") == 0


TAP_THRESHOLD = 5  # Named constant for tap detection threshold in tests


def test_was_tap_true_under_threshold():
    """was_tap returns True when held for fewer frames than threshold."""
    hold_count = 3
    # Hold for hold_count frames
    mock_pyxel.btn.side_effect = lambda k: k == mock_pyxel.KEY_LEFT
    mock_pyxel.btnr.return_value = False
    for _ in range(hold_count):
        input_manager.update()

    # Release frame: update first (resets hold to 0), then check was_tap
    mock_pyxel.btn.return_value = False
    mock_pyxel.btn.side_effect = None
    input_manager.update()

    # Now btnr fires on the release frame
    mock_pyxel.btnr.side_effect = lambda k: k == mock_pyxel.KEY_LEFT
    assert input_manager.was_tap("left", TAP_THRESHOLD) is True


def test_was_tap_false_over_threshold():
    """was_tap returns False when held for more frames than threshold."""
    hold_count = 10
    # Hold for hold_count frames
    mock_pyxel.btn.side_effect = lambda k: k == mock_pyxel.KEY_LEFT
    mock_pyxel.btnr.return_value = False
    for _ in range(hold_count):
        input_manager.update()

    # Release frame
    mock_pyxel.btn.return_value = False
    mock_pyxel.btn.side_effect = None
    input_manager.update()

    mock_pyxel.btnr.side_effect = lambda k: k == mock_pyxel.KEY_LEFT
    assert input_manager.was_tap("left", TAP_THRESHOLD) is False


def test_action_map_has_all_keys():
    """_ACTION_MAP contains all expected action names."""
    expected_actions = {"left", "right", "up", "down", "jump", "spit", "dash"}
    assert set(input_manager._ACTION_MAP.keys()) == expected_actions
