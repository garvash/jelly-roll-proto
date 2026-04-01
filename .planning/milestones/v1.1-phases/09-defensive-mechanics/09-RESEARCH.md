# Phase 09: Defensive Mechanics - Research

**Researched:** 2026-03-28
**Domain:** Pyxel game abilities (hazard zones, vertical boost, input remap, charge recoil)
**Confidence:** HIGH

## Summary

Phase 9 adds two new slime-powered abilities (Bubble Shield and Slime Boost), three new hazard zone tile types (water/acid/lava), an input remap for axis consistency (Drill Dive moves from DOWN+V to DOWN+SPACE), charge shot recoil physics, and new item pickups. ABL-07 (Reform Block) is removed from scope per D-21.

The codebase is well-structured for extension. All new abilities follow the established `has_X` boolean + item pickup pattern from Phase 8. Hazard zones require expanding the existing `check_hazard()` system from instant-damage spikes to continuous-drain zone types. The input remap is a surgical change in `handle_input()` only (no new actions needed in `_ACTION_MAP`). Slime Boost introduces a new "BOOSTING" player state with per-tap committed bursts and a re-commit window.

**Primary recommendation:** Implement in 4 waves: (1) hazard zone tile infrastructure + input remap, (2) Bubble Shield ability with tier system, (3) Slime Boost ability, (4) charge shot recoil + cleanup.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- D-01: Bubble Shield auto-activates on hazard zone entry at 100% juice (NOT button-press)
- D-02: Shield = fused state; mana shield also applies while shielded
- D-03: Juice drains at hazard-type-specific rates (water=slow, acid=medium, lava=fast)
- D-04: Juice empty in hazard zone = rapid HP drain
- D-05: Tiered progression (T1 = base drain, T2 = reduced drain; slow-drain becomes free)
- D-06: Visual = translucent circle outline, color shifts per tier (blue=T1, green=T2)
- D-07: Slime Boost = fused-only, airborne, SPACE tap for upward burst
- D-08: Multi-tap chaining with re-commit window between taps
- D-09: Exit conditions: stop pressing = normal unfuse; juice empty = dissipate + burnout
- D-10: Boost damages enemies below player on each tap
- D-11: Unlocked via BOOST_PICKUP item
- D-12: Drill Dive remap from DOWN+V to DOWN+SPACE
- D-13: Full input map: SPACE=vertical (jump/boost/drill), V=horizontal (dash/ram), Z=spit/recall/charge
- D-14: New tile constants TILE_WATER, TILE_ACID, TILE_LAVA with distinct drain rates
- D-15: Minimal pixel art for hazard tiles (simple 8x8 tiles)
- D-16: Existing TILE_HAZARD (spikes) unchanged
- D-17: Charge shot recoil = physics-based emergent vertical momentum (bomb-climb exploit)
- D-18: Real gating uses doors/locks, not ability checks
- D-19: Slime Ram fully committed, no cancel
- D-20: Fused ability commitment spectrum defined
- D-21: ABL-07 Reform Block removed from scope

### Claude's Discretion
- Specific juice drain rates per hazard tier (exact numbers)
- Slime Boost juice cost per tap
- Charge shot recoil force magnitude
- Shield circle VFX animation details (pulse frequency, flicker pattern)
- Re-commit window duration between Slime Boost taps

### Deferred Ideas (OUT OF SCOPE)
- ABL-07 Reform Block (already covered by Phase 7 block regeneration)
- Juice capacity upgrades (SYS-04) -- Phase 11
- Additional hazard biomes beyond water/acid/lava
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ABL-05 | Bubble Shield (Consumes juice on hit) | Hazard zone tile infrastructure, auto-fuse on zone entry, passive juice drain system, tiered progression with item pickups, shield VFX via Pyxel circb |
| ABL-06 | Yoshi-style Double Jump | Slime Boost: fused airborne SPACE tap, multi-tap chain with re-commit window, enemy damage below, BOOST_PICKUP item |
| ABL-07 | Reform Block | REMOVED per D-21 -- existing block regeneration from Phase 7 covers this |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pyxel | 2.8.7 | Game engine | Already installed, project engine |
| Python | 3.13 | Runtime | Already installed via .venv |
| pytest | 9.0.2 | Testing | Already installed, test infrastructure exists |

