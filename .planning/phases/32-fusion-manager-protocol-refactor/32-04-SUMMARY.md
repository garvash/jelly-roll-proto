---
phase: 32-fusion-manager-protocol-refactor
plan: 04
subsystem: fusion
tags: [fusion, refactor, manager, charge-controller, fsm, wave-2]

# Dependency graph
requires:
  - phase: 32-fusion-manager-protocol-refactor
    plan: 02
    provides: src.fusion.protocol.FusionAbility (D-09 @runtime_checkable Protocol) + TickResult dataclass
provides:
  - src/fusion/manager.FusionManager (FUSED+EXIT FSM, 5 public methods + is_fused mirror)
  - src/fusion/charge_controller.ChargeController (RECALL+WINDUP FSM, handle_z_input + 2 named constants)
  - src/fusion/__init__.py extended re-exports (FusionManager, ChargeController)
affects:
  - 32-05 (DrillDive + Pogo: implement FusionAbility, plug into FusionManager via abilities dict)
  - 32-06 (Player.handle_input wiring: routes Z-input through charge_controller, DOWN+SPACE through fusion_manager)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "FSM-shell driver with construction-time isinstance Protocol validation (mirrors AnimFSM missing-clip-id check)"
    - "Per-frame TickResult-driven dispatch: ability owns physics, manager applies dx/dy intent and routes exit"
    - "Sub-FSM via state-string + private progress accumulator (RECALL/WINDUP) — consistent with Player.state == 'DIVING' precedent"
    - "Latch-site emission split: ChargeController emits fuse_start; FusionManager emits fuse_end (D-06 / D-07)"

key-files:
  created:
    - src/fusion/manager.py
    - src/fusion/charge_controller.py
  modified:
    - src/fusion/__init__.py

key-decisions:
  - "D-08 handoff: ChargeController calls fusion_manager.latch_fuse(slime) directly at WINDUP latch (no callback/polled-flag intermediary)"
  - "D-14 implementation deferred to Plan 06: FusionManager exposes is_fused as a public attribute (not @property); Plan 06 adds the @property forward on Player"
  - "Discretion #8 (accelerated regen): ChargeController calls slime.refill(ACCELERATED_REGEN_RATE) per frame while Z held + slime docked + not dissipated. Slime stays unchanged."
  - "force_exit signature: (player, slime, reason) — chosen over the plan-text transitional (reason)-only because force_exit needs player context for slime.reform on non-dissipate exits and is consistent with the Wave 0 test fixtures that already pass (player, slime, reason)"
  - "Rule 1 deviation from plan logic: dropped hold_frames >= SPIT_HOLD_THRESHOLD gate from RECALL start. Locked Wave 0 test contract (test_fusion_fsm.py:158) mocks hold_frames=0 and expects WINDUP within 10 frames. Tap-presses cleanly cancel via the existing Z-release branch with no juice spent. tap-vs-hold disambiguation can live at Player.handle_input layer in Plan 06 if production tap-spit needs further isolation."

patterns-established:
  - "src/fusion/ subsystem now ships its full Wave 2 driver layer — Plan 05 abilities can be plugged into the existing dispatch shell"
  - "Construction-time Protocol-conformance validation pattern: FusionManager._init_ raises TypeError on non-FusionAbility entries — the analogous check used by AnimFSM for missing clip ids, applied to a typed Protocol"

requirements-completed: [FUS-04, FUS-05]

# Metrics
duration: ~30min
completed: 2026-04-26
---

# Phase 32 Plan 04: FusionManager + ChargeController Summary

**FUS-04 middle-layer ships — FusionManager (FUSED+EXIT FSM driver, ability dispatch, mana shield routing) and ChargeController (RECALL+WINDUP FSM with fuse_start latch emission) land as the home for Player.fuse / Player.unfuse / Z-input / DOWN+SPACE-airborne logic that Plan 06 will delete.**

## Performance

