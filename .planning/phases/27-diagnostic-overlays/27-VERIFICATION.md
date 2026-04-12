---
phase: 27-diagnostic-overlays
verified: 2026-04-12T00:00:00Z
status: human_needed
score: 4/4 must-haves verified
overrides_applied: 0
gaps:
  - truth: "Full test suite passes without regression"
    status: failed
    reason: "Phase 27 commit f8817a5 deleted Level_17 assets; test_ldtk_migration::test_tileset_relpath_cavern now fails (assertion: tileset uid=64 not found)"
    artifacts:
      - path: "assets/output/simplified/Level_17/"
        issue: "Directory and all files deleted in commit f8817a5 (test(27-01): add failing tests for overlay manager)"
    missing:
      - "Restore Level_17 assets from before commit f8817a5, or fix the test to not depend on Level_17 if the level was intentionally removed"
human_verification:
  - test: "Run the game with python main.py and press F2"
    expected: "Colored wireframe boxes appear around all live entities — red on player, green on slime (when not fused/dissipated), orange on enemies, yellow on projectiles, grey on doors, dark purple on mole (boss). Boxes track entity positions exactly as they move."
    why_human: "Pixel-correct rendering, camera offset, and visual overlap with game world cannot be verified without running Pyxel"
  - test: "Press F3 while moving"
    expected: "Red arrow shows horizontal velocity direction and magnitude from player center. Blue arrow shows vertical velocity. Frame-time graph appears in top-right corner: green bars under 60fps threshold, red bars when spiking. Arrows also appear on slime."
    why_human: "Velocity magnitude scaling (VEL_SCALE=8, ARROW_MIN/MAX=8/32), arrowhead direction, and graph position relative to camera require visual confirmation"
  - test: "Press F4, walk off a ledge, then press jump while falling"
    expected: "Green dot appears at ground-leave position (coyote trigger). Red dot appears at jump-press position. Yellow line connects them showing the spatial gap. Small green pixel under player feet while coyote timer is active. Small blue pixel above player head while jump buffer timer is active."
    why_human: "Event-bus-driven blip placement and fade timing require gameplay interaction to trigger and visually inspect"
  - test: "Press F5 and walk around while slime follows"
    expected: "Breadcrumb dots trail behind slime — green (recent), dark green (mid), grey (old). Red circle around player showing SLIME_MAX_DIST boundary (~100px radius). Yellow circle showing SLIME_REFORM_DIST boundary (~8px radius). Pink dot at slime follow target. If slime gets stuck: flashing red X at slime center. Blue directional arrow when slime is catching up."
    why_human: "Slime follow state (stuck vs. catch-up), breadcrumb age coloring, and circle radii require real gameplay observation"
  - test: "Press F2, F3, F4, and F5 simultaneously, then play normally for 10 seconds"
    expected: "All four overlays active together. Gameplay movement, jumping, and slime follow behave identically to baseline — no input lag, no visual glitches. Toggle indicator visible in top-left corner showing all four keys active."
    why_human: "Overlay interaction, absence of gameplay state mutation, and frame-time impact require real-time play"
---

# Phase 27: Diagnostic Overlays Verification Report

