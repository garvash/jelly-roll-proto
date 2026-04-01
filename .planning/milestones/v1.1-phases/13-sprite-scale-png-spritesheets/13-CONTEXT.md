# Phase 13: Sprite Scale & PNG Spritesheet Support - Context

**Gathered:** 2026-03-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Draw all entities at 2x visual scale (16x16 rendered, 8x8 collision) for better readability at 320x176, replace Pyxel image bank sprites with PNG spritesheet loading (Aseprite workflow), and update entity-schema.json with sprite metadata for the map converter. Tiles stay 8x8. HUD stays as draw primitives.

</domain>

<decisions>
## Implementation Decisions

### Scaling Approach
- **D-01:** All entity sprites are pre-scaled 16x16 art (not runtime `scale=2`). Source art is 16x16 from the start.
- **D-02:** Tiles stay 8x8 — only entities scale up. Entities visually span 2x2 tile cells.
- **D-03:** Boss scales to 32x32 visual (currently 16x8 collision, becomes 32x32 visual).
- **D-04:** Collision boxes remain 8x8 for standard entities. 1-tile-gap traversal is fine — visual overhang is cosmetic (standard industry practice).
- **D-05:** Initial sprites are auto-upscaled from existing 8x8 (each pixel becomes 2x2 block) as reference templates. User will hand-draw improved 16x16 replacements on top of these.

### PNG Spritesheet Workflow
- **D-06:** One PNG per entity — `assets/sprites/player.png`, `assets/sprites/slime.png`, etc. Not a combined atlas.
- **D-07:** Horizontal strip layout — all animation frames in a single row, left to right. Frame N starts at `(N * frame_width, 0)`.
- **D-08:** JSON sidecar per sprite (Aseprite format) — `player.json`, `slime.json`, etc. Contains `frameTags` with animation name → frame range mapping. Code reads JSON to resolve tag names to frame offsets.
- **D-09:** Load PNGs via `pyxel.images[N].load()` — replaces `pyxel.load("assets/game.pyxres")` entirely. No more pyxres dependency.
- **D-10:** `tiles.png` provides tile graphics for image bank 0. Same 8x8 cell layout as the current pyxres tile sheet. `pyxel.bltm()` pipeline unchanged.
- **D-11:** Drop `game.pyxres` entirely. All graphics come from PNGs.

### Collision vs Visual Offset
- **D-12:** Bottom-center anchor — collision box sits at bottom-center of visual sprite. Feet align with ground. Extra visual pixels extend upward and to each side. Formula: `draw_x = collision_x - (visual_w - collision_w) // 2`, `draw_y = collision_y - (visual_h - collision_h)`.
- **D-13:** Central `SPRITE_SCALE = 2` constant in `constants.py`. All standard entities use the same offset formula derived from this constant.

### Flip/Mirror Handling
- **D-14:** Keep negative-width flip in `pyxel.blt()` (current pattern). Pass `-16` as width to flip horizontally. Only right-facing sprites in PNGs.

### Image Bank Layout
- **D-15:** Bank 0 = tiles (tiles.png, 8x8 cells). Bank 1 = all entity sprites (16x16/32x32 frames). Bank 2 = reserved (future HUD icons, etc).
- **D-16:** Sprite loading manifest hardcoded in `main.py` as a dict mapping entity names to `(bank, x, y, path)`. Simple loop loads all PNGs at startup.

### Effects & Particles
- **D-17:** Explosion/effect sprites scale to 16x16 (from effects.png). Particles stay as single-pixel `pyxel.pset()` — tiny debris provides visual contrast against larger sprites.

### HUD
- **D-18:** HUD icons (HP pips, juice meter) stay as `pyxel.rect()`/`pyxel.circ()` draw primitives. PNG HUD icons deferred to a future art polish phase.

### generate_assets.py Evolution
- **D-19:** `generate_assets.py` becomes `upscale_sprites.py` — a one-time migration tool that reads current 8x8 programmatic sprites, outputs 16x16 PNGs (2x pixel doubling) + JSON sidecars + tiles.png. Run once, then PNGs become source of truth.

