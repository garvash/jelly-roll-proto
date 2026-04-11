---
phase: 24-tuning-foundation-schema-inversion
plan: 02
type: execute
wave: 2
depends_on: [24-01]
files_modified:
  - assets/physics-schema.json
autonomous: true
requirements:
  - FND-01
tags: [schema, restructure, breaking-change]
must_haves:
  truths:
    - "physics-schema.json version is 0.3.0"
    - "Top-level keys are exactly: $schema, title, description, version, updated, fps, tile_size, tuning, derived"
    - "source_constants block is deleted"
    - "derived.player / derived.jump / derived.fall / derived.clearance / derived.placement_rules all exist with unchanged field shapes"
    - "tuning.* has ~22 groups mirroring constants.py comment headers"
    - "Every named constant in constants.py has exactly one entry under some tuning.* group (flat-key uniqueness)"
  artifacts:
    - path: "assets/physics-schema.json"
      provides: "v0.3.0 restructured schema with tuning.* (raw inputs) and derived.* (converter-facing)"
      contains: "\"version\": \"0.3.0\""
  key_links:
    - from: "assets/physics-schema.json tuning.movement.GRAVITY"
      to: "src/core/constants.py GRAVITY"
      via: "flat-key → group index built by tuning.load()"
      pattern: "\"GRAVITY\":\\s*0.0875"
    - from: "assets/physics-schema.json derived.jump.max_height_tiles"
      to: "v0.2.0 player block (unchanged shape)"
      via: "one-level-deeper move, no field renames"
      pattern: "\"max_height_tiles\":\\s*3"
---

<objective>
Rewrite `assets/physics-schema.json` from v0.2.0 to v0.3.0: move the existing top-level converter-facing blocks under `derived.*` unchanged, delete `source_constants`, and add a new `tuning.*` block that holds every named constant from `src/core/constants.py` grouped by comment-header section with globally-unique leaf keys.

Purpose: This is the source-of-truth flip (D-06 through D-09). After this plan, the JSON file contains every raw input the game uses plus the converter's derived view — no behavior change on disk until Plan 03's loader reads it.

Output: `assets/physics-schema.json` bumped to v0.3.0, structurally reshaped, schematically equivalent (same GRAVITY value, same derived.jump.max_height_tiles, etc.).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@assets/physics-schema.json
@src/core/constants.py
@.planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md

<interfaces>
<!-- The 22 tuning groups mirror constants.py comment headers. Every leaf key under tuning.* must be globally unique (D-15). -->

constants.py headers → tuning group name → member keys:

