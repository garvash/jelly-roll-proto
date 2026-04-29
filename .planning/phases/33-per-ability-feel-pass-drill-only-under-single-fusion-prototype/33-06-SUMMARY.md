---
phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
plan: 06
subsystem: debug + feel-targets + preset-bake
tags: [debug, warps, feel-targets, preset, signoff, complete]
status: COMPLETE -- 3/3 tasks done; v2.0-default baked; FUS-06 ready for verification
requires: [33-01, 33-02, 33-03, 33-04, 33-05]
provides:
  - "Multi-target debug warps Ctrl+4..7 for D-09 drill-relevant rooms"
  - "33-FEEL-TARGETS.md APPROVED with all 18 feel targets signed off"
  - "v2.0-default preset bake -- 6 panel-tunable Phase 33 keys persisted to slot_1.json"
  - "panel save_preset() now persists POGO_* keys (FEEL_GROUPS gains 'pogo')"
affects:
  - "src/core/debug.py (warp_target one-shot flag + 4 named WARP_LEVEL_* constants)"
  - "main.py:Game.update (warp consumer mirroring teleport_requested pattern)"
  - "src/ui/presets.py (FEEL_GROUPS includes 'pogo' so panel Save persists POGO_*)"
  - "assets/presets/slot_1.json (alias v2.0-default; gains 6 Phase 33 baked keys)"
  - "tests/test_debug.py (8 new test cases for Phase 33 warps)"
  - "tests/test_tuning_migration.py (14 new tests for v2.0-default bake + frozen v1.3 + FEEL_GROUPS pogo)"
  - ".planning/phases/33-.../33-FEEL-TARGETS.md (DRAFT -> APPROVED 2026-04-29)"
  - ".planning/phases/33-.../deferred-items.md (NEW; pre-existing test failures logged)"
tech-stack:
  added: []
  patterns:
    - "One-shot string-flag pattern for multi-target navigation (mirrors teleport_requested)"
    - "Falsifiable feel-target table (29-FEEL-TARGETS.md format inheritance)"
    - "Preset bake via direct JSON edit (D-11 — schema seed -> v2.0-default values dict)"
key-files:
  created:
    - ".planning/phases/33-.../33-FEEL-TARGETS.md"
    - ".planning/phases/33-.../deferred-items.md"
  modified:
    - "src/core/debug.py"
    - "main.py"
    - "src/ui/presets.py"
    - "assets/presets/slot_1.json"
    - "tests/test_debug.py"
    - "tests/test_tuning_migration.py"
decisions:
  - "Substituted 3 of 4 warp targets to closest-analog gym levels (gym.ldtk lacks soft_block tiles and Snail/Bat enemies); recorded inline in debug.py."
  - "Pre-existing test failures (10 unrelated to Plan 06) logged to deferred-items.md per scope-boundary rules."
  - "Mid-tuning gym -> output map merge (D3549cf) shifted the active world; debug warp constants still target gym levels but now boot through merged output.ldtk."
  - "Bake values are schema-default (no panel iteration). User signed off on the schema seeds: WINDUP=30, ACCEL_REGEN=1.0, POGO_BOUNCE=-2.5, POGO_COOLDOWN=0, DRILL_ENEMY_COST=15.0, SLIME_DAZE_COST=20.0."
  - "Rule 2 fix bundled into bake commit: presets.FEEL_GROUPS extended with 'pogo' so panel Save persists POGO_BOUNCE_VELOCITY + POGO_COOLDOWN_FRAMES (Phase 33 D-02 added the group but never updated FEEL_GROUPS)."
metrics:
  duration: ~25min Task 1 (RED + GREEN + DRAFT scaffold) + ~5min Task 3 (RED + GREEN bake + sign-off)
  completed: 2026-04-29
---

# Phase 33 Plan 06: Debug Warps + Feel Targets + Preset Bake (COMPLETE)

**One-liner:** Ctrl+4..7 warps to drill-relevant gym rooms via one-shot string flag; 33-FEEL-TARGETS.md signed off on all 18 falsifiable targets; 6 Phase-33-migrated keys baked into slot_1.json (alias v2.0-default); panel `Save Preset` extended to include the `pogo` group.

