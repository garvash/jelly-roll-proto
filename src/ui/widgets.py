"""Interactive widget classes for the live-tuning panel overlay.

Provides Slider, BoolToggle, CollapsibleGroup, and TabBar widgets that
render with Pyxel primitives and interact via mouse/keyboard input.
All layout values match the Phase 28 UI-SPEC pixel-exact contract.
"""

import math

import pyxel

from src.core import tuning

# ---------------------------------------------------------------------------
# Screen layout (UI-SPEC Layout Contract)
# ---------------------------------------------------------------------------
SCREEN_W = 320
SCREEN_H = 192
TAB_BAR_H = 12       # md spacing -- tab bar height
HEADER_H = 12        # md spacing -- header bar height
CONTENT_H = 156      # 192 - 12 - 12 - 12 = 156px content area
FOOTER_H = 12        # md spacing -- footer bar height
CONTENT_Y = TAB_BAR_H + HEADER_H  # 24px from top

# ---------------------------------------------------------------------------
# Slider row layout (UI-SPEC: 8px rows, 320px wide)
# Pixel math: 4 + 48 + 4 + 176 + 4 + 44 + 4 + 12 + 24 = 320px
# ---------------------------------------------------------------------------
ROW_H = 8             # sm spacing -- slider row height
LABEL_X = 4           # xs spacing -- left padding
LABEL_W = 48          # 12 chars * 4px per char
TRACK_X = 56          # LABEL_X + LABEL_W + 4px gap
TRACK_W = 176         # slider track width
VALUE_X = 236         # TRACK_X + TRACK_W + 4px gap
VALUE_W = 44          # 11 chars * 4px per char
RESET_X = 284         # VALUE_X + VALUE_W + 4px gap
RESET_W = 12          # reset arrow hit area

# ---------------------------------------------------------------------------
# Sub-group header
# ---------------------------------------------------------------------------
SUBGROUP_H = 12       # md spacing -- collapsible header height

# ---------------------------------------------------------------------------
# Palette colors (from UI-SPEC Color section)
# ---------------------------------------------------------------------------
BG_COLOR = 1              # Dark navy panel background
CONTENT_BG = 0            # Black content/track background
TAB_ACTIVE_BG = 5         # Dark grey
TAB_INACTIVE_BG = 1       # Dark navy
SUBGROUP_BG = 2           # Dark purple
TEXT_COLOR = 7             # White
TEXT_INACTIVE = 13         # Light grey
TEXT_SUBGROUP = 6          # Light blue
TEXT_STATUS = 10           # Yellow
TRACK_BELOW_COLOR = 5     # Dark grey -- below baseline
TRACK_ABOVE_COLOR = 8     # Red -- above baseline
BASELINE_TICK_COLOR = 13   # Light grey tick
HANDLE_COLOR = 7           # White handle
RESET_COLOR = 11           # Green arrow
RESET_FLASH_COLOR = 10     # Yellow flash
MODIFIED_VALUE_COLOR = 8   # Red -- value != baseline
EDIT_COLOR = 10            # Yellow -- keyboard edit mode
BOOL_ON_COLOR = 11         # Green checkbox
BOOL_OFF_COLOR = 2         # Dark purple checkbox
SAVE_BTN_BG = 3            # Dark teal
SAVE_BTN_TEXT = 7           # White
PROTECTED_WARN_COLOR = 8   # Red warning

# ---------------------------------------------------------------------------
# Log2 scale constants for slider mapping
# 0.25x .. 4x baseline range mapped via 2^(ratio*4 - 2):
#   ratio=0 -> 2^(-2)=0.25x, ratio=0.5 -> 2^0=1x, ratio=1 -> 2^2=4x
# ---------------------------------------------------------------------------
_LOG2_RANGE = 4       # exponent span (from -2 to +2)
_LOG2_OFFSET = 2      # exponent offset so center = 1x


def _value_to_ratio(value, baseline):
    """Convert a tuning value to a 0..1 track ratio using log2 scale.

    Returns 0.5 when value equals baseline (center of track).
    Clamps to [0, 1] for values outside 0.25x..4x range.
    """
    if baseline == 0:
        return 0.5
    multiplier = value / baseline
    if multiplier <= 0:
        return 0.0
    exponent = math.log2(multiplier)  # -2 at 0.25x, 0 at 1x, +2 at 4x
    ratio = (exponent + _LOG2_OFFSET) / _LOG2_RANGE
    return max(0.0, min(1.0, ratio))


