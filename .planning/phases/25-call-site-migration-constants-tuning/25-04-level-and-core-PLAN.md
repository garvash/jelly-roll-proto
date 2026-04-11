---
phase: 25
plan: 04
type: execute
wave: 2
depends_on:
  - 25-01
files_modified:
  - src/level/map.py
  - src/level/world.py
  - src/core/save_manager.py
  - src/core/sprite_utils.py
autonomous: true
requirements:
  - FND-05
must_haves:
  truths:
    - "src/level/world.py imports `from src.core import tuning` and reads `tuning.VIEWPORT_W / VIEWPORT_H`"
    - "src/level/map.py imports `from src.core import tuning` and reads `tuning.TILE_SIZE / TILE_EMPTY / VIEWPORT_W / VIEWPORT_H`"
    - "src/level/map.py still imports `HAZARD_DRAIN_RATES` from `src.core.constants` (int-key form required for IntGrid ID lookup)"
    - "src/core/save_manager.py reads `tuning.SAVE_FILE`"
    - "src/core/sprite_utils.py reads `tuning.SPRITE_SIZE / BOSS_SPRITE_SIZE`"
    - "Game boots and the full pytest suite stays green"
  artifacts:
    - path: "src/level/map.py"
      provides: "LevelMap reading tile/viewport tuning live; HAZARD_DRAIN_RATES explicitly preserved on shim"
      contains: "from src.core import tuning"
    - path: "src/level/world.py"
      provides: "World / LevelBounds reading viewport tuning live"
      contains: "from src.core import tuning"
    - path: "src/core/save_manager.py"
      provides: "SaveManager reading SAVE_FILE via tuning"
      contains: "from src.core import tuning"
    - path: "src/core/sprite_utils.py"
      provides: "draw_sprite helper reading SPRITE_SIZE/BOSS_SPRITE_SIZE via tuning"
      contains: "from src.core import tuning"
  key_links:
    - from: "src/level/map.py"
      to: "src/core/constants.py"
      via: "HAZARD_DRAIN_RATES explicit import (int-key dict, non-feel, stays on shim — per D-01 rule-of-thumb)"
      pattern: "from src\\.core\\.constants import HAZARD_DRAIN_RATES"
    - from: "src/level/map.py"
      to: "src/core/tuning.py"
      via: "tuning.TILE_SIZE and tuning.TILE_EMPTY reads at module level and per-frame draw"
      pattern: "tuning\\.(TILE_SIZE|TILE_EMPTY|VIEWPORT_)"
---

<objective>
Close out the non-entity half of Phase 25 FND-05 by migrating the four remaining files (`src/level/map.py`, `src/level/world.py`, `src/core/save_manager.py`, `src/core/sprite_utils.py`) from `src.core.constants` to use-site `tuning.X` reads. The wrinkle versus Plan 03 is `src/level/map.py`: it uses `HAZARD_DRAIN_RATES`, the non-scalar int-keyed dict with the fix-up at `constants.py:26`. Per the 25-CONTEXT "Known Constraints" note and the general D-01 rule-of-thumb ("values that don't benefit from live-tuning keep the shim import"), `map.py` explicitly keeps `HAZARD_DRAIN_RATES` on the shim.

Purpose: Finishes every file in Phase 25's 12-file target. After Plan 01 (player.py), Plan 03 (7 entities), and this plan (4 level+core files), 12/12 files will read `tuning.X` at use sites, and the only remaining `src.core.constants` references in production code will be the two deliberate `HAZARD_DRAIN_RATES` exceptions in player.py and map.py.

Output: Four source files, each with a new `from src.core import tuning` import and every previously-imported name prefixed with `tuning.` at every use site, plus the one explicit `HAZARD_DRAIN_RATES` exception in map.py.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/25-call-site-migration-constants-tuning/25-CONTEXT.md
@src/core/tuning.py
@src/core/constants.py
@src/level/map.py
@src/level/world.py
@src/core/save_manager.py
@src/core/sprite_utils.py

<interfaces>
<!-- Current import lines per file (extracted from codebase). -->

src/level/world.py line 2:
```python
from src.core.constants import VIEWPORT_W, VIEWPORT_H
```
2 names.

