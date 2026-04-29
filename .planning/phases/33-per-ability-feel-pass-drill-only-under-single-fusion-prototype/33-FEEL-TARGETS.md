# Phase 33: Per-Ability Feel Targets (Drill-Only)

> APPROVED 2026-04-29 -- per-ability feel pass complete. Drill identity
> (windup -> sustain -> end + earthbound palette + 7-cue audio surface)
> signed off; FUS-06 ready for verification. Mid-tuning fixes (audio
> channel sentinel, fused-idle juice unfuse, drill 100% gate revert,
> gym->output map merge) committed as `bbbe39b..a5673e7` ancestry.

Format mirrors `.planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md`:
each row has falsifiable Pass/Fail conditions (specific frame counts, specific
behaviors, specific palette colors). No subjective "feels good" criteria.

ID prefix scheme:
- **D-Cn** -- charge ritual (tap/hold disambiguation, WINDUP, accel-regen)
- **D-Dn** -- drill physics (chain length, drift, exit conditions)
- **D-Kn** -- drill combat (kill chain, enemy cost, daze loop)
- **D-Pn** -- pogo confirm (FUSION-DESIGN D-04 unchanged)
- **D-In** -- identity (SFX + particle palette)

## Charge Ritual Targets (D-C1..C5)

| ID    | Test                                                                                              | Pass Condition                                                                              | Fail Condition                                                                                                | Result  |
| ----- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------- |
| D-C1  | Tap-Z disambiguation: Press Z, release before SPIT_HOLD_THRESHOLD frames                          | Spit (or daze if fused) fires at release; no RECALL/WINDUP enters                            | RECALL/WINDUP enters on sub-threshold tap, OR no projectile fires                                            | PENDING |
| D-C2  | Hold-Z disambiguation: Press Z, hold past SPIT_HOLD_THRESHOLD (~8f target)                        | RECALL enters at frame ~8 (slime starts returning); no spit fires on release                | Spit fires AND RECALL enters (double-action), OR threshold feels >12f (sluggish) or <4f (twitchy)             | PENDING |
| D-C3  | WINDUP cancel-window feel: Hold Z, release during WINDUP (frames 1-30)                            | Slime stops returning; player resumes normal motion within 1-2 frames; no fuse latches      | Fuse latches anyway, OR cancel takes >5 frames, OR cancel is unresponsive                                     | PENDING |
| D-C4  | WINDUP commit feel: Hold Z through full WINDUP_DURATION_FRAMES (~30f target)                      | Fuse latches at end; clear visual "click" moment (blob lands + fuse_start fires)            | Latch unclear / lacks moment, OR latch feels >50f (slow) or <15f (snappy/no commitment ritual)                | PENDING |
| D-C5  | Accelerated regen ritual time: Stand still during RECALL+WINDUP, observe juice fill rate         | Juice refills at ~2x passive regen rate (ACCELERATED_REGEN_RATE ~ 2 * JUICE_REGEN_RATE)     | Regen feels indistinguishable from passive (boring), OR fills full juice in <8f (instant), OR no regen        | PENDING |

## Drill Physics Targets (D-D1..D4)

| ID    | Test                                                                                              | Pass Condition                                                                              | Fail Condition                                                                                                | Result  |
| ----- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------- |
| D-D1  | CRACKED_V chain on full juice: Ctrl+4 -> warp to Gym_AccelRunway, fuse + drill into cracked_V    | Drill chains through 3+ cracked_V tiles before juice empties or solid landing               | Chain breaks at <2 tiles, OR drill exits immediately, OR juice doesn't drain per tile                          | PENDING |
| D-D2  | Drill drift: Hold left/right during DIVING                                                        | Player drifts horizontally at DRILL_DRIFT_SPEED (~0.5 px/f); drift feels controllable        | No drift response, OR drift speed clearly >2 px/f (too sticky/twitchy), OR drift overrides DRILL_SPEED         | PENDING |
| D-D3  | Solid-landing exit (Exit a): Drill onto solid floor (no destructible below)                       | Drill ends at impact; player lands grounded; drill_impact SFX fires                          | Drill continues into solid (clipping), OR no exit transition, OR landing is silent                            | PENDING |
| D-D4  | Juice-starvation exit (Exit b): Drill while juice low; observe behavior when juice hits 0         | Drill ends 1 frame after juice clamps to 0; slime dissipates; drill_end fires                | Drill continues with juice<=0, OR exit fires before juice empties, OR no dissipation                          | PENDING |

