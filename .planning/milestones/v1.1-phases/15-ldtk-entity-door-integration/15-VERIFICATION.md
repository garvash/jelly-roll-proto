---
phase: 15-ldtk-entity-door-integration
verified: 2026-04-01T00:00:00Z
status: human_needed
score: 11/11 automated must-haves verified
re_verification: false
human_verification:
  - test: "Save->Die->Reload E2E flow"
    expected: "Player saves at SavePoint, dies, reloads to SavePoint position with no duplicate entities visible"
    why_human: "Requires full game loop execution — save persistence, death screen, reload teleport, and runtime entity list inspection cannot be exercised by unit tests alone"
  - test: "Room transitions with Doors (direction correctness)"
    expected: "Player is nudged correctly into the new room after walking through a door; direction arrow renders correctly; no crash"
    why_human: "Requires running game with actual LDtk map data and player movement input through a door boundary"
  - test: "Boss room trigger via FinalBoss alias"
    expected: "Navigating to boss room triggers gate lock-down and BossMole appearance"
    why_human: "Requires navigating to a specific room in the running game; boss trigger depends on spatial proximity logic at runtime"
  - test: "Event-gated door with action='event' and event_id"
    expected: "Door with action='event' checks event_flags; opens only if flag is set"
    why_human: "Requires a door with action=event in LDtk data and a controllable event_flags state to observe open/closed behavior"
  - test: "New entity stub rendering in-game"
    expected: "If OneWay, HiddenLoot, or Map entities exist in LDtk data, they render as placeholder rectangles without crash; no 'Unknown entity type' warnings for them"
    why_human: "Requires running game with LDtk data containing these entity types and visual inspection of rendered output"
---

# Phase 15: LDtk Entity & Door Integration Fixes — Verification Report

**Phase Goal:** Fix entity name mismatches, Door customFields flattening, direction capitalization, double spawn on restore, and stub new LDtk entity types (OneWay, HiddenLoot, Map)
**Verified:** 2026-04-01
**Status:** human_needed — all automated checks pass; 5 E2E scenarios require human playtest
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (Plan 01)

| #  | Truth                                                                              | Status     | Evidence                                                                                 |
|----|------------------------------------------------------------------------------------|------------|------------------------------------------------------------------------------------------|
| 1  | LDtk entity 'Save' is recognized as SavePoint in spawn code                        | VERIFIED   | `ENTITY_ALIASES = {"Save": "SavePoint", ...}` at main.py:133; resolved in spawn_enemies (line 276), classify_room_types (line 26), check_boss_trigger (line 374), restore_from_save (line 911) — 4 sites covered including an extra site added beyond the plan |
| 2  | LDtk entity 'FinalBoss' is recognized as BossMole in spawn code                   | VERIFIED   | Same ENTITY_ALIASES dict; `ENTITY_ALIASES.get(ent["type"], ent["type"]) == "BossMole"` at line 374 |
| 3  | Door customFields (action, event_id) reach the Door constructor from LDtk data    | VERIFIED   | main.py lines 311-312: `action = ent.get("action")`, `event_id = ent.get("event_id")` — flat reads confirmed; "none" string normalized to None at line 314-315 |
| 4  | Direction values from LDtk are lowercase when consumed by game code                | VERIFIED   | map.py lines 85-88 and 92-96: `isinstance(val, str)` + `val.lower()` in both customFields loop and top-level fields loop |
| 5  | restore_from_save does not produce duplicate entities                              | VERIFIED   | main.py lines 932-940: explicit clear of enemies, items, projectiles, stains, doors, save_points, fixtures before spawn_enemies(); structural test `test_no_double_spawn_on_restore` passes |

### Observable Truths (Plan 02)

