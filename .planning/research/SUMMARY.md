# Project Research Summary

**Project:** Jelly Roll Proto — v2.0 Game Feel
**Domain:** Pyxel Metroidvania polish milestone — live-tuning tooling, animation FSM, fusion lifecycle redesign, juice
**Researched:** 2026-04-11
**Confidence:** HIGH

## Executive Summary

v2.0 Game Feel is a polish/redesign milestone on an existing, shipped prototype (v1.3, ~118K LOC). The user's verdict — "each function works to spec but doesn't feel right" — is resolved by inverting the tuning source of truth (`physics-schema.json` becomes authoritative, not `constants.py`), building a GMTK Platformer Toolkit–style live-tuning panel, replacing the hardcoded 2-frame sprite toggle with a real animation state machine + event bus, redesigning fusion as an explicit initiate/sustain/end lifecycle, and adding the Nijman juice trio (screen shake, hitstop, dust particles). The work is ~600 LOC of new code across ~6 modules plus targeted refactors to `player.py`, `slime.py`, and the fusion system.

The approach is almost entirely "build custom, not library." Pyxel's framebuffer is incompatible with every mainstream UI/animation/particle library (pygame-gui, imgui, pytransitions, arcade particles all require different render backends or C extensions). The one exception is `watchdog 6.0.0` for schema hot-reload, and even that has a viable 10-line mtime-polling fallback. Everything else is well-trodden hand-rolled patterns: PEP 562 module `__getattr__` for the tuning loader, a ~150 LOC FSM + pub-sub event bus, a Protocol+registry for fusion abilities, and trauma-squared screen shake.

The dominant risk is regression, not novelty. v1.0–v1.3 shipped working movement, fusion, combat, bosses, save, and pml-to-ldtk converter integration. Every pitfall worth tracking is a variation on "don't break what already works": converter contract drift, `constants.py` import-time caching defeating hot-reload, float/int silent coercion through JSON, squash/stretch accidentally scaling hitboxes, transition frames introducing input latency vs the v1.3 baseline, and "chase feel endlessly" with no exit criteria. Mitigation centers on a keystone Phase 1 (schema inversion + compat shim + converter smoke test), explicit feel targets per tuning phase, and hitbox-vs-visual separation from day one.

## Key Findings

### Recommended Stack

Add exactly **one runtime dependency: `watchdog>=6.0.0,<7`** for cross-platform file watching. Everything else is custom Python against Pyxel's primitive draw calls. Total new code is ~600 LOC across six new modules plus three small patches.

**Core additions:**
- **`watchdog 6.0.0`** — cross-platform schema hot-reload; Windows uses pure-Python ctypes fallback, zero transitive deps. Mtime-polling fallback available if thread-safety issues surface.
- **`src/core/tuning.py`** (~120 LOC) — schema loader with PEP 562 module `__getattr__`, dotted-key lookup, reload listeners, atomic disk writes.
- **`src/anim/` package** (~250 LOC) — `event_bus.py`, `state_machine.py`, `anim_clip.py`, `anim_player.py`, `player_anim.py`. Generic FSM + player-specific wiring.
- **`src/debug/` package** (~300 LOC) — `panel.py`, `slider.py`, `category.py`, `presets.py`, `overlays.py`. Custom Pyxel widgets, mouse-driven.
- **`src/fusion/` package** (~400 LOC refactor out of `player.py`) — `ability.py` Protocol, `manager.py` lifecycle, six ability modules.
- **`src/fx/` package** (~130 LOC) — `particles.py` pooled system, `hitstop.py` frame-freeze, camera shake patch.

**Explicitly rejected:** pygame-gui, pygame_menu, pyimgui, dearpygui (non-Pyxel render backends); pytransitions, python-statemachine (10× too heavy); arcade/pyglet particles (different backend); watchfiles (Rust wheel overkill). Full rationale and sources in STACK.md.

### Expected Features

