---
phase: 25
plan: 01
subsystem: player-entity
tags: [refactor, tuning, constants-migration, call-sites]
requires:
  - src/core/tuning.py (Phase 24 — tuning loader with PEP 562 flat access)
  - src/core/constants.py (compat shim with HAZARD_DRAIN_RATES int-key fix-up)
provides:
  - src/entities/player.py reads physics values live via tuning.X at every per-frame use site
affects:
  - Every per-frame physics read in Player is now hot-reloadable by Phase 28 panel
tech_stack:
  added: []
  patterns:
    - "from src.core import tuning + tuning.X at use site (D-03)"
    - "Explicit from src.core.constants import HAZARD_DRAIN_RATES for int-keyed dict (D-02a exception)"
key_files:
  created: []
  modified:
    - src/entities/player.py
decisions:
  - "Kept HAZARD_DRAIN_RATES on the shim — int-key dict built by constants.py line 26, not per-frame, does not benefit from live-tuning"
  - "Left INTGRID_CRACKED_H/V (lines 11-12) as local literals — tied to entity-schema.json, not tuning keys"
  - "Used six-step ordered sweep per D-03a: collision grep -> add import -> explicit HAZARD_DRAIN_RATES -> prefix sweep -> delete wildcard -> boot check"
metrics:
  duration: ~15min
  completed: 2026-04-12
  tuning_refs_added: 90
  distinct_tuning_keys: 49
  files_changed: 1
  lines_added: 77
  lines_removed: 76
requirements:
  - FND-05
---

# Phase 25 Plan 01: Player Migration Summary

**One-liner:** Migrated `src/entities/player.py` from `from src.core.constants import *` wildcard onto 90 use-site `tuning.X` reads across 49 distinct flat keys, keeping `HAZARD_DRAIN_RATES` on the compat shim for its int-keyed form.

## What Changed

Single file edited: `src/entities/player.py` (822 LOC).

- **Import block:** removed `from src.core.constants import *`, added `from src.core import tuning` and `from src.core.constants import HAZARD_DRAIN_RATES`.
- **Call sites:** 90 bare tuning-key references prefixed with `tuning.` across 49 distinct keys.
- **Preserved:** `INTGRID_CRACKED_H = 11` and `INTGRID_CRACKED_V = 12` module-level literals (lines 11-12) untouched — these are entity-schema values, not tuning keys.
- **Preserved:** every `HAZARD_DRAIN_RATES` reference stays unprefixed (int-keyed shim copy).
- **No logic changes.** Diff is a pure rename: 77 insertions / 76 deletions (the single net +1 line is the explicit `HAZARD_DRAIN_RATES` import).

## Distinct tuning keys migrated (49)

BOOST_CRACKED_V_COST, BOOST_FORCE, BOOST_JUICE_COST, BOOST_RECOMMIT_WINDOW,
CHARGE_RECOIL_FORCE, COYOTE_TIME, DASH_COOLDOWN, DASH_DURATION, DASH_IFRAMES,
DASH_SPEED, DRILL_ACTIVATION_COST, DRILL_BLOCK_REFUND, DRILL_CRACKED_V_COST,
DRILL_DRIFT_SPEED, DRILL_HITSTOP_FRAMES, DRILL_IMPACT_COST, DRILL_SHAKE_DURATION,
DRILL_SPEED, FALLING_GRAVITY_MULTIPLIER, GRAVITY, HAZARD_DRAIN_SLOW,
HAZARD_HP_DRAIN_INTERVAL, HOLD_TAP_THRESHOLD, INVULN_DURATION, JUMP_BUFFER,
JUMP_FORCE, KNOCKBACK_FORCE_X, KNOCKBACK_FORCE_Y, MANA_SHIELD_COST, MAX_FALL_SPEED,
MAX_WALK_SPEED, PLAYER_MAX_HP, PROJECTILE_SPEED, RAM_BLOCK_COST, RAM_DIAGONAL_FACTOR,
RAM_SPEED, SHIELD_REACTIVATION_COOLDOWN, SHIELD_T2_DRAIN_REDUCTION, SLIME_MAX_DIST,
SPIT_AIM_RANGE, SPIT_HOLD_THRESHOLD, SPRITE_SIZE, TILE_SIZE, VARIABLE_JUMP_REDUCTION,
WALK_ACCEL, WALK_FRICTION, WALL_JUMP_X_IMPULSE, WALL_JUMP_Y_FORCE, WALL_SLIDE_FRICTION.

