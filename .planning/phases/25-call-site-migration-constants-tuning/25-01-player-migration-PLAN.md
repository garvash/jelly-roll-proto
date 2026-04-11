---
phase: 25
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/entities/player.py
autonomous: true
requirements:
  - FND-05
must_haves:
  truths:
    - "src/entities/player.py no longer has `from src.core.constants import *` at line 2"
    - "src/entities/player.py imports `from src.core import tuning` exactly once"
    - "Every per-frame physics read in player.py (GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, ACCEL, FRICTION, WALL_*, DRILL_*, CHARGE_*, BOOST_*, RAM_*, KICK_*, etc.) resolves via `tuning.<NAME>`"
    - "HAZARD_DRAIN_RATES continues to import from src.core.constants (int-key form required)"
    - "`python -c \"import src.entities.player\"` exits 0"
    - "`pytest -q` green on the existing 27 test files (shim still works)"
    - "Player boots with frame-for-frame v1.3 physics (numerical identity by construction)"
  artifacts:
    - path: "src/entities/player.py"
      provides: "Player entity reading tuning.* at every per-frame use site"
      contains: "from src.core import tuning"
  key_links:
    - from: "src/entities/player.py"
      to: "src/core/tuning.py"
      via: "module attribute reads (`tuning.GRAVITY`, `tuning.JUMP_FORCE`, ...) inside update()/move()/apply_gravity()/jump()/drill_dive()/etc."
      pattern: "tuning\\.(GRAVITY|JUMP_FORCE|MAX_WALK_SPEED|WALK_ACCEL|WALK_FRICTION|WALL_|DRILL_|CHARGE_|BOOST_|RAM_|KICK_|DASH_|SPIT_|HOLD_|COYOTE|JUMP_BUFFER|FALLING_GRAVITY|MAX_FALL|KNOCKBACK|INVULN|VARIABLE_JUMP|SPRITE_SIZE|TILE_SIZE|PLAYER_MAX_HP|MANA_SHIELD|SHIELD_|HAZARD_HP|PROJECTILE_SPEED|SLIME_MAX_DIST)"
    - from: "src/entities/player.py"
      to: "src/core/constants.py"
      via: "HAZARD_DRAIN_RATES import (int-keyed dict, non-feel, stays on shim)"
      pattern: "from src\\.core\\.constants import HAZARD_DRAIN_RATES"
---

<objective>
Migrate `src/entities/player.py` (822 LOC, dominant work item) off the `from src.core.constants import *` wildcard and onto use-site `tuning.X` reads. This is the single largest file in Phase 25 and accounts for ~50 of the ~104 call sites in the entire migration. After this plan, every per-frame physics read in player.py resolves live against `src.core.tuning._model`, so future `tuning.set_value()` calls (Phase 28 panel) reach gameplay on the next frame with zero mid-run cache.

Purpose: Phase 25 requirement FND-05 (call-site migration) is bottlenecked on this one file. If player.py is clean, the other 11 files in Plans 03 and 04 are copy-paste. The livereach test in Plan 02 exercises Player directly, so this plan must land first.

Output: `src/entities/player.py` with one new `from src.core import tuning` import, the old `from src.core.constants import *` deleted, every bare tuning-key name prefixed with `tuning.`, and `HAZARD_DRAIN_RATES` explicitly still imported from `src.core.constants` for its int-key form.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/25-call-site-migration-constants-tuning/25-CONTEXT.md
@.planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md
@src/core/tuning.py
@src/core/constants.py
@src/entities/player.py

<interfaces>
<!-- Key contracts the executor needs. Extracted from codebase. -->
<!-- Executor should use these directly — no codebase exploration needed. -->

From src/core/tuning.py (PEP 562 flat access — D-13):
```python
# Importing `tuning` triggers auto-load() at module bottom.
# Every flat key in assets/physics-schema.json is exposed via __getattr__:
from src.core import tuning
tuning.GRAVITY           # -> float, live read from _model['movement']['GRAVITY']
tuning.JUMP_FORCE        # -> float
tuning.MAX_WALK_SPEED    # -> float
tuning.set_value('GRAVITY', 0.09)  # mutates in-memory; next tuning.GRAVITY read sees 0.09
tuning.reset()           # restores _model from _baseline (for test teardown)
```

