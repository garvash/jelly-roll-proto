# Phase 12: Screen Size Expansion - Research

**Researched:** 2026-03-28
**Domain:** Pyxel display sizing, camera system, HUD rendering, LDtk level dimensions
**Confidence:** HIGH

## Summary

Phase 12 expands the game display from 128x128 to 320x192, introducing a Super Metroid-style bottom HUD strip (16px). The game viewport becomes 320x176, with standard rooms matching that exactly so the camera locks (no scroll). This is primarily a constants-and-propagation task: define central screen constants, replace all hardcoded 128 values, add a HUD draw pass, update LDtk world settings, and update the entity schema.

The codebase is well-structured for this change. `WorldManager.SCREEN_W/SCREEN_H` already drives camera clamping, and room transitions use these constants. The main risk is missing a hardcoded 128 somewhere (there are 12+ locations in production code) or getting the camera/clip interaction wrong for the HUD strip.

**Primary recommendation:** Define all screen constants in `constants.py`, update `WorldManager` to use viewport dimensions for camera math, use `pyxel.clip()` to constrain game drawing to the top 176px, and draw HUD in screen-space after resetting camera.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Display size = 320x192 via `pyxel.init(320, 192)`
- **D-02:** Game viewport = 320x176 (40x22 tiles)
- **D-03:** HUD strip = 16px (2 tiles) fixed at bottom, Super Metroid-style
- **D-04:** HUD content = HP pips + juice meter at minimum; minimap if space allows in 16px
- **D-05:** Standard rooms = 320x176 (40x22 tiles), camera locks perfectly
- **D-06:** Large rooms use multiples like 320x352 (40x44) for intentional scrolling
- **D-07:** PML-to-LDtk converter receives updated room dimensions (320x176, TILE_SIZE=8)
- **D-08:** Central constants in constants.py: SCREEN_W=320, SCREEN_H=192, VIEWPORT_W=320, VIEWPORT_H=176, HUD_H=16
- **D-09:** Replace ALL hardcoded 128 values with central constants
- **D-10:** Pyxel default auto-scaling, no explicit scale factor

### Claude's Discretion
- HUD layout within the 16px strip (positioning of HP pips vs juice bar)
- Draw order for HUD (drawn after game world, before/after shake offset)
- Whether to add a visual separator line between game viewport and HUD

### Deferred Ideas (OUT OF SCOPE)
None
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pyxel | 2.8.2 | Game engine | Already installed, project engine |
| pytest | 9.0.2 | Testing | Already installed, project test runner |

No new libraries needed. This phase is purely constants + code changes + LDtk file updates.

## Architecture Patterns

### Constants Architecture (D-08)

All screen-related constants go in `src/core/constants.py`:

```python
# Screen / Display
SCREEN_W = 320       # Full pyxel window width
SCREEN_H = 192       # Full pyxel window height
VIEWPORT_W = 320     # Playable area width (same as screen for now)
VIEWPORT_H = 176     # Playable area height (above HUD)
HUD_H = 16           # HUD strip height at bottom
```

**Critical distinction:** `VIEWPORT_W/H` is what the camera system uses for clamping and boundary checks. `SCREEN_W/H` is what `pyxel.init()` uses. They differ in height by `HUD_H`.

### Camera System Update

`WorldManager.SCREEN_W/SCREEN_H` must become `VIEWPORT_W/VIEWPORT_H` (not `SCREEN_W/SCREEN_H`). The camera clamps to the playable viewport, not the full screen. If you use SCREEN_H (192), the camera would show 16px of out-of-bounds area below the viewport.

```python
# world.py -- import from constants
from src.core.constants import VIEWPORT_W, VIEWPORT_H

class WorldManager:
    SCREEN_W = VIEWPORT_W  # 320 -- camera viewport width
    SCREEN_H = VIEWPORT_H  # 176 -- camera viewport height (excludes HUD)
```

### Draw Pipeline (HUD Pattern)

The draw method needs three phases:

```python
def draw(self):
    pyxel.cls(0)

    # Phase 1: Game world (clipped to viewport)
    pyxel.clip(0, 0, VIEWPORT_W, VIEWPORT_H)
    offset_x = self.cam_x
    offset_y = self.cam_y
    if self.shake_timer > 0:
        offset_x += pyxel.rndi(-2, 2)
        offset_y += pyxel.rndi(-2, 2)
    pyxel.camera(offset_x, offset_y)

    # ... draw all game entities (tilemap, enemies, player, effects, etc.)

    # Phase 2: Reset clip and camera for HUD
    pyxel.clip()       # Reset clipping to full screen
    pyxel.camera()     # Reset camera to (0, 0) screen coords

    # Phase 3: Draw HUD in screen space
    # HUD occupies y=176 to y=192 (bottom 16px)
    self._draw_hud()
```

