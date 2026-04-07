# Phase 18: Schema-Driven Integration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-05
**Phase:** 18-schema-driven-integration
**Areas discussed:** Schema loading strategy, Constant elimination scope, Converter integration, Behavior lookup model, Biome selection at runtime, Test strategy, Migration / backwards compat

---

## Schema Loading Strategy

### Q1: When should the game load the schema?

| Option | Description | Selected |
|--------|-------------|----------|
| Startup once | Load and parse once at game init, build val_to_tile from biomes.cavern.tile_coords | ✓ |
| Per-room load | Re-read schema each room load for hot-reloading | |
| You decide | Claude picks | |

**User's choice:** Startup once
**Notes:** Matches current pattern where constants are available globally.

### Q2: If schema is missing or malformed?

| Option | Description | Selected |
|--------|-------------|----------|
| Hard crash with message | Game refuses to start with clear error | ✓ |
| Fallback to hardcoded | Keep constants as fallback | |
| You decide | Claude picks | |

**User's choice:** Hard crash with message
**Notes:** Schema is required infrastructure — no fallback for prototype.

### Q3: Where should schema loading code live?

| Option | Description | Selected |
|--------|-------------|----------|
| New src/core/schema.py | Dedicated module with typed lookups | ✓ |
| Inside constants.py | Mix static and dynamic config | |
| Inside map.py | Load where consumed | |

**User's choice:** New src/core/schema.py

---

## Constant Elimination Scope

### Q1: What replaces TILE_* constants in collision/behavior checks?

| Option | Description | Selected |
|--------|-------------|----------|
| IntGrid values | collision_data stores ints, is_solid() checks value sets | ✓ |
| Named constants from schema | schema.py exposes SOLID=1 etc. | |
| Keep tile tuples | val_to_tile from schema but collision still uses tuples | |

**User's choice:** IntGrid values
**Notes:** Decouples collision from visuals entirely — aligns with Phase 17 separation.

### Q2: Should HAZARD_DRAIN_RATES switch to IntGrid keys?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, IntGrid keys | {6: SLOW, 7: MEDIUM, 8: FAST} | ✓ |
| Move drain rates to schema | Add numeric drain values to schema | |
| You decide | Claude picks | |

**User's choice:** Yes, IntGrid keys

---

## Converter Integration

### Q1: How should the converter access the shared schema?

| Option | Description | Selected |
|--------|-------------|----------|
| Manual copy | Copy file when it changes | |
| Git submodule | Formal dependency tracking | |
| Symlink / shared path | Both repos reference same file | |
| Relative path | ../jelly-roll-proto/assets/entity-schema.json | ✓ |

**User's choice:** Relative path
**Notes:** User has a two-repo workspace setup. Initially asked about submodule approach — after discussing pros/cons, chose relative path as simplest for prototype.

### Q2: What converter changes in scope?

| Option | Description | Selected |
|--------|-------------|----------|
| Document contract only | Focus on game-side, document converter expectations | ✓ |
| Both game + converter | Implement in both repos | |
| You decide | Claude picks | |

**User's choice:** Document contract only

---

## Behavior Lookup Model

### Q1: Schema behavior strings or hardcoded IntGrid value sets?

| Option | Description | Selected |
|--------|-------------|----------|
| Schema behavior strings | Parse intgrid.values behavior fields, build sets dynamically | ✓ |
| Hardcoded IntGrid sets | Explicit value lists in code | |
| You decide | Claude picks | |

**User's choice:** Schema behavior strings
**Notes:** Adding new tile types only requires schema entry — no code changes.

### Q2: collision_data storage model?

| Option | Description | Selected |
|--------|-------------|----------|
| IntGrid values only | collision_data[(tx,ty)] = int | ✓ |
| Both value and category | Richer object with precomputed flags | |

**User's choice:** IntGrid values only

---

## Biome Selection at Runtime

### Q1: How to determine which biome?

| Option | Description | Selected |
|--------|-------------|----------|
| Hardcode 'cavern' | Default biome, multi-biome is future scope | ✓ |
| Config parameter | Pass biome name, default cavern | |
| You decide | Claude picks | |

**User's choice:** Hardcode 'cavern'

### Q2: Should tileset PNG loading be schema-driven?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, from schema path | Read biomes.cavern.tileset path from schema | ✓ |
| Keep current loading | Just update hardcoded path | |
| You decide | Claude picks | |

**User's choice:** Yes, from schema path

---

## Test Strategy

### Q1: Testing level?

| Option | Description | Selected |
|--------|-------------|----------|
| Unit + integration | Unit tests for schema.py + integration with real room loading | ✓ |
| Unit tests only | Test schema.py in isolation | |
| You decide | Claude picks | |

**User's choice:** Unit + integration

### Q2: Explicit schema mutation test for SC-3?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, schema mutation test | Modify tile_coord, verify pyxel.tilemaps changes | ✓ |
| No, trust the pipeline | Implicit satisfaction | |

**User's choice:** Yes, schema mutation test

---

## Migration / Backwards Compat

### Q1: How to handle TILE_* removal?

| Option | Description | Selected |
|--------|-------------|----------|
| Clean break | Remove all, update all code/tests at once | ✓ |
| Deprecation period | Keep as aliases, remove later | |
| You decide | Claude picks | |

**User's choice:** Clean break

### Q2: Save file compatibility concern?

| Option | Description | Selected |
|--------|-------------|----------|
| No concern | Saves use coordinates/IIDs, not tile tuples | ✓ |
| Need to verify | Check save system first | |
| You decide | Claude checks | |

**User's choice:** No concern

---

## Claude's Discretion

- Internal naming in schema.py (function names, class structure)
- Whether schema.py uses a class or module-level functions
- How to structure the schema mutation test
- Exact refactoring order

## Deferred Ideas

- Per-room biome selection (BIOME-02) — future milestone
- Actual pml-to-ldtk converter code changes — separate repo
- Layer/parallax rendering — Phase 19
- IntGrid value 4 reclamation — deferred from Phase 17
