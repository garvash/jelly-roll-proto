# Phase 10: Nitro-Ejection & Endgame (ABL-02) - Research

**Researched:** 2026-03-28
**Domain:** Pyxel 2.x game engine -- vertical traversal gating, gamepad input, ability VFX, code cleanup
**Confidence:** HIGH

## Summary

Phase 10 has four distinct workstreams: (1) CRACKED_V block breaking via Drill Dive (downward) and Slime Boost (upward), (2) gamepad controller support via Pyxel's built-in GAMEPAD1_* constants, (3) minimal VFX using existing Particle/Effect patterns, and (4) Goo-Mold code removal. All workstreams build on well-established codebase patterns with no new libraries or architectural changes required.

The CRACKED_V breaking is the most nuanced workstream. Drill Dive already passes through destructible tiles including CRACKED_V (since `is_destructible()` includes CRACKED_V), but the collision handler hardcodes `TILE_DESTRUCTIBLE` in `on_block_destroyed()` and gives a juice refund -- both wrong for gate blocks. Boost has no upward collision check at all. A new `get_cracked_v_at()` method on LevelMap and a ceiling collision branch for BOOSTING state are needed.

**Primary recommendation:** Implement CRACKED_V breaking and gamepad support first (core functionality), then Goo-Mold cleanup (safe deletion), then VFX (polish layer). The ability tuning pass should happen throughout as edge cases are discovered.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Drill Dive breaks CRACKED_V blocks on downward contact. Same pattern as existing TILE_DESTRUCTIBLE breaking -- player dives through, blocks break as they pass. Consistent with current drill behavior.
- **D-02:** Slime Boost breaks CRACKED_V blocks on upward contact during flight. Mirrors Drill Dive symmetry -- downward=Drill, upward=Boost. Enables two-way vertical passages through previously one-way routes.
- **D-03:** Both abilities break CRACKED_V on first contact -- no multi-hit durability, no fused-only requirement.
- **D-04:** Standard platformer button layout: D-pad=movement, A=Jump/Boost/Drill, B=Spit/Recall/Charge, X=Dash/Ram, Y=unused, Start=reserved.
- **D-05:** Implementation via existing `_ACTION_MAP` in `src/core/input.py`. Add Pyxel gamepad constants to each action's key list.
- **D-06:** Remove TILE_GOO_MOLD entirely from codebase (constants.py, map.py, entity-schema.json).
- **D-07:** No LDtk maps currently use Goo-Mold tiles, so no data migration needed.
- **D-08:** Full tuning pass across all 6 abilities: Dash, Ram, Drill Dive, Charge Shot, Bubble Shield, Slime Boost.
- **D-09:** Focus areas: state transitions, collision edge cases, ability cancellation rules.
- **D-10:** Minimal VFX using Pyxel built-in drawing primitives (pyxel.pix/circ/rect). Ram=screen shake, Drill=particles, Charge=flash, Boost=trail, Shield=circle flash.
- **D-11:** No audio/sound effects in this phase.
- **D-12:** "Nitro-Ejection" is not a separate ability. Infinite jump is emergent from SYS-04 juice capacity upgrades.
- **D-13:** Infinite juice threshold logic deferred to Phase 11.

### Claude's Discretion
- Specific tuning constant values (boost force, dash speed, i-frame durations, etc.)
- Exact VFX implementation details (particle count, shake magnitude, trail length)
- Order of ability tuning (which to address first)
- Edge case prioritization during the tuning pass

### Deferred Ideas (OUT OF SCOPE)
- Infinite juice threshold (SYS-04 dependent) -- Phase 11
- Pyxel audio/SFX -- separate pass later
- New block type replacing Goo-Mold slot (IntGrid value 10)
- 5x5mapdesign.txt cleanup/archival
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pyxel | 2.8.7 | Game engine with built-in gamepad support | Already in use, GAMEPAD1_* constants verified available |
| pytest | (existing) | Unit tests | 201 tests already in place, established test patterns |

### Supporting
No new libraries needed. All work uses existing Pyxel primitives and project patterns.

## Architecture Patterns

