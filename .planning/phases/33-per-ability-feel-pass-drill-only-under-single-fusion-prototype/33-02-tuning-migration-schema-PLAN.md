---
phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
plan: 02
type: execute
wave: 1
depends_on: ["33-01"]
files_modified:
  - assets/physics-schema.json
  - src/fusion/charge_controller.py
  - src/fusion/pogo.py
  - src/ui/panel.py
autonomous: true
requirements: [FUS-06]
requirements_addressed: [FUS-06]
tags: [fusion, tuning, schema, panel]

must_haves:
  truths:
    - "tuning.WINDUP_DURATION_FRAMES, tuning.ACCELERATED_REGEN_RATE, tuning.POGO_BOUNCE_VELOCITY, tuning.POGO_COOLDOWN_FRAMES, tuning.DRILL_ENEMY_COST, tuning.SLIME_DAZE_COST all readable post-migration"
    - "charge_controller.py and pogo.py read tuning.X at use-site (Phase 25 pattern); module constants for migrated names are deleted"
    - "Panel surfaces all 6 new keys (FEEL_GROUPS includes 'pogo'; existing TAB_DEFS or extension covers all keys)"
    - "Phase 32 fusion FSM tests still pass (Pitfall 5 — schema seed equals current hardcoded baseline)"
    - "pogo group sits at the END of the tuning dict (last key), AFTER gates — deterministic key ordering for diff stability and downstream tooling"
  artifacts:
    - path: "assets/physics-schema.json"
      provides: "6 new tuning keys at schema-seed values matching current hardcoded baselines; pogo group inserted as new last key in tuning dict"
      contains: "WINDUP_DURATION_FRAMES, ACCELERATED_REGEN_RATE, POGO_BOUNCE_VELOCITY, POGO_COOLDOWN_FRAMES, DRILL_ENEMY_COST, SLIME_DAZE_COST"
    - path: "src/fusion/charge_controller.py"
      provides: "use-site tuning reads for ACCELERATED_REGEN_RATE + WINDUP_DURATION_FRAMES; module constants deleted"
    - path: "src/fusion/pogo.py"
      provides: "use-site tuning reads for POGO_BOUNCE_VELOCITY + POGO_COOLDOWN_FRAMES; POGO_INITIAL_DY and POGO_DAMAGE stay hardcoded"
    - path: "src/ui/panel.py"
      provides: "FEEL_GROUPS extended with 'pogo'; TAB_DEFS routes pogo group into Fuse tab (or new sub-tab if Pitfall 7)"
  key_links:
    - from: "src/fusion/charge_controller.py"
      to: "src/core/tuning.py"
      via: "use-site read in handle_z_input"
      pattern: "tuning\\.(WINDUP_DURATION_FRAMES|ACCELERATED_REGEN_RATE)"
    - from: "src/fusion/pogo.py"
      to: "src/core/tuning.py"
      via: "use-site read in on_tick / on_event"
      pattern: "tuning\\.POGO_BOUNCE_VELOCITY"
    - from: "src/ui/panel.py"
      to: "assets/physics-schema.json"
      via: "FEEL_GROUPS allowlist + TAB_DEFS dispatch"
      pattern: "\"pogo\""
---

<objective>
Migrate 6 hardcoded constants to `assets/physics-schema.json` so the live panel surfaces them per D-01, D-02, D-05, D-17. Tune values stay at current baseline (no behavior change in this plan; Phase 33 final plan iterates via panel and bakes into v2.0-default.json).

Purpose: Phase 25 use-site-read pattern + Phase 28 panel auto-flat-index together give Phase 33 free live-tuning reach for windup/regen/pogo/enemy-cost/daze-cost. Without this migration, charge ritual and pogo cannot be tuned via the panel.

Output: schema additions, module-constant deletions, use-site reads, panel allowlist update.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-CONTEXT.md
@.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-RESEARCH.md
@.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md
@assets/physics-schema.json
@src/fusion/charge_controller.py
@src/fusion/pogo.py
@src/ui/panel.py
@src/core/tuning.py
@src/fusion/drill_dive.py

