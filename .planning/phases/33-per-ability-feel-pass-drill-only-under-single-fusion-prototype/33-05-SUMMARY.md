---
phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
plan: 05
subsystem: audio-particles
tags: [audio, particles, event-bus, pyxel, identity, subscribers]

# Dependency graph
requires:
  - phase: 32
    provides: FusionManager + DrillDive/Pogo abilities + drill_start / drill_block_break / drill_impact / fuse_start emit sites
  - phase: 32.1
    provides: FUSION-DESIGN re-lock with Enemy Interaction subsection (D-03/D-04/D-05) — drill_enemy_hit emit contract
  - phase: 33-03
    provides: drill_dive.py:_scan_and_damage_enemies emits drill_enemy_hit with x/y kwargs
  - phase: 33-04
    provides: player.py fused-tap-Z branch emits daze_fire on projectile spawn
provides:
  - "src/core/audio.py module with 7 named SFX slot constants + init_sounds + play_sfx"
  - "PARTICLE_TYPE_TABLE dispatch in main.py routing type arg to bank-2 cells"
  - "particles.png bank-2 expansion (64x32 -> 64x48) with 3 new 16x16 cells"
  - "7 audio subscribers + 1 drill_enemy_hit particle subscriber wired in Game.__init__"
  - "pogo_bounce event emitted from src/fusion/pogo.py on both bounce paths"
affects: [phase-33-06-feel-targets-signoff, phase-35-audio-debounce-channel-map]

# Tech tracking
tech-stack:
  added:
    - "pyxel.sounds[N].set() audio surface (first audio module in repo)"
  patterns:
    - "src/core/audio.py: module-level constants + name->slot dict + thin play wrapper"
    - "spawn_particle_burst type-keyed dispatch table with safe default"
    - "Subscriber wiring concentrated in Game.__init__ (Phase 31 Pitfall 5)"
    - "Event-bus emit at the gameplay site, audio/particle reaction in Game subscribers (side-channel pattern from Phase 31)"

key-files:
  created:
    - "src/core/audio.py"
  modified:
    - "main.py"
    - "src/fusion/pogo.py"
    - "assets/sprites/particles.png"

key-decisions:
  - "Drill block-break subscriber refactored to call self.spawn_particle_burst(type=\"drill_block_break\") instead of inlining Particle construction with hardcoded PARTICLE_BURST_U/V — single source of bank-2 dispatch policy lives in PARTICLE_TYPE_TABLE."
  - "pogo_bounce emit added to BOTH bounce paths in pogo.py (soft-destructible at line ~118 AND enemy-contact at line ~134); landing path (\"landed\" reason) does NOT emit pogo_bounce because it is a confirm-only landing, not a bounce."
  - "particles.png stored as RGBA PNG (Pyxel loads it fine — image bank is always 256x256 internally regardless of source mode)."
  - "Audio cue note/tone/volume/effect/speed strings are feel sketches; tweak via panel iteration in Plan 06 (per CONTEXT § Claude's Discretion)."

patterns-established:
  - "Side-channel audio: gameplay code emits event_bus.emit(name); audio/particles subscribe in Game.__init__. Audio is never driven directly from FSM tick paths."
  - "Type-keyed particle dispatch: PARTICLE_TYPE_TABLE.get(type, default) — adding a new visual variant is a 1-line table entry + new (u,v) constants, not a code-path branch."
  - "Auto-channel sentinel pattern: pyxel.play(-1, slot) with -1 as a named module constant (_AUTO_CHANNEL) instead of magic number."

requirements-completed: [FUS-06]

# Metrics
duration: 35min
completed: 2026-04-29
---

# Phase 33 Plan 05: Audio + Particle Subscriber Wiring Summary

**Per-cue audio identity for 7 Phase 33 events + bank-2 particle differentiation routed through PARTICLE_TYPE_TABLE; drill / daze / pogo now sound and look distinct (FUS-06 blindfolded-observer surface).**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-04-29T17:25:00Z (worktree base correction)
- **Completed:** 2026-04-29T17:52:00Z
- **Tasks:** 3 / 3
- **Files modified:** 4 (1 new + 3 modified)

## Accomplishments

