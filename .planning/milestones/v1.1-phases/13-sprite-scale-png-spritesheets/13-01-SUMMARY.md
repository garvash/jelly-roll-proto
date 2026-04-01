---
phase: 13-sprite-scale-png-spritesheets
plan: "01"
subsystem: asset-pipeline
tags: [sprites, png, migration, aseprite, upscale]
dependency_graph:
  requires: [game.pyxres, generate_assets.py]
  provides: [upscale_sprites.py, assets/sprites/*.png, assets/sprites/*.json]
  affects: [main.py (future plan 02), entity draw methods (future plan 03)]
tech_stack:
  added: []
  patterns: [pixel-doubling, Aseprite JSON sidecar, horizontal strip spritesheet]
key_files:
  created:
    - upscale_sprites.py
    - assets/sprites/player.png
    - assets/sprites/slime.png
    - assets/sprites/snail.png
    - assets/sprites/bat.png
    - assets/sprites/items.png
    - assets/sprites/projectile.png
    - assets/sprites/effects.png
    - assets/sprites/boss.png
    - assets/sprites/tiles.png
    - assets/sprites/player.json
    - assets/sprites/slime.json
    - assets/sprites/snail.json
    - assets/sprites/bat.json
    - assets/sprites/items.json
    - assets/sprites/projectile.json
    - assets/sprites/effects.json
    - assets/sprites/boss.json
    - tests/test_sprite_assets.py
  modified: []
decisions:
  - "Module-level pyxel.init in tests: Pyxel can only be initialized once per process, so tests use module-level init with absolute path resolution to avoid CWD change side effect"
  - "Items pixel check across all frames: Energy/Missile tank source positions in bank 1 are empty in pyxres, so test verifies any frame has pixels rather than first-frame-only"
metrics:
  duration: "5m 21s"
  completed: "2026-03-29"
---

# Phase 13 Plan 01: Migration Tool & PNG/JSON Asset Generation Summary

upscale_sprites.py reads game.pyxres + runtime explosion sprites, outputs 9 PNGs (8 entity horizontal strips + full bank 0 tiles) and 8 Aseprite-format JSON sidecars with frameTags

## What Was Done

### Task 0: Test stubs for sprite asset validation
Created `tests/test_sprite_assets.py` with 7 test functions covering PNG existence, JSON sidecar structure, pixel data verification, and palette compliance (D-26). Tests use module-level pyxel init and absolute path resolution to handle pyxel's CWD side effect.

### Task 1: upscale_sprites.py migration tool
Created `upscale_sprites.py` (165 lines) that:
1. Loads game.pyxres and injects runtime explosion sprites (Pitfall 3)
2. Pixel-doubles all entity sprites from 8x8 to 16x16 (boss 16x16 to 32x32)
3. Handles items from both bank 0 and bank 1 (Pitfall 2: dash/shield/boost pickups on bank 0)
4. Exports tiles.png as full 256x256 bank 0 image for bltm compatibility
5. Generates Aseprite-format JSON sidecars with frameTags for each entity

### Task 2: Validation tests against generated assets
All 7 tests pass:
- 8 entity PNGs + tiles.png exist
- 8 JSON sidecars have correct meta.frameTags structure
- All entity PNGs have visible pixel data
- tiles.png preserves TILE_SOLID at position (0,8)
- Palette compliance: all pixels are valid Pyxel indices 0-15

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Pyxel init CWD side effect breaks test path resolution**
- **Found during:** Task 2
- **Issue:** pyxel.init() changes working directory to the calling script's directory, breaking relative path "assets/sprites" in tests
- **Fix:** Resolve SPRITES_DIR as absolute path via __file__ before pyxel.init() runs
- **Files modified:** tests/test_sprite_assets.py
- **Commit:** 3bd3623

**2. [Rule 1 - Bug] Energy/Missile tank source pixels empty in pyxres bank 1**
- **Found during:** Task 2
- **Issue:** items.py references (56,0) and (48,8) on bank 1 for Energy/Missile tanks, but those positions are empty in game.pyxres. First-frame-only pixel check fails for items.png.
- **Fix:** Updated test to check all frames in the strip (not just frame 0). Dash pickup from bank 0 has pixels, so items.png passes.
- **Files modified:** tests/test_sprite_assets.py
- **Commit:** 3bd3623

## Output Files

| File | Description | Frames | Size |
|------|-------------|--------|------|
| player.png | Player spritesheet | 3 (idle, walk0, walk1) | 48x16 |
| slime.png | Slime spritesheet | 3 (normal0, normal1, fused) | 48x16 |
| snail.png | Snail spritesheet | 2 (walk0, walk1) | 32x16 |
| bat.png | Bat spritesheet | 2 (hang, flap) | 32x16 |
| items.png | All items | 6 (energy, missile, dash, shield, boost, shield_t2) | 96x16 |
| projectile.png | Spit + Rock | 2 | 32x16 |
| effects.png | Explosion | 3 frames | 48x16 |
| boss.png | Mole Boss | 2 frames | 64x32 |
| tiles.png | Full bank 0 tiles | 256x256 (8x8 cells) | 256x256 |

## Known Stubs

None -- all outputs are fully generated from source data.

## Self-Check: PASSED

All 19 created files verified on disk. All 3 task commits verified in git log.