**Phase Goal:** F2-F5 overlays for hitboxes, velocity, input state, slime follow; makes "feels off" falsifiable
**Verified:** 2026-04-12
**Status:** human_needed (one regression gap + visual verification pending)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|---------|
| 1 | F2 toggles hitbox wireframe overlay independently | VERIFIED | `overlays.show_hitboxes = False` toggled by `pyxel.btnp(pyxel.KEY_F2)` in `update()`. `_draw_hitbox_overlay(game)` draws `rectb` for player (8/red), slime (11/green), enemies (9/orange), projectiles (10/yellow), doors (6/grey), boss (2/purple). All 16 tests pass including `test_f2_toggles_hitboxes`. |
| 2 | F3 toggles velocity arrows and frame-time graph independently | VERIFIED | `show_velocity` toggled by F3. `_draw_velocity_overlay(game)` draws `pyxel.line()` arrows with VEL_SCALE=8, ARROW_MIN_LEN=8, ARROW_MAX_LEN=32, 2px chevrons. Frame-time graph uses `deque(maxlen=64)`, 64px wide x 24px tall, green/red at 16.67ms threshold. `test_f3_toggles_velocity` and `test_frame_time_buffer_maxlen` pass. |
| 3 | F4 toggles input state blips showing coyote and jump buffer spatial gaps | VERIFIED | `show_input` toggled by F4. `_draw_input_overlay(game)` draws coyote blips (green circ), jump blips (red circ), connector lines (yellow), buffer blips (blue), buffer-to-land connectors (pink), active coyote/buffer pixel indicators. Event bus subscriptions for `fall_start`/`jump_start`/`land` in `init()`. `test_coyote_blips_maxlen`, `test_record_coyote_blip`, `test_init_subscribes_events`, `test_init_idempotent` all pass. |
| 4 | F5 toggles slime follow overlay with breadcrumb trail and distance circles | VERIFIED | `show_slime` toggled by F5. `_draw_slime_overlay(game)` iterates `s.history` read-only with 3-tier color (green/dark-green/grey), draws `circb` at SLIME_MAX_DIST (100) and SLIME_REFORM_DIST (8), follow-target `circ` at `s.target_x/target_y` (pink), stuck detection `_slime_stuck_frames` counter with flashing X, catch-up arrow. `test_slime_trail_readonly`, `test_stuck_counter_increments`, `test_stuck_counter_resets` pass. |
| 5 | Overlay flags default to False on game boot | VERIFIED | Module-level `show_hitboxes = False`, `show_velocity = False`, `show_input = False`, `show_slime = False`. `test_flags_default_false` passes. `python -c "from src.core import overlays; print(overlays.show_hitboxes)"` outputs `False`. |
| 6 | Overlay drawing reads entity state without mutation | VERIFIED | All draw functions use read-only attribute access (`p.x`, `s.history`, etc.) — no setattr, no method calls that mutate. `test_hitbox_no_mutation`, `test_velocity_no_mutation`, `test_slime_trail_readonly` confirm x/y/w/h and history length unchanged after draw calls. |
| 7 | All overlays render on top of game without modifying gameplay state | VERIFIED (partial — visual confirmation pending) | main.py calls `overlays.draw(self)` after all entity `draw()` calls in `_draw_game_world()`, before victory overlay. `overlays.draw_indicator()` called after `pyxel.camera()` reset in `Game.draw()`. Read-only contract verified by tests. Visual confirmation requires human. |
| 8 | Toggle status indicator visible in screen-space top-left corner | VERIFIED (partial — visual confirmation pending) | `draw_indicator()` draws dark-blue rect + "F2/F3/F4/F5" labels at (2,2) after `pyxel.camera()` reset. Called at main.py:791. Screen-space position confirmed by code; visual confirmation requires human. |

