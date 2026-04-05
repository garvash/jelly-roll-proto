# Phase 17: Unified Schema Definition - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Extend entity-schema.json to also define tile types (IntGrid-to-tileset-coordinate mappings), layer definitions with z-order and parallax, and a per-biome tileset structure. The result is a single JSON file that is the source of truth for both tiles and entities, structured so future biomes slot in without restructuring.

</domain>

<decisions>
## Implementation Decisions

### Schema Structure
- **D-01:** `intgrid.values` stays behavior-only (name, behavior, broken_by) — shared across all biomes
- **D-02:** New top-level `biomes` key holds per-biome visual definitions: tileset image path, IntGrid-value-to-tile-coordinate mappings, and layer definitions
- **D-03:** Separation of concerns: `intgrid` = what tiles DO, `biomes` = what tiles LOOK LIKE

### Tile Coordinate Format
- **D-04:** Tile coordinates use `[col, row]` grid format matching existing constants.py convention — e.g., `[0, 1]` means column 0, row 1 on the 8px tile grid
- **D-05:** Coordinates map directly to `pyxel.tilemaps[].pset(tx, ty, (u, v))` with zero conversion

### Tileset Image Model
- **D-06:** One tileset PNG per biome (e.g., `cavern.png`, `jungle.png`)
- **D-07:** Tileset images live in `assets/tilesets/` subfolder — current `tiles.png` moves to `assets/tilesets/cavern.png`
- **D-08:** Schema references tileset via relative path in each biome's definition

### Layer & Parallax Model
- **D-09:** Layers defined per-biome as an ordered list with: name, tilemap index, z-order, scroll rate
- **D-10:** Cavern starts with 2 layers: background (tilemap 1, z: -1, scroll: 0.5) and terrain (tilemap 0, z: 0, scroll: 1.0)
- **D-11:** Foreground layer deferred — can be added to cavern later without schema changes

### Biome Extensibility
- **D-12:** Biomes are fully self-contained — no inheritance or base/default merging
- **D-13:** Each biome defines its own complete tile_coords + layers + tileset path
- **D-14:** If biomes share tile coords, they duplicate them (simple > clever for prototype)

### Schema Versioning
- **D-15:** Bump schema version to v1.0.0 — marks the unified schema milestone (tiles + entities in one file)

### Empty/Special Tile Handling
- **D-16:** IntGrid values 0 (empty) and 4 (deprecated) are excluded from biome tile_coords — absence means no visual tile
- **D-17:** `TILE_EMPTY = (31, 31)` stays as a code-level constant for tile clearing operations
- **D-18:** IntGrid value 4 can be reclaimed for a new purpose in a future phase if needed

### Claude's Discretion
- Exact key naming within the schema (e.g., `tile_coords` vs `tiles`, `scroll` vs `scroll_rate`) — as long as the structure matches the decisions above
- Whether to add a `$schema` self-reference or JSON Schema validation for the new biomes section
- How to handle the `reserved_ranges` section in intgrid — update or leave as-is

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Schema
- `assets/entity-schema.json` — Current v0.6.0 schema being extended. Contains intgrid values, entity definitions, converter_mapping, simplified_export structure.

### Tile Constants (to be replaced by schema)
- `src/core/constants.py` lines 19-32 — Hardcoded `TILE_*` tuples that map IntGrid values to (col, row) coordinates. These are the values that must be migrated into the schema's biome tile_coords.

### Tilemap Loading
- `src/level/map.py` — `load_ldtk_simplified()` builds `val_to_tile` dict from constants and populates `pyxel.tilemaps[0]`. Lines 130-138 are the core tile-setting loop. Line 332 has an existing autoLayerTiles fallback path.

### Requirements
- `.planning/REQUIREMENTS.md` — SCHEMA-01, SCHEMA-04, TILE-05 are the requirements for this phase.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `entity-schema.json` v0.6.0: Well-structured JSON with intgrid, entities, converter_mapping sections — extend rather than rewrite
- `val_to_tile` dict pattern in `map.py`: Already maps IntGrid values to tile tuples — schema will feed this dict instead of constants.py

### Established Patterns
- Constants defined in `src/core/constants.py` as UPPER_SNAKE_CASE — tile constants there will be replaced by schema lookups in Phase 18
- JSON schema uses `"$schema"` field and semver `"version"` field — maintain this convention
- Schema has `description` and `note` fields on entries for documentation — continue this pattern

### Integration Points
- `map.py:load_ldtk_simplified()` — will consume biome tile_coords (Phase 18, not this phase)
- `pml-to-ldtk converter` — reads entity-schema.json for converter_mapping; schema changes must not break existing converter fields
- `assets/tiles.png` — will be moved to `assets/tilesets/cavern.png` as part of this phase

</code_context>

<specifics>
## Specific Ideas

- Schema preview structure discussed and confirmed:
  ```json
  "intgrid": {
    "values": {
      "1": { "name": "solid", "behavior": "collision" }
    }
  },
  "biomes": {
    "cavern": {
      "tileset": "assets/tilesets/cavern.png",
      "tile_coords": {
        "1": [0, 1],
        "3": [2, 1]
      },
      "layers": [
        { "name": "bg",      "tilemap": 1, "z": -1, "scroll": 0.5 },
        { "name": "terrain", "tilemap": 0, "z": 0,  "scroll": 1.0 }
      ]
    }
  }
  ```

</specifics>

<deferred>
## Deferred Ideas

- IntGrid value 4 reclamation — find a new purpose for the deprecated value (future phase)
- Foreground layer for cavern biome — add when foreground tile art exists
- Biome inheritance/defaults — revisit if biome count grows and duplication becomes painful

</deferred>

---

*Phase: 17-unified-schema-definition*
*Context gathered: 2026-04-05*
