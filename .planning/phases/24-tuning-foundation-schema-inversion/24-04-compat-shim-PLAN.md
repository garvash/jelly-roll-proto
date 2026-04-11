---
phase: 24-tuning-foundation-schema-inversion
plan: 04
type: execute
wave: 3
depends_on: [24-02, 24-03]
files_modified:
  - src/core/constants.py
autonomous: true
requirements:
  - FND-03
tags: [compat-shim, constants, re-export]
must_haves:
  truths:
    - "src/core/constants.py is a passthrough shim re-exporting every name from src.core.tuning"
    - "`from src.core.constants import GRAVITY` returns 0.0875 at import time"
    - "All 12 legacy callers (boss.py, slime.py, enemies.py, effects.py, player.py, save_point.py, items.py, projectile.py, map.py, world.py, save_manager.py, sprite_utils.py) still import cleanly"
    - "Non-scalar leaves (HAZARD_DRAIN_RATES, TILE_EMPTY) survive the re-export with correct Python types"
    - "Known limitation (D-17): legacy import-site readers will NOT see runtime set_value() mutations until Phase 25 migrates them — this is expected and acceptable for Phase 24"
  artifacts:
    - path: "src/core/constants.py"
      provides: "compat shim re-exporting src.core.tuning flat namespace"
      contains: "from src.core.tuning import"
  key_links:
    - from: "src/core/constants.py"
      to: "src/core/tuning.py"
      via: "from src.core.tuning import * (picks up __all__)"
      pattern: "from src\\.core\\.tuning import \\*"
    - from: "src/core/constants.py HAZARD_DRAIN_RATES"
      to: "src/core/tuning.py _model['hazards']['HAZARD_DRAIN_RATES']"
      via: "dict re-cast with int keys (post-import shim)"
      pattern: "HAZARD_DRAIN_RATES"
---

<objective>
Rewrite `src/core/constants.py` as a passthrough compat shim so the 12 legacy callers that do `from src.core.constants import X` keep working unchanged after the source-of-truth flip.

Purpose: This is FND-03. Phase 25 will migrate each of the 12 callers from import-site to use-site reads (so hot-tuning via the Phase 28 panel actually reaches entity behavior). Phase 24 only needs the imports to not crash and return v1.3 baseline values at boot. D-17 explicitly accepts that legacy callers will not see live mutations until Phase 25.

Output: `src/core/constants.py` reduced from 156 lines to a minimal shim (under ~30 lines) that re-exports every `tuning.*` flat name, plus a hand-maintained fix-up for the non-scalar dict `HAZARD_DRAIN_RATES` (JSON serialises int keys as strings; Python callers expect int keys).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@src/core/constants.py
@src/core/tuning.py
@.planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md

<interfaces>
<!-- The shim is a single-purpose passthrough. Legacy imports must still work. -->

Target file: src/core/constants.py

Shape after rewrite:

    """Compat shim for Phase 24 source-of-truth inversion.

    The authoritative home for every named constant in this module is now
    `src/core/tuning.py`, which reads `assets/physics-schema.json` at import time.
    This file exists only so that legacy call sites doing

        from src.core.constants import GRAVITY

    keep working without touching every caller in this phase. Phase 25 will
    migrate callers to read `tuning.GRAVITY` at use time so that live-tuning
    panel edits (Phase 28) reach their behavior in real time.

    Known limitation (Phase 24, D-17): legacy `from` imports bind a local name
    at module-import time, so `set_value('GRAVITY', 0.09)` will NOT be visible
    to a caller that already imported `GRAVITY`. That is the exact problem
    Phase 25 exists to solve; do not try to work around it here.
    """

    from src.core.tuning import *  # noqa: F401,F403 — intentional wildcard re-export
    from src.core import tuning as _tuning

    # Non-scalar leaf fix-up: JSON serializes HAZARD_DRAIN_RATES's int keys as strings.
    # Legacy callers index this dict with int IntGrid IDs (6/7/8), so we rebuild it
    # with int keys here. The re-export above pulls in the string-keyed original; we
    # shadow it with the int-keyed version.
    HAZARD_DRAIN_RATES = {int(k): v for k, v in _tuning.HAZARD_DRAIN_RATES.items()}

That's it. ~5 code lines + docstring. No other statements, no re-definitions of scalars,
no conditional imports.

