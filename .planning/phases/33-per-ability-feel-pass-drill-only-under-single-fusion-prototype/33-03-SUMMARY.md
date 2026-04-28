---
phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
plan: 03
subsystem: fusion
tags: [fusion, drill-dive, combat, event-bus, enemy, stun-primitive, aabb]

# Dependency graph
requires:
  - phase: 32-fusion-manager-protocol-refactor
    provides: DrillDive class on_tick skeleton + TickResult contract this plan extends with the enemy-AABB scan
  - phase: 33-per-ability-feel-pass (plan 01)
    provides: tests/test_destructive_drill.py RED stubs (4 skipped tests this plan unskips and turns GREEN)
  - phase: 33-per-ability-feel-pass (plan 02)
    provides: tuning.DRILL_ENEMY_COST schema-seed (15.0) this plan reads at the new use-site
  - phase: 32.1-fusion-design-destructive-drill-relock
    provides: FUSION-DESIGN.md § Drill-Dive Contract → Enemy Interaction subsection (D-03/D-04/D-05) this plan implements

provides:
  - DRILL_DAMAGE = 1 module constant in src/fusion/drill_dive.py (Phase 33 D-04 hardcoded gameplay constant)
  - DrillDive._scan_and_damage_enemies private helper (iterates ALL intersecting alive enemies; calls take_damage + slime.consume + event_bus.emit per hit; no return-on-first)
  - on_tick wires the scan AFTER tile-coord block and BEFORE solid-landing block (Pattern 1 ordering — preserves Phase 32 v1.3 parity)
  - drill_enemy_hit event surface in event_bus dispatch (with x/y pixel-coord kwargs)
  - Enemy.stun_timer field on base Enemy class (set to 0 in __init__; groundwork for Plan 04 daze-shot)
  - Snail.update + Bat.update early-return guard when stun_timer > 0 (decrements timer; freezes movement/AI)
  - 33-IMPLEMENTATION-NOTES.md — documents Pitfall 2 juice-clamp option (a) decision + Plan 04 stun-primitive carry-over rationale

