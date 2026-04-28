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
   `tests/test_destructive_drill.py::test_drill_juice_starvation_after_kill_chain`.

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
