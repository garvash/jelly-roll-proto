---
phase: 24
plan: 04
subsystem: compat-shim
tags: [compat-shim, constants, re-export, foundation, wildcard-import]
dependency_graph:
  requires:
    - "24-02 (assets/physics-schema.json v0.3.0 with tuning.* + derived.*)"
    - "24-03 (src/core/tuning.py loader exposing flat __all__)"
  provides:
    - "src/core/constants.py as a passthrough compat shim (FND-03)"
    - "Legacy `from src.core.constants import X` path preserved for 12 callers"
  affects:
    - "src/core/constants.py (reduced 156 -> 26 lines)"
tech_stack:
  added: []
  patterns:
    - "Wildcard re-export (`from src.core.tuning import *`) picking up `tuning.__all__` automatically"
    - "Post-import shim to re-cast non-scalar leaf keys (HAZARD_DRAIN_RATES int-key fix-up)"
key_files:
  created: []
  modified:
    - "src/core/constants.py"
decisions:
  - "Shim defers to tuning.__all__ rather than hardcoding a name list (D-16) — new leaves added to tuning flow through without editing constants.py"
  - "Only HAZARD_DRAIN_RATES needs a shim fix-up; all other non-scalar leaves (TILE_EMPTY list, RAM_INVINCIBLE bool, SAVE_FILE str) survive the wildcard re-export unchanged"
  - "D-17 limitation (import-site readers don't see runtime mutations) is accepted, not worked around — Phase 25 owns that migration"
metrics:
  duration_seconds: 68
  completed: 2026-04-11
  tasks: 1
  files_changed: 1
requirements_completed:
  - FND-03
---

# Phase 24 Plan 04: Compat Shim Summary

**One-liner:** Rewrote `src/core/constants.py` from a 156-line constant definition file into a 26-line passthrough shim that re-exports every flat leaf from `src.core.tuning` via a wildcard import, with a single post-import fix-up rebuilding `HAZARD_DRAIN_RATES` with integer keys after JSON round-tripping stringifies them.

## What Changed

### src/core/constants.py (Task 1) — 156 lines -> 26 lines

**Shape after rewrite (verbatim per plan §interfaces):**

```python
"""Compat shim for Phase 24 source-of-truth inversion.

The authoritative home for every named constant in this module is now
`src/core/tuning.py`, which reads `assets/physics-schema.json` at import time.
...
Known limitation (Phase 24, D-17): legacy `from` imports bind a local name
at module-import time, so `set_value('GRAVITY', 0.09)` will NOT be visible
to a caller that already imported `GRAVITY`.
"""

from src.core.tuning import *  # noqa: F401,F403 — intentional wildcard re-export
from src.core import tuning as _tuning

# Non-scalar leaf fix-up: JSON serializes HAZARD_DRAIN_RATES's int keys as strings.
HAZARD_DRAIN_RATES = {int(k): v for k, v in _tuning.HAZARD_DRAIN_RATES.items()}
```

**How D-16 is honoured:** the shim does not list names. `tuning.py` builds `__all__` at `load()` time from `sorted(_flat_index.keys())` (the 87 flat leaves produced by the schema). The shim's `from src.core.tuning import *` therefore picks up the full set implicitly — if a future plan adds a new leaf to `physics-schema.json`, it flows through to `src.core.constants` without touching this file.

**Why HAZARD_DRAIN_RATES needs a shim:** in the old `constants.py`, this dict was authored with int keys `{6: 0.25, 7: 0.75, 8: 1.5}`. After being moved into `physics-schema.json` in Plan 02, JSON serialisation stringifies those keys to `"6"`, `"7"`, `"8"`. Legacy callers index with int IntGrid IDs (6/7/8), so the shim rebuilds the dict with int keys. Per D-15 (name uniqueness) the wildcard re-export still binds the original string-keyed dict into the shim's namespace first; the explicit assignment on line 26 then shadows it with the int-keyed version — so `from src.core.constants import HAZARD_DRAIN_RATES` yields the int-keyed dict.

**Why no other non-scalar fix-ups were needed:**
- `TILE_EMPTY` — JSON round-trips as `[15, 15]` (list). Callers iterate it (`a, b = TILE_EMPTY`), no tuple-specific behaviour depended on.
- `RAM_INVINCIBLE` — `true` in JSON is Python `True`, identity-compared with `is True` in the plan's acceptance test and it passes.
- `SAVE_FILE` — plain string, passes through.

## Tasks Completed

| Task | Name                                              | Commit  | Files                  |
| ---- | ------------------------------------------------- | ------- | ---------------------- |
| 1    | Rewrite src/core/constants.py as a compat shim    | 19b4f56 | src/core/constants.py  |

## Verification

All plan acceptance criteria executed in-session:

