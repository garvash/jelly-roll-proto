# Phase 17: Unified Schema Definition - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-05
**Phase:** 17-unified-schema-definition
**Areas discussed:** Schema structure, Tile coordinate format, Layer & parallax model, Biome extensibility, Schema versioning, Empty/special tile handling, Tileset image naming

---

## Schema Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Extend intgrid + biomes key | Keep intgrid.values for behavior. Add top-level "biomes" key with tileset image + tile coordinate mappings per biome. | ✓ |
| All in biomes | Move intgrid values entirely under each biome, co-locating behavior + visuals. | |
| Flat tilesets section | Add parallel "tilesets" key mapping biome names to image + coordinates. | |

**User's choice:** Extend intgrid + biomes key
**Notes:** User first asked about tileset image organization (single PNG per biome?) which informed the structure decision. Confirmed behavior/visual separation.

---

## Tile Coordinate Format

| Option | Description | Selected |
|--------|-------------|----------|
| [col, row] grid coords | Same as constants.py — maps directly to pyxel.tilemaps pset(). Zero conversion. | ✓ |
| Pixel offsets | [px_x, px_y] on tileset image. Requires dividing by TILE_SIZE before use. | |

**User's choice:** [col, row] grid coords
**Notes:** None — straightforward match to existing convention.

---

## Layer & Parallax Model

| Option | Description | Selected |
|--------|-------------|----------|
| Per-biome layer list | Each biome defines ordered list of layers with name, tilemap index, z-order, scroll rate. | ✓ |
| Global layer definitions | Layers defined once at top level, shared across all biomes. | |
| You decide | Claude picks best approach. | |

**User's choice:** Per-biome layer list
**Notes:** None.

### Cavern Layer Count

| Option | Description | Selected |
|--------|-------------|----------|
| 2 layers | Background (scroll 0.5) + terrain (scroll 1.0). Minimal for working parallax. | ✓ |
| 3 layers | Background + terrain + foreground. More visual richness but needs foreground art. | |
| You decide | Claude picks based on prototype constraints. | |

**User's choice:** 2 layers
**Notes:** Foreground deferred.

---

## Biome Extensibility

| Option | Description | Selected |
|--------|-------------|----------|
| Self-contained | Each biome defines complete tileset + tile_coords + layers. No inheritance. | ✓ |
| Base + override | Default biome defines shared coords. Named biomes override what differs. | |

**User's choice:** Self-contained
**Notes:** None — simplicity preferred for prototype.

---

## Schema Versioning

| Option | Description | Selected |
|--------|-------------|----------|
| Bump to v1.0.0 | Marks unified schema milestone. Major version signals structural shift. | ✓ |
| Stay 0.x (v0.7.0) | Keep pre-1.0 since game is prototype. | |

**User's choice:** Bump to v1.0.0
**Notes:** None.

---

## Empty/Special Tile Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Exclude both | Don't list 0 or 4 in tile_coords. Absence = no visual tile. | ✓ |
| Include with null/sentinel | List with null marker for documentation. | |

**User's choice:** Exclude both
**Notes:** User noted IntGrid value 4 can be reclaimed if a good use is found in the future.

---

## Tileset Image Naming

| Option | Description | Selected |
|--------|-------------|----------|
| assets/tilesets/ subfolder | New directory: cavern.png, jungle.png, etc. Current tiles.png moves/renames. | ✓ |
| Flat in assets/ | tiles_cavern.png alongside existing files. | |

**User's choice:** assets/tilesets/ subfolder
**Notes:** None.

---

## Claude's Discretion

- Exact key naming within schema structure
- Whether to add JSON Schema validation for biomes section
- How to handle reserved_ranges section in intgrid

## Deferred Ideas

- IntGrid value 4 reclamation for future use
- Foreground layer for cavern biome
- Biome inheritance/defaults if duplication becomes painful
