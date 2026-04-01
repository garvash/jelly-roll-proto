# Phase 8: New Fusion Abilities - Research

**Researched:** 2026-03-28
**Domain:** Pyxel game mechanics -- state machine expansion, input abstraction, ability system, resource-gated combat
**Confidence:** HIGH

## Summary

Phase 8 transforms the existing player-slime relationship from a simple drill-dive fusion into a full charge-to-fuse ability system with three new abilities (Slime Ram, Directional Slime Hold, Charge Shot), a basic dash, input remapping, and several retcons (drill activation key, kick removal, DRILL item removal). The codebase is well-structured for this: `Player.handle_input()` is the single entry point for all controls, `Slime` already has `is_fused`, `consume()`, `refill()`, and `reform()` methods, and the `constants.py` file follows a clear UPPER_SNAKE_CASE pattern for all tuning values.

The primary technical challenge is the input abstraction layer. Currently, all input reads `pyxel.btn()`/`pyxel.btnp()`/`pyxel.btnr()` directly with hardcoded key constants scattered across `player.py`. Adding WASD+JK secondary mapping requires an input wrapper that maps logical actions to multiple physical keys. The secondary challenge is the state machine expansion: the player currently has 6 states (IDLE, RUNNING, JUMPING, FALLING, DIVING, WALL_SLIDING) and needs at least 2 more (DASHING, RAMMING), plus the fusion system adds a pre-fusion charging phase and post-fusion enhanced state that modifies behavior of existing inputs.

The existing Drill Dive implementation in `move_and_collide()` (lines 347-371) provides the exact pattern for Slime Ram's block-breaking: detect specific tile type, call `on_block_destroyed()`, remove tile, spawn explosion, refill juice. The key difference is Ram moves horizontally while Drill moves vertically, and Ram checks for `TILE_CRACKED_H` specifically while Drill checks generic destructibles.

**Primary recommendation:** Build an input abstraction module first (`src/core/input.py`), then layer abilities on top. Structure the fusion system as a state modifier on the existing player state machine rather than a parallel state machine.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- D-01: Fusion is NOT a toggle. Charge juice to 100% (JUICE_MAX), hold Z to recall slime and fuse.
- D-02: Hold Z = slime zips to player (~4-6 frames rubber-band recall) + charge builds visually. Auto-fuse when slime arrives and juice is at 100%.
- D-03: While fused, all abilities are enhanced. Each fused ability ends fusion on use.
- D-04: Mana shield while fused: juice absorbs ALL damage instead of HP. Hits cost ~20 juice.
- D-05: Juice empty while fused = slime dissipates. Cooldown before slime reforms at full size.
- D-06: Z = tap to spit (unfused) | hold to recall + charge (unfused) | release to fire charge shot (fused).
- D-07: V = basic dash (unfused) | Slime Ram (fused). DOWN+V = Drill Dive (unfused+fused).
- D-08: SPACE = jump only. Arrows = movement.
- D-09: Secondary input mapping: WASD mirrors arrows, J mirrors Z, K mirrors V, SPACE shared.
- D-10: Kick mechanic retired entirely. Switch-flipping via spit or ram.
- D-11: X button freed up, reserved for Phase 9.
- D-12: Slime Ram = Shinespark/Crystal Dash style. High speed, invincible, directional. Breaks CRACKED_H.
- D-13: Juice-powered penetration: each CRACKED_H block costs ~15 juice. More juice = deeper penetration.
- D-14: Ram ending: juice empty during ram = stop, unfuse, slime dissipates.
- D-15: Basic Dash = short combat dodge (~2 tiles). ~8 frames i-frames. ~20 frame cooldown. Air-usable once.
- D-16: Charge Shot = all-or-nothing max power. Dumps all remaining juice. Slime IS the projectile.
- D-17: Auto-unfuse on fire. Slime lands at hit destination, resumes solo mode.
- D-18: No charge levels -- every charge shot is the same big payoff.
- D-19: Directional Slime Hold: quick tap LEFT/RIGHT (~4-6 frames) = reposition slime. Hold = normal walk.
- D-20: Slime moves to take cover in tapped direction -- finds next available tile.
- D-21: Slime acts as detached turret while unfused (R-Type Force pod).
- D-22: Drill Dive moves from DOWN+SPACE to DOWN+V.
- D-23: DRILL item pickup removed. Drill Dive earned from defeating Mole Boss.
- D-24: Progression: Start (walk/jump/spit) -> Early (find dash, V unlocked) -> Mole Boss (drill dive, DOWN+V) -> Juice 100% (fuse).
- D-25: Hold Z (unfused) = slime zips to player at high speed (~4-6 frames). Rubber-band arc/trail.
- D-26: Slime must reach and overlap player before fusion triggers.