**Why clip is needed:** Without `pyxel.clip()`, game world entities near the bottom of the viewport could bleed into the HUD area (particles, effects, large sprites). The clip constrains all drawing to the 320x176 game area.

**HUD is drawn in screen-space** (camera reset to 0,0), so HUD coordinates are absolute pixel positions on screen, not world positions. This means HUD is unaffected by camera shake.

### Boundary Check Pattern

All off-screen culling checks need updating from `cam + 128` to use viewport constants:

```python
# BEFORE (hardcoded)
if (self.x < cam_x or self.x > cam_x + 128 or
    self.y < cam_y or self.y > cam_y + 128):

# AFTER (using constants)
from src.core.constants import VIEWPORT_W, VIEWPORT_H
if (self.x < cam_x or self.x > cam_x + VIEWPORT_W or
    self.y < cam_y or self.y > cam_y + VIEWPORT_H):
```

For the `+ 144` checks (128 + 16 margin), use `VIEWPORT_W + 16` / `VIEWPORT_H + 16`:

```python
# BEFORE
if (self.x < cam_x - 16 or self.x > cam_x + 144 or
    self.y < cam_y - 16 or self.y > cam_y + 144):

# AFTER
if (self.x < cam_x - 16 or self.x > cam_x + VIEWPORT_W + 16 or
    self.y < cam_y - 16 or self.y > cam_y + VIEWPORT_H + 16):
```

### Anti-Patterns to Avoid
- **Using SCREEN_H for camera clamping:** Camera must clamp to VIEWPORT_H (176), not SCREEN_H (192). Using 192 would show 16px of void below the room.
- **Drawing HUD in world-space:** HUD must be drawn after `pyxel.camera()` reset, or it will scroll with the game world and shake with screen shake.
- **Hardcoding new values:** Do not replace `128` with `320` or `176` literals. Always use the named constants.

## Complete Hardcoded 128 Inventory

### Production Code (MUST change)

| File | Line | Current Code | Replacement |
|------|------|-------------|-------------|
| `main.py:16` | `pyxel.init(128, 128, ...)` | `pyxel.init(SCREEN_W, SCREEN_H, ...)` |
| `main.py:123` | `room_w, room_h = 128, 128` | `room_w, room_h = VIEWPORT_W, VIEWPORT_H` |
| `main.py:195` | `rx, ry, rw, rh = self.cam_x, self.cam_y, 128, 128` | Use `VIEWPORT_W, VIEWPORT_H` |
| `main.py:262` | `16 < rel_x < 112 and 16 < rel_y < 112` | `16 < rel_x < VIEWPORT_W - 16 and 16 < rel_y < VIEWPORT_H - 16` |
| `main.py:314-315` | `cam_x + 128`, `cam_y + 128` | `cam_x + VIEWPORT_W`, `cam_y + VIEWPORT_H` |
| `main.py:554-559` | HP drawn at `cam_y + 4` (in-game overlay) | Move to HUD strip in screen-space |
| `main.py:564-567` | Victory text centered for 128px | Re-center for 320px wide viewport |
| `world.py:27-28` | `SCREEN_W = 128`, `SCREEN_H = 128` | Import `VIEWPORT_W`, `VIEWPORT_H` from constants |
| `effects.py:23-24` | `cam_x + 128`, `cam_y + 128` | `cam_x + VIEWPORT_W`, `cam_y + VIEWPORT_H` |
| `effects.py:56-57` | `cam_x + 128`, `cam_y + 128` | `cam_x + VIEWPORT_W`, `cam_y + VIEWPORT_H` |
| `boss.py:29-30` | `cam_x + 144`, `cam_y + 144` | `cam_x + VIEWPORT_W + 16`, `cam_y + VIEWPORT_H + 16` |
| `projectile.py:41-42` | `cam_x + 144`, `cam_y + 144` | `cam_x + VIEWPORT_W + 16`, `cam_y + VIEWPORT_H + 16` |
| `projectile.py:90-91` | `cam_x + 144`, `cam_y + 144` | `cam_x + VIEWPORT_W + 16`, `cam_y + VIEWPORT_H + 16` |
| `map.py:61-62` | `data.get("width", 128)`, `data.get("height", 128)` | Change default to `VIEWPORT_W`, `VIEWPORT_H` |

### Asset Files (MUST change)

