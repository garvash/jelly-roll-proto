---
phase: 24
plan: 02
subsystem: physics-schema
tags: [schema, restructure, breaking-change, foundation]
dependency_graph:
  requires:
    - "24-01 (FND-04 wording revision; did not touch the schema file itself)"
  provides:
    - "assets/physics-schema.json v0.3.0 with tuning.* (raw inputs) + derived.* (converter-facing)"
    - "Flat-key namespace for Plan 03's tuning.load() loader"
    - "Group index (22 groups) for Phase 28 panel tab placement (D-14)"
  affects:
    - "assets/physics-schema.json"
    - "External pml-to-ldtk converter contract (breaking change, documented in Plan 06)"
tech_stack:
  added: []
  patterns:
    - "Raw-inputs-vs-derived split in a single JSON Schema document"
    - "Group-scoped namespacing with globally-unique flat leaves (D-15 invariant)"
    - "One-level-deeper lift-and-shift preserving byte-identical value shapes (D-09)"
key_files:
  created: []
  modified:
    - "assets/physics-schema.json"
decisions:
  - "Mirrored constants.py comment headers into 22 tuning.* groups verbatim (D-08 planner discretion)"
  - "Preserved intra-group key order to match constants.py top-to-bottom for diff-friendliness"
  - "Kept top-level tile_size=16 and fps=60 metadata keys (distinct from tuning.tile.TILE_SIZE which uses UPPER_SNAKE)"
  - "HAZARD_DRAIN_RATES serialised with JSON string keys ('6','7','8') — Plan 03's loader re-casts to int"
metrics:
  duration_seconds: 420
  completed: 2026-04-11
  tasks: 1
  files_changed: 1
requirements_completed:
  - FND-01
---

# Phase 24 Plan 02: Schema Restructure Summary

**One-liner:** Flipped `physics-schema.json` from v0.2.0 (derived values only) to v0.3.0 (raw inputs under `tuning.*` + derived values under `derived.*`), placing every one of the 87 named constants from `src/core/constants.py` into exactly one of 22 system-scoped groups with globally unique flat leaves.

## What Changed

### assets/physics-schema.json (Task 1)

Version bumped `0.2.0` → `0.3.0`. Top-level keys reshaped to exactly the D-06 nine: `$schema`, `title`, `description`, `version`, `updated`, `fps`, `tile_size`, `tuning`, `derived` (in that order).

**`source_constants` block deleted.** Its six values (GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, MAX_FALL_SPEED, FALLING_GRAVITY_MULTIPLIER, TILE_SIZE) now live under their natural tuning groups: five inside `tuning.movement`, TILE_SIZE inside `tuning.tile`.

**`tuning.*` added with 22 groups** (order matches plan §interfaces exactly):

1. `tuning.tile` — TILE_SIZE, TILE_EMPTY (2 leaves)
2. `tuning.display` — SCREEN_W, SCREEN_H, VIEWPORT_W, VIEWPORT_H, HUD_H, CULL_MARGIN (6)
3. `tuning.sprite` — SPRITE_SIZE, BOSS_SPRITE_SIZE (2)
4. `tuning.hazards` — HAZARD_DRAIN_SLOW/MEDIUM/FAST, HAZARD_DRAIN_RATES, SHIELD_T2_DRAIN_REDUCTION, HAZARD_HP_DRAIN_INTERVAL, SHIELD_REACTIVATION_COOLDOWN (7)
5. `tuning.movement` — WALK_ACCEL, WALK_FRICTION, MAX_WALK_SPEED, GRAVITY, MAX_FALL_SPEED, JUMP_FORCE, VARIABLE_JUMP_REDUCTION, FALLING_GRAVITY_MULTIPLIER (8)
6. `tuning.forgiving` — COYOTE_TIME, JUMP_BUFFER (2)
7. `tuning.wall` — WALL_SLIDE_FRICTION, WALL_JUMP_X_IMPULSE, WALL_JUMP_Y_FORCE (3)
8. `tuning.slime_follow` — SLIME_FOLLOW_DELAY, SLIME_MAX_DIST, SLIME_REFORM_DIST, SLIME_LERP_FACTOR (4)
9. `tuning.slime_juice` — JUICE_MAX, JUICE_REGEN_RATE, JUICE_MIN_SCALE, SLIME_SPIT_COST (4)
10. `tuning.projectile` — PROJECTILE_SPEED, SPIT_AIM_RANGE, BOSS_ROCK_SPEED (3)
11. `tuning.drill` — DRILL_SPEED, DRILL_DRIFT_SPEED, DRILL_IMPACT_COST, DRILL_ACTIVATION_COST, DRILL_BLOCK_REFUND (5)
12. `tuning.juice_effects` — DRILL_SHAKE_DURATION, DRILL_HITSTOP_FRAMES (2)
13. `tuning.health` — PLAYER_MAX_HP, INVULN_DURATION, KNOCKBACK_FORCE_X, KNOCKBACK_FORCE_Y (4)
14. `tuning.dash` — DASH_SPEED, DASH_DURATION, DASH_IFRAMES, DASH_COOLDOWN (4)
15. `tuning.fusion` — RECALL_SPEED, RECALL_OVERLAP_DIST, MANA_SHIELD_COST, SLIME_DISSIPATE_COOLDOWN, RECALL_TRAIL_COLOR, SPIT_HOLD_THRESHOLD, HOLD_TAP_THRESHOLD (7)
16. `tuning.slime_ram` — RAM_SPEED, RAM_DIAGONAL_FACTOR, RAM_BLOCK_COST, RAM_INVINCIBLE (4)
17. `tuning.charge_shot` — CHARGE_SHOT_SPEED, CHARGE_SHOT_SIZE, CHARGE_SHOT_DAMAGE, CHARGE_RECOIL_FORCE, CHARGE_WINDUP_DURATION (5)
18. `tuning.boost` — BOOST_FORCE, BOOST_JUICE_COST, BOOST_RECOMMIT_WINDOW, BOOST_DOWNWARD_DAMAGE_W, BOOST_DOWNWARD_DAMAGE_H (5)
19. `tuning.gates` — DRILL_CRACKED_V_COST, BOOST_CRACKED_V_COST (2)
20. `tuning.save` — MAX_HP_CAP, MAX_JUICE_CAP, SAVE_FILE (3)
21. `tuning.death` — DEATH_FREEZE_FRAMES, DEATH_FADE_FRAMES (2)
22. `tuning.save_point` — SAVE_PULSE_CYCLE, SAVE_PULSE_HALF, SAVE_PROMPT_DURATION (3)

