# Roadmap - Jelly Roll Proto

## Milestones

- v1.0 Vertical Slice — Phases 1-6 (shipped 2026-03-28)
- v1.1 World Expansion & New Abilities — Phases 7-16 (shipped 2026-04-01)
- v1.2 Unified Schema & Tilemap Rendering — Phases 17-19 (shipped 2026-04-07)
- v1.3 16x16 Tile Migration — Phases 20-23 (shipped 2026-04-09)
- v2.0 Game Feel — Phases 24-36 (in progress, started 2026-04-11)

## Phases

<details>
<summary>v1.0 Vertical Slice (Phases 1-6) — SHIPPED 2026-03-28</summary>

- [x] Phase 1: Core Movement & Physics (2/2 plans) — completed 2026-03-12
- [x] Phase 2: Slime Companion & Fusion (4/4 plans) — completed 2026-03-13
- [x] Phase 3: Destructive World & Boss (4/4 plans) — completed 2026-03-14
- [x] Phase 4: Level Interactivity & Items (2/2 plans) — completed 2026-03-15
- [x] Phase 5: New Enemies & Player Health (2/2 plans) — completed 2026-03-14
- [x] Phase 6: Physics Refinement & Test Gaps (1/1 plan) — completed 2026-03-22

</details>

<details>
<summary>v1.1 World Expansion & New Abilities (Phases 7-16) — SHIPPED 2026-04-01</summary>

- [x] Phase 7: Macro-Map & Room Persistence (2/2 plans) — completed 2026-03-27
- [x] Phase 8: New Fusion Abilities (6/6 plans) — completed 2026-03-28
- [x] Phase 9: Defensive Mechanics (3/3 plans) — completed 2026-03-28
- [x] Phase 10: Nitro-Ejection & Endgame (3/3 plans) — completed 2026-03-28
- [x] Phase 11: Save System & HUD (3/3 plans) — completed 2026-04-01
- [x] Phase 12: Screen Size Expansion (3/3 plans) — completed 2026-03-28
- [x] Phase 13: Sprite Scale & PNG Spritesheets (3/3 plans) — completed 2026-03-29
- [x] Phase 14: Tech Debt & Schema Cleanup (3/3 plans) — completed 2026-03-29
- [x] Phase 15: LDtk Entity & Door Integration (2/2 plans) — completed 2026-04-01
- [x] Phase 16: v1.1 Housekeeping & Verification (2/2 plans) — completed 2026-04-01

</details>

<details>
<summary>v1.2 Unified Schema & Tilemap Rendering (Phases 17-19) — SHIPPED 2026-04-07</summary>

- [x] Phase 17: Unified Schema Definition (1/1 plan) — completed 2026-04-05
- [x] Phase 18: Schema-Driven Integration (3/3 plans) — completed 2026-04-05
- [x] Phase 19: Tilemap Rendering (2/2 plans) — completed 2026-04-07

</details>

<details>
<summary>v1.3 16x16 Tile Migration (Phases 20-23) — SHIPPED 2026-04-09</summary>

- [x] Phase 20: Grid Constants & Schema Metadata (2/2 plans) — completed 2026-04-08
- [x] Phase 21: Tileset & LDtk Pipeline (2/2 plans) — completed 2026-04-08
- [x] Phase 22: Entity Alignment & Physics Tuning (2/2 plans) — completed 2026-04-08
- [x] Phase 23: Converter Handoff (1/1 plan) — completed 2026-04-09

</details>

### v2.0 Game Feel (In Progress)

**Milestone Goal:** Make player, slime, fusion, and ability systems feel right — not just meet spec. Invert tuning source of truth to `physics-schema.json`, build a GMTK-style live-tuning panel, replace hardcoded sprite toggle with an animation FSM + event bus, redesign fusion lifecycle with a juice-as-mana economy, tune systematically against written feel targets, and polish with the Nijman juice trio.

- [x] **Phase 24: Tuning Foundation (Schema Inversion)** — Promote `physics-schema.json` to source of truth with loader, mutation API, compat shim, and converter handoff update
 (completed 2026-04-11)
