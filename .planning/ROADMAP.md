# Roadmap - Jelly Roll Proto

## Milestones

- v1.0 Vertical Slice — Phases 1-6 (shipped 2026-03-28)
- v1.1 World Expansion & New Abilities — Phases 7-16 (shipped 2026-04-01)
- v1.2 Unified Schema & Tilemap Rendering — Phases 17-19 (in progress)

## Phases

<details>
<summary>v1.0 Vertical Slice (Phases 1-6) — SHIPPED 2026-03-28</summary>

- [x] Phase 1: Core Movement & Physics (2/2 plans) — completed 2026-03-12
- [x] Phase 2: Slime Companion & Fusion (4/4 plans) — completed 2026-03-13
- [x] Phase 3: Destructive World & Boss (4/4 plans) — completed 2026-03-14
- [x] Phase 4: Level Interactivity & Items (2/2 plans) — completed 2026-03-15
- [x] Phase 5: New Enemies & Player Health (2/2 plans) — completed 2026-03-14
- [x] Phase 6: Physics Refinement & Test Gaps (1/1 plan) — completed 2026-03-22

</details>

<details>
<summary>v1.1 World Expansion & New Abilities (Phases 7-16) — SHIPPED 2026-04-01</summary>

- [x] Phase 7: Macro-Map & Room Persistence (2/2 plans) — completed 2026-03-27
- [x] Phase 8: New Fusion Abilities (6/6 plans) — completed 2026-03-28
- [x] Phase 9: Defensive Mechanics (3/3 plans) — completed 2026-03-28
- [x] Phase 10: Nitro-Ejection & Endgame (3/3 plans) — completed 2026-03-28
- [x] Phase 11: Save System & HUD (3/3 plans) — completed 2026-04-01
- [x] Phase 12: Screen Size Expansion (3/3 plans) — completed 2026-03-28
- [x] Phase 13: Sprite Scale & PNG Spritesheets (3/3 plans) — completed 2026-03-29
- [x] Phase 14: Tech Debt & Schema Cleanup (3/3 plans) — completed 2026-03-29
- [x] Phase 15: LDtk Entity & Door Integration (2/2 plans) — completed 2026-04-01
- [x] Phase 16: v1.1 Housekeeping & Verification (2/2 plans) — completed 2026-04-01

</details>

### v1.2 Unified Schema & Tilemap Rendering (In Progress)

**Milestone Goal:** Define tiles and entities in a single shared schema and render LDtk tilemaps visually in-game, establishing the infrastructure for multi-biome support.

- [x] **Phase 17: Unified Schema Definition** - Extend entity-schema.json to cover tile definitions, layer definitions, and biome-ready structure (completed 2026-04-05)
- [x] **Phase 18: Schema-Driven Integration** - Game and converter both read tile/entity definitions from the unified schema (completed 2026-04-05)
- [x] **Phase 19: Tilemap Rendering** - Load and render autoLayerTiles with multi-layer parallax for proper terrain visuals (completed 2026-04-07)

## Phase Details

### Phase 17: Unified Schema Definition
**Goal**: A single schema file defines both tile types and entity types, structured to support future biomes and multiple tilemap layers
**Depends on**: Nothing (first phase of v1.2)
**Requirements**: SCHEMA-01, SCHEMA-04, TILE-05
**Success Criteria** (what must be TRUE):
  1. A single JSON file contains tile definitions (IntGrid values, tileset source image, tile coordinates) alongside the existing entity definitions
  2. The schema has a per-biome tileset section with a "cavern" default biome populated with all current IntGrid-to-tile mappings
  3. Every IntGrid value currently used in the game has a corresponding entry in the schema
  4. Schema defines tilemap layers with z-order and optional parallax scroll rate
**Plans:** 1/1 plans complete
Plans:
- [ ] 17-01-PLAN.md — Extend schema with biomes section, move tileset, add tests

