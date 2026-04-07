# Phase 19: Tilemap Rendering - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-06
**Phase:** 19-tilemap-rendering
**Areas discussed:** Auto-tile data source, Tile flip handling, Parallax layer rendering, Auto-tile rule quality, Tileset image size

---

## Auto-tile Data Source

| Option | Description | Selected |
|--------|-------------|----------|
| Full .ldtk file | Parse cave.ldtk directly for autoLayerTiles | |
| Reconfigure simplified export | Change LDtk settings to include autoLayerTiles in data.json | |
| Hybrid (simplified + .ldtk) | Keep simplified for collision, add .ldtk for visuals | |

**Initial exploration:** User asked about full vs partial LDtk autotile coverage. Explained that full .ldtk provides px, src, f, t, d, a fields — nearly complete coverage with only flip flags as a potential gap.

**Follow-up:** User asked about benefits of dropping simplified export entirely. Explained trade-offs: single source is simpler conceptually but requires rewriting 150 lines of working loader code.

**User's choice:** Hybrid — keep simplified export for collision/entities, add .ldtk parsing for autoLayerTiles visuals.

### LDtk File Selection

| Option | Description | Selected |
|--------|-------------|----------|
| output.ldtk | 46 auto-tile rules, 26 tile variants, 18 levels | ✓ |
| cave.ldtk | 4 basic rules, minimal variation | |
| Merge into one file | Combine rules into single canonical .ldtk | |

**User's choice:** output.ldtk — the production file with rich auto-tile rules.

---

## Tile Flip Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Defer flips | Parse flag, warn if non-zero, ignore for now | ✓ |
| Pre-bake flipped tiles | Generate flipped copies into tileset at load time | |
| Per-tile blt() fallback | Use blt() for individual flipped tiles | |

**Initial decision:** Defer flips since all tiles in cave.ldtk had f=0.

**Revisit:** Found 231 tiles (1.3%) with f=1 in output.ldtk. Proposed pre-baking. User corrected: the flips were from incomplete tile supply. Re-checked output.ldtk — confirmed all 18,094 tiles have f=0.

**User's choice:** Defer flips. All autoLayerTiles in output.ldtk have f=0. The complete tileset provides explicit tiles for all orientations.

---

## Parallax Layer Rendering

| Option | Description | Selected |
|--------|-------------|----------|
| Pipeline only, fill later | Multi-layer bltm() with scroll offsets, bg layer empty | ✓ |
| Solid bg color fill | Fill bg with single dark tile | |
| Procedural checkerboard | Test pattern for parallax verification | |
| Skip parallax entirely | Only render terrain layer | |

**Exploration:** User asked if bg image could come from LDtk. Checked cave.ldtk — bgRelPath is None for all levels, no background layer defined. Only Entities and IntGrid layers exist.

**User's choice:** Pipeline only — build the multi-layer rendering, leave bg empty until content is added.

---

## Auto-tile Rule Quality

| Option | Description | Selected |
|--------|-------------|----------|
| Code renders what exists | 46 rules, 26 variants are complete | ✓ |
| Ship with placeholder variation | Add basic edge/corner tiles as part of phase | |
| Block on proper tileset | Don't ship until proper tileset exists | |

**Key discovery:** Initially thought cave.ldtk had minimal rules (4 rules, 1 tile each). User recalled adding variations — checked output.ldtk and found 46 rules with 26 unique tile sources.

**User's choice:** Render what exists. User confirmed the tileset is now complete after fixing the tile supply based on observations during discussion.

---

## Tileset Image Size

| Option | Description | Selected |
|--------|-------------|----------|
| Keep current (96x80) | Already fits two stacked templates | |
| Round to 128x128 | Room for future tiles, clean power-of-2 | ✓ |
| 256x256 (full bank) | Maximum Pyxel capacity | |

**Context:** Explained Pyxel image banks are 256x256, current tileset only uses 120 of 1024 possible tile slots.

**User's choice:** 128x128 — room for growth with clean dimensions.

---

## Claude's Discretion

- LDtk parser structure (separate module or map.py extension)
- autoLayerTiles caching strategy
- Parallax camera offset math
- Tileset path update method (rename vs copy vs schema update)

## Deferred Ideas

- Background layer content — when art exists
- Foreground parallax layer — future schema addition
- Tile flip support — if future rules use non-zero flips
- Merging cave.ldtk and output.ldtk