- [x] **Phase 25: Call-Site Migration** — Sweep `src/entities/` to read `tuning.X` at use site so hot-reload reaches entity values (completed 2026-04-11)
- [x] **Phase 26: Event Bus + Animation FSM Skeleton** — `src/anim/` package with FSM replacing hardcoded sprite toggle; no new content yet (completed 2026-04-12)
- [ ] **Phase 27: Diagnostic Overlays** — F2-F5 overlays for hitboxes, velocity, input state, slime follow; makes "feels off" falsifiable
- [x] **Phase 28: Live-Tuning Panel MVP** — F1-toggle overlay panel with mouse-driven sliders, presets, autosave journal, baseline diff, A/B compare (completed 2026-04-12)
- [x] **Phase 29: Player Movement Feel Pass** — Retune accel/gravity/jump curves/coyote/buffer/wall jump against written feel targets using the panel (completed 2026-04-19)
- [x] **Phase 30: Fusion Lifecycle Design Doc** — Locked `FUSION-DESIGN.md` defining initiate/sustain/end, juice-as-mana model, and per-ability contracts; design only, no code
 (completed 2026-04-19)
- [x] **Phase 31: Animation Content + Particle Bank Separation** — Transition frames via procedural placeholders, `anim-schema.json`, dedicated particle image bank, hitbox-independence invariant
 (completed 2026-04-22)
- [x] **Phase 31.5: Cut-Ability Code-Strip** (INSERTED) — Full-coverage strip of cut abilities (ram, charge_shot, boost, bubble_shield) across code + schema + presets + input + save + tests; drop tuning groups entirely, remove dash from `_ACTION_MAP`. **Hard gate before Phase 32.**
 (completed 2026-04-26)
- [x] **Phase 32: Fusion Manager + Protocol Refactor** — `src/fusion/` package with FusionAbility Protocol, FusionManager shell, one ability module (drill_dive); pure refactor, save format versioned (completed 2026-04-26)
- [ ] **Phase 33: Per-Ability Feel Pass** — Drill dive retuned against new lifecycle using the panel; per-ability identity (windup/sustain/end/SFX/particle color)
- [ ] **Phase 34: Slime Follow/AI Feel Pass** — Retune slime follow accel, catch-up, stuck detection, terrain reactions; half of the dual-hero identity
- [ ] **Phase 35: Juice Polish (Shake + Hitstop + Particles + Audio)** — Trauma-squared camera shake, hitstop with input-buffer protection, pooled particles, impact flash, sound channel map
- [ ] **Phase 36: Milestone Cap — Preset Bake + Regression Check** — Lock shipping preset, regression playthrough against v1.0-v1.3, CONVERTER-HANDOFF.md final, PROJECT.md evolution

## Phase Details

### Phase 24: Tuning Foundation (Schema Inversion)
**Goal**: Promote `physics-schema.json` to the single source of truth, with a loader that exposes a mutation API (`set_value`/`save`/`reset`/`bake_derived`) and a compat shim that keeps existing `constants.py` call sites working. Game boots with values identical to v1.3.
**Depends on**: Phase 23 (v1.3 shipped)
**Requirements**: FND-01, FND-02, FND-03, FND-04, FND-06
**Success Criteria** (what must be TRUE):
  1. Game boots from `physics-schema.json` values and plays identically to v1.3 (spot-check: walk speed, jump height, gravity, drill, ram all match frame-for-frame)
  2. Calling `tuning.set_value(key, value)` makes the new value visible to subsequent `getattr(tuning, key)` reads in the same process (verified by `tests/test_tuning.py::test_set_value_visibility`). File-watcher hot-reload is explicitly not implemented — the live-tuning panel (Phase 28) is the only editing interface.
  3. Every existing `from src.core.constants import X` call site still imports successfully (compat shim verified by `python -c "import src.core.constants"`)
  4. pml-to-ldtk converter smoke test passes against the restructured schema; CONVERTER-HANDOFF.md reflects the new `tuning.*` / `derived.*` layout
