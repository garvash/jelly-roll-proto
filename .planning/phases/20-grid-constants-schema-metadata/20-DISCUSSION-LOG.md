# Phase 20: Grid Constants & Schema Metadata - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-08
**Phase:** 20-grid-constants-schema-metadata
**Areas discussed:** Room dimension strategy, SPRITE_SCALE removal scope, Schema version bump, Test migration, Tileset coord mapping, TILE_EMPTY sentinel, export_tilemap_csv.py

---

## Room Dimension Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Derive from pixels | Keep default_room_size as [320, 176] pixels. Derive tile counts from pixel size / grid_size. No hardcoded tile counts. | ✓ |
| Store both | Keep pixel size AND add explicit tile counts in schema and constants. Redundant but explicit. | |
| You decide | Claude picks the cleanest approach. | |

**User's choice:** Derive from pixels (Recommended)
**Notes:** None

---

## SPRITE_SCALE Removal Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Keep SPRITE_SIZE = 16 | SPRITE_SIZE stays as named constant (= TILE_SIZE). BOSS_SPRITE_SIZE = 32. No SPRITE_SCALE. | ✓ |
| Replace with TILE_SIZE | Delete SPRITE_SIZE entirely. Use TILE_SIZE everywhere. Fewer constants but conflates rendering/collision. | |
| You decide | Claude picks based on code readability. | |

**User's choice:** Keep SPRITE_SIZE = 16 (Recommended)
**Notes:** None

---

## Schema Version Bump

| Option | Description | Selected |
|--------|-------------|----------|
| 2.0.0 (major) | SemVer breaking change. grid_size change alters room tile counts and entity positions. Clear signal. | ✓ |
| 1.1.0 (minor) | Treat as feature addition since pixel dimensions don't change. Misleading for tooling. | |
| You decide | Claude picks based on SemVer conventions. | |

**User's choice:** 2.0.0 (major) (Recommended)
**Notes:** None

---

## Test Migration

| Option | Description | Selected |
|--------|-------------|----------|
| Replace assertions | Delete SPRITE_SCALE assertions. Replace with TILE_SIZE==16, SPRITE_SIZE==16, BOSS_SPRITE_SIZE==32, SPRITE_SCALE not importable. | ✓ |
| Delete test file entirely | File was testing old indirection. Constants are self-evident. | |
| You decide | Claude picks based on test value. | |

**User's choice:** Replace assertions (Recommended)
**Notes:** None

---

## Tileset Coord Mapping

| Option | Description | Selected |
|--------|-------------|----------|
| Update description only | Change description from '8px' to '16px'. Leave coordinate values for Phase 21 when tileset is ready. | ✓ |
| Update coords now | Recalculate [col, row] values for 16px grid. Risk: tileset doesn't exist yet. | |
| You decide | Claude picks based on phase boundaries. | |

**User's choice:** Update description only (Recommended)
**Notes:** None

---

## TILE_EMPTY Sentinel

| Option | Description | Selected |
|--------|-------------|----------|
| Change to (15, 15) | Bottom-right corner of 256x256 bank at 16px tiles. Keeps 'last tile' convention. | ✓ |
| Keep (31, 31) | Pyxel may handle out-of-bounds gracefully. Keep as sentinel regardless. | |
| You decide | Claude investigates Pyxel behavior and picks. | |

**User's choice:** Change to (15, 15) (Recommended)
**Notes:** None

---

## export_tilemap_csv.py

| Option | Description | Selected |
|--------|-------------|----------|
| Update it | Fix tile count math and tiles-per-row for 16px. Keep working. | ✓ |
| Delete it | autoLayerTiles pipeline made it obsolete. Remove stale code. | |
| You decide | Claude checks references and picks. | |

**User's choice:** Update it (Recommended)
**Notes:** None

---

## Claude's Discretion

- Constants ordering and comment updates in constants.py
- Schema field ordering and note updates in entity-schema.json
- variable_rooms_note text update

## Deferred Ideas

None — discussion stayed within phase scope.
