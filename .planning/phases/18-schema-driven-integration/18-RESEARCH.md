# Phase 18: Schema-Driven Integration - Research

**Researched:** 2026-04-06
**Domain:** JSON schema consumption, constant elimination, runtime tile lookup refactoring
**Confidence:** HIGH

## Summary

Phase 18 replaces all hardcoded `TILE_*` visual constants in the game with runtime lookups from `entity-schema.json`. The schema (v1.0.0, created in Phase 17) already contains all required data: `intgrid.values` with behavior strings and `biomes.cavern.tile_coords` with IntGrid-to-coordinate mappings. The refactoring is entirely internal to the game codebase -- the schema file itself does not change.

The core change is conceptual: `collision_data` currently stores tuples like `(0, 1)` (the visual tileset coordinate). After refactoring, it stores IntGrid integer values like `1`. Visual coordinates are looked up from the schema only when setting `pyxel.tilemaps` and when restoring broken blocks. Behavior checks (`is_solid`, `is_hazard`, etc.) switch from tuple comparison to set membership on IntGrid values, driven by parsing the schema's behavior strings.

**Primary recommendation:** Create `src/core/schema.py` that loads `entity-schema.json` once at startup, builds all lookup structures (val_to_tile dict, behavior sets, drain rate mapping), then refactor `map.py` and `constants.py` to consume these lookups. Update all tests that reference removed `TILE_*` constants.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Load and parse `entity-schema.json` once at game startup. Build all lookup data structures at init time.
- **D-02:** If the schema file is missing or malformed, hard crash with a clear error message. No fallback to hardcoded constants.
- **D-03:** Schema loading lives in a new `src/core/schema.py` module. Exposes typed lookups (tile coords, behavior sets, biome layers, tileset path).
- **D-04:** All `TILE_*` visual constants removed from `constants.py` (TILE_SOLID, TILE_HAZARD, TILE_DESTRUCTIBLE, TILE_SWITCH, TILE_CRACKED_H, TILE_CRACKED_V, TILE_WATER, TILE_ACID, TILE_LAVA). Only `TILE_EMPTY = (31, 31)` stays per Phase 17 D-17.
- **D-05:** `collision_data` stores IntGrid integer values (1, 2, 3, etc.) instead of tile tuples.
- **D-06:** `HAZARD_DRAIN_RATES` keys switch from tile tuples to IntGrid values (e.g., `{6: SLOW, 7: MEDIUM, 8: FAST}`). Drain rate numeric values stay as gameplay constants.
- **D-07:** Clean break -- remove all constants and update all code/tests in one shot. No deprecation period.
- **D-08:** Behavior checks driven by schema `intgrid.values` behavior strings. `schema.py` parses behavior fields and builds sets like `SOLID_VALUES = {1, 3, 11, 12}` from entries containing `"collision"` in their behavior.
- **D-09:** `is_solid()`, `is_hazard()`, `is_destructible()` etc. check IntGrid values against schema-built behavior sets instead of comparing tile tuples.
- **D-10:** Adding a new tile type with collision behavior only requires a schema entry -- no code changes needed.
- **D-11:** Hardcode `'cavern'` as the active biome. Multi-biome room selection is future milestone scope (BIOME-02).
- **D-12:** Tileset PNG loading is schema-driven -- read `biomes.cavern.tileset` path from schema and load into pyxel image bank.
- **D-13:** pml-to-ldtk converter accesses the shared schema via relative path (`../jelly-roll-proto/assets/entity-schema.json`) in the two-repo workspace.
- **D-14:** This phase documents the converter contract only. Actual converter code changes happen when working in the converter repo.
- **D-15:** Save file compatibility is not affected.
- **D-16:** Unit tests for `schema.py` (loading, val_to_tile generation, behavior set building) plus integration tests that load a real room with schema-driven tiles.
- **D-17:** Explicit schema mutation test -- modify a tile_coord value in schema and verify `pyxel.tilemaps` receives the changed coordinates. Directly validates Success Criterion 3.

### Claude's Discretion
- Internal naming in schema.py (function names, class structure)
- Whether schema.py uses a class or module-level functions
- How to structure the schema mutation test (temp file vs monkeypatch)
- Exact refactoring order (constants first vs map.py first)

