# Phase 18: Schema-Driven Integration - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Both the game runtime and the pml-to-ldtk converter consume tile and entity definitions from the unified schema (entity-schema.json v1.0.0), eliminating hardcoded tile constants from the game code. The game loads tile coordinates, behavior data, and tileset paths from the schema at startup. The converter's integration is documented but not implemented in this phase (separate repo).

</domain>

<decisions>
## Implementation Decisions

### Schema Loading Strategy
- **D-01:** Load and parse `entity-schema.json` once at game startup. Build all lookup data structures at init time.
- **D-02:** If the schema file is missing or malformed, hard crash with a clear error message. No fallback to hardcoded constants.
- **D-03:** Schema loading lives in a new `src/core/schema.py` module. Exposes typed lookups (tile coords, behavior sets, biome layers, tileset path).

### Constant Elimination
- **D-04:** All `TILE_*` visual constants removed from `constants.py` (TILE_SOLID, TILE_HAZARD, TILE_DESTRUCTIBLE, TILE_SWITCH, TILE_CRACKED_H, TILE_CRACKED_V, TILE_WATER, TILE_ACID, TILE_LAVA). Only `TILE_EMPTY = (31, 31)` stays per Phase 17 D-17.
- **D-05:** `collision_data` stores IntGrid integer values (1, 2, 3, etc.) instead of tile tuples.
- **D-06:** `HAZARD_DRAIN_RATES` keys switch from tile tuples to IntGrid values (e.g., `{6: SLOW, 7: MEDIUM, 8: FAST}`). Drain rate numeric values stay as gameplay constants.
- **D-07:** Clean break — remove all constants and update all code/tests in one shot. No deprecation period.

### Behavior Lookup Model
- **D-08:** Behavior checks driven by schema `intgrid.values` behavior strings. `schema.py` parses behavior fields and builds sets like `SOLID_VALUES = {1, 3, 11, 12}` from entries containing `"collision"` in their behavior.
- **D-09:** `is_solid()`, `is_hazard()`, `is_destructible()` etc. check IntGrid values against schema-built behavior sets instead of comparing tile tuples.
- **D-10:** Adding a new tile type with collision behavior only requires a schema entry — no code changes needed.

### Biome Selection
- **D-11:** Hardcode `'cavern'` as the active biome. Multi-biome room selection is future milestone scope (BIOME-02).
- **D-12:** Tileset PNG loading is schema-driven — read `biomes.cavern.tileset` path from schema and load into pyxel image bank.

### Converter Integration
- **D-13:** pml-to-ldtk converter accesses the shared schema via relative path (`../jelly-roll-proto/assets/entity-schema.json`) in the two-repo workspace.
- **D-14:** This phase documents the converter contract only. Actual converter code changes happen when working in the converter repo.

### Migration
- **D-15:** Save file compatibility is not affected — save system stores destroyed blocks and collected items by tile coordinates and IIDs, not by tile tuple values.

### Test Strategy
- **D-16:** Unit tests for `schema.py` (loading, val_to_tile generation, behavior set building) plus integration tests that load a real room with schema-driven tiles.
- **D-17:** Explicit schema mutation test — modify a tile_coord value in schema and verify `pyxel.tilemaps` receives the changed coordinates. Directly validates Success Criterion 3.

### Claude's Discretion
- Internal naming in schema.py (function names, class structure)
- Whether schema.py uses a class or module-level functions
- How to structure the schema mutation test (temp file vs monkeypatch)
- Exact refactoring order (constants first vs map.py first)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Schema
- `assets/entity-schema.json` — v1.0.0 unified schema with intgrid values, biomes.cavern (tile_coords, layers, tileset path), entities, converter_mapping, simplified_export structure.

### Code to Refactor
- `src/core/constants.py` lines 19-32 — Hardcoded `TILE_*` tuples to be removed (except TILE_EMPTY). Also `HAZARD_DRAIN_RATES` dict at line 38-43 needs key migration.
- `src/level/map.py` — `val_to_tile` dict (line 35-42), `collision_data` storage, `is_solid()`/`is_hazard()`/`is_destructible()` checks, tilemap pset calls. Core refactoring target.

### Tests to Update
- `tests/test_schema.py` — Existing schema validation tests from Phase 17.
- `tests/test_cracked_v.py` — References TILE_CRACKED_V constant.
- `tests/test_hazard_zones.py` — References TILE_WATER/TILE_ACID/TILE_LAVA and HAZARD_DRAIN_RATES.
- `tests/test_goo_mold_removal.py` — References tile constants.
- `tests/test_entity_integration.py` — May reference tile constants.

### Prior Phase Context
- `.planning/phases/17-unified-schema-definition/17-CONTEXT.md` — Schema structure decisions (D-01 through D-18) that this phase builds on.

### Requirements
- `.planning/REQUIREMENTS.md` — SCHEMA-02 (game loads from schema), SCHEMA-03 (converter reads from schema).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `entity-schema.json` v1.0.0: Complete with `biomes.cavern.tile_coords` mapping all IntGrid values to `[col, row]` coordinates — ready to consume.
- `val_to_tile` dict pattern in `map.py`: Already maps IntGrid values to tuples — schema.py replaces the source but the consumption pattern stays similar.
- `test_schema.py`: Existing schema validation tests provide a foundation for new schema loading tests.

### Established Patterns
- Constants in `src/core/constants.py` as UPPER_SNAKE_CASE — TILE_EMPTY stays, visual TILE_* constants go.
- Map loading in `load_ldtk_simplified()` — IntGrid.csv parsing loop is the main integration point.
- Behavior checks via `is_solid()`, `is_hazard()`, `is_destructible()` public API in map.py — signatures stay, internals change.

### Integration Points
- `map.py:load_ldtk_simplified()` — Primary consumer of schema tile data. Builds collision_data and sets tilemaps.
- Game init (likely `app.py` or `game.py`) — Where schema.py initialization should be called.
- All modules importing `TILE_*` from constants — Need updating to use IntGrid values or schema lookups.

</code_context>

<specifics>
## Specific Ideas

- schema.py should expose a clear API: `get_val_to_tile()` for the IntGrid-to-coordinate dict, `get_behavior_sets()` for collision/hazard/destructible value sets, `get_tileset_path()` for the PNG path, `get_layers()` for layer definitions.
- The behavior string parsing should handle compound behaviors like `"collision+destructible"` — a tile with this behavior appears in both SOLID_VALUES and DESTRUCTIBLE_VALUES sets.
- Phase 17's `[col, row]` format maps directly to pyxel tuple `(col, row)` with zero conversion — schema.py just converts JSON arrays to Python tuples.

</specifics>

<deferred>
## Deferred Ideas

- Per-room biome selection (BIOME-02) — future milestone
- Actual pml-to-ldtk converter code changes — separate repo, separate work session
- Layer/parallax rendering from schema — Phase 19 scope
- IntGrid value 4 reclamation — deferred from Phase 17

</deferred>

---

*Phase: 18-schema-driven-integration*
*Context gathered: 2026-04-05*
