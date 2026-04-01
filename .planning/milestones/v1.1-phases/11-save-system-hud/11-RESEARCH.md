# Phase 11: Save System & HUD - Research

**Researched:** 2026-03-30
**Domain:** Game save/load persistence, HUD rendering, pause screen overlay, capacity upgrades (Pyxel 2.8.2 / Python 3.13)
**Confidence:** HIGH

## Summary

Phase 11 delivers the remaining 4 SYS requirements for v1.1: JSON save/load with save-room entities, mini-map in the HUD strip, pause screen with macro-map, and capacity upgrade items. The codebase already has strong foundations -- `collected_iids`, `event_flags`, `rooms_visited`, and the ENERGY/MISSILE item types all exist and work. The primary engineering work is (1) serializing/deserializing game state to a JSON file, (2) adding a SavePoint entity type to the entity-schema and LDtk pipeline, (3) drawing a mini-map in the 16px HUD strip, (4) adding PAUSED/TITLE/DEAD game states, and (5) wiring death to revert to last save instead of calling `reset()`.

The room grid is NOT a regular 5x5 grid -- current LDtk has 5 rooms at varying positions and sizes. The mini-map and macro-map must handle variable room sizes (some rooms are 320x528 or 320x352, not just 320x176). This is a critical design consideration for map rendering.

**Primary recommendation:** Use Python's built-in `json` module for save/load (no external dependencies). Extend the existing `game_state` string state machine to handle TITLE, PAUSED, and DEAD states. Keep all save logic in a new `src/core/save_manager.py` module separate from main.py.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- D-01: Save rooms -- dedicated save point entities, player walks onto save point and presses UP to save
- D-02: Single save slot -- one JSON file, overwritten each save
- D-03: Full game state saved -- player state (HP, max_hp, unlocked abilities), slime state (juice, max_juice), world progress (collected_iids, event_flags, current save room coordinates, visited_rooms set)
- D-04: On load, player respawns at last save room with full HP and juice restored
- D-05: Save point visual -- glowing pedestal/crystal, floor-mounted, 8x8 or 16x16 sprite with Pyxel palette color pulse (color 10 yellow)
- D-06: Mini-map centered in the existing 16px HUD strip, between HP pips (left) and juice bar (right)
- D-07: Dot grid style -- each room is a small square (2-3px). Only visited rooms shown. Current room blinks/highlights. Unvisited rooms invisible
- D-08: Color-coded rooms -- save rooms green, boss rooms red, current room white/blinking, visited rooms gray
- D-09: Visited rooms persisted in save file JSON
- D-10: ESC key opens/closes pause screen
- D-11: Pause screen shows: full macro-map (5x5 room grid, larger), player stats overlay, menu options (Resume, Save if in save room, Quit)
- D-12: Macro-map uses same color-coding as mini-map. No item markers
- D-13: Reuse existing ENERGY (+1 max_hp) and MISSILE (+50 max_juice) item types
- D-14: 2 heart containers + 2 juice tanks in the world. Start: 3 HP / 200 juice. Max: 5 HP / 300 juice. Placed in LDtk rooms
- D-15: On death, revert to last save state -- world progress rolls back to what was saved
- D-16: Brief death animation -- short freeze + fade to black (30-60 frames), then respawn at save room
- D-17: Simple title screen -- game title + Continue (if save exists) / New Game
- D-18: Verify map.py legacy gate scan +16 hardcode is fixed

### Claude's Discretion
- Save file location and format details (filename, JSON structure)
- Save point sprite animation specifics (pulse rate, colors)
- Death animation exact timing and visual effect
- Title screen layout and font styling
- Pause screen layout (positioning of map, stats, menu)
- Mini-map exact pixel sizing within 16px HUD strip
- How to surface "Save?" prompt when on save point
- Gamepad mapping for ESC/pause (Start button)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SYS-01 | Save Rooms/Checkpoints with JSON persistence | D-01 through D-05: SavePoint entity, json save/load module, save file format |
| SYS-02 | Mini-map HUD bar (showing room grid and current location) | D-06 through D-09: Dot grid in 16px HUD strip, color-coded, visited-only |
| SYS-03 | Pause Screen with full Macro-Map view | D-10 through D-12: ESC pause, macro-map, stats, menu overlay |
| SYS-04 | Heart Containers and Juice Capacity upgrade items | D-13 through D-14: Existing ENERGY/MISSILE types, placement in LDtk |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| json (stdlib) | built-in | Save file serialization/deserialization | No external deps needed for single-file JSON persistence |
| os.path (stdlib) | built-in | Save file path resolution | Cross-platform path handling |
| pyxel | 2.8.2 | Game framework (rendering, input, timing) | Already installed; all drawing/input through Pyxel API |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pathlib (stdlib) | built-in | Save file directory creation | Only if save dir needs to be created |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| json | pickle | JSON is human-readable and debuggable; pickle has security issues |
| json | msgpack | Overkill for a single save slot; adds external dependency |