1. "Tile Constants"                        → tuning.tile          → TILE_SIZE, TILE_EMPTY
2. "Screen / Display"                      → tuning.display       → SCREEN_W, SCREEN_H, VIEWPORT_W, VIEWPORT_H, HUD_H, CULL_MARGIN
3. "Sprite Dimensions"                     → tuning.sprite        → SPRITE_SIZE, BOSS_SPRITE_SIZE
4. "Zone Hazard Drain Rates" (+ adjacent)  → tuning.hazards       → HAZARD_DRAIN_SLOW, HAZARD_DRAIN_MEDIUM, HAZARD_DRAIN_FAST, HAZARD_DRAIN_RATES, SHIELD_T2_DRAIN_REDUCTION, HAZARD_HP_DRAIN_INTERVAL, SHIELD_REACTIVATION_COOLDOWN
5. "Horizontal Movement" + "Vertical Movement" → tuning.movement  → WALK_ACCEL, WALK_FRICTION, MAX_WALK_SPEED, GRAVITY, MAX_FALL_SPEED, JUMP_FORCE, VARIABLE_JUMP_REDUCTION, FALLING_GRAVITY_MULTIPLIER
6. "Forgiving Mechanics"                   → tuning.forgiving     → COYOTE_TIME, JUMP_BUFFER
7. "Wall Slide/Jump"                        → tuning.wall          → WALL_SLIDE_FRICTION, WALL_JUMP_X_IMPULSE, WALL_JUMP_Y_FORCE
8. "Slime Follow Constants"                → tuning.slime_follow  → SLIME_FOLLOW_DELAY, SLIME_MAX_DIST, SLIME_REFORM_DIST, SLIME_LERP_FACTOR
9. "Slime Juice Resource"                  → tuning.slime_juice   → JUICE_MAX, JUICE_REGEN_RATE, JUICE_MIN_SCALE, SLIME_SPIT_COST
10. "Projectile"                            → tuning.projectile    → PROJECTILE_SPEED, SPIT_AIM_RANGE, BOSS_ROCK_SPEED
11. "Drill Dive"                            → tuning.drill         → DRILL_SPEED, DRILL_DRIFT_SPEED, DRILL_IMPACT_COST, DRILL_ACTIVATION_COST, DRILL_BLOCK_REFUND
12. "Juice Effects"                         → tuning.juice_effects → DRILL_SHAKE_DURATION, DRILL_HITSTOP_FRAMES
13. "Player Health & Damage"                → tuning.health        → PLAYER_MAX_HP, INVULN_DURATION, KNOCKBACK_FORCE_X, KNOCKBACK_FORCE_Y
14. "Basic Dash"                            → tuning.dash          → DASH_SPEED, DASH_DURATION, DASH_IFRAMES, DASH_COOLDOWN
15. "Fusion System" + "Slime Recall Visual" + "Spit vs Recall threshold" + "Directional Slime Hold" → tuning.fusion → RECALL_SPEED, RECALL_OVERLAP_DIST, MANA_SHIELD_COST, SLIME_DISSIPATE_COOLDOWN, RECALL_TRAIL_COLOR, SPIT_HOLD_THRESHOLD, HOLD_TAP_THRESHOLD
16. "Slime Ram"                             → tuning.slime_ram     → RAM_SPEED, RAM_DIAGONAL_FACTOR, RAM_BLOCK_COST, RAM_INVINCIBLE
17. "Charge Shot" + "Charge Shot Recoil" + "Charge Shot Windup" → tuning.charge_shot → CHARGE_SHOT_SPEED, CHARGE_SHOT_SIZE, CHARGE_SHOT_DAMAGE, CHARGE_RECOIL_FORCE, CHARGE_WINDUP_DURATION
18. "Slime Boost"                           → tuning.boost         → BOOST_FORCE, BOOST_JUICE_COST, BOOST_RECOMMIT_WINDOW, BOOST_DOWNWARD_DAMAGE_W, BOOST_DOWNWARD_DAMAGE_H
19. "CRACKED_V Gate Breaking"               → tuning.gates         → DRILL_CRACKED_V_COST, BOOST_CRACKED_V_COST
20. "Save System"                           → tuning.save          → MAX_HP_CAP, MAX_JUICE_CAP, SAVE_FILE
21. "Death Animation"                       → tuning.death         → DEATH_FREEZE_FRAMES, DEATH_FADE_FRAMES
22. "Save Point Visual"                     → tuning.save_point    → SAVE_PULSE_CYCLE, SAVE_PULSE_HALF, SAVE_PROMPT_DURATION

Note: TILE_SIZE lives in BOTH constants.py (top of file) and the existing top-level schema key. The authoritative home becomes tuning.tile.TILE_SIZE. The top-level `tile_size: 16` and `fps: 60` keys STAY at the top level (D-06 lists them among the top-level keys) — they are metadata the converter reads without traversing `tuning`. This is not a duplicate leaf key because "tile_size" (lowercase) at the top level and "TILE_SIZE" (uppercase) under tuning.tile are distinct key strings; the flat-key namespace for the loader is only the UPPER_SNAKE_CASE leaves under tuning.*.

Non-scalar leaves that MUST be preserved verbatim:
- TILE_EMPTY = [15, 15]             (list of two ints)
- HAZARD_DRAIN_RATES = {"6": 0.25, "7": 0.75, "8": 1.5}   (JSON object — Python int keys become JSON string keys; the loader re-casts to int when exposing this constant. Plan 03 handles that.)
- RAM_INVINCIBLE = true             (JSON bool)
- SAVE_FILE = "save.json"           (string)

derived.* block shape (exact one-level-deeper move from v0.2.0 — NO field renames):

