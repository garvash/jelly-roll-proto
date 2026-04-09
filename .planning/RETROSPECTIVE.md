# Retrospective - Jelly Roll Proto

## Milestone: v1.0 — Vertical Slice

**Shipped:** 2026-03-28
**Phases:** 6 | **Plans:** 14

### What Was Built
- Celeste-style platforming with walk, jump, wall slide, and kick mechanics
- Independent slime companion with juice resource and shadow follow logic
- Drill Dive fusion ability for destructive traversal through soft blocks
- Giant Mole boss with spit-stun-drill combat loop
- Cavern biome with hazards, destructible blocks, and collectible items
- 3 HP health system with Snail and Bat enemies
- Physics refinement pass resolving tech debt from early phases

### What Worked
- **Rapid iteration speed:** 11-day timeline from first commit to playable vertical slice
- **Phase-based planning:** Breaking work into focused phases kept scope manageable
- **Automated test coverage:** Tests caught regressions early, especially during physics refinement (Phase 6)
- **LDtk integration:** Level editor enabled fast biome design without manual tile placement
- **Hit-stop and screen shake:** Small juice effects made drilling feel satisfying immediately

### What Was Inefficient
- **Phase 4 artifacts in Phase 3 directory:** Required cleanup in Phase 6 (ORG-01)
- **Dash mechanic built then removed:** MOV-02 (Dash) was implemented in Phase 1 then replaced by Kick in Phase 4 — could have been caught earlier in design
- **Nyquist validation gaps:** Phases 02 and 03 lack validation files; Phase 01 has stubs only

### Patterns Established
- Death state locking (bypass update when is_alive is False)
- Timer-based respawn loops
- Physics constants in `src/core/constants.py` for all numeric tuning values
- Entity schema contract (`assets/entity-schema.json`) shared with pml-to-ldtk converter

### Key Lessons
- **Validate mechanics in design before implementing:** The dash-to-kick pivot cost implementation time
- **Create phase directories upfront:** Prevents cross-phase artifact contamination
- **Physics-based movement > lerp-based:** Acceleration/friction feels more natural and integrates better with collision

---

## Milestone: v1.1 — World Expansion & New Abilities

**Shipped:** 2026-04-01
**Phases:** 10 | **Plans:** 30 | **Tasks:** 52

### What Was Built
- Macro-Map with 5x5 room grid, camera snapping, and room state persistence
- 6 fusion abilities: Slime Ram, Directional Hold, Charge Shot, Bubble Shield, Slime Boost, CRACKED_V gating
- Save/checkpoint system with JSON persistence, title/pause/death screens, mini-map HUD
- 320x180 display expansion with 2x sprite scale and PNG spritesheet pipeline
- Event-gated door system replacing hardcoded tile ID 4 boss gates
- LDtk entity/door integration fixes and 3 new entity stubs (entity-schema v0.4.0)
- Complete tech debt cleanup and retroactive Phase 10 verification

### What Worked
- **Milestone audit as quality gate:** Running `/gsd:audit-milestone` before completion caught 4 integration bugs (INT-01 through INT-04) and 6 tech debt items — all fixed in Phases 15-16 before shipping
- **Gap closure phases:** Creating targeted phases (14, 15, 16) specifically to close audit gaps was very effective
- **Entity-schema as contract:** Shared JSON schema between code and pml-to-ldtk converter prevented drift
- **Charge-to-fuse unification:** Single activation model for all fusion abilities reduced input complexity
- **Worktree parallelization:** Running agents in isolated worktrees enabled parallel plan execution

### What Was Inefficient
- **ABL-07 designed then removed:** Reform Block was specced, assigned to Phase 9, then cut (D-21) — wasted some planning time
- **Integration bugs found late:** Entity name mismatches and Door customFields issues could have been caught earlier with E2E integration tests after Phase 7
- **Screen size changes cascaded:** Phase 12 (320x180) required touching nearly every draw call; doing this earlier would have reduced rework in Phases 8-10
- **Multiple gap-fix plans:** Phases 08-05, 08-06 were reactive gap fixes that could have been avoided with more thorough initial planning

### Patterns Established
- Event-gated doors (action="event" + event_id) for flexible world gating
- Charge-to-fuse activation model for all fusion abilities
- PNG spritesheet loading via manifest.json (replacing pyxres image banks)
- God-mode debug module (replacing DEBUG_ALL_ABILITIES flag)
- Entity alias system for LDtk name normalization