**Plans**: 6 plans
- [x] 24-01-requirements-doc-revision-PLAN.md — Revise FND-04 + ROADMAP §Phase 24 success criterion #2 (blocking doc update, must run before any code task)
- [x] 24-02-schema-restructure-PLAN.md — Restructure physics-schema.json v0.2.0 → v0.3.0 with tuning.* (raw inputs) and derived.* (converter-facing)
- [x] 24-03-tuning-loader-PLAN.md — Write src/core/tuning.py with load/set_value/save/reset/get_baseline/get_group/bake_derived + PEP 562 flat access
- [x] 24-04-compat-shim-PLAN.md — Rewrite src/core/constants.py as passthrough shim (from src.core.tuning import *) plus HAZARD_DRAIN_RATES int-key fix-up
- [x] 24-05-tests-PLAN.md — tests/test_tuning.py with 11 tests covering FND-02, FND-04 (revised), FND-06, and 12-caller compat smoke
- [x] 24-06-converter-handoff-PLAN.md — Update CONVERTER-HANDOFF.md with v0.3.0 migration table + staleness note (D-11) + human-verify checkpoint

### Phase 25: Call-Site Migration (constants -> tuning)
**Goal**: Move entity files from import-site constants to use-site `tuning.X` reads so hot-reload actually reaches gameplay values. Mechanical refactor with zero behavior change.
**Depends on**: Phase 24
**Requirements**: FND-05
**Success Criteria** (what must be TRUE):
  1. `src/entities/player.py`, `slime.py`, `projectile.py`, and `enemies/*.py` read `tuning.*` values each frame instead of caching them at import time
  2. Editing a movement value in `physics-schema.json` changes player behavior on the very next frame (verified live with stopwatch against Phase 24 loader)
  3. Regression playthrough (Room 0 -> boss room, drill dive, ram, kick, bubble shield) produces identical behavior to v1.3 baseline
**Plans**: 5 plans
- [x] 25-01-player-migration-PLAN.md — Migrate player.py wildcard import + ~50 call sites to use-site tuning reads
- [x] 25-02-livereach-test-PLAN.md — tests/test_tuning_livereach.py proving set_value reaches GRAVITY/JUMP_FORCE/MAX_WALK_SPEED/FRICTION on next frame
- [x] 25-03-small-entities-PLAN.md — Migrate slime/projectile/boss/enemies/effects/save_point/items to tuning reads
- [x] 25-04-level-and-core-PLAN.md — Migrate map/world/save_manager/sprite_utils (map.py keeps HAZARD_DRAIN_RATES on shim)
- [x] 25-05-regression-playthrough-PLAN.md — Human v1.3 regression playthrough documenting frame-for-frame parity

### Phase 26: Event Bus + Animation FSM Skeleton
**Goal**: Stand up `src/anim/` with an event bus and a generic animation FSM wired to the player's existing IDLE/RUN/JUMP/FALL states, replacing the hardcoded sprite frame toggle in `player.py:790`. No new animation content yet — the skeleton just reproduces current behavior.
**Depends on**: Phase 24 (tuning loader for anim schema in later phases)
**Requirements**: ANIM-01, ANIM-02, ANIM-03
**Success Criteria** (what must be TRUE):
  1. `src/anim/` package exists with `event_bus.py`, `state_machine.py`, `anim_clip.py`, `anim_player.py`, `player_anim.py`; player sprite frames are driven by `fsm.current_frame()` instead of the hardcoded `u = 16 + ...` line
  2. Event bus emits all listed transition events from gameplay code (direction_change, jump_start, jump_released, fall_start, land, wall_touch, wall_jump, drill_impact, fuse_start, fuse_end, ram_start, ram_impact, boost_tap, charge_shot_fire, spit, damaged, death) and a debug subscriber can log them to confirm firing
  3. Player visually looks identical to v1.3 (same two frames per state) after the FSM takes over — the skeleton is a refactor, not a content change
**Plans**: TBD

