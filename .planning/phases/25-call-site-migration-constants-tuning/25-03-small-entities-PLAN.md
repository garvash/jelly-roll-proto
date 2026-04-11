---
phase: 25
plan: 03
type: execute
wave: 2
depends_on:
  - 25-01
files_modified:
  - src/entities/slime.py
  - src/entities/projectile.py
  - src/entities/boss.py
  - src/entities/enemies.py
  - src/entities/effects.py
  - src/entities/save_point.py
  - src/entities/items.py
autonomous: true
requirements:
  - FND-05
must_haves:
  truths:
    - "None of the 7 entity files in this plan have a `from src.core.constants import` line anymore"
    - "All 7 files have `from src.core import tuning` as the single replacement import"
    - "Every per-frame read in slime.update() / projectile.update() / boss.BossRock.update() / enemies.update() resolves via `tuning.*`"
    - "Game boots and the full pytest suite stays green"
  artifacts:
    - path: "src/entities/slime.py"
      provides: "Slime entity with live tuning reads"
      contains: "from src.core import tuning"
    - path: "src/entities/projectile.py"
      provides: "Projectile entity with live tuning reads"
      contains: "from src.core import tuning"
    - path: "src/entities/boss.py"
      provides: "BossRock entity with live tuning reads"
      contains: "from src.core import tuning"
    - path: "src/entities/enemies.py"
      provides: "Enemy entity with live tuning reads"
      contains: "from src.core import tuning"
    - path: "src/entities/effects.py"
      provides: "Effect/Particle entities with live tuning reads"
      contains: "from src.core import tuning"
    - path: "src/entities/save_point.py"
      provides: "SavePoint entity with live tuning reads"
      contains: "from src.core import tuning"
    - path: "src/entities/items.py"
      provides: "Item entity with live tuning reads"
      contains: "from src.core import tuning"
  key_links:
    - from: "src/entities/slime.py"
      to: "src/core/tuning.py"
      via: "tuning.SLIME_FOLLOW_DELAY / SLIME_MAX_DIST / SLIME_LERP_FACTOR / JUICE_* reads inside update()/follow()"
      pattern: "tuning\\.SLIME_"
    - from: "src/entities/projectile.py"
      to: "src/core/tuning.py"
      via: "tuning.PROJECTILE_SPEED / CHARGE_SHOT_* / CULL_MARGIN / SPRITE_SIZE / TILE_SIZE / VIEWPORT_* reads"
      pattern: "tuning\\.(PROJECTILE_SPEED|CHARGE_SHOT)"
---

<objective>
Migrate the seven "small" entity files off `src.core.constants` and onto use-site `tuning.X` reads. These are the mechanical copy-paste targets that become trivial once Plan 01 has sorted player.py: each file has an explicit `from src.core.constants import (...)` line, not a wildcard, so the rewrite is surgical — delete the old import, add `from src.core import tuning`, prefix each previously-listed name at its call sites.

Purpose: Closes the entity half of Phase 25 requirement FND-05. No new logic; the target is frame-for-frame parity with pre-migration builds by construction (the refactor is a rename).

Output: Seven source files, each with one `from src.core import tuning` import and every previously-imported constant prefixed with `tuning.` at every use site.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/25-call-site-migration-constants-tuning/25-CONTEXT.md
@src/core/tuning.py
@src/entities/slime.py
@src/entities/projectile.py
@src/entities/boss.py
@src/entities/enemies.py
@src/entities/effects.py
@src/entities/save_point.py
@src/entities/items.py

<interfaces>
<!-- Current import lines per file (extracted from codebase). Replace each
     with `from src.core import tuning` and prefix the listed names at use
     sites. -->

src/entities/slime.py line 4 — multi-line block:
```python
from src.core.constants import (
    SLIME_FOLLOW_DELAY,
    SLIME_MAX_DIST,
    SLIME_REFORM_DIST,
    SLIME_LERP_FACTOR,
    JUICE_MAX,
    JUICE_REGEN_RATE,
    JUICE_MIN_SCALE,
    SLIME_SPIT_COST,
    RECALL_SPEED,
    RECALL_OVERLAP_DIST,
    SLIME_DISSIPATE_COOLDOWN,
    RECALL_TRAIL_COLOR,
    HOLD_TAP_THRESHOLD,
    TILE_SIZE,
    SPRITE_SIZE,
)
```
15 names to prefix with `tuning.` at use sites.