### Entity-Schema Metadata
- **D-20:** Add `sprite` object to each entity in `entity-schema.json` with `sheet` (PNG filename) and `frame_size` ([w, h]) fields.
- **D-21:** Existing `size` field remains collision dimensions (e.g., [8, 8]). Visual size is derived from `sprite.frame_size`. No breaking change to schema consumers.

### Aseprite Artist Contract
- **D-22:** Export as horizontal strip PNG + JSON sidecar (Aseprite "Array" sheet type with JSON data output).
- **D-23:** Animation tags must match game state names (idle, walk, jump, fall, dash, drill, etc.). Code resolves tags by name from JSON.
- **D-24:** Frame size: 16x16 for standard entities, 32x32 for boss.
- **D-25:** Direction: right-facing only. Code flips via negative blt width.
- **D-26:** Palette: Pyxel's 16 colors, index 0 = transparent.

### Claude's Discretion
- Exact row layout within bank 1 (which entity goes at which Y offset)
- JSON sidecar parsing implementation details (loader class vs inline)
- upscale_sprites.py implementation approach (Pillow, pure Pyxel, etc.)
- Animation state machine refactor details per entity class

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Current Sprite System
- `generate_assets.py` — Current programmatic sprite generator (to be replaced by upscale_sprites.py)
- `main.py:19-45` — Current asset loading (pyxel.load, pyxel.images[1].pset for HUD circles)
- `main.py:529` — Tilemap rendering via pyxel.bltm()
- `assets/game.pyxres` — Current sprite resource file (to be removed)

### Entity Draw Sites (all pyxel.blt calls to update)
- `src/entities/player.py:772` — Player draw (bank 1, 8x8)
- `src/entities/slime.py:375,381,390` — Slime draw (bank 1, 8x8, already uses scale=)
- `src/entities/enemies.py:97,138` — Snail and Bat draw (bank 1, 8x8)
- `src/entities/boss.py:35,159,163,165` — Mole Boss draw (bank 1, 16x8)
- `src/entities/items.py:60` — Item draw (bank 0/1, 8x8)
- `src/entities/projectile.py:52,132` — Spit and ChargeProjectile draw (bank 1, 8x4/8x8)
- `src/entities/effects.py:32` — Explosion draw (bank 1, 8x8)

### Tilemap System
- `src/level/map.py` — LevelMap class using pyxel.tilemaps[0] with image bank 0 for tiles
- `src/core/constants.py` — TILE_SIZE, TILE_SOLID, TILE_EMPTY, and screen constants from Phase 12

### Schema Contract
- `assets/entity-schema.json` — Shared schema with PML-to-LDtk converter (add sprite metadata)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/core/constants.py` — Central constants file; add SPRITE_SCALE here
- Slime already uses `scale=` param in pyxel.blt — pattern exists for scaled drawing
- `pyxel.images[N].load(x, y, path)` — Built-in PNG loading, no external deps needed

### Established Patterns
- All entities use `pyxel.blt(self.x, self.y, bank, u, v, w, h, colkey)` for drawing
- Facing direction via negative width: `w = self.w if self.facing_right else -self.w`
- Animation frame selection via `self.frame // speed * frame_width` for u-offset
- Tilemap rendering via `pyxel.bltm()` referencing image bank 0

### Integration Points
- `main.py` init — Replace `pyxel.load()` with PNG loading loop
- Every entity `draw()` method — Update blt coordinates for 16x16 + bottom-center offset
- `entity-schema.json` — Add sprite metadata fields
- `generate_assets.py` → `upscale_sprites.py` — Migration tool

</code_context>

<specifics>
## Specific Ideas

- Auto-upscaled 16x16 PNGs serve as **reference templates** for the artist to draw over — not final art
- Aseprite JSON sidecar is the native export format — no custom tooling needed for the artist workflow
- Artist is experienced with Aseprite animation tags — pipeline should honor that workflow naturally

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 13-sprite-scale-png-spritesheets*
*Context gathered: 2026-03-29*