### Phase 27: Diagnostic Overlays
**Goal**: Ship per-system debug overlays (hitbox, velocity, input state, slime AI) toggled by F2-F5. Must exist before Phase 28 panel validation and Phase 29 input audit so that "feels off" becomes measurable.
**Depends on**: Phase 24 (values come from tuning loader)
**Requirements**: TOOL-08, TOOL-09
**Success Criteria** (what must be TRUE):
  1. F2 toggles a hitbox wireframe overlay that draws every live entity's collision box in the correct position (regression-checked against v1.3 screenshots)
  2. F3 toggles velocity vectors and a frame-time graph; F4 toggles input state glyphs with visible coyote and jump-buffer timer bars
  3. F5 toggles a slime-specific overlay showing follow anchor, target point, stuck detection state, and catch-up state
  4. All overlays render on top of the game without modifying gameplay state or impacting measured frame time
**Plans**: 2 plans
- [ ] 27-01-PLAN.md — Overlay manager module with F2 hitbox wireframes, F3 velocity arrows + frame-time graph, and unit tests
- [ ] 27-02-PLAN.md — F4 input state blips (coyote/buffer), F5 slime follow overlay, main.py wiring, visual verification checkpoint
**UI hint**: yes

### Phase 28: Live-Tuning Panel MVP
**Goal**: Ship a GMTK-Platformer-Toolkit-style overlay panel (no pause) with mouse-driven sliders grouped by system, presets, autosave journal, baseline diff, and A/B compare. This is the milestone accelerator — every subsequent feel phase uses it.
**Depends on**: Phase 24 (loader), Phase 27 (overlays for validation)
**Requirements**: TOOL-01, TOOL-02, TOOL-03, TOOL-04, TOOL-05, TOOL-06, TOOL-07
**Success Criteria** (what must be TRUE):
  1. Pressing F1 toggles an on-screen panel with category tabs; the panel is an overlay while the game continues running (no pause mode)
  2. Sliders respond to mouse click-and-drag on handles and mouse clicks on category tabs; keyboard numeric entry works as a precision fallback
  3. Dragging a slider updates the live gameplay value at the next frame boundary without mid-frame discontinuities (double-buffered write), and a reset-to-default arrow restores the v1.3 baseline per slider
  4. Preset save/load reads/writes versioned JSON in `assets/presets/`; ships with the immutable v1.3 baseline plus "tight" and "floaty"; two-slot A/B loader lets the user flip between presets to feel the difference
  5. Every slider edit is appended to a rolling journal file so a crash mid-session does not lose progress
**Plans**: TBD
**UI hint**: yes

### Phase 29: Player Movement Feel Pass
**Goal**: Retune accel/friction, gravity/jump curves, variable jump, coyote, jump buffer, wall slide/jump against written feel targets using the panel and overlays. First feel phase; lowest-coupling system.
**Depends on**: Phase 28 (panel), Phase 27 (overlays), Phase 25 (use-site reads)
**Requirements**: MOV-04, MOV-05, MOV-06
**Success Criteria** (what must be TRUE):
  1. A written list of feel targets exists before tuning starts (e.g. "cross 4-tile gap, land 1 tile in"; "coyote 6 frames ok, 7 fail") and every target passes a manual playtest at phase end
  2. Input buffering, coyote windows, and cancel windows have been audited across all player states with the input visualizer overlay and regressions are impossible to hide
  3. A "tight" and a "floaty" preset are both saved to `assets/presets/` and both produce coherent, distinct feels through the same controls
  4. Phase exits within its 1-1.5 week timebox with the exit criteria explicitly checked off
**Plans**: 3 plans
Plans:
- [x] 29-01-PLAN.md — Setup: draft feel targets from physics math, create LDtk test level, add debug teleport, freeze v1.3 baseline preset
- [x] 29-02-PLAN.md — Ground + Air tuning playtest loops with F4 input audit (coyote/buffer)
- [x] 29-03-PLAN.md — Wall tuning, preset capture (v2.0-default/tight/floaty), derived bake, final sign-off