### Claude's Discretion
None specified -- all major decisions are locked.

### Deferred Ideas (OUT OF SCOPE)
- Phase 9 (Defensive Mechanics): X button for Bubble Shield (ABL-05), Yoshi Double Jump (ABL-06), Reform Block (ABL-07).
- Juice capacity upgrades: Max juice increases for deeper CRACKED_H walls. Fits SYS-04 in Phase 11.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ABL-01 | Slime Ram fusion (Forward Dash) with horizontal gating capability | D-12 through D-14 define Ram as Shinespark-style, juice-powered penetration through CRACKED_H. Existing `move_and_collide()` drill pattern is directly reusable for horizontal block-breaking. `LevelMap.is_cracked_horizontal()` already exists. |
| ABL-03 | Directional Slime Hold (Tap left/right to position and freeze slime) | D-19 through D-21 define tap-vs-hold input threshold. Requires input duration tracking in the input abstraction layer. Slime positioning logic extends existing `Slime.reform()` pattern with directional tile-finding. |
| ABL-04 | Charge Slime Shot (Hold button to increase power/size) | D-16 through D-18 simplify this to all-or-nothing (no charge levels). Existing `Slime.spit()` and `Projectile` class provide base pattern. Charge shot creates a special projectile where slime IS the projectile -- slime teleports to impact point. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pyxel | 2.8.7 | Game engine | Already installed and in use. All rendering, input, audio. |
| Python | 3.13.11 | Runtime | Already installed in .venv |

### Supporting
No additional libraries needed. This phase is pure game logic built on Pyxel's existing API.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom input wrapper | Direct pyxel.btn() calls with OR conditions | Wrapper is cleaner and avoids duplicating OR logic at every input check site |

**Version verification:** Pyxel 2.8.7 confirmed installed via `pip show pyxel`. Python 3.13.11 confirmed via `python --version`.

## Architecture Patterns

### Recommended Project Structure
```
src/
  core/
    constants.py       # All new ability constants (DASH_*, RAM_*, CHARGE_*, FUSION_*, RECALL_*)
    input.py           # NEW: Input abstraction layer (logical actions -> physical keys)
  entities/
    player.py          # Expand state machine, refactor handle_input(), add fusion logic
    slime.py           # Add recall(), charge_shot_launch(), hold_position(), dissipate/reform cooldown
    projectile.py      # Add ChargeProjectile subclass or mode flag for charge shot behavior
    items.py           # Remove DRILL item type, add DASH pickup type
  level/
    map.py             # Add get_cracked_h_at() for ram-specific block detection (horizontal scan)
    world.py           # No changes expected
```

### Pattern 1: Input Abstraction Layer
**What:** A module that maps logical game actions to one or more physical keys, replacing all direct `pyxel.btn()`/`pyxel.btnp()`/`pyxel.btnr()` calls in player.py.
**When to use:** Every input check in the game.
**Example:**
```python
# src/core/input.py
import pyxel

# Logical action -> list of physical keys
_ACTION_MAP = {
    "left":   [pyxel.KEY_LEFT, pyxel.KEY_A],
    "right":  [pyxel.KEY_RIGHT, pyxel.KEY_D],
    "up":     [pyxel.KEY_UP, pyxel.KEY_W],
    "down":   [pyxel.KEY_DOWN, pyxel.KEY_S],
    "jump":   [pyxel.KEY_SPACE],
    "spit":   [pyxel.KEY_Z, pyxel.KEY_J],   # Z primary, J secondary
    "dash":   [pyxel.KEY_V, pyxel.KEY_K],   # V primary, K secondary
}

def btn(action):
    """Returns True if any mapped key for the action is held."""
    return any(pyxel.btn(k) for k in _ACTION_MAP[action])

def btnp(action, hold=None, repeat=None):
    """Returns True if any mapped key for the action was pressed this frame."""
    kwargs = {}
    if hold is not None:
        kwargs["hold"] = hold
    if repeat is not None:
        kwargs["repeat"] = repeat
    return any(pyxel.btnp(k, **kwargs) for k in _ACTION_MAP[action])

def btnr(action):
    """Returns True if any mapped key for the action was released this frame."""
    return any(pyxel.btnr(k) for k in _ACTION_MAP[action])

# Hold duration tracking for tap-vs-hold detection (D-19)
_hold_frames = {}

def update():
    """Call once per frame to update hold duration tracking."""
    for action, keys in _ACTION_MAP.items():
        if any(pyxel.btn(k) for k in keys):
            _hold_frames[action] = _hold_frames.get(action, 0) + 1
        else:
            _hold_frames[action] = 0

def hold_frames(action):
    """Returns how many consecutive frames the action has been held."""
    return _hold_frames.get(action, 0)

def was_tap(action, threshold):
    """Returns True if action was just released after being held for <= threshold frames."""
    if any(pyxel.btnr(k) for k in _ACTION_MAP[action]):
        # Check previous hold duration (it was reset to 0 this frame by update())
        # Need to track previous value -- use a _prev_hold dict
        pass
    return False
```

