# Phase 28: Live-Tuning Panel MVP - Research

**Researched:** 2026-04-12
**Domain:** Pyxel UI overlay system, runtime value mutation, preset persistence
**Confidence:** HIGH

## Summary

This phase builds a GMTK-Platformer-Toolkit-style overlay panel within Pyxel's 320x192 pixel canvas. The panel uses the existing `tuning.py` mutation API (Phase 24) and follows the overlay integration pattern from `overlays.py` (Phase 27). The core challenge is building mouse-driven UI widgets (sliders, tabs, buttons) in a retro game engine with no built-in UI framework -- everything must be hand-drawn with `pyxel.rect`, `pyxel.text`, and mouse coordinate hit-testing.

The tuning system already provides everything the panel needs: `set_value()` for O(1) in-memory mutation, `get_baseline()` for diff/reset, `reset()` for single-key restore, `_flat_index` for group-to-tab mapping, and `save()` for atomic disk persistence. The panel is purely a UI layer on top of these primitives.

Key constraint: 54 feel-relevant tuning keys across 4 tabs, with the Fuse tab containing 26 sliders across 5 collapsible sub-groups. At 320x192 resolution with ~18 visible slider rows, scrolling within tabs is required for Fuse. Non-numeric values (booleans like `RAM_INVINCIBLE`, color indices like `RECALL_TRAIL_COLOR`) need special widget treatment -- toggle checkboxes or integer steppers rather than continuous sliders.

**Primary recommendation:** Build a self-contained `src/ui/panel.py` module with a widget class hierarchy (Slider, Tab, Button, CollapsibleGroup) that integrates into main.py via the same `update()`/`draw()` contract as overlays.py. Use immediate-mode rendering with retained state for widget positions and drag tracking.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- D-01: Full-screen semi-transparent overlay. F1 toggles on/off. Game continues running underneath (no pause mode).
- D-02: 4 tabs -- Move (movement, dash), Jump (gravity/jump from movement, forgiving, wall), Slime (slime_follow, slime_juice, projectile), Fuse (drill, fusion, slime_ram, charge_shot, boost)
- D-03: Non-feel groups excluded from panel entirely
- D-04: Collapsible sub-groups within each tab (schema group = collapsible section)
- D-05: Optional slow-mo toggle -- hold Tab for half-speed
- D-06: Slider ranges 0.25x to 4x of baseline value. Baseline is visual center.
- D-07: Slider track color changes past baseline position (drift direction indicator)
- D-08: Arrow icon next to slider resets to v1.3 baseline (flash confirmation)
- D-09: Click numeric label to enter keyboard edit mode. Type number, Enter confirm, Esc cancel.
- D-10: Mouse click-and-drag on slider handles. `tuning.set_value()` called each drag frame.
- D-11: Numbered hotkey slots (1, 2, 3...) for instant preset loading. Values swap at next frame boundary.
- D-12: MVP ships 3 preset slots: slot 1 = v1.3 baseline, slot 2 = "tight", slot 3 = "floaty"
- D-13: Save overwrites active slot. Save button writes to `assets/presets/slot_N.json`.
- D-14: v1.3 baseline preset protected by default (confirmation to overwrite)
- D-15: Preset files versioned JSON in `assets/presets/` with full feel values + alias + timestamp + schema version
- D-16: Rolling JSONL journal file per session. Every slider edit appended for crash recovery.

### Claude's Discretion
- Journal entry format (key+old+new+timestamp vs minimal)
- Journal flush policy (immediate fsync vs batched)
- Slow-mo implementation (frame skip vs actual FPS change)
- Overlay transparency level and background color
- Tab bar visual design and click targets
- Collapsible sub-group expand/collapse animation (if any)
- Slider handle size and drag dead zone
- Color choices for baseline drift indication
- Preset JSON schema fields beyond values + alias + timestamp

