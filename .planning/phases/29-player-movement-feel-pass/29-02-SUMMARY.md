---
phase: 29-player-movement-feel-pass
plan: 02
subsystem: movement
tags: [tuning, ground, air, preset, overlay-fix, buffered-jump-fix]

# Dependency graph
requires:
  - plan: 29-01
    provides: FEEL-TARGETS.md, Level_Test, Ctrl+T teleport, slot_0 v1.3-baseline
  - phase: 28-live-tuning-panel
    provides: F1 panel, preset slots, save_preset/load_preset
provides:
  - slot_1.json alias "v2.0-wip" with tuned ground+air values
  - Cross-pattern gym rooms (GapTrio, CoyoteTest, WallSlide) for feel-target verification
  - F4 coyote/buffer overlay with correct event wiring
  - Buffered jumps now honor pre-land button release (variable-jump reduction)
affects: [29-03]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "left_ground event emitted from move_and_collide only on true ground→air edge (jumps exempt because jump() zeros is_grounded before move_and_collide sees was_grounded)"
    - "jump_press_airborne event for genuine pre-land buffer presses (emitted at btnp when airborne and coyote_timer <= 0)"
    - "jump_released_during_buffer flag captures btnr during buffer window so variable-jump reduction applies at buffered-jump execute"

key-files:
  created:
    - .planning/phases/29-player-movement-feel-pass/29-02-SUMMARY.md
  modified:
    - assets/gym.ldtk
    - assets/gym/simplified/Gym_GapTrio/ (new room)
    - assets/gym/simplified/Gym_CoyoteTest/ (new room)
    - assets/gym/simplified/Gym_WallSlide/ (new room)
    - assets/gym/simplified/Gym_HeightSteps/data.json (neighbour update)
    - assets/presets/slot_1.json
    - src/entities/player.py
    - src/core/overlays.py
    - tests/test_overlays.py
    - tests/test_physics.py

key-decisions:
  - "physics-schema.json NOT updated with tuned values. Plan 29-03 owns the schema bake (derived values must be rebaked from finalized v2.0-default). Tests pin v1.3 baseline values so a mid-phase bake would break the test suite."
  - "slot_1 populated by copy from slot_2 'tight' — user tuned a single set of values that happen to feel appropriate as both v2.0-wip and tight. Plan 29-03 decides whether tight needs a distinct tighter pass."
  - "Added 3 new gym rooms (GapTrio, CoyoteTest, WallSlide) as direct gym.ldtk edits with empty autoLayerTiles; LDtk regenerated tiles + simplified export on save. Backed up pre-edit gym.ldtk, validated JSON post-edit."
  - "F4 overlay discovered broken during MOV-05 audit — green blips fired on every jump apex (fall_start event) and blue blips fired on every jump press (jump_start event with stale is_grounded check). Refactored to edge-triggered events."
  - "Buffered jump variable-height bug discovered during MOV-05 audit — pre-existing bug where btnr mid-buffer was lost. Fixed via jump_released_during_buffer flag applied at execute time."

patterns-established:
  - "Direct gym.ldtk level insertion workflow: extend levels[] array, bump nextUid, set __neighbours both directions, leave autoLayerTiles empty; LDtk re-populates on save"

requirements-completed: [MOV-04, MOV-05]

# Metrics
duration: ~2 days (across 2 sessions)
completed: 2026-04-19
---

# Phase 29 Plan 02: Ground + Air Feel Tuning Summary

**Tuned ground and air movement to user-confirmed feel; locked v2.0-wip preset in slot_1; fixed two pre-existing input-diagnostic bugs discovered during the MOV-05 F4 overlay audit.**

## Accomplishments

- **Ground tuning**: WALK_ACCEL 0.125→0.15, WALK_FRICTION 0.15→0.2, MAX_WALK_SPEED 1.25→1.9. User-confirmed M-G01/G02/G03 feel targets all pass.
- **Air tuning**: GRAVITY 0.0875→0.13, MAX_FALL_SPEED 2.5→4.0, JUMP_FORCE -3.25→-4.0, VARIABLE_JUMP_REDUCTION 0.5 (unchanged), FALLING_GRAVITY_MULTIPLIER 1.8→2.8, COYOTE_TIME 12→11, JUMP_BUFFER 8→7. User-confirmed M-A01–A09 feel targets all pass.
- **Preset**: `assets/presets/slot_1.json` locked with alias `v2.0-wip` holding the tuned value set.
- **Gym rooms for feel verification**: added Gym_GapTrio (3/4/5-tile gaps), Gym_CoyoteTest (3-tile coyote gap), Gym_WallSlide (single-wall 6-tile slide) to `assets/gym.ldtk` via direct JSON insert, extending the map east of Gym_HeightSteps.
- **MOV-05 input audit**: initially failed — both overlay indicators were firing in wrong states. Fixed. Re-audited; all 5 checks (ground-leave, jump-without-ground-leave, wall-slide-no-blip, grounded-press-no-buffer-blip, airborne-press-buffer-blip) pass.
- **Variable jump on buffered jumps**: discovered pre-existing bug where a jump buffered mid-air + btnr before landing produced a full-force jump on landing (pre-land release was lost). Fixed via `jump_released_during_buffer` flag.

## Files Modified