src/level/map.py line 2 — multi-line block across lines 2–4:
```python
from src.core.constants import (TILE_SIZE, TILE_EMPTY,
                                HAZARD_DRAIN_RATES,
                                VIEWPORT_W, VIEWPORT_H)
```
5 names TOTAL. Of these, HAZARD_DRAIN_RATES is the HAZARD exception: it is a non-scalar dict with int keys synthesised by constants.py:26, used at map.py:336 for IntGrid-ID lookup. This name MUST keep importing from `src.core.constants` in a separate explicit line. The other 4 names (TILE_SIZE, TILE_EMPTY, VIEWPORT_W, VIEWPORT_H) migrate normally.

src/core/save_manager.py line 5:
```python
from src.core.constants import SAVE_FILE
```
1 name. SAVE_FILE is a path string, read-once at save time. Per D-01 this still rewrites to `tuning.SAVE_FILE` for grep uniformity.

src/core/sprite_utils.py line 4:
```python
from src.core.constants import SPRITE_SIZE, BOSS_SPRITE_SIZE
```
2 names.

<!-- The TILES_PER_ROW derivation at src/level/map.py:9 -->
```python
TILES_PER_ROW = 256 // TILE_SIZE
```
This is a MODULE-LEVEL computation at import time. It reads TILE_SIZE exactly once when the module is first imported. Two options for handling it:
  (a) Compute it lazily: make `TILES_PER_ROW` a `@property` or helper function.
  (b) Rewrite the RHS to `tuning.TILE_SIZE` — still computed once at import, but the grep surface is uniform.
Per D-01 rule-of-thumb: module-level constants derived at import time are analogous to `__init__` captures; the value is read once, not per frame. Option (b) is the correct mechanical choice: `TILES_PER_ROW = 256 // tuning.TILE_SIZE`. This is still read-once behaviour — if the Phase 28 panel changes TILE_SIZE live, the tilemap row count wouldn't update anyway because tilemap data is baked into the pyxel image bank at load. So leaving it as a module-level capture is correct, and rewriting the RHS keeps the grep surface uniform.

<!-- The _EMPTY_8PX derivation at src/level/map.py:13 -->
```python
_EMPTY_8PX = (TILE_EMPTY[0] * 2, TILE_EMPTY[1] * 2)
```
Same treatment: module-level, read-once, rewrite RHS to `tuning.TILE_EMPTY` for grep uniformity.

<!-- HAZARD_DRAIN_RATES at map.py line 336: -->
```python
if worst is None or HAZARD_DRAIN_RATES[tile] > HAZARD_DRAIN_RATES.get(worst, 0):
```
Indexed by `tile` (an int IntGrid ID 6/7/8). MUST resolve via the int-keyed shim dict, NOT via `tuning.HAZARD_DRAIN_RATES` (which has string keys from JSON). Keep as bare name, add explicit shim import.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Migrate world.py, save_manager.py, sprite_utils.py (the three trivial files)</name>
  <files>src/level/world.py, src/core/save_manager.py, src/core/sprite_utils.py</files>
  <read_first>
    - src/level/world.py, src/core/save_manager.py, src/core/sprite_utils.py (read in full — all are under 300 LOC)
    - src/core/tuning.py (confirm flat attribute access)
    - .planning/phases/25-call-site-migration-constants-tuning/25-CONTEXT.md §D-01 and §D-03b
    - `.planning/phases/25-call-site-migration-constants-tuning/25-01-SUMMARY.md` IF IT EXISTS (confirm Plan 01 landed — Wave 2 depends on Wave 1)
  </read_first>
  <action>
Process the three trivial files with the same three-step recipe used in Plan 03.

### File 1 — src/level/world.py (294 LOC, 2 names)
- Delete line 2: `from src.core.constants import VIEWPORT_W, VIEWPORT_H`.
- Add `from src.core import tuning` in its place.
- Prefix: `VIEWPORT_W` → `tuning.VIEWPORT_W`, `VIEWPORT_H` → `tuning.VIEWPORT_H` at every use site.
- D-01 note: LevelBounds uses these as comparison/bounding constants; some may be inside `__init__` (instance capture — RHS rewrites, LHS stays). Apply uniformly.
- Verify: `python -c "import src.level.world"` exits 0.