**Must have (P1, defines v2.0):**
- Schema-as-source-of-truth migration — `physics-schema.json` authoritative, `constants.py` becomes PEP 562 compat shim
- Live-tuning panel MVP — grouped sliders, hot-reload, reset-to-default, toggle visibility (F1)
- Animation FSM + event hooks — `jump_start`, `land`, `direction_change`, `wall_touch`, `fuse_start`, `fuse_end`, `drill_impact`, etc.
- Transition frame insertion — jump crouch, land squash, turn-around, drill recoil
- Input visualizer overlay — makes the input-responsiveness audit falsifiable
- Movement/jump tuning pass — accel/friction/gravity/jump curves/coyote/buffer/wall jump/kick
- **Fusion lifecycle design doc (locked before re-implementation)**
- Fusion lifecycle re-implementation — initiate/sustain/end as real FSM phases
- Juice trio: screen shake + hitstop + dust particles (hooked to anim events)

**Should have (P2, polish tier):**
- Preset save/load with baseline diff (2–3 shipped presets)
- Slime follow feel pass (half the dual-hero identity)
- Squash/stretch via pre-baked sprite variants (Pyxel `blt` has no destination scale)
- Impact flash + hit sound layering
- Velocity / hitbox / ground-sensor debug overlays
- Per-ability feel pass (drill, ram, hold, charge shot, bubble, boost)
- Camera smoothing + look-ahead tuning
- Cancel windows on ability states

**Defer (v2.1+):**
- Replay / timeline scrubber
- Frame-by-frame step mode
- Side-by-side preset diff mode
- GIF export hotkey
- Landing hitstop scaled by fall velocity
- Playground test room
- Pitch-shifted repeat sounds

**Anti-features (do NOT build):**
- Animation blending / skeletal / bone rigs
- Mobile-style touch slider UI
- Inventory / skill tree for fusion
- Cinematic fusion camera (takes control away)
- Shader chain (Pyxel has no shader pipeline)
- Tutorial/help overlay for the panel
- Replacing fusion mechanic entirely
- Per-frame tuning of every magic number (curate ~30–50 params)

### Architecture Approach

Four architectural decisions are already made and carry through the roadmap:

1. **`tuning.py` loader with PEP 562 `__getattr__`** — single module owns schema load, hot-reload via mtime check in `update()`, writebacks via `set_value()`, reload listeners for subsystems that cache derived values. `constants.py` becomes a dumb shim that re-exports from `tuning` so existing call sites keep working during incremental migration. The shim is load-bearing — it makes Phase 1 non-breaking.

2. **Dual FSMs + event bus** — gameplay FSM stays on `Player`, new animation FSM lives in `src/anim/` and *derives* state from gameplay + events (not parallel/authoritative). The event bus (dead-simple pub/sub in `src/anim/event_bus.py`) is the decoupling layer that lets juice (particles, shake, hitstop, audio) subscribe without coupling to animation or gameplay directly.

3. **Fusion as Protocol + registry** — `FusionAbility` Protocol with `can_initiate / initiate / sustain / should_end / end` + `juice_cost / duration_cap`. `FusionManager` owns the `INACTIVE → INITIATING → SUSTAINING → ENDING` state shell; abilities are near-stateless. Charge-to-fuse lives in a pre-manager `ChargeController`. Existing per-ability code in `player.py` is cut-and-pasted into module classes.

4. **Physics executes on input frame; visuals lag** — transition frames render *on top of* physics that already happened. The velocity change occurs the frame the button is pressed; the anticipation sprite is ornamental. This is the single most important anti-regression rule in the milestone.

**Major components:**
1. **Tuning foundation** — `tuning.py` + `derive.py` + restructured `physics-schema.json` (nested `tuning.*` + `derived.*`). Converter reads only `derived.*` + `placement_rules` + `player`.
2. **Animation subsystem** — `event_bus`, `state_machine`, `anim_clip`, `anim_player`, `player_anim`, backed by separate `assets/anim-schema.json` (keeps converter contract clean).
3. **Debug/tuning UI** — `panel.py` (controller), `slider.py`, `category.py` (tabs), `presets.py` (versioned + autosave), `overlays.py`.
4. **Fusion subsystem** — `manager.py` + `ability.py` Protocol + six ability modules, integrated on `Player.update()`.
5. **FX layer** — `particles.py` (pooled, capped ~128), `hitstop.py` (global freeze with input buffer protection), camera shake patch (trauma-squared).