| File | Field | Current | New |
|------|-------|---------|-----|
| `assets/cave.ldtk:18` | `worldGridWidth` | 128 | 320 |
| `assets/cave.ldtk:19` | `worldGridHeight` | 128 | 176 |
| `assets/cave.ldtk:20` | `defaultLevelWidth` | 128 | 320 |
| `assets/cave.ldtk:21` | `defaultLevelHeight` | 128 | 176 |
| `assets/entity-schema.json:13` | `default_room_size` | `[128, 128]` | `[320, 176]` |
| `assets/entity-schema.json:15` | `variable_rooms_note` | mentions 128 | Update to 320x176 base |

### Utility Scripts

| File | Line | Current | New |
|------|------|---------|-----|
| `export_tilemap_csv.py:21-22` | `width = 128`, `height = 128` | Use constants or update default |

### Test Files (MUST update)

| File | Impact |
|------|--------|
| `tests/test_world_manager.py` | All `LevelBounds(..., 128, 128)` become `320, 176`. Camera clamping assertions change. Fallback grid-snap divisor changes from 128 to viewport dimensions. |

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Viewport clipping | Custom pixel-by-pixel boundary checks | `pyxel.clip(0, 0, VIEWPORT_W, VIEWPORT_H)` | Built-in GPU clipping, zero overhead |
| Screen scaling | Manual scale factor math | Pyxel auto-scaling (D-10) | Pyxel picks largest integer scale for the monitor automatically |
| HUD separator | Complex drawing logic | `pyxel.line(0, VIEWPORT_H, SCREEN_W, VIEWPORT_H, color)` | Single line call if desired |

## Common Pitfalls

### Pitfall 1: Camera Clamps to SCREEN_H Instead of VIEWPORT_H
**What goes wrong:** Camera uses 192 instead of 176 for vertical clamping, causing the game world to show 16px of area below the room where the HUD should be.
**Why it happens:** Confusing SCREEN_H (full window) with VIEWPORT_H (game area).
**How to avoid:** WorldManager must use VIEWPORT_W/VIEWPORT_H for all camera math. SCREEN_W/SCREEN_H is only for `pyxel.init()`.
**Warning signs:** Rooms show black space below the tilemap, or HUD overlaps with game content.

### Pitfall 2: Forgetting to Reset Clip Before HUD Draw
**What goes wrong:** HUD drawn while clip is still set to viewport area, so HUD at y=176-192 is invisible.
**Why it happens:** clip(0, 0, 320, 176) excludes the bottom 16px.
**How to avoid:** Always call `pyxel.clip()` (no args) before drawing HUD.
**Warning signs:** HUD simply does not appear.

### Pitfall 3: HUD Shaking with Screen Shake
**What goes wrong:** HUD bounces around during screen shake because camera offset was not reset.
**Why it happens:** `pyxel.camera(offset_x, offset_y)` still active when HUD draws.
**How to avoid:** Call `pyxel.camera()` (no args) before HUD drawing. HUD uses absolute screen coordinates.
**Warning signs:** HUD jitters when player takes damage or breaks blocks.

### Pitfall 4: Missing a Hardcoded 128
**What goes wrong:** One file still uses 128, causing entities to despawn too early on the wider screen or boundary checks to be wrong.
**Why it happens:** Many files had inline 128 values; easy to miss one.
**How to avoid:** Use the complete inventory above. After changes, grep for `\b128\b` in all `.py` files to verify none remain.
**Warning signs:** Projectiles disappearing mid-screen, particles culled too early on the right side.

### Pitfall 5: LDtk Level Sizes Not Updated
**What goes wrong:** LDtk simplified export still produces 128x128 levels, causing room detection and camera to malfunction.
**Why it happens:** Only updating code but not the LDtk project file.
**How to avoid:** Update `cave.ldtk` worldGridWidth/Height and defaultLevelWidth/Height. Also update each individual level's width/height. Then re-export simplified data.
**Warning signs:** Room transitions fail, camera snaps to wrong positions, entities spawn at wrong coordinates.

### Pitfall 6: Test Fixtures Using Old Room Sizes
**What goes wrong:** Tests pass with old 128x128 dimensions but fail when WorldManager.SCREEN_W/H changes to 320/176.
**Why it happens:** Test fixtures create LevelBounds(128, 128) which no longer match the constants.
**How to avoid:** Update all test room dimensions and camera assertions to match new viewport size.
**Warning signs:** test_world_manager.py failures on camera clamping tests.

## Code Examples

### HUD Drawing (16px Strip)