This plan delivers Phase 33's iteration tooling, human-verified per-ability
feel pass, and final preset bake. Task 1 shipped the warps + FEEL-TARGETS
draft autonomously; Task 2 was a `checkpoint:human-verify` that the user
approved without panel iteration (schema seeds passed all targets); Task 3
baked the schema seeds into v2.0-default and patched the panel Save surface.
Phase 33 is now ready for `/gsd-verify-work`.

## Task 1 (COMPLETE) — Debug warps + FEEL-TARGETS draft

### 1a. Debug warps (Ctrl+4..7) — `src/core/debug.py` + `main.py`

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
during planning.

| Constant                    | gym.ldtk level     | Carve-out reason                                          |
| --------------------------- | ------------------ | --------------------------------------------------------- |
| `WARP_LEVEL_CRACKED_V`      | `Gym_AccelRunway`  | Only gym level with `cracked_V` tiles (9 tiles)           |
| `WARP_LEVEL_SOFT_BLOCK`     | `Gym_GapTrio`      | No level has `soft_block`; gap-traversal is closest analog |
| `WARP_LEVEL_ENEMY_CLUSTER`  | `Gym_HeightSteps`  | No level has Snail/Bat entities; open playground analog   |
| `WARP_LEVEL_JUICE_DRAIN`    | `Gym_ZigzagShaft`  | No level has dedicated juice-drain hazards; vertical shaft |

### 1b. 33-FEEL-TARGETS.md DRAFT (signed off in Task 2)

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

Plus a Reference Values table (17 tunables with starting values + sources).

### 1c. Tests

`tests/test_debug.py` extended with 8 Phase 33 cases. All 14 cases GREEN.

## Mid-tuning fixes (between Task 2 checkpoint and resume)

While the user evaluated the 18 feel targets, four bugs surfaced and were
landed on `main` before Task 3 resumed. Each is preserved in this worktree's
ancestry (verified at startup; base = `a5673e7`):

| Commit    | Fix                                                                            |
| --------- | ------------------------------------------------------------------------------ |
| `bbbe39b` | `fix(audio)`: use channel `0` instead of nonexistent `-1` auto-channel sentinel |
| `cb9a349` | `fix(fusion)`: `force_exit` fused-idle FSM when juice hits 0                    |
| `5ecfd1f` | `fix(drill)`: revert 100% entry gate to v1.3 `juice > 0` (felt restrictive)    |
| `d3549cf` | `feat(33-06)`: merge gym.ldtk into output.ldtk + add Ctrl+8 boss warp           |
| `a5673e7` | `feat(33-06)`: switch loader to merged output world; commit re-exported simplified |

These are not Plan 06 deviations — they are user-discovered tuning bugs
landed inline during the human-verify checkpoint. They are noted here so
the verifier sees the full ancestry of the v2.0-default sign-off.

## Task 2 (COMPLETE) — User feel-target sign-off

User approved all 18 feel targets via "approved" resume signal without
panel iteration. All schema-default values from physics-schema.json (the
Plan 02 baseline) passed every target with the mid-tuning fixes above
applied. The drill identity ("blindfolded observer" SFX test, earthbound
particle palette, 7-cue audio surface) is signed off; FUS-06 success
criterion #1 ("distinguishable windup -> sustain -> end curve") is
satisfied.

`33-FEEL-TARGETS.md` header flipped DRAFT -> APPROVED 2026-04-29; Results
+ Sign-off sections populated.

## Task 3 (COMPLETE) — Preset bake into v2.0-default

Per D-11, the 6 panel-tunable Phase-33-migrated keys are persisted into
`assets/presets/slot_1.json` (alias `v2.0-default`) at the schema-default
values that the user signed off on. `_v1.3-reference.json` stays FROZEN
(no diff).

### Baked values

| Key                       | Value | Schema group | Source                              |
| ------------------------- | ----- | ------------ | ----------------------------------- |
| WINDUP_DURATION_FRAMES    | 30    | fusion       | Phase 33 D-01 (FUSION-DESIGN draft) |
| ACCELERATED_REGEN_RATE    | 1.0   | fusion       | Phase 33 D-01 (~2x passive 0.5)     |
| POGO_BOUNCE_VELOCITY      | -2.5  | pogo         | Phase 33 D-02                       |
| POGO_COOLDOWN_FRAMES      | 0     | pogo         | Phase 33 D-02                       |
| DRILL_ENEMY_COST          | 15.0  | drill        | Phase 33 D-05                       |
| SLIME_DAZE_COST           | 20.0  | slime_juice  | Phase 33 D-17                       |