### File 2 — src/core/save_manager.py (74 LOC, 1 name)
- Delete line 5: `from src.core.constants import SAVE_FILE`.
- Add `from src.core import tuning`.
- Prefix `SAVE_FILE` → `tuning.SAVE_FILE` at every use site. This will be inside the static `_get_save_path()` method — rewrite the constant at its use line.
- D-01 note: SAVE_FILE is a path string and fundamentally non-feel — the Phase 28 panel will never scrub it. Per the D-01 "rule of thumb", it's captured-at-use by `_get_save_path()` which is called every save, so the `tuning.SAVE_FILE` read technically becomes per-save (not per-frame). This is fine — the rewrite is consistent, not load-bearing.
- Verify: `python -c "import src.core.save_manager"` exits 0.

### File 3 — src/core/sprite_utils.py (59 LOC, 2 names)
- Delete line 4: `from src.core.constants import SPRITE_SIZE, BOSS_SPRITE_SIZE`.
- Add `from src.core import tuning`.
- Prefix: `SPRITE_SIZE` → `tuning.SPRITE_SIZE`, `BOSS_SPRITE_SIZE` → `tuning.BOSS_SPRITE_SIZE` at every use site. These are likely passed as function arguments, default values, or used inside draw calls — apply the rewrite wherever the bare name appears.
- D-01 note: if either appears as a default argument value (e.g., `def draw_sprite(..., visual_w=SPRITE_SIZE, ...)`), this is a MODULE-LOAD-TIME binding. Rewriting to `def draw_sprite(..., visual_w=tuning.SPRITE_SIZE, ...)` works because Python evaluates defaults at def-time, so it's still a one-shot read — same semantics, consistent grep surface. This is the desired D-01 treatment.
- Verify: `python -c "import src.core.sprite_utils"` exits 0.

These three files are small and independent. Commit each one separately if bisect precision matters, or bundle into a single commit. No cross-file dependencies within this task.
  </action>
  <verify>
    <automated>python -c "import src.level.world; import src.core.save_manager; import src.core.sprite_utils"</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "from src.core.constants" src/level/world.py` returns 0
    - `grep -c "from src.core.constants" src/core/save_manager.py` returns 0
    - `grep -c "from src.core.constants" src/core/sprite_utils.py` returns 0
    - `grep -c "from src.core import tuning" src/level/world.py` returns 1
    - `grep -c "from src.core import tuning" src/core/save_manager.py` returns 1
    - `grep -c "from src.core import tuning" src/core/sprite_utils.py` returns 1
    - `grep -c "tuning.VIEWPORT_W" src/level/world.py` returns at least 1
    - `grep -c "tuning.SAVE_FILE" src/core/save_manager.py` returns at least 1
    - `grep -c "tuning.SPRITE_SIZE" src/core/sprite_utils.py` returns at least 1
    - `python -c "import src.level.world; import src.core.save_manager; import src.core.sprite_utils"` exits 0
  </acceptance_criteria>
  <done>
    Three files migrated, each imports `tuning`, each import cleanly, the constants shim is no longer referenced by any of them.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Migrate map.py (the HAZARD_DRAIN_RATES special case)</name>
  <files>src/level/map.py</files>
  <read_first>
    - src/level/map.py (read in full, 503 LOC — needed to find the exact HAZARD_DRAIN_RATES use site at line ~336 and the module-level TILES_PER_ROW / _EMPTY_8PX derivations)
    - src/core/constants.py (re-read the HAZARD_DRAIN_RATES int-key fix-up block around line 26 — DO NOT MODIFY this file; just understand why map.py needs to keep importing from it)
    - src/core/tuning.py (confirm `tuning.TILE_SIZE` / `tuning.TILE_EMPTY` / `tuning.VIEWPORT_W` / `tuning.VIEWPORT_H` resolve; `tuning.HAZARD_DRAIN_RATES` resolves but has STRING keys from JSON — that's why map.py cannot use it)
    - .planning/phases/25-call-site-migration-constants-tuning/25-CONTEXT.md §D-01, §"Known Constraints" — HAZARD_DRAIN_RATES paragraph
  </read_first>
  <action>
This task handles `src/level/map.py`, which has one non-standard constraint: it uses `HAZARD_DRAIN_RATES` as an int-keyed dict (constants.py:26 fix-up). Per 25-CONTEXT's "Known Constraints" paragraph, the right answer is option (a): keep importing `HAZARD_DRAIN_RATES` from `src.core.constants` while everything else moves to `tuning.X`.

**Step 1 — Rewrite the import block.**

Current lines 2–4:
```python
from src.core.constants import (TILE_SIZE, TILE_EMPTY,
                                HAZARD_DRAIN_RATES,
                                VIEWPORT_W, VIEWPORT_H)
