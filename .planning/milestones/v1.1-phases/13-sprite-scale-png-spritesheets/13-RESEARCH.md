# Phase 13: Sprite Scale & PNG Spritesheet Support - Research

**Researched:** 2026-03-29
**Domain:** Pyxel sprite rendering, PNG asset pipeline, Aseprite workflow integration
**Confidence:** HIGH

## Summary

This phase migrates all entity graphics from programmatic pixel-setting (`generate_assets.py` + `game.pyxres`) to PNG spritesheets loaded at startup, while simultaneously scaling all entity sprites from 8x8 to 16x16 visual (keeping 8x8 collision). The Pyxel 2.8.7 API fully supports this -- `pyxel.images[N].load(x, y, filename)` loads PNG data directly into image banks at specified coordinates, and the palette round-trip (save scale=1, load) is verified pixel-perfect.

The codebase has 13 `pyxel.blt()` call sites across 7 entity files that need updating. The tilemap pipeline (`pyxel.bltm()` at main.py:529 referencing bank 0) is completely unaffected -- tiles stay 8x8 on bank 0. The main complexity is the bottom-center anchor offset formula that must be consistently applied at every entity draw site, and properly separating the new 16x16 entity sprites into bank 1 while keeping tile data on bank 0.

**Primary recommendation:** Build `upscale_sprites.py` first (generates all PNG assets from existing pyxres data), then update the loading pipeline in `main.py`, then systematically update each entity draw method with the offset formula. JSON sidecar parsing can be a simple loader function -- no class hierarchy needed for this prototype.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** All entity sprites are pre-scaled 16x16 art (not runtime scale=2). Source art is 16x16 from the start.
- **D-02:** Tiles stay 8x8 -- only entities scale up. Entities visually span 2x2 tile cells.
- **D-03:** Boss scales to 32x32 visual (currently 16x8 collision, becomes 32x32 visual).
- **D-04:** Collision boxes remain 8x8 for standard entities.
- **D-05:** Initial sprites are auto-upscaled from existing 8x8 (pixel doubling) as reference templates.
- **D-06:** One PNG per entity -- `assets/sprites/player.png`, `assets/sprites/slime.png`, etc.
- **D-07:** Horizontal strip layout -- frames left to right, Frame N at `(N * frame_width, 0)`.
- **D-08:** JSON sidecar per sprite (Aseprite format) with `frameTags`.
- **D-09:** Load PNGs via `pyxel.images[N].load()` -- replaces `pyxel.load("assets/game.pyxres")` entirely.
- **D-10:** `tiles.png` provides tile graphics for image bank 0.
- **D-11:** Drop `game.pyxres` entirely.
- **D-12:** Bottom-center anchor -- `draw_x = collision_x - (visual_w - collision_w) // 2`, `draw_y = collision_y - (visual_h - collision_h)`.
- **D-13:** Central `SPRITE_SCALE = 2` constant in `constants.py`.
- **D-14:** Keep negative-width flip in `pyxel.blt()`. Only right-facing sprites in PNGs.
- **D-15:** Bank 0 = tiles, Bank 1 = entities (16x16/32x32), Bank 2 = reserved.
- **D-16:** Sprite loading manifest hardcoded in `main.py` as dict.
- **D-17:** Effect sprites scale to 16x16. Particles stay as `pyxel.pset()`.
- **D-18:** HUD stays as draw primitives.
- **D-19:** `generate_assets.py` becomes `upscale_sprites.py` -- one-time migration tool.
- **D-20:** Add `sprite` object to entity-schema.json with `sheet` and `frame_size`.
- **D-21:** Existing `size` field remains collision dimensions.
- **D-22:** Aseprite export: horizontal strip PNG + JSON sidecar.
- **D-23:** Animation tags must match game state names.
- **D-24:** Frame size: 16x16 standard, 32x32 boss.
- **D-25:** Right-facing only. Code flips via negative blt width.
- **D-26:** Palette: Pyxel's 16 colors, index 0 = transparent.

