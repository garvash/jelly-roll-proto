---
phase: 08-new-fusion-abilities
plan: 04
subsystem: fusion-combat
tags: [ram, charge-shot, cracked-h, gate-breaking, fusion, projectile]

requires:
  - phase: 08-new-fusion-abilities
    plan: 03
    provides: Fusion system core (fuse/unfuse, mana shield, recall, directional hold)
provides:
  - Slime Ram ability (ABL-01): V while fused = high-speed horizontal dash breaking CRACKED_H blocks
  - Charge Shot ability (ABL-04): Z release while fused = max-power slime projectile with teleport
affects: [player, slime, projectile, enemies, doors, level-map]

tech-stack:
  added: []
  patterns: [ram-through-breakable, slime-as-projectile-teleport, damage-attribute-polymorphism]

key-files:
  created: [tests/test_ram.py, tests/test_charge_shot.py]
  modified: [src/core/constants.py, src/level/map.py, src/entities/player.py, src/entities/projectile.py, src/entities/enemies.py, main.py]

key-decisions:
  - "Ram uses invuln_timer=9999 during ram, reset to DASH_IFRAMES on end"
  - "Charge shot sets is_fused=False directly (not via unfuse) because slime position is managed by ChargeProjectile"
  - "Enemy.take_damage accepts optional amount parameter for charge shot damage scaling"
  - "ChargeProjectile nudges slime upward on solid impact to prevent wall embedding (Pitfall 6)"

requirements-completed: [ABL-01, ABL-04]

duration: 6min
completed: 2026-03-28
---

# Phase 08 Plan 04: Slime Ram and Charge Shot Summary

**Slime Ram (Shinespark-style CRACKED_H gate breaker) and Charge Shot (all-or-nothing slime projectile with teleport on impact)**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-28T06:32:20Z
- **Completed:** 2026-03-28T06:38:00Z
- **Tasks:** 3/3
- **Files modified:** 6

## Accomplishments
- Added RAM_SPEED, RAM_BLOCK_COST, RAM_DIAGONAL_FACTOR constants and CHARGE_SHOT_SPEED/SIZE/DAMAGE constants
- Added LevelMap.get_cracked_h_at() mirroring get_destructible_at pattern for CRACKED_H-specific scanning
- Implemented full Slime Ram: RAMMING state, start_ram/apply_ram_physics/end_ram methods, diagonal support, CRACKED_H block breaking at 15 juice/block, stops at solids, dissipates on juice empty
- Ram opens doors (D-10 -- replaces kick for door interaction)
- Implemented ChargeProjectile class: slime IS the projectile, teleports to impact point, safety check prevents wall embedding
- Added fire_charge_shot: Z release while fused dumps all juice, auto-unfuses, spawns ChargeProjectile
- Updated Enemy.take_damage to accept optional damage amount for charge shot's 3-damage hits
- 19 new tests (10 ram + 9 charge shot) covering all mechanics

## Task Commits

Each task was committed atomically:

1. **Task 1: Add ram/charge constants and get_cracked_h_at()** - `a056ad9` (feat)
2. **Task 2: Implement Slime Ram with CRACKED_H block breaking** - `1481ee6` (feat)
3. **Task 3: Implement Charge Shot with slime-as-projectile** - `6393c19` (feat)

## Files Created/Modified
- `src/core/constants.py` - Added RAM_SPEED, RAM_BLOCK_COST, RAM_DIAGONAL_FACTOR, RAM_INVINCIBLE, CHARGE_SHOT_SPEED, CHARGE_SHOT_SIZE, CHARGE_SHOT_DAMAGE
- `src/level/map.py` - Added get_cracked_h_at() method for CRACKED_H tile detection
- `src/entities/player.py` - Added RAMMING state, start_ram/apply_ram_physics/end_ram/fire_charge_shot methods, ram branch in handle_input, RAMMING collision handling in move_and_collide
- `src/entities/projectile.py` - Added ChargeProjectile class with slime teleport, safety nudge, damage attribute
- `src/entities/enemies.py` - Updated Enemy.take_damage to accept optional damage parameter
- `main.py` - Added ram-opens-door logic, charge shot damage attribute usage in enemy collision
- `tests/test_ram.py` - 10 tests: state, speed, direction, diagonal, invincibility, CRACKED_H breaking, solid stopping, juice depletion, unfuse
- `tests/test_charge_shot.py` - 9 tests: creation, damage, movement, direction, juice dump, unfuse, slime reposition, wall safety

## Decisions Made
- Ram invincibility uses invuln_timer=9999, cleared to DASH_IFRAMES on ram end (clean reuse of existing system)
- Charge shot bypasses unfuse() because slime position is deferred to ChargeProjectile impact handler
- Enemy.take_damage made backward-compatible with default amount=1 for existing callers
- ChargeProjectile nudges slime upward in TILE_SIZE increments to find valid non-solid position on impact

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Enemy.take_damage damage parameter**
- **Found during:** Task 3
- **Issue:** Enemy.take_damage() always decremented HP by 1, ignoring charge shot's CHARGE_SHOT_DAMAGE=3
- **Fix:** Added optional `amount=1` parameter to Enemy.take_damage, used getattr(p, 'damage', 1) in main.py
- **Files modified:** src/entities/enemies.py, main.py
- **Committed in:** 6393c19

---

**Total deviations:** 1 auto-fixed (missing critical)
**Impact on plan:** Necessary for charge shot to deal correct damage. No scope creep.

## Known Stubs
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All four fusion abilities now implemented: Dash (unfused), Drill Dive (DOWN+V), Slime Ram (fused V), Charge Shot (fused Z release)
- CRACKED_H world gating ready for level design (ram breaks horizontal cracked blocks)
- Charge shot provides tactical slime repositioning for advanced play

---
*Phase: 08-new-fusion-abilities*
*Completed: 2026-03-28*