- **Tasks:** 2 (both `auto`, both committed atomically)
- **Files created:** 2 (`src/fusion/manager.py` 167 lines, `src/fusion/charge_controller.py` 130 lines)
- **Files modified:** 1 (`src/fusion/__init__.py` — appended FusionManager + ChargeController exports)
- **Tests added:** 0 (Plan 01 already wrote the RED tests; this plan turns the GREEN gates on once Plan 05 ships drill_dive)
- **Regression check:** 398 passed, 25 skipped, 10 pre-existing failures (all enumerated in `deferred-items.md`); no NEW failures introduced.

## Accomplishments

- **`src/fusion/manager.py` — FusionManager (167 lines).** 5 public methods (`tick`, `handle_jump_input`, `latch_fuse`, `force_exit`, `apply_fused_damage`) plus public `is_fused` mirror. Construction-time `isinstance(ability, FusionAbility)` validation per D-09 @runtime_checkable — boot-time TypeError on a non-conforming ability, never a silent mid-frame AttributeError. All juice/cooldown values read at use-site from `tuning.*` per Phase 25.
- **`src/fusion/charge_controller.py` — ChargeController (130 lines).** Single public method `handle_z_input(player, slime, input_manager)` that runs the IDLE → RECALL → WINDUP FSM. Two named module constants — `ACCELERATED_REGEN_RATE = 1.0` (juice/frame) and `WINDUP_DURATION_FRAMES = 30` — at module top with banner comment per project MEMORY no-magic-numbers rule. State string constants (`_STATE_IDLE`, `_STATE_RECALL`, `_STATE_WINDUP`) module-private. Free-cancel path on Z release during WINDUP (no juice spent).
- **`fuse_start` / `fuse_end` emit responsibility split per D-06 / D-07.** ChargeController owns `fuse_start` at the 200% latch site (immediately before `fusion_manager.latch_fuse(slime)`). FusionManager owns `fuse_end` at exit — both `tick()` (request_exit branch) and `force_exit()` (outside-ability triggers). Manager emits exactly once per exit; tick-driven exit and force_exit don't double-fire because force_exit early-returns when `is_fused == False`.
- **Pitfall 4 satisfied (slime.is_fused dual write).** Three sites: `latch_fuse(slime)` writes `slime.is_fused = True`, `tick()` exit branch writes `False`, `force_exit()` writes `False`. overlays.py + slime.update read this flag.
- **D-17 single-dispatcher invariant.** `handle_jump_input` is the only entry point for DOWN+SPACE airborne — branches on `is_fused` to pick `drill_dive` (fused) vs `pogo` (unfused), calls `can_activate()` then `on_enter(context={})`. Plan 06 will delete the now-orphaned drill-entry + mid-drill-cancel block in `Player.handle_input`.
- **Discretion #8 accelerated-regen layer.** ChargeController calls `slime.refill(ACCELERATED_REGEN_RATE)` per frame while Z held + slime docked + not dissipated. Slime API unchanged.
- **Wave 2 GREEN-gate readiness verified.** Manually simulated `test_fuse_start_emits_at_latch` and `test_windup_release_free_cancel` with stubbed DrillDive/Pogo: both pass (WINDUP entered in 1 frame from docked+full-juice; latch fired exactly once at 30 frames; free-cancel left juice unchanged at 200.0). Tests will activate from SKIPPED → GREEN automatically once Plan 05 ships `src.fusion.drill_dive`.

## Task Commits

| # | Type | Hash      | Subject                                                                  |
| - | ---- | --------- | ------------------------------------------------------------------------ |
| 1 | feat | `fa7f9dc` | feat(32-04): add FusionManager (FUSED+EXIT FSM, dispatch, mana shield)   |
| 2 | feat | `7df6f22` | feat(32-04): add ChargeController (RECALL+WINDUP FSM, fuse_start latch)  |

## Files Created/Modified

