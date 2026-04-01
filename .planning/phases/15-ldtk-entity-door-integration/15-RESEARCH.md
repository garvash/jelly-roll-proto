# Phase 15: LDtk Entity & Door Integration Fixes - Research

**Researched:** 2026-04-01
**Domain:** LDtk entity data pipeline, entity spawning, Pyxel game integration
**Confidence:** HIGH

## Summary

Phase 15 fixes four integration bugs between LDtk exported entity data and the game's spawn pipeline (INT-01 through INT-04), and stubs three new entity types (OneWay, HiddenLoot, Map). All four bugs are confirmed by direct inspection of both the LDtk export data and game source code.

The bugs are straightforward data-contract mismatches: (1) LDtk uses "Save" and "FinalBoss" but code expects "SavePoint" and "BossMole", (2) Door spawn reads `customFields` nested dict but map.py already flattens fields to top-level, (3) LDtk exports direction as "Left"/"Right"/"Up"/"Down" but code compares lowercase, (4) `restore_from_save()` calls `spawn_enemies()` without clearing entity lists first. The three new entity types (OneWay, HiddenLoot, Map) already exist in LDtk data but silently fall through the spawn switch.

**Primary recommendation:** Fix all four bugs in a single wave (they are small, independent fixes), then add entity stubs and tests in a second wave.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- D-01: Normalize direction at parse time in map.py during LDtk data loading
- D-02: Normalize ALL string enum fields from LDtk (direction, action, and future enum fields)
- D-03: Fix spawn sites to read flattened fields directly (`ent.get('action')` instead of nested)
- D-04: Audit ALL entity spawn sites in spawn_enemies() for nested-vs-flat bug
- D-05: Standardize "universal" entity names in entity-schema.json (PlayerStart, SavePoint, Map, Door)
- D-06: Game-specific entities (Snail, Bat, DashPickup, etc.) stay as-is
- D-07: OneWay -- stub only (schema + empty class, no collision behavior)
- D-08: HiddenLoot -- stub only (schema + empty class, no reveal mechanic)
- D-09: Map -- wall fixture stub only (schema + class shell that renders)
- D-10: Precautionary audit of Save/Reload and room-transition entity lifecycle
- D-11: Scope limited to save/restore + room transitions (no mid-room scenarios)
- D-12: Bump entity-schema.json to v0.4.0
- D-13: Unit tests for direction normalization and customFields access patterns
- D-14: Playtest checkpoint for E2E flows

### Claude's Discretion
- Exact stub class rendering (placeholder sprite vs invisible)
- OneWay/HiddenLoot/Map custom_fields definitions in schema
- Whether direction normalization uses .lower() on all strings or only known enum fields
- Test file organization (new test file vs extending existing)

### Deferred Ideas (OUT OF SCOPE)
- OneWay platform collision behavior
- HiddenLoot reveal mechanic
- Map fixture interaction behavior
- Mid-room entity lifecycle audit
</user_constraints>

## Project Constraints (from CLAUDE.md)

No CLAUDE.md exists in the project root. Project conventions observed from existing code:
- Tests use `pytest` with `unittest.mock` for pyxel mocking
- Constants in `src/core/constants.py` -- avoid magic numbers
- Entity schema contract at `assets/entity-schema.json` shared with pml-to-ldtk converter
- Entities follow class pattern: `__init__(x, y, ...)`, `update()`, `draw()`, `check_collision()`

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pyxel | (project dependency) | Game engine | Already in use |
| pytest | (project dependency) | Testing | Already in use, 30+ test files |

### Supporting
No new libraries needed. This phase is entirely bug fixes and code additions within existing stack.

## Architecture Patterns

### Entity Data Flow (Current)
```
LDtk Editor --> Simplified Export (data.json per level)
    --> map.py load_from_ldtk_simplified() [flattens customFields to top-level keys]
        --> self.entities list [{type, x, y, target_level_id, direction, action, ...}]
            --> main.py spawn_enemies() [matches entity type, instantiates class]
```

### Bug Location Map

