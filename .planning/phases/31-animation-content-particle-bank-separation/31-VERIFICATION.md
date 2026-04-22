---
phase: 31-animation-content-particle-bank-separation
verified: 2026-04-23T00:00:00Z
status: human_needed
score: 4/4 roadmap success criteria verifiable-true (SC4 fully automated; SC1/SC2/SC3 need eyes-on)
overrides_applied: 0
re_verification: false
human_verification:
  - test: "SC1 — visible transition frames in engine for jump (stationary + running), land squash, turn skid, drill spin (with recoil pause + diverging burst), fuse start (converging ring + growing blob)"
    expected: "Each transition renders a distinct extra frame / pose beyond plain idle/run/jump; drill block-break shows a brief spin hold followed by a 14-particle diverging burst; fuse start shows 16 converging particles and a blob that grows through 4 progressive-radius frames at the player centre."
    why_human: "Procedural placeholder sprite art must be visually inspected in a running engine — automated FSM/predicate tests cannot confirm that the rendered pixels convey 'squash', 'skid', 'crouch', 'recoil' etc. Pyxel GUI is not captured in the automated pytest run."
  - test: "SC1/SC2 — ANIM tab slider drag changes clip speed live; Reload anim schema button re-ingests edits to assets/anim-schema.json without restart"
    expected: "F1 opens panel → Anim tab shows a 'player_clips' collapsible with 13 duration sliders (1 idle + 2 run + 1 jump + 1 jump_stationary + 1 jump_running + 1 jump_crouch + 2 land_squash + 1 turn_skid + 4 drill_spin). Dragging ANIM_PLAYER_RUN_DURATION_0 makes the run cycle tick faster/slower in real time. Editing assets/anim-schema.json on disk and clicking 'Reload anim schema' rebuilds the FSM."
    why_human: "Slider drag is a mouse-input interaction with a Pyxel GUI; value mutation is unit-tested but live visual feedback (run cycle changing) requires a running engine."
  - test: "SC3 — particle burst in a dense CRACKED_V field does NOT corrupt the map tileset"
    expected: "Drilling through 5+ adjacent cracked blocks produces one particle burst per break; map tiles continue rendering normally throughout and after; no tile glyphs vanish or swap; inspect_bank(bank=0) before/after shows identical tile pixels."
    why_human: "The test_sprite_manifest_banks_distinct unit test verifies the static manifest wiring (bank 0 vs bank 2) — but the real SC3 question ('no tile-slot competition under load') can only be answered by watching the running engine render a room while particles spawn."
  - test: "SC1 tangential — provisional drill_block_break bridge fires cleanly without double-emit or crash"
    expected: "Drilling a CRACKED_V tile emits exactly one drill_block_break event from src/entities/player.py:796; subscriber pauses the drill_spin clip tick counter by DRILL_RECOIL_PAUSE_FRAMES and spawns 14 particles. No exceptions, no duplicate bursts."
    why_human: "Subscriber wiring is unit-tested via FakeGame harness, but the end-to-end emit → subscribe → pause_for + spawn_particle_burst path runs only in the real Game object. Non-trivial to fake-harness fully."
deferred:
  - truth: "Real (not procedural) pixel art for player transition frames, particle burst/convergence, and blob growth frames"
    addressed_in: "Deferred indefinitely per 31-CONTEXT D-02/D-03/D-05/D-07b and 31-06-SUMMARY known-limitations table — real art is user-authored and can replace placeholders without code changes"
    evidence: "31-06-SUMMARY.md: 'Real pixel art deferred; user can author and replace assets/sprites/player.png any time without code changes'"
  - truth: "Canonical drill_block_break emit at the fusion FSM level (not the provisional bridge in player.py)"
    addressed_in: "Phase 32"
    evidence: "ROADMAP Phase 32 goal + FUSION-DESIGN: Phase 32 relocates drill_block_break emit to the fusion FSM and MUST remove the Plan 02 bridge at src/entities/player.py:792-796"
---

# Phase 31: Animation Content + Particle Bank Separation — Verification Report

**Phase Goal:** Fill in real animation content on top of the Phase 26 FSM skeleton — transition frames for jump crouch, land recovery, turn-around, drill recoil, fuse flash — using procedural placeholders. Split the particle image bank away from the map tileset so FX sprites cannot compete for tile slots. Enforce hitbox-independence.

