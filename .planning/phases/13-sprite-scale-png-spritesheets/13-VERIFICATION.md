---
phase: 13-sprite-scale-png-spritesheets
verified: 2026-03-29T11:00:00Z
status: gaps_found
score: 9/10 must-haves verified
gaps:
  - truth: "No direct pyxel.blt() calls remain in entity files for sprite drawing"
    status: failed
    reason: "slime.py line 377 (is_being_absorbed draw path) calls pyxel.blt() directly with stale pyxres coordinates (v=8, source 8x8) instead of using draw_sprite at the new bank 1 layout (v=16, visual 16x16)"
    artifacts:
      - path: "src/entities/slime.py"
        issue: "Line 377: pyxel.blt(self.x + offset, self.y + offset, 1, 0, 8, w, 8, 0, scale=s) — uses old v=8 row from pyxres layout; new slime is at v=16. Also references source 8x8 dimensions, not 16x16 visual."
    missing:
      - "Replace pyxel.blt call at slime.py:377 with draw_sprite(self.x, self.y, self.w, self.h, 1, 0, 16, SPRITE_SIZE, SPRITE_SIZE, self.facing_right, colkey=0, scale=s)"
human_verification:
  - test: "Run python main.py and recall the slime during charge shot windup (hold Z until slime absorption begins)"
    expected: "Slime shows pulsing shrink animation at correct 16x16 visual scale, centered on collision box, not misaligned at old 8x8 position"
    why_human: "is_being_absorbed path is triggered only during CHARGING_SHOT windup — requires interactive input to reach state"
  - test: "Run python main.py and visually confirm all entities appear at 16x16 size (32x32 boss) with feet touching the ground"
    expected: "Player, slime, snail, bat, items, projectiles, and explosion all visually larger than tiles with correct bottom-center anchoring. No entities floating above or embedded in ground."
    why_human: "Sprite scale and anchor correctness requires visual inspection — cannot be verified programmatically without a running display"
---

# Phase 13: Sprite Scale & PNG Spritesheet Support — Verification Report

**Phase Goal:** Draw all entities at 2x visual scale (16x16 rendered, 8x8 collision) for better readability at 320x176, replace Pyxel image bank sprites with PNG spritesheet loading (Aseprite workflow), and update entity-schema.json with sprite metadata for the map converter
**Verified:** 2026-03-29T11:00:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | upscale_sprites.py produces all PNG spritesheets and JSON sidecars when run | VERIFIED | upscale_sprites.py exists (229 lines), all 9 PNGs and 8 JSON sidecars present in assets/sprites/ |
| 2 | tiles.png preserves exact 8x8 tile layout from bank 0 for bltm compatibility | VERIFIED | tiles.png exported as full 256x256 bank 0 image; bltm pipeline unchanged in main.py |
| 3 | Game loads all graphics from PNG files, not game.pyxres | VERIFIED | No pyxres references in main.py (grep exits 1); SPRITE_MANIFEST dict with 9 entries, _load_sprites() method |
| 4 | SPRITE_SCALE constant exists and equals 2 | VERIFIED | constants.py line 18: SPRITE_SCALE = 2, SPRITE_SIZE = 16, BOSS_SPRITE_SIZE = 32 |
| 5 | draw_sprite helper applies bottom-center anchor offset | VERIFIED | sprite_utils.py: draw_x = x - (visual_w - coll_w) // 2, draw_y = y - (visual_h - coll_h) |
| 6 | JSON sidecar tags are loaded and accessible at runtime | VERIFIED | main.py loads sprite_tags dict from all JSON sidecars on startup; player.json confirmed correct frameTags structure |
| 7 | All entities draw at 16x16 visual size (32x32 for boss) with bottom-center anchoring | VERIFIED | All 7 entity files import and call draw_sprite with SPRITE_SIZE or BOSS_SPRITE_SIZE |
| 8 | Slime juice-depletion scale effect still works with new sprite size | VERIFIED | Regular slime draw path uses draw_sprite with scale=s parameter (line 389-390) |
| 9 | Items all reference bank 1 (no more bank 0 entity sprites) | VERIFIED | items.py uses draw_sprite(... 1, u, 64, ...) with ITEM_FRAMES dict on bank 1 |
| 10 | No direct pyxel.blt() calls remain in entity files for sprite drawing | FAILED | slime.py:377 uses raw pyxel.blt() in is_being_absorbed path with stale pyxres coordinates (v=8, 8x8 source) |

