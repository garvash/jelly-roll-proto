---
phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
plan: 06
subsystem: debug + feel-targets
tags: [debug, warps, feel-targets, checkpoint, partial]
status: PARTIAL -- Task 1 complete + 33-FEEL-TARGETS.md DRAFT authored; PAUSED at Task 2 (checkpoint:human-verify) for user playtest sign-off
requires: [33-01, 33-02, 33-03, 33-04, 33-05]
provides:
  - "Multi-target debug warps Ctrl+4..7 for D-09 drill-relevant rooms"
  - "33-FEEL-TARGETS.md DRAFT with 18 falsifiable feel targets"
affects:
  - "src/core/debug.py (warp_target one-shot flag + 4 named WARP_LEVEL_* constants)"
  - "main.py:Game.update (warp consumer mirroring teleport_requested pattern)"
  - "tests/test_debug.py (8 new test cases for Phase 33 warps)"
  - ".planning/phases/33-.../33-FEEL-TARGETS.md (NEW, DRAFT)"
  - ".planning/phases/33-.../deferred-items.md (NEW; pre-existing test failures logged)"
tech-stack:
  added: []
  patterns:
    - "One-shot string-flag pattern for multi-target navigation (mirrors teleport_requested)"
    - "Falsifiable feel-target table (29-FEEL-TARGETS.md format inheritance)"
key-files:
  created:
    - ".planning/phases/33-.../33-FEEL-TARGETS.md"
    - ".planning/phases/33-.../deferred-items.md"
  modified:
    - "src/core/debug.py"
    - "main.py"
    - "tests/test_debug.py"
decisions:
  - "Substituted 3 of 4 warp targets to closest-analog gym levels (gym.ldtk lacks soft_block tiles and Snail/Bat enemies); recorded inline in debug.py and below."
  - "Pre-existing test failures (10 unrelated to Plan 06) logged to deferred-items.md per scope-boundary rules; not blocking Plan 06."
metrics:
  duration: ~25min Task 1 (RED + GREEN + DRAFT scaffold)
  completed: PARTIAL -- 2026-04-29
---

# Phase 33 Plan 06: Debug Warps + Feel Targets (PARTIAL — Task 2 PENDING)

**One-liner:** Ctrl+4..7 warps to drill-relevant gym rooms via one-shot string flag; 33-FEEL-TARGETS.md DRAFT scaffolds 18 falsifiable feel targets pending user playtest sign-off.

This plan splits across a checkpoint: Task 1 ships the iteration tooling
(debug warps + FEEL-TARGETS draft) autonomously; Task 2 is a blocking
`checkpoint:human-verify` that requires the user to playtest with the live
panel, walk D-10 layered tuning order, and sign off each of the 18 targets.
Task 3 (preset bake to `assets/presets/v2.0-default.json`) runs after the
user signs off; it is NOT covered by this partial summary.

## What's Done (Task 1)

### 1. Debug warps (Ctrl+4..7) — `src/core/debug.py` + `main.py`

The existing `Ctrl+T -> teleport_requested` one-shot pattern (Phase 29) extends
to a generic string-flag `warp_target: str | None`:

- **debug.py:** new `warp_target` flag + 4 named `WARP_LEVEL_*` constants;
  `update()` sets `warp_target` to the matching constant on `Ctrl+4..7`.
- **main.py:Game.update:** consumer block reads `debug.warp_target`, looks up
  the matching level by id in `self.world.levels`, repositions player + camera,
  resets `warp_target` to None. Mirrors the `teleport_requested` block above
  it. `WARP_NUDGE = 32` constant avoids the magic-number rule.

**Level mapping (substitutions noted):** gym.ldtk has 6 levels but lacks
soft_block tiles and Snail/Bat enemies. Verified by parsing the world JSON
during planning. Per the plan NOTE allowing closest-analog substitutions:

| Constant                    | gym.ldtk level     | Carve-out reason                                          |
| --------------------------- | ------------------ | --------------------------------------------------------- |
| `WARP_LEVEL_CRACKED_V`      | `Gym_AccelRunway`  | Only gym level with `cracked_V` tiles (9 tiles)           |
| `WARP_LEVEL_SOFT_BLOCK`     | `Gym_GapTrio`      | No level has `soft_block`; gap-traversal is closest analog |
| `WARP_LEVEL_ENEMY_CLUSTER`  | `Gym_HeightSteps`  | No level has Snail/Bat entities; open playground analog   |
| `WARP_LEVEL_JUICE_DRAIN`    | `Gym_ZigzagShaft`  | No level has dedicated juice-drain hazards; vertical shaft |

If Phase 33 playtest reveals the gym world lacks the right scenarios for
drill-feel testing, the planner-discretion option per CONTEXT D-09 is to
either (a) extend gym.ldtk in-place with a new test room mid-phase OR
(b) switch `main.py:367` to load `assets/output.ldtk` (`Level_0..Level_16`)
for the duration of Phase 33. Both are deferred to post-playtest if needed.

### 2. 33-FEEL-TARGETS.md DRAFT

18 falsifiable feel targets in `.planning/phases/33-.../33-FEEL-TARGETS.md`
mirroring `29-FEEL-TARGETS.md` format:

- **Charge ritual (D-C1..C5)** — tap/hold disambiguation (~8f target),
  WINDUP cancel-window feel, WINDUP commit feel, accel-regen ritual time
  (~2x passive).
- **Drill physics (D-D1..D4)** — chain on full juice (CRACKED_V column),
  drift, solid-landing exit (a), juice-starvation exit (b).
- **Drill combat (D-K1..K5)** — single kill, 3-enemy chain, juice-starvation
  mid-chain (Pitfall 2 option-a), boss daze->drill loop (D-17 carve-out),
  daze low-juice gate (Pitfall 4).
- **Pogo confirm (D-P1)** — FUSION-DESIGN D-04 unchanged after destructive-drill.
- **Identity (D-I1..I3)** — blindfolded SFX, drill earthbound palette,
  daze splat differentiation.

Plus a Reference Values table (17 tunables with starting values + sources),
and empty placeholder Results / Sign-off sections.

Header reads `> DRAFT`; will flip to `> APPROVED YYYY-MM-DD` after Task 2.

### 3. Tests

`tests/test_debug.py` extended with 8 Phase 33 cases:
- defaults
- 4 named constants exist
- W#4 closure: every constant matches a real `gym.ldtk` identifier
- Ctrl+4/5/6/7 each set `warp_target` to the right constant
- Ctrl-less press doesn't set warp_target
- main.py consumes warp_target with read + reset

All 14 test_debug.py cases GREEN: `14 passed in 0.06s`.

## Acceptance Criteria (Task 1)

| Check                                                                              | Threshold | Actual |
| ---------------------------------------------------------------------------------- | --------- | ------ |
| `grep "warp_target" src/core/debug.py`                                             | >= 5      | 6      |
| `grep "WARP_LEVEL_" src/core/debug.py`                                             | >= 4      | 8      |
| `grep "if pyxel.btnp(pyxel.KEY_4)" src/core/debug.py`                              | == 1      | 1      |
| `grep "debug.warp_target" main.py`                                                 | >= 2      | 3      |
| W#4 closure: every WARP_LEVEL_* matches gym.ldtk `identifier`                      | OK        | OK     |
| `pytest tests/test_debug.py -x -q`                                                 | exits 0   | 14 PASS |
| `test -f .planning/phases/33-.../33-FEEL-TARGETS.md`                               | exists    | OK     |
| `grep -c "^| D-" 33-FEEL-TARGETS.md`                                               | >= 15     | 18     |
| `grep -c "PENDING" 33-FEEL-TARGETS.md`                                             | >= 15     | 19     |
| `grep "^> DRAFT" 33-FEEL-TARGETS.md`                                               | == 1      | 1      |
| `grep -E "## Reference Values\|## Results\|## Sign-off" 33-FEEL-TARGETS.md`        | == 3      | 3      |

All Task 1 acceptance criteria PASS.