### Deferred Ideas (OUT OF SCOPE)
- Per-room biome selection (BIOME-02) -- future milestone
- Actual pml-to-ldtk converter code changes -- separate repo, separate work session
- Layer/parallax rendering from schema -- Phase 19 scope
- IntGrid value 4 reclamation -- deferred from Phase 17
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SCHEMA-02 | Game loads tile-to-coordinate mappings from schema at runtime, replacing hardcoded constants in constants.py and map.py | Full code audit of constants.py (lines 19-32, 39-43), map.py (val_to_tile dict, collision_data, behavior checks), player.py (TILE_CRACKED_H/V usage, HAZARD_DRAIN_RATES), and all 8 test files importing TILE_* constants. Schema data in entity-schema.json biomes.cavern.tile_coords is ready to consume. |
| SCHEMA-03 | pml-to-ldtk converter reads tile and entity definitions from the same schema file | Schema already contains converter_mapping section. D-13/D-14 limit this phase to documenting the contract only -- actual converter changes are out of scope. |
</phase_requirements>

## Architecture Patterns

### Recommended Project Structure
```
src/
  core/
    schema.py          # NEW: Schema loading and lookup API
    constants.py       # MODIFIED: Remove TILE_* visual constants, keep TILE_EMPTY and gameplay constants
  level/
    map.py             # MODIFIED: Use schema lookups, store IntGrid ints in collision_data
  entities/
    player.py          # MODIFIED: Use IntGrid ints for TILE_CRACKED_H/V checks, updated HAZARD_DRAIN_RATES keys
```

### Pattern 1: Module-Level Schema Singleton
**What:** `schema.py` loads the JSON file once and exposes module-level functions that return pre-built data structures. No class needed -- the schema is read-only after init.
**When to use:** Always -- called once at startup before any map loading.
**Example:**
```python
# src/core/schema.py
import json
import os

_schema = None
_val_to_tile = None
_behavior_sets = None
_hazard_drain_map = None

def init(schema_path="assets/entity-schema.json"):
    """Load schema and build all lookup structures. Call once at startup.
    Raises RuntimeError if schema is missing or malformed (D-02)."""
    global _schema, _val_to_tile, _behavior_sets, _hazard_drain_map
    if not os.path.exists(schema_path):
        raise RuntimeError(f"Schema file not found: {schema_path}")
    with open(schema_path) as f:
        _schema = json.load(f)
    _build_lookups()

def _build_lookups():
    """Parse schema and build optimized lookup structures."""
    global _val_to_tile, _behavior_sets, _hazard_drain_map
    biome = "cavern"  # D-11: hardcoded for now
    tile_coords = _schema["biomes"][biome]["tile_coords"]
    
    # IntGrid value -> (col, row) tuple for pyxel.tilemaps.pset
    _val_to_tile = {}
    for key, coords in tile_coords.items():
        if key == "description":
            continue
        _val_to_tile[int(key)] = tuple(coords)
    
    # Behavior sets from intgrid.values behavior strings
    _behavior_sets = {
        "collision": set(),
        "destructible": set(),
        "damage": set(),
        "zone_hazard": set(),
        "interactive": set(),
    }
    for key, entry in _schema["intgrid"]["values"].items():
        val = int(key)
        behavior = entry.get("behavior", "none")
        if behavior == "none":
            continue
        parts = behavior.split("+")
        for part in parts:
            if part in _behavior_sets:
                _behavior_sets[part].add(val)
    
    # Hazard drain map: IntGrid value -> drain string
    _hazard_drain_map = {}
    for key, entry in _schema["intgrid"]["values"].items():
        if "drain" in entry:
            _hazard_drain_map[int(key)] = entry["drain"]

def get_val_to_tile():
    """Returns dict mapping IntGrid int -> (col, row) tuple."""
    return _val_to_tile

def get_solid_values():
    """Returns set of IntGrid values with collision behavior."""
    return _behavior_sets["collision"]

def get_hazard_values():
    """Returns set of IntGrid values with damage behavior."""
    return _behavior_sets["damage"]

def get_zone_hazard_values():
    """Returns set of IntGrid values with zone_hazard behavior."""
    return _behavior_sets["zone_hazard"]

def get_destructible_values():
    """Returns set of IntGrid values with destructible behavior."""
    return _behavior_sets["destructible"]

def get_interactive_values():
    """Returns set of IntGrid values with interactive behavior."""
    return _behavior_sets["interactive"]

def get_tileset_path():
    """Returns tileset PNG path for active biome."""
    return _schema["biomes"]["cavern"]["tileset"]

def get_layers():
    """Returns layer definitions for active biome."""
    return _schema["biomes"]["cavern"]["layers"]
```