From src/core/constants.py (compat shim — STAYS UNCHANGED in Phase 25):
```python
# Wildcard re-export of tuning.* plus int-keyed HAZARD_DRAIN_RATES.
# HAZARD_DRAIN_RATES is a NON-SCALAR dict: assets/physics-schema.json stores its
# keys as strings ("6","7","8") because JSON, but callers index it with int
# IntGrid IDs. The shim rebuilds it with int keys at line 26:
HAZARD_DRAIN_RATES = {int(k): v for k, v in _tuning.HAZARD_DRAIN_RATES.items()}
# Any migrated caller that uses HAZARD_DRAIN_RATES must still import it from
# constants (not tuning) to get the int-keyed form. This is the ONE exception
# to the "move everything to tuning.X" rule in Phase 25.
```

Current player.py import block (lines 1–10):
```python
import pyxel
from src.core.constants import *
from src.entities.effects import Particle
from src.core.sprite_utils import draw_sprite
import src.core.input as input_manager
import src.core.debug as debug

# IntGrid values for cracked blocks (from entity-schema.json)
INTGRID_CRACKED_H = 11  # Horizontal cracked block
INTGRID_CRACKED_V = 12  # Vertical cracked block
```
Lines 9–10 (`INTGRID_CRACKED_H/V`) are local literals tied to entity-schema.json, NOT tuning keys. Leave them untouched.

Bare-name references observed in player.py that become `tuning.X` (non-exhaustive — executor must grep to find them all):
- Movement: GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, WALK_ACCEL, WALK_FRICTION, MAX_FALL_SPEED, FALLING_GRAVITY_MULTIPLIER, VARIABLE_JUMP_REDUCTION
- Forgiving: COYOTE_TIME, JUMP_BUFFER
- Wall: WALL_SLIDE_FRICTION, WALL_JUMP_X_IMPULSE, WALL_JUMP_Y_FORCE
- Drill: DRILL_SPEED, DRILL_SHAKE_DURATION, DRILL_HITSTOP_FRAMES, DRILL_ACTIVATION_COST, DRILL_CRACKED_V_COST, DRILL_BLOCK_REFUND, DRILL_IMPACT_COST, DRILL_DRIFT_SPEED
- Charge shot: CHARGE_RECOIL_FORCE (plus any CHARGE_SHOT_* the file references)
- Boost: BOOST_FORCE, BOOST_JUICE_COST, BOOST_RECOMMIT_WINDOW, BOOST_CRACKED_V_COST
- Ram: RAM_SPEED, RAM_DIAGONAL_FACTOR, RAM_BLOCK_COST
- Dash: DASH_SPEED, DASH_DURATION, DASH_COOLDOWN, DASH_IFRAMES
- Spit / hold: SPIT_HOLD_THRESHOLD, SPIT_AIM_RANGE, HOLD_TAP_THRESHOLD, PROJECTILE_SPEED, SLIME_MAX_DIST
- Combat / shield: PLAYER_MAX_HP, INVULN_DURATION, MANA_SHIELD_COST, SHIELD_T2_DRAIN_REDUCTION, SHIELD_REACTIVATION_COOLDOWN, HAZARD_DRAIN_SLOW, HAZARD_HP_DRAIN_INTERVAL, KNOCKBACK_FORCE_X, KNOCKBACK_FORCE_Y
- Tile / sprite: TILE_SIZE, SPRITE_SIZE
- HAZARD_DRAIN_RATES → EXCEPTION, stays on shim import
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Migrate player.py from wildcard to use-site tuning reads</name>
  <files>src/entities/player.py</files>
  <read_first>
    - src/entities/player.py (read the WHOLE file, 822 LOC, before any edit — you will miss call sites if you skim)
    - src/core/tuning.py (understand PEP 562 `__getattr__`, set_value, reset, _flat_index)
    - src/core/constants.py (understand the HAZARD_DRAIN_RATES int-key fix-up at line 26 — DO NOT MODIFY this file)
    - .planning/phases/25-call-site-migration-constants-tuning/25-CONTEXT.md (especially D-01, D-03, D-03a, and the `HAZARD_DRAIN_RATES` note in the "Known Constraints" section)
  </read_first>
  <action>