src/entities/projectile.py line 2:
```python
from src.core.constants import PROJECTILE_SPEED, TILE_SIZE, CHARGE_SHOT_SPEED, CHARGE_SHOT_SIZE, CHARGE_SHOT_DAMAGE, VIEWPORT_W, VIEWPORT_H, CULL_MARGIN, SPRITE_SIZE
```
9 names.

src/entities/boss.py line 4:
```python
from src.core.constants import TILE_SIZE, BOSS_ROCK_SPEED, VIEWPORT_W, VIEWPORT_H, CULL_MARGIN, SPRITE_SIZE, BOSS_SPRITE_SIZE
```
7 names.

src/entities/enemies.py line 2:
```python
from src.core.constants import TILE_SIZE, SPRITE_SIZE
```
2 names.

src/entities/effects.py line 3:
```python
from src.core.constants import VIEWPORT_W, VIEWPORT_H, SPRITE_SIZE
```
3 names.

src/entities/save_point.py line 3:
```python
from src.core.constants import SAVE_PULSE_CYCLE, SAVE_PULSE_HALF, SAVE_PROMPT_DURATION
```
3 names.

src/entities/items.py line 2:
```python
from src.core.constants import SPRITE_SIZE, MAX_HP_CAP, MAX_JUICE_CAP
```
3 names.

<!-- Total across the 7 files: ~42 unique names to prefix. Use Grep + Edit
     (`replace_all: true` where safe) per file. -->

<!-- IMPORTANT: none of these 7 files use HAZARD_DRAIN_RATES. The int-key
     fix-up exception applies ONLY to player.py (Plan 01) and map.py
     (Plan 04). This plan has no HAZARD_DRAIN_RATES carve-outs. -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Migrate slime.py, projectile.py, boss.py, enemies.py, effects.py, save_point.py, items.py</name>
  <files>src/entities/slime.py, src/entities/projectile.py, src/entities/boss.py, src/entities/enemies.py, src/entities/effects.py, src/entities/save_point.py, src/entities/items.py</files>
  <read_first>
    - src/entities/slime.py, src/entities/projectile.py, src/entities/boss.py, src/entities/enemies.py, src/entities/effects.py, src/entities/save_point.py, src/entities/items.py (read each in full before editing — several are short; none exceed 360 LOC)
    - src/core/tuning.py (confirm PEP 562 access pattern)
    - .planning/phases/25-call-site-migration-constants-tuning/25-CONTEXT.md §D-01, §D-03, §D-03b
    - `.planning/phases/25-call-site-migration-constants-tuning/25-01-SUMMARY.md` IF IT EXISTS (confirm Plan 01 landed; if not, stop and escalate — Wave 2 depends on Wave 1)
  </read_first>
  <action>
Process the seven files in the order listed below (smallest first keeps early commits low-risk and verifiable). For each file, apply the same three-step recipe.

**Per-file recipe (identical for all 7 files):**

1. **Delete the explicit `from src.core.constants import ...` line** (single-line or multi-line block). Per 25-CONTEXT D-03 / D-03b, this line is deleted, not commented-out.

2. **Insert `from src.core import tuning`** in the same position in the import block. Keep the rest of the import block (pyxel, draw_sprite, debug, etc.) untouched.

