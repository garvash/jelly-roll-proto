# Requirements — v2.0 Game Feel

**Milestone:** v2.0 Game Feel
**Started:** 2026-04-11
**Goal:** Make player, slime, fusion, and ability systems feel right. Invert tuning source of truth, build live-tuning panel, replace primitive animation with FSM + event hooks, redesign fusion lifecycle with juice-as-mana economy, tune systematically, polish with juice.

---

## v2.0 Requirements

### Tuning Foundation

- [ ] **FND-01**: `physics-schema.json` is promoted to source of truth. Restructure into nested `tuning.*` (grouped source values) and `derived.*` (converter-facing derived values). Game boots with values identical to v1.3.
- [ ] **FND-02**: `src/core/tuning.py` loads the schema at startup, exposes values via PEP 562 `__getattr__`, supports in-memory mutation via `set_value()`, and atomic disk writes.
- [ ] **FND-03**: `src/core/constants.py` is rewritten as a passthrough compat shim so existing `from src.core.constants import X` call sites keep working.
- [ ] **FND-04**: Mutations via `tuning.set_value()` are visible to subsequent reads in the same process (verified via unit test). File-watch hot-reload is not implemented — the live-tuning panel (Phase 28) is the only editing interface. The git-pull workflow is "restart the game."
- [ ] **FND-05**: Call-site migration sweep — `src/entities/*.py` read `tuning.X` at use site (not import site) so hot-reload actually reaches entity values.
- [ ] **FND-06**: pml-to-ldtk converter contract smoke test verifies the restructured schema is still parseable by the external converter. CONVERTER-HANDOFF.md updated.

### Developer Tooling

- [ ] **TOOL-01**: Live-tuning panel MVP with F1 toggle, category tabs, grouped sliders for all `tuning.*` values.
- [ ] **TOOL-02**: Panel supports mouse-first interaction — click slider handles, drag to adjust, click category tabs. Keyboard fallback for precision entry.
- [ ] **TOOL-03**: Double-buffered writes prevent mid-frame state corruption (pending dict swaps to live dict at frame boundary).
- [ ] **TOOL-04**: Reset-to-default per slider; baseline-diff indicator shows how far each value has drifted from the v1.3 immutable baseline.
- [ ] **TOOL-05**: Preset save/load as versioned JSON files in `assets/presets/`. Ships with ≥2 presets (e.g. "tight", "floaty") plus the locked v1.3 baseline.
- [ ] **TOOL-06**: Autosave tuning journal — every panel edit written to a rolling journal file so crashes don't lose session progress.
- [ ] **TOOL-07**: A/B preset compare — two-slot loader to flip between two presets and feel the difference without losing either.
- [ ] **TOOL-08**: Diagnostic overlays toggled independently via F2–F5: hitbox wireframes, velocity vectors, input state glyphs + coyote/buffer timers, frame-time graph.
- [ ] **TOOL-09**: Slime-specific diagnostic overlay showing follow anchor, target point, stuck detection state, catch-up state.

### Animation System

- [ ] **ANIM-01**: `src/anim/` package with `event_bus.py` (pub-sub dispatcher), `state_machine.py` (generic AnimFSM class), `anim_clip.py` (clip data with frames/duration/events), `anim_player.py` (frame ticker), `player_anim.py` (player-specific wiring).
- [ ] **ANIM-02**: Event bus emits transition events from gameplay code: `direction_change`, `jump_start`, `jump_released`, `fall_start`, `land`, `wall_touch`, `wall_jump`, `drill_impact`, `fuse_start`, `fuse_end`, `ram_start`, `ram_impact`, `boost_tap`, `charge_shot_fire`, `spit`, `damaged`, `death`.
- [ ] **ANIM-03**: Hardcoded sprite frame toggle in `src/entities/player.py:790` replaced with AnimFSM-driven frame lookup. Player state machine unchanged; animation derives from it.
- [ ] **ANIM-04**: Transition frame insertion for key events — jump crouch, land recovery, turn-around, drill recoil, fuse flash. Procedural placeholders (palette swaps, 1-tick holds, y-offsets) used where real art is not ready.
- [ ] **ANIM-05**: `assets/anim-schema.json` holds animation clip data (frames, durations, event bindings). Loaded by `tuning.py` as a second schema; frame timings are tunable via the live panel.
- [ ] **ANIM-06**: Particle image bank is separated from the map tileset so particles cannot compete for map tile slots. Dedicated bank for FX sprites.
- [ ] **ANIM-07**: Animation state read must not modify hitbox dimensions — visual transforms (y-offset, frame swap) MUST NOT change `.w/.h`. Regression test in CI.

### Fusion Lifecycle Redesign