### Bundled Rule 2 fix — panel Save persistence for POGO_*

Phase 33 D-02 added the `pogo` group to `physics-schema.json`, but
`src/ui/presets.FEEL_GROUPS` was never extended. Without a fix,
`save_preset()` silently drops POGO_BOUNCE_VELOCITY + POGO_COOLDOWN_FRAMES
on every panel Save (Pitfall 6 surface contract violation). Plan 06 Task 3
adds `"pogo"` to `FEEL_GROUPS` so the panel persists those keys correctly.

### TDD gate sequence (Task 3)

| Phase  | Commit    | Tests                                                            |
| ------ | --------- | ---------------------------------------------------------------- |
| RED    | `ab16552` | 14 new failing tests in `test_tuning_migration.py` (7 fail RED)  |
| GREEN  | `7b6b554` | All 23 tests in `test_tuning_migration.py` GREEN                 |
| SIGNOFF| `ed8acf5` | 33-FEEL-TARGETS.md APPROVED                                      |

## Acceptance Criteria

### Task 1

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

### Task 3

| Check                                                                                  | Threshold | Actual                  |
| -------------------------------------------------------------------------------------- | --------- | ----------------------- |
| `python -c "import json; json.load(open('assets/presets/slot_1.json'))"`               | exits 0   | OK                      |
| `slot_1.json` `values` dict contains all 6 Phase 33 keys                               | 6/6       | 6/6                     |
| `git diff assets/presets/_v1.3-reference.json` returns empty                           | empty     | empty                   |
| `pytest tests/test_tuning_migration.py -q`                                             | exits 0   | 23 PASS                 |
| `grep "APPROVED" 33-FEEL-TARGETS.md`                                                   | >= 1      | 1 (header)              |
| `grep -c "PENDING" 33-FEEL-TARGETS.md` (rows)                                          | == 0      | 18 -- see note below    |
| `presets.FEEL_GROUPS` includes `pogo`                                                  | True      | True                    |

**PENDING-row note (user-directed deviation from plan AC):** the plan's
Task 3 AC asks for `PENDING == 0` after sign-off (i.e., flip every row
from PENDING -> PASS). The continuation prompt from the user explicitly
overrode this: "Do NOT mark individual target rows PASS -- the human
verification is implicit in user approval. Just update the doc-level
header + sign-off block." So the 18 row-level `PENDING` markers remain
as authored, while the document is signed off at the body level
(`> APPROVED 2026-04-29` header + populated Results + Sign-off sections).
Document-level approval is authoritative; row-level markers are kept as
the authored falsifiable spec for future regression reference.

### In-scope test suite (139 cases)

`pytest tests/test_tuning_migration.py tests/test_destructive_drill.py
tests/test_daze_shot.py tests/test_audio.py tests/test_pogo.py
tests/test_fusion_fsm.py tests/test_drill_dive_parity.py tests/test_debug.py
tests/test_tuning_livereach.py tests/test_fusion.py tests/test_fusion_protocol.py
tests/test_persistence.py tests/test_save_system.py -q`
-> `139 passed in 0.88s`.

The 5 `test_tuning.py` failures and 5 other failures (`test_phase22.py`,
`test_physics.py`, `test_sprite_assets.py`, `test_ldtk_migration.py`) remain
out of scope per `deferred-items.md` (pre-existing in base commit, unrelated
to Plan 06; verified by `git stash` re-run).

## Deviations from Plan

### [Rule 3 - Blocking] Closest-analog level substitutions for warp targets

- **Found during:** Task 1 Step 1 (gym.ldtk content audit).
- **Issue:** The plan recommended mapping `WARP_LEVEL_SOFT_BLOCK -> Gym_GapTrio`
  among others, but a content audit revealed gym.ldtk has NO soft_block tiles
  in any level, NO Snail/Bat enemies anywhere, and only `Gym_AccelRunway`
  contains cracked_V tiles (9 tiles). The plan explicitly anticipates this
  with "if gym.ldtk lacks a feature, use the closest analog and note the
  substitution" — handled inline.
- **Fix:** Picked closest-analog gym levels for the 3 missing-feature slots.
- **Files modified:** `src/core/debug.py` (substitution rationale comments).
- **Commit:** `78b2d48`.