**Important note on tap detection:** The tap-vs-hold for Directional Slime Hold (D-19) requires tracking hold duration *before* release. The input module must store the previous frame's hold count so `was_tap()` can check it on the release frame. This is a subtle timing issue.

### Pattern 2: Fusion as State Modifier (Not Parallel State Machine)
**What:** `player.is_fused` remains a boolean flag that modifies how existing states and inputs behave, rather than creating a separate "FUSED_IDLE", "FUSED_RUNNING" etc.
**When to use:** All fusion-dependent behavior branching.
**Example:**
```python
# In handle_input():
if input.btnp("dash") and self.state != "DIVING":
    if input.btn("down"):
        # DOWN+V = Drill Dive (both unfused and fused per D-07/D-22)
        self.start_drill_dive(slime)
    elif self.is_fused:
        # V while fused = Slime Ram (D-07)
        self.start_ram(slime)
    elif self.has_dash:
        # V while unfused = Basic Dash (D-15)
        self.start_dash()
```

### Pattern 3: Ability Activation with Resource Gate
**What:** Every fused ability follows: check is_fused -> consume juice -> change state -> on completion: unfuse + slime dissipate/reposition.
**When to use:** Ram, Charge Shot, enhanced Drill Dive.
**Example:**
```python
def start_ram(self, slime):
    """Activate Slime Ram (fused V). D-12 through D-14."""
    self.state = "RAMMING"
    # Direction from facing + input
    self.ram_dx = RAM_SPEED if self.facing_right else -RAM_SPEED
    self.ram_dy = 0
    # Diagonal support: check UP input
    if input.btn("up"):
        self.ram_dy = -RAM_SPEED * RAM_DIAGONAL_FACTOR
    # No initial juice cost -- juice consumed per block broken (D-13)
```

### Pattern 4: Horizontal Block-Breaking Scan (Ram)
**What:** Ram needs to detect and break CRACKED_H tiles in the horizontal movement path, analogous to how Drill Dive scans vertically.
**When to use:** During RAMMING state collision resolution.
**Example:**
```python
# In move_and_collide(), when state == "RAMMING" and horizontal collision detected:
def get_cracked_h_at(self, x, y, width, height):
    """Returns (tx, ty) of a CRACKED_H tile overlapping the AABB, or None."""
    x1 = int(x // TILE_SIZE)
    y1 = int(y // TILE_SIZE)
    x2 = int((x + width - 1) // TILE_SIZE)
    y2 = int((y + height - 1) // TILE_SIZE)
    for ty in range(y1, y2 + 1):
        for tx in range(x1, x2 + 1):
            if self.is_cracked_horizontal(tx, ty):
                return (tx, ty)
    return None
```