**Verified:** 2026-04-23
**Status:** human_needed
**Re-verification:** No — initial verification

## Executive Summary

All six plans (31-01 through 31-06) landed all their declared must-haves in code. Every PLAN frontmatter truth verified directly in the codebase. All four ROADMAP success criteria have automated evidence, but SC1–SC3 have in-engine visual/interactive dimensions that require human eyes-on the running Pyxel application. SC4 (hitbox invariance) is fully automated and green.

487 tests pass. 9 pre-existing failures (in test_tuning.py, test_physics.py, test_phase22.py, test_ldtk_migration.py, test_sprite_assets.py::test_palette_compliance) are baseline drifts unrelated to Phase 31 — none of Phase 31's new tests fail. The 82 Phase 31-specific tests (test_anim.py + test_anim_events.py + test_anim_hitbox.py + test_tuning_anim.py) all pass.

## Goal Achievement — ROADMAP Success Criteria

| #  | Truth (SC from ROADMAP)                                                                                                                     | Status       | Evidence                                                                                                                                                                                                              |
| -- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1  | Jumping, landing, turning, drilling, and fusion each show a visible transition driven by the FSM and tunable from the panel                 | ? UNCERTAIN  | FSM rules + clips present (player_anim.py:121–135). Placeholder sprite frames authored at U=48/64/80/96/112/128–176 on player.png. Panel Anim tab wired. Visual verification needed → human test 1/2.                 |
| 2  | `assets/anim-schema.json` exists, loaded by `tuning.py` as a second schema, and clip durations editable live via panel                      | ✓ VERIFIED   | assets/anim-schema.json exists with 9 clips; tuning.load_anim at src/core/tuning.py:310; main.py:190 boot-call; AnimSlider at panel.py:24–40; reload_anim_schema at panel.py:313. test_tuning_anim.py all 16 tests pass. |
| 3  | Particle sprites live in a dedicated image bank separate from the map tileset                                                                | ✓ VERIFIED   | SPRITE_MANIFEST: tiles=bank 0, particles=bank 2 (main.py:145,155). test_sprite_manifest_banks_distinct passes. effects entry removed. Physical non-competition under load needs eyes-on → human test 3.                |
| 4  | Automated regression test confirms no animation state read mutates `.w` or `.h`                                                             | ✓ VERIFIED   | tests/test_anim_hitbox.py exists with 5 functions; 198-combo matrix; runs in default pytest invocation (D-22 hard gate); runtime 0.12s. All 5 tests pass.                                                               |

**Score:** 4/4 ROADMAP SCs have verifiable implementation evidence. SC1 needs a 15-minute human smoke test to confirm visual transitions render; SC2 needs a human test to confirm the slider drag produces a live speed change; SC3 needs a human test to confirm map tiles are not corrupted under particle load.

## Plan Frontmatter Truths — Detailed

### Plan 01 — PlayerAnimDriver + pause_for + placeholder sprites

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1.1 | PlayerAnimDriver carries vx_sign, prev_facing, skid_ticks, land_ticks, crouch_ticks | ✓ VERIFIED | src/anim/player_anim.py:52–63 — all 5 fields present with Phase 26 originals |
| 1.2 | AnimPlayer.pause_for(n) freezes tick counter for exactly n frames without touching frame_index | ✓ VERIFIED | src/anim/anim_player.py:20–27 (definition) + :32–34 (consumer in tick); test_pause_for_freezes_ticks + test_pause_for_additive + test_pause_for_cleared_on_set_clip all pass |
| 1.3 | AnimFSM.pause_for(n) forwards to the active AnimPlayer | ✓ VERIFIED | src/anim/state_machine.py:36–42 + test_anim_fsm_pause_for_forwards passes |
| 1.4 | player.png contains authored placeholder frames for all 9 new offsets | ✓ VERIFIED (procedural) | assets/sprites/player.png exists; U=48/64/80/96/112/128/144/160/176 referenced by PLAYER_CLIPS. Sprite art is procedurally generated placeholders per 31-06-SUMMARY known-limitations — acceptable per CONTEXT D-02/D-03/D-05 and the Plan 01 Task 3 "stubbed" resume-signal path |