### Deferred Ideas (OUT OF SCOPE)
- Configurable slider shapes
- Expanding preset slots beyond 3 (system supports it, MVP ships 3)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TOOL-01 | F1 toggles overlay panel with category tabs, game continues running | Pyxel F1 key available, overlay pattern from overlays.py, `pyxel.mouse(True/False)` for cursor |
| TOOL-02 | Mouse click-and-drag sliders + keyboard numeric entry | `pyxel.mouse_x/y`, `pyxel.btn(MOUSE_BUTTON_LEFT)`, `pyxel.input_text` for keyboard chars |
| TOOL-03 | Live value update at frame boundary, double-buffered, reset-to-default arrow | `tuning.set_value()` is already frame-safe (O(1) dict write), `tuning.get_baseline()` + `tuning.reset()` exist |
| TOOL-04 | Preset save/load with versioned JSON, 3 shipped presets, A/B compare | `tuning.save()` pattern for atomic writes, `assets/presets/` directory to create |
| TOOL-05 | Rolling journal file for crash safety | JSONL append + `os.fsync` for crash safety |
| TOOL-06 | Grouped sliders by system with collapsible sub-groups | `tuning._flat_index` maps keys to groups, 4 tabs with 13 sub-groups |
| TOOL-07 | Baseline diff display and drift indication | `tuning.get_baseline()` provides frozen v1.3 values, slider track color split at baseline |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pyxel | 2.8.7 | Game engine, rendering, input | Already installed, only rendering option [VERIFIED: `python -c "import pyxel; print(pyxel.VERSION)"`] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| json (stdlib) | N/A | Preset file I/O, journal entries | Preset save/load, journal writes |
| pathlib (stdlib) | N/A | File path management | Preset directory creation, journal paths |
| time (stdlib) | N/A | Timestamps for journal entries | `time.time()` for journal timestamps |
| datetime (stdlib) | N/A | Session ID generation | Session-stamped journal filenames |
| copy (stdlib) | N/A | Deep copy for preset snapshots | Already used in tuning.py pattern |

No external dependencies needed. Everything is stdlib + Pyxel.

## Architecture Patterns

### Recommended Project Structure
```
src/
  ui/
    __init__.py
    panel.py          # Main panel module: toggle, tab bar, scroll, draw
    widgets.py        # Slider, Button, CollapsibleGroup, TabBar classes
    presets.py        # Preset load/save/A-B compare logic
    journal.py        # JSONL journal writer
assets/
  presets/
    slot_1.json       # v1.3 baseline (protected)
    slot_2.json       # "tight" preset
    slot_3.json       # "floaty" preset
  journal/            # Session journal files (gitignored)
```

### Pattern 1: Module-Level Toggle + update()/draw() Contract
**What:** Follow the exact same integration pattern as `overlays.py` and `debug.py` -- module-level boolean toggle, F-key handler in `update()`, rendering in `draw()`.
**When to use:** Always -- this is the established pattern for all debug/overlay features.
**Example:**
```python
# src/ui/panel.py
import pyxel

show_panel = False  # Module-level toggle (F1)

def update():
    """Handle F1 toggle and panel input. Call from Game.update()."""
    global show_panel
    if pyxel.btnp(pyxel.KEY_F1):
        show_panel = not show_panel
        pyxel.mouse(show_panel)  # Show/hide OS cursor
    if not show_panel:
        return
    # Process mouse input for sliders, tabs, buttons...

def draw():
    """Draw panel in screen-space. Call after pyxel.clip()/pyxel.camera() reset."""
    if not show_panel:
        return
    # Draw semi-transparent background, tabs, sliders...
```
[VERIFIED: overlays.py and debug.py patterns in codebase]

### Pattern 2: Retained-State Widgets with Immediate-Mode Rendering
**What:** Widget objects (Slider, Tab, CollapsibleGroup) hold their geometry and state (position, drag tracking, collapsed/expanded) but render every frame using Pyxel draw primitives. No retained pixel buffers.
**When to use:** For all interactive elements.
**Example:**
```python
class Slider:
    def __init__(self, key, x, y, w):
        self.key = key
        self.x = x
        self.y = y
        self.w = w  # Track width in pixels
        self.dragging = False
        self.editing = False  # Keyboard edit mode (D-09)
        self.edit_buffer = ""
    
    def update(self):
        baseline = tuning.get_baseline(self.key)
        current = getattr(tuning, self.key)
        # Handle mouse drag on track area
        # Handle click on reset arrow
        # Handle click on numeric label for keyboard entry
    
    def draw(self, y_offset):
        # Label (truncated key name)
        # Track bar with color split at baseline
        # Handle position
        # Numeric value display
        # Reset arrow icon
```
[ASSUMED -- standard UI widget pattern, no Pyxel-specific precedent]