- **`src/fusion/manager.py` (created, 167 lines).** Module docstring cites D-07/D-13/D-15/D-17. Imports `FusionAbility, TickResult` from `src.fusion.protocol`, `event_bus` from `src.anim`, `tuning` from `src.core`. Private state: `_abilities`, `_active`, `_exit_cooldown_frames`. Public state: `is_fused`. `tick()` decrements EXIT cooldown, runs `on_tick`, applies dx/dy, handles `request_exit` with `slime.dissipate()` + `_exit_cooldown_frames = tuning.SLIME_DISSIPATE_COOLDOWN` on `juice_empty`. `force_exit(player, slime, reason)` mirrors the exit path for outside-ability triggers; idempotent (early-returns on `not is_fused`); calls `slime.reform` on non-dissipate exits. `apply_fused_damage(player, slime, source_x)` consumes `tuning.MANA_SHIELD_COST`, sets `player.invuln_timer = tuning.INVULN_DURATION`, triggers `force_exit('juice_empty')` if juice drains to 0; returns True if absorbed (knockback application stays on `Player.take_damage` per Plan 06).
- **`src/fusion/charge_controller.py` (created, 130 lines).** Module docstring cites D-06/D-08/D-15/D-23, plus an explicit explanation of the tap/hold note (why `hold_frames` threshold isn't gated here). Module constants: `ACCELERATED_REGEN_RATE`, `WINDUP_DURATION_FRAMES`, `_STATE_IDLE`, `_STATE_RECALL`, `_STATE_WINDUP`. `__init__(fusion_manager: FusionManager)` keeps a private reference. `handle_z_input` runs 4 logical branches in order: (1) hold + recall start, (2) RECALL per-frame with accelerated regen + 100%-gate WINDUP entry, (3) WINDUP per-frame with free-cancel + latch (`event_bus.emit("fuse_start")` → `self._fusion_manager.latch_fuse(slime)` at progress ≥ 1.0), (4) Z release while RECALL → IDLE.
- **`src/fusion/__init__.py` (modified, +2 imports +2 `__all__` entries).** Now re-exports `FusionAbility, TickResult, FusionManager, ChargeController`. Plan 05 will append `DrillDive` and `Pogo`.

## Decisions Made

- **D-08 handoff: direct call.** ChargeController calls `self._fusion_manager.latch_fuse(slime)` at the latch site. The plan offered three options (callback / polled flag / direct observation); direct call is the lightest touch and matches RESEARCH § Open Question 2 recommendation.
- **D-14 deferred to Plan 06.** FusionManager exposes `is_fused` as a public attribute, not a `@property`. Plan 06 will introduce the `@property is_fused` on Player that reads `self.game.fusion_manager.is_fused`. Deferring keeps Plan 04 minimally diff'd — no Player edits in this plan.
- **`force_exit(player, slime, reason)` signature.** Plan 04's PLAN.md shows two candidate signatures and recommends `(player, slime, reason)` — adopted. The `(reason)`-only form was rejected because `force_exit` needs `player.x/y/facing_right/level_map` for the non-dissipate `slime.reform()` path. Wave 0 test fixtures already pass `(player, slime, reason)` (per 32-01-SUMMARY's Rule 1 fix), so this also keeps tests aligned.
- **Discretion #8: ChargeController calls slime.refill().** Per the plan's instruction: avoids adding a slime-mode flag; slime API stays unchanged. Phase 33 will tune the rate.
- **Constants chosen.** `ACCELERATED_REGEN_RATE = 1.0` (FUSION-DESIGN draft 2× passive regen). `WINDUP_DURATION_FRAMES = 30` (~0.5s @ 60 fps; FUSION-DESIGN D-23c base target). Both are pinned at module top with inline-comment provenance; Phase 33 retunes.
- **State strings over enum.** Used string constants (`"IDLE"` / `"RECALL"` / `"WINDUP"`) instead of an Enum, per the plan's "consistent with `Player.state == 'DIVING'` precedent" guidance. Module-private `_STATE_*` constants give the rename-safety of an enum without the import overhead.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Bug] Dropped `hold_frames >= SPIT_HOLD_THRESHOLD` gate from ChargeController RECALL start**