### Critical Pitfalls

Twenty pitfalls cataloged in PITFALLS.md. The top five:

1. **Schema inversion load order / circular import trap** — `constants.py` currently imports cleanly; JSON parse at import time risks circular imports. Mitigation: dedicated `tuning.py` that loads lazily, `constants.py` becomes dumb PEP 562 shim importing only `json`+`pathlib`, smoke test `python -c "import src.core.constants"` in CI.
2. **Converter contract break (pml-to-ldtk)** — panel UX wants grouped/labeled/ranged values; that's a breaking reshape. Mitigation: version `physics-schema.json` (→ v0.3.0), keep `derived.*` + `placement_rules` stable, contract test loading the schema "as the converter sees it," update CONVERTER-HANDOFF.md in the same phase.
3. **Live-tuning panel mid-frame state corruption** — physics is stateful; slider writes mid-jump create discontinuities. Mitigation: double-buffer the tuning dict (`tuning_pending` → `tuning_live` atomic swap at frame boundary), snapshot values that must persist through a motion at state entry.
4. **Transition frame non-cancellable / input latency regression** — naive "play anticipation, then execute" adds 1+ frames of delay, regressing v1.3. Mitigation: physics on input frame, anticipation sprite ornamental; record v1.3 input-to-response baseline and regression-test.
5. **Fusion redesign breaks validated ability flows** — abilities are woven into player/damage/juice/collision. Mitigation: one-page "contract" per ability (ABL-01..06) BEFORE touching code, keep `fusion_legacy.py` behind flag during transition, regression playthrough suite.

Honorable mentions shaping roadmap decisions: float/int type coercion through JSON; squash/stretch modifying hit volumes (hitbox MUST stay constant); juice budget (NONE/SUBTLE/MEDIUM/BIG per event) to avoid juice-for-juice-sake; hitstop must keep input polling; feel tuning needs explicit testable exit criteria and timeboxes; save format versioning from day one; particle cap at ~128 with `pyxel.pset` over `pyxel.rect`.

## Implications for Roadmap

Research converges on a **13-phase sequence**. Phase 1 is non-negotiable and blocking; Phases 3–4 parallelize; Phases 6–7 parallelize; Phase 9 is gated on Phase 7 design doc lock.

### Phase 1: Tuning Foundation (Schema Inversion)
**Rationale:** Keystone — nothing downstream can live-tune until `physics-schema.json` is authoritative and the loader exists. The compat shim makes this non-breaking for the ~50 existing `from src.core.constants import X` call sites.
**Delivers:** Restructured `physics-schema.json` (nested `tuning.*` + `derived.*`), `src/core/tuning.py` with PEP 562 `__getattr__`, `constants.py` → dumb shim, `derive.py` recompute pass, `reload_if_changed()`, updated CONVERTER-HANDOFF.md, converter contract smoke test.
**Addresses:** Schema-as-SoT (P1 must-have).
**Avoids:** Pitfalls 1 (load order), 2 (type coercion), 3 (converter break), 4 (missing-value crash).
**Exit gate:** Game boots with schema-driven values identical to v1.3; converter smoke test passes.

### Phase 2: Call-Site Migration (constants → tuning)
**Rationale:** Mechanical refactor to make hot-reload actually work. Compat shim hides static imports; this phase moves the ~20 `src/entities/` files to read `tuning.X` at use site, not import site.
**Delivers:** `player.py`, `slime.py`, `projectile.py`, `enemies/*.py` read `tuning.*` each frame. No behavior change.
**Can partially overlap with Phase 3 and Phase 4.**