**Installation:** No new packages needed. All functionality uses Python stdlib + existing Pyxel.

## Architecture Patterns

### Recommended Project Structure
```
src/
  core/
    save_manager.py    # SaveManager class: save(), load(), delete(), exists()
    constants.py       # New constants: SAVE_FILE_PATH, death timing, map colors
  entities/
    save_point.py      # SavePoint entity class (interaction, visual, proximity check)
  level/
    world.py           # Existing (expose room grid data for mini-map)
main.py                # Extended game_state machine: TITLE, PLAYING, PAUSED, DEAD
assets/
  entity-schema.json   # Add SavePoint entity definition
  sprites/
    save_point.png     # SavePoint sprite (8x8 or 16x16 frames)
```

### Pattern 1: Centralized Save Manager
**What:** A `SaveManager` class that owns all serialization logic. Reads game state from Game object, writes to JSON, and can restore state back onto Game object.
**When to use:** All save/load operations go through this single module.
**Example:**
```python
# src/core/save_manager.py
import json
import os

SAVE_FILE = "save.json"

class SaveManager:
    @staticmethod
    def save(game):
        """Serialize current game state to JSON file."""
        data = {
            "version": 1,
            "player": {
                "hp": game.player.hp,
                "max_hp": game.player.max_hp,
                "has_dash": game.player.has_dash,
                "has_shield": game.player.has_shield,
                "has_shield_t2": game.player.has_shield_t2,
                "has_boost": game.player.has_boost,
            },
            "slime": {
                "juice": game.slime.juice,
                "max_juice": game.slime.max_juice,
            },
            "world": {
                "collected_iids": list(game.world.collected_iids),
                "event_flags": dict(game.event_flags),
                "save_room_id": game.world.current_level.id if game.world.current_level else None,
                "visited_rooms": list(game.rooms_visited),
            },
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load():
        """Deserialize save file. Returns dict or None if no save."""
        if not os.path.exists(SAVE_FILE):
            return None
        with open(SAVE_FILE) as f:
            return json.load(f)

    @staticmethod
    def exists():
        return os.path.exists(SAVE_FILE)

    @staticmethod
    def delete():
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
```

### Pattern 2: Extended Game State Machine
**What:** Extend the existing `game_state` string from `"PLAYING"/"WON"` to include `"TITLE"`, `"PAUSED"`, and `"DEAD"` states.
**When to use:** State-driven update/draw dispatch in main.py.
**Example:**
```python
# In Game.update():
if self.game_state == "TITLE":
    self._update_title()
    return
elif self.game_state == "PAUSED":
    self._update_pause()
    return
elif self.game_state == "DEAD":
    self._update_death()
    return
# ... existing PLAYING/WON logic

# In Game.draw():
if self.game_state == "TITLE":
    self._draw_title()
    return
elif self.game_state == "PAUSED":
    # Draw game world first (frozen), then overlay
    self._draw_game_world()
    self._draw_pause_overlay()
    return
elif self.game_state == "DEAD":
    self._draw_death()
    return
```

### Pattern 3: Save Point Entity with Proximity Interaction
**What:** SavePoint entity placed via LDtk, checks player proximity + UP key press.
**When to use:** Save room interaction.
**Example:**
```python
# src/entities/save_point.py
class SavePoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8  # Collision box
        self.pulse_timer = 0

    def is_player_near(self, player):
        """Check if player overlaps save point hitbox."""
        return (player.x < self.x + self.w and
                player.x + player.w > self.x and
                player.y < self.y + self.h and
                player.y + player.h > self.y)

    def draw(self):
        # Pulsing yellow glow (color 10) cycling every 30 frames
        self.pulse_timer = (self.pulse_timer + 1) % 60
        color = 10 if self.pulse_timer < 30 else 9  # Yellow/orange pulse
        # Draw pedestal sprite or rect placeholder
        draw_sprite(self.x, self.y, self.w, self.h, ...)
```