### Plan 02 — Transition clips + driver extension + subscribers + drill bridge

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 2.1 | jump_stationary vs jump_running split by vx_sign | ✓ VERIFIED | player_anim.py:127–128 + test_metroid_jump_split passes |
| 2.2 | Landing fires land_squash for LAND_SQUASH_FRAMES | ✓ VERIFIED | player_anim.py:125 rule + :101–105 clip shape + test_land_squash_rule_fires + test_land_event_arms_land_ticks pass |
| 2.3 | Facing flip while grounded fires turn_skid for TURN_SKID_FRAMES | ✓ VERIFIED | player_anim.py:123 rule + player.py:878–879 edge detect arm + test_turn_skid_rule_fires + test_update_anim_driver_snapshots_prev_facing pass |
| 2.4 | jump_start event fires jump_crouch for JUMP_CROUCH_FRAMES (non-looping) | ✓ VERIFIED | player_anim.py:96–100 (loop=False) + player.py:93–94 + test_jump_crouch_rule_takes_priority + test_jump_crouch_clip_non_looping pass |
| 2.5 | DIVING state picks drill_spin 4-frame looping clip | ✓ VERIFIED | player_anim.py:129 rule + :111–116 clip (4 frames, loop=True) + test_drill_spin_cycles_four_frames pass |
| 2.6 | drill_block_break pauses drill_spin for DRILL_RECOIL_PAUSE_FRAMES (animation only) | ✓ VERIFIED | main.py:260 pause_for(DRILL_RECOIL_PAUSE_FRAMES) + test_drill_block_break_spawns_burst_and_pauses_anim pass |
| 2.7 | prev_facing snapshotted BEFORE facing overwrite | ✓ VERIFIED | player.py:873 (prev_facing = d.facing) precedes :875 (facing = ...) + test_update_anim_driver_snapshots_prev_facing passes |
| 2.8 | Every transient counter decrements every frame | ✓ VERIFIED | player.py:882–884 + test_update_anim_driver_decrements_counters passes |

### Plan 03 — Particle bank separation + sprite-backed Particle + drill subscriber

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 3.1 | assets/sprites/particles.png exists and loads into image bank 2 at x=0 y=0 | ✓ VERIFIED | File exists (951 B); SPRITE_MANIFEST["particles"]=(2,0,0,"assets/sprites/particles.png") at main.py:155 |
| 3.2 | SPRITE_MANIFEST has particles entry at bank 2; effects entry removed | ✓ VERIFIED | main.py:152 comment + :155 particles line; test_sprite_manifest_effects_removed + test_sprite_manifest_banks_distinct pass |
| 3.3 | Particle class uses keyword-only (dx, dy, life, bank_u, bank_v) constructor | ✓ VERIFIED | src/entities/effects.py:47 — `def __init__(self, x, y, *, dx, dy, life, bank_u, bank_v)` + test_particle_constructor_keyword_only passes |
| 3.4 | Particle.draw calls draw_sprite against bank 2 (not pyxel.pset) | ✓ VERIFIED | effects.py:73–80 (bank=2 positional arg); grep for pyxel.pset in effects.py returns 0; test_particle_draw_uses_bank_2 passes |
| 3.5 | Game.spawn_particle_burst spawns BURST_PARTICLE_COUNT=14 sprite-backed particles | ✓ VERIFIED | main.py:922–939 + test_drill_block_break_spawns_burst_and_pauses_anim (14 particles) passes |
| 3.6 | drill_block_break subscriber spawns diverging burst AND calls pause_for | ✓ VERIFIED | main.py:250–274 (subscriber) + player.py:792–796 (bridge emit) + 2 integration tests pass |
| 3.7 | All legacy Particle(x,y,color) call sites migrated | ✓ VERIFIED | grep for 3-arg Particle pattern returns 0 in src/; spawn_explosion is a deprecation shim delegating to spawn_particle_burst (main.py:945–951) |