### Claude's Discretion
- Exact row layout within bank 1 (which entity at which Y offset)
- JSON sidecar parsing implementation (loader class vs inline)
- upscale_sprites.py implementation approach (Pillow, pure Pyxel, etc.)
- Animation state machine refactor details per entity class

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pyxel | 2.8.7 | Game engine, image banks, sprite rendering | Already in use; `images[N].load()` confirmed working for PNG pipeline |
| Python stdlib `json` | 3.x | Parse Aseprite JSON sidecars | No external deps needed; JSON is trivial to parse |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pyxel `Image.save()` | 2.8.7 | Export PNGs from current pyxres sprites | In `upscale_sprites.py` for migration |
| Pyxel `Image.load()` | 2.8.7 | Load PNG spritesheets into image banks | Startup asset loading in `main.py` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Pyxel-native PNG export | Pillow for upscale_sprites.py | Pillow NOT installed; Pyxel can do pixel-doubling natively via nested loops -- no external dep needed |
| Per-entity PNG files | Single atlas PNG | Per-entity is simpler for artist workflow, decision D-06 locks this |

**No installation needed.** All required tools are already available via Pyxel 2.8.7.

## Architecture Patterns

### Recommended Bank 1 Layout

Bank 1 is 256x256 pixels. With 16x16 entity frames, that gives 16 columns and 16 rows (256 slots). With 32x32 boss frames, the boss takes 4 slots per frame.

```
Bank 1 (256x256, 16x16 cells):
Row 0 (y=0):   Player frames   [idle, walk0, walk1, jump, fall, dash, drill, ...]
Row 1 (y=16):  Slime frames    [idle0, idle1, fused/drill, ...]
Row 2 (y=32):  Snail frames    [walk0, walk1, ...]
Row 3 (y=48):  Bat frames      [hang, flap0, flap1, ...]
Row 4 (y=64):  Items           [energy, missile, dash_pickup, shield, boost, shield_t2, ...]
Row 5 (y=80):  Projectiles     [spit, charge_shot, rock, ...]
Row 6 (y=96):  Effects         [explosion0, explosion1, explosion2, ...]
Rows 8-9 (y=128, 32x32): Boss  [mole_idle0, mole_idle1, ...]
```

Each PNG strip is loaded at `(0, row * 16)` for standard entities or `(0, 128)` for the 32x32 boss.

### Pattern 1: Sprite Loading Manifest

**What:** Hardcoded dict in `main.py` mapping entity names to bank position and PNG path.
**When to use:** At startup, replacing `pyxel.load("assets/game.pyxres")`.

```python
# In main.py __init__
SPRITE_MANIFEST = {
    "tiles":      (0, 0, 0,   "assets/sprites/tiles.png"),
    "player":     (1, 0, 0,   "assets/sprites/player.png"),
    "slime":      (1, 0, 16,  "assets/sprites/slime.png"),
    "snail":      (1, 0, 32,  "assets/sprites/snail.png"),
    "bat":        (1, 0, 48,  "assets/sprites/bat.png"),
    "items":      (1, 0, 64,  "assets/sprites/items.png"),
    "projectile": (1, 0, 80,  "assets/sprites/projectile.png"),
    "effects":    (1, 0, 96,  "assets/sprites/effects.png"),
    "boss":       (1, 0, 128, "assets/sprites/boss.png"),
}

for name, (bank, x, y, path) in SPRITE_MANIFEST.items():
    pyxel.images[bank].load(x, y, path)
```

### Pattern 2: Bottom-Center Anchor Offset

**What:** Standard formula to draw 16x16 visual sprite anchored at bottom-center of 8x8 collision box.
**When to use:** Every entity `draw()` method.

```python
# constants.py
SPRITE_SCALE = 2
SPRITE_SIZE = 8 * SPRITE_SCALE  # 16 -- visual sprite dimensions
BOSS_SPRITE_SIZE = 16 * SPRITE_SCALE  # 32

# In any entity draw():
# self.x, self.y = collision box top-left (8x8)
# self.w, self.h = collision dimensions (8, 8)
visual_w = SPRITE_SIZE  # 16
visual_h = SPRITE_SIZE  # 16
draw_x = self.x - (visual_w - self.w) // 2   # Center horizontally: x - 4
draw_y = self.y - (visual_h - self.h)         # Extend upward: y - 8
w = visual_w if self.facing_right else -visual_w
pyxel.blt(draw_x, draw_y, 1, u, v, w, visual_h, 0)
```

### Pattern 3: JSON Sidecar Loader

**What:** Simple function to parse Aseprite JSON and return animation tag-to-frame mapping.
**When to use:** At startup alongside PNG loading.

```python
import json

def load_sprite_tags(json_path):
    """Parse Aseprite JSON sidecar, return {tag_name: (start_frame, end_frame)}."""
    with open(json_path) as f:
        data = json.load(f)
    tags = {}
    if "meta" in data and "frameTags" in data["meta"]:
        for tag in data["meta"]["frameTags"]:
            tags[tag["name"]] = (tag["from"], tag["to"])
    return tags
```