### Phase 3: Event Bus + Animation FSM Skeleton
**Rationale:** Architectural prerequisite for juice + fusion lifecycle.
**Delivers:** `src/anim/event_bus.py`, `state_machine.py`, `anim_clip.py`, `anim_player.py`, `player_anim.py` stub wired to Player's current IDLE/RUN/JUMP/FALL. Hardcoded `u = 16 + ...` in `player.py:790` replaced with `fsm.current_frame()`. No new content yet.
**Avoids:** Pitfall 9 (anim/gameplay desync — enforces "anim derives from game state"), Pitfall 11 (hitbox never touches visual transform).
**Parallel with Phase 4.**

### Phase 4: Diagnostic Overlays
**Rationale:** Visualizers must exist BEFORE input audit (Phase 6) and tuning panel validation (Phase 5). Without them, "feels off" is unfalsifiable.
**Delivers:** `src/debug/overlays.py` — hitbox wireframes, velocity vectors, input state glyphs, coyote/buffer timer bars, collision grid, frame-time graph, slime follow anchor. F2–F5 hotkeys.
**Avoids:** Pitfall 20 (overlays impacting measured feel — defines cost budget).
**Parallel with Phase 3.**

### Phase 5: Live-Tuning Panel MVP
**Rationale:** The milestone accelerator. Every subsequent feel phase benefits.
**Delivers:** `src/debug/panel.py`, `slider.py`, `category.py`, `presets.py`. F1 toggle, grouped sliders by system, mouse-driven, numeric entry fallback, reset-to-default, baseline diff indicator, autosave tuning journal. Presets: "v1.3 baseline" (locked/immutable), "tight", "floaty".
**Avoids:** Pitfalls 5 (mid-frame corruption — double-buffered dict), 6 (input bleed — `input_consumed_by_ui` flag), 7 (preset loss — autosave + versioning + immutable baseline), 8 (slider range — numeric entry + unlocked mode), 15 (A/B impossible — two-slot preset compare).
**Exit gate:** Panel driveable for 60s with arbitrary inputs, player position/velocity/state unchanged from initial (determinism test).

### Phase 6: Player Movement Feel Pass (Track A)
**Rationale:** First feel phase using the panel. Lowest-coupling system (no fusion, no slime AI), highest perceived impact.
**Delivers:** Tuned accel/friction, gravity/jump curves, variable jump, coyote, jump buffer, wall slide/jump, kick. Input responsiveness audit with input visualizer. **Written feel targets upfront** ("cross 4-tile gap, land 1 tile in"; "coyote 6 frames ok, 7 fail"). Cancel windows framework.
**Avoids:** Pitfall 10 (transition frame input latency), Pitfall 14 (no convergence — feel targets upfront, 1–1.5 week timebox).
**Parallel with Phase 7.**

### Phase 7: Fusion Lifecycle Design Doc (Design Only, No Code)
**Rationale:** PROJECT.md and user explicitly require a locked design doc BEFORE fusion re-implementation. Charge-to-fuse, V button, mana shield all open for reconsideration.
**Delivers:** `.planning/FUSION-DESIGN.md` defining initiate/sustain/end model, Kirby Mouthful analog decision, activation input model, windup duration schema, per-ability "contracts" (one page each for ABL-01..06). Acceptance checklist for Phase 9.
**Avoids:** Pitfall 12 (fusion redesign breaks validated abilities — contracts ARE the regression suite).
**Hard gate:** Phase 9 cannot start until this closes.
**Parallel with Phase 6.**

### Phase 8: Animation States + Transition Frames
**Rationale:** Builds content on Phase 3 FSM skeleton. Depends on sprite asset pipeline.
**Delivers:** Full player clips (idle, run, jump_anticipation, jump_rising, jump_apex, fall, land_recovery, wallslide, turn, drill_recoil). `assets/anim-schema.json`. Pre-baked squash/stretch sprite variants (not transform — Pyxel `blt` cannot scale).
**Avoids:** Pitfall 10 (physics-visual separation), Pitfall 11 (hitbox never transformed).
**Flag:** Sprite asset readiness potential blocker.