### Pattern 2: collision_data Migration (Tuples to Ints)
**What:** `collision_data` dict changes from `{(tx,ty): (col,row)}` to `{(tx,ty): intgrid_value}`.
**Impact cascade:**
1. `map.py:load_from_ldtk_simplified()` -- store `v` directly instead of `val_to_tile[v]`
2. `map.py:is_solid()` -- check `tile in get_solid_values()` instead of `tile in (TILE_SOLID, ...)`
3. `map.py:get_zone_hazard_type()` -- return IntGrid int (6/7/8) instead of tuple
4. `map.py:restore_tile()` -- must look up visual coords from schema to call `pset()`
5. `player.py:update_shield()` -- `HAZARD_DRAIN_RATES` keys are now ints
6. `player.py` -- `TILE_CRACKED_H`/`TILE_CRACKED_V` comparisons become IntGrid value comparisons (11/12)
7. `world.py:break_block()` -- `tile_data` stored is now an IntGrid int; `restore_tile()` uses it

### Pattern 3: Behavior String Parsing
**What:** The schema's `behavior` field uses `+` delimited strings like `"collision+destructible"`. A tile with compound behavior appears in multiple behavior sets.
**Schema entries and their set membership:**

| IntGrid | Name | Behavior String | Sets |
|---------|------|-----------------|------|
| 1 | solid | `collision` | collision |
| 2 | hazard | `damage` | damage |
| 3 | soft_block | `collision+destructible` | collision, destructible |
| 5 | switch | `interactive` | interactive |
| 6 | water | `zone_hazard` | zone_hazard |
| 7 | acid | `zone_hazard` | zone_hazard |
| 8 | lava | `zone_hazard` | zone_hazard |
| 11 | cracked_h | `collision+destructible` | collision, destructible |
| 12 | cracked_v | `collision+destructible` | collision, destructible |

### Anti-Patterns to Avoid
- **Importing schema data at module level:** `schema.init()` must be called before any module uses schema data. Don't call schema functions at import time -- call them in `__init__` or on first use.
- **Partial migration:** Don't leave some checks using tuples and others using ints. Clean break per D-07.
- **Re-reading schema per room load:** Schema is loaded once at startup. `map.py` gets the val_to_tile dict reference once and reuses it.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Behavior classification | Hardcoded if/elif chains mapping IntGrid values to behaviors | Schema behavior string parsing with set membership | D-10: new tile types require only a schema entry |
| Tile coordinate lookup | Hardcoded `val_to_tile` dict in map.py | Schema-built dict from `biomes.cavern.tile_coords` | Single source of truth across game and converter |
| Drain rate mapping | `HAZARD_DRAIN_RATES` dict with tuple keys | Dict with IntGrid int keys, drain rate values from gameplay constants | Keys derived from schema, rates remain gameplay constants |

## Common Pitfalls

### Pitfall 1: restore_tile Must Look Up Visual Coords
**What goes wrong:** After refactor, `collision_data` stores ints, but `pyxel.tilemaps.pset()` still needs `(col, row)` tuples. `restore_tile(tx, ty, tile_data)` where `tile_data` is now an int must convert via `val_to_tile`.
**Why it happens:** `break_block` in `world.py` stores the collision_data value for later restoration. After migration, this is an int, not a visual tuple.
**How to avoid:** `restore_tile` must call `schema.get_val_to_tile()[tile_data]` to get the visual coords for `pset()`. Same for the initial `pset()` call in `load_from_ldtk_simplified`.
**Warning signs:** Blocks regenerate as invisible tiles or wrong visuals.

### Pitfall 2: player.py Uses Wildcard Import
**What goes wrong:** `player.py` uses `from src.core.constants import *`. Removing `TILE_CRACKED_H`, `TILE_CRACKED_V` from constants.py causes NameError at runtime in player.py lines 666, 721, 748.
**Why it happens:** Wildcard import hides which names are actually used.
**How to avoid:** Replace TILE_CRACKED_H/V references in player.py with IntGrid integer values (11, 12) or import named constants from schema. Since player.py currently compares `tile_type` (from collision_data) against these constants, and collision_data will store ints, player.py should compare against `11` and `12` directly (or named constants).
**Warning signs:** NameError on `TILE_CRACKED_H` when ram ability triggers.

