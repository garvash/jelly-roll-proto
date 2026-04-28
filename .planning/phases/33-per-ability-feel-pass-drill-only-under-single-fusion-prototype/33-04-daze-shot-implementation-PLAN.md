---
phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
plan: 04
type: execute
wave: 2
depends_on: ["33-02"]
files_modified:
  - src/entities/player.py
  - src/entities/projectile.py
  - main.py
  - tests/test_daze_shot.py
autonomous: true
requirements: [FUS-06]
requirements_addressed: [FUS-06]
tags: [fusion, daze, projectile, combat]

must_haves:
  truths:
    - "Fused player can fire spit/daze projectile via tap-Z (the `not self.is_fused` gate at player.py:197 is removed)"
    - "Fused-branch consumes EXACTLY tuning.SLIME_DAZE_COST from slime juice (no double-cost; slime.spit's internal SLIME_SPIT_COST path is bypassed via direct Projectile construction)"
    - "Fused-branch with juice < tuning.SLIME_DAZE_COST does NOT fire and does NOT consume juice (Pitfall 4 cancel-spam guard)"
    - "Fused-branch emits daze_fire event"
    - "Daze projectile flagged with applies_daze_stun = True"
    - "main.py per-frame loop scans projectile-vs-enemy AABB intersections; when proj.applies_daze_stun AND enemy has stun_timer field, sets enemy.stun_timer = STUN_DURATION_FRAMES and consumes the projectile"
    - "Boss daze contact does NOT raise (Boss has no stun_timer; hasattr-guarded contact site is a graceful no-op verified by regression test)"
    - "Unfused tap-Z spit path unchanged (slime.spit pays SLIME_SPIT_COST internally; pre-Phase-33 behavior preserved)"
  artifacts:
    - path: "src/entities/player.py"
      provides: "fused-branch added to spit handler at :197 with cost gate + daze_fire emit + applies_daze_stun flag set on directly-constructed Projectile (bypasses slime.spit double-cost)"
    - path: "src/entities/projectile.py"
      provides: "applies_daze_stun: bool = False default field on Projectile + STUN_DURATION_FRAMES module constant"
    - path: "main.py"
      provides: "per-frame projectile-vs-enemy AABB scan in Game.update; on intersect with proj.applies_daze_stun and enemy.stun_timer attr present, sets stun_timer and marks projectile inactive"
    - path: "tests/test_daze_shot.py"
      provides: "Test 1 (fire fused), Test 2 (low-juice gate), Test 3 (stun on Snail contact via main.py loop), Test 4 (Boss contact does not raise)"
  key_links:
    - from: "src/entities/player.py:handle_input"
      to: "src/entities/projectile.py:Projectile"
      via: "fused-branch directly constructs Projectile(...) with applies_daze_stun=True; bypasses slime.spit"
      pattern: "applies_daze_stun"
    - from: "main.py:Game.update"
      to: "src/entities/enemies.py:Enemy.stun_timer"
      via: "per-frame projectile-vs-enemy AABB scan; sets enemy.stun_timer if proj.applies_daze_stun and hasattr"
      pattern: "stun_timer = STUN_DURATION_FRAMES|stun_timer = max"
---