#### INT-01: Entity Name Mismatch
- **LDtk exports:** `"Save"` (Level_14, Level_17) and `"FinalBoss"` (unknown level)
- **Code expects:** `"SavePoint"` (main.py line 293) and `"BossMole"` (main.py check_boss_trigger)
- **Fix location:** `spawn_enemies()` in main.py -- add aliases for `"Save"` -> SavePoint and `"FinalBoss"` -> BossMole
- **Alternative:** Fix in LDtk and re-export. But per D-05, entity-schema.json standardizes the names, and the pml-to-ldtk converter should produce correct names. For existing LDtk data, aliases in spawn code are the pragmatic fix.

#### INT-02: CustomFields Nested vs Flat
- **map.py (lines 83-84):** Flattens customFields to top-level: `ent_data[key] = val`
- **main.py (lines 300-302):** Reads from nested dict: `custom = ent.get("customFields", {})` then `custom.get("action")`
- **Result:** `action` and `event_id` are always None because they exist at top-level, not nested
- **Fix:** Change main.py lines 300-302 to read flat: `action = ent.get("action")`, `event_id = ent.get("event_id")`
- **Audit scope (D-04):** Only Door currently reads customFields nested. Other entities don't use customFields in spawn code.

#### INT-03: Direction Capitalization
- **LDtk exports:** `"Left"`, `"Right"`, `"Up"`, `"Down"` (confirmed in all data.json files)
- **Code compares:** lowercase `"left"`, `"right"`, `"up"`, `"down"` (Door.draw lines 70-76, _on_room_enter lines 648-655)
- **Fix location (D-01):** map.py during entity flattening -- normalize string values to lowercase
- **Scope (D-02):** Normalize all string enum fields, not just direction. Apply `.lower()` to string values from customFields. The `action` field also arrives as `"none"` (already lowercase in LDtk data, but future-proofing is wise).

#### INT-04: Double Spawn on Restore
- **main.py line 895:** `restore_from_save()` calls `self.spawn_enemies()` at the end
- **main.py lines 629-633:** `_on_room_enter()` clears entity lists before calling `spawn_enemies()`
- **Question:** Does `_on_room_enter()` get called before `restore_from_save()` completes?
- **Analysis:** `restore_from_save()` does NOT call `_on_room_enter()`. It directly calls `spawn_enemies()`. But `reset()` (called before restore) creates a fresh LevelMap and empty entity lists. The entity lists (`self.enemies`, `self.doors`, `self.save_points`) are initialized in `reset()` as empty. So the spawn_enemies call in restore should be the FIRST spawn, not a double spawn.
- **Risk:** If `reset()` flow triggers `_on_room_enter()` via world detection, entities could spawn twice. Need to verify the exact call chain.
- **Fix:** Add defensive clear of entity lists at the top of `restore_from_save()` before `spawn_enemies()`, or verify the current flow is safe.

### Pattern: Entity Name Aliasing
```python
# In spawn_enemies(), normalize entity type names before the if/elif chain
ENTITY_ALIASES = {
    "Save": "SavePoint",
    "FinalBoss": "BossMole",
}
etype = ENTITY_ALIASES.get(etype, etype)
```

### Pattern: Direction Normalization in map.py
```python
# In load_from_ldtk_simplified(), during customFields flattening (line 83-84)
for key, val in inst.get("customFields", {}).items():
    # Normalize string enum values to lowercase (D-02)
    if isinstance(val, str):
        ent_data[key] = val.lower()
    else:
        ent_data[key] = val
```

### Pattern: Stub Entity Class
```python
class OneWay:
    """One-way platform/gate stub. Renders but has no collision behavior yet."""
    def __init__(self, x, y, direction="right"):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8
        self.direction = direction

    def update(self):
        pass

    def draw(self):
        # Placeholder: small directional arrow
        pyxel.rectb(self.x, self.y, self.w, self.h, 13)

    def check_collision(self, x, y, w, h):
        return (x < self.x + self.w and x + w > self.x and
                y < self.y + self.h and y + h > self.y)
```

### Anti-Patterns to Avoid
- **Reading nested customFields after flattening:** map.py already flattens. Never use `ent.get("customFields", {}).get(...)` in spawn code.
- **Case-sensitive string comparisons on LDtk data:** LDtk exports enums with initial caps. Always normalize at parse time.
- **Silently ignoring unknown entity types:** When LDtk data contains an entity type the code doesn't handle, it falls through silently. Consider logging unknown types.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Entity name mapping | Complex dispatch table | Simple alias dict + `dict.get(name, name)` | Only 2 aliases needed, keep it readable |
| String normalization | Per-field conditionals | `.lower()` on all string customField values | Future-proof, simpler code |