- [ ] **FUS-01**: `.planning/FUSION-DESIGN.md` locked before any fusion re-implementation. Defines the `initiate → sustain → end` model, activation input (charge-to-fuse vs alternatives), cancel windows, exit model, and the juice-as-mana economy.
- [ ] **FUS-02**: Juice-as-mana resource model — juice behaves like mana with distinct per-ability costs. Design doc enumerates cost for each ability (spit, drill, ram, hold, charge shot, bubble shield, boost) plus regen rate, mana shield drain, and empty-state behavior.
- [ ] **FUS-03**: Per-ability "contract" doc (one page each) for ABL-01..06 capturing the v1.3 behavior so Phase 9 refactor has an explicit regression target.
- [ ] **FUS-04**: `src/fusion/` package with `FusionAbility` Protocol, `FusionManager` state shell, `ChargeController` pre-manager, and six ability modules (drill_dive, slime_ram, slime_hold, charge_shot, bubble_shield, slime_boost). Old per-ability code stripped from `player.py`.
- [ ] **FUS-05**: Fusion refactor preserves validated v1.3 behavior for ABL-01..06 — regression playthrough against the contract docs passes before Phase 9 closes.
- [ ] **FUS-06**: Per-ability feel pass — each of the six abilities retuned and polished against the new lifecycle: windup timing, sustain behavior, end/cancel feel, particle colors, button mapping, SFX identity.
- [ ] **FUS-07**: Save format versioned with a `save_version` field. v1.3 saves may break (explicit user acceptance).

### Player Movement Tuning

- [ ] **MOV-04**: Player movement/jump feel tuning pass — retune accel, friction, gravity, jump force, variable jump, falling gravity multiplier, coyote time, jump buffer, wall slide friction, wall jump impulse, kick parameters. Uses live panel.
- [ ] **MOV-05**: Input responsiveness audit — buffering, coyote windows, cancel windows audited across all player states. Input visualizer overlay (TOOL-08) makes regressions falsifiable.
- [ ] **MOV-06**: Written feel targets defined before tuning starts (e.g. "cross 4-tile gap, land 1 tile in"; "coyote 6 frames ok, 7 fail"). Each tuning phase has an explicit exit criterion and 1–1.5 week time-box.

### Slime Feel Tuning

- [ ] **SLM-04**: Slime follow/AI feel pass — retune follow accel, max speed, catch-up threshold, stuck timeout, look-ahead distance, terrain reactions. The dual-hero identity depends on slime feeling alive, not draggy.

### Juice Polish

- [ ] **JUICE-01**: Camera shake — trauma-squared model in `src/fx/`. Hooked to `drill_impact`, `land` (velocity-scaled), `ram_impact`, `damaged` events. Intensity tunable via panel. Juice budget defined (NONE/SUBTLE/MEDIUM/BIG per event) to avoid over-application.
- [ ] **JUICE-02**: Hitstop (global frame freeze) — duration tunable per event, ~3–8 frames. Must preserve input polling during freeze (inputs buffer, not drop). Hooked to `drill_impact`, `ram_impact`, `damaged`, `charge_shot_fire`, boss hits.
- [ ] **JUICE-03**: Pooled particle system in `src/fx/particles.py` — fixed pool ~128 particles, no per-frame allocations, `pyxel.pset` over `pyxel.rect` for cheap plotting. Presets: `burst_dust`, `drill_impact`, `jump_dust`, `fuse_spark`, `death_explode`.
- [ ] **JUICE-04**: Impact flash (screen-wide white tint, ~2 frames) on high-impact events.
- [ ] **JUICE-05**: Sound channel map + debounce — assign each event class to a channel, prevent repeated-frame sound spam, layer hit sounds for weight.

---

## Future Requirements (Deferred)

- Replay / timeline scrubber (defer to v2.1+)
- Frame-by-frame step mode
- Side-by-side preset diff mode
- GIF export hotkey
- Landing hitstop scaled by fall velocity
- Tuning playground/sandbox test room
- Pitch-shifted repeat sounds
- Real hand-drawn transition frames in Aseprite (replace procedural placeholders)
- Camera smoothing + look-ahead tuning (defer; current camera is acceptable)
- Authored squash/stretch sprite variants (deferred — Pyxel cannot procedurally scale; replaced by transition frames for v2.0)

## Out of Scope

- **Animation blending / skeletal / bone rigs** — Pyxel is pixel-per-pixel, no tweening runtime
- **Mobile-style touch slider UI** — desktop prototype only, mouse+keyboard
- **Inventory / skill tree for fusion** — fusion abilities remain mechanical, no unlock currency
- **Cinematic fusion camera** — takes control away, bad feel
- **Shader chain / post-processing** — Pyxel has no shader pipeline
- **Tutorial/help overlay for the panel** — debug tool for single developer, no need
- **Replacing fusion mechanic entirely** — dual-hero fusion is the core vision, redesign is lifecycle not concept
- **Per-frame tuning of every magic number** — curated ~30–50 params, not 500
- **Round-trip v1.3 save compatibility** — saves may break in v2.0 (explicit acceptance)
- **Gamepad input for debug panel** — mouse covers the 90% iteration case
- **External UI libraries (pygame-gui, imgui, dearpygui)** — incompatible with Pyxel framebuffer
- **FSM libraries (pytransitions, python-statemachine)** — 10× heavier than needed for ~6 states

