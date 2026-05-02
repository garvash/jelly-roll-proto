# Phase 34: Slime Follow/AI Feel Targets

> **PENDING** — Skeleton drafted at context-gathering (2026-05-02). Pass/Fail
> conditions are falsifiable per Phase 29/33 pattern. Final tuning values land
> in `assets/presets/v2.0-default.json` (alias `v2.0-default`, backed by
> `slot_1.json`). `_v1.3-reference.json` stays FROZEN.

Format mirrors `.planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md`
and `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md`:
each row has falsifiable Pass/Fail conditions (specific frame counts, specific
behaviors, specific gym setups). No subjective "feels good" criteria.

ID prefix scheme:
- **S-Cn** — catch-up scenarios (anchors success criterion #1)
- **S-Sn** — stuck/recovery scenarios (anchors success criterion #2)
- **S-Mn** — mode-switch scenarios (hybrid float↔ground state machine)
- **S-Ln** — look-ahead / anticipation scenarios
- **S-Pn** — panel smoothness scenarios (anchors success criterion #3)

## Catch-Up Targets (S-C1..C3)

| ID    | Test                                                                                              | Pass Condition                                                                              | Fail Condition                                                                                                | Result  |
| ----- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------- |
| S-C1  | 10-tile gap closure: Warp to Gym_AccelRunway, position slime 10 tiles behind player, hold-still   | Slime closes the 160px gap in ≤60 frames (1.0s budget per D-13)                              | Closes in >75f (sluggish) or <30f (snap-teleport feel), OR overshoots past player by >0.5 tile                  | PENDING |
| S-C2  | Dash-away-and-stop reunion: Player runs 10 tiles right at max walk speed, then stops              | Slime catches up smoothly via ease-out (sqrt) curve; arrives within 1 tile of target in ≤90f | Slime rubber-bands (visible speed jump), OR arrives but then oscillates around target, OR takes >120f          | PENDING |
| S-C3  | Mid-air gap chase: At Gym_GapTrio, player jumps a 5-tile pit; slime follows from the far side     | Slime promotes to float-mode (per S-M1), arcs across the gap, lands behind player on the far ledge | Slime falls into pit (didn't promote to float), OR floats but never lands (mode-switch broken), OR lands ahead of player | PENDING |

## Stuck/Recovery Targets (S-S1..S-S3)

| ID    | Test                                                                                              | Pass Condition                                                                              | Fail Condition                                                                                                | Result  |
| ----- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------- |
| S-S1  | Random-terrain follow: Run player through Gym_ZigzagShaft + Gym_WallSlide top-to-bottom           | Slime never visibly pinned for >30 contiguous frames; reaches player at end                  | Slime visibly stuck (no progress) for >60f, OR fails to reach player at end of route                          | PENDING |
| S-S2  | Forced-stuck pocket (NEW Gym_SlimeFollow): Player teleports into the sealed 2x2 pocket            | Stuck-detection fires within SLIME_STUCK_WINDOW_FRAMES; glow-fade plays; slime reappears inside the pocket near player | Stuck never fires (slime sits at the wall indefinitely), OR slime hard-teleports without fade, OR appears outside the pocket | PENDING |
| S-S3  | v1.0 vertical-slice route: Full playthrough Room 0 → boss room                                    | No frame in the recording where slime is permanently stuck on geometry (success criterion #2) | Any visible permanent-stuck frame, OR any panic-recovery loop (recovery firing >3x within 5s)                  | PENDING |

## Mode Switch Targets (S-M1..S-M3)

| ID    | Test                                                                                              | Pass Condition                                                                              | Fail Condition                                                                                                | Result  |
| ----- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------- |
| S-M1  | Jump → float promotion: Player jumps from flat ground at Gym_AccelRunway                          | Slime promotes to float-mode within 1 frame of player.is_grounded going False                 | Slime stays grounded after player jumps (mode flag stuck), OR mode flag flickers within the jump arc           | PENDING |
| S-M2  | Land → ground demotion: Player lands after a jump on flat ground                                  | Slime demotes to ground-mode within SLIME_FLOAT_GROUND_K_FRAMES of player landing AND slime being able to reach a tile | Slime stays floating indefinitely after player lands, OR demotes but snaps vertically to ground (no smooth ease-down) | PENDING |
| S-M3  | Boundary anti-oscillation: Player rapidly jumps in place (1f-on/1f-off pattern)                   | Slime mode does NOT toggle every frame; uses hysteresis or minimum-state-duration to stay stable | Mode flag toggles every frame, OR slime visibly jitters at the float↔ground boundary                          | PENDING |

## Look-Ahead / Anticipation Targets (S-L1..S-L2)

| ID    | Test                                                                                              | Pass Condition                                                                              | Fail Condition                                                                                                | Result  |
| ----- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------- |
| S-L1  | Constant-velocity lean: Player walks right at max speed across Gym_AccelRunway                    | Slime sits AT the path-target (lean cancels SLIME_FOLLOW_DELAY trail) within ±2px            | Slime sits SLIME_FOLLOW_DELAY frames behind target (no lean firing), OR sits >4 tiles ahead (over-lean)        | PENDING |
| S-L2  | Stationary-aim lean fallback: Player stops, holds facing-right (\|player.dx\| < ε)                | Slime drifts to a small bias in player.facing_right direction (per D-11 fallback)            | Slime sits exactly on player center (fallback didn't fire), OR drifts >1 tile ahead (fallback over-applied)    | PENDING |

## Panel Smoothness Targets (S-P1..S-P2)

| ID    | Test                                                                                              | Pass Condition                                                                              | Fail Condition                                                                                                | Result  |
| ----- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------- |
| S-P1  | Slide every slime_follow tunable across full schema range during gameplay                          | All values reachable from live panel; behavior changes smoothly with no snap-back, no NaN, no dropped frames (success criterion #3) | Any value not exposed to panel, OR slider produces a snap-back, OR NaN/exception, OR observable frame drop    | PENDING |
| S-P2  | Mid-flight tunable change: Slime is mid-catch-up; user drags SLIME_MAX_FOLLOW_SPEED slider         | Speed responds on the very next frame; no snap-back to old value; no oscillation              | Change requires re-trigger to take effect, OR slime snaps to old value once, OR enters a feedback loop          | PENDING |

---

## Reference Values (Phase 34 starting point)

These are the schema seeds + module constants entering Phase 34's tuning pass.
Final values land in `assets/presets/v2.0-default.json` (alias `v2.0-default`,
backed by `slot_1.json`). `_v1.3-reference.json` stays FROZEN.

| Tunable                          | Group           | Starting value | Source                                           |
| -------------------------------- | --------------- | -------------- | ------------------------------------------------ |
| SLIME_FOLLOW_DELAY               | slime_follow    | 16             | Existing schema (slime.py:20 deque maxlen base)  |
| SLIME_MAX_DIST                   | slime_follow    | 100            | Existing schema (reform-distance trigger)        |
| SLIME_REFORM_DIST                | slime_follow    | 8              | Existing schema                                  |
| SLIME_LERP_FACTOR                | slime_follow    | 0.4            | Existing schema                                  |
| SLIME_MAX_FOLLOW_SPEED           | slime_follow    | TBD            | Phase 34 D-05 (promoted from MAX_SHADOW_SPEED=4.0). Researcher computes peak from D-13 60f budget + ease-out curve. |
| SLIME_LOOKAHEAD_FRAMES           | slime_follow    | TBD            | Phase 34 D-11. Should be ≤ SLIME_FOLLOW_DELAY (16). |
| SLIME_LOOKAHEAD_FALLBACK_BIAS    | slime_follow    | TBD            | Phase 34 D-11 (stationary fallback in facing direction) |
| SLIME_STUCK_WINDOW_FRAMES        | slime_follow    | TBD            | Phase 34 D-10 (no-progress window before recovery) |
| SLIME_FLOAT_GROUND_K_FRAMES      | slime_follow    | TBD            | Phase 34 D-08 (mode-switch reach-tile budget)    |
| SLIME_CATCHUP_CURVE_K            | slime_follow    | TBD            | Phase 34 D-09 (sqrt curve coefficient)           |
| RECALL_TRAIL_MAX_LENGTH          | (module const)  | 6              | slime.py:74 — stays as named const per D-05 (visual only, not panel-tunable) |

---

## Results

PENDING — verification phase will fill this in after Phase 34 execution.

## Sign-off

PENDING — Phase 34 sign-off requires all S-C / S-S / S-M / S-L / S-P targets to PASS against the active preset.