<interfaces>
<!-- Existing schema groups (lines 60-104 in physics-schema.json): -->
<!-- slime_juice (line 66) — adds SLIME_DAZE_COST per D-17 -->
<!-- drill (line 77) — adds DRILL_ENEMY_COST per D-05 -->
<!-- fusion (line 94) — adds WINDUP_DURATION_FRAMES + ACCELERATED_REGEN_RATE per D-01 -->
<!-- NEW pogo group — adds POGO_BOUNCE_VELOCITY + POGO_COOLDOWN_FRAMES per D-02 -->
<!-- Pogo group MUST be inserted as the new LAST key in the `tuning` dict
     (i.e. AFTER `gates`, with `gates` no longer being last). The current last
     key in `tuning` post-edit will be `pogo`. This keeps the `tuning.X` group
     order deterministic and minimizes diff drift in downstream consumers
     (panel TAB_DEFS, schema-walking helpers). -->

<!-- src/core/tuning.py:_flat_index auto-builds at load() — every new key becomes
     accessible as `tuning.KEY`. No tuning.py edit required. -->

<!-- src/ui/panel.py:74-78 FEEL_GROUPS — hardcoded allowlist; new "pogo" group
     MUST be added here AND TAB_DEFS for panel surface (Pitfall 6). -->