derived = {
  "player":          <v0.2.0 top-level "player" block, byte-identical>,
  "jump":            <v0.2.0 top-level "jump" block, byte-identical>,
  "fall":            <v0.2.0 top-level "fall" block, byte-identical>,
  "clearance":       <v0.2.0 top-level "clearance" block, byte-identical>,
  "placement_rules": <v0.2.0 top-level "placement_rules" block, byte-identical>
}
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Write physics-schema.json v0.3.0 with tuning.* and derived.*</name>
  <files>assets/physics-schema.json</files>
  <read_first>
    - assets/physics-schema.json (current v0.2.0 — 64 lines, you must preserve every value exactly)
    - src/core/constants.py (all 156 lines — every named constant must land in exactly one tuning.* group)
    - .planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md (§decisions D-06..D-09, D-15)
  </read_first>
  <action>
    Overwrite `assets/physics-schema.json` with the v0.3.0 structure. Use the Write tool (not cat heredoc).

    The file MUST have these top-level keys in this order:
    1. "$schema"       → "https://json-schema.org/draft/2020-12/schema"
    2. "title"         → "Jelly Roll Proto -- Physics Contract"
    3. "description"   → "Physics tuning source of truth. `tuning.*` holds raw game inputs grouped by system (mirrors src/core/constants.py comment headers). `derived.*` holds converter-facing values computed from `tuning.*` via Euler integration — updated explicitly via `python -m src.core.tuning bake`. The pml-to-ldtk converter reads `derived.*` for placement rules; the game reads `tuning.*` via the src/core/tuning loader."
    4. "version"       → "0.3.0"
    5. "updated"       → "2026-04-11"
    6. "fps"           → 60
    7. "tile_size"     → 16
    8. "tuning"        → (see below — 22 groups, every constants.py leaf must appear exactly once)
    9. "derived"       → (see below — one-level-deeper move of v0.2.0 top-level blocks)

    `source_constants` MUST NOT appear anywhere in the new file.

    **`tuning.*` block** — write all 22 groups below verbatim with the values pulled from src/core/constants.py. Do NOT change a single numeric value. Preserve key order inside each group to match constants.py top-to-bottom for diff-friendliness (D-08 Claude discretion).

    Values to write (copy-paste targets — every one is lifted from constants.py):

    - tuning.tile:
        TILE_SIZE: 16
        TILE_EMPTY: [15, 15]

    - tuning.display:
        SCREEN_W: 320
        SCREEN_H: 192
        VIEWPORT_W: 320
        VIEWPORT_H: 176
        HUD_H: 16
        CULL_MARGIN: 16

    - tuning.sprite:
        SPRITE_SIZE: 16
        BOSS_SPRITE_SIZE: 32

    - tuning.hazards:
        HAZARD_DRAIN_SLOW: 0.25
        HAZARD_DRAIN_MEDIUM: 0.75
        HAZARD_DRAIN_FAST: 1.5
        HAZARD_DRAIN_RATES: {"6": 0.25, "7": 0.75, "8": 1.5}
        SHIELD_T2_DRAIN_REDUCTION: 0.25
        HAZARD_HP_DRAIN_INTERVAL: 60
        SHIELD_REACTIVATION_COOLDOWN: 120

    - tuning.movement:
        WALK_ACCEL: 0.125
        WALK_FRICTION: 0.15
        MAX_WALK_SPEED: 1.25
        GRAVITY: 0.0875
        MAX_FALL_SPEED: 2.5
        JUMP_FORCE: -3.25
        VARIABLE_JUMP_REDUCTION: 0.5
        FALLING_GRAVITY_MULTIPLIER: 1.8

    - tuning.forgiving:
        COYOTE_TIME: 12
        JUMP_BUFFER: 8

    - tuning.wall:
        WALL_SLIDE_FRICTION: 0.2
        WALL_JUMP_X_IMPULSE: 1.5
        WALL_JUMP_Y_FORCE: -1.75

    - tuning.slime_follow:
        SLIME_FOLLOW_DELAY: 16
        SLIME_MAX_DIST: 100
        SLIME_REFORM_DIST: 8
        SLIME_LERP_FACTOR: 0.4

    - tuning.slime_juice:
        JUICE_MAX: 200.0
        JUICE_REGEN_RATE: 0.5
        JUICE_MIN_SCALE: 0.25
        SLIME_SPIT_COST: 10.0

    - tuning.projectile:
        PROJECTILE_SPEED: 2.0
        SPIT_AIM_RANGE: 80
        BOSS_ROCK_SPEED: 1.0

    - tuning.drill:
        DRILL_SPEED: 2.0
        DRILL_DRIFT_SPEED: 0.5
        DRILL_IMPACT_COST: 20.0
        DRILL_ACTIVATION_COST: 5.0
        DRILL_BLOCK_REFUND: 15.0

    - tuning.juice_effects:
        DRILL_SHAKE_DURATION: 12
        DRILL_HITSTOP_FRAMES: 6

    - tuning.health:
        PLAYER_MAX_HP: 3
        INVULN_DURATION: 120
        KNOCKBACK_FORCE_X: 1.0
        KNOCKBACK_FORCE_Y: -1.25

    - tuning.dash:
        DASH_SPEED: 2.0
        DASH_DURATION: 16
        DASH_IFRAMES: 16
        DASH_COOLDOWN: 40

    - tuning.fusion:
        RECALL_SPEED: 4.0
        RECALL_OVERLAP_DIST: 4
        MANA_SHIELD_COST: 20.0
        SLIME_DISSIPATE_COOLDOWN: 240
        RECALL_TRAIL_COLOR: 11
        SPIT_HOLD_THRESHOLD: 16
        HOLD_TAP_THRESHOLD: 10

    - tuning.slime_ram:
        RAM_SPEED: 2.5
        RAM_DIAGONAL_FACTOR: 0.7
        RAM_BLOCK_COST: 15.0
        RAM_INVINCIBLE: true

    - tuning.charge_shot:
        CHARGE_SHOT_SPEED: 3.0
        CHARGE_SHOT_SIZE: 8
        CHARGE_SHOT_DAMAGE: 3
        CHARGE_RECOIL_FORCE: -1.25
        CHARGE_WINDUP_DURATION: 40

    - tuning.boost:
        BOOST_FORCE: -1.75
        BOOST_JUICE_COST: 25.0
        BOOST_RECOMMIT_WINDOW: 24
        BOOST_DOWNWARD_DAMAGE_W: 12
        BOOST_DOWNWARD_DAMAGE_H: 8

    - tuning.gates:
        DRILL_CRACKED_V_COST: 20.0
        BOOST_CRACKED_V_COST: 25.0

    - tuning.save:
        MAX_HP_CAP: 5
        MAX_JUICE_CAP: 300.0
        SAVE_FILE: "save.json"

    - tuning.death:
        DEATH_FREEZE_FRAMES: 60
        DEATH_FADE_FRAMES: 60

    - tuning.save_point:
        SAVE_PULSE_CYCLE: 120
        SAVE_PULSE_HALF: 60
        SAVE_PROMPT_DURATION: 120

    **Uniqueness check (D-15):** verify before writing that every UPPER_SNAKE_CASE leaf appears in exactly one tuning.* group. No duplicates allowed. If the current constants.py grows a name that collides with an existing one, STOP and report — this is a phase-blocking decision.

    **`derived.*` block** — copy the existing v0.2.0 top-level blocks one level deeper. These four blocks must be byte-identical in content to the current file (only their nesting changes):

    - derived.player           ← current top-level "player"
    - derived.jump             ← current top-level "jump"
    - derived.fall             ← current top-level "fall"
    - derived.clearance        ← current top-level "clearance"
    - derived.placement_rules  ← current top-level "placement_rules"

    **Emphatically do NOT:**
    - rename any derived.* field (D-09: "everything moved one level deeper — field shapes are unchanged")
    - add new derived.* fields in this plan (Plan 03 owns `bake_derived()`; this plan just lifts-and-shifts the existing values)
    - delete the comment-style "note" strings inside derived.jump / derived.fall / derived.clearance / derived.placement_rules — they stay verbatim
    - restore `source_constants` in any form
    - touch any other file
  </action>
  <verify>
    <automated>python -c "import json; d=json.load(open('assets/physics-schema.json')); assert d['version']=='0.3.0'; assert set(d.keys())=={'$schema','title','description','version','updated','fps','tile_size','tuning','derived'}; assert 'source_constants' not in d; assert d['tuning']['movement']['GRAVITY']==0.0875; assert d['tuning']['movement']['JUMP_FORCE']==-3.25; assert d['derived']['jump']['max_height_tiles']==3; assert d['tuning']['slime_ram']['RAM_INVINCIBLE'] is True; assert d['tuning']['save']['SAVE_FILE']=='save.json'; print('ok')"</automated>
  </verify>
  <acceptance_criteria>
    - `python -c "import json; d=json.load(open('assets/physics-schema.json')); assert d['version']=='0.3.0'"` exits 0
    - `python -c "import json; d=json.load(open('assets/physics-schema.json')); assert set(d.keys())=={'$schema','title','description','version','updated','fps','tile_size','tuning','derived'}"` exits 0
    - `python -c "import json; d=json.load(open('assets/physics-schema.json')); assert 'source_constants' not in d"` exits 0
    - `python -c "import json; d=json.load(open('assets/physics-schema.json')); assert d['tuning']['movement']['GRAVITY']==0.0875 and d['tuning']['movement']['JUMP_FORCE']==-3.25 and d['tuning']['movement']['MAX_WALK_SPEED']==1.25 and d['tuning']['movement']['MAX_FALL_SPEED']==2.5"` exits 0
    - `python -c "import json; d=json.load(open('assets/physics-schema.json')); assert d['derived']['jump']['max_height_tiles']==3 and d['derived']['jump']['max_width_tiles']==5 and d['derived']['clearance']['min_vertical_tiles']==1"` exits 0
    - `python -c "import json; d=json.load(open('assets/physics-schema.json')); leaves=[k for g in d['tuning'].values() for k in g.keys()]; assert len(leaves)==len(set(leaves)), f'duplicate leaf keys: {[k for k in leaves if leaves.count(k)>1]}'"` exits 0 (name uniqueness invariant D-15)
    - `python -c "import json; d=json.load(open('assets/physics-schema.json')); assert d['tuning']['slime_ram']['RAM_INVINCIBLE'] is True"` exits 0
    - `python -c "import json; d=json.load(open('assets/physics-schema.json')); assert d['tuning']['save']['SAVE_FILE']=='save.json'"` exits 0
    - `python -c "import json; d=json.load(open('assets/physics-schema.json')); t=d['tuning']; expected=['tile','display','sprite','hazards','movement','forgiving','wall','slime_follow','slime_juice','projectile','drill','juice_effects','health','dash','fusion','slime_ram','charge_shot','boost','gates','save','death','save_point']; assert list(t.keys())==expected, f'group order/mismatch: {list(t.keys())}'"` exits 0
    - `python -c "import json; d=json.load(open('assets/physics-schema.json')); assert set(d['derived'].keys())=={'player','jump','fall','clearance','placement_rules'}"` exits 0
  </acceptance_criteria>
  <done>physics-schema.json v0.3.0 exists with exactly the 9 top-level keys in the listed order; tuning.* has the 22 groups in the listed order with every constants.py leaf present exactly once (D-15 verified); derived.* contains the 5 v0.2.0 top-level blocks unchanged in shape; source_constants is gone; no numeric value drifted.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| disk → game boot | Malformed schema would crash the game at import time |