Execute the wildcard-kill in six ordered steps. Do NOT shortcut the order — the safe sequence is adopted from D-03a of 25-CONTEXT.md and prevents NameError hunt-and-peck:

**Step 1 — Collision grep (5 seconds, mandatory).**
Before touching imports, run a grep on player.py for any local names that might shadow a tuning key. Use the Grep tool: pattern `^\s*(def |class |[A-Z_]+ ?=)` over `src/entities/player.py`. The only local UPPER_SNAKE names currently expected are `INTGRID_CRACKED_H` and `INTGRID_CRACKED_V` on lines 9–10 (these are NOT tuning keys and must not be prefixed). If you find any other local UPPER_SNAKE name, STOP and report a collision — a name like `MAX_WALK_SPEED = something` inside the file would be shadowed by a bare use after the wildcard deletion. Expected result: only INTGRID_CRACKED_H/V; proceed.

**Step 2 — Add the new import alongside the old one.**
Edit the top of player.py to insert `from src.core import tuning` on a new line. At this point the file must look like:
```python
import pyxel
from src.core.constants import *
from src.core import tuning
from src.entities.effects import Particle
...
```
Do NOT delete the wildcard yet. This intermediate state must still parse and boot — the game will import `tuning` and the wildcard keeps bare names bound. Verify: `python -c "import src.entities.player"` exits 0.

**Step 3 — Preserve HAZARD_DRAIN_RATES binding explicitly.**
Add a second, explicit import line right after the `from src.core import tuning` line:
```python
from src.core.constants import HAZARD_DRAIN_RATES
```
Rationale (per 25-CONTEXT.md "Known Constraints"): `HAZARD_DRAIN_RATES` is a dict with int-keyed entries that only `constants.py` builds (line 26 int-key fix-up). It is read once per hazard-zone entry, is not per-frame physics, and gains nothing from live-tuning. It stays on the shim import. After Step 5 (wildcard deletion), this explicit import is the ONLY remaining line that sources from `src.core.constants` in player.py.

**Step 4 — Sweep the file, prefixing every bare tuning-key reference with `tuning.`.**
For every occurrence of a bare UPPER_SNAKE name that maps to a `tuning.*` flat key, replace `NAME` with `tuning.NAME`. The full list of categories to sweep (per D-01 and the interfaces block above):

- **Movement / per-frame physics (these are the FEEL values — MUST be live reads):** GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, WALK_ACCEL, WALK_FRICTION, MAX_FALL_SPEED, FALLING_GRAVITY_MULTIPLIER, VARIABLE_JUMP_REDUCTION
- **Forgiving timers:** COYOTE_TIME, JUMP_BUFFER
- **Wall:** WALL_SLIDE_FRICTION, WALL_JUMP_X_IMPULSE, WALL_JUMP_Y_FORCE
- **Drill cluster:** DRILL_SPEED, DRILL_SHAKE_DURATION, DRILL_HITSTOP_FRAMES, DRILL_ACTIVATION_COST, DRILL_CRACKED_V_COST, DRILL_BLOCK_REFUND, DRILL_IMPACT_COST, DRILL_DRIFT_SPEED
- **Charge shot cluster:** CHARGE_RECOIL_FORCE and any other CHARGE_SHOT_* the file references
- **Boost cluster:** BOOST_FORCE, BOOST_JUICE_COST, BOOST_RECOMMIT_WINDOW, BOOST_CRACKED_V_COST
- **Ram cluster:** RAM_SPEED, RAM_DIAGONAL_FACTOR, RAM_BLOCK_COST
- **Dash cluster:** DASH_SPEED, DASH_DURATION, DASH_COOLDOWN, DASH_IFRAMES
- **Spit / hold / projectile:** SPIT_HOLD_THRESHOLD, SPIT_AIM_RANGE, HOLD_TAP_THRESHOLD, PROJECTILE_SPEED, SLIME_MAX_DIST
- **Combat / shield / hazard:** PLAYER_MAX_HP, INVULN_DURATION, MANA_SHIELD_COST, SHIELD_T2_DRAIN_REDUCTION, SHIELD_REACTIVATION_COOLDOWN, HAZARD_DRAIN_SLOW, HAZARD_HP_DRAIN_INTERVAL, KNOCKBACK_FORCE_X, KNOCKBACK_FORCE_Y
- **Tile / sprite dims:** TILE_SIZE, SPRITE_SIZE

