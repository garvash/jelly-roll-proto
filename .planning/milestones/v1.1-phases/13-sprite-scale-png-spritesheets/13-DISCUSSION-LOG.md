# Phase 13: Sprite Scale & PNG Spritesheet Support - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-29
**Phase:** 13-sprite-scale-png-spritesheets
**Areas discussed:** Scaling approach, PNG spritesheet workflow, Collision vs visual offset, Entity-schema metadata, Flip/mirror handling, Tile rendering after pyxres removal, generate_assets.py evolution, Image bank layout, HUD sprite source, Particle/effect sprites, Sprite loading manifest, Aseprite tag/slice conventions

---

## Scaling Approach

### How should entities be rendered at 2x size?

| Option | Description | Selected |
|--------|-------------|----------|
| pyxel.blt scale=2 | Keep 8x8 source sprites, use Pyxel's built-in scale= at draw time | |
| Pre-scaled 16x16 PNGs | Create actual 16x16 sprites. Source art is 16x16 from the start | ✓ |
| Hybrid — scale=2 now, 16x16 art later | Use scale=2 immediately, replace with 16x16 incrementally | |

**User's choice:** Pre-scaled 16x16 PNGs
**Notes:** Full 16x16 detail preferred over runtime scaling.

### Should tiles also scale to 16x16?

| Option | Description | Selected |
|--------|-------------|----------|
| Tiles stay 8x8 | Only entities scale up. No LDtk/tilemap changes needed | ✓ |
| Tiles also scale to 16x16 | Everything scales. Requires full LDtk re-authoring | |

**User's choice:** Tiles stay 8x8

### Art source for initial 16x16 sprites?

| Option | Description | Selected |
|--------|-------------|----------|
| Claude generates placeholder 16x16 art | Programmatic generation at 16x16 | |
| Hand-draw in Aseprite now | User creates art from scratch | |
| Use existing 8x8 + upscale to 16x16 | Mechanically double each pixel to 16x16 | ✓ |

**User's choice:** Upscale existing 8x8 as reference templates
**Notes:** User wants upscaled sheet as reference to work on new sprites.

### Boss visual size?

| Option | Description | Selected |
|--------|-------------|----------|
| 32x32 | Scale both dimensions. Imposing 4x4 tile presence | ✓ |
| 32x16 | Only scale width, keep squat ratio | |

**User's choice:** 32x32

### 1-tile gap collision behavior?

| Option | Description | Selected |
|--------|-------------|----------|
| 8x8 collision is fine | Player fits through 1-tile gaps, visual overhang cosmetic | ✓ |
| Widen collision to 12x12 | Prevent 1-tile gap traversal | |

**User's choice:** 8x8 collision is fine
**Notes:** User asked about gap behavior. Clarified this is standard industry practice (Hollow Knight, Celeste).

### Collision-to-visual offset: production concern?

**User's question:** "This is great for the prototype but feels botchy for the final release. Would you keep this in the final Godot/Unity version?"
**Response:** Yes — this is standard in production. Godot uses Sprite2D node offset from CollisionShape2D, Unity uses SpriteRenderer offset from BoxCollider2D. Same math, different UI.
**Notes:** User reassured that this is not a prototype hack.

---

## PNG Spritesheet Workflow

### How should PNGs be loaded into Pyxel?

| Option | Description | Selected |
|--------|-------------|----------|
| pyxel.images[N].load() | Load each entity PNG directly into image bank | ✓ |
| Keep pyxres + PNG fallback | Dual loading systems | |
| PIL/Pillow pre-process | Combine PNGs at build time | |

**User's choice:** pyxel.images[N].load()

### Animation frame layout in PNGs?

| Option | Description | Selected |
|--------|-------------|----------|
| Horizontal strip | All frames in single row, left to right | ✓ |
| Grid (rows per animation) | Each row is a different animation | |

**User's choice:** Horizontal strip

### Keep game.pyxres for tiles?

| Option | Description | Selected |
|--------|-------------|----------|
| Drop pyxres entirely | Load everything from PNGs | ✓ |
| Keep pyxres for tiles | Tiles in pyxres, entities in PNGs | |

**User's choice:** Drop pyxres entirely

---

## Collision vs Visual Offset

### Anchor point?