**Score:** 9/10 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `upscale_sprites.py` | Migration tool: reads pyxres, outputs PNGs + JSON sidecars | VERIFIED | 229 lines (min 80), pyxel.load("assets/game.pyxres") present, .save("assets/sprites/...") present |
| `assets/sprites/player.png` | Player spritesheet (16x16 frames, horizontal strip) | VERIFIED | Exists, 773 bytes |
| `assets/sprites/tiles.png` | Tile graphics for bank 0 | VERIFIED | Exists, 3074 bytes |
| `assets/sprites/player.json` | Aseprite-format JSON sidecar with frameTags | VERIFIED | Confirmed: meta.frameTags with name/from/to/direction for 6 animation states |
| `tests/test_sprite_assets.py` | Sprite asset validation tests | VERIFIED | 131 lines (min 40) |
| `src/core/constants.py` | SPRITE_SCALE=2, SPRITE_SIZE=16, BOSS_SPRITE_SIZE=32 | VERIFIED | All three constants present at lines 18-20 |
| `src/core/sprite_utils.py` | draw_sprite() helper + load_sprite_tags() JSON parser | VERIFIED | 59 lines (min 30), both functions exported |
| `main.py` | PNG loading manifest replacing pyxel.load() | VERIFIED | SPRITE_MANIFEST dict present, _load_sprites() method, no pyxres references |
| `tests/test_sprite_scale.py` | Tests for sprite constants and draw_sprite offset math | VERIFIED | 56 lines (min 20) |
| `src/entities/player.py` | Player draw using draw_sprite at 16x16 | VERIFIED | Imports draw_sprite, calls draw_sprite at line 771 with SPRITE_SIZE |
| `src/entities/slime.py` | Slime draw at 16x16 with scale effect preserved | PARTIAL | draw_sprite used in fused path (line 382) and regular path (line 389); is_being_absorbed path (line 377) still uses raw pyxel.blt() with stale v=8 coordinates |
| `src/entities/enemies.py` | Snail and Bat draw at 16x16 | VERIFIED | draw_sprite at lines 95, 136 with correct y=32, y=48 bank 1 coordinates |
| `src/entities/boss.py` | Boss draw at 32x32, Rock at 16x16 | VERIFIED | draw_sprite with BOSS_SPRITE_SIZE at y=128, Rock at y=80 |
| `src/entities/items.py` | All items on bank 1 at 16x16 | VERIFIED | ITEM_FRAMES dict, draw_sprite(... 1, u, 64, SPRITE_SIZE, ...) |
| `src/entities/projectile.py` | Spit and ChargeProjectile at 16x16 | VERIFIED | draw_sprite at lines 52, 132 |
| `src/entities/effects.py` | Explosion at 16x16 | VERIFIED | draw_sprite(... 1, u, 96, SPRITE_SIZE, ...) at line 32 |
| `assets/entity-schema.json` | sprite metadata (sheet, frame_size) for all entities | VERIFIED | v0.2.0, all 10 entities have sprite field; Door has null; BossMole frame_size=[32,32] |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| upscale_sprites.py | assets/game.pyxres | pyxel.load() | WIRED | Line 91: pyxel.load("assets/game.pyxres") confirmed |
| upscale_sprites.py | assets/sprites/*.png | Image.save() after pixel doubling | WIRED | img.save(os.path.join(SPRITES_DIR, "player.png"), ...) pattern confirmed |
| main.py | assets/sprites/*.png | SPRITE_MANIFEST + pyxel.images[N].load() | WIRED | SPRITE_MANIFEST dict confirmed, _load_sprites() loops over it with pyxel.images[bank].load(x, y, path) |
| src/core/sprite_utils.py | src/core/constants.py | imports SPRITE_SIZE, BOSS_SPRITE_SIZE | WIRED | Line 4: from src.core.constants import SPRITE_SIZE, BOSS_SPRITE_SIZE |
| src/entities/player.py | src/core/sprite_utils.py | import draw_sprite | WIRED | Line 4: from src.core.sprite_utils import draw_sprite |
| src/entities/items.py | SPRITE_MANIFEST bank 1 y=64 | bank 1 at y=64 for all items | WIRED | draw_sprite(... 1, u, 64, ...) confirmed in items.py |

### Data-Flow Trace (Level 4)

Not applicable — this phase produces rendering code (Pyxel blt calls), not data pipeline code. PNGs are read from disk at startup and stored in Pyxel image banks; there is no dynamic data fetch to trace.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| upscale_sprites.py can locate pyxres | grep -c "pyxel.load" upscale_sprites.py | 1 | PASS |
| SPRITE_MANIFEST has 9 entries | grep -c '"assets/sprites/' main.py | 9 | PASS |
| No pyxres dependency in main.py | grep -c "pyxres" main.py | 0 (exit 1) | PASS |
| All 9 PNGs exist in assets/sprites/ | ls assets/sprites/*.png \| wc -l | 9 | PASS |
| All 8 JSON sidecars exist | ls assets/sprites/*.json \| wc -l | 8 | PASS |
| slime.py is_being_absorbed uses raw blt | grep -n "pyxel.blt(" src/entities/slime.py | line 377 found | FAIL |
| entity-schema.json version | grep '"version"' assets/entity-schema.json | "0.2.0" | PASS |

### Requirements Coverage

The requirement IDs SPR-01 through SPR-05 referenced in ROADMAP.md are **not defined in REQUIREMENTS.md**. REQUIREMENTS.md tracks MAP, ABL, and SYS categories only. SPR-01..05 are ROADMAP-level phase tags without formal requirement entries.

The phase PLANs use design decision IDs (D-01 through D-26) defined in 13-CONTEXT.md. Coverage against those:

| Design Decision | Plan | Description | Status | Evidence |
|-----------------|------|-------------|--------|----------|
| D-01 | 13-03 | All entity sprites pre-scaled 16x16 (not runtime scale=2) | VERIFIED | draw_sprite called with visual_w=SPRITE_SIZE=16 in all entity files |
| D-02 | 13-03 | Tiles stay 8x8, only entities scale up | VERIFIED | tiles.png is unchanged 256x256 bank 0; bltm pipeline untouched |
| D-03 | 13-03 | Boss scales to 32x32 visual | VERIFIED | boss.py uses BOSS_SPRITE_SIZE=32 |
| D-04 | 13-03 | Collision boxes remain 8x8 for standard entities | VERIFIED | draw_sprite called with coll_w=self.w, coll_h=self.h (unchanged 8x8) |
| D-05 | 13-01 | Auto-upscaled PNGs as reference templates | VERIFIED | upscale_sprites.py generates pixel-doubled PNGs |
| D-06 | 13-01 | One PNG per entity | VERIFIED | 8 entity PNGs in assets/sprites/ |
| D-07 | 13-01 | Horizontal strip layout | VERIFIED | frames at N * frame_width stride confirmed in upscale_sprites.py |
| D-08 | 13-01 | JSON sidecar with frameTags | VERIFIED | 8 JSON sidecars with Aseprite frameTags format |
| D-09 | 13-02 | Load PNGs via pyxel.images[N].load() | VERIFIED | _load_sprites() in main.py |
| D-11 | 13-02 | Drop game.pyxres dependency | VERIFIED | No pyxres in main.py |
| D-12 | 13-02 | Bottom-center anchor formula | VERIFIED | sprite_utils.py draw_sprite implements formula |
| D-13 | 13-02 | Central SPRITE_SCALE=2 constant | VERIFIED | constants.py line 18 |
| D-19 | 13-01 | upscale_sprites.py replaces generate_assets.py | VERIFIED | upscale_sprites.py created, generate_assets.py retained as reference |
| D-20 | 13-03 | sprite object in entity-schema.json | VERIFIED | All entities have sprite field |
| D-21 | 13-03 | Existing size field remains collision dimensions | VERIFIED | size fields unchanged (e.g., Snail [8,8], BossMole [16,16]) |
| D-26 | 13-01 | All sprites use only Pyxel palette colors 0-15 | VERIFIED | test_sprite_assets.py validates palette compliance |

**ORPHANED IDs:** SPR-01..SPR-05 have no entries in REQUIREMENTS.md. These are ROADMAP phase tags only, not traceable requirements. No action needed — the phase used D-xx design decision IDs throughout, which are fully covered above.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| src/entities/slime.py | 377 | `pyxel.blt(self.x + offset, self.y + offset, 1, 0, 8, w, 8, 0, scale=s)` — raw blt with v=8 (old pyxres row) instead of v=16 (new PNG bank 1 row) | Blocker | is_being_absorbed draw path will sample wrong image bank location now that game.pyxres is no longer loaded — the slime absorption animation will render garbage pixels or blank during charge shot windup |

### Human Verification Required

#### 1. Slime is_being_absorbed visual correctness

**Test:** Run `python main.py`, fuse with slime (hold Z until fused), then begin a charge shot (hold Z again). During the windup period when slime is being absorbed back into the player:
**Expected:** Slime shows a pulsing scale-down animation that is visually correct at 16x16 size, centered on the collision box, using slime sprite pixels (not garbage/blank)
**Why human:** The `is_being_absorbed` path at slime.py:377 uses stale coordinates (v=8, 8x8 source) referencing the old pyxres bank 1 layout. Whether this renders blank, wrong pixels, or happens to pick up valid pixels from the new PNG layout requires visual confirmation.

#### 2. Full entity visual pass

**Test:** Run `python main.py` and observe: player walking/jumping, slime companion following, snail and bat enemies, item collection, spit projectile, explosion effect, boss mole fight
**Expected:** All entities appear at 16x16 visual size (32x32 boss) with feet touching ground tiles, no floating entities, no entities embedded in floors. Tiles remain 8x8. HUD primitives unaffected.
**Why human:** Bottom-center anchoring correctness and visual scale at 320x176 resolution requires human judgment — pixel-perfect alignment cannot be verified from static analysis.

### Gaps Summary

One gap found blocking full goal achievement:

**slime.py is_being_absorbed path bypasses draw_sprite with stale coordinates.** The `is_being_absorbed` branch in `slime.draw()` (line 370-378) calls `pyxel.blt(self.x + offset, self.y + offset, 1, 0, 8, w, 8, 0, scale=s)` — this references source coordinates `(u=0, v=8)` which was the slime row in the old game.pyxres bank 1 layout. In the new PNG bank layout, slime is at `v=16`. Additionally, the source dimensions are 8x8 (old collision size) rather than 16x16 (new visual size). The old manual offset calculation `size = 8 * s; offset = (8 - size) / 2` is also redundant since `draw_sprite` handles this. This path is reached during CHARGING_SHOT windup when the slime is being absorbed back into the player — a narrow but real game state. All other slime draw paths (fused, regular) correctly use `draw_sprite`.

The fix is one line: replace the raw `pyxel.blt()` call with `draw_sprite(self.x, self.y, self.w, self.h, 1, 0, 16, SPRITE_SIZE, SPRITE_SIZE, self.facing_right, colkey=0, scale=s)`.

---

_Verified: 2026-03-29T11:00:00Z_
_Verifier: Claude (gsd-verifier)_