## What's Pending (Task 2 — checkpoint:human-verify)

The plan blocks here. Task 2 requires the user to:
1. Boot `python main.py` with F1 panel open.
2. Walk D-10 layered tuning order (charge -> drill physics -> drill combat -> pogo).
3. Iterate values via the live panel until each of the 18 feel targets reads PASS.
4. Mark every PENDING -> PASS in 33-FEEL-TARGETS.md.
5. Flip header from `> DRAFT` to `> APPROVED YYYY-MM-DD`.
6. Populate Results + Sign-off sections.

Then Task 3 bakes the final values into `assets/presets/v2.0-default.json`.

## What's Pending (Task 3 — runs after Task 2 sign-off)

`assets/presets/v2.0-default.json` (alias backed by `slot_1.json`) gains 6
new keys: `WINDUP_DURATION_FRAMES`, `ACCELERATED_REGEN_RATE`, `POGO_BOUNCE_VELOCITY`,
`POGO_COOLDOWN_FRAMES`, `DRILL_ENEMY_COST`, `SLIME_DAZE_COST`. `_v1.3-reference.json`
stays FROZEN. Out of scope for this partial summary.

## Deviations from Plan

### [Rule 3 - Blocking] Closest-analog level substitutions for warp targets

- **Found during:** Task 1 Step 1 (gym.ldtk content audit).
- **Issue:** The plan recommended mapping `WARP_LEVEL_SOFT_BLOCK -> Gym_GapTrio`
  among others, but a content audit revealed gym.ldtk has NO soft_block tiles
  in any level, NO Snail/Bat enemies anywhere, and only `Gym_AccelRunway`
  contains cracked_V tiles (9 tiles). The plan explicitly anticipates this
  with "if gym.ldtk lacks a feature, use the closest analog and note the
  substitution" — handled inline.
- **Fix:** Picked closest-analog gym levels for the 3 missing-feature slots;
  documented the substitution in `src/core/debug.py` comment block AND in this
  SUMMARY's level-mapping table. The planner-discretion fallback (extend
  gym.ldtk in-place OR switch main.py to load output.ldtk) remains available
  if Task 2 playtest reveals the substitutions don't expose the right scenarios.
- **Files modified:** `src/core/debug.py` (substitution rationale comments)
- **Commit:** `78b2d48`

### [Rule 3 - Out-of-scope] Pre-existing test-suite failures logged to deferred-items.md

- **Found during:** Task 1 GREEN-phase verification (`pytest tests/ -x -q`).
- **Issue:** 10 tests fail on the base commit unrelated to Plan 06: 1 LDtk
  tileset uid drift, 9 tests asserting pre-Phase-29 v1.3 physics constants /
  derived bakes that have moved on to v2.0-default. None touch debug.py,
  main.py:Game.update, or any file modified by Plan 06.
- **Fix:** Logged each to `.planning/phases/33-.../deferred-items.md` with
  test name, likely owner, and reason; verified pre-existing via `git stash`
  + re-run on clean tree (same 10 failures).
- **Files added:** `.planning/phases/33-.../deferred-items.md`
- **Commit:** `78b2d48` (bundled with the implementation)

## Self-Check: PASSED

Files created:
- `.planning/phases/33-.../33-FEEL-TARGETS.md` — FOUND
- `.planning/phases/33-.../deferred-items.md` — FOUND

Commits exist (verified via `git log --oneline -5`):
- `d63be71` — RED phase: failing tests for debug warp_target Ctrl+4..7 — FOUND
- `78b2d48` — GREEN phase: feat add multi-target debug warps + deferred-items.md — FOUND
- `4326b6d` — DRAFT phase: 33-FEEL-TARGETS.md scaffold — FOUND

Targeted in-scope test suite GREEN:
`pytest tests/test_drill_dive_parity.py tests/test_fusion_fsm.py tests/test_pogo.py tests/test_destructive_drill.py tests/test_daze_shot.py tests/test_audio.py tests/test_debug.py -q` -> `39 passed in 0.23s`.
