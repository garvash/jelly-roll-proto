# Phase 33 Implementation Notes

Cross-plan implementation decisions captured during execution. Each section
attributes its plan source so wave-merge collisions are resolvable by reading
the plan-of-origin.

## Drill juice-clamp ordering on enemy hit

*Source: Plan 33-03 destructive-drill-implementation, Wave 2.*

Documents non-obvious implementation choice flagged by RESEARCH.md § Pitfall 2
/ Open Question 3.

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
   `tests/test_destructive_drill.py::test_drill_juice_starvation_after_kill_chain`.

**Alternatives rejected:**
- Option (b): juice-pre-check before each enemy hit — partial damage; first
  hit then exit. Rejected because it makes the rule harder to predict and
  conflicts with existing block-break semantics.
- Option (c): tally all damage then check before applying — adds bookkeeping
  complexity for no behavioral benefit.

## Daze-on-hit stun primitive

*Source: Plan 33-03 (primitive) + Plan 33-04 (consumer), Wave 2.*

**Decision:** Ship in Phase 33 (Open Question 1 resolution). 5-line
addition to `Enemy.__init__` (`self.stun_timer = 0`) + early-return guard
at top of subclass `update()` methods (Plan 03 Task 1). Plan 04
(daze-shot) sets `enemy.stun_timer = STUN_DURATION_FRAMES` when a daze
projectile contacts.

**Why ship vs. defer:** ~5 lines of code; the boss has its own state
machine that is NOT a reusable stun primitive (verified in RESEARCH);
deferring would leave daze-shot incomplete in this phase.

## Daze double-cost resolution (W#1 closure)

*Source: Plan 33-04 daze-shot-implementation, Wave 2.*

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
