# Phase 22: Entity Alignment & Physics Tuning - Research

**Researched:** 2026-04-08
**Domain:** Entity collision boxes, draw_sprite offset math, physics-schema.json recalculation
**Confidence:** HIGH

## Summary

Phase 22 is a focused alignment pass: update entity collision sizes to match 16x16 visuals (established in Phase 21), simplify draw_sprite offset math where collision equals visual, and recalculate physics-schema.json tile-unit values for the new 16px base. No new gameplay, no physics constant changes, no visual changes.

The codebase is well-structured for this work. Entity hitboxes are set in `__init__` as `self.w`/`self.h`. The `draw_sprite()` function already handles bottom-center anchoring with arbitrary collision vs visual sizes. The main risk areas are: (1) the legacy spawn path in main.py still using `* 8` pixel math, (2) boss rock spawn offset using hardcoded `+ 8`, and (3) the Slime's dynamic scaling interacting with its collision size.

**Primary recommendation:** Update entity sizes in declaration order (Slime, Snail, Bat, BossRock, Mole, Effect), then simplify draw_sprite calls for 16x16=16x16 entities, then recalculate physics-schema.json. The legacy tile-scan spawn path needs `* 8` changed to `* TILE_SIZE` (or removed if dead code).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Player hitbox stays 10x14. Visual sprite is 16x16. draw_sprite bottom-center offset math remains (3px horizontal, 2px vertical overhang).
- **D-02:** Door dimensions stay 8x32 (vertical) and 32x8 (horizontal). Invisible trigger zones -- no change needed.
- **D-03:** Only update physics-schema.json tile-unit math for 16px base. No changes to actual physics constants (GRAVITY, JUMP_FORCE, etc.).
- **D-04:** Boss (Mole) collision box changes from 16x16 to 24x28. Visual sprite is 32x32. Same proportional overhang approach as the player.
- **D-05:** Hitbox inventory:
  - Player: 10x14 (no change)
  - Slime: 8x8 -> 16x16
  - Snail: 8x8 -> 16x16
  - Bat: 8x8 -> 16x16
  - Boss (Mole): 16x16 -> 24x28
  - Projectile (rock): 8x8 -> 16x16
  - Door: no change
  - Items: already 16x16
  - Effects: 8x8 -> 16x16
- **D-06:** For entities where collision == visual (16x16), draw_sprite offset math simplifies to draw_x = x, draw_y = y. For entities with smaller collision (player 10x14, boss 24x28), the bottom-center anchor offset remains.

### Claude's Discretion
- Slime hitbox may need special handling due to dynamic scaling (juice-based shrink). Claude can decide the appropriate base size and scaling behavior.
- Enemy spawn positions in existing levels may need nudging after hitbox changes. Claude can adjust as needed during execution.

### Deferred Ideas (OUT OF SCOPE)
None
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ENT-01 | Player collision box matches 16x16 visual sprite | D-01 overrides: player stays 10x14 with bottom-center offset. ENT-01 is satisfied by D-01's proportional overhang approach. |
| ENT-02 | Enemy collision boxes (Snail, Bat) match 16x16 visual sprites | Direct: change Enemy base default w=8,h=8 to w=16,h=16; update Snail/Bat constructors |
| ENT-03 | Boss collision box scaled proportionally (32x32 collision, 32x32 visual) | D-04 overrides: Mole goes to 24x28 (not 32x32). Same overhang approach as player. |
| ENT-04 | Door entity dimensions updated for 16x16 grid | D-02: doors stay 8x32/32x8 (no change). Already work as trigger zones. |
| ENT-05 | draw_sprite() offset math simplified -- collision equals visual size | D-06: simplify for 16x16=16x16 entities (Snail, Bat, Slime, Effect, Rock). Player and Boss keep offset math. |
| PHYS-01 | Jump height and gravity tuned for 16x16 tile passages | D-03: no constant changes. Pixel physics unchanged. Only update schema tile-unit descriptions. |
| PHYS-02 | Minimum passage sizes defined in new tile units (1-tile wide/tall corridors passable) | Recalculate: player 10x14 fits in 1x1 tile (16x16). Document in physics-schema.json. |
| PHYS-03 | physics-schema.json updated with 16x16 base values | Full recalculation of all tile-unit values (divide px values by 16 instead of 8). |
</phase_requirements>