- Created `src/core/audio.py` (87 LOC) with 7 named SFX slot constants, `_NAME_TO_SLOT` dispatch dict, `_AUTO_CHANNEL = -1` sentinel, `init_sounds()` and `play_sfx(name)` — all 3 RED tests in `tests/test_audio.py` go GREEN.
- Expanded `assets/sprites/particles.png` from 64x32 to 64x48 with 3 new 16x16 cells in the y=32 row (drill_block_break earthbound brown/orange shrapnel; drill_enemy_hit combat yellow/orange radial; daze_splat blue/green splat).
- Added 6 new `(u, v)` module-level constants and a `PARTICLE_TYPE_TABLE` dispatch dict to `main.py`; refactored `spawn_particle_burst` to look up bank-2 offsets via `PARTICLE_TYPE_TABLE.get(type, default)` so the legacy `spawn_explosion` shim still works.
- Wired 7 audio subscribers + 1 `drill_enemy_hit` particle subscriber in `Game.__init__` (Phase 31 Pitfall 5 — never `Player.__init__`); added `_audio.init_sounds()` call once after the existing `_event_bus` import block.
- Refactored existing `_on_drill_block_break` subscriber to route through `self.spawn_particle_burst(type="drill_block_break")` so the new earthbound bank-2 cell renders for drill block-breaks (instead of the generic `PARTICLE_BURST_*` cell).
- Added `event_bus.emit("pogo_bounce")` to both bounce paths in `src/fusion/pogo.py` (soft-destructible bounce + enemy-contact bounce); landing path intentionally silent.

## Task Commits

Each task was committed atomically (worktree mode, --no-verify per parallel-execution protocol):

1. **Task 1: Create src/core/audio.py module** — `92d5a00` (feat)
2. **Task 2: particles.png bank-2 expansion + PARTICLE_TYPE_TABLE dispatch** — `2286f59` (feat)
3. **Task 3: Game.__init__ subscriber wiring + pogo_bounce emit** — `75dafd0` (feat)

_Note: Each task's TDD GREEN landed in a single commit; no separate test commits were needed because tests/test_audio.py was already shipped RED in Wave 0 (Plan 33-01) and went GREEN automatically once the audio module existed._

## Files Created/Modified

- `src/core/audio.py` (NEW) — Phase 33 D-12 minimal audio surface (7 SFX cues, init/play API).
- `main.py` — added `_audio` import, `_audio.init_sounds()` call, 7 audio subscribers, `_on_drill_enemy_hit` particle subscriber, 6 new bank-2 (u,v) constants, `PARTICLE_TYPE_TABLE` dispatch dict; refactored `spawn_particle_burst` to use the table; refactored `_on_drill_block_break` to route through `spawn_particle_burst(type=...)`.
- `src/fusion/pogo.py` — added `from src.anim import event_bus` import; emit `pogo_bounce` immediately before each `TickResult(... exit_reason="bounced")` return (soft-destructible bounce site + enemy-contact bounce site).
- `assets/sprites/particles.png` — expanded from 64x32 to 64x48; new y=32 row contains drill_block_break / drill_enemy_hit / daze_splat 16x16 cells using pyxel earthbound (4/9/10) and blue/green (11/12) palette colors per D-15.

## Decisions Made

- **Drill block-break subscriber refactored to use spawn_particle_burst:** Plan called for "If the subscriber currently uses raw u/v args, update to use the type-keyed path so the new earthtone cell renders." The pre-existing `_on_drill_block_break` inlined Particle construction; refactoring to `self.spawn_particle_burst(tx*TILE_SIZE, ty*TILE_SIZE, type="drill_block_break")` consolidates the dispatch policy in one place (`PARTICLE_TYPE_TABLE`).
- **Both pogo bounce paths emit pogo_bounce:** pogo.py has two `exit_reason="bounced"` return sites — soft destructible (~line 118) and enemy contact (~line 134). Both qualify as "bounce" semantics; landing (`exit_reason="landed"`) does NOT emit because it is confirm-only contact, not a bounce.
- **particles.png as RGBA PNG:** PIL paste preserved colors better when saved as RGBA. Pyxel's image bank loader handles the conversion automatically (verified via `pyxel.images[2].load(...)` round-trip — bank reports as 256x256 regardless of source dimensions, so the new cells at (0,32), (16,32), (32,32) are reachable).
- **Audio cue note strings are feel sketches:** Per CONTEXT § Claude's Discretion, the specific note/tone/volume/effect/speed values in `init_sounds()` are placeholders for Plan 33-06 panel-iteration playtest. The `init_sounds` test only asserts `.set` is called — it does not pin specific note strings.