### Anti-Patterns to Avoid
- **Separate fused state machine:** Do NOT create FUSED_IDLE, FUSED_RUNNING, etc. This doubles the state space. Use `is_fused` as a modifier on existing states.
- **Hardcoded key checks after abstraction:** Once the input module exists, NEVER use `pyxel.btn(pyxel.KEY_Z)` directly. Always go through the abstraction.
- **Magic numbers for tuning:** All frame durations, speeds, costs, thresholds MUST be named constants in `constants.py`. The user has explicitly flagged this as a requirement (see CLAUDE.md memory).
- **Modifying `check_collision()` behavior:** Do NOT change the base collision function. Add new type-specific query methods (like `get_cracked_h_at()`) alongside `get_destructible_at()`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Input mapping | Inline `pyxel.btn(KEY_Z) or pyxel.btn(KEY_J)` everywhere | `src/core/input.py` abstraction | 13+ input check sites in player.py alone. Duplicating OR logic is error-prone. |
| Tap-vs-hold detection | Ad-hoc frame counters in handle_input | Input module `hold_frames()` + `was_tap()` | Timing logic is subtle (must check on release frame). Centralizing prevents bugs. |
| Horizontal block scan | Custom scan in ram collision handler | Extend `LevelMap` with `get_cracked_h_at()` mirroring existing `get_destructible_at()` | Consistent API, reusable for future horizontal abilities. |

**Key insight:** The existing codebase has strong patterns (state machine in player, consume/refill on slime, get_destructible_at on map). Every new ability should follow these patterns exactly. The only genuinely new infrastructure is the input abstraction.

## Common Pitfalls

### Pitfall 1: Tap-vs-Hold Input Timing
**What goes wrong:** Directional Slime Hold (D-19) requires distinguishing a 4-6 frame tap from a normal walk hold. If the detection runs on keydown, you can't distinguish until the threshold passes, creating input lag for walking.
**Why it happens:** The determination can only be made retroactively (on release or when threshold is exceeded).
**How to avoid:** Two approaches: (A) Commit to walk immediately but on release-before-threshold, trigger slime hold retroactively. This feels more responsive. (B) Delay walk start by threshold frames. This feels laggy. Recommend approach A.
**Warning signs:** Walking feels sluggish, or slime hold triggers accidentally during normal movement.

### Pitfall 2: Spit vs Charge Ambiguity on Z
**What goes wrong:** Z tap = spit, Z hold = recall/charge. If spit fires on `btnp()` (press frame), the player can never hold Z without also spitting first.
**Why it happens:** `btnp()` fires on the first frame of a press, before hold duration is known.
**How to avoid:** Change spit to fire on Z release (if hold duration < threshold) rather than on Z press. This adds a tiny delay to spit but cleanly separates tap from hold. Alternative: spit fires immediately on press AND recall starts simultaneously -- but this wastes a spit every time the player wants to recall.
**Warning signs:** Player spits every time they try to recall slime.

### Pitfall 3: Fusion State Desync Between Player and Slime
**What goes wrong:** `player.is_fused` and `slime.is_fused` get out of sync, causing visual glitches or logic errors.
**Why it happens:** Multiple code paths can end fusion (ability use, damage, juice empty, manual cancel). Missing one path leaves one entity fused while the other is not.
**How to avoid:** Create a single `fuse()` and `unfuse()` method on Player that ALWAYS updates both `player.is_fused` and `slime.is_fused` atomically. Never set either flag directly.
**Warning signs:** Slime draws as drill attachment while player is in IDLE state, or vice versa.

### Pitfall 4: Ram Collision With Non-CRACKED_H Solids
**What goes wrong:** Ram plows through CRACKED_H blocks (correct) but then hits a normal SOLID block and the player clips through or gets stuck.
**Why it happens:** The horizontal collision in `move_and_collide()` currently just stops dx. During RAMMING, the logic needs to: (1) check if the blocking tile is CRACKED_H, (2) if yes, break it and continue, (3) if no, stop ram and unfuse.
**How to avoid:** Mirror the drill dive collision pattern exactly. In the vertical collision section of `move_and_collide()`, drill checks for destructibles before snapping. Do the same in horizontal collision for ram.
**Warning signs:** Ram stops at CRACKED_H blocks instead of breaking through, or clips through solid walls.

### Pitfall 5: Drill Dive Retcon Breaking Existing Controls
**What goes wrong:** Moving Drill Dive from DOWN+SPACE to DOWN+V changes a fundamental control that players have already learned from Phase 7.
**Why it happens:** The old activation check (`pyxel.btn(KEY_DOWN) and pyxel.btnp(KEY_SPACE)`) must be replaced with (`input.btn("down") and input.btnp("dash")`).
**How to avoid:** When refactoring, search for ALL references to the old activation pattern. There are activation checks in `handle_input()` (line 187-196) and cancellation in line 203-207 (SPACE to cancel -- should this also change to V?). Verify cancellation controls are consistent.
**Warning signs:** Drill Dive still activates on DOWN+SPACE, or cancellation doesn't work.