## Architecture Patterns

### Entity Hitbox Pattern
All entities follow the same pattern -- hitbox set in `__init__`:
```python
class SomeEntity:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 16  # collision width
        self.h = 16  # collision height
```

The `Enemy` base class accepts `w, h` as constructor params with defaults:
```python
class Enemy:
    def __init__(self, x, y, w=8, h=8, game=None):  # <-- defaults need updating
```

Subclasses (Snail, Bat) call `super().__init__(x, y, game=game)` without explicit w/h, inheriting the base default. Changing the Enemy default from 8 to 16 propagates to all subclasses automatically.

### draw_sprite Offset Math
`draw_sprite()` in sprite_utils.py:
- **Without scale:** `draw_x = x - (visual_w - coll_w) // 2`, `draw_y = y - (visual_h - coll_h)`
- **With scale:** bottom-center anchor using `round()` math

When `coll_w == visual_w` and `coll_h == visual_h`, the offset becomes `draw_x = x`, `draw_y = y`. The function already handles this correctly -- no code change needed in sprite_utils.py itself. The simplification is that callers can rely on collision position equaling draw position.

### Slime Dynamic Scaling (Claude's Discretion)
The Slime has a `scale` property that varies from `JUICE_MIN_SCALE` (0.25) to 1.0 based on juice level. The visual scales but collision stays fixed. Current collision is 8x8.

**Recommendation:** Change Slime collision to 16x16 to match full visual. The `draw()` method already handles scaling independently -- it manually computes `scaled_w/scaled_h` from `SPRITE_SIZE * scale` and anchors bottom-center. The collision box remains fixed at 16x16 regardless of visual scale. This is the correct behavior: a smaller-looking slime still has full collision for gameplay consistency (follow, reform, punt physics all work with fixed size).

The `JUICE_MIN_SCALE` constant comment says "2x2 vs 8x8 (0.25 * 8 = 2)" -- this becomes visually 4x4 vs 16x16 at the new scale, which still looks fine as a "depleted" slime.

### Boss Rock Spawn Offset
In boss.py line 103:
```python
self.rocks.append(BossRock(self.x + 8, self.y + 8, dx, dy))
```
The `+ 8` centers the rock spawn on the current 16x16 boss. With boss changing to 24x28, this should become `self.x + self.w // 2` and `self.y + self.h // 2` to stay centered.

### Legacy Spawn Path
In main.py lines 362-382, there is a legacy tile-scan spawn path that uses `* 8` for pixel coordinates:
```python
self.enemies.append(Snail(tx * 8, ty * 8))
```
This needs updating to `tx * TILE_SIZE, ty * TILE_SIZE` -- or better, note that this legacy path may be dead code now that LDtk entity spawning is the primary path. Verify during execution.

## Exact Change Inventory

### File: src/entities/enemies.py
| Line | Current | Target | Reason |
|------|---------|--------|--------|
| 6 | `def __init__(self, x, y, w=8, h=8, game=None)` | `w=16, h=16` | ENT-02: match 16x16 visual |

No changes needed in Snail or Bat constructors -- they inherit from Enemy base.

### File: src/entities/slime.py
| Line | Current | Target | Reason |
|------|---------|--------|--------|
| 27 | `self.w = 8` | `self.w = 16` | D-05: match 16x16 visual |
| 28 | `self.h = 8` | `self.h = 16` | D-05: match 16x16 visual |

