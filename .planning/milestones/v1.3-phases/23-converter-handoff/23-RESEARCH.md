# Phase 23: Converter Handoff - Research

**Researched:** 2026-04-08
**Domain:** Documentation -- migration handoff for pml-to-ldtk converter
**Confidence:** HIGH

## Summary

Phase 23 is a documentation-only phase. The deliverable is a single file, `CONVERTER-HANDOFF.md`, placed at the repo root. It documents all breaking changes from the v1.3 migration (Phases 20-22) that affect the pml-to-ldtk converter.

The research below inventories every before/after value change across entity-schema.json (v1.0.0 to v2.0.0) and physics-schema.json (v0.1.0 to v0.2.0), confirmed via git history. The converter maintainer needs three categories of information: (1) grid/room dimension changes, (2) entity size and hitbox changes, and (3) physics placement rule changes. All values have been extracted and cross-verified.

**Primary recommendation:** Write a self-contained CONVERTER-HANDOFF.md with before/after tables for every changed value, organized by schema file. No code changes required.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- D-01: Claude's discretion on depth, guided by CONV-01 through CONV-03
- D-02: CONVERTER-HANDOFF.md is standalone v1.3 migration note. PML-to-LDtk Converter.md stays as living reference. No duplication of purpose.
- D-03: Claude's discretion on migration guidance level, guided by CONV-03 success criterion
- D-04: All before/after values enumerated inline. Self-contained -- no cross-referencing entity-schema.json required.
- D-05: File placed in repo root, next to PML-to-LDtk Converter.md
- D-06: Only mention converter_mapping if something actually changed in v1.3. No padding with "no change" sections.

### Claude's Discretion
- Document depth and structure (D-01)
- Whether to include suggested converter actions (D-03)
- Level of detail in before/after tables

### Deferred Ideas (OUT OF SCOPE)
None.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CONV-01 | CONVERTER-HANDOFF.md documents all schema/grid changes for pml-to-ldtk agent | Complete inventory of all changes compiled below in "Change Inventory" section |
| CONV-02 | Handoff includes before/after values for grid_size, room dimensions, entity sizes | All before/after values extracted from git history -- see "Change Inventory" |
| CONV-03 | Handoff notes any breaking changes to the shared entity-schema contract | Breaking changes identified: grid_size, tileset path, tile_coords description, physics tile-unit values |
</phase_requirements>

## Change Inventory (Source Data for Handoff)

This is the core research output. All values verified against git history (pre-Phase-20 commit `dde32fe^` vs current HEAD).

### entity-schema.json: v1.0.0 -> v2.0.0

#### Level Structure (BREAKING)

| Property | Before (v1.0.0) | After (v2.0.0) | Impact |
|----------|-----------------|-----------------|--------|
| `version` | 1.0.0 | 2.0.0 | Major version bump signals breaking change |
| `level.grid_size` | 8 | 16 | BREAKING: All grid math doubles tile size |
| `level.default_room_size` | [320, 176] | [320, 176] | No change (pixels unchanged) |
| Room size in tiles | 40x22 | 20x11 | Derived: same pixels, half the tile count |
| `level.variable_rooms_note` | referenced "40x22 tiles" | references "20x11 tiles" | Note text updated |

#### Tileset (BREAKING)

| Property | Before (v1.0.0) | After (v2.0.0) | Impact |
|----------|-----------------|-----------------|--------|
| `biomes.cavern.tileset` | `assets/tiles.png` | `assets/tilesets/cavern.png` | BREAKING: Tileset path changed |
| `tile_coords` values | Same [col, row] pairs | Same [col, row] pairs | No change to actual coordinates |
| `tile_coords` description | "8px tile grid" | "16px tile grid" | Description updated |

#### IntGrid Values

No changes to intgrid values, behaviors, or broken_by arrays between v1.0.0 and v2.0.0. The intgrid mapping is identical.

#### Entity Definitions (Schema)

Entity sizes in the schema were already 16x16 in v1.0.0 (they represented visual size, not collision). No changes to entity schema entries.

| Entity | Size (v1.0.0) | Size (v2.0.0) | Change |
|--------|---------------|----------------|--------|
| PlayerStart | [16, 16] | [16, 16] | None |
| Door | [8, 8] | [8, 8] | None |
| Snail | [16, 16] | [16, 16] | None |
| Bat | [16, 16] | [16, 16] | None |
| Boss | [16, 16] | [16, 16] | None |
| All pickups | [16, 16] | [16, 16] | None |