def _ratio_to_value(ratio, baseline):
    """Convert a 0..1 track ratio back to a tuning value using log2 scale.

    ratio=0 -> 0.25x baseline, ratio=0.5 -> 1x baseline, ratio=1 -> 4x baseline.
    """
    multiplier = 2 ** (ratio * _LOG2_RANGE - _LOG2_OFFSET)
    return baseline * multiplier


# ===================================================================
# Slider -- continuous value with log2-scale drag, keyboard edit,
#           reset arrow, and baseline-diff track coloring
# ===================================================================
class Slider:
    """A single tuning key slider with drag, keyboard edit, and reset."""

    def __init__(self, key, is_bool=False):
        self.key = key
        self.baseline = tuning.get_baseline(key)
        self.dragging = False
        self.editing = False
        self.edit_buffer = ""
        self.flash_timer = 0

        # Type detection for snapping and widget choice
        self.is_bool = isinstance(self.baseline, bool) or is_bool
        self.is_int = isinstance(self.baseline, int) and not self.is_bool

    def update(self, x, y, scroll_y, content_top, content_bottom):
        """Process mouse/keyboard input for this slider row.

        Parameters
        ----------
        x : int
            Left edge of row (always 0 for full-width layout).
        y : int
            Absolute y position of this row in content space.
        scroll_y : int
            Current scroll offset for the active tab.
        content_top : int
            Top pixel of visible content area (CONTENT_Y).
        content_bottom : int
            Bottom pixel of visible content area (CONTENT_Y + CONTENT_H).
        """
        screen_y = y - scroll_y

        # Decrement flash timer regardless of visibility
        if self.flash_timer > 0:
            self.flash_timer -= 1

        # --- Keyboard edit mode (active regardless of visibility) ---
        if self.editing:
            self._handle_keyboard_edit()
            return

        # Skip input if row is outside visible content area
        if screen_y + ROW_H < content_top or screen_y > content_bottom:
            self.dragging = False
            return

        my = pyxel.mouse_y
        mx = pyxel.mouse_x

        # Only process clicks within content bounds
        if my < content_top or my >= content_bottom:
            return

        row_hit = screen_y <= my < screen_y + ROW_H

        # 1. Track area -- drag interaction
        if self.dragging:
            if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                self._apply_drag(mx)
            else:
                self.dragging = False
        elif row_hit and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if TRACK_X <= mx < TRACK_X + TRACK_W:
                self.dragging = True
                self._apply_drag(mx)
            # 2. Value area -- enter keyboard edit mode
            elif VALUE_X <= mx < VALUE_X + VALUE_W:
                self.editing = True
                self.edit_buffer = ""
            # 3. Reset area -- reset to baseline
            elif RESET_X <= mx < RESET_X + RESET_W:
                tuning.reset(self.key)
                self.flash_timer = 6  # 6-frame yellow flash

    def _apply_drag(self, mx):
        """Map mouse x position to a tuning value via log2 scale."""
        ratio = (mx - TRACK_X) / TRACK_W
        ratio = max(0.0, min(1.0, ratio))
        new_val = _ratio_to_value(ratio, self.baseline)
        if self.is_int:
            new_val = round(new_val)
        tuning.set_value(self.key, new_val)

    def _handle_keyboard_edit(self):
        """Process keyboard input while in edit mode."""
        # Read typed characters from pyxel.input_text
        for ch in pyxel.input_text:
            if ch in "0123456789.-":
                self.edit_buffer += ch

        # Enter -- commit value
        if pyxel.btnp(pyxel.KEY_RETURN):
            self._commit_edit()
            return

        # Escape -- cancel edit
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.editing = False
            self.edit_buffer = ""
            return

        # Backspace -- delete last char
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.edit_buffer = self.edit_buffer[:-1]

    def _commit_edit(self):
        """Parse edit buffer and apply value, with T-28-02 clamping."""
        self.editing = False
        if not self.edit_buffer:
            return
        try:
            parsed = float(self.edit_buffer)
        except ValueError:
            # T-28-02: reject silently on parse failure
            return
        # Clamp to [0.25x, 4x] baseline range (T-28-02)
        if self.baseline != 0:
            low = self.baseline * 0.25
            high = self.baseline * 4.0
            # Handle negative baselines where low > high
            if low > high:
                low, high = high, low
            parsed = max(low, min(high, parsed))
        if self.is_int:
            parsed = round(parsed)
        tuning.set_value(self.key, parsed)

    def draw(self, x, y, scroll_y, content_top, content_bottom):
        """Render this slider row. Clips to content area bounds."""
        screen_y = y - scroll_y

        # Skip draw if completely outside visible area
        if screen_y + ROW_H < content_top or screen_y > content_bottom:
            return

        current = getattr(tuning, self.key)

        # 1. Label -- truncated key name, left-aligned, max 12 chars
        label = self.key[:12]
        pyxel.text(LABEL_X, screen_y + 1, label, TEXT_COLOR)

        # 2. Track background
        pyxel.rect(TRACK_X, screen_y + 2, TRACK_W, 3, CONTENT_BG)

        # Compute handle position and baseline tick position
        baseline_x = TRACK_X + TRACK_W // 2  # baseline at center (ratio=0.5)
        handle_ratio = _value_to_ratio(current, self.baseline)
        handle_x = TRACK_X + int(handle_ratio * TRACK_W)
        handle_x = max(TRACK_X, min(TRACK_X + TRACK_W - 1, handle_x))

        # Track fill: below or above baseline
        if handle_x < baseline_x:
            fill_w = baseline_x - handle_x
            if fill_w > 0:
                pyxel.rect(handle_x, screen_y + 2, fill_w, 3, TRACK_BELOW_COLOR)
        elif handle_x > baseline_x:
            fill_w = handle_x - baseline_x
            if fill_w > 0:
                pyxel.rect(baseline_x, screen_y + 2, fill_w, 3, TRACK_ABOVE_COLOR)

        # Baseline tick mark -- 1px wide, 5px tall, centered on track
        pyxel.rect(baseline_x, screen_y + 1, 1, 5, BASELINE_TICK_COLOR)

        # Handle -- 3px wide, full row height
        pyxel.rect(handle_x - 1, screen_y, 3, ROW_H, HANDLE_COLOR)

        # 3. Value readout
        if self.editing:
            # Show edit buffer with cursor indicator
            display = self.edit_buffer + "_"
            pyxel.text(VALUE_X, screen_y + 1, display[:11], EDIT_COLOR)
        else:
            val_str = _format_value(current)
            val_color = MODIFIED_VALUE_COLOR if current != self.baseline else TEXT_COLOR
            pyxel.text(VALUE_X, screen_y + 1, val_str[:11], val_color)

        # 4. Reset arrow "<"
        arrow_color = RESET_FLASH_COLOR if self.flash_timer > 0 else RESET_COLOR
        pyxel.text(RESET_X, screen_y + 1, "<", arrow_color)