```python
# Source: Project-specific pattern for Super Metroid-style HUD
def _draw_hud(self):
    """Draw HUD in the bottom 16px strip (screen-space)."""
    hud_y = VIEWPORT_H  # 176 -- top of HUD strip

    # Background bar
    pyxel.rect(0, hud_y, SCREEN_W, HUD_H, 1)  # Dark blue background

    # HP pips (left side)
    for i in range(self.player.max_hp):
        pip_x = 4 + i * 10
        pip_y = hud_y + 4
        if i < self.player.hp:
            pyxel.rect(pip_x, pip_y, 8, 8, 8)  # Red filled
        else:
            pyxel.rect(pip_x, pip_y, 8, 8, 5)  # Dark empty

    # Juice meter (right side) -- bar representation
    juice_pct = self.slime.juice / JUICE_MAX
    bar_w = 80  # Max bar width in pixels
    bar_x = SCREEN_W - bar_w - 4
    bar_y = hud_y + 4
    pyxel.rect(bar_x, bar_y, bar_w, 8, 5)  # Background
    pyxel.rect(bar_x, bar_y, int(bar_w * juice_pct), 8, 11)  # Filled (green)
```

### Victory Text Re-centering

```python
# BEFORE (centered for 128px)
pyxel.rect(self.cam_x + 14, self.cam_y + 49, 100, 30, 0)
pyxel.text(self.cam_x + 44, self.cam_y + 59, "VICTORY!", ...)

# AFTER (centered for 320x176 viewport, screen-space)
box_w, box_h = 100, 30
box_x = (VIEWPORT_W - box_w) // 2  # 110
box_y = (VIEWPORT_H - box_h) // 2  # 73
pyxel.rect(box_x, box_y, box_w, box_h, 0)
pyxel.text(box_x + 30, box_y + 10, "VICTORY!", ...)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| 128x128 square display | 320x192 widescreen with HUD | Phase 12 | 2.5x wider view, dedicated HUD strip |
| HP overlay on game world | Dedicated HUD strip below viewport | Phase 12 | Clean separation, no obscured gameplay |
| Hardcoded screen dimensions | Central constants in constants.py | Phase 12 | Single source of truth for all screen math |

## Open Questions

1. **Individual LDtk level resizing**
   - What we know: `cave.ldtk` has `defaultLevelWidth/Height` and each level has its own `pxWid/pxHei`.
   - What's unclear: Whether changing defaults auto-updates existing levels, or each level needs individual edits.
   - Recommendation: Update defaults AND manually check/update each level entry. May need to regenerate via PML-to-LDtk converter (D-07 suggests this).

2. **Minimap feasibility in 16px**
   - What we know: D-04 says "minimap if space allows in 16px."
   - What's unclear: Whether a useful minimap fits in 16px height with the 5x5 room grid.
   - Recommendation: A 5x5 grid at 3px per cell = 15px fits. Each cell is a colored square. Implement as stretch goal after core HUD works.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | None (default pytest discovery) |
| Quick run command | `python -m pytest tests/test_world_manager.py -x` |
| Full suite command | `python -m pytest tests/ -x` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| D-01 | pyxel.init(320, 192) | manual | Visual verification | N/A |
| D-02 | Viewport = 320x176 | unit | `python -m pytest tests/test_world_manager.py -x` | Needs update |
| D-05 | Standard rooms = 320x176, camera locks | unit | `python -m pytest tests/test_world_manager.py -x` | Needs update |
| D-08 | Central constants defined | unit | `python -m pytest tests/test_screen_constants.py -x` | Wave 0 |
| D-09 | No hardcoded 128 in codebase | smoke | `grep -rn "\b128\b" --include="*.py" src/ main.py` | Script check |

### Wave 0 Gaps
- [ ] `tests/test_world_manager.py` -- update all room dimensions from 128x128 to 320x176, fix camera clamping assertions
- [ ] `tests/test_screen_constants.py` -- verify constants exist and are consistent (SCREEN_W, SCREEN_H, VIEWPORT_W, VIEWPORT_H, HUD_H, SCREEN_H == VIEWPORT_H + HUD_H)

## Sources

### Primary (HIGH confidence)
- Project source code: `main.py`, `world.py`, `effects.py`, `boss.py`, `projectile.py`, `map.py`, `constants.py`
- Project assets: `assets/cave.ldtk`, `assets/entity-schema.json`
- Pyxel 2.8.2 installed locally: `pyxel.clip(x, y, w, h)` and `pyxel.camera(x, y)` confirmed via `help()`
- [Pyxel GitHub](https://github.com/kitao/pyxel) - clip/camera API reference

### Secondary (MEDIUM confidence)
- [Pyxel PyPI](https://pypi.org/project/pyxel/2.1.6/) - version reference (local is 2.8.2, newer)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no new dependencies, all existing tools
- Architecture: HIGH - clip/camera pattern verified locally, hardcoded inventory from direct grep
- Pitfalls: HIGH - derived from actual code analysis, not speculation

**Research date:** 2026-03-28
**Valid until:** 2026-04-28 (stable -- no external dependency changes expected)