### Pattern 4: Animation Frame Selection (Updated)

**What:** Use frame tags from JSON to select u-offset for current animation state.
**When to use:** In entity draw methods that need multi-frame animation.

```python
# frame_width = 16 for standard entities, 32 for boss
# tags = {"idle": (0, 1), "walk": (2, 3), "jump": (4, 4), ...}
tag = self.tags.get(self.state.lower(), (0, 0))
frame_start, frame_end = tag
frame_count = frame_end - frame_start + 1
anim_frame = (pyxel.frame_count // anim_speed) % frame_count
u = (frame_start + anim_frame) * frame_width
```

### Anti-Patterns to Avoid
- **Runtime scale=2:** D-01 explicitly forbids this. Pre-baked 16x16 art, not runtime upscaling. The slime's current `scale=s` for juice-depletion shrink is a separate visual effect and should remain.
- **Modifying collision boxes:** Collision stays 8x8 for all standard entities. Only the draw position changes.
- **Loading PNGs per frame:** Load once at startup, not per draw call. `pyxel.images[N].load()` writes to the image bank permanently.
- **Mixing tile and entity sprites on bank 0:** Bank 0 is exclusively for tiles. Keep strict separation per D-15.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PNG export from pyxres | Custom file format parser | `pyxel.images[N].pget()` + `Image.save()` | Pyxel already has the sprites in memory after `pyxel.load()` |
| JSON parsing | Custom tag parser | Python stdlib `json` module | Aseprite JSON is standard JSON |
| Palette color mapping | Custom RGB-to-index converter | Pyxel's native PNG load (palette-aware) | Verified: save(scale=1) + load() round-trips all 16 colors perfectly |
| Pixel doubling | Pillow/numpy resize | Nested loop: `for dy in range(2): for dx in range(2): new.pset(x*2+dx, y*2+dy, old.pget(x, y))` | Pure Pyxel, no external deps. Simple enough for a migration tool. |

**Key insight:** Pyxel's `Image.save(filename, scale=1)` and `Image.load(x, y, filename)` handle PNG palette encoding/decoding natively. No external image library needed for the entire pipeline.

## Common Pitfalls

### Pitfall 1: Forgetting the Draw Offset at One Site
**What goes wrong:** One entity draws at `(self.x, self.y)` without the bottom-center offset, causing it to appear misaligned -- feet floating above ground or head clipping into ceiling.
**Why it happens:** 13 `pyxel.blt()` call sites across 7 files. Easy to miss one.
**How to avoid:** Create a helper function `draw_entity_sprite(x, y, w, h, bank, u, v, visual_w, visual_h, facing_right, colkey=0)` that applies the offset formula. All entity draw methods call this helper.
**Warning signs:** Entity sprite doesn't line up with tile grid at feet.

### Pitfall 2: Items Use Bank 0 Currently
**What goes wrong:** Items currently reference bank 0 for some sprites (DASH_PICKUP, SHIELD_PICKUP, BOOST_PICKUP, SHIELD_T2) and bank 1 for others (ENERGY, MISSILE). After migration, all entity sprites should be on bank 1.
**Why it happens:** Items were added incrementally, some sharing tile-sheet space on bank 0.
**How to avoid:** Migrate ALL item sprites to bank 1 in the items row. Update the item draw method to always use bank 1.
**Warning signs:** Items rendering as tile graphics or appearing transparent.

### Pitfall 3: Explosion Sprites Are Runtime-Generated
**What goes wrong:** Explosion sprites are drawn via `pyxel.images[1].pset()` loops in `main.py:reset()`, not stored in `game.pyxres`. If you only export from pyxres, explosions will be missing.
**Why it happens:** Explosion sprites were added as code-generated art, not saved to the resource file.
**How to avoid:** `upscale_sprites.py` must regenerate explosion sprites programmatically (matching the main.py:28-45 code), then upscale and save as `effects.png`.
**Warning signs:** Explosions render as empty/transparent sprites.

### Pitfall 4: Boss Collision Size != Visual Size
**What goes wrong:** Boss Mole currently has `self.w = 16, self.h = 16` collision AND visual. After phase 13, visual becomes 32x32 but collision should stay 16x16. The offset formula differs from standard entities.
**Why it happens:** Boss was always 16x16 (2-tile), not 8x8 like standard entities. D-03 says visual becomes 32x32.
**How to avoid:** Boss draw offset: `draw_x = self.x - (32 - 16) // 2 = self.x - 8`, `draw_y = self.y - (32 - 16) = self.y - 16`.
**Warning signs:** Boss sprite offset is double what it should be, or collision box is wrong.