### Key Lessons
- **Run integration tests early:** After any pipeline change (LDtk → code), verify the full spawn chain
- **Do display-size changes first:** Screen size affects every visual system — do it before building on top
- **Audit before shipping:** The milestone audit caught real blockers (2 E2E flows broken) that would have shipped as bugs
- **Cut features early:** ABL-07 should have been removed during requirements, not after Phase 9 planning

---

## Milestone: v1.2 — Unified Schema & Tilemap Rendering

**Shipped:** 2026-04-07
**Phases:** 3 | **Plans:** 6 | **Tasks:** 10

### What Was Built
- Unified entity-schema.json v1.0.0 with biomes section (tiles, entities, layers)
- Schema.py module with 9 public lookup functions replacing hardcoded TILE_* constants
- autoLayerTiles parsing from LDtk (18,094 tiles, 32 unique variants)
- Multi-layer parallax rendering pipeline with z-ordered independent scroll rates
- Collision/visual separation (IntGrid for physics, autoLayerTiles for visuals)

### What Worked
- **Schema as single source of truth:** Both game and converter consuming from one file eliminated constant drift
- **Small focused milestone:** 3 phases, 6 plans — tight scope shipped in 3 days
- **Parallax pipeline design:** Layer-based z-ordering made adding visual depth straightforward

### What Was Inefficient
- **Flip flags deferred:** TILE-03 explicitly deferred flip rendering (all tiles f=0), creating known tech debt
- **Schema migration required careful coordination:** entity-schema v0.4.0 → v1.0.0 touched multiple consumers

### Patterns Established
- Schema-driven tile/entity lookup replacing hardcoded constants
- Full LDtk project file parsing for autoLayerTiles (simplified export lacks tile data)
- Layer definitions with z-order and scroll_rate in schema

### Key Lessons
- **Unify early:** Having tiles, entities, and layers in one schema file saves cross-referencing
- **Parse the full LDtk file when needed:** Simplified export is great for entities/IntGrid but lacks autoLayerTile data

---

## Milestone: v1.3 — 16x16 Tile Migration

**Shipped:** 2026-04-09
**Phases:** 4 | **Plans:** 7 | **Tasks:** 15

### What Was Built
- TILE_SIZE=16 across entire codebase with SPRITE_SCALE indirection removed
- entity-schema.json v2.0.0 (grid_size=16, rooms=20x11 tiles)
- LDtk project reconfigured for 16x16 grid (tileset, autoLayerTiles, entities)
- All entity collision boxes aligned to 16x16 visuals
- physics-schema.json v0.2.0 (tile-unit values halved, pixel values unchanged)
- CONVERTER-HANDOFF.md for pml-to-ldtk converter maintainer
- Boss spawn offset fix after LDtk entity resize (32x32 to match sprite)

### What Worked
- **"Same pixels, different tiles" framing:** Made the migration conceptually clear — pixel dimensions don't change, only tile counts
- **Phase ordering:** Constants first → LDtk pipeline → entities/physics → handoff doc was the natural dependency chain
- **Fast execution:** 4 phases in 2 days, parallel worktree agents for independent plans
- **UAT caught real bug:** Boss positioning issue found during user testing, diagnosed and fixed inline

### What Was Inefficient
- **CONV requirements not auto-marked:** Phase 23 completed but CONV-01/02/03 checkboxes stayed unchecked — stale REQUIREMENTS.md traceability
- **Boss pivot issue missed by automated verification:** The LDtk entity pivot (center vs top-left) and size mismatch wasn't caught until manual play testing — automated checks verified file content but not visual positioning
- **20-02 plan count discrepancy:** ROADMAP showed 1/2 plans for Phase 20 but both were complete on disk

### Patterns Established
- Visual-to-hitbox spawn offset for entities with different LDtk and game sizes
- Bottom-center anchored sprite drawing with explicit collision-to-visual conversion
- Handoff documents for cross-repo changes

### Key Lessons
- **Manual play testing catches what automated checks miss:** Entity pivot/size visual mismatches need eyeballs
- **LDtk entity size should match game visual size:** Prevents placement confusion in the editor
- **Keep traceability table in sync:** Requirement checkboxes should update when phase completes, not at milestone end

---

## Cross-Milestone Trends

| Metric | v1.0 | v1.1 | v1.2 | v1.3 |
|--------|------|------|------|------|
| Phases | 6 | 10 | 3 | 4 |
| Plans | 14 | 30 | 6 | 7 |
| Timeline (days) | 11 | 6 | 3 | 2 |
| Requirements shipped | 15 | 14 | 12 | 20 |
| Audit result | Passed | tech_debt → gaps closed | — | — |
| Commits | — | 221 | — | ~30 |
| LOC delta | — | +54,921 / -2,497 | +884 / -175 | +11,483 / -20,375 |