### Pitfall 3: get_zone_hazard_type Return Value Change
**What goes wrong:** `get_zone_hazard_type()` currently returns a tuple (e.g., `TILE_WATER = (9, 1)`). After refactor it returns an IntGrid int (6). All callers must handle ints.
**Why it happens:** Player.py line 262 does `HAZARD_DRAIN_RATES.get(zone_type, ...)` -- the key type changes.
**How to avoid:** Ensure `HAZARD_DRAIN_RATES` keys are updated to IntGrid ints (D-06) at the same time as the collision_data migration.
**Warning signs:** Shield drain rate always falls through to default.

### Pitfall 4: Test Files Import Removed Constants
**What goes wrong:** 8 test files import `TILE_*` constants that will be removed. Tests fail with ImportError before they can even run.
**Files affected:**
- `tests/test_map_identification.py` -- imports `TILE_SOLID, TILE_HAZARD, TILE_DESTRUCTIBLE, TILE_GATE` (TILE_GATE already broken)
- `tests/test_destruction.py` -- imports `TILE_SOLID, TILE_DESTRUCTIBLE`
- `tests/test_persistence.py` -- imports `TILE_DESTRUCTIBLE, TILE_CRACKED_H, TILE_CRACKED_V`
- `tests/test_hazard_zones.py` -- imports `TILE_WATER, TILE_ACID, TILE_LAVA, TILE_SOLID, HAZARD_DRAIN_RATES`
- `tests/test_bubble_shield.py` -- imports `TILE_WATER, TILE_ACID, TILE_LAVA`
- `tests/test_ram.py` -- imports `TILE_CRACKED_H, TILE_SOLID`
- `tests/test_cracked_v.py` -- checks source text for TILE_CRACKED_V (source-reading, not import)
- `tests/test_goo_mold_removal.py` -- checks source text (source-reading, not import)
**How to avoid:** Update all test files in the same commit as the constant removal. Tests that set collision_data should use IntGrid ints. Tests that mock `get_zone_hazard_type` return values should return ints.

### Pitfall 5: test_cracked_v.py Checks Source Text
**What goes wrong:** `test_cracked_v.py` reads `src/entities/player.py` source text and asserts `TILE_CRACKED_V` is present. After refactor, player.py won't contain this string.
**How to avoid:** Update these source-text-checking tests to assert the new pattern (IntGrid value comparisons or schema-based lookups).

### Pitfall 6: Circular Import Risk
**What goes wrong:** If `schema.py` imports from `constants.py` and `constants.py` tries to use schema data, you get a circular import.
**How to avoid:** `schema.py` is independent -- it reads JSON and builds data. It does NOT import from constants.py. `constants.py` does NOT import from schema.py. The HAZARD_DRAIN_RATES dict in constants.py uses IntGrid int keys (literal numbers), not schema lookups.

### Pitfall 7: SPRITE_MANIFEST Tileset Path
**What goes wrong:** `main.py` line 141 hardcodes `"assets/tilesets/cavern.png"` in SPRITE_MANIFEST. D-12 says tileset loading should be schema-driven.
**How to avoid:** After `schema.init()`, read tileset path via `schema.get_tileset_path()` and use it for `pyxel.images[0].load()`. SPRITE_MANIFEST can keep the tiles entry but the path should come from schema.

## Code Examples

### collision_data Storage Change
```python
# BEFORE (map.py:load_from_ldtk_simplified)
self.collision_data[(tx, ty)] = val_to_tile[v]  # stores tuple (0, 1)
pyxel.tilemaps[self.tilemap_id].pset(tx, ty, val_to_tile[v])

# AFTER
from src.core import schema
val_to_tile = schema.get_val_to_tile()
self.collision_data[(tx, ty)] = v  # stores IntGrid int
pyxel.tilemaps[self.tilemap_id].pset(tx, ty, val_to_tile[v])  # visual still needs tuple
```

