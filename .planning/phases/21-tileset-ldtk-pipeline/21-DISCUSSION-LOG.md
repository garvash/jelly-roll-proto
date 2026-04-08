# Phase 21: Tileset & LDtk Pipeline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md -- this log preserves the alternatives considered.

**Date:** 2026-04-08
**Phase:** 21-tileset-ldtk-pipeline
**Areas discussed:** Tileset image strategy, LDtk project reconfiguration, Auto-tile coordinate pipeline, File roles & cleanup, Tileset upscale method, Verification strategy, Simplified export regen, Tileset tile_coords update, Migration script scope, Entity layer grid, File organization (tilesets/ folder), Background layer handling

---

## Tileset Image Strategy

### Tile Art Approach

| Option | Description | Selected |
|--------|-------------|----------|
| Upscale 2x (Recommended) | Nearest-neighbor upscale, preserves pixel art, no new art needed | ✓ |
| New 16px art | Fresh 16px tiles from scratch | |
| You decide | Claude picks pragmatic approach | |

**User's choice:** Upscale 2x
**Notes:** None

### Source of Truth File

| Option | Description | Selected |
|--------|-------------|----------|
| tileset.png (256x256) | LDtk-native tileset, update entity-schema to reference it | ✓ |
| tiles.png (96x80) | Smaller Aseprite-exported tileset | |
| You decide | Claude picks cleanest integration | |

**User's choice:** tileset.png (256x256)
**Notes:** Later revised -- tiles.png became the new complete tileset at 256x256, consolidated into tilesets/cavern.png

---

## LDtk Project Reconfiguration

### Migration Method

| Option | Description | Selected |
|--------|-------------|----------|
| Script-patch JSON (Recommended) | Programmatically update LDtk files, reproducible | ✓ |
| Edit in LDtk editor | Manual editing, re-export | |
| You decide | Claude picks | |

**User's choice:** Script-patch first to test
**Notes:** User noted: "we need to update the pml-to-ldtk to match the new specs so the newly generated maps will work out of the box"

### Auto-Layer Rules

| Option | Description | Selected |
|--------|-------------|----------|
| Rules survive scaling | Rules reference IntGrid neighbors, work at any grid size | ✓ |
| Rules need rework | Rules authored for 8px granularity | |
| You decide | Claude investigates | |

**User's choice:** Rules survive scaling

---

## Auto-tile Coordinate Pipeline

### Grid Source in Code

| Option | Description | Selected |
|--------|-------------|----------|
| Use TILE_SIZE constant (Recommended) | Replace hardcoded 8 with TILE_SIZE from constants.py | ✓ |
| Read from LDtk file | Parse defaultGridSize from JSON | |
| Read from entity-schema | Use schema.get('level.grid_size') | |

**User's choice:** Use TILE_SIZE constant

### Both Loaders

| Option | Description | Selected |
|--------|-------------|----------|
| Update both loaders (Recommended) | Both simplified and auto-tile loaders use TILE_SIZE | ✓ |
| Auto-tiles only | Only update load_autotiles_from_ldtk | |
| You decide | Claude checks both code paths | |

**User's choice:** Update both loaders

---

## File Roles & Cleanup

### LDtk File Authority

| Option | Description | Selected |
|--------|-------------|----------|
| cave.ldtk is source, output.ldtk is generated | cave.ldtk editable, output.ldtk is export | |
| output.ldtk is authoritative | Converter produces output.ldtk, cave.ldtk may be stale | ✓ |
| You decide | Claude investigates | |

**User's choice:** output.ldtk is authoritative

---

## Tileset Upscale Method

### Upscale Tool

| Option | Description | Selected |
|--------|-------------|----------|
| Python script with PIL (Recommended) | Reproducible nearest-neighbor upscale | |
| Aseprite re-export | Manual from tiles.aseprite | ✓ |
| You decide | Claude picks | |

**User's choice:** Aseprite re-export
**Notes:** User clarified they already exported the image to 256x256 so 8x8 tiles now have 16x16 size. No layout change.

### Image Size

| Option | Description | Selected |
|--------|-------------|----------|
| 256x256 is enough | 256 tiles at 16px sufficient for single biome | ✓ |
| Expand to 512x512 | Keep all original positions (but Pyxel banks are 256x256) | |
| You decide | Claude checks tile usage | |