**D-01 exception — RHS of `__init__` captures:** Lines like `self.hp = PLAYER_MAX_HP` and `self.max_hp = PLAYER_MAX_HP` inside `__init__` stay as captures (not @property). The LEFT side stays; the RIGHT side becomes `tuning.PLAYER_MAX_HP`. Per D-01, these are non-feel captures kept for grep uniformity. The same rule applies to any other `self.FOO = BARE_NAME` assignment in `__init__`: rewrite RHS only.

**EXCLUSIONS (do NOT prefix):**
- `HAZARD_DRAIN_RATES` (kept as bare name via Step 3 explicit import)
- `INTGRID_CRACKED_H`, `INTGRID_CRACKED_V` (local literals, lines 9–10)
- String literals that happen to contain these names (e.g., `"IDLE"`, `"RUNNING"` state names — these are strings, not tuning keys)
- Any dotted references that are already prefixed (e.g., `self.SOMETHING` — these are attributes, not bare names)

**Sweep technique:** use Grep (not manual reading) to find every bare UPPER_SNAKE token. Pattern: `\b[A-Z][A-Z0-9_]{2,}\b` over player.py. For each hit, classify as (a) tuning key → prefix with `tuning.`, (b) HAZARD_DRAIN_RATES → leave, (c) INTGRID_CRACKED_* → leave, (d) Python built-in / string / state name → leave. The Edit tool can do per-line replacements; for names with many occurrences, use `replace_all: true` on the Edit tool but ONLY after verifying the name does not appear as a substring of a different identifier (e.g., `RAM_SPEED` is fine; `SPEED` alone would not be since `WALK_SPEED` contains it).

**Step 5 — Delete the wildcard line.**
Once Step 4 is complete, remove `from src.core.constants import *` from line 2. The file's import block should now end with `from src.core import tuning` + `from src.core.constants import HAZARD_DRAIN_RATES` (plus the pyxel/effects/sprite_utils/input_manager/debug imports that were already there).

**Step 6 — Boot check.**
Run `python -c "import src.entities.player"` — it must exit 0. If NameError fires, a bare tuning key was missed in Step 4; grep for the missing name, prefix it, retry. Repeat until the import is clean.