### Pattern 4: Mini-Map Room Grid Rendering
**What:** Convert world-space room coordinates to a small pixel grid for the HUD.
**When to use:** HUD mini-map and pause screen macro-map.
**Example:**
```python
def _draw_minimap(self, center_x, center_y, scale):
    """Draw room grid as colored rectangles.

    scale: pixels per world-tile (e.g., 0.05 for mini-map, 0.2 for macro-map)
    """
    # Find world bounds to normalize room positions
    min_wx = min(lb.x for lb in self.world.levels)
    min_wy = min(lb.y for lb in self.world.levels)

    for lb in self.world.levels:
        if lb.id not in self.rooms_visited:
            continue  # Only show visited rooms
        rx = center_x + int((lb.x - min_wx) * scale)
        ry = center_y + int((lb.y - min_wy) * scale)
        rw = max(2, int(lb.w * scale))
        rh = max(2, int(lb.h * scale))

        # Color coding per D-08
        color = 5  # Gray for visited
        if lb.id == current_room_id:
            color = 7 if pyxel.frame_count % 30 < 15 else 0  # Blink white
        elif is_save_room(lb.id):
            color = 11  # Green
        elif is_boss_room(lb.id):
            color = 8   # Red

        pyxel.rect(rx, ry, rw, rh, color)
```

### Anti-Patterns to Avoid
- **Saving entire Game object:** Never try to serialize the whole Game instance. Cherry-pick only the state fields that matter (HP, items, flags, room). Pyxel objects, level_map data, and entity references are not serializable.
- **Modifying WorldManager for save data:** Keep save serialization in SaveManager, not scattered across WorldManager. WorldManager owns runtime state; SaveManager owns persistence.
- **Drawing pause overlay in world-space:** The pause screen must be drawn in screen-space (after `pyxel.camera()` reset), not world-space. Same as HUD.
- **Hardcoding room grid positions:** Use `world.levels` data to compute map positions dynamically. The room layout is defined in LDtk and loaded at runtime.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON serialization | Custom binary format | `json.dump/load` | Human-readable, debuggable, stdlib |
| Save file versioning | Complex migration system | Simple `version` field + defaults for missing keys | Single save slot, prototype scope |
| Set serialization | Custom set encoding | `list(set)` for JSON, `set(list)` on load | Python sets are not JSON-serializable; convert at boundary |
| Room type detection | Hardcoded room-type map | Entity scan at load time | Check if room contains SavePoint or BossMole entity to classify |

**Key insight:** The save system is simple (one slot, one JSON file). Resist over-engineering -- a flat JSON dict with version field is sufficient for a prototype.

## Common Pitfalls

### Pitfall 1: Set Serialization
**What goes wrong:** `json.dump` raises TypeError on Python `set` objects.
**Why it happens:** JSON has no set type. `collected_iids` and `rooms_visited` are both sets.
**How to avoid:** Convert to list before saving: `list(game.world.collected_iids)`. Convert back on load: `set(data["collected_iids"])`.
**Warning signs:** TypeError during save.

### Pitfall 2: Death Rollback vs Reset
**What goes wrong:** Using `self.reset()` on death wipes all progress instead of reverting to last save.
**Why it happens:** Current death handler (line 308-310) calls `reset()` which reinitializes everything.
**How to avoid:** Replace death logic with "load from save file" flow: `SaveManager.load()` -> restore state -> respawn at save room. Only `reset()` on "New Game".
**Warning signs:** Player loses all items/progress on death even though they saved.

### Pitfall 3: Save Room Detection for Map Color-Coding
**What goes wrong:** No way to know which rooms contain save points without scanning entities.
**Why it happens:** Room type is not stored in LevelBounds; it's inferred from entity placement.
**How to avoid:** On world load, scan all entities to build a room-type lookup dict: `{level_id: "save" | "boss" | "normal"}`. Cache this once.
**Warning signs:** All rooms appear gray on mini-map.

### Pitfall 4: Pause Screen Input Bleed
**What goes wrong:** Player character moves or shoots when unpausing because the unpause key press also triggers gameplay input.
**Why it happens:** `btnp()` returns True for the frame the key is pressed; if pause toggle and gameplay both check on the same frame, both fire.
**How to avoid:** Set game_state to PAUSED and `return` immediately from update. On unpause frame, set state back but `return` before processing gameplay input (consume the frame).
**Warning signs:** Player jumps or attacks when pressing ESC to unpause.