**User's choice:** 256x256 is enough

### Tileset Completeness

User clarified: tiles.png already has entity icons grafted at y=160 from original tileset.png at 200% scale. tiles.png is the complete tileset.

---

## Verification Strategy

### Verification Method

| Option | Description | Selected |
|--------|-------------|----------|
| Run & capture with MCP (Recommended) | Pyxel MCP tools for automated visual verification | ✓ |
| Manual play-test | Visual inspection | |
| Both | MCP + manual | |

**User's choice:** Run & capture with MCP

### Regression Test

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, tile count test (Recommended) | Test tile count and 16px-aligned coordinates | ✓ |
| No new tests | Existing tests + MCP sufficient | |
| You decide | Claude adds tests where valuable | |

**User's choice:** Yes, tile count test

---

## Simplified Export Regen

| Option | Description | Selected |
|--------|-------------|----------|
| Patch both (Recommended) | Script-patch output.ldtk AND simplified export JSONs/CSVs | ✓ |
| Regenerate from LDtk editor | Open patched project, re-export | |
| You decide | Claude investigates | |

**User's choice:** Patch both

---

## Tileset tile_coords Update

User clarified: "the image is just scaled" -- since the tileset is a straight 2x upscale with no layout change, tile_coords [col, row] values in entity-schema stay the same. Col/row indices are unchanged.

---

## Migration Script Scope

### Script Lifetime

| Option | Description | Selected |
|--------|-------------|----------|
| Keep in scripts/ (Recommended) | Useful for converter handoff documentation | ✓ |
| One-shot, delete after | Less clutter | |

**User's choice:** Keep in scripts/

---

## Entity Layer Grid

### Snap Method

| Option | Description | Selected |
|--------|-------------|----------|
| Round to nearest 16px (Recommended) | PlayerStart (128,88)->(128,96), SavePoint (152,96)->(160,96) | ✓ |
| Defer to Phase 22 | Leave positions as-is | |
| You decide | Claude picks | |

**User's choice:** Round to nearest 16px
**Notes:** Only 2 of 42 entities misaligned. Caused by converter placing on 8px grid -- odd-row entities don't align to 16px.

---

## IntGrid Downsampling

| Option | Description | Selected |
|--------|-------------|----------|
| Top-left wins (Recommended) | Take top-left cell of each 2x2 block | ✓ |
| Majority vote | Most common value in 2x2 block wins | |
| You decide | Claude picks simplest approach | |

**User's choice:** Top-left wins

---

## Simplified Export Patching Detail

| Option | Description | Selected |
|--------|-------------|----------|
| Patch CSV + data.json only (Recommended) | Skip PNG regeneration, game doesn't use them | ✓ |
| Full regen | Patch everything including PNGs | |
| You decide | Claude checks what game loads | |

**User's choice:** Patch CSV + data.json only

---

## File Organization (tilesets/ folder)

### Layout

| Option | Description | Selected |
|--------|-------------|----------|
| tilesets/cavern.png + source (Recommended) | Move tiles.png -> tilesets/cavern.png, tiles.aseprite -> tilesets/cavern.aseprite | ✓ |
| tilesets/tileset.png | Keep LDtk-friendly name | |
| Custom layout | User describes | |

**User's choice:** tilesets/cavern.png + source
**Notes:** User requested consolidation: "should we move the tileset related files to tilesets folder like how we planned initially? i was scrambling to update the image and didn't put much thought to categorize them."

### Old Files

| Option | Description | Selected |
|--------|-------------|----------|
| Delete it | In git history if needed | ✓ |
| Keep as backup | Rename to tileset_8px_backup.png | |

**User's choice:** Delete old tileset.png

---

## Background Layer Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Skip it (Recommended) | Empty layer, no migration needed | ✓ |
| Update grid definition | Update gridSize for consistency | |

**User's choice:** Skip it

---

## Claude's Discretion

- Migration script internal structure and error handling
- Order of operations within the script
- Specific test assertions beyond tile count and alignment
- data.json field updates in simplified export

## Deferred Ideas

- pml-to-ldtk converter update to generate 16px output -- Phase 23 handoff scope