Rationale for the order: adding the new import first (Step 2) keeps the file bootable throughout the sweep. Deleting the wildcard last (Step 5) means the executor never has to chase NameErrors across a half-migrated file. The explicit `HAZARD_DRAIN_RATES` import (Step 3) is the ONE deliberate exception per the int-key fix-up; documenting it in code prevents a future cleanup from accidentally removing it.
  </action>
  <verify>
    <automated>python -c "import src.entities.player"</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "from src.core.constants import \*" src/entities/player.py` returns 0
    - `grep -c "from src.core import tuning" src/entities/player.py` returns 1
    - `grep -c "from src.core.constants import HAZARD_DRAIN_RATES" src/entities/player.py` returns 1
    - `grep -c "tuning.GRAVITY" src/entities/player.py` returns at least 1
    - `grep -c "tuning.JUMP_FORCE" src/entities/player.py` returns at least 1
    - `grep -c "tuning.MAX_WALK_SPEED" src/entities/player.py` returns at least 1
    - `grep -c "tuning.FALLING_GRAVITY_MULTIPLIER" src/entities/player.py` returns at least 1
    - `grep -c "tuning.DRILL_SPEED" src/entities/player.py` returns at least 1
    - `grep -c "tuning.BOOST_FORCE" src/entities/player.py` returns at least 1
    - `grep -c "tuning.RAM_SPEED" src/entities/player.py` returns at least 1
    - `grep -c "tuning.PLAYER_MAX_HP" src/entities/player.py` returns at least 1
    - `grep -nE "\bGRAVITY\b" src/entities/player.py | grep -v "tuning\.GRAVITY" | grep -v "^[0-9]*:.*#"` returns 0 matches (no bare `GRAVITY` outside a `tuning.` prefix and outside comments)
    - `grep -c "INTGRID_CRACKED_H = 11" src/entities/player.py` returns 1 (local literal preserved)
    - `grep -c "INTGRID_CRACKED_V = 12" src/entities/player.py` returns 1 (local literal preserved)
    - `python -c "import src.entities.player"` exits 0
    - `pytest tests/test_tuning.py -q` exits 0 (compat shim still works for 12 legacy callers)
    - `pytest -q` exits 0 (the full existing suite — all 27 test files still green, including tests/test_physics.py which imports `from src.core.constants import *`)
    - The file diff shows exactly one import-block addition (`from src.core import tuning` plus `from src.core.constants import HAZARD_DRAIN_RATES`) and one deletion (`from src.core.constants import *`), plus per-call-site `tuning.` prefixes; no logic changes, no reordering, no whitespace churn beyond what Edit required
  </acceptance_criteria>
  <done>
    player.py imports `tuning` at module top, reads `tuning.X` at every per-frame physics use site, keeps the one explicit `HAZARD_DRAIN_RATES` shim import for the int-key dict, and boots cleanly under both `python -c "import src.entities.player"` and the full pytest suite. Frame-for-frame physics identity is guaranteed by construction: the refactor is a rename, not a value change.
  </done>
</task>

</tasks>

<verification>
After the task completes:
1. `pytest -q` — all existing tests pass (shim is intact for 27 test files)
2. `python -c "import src.entities.player"` — zero NameErrors
3. `grep -n "tuning\." src/entities/player.py | wc -l` — should be roughly 50+ lines (sanity check that the sweep was not silently skipped)
4. Spot-diff against HEAD: every change should be an import-line edit or a `NAME → tuning.NAME` prefix; no re-ordered code blocks
</verification>

<success_criteria>
- player.py is the only file changed in this plan
- `from src.core.constants import *` is gone from player.py
- `from src.core import tuning` is present, exactly once
- `from src.core.constants import HAZARD_DRAIN_RATES` is present, exactly once
- Every per-frame tuning key (GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, WALK_ACCEL, WALK_FRICTION, FALLING_GRAVITY_MULTIPLIER, VARIABLE_JUMP_REDUCTION, WALL_JUMP_*, WALL_SLIDE_FRICTION, COYOTE_TIME, JUMP_BUFFER, DRILL_*, CHARGE_RECOIL_FORCE, BOOST_*, RAM_*, DASH_*, SPIT_*, HOLD_TAP_THRESHOLD, PROJECTILE_SPEED, SLIME_MAX_DIST, MAX_FALL_SPEED, PLAYER_MAX_HP, INVULN_DURATION, MANA_SHIELD_COST, SHIELD_*, HAZARD_DRAIN_SLOW, HAZARD_HP_DRAIN_INTERVAL, KNOCKBACK_*, TILE_SIZE, SPRITE_SIZE) that appeared as a bare name now appears as `tuning.NAME`
- Game boots, all 27 existing tests still pass, no visible behavior change
</success_criteria>

<output>
After completion, create `.planning/phases/25-call-site-migration-constants-tuning/25-01-SUMMARY.md` with:
- The exact count of `tuning.X` references added (from grep)
- Any name collisions encountered in Step 1 (likely: none)
- The `HAZARD_DRAIN_RATES` decision confirmation
- Verification of `pytest -q` green
- A note that `tests/test_physics.py` still imports `from src.core.constants import *` — this is intentional (D-02b) and the shim covers it
</output>
