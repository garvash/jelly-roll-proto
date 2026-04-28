---
phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
plan: 03
type: execute
wave: 2
depends_on: ["33-02"]
files_modified:
  - src/fusion/drill_dive.py
  - src/entities/enemies.py
  - src/anim/event_bus.py
  - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-IMPLEMENTATION-NOTES.md
autonomous: true
requirements: [FUS-06]
requirements_addressed: [FUS-06]
tags: [fusion, combat, event-bus, enemy]

must_haves:
  truths:
    - "Drill in flight that intersects an alive enemy AABB deals DRILL_DAMAGE, drains tuning.DRILL_ENEMY_COST juice, emits drill_enemy_hit, and continues drilling (no exit, no bounce)"
    - "Multi-enemy intersection in one frame damages all enemies and drains cost per hit"
    - "Drill takes NO damage from enemies during DIVING (D-06: no iframes knob; safety via offense)"
    - "v1.3 tile-interaction parity preserved (Phase 32 regression suite GREEN)"
    - "Enemy.stun_timer field exists on Enemy base class (groundwork for daze-shot stun in Plan 04)"
    - "drill_enemy_hit appears in event_bus dispatch traces"
  artifacts:
    - path: "src/fusion/drill_dive.py"
      provides: "DRILL_DAMAGE module constant + _scan_and_damage_enemies helper invoked from on_tick AFTER tile-collision and BEFORE solid-landing check"
      contains: "DRILL_DAMAGE"
    - path: "src/entities/enemies.py"
      provides: "stun_timer: int = 0 field on Enemy base class + decrement in subclass update() early-return guard"
      contains: "stun_timer"
    - path: ".planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-IMPLEMENTATION-NOTES.md"
      provides: "Documents the drill juice-clamp ordering choice (option (a): damage all enemies in same frame, Exit (b) on next frame)"
      contains: "juice-clamp"
  key_links:
    - from: "src/fusion/drill_dive.py:on_tick"
      to: "src/anim/event_bus.py"
      via: "event_bus.emit('drill_enemy_hit', x=..., y=...)"
      pattern: "drill_enemy_hit"
    - from: "src/fusion/drill_dive.py:_scan_and_damage_enemies"
      to: "src/entities/enemies.py:Enemy.take_damage"
      via: "enemy.take_damage(DRILL_DAMAGE)"
      pattern: "take_damage\\(DRILL_DAMAGE\\)"
---

<objective>
Implement the destructive-drill mechanic per D-03/D-04/D-05/D-13: drill in flight intersecting an alive enemy AABB deals damage, drains juice, emits `drill_enemy_hit`, continues through (no exit). Add `stun_timer` field to the Enemy base class as groundwork for the daze-shot stun primitive (Plan 04 will consume it).

Purpose: this plan delivers the first new gameplay rule of Phase 33 — the "drill is destructive" identity that resolves FUSION-DESIGN Open-Q #1 (drill iframes) structurally per D-06. PROJECT.md core fantasy "shoot to daze → drill to finish" requires drill to actually kill enemies; today drill only carves tiles.

Output: drill_dive.py extended with enemy-AABB scan; enemies.py base class has stun_timer; event_bus gains a new event name (no code change to event_bus.py — registry-free); IMPLEMENTATION-NOTES documents Pitfall 2 ordering choice.
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
@src/fusion/drill_dive.py
@src/fusion/pogo.py
@src/entities/enemies.py
@src/entities/slime.py
@src/anim/event_bus.py
@tests/test_destructive_drill.py
@tests/test_drill_dive_parity.py

<interfaces>
<!-- Existing on_tick skeleton (drill_dive.py:94-183 from Phase 32 verbatim port). -->
<!-- The new enemy-scan goes BETWEEN step 3 (tile_coord break-or-no-break) and -->
<!-- step 4 (solid-landing check). Per RESEARCH § Pattern 1: "tile-first preserves -->
<!-- Phase 32 v1.3 parity" — do NOT swap to enemy-first. -->

<!-- Existing AABB scan pattern in src/fusion/pogo.py:168-217 (mirror it but -->
<!-- iterate ALL intersecting enemies; do NOT return on first hit; do NOT -->
<!-- request_exit). -->