**Score:** 4/4 roadmap success criteria verified (all automated checks green; visual checkpoint pending)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/core/overlays.py` | Overlay manager with toggle flags, hitbox/velocity/input/slime drawing | VERIFIED | 479 lines. Exports `update`, `draw`, `draw_indicator`, `init`, `show_hitboxes`, `show_velocity`, `show_input`, `show_slime`. All four overlay draw functions implemented (no stubs). |
| `tests/test_overlays.py` | 16+ unit tests covering toggle logic, buffer management, read-only access | VERIFIED | 395 lines. Exactly 16 test functions. Plan 01 tests (1-8) + Plan 02 tests (9-16). All 16 pass. |
| `main.py` | Game loop wired to overlay calls | VERIFIED | `from src.core import overlays` at line 132. `overlays.init(self)` at line 271. `overlays.update()` at line 417. `overlays.draw_indicator()` at line 791. `overlays.draw(self)` at line 856. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/core/overlays.py` | `pyxel.btnp(KEY_F2..F5)` | `update()` toggle handler | VERIFIED | Lines 130-137: four `if pyxel.btnp(pyxel.KEY_F2/F3/F4/F5)` toggle blocks |
| `src/core/overlays.py` | `game.player, game.slime, game.enemies` | `draw(game)` read-only entity access | VERIFIED | `_draw_hitbox_overlay` accesses `game.player`, `game.slime`, `game.enemies`, `game.projectiles`, `game.doors`, `game.mole` |
| `src/core/overlays.py` | `src/anim/event_bus.py` | `subscribe('fall_start'/'jump_start'/'land')` for blip placement | VERIFIED | Lines 116-118: `event_bus.subscribe("fall_start", _on_fall_start)` etc. in `init()`. `test_init_subscribes_events` confirms `_subscribers` populated. |
| `src/core/overlays.py` | `game.slime.history` | read-only iteration for breadcrumb trail | VERIFIED | Line 433: `for i, (hx, hy) in enumerate(s.history)` — enumerate only, no append/pop |
| `src/core/overlays.py` | `src/core/constants.py` (SLIME_MAX_DIST, SLIME_REFORM_DIST) | module-level import | VERIFIED | Lines 14-17: `from src.core.constants import VIEWPORT_W, VIEWPORT_H, SLIME_MAX_DIST, SLIME_REFORM_DIST`. Note: plan specified `tuning.py` but `constants.py` is the correct source (shim re-exports tuning values). Correctly resolved as deviation #2 in Summary. |
| `main.py` | `src/core/overlays.py` | `overlays.update()` in `Game.update()`, `overlays.draw(self)` in `_draw_game_world()`, `overlays.draw_indicator()` in `Game.draw()` | VERIFIED | All four call sites confirmed at lines 132, 271, 417, 791, 856 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `_draw_hitbox_overlay` | `game.player.x/y/w/h` | Entity attributes set by physics engine each frame | Yes — directly reads live entity state | FLOWING |
| `_draw_velocity_overlay` | `game.player.dx/dy` | Player physics velocity each frame | Yes — directly reads live velocity | FLOWING |
| `_draw_input_overlay` | `_coyote_blips`, `_jump_blips` | Event bus callbacks `_on_fall_start`, `_on_jump_start`, `_on_land` subscribed in `init()` | Yes — populated by real player events | FLOWING |
| `_draw_slime_overlay` | `game.slime.history` | Slime entity `self.history` deque populated during slime update | Yes — reads real position trail | FLOWING |
| `_draw_frame_time_graph` | `_frame_times` | `_update_frame_time()` called every frame via `update()` using `time.perf_counter()` | Yes — real wall-clock measurements | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Module imports with defaults False | `python -c "from src.core import overlays; print(overlays.show_hitboxes)"` | `False` | PASS |
| All overlay tests pass | `python -m pytest tests/test_overlays.py -x -q` | `16 passed in 0.08s` | PASS |
| main.py wiring present | `grep -n "overlays\." main.py` | 5 call sites at lines 132, 271, 417, 791, 856 | PASS |
| No stubs remain in overlays.py | grep for `pass$` in overlays.py | No results | PASS |
| D-03: no text in entity draw functions | `grep -n "pyxel.text" src/core/overlays.py` | Only line 231 (inside `draw_indicator`, correct) | PASS |
| Full suite regression | `python -m pytest tests/ -x -q` | **1 FAILED** — `test_ldtk_migration::test_tileset_relpath_cavern` (Level_17 assets deleted in commit f8817a5) | FAIL |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| TOOL-08 | 27-01, 27-02 | Diagnostic overlays toggled independently via F2-F5: hitbox wireframes, velocity vectors, input state glyphs + coyote/buffer timers, frame-time graph | SATISFIED | F2 hitbox: `_draw_hitbox_overlay` with per-type palette colors. F3 velocity: `_draw_velocity_overlay` with VEL_SCALE/ARROW constants. F4 input: `_draw_input_overlay` with event bus blips, coyote/buffer indicators. Frame-time graph: 64-entry deque, 64x24px graph. 16 tests pass. |
| TOOL-09 | 27-02 | Slime-specific diagnostic overlay showing follow anchor, target point, stuck detection state, catch-up state | SATISFIED | `_draw_slime_overlay`: breadcrumb trail from `s.history`, `circb` at SLIME_MAX_DIST/SLIME_REFORM_DIST, `circ` at `s.target_x/target_y` (follow anchor/target), `_slime_stuck_frames` counter with flashing X (stuck), catch-up arrow toward target when velocity > threshold. `test_stuck_counter_increments`, `test_stuck_counter_resets`, `test_slime_trail_readonly` pass. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `assets/output/simplified/Level_17/` | — | Directory deleted in commit f8817a5 | Blocker | Breaks `test_ldtk_migration::test_tileset_relpath_cavern` — full test suite not green |