### [Rule 3 - Out-of-scope] Pre-existing test-suite failures logged to deferred-items.md

- **Found during:** Task 1 GREEN-phase verification (`pytest tests/ -x -q`).
- **Issue:** 10 tests fail on the base commit unrelated to Plan 06.
- **Fix:** Logged each to `.planning/phases/33-.../deferred-items.md` with
  test name, likely owner, and reason; verified pre-existing via `git stash`
  + re-run on clean tree (same 10 failures).
- **Files added:** `.planning/phases/33-.../deferred-items.md`.
- **Commit:** `78b2d48`.

### [Rule 2 - Missing critical functionality] panel Save dropped POGO_* keys

- **Found during:** Task 3 RED-phase test authoring (FEEL_GROUPS audit).
- **Issue:** Phase 33 D-02 added the `pogo` schema group, but
  `src/ui/presets.FEEL_GROUPS` was never extended. As a result,
  `save_preset()` silently drops POGO_BOUNCE_VELOCITY + POGO_COOLDOWN_FRAMES
  on every panel Save — a Pitfall 6 surface-contract violation.
- **Fix:** Added `"pogo"` to `FEEL_GROUPS` in `src/ui/presets.py`.
  `_feel_keys()` now surfaces both POGO_* keys; `save_preset()` persists
  them. New test `test_pogo_in_feel_groups_so_save_preset_persists_pogo_keys`
  guards the surface contract.
- **Files modified:** `src/ui/presets.py`, `tests/test_tuning_migration.py`.
- **Commit:** `7b6b554`.

## Commits (full plan)

| Hash      | Phase | Description                                                                |
| --------- | ----- | -------------------------------------------------------------------------- |
| `d63be71` | RED   | failing tests for debug warp_target Ctrl+4..7                              |
| `78b2d48` | GREEN | feat add multi-target debug warps + deferred-items.md                      |
| `4326b6d` | DOCS  | DRAFT scaffold: 33-FEEL-TARGETS.md                                         |
| `8e38775` | DOCS  | partial SUMMARY at Task 2 checkpoint (superseded)                          |
| (mid-tune) | FIX  | bbbe39b, cb9a349, 5ecfd1f, d3549cf, a5673e7 — see "Mid-tuning fixes" above |
| `ab16552` | RED   | failing tests for v2.0-default bake (D-11) + FEEL_GROUPS pogo              |
| `7b6b554` | GREEN | bake 6 phase-33 keys into v2.0-default + add 'pogo' to FEEL_GROUPS         |
| `ed8acf5` | DOCS  | sign off 33-FEEL-TARGETS.md (APPROVED 2026-04-29)                          |

## Sign-off

See `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md`.

> Phase 33 approved by user on 2026-04-29. Drill identity (windup -> sustain
> -> end + earthbound palette + 7-cue audio surface) signed off. Per-ability
> feel pass complete; FUS-06 ready for verification.

## Self-Check: PASSED

Files created:
- `.planning/phases/33-.../33-FEEL-TARGETS.md` — FOUND (APPROVED 2026-04-29)
- `.planning/phases/33-.../deferred-items.md` — FOUND

Files modified (Task 3):
- `assets/presets/slot_1.json` — 6 keys added; alias still `v2.0-default`
- `src/ui/presets.py` — FEEL_GROUPS gains `pogo`
- `tests/test_tuning_migration.py` — 14 new tests (all GREEN)

Files frozen (verified):
- `assets/presets/_v1.3-reference.json` — `git diff` empty

Commits exist (verified):
- `d63be71`, `78b2d48`, `4326b6d`, `8e38775` — Task 1 + partial SUMMARY
- `ab16552` (RED Task 3), `7b6b554` (GREEN Task 3), `ed8acf5` (sign-off)

Targeted in-scope test suite GREEN:
`pytest tests/test_tuning_migration.py tests/test_destructive_drill.py
tests/test_daze_shot.py tests/test_audio.py tests/test_pogo.py
tests/test_fusion_fsm.py tests/test_drill_dive_parity.py tests/test_debug.py
tests/test_tuning_livereach.py tests/test_fusion.py tests/test_fusion_protocol.py
tests/test_persistence.py tests/test_save_system.py -q` -> `139 passed in 0.88s`.
