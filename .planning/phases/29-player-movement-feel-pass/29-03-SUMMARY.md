---
phase: 29-player-movement-feel-pass
plan: 03
subsystem: movement
tags: [tuning, wall, preset, derived-bake, sign-off]

# Dependency graph
requires:
  - plan: 29-01
    provides: FEEL-TARGETS.md draft, Level_Test, slot_0 v1.3-baseline
  - plan: 29-02
    provides: slot_1 v2.0-wip with ground+air tuned values, F4 overlay fix, buffered-jump variable-height fix
provides:
  - slot_1.json alias "v2.0-default" (promoted from v2.0-wip)
  - slot_2.json alias "tight" (preserved playtest end-state; equals v2.0-default for non-wall values)
  - slot_3.json alias "floaty" (Hollow Knight-style per D-08)
  - assets/physics-schema.json with derived.jump baked from v2.0-default (max_height_tiles=4, max_width_tiles=6)
  - 29-FEEL-TARGETS.md with PASS annotations on all 15 targets + user sign-off block
affects: [30, 31, 33]  # downstream v2.0 phases consume v2.0-default preset + baked derived values

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Preset capture workflow: tune via F1 panel -> save_preset(slot, alias) -> tuning.save() + tuning.bake_derived() for active preset only"
    - "derived.jump.max_height_note / max_width_note refresh is part of the bake ceremony when the active preset changes"

key-files:
  created:
    - .planning/phases/29-player-movement-feel-pass/29-03-SUMMARY.md
  modified:
    - assets/presets/slot_1.json        # alias v2.0-wip -> v2.0-default, values unchanged from 29-02
    - assets/presets/slot_2.json        # alias tight preserved; non-wall values == v2.0-default (intentional)
    - assets/presets/slot_3.json        # alias floaty, D-08 Hollow Knight-style values
    - assets/physics-schema.json        # tuning.movement/forgiving/wall locked to v2.0-default; derived.jump baked; derived notes refreshed
    - .planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md  # Result column + Results section + Sign-off block

key-decisions:
  - "Wall tuning values: WALL_SLIDE_FRICTION=0.2 (kept), WALL_JUMP_X_IMPULSE 1.5 -> 3.0, WALL_JUMP_Y_FORCE -1.75 -> -3.0. User tuned via F1 Jump tab in Gym_WallSlide + zigzag shaft; all three M-W targets pass."
  - "Tight preset (slot_2) intentionally kept identical to v2.0-default for non-wall values. User elected to defer a Celeste-style tightening pass rather than ship a half-tuned identity. slot_2 retains the user's tight-session wall values from playtest."
  - "Floaty preset (slot_3) regenerated per D-08 Hollow Knight-style: GRAVITY 0.055, JUMP_FORCE -3.5, FALLING_GRAVITY_MULTIPLIER 1.2, COYOTE_TIME 14, JUMP_BUFFER 10, WALL_SLIDE_FRICTION 0.3, WALL_JUMP_X_IMPULSE 1.3, WALL_JUMP_Y_FORCE -2.0."
  - "Derived bake ran from v2.0-default active state. Output: max_height_px=64 (4.0 tiles exact), max_width_px=97 (6.06 tiles, floored to 6). Notes refreshed to reflect the new integration output rather than the stale v1.3 strings."
  - "slot_0 alias 'v1.3-baseline' preserved unchanged across the entire phase (T-29-06 integrity marker still intact)."

patterns-established:
  - "Preset-bake-sign-off ceremony: save active preset -> regenerate variant presets -> restore active -> tuning.save() -> tuning.bake_derived() -> refresh derived notes -> update FEEL-TARGETS.md with PASS + Sign-off"

requirements-completed: [MOV-04, MOV-06]

# Metrics
duration: ~1 day (continuation session)
completed: 2026-04-19
---

# Phase 29 Plan 03: Wall Tuning, Preset Capture, Derived Bake, Sign-off Summary

**Completed the movement feel pass: locked wall values, promoted v2.0-wip to v2.0-default, regenerated the floaty identity preset, baked derived jump values into the schema, and signed off on all 15 feel targets.**

## Accomplishments