```

Replace with two lines:
```python
from src.core import tuning
from src.core.constants import HAZARD_DRAIN_RATES
```

The two-line form is deliberate. The first line is the Phase 25 standard `tuning` import (D-03). The second line is the ONE explicit exception in map.py — it binds the int-keyed `HAZARD_DRAIN_RATES` dict from the compat shim. This is the same pattern as player.py Plan 01 Step 3: one tuning import + one explicit HAZARD_DRAIN_RATES shim import.

Add a one-line comment above the HAZARD_DRAIN_RATES import to document WHY it bypasses the standard pattern:
```python
from src.core import tuning
# HAZARD_DRAIN_RATES stays on the compat shim: constants.py rebuilds it with
# int keys for IntGrid ID lookup (6/7/8), while tuning.HAZARD_DRAIN_RATES has
# the raw JSON string keys. See 25-CONTEXT.md "Known Constraints".
from src.core.constants import HAZARD_DRAIN_RATES
```

**Step 2 — Sweep the file for the 4 migrating names.**

For each occurrence of `TILE_SIZE`, `TILE_EMPTY`, `VIEWPORT_W`, `VIEWPORT_H`, prefix with `tuning.`. Pay special attention to the two module-level derivations:

- Line 9: `TILES_PER_ROW = 256 // TILE_SIZE` → `TILES_PER_ROW = 256 // tuning.TILE_SIZE`. This evaluates once at import time (Python module-level execution). That's exactly what we want — `TILES_PER_ROW` is used to pre-compute a pyxel image bank layout, and that layout is fixed for the session. D-01 rule-of-thumb says: module-level one-shot reads rewrite their RHS for grep uniformity.
- Line 13: `_EMPTY_8PX = (TILE_EMPTY[0] * 2, TILE_EMPTY[1] * 2)` → `_EMPTY_8PX = (tuning.TILE_EMPTY[0] * 2, tuning.TILE_EMPTY[1] * 2)`. Same treatment — read-once at module load.