Note: The schema entity sizes did not change. What changed was the runtime hitbox sizes in game code (Phase 22), but those are not part of the entity-schema contract. The converter only cares about LDtk entity placement sizes, which remain 16x16 (or 8x8 for Door).

#### Converter Mapping

No changes to `converter_mapping` section between v1.0.0 and v2.0.0. The `renamed_from` entries (Save -> SavePoint, StartPosition -> PlayerStart) were already present in v1.0.0.

Per D-06: converter_mapping should NOT be included in the handoff since nothing changed.

#### Simplified Export Format

No structural changes. The expected file structure (data.json, IntGrid.csv, IntGrid.png per level) is identical. What changes is the data within:
- IntGrid.csv: 40x22 grid -> 20x11 grid (half dimensions due to 2x tile size)
- Entity positions: snapped to 16px grid (most were already aligned)

### physics-schema.json: v0.1.0 -> v0.2.0

| Property | Before (v0.1.0) | After (v0.2.0) | Impact |
|----------|-----------------|-----------------|--------|
| `version` | 0.1.0 | 0.2.0 | Minor version bump |
| `tile_size` | 8 | 16 | Base unit changed |
| `player.hitbox_tiles` | [1, 1] | [1, 1] | Same (1 tile in both systems) |
| `player.hitbox_px` | [8, 8] | [10, 14] | Changed: actual collision box measured |
| `player.visual_tiles` | [2, 2] | [1, 1] | Changed: 16px sprite = 1 tile now |
| `player.visual_px` | [16, 16] | [16, 16] | Same pixels |
| `jump.max_height_tiles` | 6 | 3 | Halved (same pixels, bigger tiles) |
| `jump.max_height_px` | 62 | 62 | Same pixels |
| `jump.max_width_tiles` | 10 | 5 | Halved |
| `jump.max_width_px` | 89 | 89 | Same pixels |
| `jump.comfortable_height_tiles` | 4 | 2 | Halved |
| `jump.comfortable_width_tiles` | 7 | 3 | Halved (rounded differently) |
| `clearance.min_vertical_tiles` | 2 | 1 | Player fits in 1 tile now |
| `clearance.min_horizontal_tiles` | 2 | 1 | Player fits in 1 tile now |
| `placement_rules.max_gap_horizontal` | 10 tiles | 5 tiles | Halved |
| `placement_rules.max_gap_vertical_up` | 6 tiles | 3 tiles | Halved |
| `placement_rules.platform_min_width_tiles` | 2 | 1 | Player fits on 1 tile now |
| `source_constants.TILE_SIZE` | 8 | 16 | Base constant changed |

### LDtk Project Changes (for converter output)

These changes were made to `output.ldtk` in Phase 21 and affect what the converter must produce:

| Property | Before | After | Impact |
|----------|--------|-------|--------|
| `defaultGridSize` | 8 | 16 | All layers use 16px grid |
| Tileset `tileGridSize` | 8 | 16 | Tileset parsed as 16px tiles |
| Tileset `relPath` | `tileset.png` | `tilesets/cavern.png` | Path changed |
| Layer `gridSize` | 8 | 16 | IntGrid and entity layers |
| AutoLayerTile `src` coords | 8px-based | 16px-based (x2) | Tile source rectangles |
| Tiles per row | 32 (256/8) | 16 (256/16) | Tile ID calculation |
| IntGrid dimensions | 40x22 per standard room | 20x11 per standard room | Half tile count |
| Entity positions | 8px-aligned | 16px-aligned | Snapped to new grid |

## Architecture Patterns

### Recommended Document Structure

The handoff document should follow this structure for maximum clarity:

```
CONVERTER-HANDOFF.md
  - Header (version, date, scope)
  - TL;DR / Quick Reference (most critical changes)
  - entity-schema.json changes (before/after tables)
  - physics-schema.json changes (before/after tables)
  - LDtk output format changes
  - Suggested converter actions (optional per D-03)
```

### Key Pattern: "Same Pixels, Different Tiles"

The central insight for the converter maintainer: pixel dimensions did not change. Room size is still 320x176. Jump height is still 62px. What changed is the tile unit -- everything that was expressed in 8px tiles is now expressed in 16px tiles, so tile counts are halved.

