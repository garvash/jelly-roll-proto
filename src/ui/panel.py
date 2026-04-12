"""Live-tuning panel overlay -- F1 toggle, tab navigation, slider interaction.

Follows the same update()/draw() contract as src/core/overlays.py.
Draws in SCREEN SPACE (after camera reset), covering the full 320x192 display.
The game renders underneath each frame but the panel covers it with a solid
dark navy background (Pyxel has no alpha blending).

Phase 28 Plan 01: Core panel module with widgets, tabs, scroll, input gating.
Phase 28 Plan 02: Preset load/save, journal wiring, slow-mo toggle.
"""

import pyxel

from src.core import tuning
from src.ui.widgets import (
    Slider, BoolToggle, CollapsibleGroup, TabBar,
    SCREEN_W, SCREEN_H, TAB_BAR_H, HEADER_H, CONTENT_H, FOOTER_H,
    CONTENT_Y, ROW_H, SUBGROUP_H, BG_COLOR, CONTENT_BG,
    TEXT_COLOR, TEXT_STATUS, TEXT_INACTIVE,
    SAVE_BTN_BG, SAVE_BTN_TEXT, PROTECTED_WARN_COLOR,
)

# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------
show_panel = False          # F1 toggle (D-01)
_tabs = None                # TabBar instance
_tab_content = None         # dict: tab_index -> list of CollapsibleGroup
_scroll_y = [0, 0, 0, 0]   # Per-tab scroll offset
_initialized = False        # Lazy init guard

# Input gating / preset state
_active_preset_slot = 0     # 0 = no preset loaded ("custom")
_active_preset_alias = "custom"

# Save button state
_save_callback = None       # Set by presets module (Plan 02)
_confirm_timer = 0          # 120-frame confirmation window for protected slot
_CONFIRM_DURATION = 120     # frames for baseline overwrite confirmation

# Error display
_error_msg = ""             # Transient error text for header
_error_timer = 0            # Frames remaining to show error

# ---------------------------------------------------------------------------
# Feel-relevant groups -- only these appear in the panel (D-03)
# 12 groups total across 4 tabs
# ---------------------------------------------------------------------------
FEEL_GROUPS = {
    "movement", "dash", "forgiving", "wall",
    "slime_follow", "slime_juice", "projectile",
    "drill", "fusion", "slime_ram", "charge_shot", "boost",
}

# Movement keys that belong in the Jump tab instead of Move tab
JUMP_TAB_MOVEMENT_KEYS = {
    "GRAVITY", "MAX_FALL_SPEED", "JUMP_FORCE",
    "VARIABLE_JUMP_REDUCTION", "FALLING_GRAVITY_MULTIPLIER",
}

# Tab definitions: (tab_name, {group_name: key_filter_or_None, ...})
# None filter = include all keys from group
# lambda filter = include only keys where lambda returns True
TAB_DEFS = [
    ("Move",  {"movement": lambda k: k not in JUMP_TAB_MOVEMENT_KEYS, "dash": None}),
    ("Jump",  {"movement": lambda k: k in JUMP_TAB_MOVEMENT_KEYS, "forgiving": None, "wall": None}),
    ("Slime", {"slime_follow": None, "slime_juice": None, "projectile": None}),
    ("Fuse",  {"drill": None, "fusion": None, "slime_ram": None, "charge_shot": None, "boost": None}),
]

