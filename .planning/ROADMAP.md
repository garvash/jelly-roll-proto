# Roadmap - Jelly Roll Proto

## Milestones

- v1.0 Vertical Slice — Phases 1-6 (shipped 2026-03-28)
- v1.1 World Expansion & New Abilities — Phases 7-16 (shipped 2026-04-01)
- v1.2 Unified Schema & Tilemap Rendering — Phases 17-19 (shipped 2026-04-07)
- v1.3 16x16 Tile Migration — Phases 20-23 (in progress)

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

<details>
<summary>v1.2 Unified Schema & Tilemap Rendering (Phases 17-19) — SHIPPED 2026-04-07</summary>

- [x] Phase 17: Unified Schema Definition (1/1 plan) — completed 2026-04-05
- [x] Phase 18: Schema-Driven Integration (3/3 plans) — completed 2026-04-05
- [x] Phase 19: Tilemap Rendering (2/2 plans) — completed 2026-04-07

</details>

### v1.3 16x16 Tile Migration (In Progress)

- [x] **Phase 20: Grid Constants & Schema Metadata** - Flip TILE_SIZE to 16, remove SPRITE_SCALE, update all derived constants and schema version (completed 2026-04-08)
- [x] **Phase 21: Tileset & LDtk Pipeline** - Reconfigure LDtk project and tileset for 16x16 grid, verify autoLayerTiles render correctly (completed 2026-04-08)
- [ ] **Phase 22: Entity Alignment & Physics Tuning** - Align all entity collision boxes to 16x16 visuals and tune physics for new tile scale
- [ ] **Phase 23: Converter Handoff** - Document all schema/grid changes for the pml-to-ldtk agent

## Phase Details

### Phase 20: Grid Constants & Schema Metadata
**Goal**: The codebase operates on a uniform 16x16 tile grid with no SPRITE_SCALE indirection
**Depends on**: Phase 19
**Requirements**: GRID-01, GRID-02, GRID-03, GRID-04, LDTK-01, LDTK-05
**Success Criteria** (what must be TRUE):
  1. TILE_SIZE equals 16 and SPRITE_SCALE is gone from the codebase -- no doubled-up indirection anywhere
  2. Room dimensions are 20x11 tiles (320x176 pixels) and the game viewport renders at the correct size
  3. entity-schema.json grid_size is 16 and schema version is bumped to reflect the breaking change
  4. All derived constants (SPRITE_SIZE, BOSS_SPRITE_SIZE, room tile counts) are consistent with 16x16 base
**Plans:** 2/2 plans complete
Plans:
- [x] 20-01-PLAN.md — Update constants.py, entity-schema.json, and export script for 16x16 grid
- [ ] 20-02-PLAN.md — Rewrite tests for 16x16 contract and update converter documentation

### Phase 21: Tileset & LDtk Pipeline
**Goal**: LDtk project and tileset produce correct 16x16 autoLayerTiles that render properly in-game
**Depends on**: Phase 20
**Requirements**: LDTK-02, LDTK-03, LDTK-04
**Success Criteria** (what must be TRUE):
  1. LDtk project (cave.ldtk) uses 16x16 default grid and rooms are 20x11 tiles
  2. Tileset is defined with 16x16 tile dimensions and tile IDs resolve correctly
  3. autoLayerTiles load and render at correct positions with no visual gaps or misalignment
**Plans:** 2/2 plans complete
Plans:
- [x] 21-01-PLAN.md — Create migration script, run it, update tests for 16px values
- [x] 21-02-PLAN.md — Update map.py hardcoded grid values, visual verification

### Phase 22: Entity Alignment & Physics Tuning
**Goal**: All entities have collision boxes matching their 16x16 visuals, and physics feel correct at the new scale
**Depends on**: Phase 21
**Requirements**: ENT-01, ENT-02, ENT-03, ENT-04, ENT-05, PHYS-01, PHYS-02, PHYS-03
**Success Criteria** (what must be TRUE):
  1. Player, enemies (Snail, Bat), and boss collision boxes match their visual sprite boundaries -- no invisible overhang or gaps
  2. Door entities have correct dimensions for the 16x16 grid
  3. draw_sprite() offset math is simplified -- collision size equals visual size, no scale compensation
  4. Player can jump through 1-tile-tall and 1-tile-wide passages without getting stuck
  5. physics-schema.json reflects 16x16 base values for gravity, jump height, and passage clearances
**Plans:** 2/2 plans complete
Plans:
- [x] 22-01-PLAN.md — Update entity hitboxes (Slime, Snail, Bat, Mole, BossRock, Effect) and fix legacy spawn path
- [x] 22-02-PLAN.md — Recalculate physics-schema.json for 16px tile base and fix existing tests

### Phase 23: Converter Handoff
**Goal**: The pml-to-ldtk agent has a clear document describing every schema and grid change needed on their side
**Depends on**: Phase 22
**Requirements**: CONV-01, CONV-02, CONV-03
**Success Criteria** (what must be TRUE):
  1. CONVERTER-HANDOFF.md exists with before/after values for grid_size, room dimensions, and entity sizes
  2. All breaking changes to the shared entity-schema contract are explicitly listed
  3. A pml-to-ldtk maintainer can read the handoff and know exactly what to change without inspecting game code
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 20 -> 21 -> 22 -> 23

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
| 17. Unified Schema Definition | v1.2 | 1/1 | Complete | 2026-04-05 |
| 18. Schema-Driven Integration | v1.2 | 3/3 | Complete | 2026-04-05 |
| 19. Tilemap Rendering | v1.2 | 2/2 | Complete | 2026-04-07 |
| 20. Grid Constants & Schema Metadata | v1.3 | 1/2 | Complete    | 2026-04-08 |
| 21. Tileset & LDtk Pipeline | v1.3 | 2/2 | Complete    | 2026-04-08 |
| 22. Entity Alignment & Physics Tuning | v1.3 | 2/2 | In Progress | - |
| 23. Converter Handoff | v1.3 | 0/TBD | Not started | - |