### Pitfall 5: Slime Scale Effect Must Still Work
**What goes wrong:** Slime uses `scale=s` parameter in `pyxel.blt()` for juice-depletion visual shrink. With 16x16 sprites, this still needs to work but the offset calculations change.
**Why it happens:** The slime shrink effect calculates size and offset from the 8x8 base. With 16x16 base, formulas need updating.
**How to avoid:** Update slime's scale offset formula: `size = 16 * s; offset = (16 - size) / 2`. The bottom-center anchor offset should be applied AFTER the scale offset.
**Warning signs:** Slime shrinks toward wrong anchor point (top-left instead of bottom-center).

### Pitfall 6: ChargeProjectile Uses Slime Sprite
**What goes wrong:** `ChargeProjectile.draw()` currently draws the slime sprite at (0, 8) from bank 1. After migration, the u,v coordinates change because bank 1 layout changes.
**Why it happens:** All hardcoded (bank, u, v) coordinates throughout the codebase change with the new layout.
**How to avoid:** Use named constants or manifest lookups for sprite coordinates instead of magic numbers.
**Warning signs:** Charge shot renders as wrong sprite.

### Pitfall 7: Tilemap Image Source Must Stay Bank 0
**What goes wrong:** `pyxel.tilemaps[0].imgsrc = 0` (set in map.py:31) must remain pointing at bank 0. If bank 0 gets entity sprites mixed in, tiles break.
**Why it happens:** `pyxel.bltm()` reads tile visuals from whatever bank `imgsrc` points to.
**How to avoid:** Bank 0 gets ONLY `tiles.png`. Verify `bltm()` still works after migration.
**Warning signs:** Map renders as garbage or entity sprites instead of tiles.

### Pitfall 8: PNG Color Index 0 is Transparent
**What goes wrong:** Pyxel palette color 0 is black. In `pyxel.blt()`, `colkey=0` makes color 0 transparent. If sprites use actual black as a visible color, those pixels disappear.
**Why it happens:** Pyxel's default palette has color 0 = black (#000000).
**How to avoid:** Per D-26, color index 0 IS transparent by convention. No entity should use color 0 for visible pixels. This is already the existing convention -- just maintain it.
**Warning signs:** Black pixels in sprites appear as holes.

## Code Examples

### upscale_sprites.py Core Logic

```python
import pyxel
import json
import os

def upscale_region(src_bank, src_x, src_y, src_w, src_h, dst_img):
    """Pixel-double an 8x8 (or NxN) region into a new Image."""
    for y in range(src_h):
        for x in range(src_w):
            color = pyxel.images[src_bank].pget(src_x + x, src_y + y)
            for dy in range(2):
                for dx in range(2):
                    dst_img.pset(x * 2 + dx, y * 2 + dy, color)

def generate_sidecar(entity_name, frames, frame_w, frame_h, tags):
    """Generate Aseprite-compatible JSON sidecar."""
    sidecar = {
        "meta": {
            "frameTags": [
                {"name": name, "from": start, "to": end, "direction": "forward"}
                for name, (start, end) in tags.items()
            ],
            "size": {"w": frames * frame_w, "h": frame_h}
        }
    }
    return sidecar

def main():
    pyxel.init(128, 128, display_scale=1)
    pyxel.load("assets/game.pyxres")
    # Also inject runtime explosion sprites (matching main.py:28-45)
    inject_explosion_sprites()

    os.makedirs("assets/sprites", exist_ok=True)

    # Example: export player (3 frames at (0,0), (8,0), (16,0) in bank 1)
    num_frames = 3
    player_img = pyxel.Image(16 * num_frames, 16)
    for frame in range(num_frames):
        # Upscale each 8x8 frame to 16x16, placed at (frame*16, 0)
        for y in range(8):
            for x in range(8):
                color = pyxel.images[1].pget(frame * 8 + x, 0 + y)
                for dy in range(2):
                    for dx in range(2):
                        player_img.pset(frame * 16 + x * 2 + dx, y * 2 + dy, color)
    player_img.save("assets/sprites/player.png", 1)

    # Write JSON sidecar
    tags = {"idle": (0, 0), "walk": (1, 2), "jump": (2, 2)}
    sidecar = generate_sidecar("player", num_frames, 16, 16, tags)
    with open("assets/sprites/player.json", "w") as f:
        json.dump(sidecar, f, indent=2)

    # Repeat for each entity...
```