Total: **87 unique leaf keys** across 22 groups. 1-to-1 correspondence with top-level UPPER_SNAKE_CASE assignments in `src/core/constants.py` (verified by regex cross-scan: zero missing, zero extra). D-15 name-uniqueness invariant holds.

**`derived.*` added** as a one-level-deeper lift-and-shift of the v0.2.0 top-level blocks. The five inner dicts (`player`, `jump`, `fall`, `clearance`, `placement_rules`) are byte-identical to their v0.2.0 positions — no field renames, no value changes, no added/removed keys, all `note` and `*_note` comment strings preserved verbatim (D-09).

Non-scalar leaves preserved as specified:
- `TILE_EMPTY` — `[15, 15]` (JSON array of two ints)
- `HAZARD_DRAIN_RATES` — `{"6": 0.25, "7": 0.75, "8": 1.5}` (string keys; loader re-casts to int in Plan 03)
- `RAM_INVINCIBLE` — `true` (JSON bool)
- `SAVE_FILE` — `"save.json"` (string)

## Tasks Completed

| Task | Name                                                          | Commit  | Files                        |
| ---- | ------------------------------------------------------------- | ------- | ---------------------------- |
| 1    | Write physics-schema.json v0.3.0 with tuning.* and derived.*  | 108e129 | assets/physics-schema.json   |

## Verification

All plan acceptance criteria from `<acceptance_criteria>` passed in a single Python command:

```
version == '0.3.0'                                                                       ✓
top-level keys == {$schema,title,description,version,updated,fps,tile_size,tuning,derived}  ✓
top-level key ORDER == [$schema,title,description,version,updated,fps,tile_size,tuning,derived] ✓
'source_constants' not in schema                                                          ✓
tuning.movement.GRAVITY == 0.0875                                                         ✓
tuning.movement.JUMP_FORCE == -3.25                                                       ✓
tuning.movement.MAX_WALK_SPEED == 1.25                                                    ✓
tuning.movement.MAX_FALL_SPEED == 2.5                                                     ✓
derived.jump.max_height_tiles == 3                                                        ✓
derived.jump.max_width_tiles == 5                                                         ✓
derived.clearance.min_vertical_tiles == 1                                                 ✓
tuning.slime_ram.RAM_INVINCIBLE is True (bool, not 1)                                     ✓
tuning.save.SAVE_FILE == 'save.json'                                                      ✓
flat-leaf uniqueness: 87 leaves, 87 unique (D-15)                                          ✓
tuning group ORDER == 22-entry expected list                                              ✓
derived.keys() == {player,jump,fall,clearance,placement_rules}                            ✓
```

**Extra cross-check performed (not in plan, Rule 2 correctness):** regex-scanned `src/core/constants.py` for all top-level `UPPER_SNAKE_CASE =` assignments and compared against the set of tuning.* leaves. Result: **87 constants.py names ↔ 87 tuning.* leaves, zero missing, zero extra.** This proves "every named constant in constants.py has exactly one entry under some tuning.* group" literally, not just approximately.

**Note on leaf count:** Plan frontmatter says "~60 named constants", plan §interfaces breakdown tallies to 87. The actual value is 87; `constants.py` has grown since the phase was scoped. All 87 are correctly placed per the plan's explicit per-group member lists.

## Deviations from Plan

None. The plan was extraordinarily precise — every group name, every key name, every value was spelled out in `<action>`. Task 1 was a literal transcription of those spec blocks into JSON form, followed by the plan's own verification commands. No bugs, no missing functionality, no blockers, no architectural decisions. No auto-fixes of Rule 1/2/3 were needed; no Rule 4 checkpoints were needed.

The only sub-plan discretionary choice (promised to the planner under D-08/§interfaces): intra-group key order matches `constants.py` top-to-bottom for diff-friendliness. This is what the plan said to do.

## Auth Gates Hit

None.

## Deferred Issues

None.

## Known Stubs

None. The schema file is complete data, not a placeholder. Plan 03 (tuning loader) will read it as-is.

## Self-Check: PASSED

- `assets/physics-schema.json` — present, parses as valid JSON, 22 tuning groups + 5 derived blocks, 87 unique leaves
- Commit `108e129` — found in `git log` (`feat(24-02): restructure physics-schema to v0.3.0 with tuning.* and derived.*`)
- `.planning/phases/24-tuning-foundation-schema-inversion/24-02-schema-restructure-SUMMARY.md` — this file, present
- Worktree base rebased to `c803e16` (per worktree_branch_check) before any edits — verified
- No unintended file modifications: `git diff --stat c803e16..HEAD` shows exactly `assets/physics-schema.json` + this SUMMARY