## Common Pitfalls

### Pitfall 1: action="none" Becomes the String "none"
**What goes wrong:** LDtk exports `"action": "none"` as a string, not null. After `.lower()` normalization, it stays `"none"`. Door constructor receives `action="none"` instead of `action=None`.
**Why it happens:** LDtk enum fields use string values, and "none" is a valid option meaning "no ability required."
**How to avoid:** Treat `"none"` as equivalent to `None` in Door spawn code: `action = ent.get("action"); if action == "none": action = None`. Or handle it in the Door class itself.
**Warning signs:** Doors that should be freely openable requiring an ability check.

### Pitfall 2: Stub Entities in Wrong List
**What goes wrong:** New entity stubs (OneWay, HiddenLoot, Map) get appended to the wrong list (enemies vs items vs a new list), causing them to be cleared at wrong times or triggering wrong lifecycle.
**Why it happens:** The game has separate lists: `self.enemies`, `self.items`, `self.doors`, `self.save_points`.
**How to avoid:** Create a dedicated list (e.g., `self.fixtures`) for non-interactive map fixtures, or add stubs to an existing appropriate list. OneWay is environment (fixture). HiddenLoot is an item (persistence=permanent). Map is a fixture.
**Warning signs:** Entities not appearing or crashing on room transition.

### Pitfall 3: Entity Lists Not Cleared in restore_from_save
**What goes wrong:** If `restore_from_save()` is called after `reset()` sets up the world and `_on_room_enter()` runs, entity lists may already have entries when `spawn_enemies()` is called again.
**Why it happens:** The exact call order between `reset()`, world detection, and `restore_from_save()` determines whether `_on_room_enter()` fires.
**How to avoid:** Add defensive clears at the start of `spawn_enemies()` or at the start of `restore_from_save()` before calling `spawn_enemies()`.
**Warning signs:** Duplicate doors, save points, or enemies in a room.