<!-- slime.consume(amount) clamps to max(0.0, juice - amount) per slime.py:223. -->
<!-- juice-empty check is at step 2 of on_tick BEFORE the enemy scan, so juice -->
<!-- depletes during enemy scan and Exit (b) fires on the NEXT frame -->
<!-- (option (a) ordering per RESEARCH Pitfall 2). -->

<!-- event_bus.emit signature: event_bus.emit(name: str, **kwargs) — no return. -->
<!-- Phase 31 subscribers consume `x=` `y=` pixel coords (main.py:282-304). -->

<!-- Enemy base class location: src/entities/enemies.py — verify exact class -->
<!-- name and __init__ before adding `self.stun_timer = 0`. Subclasses Snail, -->
<!-- Bat exist; their update() must early-return if stun_timer > 0 (decrement -->
<!-- before return so the timer ticks down). -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Enemy base class — stun_timer groundwork</name>
  <files>src/entities/enemies.py</files>
  <read_first>
    - src/entities/enemies.py (full file — locate Enemy base class __init__, Snail.update, Bat.update or whatever the subclass surface is)
    - src/entities/player.py:50 (analog: self.invuln_timer = 0 + decrement in update_timers)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-RESEARCH.md (§ Don't Hand-Roll: 5-line stun_timer addition; § Open Question 1: ship-vs-defer recommendation)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md (§ No Analog Found — invuln_timer analog reference)
  </read_first>
  <behavior>
    - Enemy base class `__init__` sets `self.stun_timer = 0`.
    - Each enemy subclass `update()` decrements stun_timer if > 0 and returns early WITHOUT advancing position/AI; this freezes movement during stun.
    - Existing behavior unchanged when stun_timer == 0 (default path runs normally).
    - The boss class is NOT modified by this task — boss has its own state machine; daze-shot stun on the boss is out-of-scope (Plan 04 only flags daze-stun on regular enemies for now).
  </behavior>
  <action>
    Step 1 — Read `src/entities/enemies.py` fully and identify:
    - The base class name (likely `Enemy`) and its `__init__` signature.
    - All subclasses with their own `update()` method (likely `Snail`, `Bat`).

    Step 2 — Add `self.stun_timer = 0` to the base `Enemy.__init__`:

    ```python
    # Phase 33 D-17 / Open Q #1: stun primitive for daze-on-hit. Plan 04
    # (daze-shot) sets stun_timer to a non-zero value when a daze projectile
    # hits this enemy. Each frame, subclass update() decrements and early-
    # returns. Analog: Player.invuln_timer (player.py:50).
    self.stun_timer = 0
    ```

    Add this line at the END of the existing `__init__` body (after all other field assignments). Do NOT introduce a `STUN_DURATION_FRAMES` constant in this plan — Plan 04 owns the consume/set side and will define the duration constant where the daze-stun is applied.

    Step 3 — In each subclass `update()`, add the stun-decrement guard at the TOP of the method (before any other logic). Example shape:

    ```python
    def update(self, *args, **kwargs):
        # Phase 33 D-17: stun primitive — frozen until timer reaches 0.
        if self.stun_timer > 0:
            self.stun_timer -= 1
            return
        # ... existing update logic unchanged ...
    ```

    Apply this guard to every subclass that has its own `update()` override. If the base class also has `update()`, add the guard there too so any future subclass without an override still honors stun. Do NOT modify Boss.update or Mole.update — boss daze interaction is out-of-scope per Plan 04 specifics.

    Step 4 — Verify no import cycles introduced (this change has no new imports; only one new field assignment + one early-return guard per subclass).
  </action>
  <verify>
    <automated>pytest tests/ -x -q -k "not destructive_drill and not daze_shot"</automated>
  </verify>
  <acceptance_criteria>
    - `grep "self.stun_timer = 0" src/entities/enemies.py` returns at least 1 match
    - `grep "self.stun_timer > 0" src/entities/enemies.py` returns at least 1 match per subclass that overrides update() (count subclasses first; minimum 1)
    - `grep "self.stun_timer -= 1" src/entities/enemies.py` returns at least 1 match
    - **Instance-level check (W#5 closure):** `python -c "from src.entities.enemies import Snail; s=Snail(0,0); assert s.stun_timer==0, f'expected stun_timer=0 on Snail instance, got {s.stun_timer}'; print('OK')"` outputs `OK` and exits 0 — verifies stun_timer is set on every fresh Enemy subclass instance via __init__ (NOT a vacuously-true class attribute check)
    - `pytest tests/ -x -q -k "not destructive_drill and not daze_shot"` exits 0 (no regressions to existing enemy tests)
    - `grep "stun_timer" src/entities/boss.py` returns NO match (boss intentionally untouched by this plan)
  </acceptance_criteria>
  <done>Enemy base class instances initialize self.stun_timer = 0; every regular-enemy subclass update() decrements and early-returns when timer > 0; boss class untouched; existing test suite GREEN.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: drill_dive.py — destructive-drill enemy AABB scan + DRILL_DAMAGE constant</name>
  <files>src/fusion/drill_dive.py, .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-IMPLEMENTATION-NOTES.md</files>
  <read_first>
    - src/fusion/drill_dive.py (full file — note module imports lines 22-25; module constants ~line 33; on_tick lines 94-183 with steps 1-5)
    - src/fusion/pogo.py:168-217 (the _touching_enemy + _damage_touched_enemy pattern to mirror)
    - src/anim/event_bus.py (verify emit signature: positional name, **kwargs payload)
    - src/entities/slime.py:220-232 (slime.consume() clamp behavior)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md (§ src/fusion/drill_dive.py — concrete code excerpts; § Shared Patterns — use-site reads)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-RESEARCH.md (§ Pitfall 2 — juice-clamp ordering option (a) recommendation)
    - .planning/FUSION-DESIGN.md (§ Drill-Dive Contract → Enemy Interaction subsection — D-03/D-04/D-05 contract source)
    - tests/test_destructive_drill.py (Wave 0 RED stubs; this task makes them GREEN)
  </read_first>
  <behavior>
    - Module-level `DRILL_DAMAGE = 1` constant added to drill_dive.py per D-04 (hardcoded gameplay constant; same value as POGO_DAMAGE).
    - New helper method `_scan_and_damage_enemies(self, player, slime) -> None` iterates `player.game.enemies`, applies AABB intersection test (mirror pogo.py:168-217 shape), and on each hit:
      - Calls `enemy.take_damage(DRILL_DAMAGE)` if the enemy has the method, else writes `enemy.hp = enemy.hp - DRILL_DAMAGE`.
      - Calls `slime.consume(tuning.DRILL_ENEMY_COST)`.
      - Emits `event_bus.emit("drill_enemy_hit", x=enemy.x + ew // 2, y=enemy.y + eh // 2)`.
    - The scan does NOT return TickResult, does NOT set request_exit; drill continues regardless.
    - Inserted in `on_tick` AFTER the tile-collision branch (currently the `if tile_coord:` block) and BEFORE the solid-landing branch (the `check_collision(player.x, player.y + 1, ...)` block) per RESEARCH Pattern 1 ordering rule.
    - Juice-clamp ordering: option (a) — all enemies in current frame take damage; juice clamps to 0 via `slime.consume`; Exit (b) fires on the NEXT frame's step-2 juice-empty check. Documented in 33-IMPLEMENTATION-NOTES.md.
  </behavior>
  <action>
    Step 1 — Add `DRILL_DAMAGE = 1` module constant to `src/fusion/drill_dive.py`. Locate the existing constant block near `EXPLOSION_SIZE_PX = 9` (~line 33) and add immediately after:

    ```python
    # Phase 33 D-04: drill damage per enemy AABB intersection per frame.
    # Hardcoded gameplay constant per CONTEXT recommendation (DAMAGE is a
    # gameplay choice, not a feel choice; same value as POGO_DAMAGE). Drill's
    # "upgrade" relative to pogo is structural via repeated-frame contact, not
    # numeric.
    DRILL_DAMAGE = 1
    ```

    Step 2 — Add the `_scan_and_damage_enemies` method to the `DrillDive` class. Place it AFTER the `on_tick` method (or before, planner discretion) at class-level indentation:

    ```python
    def _scan_and_damage_enemies(self, player, slime) -> None:
        """Phase 33 D-03/D-04/D-05: destructive-drill enemy AABB scan.

        Iterates ALL intersecting enemies in a single frame (vs. pogo's
        return-on-first-hit). Each hit deals DRILL_DAMAGE, drains
        tuning.DRILL_ENEMY_COST juice, and emits drill_enemy_hit. Drill
        continues regardless (no request_exit; mana-shield path irrelevant
        during DIVING per D-06).

        Juice-clamp ordering (Pitfall 2 / 33-IMPLEMENTATION-NOTES.md):
        option (a) — damage all enemies in the same frame, let slime.consume
        clamp to 0; Exit (b) fires on the NEXT frame's step-2 juice-empty
        check. Matches existing block-break semantics.
        """
        if not player.game:
            return
        enemies = getattr(player.game, "enemies", None)
        if not enemies:
            return
        for enemy in enemies:
            if not getattr(enemy, "is_alive", True):
                continue
            ew = getattr(enemy, "w", 0)
            eh = getattr(enemy, "h", 0)
            if (
                player.x < enemy.x + ew
                and player.x + player.w > enemy.x
                and player.y < enemy.y + eh
                and player.y + player.h > enemy.y
            ):
                if hasattr(enemy, "take_damage"):
                    enemy.take_damage(DRILL_DAMAGE)
                else:
                    enemy.hp = getattr(enemy, "hp", 0) - DRILL_DAMAGE
                slime.consume(tuning.DRILL_ENEMY_COST)
                event_bus.emit(
                    "drill_enemy_hit",
                    x=enemy.x + ew // 2,
                    y=enemy.y + eh // 2,
                )
    ```

    Step 3 — Insert the call to `_scan_and_damage_enemies` inside `on_tick`. Read the existing `on_tick` carefully, identify:
    - Step 3 (the `if tile_coord:` block that handles block-break and returns TickResult on success).
    - Step 4 (the `if player.level_map.check_collision(player.x, player.y + 1, ...)` solid-landing block).

    Insert the scan call BETWEEN steps 3 and 4 — i.e. immediately AFTER the close of the `if tile_coord:` block (or its `return TickResult(...)` exit) and BEFORE the `if player.level_map.check_collision(...)` line. Add an explanatory comment:

    ```python
    # *** Phase 33 D-03: destructive-drill enemy-AABB scan ***
    # Continue-through; does NOT request_exit. Tile-first preserves Phase 32
    # v1.3 parity (RESEARCH § Pattern 1 ordering rule). Mana-shield path is
    # irrelevant during DIVING per D-06.
    self._scan_and_damage_enemies(player, slime)
    ```

    Step 4 — Author `33-IMPLEMENTATION-NOTES.md` documenting the juice-clamp ordering choice (Pitfall 2). Create the file with:

    ```markdown
    # Phase 33: Implementation Notes

    > Created during Plan 03 execution. Documents non-obvious implementation
    > choices flagged by RESEARCH.md § Pitfall 2 / Open Question 3.

    ## Drill juice-clamp ordering on enemy hit

    **Decision:** Option (a) — damage all enemies in the same frame, let
    `slime.consume()` clamp juice to 0, Exit (b) fires on the NEXT frame's
    step-2 juice-empty check.

    **Why:**
    1. Matches existing block-break semantics (drill consumes
       `DRILL_CRACKED_V_COST = 20` on the same frame as the break, regardless
       of remaining juice).
    2. More rewarding feel ("you got the kill chain even though juice ran
       out").
    3. Naturally falls out of the existing per-frame on_tick step ordering —
       no special juice-pre-check between enemy iterations.
    4. Decision recorded in PLAN 03 acceptance criteria; verified by
       `tests/test_destructive_drill.py::test_drill_juice_empty_during_chain`.

    **Alternatives rejected:**
    - Option (b): juice-pre-check before each enemy hit — partial damage; first
      hit then exit. Rejected because it makes the rule harder to predict and
      conflicts with existing block-break semantics.
    - Option (c): tally all damage then check before applying — adds bookkeeping
      complexity for no behavioral benefit.

    ## Daze-on-hit stun primitive (continued in Plan 04)

    **Decision:** Ship in Phase 33 (Open Question 1 resolution). 5-line
    addition to `Enemy.__init__` (`self.stun_timer = 0`) + early-return guard
    at top of subclass `update()` methods (Plan 03 Task 1). Plan 04
    (daze-shot) sets `enemy.stun_timer = STUN_DURATION_FRAMES` when a daze
    projectile contacts.

    **Why ship vs. defer:** ~5 lines of code; the boss has its own state
    machine that is NOT a reusable stun primitive (verified in RESEARCH);
    deferring would leave daze-shot incomplete in this phase.
    ```

    Step 5 — Run the destructive-drill RED tests (which Plan 01 created with `pytest.mark.skip`). UNSKIP them by deleting the `@pytest.mark.skip(...)` decorator (Plan 01 added it specifically as a Wave 0 placeholder). After unskip, confirm all 4 tests in `test_destructive_drill.py` go GREEN.

    NOTE on test unskip mechanics: `tests/test_destructive_drill.py` was created with `pytest.importorskip("src.fusion.drill_dive", reason="Wave 2 will add DRILL_DAMAGE constant")` at module level — once `DRILL_DAMAGE` exists in drill_dive.py the importorskip becomes a no-op and the previously-marked tests run. If Plan 01 chose `pytest.mark.skip` per-test (instead of importorskip), executor must additionally remove those `@pytest.mark.skip` decorators on the 4 destructive-drill tests as part of this task.
  </action>
  <verify>
    <automated>pytest tests/test_destructive_drill.py tests/test_drill_dive_parity.py tests/test_fusion_fsm.py -x -v</automated>
  </verify>
  <acceptance_criteria>
    - `grep "^DRILL_DAMAGE = 1$" src/fusion/drill_dive.py` returns 1 match
    - `grep "_scan_and_damage_enemies" src/fusion/drill_dive.py` returns at least 2 matches (definition + call site)
    - `grep "drill_enemy_hit" src/fusion/drill_dive.py` returns at least 1 match (the event_bus.emit call)
    - `grep "tuning.DRILL_ENEMY_COST" src/fusion/drill_dive.py` returns 1 match
    - `grep "request_exit" src/fusion/drill_dive.py | grep -v '^#' | grep -c .` returns the SAME count as before this plan (no new request_exit added by the enemy scan; only existing tile-coord and solid-landing exits)
    - `pytest tests/test_destructive_drill.py -x -v` exits 0 (all 4 tests GREEN: hits-and-continues, multi-enemy chain, no-exit, juice-empty Exit-b)
    - `pytest tests/test_drill_dive_parity.py -x -v` exits 0 (Phase 32 v1.3 parity preserved)
    - `pytest tests/test_fusion_fsm.py -x -v` exits 0 (Phase 32 FSM contract preserved)
    - `cat .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-IMPLEMENTATION-NOTES.md | grep -c "juice-clamp"` returns at least 1
    - `cat .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-IMPLEMENTATION-NOTES.md | grep -c "Option (a)"` returns at least 1
  </acceptance_criteria>
  <done>DRILL_DAMAGE constant in place; _scan_and_damage_enemies helper iterates enemies and emits drill_enemy_hit per hit; on_tick calls the helper after tile-break and before solid-landing; juice-clamp ordering option (a) documented in 33-IMPLEMENTATION-NOTES.md; all 4 destructive-drill tests GREEN; Phase 32 regression tests GREEN.</done>
</task>

</tasks>

<verification>
- `pytest tests/ -x -q` runs the full suite GREEN (Phase 32 regression + Phase 33 destructive-drill all pass).
- v1.3 parity check: `pytest tests/test_drill_dive_parity.py -x -v` shows all Phase 32 cases still pass — destructive-drill is purely additive (continue-through, no exit, no state change).
- Drill chain manual smoke (post-Plan 06): drilling through 3 enemies with juice = 100 and DRILL_ENEMY_COST = 15 should kill all 3 and leave juice ~55.
- Pitfall 2 closure: `tests/test_destructive_drill.py::test_drill_juice_empty_during_chain` enforces option (a) — failing this test is a regression.
</verification>

<success_criteria>
- DRILL_DAMAGE = 1 module constant in drill_dive.py
- _scan_and_damage_enemies helper iterates ALL intersecting enemies (no return-on-first)
- Insertion site in on_tick: AFTER tile-coord branch, BEFORE solid-landing branch
- enemies.py base class has self.stun_timer = 0; subclasses early-return when stun_timer > 0
- 33-IMPLEMENTATION-NOTES.md documents juice-clamp ordering option (a)
- All 4 tests in test_destructive_drill.py GREEN
- Phase 32 regression suite (test_drill_dive_parity, test_fusion_fsm, test_pogo) GREEN
</success_criteria>

<output>
After completion, create `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-03-SUMMARY.md` per @$HOME/.claude/get-shit-done/templates/summary.md.
</output>
