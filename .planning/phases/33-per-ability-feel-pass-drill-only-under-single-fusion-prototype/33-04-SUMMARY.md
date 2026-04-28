---
phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
plan: 04
subsystem: fusion
tags: [fusion, daze, projectile, combat, event-bus, stun, aabb-scan]

# Dependency graph
requires:
  - phase: 33-per-ability-feel-pass (plan 02)
    provides: tuning.SLIME_DAZE_COST live via physics-schema (consumed by fused-branch)
  - phase: 33-per-ability-feel-pass (plan 03)
    provides: Enemy.stun_timer field on Enemy base class (consumed by main.py contact-scan; defensive setattr in Test 3 keeps Plan 04 self-contained at parallel-wave-execute time)
  - phase: 32-fusion-manager-protocol-refactor
    provides: FusionManager + ChargeController + is_fused @property (Z-tap fused-branch reads p.is_fused)
provides:
  - Projectile.applies_daze_stun field + STUN_DURATION_FRAMES = 60 module constant
  - Player.handle_input fused-branch — direct Projectile construction (no slime.spit), exact SLIME_DAZE_COST consumption (no double-cost — W#1 closure), daze_fire event emit
  - main.apply_daze_stun_contacts module-level helper — per-frame projectile-vs-enemy AABB scan applying stun to enemies with stun_timer field (Blocker #2 closure — D-17 stun half delivered)
  - Boss-no-raise regression contract (Test 4) locking in graceful no-op for daze-flagged projectile vs Mole.update_emerging (W#6 closure — boss.py NOT in files_modified)
  - 4 new live tests in tests/test_daze_shot.py (was 2 skipped wave-0 stubs)
affects: [33-05 audio-particle-subscriber-wiring, 33-06 debug-warps-tuning-feel-targets]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Direct Projectile construction in fused-branch — bypasses slime.spit's internal cost path; documented as the W#1 single-approach pinned resolution"
    - "Module-level scan helper extracted from Game.update so unit tests drive the AABB contact scan without instantiating Game (which requires pyxel.init)"
    - "hasattr/getattr defensive guards on enemy.stun_timer — main.py contact loop is forward-compatible with Enemy subclasses that opt out of stun (boss intentionally has no stun_timer)"

key-files:
  created:
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-IMPLEMENTATION-NOTES.md
  modified:
    - src/entities/projectile.py
    - src/entities/player.py
    - main.py
    - tests/test_daze_shot.py

key-decisions:
  - "Fused-branch constructs Projectile directly (no slime.spit call) — only way to consume EXACTLY SLIME_DAZE_COST without a refund hack; pinned resolution from W#1"
  - "STUN_DURATION_FRAMES kept as a hardcoded module constant (not migrated to physics-schema in Phase 33) per plan-author intent — Phase 33 D-17 deferred schema migration to a later feel-pass"
  - "Module-level apply_daze_stun_contacts helper extracted (planner-discretion per plan Step 3 alternative) for testability — Game.update calls it once per frame between projectile.update and door scan"
  - "Defensive Test 3 setattr stun_timer=0 — Plan 04 runs in parallel wave with Plan 03 (which adds Enemy.stun_timer); the setattr is idempotent after Plan 03 merges and keeps Plan 04 self-contained at execute time"

patterns-established:
  - "Parallel-wave self-containment: when a plan tests work across a parallel-wave dependency boundary (Plan 04 calls into Plan 03's stun_timer), the test setattr's the missing attribute defensively so the plan passes against its own worktree base AND against the merged tree"
  - "Helper-extraction-for-testability: gameplay loops that need unit-test coverage but live inside Game.update get extracted as module-level helpers; Game.update becomes a one-line caller; tests bypass pyxel.init entirely"

requirements-completed: [FUS-06]

# Metrics
duration: 9min
completed: 2026-04-28
---

# Phase 33 Plan 04: Daze Shot Implementation Summary

**Fused tap-Z fires a daze projectile that costs exactly SLIME_DAZE_COST (no double-charge), flags applies_daze_stun=True, and main.py's per-frame AABB scan stuns enemies with a stun_timer field for 60 frames — closing both halves of D-17 (input + stun) and three open items (W#1 double-cost, W#6 boss-no-raise, Blocker #2 stun-application missing).**

## Performance

- **Duration:** ~9 min
- **Started:** 2026-04-28T17:29:24Z
- **Completed:** 2026-04-28T17:37:51Z
- **Tasks:** 3
- **Files modified:** 4 (1 entity field, 1 player handler, 1 game loop helper + wire-in, 1 test file with 4 tests)

## Accomplishments

- Projectile gains `applies_daze_stun: bool = False` default + module-level `STUN_DURATION_FRAMES = 60`. No other changes — Projectile remains a passive data carrier.
- Player.handle_input spit handler at line 199: `not self.is_fused` gate REMOVED; fused/unfused branch added. Fused branch consumes exactly `tuning.SLIME_DAZE_COST` (gated by Pitfall 4 cancel-spam pre-check), constructs Projectile directly with `applies_daze_stun=True`, emits `daze_fire`. Unfused branch unchanged (calls slime.spit which pays SLIME_SPIT_COST internally).
- main.py gains `apply_daze_stun_contacts(projectiles, enemies, stun_duration_frames)` module-level helper + a wire-in inside Game.update between the projectile-update loop and the door scan. The helper uses hasattr/getattr guards so enemies without `stun_timer` (e.g., the boss, which is owned separately at `self.mole`) are gracefully skipped.
- 4 tests in tests/test_daze_shot.py — Tests 1+2 unskipped from Plan 01 wave-0 stubs (fused-fire + low-juice gate), Tests 3+4 added for stun-on-Snail-contact and boss-no-raise regression.
- Phase 32 regression suite (drill_dive_parity + fusion_fsm + pogo + projectile, 19 tests) all GREEN — no destabilization of Phase 32 work.

## Task Commits

Each task committed atomically (TDD-aligned where the wave-0 stub tests guided implementation):

1. **Task 1: Projectile.applies_daze_stun field + STUN_DURATION_FRAMES constant** — `cd71074` (feat)
   - src/entities/projectile.py: 9 insertions

2. **Task 2: player.py:197 fused-branch — gate removal + direct Projectile construction (no double-cost) + daze_fire emit** — `0e69f88` (feat)
   - src/entities/player.py: spit handler refactored; fused/unfused branch added
   - tests/test_daze_shot.py: Test 1 + Test 2 unskipped; mock_slime.consume wired to actually decrement; game-mock attributes populated to neutralize auto-aim block
   - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-IMPLEMENTATION-NOTES.md: NEW file with W#1 double-cost resolution

3. **Task 3: main.py per-frame projectile-vs-enemy AABB scan + Boss-no-raise regression test** — `27613cc` (feat)
   - main.py: Projectile import added; module-level apply_daze_stun_contacts helper added; Game.update calls it; re-filter projectiles after scan
   - tests/test_daze_shot.py: Test 3 + Test 4 added

## Files Created/Modified

- `src/entities/projectile.py` — Added module-level `STUN_DURATION_FRAMES = 60` constant; added `self.applies_daze_stun = False` default in `__init__`. Projectile.update / Projectile.draw unchanged — daze-stun application is at the contact site, not in Projectile.
- `src/entities/player.py` — Spit handler at line 199: `not self.is_fused` gate removed. Replaced single `proj = slime.spit(...)` line with a fused/unfused branch: fused pre-checks juice >= SLIME_DAZE_COST (Pitfall 4 cancel-spam guard), consumes SLIME_DAZE_COST, constructs Projectile directly (W#1 closure — bypasses slime.spit's internal SLIME_SPIT_COST), sets applies_daze_stun=True, emits daze_fire. Unfused branch unchanged.
- `main.py` — Added `from src.entities.projectile import STUN_DURATION_FRAMES`. Added module-level `apply_daze_stun_contacts(projectiles, enemies, stun_duration_frames=STUN_DURATION_FRAMES)` helper before `class Game:`. Game.update now calls it between the projectile.update loop (line 791) and the stains loop, with a re-filter after the call to drop projectiles consumed by the scan.
- `tests/test_daze_shot.py` — Removed `@pytest.mark.skip` decorators on Tests 1 and 2; added defensive game-mock setup (game.mole=None, game.enemies=[], game.projectiles=[], game.world.current_level=None) so handle_input's auto-aim block is a no-op against a MagicMock game; wired mock_slime.consume to actually decrement .juice so the EXACT-COST assertion validates the no-double-charge contract. Added Test 3 (Snail contact via apply_daze_stun_contacts helper, with defensive `setattr stun_timer=0` for parallel-wave-Plan-03 independence) and Test 4 (Mole.update_emerging boss-no-raise regression).
- `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-IMPLEMENTATION-NOTES.md` — NEW. Documents the W#1 double-cost resolution: why fused-branch must NOT call slime.spit, what the spawn-coord formula preserves, and the verification path (test_fused_tap_fires_daze EXACT-cost assertion).

## Decisions Made

1. **Module-level helper over inline scan.** The plan's Step 2 inlined the projectile-vs-enemy scan into Game.update; the plan's Step 3 explicitly said "alternative: extract scan into a helper and call it directly; planner-discretion." I extracted to `apply_daze_stun_contacts(projectiles, enemies, stun_duration_frames=STUN_DURATION_FRAMES)` so Test 3 can drive it directly without instantiating a `Game` (which requires `pyxel.init()` and a full asset load). The helper is module-level so it has the same lifetime as `Game` and adds zero per-frame allocation overhead. Game.update is a one-line call. This pattern is logged for future Phase 33 + later phases — gameplay loops that warrant unit-test coverage migrate out of Game.update into module-level helpers.

2. **Defensive `setattr stun_timer=0` in Test 3.** Plan 04 declares `depends_on: ["33-02"]` (NOT 33-03) but the plan body relies on Plan 03's Enemy.stun_timer field. Plan 04 + Plan 03 run in parallel (both `wave: 2`) against the same wave-1 base. My worktree base does NOT have `Enemy.stun_timer`. I made Test 3 self-contained by `if not hasattr(snail, "stun_timer"): snail.stun_timer = 0` — once Plan 03 merges, this is idempotent. The production code path (`apply_daze_stun_contacts`) already uses `hasattr(enemy, "stun_timer")` per plan Step 2, so production behavior is correct against both pre-merge and post-merge trees. The test just mirrors that defensive pattern.

3. **mock_slime.consume wired via lambda.** The shared `mock_slime` fixture in conftest.py is a plain `MagicMock(juice=100)`. Calling `slime.consume(20)` on a MagicMock is a no-op call recorded for spy assertions, but it does NOT decrement `mock_slime.juice`. Test 1's EXACT-cost contract (`mock_slime.juice == initial_juice - tuning.SLIME_DAZE_COST`) requires real decrement. I attached `mock_slime.consume = lambda amount: setattr(mock_slime, "juice", max(0.0, mock_slime.juice - amount))` inside the test. This is in-test wiring (not a fixture change) so other tests using `mock_slime` are unaffected. Documented in test docstring why the wiring is necessary.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Auto-aim block iterates `game.enemies`/`game.mole` against MagicMock — TypeError on `target.x > self.x`**
- **Found during:** Task 2 first test run (test_fused_tap_fires_daze)
- **Issue:** `make_game_with_fusion` returns a MagicMock for `game`. The handle_input auto-aim block at player.py:222-264 reads `self.game.mole`, `self.game.enemies`, and `self.game.world.current_level`. With a default MagicMock, `game.mole` is truthy and `game.mole.is_alive` is truthy, so the block enters and accesses `target.x` (a MagicMock) compared to `self.x` (an int) → `TypeError: '>' not supported between instances of 'MagicMock' and 'int'`. The plan-authored test fixture (Wave 0 stub) didn't populate these attributes — this only became visible after the gate was removed.
- **Fix:** In Tests 1 and 2, set `game.mole = None`, `game.enemies = []`, `game.projectiles = []`, and `game.world.current_level = None` before instantiating the Player. This neutralizes the auto-aim block (no candidates iterated) without changing handle_input's logic. Documented in test setup with a comment.
- **Files modified:** tests/test_daze_shot.py
- **Verification:** Tests 1 and 2 both pass; the auto-aim block is now a no-op against the MagicMock game.
- **Committed in:** 0e69f88 (Task 2 commit)

**2. [Rule 3 - Blocking] mock_slime.consume is a no-op MagicMock — slime.juice doesn't decrement**
- **Found during:** Task 2 second test run (test_fused_tap_fires_daze, after fix #1)
- **Issue:** Even after the auto-aim block was bypassed, the test's `mock_slime.juice == initial_juice - tuning.SLIME_DAZE_COST` assertion failed: `30.0 == (30.0 - 20.0)`. The fused branch DID call `slime.consume(20.0)` (verified via the daze_fire event emission), but `mock_slime.consume` is a default MagicMock callable that records the call but doesn't mutate `mock_slime.juice`.
- **Fix:** Inside Test 1, attach a lambda to `mock_slime.consume` that actually decrements `mock_slime.juice`: `mock_slime.consume = lambda amount: setattr(mock_slime, "juice", max(0.0, mock_slime.juice - amount))`. This mirrors the real Slime.consume implementation. Done in-test (not in conftest fixture) so other tests' usage of mock_slime is unaffected.
- **Files modified:** tests/test_daze_shot.py
- **Verification:** Test 1 now passes; `mock_slime.juice == 30.0 - 20.0 == 10.0` exactly. The W#1 EXACT-cost contract is now enforced.
- **Committed in:** 0e69f88 (Task 2 commit)

**3. [Rule 3 - Blocking] 33-IMPLEMENTATION-NOTES.md does not yet exist (Plan 03 hasn't merged) — plan Step 6 says "extend the file Plan 03 created"**
- **Found during:** Task 2 Step 6 (documenting W#1 closure in 33-IMPLEMENTATION-NOTES.md)
- **Issue:** Plan 04 Step 6 instructs "DOCUMENT the resolution in 33-IMPLEMENTATION-NOTES.md (extend the file Plan 03 created)". Plan 03 is in the same wave (2) as Plan 04 and runs in a parallel worktree; my base does not have the file.
- **Fix:** Created `33-IMPLEMENTATION-NOTES.md` with a top-level header explaining cross-plan scope, then added the "Daze double-cost resolution (W#1 closure)" section attributed to Plan 04. Each section will carry a `*Source: Plan 33-NN ...*` line so the orchestrator merge can resolve any collision. Plan 03's eventual merge will append its drill-juice-clamp section under a sibling heading; section headings prevent textual conflict.
- **Files modified:** .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-IMPLEMENTATION-NOTES.md (NEW)
- **Verification:** File exists; `grep -c "double-cost"` returns 2; `grep -c "W#1"` returns 1; content includes all three sub-bullets the plan requires (avoid refund hack, self-contained, no spit-event collision) plus spawn-coords + verification hooks.
- **Committed in:** 0e69f88 (Task 2 commit)

---

**Total deviations:** 3 auto-fixed (3 blocking — all Rule 3)
**Impact on plan:** All three fixes are scaffolding for the parallel-wave execution model + Wave 0 stub limitations. None change the plan's intent or scope. The production code (player.py + main.py + projectile.py) is exactly what the plan specifies; the deviations only touch test fixtures and the cross-plan docs file.

## Issues Encountered

- **Test 3 stun_timer dependency on Plan 03.** Test 3 reads `snail.stun_timer == 0` as the "Plan 03 Task 1 default". My worktree base (parallel-wave) doesn't have Plan 03's enemy field. Resolved by `setattr stun_timer=0` defensively (see Decision 2 above) so the test passes against both pre-merge and post-merge trees. The production helper `apply_daze_stun_contacts` already uses `hasattr` guards per the plan, so no production deviation was needed.

- **Pre-existing test failures (not introduced by this plan).** Six pre-existing failures noted in 33-02 SUMMARY's Issues Encountered persist out of scope:
  - tests/test_ldtk_migration.py (cavern tileset uid)
  - tests/test_phase05_nyquist.py
  - tests/test_phase22.py
  - tests/test_physics.py::test_walk_logic
  - tests/test_sprite_assets.py::test_palette_compliance
  - tests/test_tuning.py::{test_pep562_flat_access, test_set_value_visibility, test_baseline_reset_single_key, test_baseline_reset_all, test_bake_derived_determinism}

  Verified pre-existing via `git stash` round-trip (5 tuning failures present at base, identical after my changes). Out of scope per scope-boundary rules; logged here for future cleanup. None of these failures are touched by Plan 04's files_modified set.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Plan 33-05 (audio-particle-subscriber-wiring)** can now subscribe to the `daze_fire` event from the fused-branch fire site; the event is emitted reliably with `mock_slime.juice >= tuning.SLIME_DAZE_COST` and silently suppressed otherwise (Pitfall 4 closure).
- **Plan 33-06 (debug-warps-tuning-feel-targets)** can include `tuning.SLIME_DAZE_COST` in playtest tuning; live-edit via the panel will affect the next daze fire on the next frame.
- **D-17 fully delivered.** Both halves of the design decision (fire + stun) are wired and tested. Manual playtest in Plan 06 D-K2/D-K5 will confirm the "shoot to daze → drill to finish" core fantasy reads as intended (Snail stays frozen ~60 frames after a daze hit, drill kill follows).
- **W#1, W#6, Blocker #2 closed.** Three open items off the phase-33 board.
- **Plan 03 merge interaction.** When orchestrator merges Plan 03 + Plan 04 worktrees, the only cross-tree contact point is `Enemy.stun_timer` (Plan 03 adds, Plan 04 reads via hasattr). No textual conflict in any source file. The 33-IMPLEMENTATION-NOTES.md merge is heading-keyed and append-only.
- No blockers for downstream Phase 33 plans.

## Self-Check: PASSED

Verifications run:

- `[ -f src/entities/projectile.py ]` → FOUND (modified)
- `[ -f src/entities/player.py ]` → FOUND (modified)
- `[ -f main.py ]` → FOUND (modified)
- `[ -f tests/test_daze_shot.py ]` → FOUND (modified)
- `[ -f .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-IMPLEMENTATION-NOTES.md ]` → FOUND (created)
- `git log --oneline | grep cd71074` → FOUND (Task 1 commit)
- `git log --oneline | grep 0e69f88` → FOUND (Task 2 commit)
- `git log --oneline | grep 27613cc` → FOUND (Task 3 commit)
- All Task 1 acceptance criteria (4 grep + 2 python -c) → PASSED
- All Task 2 acceptance criteria (8 grep + 2 python -c + IMPLEMENTATION-NOTES greps + Test 1 + Test 2 + Phase 32 regression) → PASSED
- All Task 3 acceptance criteria (3 grep + insertion-site invariant + 4 test functions + 0 skips + boss-no-raise) → PASSED
- Phase 32 regression suite (test_drill_dive_parity + test_fusion_fsm + test_pogo + test_projectile, 19 tests) → GREEN
- Full test suite minus pre-existing out-of-scope failures (416 passed, 6 skipped) → GREEN

---
*Phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype*
*Completed: 2026-04-28*
