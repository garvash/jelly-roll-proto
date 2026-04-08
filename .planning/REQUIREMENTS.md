# Requirements: Jelly Roll Proto

**Defined:** 2026-04-08
**Core Value:** Prototyping the satisfying "fusion" loop between a player and a companion slime

## v1.3 Requirements

Requirements for 16x16 tile migration. Each maps to roadmap phases.

### Grid & Constants

- [ ] **GRID-01**: Game uses 16x16 as the base tile size (TILE_SIZE=16)
- [ ] **GRID-02**: SPRITE_SCALE indirection removed — sprites render at native 16x16
- [ ] **GRID-03**: All derived constants (SPRITE_SIZE, BOSS_SPRITE_SIZE, room dimensions) updated for 16x16 base
- [ ] **GRID-04**: Room dimensions are 20x11 tiles (320x176 pixels) in the new grid

### Entity Alignment

- [ ] **ENT-01**: Player collision box matches 16x16 visual sprite
- [ ] **ENT-02**: Enemy collision boxes (Snail, Bat) match 16x16 visual sprites
- [ ] **ENT-03**: Boss collision box scaled proportionally (32x32 collision, 32x32 visual)
- [ ] **ENT-04**: Door entity dimensions updated for 16x16 grid
- [ ] **ENT-05**: draw_sprite() offset math simplified — collision equals visual size

### LDtk & Schema

- [ ] **LDTK-01**: entity-schema.json grid_size updated to 16
- [ ] **LDTK-02**: LDtk project (cave.ldtk) reconfigured with 16x16 default grid
- [ ] **LDTK-03**: autoLayerTiles coordinates and tile IDs correct at 16x16
- [ ] **LDTK-04**: Tileset adapted for 16x16 tile definitions
- [ ] **LDTK-05**: Schema version bumped to reflect breaking grid change

### Physics

- [ ] **PHYS-01**: Jump height and gravity tuned for 16x16 tile passages
- [ ] **PHYS-02**: Minimum passage sizes defined in new tile units (1-tile wide/tall corridors passable)
- [ ] **PHYS-03**: physics-schema.json updated with 16x16 base values

### Converter Handoff

- [ ] **CONV-01**: CONVERTER-HANDOFF.md documents all schema/grid changes for pml-to-ldtk agent
- [ ] **CONV-02**: Handoff includes before/after values for grid_size, room dimensions, entity sizes
- [ ] **CONV-03**: Handoff notes any breaking changes to the shared entity-schema contract

## Future Requirements

(None deferred — this is a focused migration milestone)

## Out of Scope

| Feature | Reason |
|---------|--------|
| New biome content | Migration only — content comes after foundation is stable |
| Tileset art rework | Existing 8x8 tiles can be used in 16x16 cells; art polish is separate |
| New abilities or enemies | No gameplay additions in this milestone |
| pml-to-ldtk converter changes | Converter is separate repo — handoff note only |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| GRID-01 | Phase 20 | Pending |
| GRID-02 | Phase 20 | Pending |
| GRID-03 | Phase 20 | Pending |
| GRID-04 | Phase 20 | Pending |
| ENT-01 | Phase 22 | Pending |
| ENT-02 | Phase 22 | Pending |
| ENT-03 | Phase 22 | Pending |
| ENT-04 | Phase 22 | Pending |
| ENT-05 | Phase 22 | Pending |
| LDTK-01 | Phase 20 | Pending |
| LDTK-02 | Phase 21 | Pending |
| LDTK-03 | Phase 21 | Pending |
| LDTK-04 | Phase 21 | Pending |
| LDTK-05 | Phase 20 | Pending |
| PHYS-01 | Phase 22 | Pending |
| PHYS-02 | Phase 22 | Pending |
| PHYS-03 | Phase 22 | Pending |
| CONV-01 | Phase 23 | Pending |
| CONV-02 | Phase 23 | Pending |
| CONV-03 | Phase 23 | Pending |

**Coverage:**
- v1.3 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0

---
*Requirements defined: 2026-04-08*
*Last updated: 2026-04-08 after roadmap creation*