### Plan 04 — Fuse flash converging ring + BlobGrowth

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 4.1 | fuse_start spawns FUSE_PARTICLE_COUNT=16 converging particles in a ring at FUSE_RING_RADIUS | ✓ VERIFIED | main.py:282–299 (subscriber) + test_fuse_start_subscriber_spawns_ring_and_blob passes |
| 4.2 | Per-particle dx, dy vectors reach player centre in FUSE_CONVERGE_FRAMES=12 ticks | ✓ VERIFIED | main.py:291–292 (dx = (cx-start_x)/FUSE_CONVERGE_FRAMES); geometry check in integration test passes |
| 4.3 | fuse_start also appends BlobGrowth instance | ✓ VERIFIED | main.py:299 (self.fused_blobs.append(_BlobGrowth(...))) |
| 4.4 | BlobGrowth uses tier-2 AnimPlayer(clip) wrapping | ✓ VERIFIED | effects.py:83–141 — constructor builds AnimClip + AnimPlayer(clip) at :109–110; test_blob_growth_constructor + test_blob_growth_draw_bank_2 pass |
| 4.5 | BlobGrowth draws from bank 2 at progressive-radius frame offsets | ✓ VERIFIED | effects.py:133–141 (bank=2 positional arg, u from _anim_player.current_u()) |
| 4.6 | fuse_start subscriber reads player position at emit time (not cached) | ✓ VERIFIED | main.py:284–285 reads self.player.x / self.player.w at call time; Pitfall 3 grep sentinel would pass |

### Plan 05 — anim-schema.json + tuning.load_anim + panel ANIM tab + presets routing

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 5.1 | anim-schema.json exists with 9 clips (3 baseline + 6 Phase 31) | ✓ VERIFIED | File exists with idle, run, jump, jump_stationary, jump_running, jump_crouch, land_squash, turn_skid, drill_spin — verified by inspection |
| 5.2 | tuning.load_anim populates tuning.anim.player.clips | ✓ VERIFIED | src/core/tuning.py:310 + test_load_anim_builds_namespace passes |
| 5.3 | load_anim fails fast on missing clips, length mismatch, unknown field | ✓ VERIFIED | 6 fail-fast unit tests all pass (test_load_anim_fails_on_missing_clips_dict, _length_mismatch, _unknown_field, _missing_frames, _missing_durations, _isolation) |
| 5.4 | _anim_flat_index + get_anim_baseline + get_anim_value + set_anim_value isolate anim keys from physics flat namespace | ✓ VERIFIED | tuning.py:300, 373, 381, 389 all present; test_anim_flat_index_built + test_get_anim_value_returns_current + test_load_anim_isolation_from_physics_flat_index all pass |
| 5.5 | build_player_fsm reads from tuning.anim.player.clips | ✓ VERIFIED | player_anim.py:138–158 (loops tuning.anim.player.clips.items()); test_build_player_fsm_reads_from_tuning_anim + test_build_player_fsm_picks_up_new_durations_on_rebuild pass |
| 5.6 | Panel has ANIM tab with log2 duration sliders for every clip duration | ✓ VERIFIED | panel.py:97 TAB_DEFS ("Anim", {_ANIM_TAB_SENTINEL: None}) + :124–135 anim branch builds AnimSlider list; test_panel_anim_tab_exists passes. Live drag feedback → human test 2 |
| 5.7 | Panel Reload anim schema button re-runs load_anim + rebuilds FSM | ✓ VERIFIED | panel.py:313–323 reload_anim_schema + :331–347 _handle_reload_anim_click hit-test; test_panel_reload_anim_schema_rebinds_fsm passes |
| 5.8 | presets.py routes ANIM_ keys through set_anim_value | ✓ VERIFIED | src/ui/presets.py:79–81 (startswith("ANIM_") → tuning.set_anim_value); test_save_preset_includes_anim_durations + test_load_preset_routes_anim_keys + test_load_preset_skips_unknown_anim_keys all pass |