| #  | Truth                                                                              | Status     | Evidence                                                                                 |
|----|------------------------------------------------------------------------------------|------------|------------------------------------------------------------------------------------------|
| 6  | OneWay entity from LDtk data spawns without crashing                              | VERIFIED   | `class OneWay` in map_entities.py:90; wired in spawn_enemies at main.py:321-323; test_oneway_stub passes |
| 7  | HiddenLoot entity from LDtk data spawns without crashing                          | VERIFIED   | `class HiddenLoot` in map_entities.py:112; wired in spawn_enemies at main.py:324-328; test_hiddenloot_stub passes |
| 8  | Map entity from LDtk data spawns without crashing                                 | VERIFIED   | `class MapFixture` in map_entities.py:134; wired at main.py:329-330 as `elif etype == "Map"`; test_map_stub passes |
| 9  | entity-schema.json is at version 0.4.0 with all three new entities defined        | VERIFIED   | `"version": "0.4.0"` at schema line 6; OneWay (line 221), HiddenLoot (line 239), Map (line 250) all present with correct custom_fields, persistence, and notes |
| 10 | Save->Die->Reload E2E flow works in-game                                           | UNCERTAIN  | Requires human playtest (Task 2 checkpoint in Plan 02) |
| 11 | Room transitions work correctly with lowercase direction and correct Door fields    | UNCERTAIN  | Requires human playtest (Task 2 checkpoint in Plan 02) |

**Automated score:** 9/11 truths fully verified by code inspection; 2 truths require human playtest

---

### Required Artifacts

| Artifact                          | Provides                                          | Exists | Substantive | Wired   | Status      |
|-----------------------------------|---------------------------------------------------|--------|-------------|---------|-------------|
| `src/level/map.py`                | String enum normalization (val.lower())           | Yes    | Yes         | Yes     | VERIFIED    |
| `main.py`                         | ENTITY_ALIASES, flat customFields, defensive clear | Yes   | Yes         | Yes     | VERIFIED    |
| `tests/test_entity_integration.py`| 15 unit tests covering INT-01 through INT-04 + stubs | Yes | Yes         | Yes     | VERIFIED    |
| `src/entities/map_entities.py`    | OneWay, HiddenLoot, MapFixture stub classes       | Yes    | Yes         | Yes     | VERIFIED    |
| `assets/entity-schema.json`       | v0.4.0 schema with OneWay, HiddenLoot, Map        | Yes    | Yes         | N/A     | VERIFIED    |

---

### Key Link Verification

| From                          | To                              | Via                                     | Status  | Evidence                                           |
|-------------------------------|---------------------------------|-----------------------------------------|---------|----------------------------------------------------|
| `src/level/map.py`            | `main.py spawn_enemies`         | entity dict with lowercase string values | WIRED  | `isinstance(val, str)` + `val.lower()` in both loops; flat dict confirmed by test_flat_customfields |
| `main.py ENTITY_ALIASES`      | `main.py spawn_enemies` if/elif | alias resolution before type dispatch   | WIRED   | `etype = ENTITY_ALIASES.get(etype, etype)` at line 276, before all elif branches |
| `main.py restore_from_save`   | `main.py spawn_enemies`         | defensive clear before spawn            | WIRED   | Lines 932-940: 6 list clears (enemies, items, projectiles, stains, doors, save_points) + fixtures cleared at line 939 |
| `assets/entity-schema.json`   | `src/entities/map_entities.py`  | entity name matching                    | WIRED   | OneWay, HiddenLoot, MapFixture classes match schema entity names (Map -> MapFixture avoids builtin shadow) |
| `main.py spawn_enemies`       | `src/entities/map_entities.py`  | class instantiation from entity type    | WIRED   | `OneWay(ex, ey, direction)`, `HiddenLoot(ex, ey, iid=ent_iid)`, `MapFixture(ex, ey)` at lines 323, 328, 330 |
| `main.py _on_room_enter`      | `self.fixtures`                 | clear on room entry                     | WIRED   | `self.fixtures = []` at line 667 in _on_room_enter block; confirmed by test_fixtures_list_exists |

---

### Data-Flow Trace (Level 4)

