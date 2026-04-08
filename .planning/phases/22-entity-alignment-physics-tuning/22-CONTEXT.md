# Phase 22: Entity Alignment & Physics Tuning - Context

**Gathered:** 2026-04-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Update all entity collision boxes and physics-schema.json to reflect the 16x16 tile grid established in Phase 21. Simplify draw_sprite offset math where collision equals visual, update stale entities still using 8px sizes, and recalculate physics-schema tile-unit values. No new gameplay mechanics, no visual changes, no level design changes.

</domain>

<decisions>
## Implementation Decisions

### Player Hitbox
- **D-01:** Player hitbox stays 10x14 (set in Phase 21, felt good during playtesting). Visual sprite is 16x16. draw_sprite bottom-center offset math remains (3px horizontal, 2px vertical overhang).

### Door Dimensions
- **D-02:** Door dimensions stay 8x32 (vertical) and 32x8 (horizontal). These are invisible trigger zones -- size works fine for catching player movement. Revisit when door visuals are replaced in a future phase.

### Physics Constants
- **D-03:** Only update physics-schema.json tile-unit math for 16px base. No changes to actual physics constants (GRAVITY, JUMP_FORCE, etc.) -- the pixel-based physics are already tuned for the screen size. Tiles are visual representation of the world, not physics units.

### Boss Collision
- **D-04:** Boss (Mole) collision box changes from 16x16 to 24x28. Visual sprite is 32x32. Same proportional overhang approach as the player -- easier to hit but some dodge grace.

### Entity Hitbox Target Sizes
- **D-05:** Based on D-01 through D-04, the target hitbox inventory is:

| Entity | Current | Target | Visual | Action |
|--------|---------|--------|--------|--------|
| Player | 10x14 | 10x14 | 16x16 | No change (D-01) |
| Slime | 8x8 | 16x16 | 16x16 | Update to match visual |
| Snail | 8x8 | 16x16 | 16x16 | Update to match visual |
| Bat | 8x8 | 16x16 | 16x16 | Update to match visual |
| Boss (Mole) | 16x16 | 24x28 | 32x32 | Update per D-04 |
| Projectile (rock) | 8x8 | 16x16 | 16x16 | Update to match visual |
| Door | 8x32/32x8 | 8x32/32x8 | N/A | No change (D-02) |
| Items | 16x16 | 16x16 | 16x16 | Already correct |
| Effects | 8x8 | 16x16 | 16x16 | Update to match visual |

### draw_sprite Simplification
- **D-06:** For entities where collision == visual (16x16), draw_sprite offset math simplifies to draw_x = x, draw_y = y. For entities with smaller collision (player 10x14, boss 24x28), the bottom-center anchor offset remains. ENT-05 is satisfied where feasible.

### Claude's Discretion
- Slime hitbox may need special handling due to dynamic scaling (juice-based shrink). Claude can decide the appropriate base size and scaling behavior.
- Enemy spawn positions in existing levels may need nudging after hitbox changes. Claude can adjust as needed during execution.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Entity System
- `src/core/constants.py` -- TILE_SIZE, SPRITE_SIZE, GRAVITY, JUMP_FORCE, all physics constants
- `src/core/sprite_utils.py` -- draw_sprite() bottom-center anchor offset logic
- `src/entities/player.py` -- Player hitbox (10x14), move_and_collide collision resolution
- `src/entities/slime.py` -- Slime hitbox, dynamic scaling, collision snap
- `src/entities/enemies.py` -- Snail/Bat hitbox (param-based), collision snap
- `src/entities/boss.py` -- Mole hitbox (16x16), Projectile hitbox (8x8)
- `src/entities/map_entities.py` -- Door dimensions (8x32/32x8), SavePoint, EventGate
- `src/entities/effects.py` -- Explosion effect hitbox (8x8)
- `src/entities/items.py` -- Item hitbox (already 16x16)

### Physics Schema
- `assets/physics-schema.json` -- Stale: still has tile_size=8, TILE_SIZE=8, hitbox_px=[8,8]. Needs full recalculation.

### Prior Phase Context
- `.planning/phases/21-tileset-ldtk-pipeline/21-CONTEXT.md` -- Tile migration decisions
- `.planning/phases/21-tileset-ldtk-pipeline/21-02-SUMMARY.md` -- 2x2 tilemap pattern, entity collision snap fixes already applied

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `draw_sprite()` in sprite_utils.py already handles bottom-center anchoring with arbitrary collision vs visual sizes
- `TILE_SIZE` and `SPRITE_SIZE` constants already set to 16 in constants.py
- Collision snap in player.py already uses TILE_SIZE (fixed in Phase 21)
- Collision snap in slime.py and enemies.py already uses TILE_SIZE (fixed in Phase 21)

### Established Patterns
- Entity hitbox set in `__init__` as `self.w` and `self.h`
- Enemy class takes `w, h` as constructor params -- callers need updating
- draw_sprite handles collision-to-visual offset via `(visual_w - coll_w)` math
- physics-schema.json is consumed by pml-to-ldtk converter (external tool)

### Integration Points
- Enemy instantiation in main.py passes w/h -- need to find all spawn sites
- Boss projectile size affects dodge windows
- Slime scale affects visual size but collision stays fixed (JUICE_MIN_SCALE)

</code_context>

<specifics>
## Specific Ideas

No specific requirements -- standard alignment pass to match the 16px grid from Phase 21.

</specifics>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 22-entity-alignment-physics-tuning*
*Context gathered: 2026-04-08*