---

## Traceability

Every v2.0 requirement maps to exactly one phase. Coverage: 38/38.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FND-01 | Phase 24 — Tuning Foundation | Pending |
| FND-02 | Phase 24 — Tuning Foundation | Pending |
| FND-03 | Phase 24 — Tuning Foundation | Pending |
| FND-04 | Phase 24 — Tuning Foundation | Pending |
| FND-05 | Phase 25 — Call-Site Migration | Pending |
| FND-06 | Phase 24 — Tuning Foundation | Pending |
| TOOL-01 | Phase 28 — Live-Tuning Panel MVP | Pending |
| TOOL-02 | Phase 28 — Live-Tuning Panel MVP | Pending |
| TOOL-03 | Phase 28 — Live-Tuning Panel MVP | Pending |
| TOOL-04 | Phase 28 — Live-Tuning Panel MVP | Pending |
| TOOL-05 | Phase 28 — Live-Tuning Panel MVP | Pending |
| TOOL-06 | Phase 28 — Live-Tuning Panel MVP | Pending |
| TOOL-07 | Phase 28 — Live-Tuning Panel MVP | Pending |
| TOOL-08 | Phase 27 — Diagnostic Overlays | Pending |
| TOOL-09 | Phase 27 — Diagnostic Overlays | Pending |
| ANIM-01 | Phase 26 — Event Bus + Animation FSM Skeleton | Pending |
| ANIM-02 | Phase 26 — Event Bus + Animation FSM Skeleton | Pending |
| ANIM-03 | Phase 26 — Event Bus + Animation FSM Skeleton | Pending |
| ANIM-04 | Phase 31 — Animation Content + Particle Bank | Pending |
| ANIM-05 | Phase 31 — Animation Content + Particle Bank | Pending |
| ANIM-06 | Phase 31 — Animation Content + Particle Bank | Pending |
| ANIM-07 | Phase 31 — Animation Content + Particle Bank | Pending |
| FUS-01 | Phase 30 — Fusion Lifecycle Design Doc | Pending |
| FUS-02 | Phase 30 — Fusion Lifecycle Design Doc | Pending |
| FUS-03 | Phase 30 — Fusion Lifecycle Design Doc | Pending |
| FUS-04 | Phase 32 — Fusion Manager + Protocol Refactor | Pending |
| FUS-05 | Phase 32 — Fusion Manager + Protocol Refactor | Pending |
| FUS-06 | Phase 33 — Per-Ability Feel Pass | Pending |
| FUS-07 | Phase 32 — Fusion Manager + Protocol Refactor | Pending |
| MOV-04 | Phase 29 — Player Movement Feel Pass | Pending |
| MOV-05 | Phase 29 — Player Movement Feel Pass | Pending |
| MOV-06 | Phase 29 — Player Movement Feel Pass | Pending |
| SLM-04 | Phase 34 — Slime Follow/AI Feel Pass | Pending |
| JUICE-01 | Phase 35 — Juice Polish | Pending |
| JUICE-02 | Phase 35 — Juice Polish | Pending |
| JUICE-03 | Phase 35 — Juice Polish | Pending |
| JUICE-04 | Phase 35 — Juice Polish | Pending |
| JUICE-05 | Phase 35 — Juice Polish | Pending |

### Coverage by Phase

| Phase | Requirements | Count |
|-------|--------------|-------|
| Phase 24 — Tuning Foundation | FND-01, FND-02, FND-03, FND-04, FND-06 | 5 |
| Phase 25 — Call-Site Migration | FND-05 | 1 |
| Phase 26 — Event Bus + Anim FSM Skeleton | ANIM-01, ANIM-02, ANIM-03 | 3 |
| Phase 27 — Diagnostic Overlays | TOOL-08, TOOL-09 | 2 |
| Phase 28 — Live-Tuning Panel MVP | TOOL-01, TOOL-02, TOOL-03, TOOL-04, TOOL-05, TOOL-06, TOOL-07 | 7 |
| Phase 29 — Player Movement Feel Pass | MOV-04, MOV-05, MOV-06 | 3 |
| Phase 30 — Fusion Lifecycle Design Doc | FUS-01, FUS-02, FUS-03 | 3 |
| Phase 31 — Animation Content + Particle Bank | ANIM-04, ANIM-05, ANIM-06, ANIM-07 | 4 |
| Phase 32 — Fusion Manager + Protocol Refactor | FUS-04, FUS-05, FUS-07 | 3 |
| Phase 33 — Per-Ability Feel Pass | FUS-06 | 1 |
| Phase 34 — Slime Follow/AI Feel Pass | SLM-04 | 1 |
| Phase 35 — Juice Polish | JUICE-01, JUICE-02, JUICE-03, JUICE-04, JUICE-05 | 5 |
| Phase 36 — Milestone Cap | (validation — no new REQ-IDs) | 0 |
| **Total** | | **38** |