No new dependencies needed. All features are implemented using existing Pyxel primitives.

### Pyxel Drawing API (for Shield VFX)
| Function | Signature | Purpose |
|----------|-----------|---------|
| `pyxel.circb(x, y, r, col)` | Circle outline | Shield bubble outline |
| `pyxel.circ(x, y, r, col)` | Filled circle | Not needed (outline only per D-06) |
| `pyxel.frame_count` | Frame counter | Pulse/flicker animation timing |

## Architecture Patterns

### Recommended Changes by File

```
src/
  core/
    constants.py      # New: TILE_WATER/ACID/LAVA, drain rates, boost costs, recoil force
    input.py           # No changes needed (_ACTION_MAP already has SPACE and V)
  entities/
    player.py          # Remap drill dive trigger, add BOOSTING state, shield logic,
                       #   charge recoil, has_shield/has_boost/has_shield_t2 flags
    slime.py           # No structural changes (consume/refill/dissipate reused as-is)
    items.py           # New item types: SHIELD_PICKUP, BOOST_PICKUP, SHIELD_T2
  level/
    map.py             # New hazard zone check methods, zone tile type identification
main.py                # Spawn new pickups, shield VFX draw, boost enemy damage check
assets/
  entity-schema.json   # New entity definitions for pickups, new IntGrid values 6-8
```

### Pattern 1: Hazard Zone Tile System
**What:** Expand the existing binary hazard check into a typed zone system. Current `check_hazard()` returns bool (is spike?). New system needs to return the hazard TYPE so drain rate can be looked up.
**When to use:** Every frame during player update to determine if passive juice drain applies.
**Example:**
```python
# constants.py -- New hazard zone tiles (IntGrid values 6, 7, 8)
TILE_WATER = (6, 1)   # IntGrid value 6
TILE_ACID  = (7, 1)   # IntGrid value 7
TILE_LAVA  = (8, 1)   # IntGrid value 8

# Drain rates per frame (at 60fps)
HAZARD_DRAIN_SLOW   = 0.5   # Water T1: ~6.7 seconds to drain 200 juice
HAZARD_DRAIN_MEDIUM = 1.5   # Acid T1: ~2.2 seconds
HAZARD_DRAIN_FAST   = 3.0   # Lava T1: ~1.1 seconds

# Tier 2 reduction (flat subtraction from drain rate)
SHIELD_T2_DRAIN_REDUCTION = 0.5  # Slow becomes 0 (free), medium becomes slow, fast becomes medium

# Hazard type -> drain rate mapping
HAZARD_DRAIN_RATES = {
    TILE_WATER: HAZARD_DRAIN_SLOW,
    TILE_ACID:  HAZARD_DRAIN_MEDIUM,
    TILE_LAVA:  HAZARD_DRAIN_FAST,
}

# HP drain when juice empty in hazard zone
HAZARD_HP_DRAIN_INTERVAL = 30  # Frames between HP ticks when juice empty (0.5s)
```

```python
# map.py -- New zone hazard detection
def get_zone_hazard_type(self, x, y, width, height):
    """Returns the zone hazard tile type overlapping the AABB, or None.
    Checks for TILE_WATER, TILE_ACID, TILE_LAVA (NOT TILE_HAZARD spikes)."""
    x1 = int(x // TILE_SIZE)
    y1 = int(y // TILE_SIZE)
    x2 = int((x + width - 1) // TILE_SIZE)
    y2 = int((y + height - 1) // TILE_SIZE)
    worst = None
    for ty in range(y1, y2 + 1):
        for tx in range(x1, x2 + 1):
            tile = self.collision_data.get((tx, ty))
            if tile in HAZARD_DRAIN_RATES:
                # Return worst (highest drain) hazard if overlapping multiple
                if worst is None or HAZARD_DRAIN_RATES[tile] > HAZARD_DRAIN_RATES.get(worst, 0):
                    worst = tile
    return worst
```