# Save button layout
_SAVE_BTN_W = 40            # px width
_SAVE_BTN_X = SCREEN_W - _SAVE_BTN_W - 4  # right-aligned with 4px margin


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------
def _init_panel():
    """Build tab bar and slider content from tuning._flat_index.

    Called once on first update(). Groups keys by their schema group,
    creates Slider or BoolToggle per key, wraps in CollapsibleGroups,
    assigns to tab_content dict.
    """
    global _tabs, _tab_content, _initialized

    tab_names = [td[0] for td in TAB_DEFS]
    _tabs = TabBar(tab_names)
    _tab_content = {}

    for tab_idx, (tab_name, group_filters) in enumerate(TAB_DEFS):
        groups_list = []

        for group_name, key_filter in group_filters.items():
            # Collect keys belonging to this group
            keys_in_group = []
            for flat_key, grp in tuning._flat_index.items():
                if grp != group_name:
                    continue
                if key_filter is not None and not key_filter(flat_key):
                    continue
                keys_in_group.append(flat_key)

            if not keys_in_group:
                continue

            # Sort keys alphabetically for stable ordering
            keys_in_group.sort()

            # Create widget for each key
            sliders = []
            for key in keys_in_group:
                baseline = tuning.get_baseline(key)
                if isinstance(baseline, bool):
                    sliders.append(BoolToggle(key))
                else:
                    sliders.append(Slider(key))

            # Fuse tab: only first group ("drill") expanded by default
            if tab_name == "Fuse":
                expanded = (group_name == "drill")
            else:
                expanded = True

            groups_list.append(CollapsibleGroup(group_name, sliders, expanded=expanded))

        _tab_content[tab_idx] = groups_list

    _initialized = True


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def is_editing():
    """Return True if any slider in the active tab is in keyboard edit mode.

    Used by main.py to suppress game key processing during panel text entry
    (Pitfall 4 -- key conflict prevention).
    """
    if not _initialized or _tab_content is None or _tabs is None:
        return False
    active = _tabs.active
    for group in _tab_content.get(active, []):
        for slider in group.sliders:
            if slider.editing:
                return True
    return False


def set_active_preset(slot, alias):
    """Update active preset display. Called by presets module (Plan 02)."""
    global _active_preset_slot, _active_preset_alias
    _active_preset_slot = slot
    _active_preset_alias = alias


def get_active_preset_slot():
    """Return active preset slot number. Called by presets module for save."""
    return _active_preset_slot


def set_error(msg, duration=120):
    """Show a transient error message in the header bar."""
    global _error_msg, _error_timer
    _error_msg = msg
    _error_timer = duration


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------
def update():
    """Process panel input. Called from Game.update() after overlays.update().

    Handles F1 toggle, tab switching, scroll, and delegates to widget updates.
    """
    global show_panel, _confirm_timer, _error_timer

    # F1 toggle
    if pyxel.btnp(pyxel.KEY_F1):
        show_panel = not show_panel
        pyxel.mouse(show_panel)

    if not show_panel:
        return

    # Lazy init on first open
    if not _initialized:
        _init_panel()

    # Decrement timers
    if _confirm_timer > 0:
        _confirm_timer -= 1
    if _error_timer > 0:
        _error_timer -= 1

    # If editing a slider value, suppress all other key processing
    if is_editing():
        _update_active_tab_widgets()
        return

    # Tab bar click handling
    tab_changed = _tabs.update()
    if tab_changed:
        _scroll_y[_tabs.active] = 0

    # Header: save button click
    _handle_save_click()

    # Mouse wheel scroll within content area
    active = _tabs.active
    wheel = pyxel.mouse_wheel
    if wheel != 0 and CONTENT_Y <= pyxel.mouse_y < CONTENT_Y + CONTENT_H:
        _scroll_y[active] -= wheel * 8  # 8px per notch (UI-SPEC)
        max_scroll = _total_content_height(active) - CONTENT_H
        max_scroll = max(0, max_scroll)
        _scroll_y[active] = max(0, min(_scroll_y[active], max_scroll))

    # Update widgets in active tab
    _update_active_tab_widgets()


def _update_active_tab_widgets():
    """Delegate update to all CollapsibleGroups in the active tab."""
    active = _tabs.active
    content_top = CONTENT_Y
    content_bottom = CONTENT_Y + CONTENT_H
    scroll = _scroll_y[active]

    y = CONTENT_Y  # absolute y in content space (before scroll)
    for group in _tab_content.get(active, []):
        group.update(0, y, scroll - CONTENT_Y, content_top, content_bottom)
        y += group.height()


def _total_content_height(tab_idx):
    """Calculate total height of all groups in a tab."""
    total = 0
    for group in _tab_content.get(tab_idx, []):
        total += group.height()
    return total