### File: src/entities/boss.py
| Line | Current | Target | Reason |
|------|---------|--------|--------|
| 43 | `self.w = 16` | `self.w = 24` | D-04: 24x28 collision |
| 44 | `self.h = 16` | `self.h = 28` | D-04: 24x28 collision |
| 13 | `self.w = 8` (BossRock) | `self.w = 16` | D-05: match 16x16 visual |
| 14 | `self.h = 8` (BossRock) | `self.h = 16` | D-05: match 16x16 visual |
| 103 | `BossRock(self.x + 8, self.y + 8, dx, dy)` | `BossRock(self.x + self.w // 2, self.y + self.h // 2, dx, dy)` | Center rock spawn on new hitbox |
| 96 | `player.take_damage(1, self.x + 8, slime=slime)` | `player.take_damage(1, self.x + self.w // 2, slime=slime)` | Knockback direction from center |

### File: src/entities/effects.py
| Line | Current | Target | Reason |
|------|---------|--------|--------|
| 33 | `draw_sprite(self.x, self.y, 8, 8, ...)` | `draw_sprite(self.x, self.y, 16, 16, ...)` | D-05: match 16x16 visual |

### File: src/entities/projectile.py
Note: The spit `Projectile` class has `self.w = 4, self.h = 4`. This is the player's spit, not the boss rock. The CONTEXT.md D-05 table does not list spit projectile -- it lists "Projectile (rock)" meaning BossRock. The spit at 4x4 is intentionally small for gameplay feel. **Do not change Projectile (spit) size.**

The `ChargeProjectile` has `self.w = CHARGE_SHOT_SIZE` (8). This is also intentional -- it's a gameplay-tuned value.

### File: main.py (legacy spawn path)
| Lines | Current | Target | Reason |
|-------|---------|--------|--------|
| 362 | `level.x // 8`, `level.y // 8`, `level.w // 8`, `level.h // 8` | `// TILE_SIZE` | Use constant |
| 369 | `Snail(tx * 8, ty * 8)` | `Snail(tx * TILE_SIZE, ty * TILE_SIZE)` | Correct pixel coords |
| 372 | `Bat(tx * 8, ty * 8)` | `Bat(tx * TILE_SIZE, ty * TILE_SIZE)` | Correct pixel coords |
| 375-382 | `Item(tx * 8, ty * 8, ...)` | `Item(tx * TILE_SIZE, ty * TILE_SIZE, ...)` | Correct pixel coords |

### File: assets/physics-schema.json
Full recalculation needed. Key new values (pixel physics unchanged, tile units recomputed):

| Field | Old (8px tiles) | New (16px tiles) | Derivation |
|-------|-----------------|-------------------|------------|
| tile_size | 8 | 16 | TILE_SIZE constant |
| player.hitbox_tiles | [1, 1] | [1, 1] | 10/16 < 1, 14/16 < 1; fits in 1 tile |
| player.hitbox_px | [8, 8] | [10, 14] | Actual collision size |
| player.visual_tiles | [2, 2] | [1, 1] | 16/16 = 1 tile |
| player.visual_px | [16, 16] | [16, 16] | Unchanged |
| jump.max_height_tiles | 6 | 3 | floor(62/16) = 3 (was floor(62/8)=7, old used 6 for safety) |
| jump.max_height_px | 62 | 62 | Unchanged (pixel physics same) |
| jump.max_width_tiles | 10 | 5 | floor(89/16) = 5 |
| jump.max_width_px | 89 | 89 | Unchanged |
| jump.comfortable_height_tiles | 4 | 2 | Conservative: ~32px comfortable |
| jump.comfortable_width_tiles | 7 | 3 | Conservative: ~48-56px comfortable |
| clearance.min_vertical_tiles | 2 | 1 | Player 14px tall < 16px tile |
| clearance.min_horizontal_tiles | 2 | 1 | Player 10px wide < 16px tile |
| placement_rules.max_gap_horizontal | 10 | 5 | Same as max_width_tiles |
| placement_rules.max_gap_vertical_up | 6 | 3 | Same as max_height_tiles |
| placement_rules.platform_min_width_tiles | 2 | 1 | Player fits in 1 tile now |
| source_constants.TILE_SIZE | 8 | 16 | Updated |