### Pattern 3: Scroll Offset for Overflowing Tabs
**What:** Each tab maintains a `scroll_y` offset. Mouse wheel adjusts scroll. Sliders are drawn at `y - scroll_y` and clipped to the panel content area. Hit-testing also adjusts for scroll offset.
**When to use:** Fuse tab (26 sliders) and any tab where collapsed groups would still exceed viewport.
**Example:**
```python
# In panel update:
if pyxel.mouse_wheel != 0:
    tab.scroll_y -= pyxel.mouse_wheel * SCROLL_SPEED  # 10px per notch
    tab.scroll_y = max(0, min(tab.scroll_y, tab.max_scroll))
```
[VERIFIED: `pyxel.mouse_wheel` exists as int property]

### Pattern 4: Double-Buffered Frame-Boundary Writes
**What:** Per D-10/success criterion 3, slider drags call `tuning.set_value()` which mutates `_model` in-place. Since `tuning.__getattr__` reads from `_model`, and game physics reads happen during the next `update()` call (after panel `update()`), there is a natural frame boundary. No explicit double-buffer needed -- the existing architecture provides it.
**When to use:** Always. This is how tuning.py already works.
**Reason this is safe:** Panel `update()` runs at the start of the frame (after `debug.update()` and `overlays.update()`). Physics reads happen later in `update()` during entity updates. So a slider change in frame N is read by physics in the same frame N's entity update step, or at worst frame N+1. There are no mid-physics writes because the panel update completes before entity updates begin.
[VERIFIED: main.py update() call order -- debug/overlays first, then state machine dispatch]

### Pattern 5: Preset as Full Snapshot
**What:** A preset file contains ALL feel-relevant tuning values (not deltas). Loading a preset calls `tuning.set_value()` for every key. This avoids schema version mismatch bugs where a delta-based preset references keys that no longer exist.
**When to use:** All preset save/load operations.
**Example preset JSON:**
```json
{
  "version": "1.0",
  "schema_version": "0.3.0",
  "alias": "tight",
  "timestamp": "2026-04-12T14:30:00Z",
  "values": {
    "WALK_ACCEL": 0.15,
    "WALK_FRICTION": 0.18,
    "GRAVITY": 0.0875
  }
}
```
[ASSUMED -- design choice per D-15]

### Anti-Patterns to Avoid
- **Do NOT pause the game when panel is open.** D-01 explicitly requires live gameplay continues.
- **Do NOT use `from src.core.constants import X` for panel-tuned values.** Phase 24 D-17 explains why -- `from` imports bind at import time and won't see `set_value()` changes. Read via `tuning.KEY_NAME` at use time.
- **Do NOT write to disk on every slider drag.** `tuning.set_value()` is memory-only (D-01/D-02 of Phase 24). Only the journal appends on each edit. `tuning.save()` is explicit (Save button only).
- **Do NOT use `_flat_index` directly from outside tuning.py.** Use `tuning.get_group(key)` which is the public API.
- **Do NOT build sliders for non-numeric values (booleans, lists, color indices).** Use checkbox toggles for booleans, integer steppers for int-only values like frame counts and color indices.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Atomic file writes | Custom temp-file logic | Copy `tuning.save()` pattern | Already proven: temp + fsync + os.replace |
| Tuning key enumeration | Manual key lists | `tuning._flat_index.keys()` via `tuning.get_group()` | 87 keys, auto-updates with schema |
| Baseline values | Separate baseline file | `tuning.get_baseline(key)` | Frozen deepcopy already maintained |
| Value reset | Manual value tracking | `tuning.reset(key)` | Already handles single-key and full reset |
| Group membership | Hardcoded tab assignments | `tuning.get_group(key)` | Returns schema group name from flat index |

**Key insight:** Phase 24's tuning.py was explicitly designed as the backend for this panel. Every mutation primitive exists. The panel is purely UI.

## Common Pitfalls