## HAZARD_DRAIN_RATES Decision

Confirmed per plan and 25-CONTEXT.md "Known Constraints": `HAZARD_DRAIN_RATES` stays on the shim import. `src/core/constants.py` line 26 builds an int-keyed copy of the JSON-stringified dict that player.py indexes by int IntGrid IDs (6/7/8). The dict is read once per frame in `update_shield()` via `HAZARD_DRAIN_RATES.get(zone_type, tuning.HAZARD_DRAIN_SLOW)` and is not a per-frame physics value, so it gains nothing from live-tuning. This is the single deliberate exception to the migration rule, documented via an explicit `from src.core.constants import HAZARD_DRAIN_RATES` at the top of player.py so future cleanups cannot accidentally remove it.

## Collisions Encountered (Step 1)

None. Collision grep found only the two local literals `INTGRID_CRACKED_H = 11` and `INTGRID_CRACKED_V = 12` (lines 11-12) plus class/method definitions. No local UPPER_SNAKE names in player.py shadow any tuning key, so the wildcard deletion was safe.

## Verification

**Step-by-step boot checks (D-03a ordering):**
1. Added `from src.core import tuning` alongside the existing wildcard — `python -c "import src.entities.player"` passed.
2. Added explicit `from src.core.constants import HAZARD_DRAIN_RATES` — passed.
3. Swept file, prefixing every bare tuning key with `tuning.` (35 `replace_all` edits + 1 targeted two-line edit for bare `GRAVITY` which needed care to avoid clobbering `FALLING_GRAVITY_MULTIPLIER`).
4. Deleted `from src.core.constants import *` — `python -c "import src.entities.player"` passed.

**Acceptance criteria (all pass):**
- `from src.core.constants import *` removed (count: 0)
- `from src.core import tuning` present (count: 1)
- `from src.core.constants import HAZARD_DRAIN_RATES` present (count: 1)
- `tuning.GRAVITY`, `tuning.JUMP_FORCE`, `tuning.MAX_WALK_SPEED`, `tuning.FALLING_GRAVITY_MULTIPLIER`, `tuning.DRILL_SPEED`, `tuning.BOOST_FORCE`, `tuning.RAM_SPEED`, `tuning.PLAYER_MAX_HP` all present
- No bare `GRAVITY` outside `tuning.GRAVITY` (excluding comments and `FALLING_GRAVITY_MULTIPLIER`)
- `INTGRID_CRACKED_H = 11` and `INTGRID_CRACKED_V = 12` preserved
- `python -c "import src.entities.player"` exits 0
- `python -m pytest tests/test_tuning.py -q` — **11 passed**
- `python -m pytest -q` — **363 passed, 3 skipped** (pre-existing skips, no regressions). The 3 skipped are not introduced by this plan; the full suite — including `tests/test_physics.py` which still imports `from src.core.constants import *` — is green.

## Notes

- **`tests/test_physics.py` still imports from the shim.** This is intentional per D-02b. The compat shim in `src/core/constants.py` remains untouched and covers the 27 legacy test files that were deliberately left on the old import pattern. No tests were migrated in this plan.
- **Frame-for-frame parity** is guaranteed by construction: the refactor is a rename, not a value change. No `if`/`else` branches, no ordering tweaks, no new temp variables (the existing `curr_gravity = tuning.GRAVITY` capture was already present as `curr_gravity = GRAVITY` — only the RHS changed).
- **D-01 captures in `__init__`** (`self.hp = tuning.PLAYER_MAX_HP`, `self.max_hp = tuning.PLAYER_MAX_HP`) kept as captures per the plan — the RHS is the migrated part, the LHS capture pattern stays for grep uniformity.
- **Phase 25 bottleneck cleared.** Player.py was the single largest file in the phase (50+ of the ~104 call sites). Plans 02-04 are now unblocked; Plan 02's livereach test can exercise this file directly.

## Deviations from Plan

None. The plan executed exactly as written, in the documented six-step D-03a order.

## Self-Check: PASSED

- FOUND: .planning/phases/25-call-site-migration-constants-tuning/25-01-SUMMARY.md (this file)
- FOUND: src/entities/player.py (modified)
- FOUND commit: 8671cc8 (refactor(25-01): migrate player.py from constants wildcard to tuning reads)