3. **Sweep the file, prefixing every bare name that was previously imported.** Use the Grep tool to find each bare name in the file; use Edit with `replace_all: true` per name ONLY after confirming the name does not appear as a substring of another identifier in the file (e.g., `SPRITE_SIZE` is fine everywhere; `TILE_SIZE` is fine; `DISPLAY_SIZE` if it existed would need a boundary-matched replace). For each name, the transformation is literal:
   - `NAME` → `tuning.NAME`
   - `self.foo = NAME` → `self.foo = tuning.NAME` (D-01: `__init__` RHS still rewrites for grep uniformity even though it's captured)
   - `NAME * 2` → `tuning.NAME * 2`
   - `min(x, NAME)` → `min(x, tuning.NAME)`

**Per-file specifics:**

### File 1 — src/entities/enemies.py (smallest, 144 LOC, 2 names)
- Delete line 2 (`from src.core.constants import TILE_SIZE, SPRITE_SIZE`).
- Add `from src.core import tuning` in its place.
- Prefix `TILE_SIZE` → `tuning.TILE_SIZE` and `SPRITE_SIZE` → `tuning.SPRITE_SIZE` at every use site.
- Verify: `python -c "import src.entities.enemies"` exits 0.

### File 2 — src/entities/effects.py (62 LOC, 3 names)
- Delete line 3 (`from src.core.constants import VIEWPORT_W, VIEWPORT_H, SPRITE_SIZE`).
- Add `from src.core import tuning`.
- Prefix `VIEWPORT_W`, `VIEWPORT_H`, `SPRITE_SIZE`.
- Verify import.

### File 3 — src/entities/save_point.py (63 LOC, 3 names)
- Delete line 3 (`from src.core.constants import SAVE_PULSE_CYCLE, SAVE_PULSE_HALF, SAVE_PROMPT_DURATION`).
- Add `from src.core import tuning`.
- Prefix `SAVE_PULSE_CYCLE`, `SAVE_PULSE_HALF`, `SAVE_PROMPT_DURATION`.
- Note: SAVE_PROMPT_DURATION is a frame count used in the per-frame draw/update path — live-tuning-reachable. The other two are pulse-cycle dividers used inline. All three become live reads.
- Verify import.

### File 4 — src/entities/items.py (62 LOC, 3 names)
- Delete line 2 (`from src.core.constants import SPRITE_SIZE, MAX_HP_CAP, MAX_JUICE_CAP`).
- Add `from src.core import tuning`.
- Prefix `SPRITE_SIZE`, `MAX_HP_CAP`, `MAX_JUICE_CAP`.
- Note: MAX_HP_CAP and MAX_JUICE_CAP might appear in item pickup logic (`if player.hp < MAX_HP_CAP: ...`). These are upper-bound guards, arguably per-frame-ish. Per D-01 they become live reads regardless.
- Verify import.

### File 5 — src/entities/boss.py (173 LOC, 7 names)
- Delete line 4 (`from src.core.constants import TILE_SIZE, BOSS_ROCK_SPEED, VIEWPORT_W, VIEWPORT_H, CULL_MARGIN, SPRITE_SIZE, BOSS_SPRITE_SIZE`).
- Add `from src.core import tuning`.
- Prefix: TILE_SIZE, BOSS_ROCK_SPEED, VIEWPORT_W, VIEWPORT_H, CULL_MARGIN, SPRITE_SIZE, BOSS_SPRITE_SIZE.
- D-01 note: BossRock `__init__` has `self.dx = dx * BOSS_ROCK_SPEED`. This is an `__init__` capture — LHS stays, RHS becomes `tuning.BOSS_ROCK_SPEED`. The dx is then read per-frame but that's the post-capture value (correct per D-01: instance state captured at spawn).
- Verify import.

### File 6 — src/entities/projectile.py (104 LOC, 9 names)
- Delete line 2.
- Add `from src.core import tuning`.
- Prefix: PROJECTILE_SPEED, TILE_SIZE, CHARGE_SHOT_SPEED, CHARGE_SHOT_SIZE, CHARGE_SHOT_DAMAGE, VIEWPORT_W, VIEWPORT_H, CULL_MARGIN, SPRITE_SIZE.
- D-01 note: `__init__` has `self.dx = dx * PROJECTILE_SPEED`. Same capture rule as boss.py. LHS stays; RHS becomes `tuning.PROJECTILE_SPEED`.
- Verify import.

### File 7 — src/entities/slime.py (360 LOC, 15 names — the biggest in this plan)
- Delete the multi-line block at lines 4–20.
- Add `from src.core import tuning` in its place (single line).
- Prefix all 15 names at every use site: SLIME_FOLLOW_DELAY, SLIME_MAX_DIST, SLIME_REFORM_DIST, SLIME_LERP_FACTOR, JUICE_MAX, JUICE_REGEN_RATE, JUICE_MIN_SCALE, SLIME_SPIT_COST, RECALL_SPEED, RECALL_OVERLAP_DIST, SLIME_DISSIPATE_COOLDOWN, RECALL_TRAIL_COLOR, HOLD_TAP_THRESHOLD, TILE_SIZE, SPRITE_SIZE.
- Slime has the most per-frame tuning reads in this plan — Slime.update() iterates follow/recall/dissipate logic every frame. Most names become live reads. A few (e.g., JUICE_MAX as a cap on regen) may be inside `__init__` captures; apply the D-01 rule uniformly.
- Verify import.

**After all 7 files are migrated, run the verification pipeline:**

1. `python -c "import src.entities.slime; import src.entities.projectile; import src.entities.boss; import src.entities.enemies; import src.entities.effects; import src.entities.save_point; import src.entities.items"` — all seven must import cleanly.
2. `python -c "import src.entities.player"` — player.py (Plan 01) must still work; this is a regression canary.
3. `pytest -q` — full suite green.

**Commit strategy (planner's discretion — D-02a of 25-CONTEXT allows bundling):** Recommended to commit each file individually so bisect is precise if frame-for-frame drift is later caught by the manual playthrough (Plan 25-05). Seven commits, each of the form `refactor(25-03): migrate <file> to use-site tuning reads`. If executor prefers a single commit for the whole plan, that is acceptable per D-02a; the acceptance criteria only require the end state to be correct.
  </action>
  <verify>
    <automated>pytest -q</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "from src.core.constants" src/entities/slime.py` returns 0
    - `grep -c "from src.core.constants" src/entities/projectile.py` returns 0
    - `grep -c "from src.core.constants" src/entities/boss.py` returns 0
    - `grep -c "from src.core.constants" src/entities/enemies.py` returns 0
    - `grep -c "from src.core.constants" src/entities/effects.py` returns 0
    - `grep -c "from src.core.constants" src/entities/save_point.py` returns 0
    - `grep -c "from src.core.constants" src/entities/items.py` returns 0
    - `grep -c "from src.core import tuning" src/entities/slime.py` returns 1
    - `grep -c "from src.core import tuning" src/entities/projectile.py` returns 1
    - `grep -c "from src.core import tuning" src/entities/boss.py` returns 1
    - `grep -c "from src.core import tuning" src/entities/enemies.py` returns 1
    - `grep -c "from src.core import tuning" src/entities/effects.py` returns 1
    - `grep -c "from src.core import tuning" src/entities/save_point.py` returns 1
    - `grep -c "from src.core import tuning" src/entities/items.py` returns 1
    - `grep -c "tuning.SLIME_FOLLOW_DELAY" src/entities/slime.py` returns at least 1
    - `grep -c "tuning.PROJECTILE_SPEED" src/entities/projectile.py` returns at least 1
    - `grep -c "tuning.BOSS_ROCK_SPEED" src/entities/boss.py` returns at least 1
    - `grep -c "tuning.CHARGE_SHOT_SPEED" src/entities/projectile.py` returns at least 1
    - For each of the 7 files: `python -c "import src.entities.<name>"` exits 0
    - `pytest -q` (full suite) exits 0
    - `pytest tests/test_tuning_livereach.py -q` still exits 0 (Plan 02's file untouched by this plan)
    - `pytest tests/test_tuning.py -q` exits 0 (Phase 24 regression canary)
  </acceptance_criteria>
  <done>
    All 7 entity files read `tuning.X` at every use site, no longer import from `src.core.constants`, and the full pytest suite (including Phase 24 tuning tests and Plan 02 livereach tests) is green.
  </done>
</task>

</tasks>

<verification>
1. `pytest -q` — full suite green
2. `grep -rn "from src.core.constants" src/entities/` — only player.py's `HAZARD_DRAIN_RATES` exception should remain (no other entity file should still hit the shim)
3. Spot-check: `grep -c "tuning\." src/entities/slime.py` — expect ≥15 (one per name previously imported, possibly many more due to repeat use sites)
4. Game boot smoke (optional, manual): `python main.py` and verify the window opens to the title screen without tracebacks. This is defense in depth; the pytest harness already imports every module under test.
</verification>

<success_criteria>
- Zero remaining `from src.core.constants` lines in any of the 7 files in this plan
- `from src.core import tuning` present exactly once per file
- Every previously-imported name prefixed with `tuning.` at every use site
- Full pytest suite green (including Plan 02's livereach tests and Phase 24's `tests/test_tuning.py`)
- No changes to files outside this plan's `files_modified` list
- No changes to `src/core/constants.py` (the shim is untouched per D-02a)
- No changes to any file in `tests/` (per D-02b)
</success_criteria>

<output>
After completion, create `.planning/phases/25-call-site-migration-constants-tuning/25-03-SUMMARY.md` with:
- Per-file name count actually swept (Grep-derived)
- Any ambiguous `__init__`-vs-per-frame call sites encountered and how D-01 was applied
- Confirmation that `pytest -q` is green
- Confirmation that `grep -rn "from src.core.constants" src/entities/` returns only the one deliberate player.py `HAZARD_DRAIN_RATES` line
</output>
