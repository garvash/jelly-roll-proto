# PML-to-LDtk Converter

Reference documentation for the PML-to-LDtk map conversion pipeline.

## Room Dimensions

Room dimensions updated in Phase 12. Standard rooms: 320x176 (40x22 tiles). Large rooms: multiples like 320x352 (40x44 tiles). See `assets/entity-schema.json` for authoritative room spec.

| Property | Value |
|----------|-------|
| Tile size | 8px |
| Standard room (px) | 320x176 |
| Standard room (tiles) | 40x22 |
| Grid width | 320 |
| Grid height | 176 |

## Entity Schema

The converter MUST produce LDtk data conforming to `assets/entity-schema.json`. This shared contract defines:

- **Level structure:** identifier format, grid size, default room size
- **IntGrid values:** tile behavior mapping (solid, hazard, destructible, gates, zones)
- **Entity definitions:** PlayerStart, Door, enemies, pickups, boss
- **Simplified export format:** expected file structure per level

## LDtk World Layout

The game uses a GridVania world layout with 320x176 grid spacing. Level positions use `worldX` and `worldY` aligned to this grid:

- Column N: `worldX = N * 320`
- Row N: `worldY = N * 176`

## Variable Room Sizes

Rooms can be any multiple of grid_size (8px). Examples:

- Standard: 320x176 (40x22 tiles)
- Tall shaft: 320x352 (40x44 tiles, 2 rooms tall)
- Wide arena: 640x176 (80x22 tiles, 2 rooms wide)
