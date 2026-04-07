# Requirements: Jelly Roll Proto

**Defined:** 2026-04-05
**Core Value:** Prototyping the satisfying "fusion" loop between a player and a companion slime

## v1.2 Requirements

Requirements for milestone v1.2: Unified Schema & Tilemap Rendering. Each maps to roadmap phases.

### Schema

- [x] **SCHEMA-01**: Unified JSON schema file defines tile types (IntGrid values, tileset coordinates) and entity types (sprite bank, sprite coordinates) in one place
- [x] **SCHEMA-02**: Game loads tile-to-coordinate mappings from schema at runtime, replacing hardcoded constants in constants.py and map.py
- [x] **SCHEMA-03**: pml-to-ldtk converter reads tile and entity definitions from the same schema file
- [x] **SCHEMA-04**: Schema structure supports per-biome tileset sections with a default biome populated

### Tilemap

- [ ] **TILE-01**: Game parses autoLayerTiles array from LDtk simplified export data.json for each level
- [ ] **TILE-02**: AutoLayerTiles are rendered on pyxel.tilemaps[0] for terrain visuals (edges, corners, variation)
- [ ] **TILE-03**: Tile flip flags (flipX, flipY, both) from LDtk auto-tile rules are handled correctly
- [ ] **TILE-04**: Collision uses IntGrid.csv data, visual rendering uses autoLayerTiles — cleanly separated
- [x] **TILE-05**: Schema defines tilemap layers with z-order and optional parallax scroll rate
- [x] **TILE-06**: Game renders multiple tilemap layers at independent scroll rates for depth effect

## Future Requirements

### Biomes

- **BIOME-01**: Multiple biome tilesets defined in schema (Cavern, Jungle, etc.)
- **BIOME-02**: Per-room biome assignment drives tileset selection
- **BIOME-03**: Biome-specific auto-tile rules in LDtk

## Out of Scope

| Feature | Reason |
|---------|--------|
| Multiple biome tilesets | Infrastructure only this milestone — biome content deferred |
| Tileset art creation | Prototype scope — use placeholder/existing tiles |
| LDtk auto-rule authoring | Rules already exist in LDtk file — no tooling changes needed |
| Entity sprite pipeline changes | Sprite loading already works via SPRITE_MANIFEST — schema references existing paths |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SCHEMA-01 | Phase 17 | Complete |
| SCHEMA-02 | Phase 18 | Complete |
| SCHEMA-03 | Phase 18 | Complete |
| SCHEMA-04 | Phase 17 | Complete |
| TILE-01 | Phase 19 | Pending |
| TILE-02 | Phase 19 | Pending |
| TILE-03 | Phase 19 | Pending |
| TILE-04 | Phase 19 | Pending |
| TILE-05 | Phase 17 | Complete |
| TILE-06 | Phase 19 | Complete |

**Coverage:**
- v1.2 requirements: 10 total
- Mapped to phases: 10
- Unmapped: 0

---
*Requirements defined: 2026-04-05*
*Last updated: 2026-04-05 after roadmap creation*