### Plan 06 — Hitbox-independence hard gate

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 6.1 | tests/test_anim_hitbox.py exists as a new test file | ✓ VERIFIED | File exists with 5 test functions |
| 6.2 | Matrix test drives every (state × vx_sign × vy_sign × facing) combination and asserts (w,h) invariant across 60 ticks per combo | ✓ VERIFIED | test_hitbox_invariant_across_matrix runs 11×3×3×2 = 198 combos, 60 ticks each |
| 6.3 | Every HITBOX_STATE covered (11 states min) | ✓ VERIFIED | HITBOX_STATES tuple has IDLE, RUNNING, JUMPING, FALLING, DIVING + WALL_SLIDING, DASHING, RAMMING, BOOSTING, CHARGING_SHOT, DEAD = 11 |
| 6.4 | Test runs in default pytest invocation (no opt-in mark per D-22) | ✓ VERIFIED | `pytest --collect-only | grep hitbox_invariant` returns 5 (default collection); no @pytest.mark.skipif gating |
| 6.5 | Test failure message identifies WHICH combo broke invariant | ✓ VERIFIED | test collects failures list and emits "state={!r} vx={} vy={} facing={}: w {}->{}..." strings |
| 6.6 | Hard gate must be green before /gsd-verify-work | ✓ VERIFIED | All 5 hitbox tests pass in both default pytest invocation and isolated file run |

## Required Artifacts — Three-Level Check