```
test -f src/core/constants.py                                              OK
wc -l src/core/constants.py (26 < 40)                                      OK
grep "^from src.core.tuning import \*"                                     OK
grep "from src.core import tuning as _tuning"                              OK
grep "HAZARD_DRAIN_RATES = {int(k)"                                        OK
from src.core.constants import GRAVITY; GRAVITY == 0.0875                  OK
from src.core.constants import JUMP_FORCE; JUMP_FORCE == -3.25             OK
from src.core.constants import MAX_WALK_SPEED; MAX_WALK_SPEED == 1.25      OK
HAZARD_DRAIN_RATES[6]==0.25, [7]==0.75, [8]==1.5 (int keys)                OK
from src.core.constants import RAM_INVINCIBLE; is True                     OK
from src.core.constants import SAVE_FILE; == 'save.json'                   OK
from src.core.constants import TILE_EMPTY; == [15,15]                      OK
import 12 legacy callers (boss,slime,enemies,effects,player,save_point,    OK
  items,projectile,map,world,save_manager,sprite_utils)
grep for scalar redefinitions (WALK_ACCEL|GRAVITY|JUMP_FORCE|              OK (0 matches)
  RAM_SPEED|CHARGE_SHOT_DAMAGE) == 0
```

**Plan-level "smoke test" line:**

```
python -c "from src.core.constants import GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, \
  HAZARD_DRAIN_RATES, RAM_INVINCIBLE, SAVE_FILE, TILE_EMPTY; \
  assert GRAVITY==0.0875; assert JUMP_FORCE==-3.25; assert MAX_WALK_SPEED==1.25; \
  assert HAZARD_DRAIN_RATES[6]==0.25; assert HAZARD_DRAIN_RATES[7]==0.75; \
  assert HAZARD_DRAIN_RATES[8]==1.5; assert RAM_INVINCIBLE is True; \
  assert SAVE_FILE=='save.json'; assert TILE_EMPTY==[15,15]; print('ok')"
```

Output: `ok`. All seven asserts pass in a single interpreter instance, confirming that wildcard re-export + single-line HAZARD_DRAIN_RATES fix-up is sufficient for the full non-scalar surface the legacy callers touch.

**12 legacy caller smoke test (T-24-14 mitigation verification):**

```
python -c "import src.entities.boss, src.entities.slime, src.entities.enemies, \
  src.entities.effects, src.entities.player, src.entities.save_point, \
  src.entities.items, src.entities.projectile, src.level.map, src.level.world, \
  src.core.save_manager, src.core.sprite_utils"
```

Exit 0. Every `from src.core.constants import ...` statement in those 12 files resolved through the shim without raising.

## Deviations from Plan

None. The plan gave the exact file contents to write; they were copied verbatim. No Rule 1 bugs, no Rule 2 missing functionality, no Rule 3 blockers, no Rule 4 architectural escalations.

## Auth Gates Hit

None.

## Deferred Issues

None.

## Known Stubs

None. The shim is fully wired — every leaf flows through to `tuning._model` at read time via the module-level `__getattr__` defined in `tuning.py`. The D-17 import-site staleness is **not** a stub: it is an accepted, documented limitation that Phase 25 resolves by migrating the 12 callers to use-site reads. Phase 24's acceptance explicitly excludes live mutation reaching legacy callers, so this is not a gap in the delivered work.

## Threat Flags

None introduced. All threat-model mitigations from the plan's `<threat_model>` are implemented:

- **T-24-14** (wildcard leaking non-constants) — `tuning.__all__` is built from `_flat_index.keys()`, which are the UPPER_SNAKE_CASE leaves under `tuning.*`. No private helpers, no functions, no module-level sentinels leak through the wildcard. Verified by the 12-caller smoke test (if anything non-constant had leaked, name collisions or unexpected callables would surface).
- **T-24-15** (HAZARD_DRAIN_RATES int/string key drift) — explicit `{int(k): v for k, v in _tuning.HAZARD_DRAIN_RATES.items()}` rebuild at shim-import time, verified by `HAZARD_DRAIN_RATES[6]==0.25` (int-indexed).
- **T-24-16** (circular import) — accepted; `tuning.py` never imports from `constants.py` (verified by reading `src/core/tuning.py`, whose only imports are `copy`, `json`, `os`, `pathlib`). The dependency is strictly `constants -> tuning`.
- **T-24-17** (Phase 25 inheriting import-site staleness) — accepted per D-17; documented in the shim's module docstring.

## Self-Check: PASSED

- `src/core/constants.py` — present, 26 lines, imports cleanly, wildcard re-export statement present, `_tuning` alias present, `HAZARD_DRAIN_RATES = {int(k)` fix-up present
- Commit `19b4f56` — found in `git log --oneline` (`feat(24-04): rewrite constants.py as tuning passthrough shim`)
- `.planning/phases/24-tuning-foundation-schema-inversion/24-04-compat-shim-SUMMARY.md` — this file, present
- Worktree rebased to `c9ec506` (per worktree_branch_check) before any edits — verified via `git reset --hard` output and subsequent `git log --oneline`
- `git status --short` after Task 1 commit was clean (no stray untracked files, no unintended modifications)
- All 13 acceptance criteria from plan executed and passed