### Recommended Project Structure
No new files needed. All changes go into existing files:
```
src/
  core/
    input.py          # Add GAMEPAD1_* constants to _ACTION_MAP
    constants.py      # Remove TILE_GOO_MOLD, add VFX constants
  level/
    map.py            # Remove goo-mold methods, add get_cracked_v_at()
  entities/
    player.py         # CRACKED_V collision in DIVING + BOOSTING, VFX triggers
    effects.py        # New effect types (trail, flash, circle)
assets/
  entity-schema.json  # Remove IntGrid value 10 (goo_mold)
```

### Pattern 1: Gamepad Input Extension
**What:** Add Pyxel GAMEPAD1_* constants to existing `_ACTION_MAP` lists
**When to use:** This is the only gamepad pattern needed -- Pyxel treats gamepad buttons identically to keyboard keys via `pyxel.btn()`/`pyxel.btnp()`/`pyxel.btnr()`.
**Example:**
```python
# Source: src/core/input.py (existing pattern, extended)
import pyxel

_ACTION_MAP = {
    "left":   [pyxel.KEY_LEFT, pyxel.KEY_A, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT],
    "right":  [pyxel.KEY_RIGHT, pyxel.KEY_D, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT],
    "up":     [pyxel.KEY_UP, pyxel.KEY_W, pyxel.GAMEPAD1_BUTTON_DPAD_UP],
    "down":   [pyxel.KEY_DOWN, pyxel.KEY_S, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN],
    "jump":   [pyxel.KEY_SPACE, pyxel.GAMEPAD1_BUTTON_A],
    "spit":   [pyxel.KEY_Z, pyxel.KEY_J, pyxel.GAMEPAD1_BUTTON_B],
    "dash":   [pyxel.KEY_V, pyxel.KEY_K, pyxel.GAMEPAD1_BUTTON_X],
}
```
**Confidence:** HIGH -- Pyxel 2.8.7 GAMEPAD1_* constants verified present via runtime inspection.

### Pattern 2: CRACKED_V Breaking (Drill Dive -- Downward)
**What:** Modify the existing Drill Dive collision in `move_and_collide()` to distinguish CRACKED_V from TILE_DESTRUCTIBLE
**When to use:** When player in DIVING state collides downward with a CRACKED_V tile
**Key difference from soft blocks:** CRACKED_V is a gate block -- it should cost juice (like Ram costs for CRACKED_H) rather than refund juice. The current code gives `DRILL_BLOCK_REFUND` for all destructible blocks.
**Example:**
```python
# In move_and_collide, DIVING downward collision:
if self.state == "DIVING" and slime:
    tile_coord = self.level_map.get_destructible_at(self.x, self.y, self.w, self.h)
    if tile_coord:
        tx, ty = tile_coord
        tile_type = self.level_map.get_tile(tx, ty)
        if self.game:
            self.game.on_block_destroyed(tx, ty, tile_type)  # Pass actual type, not hardcoded
        self.level_map.remove_tile(tx, ty)
        if self.game:
            self.game.spawn_explosion(tx * TILE_SIZE, ty * TILE_SIZE, 9)
        if tile_type == TILE_CRACKED_V:
            slime.consume(DRILL_BLOCK_COST)  # Gate cost, no refund
        else:
            slime.refill(DRILL_BLOCK_REFUND)  # Soft block refund
        self.on_block_break()
        return
```

### Pattern 3: CRACKED_V Breaking (Boost -- Upward)
**What:** Add ceiling collision check during BOOSTING state to break CRACKED_V blocks
**When to use:** When player in BOOSTING state has upward velocity (dy < 0) and collides with ceiling
**Critical insight:** The current ceiling collision code (line 692-695) just snaps and zeroes dy. It needs a pre-check for CRACKED_V similar to how Ram checks for CRACKED_H in horizontal collision.
**Example:**
```python
# In move_and_collide, vertical collision, dy < 0 branch:
elif self.dy < 0:
    # Check for CRACKED_V during Boost (ABL-02, D-02)
    if self.state == "BOOSTING" and slime:
        cracked = self.level_map.get_cracked_v_at(self.x, self.y, self.w, self.h)
        if cracked:
            tx, ty = cracked
            if self.game:
                self.game.on_block_destroyed(tx, ty, TILE_CRACKED_V)
            self.level_map.remove_tile(tx, ty)
            if self.game:
                self.game.spawn_explosion(tx * TILE_SIZE, ty * TILE_SIZE, 9)
            slime.consume(BOOST_JUICE_COST)  # Or a separate BOOST_BREAK_COST
            self.on_block_break()
            return  # Continue through broken block
    # Snap to ceiling
    self.y = (int(self.y // TILE_SIZE) + 1) * TILE_SIZE
    self.dy = 0
```