No stubs, no TODOs, no hardcoded empty returns found in `src/core/overlays.py` or `tests/test_overlays.py`.

`pyxel.text()` appears only in `draw_indicator()` (screen-space HUD) — not in entity draw functions. D-03 (no text readouts in world-space overlays) is honored.

All numeric literals use named constants (`VEL_SCALE`, `ARROW_MIN_LEN`, `BLIP_RADIUS`, etc.) — no magic numbers.

### Human Verification Required

#### 1. F2 Hitbox Overlay Visual Correctness

**Test:** Run `python main.py`, press F2, move around, encounter enemies.
**Expected:** Red wireframe box exactly tracks player collision bounds. Green box tracks slime (absent when fused/dissipated). Orange boxes on enemies. Yellow on projectiles. Grey on doors. Dark purple on boss (mole) if present.
**Why human:** Camera offset in world-space rendering and pixel-exact alignment with entity positions require visual inspection.

#### 2. F3 Velocity + Frame-Time Graph Visual Correctness

**Test:** Press F3 while walking, jumping, and falling.
**Expected:** Red horizontal arrow and blue vertical arrow extend from player center, scaling with speed. Frame-time graph appears in top-right corner of viewport (not off-screen), green bars at 60fps, red when spiking. Arrows also visible on slime.
**Why human:** Arrow length scaling (VEL_SCALE=8), camera-offset graph position, and color-coding require real-time visual inspection.

#### 3. F4 Input Blip Spatial Gap Visualization

**Test:** Press F4, walk off a ledge and press jump while falling.
**Expected:** Green dot marks ground-leave position. Red dot marks jump-press position. Yellow connector line shows the gap. Green pixel under player feet while coyote timer active. Blue pixel above player head while buffer timer active. Dots fade after ~0.5s.
**Why human:** Event-bus-driven blip placement, fade timing, and connector visibility require gameplay interaction to trigger and observe.

#### 4. F5 Slime Follow Overlay Visual Correctness

**Test:** Press F5, walk around for 10+ seconds, trigger stuck state by blocking slime against geometry.
**Expected:** Breadcrumb trail behind slime with green-to-grey aging. Large red circle (~100px radius) around player. Small yellow circle (~8px) around player. Pink dot at slime's follow target. When slime is stuck: flashing red X. When chasing: small blue arrow toward target.
**Why human:** Slime follow state transitions (stuck/catch-up), breadcrumb age coloring, and large-radius circles require gameplay observation.

#### 5. All Four Overlays Simultaneously + No Gameplay Impact

**Test:** Activate all four overlays (F2+F3+F4+F5), play normally for 10 seconds including jumps and slime interaction.
**Expected:** All four overlays render together without visual corruption. Movement, jumping, slime follow behave identically to baseline. Toggle indicator in top-left shows all four keys active (white text). No frame drops visible in F3 graph.
**Why human:** Overlay stacking, gameplay state preservation, and frame-time impact can only be confirmed with real-time play.

### Gaps Summary

**One blocker gap: test suite regression from Level_17 asset deletion.**

Commit `f8817a5` (Phase 27 Plan 01 RED phase) deleted `assets/output/simplified/Level_17/` files. This causes `tests/test_ldtk_migration::test_tileset_relpath_cavern` to fail. The deletion appears to be a worktree merge artifact — Level_17 was an extra level in the original map that may have been intentionally removed from the LDtk project. However, the regression test still references it. The fix is either: (a) restore the Level_17 assets, or (b) update `test_ldtk_migration.py` to not expect Level_17 if it was intentionally removed from the map.

All overlay code itself (TOOL-08, TOOL-09) is correctly implemented, wired, and tested. The 16 overlay-specific tests all pass. Human visual verification (Task 2 of Plan 02) remains pending.

---

_Verified: 2026-04-12_
_Verifier: Claude (gsd-verifier)_