def _format_value(value):
    """Format a tuning value for display. Max 11 chars."""
    if isinstance(value, bool):
        return "ON" if value else "OFF"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        # Show up to 4 decimal places, strip trailing zeros
        formatted = f"{value:.4f}".rstrip("0").rstrip(".")
        return formatted
    return str(value)[:11]


# ===================================================================
# BoolToggle -- checkbox widget for boolean tuning values
# ===================================================================
class BoolToggle:
    """Toggle checkbox for boolean tuning keys like RAM_INVINCIBLE."""

    def __init__(self, key):
        self.key = key
        self.baseline = tuning.get_baseline(key)
        self.dragging = False   # Unused, kept for interface compatibility
        self.editing = False    # Unused, kept for interface compatibility
        self.flash_timer = 0

    def update(self, x, y, scroll_y, content_top, content_bottom):
        """Process click to toggle boolean value."""
        screen_y = y - scroll_y

        if self.flash_timer > 0:
            self.flash_timer -= 1

        if screen_y + ROW_H < content_top or screen_y > content_bottom:
            return

        my = pyxel.mouse_y
        mx = pyxel.mouse_x

        if my < content_top or my >= content_bottom:
            return

        row_hit = screen_y <= my < screen_y + ROW_H
        if not row_hit or not pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            return

        # Click on track area toggles the value
        if TRACK_X <= mx < TRACK_X + TRACK_W:
            current = getattr(tuning, self.key)
            tuning.set_value(self.key, not current)
        # Click on reset area resets to baseline
        elif RESET_X <= mx < RESET_X + RESET_W:
            tuning.reset(self.key)
            self.flash_timer = 6

    def draw(self, x, y, scroll_y, content_top, content_bottom):
        """Render boolean toggle as a checkbox."""
        screen_y = y - scroll_y

        if screen_y + ROW_H < content_top or screen_y > content_bottom:
            return

        current = getattr(tuning, self.key)

        # Label
        label = self.key[:12]
        pyxel.text(LABEL_X, screen_y + 1, label, TEXT_COLOR)

        # Checkbox -- 6x6 filled rect in track area
        CHECKBOX_SIZE = 6  # px square
        checkbox_x = TRACK_X + 2
        checkbox_y = screen_y + 1
        box_color = BOOL_ON_COLOR if current else BOOL_OFF_COLOR
        pyxel.rect(checkbox_x, checkbox_y, CHECKBOX_SIZE, CHECKBOX_SIZE, box_color)

        # Value text
        val_str = "ON" if current else "OFF"
        val_color = MODIFIED_VALUE_COLOR if current != self.baseline else TEXT_COLOR
        pyxel.text(VALUE_X, screen_y + 1, val_str, val_color)

        # Reset arrow
        arrow_color = RESET_FLASH_COLOR if self.flash_timer > 0 else RESET_COLOR
        pyxel.text(RESET_X, screen_y + 1, "<", arrow_color)