### Pattern 4: LevelMap.get_cracked_v_at() (New Method)
**What:** Mirror of existing `get_cracked_h_at()` for vertical cracked blocks
**Example:**
```python
# Source: follows established get_cracked_h_at pattern in map.py
def get_cracked_v_at(self, x, y, width, height):
    """Returns (tx, ty) of a CRACKED_V tile overlapping the AABB, or None.
    Used by Drill Dive and Slime Boost for vertical gate breaking (ABL-02)."""
    x1 = int(x // TILE_SIZE)
    y1 = int(y // TILE_SIZE)
    x2 = int((x + width - 1) // TILE_SIZE)
    y2 = int((y + height - 1) // TILE_SIZE)
    for ty in range(y1, y2 + 1):
        for tx in range(x1, x2 + 1):
            if self.is_cracked_vertical(tx, ty):
                return (tx, ty)
    return None
```

### Pattern 5: VFX via Existing Effect/Particle System
**What:** Use existing `Particle` class for pixel effects, `Effect` for sprite-based animations, and `game.shake_timer` for screen shake
**When to use:** All VFX in this phase
**Key observation:** The project already has a working particle system (`src/entities/effects.py`) with gravity, random spread, and lifetime. Screen shake is already implemented in `main.py` draw loop. New VFX only needs new trigger points and possibly new effect_type strings.
```python
# Ram impact VFX -- screen shake already exists, just set timer:
self.game.shake_timer = 3  # 3-frame shake (D-10)

# Drill block break -- already calls spawn_explosion() with 8 particles

# Boost trail -- spawn 2-3 particles downward on each boost tap:
for _ in range(3):
    self.game.particles.append(Particle(self.x + 4, self.y + 8, 11))  # Color 11 = green

# Charge shot flash -- single frame bright pixel at spawn point:
# Can use a short-lived Effect or direct pyxel.circ in draw
```

### Anti-Patterns to Avoid
- **Hardcoding tile types in on_block_destroyed:** Current code passes `TILE_DESTRUCTIBLE` even for CRACKED_V. Must pass actual tile type for proper regen tracking.
- **Juice refund for gate blocks:** CRACKED_V is a progression gate, not a resource block. Breaking it should cost juice, not refund.
- **Bare is_fused assignments:** Always use `fuse()`/`unfuse()` atomic pair (Pitfall 3 from Phase 08).
- **Direct pyxel.btn() calls:** Always use `input_manager.btn()` to maintain abstraction layer.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Gamepad input | Custom SDL/input polling | Pyxel GAMEPAD1_* constants in _ACTION_MAP | Pyxel handles all controller detection internally |
| Screen shake | Custom camera offset system | Existing `game.shake_timer` + draw offset | Already implemented and working |
| Particles | Custom particle engine | Existing `Particle` class in effects.py | Has gravity, spread, lifetime, draw culling |
| Sprite effects | Frame-based animation system | Existing `Effect` class in effects.py | Already handles 3-frame animations |

## Common Pitfalls

### Pitfall 1: Drill Dive Already Breaks CRACKED_V (Partially)
**What goes wrong:** `is_destructible()` already returns True for CRACKED_V, so Drill Dive can already break them -- but with wrong juice behavior (refund instead of cost) and wrong block type tracking (hardcoded TILE_DESTRUCTIBLE).
**Why it happens:** CRACKED_V was added to `is_destructible()` for collision grouping, and the drill collision handler treats all destructible tiles identically.
**How to avoid:** In the drill collision handler, check the actual tile type via `get_tile(tx, ty)` and branch behavior: soft blocks get refund, gate blocks get cost.
**Warning signs:** Tests passing despite not "implementing" drill vs CRACKED_V. Blocks breaking but juice going UP instead of down.

### Pitfall 2: Boost Upward Collision Has No Block Breaking Path
**What goes wrong:** Boost moves player upward (dy < 0), but the ceiling collision code (dy < 0 branch) just snaps to ceiling and zeroes velocity. There is no destructible tile check.
**Why it happens:** The dy < 0 branch was written for basic ceiling bonk, before any ability needed to break ceiling blocks.
**How to avoid:** Add a CRACKED_V check before the ceiling snap, mirroring how Ram checks CRACKED_H before horizontal wall snap.
**Warning signs:** Player bonks off CRACKED_V blocks from below during Boost instead of breaking them.