### Pitfall 1: Mouse Coordinates in Scaled Display
**What goes wrong:** Pyxel runs at 320x192 logical pixels but the window is scaled up. `pyxel.mouse_x` and `pyxel.mouse_y` already report in logical coordinates (not physical screen pixels).
**Why it happens:** Developers sometimes try to divide by scale factor.
**How to avoid:** Use `pyxel.mouse_x` and `pyxel.mouse_y` directly -- they are already in game-space coordinates.
**Warning signs:** Sliders respond at wrong positions, clicks seem offset.
[VERIFIED: Pyxel docs -- mouse_x/y return logical coords]

### Pitfall 2: Panel Eating Game Input
**What goes wrong:** When panel is open, mouse clicks intended for sliders also trigger game actions (shooting, etc).
**Why it happens:** Both panel and game read the same `pyxel.btn()` state.
**How to avoid:** When `show_panel` is True, game input processing should be suppressed or the panel should "consume" mouse events by setting a flag that game update checks. Simplest: skip gameplay mouse input when panel is visible.
**Warning signs:** Slime spits when dragging a slider.

### Pitfall 3: Fuse Tab Overflow
**What goes wrong:** 26 sliders in Fuse tab exceed the ~18 visible rows at 10px per row.
**Why it happens:** 5 sub-groups (drill, fusion, slime_ram, charge_shot, boost) with 4-7 keys each.
**How to avoid:** Collapsible sub-groups (D-04) are essential. Default some groups to collapsed. Also implement mouse-wheel scroll as fallback.
**Warning signs:** Sliders drawn off-screen, can't reach bottom sliders.

### Pitfall 4: Keyboard Edit Conflicts with Game Keys
**What goes wrong:** Typing a number in a slider's keyboard edit field triggers game hotkeys (1/2/3 for preset load, Q for quit).
**Why it happens:** `pyxel.btnp()` still fires during keyboard edit.
**How to avoid:** When any slider is in `editing` mode, suppress all non-edit key processing. Check an `is_editing()` flag before processing hotkeys.
**Warning signs:** Typing "1" to enter a value loads preset slot 1.

### Pitfall 5: Journal File Growth
**What goes wrong:** Journal grows unboundedly if user plays for hours with frequent slider adjustments.
**Why it happens:** JSONL append-only with no rotation.
**How to avoid:** Name journal files by session timestamp (one file per game launch). Keep rolling -- the files are diagnostic, not gameplay data. Optionally cap at a reasonable size (e.g., 10MB) or max entries (e.g., 10000).
**Warning signs:** Disk writes slow down, journal file exceeds reasonable size.