<!-- Phase 25 use-site-read pattern (drill_dive.py:89-91 reference): -->
```python
player.dy = tuning.DRILL_SPEED                         # use-site read
slime.consume(tuning.DRILL_ACTIVATION_COST)            # use-site read
self._windup_progress += 1.0 / tuning.WINDUP_DURATION_FRAMES   # NEW post-migration
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Schema additions — 6 new keys + new pogo group (pinned as last tuning key)</name>
  <files>assets/physics-schema.json, src/ui/panel.py</files>
  <read_first>
    - assets/physics-schema.json (lines 60-105 — slime_juice, drill, fusion, gates groups; verify the LAST key currently in `tuning` dict before editing — see Step 1 invariant below)
    - src/ui/panel.py (lines 74-98 — FEEL_GROUPS set + TAB_DEFS list)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-CONTEXT.md (D-01, D-02, D-05, D-17 — schema-group placement guidance)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md (§ assets/physics-schema.json — concrete additions; § src/ui/panel.py TAB_DEFS — extension pattern)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-RESEARCH.md (Pitfall 5: schema seed must equal current hardcoded baseline; Pitfall 6: FEEL_GROUPS edit required)
    - src/fusion/charge_controller.py:33-34 (current baseline values)
    - src/fusion/pogo.py:30-32 (current baseline values)
  </read_first>
  <behavior>
    - assets/physics-schema.json `tuning.slime_juice` group gains key `SLIME_DAZE_COST: 20.0` (D-17 baseline) AS THE NEW LAST KEY of the slime_juice group (after SLIME_SPIT_COST).
    - assets/physics-schema.json `tuning.drill` group gains key `DRILL_ENEMY_COST: 15.0` (D-05 baseline; CONTEXT recommended 10–20 range, midpoint chosen for predictable starting feel) AS THE NEW LAST KEY of the drill group (after DRILL_BLOCK_REFUND).
    - assets/physics-schema.json `tuning.fusion` group gains keys `ACCELERATED_REGEN_RATE: 1.0` and `WINDUP_DURATION_FRAMES: 30` (D-01 baselines matching `charge_controller.py:33-34`) AS THE NEW LAST TWO KEYS of the fusion group (after SPIT_HOLD_THRESHOLD), in that order.
    - assets/physics-schema.json grows a NEW `tuning.pogo` group containing keys `POGO_BOUNCE_VELOCITY: -2.5` and `POGO_COOLDOWN_FRAMES: 0` (D-02 baselines matching `pogo.py:30-32`). The pogo group MUST be inserted AFTER `gates` and BEFORE `save` — making `pogo` the second-to-last key... NO WAIT. Re-read the rule: pogo MUST be the NEW LAST KEY of the `tuning` dict. The existing `save` group is OUTSIDE `tuning` (top-level), but verify before editing. If `save` is inside `tuning`, MOVE pogo to after `save`. The invariant: pogo is the LAST key inside `tuning` post-edit.
    - src/ui/panel.py `FEEL_GROUPS` set adds `"pogo"`.
    - src/ui/panel.py `TAB_DEFS` "Fuse" tab dict gains `"pogo": None` so all pogo keys surface in the existing Fuse tab (per RESEARCH Pitfall 7 viewport check — 11 existing + 6 new = 17 sliders; existing panel scroll handles this; no new tab required).
  </behavior>
  <action>
    Step 0 — INVARIANT VERIFICATION. Before any edit, run:
    ```bash
    python -c "import json; d=json.load(open('assets/physics-schema.json')); keys=list(d['tuning'].keys()); print('LAST_TUNING_KEY:', keys[-1]); print('ALL_KEYS:', keys)"
    ```
    Record the current last key of the `tuning` dict. Per the read above, it is currently `gates`. The post-edit invariant is: `keys[-1] == 'pogo'`. If your reading shows a DIFFERENT current last key, STOP and re-read the file — Step 1 below assumes `gates` is the current last key in `tuning`.

    Step 1 — `assets/physics-schema.json` — apply the following exact edits (preserve all other content, indentation, and key order EXCEPT for the explicit insertions specified):

    Edit 1a — Inside `tuning.slime_juice` (currently lines 66-71), add `SLIME_DAZE_COST` AS THE NEW LAST KEY of that group, AFTER `SLIME_SPIT_COST: 10.0`:

    ```json
    "slime_juice": {
      "JUICE_MAX": 200.0,
      "JUICE_REGEN_RATE": 0.5,
      "JUICE_MIN_SCALE": 0.25,
      "SLIME_SPIT_COST": 10.0,
      "SLIME_DAZE_COST": 20.0
    },
    ```

    Edit 1b — Inside `tuning.drill` (currently lines 77-83), add `DRILL_ENEMY_COST` AS THE NEW LAST KEY of that group, AFTER `DRILL_BLOCK_REFUND: 15.0`:

    ```json
    "drill": {
      "DRILL_SPEED": 2.0,
      "DRILL_DRIFT_SPEED": 0.5,
      "DRILL_IMPACT_COST": 20.0,
      "DRILL_ACTIVATION_COST": 5.0,
      "DRILL_BLOCK_REFUND": 15.0,
      "DRILL_ENEMY_COST": 15.0
    },
    ```

    Edit 1c — Inside `tuning.fusion` (currently lines 94-101), add `ACCELERATED_REGEN_RATE` THEN `WINDUP_DURATION_FRAMES` AS THE NEW LAST TWO KEYS of that group, AFTER `SPIT_HOLD_THRESHOLD: 16` (in that order):

    ```json
    "fusion": {
      "RECALL_SPEED": 4.0,
      "RECALL_OVERLAP_DIST": 4,
      "MANA_SHIELD_COST": 20.0,
      "SLIME_DISSIPATE_COOLDOWN": 240,
      "RECALL_TRAIL_COLOR": 11,
      "SPIT_HOLD_THRESHOLD": 16,
      "ACCELERATED_REGEN_RATE": 1.0,
      "WINDUP_DURATION_FRAMES": 30
    },
    ```

    Edit 1d — Insert the new `pogo` group AS THE NEW LAST KEY of the `tuning` dict. The current last key of `tuning` is `gates` (per Step 0 verification). After this edit, `gates` is followed by a comma, and `pogo` becomes the new last key (no trailing comma after pogo's closing brace):

    ```json
    "gates": {
      "DRILL_CRACKED_V_COST": 20.0
    },
    "pogo": {
      "POGO_BOUNCE_VELOCITY": -2.5,
      "POGO_COOLDOWN_FRAMES": 0
    }
    ```

    NOTE: the existing `save` group at line 105 is OUTSIDE the `tuning` dict (top-level config), NOT inside `tuning`. Verify this with the Step 0 ALL_KEYS output. The `save` group should NOT appear in the Step 0 output's `keys` list. If it does, your Step 0 read got `tuning` wrong — re-read the file before editing. The pogo insertion goes AFTER `gates`'s closing brace+comma and BEFORE the closing brace of the `tuning` dict.

    Edit 1e — Trailing-comma JSON validity sanity check: run after every edit:
    ```bash
    python -c "import json; json.load(open('assets/physics-schema.json'))"
    ```
    Exit 0 = valid JSON.

    Step 2 — `src/ui/panel.py` — extend FEEL_GROUPS and TAB_DEFS.

    Locate the line `FEEL_GROUPS = {` (around line 74). Add `"pogo"` to the set. The result must be:

    ```python
    FEEL_GROUPS = {
        "movement", "forgiving", "wall",
        "slime_follow", "slime_juice", "projectile",
        "drill", "fusion", "pogo",
    }
    ```

    Locate the `TAB_DEFS` list (around lines 80-98). Find the `("Fuse", { ... })` entry and add `"pogo": None` to its dict value. The result must be:

    ```python
    ("Fuse",  {"drill": None, "fusion": None, "pogo": None}),
    ```

    Do NOT change any other tab; do NOT add `pogo` to FEEL_GROUPS twice; do NOT introduce a separate "Pogo" tab — the 17-slider Fuse tab is acceptable per RESEARCH Pitfall 7 (existing scroll handles it).
  </action>
  <verify>
    <automated>python -c "import json; d=json.load(open('assets/physics-schema.json')); t=d['tuning']; keys=list(t.keys()); assert keys[-1]=='pogo', f'pogo must be LAST tuning key, got order: {keys}'; assert t['slime_juice']['SLIME_DAZE_COST']==20.0; assert t['drill']['DRILL_ENEMY_COST']==15.0; assert t['fusion']['ACCELERATED_REGEN_RATE']==1.0; assert t['fusion']['WINDUP_DURATION_FRAMES']==30; assert t['pogo']['POGO_BOUNCE_VELOCITY']==-2.5; assert t['pogo']['POGO_COOLDOWN_FRAMES']==0; print('OK')"</automated>
  </verify>
  <acceptance_criteria>
    - `python -c "import json; json.load(open('assets/physics-schema.json'))"` exits 0 (valid JSON)
    - **Key-order invariant (W#7 closure):** `python -c "import json; d=json.load(open('assets/physics-schema.json')); keys=list(d['tuning'].keys()); assert keys[-1]=='pogo', f'pogo must be LAST tuning key, got: {keys}'; print('OK')"` exits 0 — pogo is the LAST key of the `tuning` dict
    - **Adjacent-to-gates invariant:** `python -c "import json; d=json.load(open('assets/physics-schema.json')); keys=list(d['tuning'].keys()); gi=keys.index('gates'); pi=keys.index('pogo'); assert pi==gi+1, f'pogo must immediately follow gates, got: {keys}'; print('OK')"` exits 0
    - `grep "SLIME_DAZE_COST" assets/physics-schema.json` returns a match
    - `grep "DRILL_ENEMY_COST" assets/physics-schema.json` returns a match
    - `grep "ACCELERATED_REGEN_RATE" assets/physics-schema.json` returns a match
    - `grep "WINDUP_DURATION_FRAMES" assets/physics-schema.json` returns a match
    - `grep "POGO_BOUNCE_VELOCITY" assets/physics-schema.json` returns a match
    - `grep "POGO_COOLDOWN_FRAMES" assets/physics-schema.json` returns a match
    - `grep -c "\"pogo\":" assets/physics-schema.json` returns at least 1 (the new tuning.pogo group)
    - `grep "\"pogo\"" src/ui/panel.py` returns at least 2 matches (FEEL_GROUPS + TAB_DEFS)
    - `python -c "from src.core import tuning; print(tuning.SLIME_DAZE_COST, tuning.DRILL_ENEMY_COST, tuning.WINDUP_DURATION_FRAMES, tuning.ACCELERATED_REGEN_RATE, tuning.POGO_BOUNCE_VELOCITY, tuning.POGO_COOLDOWN_FRAMES)"` outputs `20.0 15.0 30 1.0 -2.5 0`
  </acceptance_criteria>
  <done>Schema valid JSON; 6 new keys readable via tuning.X; pogo is the LAST key of tuning dict (immediately after gates); FEEL_GROUPS includes "pogo"; TAB_DEFS Fuse tab routes pogo group; baselines exactly match current hardcoded values (Pitfall 5 closed); deterministic key ordering closed (W#7).</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: charge_controller.py + pogo.py — delete module constants, switch to use-site reads</name>
  <files>src/fusion/charge_controller.py, src/fusion/pogo.py</files>
  <read_first>
    - src/fusion/charge_controller.py (full file — note lines 33-34 module constants; lines 94, 120 use sites; lines 25-26 imports)
    - src/fusion/pogo.py (full file — note lines 28-33 module constants; lines 117, 135 use sites of POGO_BOUNCE_VELOCITY; existing imports)
    - src/fusion/drill_dive.py (lines 22-25 imports + lines 89-91, 117-122 use-site read pattern)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md (§ src/fusion/charge_controller.py and § src/fusion/pogo.py — concrete BEFORE/AFTER excerpts)
    - tests/test_tuning_migration.py (asserts use-site reads exist + module constants deleted)
  </read_first>
  <behavior>
    - charge_controller.py: delete module-level `WINDUP_DURATION_FRAMES = 30` and `ACCELERATED_REGEN_RATE = 1.0` lines. Replace ALL use sites with `tuning.WINDUP_DURATION_FRAMES` and `tuning.ACCELERATED_REGEN_RATE`. Keep `_STATE_IDLE`, `_STATE_RECALL`, `_STATE_WINDUP` constants (gameplay-stable, not feel-tunable).
    - pogo.py: delete module-level `POGO_BOUNCE_VELOCITY = -2.5` and `POGO_COOLDOWN_FRAMES = 0` lines. Replace ALL use sites with `tuning.POGO_BOUNCE_VELOCITY` and `tuning.POGO_COOLDOWN_FRAMES`. Keep `POGO_INITIAL_DY = 2.0` (D-02: Mario-64 visual parity with DRILL_SPEED), `POGO_DAMAGE = 1` (D-02: gameplay constant), `EXPLOSION_SIZE_PX`, `INTGRID_CRACKED_V` (per D-02 list of stay-hardcoded). Add `from src.core import tuning` import if not already present.
    - Behavior unchanged frame-for-frame: schema seed values equal old module constants (Pitfall 5 — verified by Phase 32 regression suite staying GREEN).
  </behavior>
  <action>
    Step 1 — `src/fusion/charge_controller.py`:

    1a. Delete the two module-constant lines (currently lines 33-34):
    ```python
    ACCELERATED_REGEN_RATE = 1.0       # juice/frame; FUSION-DESIGN draft 2x passive
    WINDUP_DURATION_FRAMES = 30        # ~0.5s @60fps; FUSION-DESIGN D-23c base target
    ```
    Also delete the comment block above them (lines 28-32, the "Phase 32 FUS-04 — ChargeController hardcoded constants..." block) — it specifically references "Phase 33 may migrate" and is now obsolete. Replace with a single line comment:
    ```python
    # Phase 33 D-01: WINDUP_DURATION_FRAMES + ACCELERATED_REGEN_RATE migrated to
    # assets/physics-schema.json (tuning.fusion group); read at use-site below.
    ```

    1b. Replace use sites. Search the file for `WINDUP_DURATION_FRAMES` and `ACCELERATED_REGEN_RATE` references. For each non-comment occurrence, prefix with `tuning.`. Specifically:
    - Inside `handle_z_input` (or wherever `slime.refill(ACCELERATED_REGEN_RATE)` appears), replace with `slime.refill(tuning.ACCELERATED_REGEN_RATE)`.
    - Inside `handle_z_input` (or wherever `1.0 / WINDUP_DURATION_FRAMES` appears), replace with `1.0 / tuning.WINDUP_DURATION_FRAMES`.
    Verify the `from src.core import tuning` import (line 25) is unchanged and present.

    Step 2 — `src/fusion/pogo.py`:

    2a. Delete the two module-constant lines (currently lines 30-32, including the trailing inline comment fragment):
    ```python
    POGO_BOUNCE_VELOCITY = -2.5    # negative = upward bounce on enemy / breakable
                                    # contact (Phase 33 tunes)
    POGO_COOLDOWN_FRAMES = 0       # D-20: free, no cooldown in v2.0 baseline
    ```
    Replace with a single line comment:
    ```python
    # Phase 33 D-02: POGO_BOUNCE_VELOCITY + POGO_COOLDOWN_FRAMES migrated to
    # assets/physics-schema.json (tuning.pogo group); read at use-site below.
    ```

    2b. KEEP `POGO_INITIAL_DY = 2.0` (line 28; required for Mario-64 visual parity per D-02), `POGO_DAMAGE = 1` (line 33; gameplay constant per D-02), `EXPLOSION_SIZE_PX = 9` (line 34; gameplay-stable), `INTGRID_CRACKED_V = 12` (line 39; sentinel).

    2c. Add `from src.core import tuning` import to the import block at the top of pogo.py if not already present. (Currently pogo.py likely imports only `TickResult` from `src.fusion.protocol`; verify the existing import block before deciding placement.)

    2d. Replace use sites. Search the file for `POGO_BOUNCE_VELOCITY` and `POGO_COOLDOWN_FRAMES` references. For each non-comment occurrence, prefix with `tuning.`. Specifically the `dy=POGO_BOUNCE_VELOCITY` arg of `TickResult(...)` calls becomes `dy=tuning.POGO_BOUNCE_VELOCITY`. Any cooldown-frame logic referencing POGO_COOLDOWN_FRAMES likewise.

    Step 3 — Run the migration smoke tests to confirm Pitfall 5 closure. The `test_tuning_migration.py` tests created in Plan 01 should now go from SKIP/FAIL to PASS for the use-site assertions.
  </action>
  <verify>
    <automated>pytest tests/test_tuning_migration.py tests/test_fusion_fsm.py tests/test_drill_dive_parity.py tests/test_pogo.py -x -q</automated>
  </verify>
  <acceptance_criteria>
    - `grep "^WINDUP_DURATION_FRAMES" src/fusion/charge_controller.py` returns NO matches
    - `grep "^ACCELERATED_REGEN_RATE" src/fusion/charge_controller.py` returns NO matches
    - `grep "tuning.WINDUP_DURATION_FRAMES" src/fusion/charge_controller.py` returns at least 1 match
    - `grep "tuning.ACCELERATED_REGEN_RATE" src/fusion/charge_controller.py` returns at least 1 match
    - `grep "^POGO_BOUNCE_VELOCITY" src/fusion/pogo.py` returns NO matches
    - `grep "^POGO_COOLDOWN_FRAMES" src/fusion/pogo.py` returns NO matches
    - `grep "tuning.POGO_BOUNCE_VELOCITY" src/fusion/pogo.py` returns at least 1 match
    - `grep "^POGO_INITIAL_DY" src/fusion/pogo.py` returns 1 match (preserved)
    - `grep "^POGO_DAMAGE" src/fusion/pogo.py` returns 1 match (preserved)
    - `grep "from src.core import tuning" src/fusion/pogo.py` returns 1 match
    - `pytest tests/test_fusion_fsm.py -x -q` exits 0 (Phase 32 FSM contract preserved)
    - `pytest tests/test_drill_dive_parity.py -x -q` exits 0 (v1.3 drill parity preserved)
    - `pytest tests/test_pogo.py -x -q` exits 0 (Phase 32 pogo contract preserved)
    - `pytest tests/test_tuning_migration.py -x -q` exits 0 (all migration assertions GREEN)
  </acceptance_criteria>
  <done>Module constants for the 4 migrated names are deleted from charge_controller.py and pogo.py; use-site `tuning.X` reads in place; POGO_INITIAL_DY and POGO_DAMAGE preserved; Phase 32 fusion suite + Phase 33 migration tests all GREEN.</done>
</task>

</tasks>

<verification>
- `pytest tests/ -x -q` runs the full suite to GREEN. Phase 32 invariants (test_fusion_fsm, test_drill_dive_parity, test_pogo) all pass; Phase 33 test_tuning_migration moves from SKIP to PASS.
- Live boot still loads:
  - `python -c "from src.core import tuning; tuning.reset(); print(tuning.WINDUP_DURATION_FRAMES, tuning.POGO_BOUNCE_VELOCITY)"` outputs `30 -2.5`.
- Panel surface:
  - `python -c "from src.ui.panel import FEEL_GROUPS, TAB_DEFS; assert 'pogo' in FEEL_GROUPS; print(TAB_DEFS)"` shows `pogo` in Fuse-tab dict.
- Schema integrity:
  - `python -c "import json; json.load(open('assets/physics-schema.json'))"` exits 0.
- Schema key-order invariant (W#7):
  - `python -c "import json; d=json.load(open('assets/physics-schema.json')); keys=list(d['tuning'].keys()); assert keys[-1]=='pogo'; print('OK')"` exits 0.
</verification>

<success_criteria>
- All 6 keys readable via `tuning.X` at schema-seed values matching current hardcoded baselines (Pitfall 5)
- charge_controller.py and pogo.py free of module-level constants for migrated names; use-site reads in place
- pogo.py retains POGO_INITIAL_DY = 2.0 and POGO_DAMAGE = 1 (D-02 hard requirements)
- panel.py FEEL_GROUPS extended with "pogo"; TAB_DEFS Fuse tab includes pogo group (Pitfall 6)
- pogo group is the LAST key in the schema's `tuning` dict (deterministic key order — W#7 closure)
- Full test suite GREEN — no Phase 32 regressions
</success_criteria>

<output>
After completion, create `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-02-SUMMARY.md` per @$HOME/.claude/get-shit-done/templates/summary.md.
</output>