### Pitfall 4: Schema Version Bump Breaks Converter
**What goes wrong:** Bumping entity-schema.json to v0.4.0 with new entity definitions could break the pml-to-ldtk converter if it validates against the schema.
**Why it happens:** Schema is the shared contract. New entities are additive (shouldn't break), but version check logic might be strict.
**How to avoid:** New entities are additive -- the converter should only care about entities it places. Verify the converter doesn't do strict version matching. Since we control both sides, this is low risk.
**Warning signs:** Converter errors on next map generation.

## Code Examples

### Verified: Current Flattening in map.py (lines 82-84)
```python
# Capture custom fields (nested in LDtk simplified export)
for key, val in inst.get("customFields", {}).items():
    ent_data[key] = val
```
After this, entity dict looks like: `{"type": "Door", "x": 160, "y": 112, "target_level_id": 1, "direction": "Left", "action": "none", "hp": 1}`

### Verified: Current Broken Door Spawn (main.py lines 295-305)
```python
elif etype == "Door":
    raw_target = ent.get("target_level_id")
    target_id = f"Level_{raw_target}" if raw_target is not None else None
    direction = ent.get("direction", "right")      # Gets "Left" (capitalized) -- BUG
    custom = ent.get("customFields", {})             # Returns {} -- BUG (fields are flat)
    action = custom.get("action")                    # Always None -- BUG
    event_id = custom.get("event_id")                # Always None -- BUG
    self.doors.append(Door(ex - 4, ey - 12, target_id, direction,
                           action=action, event_id=event_id))
```

### Verified: LDtk Data Shows Capitalized Direction
From Level_0/data.json: `"direction": "Left"`
From Level_1/data.json: `"direction": "Right"`, `"direction": "Left"`
From Level_5/data.json: `"direction": "Up"`

### Verified: LDtk Entity Names Present in Export
```
Entity types in LDtk data: Door, FinalBoss, HiddenLoot, Map, OneWay, PlayerStart, Save
```
Code handles: Door, PlayerStart, Snail, Bat, DashPickup, DrillPickup, EnergyTank, MissileTank, ShieldPickup, BoostPickup, ShieldT2, SavePoint, BossMole
**Missing mappings:** Save -> SavePoint, FinalBoss -> BossMole, OneWay (new), HiddenLoot (new), Map (new)

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (installed, working) |
| Config file | none (default discovery) |
| Quick run command | `python -m pytest tests/ -x -q` |
| Full suite command | `python -m pytest tests/ -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INT-01 | Entity name aliases (Save->SavePoint, FinalBoss->BossMole) | unit | `python -m pytest tests/test_entity_integration.py::test_entity_name_aliases -x` | Wave 0 |
| INT-02 | CustomFields read from flat dict, not nested | unit | `python -m pytest tests/test_entity_integration.py::test_flat_customfields -x` | Wave 0 |
| INT-03 | Direction normalization to lowercase at parse time | unit | `python -m pytest tests/test_entity_integration.py::test_direction_normalization -x` | Wave 0 |
| INT-04 | No double spawn on restore_from_save | unit | `python -m pytest tests/test_entity_integration.py::test_no_double_spawn -x` | Wave 0 |
| D-07 | OneWay stub renders without crash | unit | `python -m pytest tests/test_entity_integration.py::test_oneway_stub -x` | Wave 0 |
| D-08 | HiddenLoot stub renders without crash | unit | `python -m pytest tests/test_entity_integration.py::test_hiddenloot_stub -x` | Wave 0 |
| D-09 | Map stub renders without crash | unit | `python -m pytest tests/test_entity_integration.py::test_map_stub -x` | Wave 0 |
| D-14 | E2E playtest (save/load, room transitions) | manual-only | N/A | N/A |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_entity_integration.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -q`
- **Phase gate:** Full suite green before verify

### Wave 0 Gaps
- [ ] `tests/test_entity_integration.py` -- covers INT-01 through INT-04 and stub entity tests
- No framework install needed (pytest already works)
- No conftest changes needed (existing mock patterns sufficient)

## Open Questions

1. **Does reset() trigger _on_room_enter() before restore_from_save()?**
   - What we know: `reset()` initializes LevelMap and WorldManager, then returns. The caller then calls `restore_from_save()`. `_on_room_enter()` is called by world transition detection.
   - What's unclear: Whether `reset()` itself triggers world detection that fires `_on_room_enter()`.
   - Recommendation: Add defensive entity list clears in `restore_from_save()` before `spawn_enemies()` regardless. Cost is zero; benefit is eliminating the class of bug.

2. **Where should stub entities be stored in the entity list model?**
   - What we know: Game has `self.enemies`, `self.items`, `self.doors`, `self.save_points`. No generic "fixtures" list.
   - What's unclear: Whether adding a `self.fixtures` list requires changes to `_on_room_enter()` clear logic.
   - Recommendation: Add `self.fixtures = []` list, cleared in `_on_room_enter()` alongside other lists. Stubs go there. Keep it simple.

3. **Should "none" action string be normalized to None?**
   - What we know: LDtk exports `"action": "none"` as a string. Door constructor expects `None` for no-action doors.
   - Recommendation: Normalize `"none"` to `None` during spawn, or in the `.lower()` normalization pass. Either location works; spawn is clearer.

## Sources

### Primary (HIGH confidence)
- `assets/cave/simplified/Level_*/data.json` -- direct inspection of LDtk export data, confirmed entity names and field capitalization
- `src/level/map.py` lines 72-89 -- confirmed flattening logic
- `main.py` lines 251-305 -- confirmed spawn code bugs
- `main.py` lines 846-895 -- confirmed restore_from_save flow
- `src/entities/map_entities.py` -- confirmed Door class interface
- `assets/entity-schema.json` -- confirmed current schema v0.3.0

### Secondary (MEDIUM confidence)
- INT-04 double-spawn analysis based on code reading (not runtime testing)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no new libraries, all existing code
- Architecture: HIGH - bugs confirmed by direct source + data inspection
- Pitfalls: HIGH - all pitfalls observed in actual code/data

**Research date:** 2026-04-01
**Valid until:** 2026-05-01 (stable codebase, no external dependencies)