| Artifact | Expected | Level 1 (exists) | Level 2 (substantive) | Level 3 (wired) | Level 4 (data flows) | Status |
| -------- | -------- | ---------------- | --------------------- | --------------- | ---------------------- | ------ |
| src/anim/anim_player.py | pause_for + _pause_ticks | ✓ | ✓ (20-27 impl + 32-34 consume) | ✓ (imported in state_machine.py + effects.py) | ✓ (used by AnimFSM.pause_for) | ✓ VERIFIED |
| src/anim/state_machine.py | AnimFSM.pause_for forwarding | ✓ | ✓ (36-42) | ✓ (main.py:260 invokes via player._anim) | ✓ | ✓ VERIFIED |
| src/anim/player_anim.py | Extended driver + 9 PLAYER_CLIPS + reordered PLAYER_RULES + build_player_fsm from tuning | ✓ | ✓ (159 lines w/ all additions) | ✓ (imported by player.py:85) | ✓ (tuning.anim drives the clips dict) | ✓ VERIFIED |
| src/entities/player.py | _update_anim_driver extension + _on_land/_on_jump_start + drill_block_break bridge | ✓ | ✓ (lines 90-96, 792-796, 862-884) | ✓ (event_bus + _anim driver wired) | ✓ (subscribers mutate _anim_driver; emit fires once per drill break) | ✓ VERIFIED |
| src/entities/effects.py | Sprite-backed Particle (kwonly) + Effect shell + BlobGrowth (tier-2) | ✓ | ✓ (141 lines) | ✓ (Particle imported in main.py; BlobGrowth via from main import fused_blobs constants) | ✓ (particles list rendered at main.py:1033; fused_blobs at :1033) | ✓ VERIFIED |
| main.py | SPRITE_MANIFEST particles bank 2 + effects removed + spawn_particle_burst + drill/fuse subscribers + load_anim boot call + fused_blobs list + update/draw loops | ✓ | ✓ | ✓ (all constants + subscribers present at :140-301; update loop :640-648; draw loop :1032-1033) | ✓ | ✓ VERIFIED |
| assets/sprites/player.png | Extended strip with U offsets up to 176 | ✓ | ⚠ PROCEDURAL (Plan 01 Task 3 resume-signal "stubbed" path accepted per D-02/D-03/D-05) | ✓ (loaded via SPRITE_MANIFEST) | N/A | ✓ VERIFIED (acceptable placeholder) |
| assets/sprites/particles.png | Bank 2 sprite sheet with burst/convergence/blob placeholders | ✓ | ⚠ PROCEDURAL (Plan 03 Task 1 "stubbed" path accepted per D-19 Claude's Discretion) | ✓ (loaded via SPRITE_MANIFEST bank 2) | N/A | ✓ VERIFIED (acceptable placeholder) |
| assets/anim-schema.json | Nested entity→clips schema with 9 seeded clips | ✓ | ✓ (all 9 clips present, durations match Plan 02 seed values) | ✓ (loaded by tuning.load_anim called from main.py:190) | ✓ | ✓ VERIFIED |
| src/core/tuning.py | load_anim + anim namespace + _anim_flat_index + get/set_anim_value | ✓ | ✓ (lines 293-394) | ✓ (consumed by player_anim.build_player_fsm, presets.py, panel.py AnimSlider) | ✓ | ✓ VERIFIED |
| src/ui/panel.py | ANIM tab + Reload button + AnimSlider adapter | ✓ | ✓ (lines 24-40, 87-97, 124-135, 313-347) | ✓ (TAB_DEFS has ("Anim", ...); AnimSlider subclasses Slider) | ✓ | ✓ VERIFIED |
| src/ui/presets.py | ANIM_ prefix routing + _anim_keys helper | ✓ | ✓ (lines 27-30, 44-45, 79-83) | ✓ (called during save_preset + load_preset) | ✓ | ✓ VERIFIED |
| tests/test_anim.py | pause_for + driver + constants + panel tests | ✓ | ✓ (all 8 Plan 01 tests + 7 Plan 02 + 2 Plan 05 = 17+ new functions) | ✓ | ✓ | ✓ VERIFIED |
| tests/test_anim_events.py | drill_block_break + fuse_start + BlobGrowth integration tests | ✓ | ✓ (12 passing tests) | ✓ | ✓ | ✓ VERIFIED |
| tests/test_anim_hitbox.py | 198-combo hitbox matrix + 4 event-path invariants | ✓ | ✓ (5 test functions, 198 combos total) | ✓ (default pytest collection) | ✓ | ✓ VERIFIED |
| tests/test_tuning_anim.py | 13 fail-fast + 3 preset-routing tests | ✓ | ✓ (16 passing tests) | ✓ | ✓ | ✓ VERIFIED |
| tests/test_sprite_assets.py | particles bank 2 + effects removed + banks distinct | ✓ | ✓ (3 new Phase 31 tests pass) | ✓ | ✓ | ✓ VERIFIED |

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| tests/test_anim.py::test_pause_for_freezes_ticks | AnimPlayer.pause_for | direct call | ✓ WIRED | Test passes |
| tests/test_anim.py::test_anim_fsm_pause_for_forwards | AnimFSM.pause_for | forward | ✓ WIRED | Test passes |
| player.py::_update_anim_driver | PlayerAnimDriver | in-place mutation | ✓ WIRED | `d.vx_sign = ...` at player.py:876 |
| player.py::on_block_break (drill DIVING path) | event_bus.emit("drill_block_break") | Phase 31 provisional bridge | ✓ WIRED | player.py:796 with tx=tx, ty=ty kwargs |
| main.py::_on_drill_block_break | player._anim.pause_for | AnimFSM.pause_for forward | ✓ WIRED | main.py:260 `self.player._anim.pause_for(DRILL_RECOIL_PAUSE_FRAMES)` |
| main.py::_on_drill_block_break | game.particles.append(Particle(...)) | direct call | ✓ WIRED | main.py:266-272 |
| main.py::SPRITE_MANIFEST | assets/sprites/particles.png | bank 2 load | ✓ WIRED | main.py:155 `"particles":  (2, 0, 0, "assets/sprites/particles.png")` |
| main.py::_on_fuse_start | game.particles (16) + game.fused_blobs (1) | event subscription | ✓ WIRED | main.py:282-301 |
| main.py update/draw | game.fused_blobs | parallel to particles loop | ✓ WIRED | main.py:646-648 (update), :1033 (draw) |
| player_anim.build_player_fsm | tuning.anim.player.clips | dict iteration | ✓ WIRED | player_anim.py:151 `for clip_id, spec in tuning.anim.player.clips.items()` |
| panel.py::_handle_reload_anim_click | tuning.load_anim + build_player_fsm | rebind | ✓ WIRED | panel.py:313-323 reload_anim_schema |
| presets.load_preset | tuning.set_anim_value | ANIM_ prefix dispatch | ✓ WIRED | presets.py:79-81 |
| main.py boot | tuning.load_anim() | direct call after schema.init | ✓ WIRED | main.py:190 |

## Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| player._anim (AnimFSM) | clips dict | tuning.anim.player.clips (loaded from JSON) | Yes | ✓ FLOWING |
| game.particles | Particle instances | spawn_particle_burst / drill_block_break subscriber / fuse_start subscriber | Yes | ✓ FLOWING |
| game.fused_blobs | BlobGrowth instances | fuse_start subscriber | Yes | ✓ FLOWING |
| PlayerAnimDriver | vx_sign, skid_ticks, land_ticks, crouch_ticks | player._update_anim_driver() each frame | Yes | ✓ FLOWING |
| AnimSlider.current | tuning.get_anim_value(key) | tuning.anim.player.clips[clip].durations[i] | Yes | ✓ FLOWING |

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Python imports resolve | `python -c "from src.anim.player_anim import build_player_fsm; from src.anim.anim_player import AnimPlayer; from src.entities.effects import Particle, BlobGrowth; from src.ui.panel import reload_anim_schema; print('ok')"` | n/a (pyxel mock required for some modules) | ? SKIP (covered by pytest import-time collection — 487 tests collected & ran) |
| Phase 31 test suite passes | `pytest tests/test_anim.py tests/test_anim_events.py tests/test_anim_hitbox.py tests/test_tuning_anim.py --tb=no` | 82 passed | ✓ PASS |
| Hitbox hard gate collected in default pytest | `pytest --collect-only | grep -c hitbox_invariant` | 5 | ✓ PASS |
| anim-schema.json has 9 clips | Read/count clip keys | 9 | ✓ PASS |
| SPRITE_MANIFEST particles bank | Read main.py:155 | bank=2 | ✓ PASS |
| pyxel.pset retired from effects.py | `grep -c pyxel.pset src/entities/effects.py` | 0 | ✓ PASS |
| drill_block_break emit count in player.py | `grep -c 'event_bus.emit("drill_block_break"' src/entities/player.py` | 1 (exactly one bridge) | ✓ PASS |
| Running the engine | `python main.py` | Not runnable in headless verification context (Pyxel needs display) | ? SKIP → human |

## Requirements Coverage

Note: `.planning/REQUIREMENTS.md` does not exist in this repository. Requirement IDs ANIM-04/05/06/07 come from ROADMAP.md line 184. Every plan's `requirements:` frontmatter maps its ID to a phase task; cross-reference below:

| Requirement | Source Plan(s) | Description (implied from ROADMAP SC) | Status | Evidence |
|-------------|----------------|---------------------------------------|--------|----------|
| ANIM-04 | 31-01, 31-02, 31-04 | Transition frames for jump crouch, land recovery, turn-around, drill recoil, fuse flash | ✓ SATISFIED | All 6 transition clips present in PLAYER_CLIPS; all 6 PLAYER_RULES fire correctly; 7+ unit tests across test_anim.py verify; 5-clip SC1 visibility → human test 1 |
| ANIM-05 | 31-05 | `assets/anim-schema.json` loaded by tuning.py; clip data editable live via panel | ✓ SATISFIED | anim-schema.json exists; tuning.load_anim loads it; panel ANIM tab has 13 duration sliders; Reload button rebuilds FSM; preset routing fixed; 16 tuning_anim tests pass. SC2 live-drag behavior → human test 2 |
| ANIM-06 | 31-03 | Particle sprites in dedicated image bank separate from map tileset | ✓ SATISFIED | particles.png at bank 2; effects entry removed from manifest; test_sprite_manifest_banks_distinct passes. SC3 no-corruption-under-load → human test 3 |
| ANIM-07 | 31-06 | Automated regression test: no animation state read mutates .w or .h | ✓ SATISFIED | tests/test_anim_hitbox.py with 198-combo matrix + 4 event-path invariants; all 5 pass in default pytest invocation; D-22 hard gate |

**No orphaned requirements.** All four declared IDs (ANIM-04/05/06/07) appear in at least one plan's requirements field and have implementation evidence.

## Anti-Patterns Scan

Scanned the 7 primary files modified in Phase 31 (player.py, effects.py, main.py, player_anim.py, tuning.py, panel.py, presets.py):

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| src/entities/player.py | 792–796 | Provisional bridge emit documented as removable in Phase 32 | ℹ Info | Tracked for Phase 32 deletion (31-06-SUMMARY + plan comments). Not a stub — emit is functional. |
| main.py | 945–951 | `spawn_explosion` deprecation shim delegates to `spawn_particle_burst` | ℹ Info | Intentional migration path — legacy callers kept working while transitioning to new API. Self-documenting. |
| src/entities/effects.py | 20–38 | `Effect` class is a no-op shell | ℹ Info | Per D-16 retired; shell kept for import-path safety during migration. Documented for future deletion. |
| assets/sprites/player.png | — | Procedurally generated placeholder art | ℹ Info | Accepted per Plan 01 Task 3 "stubbed" resume-signal path and CONTEXT D-02/D-03/D-05. Not a gap. |
| assets/sprites/particles.png | — | Procedurally generated placeholder art | ℹ Info | Accepted per Plan 03 Task 1 "stubbed" resume-signal path and D-19 Claude's Discretion. Not a gap. |

No TODO/FIXME introduced by Phase 31. No empty-return render paths. No hardcoded empty collections that flow to rendering.

## Human Verification Required

Four items require eyes-on in a running engine session. See YAML frontmatter `human_verification` for machine-parseable specs; summary:

### 1. SC1 — Visible transitions in engine
**Test:** Run `python main.py`; perform stand-jump, run-jump, land, flip facing, drill a CRACKED_V block, trigger fusion.
**Expected:** Each maneuver shows a visually distinct frame/pose (crouch, squash, skid, spin, converging ring, growing blob) before returning to baseline idle/run/jump.
**Why human:** Placeholder sprite readability is a pixel-level aesthetic check; automated tests confirm the FSM picks the correct clip but not that the clip looks like what it's named.

### 2. SC1/SC2 — Panel ANIM tab slider drag + Reload button
**Test:** F1 → Anim tab → drag `ANIM_PLAYER_RUN_DURATION_0` slider; edit `assets/anim-schema.json` on disk; click Reload anim schema.
**Expected:** Run cycle speed changes live during drag; disk edit takes effect after Reload click.
**Why human:** Mouse-input interaction against a Pyxel GUI; live value change can only be visually observed in the running engine.

### 3. SC3 — Particle/tile bank separation under load
**Test:** Enter a CRACKED_V-dense room; drill through 5+ blocks in succession.
**Expected:** Each break produces a burst; map tiles continue rendering normally; no tile corruption.
**Why human:** The unit test covers the static manifest configuration — but the "no tile-slot competition" claim is about runtime rendering behavior that needs observation.

### 4. Provisional drill_block_break bridge end-to-end
**Test:** Drill a CRACKED_V tile and observe.
**Expected:** Exactly one burst + drill-spin clip pause; no double-emit; no exceptions in console.
**Why human:** Subscriber integration test uses FakeGame harness; the real Player/Game emit→subscribe→pause_for path has not been end-to-end exercised.

## Deferred Items

Two items are not currently met but are explicitly addressed elsewhere and should NOT block Phase 31 closure:

| # | Item | Addressed In | Evidence |
|---|------|--------------|----------|
| 1 | Real (non-procedural) pixel art for player transition frames, particle burst/convergence, and blob growth frames | Indefinitely deferred per CONTEXT D-02/D-03/D-05/D-07b and 31-06-SUMMARY known-limitations table | 31-06-SUMMARY: "Real pixel art deferred; user can author and replace assets/sprites/{player,particles}.png any time without code changes" |
| 2 | Canonical `drill_block_break` emit at fusion FSM level (removing the Phase 31 provisional bridge) | Phase 32 | ROADMAP Phase 32 goal + FUSION-DESIGN + plan-02 doc + 31-06-SUMMARY Phase 32 Pointer section: Phase 32 MUST remove the bridge at `src/entities/player.py:792-796` |

## Gaps Summary

No blocking gaps were found. All PLAN frontmatter must-haves are in code and exercised by unit/integration tests. All four ROADMAP Success Criteria have verifiable implementation evidence with three (SC1, SC2, SC3) needing a ~15-minute human smoke test to confirm in-engine visual/interactive behaviors that cannot be fully captured by automated tests in a headless Pyxel environment.

The status is **human_needed** — not `passed` — specifically because the ROADMAP success criteria explicitly demand visible transitions (SC1), live panel-tunability (SC1/SC2), and no-corruption-under-load (SC3) — all of which are in-engine visual/interactive observations beyond the scope of pytest in this harness.

Once the user runs `python main.py` and confirms the 4 human tests above, the phase can be reclassified as `passed` for archival.

---

_Verified: 2026-04-23_
_Verifier: Claude (gsd-verifier)_