### Phase 30: Fusion Lifecycle Design Doc
**Goal**: Produce a locked `.planning/FUSION-DESIGN.md` that narrows the prototype to **one fusion mechanic (Drill Dive)**, defines the initiate/sustain/end FSM under a 100%-gated juice-as-mana economy, specifies a unified single-button input model, captures v1.3 drill behavior as Phase 32 regression target, and lists acceptance checks Phase 32 must satisfy. Design only — no code changes.
**Depends on**: Phase 24 (can run in parallel with Phase 29)
**Requirements**: FUS-01, FUS-02, FUS-03
**Success Criteria** (what must be TRUE):
  1. `.planning/FUSION-DESIGN.md` exists and is marked LOCKED; it defines `IDLE → RECALL → WINDUP → FUSED → EXIT` as explicit FSM phases with unified Z/V input model, 100% juice gate, second-pass (100→200%) charge commitment ritual, and a single auto exit path (juice → 0 → dissipate; manual exit removed 2026-04-20)
  2. The doc enumerates drill-dive's juice cost, regen rate, mana shield drain, and empty-state behavior under the juice-as-mana model (one fusion mechanic, not six — per scope pivot)
  3. A drill-dive contract captures current v1.3 behavior as Phase 32 regression target (velocity, per-block cost, CRACKED_V handling, two exit conditions: solid contact + juice empty); cut abilities are enumerated as one-liners
  4. The doc lists explicit acceptance checks that Phase 32 must satisfy before it can close
**Plans**: 1 plan
Plans:
- [x] 30-01-PLAN.md — Author and lock FUSION-DESIGN.md (scope pivot rationale, input model, FSM, juice economy, drill-dive contract, cut abilities, acceptance checklist, two-commit lock dance, ROADMAP update)

> **Follow-up (code-strip phase, TBD number — insert via `/gsd-insert-phase`)**: Remove cut-ability code from `src/entities/player.py` (ram_dx/dy, shield_*, charge_shot_*, boost_*, has_shield/has_boost flags, `start_ram`/`apply_ram_physics`/`end_ram`, `start_boost`/`end_boost`, bubble-shield + charge-shot branches), `src/entities/slime.py`, and tuning groups `ram` / `charge_shot` / `boost` / `bubble_shield` from `assets/physics-schema.json`. **Hard gate before Phase 32.**

### Phase 31: Animation Content + Particle Bank Separation
**Goal**: Fill in real animation content on top of the Phase 26 FSM skeleton — transition frames for jump crouch, land recovery, turn-around, drill recoil, fuse flash — using procedural placeholders (palette swaps, y-offsets, 1-tick holds) since real art is deferred. Split the particle image bank away from the map tileset so FX sprites cannot compete for tile slots. Enforce hitbox-independence.
**Depends on**: Phase 26 (FSM skeleton), Phase 24 (tuning loader for anim-schema)
**Requirements**: ANIM-04, ANIM-05, ANIM-06, ANIM-07
**Success Criteria** (what must be TRUE):
  1. Jumping, landing, turning around, drilling into a block, and entering fusion each show a visible transition (at least one extra frame or palette shift) driven by the FSM and tunable from the panel
  2. `assets/anim-schema.json` exists, is loaded by `tuning.py` as a second schema, and animation clip frame counts / durations / event bindings are editable live via the panel
  3. Particle sprites live in a dedicated image bank separate from the map tileset; verified by loading a room with many particles and confirming no map tile slot is overwritten or competed for
  4. Automated regression test confirms that no animation state read ever mutates an entity's `.w` or `.h` — visuals may move, hitboxes never change
**Plans**: 6 plans
Plans:
- [x] 31-01-PLAN.md — PlayerAnimDriver extension + AnimPlayer.pause_for primitive + placeholder player sprite frames (Wave 1, blocking prereq)
- [x] 31-02-PLAN.md — ANIM-04 transition clips: PLAYER_CLIPS + reordered rules + _update_anim_driver extension + land/jump_start subscribers + provisional drill_block_break bridge emit (Wave 2)
- [x] 31-03-PLAN.md — ANIM-06 particle bank separation: particles.png at bank 2, sprite-backed Particle rewrite, Effect retired, spawn_particle_burst + drill_block_break subscriber (Wave 2)
- [x] 31-04-PLAN.md — ANIM-04 D-07 fuse flash: 16-particle converging ring + BlobGrowth (tier-2 AnimPlayer) + fuse_start subscriber (Wave 2)
- [x] 31-05-PLAN.md — ANIM-05 anim-schema.json + tuning.load_anim + panel ANIM tab + Reload button + presets.py ANIM_ routing (Pitfall 6 fix, Wave 2)
- [x] 31-06-PLAN.md — ANIM-07 hitbox-independence matrix test (hard gate, Wave 3)