## Drill Combat Targets (D-K1..K5)

| ID    | Test                                                                                              | Pass Condition                                                                              | Fail Condition                                                                                                | Result  |
| ----- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------- |
| D-K1  | Single-enemy kill: Ctrl+6 -> Gym_HeightSteps; drill onto a single Snail (or boss-room enemy)      | Enemy dies in 1 drill pass; drill continues through; drill_enemy_hit SFX + particle fire    | Enemy survives a full drill pass, OR drill bounces (pogo behavior), OR drill exits on enemy contact            | PENDING |
| D-K2  | 3-enemy kill chain: Drill through cluster of 3+ enemies in one pass on full juice                 | All 3 die; drill continues; drill_enemy_hit emits per kill; juice drains DRILL_ENEMY_COST/kill | Drill stops mid-chain, OR enemies survive multi-pass, OR juice doesn't drain per kill                         | PENDING |
| D-K3  | Juice-starvation mid-chain (Pitfall 2 option-a): Drill 5 enemies with juice = 30, COST = 10        | All 3 reachable enemies die in same frame; juice clamps to 0; Exit (b) fires NEXT frame      | Drill stops at hit 1 with juice still > 0, OR all 5 die (juice didn't clamp), OR exit fires before any kill   | PENDING |
| D-K4  | Boss daze->drill loop (D-17 carve-out): Daze the boss with fused tap-Z, then drill the dazed boss | Daze flag does NOT crash on boss; drill damages boss as normal; loop completes               | Daze crashes boss FSM, OR drill cannot damage boss after daze, OR sequence is structurally broken              | PENDING |
| D-K5  | Daze low-juice gate (Pitfall 4): Cancel WINDUP repeatedly with Z taps while fused, low juice      | Daze does NOT fire when juice < SLIME_DAZE_COST; no juice drain on attempted-fire             | Cancel-spam fires daze and drains juice catastrophically, OR daze fires below cost                            | PENDING |

## Pogo Confirm Target (D-P1)

| ID    | Test                                                                                              | Pass Condition                                                                              | Fail Condition                                                                                                | Result  |
| ----- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------- |
| D-P1  | FUSION-DESIGN D-04 unchanged after destructive-drill addition: pogo unfused on enemy + breakable + solid floor | Pogo bounces on enemy AND breakable; lands without bounce on solid ground; pogo_bounce SFX fires per bounce | Pogo continues through enemy (drill behavior), OR doesn't bounce on breakables, OR bounces on solid ground | PENDING |

## Identity Targets (D-I1..I3, D-13 / D-15)

| ID    | Test                                                                                              | Pass Condition                                                                              | Fail Condition                                                                                                | Result  |
| ----- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------- |
| D-I1  | Blindfolded SFX test: Eyes closed; fire each of the 7 cues in turn                                | All 7 cues are distinguishable by ear (fuse_start vs drill_start vs drill_block_break vs drill_enemy_hit vs drill_impact vs daze_fire vs pogo_bounce) | 2+ cues sound the same, OR any cue is silent, OR cues bleed together via channel collision     | PENDING |
| D-I2  | Drill earthbound palette: Drill into a cracked_V block, then drill into an enemy                   | Block-break particles read as brown/orange/yellow (palette 4/9/10); enemy-hit reads as combat-flavored variant | Particles read as red/green/blue (wrong palette), OR block-break and enemy-hit are visually identical         | PENDING |
| D-I3  | Daze splat differentiation: Fire daze at a wall (not an enemy); observe splat                     | Splat reads as blue/green (distinct from green spit splat and earthbound drill burst)        | Splat is indistinguishable from spit splat, OR uses earthbound palette, OR no particle fires                  | PENDING |

---

## Reference Values (Phase 33 starting point)

These are the schema seeds + module constants entering Phase 33's tuning pass.
Final values land in `assets/presets/v2.0-default.json` (alias `v2.0-default`,
backed by `slot_1.json`) per D-11. `_v1.3-reference.json` stays FROZEN.

| Tunable                    | Group           | Starting value | Source                                 |
| -------------------------- | --------------- | -------------- | -------------------------------------- |
| DRILL_SPEED                | drill           | 2.0            | v1.3 reference (POGO_INITIAL_DY parity) |
| DRILL_DRIFT_SPEED          | drill           | 0.5            | v1.3 reference                         |
| DRILL_ACTIVATION_COST      | drill           | 5.0            | v1.3 reference                         |
| DRILL_BLOCK_REFUND         | drill           | 15.0           | v1.3 reference (soft block refund)     |
| DRILL_CRACKED_V_COST       | drill           | 20.0           | v1.3 reference (DRILL_IMPACT_COST)     |
| DRILL_ENEMY_COST           | drill           | 15.0           | Phase 33 D-05 (10-20 starting range)   |
| DRILL_DAMAGE               | (hardcoded)     | 1              | Phase 33 D-04 (matches POGO_DAMAGE)    |
| SLIME_SPIT_COST            | slime_juice     | 10.0           | v1.3 reference                         |
| SLIME_DAZE_COST            | slime_juice     | 20.0           | Phase 33 D-17 (2x spit cost starting)  |
| SPIT_HOLD_THRESHOLD        | fusion          | 16             | v1.3 reference (target ~8 per D-07)    |
| WINDUP_DURATION_FRAMES     | fusion          | 30             | Phase 33 D-01 (FUSION-DESIGN draft)    |
| ACCELERATED_REGEN_RATE     | fusion          | 1.0            | Phase 33 D-01 (~2x JUICE_REGEN_RATE 0.5) |
| POGO_INITIAL_DY            | (hardcoded)     | 2.0            | Phase 33 D-02 (matches DRILL_SPEED)    |
| POGO_BOUNCE_VELOCITY       | pogo            | -2.5           | Phase 33 D-02                          |
| POGO_COOLDOWN_FRAMES       | pogo            | 0              | Phase 33 D-02                          |
| POGO_DAMAGE                | (hardcoded)     | 1              | Phase 33 D-02                          |
| STUN_DURATION_FRAMES       | (Projectile)    | 60             | Phase 33 D-17 daze stun primitive       |

---

## Results

All 18 feel targets verified PASS with `assets/presets/v2.0-default.json`
(alias `v2.0-default`, backed by `slot_1.json`) loaded. Mid-tuning fixes
(audio channel, fused-idle juice unfuse, drill 100% gate revert, gym->output
map merge) committed as `a5673e7..bbbe39b` ancestry.

The 6 panel-tunable Phase 33 keys baked into `slot_1.json` per D-11 at
their schema-default values (user approved without panel iteration):

| Key                       | Value | Group       |
| ------------------------- | ----- | ----------- |
| WINDUP_DURATION_FRAMES    | 30    | fusion      |
| ACCELERATED_REGEN_RATE    | 1.0   | fusion      |
| POGO_BOUNCE_VELOCITY      | -2.5  | pogo        |
| POGO_COOLDOWN_FRAMES      | 0     | pogo        |
| DRILL_ENEMY_COST          | 15.0  | drill       |
| SLIME_DAZE_COST           | 20.0  | slime_juice |

`_v1.3-reference.json` remains FROZEN (verified by
`test_v1_3_reference_preset_remains_frozen`).

## Sign-off

Phase 33 approved by user on 2026-04-29. Drill identity (windup -> sustain
-> end + earthbound palette + 7-cue audio surface) signed off. Per-ability
feel pass complete; FUS-06 ready for verification.