### Pitfall 6: Charge Shot Slime Teleport Creates Invalid State
**What goes wrong:** Charge shot fires slime as projectile to impact point. If impact point is inside a wall, slime is stuck in solid geometry.
**Why it happens:** Projectile hits a wall and slime teleports to the impact coordinates, which are inside the wall.
**How to avoid:** On charge shot impact, use the same safety check as `Slime.reform()` -- if destination is solid, snap to nearest valid position. The existing `reform()` already has this pattern (lines 164-166 of slime.py).
**Warning signs:** Slime gets stuck in walls after charge shot, or appears in unreachable locations.

### Pitfall 7: Door Opening After Kick Removal
**What goes wrong:** Doors currently open via kick (main.py lines 376-380). Removing kick breaks door interaction.
**Why it happens:** D-10 says "Switch-flipping via spit or ram." Doors already have projectile-hit detection (lines 383-388), so spit works. But ram needs to be added as a door opener.
**How to avoid:** When removing kick, verify all kick-dependent interactions are ported: (1) door opening -- already handled by spit projectiles, add ram collision. (2) switch flipping -- the `kick()` method flips switches at line 118-121, need to add switch-flipping to ram and/or spit impact. (3) slime punting -- replaced by charge shot (D-10).
**Warning signs:** Doors cannot be opened, switches cannot be flipped.

## Code Examples

### Existing Pattern: Drill Dive Block Breaking (Reference for Ram)
```python
# From player.py move_and_collide(), lines 347-360
# This exact pattern should be adapted for horizontal RAMMING
if self.state == "DIVING" and slime:
    tile_coord = self.level_map.get_destructible_at(self.x, self.y, self.w, self.h)
    if tile_coord:
        tx, ty = tile_coord
        if self.game:
            self.game.on_block_destroyed(tx, ty, TILE_DESTRUCTIBLE)
        self.level_map.remove_tile(tx, ty)
        if self.game:
            self.game.spawn_explosion(tx * 8, ty * 8, 9)
        slime.refill(DRILL_BLOCK_REFUND)
        self.on_block_break()
        return  # Continue through broken block
```

### Existing Pattern: Slime Reform (Reference for Recall)
```python
# From slime.py reform(), lines 158-175
# Recall (D-25) should animate toward player instead of teleporting
def reform(self, player_x, player_y, player_facing_right, level_map=None):
    offset_x = -SLIME_REFORM_DIST if player_facing_right else SLIME_REFORM_DIST
    new_x = player_x + offset_x
    new_y = player_y
    if level_map and level_map.check_collision(new_x, new_y, self.w, self.h):
        new_x = player_x
        new_y = player_y
    self.x = new_x
    self.y = new_y
    self.dx = 0
    self.dy = 0
    self.history.clear()
```