- **Found during:** Task 2 verification — manually simulated `test_fuse_start_emits_at_latch` against the literal plan port. With `input_manager.hold_frames = lambda name: 0` (Wave 0 test contract), the plan's literal `hold_frames("spit") >= tuning.SPIT_HOLD_THRESHOLD` gate would never let RECALL start, leaving the FSM in IDLE for all 10 frames. The test asserts `_state == "WINDUP"` within 10 frames — would FAIL once Plan 05 ships drill_dive and the importorskip clears.
- **Issue:** The Wave 0 test contract (LOCKED) and the Plan 04 literal logic (REVISED final draft) have an irreconcilable tension on the tap/hold disambiguation site. The Wave 0 author wired the test mock to `hold_frames=0` and expected ChargeController to enter WINDUP from a docked-full-juice-Z-held state without any hold-threshold gating. The Plan 04 author wrote a literal port of `player.py:265-281` which DOES gate on the threshold.
- **Fix:** ChargeController treats `btn("spit") held` as the RECALL signal directly. Tap-presses now produce a single-frame RECALL blip that immediately cancels via Step 4 (Z-release-during-RECALL → IDLE). `slime.recall()` is idempotent and only flips a flag; no juice is spent during a 1-frame recall blip. tap-vs-hold disambiguation for the spit-projectile branch lives on `Player.handle_input` (will be retained in Plan 06's diff) — that's where `was_tap("spit", SPIT_HOLD_THRESHOLD)` is the right primitive.
- **Files modified:** `src/fusion/charge_controller.py` (omitted the threshold gate; added a documenting paragraph in the module docstring).
- **Commit:** `7df6f22`.
- **Acceptance criteria impact:** The Plan 04 acceptance criteria includes `grep -nE "tuning\.SPIT_HOLD_THRESHOLD" src/fusion/charge_controller.py returns ≥ 1` — this grep now returns 0. Documented as an intentional miss; the alternative (gate on the threshold) breaks the locked Wave 0 test contract.

### Auto-fixed style choices

None — no further deviations.

## Issues Encountered

- **Wave 0 test contract vs Plan 04 literal logic mismatch on tap/hold gate.** Resolved by the Rule 1 deviation above. The orchestrator's note ("the skipped tests in `tests/test_fusion_fsm.py` should turn GREEN once your FusionManager + ChargeController land") is partially overstated — the tests' `_require_fusion_modules()` helper requires `src.fusion.drill_dive` (Plan 05 / Wave 3), so they remain SKIPPED at the end of this plan. They WILL turn GREEN once Plan 05 ships, verified by manual stub-DrillDive simulation in this plan's verification step.

## Authentication Gates

None — Wave 2 is local code only.

## Threat Flags

None — manager.py + charge_controller.py introduce no new network endpoints, file access patterns, auth paths, or schema changes. The threat model in 32-04-PLAN.md (T-32-04-01..04) is satisfied:

- **T-32-04-01 (mitigate):** Construction-time `isinstance(ability, FusionAbility)` check in `FusionManager.__init__` raises TypeError on non-conforming ability entries.
- **T-32-04-02 (accept):** Ability `on_tick` exception path is unchanged — propagates up the call stack as standard Python uncaught exception (game crashes loudly, surfacing the bug).
- **T-32-04-03 (mitigate):** `slime.is_fused` dual-write check passes — three write sites (`latch_fuse` True; `tick()` exit branch False; `force_exit` False).
- **T-32-04-04 (mitigate):** `force_exit` is idempotent (early-return on `not is_fused`); `tick()` handles its own exit cleanup directly. No double `fuse_end` emission possible.

## Known Stubs

None — both modules are fully wired against existing APIs:

- `FusionManager` calls real `event_bus.emit`, real `slime.dissipate`, real `slime.reform`, real `slime.consume`, real `tuning.*` constants.
- `ChargeController` calls real `event_bus.emit`, real `slime.recall`, real `slime.update_recall`, real `slime.refill`, real `slime.recall_trail.clear()`, real `fusion_manager.latch_fuse`.

The `_active` field on FusionManager is `None` between abilities — that's expected FSM state (no ability dispatched), not a stub.

## Self-Check

Files claimed to be created:

- `src/fusion/manager.py` — FOUND (167 lines)
- `src/fusion/charge_controller.py` — FOUND (130 lines)

Files claimed to be modified:

- `src/fusion/__init__.py` — FOUND (modified; FusionManager + ChargeController re-exports added)

Commits claimed:

- `fa7f9dc` (Task 1) — FOUND in `git log --oneline`
- `7df6f22` (Task 2) — FOUND in `git log --oneline`

Acceptance criteria spot-check (per Plan 04 `<acceptance_criteria>`):

- `python -c "from src.fusion.manager import FusionManager"` exits 0 — VERIFIED
- `python -c "from src.fusion import FusionAbility, TickResult, FusionManager, ChargeController"` exits 0 — VERIFIED
- `grep -nE "^class FusionManager" src/fusion/manager.py` → 1 match (line 21) — VERIFIED
- `grep -n "def tick" src/fusion/manager.py` → 1 match (line 53) — VERIFIED
- `grep -n "def handle_jump_input" src/fusion/manager.py` → 1 match (line 83) — VERIFIED
- `grep -n "def latch_fuse" src/fusion/manager.py` → 1 match (line 108) — VERIFIED
- `grep -n "def force_exit" src/fusion/manager.py` → 1 match (line 123) — VERIFIED
- `grep -n "def apply_fused_damage" src/fusion/manager.py` → 1 match (line 148) — VERIFIED
- `grep -n 'event_bus.emit("fuse_end")' src/fusion/manager.py` → 2 matches (lines 81, 146) — VERIFIED (≥1 required)
- `grep -nE 'event_bus.emit\("fuse_start"\)|event_bus.emit\("drill_' src/fusion/manager.py` → 0 matches — VERIFIED (must be 0)
- `grep -n "slime.is_fused = " src/fusion/manager.py` → 3 matches — VERIFIED (≥2 required)
- `grep -nE "tuning\.SLIME_DISSIPATE_COOLDOWN|tuning\.MANA_SHIELD_COST|tuning\.INVULN_DURATION" src/fusion/manager.py` → 5 matches — VERIFIED (≥3 required)
- `wc -l src/fusion/manager.py` → 167 — VERIFIED (≥80 required)
- `grep -nE "^class ChargeController" src/fusion/charge_controller.py` → 1 match (line 42) — VERIFIED
- `grep -n "def handle_z_input" src/fusion/charge_controller.py` → 1 match (line 57) — VERIFIED
- `grep -n 'event_bus.emit("fuse_start")' src/fusion/charge_controller.py` → 1 match (line 119) — VERIFIED
- `grep -nE "WINDUP_DURATION_FRAMES|ACCELERATED_REGEN_RATE" src/fusion/charge_controller.py` → 6 matches — VERIFIED (≥4 required)
- `grep -nE 'slime.juice >= slime.max_juice' src/fusion/charge_controller.py` → 1 match (line 98) — VERIFIED
- `grep -nE "self\._fusion_manager\.latch_fuse" src/fusion/charge_controller.py` → 1 match (line 120) — VERIFIED
- `grep -n "FusionManager" src/fusion/__init__.py` → ≥1 match — VERIFIED
- `grep -n "ChargeController" src/fusion/__init__.py` → ≥1 match — VERIFIED
- `wc -l src/fusion/charge_controller.py` → 130 — VERIFIED (≥70 required)
- `python -m pytest tests/test_fusion_fsm.py -x -q` → 4 skipped (pending Plan 05 drill_dive) — RUNS CLEAN

Acceptance criteria miss (intentional, documented above):

- `grep -nE "tuning\.SPIT_HOLD_THRESHOLD" src/fusion/charge_controller.py` → 0 matches (plan asked ≥1). Reason: Rule 1 deviation — keeping the threshold gate breaks the locked Wave 0 test contract (`test_fusion_fsm.py:158` mocks `hold_frames=0`).

Wave 2 GREEN-gate verification (manual simulation with stubbed DrillDive/Pogo):

- `test_fuse_start_emits_at_latch`: WINDUP reached in 1 frame; 0 emits at WINDUP entry; 1 emit at latch (after 30 WINDUP frames) — PASS
- `test_windup_release_free_cancel`: state → IDLE on Z release; juice unchanged at 200.0; 0 fuse_start emits; is_fused=False — PASS

Regression check: `python -m pytest -q` → 398 passed, 25 skipped, 10 pre-existing failures (all enumerated in `deferred-items.md`); no new failures introduced by Plan 04.

## Self-Check: PASSED

---
*Phase: 32-fusion-manager-protocol-refactor*
*Completed: 2026-04-26*
