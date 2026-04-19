# Phase 29: Movement Feel Targets

> **APPROVED 2026-04-19** -- Targets originally drafted from v1.3 baseline physics. All 15 targets verified PASS against v2.0-default preset (see Results + Sign-off below).

## Ground Targets

| ID | Test | Pass Condition | Fail Condition | Result |
|----|------|----------------|----------------|--------|
| M-G01 | Accel responsiveness: From standstill, reach max speed | Within 10 frames (167ms) | >15 frames (sluggish) or <4 frames (twitchy) | PASS |
| M-G02 | Stop distance: Release walk at max speed | Stop within 9 frames (150ms) | >14 frames (ice skating) or <3 frames (wall-of-friction) | PASS |
| M-G03 | Run corridor feel: Run 20-tile corridor | Feels responsive to input changes, direction reversal smooth | Sluggish direction changes or uncontrollable | PASS |

## Air Targets

| ID | Test | Pass Condition | Fail Condition | Result |
|----|------|----------------|----------------|--------|
| M-A01 | 3-tile gap from standing: Jump a 3-tile gap without running start | Clear with 0.5+ tiles margin | Requires running start | PASS |
| M-A02 | 4-tile gap at full speed: Jump 4-tile gap with running start + full hold | Land 1+ tile in | Fall short | PASS |
| M-A03 | 5-tile gap at full speed: Jump 5-tile gap at max speed + full hold | Clear or just barely miss (0.08 tiles = 1.3px) | Clear by >1 tile (too far) or miss by >0.5 tile (too short) | PASS |
| M-A04 | Variable jump min height: Tap jump (instant release) | Reach 0.8-1.2 tiles | <0.5 tiles (useless) or >2 tiles (no control) | PASS |
| M-A05 | Full jump max height: Hold jump fully | Reach 3.5-4.2 tiles | <3 tiles or >5 tiles | PASS |
| M-A06 | Coyote time: Walk off ledge, jump within 12 frames | Jump executes | Falls | PASS |
| M-A07 | Coyote boundary: Walk off ledge, jump at frame 13+ | Falls (no jump) | Jump still works (too generous) | PASS |
| M-A08 | Jump buffer: Press jump 8 frames before landing | Jump triggers on land | No jump | PASS |
| M-A09 | Apex hang: At jump peak, hold direction | Brief floaty hang before descent | Sharp velocity reversal at apex | PASS |

## Wall Targets

| ID | Test | Pass Condition | Fail Condition | Result |
|----|------|----------------|----------------|--------|
| M-W01 | Wall slide speed: Slide down 6-tile wall | Noticeably slower than free fall | Same speed as free fall or barely moving | PASS |
| M-W02 | Wall jump ascent: Wall jump up 3-tile shaft | Gain at least 1.5 tiles height per jump | Lose height each jump | PASS |
| M-W03 | Wall jump zigzag: Alternate wall jumps in 3-tile wide shaft | Can ascend steadily | X impulse overshoots wall or undershoots | PASS |

---

## Reference Values (v1.3 Baseline)

These values were used to derive the pass/fail criteria above:

| Metric | Value | Source |
|--------|-------|--------|
| Frames to max walk speed | 10 frames (167ms) | WALK_ACCEL=0.125, MAX_WALK_SPEED=1.25 |
| Frames to stop from max | 9 frames (150ms) | WALK_FRICTION=0.15 |
| Jump peak height | 62.0px (3.87 tiles) | JUMP_FORCE=-3.25, GRAVITY=0.0875 |
| Variable jump peak (instant release) | 15.9px (0.99 tiles) | VARIABLE_JUMP_REDUCTION=0.5 |
| Full jump airtime | 65 frames (1.08s) | FALLING_GRAVITY_MULTIPLIER=1.8 |
| Full jump horiz distance | 81.2px (5.08 tiles) | At MAX_WALK_SPEED=1.25 |
| Coyote time | 12 frames (200ms) | COYOTE_TIME=12 |
| Jump buffer | 8 frames (133ms) | JUMP_BUFFER=8 |
| Wall slide terminal velocity | 1.25 px/frame | WALL_SLIDE_FRICTION=0.2 |
| Wall jump X impulse | 1.5 px/frame | WALL_JUMP_X_IMPULSE=1.5 |
| Wall jump Y force | -1.75 | WALL_JUMP_Y_FORCE=-1.75 |

---

## Results (2026-04-19)

All 15 feel targets verified PASS with `assets/presets/slot_1.json` (alias `v2.0-default`) loaded.

- Ground: M-G01, M-G02, M-G03 -- PASS
- Air: M-A01, M-A02, M-A03, M-A04, M-A05, M-A06, M-A07, M-A08, M-A09 -- PASS
- Wall: M-W01, M-W02, M-W03 -- PASS

Preset set shipped in `assets/presets/`:

- `_v1.3-reference.json` -- `v1.3-baseline` (frozen reference, outside 4-slot rotation)
- `slot_0.json` -- `auto` (phase 28 autosave slot, holds current live tuning state)
- `slot_1.json` -- `v2.0-default` (active)
- `slot_2.json` -- `tight` (identical to v2.0-default for non-wall values, pending a future tightening pass)
- `slot_3.json` -- `floaty` (Hollow Knight-style per D-08)

## Sign-off

Phase 29 approved by user on 2026-04-19. `v2.0-default` is the active preset and the source of `derived.*` bakes in `assets/physics-schema.json`. All 15 M-XX targets pass.

**Post-phase correction (2026-04-19):** Phase 29-01 originally repurposed `slot_0` as the frozen v1.3 baseline, conflicting with phase 28's autosave contract. Reverted inline: v1.3 values moved to `assets/presets/_v1.3-reference.json` (outside the 4-slot rotation); `slot_0` restored to `alias="auto"` per phase 28 design.

`tight` intentionally equals `v2.0-default` for non-wall values and will be re-tuned in a later tightening pass (tracked as a deferred item, not a phase 29 blocker).
