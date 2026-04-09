# Phase 23: Converter Handoff - Context

**Gathered:** 2026-04-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Create CONVERTER-HANDOFF.md documenting all schema/grid changes from v1.3 (16x16 tile migration) for the pml-to-ldtk converter maintainer. This is a documentation-only phase — no code changes, no converter modifications, no gameplay changes.

</domain>

<decisions>
## Implementation Decisions

### Document Scope & Depth
- **D-01:** Claude's discretion on depth, guided by CONV-01 through CONV-03 requirements. The document should be practical — enough detail that a converter maintainer knows exactly what to change without inspecting game code (CONV-03).

### Relationship to Existing Doc
- **D-02:** CONVERTER-HANDOFF.md is a standalone v1.3 migration note. `PML-to-LDtk Converter.md` stays as the living reference doc. No duplication of purpose — handoff focuses on "what changed since entity-schema v1.0.0".

### Migration Guidance Level
- **D-03:** Claude's discretion, guided by CONV-03 success criterion ("maintainer can know exactly what to change without inspecting game code"). Include suggested actions where they help the reader understand impact.

### Entity-Schema as Source of Truth
- **D-04:** All before/after values enumerated inline in the handoff. Self-contained document — no cross-referencing entity-schema.json required to understand changes. The schema remains authoritative, but the handoff duplicates the key values for readability.

### File Placement
- **D-05:** CONVERTER-HANDOFF.md placed in repo root, next to `PML-to-LDtk Converter.md`. Maximum discoverability for the converter maintainer.

### Converter Mapping
- **D-06:** Only mention converter_mapping section if something actually changed in v1.3. Don't pad the document with "no change" sections.

### Claude's Discretion
- Document depth and structure (D-01)
- Whether to include suggested converter actions (D-03)
- Level of detail in before/after tables

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Schema & Contract
- `assets/entity-schema.json` — v2.0.0, the authoritative schema the handoff documents. Contains all current values for grid_size, room dimensions, entity sizes, intgrid values, converter_mapping, biomes, and simplified export format.
- `assets/physics-schema.json` — Physics constants updated for 16px tile base in Phase 22.

### Existing Converter Documentation
- `PML-to-LDtk Converter.md` — Living reference doc for the converter. Partially updated in Phase 20 with room dimensions. Handoff supplements this, does not replace it.

### Requirements
- `.planning/REQUIREMENTS.md` §Converter Handoff — CONV-01, CONV-02, CONV-03 define acceptance criteria.

### Prior Phase Context (change inventory)
- `.planning/phases/20-grid-constants-schema-metadata/20-CONTEXT.md` — Grid constant changes: TILE_SIZE=16, SPRITE_SCALE removed, schema v2.0.0, room dims 20x11.
- `.planning/phases/21-tileset-ldtk-pipeline/21-CONTEXT.md` — LDtk project reconfigured for 16x16, tileset and autoLayerTiles adapted.
- `.planning/phases/22-entity-alignment-physics-tuning/22-CONTEXT.md` — Entity hitbox changes (Slime/Snail/Bat 8→16, Boss 16→24x28), physics-schema recalculated.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `assets/entity-schema.json` — Contains complete current state of all values the handoff needs to document. Before values must be reconstructed from Phase 20-22 context files and git history.
- `PML-to-LDtk Converter.md` — Already has partial v1.3 updates (room dimensions table). Handoff can reference its format style for consistency.

### Established Patterns
- Prior milestone handoffs were informal (no dedicated handoff doc existed before). This is the first formal converter handoff document.
- `converter_mapping` section in entity-schema.json already has a `renamed_from` pattern for tracking name changes.

### Integration Points
- The handoff is consumed by a separate repository (pml-to-ldtk converter). No runtime integration — purely documentation.
- `entity-schema.json` is the shared contract between game and converter.

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 23-converter-handoff*
*Context gathered: 2026-04-08*