The player note should update: "Collision box is 10x14 (~1 tile). Visual sprite is 16x16 (1 tile). No SPRITE_SCALE indirection."

## Common Pitfalls

### Pitfall 1: Spit Projectile Size Confusion
**What goes wrong:** Changing the spit Projectile (4x4) to 16x16, thinking it matches the CONTEXT.md table
**Why it happens:** CONTEXT.md D-05 says "Projectile (rock)" meaning BossRock, not spit
**How to avoid:** Only change BossRock.w/h. Leave Projectile and ChargeProjectile untouched.
**Warning signs:** Spit becomes unreasonably large, makes gameplay trivial

### Pitfall 2: Boss Hardcoded Offsets
**What goes wrong:** Changing boss hitbox but leaving hardcoded `+ 8` offsets for rock spawn and damage direction
**Why it happens:** These offsets assumed a 16x16 hitbox centered at origin
**How to avoid:** Replace all `self.x + 8` and `self.y + 8` with `self.x + self.w // 2` and `self.y + self.h // 2`
**Warning signs:** Rocks spawn from boss corner instead of center

### Pitfall 3: Legacy Spawn Path Pixel Math
**What goes wrong:** Enemies spawn at wrong positions in legacy rooms
**Why it happens:** Legacy path uses `tx * 8` instead of `tx * TILE_SIZE`
**How to avoid:** Update all `* 8` to `* TILE_SIZE` in the legacy spawn scan
**Warning signs:** Enemies appear at half their expected positions

### Pitfall 4: Slime Collision-vs-Visual Mismatch During Scale
**What goes wrong:** Slime collision area appears larger than the visual when juice is low
**Why it happens:** Collision stays 16x16 but visual shrinks to 4x4 at min scale
**How to avoid:** This is acceptable and intentional -- document it. The collision box is the "real" slime; the visual just represents depletion state.
**Warning signs:** Players report hitting invisible slime collision

### Pitfall 5: Enemy Hurtbox Margin Stacking
**What goes wrong:** Enemy `HURTBOX_MARGIN = 4` on top of 16x16 collision makes effective hurtbox 24x24
**Why it happens:** The margin was tuned for 8x8 collision (effective 16x16). Now at 16x16 collision it becomes 24x24.
**How to avoid:** Consider reducing HURTBOX_MARGIN from 4 to 2. Or leave it -- more generous hit detection could feel good. This is a tuning decision to evaluate during playtesting.
**Warning signs:** Enemies feel too easy to hit from far away

