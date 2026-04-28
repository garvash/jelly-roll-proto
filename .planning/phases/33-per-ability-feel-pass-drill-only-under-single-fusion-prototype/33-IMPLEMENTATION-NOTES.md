# Phase 33 Implementation Notes

Cross-plan implementation decisions captured during execution. Each section
attributes its plan source so wave-merge collisions are resolvable by reading
the plan-of-origin.

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