- **Wall tuning**: WALL_SLIDE_FRICTION=0.2 (unchanged), WALL_JUMP_X_IMPULSE 1.5 -> 3.0, WALL_JUMP_Y_FORCE -1.75 -> -3.0. M-W01, M-W02, M-W03 all PASS.
- **Preset set shipped** (4 of 4):
  - slot_0: `v1.3-baseline` -- frozen integrity marker, unchanged since 29-01
  - slot_1: `v2.0-default` -- active preset (renamed from v2.0-wip, values unchanged from 29-02)
  - slot_2: `tight` -- preserved; non-wall values intentionally equal v2.0-default; future tightening pass deferred
  - slot_3: `floaty` -- regenerated per D-08
- **Derived bake**: `python -m src.core.tuning bake` produced `max_height_tiles=4` / `max_height_px=64` and `max_width_tiles=6` / `max_width_px=97` from the live v2.0-default tuning state.
- **Derived notes refreshed** in physics-schema.json: both `max_height_note` and `max_width_note` now describe the v2.0-default integration output (previously referenced v1.3 floats 3.875 / 5.5625).
- **Feel targets signed off**: 29-FEEL-TARGETS.md now carries a `Result` column on every row with PASS for all 15 M-XX targets, plus a dated Results + Sign-off block. User approved phase 2026-04-19.

## Values Reference (v2.0-default -- active after this plan)

| Group | Key | v1.3 baseline | v2.0-default |
|-------|-----|---------------|--------------|
| movement | WALK_ACCEL | 0.125 | 0.15 |
| movement | WALK_FRICTION | 0.15 | 0.2 |
| movement | MAX_WALK_SPEED | 1.25 | 1.9 |
| movement | GRAVITY | 0.0875 | 0.13 |
| movement | MAX_FALL_SPEED | 2.5 | 4.0 |
| movement | JUMP_FORCE | -3.25 | -4.0 |
| movement | VARIABLE_JUMP_REDUCTION | 0.5 | 0.5 |
| movement | FALLING_GRAVITY_MULTIPLIER | 1.8 | 2.8 |
| forgiving | COYOTE_TIME | 12 | 11 |
| forgiving | JUMP_BUFFER | 8 | 7 |
| wall | WALL_SLIDE_FRICTION | 0.2 | 0.2 |
| wall | WALL_JUMP_X_IMPULSE | 1.5 | 3.0 |
| wall | WALL_JUMP_Y_FORCE | -1.75 | -3.0 |

| Derived (baked 2026-04-19) | Value |
|----------------------------|-------|
| derived.jump.max_height_tiles | 4 |
| derived.jump.max_height_px | 64 |
| derived.jump.max_width_tiles | 6 |
| derived.jump.max_width_px | 97 |

## Commits

| Task | Name | Hash | Notes |
|------|------|------|-------|
| 1 | Wall tuning playtest loop | 589636c | locked wall values into physics-schema.json (slide=0.2, jump_x=3.0, jump_y=-3.0) |
| 2 | Save presets and bake derived | 2a0fa1a | slot_1 alias v2.0-default; slot_3 regenerated floaty; derived baked |
| 3 | Refresh derived notes, mark feel targets PASS, sign off | 5ee4aa6 | physics-schema.json note refresh + 29-FEEL-TARGETS.md results + sign-off |

## Decisions Made

- **Tight preset intentionally deferred.** User elected to keep slot_2 equal to v2.0-default for non-wall values rather than ship a half-tuned Celeste-style identity. The plan's Step 2 starting values (WALK_ACCEL 0.35, FRICTION 0.35, etc.) were treated as discretionary scaffolding, not a contract. A future tightening pass will re-tune slot_2 with dedicated playtest attention. Documented in 29-FEEL-TARGETS.md Sign-off block.
- **Derived bake scope.** Only the numeric jump block was rebaked (`max_*_tiles` / `max_*_px`). `comfortable_*` values and `derived.player` / `derived.fall` / `derived.clearance` / `derived.placement_rules` are hand-authored curation and were not touched, per tuning.bake_derived docstring.
- **Derived notes refreshed in plan scope.** bake_derived() deliberately does not overwrite the `*_note` strings (they are curation, not integration output). Refreshing them when the active preset changes is the bake ceremony's responsibility; this plan treated it as a correctness requirement (Rule 2) so the converter-facing schema does not advertise stale v1.3 math.
- **slot_0 integrity marker verified unchanged.** T-29-06 mitigation required confirming `alias: v1.3-baseline` at phase exit. Verified.