| game → pml-to-ldtk converter | Schema shape change is a breaking contract change for an external tool |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-24-04 | Tampering | assets/physics-schema.json | mitigate | Acceptance criteria assert every numeric value (GRAVITY, JUMP_FORCE, max_height_tiles, etc.) to catch fat-finger errors; JSON-parse check runs in acceptance |
| T-24-05 | Denial of Service | game boot path | mitigate | `python -c "import json; json.load(...)"` acceptance check ensures the file parses before Plan 03's loader sees it; silent corruption cannot advance to downstream plans |
| T-24-06 | Repudiation | external converter | accept | This is a deliberate breaking change for the converter team, documented in Plan 06 (CONVERTER-HANDOFF.md update). The version bump 0.2.0 → 0.3.0 is the contract signal |
| T-24-07 | Information Disclosure | n/a | accept | Schema contains no secrets, only tuning values already in the source tree |
</threat_model>

<verification>
- `python -c "import json; json.load(open('assets/physics-schema.json'))"` parses cleanly
- Every tuning.* leaf is globally unique (D-15)
- Numeric values match constants.py byte-for-byte (spot-checked: GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, MAX_FALL_SPEED, FALLING_GRAVITY_MULTIPLIER, JUICE_MAX, RAM_SPEED, CHARGE_SHOT_DAMAGE, PLAYER_MAX_HP)
- `git diff assets/physics-schema.json` shows exactly one file changed
</verification>

<success_criteria>
- version="0.3.0", source_constants removed, tuning.* and derived.* blocks present
- 22 tuning groups in listed order
- Every named constant in src/core/constants.py appears under exactly one tuning.* group with its exact current value
- derived.* mirrors v0.2.0 top-level shape with no field renames
- Name-uniqueness invariant holds for flat-key lookup (D-15)
</success_criteria>

<output>
After completion, create `.planning/phases/24-tuning-foundation-schema-inversion/24-02-SUMMARY.md`
</output>