### Pattern 2: Auto-Fuse Shield Activation (D-01, D-02)
**What:** When player enters a hazard zone with 100% juice and has_shield, auto-fuse and begin passive drain. Shield = fused state, so mana shield (D-04 from Phase 8) also applies.
**When to use:** In `player.update()`, checked every frame.
**Example:**
```python
# In Player.update(), after movement but before state update:
def update_shield(self, slime):
    zone_type = self.level_map.get_zone_hazard_type(self.x, self.y, self.w, self.h)

    if zone_type and self.has_shield and not self.is_fused:
        # Auto-fuse if at full juice (D-01)
        if slime.juice >= slime.max_juice:
            self.fuse(slime)
            self.shield_active = True

    if self.shield_active and self.is_fused:
        if zone_type:
            # Drain juice based on hazard type (D-03)
            drain = HAZARD_DRAIN_RATES.get(zone_type, HAZARD_DRAIN_SLOW)
            if self.has_shield_t2:
                drain = max(0, drain - SHIELD_T2_DRAIN_REDUCTION)
            slime.consume(drain)

            if slime.juice <= 0:
                # Juice empty: unfuse, start HP drain (D-04)
                self.unfuse(slime, dissipate=True)
                self.shield_active = False
                self.hazard_hp_timer = HAZARD_HP_DRAIN_INTERVAL
        else:
            # Left hazard zone: deactivate shield, unfuse
            self.shield_active = False
            self.unfuse(slime)
```

### Pattern 3: Slime Boost State Machine (D-07, D-08)
**What:** New "BOOSTING" player state for fused airborne vertical bursts. Each SPACE tap is one committed burst. Re-commit window between taps allows chaining.
**When to use:** When fused + airborne + has_boost + SPACE pressed.
**Example:**
```python
# constants.py
BOOST_FORCE = -3.5          # Upward burst force (similar to JUMP_FORCE)
BOOST_JUICE_COST = 25.0     # Juice per tap
BOOST_RECOMMIT_WINDOW = 12  # Frames to chain next boost (~0.2s)
BOOST_DOWNWARD_DAMAGE_W = 12  # Hitbox width for enemy damage below
BOOST_DOWNWARD_DAMAGE_H = 8   # Hitbox height for enemy damage below

# Player state: "BOOSTING"
# - Each SPACE tap: committed upward burst, costs juice
# - Between taps: recommit_timer counts down
# - If timer expires without tap: exit boost (drop slime, unfuse)
# - If juice empties: dissipate + burnout (D-09)
```

### Pattern 4: Input Remap (D-12)
**What:** Move Drill Dive trigger from DOWN+V (dash button) to DOWN+SPACE (jump button). The `_ACTION_MAP` does NOT need changes -- the trigger logic in `handle_input()` changes.
**Current code (line ~283-293 of player.py):**
```python
# CURRENT: Drill dive is under "dash" button (V) + down
if input_manager.btnp("dash") and self.state not in ("DIVING", "DASHING", "RAMMING"):
    if input_manager.btn("down") and self.has_drill and not self.is_grounded and slime.juice > 0:
        # DOWN+V = Drill Dive
```
**New:** Move drill dive check to the jump button section:
```python
# NEW: Drill dive is under "jump" button (SPACE) + down
if input_manager.btnp("jump"):
    if input_manager.btn("down") and self.has_drill and not self.is_grounded and slime.juice > 0:
        # DOWN+SPACE = Drill Dive (D-12 remap)
        ...
    elif self.is_fused and not self.is_grounded and self.has_boost:
        # SPACE while fused+airborne = Slime Boost (D-07)
        ...
    else:
        # Normal jump (existing logic)
        self.jump_buffer_timer = JUMP_BUFFER
```