This pattern should be emphasized prominently in the handoff to prevent confusion.

### Anti-Patterns to Avoid
- **Listing "no change" sections:** D-06 explicitly says don't pad with unchanged items. converter_mapping didn't change, so omit it.
- **Requiring cross-referencing:** D-04 says self-contained. All values must be inline.
- **Duplicating the living reference doc:** D-02 says this is a migration note, not a replacement for PML-to-LDtk Converter.md.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Before/after values | Manual reconstruction from memory | Git history extraction (already done in this research) | Accuracy -- git history is the source of truth |
| Change classification | Guessing what's breaking | Schema version bump semantics (1.0.0->2.0.0 = breaking) | Standard semver signals |

## Common Pitfalls

### Pitfall 1: Confusing Schema Entity Sizes with Runtime Hitboxes
**What goes wrong:** Documenting entity hitbox changes (Phase 22) as schema changes when the entity-schema.json entity sizes did not actually change.
**Why it happens:** Phase 22 changed runtime hitboxes in game code, but the schema entity `size` fields were already 16x16 in v1.0.0.
**How to avoid:** Clearly distinguish "schema contract values" (what the converter produces) from "game runtime values" (what the game does with those values). The converter only cares about schema values.
**Warning signs:** Writing entity before/after tables that show changes when none exist in the schema.

### Pitfall 2: Forgetting Physics Schema
**What goes wrong:** Only documenting entity-schema.json changes and missing the physics-schema.json changes.
**Why it happens:** CONV-01 through CONV-03 mention "entity-schema contract" but physics-schema is also consumed by the converter for placement rules.
**How to avoid:** Include physics-schema changes explicitly. The tile-unit values all halved and the converter uses them for gap validation and stepping stone placement.

### Pitfall 3: Over-documenting Unchanged Values
**What goes wrong:** Padding the document with "no change" entries that make it harder to find actual changes.
**Why it happens:** Desire for completeness.
**How to avoid:** Per D-06, only document what actually changed. IntGrid values didn't change. Entity schema sizes didn't change. Converter mapping didn't change.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual review (documentation phase) |
| Config file | N/A |
| Quick run command | `cat CONVERTER-HANDOFF.md` (verify file exists and has content) |
| Full suite command | Manual review against CONV-01/02/03 criteria |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CONV-01 | CONVERTER-HANDOFF.md exists with schema/grid changes | smoke | `test -f CONVERTER-HANDOFF.md && echo PASS` | Wave 0 |
| CONV-02 | Before/after values for grid_size, room dims, entity sizes present | manual | Grep for key terms in document | N/A |
| CONV-03 | Breaking changes to entity-schema contract listed | manual | Grep for "BREAKING" in document | N/A |

### Sampling Rate
- **Per task commit:** Verify file exists and contains expected sections
- **Per wave merge:** Manual review of document content against requirements
- **Phase gate:** All three CONV requirements verified

### Wave 0 Gaps
None -- this is a documentation phase. No test infrastructure needed. Verification is content review.

## Sources

### Primary (HIGH confidence)
- `assets/entity-schema.json` (current HEAD) -- v2.0.0 current state
- `assets/physics-schema.json` (current HEAD) -- v0.2.0 current state
- Git history commit `dde32fe^` -- pre-Phase-20 state of both schemas (v1.0.0 / v0.1.0)
- `.planning/phases/20-grid-constants-schema-metadata/20-CONTEXT.md` -- Phase 20 decisions
- `.planning/phases/21-tileset-ldtk-pipeline/21-CONTEXT.md` -- Phase 21 decisions
- `.planning/phases/22-entity-alignment-physics-tuning/22-CONTEXT.md` -- Phase 22 decisions

### Secondary (MEDIUM confidence)
- `PML-to-LDtk Converter.md` -- existing converter reference (partially updated in Phase 20)

## Metadata

**Confidence breakdown:**
- Change inventory: HIGH -- all values verified against git history (pre/post comparison)
- Document structure: HIGH -- constrained by CONTEXT.md decisions D-01 through D-06
- Pitfalls: HIGH -- based on actual data analysis showing entity sizes didn't change in schema

**Research date:** 2026-04-08
**Valid until:** Indefinite (documenting completed migration, no moving target)