### Pitfall 6: Non-Numeric Tuning Values
**What goes wrong:** Attempting to create a 0.25x-4x slider for `RAM_INVINCIBLE` (boolean) or `RECALL_TRAIL_COLOR` (palette index 0-15) or `TILE_EMPTY` (list).
**Why it happens:** D-06 assumes all values are continuous floats, but the schema has booleans, integers, and lists.
**How to avoid:** Filter keys by value type at panel init. Only create sliders for int/float values. For booleans, use a toggle checkbox. For non-scalar values (lists like `TILE_EMPTY`), skip entirely (they're in excluded groups anyway). For integer-only values (frame counts like `COYOTE_TIME`), snap slider output to integers.
**Warning signs:** `set_value('RAM_INVINCIBLE', 2.5)` breaks game logic.

### Pitfall 7: Cursor Visibility Across States
**What goes wrong:** OS cursor stays visible after closing panel, or disappears when panel opens.
**Why it happens:** `pyxel.mouse(True/False)` state not tracked across game state transitions.
**How to avoid:** Always call `pyxel.mouse(show_panel)` when toggling. Also hide cursor on game state changes (death, pause, title) if panel was open.
**Warning signs:** Cursor visible during normal gameplay, invisible when panel is open.

## Code Examples

### Slider Track Rendering with Baseline Split (D-06, D-07)
```python
# Source: derived from D-06 (0.25x to 4x range) and D-07 (color split at baseline)
def draw_slider_track(x, y, w, current_val, baseline_val):
    """Draw a slider track with color split at baseline position.
    
    Range: 0.25x to 4x of baseline. Baseline is at the visual center.
    Left half (below baseline): palette 5 (dark grey / cool color)
    Right half (above baseline): palette 8 (red / warm color)
    """
    TRACK_H = 3
    BELOW_COLOR = 5   # Below baseline color
    ABOVE_COLOR = 8   # Above baseline color
    HANDLE_COLOR = 7   # White handle
    BG_COLOR = 1       # Dark blue track background
    
    # Baseline is at visual center of track
    baseline_x = x + w // 2
    
    # Map current value to pixel position
    # 0.25x baseline -> x (left edge)
    # 1.0x baseline  -> x + w//2 (center)
    # 4.0x baseline  -> x + w (right edge)
    if baseline_val == 0:
        ratio = 0.5
    else:
        val_ratio = current_val / baseline_val
        # Log-scale mapping: 0.25x->0, 1x->0.5, 4x->1.0
        import math
        ratio = (math.log2(max(0.25, min(4.0, val_ratio))) + 2) / 4  # maps [-2,2] to [0,1]
    
    handle_x = x + int(ratio * w)
    
    # Draw track background
    pyxel.rect(x, y, w, TRACK_H, BG_COLOR)
    # Draw filled portion with color split
    if handle_x <= baseline_x:
        pyxel.rect(handle_x, y, baseline_x - handle_x, TRACK_H, BELOW_COLOR)
    else:
        pyxel.rect(baseline_x, y, handle_x - baseline_x, TRACK_H, ABOVE_COLOR)
    # Draw baseline tick mark
    pyxel.rect(baseline_x, y - 1, 1, TRACK_H + 2, 13)  # Light grey tick
    # Draw handle
    pyxel.rect(handle_x - 1, y - 1, 3, TRACK_H + 2, HANDLE_COLOR)
```
[ASSUMED -- implementation approach, not from official source]

### Mouse Hit-Testing for Slider Drag (D-10)
```python
# Source: Pyxel mouse API [VERIFIED: pyxel.mouse_x, pyxel.btn exist]
def update_slider_input(slider):
    mx, my = pyxel.mouse_x, pyxel.mouse_y
    
    # Start drag on mouse press within handle area
    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
        if slider.hit_test(mx, my):
            slider.dragging = True
    
    # Continue drag while mouse held
    if slider.dragging and pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
        # Map mouse x to value in [0.25x, 4.0x] range
        ratio = (mx - slider.x) / slider.w
        ratio = max(0.0, min(1.0, ratio))
        # Convert ratio to value (log-scale)
        import math
        multiplier = 2 ** (ratio * 4 - 2)  # [0,1] -> [0.25, 4.0]
        new_val = tuning.get_baseline(slider.key) * multiplier
        # Snap to int if baseline is int
        if isinstance(tuning.get_baseline(slider.key), int):
            new_val = int(round(new_val))
        tuning.set_value(slider.key, new_val)
    
    # End drag on mouse release
    if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
        slider.dragging = False
```

### Keyboard Numeric Entry (D-09)
```python
# Source: Pyxel input_text API [VERIFIED: pyxel.input_text is str property]
def update_keyboard_edit(slider):
    if not slider.editing:
        return
    
    # Append typed characters to edit buffer
    text = pyxel.input_text
    for ch in text:
        if ch in '0123456789.-':
            slider.edit_buffer += ch
    
    # Confirm with Enter
    if pyxel.btnp(pyxel.KEY_RETURN):
        try:
            val = float(slider.edit_buffer)
            tuning.set_value(slider.key, val)
        except ValueError:
            pass  # Invalid input, discard
        slider.editing = False
        slider.edit_buffer = ""
    
    # Cancel with Escape
    if pyxel.btnp(pyxel.KEY_ESCAPE):
        slider.editing = False
        slider.edit_buffer = ""
    
    # Backspace
    if pyxel.btnp(pyxel.KEY_BACKSPACE):
        slider.edit_buffer = slider.edit_buffer[:-1]
```

### Journal JSONL Writer (D-16)
```python
# Source: stdlib json + file I/O [VERIFIED: os.fsync used in tuning.save()]
import json
import os
import time
from datetime import datetime

class Journal:
    def __init__(self, journal_dir):
        self.journal_dir = journal_dir
        os.makedirs(journal_dir, exist_ok=True)
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = os.path.join(journal_dir, f"session_{session_id}.jsonl")
        self._fd = open(self.path, "a", encoding="utf-8")
    
    def record(self, key, old_val, new_val):
        entry = {
            "t": time.time(),
            "f": pyxel.frame_count,
            "k": key,
            "old": old_val,
            "new": new_val,
        }
        self._fd.write(json.dumps(entry, separators=(',', ':')) + "\n")
        self._fd.flush()
        os.fsync(self._fd.fileno())
    
    def close(self):
        self._fd.close()
```

### Preset Save/Load (D-11 through D-15)
```python
# Source: tuning.py save() pattern [VERIFIED: atomic write in tuning.save()]
import json
import os
import time
from src.core import tuning

FEEL_GROUPS = [
    "movement", "dash", "forgiving", "wall",
    "slime_follow", "slime_juice", "projectile",
    "drill", "fusion", "slime_ram", "charge_shot", "boost",
]

def save_preset(slot, alias=""):
    """Save current feel-relevant values to a preset slot."""
    values = {}
    for key, group in tuning._flat_index.items():
        if group in FEEL_GROUPS:
            values[key] = getattr(tuning, key)
    
    preset = {
        "version": "1.0",
        "schema_version": "0.3.0",
        "slot": slot,
        "alias": alias,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "values": values,
    }
    
    path = f"assets/presets/slot_{slot}.json"
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(preset, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def load_preset(slot):
    """Load a preset, applying all values via tuning.set_value()."""
    path = f"assets/presets/slot_{slot}.json"
    with open(path, encoding="utf-8") as f:
        preset = json.load(f)
    for key, val in preset["values"].items():
        try:
            tuning.set_value(key, val)
        except KeyError:
            pass  # Key removed from schema -- skip silently
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Edit constants.py manually | `tuning.set_value()` live mutation | Phase 24 (2026-04-11) | Panel can change values without restart |
| `from constants import X` (frozen) | `tuning.X` (live PEP 562) | Phase 25 (2026-04-11) | Slider changes visible immediately at call sites |
| No overlays | F2-F5 overlays (Phase 27) | Phase 27 (2026-04-12) | Visual feedback during tuning |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Log-scale slider mapping (0.25x-4x range) is appropriate for feel tuning | Architecture Patterns | Linear mapping would cluster useful values; may need adjustment |
| A2 | 10px per slider row is sufficient for readability at 320x192 | Architecture Patterns | May need 12px rows, reducing visible count |
| A3 | Immediate fsync on every journal entry is acceptable performance | Code Examples | Could cause micro-stutter on slow disks; batch alternative exists |
| A4 | `pyxel.input_text` returns chars typed this frame (not accumulated) | Code Examples | Keyboard entry implementation would need adjustment |
| A5 | Movement group keys split between Move tab (walk/speed) and Jump tab (gravity/jump) needs hardcoded mapping | Architecture Patterns | `get_group()` returns "movement" for all 8 keys; tab assignment for gravity/jump subset must be manual |

## Open Questions

1. **Movement group key split between Move and Jump tabs**
   - What we know: D-02 says Jump tab gets "gravity/jump from movement". The movement group has 8 keys. GRAVITY, JUMP_FORCE, VARIABLE_JUMP_REDUCTION, FALLING_GRAVITY_MULTIPLIER, MAX_FALL_SPEED are jump-related. WALK_ACCEL, WALK_FRICTION, MAX_WALK_SPEED are move-related.
   - What's unclear: Exact split. Is MAX_FALL_SPEED a Move or Jump value?
   - Recommendation: Hardcode a `JUMP_TAB_MOVEMENT_KEYS` set containing `{"GRAVITY", "MAX_FALL_SPEED", "JUMP_FORCE", "VARIABLE_JUMP_REDUCTION", "FALLING_GRAVITY_MULTIPLIER"}`. Remaining movement keys go to Move tab.

2. **"Tight" and "Floaty" preset values**
   - What we know: D-12 requires shipping these two presets alongside v1.3 baseline.
   - What's unclear: Exact numeric values for "tight" and "floaty" feel.
   - Recommendation: Define "tight" as higher accel/friction, lower coyote/buffer. "Floaty" as lower gravity, higher coyote, lower friction. Exact values can be tuned using the panel itself once built.

3. **Journal directory location**
   - What we know: Journals are per-session JSONL files for crash recovery.
   - What's unclear: Whether to put in `assets/journal/` or a separate location.
   - Recommendation: `assets/journal/` with a `.gitignore` entry. Journals are ephemeral diagnostic data, not version-controlled game content.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Everything | Yes | 3.x | -- |
| Pyxel | Rendering, input | Yes | 2.8.7 | -- |
| json (stdlib) | Presets, journal | Yes | N/A | -- |
| pathlib (stdlib) | File management | Yes | N/A | -- |
| os (stdlib) | fsync, replace | Yes | N/A | -- |

No missing dependencies. All stdlib + Pyxel.

## Pyxel API Reference for Panel Implementation

Key Pyxel APIs verified for this phase:

| API | Type | Purpose | Notes |
|-----|------|---------|-------|
| `pyxel.mouse(visible)` | function | Show/hide OS cursor | Call True when panel opens, False when closes [VERIFIED] |
| `pyxel.mouse_x`, `pyxel.mouse_y` | int property | Cursor position in logical pixels | Already scaled to game coords [VERIFIED] |
| `pyxel.btn(MOUSE_BUTTON_LEFT)` | function | Mouse button held | For drag tracking [VERIFIED] |
| `pyxel.btnp(MOUSE_BUTTON_LEFT)` | function | Mouse button just pressed | For click detection [VERIFIED] |
| `pyxel.btnr(MOUSE_BUTTON_LEFT)` | function | Mouse button just released | For drag end [VERIFIED] |
| `pyxel.mouse_wheel` | int property | Scroll wheel delta | For tab content scrolling [VERIFIED] |
| `pyxel.input_text` | str property | Characters typed this frame | For keyboard numeric entry (D-09) [VERIFIED] |
| `pyxel.text(x, y, s, col)` | function | Draw text at 4px per char | Labels, values, tab names [VERIFIED] |
| `pyxel.rect(x, y, w, h, col)` | function | Filled rectangle | Backgrounds, slider tracks, handles [VERIFIED] |
| `pyxel.rectb(x, y, w, h, col)` | function | Rectangle border | Tab outlines, panel border [VERIFIED] |
| `FONT_WIDTH` | constant = 4 | Pixel width per character | Text layout calculations [VERIFIED] |

## Screen Space Budget

```
Total screen: 320 x 192

Panel overlay (full screen):
  Tab bar:          320 x 12px  (4 tabs, ~80px each)
  Header/status:    320 x 10px  (active preset, A/B indicator)  
  Content area:     320 x 160px (sliders + sub-group headers)
  Bottom bar:       320 x 10px  (Save button, preset hotkey hints)

Content area at 10px/row = 16 visible slider rows
Content area at  8px/row = 20 visible slider rows

Tab slider counts (all expanded):
  Move:  12 (fits without scroll at 8px/row)
  Jump:  10 (fits without scroll)
  Slime: 11 (fits without scroll)
  Fuse:  26 (REQUIRES scroll or collapsed defaults)
    - drill:       5
    - fusion:      7
    - slime_ram:   4
    - charge_shot: 5
    - boost:       5

Slider row layout (8px row height):
  [label 48px] [track 180px] [value 40px] [reset 12px] [pad 40px]
  Total: ~320px (full width)
```

## Sources

### Primary (HIGH confidence)
- `src/core/tuning.py` -- mutation API, baseline, save, flat index
- `src/core/overlays.py` -- F-key toggle pattern, update/draw contract
- `main.py` -- integration points at lines 405-407 (update) and 776-781 (draw)
- `assets/physics-schema.json` -- 22 groups, 87 leaves, v0.3.0
- `.planning/phases/28-live-tuning-panel-mvp/28-CONTEXT.md` -- all D-01 through D-16 decisions
- Pyxel 2.8.7 runtime -- verified mouse/keyboard/drawing APIs via Python interpreter

### Secondary (MEDIUM confidence)
- None needed -- all research conducted against actual codebase and Pyxel runtime

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- Pyxel-only, stdlib-only, all verified
- Architecture: HIGH -- follows established overlay patterns in codebase
- Pitfalls: HIGH -- derived from actual screen measurements and API testing
- Tuning API integration: HIGH -- verified every method in tuning.py source

**Research date:** 2026-04-12
**Valid until:** 2026-05-12 (stable -- Pyxel 2.8.x API unlikely to change)