### Updated Entity Draw with Helper

```python
# src/core/sprite_utils.py (new file)
from src.core.constants import SPRITE_SIZE

def draw_sprite(x, y, coll_w, coll_h, bank, u, v,
                visual_w, visual_h, facing_right, colkey=0, scale=None):
    """Draw a sprite with bottom-center anchor offset.

    x, y: collision box top-left
    coll_w, coll_h: collision dimensions
    visual_w, visual_h: sprite pixel dimensions
    """
    import pyxel
    draw_x = x - (visual_w - coll_w) // 2
    draw_y = y - (visual_h - coll_h)
    w = visual_w if facing_right else -visual_w
    pyxel.blt(draw_x, draw_y, bank, u, v, w, visual_h, colkey, scale=scale)
```

### Loading Pipeline Replacement

```python
# In main.py __init__, replacing pyxel.load("assets/game.pyxres")

# Load tile graphics into bank 0
pyxel.images[0].load(0, 0, "assets/sprites/tiles.png")

# Load entity sprites into bank 1
SPRITE_MANIFEST = {
    "player":     (1, 0, 0,   "assets/sprites/player.png"),
    "slime":      (1, 0, 16,  "assets/sprites/slime.png"),
    "snail":      (1, 0, 32,  "assets/sprites/snail.png"),
    "bat":        (1, 0, 48,  "assets/sprites/bat.png"),
    "items":      (1, 0, 64,  "assets/sprites/items.png"),
    "projectile": (1, 0, 80,  "assets/sprites/projectile.png"),
    "effects":    (1, 0, 96,  "assets/sprites/effects.png"),
    "boss":       (1, 0, 128, "assets/sprites/boss.png"),
}
for name, (bank, x, y, path) in SPRITE_MANIFEST.items():
    pyxel.images[bank].load(x, y, path)
```

## Verified Pyxel 2.8.7 API Facts

| API | Signature | Verified Behavior |
|-----|-----------|-------------------|
| `Image.load()` | `load(x, y, filename, include_colors=None)` | Loads PNG pixels into bank at (x,y). Palette round-trip confirmed perfect. |
| `Image.save()` | `save(filename, scale)` | Exports as PNG. `scale=1` gives 1:1 pixel output. Palette colors preserved. |
| `Image.pget()` | `pget(x, y)` | Returns palette index (0-15) at pixel. |
| `Image.pset()` | `pset(x, y, color)` | Sets pixel to palette index. |
| `pyxel.blt()` | `blt(x, y, img, u, v, w, h, colkey=None, rotate=None, scale=None)` | Negative w flips horizontally. `colkey=0` treats color 0 as transparent. `scale` param available for runtime scaling. |
| Image bank size | 256x256 | 3 banks (indices 0, 1, 2). Each 256x256 pixels. |

**Confidence: HIGH** -- All verified by direct execution against Pyxel 2.8.7 on this machine.

## Entity Sprite Inventory

Current sprite locations in bank 1 (all 8x8 unless noted):

| Entity | Bank | Position | Size | Frames | Draw Sites |
|--------|------|----------|------|--------|------------|
| Player | 1 | (0,0), (8,0), (16,0) | 8x8 | 3 (idle, run0, run1) | player.py:772 |
| Slime | 1 | (0,8), (8,8) + (16,8) fused | 8x8 | 3 | slime.py:375, 381, 390 |
| Spit Projectile | 1 | (24,8) | 4x4 | 1 | projectile.py:52 |
| Snail | 1 | (0,16), (8,16) | 8x8 | 2 | enemies.py:97 |
| Bat | 1 | (0,24), (8,24) | 8x8 | 2 | enemies.py:138 |
| Mole Boss | 1 | (0,32), (16,32) | 16x16 | 2 | boss.py:159, 163, 165 |
| Rock (boss proj) | 1 | (32,32) | 8x8 | 1 | boss.py:35 |
| Explosion | 1 | (0,48), (8,48), (16,48) | 8x8 | 3 | effects.py:32 |
| Energy Tank | 1 | (56,0) | 8x8 | 1 | items.py:46 |
| Missile Tank | 1 | (48,8) | 8x8 | 1 | items.py:48 |
| Charge Shot | 1 | uses (0,8) slime sprite | 8x8 | 1 | projectile.py:132 |

