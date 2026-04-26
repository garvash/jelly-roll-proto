import pyxel

# Logical action -> list of physical keys (D-09: WASD+JK secondary mapping)
_ACTION_MAP = {
    "left":   [pyxel.KEY_LEFT, pyxel.KEY_A, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT],
    "right":  [pyxel.KEY_RIGHT, pyxel.KEY_D, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT],
    "up":     [pyxel.KEY_UP, pyxel.KEY_W, pyxel.GAMEPAD1_BUTTON_DPAD_UP],
    "down":   [pyxel.KEY_DOWN, pyxel.KEY_S, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN],
    "jump":   [pyxel.KEY_SPACE, pyxel.GAMEPAD1_BUTTON_A],
    "spit":   [pyxel.KEY_Z, pyxel.KEY_J, pyxel.GAMEPAD1_BUTTON_B],
    "pause":  [pyxel.KEY_ESCAPE, pyxel.GAMEPAD1_BUTTON_START],
    "confirm": [pyxel.KEY_Z, pyxel.KEY_RETURN, pyxel.GAMEPAD1_BUTTON_A],
}

# Hold duration tracking (frame counts per action)
_hold_frames = {}
_prev_hold_frames = {}


def btn(action):
    """Check if any mapped key for the action is currently held."""
    return any(pyxel.btn(k) for k in _ACTION_MAP[action])


def btnp(action, hold=None, repeat=None):
    """Check if any mapped key for the action was just pressed."""
    kwargs = {}
    if hold is not None:
        kwargs["hold"] = hold
    if repeat is not None:
        kwargs["repeat"] = repeat
    return any(pyxel.btnp(k, **kwargs) for k in _ACTION_MAP[action])


def btnr(action):
    """Check if any mapped key for the action was just released."""
    return any(pyxel.btnr(k) for k in _ACTION_MAP[action])


def update():
    """Update hold duration tracking. Must be called once per frame BEFORE any input checks."""
    global _prev_hold_frames
    _prev_hold_frames = dict(_hold_frames)
    for action, keys in _ACTION_MAP.items():
        if any(pyxel.btn(k) for k in keys):
            _hold_frames[action] = _hold_frames.get(action, 0) + 1
        else:
            _hold_frames[action] = 0


def hold_frames(action):
    """Return the number of consecutive frames the action has been held."""
    return _hold_frames.get(action, 0)


def was_tap(action, threshold):
    """Check if the action was just released after being held for <= threshold frames."""
    if any(pyxel.btnr(k) for k in _ACTION_MAP[action]):
        prev = _prev_hold_frames.get(action, 0)
        return 0 < prev <= threshold
    return False