### Pitfall 5: HUD Space Constraint
**What goes wrong:** Mini-map overlaps with HP pips or juice bar.
**Why it happens:** HUD strip is only 16px tall and 320px wide. HP pips use left ~54px (5 pips * 10px + 4px margin). Juice bar uses right ~84px. That leaves ~182px in the center.
**How to avoid:** Calculate available space precisely. HP max = 5 pips = 54px from left. Juice bar = 84px from right. Center region: x=54 to x=236 (182px wide). Mini-map fits easily.
**Warning signs:** Visual overlap, elements drawn on top of each other.

### Pitfall 6: Variable Room Sizes in Map Display
**What goes wrong:** Map assumes all rooms are 320x176 and renders them uniformly.
**Why it happens:** Room D-11 mentions "5x5 room grid" but actual LDtk data has rooms of varying height (176, 352, 528 pixels).
**How to avoid:** Scale room rectangles proportionally based on actual LevelBounds dimensions. A 320x528 room should render 3x taller than a 320x176 room.
**Warning signs:** Map layout doesn't match actual world; rooms overlap or have gaps.

### Pitfall 7: Save File Location Portability
**What goes wrong:** Save file written to current working directory, which varies depending on how the game is launched.
**Why it happens:** `os.path.exists("save.json")` is relative to CWD.
**How to avoid:** Use a path relative to the script location: `os.path.join(os.path.dirname(__file__), "../../save.json")` or place in project root with explicit path.
**Warning signs:** Save file "disappears" when launching game from different directory.

## Code Examples

### Save File JSON Format (Recommended)
```json
{
  "version": 1,
  "player": {
    "max_hp": 4,
    "has_dash": true,
    "has_shield": true,
    "has_shield_t2": false,
    "has_boost": true
  },
  "slime": {
    "max_juice": 250.0
  },
  "world": {
    "collected_iids": ["iid-abc-123", "iid-def-456"],
    "event_flags": {"boss_defeated": true},
    "save_room_id": "Level_2",
    "visited_rooms": ["Level_0", "Level_1", "Level_2"]
  }
}
```
Note: HP and juice are NOT saved -- D-04 says respawn at full HP and juice.

### Restoring Game State from Save Data
```python
def restore_from_save(self, data):
    """Apply saved state to current game. Called after reset() sets up the world."""
    p = data["player"]
    self.player.max_hp = p["max_hp"]
    self.player.hp = self.player.max_hp  # Full HP on load (D-04)
    self.player.has_dash = p["has_dash"]
    self.player.has_shield = p["has_shield"]
    self.player.has_shield_t2 = p["has_shield_t2"]
    self.player.has_boost = p["has_boost"]

    s = data["slime"]
    self.slime.max_juice = s["max_juice"]
    self.slime.juice = self.slime.max_juice  # Full juice on load (D-04)

    w = data["world"]
    self.world.collected_iids = set(w["collected_iids"])
    self.event_flags = dict(w["event_flags"])
    self.rooms_visited = set(w["visited_rooms"])

    # Teleport player to save room
    save_room_id = w["save_room_id"]
    for level in self.world.levels:
        if level.id == save_room_id:
            # Spawn at save point entity location within this room
            for ent in self.level_map.entities:
                if ent["type"] == "SavePoint" and level.contains(ent["x"], ent["y"]):
                    self.player.x = ent["x"]
                    self.player.y = ent["y"]
                    break
            else:
                # Fallback: room center
                self.player.x = level.x + level.w // 2
                self.player.y = level.y + level.h // 2
            # Set camera and detect level
            self.world.detect_level(self.player.x, self.player.y)
            self.cam_x, self.cam_y = self.world.get_camera_clamped(self.player.x, self.player.y)
            break

    self.spawn_enemies()
```