affects: [33-04 daze-shot-implementation, 33-05 polish-tuning, 33-06 debug-warps-tuning-feel-targets]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Multi-target AABB scan in fusion ability (vs. pogo's return-on-first-hit) — drill iterates and applies effects to every intersecting enemy in a single frame"
    - "Stun primitive at Enemy base class with subclass early-return guard — analog of Player.invuln_timer; reusable surface for any future stun source (not just daze)"
    - "Juice-clamp option (a) ordering invariant: same-frame full damage + Exit on next frame's juice check (matches existing block-break semantics)"

key-files:
  created:
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-IMPLEMENTATION-NOTES.md
  modified:
    - src/fusion/drill_dive.py
    - src/entities/enemies.py
    - tests/test_destructive_drill.py
    - tests/test_enemies.py

key-decisions:
  - "Juice-clamp option (a): all enemies take damage in same frame; juice clamps to 0; Exit (b) fires NEXT frame — matches block-break semantics; alternative (b/c) rejected as harder to predict and inconsistent"
  - "Stun primitive shipped now (not deferred): 5-line addition is cheaper than dragging into Plan 04; boss intentionally untouched (own state machine)"
  - "Test 3 (test_drill_enemy_contact_does_not_request_exit) passes vacuously by absence pre-implementation — kept as a guard against future regressions even though it was technically GREEN under the old code path"
  - "tuning.DRILL_ENEMY_COST appears 2x in drill_dive.py (1 docstring reference + 1 use-site call) — plan AC4 said '1 match' but the docstring naturally references the same constant; use-site count is exactly 1 as specified"

patterns-established:
  - "Drill chain ordering: tile-break first (return-on-hit), enemy-scan second (continue-through), solid-landing third (return-on-hit). The middle step is the only continue-through step in the on_tick chain."
  - "Test scaffolds with @pytest.mark.skip placeholders: subsequent waves remove the decorator atomically as part of the implementing task's RED commit (not as a separate cleanup task)"

requirements-completed: [FUS-06]

# Metrics
duration: 7min
completed: 2026-04-28
---

# Phase 33 Plan 03: Destructive-Drill Implementation Summary

**Drill in flight that intersects an alive enemy AABB now deals DRILL_DAMAGE=1, drains tuning.DRILL_ENEMY_COST juice, emits drill_enemy_hit, and continues drilling — plus Enemy.stun_timer primitive groundwork for Plan 04 daze-shot.**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-04-28T17:28:45Z
- **Completed:** 2026-04-28T17:35:31Z
- **Tasks:** 2 (both TDD: RED → GREEN)
- **Files modified:** 4 (2 source: drill_dive.py + enemies.py; 2 test: test_destructive_drill.py + test_enemies.py)
- **Files created:** 1 (33-IMPLEMENTATION-NOTES.md)

## Accomplishments

- `DRILL_DAMAGE = 1` module constant in `src/fusion/drill_dive.py` per D-04 (hardcoded gameplay constant; matches POGO_DAMAGE numerically — drill's "upgrade" relative to pogo is structural via per-frame contact, not damage value)
- `DrillDive._scan_and_damage_enemies` helper iterates ALL intersecting alive enemies and applies per-hit `take_damage(DRILL_DAMAGE)` + `slime.consume(tuning.DRILL_ENEMY_COST)` + `event_bus.emit("drill_enemy_hit", x=..., y=...)` (mirrors `pogo._touching_enemy` AABB shape but does NOT return on first hit, does NOT request_exit)
- `on_tick` chain reordered to: (1) tile-break → (2) enemy-scan → (3) solid-landing — preserves Phase 32 v1.3 parity (RESEARCH § Pattern 1) and ensures CRACKED_V tile drilling still costs juice and emits drill_block_break
- `Enemy.stun_timer = 0` field on base class with subclass early-return guards in `Snail.update` and `Bat.update` (decrement + return when > 0); Boss/Mole intentionally untouched
- All 4 destructive-drill tests in `tests/test_destructive_drill.py` GREEN (was RED via Plan 01 stubs); 5 new stun_timer tests in `tests/test_enemies.py` GREEN
- Phase 32 regression suite intact: `test_drill_dive_parity` (6 tests) + `test_fusion_fsm` (5 tests) + `test_fusion` + `test_fusion_protocol` + `test_pogo` + `test_event_bus` all GREEN (67 passed, 1 pre-existing skip)
- 33-IMPLEMENTATION-NOTES.md captures Pitfall 2 juice-clamp option (a) rationale and Plan 04 stun-primitive carry-over decision

## Task Commits

Each task was TDD-committed atomically (test → feat):

1. **Task 1 RED: Failing tests for Enemy.stun_timer primitive** — `c36a16a` (test)
   - tests/test_enemies.py: 5 RED tests covering Snail/Bat init, early-return guard, default-path preservation
2. **Task 1 GREEN: Enemy.stun_timer primitive + Snail/Bat early-return guards** — `f2bb0d0` (feat)
   - src/entities/enemies.py: `self.stun_timer = 0` on base __init__; decrement+return guard in Snail.update + Bat.update
3. **Task 2 RED: Unskip 4 destructive-drill RED tests for Wave 2 GREEN** — `355dcce` (test)
   - tests/test_destructive_drill.py: removed 4 `@pytest.mark.skip` placeholders
4. **Task 2 GREEN: Destructive-drill enemy AABB scan + DRILL_DAMAGE constant** — `d23da22` (feat)
   - src/fusion/drill_dive.py: DRILL_DAMAGE=1 + _scan_and_damage_enemies helper + on_tick wiring
   - .planning/phases/33-.../33-IMPLEMENTATION-NOTES.md: created with juice-clamp + stun-primitive notes

## Files Created/Modified

- `src/fusion/drill_dive.py` — Added `DRILL_DAMAGE = 1` module constant; added `_scan_and_damage_enemies` private helper method; inserted scan call in on_tick between tile-break and solid-landing branches
- `src/entities/enemies.py` — Added `self.stun_timer = 0` to base `Enemy.__init__`; added stun-decrement early-return guard at top of `Snail.update` and `Bat.update`
- `tests/test_enemies.py` — Added 5 stun_timer tests (init, early-return, default-path preservation for both Snail and Bat)
- `tests/test_destructive_drill.py` — Removed 4 `@pytest.mark.skip` placeholders so Plan 01 stubs run against Plan 03 implementation
- `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-IMPLEMENTATION-NOTES.md` — Created with juice-clamp option (a) rationale + Plan 04 stun-primitive carry-over

## Decisions Made

1. **Juice-clamp option (a) confirmed and documented.** All enemies in the same frame take damage; `slime.consume` clamps juice to 0 via its existing `max(0.0, ...)` guard; Exit (b) fires on the NEXT frame's step-2 juice-empty check (existing on_tick line 134). This matches block-break semantics (drill pays `DRILL_CRACKED_V_COST` on the same frame as the break regardless of remaining juice) and lets the player feel rewarded for the kill chain even when juice runs out. Verified by `test_drill_juice_starvation_after_kill_chain` (5 enemies + 30 juice + 15 cost → all 5 hit, juice=0, first call doesn't exit, second call exits).

2. **Stun primitive shipped now, not deferred.** Plan 03 RESEARCH and CONTEXT both flagged this as Open Q #1. Cost is ~10 lines (1 base init + 4 lines × 2 subclasses); deferring would leave Plan 04 (daze-shot) without a place to write its `stun_timer = STUN_DURATION_FRAMES`. Boss intentionally untouched — its own state machine (`BURROWED/EMERGING/VULNERABLE/DYING` plus separate `state_timer`) is not a reusable stun primitive surface, and Plan 04 only flags daze-stun on regular enemies.

3. **Test 3 (`test_drill_enemy_contact_does_not_request_exit`) kept despite vacuous pre-impl pass.** This test asserts a *negative* property — that the on_tick scan does NOT produce `request_exit=True`. Pre-implementation, the test passed by absence (no enemy scan existed). Post-implementation, it still passes. The test stays as a regression guard against any future change that might accidentally route enemy contact into `solid_landing` exit (D-03 invariant violation).

## Deviations from Plan

None — plan executed exactly as written.

The plan's Task 1 acceptance criterion "AC4: tuning.DRILL_ENEMY_COST returns 1 match" was technically off-by-one because the helper docstring naturally describes the constant (`drains tuning.DRILL_ENEMY_COST juice...`), giving `grep` 2 matches in `src/fusion/drill_dive.py`. The substantive intent (one use-site call) is satisfied — there is exactly 1 occurrence at the actual code call (line 260: `slime.consume(tuning.DRILL_ENEMY_COST)`). Documented here per "minor clarification" guidance, not flagged as a deviation since no behavior changed and no unplanned work was done.

The plan's Task 2 acceptance criterion AC5 ("`request_exit` count unchanged from pre-plan") is verified semantically:
- Pre-plan: 2 `request_exit=True` call sites in TickResult constructions.
- Post-plan: 2 `request_exit=True` call sites (juice_empty + solid_landing).
- The grep formula in the plan (`grep -v '^#'`) excludes only line-start `#`-comments and double-counts indented comment references; the underlying invariant (no new exit routes added by the enemy scan) holds exactly.

## Issues Encountered

- **Pre-existing test failures outside this plan's scope.** Running the full `pytest tests/` revealed 10 unique pre-existing failures in `test_ldtk_migration.py`, `test_phase05_nyquist.py`, `test_phase22.py`, `test_physics.py`, `test_sprite_assets.py`, `test_tuning.py` — same set documented in Plan 02's Issues Encountered. Verified pre-existing via `git stash` round-trip: stashed RED+GREEN diff, ran the suite, observed identical 10 failures. None of these tests touch the drill or enemy code paths. Out of scope per execute-plan.md SCOPE BOUNDARY rule.
- **`@pytest.mark.skip` removal mechanics.** The plan's Step 5 noted that Plan 01 might have used `pytest.importorskip` (which becomes a no-op once `DRILL_DAMAGE` exists) instead of per-test `@pytest.mark.skip`. Inspection showed Plan 01 used BOTH: `pytest.importorskip` at module level (which became a no-op as expected) AND `@pytest.mark.skip` decorators on each of the 4 tests. Removed all 4 decorators in a separate commit (the RED gate commit) before implementing GREEN, as per plan.

## TDD Gate Compliance

This plan follows the per-task TDD pattern (each task has its own RED → GREEN cycle). Both tasks committed in the correct gate sequence:
- Task 1: `c36a16a` (test = RED) → `f2bb0d0` (feat = GREEN). RED gate verified failing pre-impl (`AttributeError: 'Snail' object has no attribute 'stun_timer'`); GREEN gate verified all 5 new tests + 4 prior tests pass.
- Task 2: `355dcce` (test unskip = RED) → `d23da22` (feat = GREEN). RED gate verified 3/4 tests fail with `ImportError: cannot import name 'DRILL_DAMAGE'`; GREEN gate verified all 4 destructive-drill tests + 6 parity + 5 FSM tests pass.

No REFACTOR commits — implementations were minimal and clean (no cleanup needed).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Plan 33-04 (daze-shot-implementation)** can now write `enemy.stun_timer = STUN_DURATION_FRAMES` when a daze projectile contacts an enemy; the surface is in place and the early-return guards in Snail/Bat will freeze them visibly during the daze window.
- **Plan 33-05 / Plan 33-06** can now expect drill to actually kill regular enemies during a fused dive — opens the door to feel-pass tuning of `DRILL_ENEMY_COST` (currently schema-seeded at 15.0 from Plan 02) via the live panel without any further code change.
- **No blockers** for downstream Phase 33 plans.
- Phase 32 destructive-drill block-break + new enemy-AABB scan share the same `on_tick` chain — future work that adds another contact effect (e.g., hazards, projectiles) should slot into the same insertion point with the same continue-through vs. return-on-hit distinction made explicit in Decision 1 above.

## Self-Check: PASSED

Verifications run:

- `[ -f src/fusion/drill_dive.py ]` → FOUND (modified)
- `[ -f src/entities/enemies.py ]` → FOUND (modified)
- `[ -f tests/test_enemies.py ]` → FOUND (modified)
- `[ -f tests/test_destructive_drill.py ]` → FOUND (modified)
- `[ -f .planning/phases/33-.../33-IMPLEMENTATION-NOTES.md ]` → FOUND (created)
- `git log --oneline | grep c36a16a` → FOUND (Task 1 RED commit)
- `git log --oneline | grep f2bb0d0` → FOUND (Task 1 GREEN commit)
- `git log --oneline | grep 355dcce` → FOUND (Task 2 RED commit)
- `git log --oneline | grep d23da22` → FOUND (Task 2 GREEN commit)
- All Task 1 acceptance criteria (5 grep + python -c invariants) → PASSED
- All Task 2 acceptance criteria (9 grep + pytest invariants) → PASSED
- Plan-level verification: `pytest tests/test_destructive_drill.py tests/test_drill_dive_parity.py tests/test_fusion_fsm.py -x -v` → 15 passed
- Broader regression: `pytest tests/test_fusion.py tests/test_fusion_protocol.py tests/test_fusion_fsm.py tests/test_drill_dive_parity.py tests/test_destructive_drill.py tests/test_pogo.py tests/test_enemies.py tests/test_event_bus.py -q` → 67 passed, 1 pre-existing skip
- Pre-existing failures unchanged from baseline (verified via git stash round-trip)

---
*Phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype*
*Plan: 03 (destructive-drill-implementation)*
*Completed: 2026-04-28*