### Pitfall 6: Bat Start Y Offset
**What goes wrong:** Bat's `self.start_y = y + TILE_SIZE` offsets it 16px down now instead of 8px
**Why it happens:** Bat constructor uses `TILE_SIZE` for ceiling offset. With TILE_SIZE=16, this doubles the offset.
**How to avoid:** Verify Bat placement looks correct. The offset should match 1 tile down from ceiling pivot, which is correct at 16px. But if Bats were previously spawned with y-coordinates assuming the 8px offset, positions may need adjusting.
**Warning signs:** Bats hang lower than expected from ceilings

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Bottom-center sprite anchoring | Custom offset per entity | `draw_sprite()` in sprite_utils.py | Already handles all cases correctly |
| Physics recalculation | Manual pixel-by-pixel sim | Euler integration formula: `px / TILE_SIZE` floor | Physics constants unchanged, just divide |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | None (default discovery) |
| Quick run command | `python -m pytest tests/ -x -q` |
| Full suite command | `python -m pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ENT-01 | Player hitbox is 10x14 (D-01 override) | unit | `python -m pytest tests/test_phase22.py::test_player_hitbox -x` | Wave 0 |
| ENT-02 | Snail/Bat hitbox is 16x16 | unit | `python -m pytest tests/test_phase22.py::test_enemy_hitboxes -x` | Wave 0 |
| ENT-03 | Boss hitbox is 24x28 (D-04 override) | unit | `python -m pytest tests/test_phase22.py::test_boss_hitbox -x` | Wave 0 |
| ENT-04 | Door dimensions unchanged (D-02) | unit | `python -m pytest tests/test_phase22.py::test_door_dimensions -x` | Wave 0 |
| ENT-05 | draw_sprite offset simplified for 16x16 entities | unit | `python -m pytest tests/test_phase22.py::test_draw_offset_simplified -x` | Wave 0 |
| PHYS-01 | Physics constants unchanged | unit | `python -m pytest tests/test_phase22.py::test_physics_constants_unchanged -x` | Wave 0 |
| PHYS-02 | Player fits in 1-tile passage | unit | `python -m pytest tests/test_phase22.py::test_passage_clearance -x` | Wave 0 |
| PHYS-03 | physics-schema.json has tile_size=16 | unit | `python -m pytest tests/test_phase22.py::test_physics_schema_updated -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_phase22.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_phase22.py` -- all ENT-* and PHYS-* requirement tests
- [ ] Existing tests `test_enemies.py`, `test_boss.py` will need expected values updated (enemy size 8->16, boss 16->24x28)

## Existing Test Impact

Tests that reference entity sizes and will break/need updating:

| Test File | What References Old Values | Update Needed |
|-----------|---------------------------|---------------|
| tests/test_enemies.py | Snail/Bat at default 8x8 | Assertions on .w/.h if any |
| tests/test_boss.py | Mole(50, 50, level_map) with 16x16 | Collision checks may shift |
| tests/test_phase05_gaps.py | Spawns at tx*8, ty*8; Bat offset checks | Legacy path coords |
| tests/test_phase05_nyquist.py | Bat(100, 100) size assumptions | May need hitbox updates |
| tests/test_sprite_scale.py | BOSS_SPRITE_SIZE assertions | Unchanged (visual stays 32) |

## Open Questions

1. **Legacy spawn path: dead code?**
   - What we know: main.py has both LDtk entity spawning (lines 278-350) and legacy tile-scan spawning (lines 361-382). The legacy path uses hardcoded `* 8`.
   - What's unclear: Whether any levels still use the tile-scan path. If all rooms come from LDtk, this is dead code.
   - Recommendation: Update the `* 8` to `* TILE_SIZE` for safety, even if dead code. Add a comment noting it's legacy.

2. **HURTBOX_MARGIN tuning after resize**
   - What we know: Enemy.HURTBOX_MARGIN = 4 was tuned for 8x8 collision. At 16x16, effective hurtbox is 24x24.
   - What's unclear: Whether this feels too generous.
   - Recommendation: Leave at 4 for now. Flag for playtesting.

## Sources

### Primary (HIGH confidence)
- Source code: `src/entities/enemies.py`, `src/entities/boss.py`, `src/entities/slime.py`, `src/entities/effects.py`, `src/entities/projectile.py`, `src/entities/map_entities.py`, `src/core/sprite_utils.py`, `src/core/constants.py`
- Source code: `main.py` lines 278-382 (entity spawn paths)
- Source code: `assets/physics-schema.json` (current stale values)
- Phase context: `22-CONTEXT.md` (all locked decisions)

### Secondary (MEDIUM confidence)
- Physics tile-unit recalculations derived from existing pixel values and new TILE_SIZE=16

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - pure Python/Pyxel project, no external deps needed
- Architecture: HIGH - all source files read, patterns verified
- Pitfalls: HIGH - identified from actual code review, not speculation

**Research date:** 2026-04-08
**Valid until:** 2026-05-08 (stable codebase, no external dependency changes expected)