### Pitfall 3: Boost Through Multiple CRACKED_V Blocks
**What goes wrong:** If two CRACKED_V blocks are stacked vertically and the player boosts through, only one might break because the collision handler returns after the first.
**Why it happens:** The collision check returns on first destructible tile found. Same issue exists for Drill Dive with vertically stacked soft blocks.
**How to avoid:** After breaking a block and returning (to continue through), the next frame's collision check will catch the next block. This is the existing drill pattern and works correctly -- just verify it works for upward movement too.
**Warning signs:** Second block in a stack not breaking.

### Pitfall 4: Gamepad D-pad Interfering with Directional Slime Hold
**What goes wrong:** D-pad taps trigger `was_tap()` for left/right, which repositions the slime. Gamepad players might trigger accidental slime repositions when tapping directions.
**Why it happens:** The `was_tap()` threshold (HOLD_TAP_THRESHOLD = 5 frames) is tuned for keyboard, where rapid direction taps are common. Gamepad D-pad presses tend to be shorter.
**How to avoid:** Test with actual gamepad. The 5-frame threshold should be fine since walking requires holding direction for > 5 frames, but verify.
**Warning signs:** Slime repositioning when player just wants to turn around.

### Pitfall 5: Goo-Mold Removal Breaking IntGrid Loading
**What goes wrong:** Removing `10: TILE_GOO_MOLD` from `val_to_tile` in `load_from_ldtk_simplified()` could cause issues if any existing level CSV has value 10.
**Why it happens:** The loading code silently skips unknown IntGrid values (they just don't get added to collision_data), so this is actually safe. But the mapping line should be removed, not left dangling.
**How to avoid:** D-07 confirms no maps use Goo-Mold. Grep the assets directory for IntGrid CSVs containing value 10 to double-check.
**Warning signs:** None expected -- failure would be silent (tile becomes empty).

### Pitfall 6: Ram Screen Shake Already Exists
**What goes wrong:** Ram already triggers `on_block_break()` which sets `shake_timer` when breaking CRACKED_H. Adding a separate shake for Ram "impact" (D-10) could double-shake.
**Why it happens:** `on_block_break()` sets shake_timer for ALL block breaks, not just drill.
**How to avoid:** The D-10 "ram impact" shake should be specifically for Ram hitting a solid (non-breakable) wall, not for block breaking. The block-break shake already handles the destructible case.
**Warning signs:** Excessive screen shake during Ram.

## Code Examples

### Goo-Mold Removal Checklist
```python
# 1. constants.py -- DELETE this line:
TILE_GOO_MOLD = (6, 1)  # IntGrid value 10: Negative Space (Goo-Mold)

# 2. map.py -- REMOVE from imports:
#    TILE_GOO_MOLD from the import list

# 3. map.py -- REMOVE from is_solid():
#    TILE_GOO_MOLD from the tuple

# 4. map.py -- REMOVE from is_destructible():
#    TILE_GOO_MOLD from the tuple

# 5. map.py -- DELETE entire method:
#    def is_goo_mold(self, tx, ty)

# 6. map.py -- REMOVE from val_to_tile dict in load_from_ldtk_simplified():
#    10: TILE_GOO_MOLD,

# 7. entity-schema.json -- REMOVE IntGrid value "10" entry entirely
#    (or replace with a placeholder "10": { "name": "reserved", ... })
```

### Drill Dive CRACKED_V Cost Constant
```python
# In constants.py -- new constant for drill breaking a gate block
DRILL_CRACKED_V_COST = 20.0  # Juice cost per CRACKED_V block broken via Drill Dive (same as DRILL_IMPACT_COST)
```

### Boost CRACKED_V Cost Constant
```python
# In constants.py -- new constant for boost breaking a gate block
BOOST_CRACKED_V_COST = 25.0  # Juice cost per CRACKED_V block broken via Boost (same as BOOST_JUICE_COST)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hardcoded `TILE_DESTRUCTIBLE` in on_block_destroyed | Must pass actual tile type | Phase 10 | Correct regen tracking for CRACKED_V |
| No ceiling block breaking | BOOSTING state checks CRACKED_V on dy < 0 collision | Phase 10 | Enables upward vertical traversal gates |
| Keyboard-only input | Keyboard + Gamepad via _ACTION_MAP | Phase 10 | Zero code changes outside input.py |

## Open Questions

1. **CRACKED_V juice cost values**
   - What we know: Drill costs 20 for impact (DRILL_IMPACT_COST), Ram costs 15 per CRACKED_H (RAM_BLOCK_COST), Boost costs 25 per tap (BOOST_JUICE_COST)
   - What's unclear: Should CRACKED_V breaking cost a flat amount, or reuse existing ability costs?
   - Recommendation: Use DRILL_IMPACT_COST (20) for drill breaking CRACKED_V, and BOOST_JUICE_COST (25) for boost breaking CRACKED_V. Gate blocks are expensive.

2. **Boost trail VFX implementation**
   - What we know: Existing Particle class supports colored pixels with gravity and random spread
   - What's unclear: Whether to spawn particles on every frame of boost, or only on tap
   - Recommendation: Spawn 2-3 particles on each boost tap (start_boost + chain tap). Simpler, less noisy.

3. **Ability tuning scope**
   - What we know: D-08/D-09 say "full tuning pass" across 6 abilities
   - What's unclear: How much tuning is needed vs. how much works well already
   - Recommendation: Start with gamepad testing. Log specific issues. Fix only confirmed problems. Avoid preemptive constant changes.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | none (uses defaults) |
| Quick run command | `python -m pytest tests/ -x -q` |
| Full suite command | `python -m pytest tests/ -q` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ABL-02a | Drill Dive breaks CRACKED_V downward | unit | `python -m pytest tests/test_cracked_v.py::test_drill_breaks_cracked_v -x` | No -- Wave 0 |
| ABL-02b | Boost breaks CRACKED_V upward | unit | `python -m pytest tests/test_cracked_v.py::test_boost_breaks_cracked_v -x` | No -- Wave 0 |
| ABL-02c | CRACKED_V costs juice (no refund) | unit | `python -m pytest tests/test_cracked_v.py::test_cracked_v_costs_juice -x` | No -- Wave 0 |
| D-05 | Gamepad buttons map to actions | unit | `python -m pytest tests/test_gamepad.py -x` | No -- Wave 0 |
| D-06 | Goo-Mold removed from collision | unit | `python -m pytest tests/test_goo_mold_removal.py -x` | No -- Wave 0 |
| VFX | VFX triggers on ability use | manual-only | Visual inspection during gameplay | N/A |
| TUNE | Ability feel with gamepad | manual-only | Playtest with controller | N/A |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/ -x -q`
- **Per wave merge:** `python -m pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_cracked_v.py` -- covers ABL-02a, ABL-02b, ABL-02c (drill + boost breaking, juice cost)
- [ ] `tests/test_gamepad.py` -- covers D-05 (gamepad constants in _ACTION_MAP)
- [ ] `tests/test_goo_mold_removal.py` -- covers D-06 (TILE_GOO_MOLD no longer in collision sets)

## Sources

### Primary (HIGH confidence)
- Runtime inspection of `pyxel` module (v2.8.7) -- verified all GAMEPAD1_BUTTON_* and GAMEPAD1_BUTTON_DPAD_* constants exist
- `src/core/input.py` -- verified _ACTION_MAP pattern, btn/btnp/btnr wrappers
- `src/entities/player.py` -- verified DIVING collision (line 664-677), BOOSTING update (line 484-505), ceiling collision (line 692-695)
- `src/level/map.py` -- verified is_destructible includes CRACKED_V, get_cracked_h_at pattern, is_cracked_vertical exists
- `src/entities/effects.py` -- verified Particle and Effect classes

### Secondary (MEDIUM confidence)
- Pyxel gamepad API behavior (btn/btnp/btnr work identically for keyboard and gamepad constants) -- based on Pyxel design and verified constant names

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new dependencies, all Pyxel built-in
- Architecture: HIGH -- extending proven patterns (get_cracked_h_at, _ACTION_MAP, Particle)
- Pitfalls: HIGH -- identified from direct code reading, not speculation

**Research date:** 2026-03-28
**Valid until:** 2026-04-28 (stable -- no external dependencies changing)