| Artifact         | Data Variable | Source                         | Produces Real Data | Status    |
|------------------|---------------|--------------------------------|--------------------|-----------|
| `main.py` Door spawn | action, event_id | `ent.get("action")`, `ent.get("event_id")` (flat entity dict from map.py) | Yes — populated from LDtk customFields at parse time | FLOWING |
| `main.py` spawn_enemies entity type | etype | `ent["type"]` resolved via `ENTITY_ALIASES.get(etype, etype)` | Yes — aliases resolve to canonical names before dispatch | FLOWING |
| `main.py` restore_from_save | entity lists | cleared + re-populated by spawn_enemies() | Yes — spawns from actual level entities, not stale data | FLOWING |

---

### Behavioral Spot-Checks

| Behavior                                        | Command                                                              | Result                            | Status  |
|-------------------------------------------------|----------------------------------------------------------------------|-----------------------------------|---------|
| All 15 entity integration tests pass            | `python -m pytest tests/test_entity_integration.py -v`              | 15 passed in 0.62s                | PASS    |
| ENTITY_ALIASES dict present and correct         | `grep -n "ENTITY_ALIASES" main.py`                                   | 5 hits: definition + 4 usage sites | PASS   |
| val.lower() in both map.py loops                | `grep -n "val.lower" src/level/map.py`                               | Lines 86, 94 — both loops covered  | PASS   |
| Flat Door reads (not nested customFields)       | `grep -n 'ent.get("action")' main.py`                                | Line 311 — flat read confirmed     | PASS   |
| Defensive clear in restore_from_save            | `grep -n "self.enemies = \[\]" main.py`                              | Lines 213, 662, 933 — restore at 933 | PASS |
| entity-schema.json at v0.4.0                    | Check `"version"` field in assets/entity-schema.json                | `"version": "0.4.0"` at line 6    | PASS    |
| OneWay/HiddenLoot/MapFixture classes exist      | `grep "class OneWay\|class HiddenLoot\|class MapFixture" map_entities.py` | 3 matches at lines 90, 112, 134 | PASS |
| self.fixtures lifecycle (reset/room/restore)    | `grep -n "self.fixtures" main.py`                                    | Lines 221, 667, 939 (lifecycle) + 323, 328, 330 (spawn) + 594, 783 (update/draw) | PASS |
| Save->Die->Reload E2E                           | Requires running game                                                | —                                 | SKIP (human) |
| Room transitions with correct direction         | Requires running game                                                | —                                 | SKIP (human) |

---

### Requirements Coverage

INT-01 through INT-04 are not defined as formal entries in `.planning/REQUIREMENTS.md` — they are integration gap IDs from `.planning/v1.1-MILESTONE-AUDIT.md`. REQUIREMENTS.md records them only in the traceability section (`Phase 15: INT-01, INT-02, INT-03, INT-04`). The formal definitions are in the audit file.

| Requirement | Source Plan | Description (from v1.1 audit)                                                            | Status    | Evidence                                                        |
|-------------|-------------|-------------------------------------------------------------------------------------------|-----------|-----------------------------------------------------------------|
| INT-01      | 15-01, 15-02 | Entity name mismatches — LDtk 'Save'/'FinalBoss' vs code 'SavePoint'/'BossMole'          | SATISFIED | ENTITY_ALIASES at main.py:133 with resolution at 4 sites; tests pass |
| INT-02      | 15-01, 15-02 | Door customFields read from nested dict but map.py flattens fields to top-level keys     | SATISFIED | Flat reads at main.py:311-312; test_flat_customfields passes      |
| INT-03      | 15-01, 15-02 | Direction arrives capitalized ('Left') but compared lowercase ('left')                    | SATISFIED | `val.lower()` in both loops of map.py:85-96; test_direction_normalization passes |
| INT-04      | 15-01, 15-02 | Double spawn on load — entities accumulate before save room spawn                        | SATISFIED | Defensive clear at main.py:932-939; test_no_double_spawn_on_restore passes |

No orphaned INT requirements: all four IDs claimed in both plan frontmatters and verified as implemented.

**Note on REQUIREMENTS.md scope:** The INT-01 through INT-04 IDs do not appear as bullet-point requirements in `.planning/REQUIREMENTS.md` because they are integration gap fixes, not feature requirements. This is consistent with the file's structure — it tracks MAP/ABL/SYS features, not pipeline correctness bugs. The requirements are fully accounted for via the milestone audit.