| Option | Description | Selected |
|--------|-------------|----------|
| Bottom-center | Collision at bottom-center, visual extends up and to sides | ✓ |
| Center-center | Collision centered, feet float above ground | |
| Per-entity custom | Each entity defines own offset | |

**User's choice:** Bottom-center

### Offset implementation?

| Option | Description | Selected |
|--------|-------------|----------|
| Central SPRITE_SCALE constant | Single constant, formula-derived offset | ✓ |
| Per-entity offset fields | Each entity stores own draw_offset | |

**User's choice:** Central SPRITE_SCALE constant

---

## Entity-Schema Metadata

### Which fields to add?

| Option | Description | Selected |
|--------|-------------|----------|
| sprite_sheet + frame_size | Path to PNG and frame dimensions | ✓ |
| frame_count + animations | Named animation ranges | |
| visual_anchor | Explicit anchor point per entity | |
| collision_size (separate) | Rename size fields for clarity | |

**User's choice:** sprite_sheet + frame_size only

### What does 'size' mean going forward?

| Option | Description | Selected |
|--------|-------------|----------|
| size = collision | Keep as collision dimensions, visual from frame_size | ✓ |
| Rename to collision_size + visual_size | Explicit naming, breaks consumers | |

**User's choice:** size = collision

---

## Flip/Mirror Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Negative width in blt | Keep current pattern, update 8→16 | ✓ |
| Store mirrored frames in PNG | Double the frames, no runtime flip | |

**User's choice:** Negative width in blt (existing pattern)

---

## Tile Rendering After Pyxres Removal

| Option | Description | Selected |
|--------|-------------|----------|
| tiles.png loaded into bank 0 | PNG tile sheet, bltm unchanged | ✓ |
| Keep pyxres just for tiles | Dual loading | |
| Generate tiles from code | Keep programmatic tiles | |

**User's choice:** tiles.png loaded into bank 0

---

## generate_assets.py Evolution

| Option | Description | Selected |
|--------|-------------|----------|
| Becomes upscale_sprites.py | One-time migration tool outputting PNGs + JSONs + tiles.png | ✓ |
| Delete entirely | Hand-create PNGs from scratch | |
| Keep as fallback | Alongside PNGs | |

**User's choice:** Becomes upscale_sprites.py

---

## Image Bank Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Bank 0 = tiles, Bank 1 = entities | Same split as today, Bank 2 reserved | ✓ |
| Bank 0 = tiles, Bank 1 = small, Bank 2 = large | Split by size | |

**User's choice:** Bank 0 = tiles, Bank 1 = all entities, Bank 2 = reserved

---

## HUD Sprite Source

| Option | Description | Selected |
|--------|-------------|----------|
| Stay as draw primitives | rect/circ calls, no PNG needed | ✓ |
| PNG icons in bank 2 | Polished icons, adds scope | |

**User's choice:** Stay as draw primitives

---

## Particle/Effect Sprites

| Option | Description | Selected |
|--------|-------------|----------|
| Effects 16x16, particles stay 1px | Explosions scale, debris stays tiny | ✓ |
| Everything stays 8x8/1px | No scaling for effects | |
| Everything scales to 16x16 | Uniform scale | |

**User's choice:** Effects 16x16, particles stay 1px

---

## Sprite Loading Manifest

| Option | Description | Selected |
|--------|-------------|----------|
| Hardcoded in main.py | Dict mapping names to (bank, x, y, path) | ✓ |
| JSON manifest file | Separate data file | |
| Auto-discover from directory | Scan assets/sprites/*.png | |

**User's choice:** Hardcoded in main.py

---

## Aseprite Tag/Slice Conventions

### Animation tag → frame index mapping?

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed tag order convention | Code indexes by known offsets | |
| JSON sidecar per sprite | Aseprite JSON export with frameTags | ✓ |

**User's choice:** JSON sidecar per sprite
**Notes:** User is experienced with Aseprite animation tags. Aseprite natively exports JSON for animation reconstruction.

### Generate placeholder JSONs in upscale script?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, generate JSONs | Both .png and .json per entity | ✓ |
| No, PNGs only | JSON comes later with real art | |

**User's choice:** Yes, generate JSONs

---

## Claude's Discretion

- Exact row layout within bank 1 (which entity at which Y offset)
- JSON sidecar parsing implementation details
- upscale_sprites.py implementation approach
- Animation state machine refactor details per entity class

## Deferred Ideas

None — discussion stayed within phase scope