### Phase 9: Fusion Manager + Ability Protocol (Refactor, No Feel Changes)
**Rationale:** Largest code move in the milestone. Pure refactor — abilities behave identically to v1.3 after this phase. Prereq for Phase 10.
**Delivers:** `src/fusion/` package, `ChargeController` pre-manager. Old `player.py` fusion code stripped. `fusion_legacy.py` kept behind flag.
**Avoids:** Pitfall 12 (regression playthrough against Phase 7 contracts).
**Exit gate:** All ABL-01..06 contracts pass; regression playthrough green.

### Phase 10: Per-Ability Feel Pass (Track B)
**Rationale:** Feel tuning on top of Phase 9 refactor. Only meaningful after lifecycle exists as real phases.
**Delivers:** Drill/ram/hold/charge shot/bubble/boost each get windup/sustain/end tuning via panel. Per-ability identity (windup SFX, sustain loop, end SFX, particle color, distinct button map). Visible fusion indicators.

### Phase 11: Slime Follow / AI Pass
**Rationale:** Dual-hero means slime feel is half the identity. Isolated system, depends on tunable accel/friction (Phase 6).
**Delivers:** Tuned follow accel, max speed, catch-up threshold, stuck timeout, look-ahead distance, terrain reactions.

### Phase 12: Juice Polish (Shake + Hitstop + Particles + Audio)
**Rationale:** Final feel layer — hooks to Phase 3 events and Phase 9 fusion events. Cannot ship earlier without over-applying juice to things still changing.
**Delivers:** `src/fx/particles.py` (pooled, capped ~128), `src/fx/hitstop.py` (with input buffer protection), camera shake trauma-squared, impact flash, hit sound layering, **juice budget enumeration upfront** (NONE/SUBTLE/MEDIUM/BIG per event). Particle presets: `burst_dust`, `drill_impact`, `jump_dust`, `fuse_spark`, `death_explode`.
**Avoids:** Pitfalls 16 (juice budget first), 17 (hitstop keeps input polling), 18 (particle cap + pset over rect), 19 (sound channel map + debounce).

### Phase 13: Milestone Cap — Preset Bake + Regression Check
**Rationale:** Lock shipping tuning, verify no regressions, close milestone.
**Delivers:** Shipping preset committed, v1.3 regression playthrough green, save format versioning verified, CONVERTER-HANDOFF.md final, PROJECT.md evolved.
**Avoids:** Pitfall 13 (save format incompatibility), Pitfall 14 (no convergence — hard exit gate).

### Phase Ordering Rationale

- **Phase 1 is the absolute prerequisite.** Every subsequent phase consumes the tuning loader or compat shim.
- **Phase 2 is mechanical** and can partially overlap with Phases 3–4.
- **Phases 3 and 4 are independent** and both unblock Phase 5. Parallel.
- **Phase 5 is the milestone accelerator.** Every feel phase after uses it heavily.
- **Phases 6 and 7 parallelize.** Track A (movement) needs the panel + event bus. Phase 7 is design-only prose.
- **Phase 8 depends on Phase 3 skeleton + sprite assets** (flag blocker).
- **Phase 9 is gated on Phase 7 design doc lock.** Hard gate.
- **Phase 10 depends on Phase 9.** Cannot tune what doesn't yet exist as real phases.
- **Phases 11 and 12 land late** because they benefit from everything before.
- **Phase 13 is cap/ship** — no new features, lock and verify.

### Research Flags

**Needs deeper research during planning (`/gsd:research-phase`):**
- **Phase 1:** Verify actual pml-to-ldtk read path in CONVERTER-HANDOFF.md — does converter read `source_constants`, `derived.*`, or both? Answer shapes the restructure.
- **Phase 7:** Not an implementation phase — a research/design phase by nature. Deep reference work (Kirby Mouthful, Metroid stance, Ori Bash) to produce the locked doc.
- **Phase 8:** Pyxel `blt` destination-scale capability needs verification before committing to pre-baked vs procedural. Current recommendation (pre-baked) is MEDIUM confidence.
- **Phase 12:** Lightweight pass on particle budget and sound channel map — specific frame counts/intensities per event — to avoid "juice for juice's sake."