### Phase 18: Schema-Driven Integration
**Goal**: Both the game runtime and the pml-to-ldtk converter consume tile and entity definitions from the unified schema, eliminating hardcoded constants
**Depends on**: Phase 17
**Requirements**: SCHEMA-02, SCHEMA-03
**Success Criteria** (what must be TRUE):
  1. Game loads IntGrid-to-tile-coordinate mappings from the schema at startup, with no hardcoded tile constants remaining in constants.py or map.py
  2. The pml-to-ldtk converter reads tile and entity definitions from the same schema file used by the game
  3. Changing a tile mapping in the schema file changes the game's rendering without any code edits
**Plans:** 3/3 plans complete
Plans:
- [x] 18-01-PLAN.md — Create schema.py module with lookup API and unit tests
- [ ] 18-02-PLAN.md — Refactor game code to use schema lookups, remove TILE_* constants, update tests
- [ ] 18-03-PLAN.md — Schema mutation integration test and converter contract verification

### Phase 19: Tilemap Rendering
**Goal**: Terrain renders with proper visual variation (edges, corners, inner tiles) using LDtk auto-tile data, with collision remaining IntGrid-driven, and multiple layers render with parallax
**Depends on**: Phase 18
**Requirements**: TILE-01, TILE-02, TILE-03, TILE-04, TILE-06
**Success Criteria** (what must be TRUE):
  1. The game parses autoLayerTiles from each level's LDtk simplified export data.json and renders them onto pyxel.tilemaps[0]
  2. Terrain edges, corners, and tile variations are visually distinct (not uniform flat tiles as currently rendered)
  3. Tile flip flags (flipX, flipY, both) from LDtk auto-tile rules render correctly
  4. Collision detection still uses IntGrid.csv data, fully independent from visual tile rendering
  5. Multiple tilemap layers render at independent scroll rates for parallax depth effect
**Plans:** 2/2 plans complete
Plans:
- [x] 19-01-PLAN.md — Parse autoLayerTiles from output.ldtk, update schema tileset path, unit tests
- [x] 19-02-PLAN.md — Multi-layer parallax rendering pipeline, visual verification

## Progress

**Execution Order:**
Phases execute in numeric order: 17 -> 18 -> 19

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|---------------|--------|-----------|
| 1. Core Movement & Physics | v1.0 | 2/2 | Complete | 2026-03-12 |
| 2. Slime Companion & Fusion | v1.0 | 4/4 | Complete | 2026-03-13 |
| 3. Destructive World & Boss | v1.0 | 4/4 | Complete | 2026-03-14 |
| 4. Level Interactivity & Items | v1.0 | 2/2 | Complete | 2026-03-15 |
| 5. New Enemies & Player Health | v1.0 | 2/2 | Complete | 2026-03-14 |
| 6. Physics Refinement & Test Gaps | v1.0 | 1/1 | Complete | 2026-03-22 |
| 7. Macro-Map & Room Persistence | v1.1 | 2/2 | Complete | 2026-03-27 |
| 8. New Fusion Abilities | v1.1 | 6/6 | Complete | 2026-03-28 |
| 9. Defensive Mechanics | v1.1 | 3/3 | Complete | 2026-03-28 |
| 10. Nitro-Ejection & Endgame | v1.1 | 3/3 | Complete | 2026-03-28 |
| 11. Save System & HUD | v1.1 | 3/3 | Complete | 2026-04-01 |
| 12. Screen Size Expansion | v1.1 | 3/3 | Complete | 2026-03-28 |
| 13. Sprite Scale & PNG Spritesheets | v1.1 | 3/3 | Complete | 2026-03-29 |
| 14. Tech Debt & Schema Cleanup | v1.1 | 3/3 | Complete | 2026-03-29 |
| 15. LDtk Entity & Door Integration | v1.1 | 2/2 | Complete | 2026-04-01 |
| 16. v1.1 Housekeeping & Verification | v1.1 | 2/2 | Complete | 2026-04-01 |
| 17. Unified Schema Definition | v1.2 | 1/1 | Complete    | 2026-04-05 |
| 18. Schema-Driven Integration | v1.2 | 1/3 | Complete    | 2026-04-05 |
| 19. Tilemap Rendering | v1.2 | 2/2 | Complete   | 2026-04-07 |