Items on bank 0 (need migration to bank 1):

| Item | Bank | Position | Draw Site |
|------|------|----------|-----------|
| Dash Pickup | 0 | (24,0) | items.py:44 |
| Shield Pickup | 0 | (32,0) | items.py:51 |
| Boost Pickup | 0 | (40,0) | items.py:54 |
| Shield T2 | 0 | (48,0) | items.py:57 |

## New Bank 1 Layout (16x16 grid)

After migration, bank 1 uses 16x16 cells:

| Y Offset | Entity | Frame Width | Max Frames (256px wide) | Notes |
|----------|--------|-------------|-------------------------|-------|
| 0 | Player | 16 | 16 | idle, walk0, walk1, jump, fall, dash, drill |
| 16 | Slime | 16 | 16 | idle0, idle1, fused, ... |
| 32 | Snail | 16 | 16 | walk0, walk1 |
| 48 | Bat | 16 | 16 | hang, flap0, flap1 |
| 64 | Items | 16 | 16 | energy, missile, dash, shield, boost, shield_t2 |
| 80 | Projectiles | 16 | 16 | spit, charge_shot, rock |
| 96 | Effects | 16 | 16 | explosion0, explosion1, explosion2 |
| 128 | Boss Mole | 32 | 8 (256/32) | idle0, idle1 (32x32 each, occupies rows 128-159) |

## Entity-Schema Changes

Add `sprite` field to each entity definition:

```json
{
  "Snail": {
    "size": [8, 8],
    "sprite": {
      "sheet": "snail.png",
      "frame_size": [16, 16]
    }
  },
  "BossMole": {
    "size": [16, 16],
    "sprite": {
      "sheet": "boss.png",
      "frame_size": [32, 32]
    }
  }
}
```

Non-breaking: existing `size` field unchanged. New `sprite` field is additive. Schema consumers that don't know about `sprite` continue working.

## tiles.png Export Strategy

Bank 0 currently contains tiles AND some entity sprites (items). For `tiles.png`:

1. Load `game.pyxres` into Pyxel
2. Export the tile region of bank 0 (rows 0-1 at minimum: empty tile, solid, hazard, destructible, gate, switch, cracked_h, cracked_v, water, acid, lava)
3. Save as `assets/sprites/tiles.png` with `scale=1`
4. The tilemap system (`pyxel.bltm()`) reads tiles from bank 0 using `(u, v)` tile coordinates -- these must stay identical

**Critical:** The tile (u,v) coordinates in `constants.py` (TILE_SOLID=(0,1), etc.) index into bank 0 as 8x8 cells. `tiles.png` must preserve this exact layout. Export the full 256x256 bank 0 to be safe, or at minimum the used region.

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
| D-12 | Bottom-center anchor offset formula | unit | `pytest tests/test_sprite_offset.py -x` | Wave 0 |
| D-09 | PNG loading replaces pyxres | smoke | `pytest tests/test_png_loading.py -x` | Wave 0 |
| D-20 | entity-schema.json has sprite metadata | unit | `pytest tests/test_schema_sprite.py -x` | Wave 0 |
| D-01 | All entities draw at 16x16 visual | manual | Visual inspection via `run_and_capture` | N/A |
| D-10 | Tilemap rendering unchanged | smoke | `pytest tests/test_tilemap_intact.py -x` | Wave 0 |

### Wave 0 Gaps
- [ ] `tests/test_sprite_offset.py` -- verify offset formula produces correct draw coords
- [ ] `tests/test_schema_sprite.py` -- verify entity-schema.json has sprite fields for all entities

## Sources

### Primary (HIGH confidence)
- Pyxel 2.8.7 API -- verified by direct Python execution on this machine
- `pyxel.images[N].load(x, y, filename)` -- signature and behavior confirmed
- `pyxel.blt()` signature with `scale` parameter -- confirmed
- PNG palette round-trip -- verified perfect for all 16 colors
- Image bank dimensions: 256x256, 3 banks -- confirmed

### Secondary (MEDIUM confidence)
- Aseprite JSON sidecar format (standard `frameTags` structure) -- based on Aseprite's well-documented export format

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all Pyxel APIs verified by direct execution
- Architecture: HIGH -- bank layout constrained by decisions, fits within 256x256 limits
- Pitfalls: HIGH -- derived from systematic audit of all 13 blt() call sites and the codebase migration path

**Research date:** 2026-03-29
**Valid until:** 2026-04-28 (Pyxel API stable, decisions locked)