### New Constants Block (to add to constants.py)
```python
# Fusion System
FUSION_CHARGE_FRAMES = 0  # Auto-fuse when slime arrives + juice at max (D-01, D-02)
RECALL_SPEED = 8.0  # Slime zip speed toward player (~4-6 frames to arrive) (D-25)
RECALL_OVERLAP_DIST = 4  # Pixels of overlap required before fusion triggers (D-26)
MANA_SHIELD_COST = 20.0  # Juice consumed per hit while fused (D-04)
SLIME_DISSIPATE_COOLDOWN = 120  # Frames before slime reforms after juice-empty dissipation (D-05)

# Basic Dash
DASH_SPEED = 4.0  # ~2 tiles in ~8 frames (D-15)
DASH_DURATION = 8  # Frames of dash movement (D-15)
DASH_IFRAMES = 8  # Frames of invulnerability during dash (D-15)
DASH_COOLDOWN = 20  # Frames before dash can be used again (D-15)

# Slime Ram
RAM_SPEED = 5.0  # High speed horizontal movement (D-12)
RAM_DIAGONAL_FACTOR = 0.7  # Multiplier for diagonal ram component
RAM_BLOCK_COST = 15.0  # Juice cost per CRACKED_H block broken (D-13)
RAM_INVINCIBLE = True  # Player is invincible during ram (D-12)

# Charge Shot
CHARGE_SHOT_SPEED = 6.0  # Projectile speed (faster than normal spit) (D-16)
CHARGE_SHOT_SIZE = 8  # Larger projectile (D-16)
CHARGE_SHOT_DAMAGE = 3  # High damage (D-16)

# Directional Slime Hold
HOLD_TAP_THRESHOLD = 5  # Frames: <= this = tap (reposition), > this = walk (D-19)

# Recall Visual
RECALL_TRAIL_COLOR = 11  # Pyxel palette color for rubber-band trail (D-25)

# Drill Dive Retcon (rename existing constants for clarity)
# DRILL_SPEED, DRILL_DRIFT_SPEED, etc. remain unchanged
# Activation key changes from DOWN+SPACE to DOWN+V (D-22)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `pyxel.btn(KEY_Z)` direct calls | Input abstraction module | Phase 8 | All 13+ input sites in player.py must migrate |
| DOWN+SPACE = Drill Dive | DOWN+V = Drill Dive | Phase 8 (D-22) | Key binding change, affects muscle memory |
| `has_drill` from DRILL item pickup | `has_drill` from Mole Boss defeat | Phase 8 (D-23) | Item entity removed, boss grants ability |
| V = kick | V = dash/ram | Phase 8 (D-10) | Kick mechanic fully removed |
| `is_fused` = only during drill dive | `is_fused` = charge-to-100% fusion state | Phase 8 (D-01) | Fusion is now a resource-earned state, not just drill attachment |

**Deprecated/outdated:**
- `Player.kick()` method: Remove entirely (D-10). All interactions it provided (door opening, switch flipping, slime punting) are replaced by spit, ram, and charge shot.
- `KICK_DURATION` and `SLIME_PUNT_SPEED` constants: Remove from constants.py.
- `DRILL` item type in items.py: Remove. `Drill` entity type in entity-schema.json should be updated.
- `player.kick_timer`: Remove field and all references.
- Door kick-hit detection in main.py (lines 376-380): Remove, ensure spit/ram cover this.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | unittest (stdlib) with unittest.mock |
| Config file | None (tests run directly) |
| Quick run command | `python -m pytest tests/ -x --timeout=10` or `python -m unittest discover tests/ -v` |
| Full suite command | `python -m unittest discover tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ABL-01 | Ram breaks CRACKED_H blocks, costs juice per block | unit | `python -m unittest tests.test_ram -v` | Wave 0 |
| ABL-01 | Ram stops at solid (non-cracked) blocks | unit | `python -m unittest tests.test_ram -v` | Wave 0 |
| ABL-01 | Ram ends + unfuses when juice hits 0 | unit | `python -m unittest tests.test_ram -v` | Wave 0 |
| ABL-03 | Tap left/right repositions slime (hold duration < threshold) | unit | `python -m unittest tests.test_slime_hold -v` | Wave 0 |
| ABL-03 | Hold left/right walks normally (hold duration > threshold) | unit | `python -m unittest tests.test_slime_hold -v` | Wave 0 |
| ABL-04 | Charge shot fires on Z release while fused, dumps all juice | unit | `python -m unittest tests.test_charge_shot -v` | Wave 0 |
| ABL-04 | Slime teleports to impact point after charge shot | unit | `python -m unittest tests.test_charge_shot -v` | Wave 0 |
| FUSION | Fusion triggers at juice 100% + slime overlap | unit | `python -m unittest tests.test_fusion -v` | Wave 0 |
| FUSION | Mana shield: fused damage consumes juice not HP | unit | `python -m unittest tests.test_fusion -v` | Wave 0 |
| FUSION | Slime dissipates when juice empties while fused | unit | `python -m unittest tests.test_fusion -v` | Wave 0 |
| INPUT | WASD+JK secondary mapping matches arrow+ZV | unit | `python -m unittest tests.test_input -v` | Wave 0 |
| DASH | Basic dash provides i-frames, respects cooldown | unit | `python -m unittest tests.test_dash -v` | Wave 0 |
| RETCON | Drill Dive activates on DOWN+V, not DOWN+SPACE | unit | `python -m unittest tests.test_drill_retcon -v` | Wave 0 |
| RETCON | Kick method removed, no kick_timer references | unit | `python -m unittest tests.test_kick_removal -v` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m unittest discover tests/ -v`
- **Per wave merge:** Full suite
- **Phase gate:** Full suite green before verify

### Wave 0 Gaps
- [ ] `tests/test_input.py` -- input abstraction module tests
- [ ] `tests/test_fusion.py` -- fusion charge/trigger/unfuse/mana shield/dissipate
- [ ] `tests/test_dash.py` -- basic dash i-frames, cooldown, air usage
- [ ] `tests/test_ram.py` -- slime ram CRACKED_H breaking, juice cost, stop conditions
- [ ] `tests/test_charge_shot.py` -- charge shot fire, slime repositioning
- [ ] `tests/test_slime_hold.py` -- tap-vs-hold detection, slime repositioning
- [ ] `tests/test_drill_retcon.py` -- DOWN+V activation, boss-grant instead of item
- [ ] `tests/test_kick_removal.py` -- verify kick code fully removed

## Open Questions

1. **Drill Dive cancellation key after retcon**
   - What we know: Currently cancelled by pressing SPACE (player.py line 204). Drill activates on DOWN+V now.
   - What's unclear: Should cancellation also move to V (release V to cancel) or remain on SPACE (jump to cancel)? SPACE as cancel is intuitive (jump out of dive).
   - Recommendation: Keep SPACE as drill cancel. It's the "escape" action and doesn't conflict. Document this decision.

2. **Dash ability pickup entity**
   - What we know: D-24 says "find dash ability, V unlocked" in early game. DRILL item is removed.
   - What's unclear: What entity type replaces Drill as the dash pickup? Need a new entity in entity-schema.json.
   - Recommendation: Add "DashBoots" or "DashPickup" entity to schema. Simple item like existing EnergyTank.

3. **Slime recall visual while slime is punted/in-flight**
   - What we know: Hold Z recalls slime (D-25). Slime can be in punted state or mid-air.
   - What's unclear: Does recall override punt? Does recall work while slime is a charge-shot projectile?
   - Recommendation: Recall overrides punt (sets `is_punted = False`, starts zip toward player). Recall does NOT work while slime is a charge-shot projectile (slime is "used up" until it lands).

4. **Entity schema update for Drill removal**
   - What we know: `assets/entity-schema.json` defines "Drill" entity. It is shared with pml-to-ldtk converter.
   - What's unclear: Should we remove Drill entirely or rename to DashPickup?
   - Recommendation: Replace "Drill" with "DashPickup" in entity-schema.json. Update converter compatibility note.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Runtime | Yes | 3.13.11 | -- |
| Pyxel | Game engine | Yes | 2.8.7 | -- |
| unittest | Test framework | Yes | stdlib | -- |

No missing dependencies.

## Sources

### Primary (HIGH confidence)
- Direct codebase analysis: `src/entities/player.py`, `src/entities/slime.py`, `src/core/constants.py`, `src/entities/projectile.py`, `src/entities/items.py`, `src/level/map.py`, `src/level/world.py`, `main.py`
- `assets/entity-schema.json` -- shared contract with converter
- Phase 8 CONTEXT.md -- 26 locked decisions
- Existing test files (`tests/test_destruction.py`) -- testing patterns with pyxel mocking
- [Pyxel GitHub](https://github.com/kitao/pyxel) -- input API (`btn`, `btnp`, `btnr`) confirmed

### Secondary (MEDIUM confidence)
- Pyxel key constant naming (`pyxel.KEY_J`, `pyxel.KEY_K`, `pyxel.KEY_A`, `pyxel.KEY_W`, `pyxel.KEY_S`, `pyxel.KEY_D`) -- standard naming pattern confirmed by Pyxel source

### Tertiary (LOW confidence)
- None. All findings based on direct code inspection.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no new dependencies, fully inspected existing codebase
- Architecture: HIGH - patterns directly derived from existing drill dive, reform, spit implementations
- Pitfalls: HIGH - identified from concrete code paths and integration points in the actual source
- Input abstraction: HIGH - Pyxel API is simple (btn/btnp/btnr), wrapper is straightforward

**Research date:** 2026-03-28
**Valid until:** 2026-04-28 (stable -- Pyxel and codebase are under our control)