### Phase 31.5: Cut-Ability Code-Strip (INSERTED)
**Goal**: Purge cut-ability code, data, and tests from the prototype so Phase 32's fusion refactor starts from a clean base. Full-coverage strip (code + schema + presets + input + save + tests): remove ram / charge_shot / boost / bubble_shield branches from `src/entities/player.py` and `src/entities/slime.py`, drop the matching tuning groups from `assets/physics-schema.json`, purge routing from `presets.py`, remove `dash` from `_ACTION_MAP`, and update/drop affected tests. Hard gate before Phase 32 per `.planning/FUSION-DESIGN.md` and `32-CONTEXT.md` D-01.
**Depends on**: Phase 30 (design doc LOCKED — cut-ability enumeration source)
**Requirements**: (maintenance phase — enables FUS-04/05/07 by shrinking Phase 32 surface area; no new REQ-IDs)
**Success Criteria** (what must be TRUE):
  1. `src/entities/player.py` contains no `ram_*`, `shield_*`, `charge_shot_*`, `boost_*`, `has_shield`, `has_boost`, `start_ram`/`apply_ram_physics`/`end_ram`, `start_boost`/`end_boost`, bubble-shield, or charge-shot code paths; `src/entities/slime.py` cut-ability code is likewise removed
  2. `assets/physics-schema.json` no longer contains `ram`, `charge_shot`, `boost`, or `bubble_shield` tuning groups; `src/core/presets.py` no longer routes those groups; all shipping presets in `assets/presets/` load without referencing cut keys
  3. `dash` is removed from `_ACTION_MAP` in the input layer; save-file schema no longer reads/writes cut-ability flags; existing save round-trip succeeds under the stripped schema (cut keys ignored on load, never written on save)
  4. Test suite passes with cut-ability tests deleted or updated; no dead references to removed symbols remain (`grep` for `ram_dx`, `has_shield`, `charge_shot`, `start_boost`, `dash` in `_ACTION_MAP` returns zero gameplay hits)
**Plans**: 5 plans
Plans:
- [x] 31.5-01-PLAN.md — Player + projectile cut-ability strip (top-down by symbol per D-17: ram, boost, dash, bubble shield, charge shot, flag init)
- [x] 31.5-02-PLAN.md — Slime Hold state strip + orphan reposition method delete
- [x] 31.5-03-PLAN.md — physics-schema.json + 5 presets clean rewrite (atomic commit)
- [x] 31.5-04-PLAN.md — Cross-cutting wiring (input + save + items + main.py LDtk + entity-schema + UI panel/presets)
- [x] 31.5-05-PLAN.md — Test cleanup + Wave 0 gates + 4-gate verification (D-18)