## Deviations from Plan

**1. [User directive] Tight preset not fully differentiated from v2.0-default.**

- **Plan expectation**: slot_2 "tight" should push Celeste-style (high accel ~0.35+, high friction ~0.35+, short coyote ~5, etc.) per D-07.
- **What shipped**: slot_2 non-wall values equal v2.0-default. Wall values retained from user's tight-session playtest end-state (preserved in commit `483eee7` prior to this plan).
- **User directive**: "Keep tight preset identical to v2.0-default for non-wall values (future pass will re-tune). No slot_2 changes needed."
- **Rationale**: The CONTEXT.md D-10 decision requires 4 preset files with distinct aliases (satisfied). It does not require every preset to be fully differentiated on ship day. A half-tuned tight preset would ship a worse identity than deferring, and this plan already delivered v2.0-default, floaty, and wall tuning.
- **Impact**: All acceptance criteria from the plan still pass. Tracked as deferred work in 29-FEEL-TARGETS.md Sign-off.

**2. [Rule 2 - missing bake ceremony step] Added derived-note refresh.**

- **Plan expectation**: bake derived values, verify presets load, sign off.
- **Gap**: bake_derived() does not update `max_height_note` / `max_width_note` strings (by design -- they are curation). Plan did not explicitly require refreshing them.
- **What shipped**: Refreshed both notes in Task 3 to reference v2.0-default baked output (64px = 4.0 tiles; 97px ~= 6.06 tiles, floored to 6). Previous strings described v1.3 integration output (3.875 / 5.5625 tiles).
- **Rationale**: The schema is the converter's source of truth for placement rules. Advertising stale v1.3 math in the notes while the numeric values are v2.0-baked is a correctness hazard for downstream consumers (pml-to-ldtk).
- **Files modified**: assets/physics-schema.json

## Issues Encountered

None in this session. Prior checkpoints in Task 1 and Task 2 were normal playtest-loop pauses for user tuning; all wall targets passed on first tuned pass.

## Threat Flags

No new trust-boundary surface introduced. Both schema-tampering threats from the plan's STRIDE register are mitigated and verified:

- **T-29-06 (slot_0 overwrite)**: slot_0 alias remains `v1.3-baseline` -- verified via direct file read before commit.
- **T-29-07 (stale derived values)**: `python -m src.core.tuning bake` called explicitly in Task 2; `derived.jump.max_height_tiles=4` reflects actual v2.0-default tuning (not v1.3's 3). Notes refreshed in Task 3 to eliminate the "stale doc string next to fresh numeric value" sub-hazard.

## Next Phase Readiness

- v2.0-default is the shipping preset until Phase 36 milestone cap revisits the bake.
- Derived jump values (max_height=4 tiles, max_width=6 tiles) are now the converter's source of truth for placement rules.
- MOV-04, MOV-06 requirements complete.
- Phase 29 exit criteria all met: (1) feel targets list exists and every target PASS; (2) input buffering / coyote / cancel windows audited with F4 (MOV-05 closed in 29-02); (3) tight + floaty presets exist in assets/presets/ and produce coherent feels (tight deferred for identity differentiation, floaty ships distinct per D-08); (4) phase closed within timebox.
- Deferred: Celeste-style tightening pass on slot_2 (tracked in 29-FEEL-TARGETS.md Sign-off block; not a phase 29 blocker).

## Self-Check: PASSED

- `.planning/phases/29-player-movement-feel-pass/29-03-SUMMARY.md` -- FOUND (this file).
- `assets/physics-schema.json` -- FOUND; `max_height_note` + `max_width_note` refreshed to v2.0-default baked values.
- `.planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md` -- FOUND; Result column + Results section + Sign-off block present; "PASS" appears 15+ times (once per target row + summary list).
- Commit 589636c -- FOUND in git log.
- Commit 2a0fa1a -- FOUND in git log.
- Commit 5ee4aa6 -- FOUND in git log.
- slot_0 alias `v1.3-baseline` -- verified unchanged (T-29-06 mitigation intact).

---
*Phase: 29-player-movement-feel-pass*
*Completed: 2026-04-19*