### Pattern 5: Charge Shot Recoil (D-17)
**What:** When charge shot fires, apply upward impulse to player. Physics-based exploit, not gated.
**Example:**
```python
# constants.py
CHARGE_RECOIL_FORCE = -2.5  # Upward impulse on charge shot fire

# In player.fire_charge_shot():
# After spawning projectile, apply recoil
self.dy = CHARGE_RECOIL_FORCE  # Emergent vertical boost
```

### Anti-Patterns to Avoid
- **Modifying `_ACTION_MAP` for the remap:** No new actions are needed. The remap is purely about which trigger condition checks which button. SPACE and V actions already exist.
- **Adding shield as a separate state from fused:** Shield IS fused state (D-02). Don't create a separate "SHIELDED" state -- use `shield_active` boolean alongside `is_fused`.
- **Making zone hazards use `check_hazard()`:** The existing `check_hazard()` handles instant-damage spikes with teleport-to-spawn. Zone hazards are fundamentally different (continuous drain). Keep them separate.
- **Setting `is_fused = True` directly:** Always use `player.fuse(slime)` / `player.unfuse(slime)` (Pitfall 3 from STATE.md).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Circle VFX | Custom pixel-by-pixel circle | `pyxel.circb(x, y, r, col)` | Built-in, anti-aliased at pixel level |
| Pulse animation | Complex sine wave system | `pyxel.frame_count % period` modulo check | Simple, deterministic, no state needed |
| Hazard type lookup | If/elif chains in player code | Dictionary mapping `HAZARD_DRAIN_RATES[tile_type]` | Clean, extensible, no code changes for new types |
| Item unlock persistence | Custom save for has_shield | Extend existing `world.collect_item(iid)` pattern | Already handles permanent item persistence |

## Common Pitfalls

### Pitfall 1: Drill Dive Remap Breaking Existing Jump
**What goes wrong:** Moving drill dive check to the SPACE button can eat normal jump inputs if the priority order is wrong.
**Why it happens:** `btnp("jump")` fires for all SPACE presses. If drill dive check runs first and consumes the input, jumps stop working on the ground.
**How to avoid:** Check conditions strictly: drill dive requires `not is_grounded AND btn("down") AND has_drill AND juice > 0`. Ground jumps only fire when `is_grounded` or `coyote_timer > 0`. Separate the code paths clearly.
**Warning signs:** Player cannot jump normally after the remap.

### Pitfall 2: Shield Auto-Fuse Loop
**What goes wrong:** Player enters hazard zone, auto-fuses, juice drains, unfuses, juice regens back to full, auto-fuses again -- rapid fuse/unfuse flickering.
**Why it happens:** Auto-fuse triggers at 100% juice. If player stands at the edge of a hazard zone, juice regens to full while unfused, triggering re-fuse.
**How to avoid:** Add a cooldown after shield deactivation before it can re-activate. Or: only auto-fuse on initial zone entry (track `was_in_hazard_zone` boolean).
**Warning signs:** Flickering visual, rapid fuse/unfuse sounds.

### Pitfall 3: Boost Conflicting with Jump Buffer
**What goes wrong:** Jump buffer timer causes unintended ground jumps after boost ends, or boost triggers from buffered jump inputs.
**Why it happens:** `jump_buffer_timer` stores recent SPACE presses. If boost ends near the ground, the buffer fires a jump.
**How to avoid:** Clear `jump_buffer_timer` when entering/exiting boost state. Don't set buffer during boost.
**Warning signs:** Unexpected jumps after boost ends.

### Pitfall 4: Zone Hazard Tiles Treated as Solid
**What goes wrong:** Zone hazard tiles (water/acid/lava) block player movement like walls.
**Why it happens:** `is_solid()` checks all collision_data entries. If zone tiles are added to collision_data without excluding them from solid checks, they become walls.
**How to avoid:** Zone hazard tiles should NOT be in `is_solid()`. They are purely "overlay" tiles -- player passes through them freely, they just trigger drain. Either (a) store them in collision_data but exclude from `is_solid()`, or (b) store them in a separate data structure.
**Warning signs:** Player cannot walk into water/acid/lava areas.