---

### Anti-Patterns Found

| File                         | Line | Pattern                          | Severity | Impact                                                               |
|------------------------------|------|----------------------------------|----------|----------------------------------------------------------------------|
| `src/entities/map_entities.py` | 100  | `def update(self): pass`         | Info     | Intentional stub — OneWay has no update behavior yet (documented)   |
| `src/entities/map_entities.py` | 124  | `def update(self): pass`         | Info     | Intentional stub — HiddenLoot has no update behavior yet            |
| `src/entities/map_entities.py` | 141  | `def update(self): pass`         | Info     | Intentional stub — MapFixture has no update behavior yet            |

All three `pass` implementations are intentional stubs per the plan design. They are documented in the plan, schema, and SUMMARY.md Known Stubs section. None render dynamic data; they are placeholder entities awaiting future phase implementation. No blocker anti-patterns found.

---

### Human Verification Required

The following 5 scenarios cannot be verified programmatically — they require running `python main.py` and testing in the live game:

#### 1. Save->Die->Reload Flow

**Test:** Start a new game, navigate to a room with a SavePoint (should now spawn from LDtk "Save" entity), press UP to save, die, choose reload on death screen.
**Expected:** Player appears at the SavePoint location; no duplicate entities visible in the room (entity counts match single spawn).
**Why human:** Requires full game loop — save persistence to disk, death state machine transition, reload teleport, and runtime entity list state are not exercised by unit tests.

#### 2. Room Transitions with Doors

**Test:** Navigate to a door, open it (spit or kick), walk through.
**Expected:** Player is nudged correctly into the new room; direction arrow renders correctly; no crash; entrance door closes behind player after grace period.
**Why human:** Requires player input, actual LDtk map door data, and observation of the spatial nudge in a running game viewport.

#### 3. Boss Room Trigger

**Test:** Navigate to the room containing FinalBoss (aliased to BossMole), walk toward room center.
**Expected:** Boss trigger fires — gates close, BossMole appears and begins behavior.
**Why human:** Requires navigating to a specific LDtk room and observing runtime spatial trigger logic in a running game.

#### 4. Event-Gated Door

**Test:** Find a door with action="event" in current LDtk data (if one exists). Observe it with event flag unset, then set.
**Expected:** Door stays closed when event flag is unset; opens when flag is set (e.g., after boss defeat).
**Why human:** Requires a door with action=event in LDtk data, controllable event_flags state, and observation of open/closed behavior at runtime.

#### 5. New Entity Stub Rendering

**Test:** If any rooms contain OneWay, HiddenLoot, or Map entities in LDtk data, navigate to those rooms.
**Expected:** Placeholder rectangles render without crash; console shows no "Unknown entity type" warnings for these types.
**Why human:** Requires LDtk data to contain the entity types and visual confirmation that the placeholder rectb calls render correctly at the entity positions.

---

### Gaps Summary

No code gaps were found. All automated must-haves pass:

- All 4 INT bugs are fixed with evidence in source code
- ENTITY_ALIASES resolves 'Save'/'FinalBoss' at 4 call sites (including one beyond the plan's scope)
- map.py normalizes string fields to lowercase at both the customFields level and top-level inst field level
- Door action/event_id read from flat entity dict; "none" string normalized to Python None
- restore_from_save clears 6 entity lists (including fixtures) before spawn_enemies
- Three new entity stub classes exist with correct interfaces (init/update/draw/check_collision)
- entity-schema.json is at v0.4.0 with all three new entity definitions matching the stub classes
- self.fixtures lifecycle is managed in reset(), _on_room_enter(), restore_from_save(), spawn_enemies(), update(), and draw()
- Unknown entity types are logged with PlayerStart excluded
- 15 unit tests pass covering all plan acceptance criteria

**Phase status is human_needed**, not gaps_found. The outstanding item is the Task 2 checkpoint (human playtest) from Plan 02, which was explicitly marked `status: partial-checkpoint-pending` in the SUMMARY. The automated half of the phase is complete and correct.

---

_Verified: 2026-04-01_
_Verifier: Claude (gsd-verifier)_