<objective>
Implement the daze-shot fused-branch per D-17: when fused, tap-Z fires a daze projectile (constructed directly to bypass slime.spit's internal SLIME_SPIT_COST) costing exactly `tuning.SLIME_DAZE_COST`, flagged `applies_daze_stun=True`. Add a per-frame projectile-vs-enemy AABB scan in main.py; when a daze-flagged projectile intersects an enemy with a `stun_timer` field, the projectile is consumed and the enemy is stunned for STUN_DURATION_FRAMES (consuming the primitive added in Plan 03 Task 1). Boss contact remains a graceful no-op (hasattr-guarded). Audio identity (`daze_fire` event) wired here; subscriber + SFX defined in Plan 05.

Purpose: closes the input contract for FUSION-DESIGN D-14 and delivers BOTH halves of D-17 (fire + stun). PROJECT.md core fantasy "shoot to daze → drill to finish" requires the daze step to actually land a stun on regular enemies. Blocker #2 (verification mode) flagged that earlier revisions of this plan deferred the stun half silently — this plan ships it.

Output: player.py:197 gate removed + fused-branch added (direct Projectile construction); projectile.py gains the flag + duration constant; main.py per-frame scan applies stun; test_daze_shot.py covers all four behaviors including the boss-no-raise regression.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/FUSION-DESIGN.md
@.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-CONTEXT.md
@.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-RESEARCH.md
@.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md
@src/entities/player.py
@src/entities/projectile.py
@src/entities/slime.py
@src/entities/boss.py
@src/entities/enemies.py
@src/anim/event_bus.py
@main.py
@tests/test_daze_shot.py

<interfaces>
<!-- Confirmed during plan revision (W#1 closure): src/entities/slime.py:225-232
     `slime.spit()` PAYS SLIME_SPIT_COST internally:
       def spit(self, dx, dy, level_map):
           if self.juice >= tuning.SLIME_SPIT_COST:
               self.consume(tuning.SLIME_SPIT_COST)   # <-- internal cost
               from src.entities.projectile import Projectile
               event_bus.emit("spit")
               return Projectile(self.x + self.w // 2 - 2, self.y, dx, dy, level_map)
           return None

     **PINNED RESOLUTION (W#1 — single approach, no implementer choice):**
     The fused-branch MUST construct `Projectile(...)` directly. The fused
     branch is a NEW code path (D-17 unfusing the gate); reusing slime.spit
     is convenience, not contract. Direct construction:
       1. Avoids the cost-refund hack (no double-charge to undo).
       2. Self-contained — the daze branch does not depend on slime.spit's
          juice gate (the fused-branch already pre-checks SLIME_DAZE_COST).
       3. Does NOT emit the existing "spit" event (which is unfused-only
          identity); fused emits "daze_fire" only.

     The unfused branch is UNCHANGED — keeps calling slime.spit. -->

<!-- Current spit handler at src/entities/player.py:197: -->
```python
if input_manager.was_tap("spit", tuning.SPIT_HOLD_THRESHOLD) and not self.is_fused and self.state != "DIVING":
    # ... auto-aim block (lines 198-262) ...
    proj = slime.spit(target_dx, target_dy, self.level_map)
    if proj and self.game:
        self.game.projectiles.append(proj)
```

<!-- After Plan 04: -->
```python
if input_manager.was_tap("spit", tuning.SPIT_HOLD_THRESHOLD) and self.state != "DIVING":
    # ... auto-aim block UNCHANGED (lines 198-262) ...
    if self.is_fused:
        if slime.juice < tuning.SLIME_DAZE_COST:
            return
        slime.consume(tuning.SLIME_DAZE_COST)
        # Direct Projectile construction — bypasses slime.spit's internal
        # SLIME_SPIT_COST path. Spawn coords match slime.spit (slime.x + w//2 - 2, slime.y).
        from src.entities.projectile import Projectile
        proj = Projectile(slime.x + slime.w // 2 - 2, slime.y, target_dx, target_dy, self.level_map)
        proj.applies_daze_stun = True
        event_bus.emit("daze_fire")
    else:
        proj = slime.spit(target_dx, target_dy, self.level_map)
    if proj and self.game:
        self.game.projectiles.append(proj)
```

<!-- main.py projectile-vs-enemy contact loop (NEW per Blocker #2 closure):
     Currently main.py has NO projectile-vs-enemy contact site for regular
     enemies. The only existing projectile-contact code is:
       - Line 832: door projectile-hit (kick gate)
       - boss.py:106-111 (Mole.update_emerging — sets boss VULNERABLE on hit)
     Plan 04 Task 3 adds a new per-frame AABB scan AFTER the projectile-update
     loop at main.py:787-791 and BEFORE the door scan at line 826. -->

<!-- Plan 03 Task 1 added Enemy.stun_timer = 0 + subclass early-return guard;
     this plan SETS the timer at the projectile-vs-enemy contact site. -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Projectile.applies_daze_stun field + STUN_DURATION_FRAMES constant</name>
  <files>src/entities/projectile.py</files>
  <read_first>
    - src/entities/projectile.py (full file — note __init__ signature lines 4-18, update method lines 20-41, screen-cull at lines 37-39)
    - src/entities/enemies.py (verify Enemy.stun_timer added by Plan 03 Task 1; Snail/Bat subclasses)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md (§ src/entities/projectile.py — concrete BEFORE/AFTER)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-RESEARCH.md (§ Code Examples → Daze-shot fused-branch sketch)
  </read_first>
  <behavior>
    - Module-level constant `STUN_DURATION_FRAMES = 60` (1 second @ 60fps; tunable later if playtest demands; not migrated to schema in Phase 33).
    - `Projectile.__init__` adds `self.applies_daze_stun = False` (default False; Player.handle_input fused-branch in Task 2 sets True for daze projectiles; main.py contact-scan in Task 3 reads it).
    - No changes to existing collision logic (terrain check, screen-cull). The daze-stun application happens at the CONTACT SITE (main.py Task 3), not inside Projectile.update.
    - Behavior of unfused spit projectiles is unchanged (applies_daze_stun stays False; main.py scan no-ops for them).
  </behavior>
  <action>
    Step 1 — Add module-level constant. In `src/entities/projectile.py`, add the constant ABOVE the `class Projectile:` line:

    ```python
    # Phase 33 D-17: daze-on-hit stun duration (1s @ 60fps). Hardcoded
    # gameplay constant; not migrated to schema in this phase. Plan 03 Task 1
    # added Enemy.stun_timer; main.py Task 3 sets it via this constant.
    STUN_DURATION_FRAMES = 60
    ```

    Step 2 — In `Projectile.__init__`, add the field default at the END of the existing init body (after `self.gravity = 0.0375` line 15, before the `if self.level_map.check_collision(...)` block at line 17):

    ```python
    # Phase 33 D-17: daze-on-hit flag. Set to True by Player.handle_input
    # fused-branch when player is fused. Read at the projectile-vs-enemy
    # contact-scan site in main.py (Task 3).
    self.applies_daze_stun = False
    ```

    Step 3 — Do NOT modify Projectile.update or Projectile.draw. The application logic lives in main.py per Task 3 — keeping Projectile a passive data carrier preserves the existing terrain-only contract and avoids cross-cutting enemy-iteration concerns into projectile.py.
  </action>
  <verify>
    <automated>pytest tests/ -x -q -k "not daze_shot"</automated>
  </verify>
  <acceptance_criteria>
    - `grep "STUN_DURATION_FRAMES = 60" src/entities/projectile.py` returns 1 match
    - `grep "self.applies_daze_stun = False" src/entities/projectile.py` returns 1 match
    - `python -c "from src.entities.projectile import Projectile, STUN_DURATION_FRAMES; print(STUN_DURATION_FRAMES)"` outputs `60`
    - `python -c "from src.entities.projectile import Projectile; from unittest.mock import MagicMock; lm=MagicMock(); lm.check_collision=lambda *a,**k: False; p=Projectile(0,0,1,0,lm); assert p.applies_daze_stun==False; print('OK')"` outputs `OK`
    - `pytest tests/ -x -q -k "not daze_shot"` exits 0 (no regressions; daze_shot tests still RED at this checkpoint, addressed in Task 2 + Task 3)
  </acceptance_criteria>
  <done>STUN_DURATION_FRAMES module constant defined; Projectile has applies_daze_stun = False default; no other Projectile changes; existing test suite GREEN (daze_shot tests still skipped pending Task 2 + Task 3).</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: player.py:197 fused-branch — gate removal + direct Projectile construction (no double-cost) + daze_fire emit</name>
  <files>src/entities/player.py</files>
  <read_first>
    - src/entities/player.py:1-7 (imports — confirm `event_bus` already imported via `from src.anim import event_bus`; if not, add the import)
    - src/entities/player.py:192-267 (full handle_input spit handler — lines 197-266, the auto-aim + slime.spit + projectile-append block)
    - src/entities/slime.py:225-232 (CONFIRMED: slime.spit pays SLIME_SPIT_COST internally — read once for understanding; the fused-branch BYPASSES this method entirely)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md (§ src/entities/player.py:197 — concrete BEFORE/AFTER + double-cost callout)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-RESEARCH.md (§ Pitfall 4 — daze tap/hold disambiguation; § Code Examples → Daze-shot fused-branch sketch)
    - tests/test_daze_shot.py (Wave 0 RED stubs — Test 1 + Test 2 made GREEN by this task)
  </read_first>
  <behavior>
    - Spit handler condition at player.py:197 changes from `... and not self.is_fused and self.state != "DIVING":` to `... and self.state != "DIVING":` (gate removal — D-17).
    - Inside the handler, the existing `proj = slime.spit(target_dx, target_dy, self.level_map)` line at line 264 is REPLACED with a fused/unfused branch:
      - Fused branch:
        - Pre-check: `if slime.juice < tuning.SLIME_DAZE_COST: return` (Pitfall 4 cancel-spam guard).
        - Cost: `slime.consume(tuning.SLIME_DAZE_COST)` — exactly one charge.
        - Spawn: construct `Projectile(...)` DIRECTLY with the same spawn-coord formula slime.spit uses (`slime.x + slime.w // 2 - 2, slime.y`). DO NOT call slime.spit — that would charge SLIME_SPIT_COST on top of SLIME_DAZE_COST (the W#1 double-cost pattern).
        - Flag: `proj.applies_daze_stun = True`.
        - Emit: `event_bus.emit("daze_fire")` — wires the audio cue subscriber (Plan 05 binds the SFX). Do NOT also emit "spit" — fused identity is "daze_fire" only.
      - Unfused branch (UNCHANGED): `proj = slime.spit(target_dx, target_dy, self.level_map)`.
    - Both branches converge at the existing `if proj and self.game: self.game.projectiles.append(proj)` line.
    - tests/test_daze_shot.py Test 1 + Test 2 go GREEN (the stun-on-contact tests Test 3 + Test 4 are made GREEN by Task 3).
  </behavior>
  <action>
    Step 1 — Edit `src/entities/player.py:197`. The current line is:

    ```python
    if input_manager.was_tap("spit", tuning.SPIT_HOLD_THRESHOLD) and not self.is_fused and self.state != "DIVING":
    ```

    Replace with:

    ```python
    if input_manager.was_tap("spit", tuning.SPIT_HOLD_THRESHOLD) and self.state != "DIVING":
    ```

    Step 2 — Verify the import block at the top of player.py imports event_bus. If not, add `from src.anim import event_bus` to the imports.

    Step 3 — Inside the handler body, locate line 264 (`proj = slime.spit(target_dx, target_dy, self.level_map)`). Replace it with:

    ```python
    # Phase 33 D-17: fused-branch fires daze; unfused-branch fires spit.
    # Pitfall 4 cancel-spam guard: gate on juice BEFORE consume to prevent
    # WINDUP-cancel-Z-release from draining juice on no-fire.
    # W#1 closure: fused-branch constructs Projectile DIRECTLY to bypass
    # slime.spit's internal SLIME_SPIT_COST charge. The fused branch is a
    # NEW code path (D-17 unfuses the gate); reusing slime.spit is convenience,
    # not contract. SLIME_DAZE_COST is the ONLY juice cost on this path.
    if self.is_fused:
        if slime.juice < tuning.SLIME_DAZE_COST:
            return
        slime.consume(tuning.SLIME_DAZE_COST)
        from src.entities.projectile import Projectile
        proj = Projectile(slime.x + slime.w // 2 - 2, slime.y,
                          target_dx, target_dy, self.level_map)
        proj.applies_daze_stun = True
        event_bus.emit("daze_fire")
    else:
        proj = slime.spit(target_dx, target_dy, self.level_map)
    ```

    The existing `if proj and self.game: self.game.projectiles.append(proj)` block STAYS unchanged below this — both branches assign `proj`.

    Step 4 — UNSKIP `tests/test_daze_shot.py` Test 1 + Test 2. Plan 01 created the file with `@pytest.mark.skip(reason="Wave 2 implements daze-shot fused-branch")` decorators on those two tests. Remove the skip decorators on Test 1 (`test_fused_tap_fires_daze`) and Test 2 (`test_daze_blocked_on_low_juice`). Do NOT remove decorators on Test 3 / Test 4 (added in Task 3) — those wait on Task 3.

    Step 5 — Update test_daze_shot.py Test 1 to assert exact-cost (no double-charge). The Wave 0 stub already asserts `mock_slime.juice == initial_juice - tuning.SLIME_DAZE_COST` — confirm this assertion is present and correct. If Wave 0 used a `>=` or approximation, tighten to `==`. Add a comment line above the assertion: `# W#1 closure: fused branch consumes EXACTLY SLIME_DAZE_COST (no SPIT_COST double-charge).`

    Step 6 — DOCUMENT the resolution in 33-IMPLEMENTATION-NOTES.md (extend the file Plan 03 created). Append:

    ```markdown
    ## Daze double-cost resolution (W#1 closure)

    **Decision:** Fused-branch constructs Projectile directly; bypasses slime.spit.

    **Why:** `src/entities/slime.py:225-232` shows `slime.spit()` calls
    `self.consume(tuning.SLIME_SPIT_COST)` internally. Phase 33 D-17 specifies
    SLIME_DAZE_COST as the ONLY cost for the fused branch; an additive double-
    charge of SPIT_COST + DAZE_COST would silently change the design intent.

    Direct Projectile construction:
    1. Avoids the cost-refund hack (no double-charge to undo).
    2. Self-contained — the daze branch does not depend on slime.spit's
       juice gate (the fused-branch already pre-checks SLIME_DAZE_COST).
    3. Does NOT emit the existing "spit" event (which is unfused-only
       identity); fused emits "daze_fire" only.

    **Spawn coordinates** match slime.spit's formula verbatim:
    `Projectile(slime.x + slime.w // 2 - 2, slime.y, dx, dy, level_map)` —
    keeps fused-vs-unfused projectile spawn pixel-identical so visual identity
    (sprite frame, projectile palette) reads consistently.

    **Verification:** `tests/test_daze_shot.py::test_fused_tap_fires_daze`
    asserts `mock_slime.juice == initial_juice - tuning.SLIME_DAZE_COST`
    EXACTLY — failing this catches double-cost regressions.
    ```
  </action>
  <verify>
    <automated>pytest tests/test_daze_shot.py::test_fused_tap_fires_daze tests/test_daze_shot.py::test_daze_blocked_on_low_juice tests/test_drill_dive_parity.py tests/test_fusion_fsm.py -x -v</automated>
  </verify>
  <acceptance_criteria>
    - `grep "not self.is_fused" src/entities/player.py` returns NO matches on the spit handler line near line 197 (the gate is removed; other `is_fused` references for unrelated logic may remain)
    - `grep -n "was_tap(\"spit\"" src/entities/player.py` shows the line WITHOUT `not self.is_fused`
    - `grep "tuning.SLIME_DAZE_COST" src/entities/player.py` returns at least 2 matches (the juice pre-check + the consume call)
    - `grep "applies_daze_stun = True" src/entities/player.py` returns 1 match
    - `grep 'event_bus.emit("daze_fire"' src/entities/player.py` returns 1 match
    - **W#1 closure (no slime.spit in fused branch):** `python -c "import re; src=open('src/entities/player.py').read(); fused_block=re.search(r'if self.is_fused:.*?else:', src, re.DOTALL); assert fused_block; assert 'slime.spit' not in fused_block.group(0), f'Fused branch must NOT call slime.spit (double-cost); got: {fused_block.group(0)[:200]}'; print('OK')"` exits 0
    - **W#1 closure (direct Projectile construction in fused branch):** `python -c "import re; src=open('src/entities/player.py').read(); fused_block=re.search(r'if self.is_fused:.*?else:', src, re.DOTALL); assert fused_block; assert 'Projectile(' in fused_block.group(0), 'Fused branch must construct Projectile directly'; print('OK')"` exits 0
    - `pytest tests/test_daze_shot.py::test_fused_tap_fires_daze -x -v` exits 0 (Test 1 GREEN; assertion `mock_slime.juice == initial_juice - tuning.SLIME_DAZE_COST` enforces no-double-cost)
    - `pytest tests/test_daze_shot.py::test_daze_blocked_on_low_juice -x -v` exits 0 (Test 2 GREEN)
    - `pytest tests/test_drill_dive_parity.py tests/test_fusion_fsm.py -x -v` exits 0 (Phase 32 invariants preserved)
    - `grep -c "double-cost" .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-IMPLEMENTATION-NOTES.md` returns at least 1
    - `grep -c "W#1" .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-IMPLEMENTATION-NOTES.md` returns at least 1
  </acceptance_criteria>
  <done>player.py:197 gate removed; fused-branch constructs Projectile directly (no slime.spit call, no double-cost); fused-branch consumes exactly SLIME_DAZE_COST + emits daze_fire + flags projectile applies_daze_stun=True; double-cost resolution documented in IMPLEMENTATION-NOTES (W#1 closure); test_daze_shot.py Test 1 + Test 2 GREEN; Phase 32 regression suite preserved.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: main.py per-frame projectile-vs-enemy AABB scan + Boss-no-raise regression test</name>
  <files>main.py, tests/test_daze_shot.py</files>
  <read_first>
    - main.py:780-832 (locate the projectile.update loop at lines 787-791 and the door projectile-hit scan at line 832 — the new enemy-AABB scan goes BETWEEN them)
    - main.py:780 (mole.update call — the boss already handles its own projectile-vs-self contact at boss.py:106-111; do NOT duplicate that path)
    - src/entities/projectile.py (verify applies_daze_stun + STUN_DURATION_FRAMES from Task 1)
    - src/entities/enemies.py (verify Enemy.stun_timer added by Plan 03 Task 1; Snail/Bat constructors `Snail(x, y, game=None)`, `Bat(x, y, game=None)`)
    - src/entities/boss.py (verify Mole class has NO stun_timer field — the regression test asserts contact does not raise)
    - tests/test_daze_shot.py (Wave 0 stubs — Task 3 adds Test 3 + Test 4 OR unskips them if Wave 0 stubbed all four)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-CONTEXT.md (D-17: "Daze-on-hit effect: stuns enemies briefly... new stun primitive on regular enemies is planner discretion — may stay TBD if the existing logic isn't reusable" — Phase 33 plan ships the wiring, NOT defers)
  </read_first>
  <behavior>
    - main.py:Game.update gains a new per-frame loop AFTER the projectile.update loop at line 791 (after `self.projectiles = [p for p in self.projectiles if p.is_active]`) and BEFORE the door scan at line 826.
    - The loop iterates `for proj in self.projectiles: for enemy in self.enemies:` and on AABB intersection:
      - If `proj.applies_daze_stun` is True AND the enemy is alive AND `hasattr(enemy, "stun_timer")`:
        - Sets `enemy.stun_timer = max(getattr(enemy, "stun_timer", 0), STUN_DURATION_FRAMES)` (uses max so an in-flight stun isn't shortened).
        - Sets `proj.is_active = False` (consumes the projectile per existing lifecycle).
        - Breaks the inner enemy loop (one projectile = one stun; daze does NOT chain).
    - The boss (Mole) is NOT iterated by this scan — boss is `self.mole`, not a member of `self.enemies` (verified via main.py:780). Boss projectile-contact remains in boss.py:106-111 (sets VULNERABLE).
    - Boss-no-raise (W#6 closure): a regression test in test_daze_shot.py constructs a daze-flagged Projectile and a Mole, calls `mole.update_emerging(projectiles=[proj], player=...)`, and asserts no exception is raised. The hasattr-guard in main.py is irrelevant here because the test verifies the EXISTING boss code path (boss.py:106-111) handles a daze-flagged projectile gracefully — boss.py reads `p.x, p.y, p.w, p.h` and `p.is_active`, NEVER touches `p.applies_daze_stun`, so the field's presence is a true no-op for the boss.
    - Test 3 in test_daze_shot.py constructs Player + Slime + Snail + a daze-flagged Projectile in self.projectiles, calls Game.update once (or directly calls the new contact-scan helper), and asserts `snail.stun_timer == STUN_DURATION_FRAMES` AND `proj.is_active == False`.
  </behavior>
  <action>
    Step 1 — Add the import at the top of main.py (or near the existing `from src.entities.projectile import ...` if one already exists; otherwise alongside the other entity imports):

    ```python
    from src.entities.projectile import STUN_DURATION_FRAMES
    ```

    If main.py does NOT currently import from src.entities.projectile (it may rely on slime.spit returning Projectile instances), add the line in the entity-imports block.

    Step 2 — Edit `main.py` Game.update. Locate lines 787-791:

    ```python
            # Update secondary entities
            for p in self.projectiles:
                stain = p.update(self.cam_x, self.cam_y)
                if stain:
                    self.stains.append(stain)
            self.projectiles = [p for p in self.projectiles if p.is_active]
    ```

    IMMEDIATELY AFTER the `self.projectiles = [...]` filter line and BEFORE the next block (the `for s in self.stains:` loop at line 793), insert:

    ```python
            # Phase 33 D-17 (Blocker #2 closure): per-frame projectile-vs-enemy
            # AABB scan. When a daze-flagged projectile (applies_daze_stun=True,
            # set in player.py fused-branch) intersects an alive enemy with a
            # stun_timer field (added by Plan 03 Task 1 to Enemy base class),
            # apply the stun and consume the projectile. Boss (self.mole) is
            # NOT scanned here — boss handles its own projectile-contact at
            # boss.py:106-111 (sets VULNERABLE state) and has no stun_timer.
            for proj in self.projectiles:
                if not getattr(proj, "applies_daze_stun", False):
                    continue
                if not proj.is_active:
                    continue
                for enemy in self.enemies:
                    if not getattr(enemy, "is_alive", True):
                        continue
                    if not hasattr(enemy, "stun_timer"):
                        continue
                    # AABB intersection (Projectile.w/h vs Enemy.w/h)
                    if (proj.x < enemy.x + enemy.w
                            and proj.x + proj.w > enemy.x
                            and proj.y < enemy.y + enemy.h
                            and proj.y + proj.h > enemy.y):
                        # max() preserves in-flight stuns of equal-or-greater
                        # duration; daze never SHORTENS an existing stun.
                        enemy.stun_timer = max(enemy.stun_timer, STUN_DURATION_FRAMES)
                        proj.is_active = False
                        break  # one projectile = one stun (no chain)
            # Re-filter projectiles consumed by the daze-stun scan.
            self.projectiles = [p for p in self.projectiles if p.is_active]
    ```

    Step 3 — Add Test 3 + Test 4 to `tests/test_daze_shot.py`. Plan 01 may have already stubbed all four tests — if so, REMOVE the skip decorator on Test 3 and Test 4. If Plan 01 only stubbed Test 1 + Test 2, ADD the new tests.

    Test 3 — daze stun applies on Snail contact via main.py loop:

    ```python
    @pytest.mark.skip(reason="Wave 2/3 — Task 3 unskips after main.py wiring")
    def test_daze_stun_applies_on_snail_contact(mock_level, mock_slime, make_game_with_fusion):
        """Phase 33 D-17 / Blocker #2 closure: daze-flagged projectile
        intersecting an alive Snail sets snail.stun_timer and consumes the
        projectile via main.py's per-frame contact-scan loop."""
        from src.entities.projectile import Projectile, STUN_DURATION_FRAMES
        from src.entities.enemies import Snail

        game = make_game_with_fusion()
        # Place Snail at known position; spawn projectile overlapping its AABB
        snail = Snail(50, 50)
        assert snail.stun_timer == 0  # Plan 03 Task 1 default
        game.enemies = [snail]

        # Direct daze-flagged projectile at snail's position
        proj = Projectile(50, 50, 1, 0, mock_level)
        proj.applies_daze_stun = True
        game.projectiles = [proj]

        # Run one update tick — exercises the new contact-scan loop
        # (alternative: extract scan into a helper and call it directly;
        # planner-discretion. The test invariant: after one frame, snail is
        # stunned AND projectile is consumed.)
        game.update()

        assert snail.stun_timer == STUN_DURATION_FRAMES, (
            f"Expected stun_timer={STUN_DURATION_FRAMES}, got {snail.stun_timer}"
        )
        assert proj not in game.projectiles or not proj.is_active, (
            "Daze-flagged projectile must be consumed on enemy contact"
        )
    ```

    Test 4 — Boss contact does NOT raise (W#6 closure regression):

    ```python
    @pytest.mark.skip(reason="Wave 2/3 — Task 3 unskips after main.py wiring")
    def test_daze_projectile_boss_contact_does_not_raise(mock_level):
        """Phase 33 D-17 / W#6 closure: a daze-flagged projectile contacting
        the Boss (Mole.update_emerging at boss.py:106-111) must NOT raise.
        Boss has no stun_timer field; the existing boss code reads
        proj.x/y/w/h/is_active only and never touches applies_daze_stun.
        This test is the regression contract that lets us safely DROP
        boss.py from files_modified."""
        from src.entities.projectile import Projectile
        from src.entities.boss import Mole
        from unittest.mock import MagicMock

        # Construct daze-flagged projectile at Mole's spawn position
        proj = Projectile(100, 100, 1, 0, mock_level)
        proj.applies_daze_stun = True

        mole = Mole(100, 100, mock_level)
        mole.state = "EMERGING"
        mole.state_timer = 30  # avoid rock-throw frames (20, 60)

        player_stub = MagicMock()
        player_stub.x = 200; player_stub.y = 200; player_stub.w = 8; player_stub.h = 16

        # Must not raise — even though projectile has applies_daze_stun set,
        # Mole.update_emerging only reads p.x/y/w/h/is_active.
        try:
            mole.update_emerging([proj], player_stub, slime=None)
        except Exception as e:
            pytest.fail(f"Boss contact with daze-flagged projectile raised: {e!r}")

        # Boss should have transitioned to VULNERABLE (existing boss behavior
        # unaffected by the daze flag) — the projectile contact still works.
        assert mole.state == "VULNERABLE", (
            f"Boss must transition to VULNERABLE on projectile hit "
            f"regardless of daze flag; got {mole.state}"
        )
        assert proj.is_active == False, "Boss code consumes projectile via is_active=False"
    ```

    Step 4 — Verify `tests/test_daze_shot.py` now has 4 test functions and the skip decorators on Test 3 + Test 4 are REMOVED (or never added — depends on Wave 0 stub state). After this task, ALL four tests must run live.

    Step 5 — Run the full daze_shot suite to confirm all four tests are GREEN:

    ```bash
    pytest tests/test_daze_shot.py -x -v
    ```

    Expected: 4 passed, 0 failed, 0 skipped.
  </action>
  <verify>
    <automated>pytest tests/test_daze_shot.py tests/test_destructive_drill.py tests/test_drill_dive_parity.py tests/test_fusion_fsm.py -x -v</automated>
  </verify>
  <acceptance_criteria>
    - `grep "applies_daze_stun" main.py` returns at least 1 match (the guard in the new scan loop)
    - `grep "STUN_DURATION_FRAMES" main.py` returns at least 2 matches (import + use site)
    - `grep "stun_timer = max" main.py` returns 1 match (the application line)
    - **Inserted at correct site:** `python -c "src=open('main.py').read(); idx=src.index('per-frame projectile-vs-enemy'); pre=src[:idx]; assert 'self.projectiles = [p for p in self.projectiles if p.is_active]' in pre, 'New scan must come AFTER projectile.update filter'; assert pre.rfind('door.update') < idx if 'door.update' in pre else True; print('OK')"` exits 0
    - `grep -c "^def test_" tests/test_daze_shot.py` returns 4 (Test 1 + Test 2 + Test 3 + Test 4)
    - `grep -c "@pytest.mark.skip" tests/test_daze_shot.py` returns 0 (no remaining skips after Task 2 and Task 3 unskip cycles)
    - `grep "test_daze_stun_applies_on_snail_contact" tests/test_daze_shot.py` returns at least 1 match
    - `grep "test_daze_projectile_boss_contact_does_not_raise" tests/test_daze_shot.py` returns at least 1 match
    - `pytest tests/test_daze_shot.py -x -v` exits 0 (all 4 tests GREEN)
    - `pytest tests/test_destructive_drill.py -x -v` exits 0 (Plan 03 work preserved)
    - `pytest tests/test_drill_dive_parity.py tests/test_fusion_fsm.py -x -v` exits 0 (Phase 32 invariants preserved)
    - `pytest tests/ -x -q` exits 0 (full suite GREEN)
    - **Boss-no-raise regression (W#6 closure):** Test 4 (`test_daze_projectile_boss_contact_does_not_raise`) is the new contract that lets us drop boss.py from `files_modified` — the test asserts boss.py:106-111 already handles a daze-flagged projectile gracefully without modification.
  </acceptance_criteria>
  <done>main.py per-frame projectile-vs-enemy AABB scan inserted between projectile.update loop and door scan; daze-flagged projectiles consumed on enemy contact and set enemy.stun_timer = STUN_DURATION_FRAMES (max-preserving); boss path is intentionally NOT modified (Test 4 regression locks in graceful no-op); all 4 tests in test_daze_shot.py GREEN; full suite GREEN; Blocker #2 + W#6 closed.</done>
</task>

</tasks>

<verification>
- Full pytest suite: `pytest tests/ -x -q` exits 0.
- Boss contact path: `pytest tests/test_daze_shot.py::test_daze_projectile_boss_contact_does_not_raise -x -v` GREEN — confirms boss.py:106-111 handles a daze-flagged projectile without modification (W#6 graceful-no-op contract).
- Cancel-spam guard manual smoke (post-Plan 06): rapidly tap Z mid-WINDUP-cancel — daze must NOT fire and juice must NOT drain (Pitfall 4 closure).
- Phase 32 regression: drill_dive_parity + fusion_fsm + pogo all GREEN.
- Daze-stun delivery (D-17 full): drill into a daze-stunned Snail in playtest — Snail stays frozen for ~60 frames after projectile contact (manual confirmation in Plan 06 D-K2 / D-K5).
- No double-cost (W#1): `tests/test_daze_shot.py::test_fused_tap_fires_daze` asserts EXACT cost equality.
</verification>

<success_criteria>
- `not self.is_fused` gate removed from player.py:197
- Fused-branch constructs Projectile directly (no slime.spit call); consumes SLIME_DAZE_COST exactly once (no double-cost — W#1 closure)
- Cancel-spam guard via juice pre-check
- daze_fire event emitted from fused-branch only
- applies_daze_stun flag set on fused-branch projectiles
- main.py per-frame scan applies STUN_DURATION_FRAMES to enemy.stun_timer at projectile-vs-enemy contact (Blocker #2 closure — D-17 stun half delivered)
- Boss path unchanged; Test 4 locks in graceful no-op (W#6 closure — boss.py NOT in files_modified)
- All 4 tests in test_daze_shot.py GREEN
- Full suite GREEN; Phase 32 regression suite preserved
</success_criteria>

<output>
After completion, create `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-04-SUMMARY.md` per @$HOME/.claude/get-shit-done/templates/summary.md.
</output>