Why wildcard import is safe here:
  - src/core/tuning.py defines __all__ at load() time as sorted(_flat_index.keys())
  - Every name in __all__ is an UPPER_SNAKE_CASE constant — no name collision with any
    Python builtin, no underscored implementation detail leaks out
  - The shim is the only place in the codebase using a wildcard import; all 12 legacy
    callers use named imports (`from src.core.constants import GRAVITY, JUMP_FORCE`)
    and those work through the wildcard re-export exactly as before

The 12 legacy caller files that MUST still import cleanly after this plan (they are
NOT modified — Phase 25 owns that migration):
  - src/entities/boss.py
  - src/entities/slime.py
  - src/entities/enemies.py
  - src/entities/effects.py
  - src/entities/player.py
  - src/entities/save_point.py
  - src/entities/items.py
  - src/entities/projectile.py
  - src/level/map.py
  - src/level/world.py
  - src/core/save_manager.py
  - src/core/sprite_utils.py
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Rewrite src/core/constants.py as a compat shim</name>
  <files>src/core/constants.py</files>
  <read_first>
    - src/core/constants.py (current 156-line file — you're replacing it entirely)
    - src/core/tuning.py (so you can confirm __all__ contains every flat name you're about to re-export)
    - .planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md (§decisions D-16, D-17)
  </read_first>
  <action>
    Overwrite `src/core/constants.py` with the shim shape given in <interfaces>. Use the Write tool.

    Exact file contents (copy verbatim, including the docstring):

        """Compat shim for Phase 24 source-of-truth inversion.

        The authoritative home for every named constant in this module is now
        `src/core/tuning.py`, which reads `assets/physics-schema.json` at import time.
        This file exists only so that legacy call sites doing

            from src.core.constants import GRAVITY

        keep working without touching every caller in this phase. Phase 25 will
        migrate callers to read `tuning.GRAVITY` at use time so that live-tuning
        panel edits (Phase 28) reach their behavior in real time.

        Known limitation (Phase 24, D-17): legacy `from` imports bind a local name
        at module-import time, so `set_value('GRAVITY', 0.09)` will NOT be visible
        to a caller that already imported `GRAVITY`. That is the exact problem
        Phase 25 exists to solve; do not try to work around it here.
        """

        from src.core.tuning import *  # noqa: F401,F403 — intentional wildcard re-export
        from src.core import tuning as _tuning

        # Non-scalar leaf fix-up: JSON serializes HAZARD_DRAIN_RATES's int keys as strings.
        # Legacy callers index this dict with int IntGrid IDs (6/7/8), so we rebuild it
        # with int keys here. The re-export above pulls in the string-keyed original; we
        # shadow it with the int-keyed version.
        HAZARD_DRAIN_RATES = {int(k): v for k, v in _tuning.HAZARD_DRAIN_RATES.items()}

    The entire file is the docstring + 3 statements. ~32 lines total.

    Do NOT:
    - keep any of the old 156 lines (no redefinitions of scalars; they all come in via the wildcard)
    - add shims for TILE_EMPTY (it's a 2-element list; Pyxel callers just iterate it and don't care about tuple-vs-list)
    - add shims for RAM_INVINCIBLE (it's a bool; Python handles that through the wildcard)
    - add shims for SAVE_FILE (it's a string)
    - import anything beyond `from src.core.tuning import *` and `from src.core import tuning as _tuning`
    - add conditional logic, try/except, or fallback paths
    - touch any other file

    Special note on HAZARD_DRAIN_RATES: in constants.py today this dict is
        HAZARD_DRAIN_RATES = {6: HAZARD_DRAIN_SLOW, 7: HAZARD_DRAIN_MEDIUM, 8: HAZARD_DRAIN_FAST}
    with int keys. After round-tripping through JSON (Plan 02 writes it as `{"6": 0.25, "7": 0.75, "8": 1.5}`),
    the keys come back as strings. The dict-comprehension shim above restores the int keys. This is the
    single known impedance mismatch for Phase 24; all other leaves pass through unchanged. If Plan 05's
    legacy-caller smoke test fails on an int-key lookup into HAZARD_DRAIN_RATES, this shim is why it shouldn't.
  </action>
  <verify>
    <automated>python -c "from src.core.constants import GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, HAZARD_DRAIN_RATES, RAM_INVINCIBLE, SAVE_FILE, TILE_EMPTY; assert GRAVITY==0.0875; assert JUMP_FORCE==-3.25; assert MAX_WALK_SPEED==1.25; assert HAZARD_DRAIN_RATES[6]==0.25; assert HAZARD_DRAIN_RATES[7]==0.75; assert HAZARD_DRAIN_RATES[8]==1.5; assert RAM_INVINCIBLE is True; assert SAVE_FILE=='save.json'; assert TILE_EMPTY==[15,15]; print('ok')"</automated>
  </verify>
  <acceptance_criteria>
    - `test -f src/core/constants.py` exits 0
    - `wc -l src/core/constants.py` reports fewer than 40 lines (compat shim, not 156-line redefinition)
    - `grep -q "^from src.core.tuning import \*" src/core/constants.py` exits 0
    - `grep -q "from src.core import tuning as _tuning" src/core/constants.py` exits 0
    - `grep -q "HAZARD_DRAIN_RATES = {int(k)" src/core/constants.py` exits 0 (int-key fix-up present)
    - `python -c "from src.core.constants import GRAVITY; assert GRAVITY==0.0875"` exits 0
    - `python -c "from src.core.constants import JUMP_FORCE; assert JUMP_FORCE==-3.25"` exits 0
    - `python -c "from src.core.constants import HAZARD_DRAIN_RATES; assert HAZARD_DRAIN_RATES[6]==0.25 and HAZARD_DRAIN_RATES[7]==0.75 and HAZARD_DRAIN_RATES[8]==1.5"` exits 0
    - `python -c "from src.core.constants import RAM_INVINCIBLE; assert RAM_INVINCIBLE is True"` exits 0
    - `python -c "from src.core.constants import SAVE_FILE; assert SAVE_FILE=='save.json'"` exits 0
    - `python -c "from src.core.constants import TILE_EMPTY; assert TILE_EMPTY==[15,15]"` exits 0
    - `python -c "import src.entities.boss, src.entities.slime, src.entities.enemies, src.entities.effects, src.entities.player, src.entities.save_point, src.entities.items, src.entities.projectile, src.level.map, src.level.world, src.core.save_manager, src.core.sprite_utils"` exits 0 (all 12 legacy callers still import)
    - `grep -cE "^(WALK_ACCEL|GRAVITY|JUMP_FORCE|RAM_SPEED|CHARGE_SHOT_DAMAGE)\s*=" src/core/constants.py` reports 0 (no redefinitions of scalars; they all come via the wildcard)
  </acceptance_criteria>
  <done>src/core/constants.py is under 40 lines, consists only of the docstring + wildcard import + tuning alias + HAZARD_DRAIN_RATES int-key shim; every scalar constant flows in through `from src.core.tuning import *`; all 12 legacy callers still import successfully; HAZARD_DRAIN_RATES behaves as an int-keyed dict; RAM_INVINCIBLE is bool True; TILE_EMPTY is [15,15]; SAVE_FILE is 'save.json'.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| legacy caller → shim → loader | Every `from src.core.constants import X` crosses this chain |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-24-14 | Tampering | wildcard import leaking non-constants | mitigate | tuning.__all__ is explicitly built from _flat_index.keys(), which is the set of UPPER_SNAKE_CASE leaves from the schema. No private helpers, no functions, no nothing else gets exposed via `*`. |
| T-24-15 | Tampering | HAZARD_DRAIN_RATES int/string key drift | mitigate | Explicit int-key rebuild in the shim closes the JSON-serialization impedance mismatch; Plan 05 legacy-caller smoke test will exercise this lookup against integer IntGrid IDs 6/7/8 |
| T-24-16 | Denial of Service | circular import between constants.py and tuning.py | accept | tuning.py never imports from constants.py (verified by Plan 03 task instructions); the dependency is strictly constants → tuning, no cycle possible |
| T-24-17 | Repudiation | Phase 25 inheriting silent import-site staleness | accept | D-17 explicitly documents that legacy callers will not see runtime set_value mutations in Phase 24. That's the entire reason Phase 25 exists. Panel UI isn't shipped until Phase 28, so the window where this could bite is empty. |
</threat_model>

<verification>
- `python -c "import src.core.constants"` exits 0
- All 12 legacy callers importable
- File is under 40 lines (compat shim shape)
- Wildcard import + tuning alias + HAZARD_DRAIN_RATES fix-up are the only substantive statements
</verification>

<success_criteria>
- constants.py is a minimal shim (<40 lines)
- Every named constant reachable through the old import path
- Non-scalar edge cases (HAZARD_DRAIN_RATES int keys, RAM_INVINCIBLE bool, TILE_EMPTY list) behave correctly
- All 12 legacy callers still load
- D-17 limitation accepted, not worked around
</success_criteria>

<output>
After completion, create `.planning/phases/24-tuning-foundation-schema-inversion/24-04-SUMMARY.md`
</output>