### Pitfall 5: Entity Schema Divergence
**What goes wrong:** New pickup entities added to game code but not to `entity-schema.json`, breaking the pml-to-ldtk converter.
**Why it happens:** Forgetting to update the shared contract when adding ShieldPickup, BoostPickup, ShieldT2 entities.
**How to avoid:** Update entity-schema.json in the same task that adds new entity types. Add IntGrid values 6-8 for zone hazard tiles.
**Warning signs:** Converter errors when processing maps with new entities.

## Code Examples

### New Constants Block
```python
# src/core/constants.py additions

# Zone Hazard Tiles (IntGrid values 6, 7, 8)
TILE_WATER = (6, 1)
TILE_ACID  = (7, 1)
TILE_LAVA  = (8, 1)

# Zone Hazard Drain Rates (juice per frame, 60fps)
HAZARD_DRAIN_SLOW   = 0.5   # Water: ~6.7s full-to-empty
HAZARD_DRAIN_MEDIUM = 1.5   # Acid: ~2.2s full-to-empty
HAZARD_DRAIN_FAST   = 3.0   # Lava: ~1.1s full-to-empty

HAZARD_DRAIN_RATES = {
    TILE_WATER: HAZARD_DRAIN_SLOW,
    TILE_ACID:  HAZARD_DRAIN_MEDIUM,
    TILE_LAVA:  HAZARD_DRAIN_FAST,
}

# Shield Tier 2 drain reduction
SHIELD_T2_DRAIN_REDUCTION = 0.5  # Flat subtraction: slow becomes free, medium becomes slow

# HP drain when shieldless in hazard zone
HAZARD_HP_DRAIN_INTERVAL = 30  # Frames between HP ticks (0.5s)

# Slime Boost (ABL-06, D-07)
BOOST_FORCE = -3.5           # Upward impulse per tap
BOOST_JUICE_COST = 25.0      # Juice per tap (~8 boosts from full)
BOOST_RECOMMIT_WINDOW = 12   # Frames between taps (~0.2s)

# Charge Shot Recoil (D-17)
CHARGE_RECOIL_FORCE = -2.5   # Upward impulse on charge shot fire
```

### Item Pickup Extension
```python
# items.py collect() additions
def collect(self, player, slime):
    if self.item_type == "SHIELD_PICKUP":
        player.has_shield = True
    elif self.item_type == "BOOST_PICKUP":
        player.has_boost = True
    elif self.item_type == "SHIELD_T2":
        player.has_shield_t2 = True
    # ... existing types ...
    self.is_active = False
```

### Shield VFX Drawing
```python
# In player.draw() or a separate draw_shield() method:
def draw_shield(self):
    if not self.shield_active:
        return
    cx = self.x + self.w // 2
    cy = self.y + self.h // 2
    radius = 6  # Slightly larger than 8x8 player sprite
    # Color per tier: blue (T1=12) or green (T2=11)
    color = 11 if self.has_shield_t2 else 12
    # Pulse: alternate radius by 1 pixel every ~10 frames
    if (pyxel.frame_count // 10) % 2 == 0:
        radius += 1
    # Flicker: skip drawing every ~40 frames for 2 frames
    if pyxel.frame_count % 40 < 2:
        return
    pyxel.circb(cx, cy, radius, color)
```

