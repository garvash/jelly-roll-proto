# v1.3 Migration Handoff: 16x16 Tile Migration

**Date:** 2026-04-08
**Scope:** Phases 20-22 of the v1.3 milestone
**Schema versions affected:**
- `entity-schema.json`: v1.0.0 -> v2.0.0 (BREAKING)
- `physics-schema.json`: v0.1.0 -> v0.2.0

**Relationship:** This document supplements `PML-to-LDtk Converter.md`, which remains the living reference for the converter. This handoff covers only what changed in v1.3.

---

## TL;DR

**Central insight: "Same pixels, different tiles."** Pixel dimensions are unchanged -- rooms are still 320x176, jump height is still 62px. The base tile size doubled from 8px to 16px, so all tile counts are halved.

**Critical breaking changes:**
1. `grid_size` changed from 8 to 16 -- all grid math uses 16px units
2. Room dimensions changed from 40x22 tiles to 20x11 tiles (same 320x176 pixels)
3. Tileset path changed from `assets/tiles.png` to `assets/tilesets/cavern.png`
4. All physics placement rules expressed in tile units are halved

---

## Section 1: entity-schema.json Changes (v1.0.0 to v2.0.0)

### Level Structure (BREAKING)

| Property | Before (v1.0.0) | After (v2.0.0) |
|----------|-----------------|-----------------|
| `version` | `1.0.0` | `2.0.0` |
| `level.grid_size` | `8` | `16` |
| `level.default_room_size` | `[320, 176]` | `[320, 176]` (unchanged) |
| Room size in tiles | 40x22 | 20x11 |
| `level.variable_rooms_note` | references "40x22 tiles" | references "20x11 tiles" |

### Tileset (BREAKING)

| Property | Before (v1.0.0) | After (v2.0.0) |
|----------|-----------------|-----------------|
| `biomes.cavern.tileset` | `assets/tiles.png` | `assets/tilesets/cavern.png` |
| `tile_coords` description | "8px tile grid" | "16px tile grid" |
| `tile_coords` values | Same `[col, row]` pairs | Same `[col, row]` pairs (unchanged) |

### Entity Definitions: No Changes

Entity sizes in the schema were already 16x16 in v1.0.0 (they represented visual size, not collision size). The converter entity placement sizes remain the same -- PlayerStart is 16x16, Door is 8x8, all enemies and pickups are 16x16. No action needed for entity definitions.

> **Note:** Phase 22 changed runtime hitbox sizes in game code, but those are internal to the game and not part of the entity-schema contract. The converter does not need to account for hitbox changes.

---

## Section 2: physics-schema.json Changes (v0.1.0 to v0.2.0)

All tile-unit values are halved because the tile size doubled. **Pixel values are unchanged** -- the physics feel identical, only the unit of measurement changed.

| Property | Before (v0.1.0) | After (v0.2.0) |
|----------|-----------------|-----------------|
| `version` | `0.1.0` | `0.2.0` |
| `tile_size` | `8` | `16` |
| `player.hitbox_px` | `[8, 8]` | `[10, 14]` |
| `player.visual_tiles` | `[2, 2]` | `[1, 1]` |
| `player.visual_px` | `[16, 16]` | `[16, 16]` (unchanged) |
| `jump.max_height_tiles` | `6` | `3` |
| `jump.max_height_px` | `62` | `62` (unchanged) |
| `jump.max_width_tiles` | `10` | `5` |
| `jump.max_width_px` | `89` | `89` (unchanged) |
| `jump.comfortable_height_tiles` | `4` | `2` |
| `jump.comfortable_width_tiles` | `7` | `3` |
| `clearance.min_vertical_tiles` | `2` | `1` |
| `clearance.min_horizontal_tiles` | `2` | `1` |
| `placement_rules.max_gap_horizontal` | `10` tiles | `5` tiles |
| `placement_rules.max_gap_vertical_up` | `6` tiles | `3` tiles |
| `placement_rules.platform_min_width_tiles` | `2` | `1` |
| `source_constants.TILE_SIZE` | `8` | `16` |

**Key takeaway:** A gap that was "10 tiles wide" at 8px is now "5 tiles wide" at 16px. Same 80 pixels. Update your placement rule comparisons to use the new tile values.

---

## Section 3: LDtk Output Format Changes

These changes affect what the converter must produce in `.ldtk` output files.

| Property | Before | After |
|----------|--------|-------|
| `defaultGridSize` | `8` | `16` |
| Tileset `tileGridSize` | `8` | `16` |
| Tileset `relPath` | `tileset.png` | `tilesets/cavern.png` |
| Layer `gridSize` | `8` | `16` |
| AutoLayerTile `src` coords | 8px-based | 16px-based |
| Tiles per row in tileset | 32 (256/8) | 16 (256/16) |
| IntGrid dimensions (standard room) | 40x22 | 20x11 |
| Entity positions | 8px-aligned | 16px-aligned |

---

## Section 4: Suggested Converter Actions

Practical action items for updating the pml-to-ldtk converter:

1. **Update grid_size constant** from `8` to `16` -- this is the root change that cascades everywhere
2. **Update tileset path** from `assets/tiles.png` to `assets/tilesets/cavern.png`
3. **Halve all tile-count room dimensions** -- standard rooms are 20x11 tiles (was 40x22)
4. **Update tile ID calculation** -- `tiles_per_row = 256 / 16 = 16` (was `256 / 8 = 32`)
5. **Snap entity positions to 16px grid** -- entity placement coordinates must be multiples of 16
6. **Update physics placement rules** to use halved tile values (e.g., max horizontal gap is 5 tiles, not 10)
7. **Validate output against entity-schema.json v2.0.0** -- the schema remains the authoritative contract
