# Phase 15: LDtk Entity & Door Integration Fixes - Context

**Gathered:** 2026-04-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix integration bugs between LDtk entity data and game code: direction capitalization mismatch, customFields flattening inconsistency, entity name mismatches, double-spawn on restore audit. Stub three new LDtk entity types (OneWay, HiddenLoot, Map) in schema and code. Unblocks "Save→Die→Reload" and "Explore→Boss→Win" E2E flows.

</domain>

<decisions>
## Implementation Decisions

### Direction Normalization
- **D-01:** Normalize at parse time in `map.py` during LDtk data loading. All downstream consumers receive clean lowercase values.
- **D-02:** Normalize ALL string enum fields from LDtk (direction, action, and any future enum fields), not just direction. Future-proofs against LDtk export quirks.

### CustomFields Flattening
- **D-03:** Fix spawn sites in `main.py` to read flattened fields directly from entity dict (`ent.get('action')` instead of `ent.get('customFields', {}).get('action')`). map.py's existing flattening is the correct pattern.
- **D-04:** Audit ALL entity spawn sites in `spawn_enemies()` for the same nested-vs-flat bug, not just Door.

### Entity Name Standardization
- **D-05:** Standardize "universal" Metroidvania entity names in entity-schema.json (PlayerStart, SavePoint, Map, Door) so the pml-to-ldtk converter produces correct names. These are the shared contract names.
- **D-06:** Game-specific entities (Snail, Bat, DashPickup, etc.) stay as-is — project-specific names don't need standardization.

### New Entity Stubs
- **D-07:** OneWay — stub only. Schema definition + empty class that renders but has no collision behavior. Behavior deferred to a future phase.
- **D-08:** HiddenLoot — stub only. Schema definition + empty class. No reveal mechanic yet. Behavior deferred.
- **D-09:** Map — a wall fixture (not a pickup). Player will interact with it to reveal map areas. This phase: stub only — schema definition + class shell that renders. Interaction behavior deferred.

### Double-Spawn Guard
- **D-10:** Precautionary audit of Save→Die→Reload and room-transition entity lifecycle flows. Verify clear-then-spawn pattern prevents duplicate entities (especially doors and save points).
- **D-11:** Scope limited to the two main flows (save/restore + room transitions). Mid-room scenarios (pause/unpause, boss triggers) are out of scope.

### Schema Version
- **D-12:** Bump entity-schema.json to v0.4.0 (3 new entity stubs + direction enum fixes).

### Testing Strategy
- **D-13:** Unit tests for direction normalization and customFields access patterns. Verify entity name matching works correctly.
- **D-14:** Playtest checkpoint to verify Save→Die→Reload and room-transition E2E flows work in-game.

### Claude's Discretion
- Exact stub class rendering (placeholder sprite vs invisible)
- OneWay/HiddenLoot/Map custom_fields definitions in schema
- Whether direction normalization uses `.lower()` on all strings or only known enum fields
- Test file organization (new test file vs extending existing)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Entity Schema & Map Pipeline
- `assets/entity-schema.json` — Shared schema with pml-to-ldtk converter. Door fields, entity definitions, version field. Primary file being modified.
- `src/level/map.py` — LDtk data loading (`load_from_ldtk_simplified`), entity parsing, customFields flattening (lines 83-84), tile collision.
- `main.py` — Entity spawning (`spawn_enemies()` lines 251-329), Door spawn (lines 295-305), room loading (`on_load_room()` lines 617-661), save restore (`restore_from_save()` lines 838-895).

### Entity Classes
- `src/entities/map_entities.py` — Door class (lines 5-88), direction-dependent draw/collision logic.
- `src/core/constants.py` — TILE_SIZE, VIEWPORT_W/H, tile type constants.

### Save System
- `src/core/save_manager.py` — Save/load JSON persistence, collected_iids tracking, event_flags.

### Prior Phase Context
- `.planning/phases/14-tech-debt-schema-cleanup/14-CONTEXT.md` — Event-gated door system decisions (D-01 through D-06), entity schema v0.3.0.

### Milestone Audit (Source of Integration Issues)
- `.planning/v1.1-MILESTONE-AUDIT.md` — INT-01 through INT-04 gap definitions.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `map.py` customFields flattening (lines 83-84) — already normalizes nested fields to flat dict. Pattern to preserve.
- `Door.__init__` — accepts direction, action, event_id parameters. Already handles the fields, just needs correct input data.
- `is_item_collected()` — existing iid-based persistence check for permanent items. New stubs may need similar patterns later.

### Established Patterns
- Entity spawning: `spawn_enemies()` iterates `self.level_map.entities`, checks type name, instantiates class
- Room lifecycle: `on_load_room()` clears transient entities → calls `spawn_enemies()` → fresh state
- Persistence: `respawn` (enemies), `permanent` (items tracked by iid), `none` (doors/save points recreated)
- customFields are flattened in map.py but some spawn sites still read from nested dict

### Integration Points
- `entity-schema.json` ↔ pml-to-ldtk converter: Schema is the shared contract. Name changes here require converter awareness.
- `map.py` parse → `main.py` spawn: Direction normalization in map.py flows to all entity constructors.
- `restore_from_save()` → `spawn_enemies()`: Save restore triggers the same spawn path as room transitions.

</code_context>

<specifics>
## Specific Ideas

- Entity-schema.json is the source of truth for the pml-to-ldtk converter. Universal Metroidvania names (PlayerStart, SavePoint, Map, Door) must be standardized there so the pipeline produces correct data end-to-end.
- Map entity is a wall fixture, not a pickup — player interacts to reveal map areas (like a terminal/kiosk).
- All three new entities (OneWay, HiddenLoot, Map) are stubs-only in this phase. They need to not crash when LDtk data includes them, but functional behavior is deferred.

</specifics>

<deferred>
## Deferred Ideas

- OneWay platform collision behavior (jump-through or one-direction gate) — future phase
- HiddenLoot reveal mechanic (shot-to-reveal, proximity, etc.) — future phase
- Map fixture interaction (UP to reveal adjacent rooms on macro-map) — future phase
- Mid-room entity lifecycle audit (pause/unpause, boss triggers) — not needed for E2E unblock

</deferred>

---

*Phase: 15-ldtk-entity-door-integration*
*Context gathered: 2026-04-01*
