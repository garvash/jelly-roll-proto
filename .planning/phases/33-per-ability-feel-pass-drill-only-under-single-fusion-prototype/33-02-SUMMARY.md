---
phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
plan: 02
subsystem: tuning
tags: [fusion, tuning, schema, panel, pogo, charge-controller, physics-schema]

# Dependency graph
requires:
  - phase: 32-fusion-manager-protocol-refactor
    provides: ChargeController + Pogo modules with hardcoded WINDUP/REGEN/POGO constants this plan migrates
  - phase: 28-live-tuning-panel-mvp
    provides: panel.py FEEL_GROUPS + TAB_DEFS pipeline this plan extends with the new pogo group
  - phase: 24-tuning-foundation-schema-inversion
    provides: tuning._flat_index auto-build mechanism that exposes new schema keys as tuning.X attrs without code change
  - phase: 33-per-ability-feel-pass (plan 01)
    provides: Wave 0 test stubs in tests/test_tuning_migration.py (RED markers this plan would flip GREEN — note Plan 01 not merged into worktree base; tests verified via grep + live boot instead)
provides:
  - 6 migrated tuning keys (WINDUP_DURATION_FRAMES, ACCELERATED_REGEN_RATE, POGO_BOUNCE_VELOCITY, POGO_COOLDOWN_FRAMES, DRILL_ENEMY_COST, SLIME_DAZE_COST) live-readable via tuning.X
  - New tuning.pogo schema group pinned as the LAST key of tuning dict (W#7 deterministic ordering)
  - charge_controller.py + pogo.py free of module-level constants for migrated names; use-site reads in place
  - panel.py FEEL_GROUPS + Fuse-tab TAB_DEFS extended with the new pogo group (17 sliders in Fuse tab — existing scroll absorbs)
affects: [33-03 destructive-drill-implementation, 33-04 daze-shot-implementation, 33-06 debug-warps-tuning-feel-targets]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Phase 25 use-site-read pattern extended to two more fusion files (charge_controller.py + pogo.py)"
    - "Schema-group key-order invariant enforced in plan acceptance criteria (W#7: pogo MUST be last; pogo MUST immediately follow gates)"

key-files:
  created: []
  modified:
    - assets/physics-schema.json
    - src/fusion/charge_controller.py
    - src/fusion/pogo.py
    - src/ui/panel.py
    - tests/test_pogo.py

key-decisions:
  - "Reorder tuning groups so save/death/save_point come before gates, gates before pogo — preserves both invariants (pogo last + pogo adjacent to gates) without introducing scope churn"
  - "Phase 32 D-18 superseded by Phase 33 D-02 for POGO_BOUNCE_VELOCITY + POGO_COOLDOWN_FRAMES; test_pogo.py::test_pogo_constants_hardcoded updated to assert the new contract (constants in tuning.* for those two; POGO_INITIAL_DY + POGO_DAMAGE remain hardcoded)"
  - "DRILL_ENEMY_COST seeded at 15.0 (midpoint of CONTEXT D-05's 10–20 range) for predictable Phase 33 starting feel"
  - "SLIME_DAZE_COST seeded at 20.0 per CONTEXT D-17 baseline"

patterns-established:
  - "Plans that migrate hardcoded constants to schema MUST update Phase-N regression tests asserting the old contract — Phase 32 D-18 hardcoded-only test was superseded inline as part of this plan, mirroring how the migration itself supersedes the design decision"
  - "Schema-group ordering invariants are first-class plan acceptance criteria — verified inline via python -c keys[-1]=='pogo' assertion, not just by JSON validity"

requirements-completed: [FUS-06]

# Metrics
duration: 6min
completed: 2026-04-28
---

# Phase 33 Plan 02: Tuning Migration Schema Summary

**Migrated 6 hardcoded constants to physics-schema.json with deterministic key-ordering; charge_controller + pogo now read tuning.X at use-site; panel surfaces all 6 new keys in the Fuse tab.**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-04-28T17:15:31Z
- **Completed:** 2026-04-28T17:21:19Z
- **Tasks:** 2
- **Files modified:** 5 (1 schema, 2 fusion modules, 1 panel, 1 regression test update)

## Accomplishments

- 6 new tuning keys live via `tuning.X` attribute access at schema-seed values matching every prior hardcoded baseline (Pitfall 5 closure — frame-for-frame behavior unchanged)
- Schema key-order invariant enforced and verified: `tuning` dict ends with `..., gates, pogo` so downstream tooling (panel TAB_DEFS, schema-walking helpers) sees stable diffs (W#7 closure)
- `charge_controller.py` lost two module-level constants (WINDUP_DURATION_FRAMES, ACCELERATED_REGEN_RATE) and gained two use-site `tuning.X` reads (Phase 25 pattern); `pogo.py` lost two (POGO_BOUNCE_VELOCITY, POGO_COOLDOWN_FRAMES) and gained the same; POGO_INITIAL_DY + POGO_DAMAGE preserved per D-02
- Panel `FEEL_GROUPS` now allowlist-includes `pogo`; `TAB_DEFS` "Fuse" tab routes the new pogo group; 17-slider Fuse tab confirmed acceptable (existing scroll handles, no new tab required per RESEARCH Pitfall 7)
- Phase 32 fusion regression suite (39 tests across test_fusion_fsm + test_drill_dive_parity + test_pogo + test_tuning_livereach + test_fusion + test_fusion_protocol) all GREEN

## Task Commits

Each task committed atomically:

1. **Task 1: Schema additions — 6 new keys + new pogo group (pinned as last tuning key)** — `eddada3` (feat)
   - assets/physics-schema.json: 6 new keys + new pogo group + reorder so pogo is last
   - src/ui/panel.py: FEEL_GROUPS + TAB_DEFS extended with `pogo`
   - tests/test_pogo.py: test_pogo_constants_hardcoded updated for D-02 supersession of D-18

2. **Task 2: charge_controller.py + pogo.py — delete module constants, switch to use-site reads** — `1352253` (refactor)
   - src/fusion/charge_controller.py: delete 2 module constants, add 2 use-site `tuning.X` reads
   - src/fusion/pogo.py: delete 2 module constants, add `from src.core import tuning` import, add 2 use-site `tuning.X` reads, preserve POGO_INITIAL_DY + POGO_DAMAGE

## Files Created/Modified

- `assets/physics-schema.json` — Added SLIME_DAZE_COST=20.0 (slime_juice), DRILL_ENEMY_COST=15.0 (drill), ACCELERATED_REGEN_RATE=1.0 + WINDUP_DURATION_FRAMES=30 (fusion), new tuning.pogo group with POGO_BOUNCE_VELOCITY=-2.5 + POGO_COOLDOWN_FRAMES=0; reordered save/death/save_point/gates so pogo is the new LAST key
- `src/fusion/charge_controller.py` — Deleted module constants WINDUP_DURATION_FRAMES + ACCELERATED_REGEN_RATE; replaced two use sites with tuning.X reads; replaced obsolete "Phase 33 may migrate" comment block with one-line migration note
- `src/fusion/pogo.py` — Deleted module constants POGO_BOUNCE_VELOCITY + POGO_COOLDOWN_FRAMES; added `from src.core import tuning` import; replaced two use sites of POGO_BOUNCE_VELOCITY with tuning.POGO_BOUNCE_VELOCITY; preserved POGO_INITIAL_DY (Mario-64 visual parity per D-02) and POGO_DAMAGE (gameplay constant per D-02)
- `src/ui/panel.py` — Extended FEEL_GROUPS allowlist with "pogo"; extended TAB_DEFS Fuse tab dict with `"pogo": None`
- `tests/test_pogo.py` — Updated test_pogo_constants_hardcoded so Phase 33 D-02 supersedes Phase 32 D-18 for the two migrated keys (asserts they live in tuning.* now); POGO_INITIAL_DY + POGO_DAMAGE still asserted as hardcoded module attrs; POGO_DAMAGE still asserted as NOT in tuning (gameplay constant)

## Decisions Made

1. **Schema reorder to satisfy both invariants.** The plan's Step 0 invariant verification revealed the actual current last key of `tuning` was `save_point`, not `gates` as the plan assumed. To satisfy BOTH the W#7 invariant (`pogo` is last) AND the adjacency invariant (`pogo` immediately follows `gates`), I reordered `save`/`death`/`save_point` to come before `gates`, then placed `pogo` after `gates`. Final order: `..., fusion, save, death, save_point, gates, pogo`. This is the minimum change that closes both invariants — alternative (delete adjacency invariant) would weaken the plan; alternative (insert pogo before save) would violate W#7.

2. **Test contract supersession applied inline.** Phase 32 D-18 (pogo constants hardcoded only, never in tuning) was the prior contract. Phase 33 D-02 supersedes that for two of the four pogo constants. The Phase 32 regression test `test_pogo_constants_hardcoded` encoded the old contract literally and would have failed after Task 1. Updated the test in the same Task 1 commit so the regression suite stays GREEN throughout the plan and the test now encodes the new (Phase 33 D-02) contract — both halves: bouncy/cooldown migrated, initial_dy/damage hardcoded.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Schema key-order assumption mismatch — reordered groups to satisfy both invariants**
- **Found during:** Task 1 Step 0 invariant verification
- **Issue:** Plan asserted `gates` was the current last key of `tuning`, but the schema actually had four groups after `gates` (save, death, save_point). The plan's Step 1 Edit 1d insertion target ("after gates closing brace, before tuning closing brace") would have left `pogo` in position 16 of 19 — failing the W#7 invariant and the explicit acceptance criterion `keys[-1]=='pogo'`. The plan's note ("If save is inside tuning, MOVE pogo to after save") covered partial cases but not the full reality (save AND death AND save_point all inside tuning).
- **Fix:** Performed Edit 1d as a reorder + insert: move save/death/save_point to come BEFORE gates (preserving their existing internal order), keep gates second-to-last, append pogo as the new last group. Final order: `..., fusion, save, death, save_point, gates, pogo`. Both invariants now hold (`keys[-1]=='pogo'` AND `pogo immediately follows gates`).
- **Files modified:** assets/physics-schema.json
- **Verification:** Both invariant python -c assertions pass; full plan-level invariant check (`keys[-1]=='pogo'` plus 6 baseline-value asserts) passes; tuning.X attribute access for all 6 keys returns the expected schema-seed values (20.0, 15.0, 30, 1.0, -2.5, 0).
- **Committed in:** eddada3 (Task 1 commit)

**2. [Rule 1 - Test contract update] Updated test_pogo.py::test_pogo_constants_hardcoded for Phase 33 D-02 supersession of Phase 32 D-18**
- **Found during:** Task 1 verification (running tests/test_pogo.py)
- **Issue:** The Phase 32 invariant test asserted `not hasattr(tuning, "POGO_BOUNCE_VELOCITY")` and `not hasattr(tuning, "POGO_COOLDOWN_FRAMES")`. Both assertions FAILED after Task 1 (the migration is the entire point of the task). Phase 33 D-02 explicitly supersedes Phase 32 D-18 for these two specific constants. Without the test update, the regression suite stays RED and Task 2 can't be verified.
- **Fix:** Rewrote test_pogo_constants_hardcoded to encode the new (post-migration) contract: POGO_INITIAL_DY + POGO_DAMAGE asserted as hardcoded module attrs (not in tuning); POGO_BOUNCE_VELOCITY + POGO_COOLDOWN_FRAMES asserted as live in tuning.* (migrated); POGO_DAMAGE still asserted as NOT in tuning. Kept the test docstring explicit about the Phase 33 D-02 supersession of Phase 32 D-18.
- **Files modified:** tests/test_pogo.py
- **Verification:** test_pogo.py now passes 3/3; Phase 32 fusion regression suite (39 tests) stays GREEN.
- **Committed in:** eddada3 (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 test contract update)
**Impact on plan:** Both auto-fixes were necessary to close the plan as written. Deviation 1 closes a plan-authoring assumption gap (the plan acknowledged the possibility but didn't enumerate the actual case); deviation 2 closes a regression-test contract that the plan implicitly invalidates. No scope creep — both changes are inside the plan's stated files_modified set or are direct corollaries (the plan touches pogo.py module constants and the test asserts on those module constants).

## Issues Encountered

- Plan 01 dependency not present in worktree base. Plan 02's frontmatter declares `depends_on: ["33-01"]`, and the plan's automated verification commands reference test files Plan 01 creates (tests/test_tuning_migration.py). The worktree base commit `c0f3d3e` predates Plan 01, so those test files do not exist in this worktree. Adapted by using the plan's per-task `<acceptance_criteria>` grep + python -c verifications (which do not depend on Plan 01) and by running the full Phase 32 fusion regression suite (39 tests, all GREEN). Once Plan 01's worktree is merged to main, its tests/test_tuning_migration.py will go from SKIP/RED to GREEN against this plan's schema additions and use-site reads automatically — no further work needed.
- Pre-existing test failures in test_tuning.py::test_pep562_flat_access (asserts GRAVITY=0.0875 against current schema baseline of 0.13), test_ldtk_migration.py, test_phase05_nyquist.py, test_phase22.py, test_physics.py::test_walk_logic, test_sprite_assets.py::test_palette_compliance — verified pre-existing via `git stash` round-trip. Out of scope per scope-boundary rules; logged here for future cleanup.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 33-03 (destructive-drill-implementation) can now reference `tuning.DRILL_ENEMY_COST` at the new on_tick enemy-AABB scan use site without further migration work.
- Plan 33-04 (daze-shot-implementation) can reference `tuning.SLIME_DAZE_COST` at the player.py:197 daze branch.
- Plan 33-06 (debug-warps-tuning-feel-targets) gets all 6 keys exposed in the Fuse tab and live-tunable via the panel — the entire purpose of this plan.
- No blockers for downstream Phase 33 plans.

## Self-Check: PASSED

Verifications run:

- `[ -f assets/physics-schema.json ]` → FOUND (modified)
- `[ -f src/fusion/charge_controller.py ]` → FOUND (modified)
- `[ -f src/fusion/pogo.py ]` → FOUND (modified)
- `[ -f src/ui/panel.py ]` → FOUND (modified)
- `[ -f tests/test_pogo.py ]` → FOUND (modified)
- `git log --oneline | grep eddada3` → FOUND (Task 1 commit)
- `git log --oneline | grep 1352253` → FOUND (Task 2 commit)
- All plan-level acceptance criteria (15 grep + python -c invariants across both tasks) → PASSED
- Phase 32 fusion regression suite (39 tests) → GREEN

---
*Phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype*
*Completed: 2026-04-28*
