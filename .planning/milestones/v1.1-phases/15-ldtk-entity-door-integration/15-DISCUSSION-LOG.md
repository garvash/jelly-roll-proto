# Phase 15: LDtk Entity & Door Integration Fixes - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-01
**Phase:** 15-ldtk-entity-door-integration
**Areas discussed:** Direction normalization, CustomFields flattening, New entity stubs, Double-spawn guard, Entity name mismatches, Schema version bump, Testing strategy

---

## Direction Normalization

| Option | Description | Selected |
|--------|-------------|----------|
| At parse time in map.py | Normalize all string fields when loading LDtk data. One fix, all entities benefit. | ✓ |
| At spawn time in main.py | Call .lower() when extracting direction from entity dict. | |
| In Door constructor | Door.__init__ calls direction.lower(). Entity-specific. | |

**User's choice:** At parse time in map.py (Recommended)

| Option | Description | Selected |
|--------|-------------|----------|
| All string enums | Normalize direction, action, and any future enum fields to lowercase during parse. | ✓ |
| Just direction | Only fix the known broken field. | |

**User's choice:** All string enums (Recommended)

---

## CustomFields Flattening

| Option | Description | Selected |
|--------|-------------|----------|
| Fix spawn site in main.py | Update main.py to read flattened fields directly from entity dict. | ✓ |
| Remove flattening from map.py | Keep customFields nested as LDtk exports them. | |
| You decide | Claude picks whichever approach is cleaner. | |

**User's choice:** Fix spawn site in main.py (Recommended)

| Option | Description | Selected |
|--------|-------------|----------|
| Audit all spawn sites | Check every entity type in spawn_enemies() for incorrect customFields access. | ✓ |
| Just Door | Only fix the known-broken Door spawn. | |

**User's choice:** Audit all spawn sites (Recommended)

---

## New Entity Stubs

### OneWay

| Option | Description | Selected |
|--------|-------------|----------|
| Jump-through platform | Solid from above, pass-through from below/sides. | |
| One-direction gate | Blocks from one side, allows from other. | |
| Stub only | Schema definition + empty class. Behavior deferred. | ✓ |

**User's choice:** Stub only — no behavior yet

### HiddenLoot

| Option | Description | Selected |
|--------|-------------|----------|
| Shot-to-reveal | Invisible until hit by projectile. | |
| Proximity-reveal | Appears when player gets close. | |
| Stub only | Schema definition + empty class. Behavior deferred. | ✓ |

**User's choice:** Stub only — no behavior yet

### Map

| Option | Description | Selected |
|--------|-------------|----------|
| Pickup item | Player collects it, reveals map area. Tracked by iid. | |
| Wall fixture | Terminal/sign in room. Player interacts to reveal map. Not consumed. | ✓ |
| Stub only | Schema definition + empty class. Behavior deferred. | |

**User's choice:** Wall fixture

| Option | Description | Selected |
|--------|-------------|----------|
| Stub only — schema + class shell | Define in schema, renders but no interaction yet. | ✓ |
| Basic interaction now | Player presses UP to reveal adjacent rooms. | |

**User's choice:** Stub only — schema + class shell

---

## Entity Name Mismatches

**User's choice:** Free-text response — standardize universal Metroidvania entity names (PlayerStart, SavePoint, Map, Door) in entity-schema.json as the shared contract with pml-to-ldtk converter. Game-specific entities (Snail, Bat, etc.) stay as-is.

---

## Schema Version Bump

| Option | Description | Selected |
|--------|-------------|----------|
| Bump to v0.4.0 | New entity stubs + direction fix is a minor schema change. | ✓ |
| Stay at v0.3.0 | Stubs have no behavior yet. Don't bump until functional. | |
| You decide | Claude picks based on converter needs. | |

**User's choice:** Bump to v0.4.0

---

## Testing Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Unit tests for normalization + spawn audit | Test direction normalization, customFields reading, entity name matching. | |
| Playtest verification only | Manual Save→Die→Reload and room-transition playtest. | |
| Both | Unit tests for parse/normalize fixes + playtest checkpoint for E2E flows. | ✓ |

**User's choice:** Both

---

## Claude's Discretion

- Exact stub class rendering (placeholder sprite vs invisible)
- OneWay/HiddenLoot/Map custom_fields definitions in schema
- Whether direction normalization uses `.lower()` on all strings or only known enum fields
- Test file organization

## Deferred Ideas

- OneWay platform collision behavior — future phase
- HiddenLoot reveal mechanic — future phase
- Map fixture interaction behavior — future phase
- Mid-room entity lifecycle audit — out of scope for Phase 15