For every other `TILE_SIZE` reference inside draw/query/collision methods — those ARE per-frame reads, so rewriting to `tuning.TILE_SIZE` makes them live-tuning-reachable. If the Phase 28 panel ever scrubs TILE_SIZE (unlikely; it's a grid invariant), the per-frame draw would see it, but `TILES_PER_ROW` at module level would not update. This is the documented tradeoff and matches D-01's capture-at-init pattern.

**Step 3 — LEAVE `HAZARD_DRAIN_RATES` as a bare name.**

At line ~336 the existing line is:
```python
if worst is None or HAZARD_DRAIN_RATES[tile] > HAZARD_DRAIN_RATES.get(worst, 0):
```
This STAYS as-is. `HAZARD_DRAIN_RATES` remains a bare name bound to the int-keyed dict from the explicit shim import added in Step 1. DO NOT prefix it with `tuning.` — doing so would re-bind it to the string-keyed JSON form and break IntGrid lookups (keys 6/7/8 would KeyError).

**Step 4 — Verify.**

Run `python -c "import src.level.map"` and confirm it imports cleanly. Run `pytest tests/test_destruction.py -q` if it exists (it tests hazard-zone drain behavior — verified via grep: `tests/test_destruction.py:4:from src.core.constants import TILE_EMPTY, DRILL_BLOCK_REFUND, DRILL_IMPACT_COST` — that test file stays on the shim per D-02b and should still pass). Then run `pytest -q` for the full suite.
  </action>
  <verify>
    <automated>pytest -q</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "from src.core.constants import (TILE_SIZE" src/level/map.py` returns 0 (old multi-line block removed)
    - `grep -c "from src.core import tuning" src/level/map.py` returns 1
    - `grep -c "from src.core.constants import HAZARD_DRAIN_RATES" src/level/map.py` returns 1
    - `grep -c "tuning.TILE_SIZE" src/level/map.py` returns at least 2 (module-level TILES_PER_ROW derivation + at least one per-frame use)
    - `grep -c "tuning.TILE_EMPTY" src/level/map.py` returns at least 1
    - `grep -c "tuning.VIEWPORT_W" src/level/map.py` returns at least 1
    - `grep -c "tuning.VIEWPORT_H" src/level/map.py` returns at least 1
    - `grep -nE "\bHAZARD_DRAIN_RATES\b" src/level/map.py` shows the name still appearing bare (at least twice: the explicit shim import line and the use at line ~336)
    - `grep -c "tuning.HAZARD_DRAIN_RATES" src/level/map.py` returns 0 (MUST NOT be prefixed — would break int-key lookup)
    - `python -c "import src.level.map"` exits 0
    - `pytest tests/test_tuning.py -q` exits 0 (Phase 24 regression canary, includes the `test_hazard_drain_rates_int_keys` test)
    - `pytest tests/test_tuning_livereach.py -q` exits 0 (Plan 02 livereach tests still green)
    - `pytest -q` (full suite) exits 0
  </acceptance_criteria>
  <done>
    map.py reads `tuning.TILE_SIZE / TILE_EMPTY / VIEWPORT_W / VIEWPORT_H` at every use site, explicitly imports `HAZARD_DRAIN_RATES` from the compat shim with a documenting comment, and the full pytest suite is green. The int-key IntGrid lookup at line ~336 continues to work because `HAZARD_DRAIN_RATES` still binds to the shim's rebuilt int-keyed dict.
  </done>
</task>

</tasks>

<verification>
1. `pytest -q` — full suite green across all test files
2. `grep -rn "from src.core.constants" src/` — only two lines should remain:
   - `src/entities/player.py` — `from src.core.constants import HAZARD_DRAIN_RATES`
   - `src/level/map.py` — `from src.core.constants import HAZARD_DRAIN_RATES`
   (Plus the `constants.py` file itself, which is the shim. No other production code should still hit the shim.)
3. `grep -c "from src.core import tuning" src/entities/player.py src/entities/slime.py src/entities/projectile.py src/entities/boss.py src/entities/enemies.py src/entities/effects.py src/entities/save_point.py src/entities/items.py src/level/map.py src/level/world.py src/core/save_manager.py src/core/sprite_utils.py` — should report 12 files each with 1 hit. This is the FND-05 coverage proof.
4. `python main.py` (manual smoke, optional) — game window opens to title screen without tracebacks.
</verification>

<success_criteria>
- All 4 files in this plan migrated
- `src/level/map.py` has EXACTLY two `from src.core.*` lines: `from src.core import tuning` and `from src.core.constants import HAZARD_DRAIN_RATES`
- `HAZARD_DRAIN_RATES` is still used bare at its IntGrid lookup site, not prefixed with `tuning.`
- Full pytest suite green
- Combined with Plans 01 and 03, all 12 Phase 25 target files now read `tuning.X` at use sites (FND-05 complete modulo manual regression playthrough in Plan 05)
</success_criteria>

<output>
After completion, create `.planning/phases/25-call-site-migration-constants-tuning/25-04-SUMMARY.md` noting:
- Per-file counts of `tuning.*` references added (Grep-derived)
- Explicit confirmation that map.py's HAZARD_DRAIN_RATES exception is preserved (import line + use site)
- Confirmation that `grep -rn "from src.core.constants" src/` returns exactly the two documented exceptions (player.py + map.py) plus the shim file itself
- Confirmation that all 12 Phase 25 target files have `from src.core import tuning`
- Full suite green confirmation
</output>