## Deviations from Plan

None - plan executed exactly as written. The `_on_drill_block_break` subscriber refactor (calling `spawn_particle_burst` instead of inlining Particle construction) was explicitly called out by the plan's Step 5 in Task 2 as the recommended path.

## Issues Encountered

- **Pre-existing test failures (out of scope):** Baseline test run before Plan 33-05 changes showed 10-11 pre-existing failures unrelated to this plan: `test_ldtk_migration::test_tileset_relpath_cavern`, `test_phase05_nyquist::test_room_spawn_update`, two `test_phase22` cases, `test_physics::test_walk_logic`, `test_sprite_assets::test_palette_compliance`, and 5 `test_tuning` cases (baseline values drifted from Phase 29/30 retunes). These are out of scope per the deviation rules' SCOPE BOUNDARY clause; deferred-items.md update not needed because they are pre-existing and tracked elsewhere. All Plan 33-05 changes pass: 449 in-scope tests GREEN, 1 skipped, 11 deselected (the pre-existing failures).
- **No real audio playback verification:** Tests use a MagicMock `pyxel`; `pyxel.sounds[N].set` and `pyxel.play(-1, slot)` are mocked. Real audio playback is verified manually in Plan 33-06 (smoke test + FEEL-TARGETS sign-off).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Plan 33-06 (smoke test + FEEL-TARGETS sign-off):** Audio + particle differentiation is now wired end-to-end. Manual smoke test from the plan: fuse + drill into 3-enemy stack should produce 3 distinct drill_enemy_hit particle bursts (yellow/orange combat) and 3 drill_enemy_hit audio cues distinguishable from drill_block_break. Pogo bounce on enemy plays pogo_bounce SFX distinct from drill_impact thud (D-20 blindfolded-observer extension to pogo).
- **Plan 33-06 panel-iteration tweaks:** The 7 audio cues' note/tone/volume/effect/speed strings in `audio.init_sounds()` are feel sketches; tweak via panel iteration during the Plan 33-06 smoke session if any cue lacks identity.
- **Phase 35 (future):** Phase 33's audio surface is bounded — no debounce, no per-cue channel reservation. Phase 35 inherits and replaces the channel strategy (Phase 33 D-12 docstring documents this handoff).

## Self-Check: PASSED

**Files:**
- `src/core/audio.py` — FOUND
- `main.py` — FOUND (modified)
- `src/fusion/pogo.py` — FOUND (modified)
- `assets/sprites/particles.png` — FOUND (modified, 64x48)

**Commits:**
- `92d5a00` — FOUND (Task 1)
- `2286f59` — FOUND (Task 2)
- `75dafd0` — FOUND (Task 3)

**Acceptance gates (per plan):**
- src/core/audio.py: 7 SFX slot constants + init_sounds + play_sfx + _NAME_TO_SLOT + _AUTO_CHANNEL — VERIFIED
- tests/test_audio.py: 3/3 GREEN — VERIFIED
- particles.png: 64x48, new y=32 row populated — VERIFIED
- PARTICLE_TYPE_TABLE in main.py: 4 entries (block_break, drill_block_break, drill_enemy_hit, daze_splat) — VERIFIED
- spawn_particle_burst dispatches via PARTICLE_TYPE_TABLE.get(type, default) — VERIFIED
- 7 audio subscribers + 1 particle drill_enemy_hit subscriber wired in Game.__init__ — VERIFIED (12 total _event_bus.subscribe calls, was 5 pre-plan)
- pogo_bounce emit on both bounce paths in pogo.py — VERIFIED
- main.py imports cleanly — VERIFIED
- Full in-scope test suite GREEN — VERIFIED (449 passed)

---
*Phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype*
*Plan: 05*
*Completed: 2026-04-29*