### IntGrid Mapping Extension
```python
# map.py -- val_to_tile additions in load_from_ldtk_simplified()
val_to_tile = {
    1: TILE_SOLID,
    2: TILE_HAZARD,
    3: TILE_DESTRUCTIBLE,
    4: TILE_GATE,
    5: TILE_SWITCH,
    6: TILE_WATER,      # NEW
    7: TILE_ACID,       # NEW
    8: TILE_LAVA,       # NEW
    10: TILE_GOO_MOLD,
    11: TILE_CRACKED_H,
    12: TILE_CRACKED_V
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| DOWN+V = Drill Dive | DOWN+SPACE = Drill Dive | Phase 9 (D-12) | V is now purely horizontal |
| Binary hazard (spike = instant damage) | Zone hazards (water/acid/lava = continuous drain) | Phase 9 (D-14) | New tile types, new drain system |
| No shield ability | Bubble Shield (auto-fuse on zone entry) | Phase 9 (ABL-05) | Hazard traversal progression |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | none (uses default discovery) |
| Quick run command | `python -m pytest tests/ -x --tb=short` |
| Full suite command | `python -m pytest tests/ -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ABL-05-a | Shield auto-fuse on zone entry at 100% juice | unit | `python -m pytest tests/test_shield.py::test_auto_fuse_on_zone_entry -x` | Wave 0 |
| ABL-05-b | Juice drains at hazard-type-specific rate | unit | `python -m pytest tests/test_shield.py::test_drain_rates -x` | Wave 0 |
| ABL-05-c | T2 reduces drain, slow becomes free | unit | `python -m pytest tests/test_shield.py::test_tier2_reduction -x` | Wave 0 |
| ABL-05-d | HP drain when juice empty in zone | unit | `python -m pytest tests/test_shield.py::test_hp_drain_no_juice -x` | Wave 0 |
| ABL-06-a | Boost triggers fused+airborne+SPACE | unit | `python -m pytest tests/test_boost.py::test_boost_trigger -x` | Wave 0 |
| ABL-06-b | Multi-tap chaining within recommit window | unit | `python -m pytest tests/test_boost.py::test_chain_boosts -x` | Wave 0 |
| ABL-06-c | Boost exit: stop pressing = unfuse | unit | `python -m pytest tests/test_boost.py::test_boost_exit_unfuse -x` | Wave 0 |
| ABL-06-d | Boost exit: juice empty = dissipate | unit | `python -m pytest tests/test_boost.py::test_boost_exit_dissipate -x` | Wave 0 |
| ABL-06-e | Boost damages enemies below | unit | `python -m pytest tests/test_boost.py::test_boost_damages_enemies -x` | Wave 0 |
| REMAP | Drill dive on DOWN+SPACE, not DOWN+V | unit | `python -m pytest tests/test_input_remap.py -x` | Wave 0 |
| RECOIL | Charge shot applies upward impulse | unit | `python -m pytest tests/test_charge_recoil.py -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/ -x --tb=short`
- **Per wave merge:** `python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_shield.py` -- covers ABL-05 (auto-fuse, drain rates, tier 2, HP drain)
- [ ] `tests/test_boost.py` -- covers ABL-06 (trigger, chaining, exit conditions, enemy damage)
- [ ] `tests/test_input_remap.py` -- covers D-12 (drill dive on SPACE, boost on SPACE, V unchanged)
- [ ] `tests/test_charge_recoil.py` -- covers D-17 (recoil force applied on charge shot)

## Sources

### Primary (HIGH confidence)
- Direct codebase analysis of `src/entities/player.py`, `src/entities/slime.py`, `src/core/constants.py`, `src/core/input.py`, `src/level/map.py`, `src/entities/items.py`, `main.py`
- Pyxel 2.8.7 API verified via `pip show pyxel` and `dir(pyxel)` for drawing primitives
- `assets/entity-schema.json` for IntGrid value mapping and entity contract
- `.planning/phases/09-defensive-mechanics/09-CONTEXT.md` for all design decisions

### Secondary (MEDIUM confidence)
- Drain rate numbers are Claude's discretion (tuning values). Chosen based on: 200 juice max, 60fps, targeting 1-7 second drain windows for gameplay feel. Easily adjustable constants.
- Boost cost (25/tap = ~8 boosts from full) chosen for meaningful resource tension. Adjustable.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new dependencies, all Pyxel built-ins verified
- Architecture: HIGH -- extends well-established patterns (has_X booleans, consume/refill, state machine, tile system)
- Pitfalls: HIGH -- identified from direct code analysis of existing collision/hazard/fuse systems
- Tuning values (drain rates, boost cost, recoil force): MEDIUM -- reasonable defaults, need playtesting

**Research date:** 2026-03-28
**Valid until:** 2026-04-28 (stable codebase, no external dependency drift)