# ===================================================================
# CollapsibleGroup -- expandable/collapsible sub-group of sliders
# ===================================================================
class CollapsibleGroup:
    """A collapsible section header with child Slider/BoolToggle widgets."""

    def __init__(self, name, sliders, expanded=True):
        self.name = name
        self.sliders = sliders
        self.expanded = expanded

    def update(self, x, y, scroll_y, content_top, content_bottom):
        """Handle header click to toggle and delegate to children."""
        screen_y = y - scroll_y

        # Header click detection
        if content_top <= screen_y < content_bottom:
            my = pyxel.mouse_y
            if (content_top <= my < content_bottom
                    and screen_y <= my < screen_y + SUBGROUP_H
                    and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)):
                self.expanded = not self.expanded

        # Update children if expanded
        if self.expanded:
            child_y = y + SUBGROUP_H
            for slider in self.sliders:
                slider.update(x, child_y, scroll_y, content_top, content_bottom)
                child_y += ROW_H

    def draw(self, x, y, scroll_y, content_top, content_bottom):
        """Draw group header and children if expanded."""
        screen_y = y - scroll_y

        # Draw header if visible
        if screen_y + SUBGROUP_H >= content_top and screen_y < content_bottom:
            pyxel.rect(0, screen_y, SCREEN_W, SUBGROUP_H, SUBGROUP_BG)
            glyph = "v" if self.expanded else ">"
            pyxel.text(x + 4, screen_y + 3, glyph, TEXT_SUBGROUP)
            pyxel.text(x + 12, screen_y + 3, self.name, TEXT_SUBGROUP)

        # Draw children if expanded
        if self.expanded:
            child_y = y + SUBGROUP_H
            for slider in self.sliders:
                slider.draw(x, child_y, scroll_y, content_top, content_bottom)
                child_y += ROW_H

    def height(self):
        """Return total height in pixels (header + visible children)."""
        return SUBGROUP_H + (len(self.sliders) * ROW_H if self.expanded else 0)


# ===================================================================
# TabBar -- horizontal tab selector with 4 equal-width tabs
# ===================================================================
class TabBar:
    """Horizontal tab bar with equal-width clickable tabs."""

    TAB_WIDTH = 80  # 320px / 4 tabs = 80px per tab

    def __init__(self, tab_names):
        self.tab_names = tab_names
        self.active = 0

    def update(self, y_offset=0):
        """Handle tab click. Returns True if active tab changed."""
        if not pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            return False
        if pyxel.mouse_y < y_offset or pyxel.mouse_y >= y_offset + TAB_BAR_H:
            return False
        idx = pyxel.mouse_x // self.TAB_WIDTH
        if 0 <= idx < len(self.tab_names) and idx != self.active:
            self.active = idx
            return True
        return False

    def draw(self, y_offset=0):
        """Draw all tabs. Active tab uses palette 5, inactive palette 1."""
        for i, name in enumerate(self.tab_names):
            tx = i * self.TAB_WIDTH
            bg = TAB_ACTIVE_BG if i == self.active else TAB_INACTIVE_BG
            text_col = TEXT_COLOR if i == self.active else TEXT_INACTIVE
            pyxel.rect(tx, y_offset, self.TAB_WIDTH, TAB_BAR_H, bg)
            # Center text within tab
            text_w = len(name) * 4  # 4px per char
            text_x = tx + (self.TAB_WIDTH - text_w) // 2
            text_y = y_offset + (TAB_BAR_H - 6) // 2
            pyxel.text(text_x, text_y, name, text_col)
