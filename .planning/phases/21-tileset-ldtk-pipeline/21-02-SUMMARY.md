---
phase: 21-tileset-ldtk-pipeline
plan: 02
subsystem: level, entities
tags: [pyxel, tilemap, collision, tile-size]

requires:
  - phase: 21-01
    provides: Migrated LDtk data at 16px grid, tilesets/cavern.png

provides:
  - map.py uses TILE_SIZE and TILES_PER_ROW constants for all grid math
  - 2x2 tilemap cell helpers for 16px tiles in Pyxel's 8px tilemap system
  - Player hitbox updated from 8x8 to 10x14 for 16px tile alignment
  - Slime and enemy collision snap updated from hardcoded 8 to TILE_SIZE

affects: [entities, level-rendering, collision]

key-files:
  created: []
  modified:
    - src/level/map.py
    - main.py
    - src/entities/player.py
    - src/entities/slime.py
    - src/entities/enemies.py
    - tests/test_tilemap.py

key-decisions:
  - "Pyxel tilemaps are hardcoded 8px — use 2x2 cell blocks for 16px tiles"
  - "Player hitbox 8x8 → 10x14 to reduce sprite-ceiling clipping with 16px tiles"
  - "_pset_tile/_pget_tile/_clear_tilemap helpers centralize the 2x2 mapping"

patterns-established:
  - "2x2 tilemap pattern: all tilemap pset/pget goes through _pset_tile/_pget_tile helpers"
  - "Entity collision snap must use TILE_SIZE constant, never hardcoded pixel values"
---

## What was done

### Task 1: Update map.py hardcoded grid values
- Replaced all `// 8`, `* 8`, `% 32`, `// 32` with `TILE_SIZE` and `TILES_PER_ROW`
- Added `TILES_PER_ROW = 256 // TILE_SIZE` module constant

### Task 2: Visual verification + runtime fixes
- Discovered Pyxel tilemaps are hardcoded to 8px cells — `bltm` renders each cell as 8x8
- Added `_pset_tile`, `_pget_tile`, `_clear_tilemap` helpers that write/read 2x2 blocks
- Updated all tilemap pset/pget calls across load_from_ldtk_simplified, load_autotiles_from_ldtk, load_from_ldtk, load_from_tiled, remove_tile, restore_tile, find_tile, get_tile
- Updated main.py tilemap 1 clear to use _clear_tilemap
- Updated player hitbox from 8x8 to 10x14 (reduces ceiling sprite clipping)
- Fixed slime.py and enemies.py collision snap from hardcoded `// 8` to `// TILE_SIZE`
- Visual verification: tiles render correctly, no gaps, collision aligned

## Deviations
- **2x2 tilemap pattern** was not in the original plan — discovered during visual verification that Pyxel has no configurable tile size
- **Entity hitbox/snap fixes** were out of original plan scope but required for correct gameplay after tile size change

## Self-Check: PASSED
- [x] map.py uses TILE_SIZE for all grid math
- [x] Tilemap renders at correct zoom (not 2x2)
- [x] Visual and collision tiles aligned (4577 each)
- [x] Player ceiling collision reasonable
- [x] All 21 related tests pass