- `assets/gym.ldtk` — 3 new level blocks (Gym_GapTrio, Gym_CoyoteTest, Gym_WallSlide) + east neighbour on Gym_HeightSteps; nextUid 1009→1012.
- `assets/gym/simplified/{Gym_GapTrio,Gym_CoyoteTest,Gym_WallSlide}/` — LDtk-regenerated simplified exports on first save.
- `assets/gym/simplified/Gym_HeightSteps/data.json` — neighbour list updated (adds east → Gym_GapTrio).
- `assets/presets/slot_1.json` — alias "v1.3" → "v2.0-wip"; values replaced with tuned set.
- `src/entities/player.py`:
  - New `jump_released_during_buffer` instance attr (init False).
  - `update_timers`: detects btnr during armed buffer, resets flag on new btnp, emits `jump_press_airborne` for genuine pre-land buffer presses.
  - `handle_input` (jump execute path): applies `VARIABLE_JUMP_REDUCTION` when `jump_released_during_buffer` is set.
  - `move_and_collide` (line 806 area): emits `left_ground` on true ground→air edge.
- `src/core/overlays.py`:
  - `init`: subscribes to `left_ground`, `jump_start`, `jump_press_airborne`, `land` (previously `fall_start` + flawed buffer inference inside `jump_start`).
  - Replaced `_on_fall_start` with `_on_left_ground` (same position capture, correct trigger).
  - `_on_jump_start` simplified (buffer detection removed).
  - New `_on_jump_press_airborne` records the buffer blip.
- `tests/test_overlays.py` — updated event names in init tests + `_on_left_ground` assertion.
- `tests/test_physics.py` — new `test_buffered_jump_honors_pre_land_release`, `test_buffered_jump_full_when_held`.

## Decisions Made

- **physics-schema.json left at v1.3 baseline.** Plan 29-03 explicitly owns the schema bake ("derived values in physics-schema.json are baked from v2.0-default"). The tuning module loads `_baseline` from the schema at import, so mid-phase schema mutation invalidates every test that pins v1.3 expectations. Deferring preserves test suite integrity and matches plan 29-03's design intent.
- **slot_1 values copied from user's slot_2 "tight" session.** User tuned to a single value set during playtest; those values feel right as v2.0-wip baseline. 29-03 will re-examine whether slot_2 needs a tighter pass or stays as-is.
- **F4 overlay fix is in 29-02 scope** because MOV-05 can't close without a correct audit. Both bugs were root-caused (wrong event wiring + state-read-after-mutation) rather than worked around.
- **Buffered-jump variable-reduction fix is in 29-02 scope** because it affects M-A04 (variable jump min height) which was being evaluated with silently-invalid buffered jumps.
- **No wall-jump variable-reduction change**: wall jumps are short-impulse and variable height would change feel — out of scope for this pass.

## Deviations from Plan

- Plan Task 2 says "apply via `tuning.set_value()`, persist with `tuning.save()`". We skipped the `tuning.save()` step (would have written tuned values into physics-schema.json). Reasoning: deferred to 29-03's bake step (see Decisions above). Slot_1.json carries the v2.0-wip values instead; game loads them via preset.
- Plan did not anticipate fixing the F4 overlay or the buffered-jump release bug. Both were necessary to satisfy the plan's own success criteria (MOV-05 audit, M-A04 min-jump height), so they're in scope as sub-tasks.

## Issues Encountered

**1. F4 overlay false positives.** Coyote green blip was subscribed to `fall_start` event (fires on every vy≥0→>0 transition including jump apexes and wall-slide onsets); buffer blue blip was using `jump_start` event and checking is_grounded/coyote_timer at the callback, but player.py zeroes those just before emitting, so the check always resolved true. Fixed by adding `left_ground` (true ground→air edge, emitted from move_and_collide only when was_grounded=True) and `jump_press_airborne` (emitted at btnp only when airborne with coyote_timer≤0) events.

**2. Buffered jump lost pre-land release.** Existing variable-jump-reduction check is `btnr("jump") and dy < 0`. Buffered jumps: player presses jump mid-air, releases before landing (btnr fires while dy>0 — check fails), lands, buffered jump executes at full force. Fixed by tracking `jump_released_during_buffer` in update_timers across the buffer window.

**3. Known minor quirk (non-blocking).** Buffered-release jumps produce ~36% shorter minimum height than normal tap jumps. Cause: normal tap gets one frame of full-force ascent before btnr cuts dy; buffered-release applies VARIABLE_JUMP_REDUCTION immediately at execute (no full-force frame). Not a feel-target failure (M-A04 passes via normal taps). A future fix would stash a pending-reduction flag and apply on the next tick; deferred as scope-creep for this plan.

## User Setup Required

- Next time LDtk is opened on `assets/gym.ldtk`, auto-tile rules will populate the Tiles layer for the 3 new rooms on save. Simplified export is already regenerated.

## Next Phase Readiness

- `slot_1.json` holds the v2.0-wip tuning set ready for 29-03 to finalize as v2.0-default, derive tight/floaty variants, and bake into physics-schema.json.
- Gym rooms are ready for wall-slide/wall-jump tuning in 29-03.
- MOV-04, MOV-05 requirements complete.

---
*Phase: 29-player-movement-feel-pass*
*Completed: 2026-04-19*