**Standard patterns (skip research-phase):**
- Phase 2 (mechanical migration), Phase 3 (canonical FSM), Phase 4 (trivial Pyxel primitives), Phase 5 (standard debug UI), Phase 6 (tuning), Phase 9 (refactor guided by Phase 7 contracts), Phase 10 (tuning), Phase 11 (tuning), Phase 13 (verification).

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | One-library verdict verified on PyPI. Build-custom rationale grounded in confirmed Pyxel API limitations (no widget/animation/particle systems, primitive-only draw). |
| Features | MEDIUM-HIGH | Table stakes + anti-features well-grounded in GMTK Toolkit, Celeste, Nijman, Swink. Fusion lifecycle analog (Kirby Mouthful) is closest but dual-hero dynamic is novel — Phase 7 must validate. |
| Architecture | HIGH | Patterns grounded in actual codebase inspection (`schema.py` singleton precedent, `player.py:790` current anim call site). PEP 562 stable since Python 3.7. One MEDIUM item: Pyxel `blt` destination scaling (pre-baked fallback viable). |
| Pitfalls | HIGH | 20 pitfalls cataloged with specific warning signs, phase assignments, mitigation patterns. Each maps to a known failure mode in the codebase or Pyxel platform. |

**Overall confidence: HIGH.**

### Gaps to Address (Surface During Requirements Gathering)

- **pml-to-ldtk converter read path** — does it read `source_constants` directly or only `derived.*` + `placement_rules`? Determines Phase 1 restructure detail.
- **Live panel interaction mode** — overlay (game running) vs paused vs both? Recommend both, pause default; confirm with user.
- **Fusion design fundamentals still open** — charge-to-fuse, V button mapping, mana shield pattern are explicitly flagged open by user. Phase 7 must lock these; roadmapper should NOT assume continuity from v1.3.
- **Sprite asset pipeline readiness** — Phase 8 depends on new spritesheet rows for transition frames. Is Aseprite → PNG pipeline ready for v2.0 additions?
- **Save format migration policy** — is breaking old saves acceptable or must v1.3 saves round-trip?
- **External playtester availability** — Pitfall 14 recommends blind A/B gate. If unavailable, tuning phases need alternative exit criteria.
- **Milestone timebox** — Pitfall 14 recommends 1–1.5 weeks per tuning phase. Does user have a hard deadline or is quality-over-time the rule?
- **Which P2 features are in-scope** — ~8 items; not all will fit. Requirements gathering should surface which are essential vs nice-to-have.

## Sources

### Primary (HIGH confidence)
- Pyxel 2.9.0 on PyPI; kitao/pyxel on GitHub
- watchdog 6.0.0 on PyPI
- Codebase inspection: `src/core/schema.py`, `src/entities/player.py:780-810`, `assets/physics-schema.json`, `.planning/PROJECT.md`, `.planning/STATE.md`
- GMTK Platformer Toolkit + Behind The Code devlog
- Celeste & Forgiveness (Maddy Thorson)
- Jan Willem Nijman — Art of Screenshake
- Art of Tiny Animations (Wayline)
- The Juice Problem (Wayline)
- SMW Central Tolerance Timer

### Secondary (MEDIUM confidence)
- pytransitions + python-statemachine (evaluated and rejected as overkill)
- Kirby Mouthful Mode (Fandom/WiKirby) — closest analog for fusion lifecycle
- Anatomy of Metroid Fusion
- Defold Animation State Machine example
- Research on Screen Shake and Hit Stop (Oreate AI) — 50–100ms hitstop
- Flynn Advanced Jump Mechanics (GameMaker)
- Hollow Knight ScreenShakeService (cautionary example)