### Phase 32: Fusion Manager + Protocol Refactor
**Goal**: Refactor fusion out of `player.py` into `src/fusion/` with a `FusionAbility` Protocol, `FusionManager` state shell, `ChargeController` pre-manager, and **one** ability module (`drill_dive`). Pure refactor gated on the Phase 30 design doc (single-fusion scope pivot). Save format gains a `save_version` field; v1.3 save round-trip is explicitly not required.
**Depends on**: Phase 30 (design doc LOCKED — hard gate), Phase 31.5 (cut-ability code-strip — hard gate)
**Requirements**: FUS-04, FUS-05, FUS-07
**Success Criteria** (what must be TRUE):
  1. `src/fusion/` exists with `FusionAbility` Protocol, `FusionManager`, `ChargeController`, and a `drill_dive` module; old fusion code (including the five cut abilities' remnants) is removed from `player.py`
  2. A regression playthrough against the Phase 30 drill-dive contract confirms FUS-03 behaves identically to v1.3 after the refactor (no feel changes yet; drill velocity, per-block costs, three exit conditions all parity)
  3. Save files written by v2.0 contain a `save_version` field; old v1.3 saves are rejected with a clear message instead of silently corrupting state
**Plans**: 6 plans
Plans (5 waves, 0–4):
- [x] 32-01-PLAN.md — Wave 0 test scaffolding: new RED test files (test_fusion_fsm, test_drill_dive_parity, test_pogo) + migrate test_fusion/test_event_bus/test_save_system to FusionManager API + save_version assertions
- [x] 32-02-PLAN.md — Wave 1: src/fusion package skeleton: `__init__.py` + `protocol.py` (FusionAbility Protocol + TickResult frozen dataclass)
- [x] 32-03-PLAN.md — Wave 1: src/core/save_manager.py: CURRENT_SAVE_VERSION = 2 + SaveVersionMismatchError + hard-fail rejection (FUS-07)
- [x] 32-04-PLAN.md — Wave 2: src/fusion/manager.py (FusionManager FUSED+EXIT) + src/fusion/charge_controller.py (RECALL+WINDUP+fuse_start emit)
- [x] 32-05-PLAN.md — Wave 3: src/fusion/drill_dive.py (verbatim v1.3 parity port + drill_start/drill_block_break/drill_end emits) + src/fusion/pogo.py (null-fusion sibling, hardcoded constants per D-18) + atomic deletion of provisional drill_block_break bridge in src/entities/player.py (Pitfall 2 closure, depends on Plan 04)
- [x] 32-06-PLAN.md — Wave 4: src/entities/player.py migration (delete fuse/unfuse/apply_diving_physics/is_charging_recall/mid-drill-cancel; add @property is_fused) + main.py wiring (Game.__init__ instantiates fusion_manager + charge_controller; SaveManager.load() callsites wrap SaveVersionMismatchError) + manual smoke checkpoint

### Phase 33: Per-Ability Feel Pass (Drill-Only under single-fusion prototype)
**Goal**: Retune drill-dive against the new lifecycle using the live panel — windup timing, sustain behavior, end/cancel feel, particle color, button-mapping confirmation, SFX identity. Per-ability identity goal reduces to drill identity under the single-fusion prototype (cut abilities are out of scope per Phase 30 design pivot).
**Depends on**: Phase 32 (refactor), Phase 28 (panel), Phase 31 (animation content + particle bank)
**Requirements**: FUS-06
**Success Criteria** (what must be TRUE):
  1. Drill-dive has a distinguishable windup -> sustain -> end curve tuned through the panel against the Phase 30 drill-dive contract; tap/hold threshold (~8f), WINDUP duration (~30f), accelerated-regen multiplier (2× draft) all validated via playtest
  2. Drill has a distinct particle color and SFX cue so a blindfolded listener/observer can name when drill fires vs. spit/daze shot
  3. Drill still satisfies its Phase 30 contract — no regression from Phase 32 refactor after feel tuning (three exit conditions, per-block costs, i-frame policy all preserved)
**Plans**: TBD

### Phase 34: Slime Follow/AI Feel Pass
**Goal**: Retune slime follow accel, max speed, catch-up threshold, stuck timeout, look-ahead distance, and terrain reactions so the slime feels alive, not draggy. Half of the dual-hero identity.
**Depends on**: Phase 25 (use-site tuning reads), Phase 27 (slime overlay), Phase 28 (panel)
**Requirements**: SLM-04
**Success Criteria** (what must be TRUE):
  1. The slime reliably catches up to the player across a 10-tile gap within a written frame budget that matches the feel target set at phase start
  2. The slime no longer gets permanently stuck on terrain geometry during a full playthrough of the v1.0 vertical-slice route
  3. Slime follow tuning values are all reachable from the live panel and produce smooth, continuous changes with no snap-back
**Plans**: TBD

### Phase 35: Juice Polish (Shake + Hitstop + Particles + Audio)
**Goal**: Layer the Nijman juice trio — trauma-squared camera shake, hitstop with input-buffer protection, pooled particles — plus impact flash and a sound channel map, all hooked to animation and fusion events. Must land after Phase 32 so fusion events are stable.
**Depends on**: Phase 32 (fusion events stable), Phase 31 (particle bank separated), Phase 26 (event bus)
**Requirements**: JUICE-01, JUICE-02, JUICE-03, JUICE-04, JUICE-05
**Success Criteria** (what must be TRUE):
  1. An explicit juice budget table (NONE/SUBTLE/MEDIUM/BIG per event) exists and every shake/hitstop/particle/flash hook respects it — no event is louder than the budget allows
  2. Hitstop freezes gameplay for its tunable 3-8 frame duration while still polling input, so buffered jumps and fusion inputs survive the freeze
  3. Particles are drawn through a pooled system capped at ~128 particles using `pyxel.pset`; no per-frame allocations and no frame-time regression with max particles on screen
  4. Impact flash fires on drill impact, ram impact, and damage; the sound channel map prevents repeated-frame sound spam via debounce rules
**Plans**: TBD

### Phase 36: Milestone Cap — Preset Bake + Regression Check
**Goal**: Lock the shipping tuning preset, run a full v1.0-v1.3 regression playthrough, verify save-format versioning, finalize CONVERTER-HANDOFF.md for v2.0, and evolve PROJECT.md. No new features.
**Depends on**: Phase 35 (everything before)
**Requirements**: (validation phase — validates all v2.0 REQ-IDs end-to-end; no new REQ-IDs)
**Success Criteria** (what must be TRUE):
  1. A single "v2.0 shipping" preset is committed to `assets/presets/` and the game boots to it by default
  2. Regression playthrough of the v1.0 vertical-slice route, v1.1 macro-map with all six abilities, v1.2 tilemap rendering, and v1.3 16x16 entity alignment all pass without behavior regression
  3. CONVERTER-HANDOFF.md reflects the final v2.0 schema layout and passes the converter smoke test one more time
  4. PROJECT.md is updated: v2.0 moved from Current Milestone to History, v2.0 requirements moved to Validated, and the milestone audit file exists
**Plans**: TBD

## Progress

| Phase | Milestone | Plans | Status | Completed |
|-------|-----------|-------|--------|-----------|
| 1-6 | v1.0 | 15/15 | Complete | 2026-03-22 |
| 7-16 | v1.1 | 30/30 | Complete | 2026-04-01 |
| 17-19 | v1.2 | 6/6 | Complete | 2026-04-07 |
| 20-23 | v1.3 | 7/7 | Complete | 2026-04-09 |
| 24. Tuning Foundation | v2.0 | 6/6 | Complete    | 2026-04-11 |
| 25. Call-Site Migration | v2.0 | 5/5 | Complete    | 2026-04-11 |
| 26. Event Bus + Anim FSM Skeleton | v2.0 | 3/3 | Complete    | 2026-04-12 |
| 27. Diagnostic Overlays | v2.0 | 0/2 | Not started | - |
| 28. Live-Tuning Panel MVP | v2.0 | 3/3 | Complete    | 2026-04-12 |
| 29. Player Movement Feel Pass | v2.0 | 3/3 | Complete   | 2026-04-19 |
| 30. Fusion Lifecycle Design Doc | v2.0 | 1/1 | Complete    | 2026-04-19 |
| 31. Animation Content + Particle Bank | v2.0 | 6/6 | Complete    | 2026-04-22 |
| 31.5. Cut-Ability Code-Strip (INSERTED) | v2.0 | 5/5 | Complete   | 2026-04-26 |
| 32. Fusion Manager + Protocol Refactor | v2.0 | 6/6 | Complete    | 2026-04-26 |
| 33. Per-Ability Feel Pass | v2.0 | 0/TBD | Not started | - |
| 34. Slime Follow/AI Feel Pass | v2.0 | 0/TBD | Not started | - |
| 35. Juice Polish | v2.0 | 0/TBD | Not started | - |
| 36. Milestone Cap | v2.0 | 0/TBD | Not started | - |