### Death Animation with Fade Effect
```python
# Pyxel has no built-in fade. Use pal() color remapping to simulate.
DEATH_FREEZE_FRAMES = 30   # 0.5s freeze
DEATH_FADE_FRAMES = 30     # 0.5s fade to black

def _update_death(self):
    self.death_timer += 1
    total = DEATH_FREEZE_FRAMES + DEATH_FADE_FRAMES
    if self.death_timer >= total:
        # Load last save
        save_data = SaveManager.load()
        if save_data:
            self.reset()
            self.restore_from_save(save_data)
            self.game_state = "PLAYING"
        else:
            # No save -- back to title
            self.game_state = "TITLE"

def _draw_death(self):
    # Draw frozen game world
    self._draw_game_world()
    # Overlay darkening rectangle
    if self.death_timer > DEATH_FREEZE_FRAMES:
        fade_t = (self.death_timer - DEATH_FREEZE_FRAMES) / DEATH_FADE_FRAMES
        # Pyxel doesn't have alpha. Use dithered black overlay:
        # Draw black pixels in a pattern that increases with fade_t
        # Simpler: just draw a black rect after freeze is done
        pyxel.rect(0, 0, SCREEN_W, SCREEN_H, 0)
```

### Title Screen
```python
def _draw_title(self):
    pyxel.cls(0)
    # Title text centered
    title = "JELLY ROLL"
    tx = (SCREEN_W - len(title) * 4) // 2  # pyxel.text is ~4px per char
    pyxel.text(tx, 60, title, 7)

    # Menu options
    if SaveManager.exists():
        pyxel.text(tx, 100, "CONTINUE", 7 if self.title_cursor == 0 else 5)
        pyxel.text(tx, 112, "NEW GAME", 7 if self.title_cursor == 1 else 5)
    else:
        pyxel.text(tx, 100, "NEW GAME", 7)

    # Cursor indicator
    cursor_y = 100 + self.title_cursor * 12
    pyxel.text(tx - 8, cursor_y, ">", 10)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `self.reset()` on death | Load from save file on death | Phase 11 | Death has stakes -- progress reverts to save |
| game_state: PLAYING/WON | TITLE/PLAYING/PAUSED/DEAD/WON | Phase 11 | Full game loop with menus |
| No HUD mini-map | Dot-grid mini-map in HUD strip | Phase 11 | Navigation aid |
| No save persistence | JSON save file with full state | Phase 11 | Game sessions survive across launches |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | none (uses defaults) |
| Quick run command | `python -m pytest tests/ -x -q` |
| Full suite command | `python -m pytest tests/ -q` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SYS-01 | SaveManager.save() serializes correct fields | unit | `python -m pytest tests/test_save_system.py::TestSaveManager -x` | Wave 0 |
| SYS-01 | SaveManager.load() restores state correctly | unit | `python -m pytest tests/test_save_system.py::TestLoadRestore -x` | Wave 0 |
| SYS-01 | SavePoint entity proximity + interaction | unit | `python -m pytest tests/test_save_system.py::TestSavePoint -x` | Wave 0 |
| SYS-01 | Death triggers save-load rollback (not reset) | unit | `python -m pytest tests/test_save_system.py::TestDeathRollback -x` | Wave 0 |
| SYS-02 | Mini-map renders only visited rooms | unit | `python -m pytest tests/test_minimap.py::TestMiniMapVisited -x` | Wave 0 |
| SYS-02 | Room color-coding (save=green, boss=red, current=white) | unit | `python -m pytest tests/test_minimap.py::TestRoomColors -x` | Wave 0 |
| SYS-03 | ESC toggles pause state | unit | `python -m pytest tests/test_pause.py::TestPauseToggle -x` | Wave 0 |
| SYS-03 | Game state machine transitions (TITLE/PLAYING/PAUSED/DEAD) | unit | `python -m pytest tests/test_save_system.py::TestGameStates -x` | Wave 0 |
| SYS-04 | ENERGY item +1 max_hp, MISSILE +50 max_juice | unit | `python -m pytest tests/test_health.py -x` | Existing (partial) |
| SYS-04 | Capacity caps at 5 HP / 300 juice | unit | `python -m pytest tests/test_save_system.py::TestCapacityCaps -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/ -x -q`
- **Per wave merge:** `python -m pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_save_system.py` -- covers SYS-01 save/load/rollback and game state machine
- [ ] `tests/test_minimap.py` -- covers SYS-02 room rendering logic
- [ ] `tests/test_pause.py` -- covers SYS-03 pause toggle and overlay state

## Existing Code Integration Points

### What Already Exists (Reuse Directly)
| Component | Location | What It Provides |
|-----------|----------|------------------|
| `collected_iids` set | world.py:58 | Item persistence -- already tracks collected items by IID |
| `event_flags` dict | main.py:96 | Boss defeat / event tracking -- already used for doors |
| `rooms_visited` set | main.py:104 | Room visit tracking -- already maintained on room entry |
| `Item.collect()` ENERGY/MISSILE | items.py:22-27 | max_hp +1 and max_juice +50 already implemented |
| `game_state` string | main.py:97 | State machine skeleton -- extend from PLAYING/WON |
| `death_timer` | main.py:98 | Death animation timer already exists (currently just counts to 15) |
| `_draw_hud()` | main.py:598-631 | HUD strip with HP pips (left) and juice bar (right) |
| `world.levels` list | world.py:43 | LevelBounds objects with id, x, y, w, h for all rooms |

### What Needs Modification
| Component | Location | Change Required |
|-----------|----------|-----------------|
| `Game.__init__` | main.py:31 | Add SaveManager, title_cursor, check for existing save |
| `Game.reset()` | main.py:50 | Add `game_state = "TITLE"` for initial launch; separate from "load save" flow |
| `Game.update()` | main.py:224 | Add TITLE/PAUSED/DEAD state dispatch before gameplay |
| `Game.draw()` | main.py:537 | Add TITLE/PAUSED/DEAD draw dispatch |
| Death handler | main.py:307-310 | Replace `reset()` with save-load rollback |
| `_draw_hud()` | main.py:598-631 | Insert mini-map between HP pips and juice bar |
| `spawn_enemies()` | main.py:128 | Add SavePoint entity spawning |
| entity-schema.json | assets/ | Add SavePoint entity definition |
| `_on_room_enter()` | main.py:465 | Track save_points list for current room (for "in save room" detection) |

### Current Room Grid Layout (from LDtk)
```
Level_0: (0,0)     320x176   -- Standard room
Level_1: (320,0)   320x528   -- Tall shaft (3x height)
Level_2: (640,176) 320x352   -- Double-height room
Level_3: (960,176) 320x176   -- Standard room
Level_4: (960,352) 320x176   -- Standard room (below Level_3)
```
Total world bounds: 1280 x 528 pixels. NOT a regular grid -- rooms have varying heights and y-offsets. Mini-map scaling must account for this.

### HUD Space Budget
```
HUD strip: y=176, h=16, w=320
HP pips:   x=4, w=50 (5 pips * 10px)    [LEFT]
Juice bar: x=236, w=80                   [RIGHT]
Available: x=54 to x=236 = 182px center  [MINI-MAP]
```

## Open Questions

1. **Save point sprite asset**
   - What we know: D-05 specifies 8x8 or 16x16 with color 10 yellow pulse
   - What's unclear: No save_point.png exists yet in assets/sprites/
   - Recommendation: Add a SavePoint frame row to items.png (frame index 6) or create save_point.png. Placeholder rect is fine for v1.1.

2. **Room type classification persistence**
   - What we know: Need to color-code save rooms (green) and boss rooms (red) on map
   - What's unclear: No metadata marks rooms as "save" or "boss" type in LDtk data
   - Recommendation: Scan entity list at world load to build `room_types` dict. If room contains SavePoint -> "save", if BossMole -> "boss", else "normal".

3. **Save file location**
   - What we know: Must be single JSON file (D-02)
   - What's unclear: Where exactly -- project root, user home, or alongside executable?
   - Recommendation: Project root `save.json` (simplest, matches prototype scope). Use `os.path.dirname(os.path.abspath(__file__))` in main.py to resolve.

## Sources

### Primary (HIGH confidence)
- Codebase analysis: main.py, world.py, items.py, player.py, constants.py, entity-schema.json
- LDtk simplified export: assets/cave/simplified/ (5 rooms verified)
- Pyxel 2.8.2 installed and verified
- pytest 9.0.2 with 35+ existing test files

### Secondary (MEDIUM confidence)
- Pyxel API knowledge (drawing, input, palette) from training data -- verified against installed version

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All stdlib, no new dependencies
- Architecture: HIGH - Extending well-understood existing patterns (game_state, entity spawning, HUD drawing)
- Pitfalls: HIGH - Based on direct codebase analysis of current death handler, HUD layout, and room data
- Integration: HIGH - All integration points verified by reading actual source code

**Research date:** 2026-03-30
**Valid until:** 2026-04-30 (stable -- no external dependency version concerns)