def _handle_save_click():
    """Handle save button interaction with baseline protection (D-14)."""
    global _confirm_timer

    my = pyxel.mouse_y
    mx = pyxel.mouse_x

    # Save button is in the header bar area
    if not pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
        return
    if not (TAB_BAR_H <= my < TAB_BAR_H + HEADER_H):
        return
    if not (_SAVE_BTN_X <= mx < _SAVE_BTN_X + _SAVE_BTN_W):
        return

    # Baseline slot protection (D-14)
    if _active_preset_slot == 1:
        if _confirm_timer > 0:
            # Second click within confirmation window -- proceed
            _confirm_timer = 0
            if _save_callback is not None:
                _save_callback()
        else:
            # First click on protected slot -- start confirmation
            _confirm_timer = _CONFIRM_DURATION
        return

    # Non-protected slot -- save immediately
    if _save_callback is not None:
        _save_callback()


# ---------------------------------------------------------------------------
# Draw
# ---------------------------------------------------------------------------
def draw():
    """Render the full panel overlay in screen space.

    Called after pyxel.camera() reset in main.py draw. Covers the entire
    320x192 screen with a dark navy background.
    """
    if not show_panel:
        return
    if not _initialized:
        return

    # 1. Full-screen background
    pyxel.rect(0, 0, SCREEN_W, SCREEN_H, BG_COLOR)

    # 2. Tab bar
    _tabs.draw()

    # 3. Header bar
    _draw_header()

    # 4. Content area with clipping
    pyxel.clip(0, CONTENT_Y, SCREEN_W, CONTENT_H)
    _draw_content()
    pyxel.clip()  # reset clip

    # 5. Footer bar
    _draw_footer()


def _draw_header():
    """Draw the header bar showing preset status and save button."""
    header_y = TAB_BAR_H

    # Preset status text (left side)
    if _error_timer > 0:
        # Show error message in red
        pyxel.text(4, header_y + 3, _error_msg[:40], PROTECTED_WARN_COLOR)
    elif _confirm_timer > 0:
        # Show baseline overwrite confirmation
        pyxel.text(4, header_y + 3, "Overwrite baseline? Save again",
                   PROTECTED_WARN_COLOR)
    else:
        if _active_preset_slot > 0:
            status = f"Slot {_active_preset_slot}: {_active_preset_alias}"
        else:
            status = "Slot -: custom"
        pyxel.text(4, header_y + 3, status, TEXT_STATUS)

    # Save button (right side)
    pyxel.rect(_SAVE_BTN_X, header_y, _SAVE_BTN_W, HEADER_H, SAVE_BTN_BG)
    if _active_preset_slot > 0:
        btn_text = f"Save {_active_preset_slot}"
    else:
        btn_text = "Save -"
    # Center text in button
    text_w = len(btn_text) * 4  # 4px per char
    text_x = _SAVE_BTN_X + (_SAVE_BTN_W - text_w) // 2
    pyxel.text(text_x, header_y + 3, btn_text, SAVE_BTN_TEXT)


def _draw_content():
    """Draw all CollapsibleGroups in the active tab with scroll offset."""
    active = _tabs.active
    content_top = CONTENT_Y
    content_bottom = CONTENT_Y + CONTENT_H
    scroll = _scroll_y[active]

    y = CONTENT_Y  # absolute y in content space
    for group in _tab_content.get(active, []):
        group.draw(0, y, scroll - CONTENT_Y, content_top, content_bottom)
        y += group.height()


def _draw_footer():
    """Draw the footer bar with preset hints and slow-mo indicator."""
    footer_y = SCREEN_H - FOOTER_H

    # Background fill for footer
    pyxel.rect(0, footer_y, SCREEN_W, FOOTER_H, BG_COLOR)

    # Preset hints (left-aligned)
    hints = "[1] v1.3  [2] tight  [3] floaty"
    pyxel.text(4, footer_y + 3, hints, TEXT_INACTIVE)

    # Slow-mo indicator (right-aligned)
    slow_text = "SLOW" if pyxel.btn(pyxel.KEY_TAB) else "Tab=slow"
    slow_color = TEXT_STATUS if pyxel.btn(pyxel.KEY_TAB) else TEXT_INACTIVE
    slow_w = len(slow_text) * 4
    pyxel.text(SCREEN_W - slow_w - 4, footer_y + 3, slow_text, slow_color)