### Behavior Check Change
```python
# BEFORE (map.py)
def is_solid(self, tx, ty):
    tile = self.collision_data.get((tx, ty))
    return tile in (TILE_SOLID, TILE_DESTRUCTIBLE, TILE_CRACKED_H, TILE_CRACKED_V)

# AFTER
from src.core import schema
_solid_values = None

def _get_solid_values():
    global _solid_values
    if _solid_values is None:
        _solid_values = schema.get_solid_values()
    return _solid_values

def is_solid(self, tx, ty):
    tile = self.collision_data.get((tx, ty))
    return tile in _get_solid_values()
```

### HAZARD_DRAIN_RATES Key Change
```python
# BEFORE (constants.py)
HAZARD_DRAIN_RATES = {
    TILE_WATER: HAZARD_DRAIN_SLOW,   # (9, 1): 0.25
    TILE_ACID:  HAZARD_DRAIN_MEDIUM, # (10, 1): 0.75
    TILE_LAVA:  HAZARD_DRAIN_FAST,   # (11, 1): 1.5
}

# AFTER (constants.py) -- IntGrid value keys per D-06
HAZARD_DRAIN_RATES = {
    6: HAZARD_DRAIN_SLOW,   # water
    7: HAZARD_DRAIN_MEDIUM, # acid
    8: HAZARD_DRAIN_FAST,   # lava
}
```

### restore_tile Change
```python
# BEFORE (map.py)
def restore_tile(self, tx, ty, tile_data):
    self.collision_data[(tx, ty)] = tile_data  # tile_data was tuple
    pyxel.tilemaps[self.tilemap_id].pset(tx, ty, tile_data)

# AFTER
def restore_tile(self, tx, ty, tile_data):
    self.collision_data[(tx, ty)] = tile_data  # tile_data is now IntGrid int
    val_to_tile = schema.get_val_to_tile()
    visual = val_to_tile.get(tile_data, TILE_EMPTY)
    pyxel.tilemaps[self.tilemap_id].pset(tx, ty, visual)
```

### Player Cracked Block Comparison Change
```python
# BEFORE (player.py line 721)
if tile_type == TILE_CRACKED_V:
    slime.consume(DRILL_CRACKED_V_COST)

# AFTER -- IntGrid value 12 = cracked_v
INTGRID_CRACKED_V = 12  # Named constant for clarity
if tile_type == INTGRID_CRACKED_V:
    slime.consume(DRILL_CRACKED_V_COST)
```

### Schema Init in Game Startup
```python
# main.py Game.__init__
from src.core import schema

class Game:
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, title="Jelly Roll Proto", fps=60, quit_key=pyxel.KEY_NONE)
        schema.init()  # Must be before _load_sprites and map loading
        self._load_sprites()
        # ...
```

## Refactoring Impact Map

Complete list of files requiring changes:

| File | Change Type | Details |
|------|-------------|---------|
| `src/core/schema.py` | **NEW** | Schema loading, lookup API, behavior set building |
| `src/core/constants.py` | **MODIFY** | Remove 9 TILE_* constants, update HAZARD_DRAIN_RATES keys to ints |
| `src/level/map.py` | **MODIFY** | Import schema, store ints in collision_data, rewrite all is_* checks, update restore_tile/get_tile |
| `src/entities/player.py` | **MODIFY** | Replace TILE_CRACKED_H/V references with IntGrid ints (11/12), HAZARD_DRAIN_RATES already uses ints from constants |
| `main.py` | **MODIFY** | Call schema.init() at startup, schema-driven tileset path for Bank 0 |
| `tests/test_schema.py` | **MODIFY** | Add schema.py loading tests, val_to_tile tests, behavior set tests |
| `tests/test_map_identification.py` | **MODIFY** | Fix broken TILE_GATE import, use IntGrid ints in collision_data |
| `tests/test_destruction.py` | **MODIFY** | Use IntGrid ints instead of TILE_* tuples |
| `tests/test_persistence.py` | **MODIFY** | Use IntGrid ints instead of TILE_CRACKED_H/V |
| `tests/test_hazard_zones.py` | **MODIFY** | Use IntGrid ints, update HAZARD_DRAIN_RATES key assertions |
| `tests/test_bubble_shield.py` | **MODIFY** | Return IntGrid ints from mocked get_zone_hazard_type |
| `tests/test_ram.py` | **MODIFY** | Use IntGrid int 11 instead of TILE_CRACKED_H |
| `tests/test_cracked_v.py` | **MODIFY** | Update source-text assertions for new pattern |
| `tests/test_goo_mold_removal.py` | **MODIFY** | Update source-text assertions if needed (may already pass) |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | None (default discovery) |
| Quick run command | `python -m pytest tests/test_schema.py -x -q` |
| Full suite command | `python -m pytest tests/ -x -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SCHEMA-02a | schema.py loads and parses entity-schema.json | unit | `python -m pytest tests/test_schema.py::test_schema_init_loads -x` | Wave 0 |
| SCHEMA-02b | val_to_tile dict built from schema tile_coords | unit | `python -m pytest tests/test_schema.py::test_val_to_tile_from_schema -x` | Wave 0 |
| SCHEMA-02c | Behavior sets built from schema behavior strings | unit | `python -m pytest tests/test_schema.py::test_behavior_sets -x` | Wave 0 |
| SCHEMA-02d | Missing schema file causes RuntimeError (D-02) | unit | `python -m pytest tests/test_schema.py::test_missing_schema_crashes -x` | Wave 0 |
| SCHEMA-02e | Schema mutation changes rendered tiles (SC-3) | integration | `python -m pytest tests/test_schema.py::test_schema_mutation -x` | Wave 0 |
| SCHEMA-02f | No TILE_* constants remain in constants.py (except TILE_EMPTY) | unit | `python -m pytest tests/test_schema.py::test_no_hardcoded_tile_constants -x` | Wave 0 |
| SCHEMA-03 | Converter contract documented | manual | Review RESEARCH.md converter section | N/A |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_schema.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_schema.py` -- needs new tests for schema.py loading, val_to_tile, behavior sets, mutation test (D-16, D-17)
- [ ] Existing test files need IntGrid int migration -- not new files, but part of the refactoring task

## Open Questions

1. **player.py TILE_CRACKED_H/V: named constants or bare ints?**
   - What we know: player.py currently compares tile_type against TILE_CRACKED_H/TILE_CRACKED_V. After refactor, these become IntGrid values 11 and 12.
   - What's unclear: Should we define `INTGRID_CRACKED_H = 11` as a named constant in player.py (or schema.py), or use bare ints with comments?
   - Recommendation: Define named constants `INTGRID_CRACKED_H = 11` and `INTGRID_CRACKED_V = 12` in player.py or schema.py for readability. Aligns with project convention of avoiding magic numbers.

2. **map.py behavior set caching: module-level or instance-level?**
   - What we know: `is_solid()` is called many times per frame (collision checks). Looking up schema sets every call has overhead.
   - What's unclear: Cache at module level (simpler) or as LevelMap instance attributes (cleaner for testing)?
   - Recommendation: Module-level lazy cache (set once on first call). Schema is init'd before any map loading, so this is safe. For tests, schema.init() can be called with a test fixture path.

## Converter Contract Documentation

Per D-13 and D-14, the converter integration is documentation-only this phase. Key contract points:
- Converter accesses schema at `../jelly-roll-proto/assets/entity-schema.json`
- Converter reads `intgrid.values` for IntGrid value assignments
- Converter reads `converter_mapping` for entity naming rules
- Converter reads `entities` for entity field definitions
- Converter reads `simplified_export.expected_structure` for output format
- Any schema version bump requires converter verification

## Sources

### Primary (HIGH confidence)
- `assets/entity-schema.json` -- direct file read, v1.0.0 schema with all required data structures
- `src/core/constants.py` -- direct file read, 9 TILE_* constants to remove (lines 19-32)
- `src/level/map.py` -- direct file read, val_to_tile dict (lines 35-45), all behavior check methods
- `src/entities/player.py` -- direct file read, TILE_CRACKED_H/V usage at lines 666, 721, 748
- `main.py` -- direct file read, SPRITE_MANIFEST tileset path, Game.__init__ startup sequence
- All 8 test files -- direct file reads for import/usage analysis

### Secondary (MEDIUM confidence)
- Phase 17 CONTEXT.md decisions -- schema design rationale

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- pure Python/JSON, no external libraries needed
- Architecture: HIGH -- schema structure is finalized, code audit is complete
- Pitfalls: HIGH -- full grep audit of all TILE_* usages across codebase, all impact files identified

**Research date:** 2026-04-06
**Valid until:** 2026-05-06 (stable -- schema v1.0.0 is locked, codebase changes are internal refactoring)
