# Phase 26: Event Bus + Animation FSM Skeleton - Context

**Gathered:** 2026-04-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Stand up `src/anim/` with a pub-sub event bus and a generic animation decision class ("AnimFSM") wired to the player's current IDLE/RUNNING/JUMPING/FALLING/WALL_SLIDING/DIVING/RAMMING/DASHING/BOOSTING/CHARGING_SHOT/DEAD states. Replace the hardcoded sprite frame toggle in `src/entities/player.py` (`u = 16 + (pyxel.frame_count // 12 % 2) * 16`) with `u = self._anim.current_frame_u()`.

After this phase:
- `src/anim/` exists with the 5 files mandated by ANIM-01: `event_bus.py`, `state_machine.py`, `anim_clip.py`, `anim_player.py`, `player_anim.py`.
- Player visuals are **frame-for-frame identical to v1.3** — this is a refactor, not a content change. Same two frames per state, same 12-frame toggle cadence, same sprite sheet offsets.
- All 17 ANIM-02 events are emitted from gameplay code (player.py + slime.py) through a module-level event bus; a pytest-only debug subscriber captures them to prove firing.
- The architecture is Reanimator-style: animation is a downstream mirror of gameplay state via a driver dataclass, NOT a commanded target and NOT a classical transition-edge FSM. "FSM" in ANIM-01 is honored as "generic animation decision class" — internal implementation is a driver-predicate rules evaluator.

**Out of scope (other phases):**
- Phase 27 — diagnostic overlays (F2–F5) will subscribe to this bus; Phase 26 does not ship the overlays or any runtime debug subscriber.
- Phase 28 — live-tuning panel; anim timings are NOT yet live-tunable in Phase 26.
- Phase 30 — fusion lifecycle design doc; Phase 26 emits fusion events at their **current** ad-hoc call sites and accepts that Phase 30's doc may rename or re-scope some of them.
- Phase 31 — anim content + particle bank split; no transition frames, no `assets/anim-schema.json` loading, no particle bank separation, no hitbox-independence regression test in this phase.
- Phase 32 — fusion manager refactor; owns migration of fusion/ability event emit sites into `src/fusion/*`.
- Phase 33 / 34 / 35 — per-ability feel, slime feel, juice polish; downstream consumers of the bus but not wired in this phase.
- AnimFSM instances for slime, boss, enemies, effects, projectiles, items, doors, save points, stains — architecture supports them but no wiring in this phase.

</domain>

<decisions>
## Implementation Decisions

### Architecture Model (Reanimator-style drivers)

- **D-00 Animation is a downstream mirror, not a commanded target.** Gameplay code never calls `play("jump")`. Gameplay code updates a **driver** (a flat dataclass snapshot of relevant game state), and the animation layer re-reads the driver every frame to pick a clip. This is the load-bearing design choice; everything else follows from it. Reference pattern: Aarthificial's Reanimator (https://github.com/aarthificial/reanimation-demo), used in the Unity game Astortion.
- **D-00a "FSM" in ANIM-01 is a loose label.** The `AnimFSM` class is a generic animation decision class — it takes driver input and produces a clip selection. Internals are a rules-list evaluator (see D-04), NOT a classical `add_transition(A, B, on=event)` transition-edge graph. The class name stays for requirement traceability. Reviewer should not expect classical FSM API.
- **D-00b Events do not drive animation.** The event bus exists for **non-animation** consumers (Phase 27 overlays, Phase 33 sfx, Phase 35 juice/shake/hitstop, the pytest debug subscriber in D-13). Animation correctness depends only on drivers. A missed or duplicated event is a future juice/sfx bug, never a broken sprite.

### Driver Set & Container

- **D-01 Forward-looking v1 driver set.** The player's driver dataclass carries: `state: str`, `is_grounded: bool`, `facing: int` (−1 or +1 following player convention), `vy_sign: int` (−1 / 0 / +1). Minimum required for v1.3 parity is `state` alone; the extra three cost ~4 lines in `_update_anim_driver()` and spare Phase 31 from re-opening `player.py` when it adds jump-crouch / land-recovery / turn-around branching.
- **D-02 `@dataclass PlayerAnimDriver` lives in `player_anim.py`.** Each entity defines its own driver dataclass in its own `*_anim.py` file. The generic `AnimFSM` class in `state_machine.py` is driver-shape-agnostic — it duck-types the driver, and predicates in the rules list encode the shape knowledge. This keeps the 5-file layout (no extra `driver.py`) and keeps the generic class reusable across entities with different driver shapes.
- **D-03 `vy_sign` is computed at driver-update time.** `driver.vy_sign = -1 if player.vy < 0 else (1 if player.vy > 0 else 0)`. One line in `_update_anim_driver()`. The driver layer stays as pure discrete signals; raw physics numbers (`vy` as a float) do not leak into it.

### Clip Picker Structure

- **D-04 Ordered rules list.** The picker holds `rules: list[tuple[Callable[[Driver], bool], str]]`, walked in list order every frame, first match wins, returns the matching `clip_id`. This is the Reanimator override-node pattern in its minimal form. A flat `{state: clip}` dict is a degenerate case of this.
  - **Skeleton rules for player** (v1.3 parity): `[(lambda d: d.state == "RUNNING", "run"), (lambda d: d.state in ("JUMPING", "FALLING"), "jump"), (lambda d: d.state == "DEAD", "death"), ..., (lambda d: True, "idle")]`. Exact ordering is planner discretion as long as the resulting frame outputs match v1.3.
- **D-05 Predicates are Python lambdas (or named functions where clarity benefits).** Not a JSON-serializable DSL. Phase 31's `anim-schema.json` holds **clip data** (frame indices, durations, event bindings) — it does NOT hold picker rules. Rules stay in Python. This trades schema-level tunability of the picker for expressive power (Phase 31 needs `d.vy_sign < 0 and d.state == "JUMPING"`-style combined predicates that are ugly in any data format).
- **D-06 Fallback rule is `(lambda d: True, "idle")` at the tail of every entity's rules list.** Unknown/unhandled driver state renders the idle clip. No exception, no "keep last clip" drift, no runtime assertion. If an animation looks wrong, the idle fallback makes the bug visible immediately.
- **D-07 Clip change resets the frame counter to 0.** When `current_frame_u()` detects that the picker selected a different `clip_id` than last frame, `anim_player` resets its frame index to 0. Phase 31's one-shot transition clips (jump_crouch, land_recovery) need this. Matches the Reanimator default.
- **D-08 Clips loop by default.** `AnimClip(frames=[...], durations=[...])` loops unless constructed with `loop=False`. v1.3 RUN and IDLE both loop. Phase 31's transition frames will use `loop=False` for one-shots.
- **D-09 Phase 26 wires `player_anim.py` only.** The generic `AnimFSM`, `AnimClip`, `AnimPlayer` classes are built. Only the player instantiates them. Slime/boss/enemies/effects/projectiles/items/doors/save points stay on their current rendering path untouched.
- **D-10 Rules list + clip table are immutable after AnimFSM construction.** `AnimFSM(rules=..., clips=...)` at init time, read-only thereafter. No `fsm.add_rule()` API, no runtime hot-swap. Phase 28's live panel will tune **clip frame timings** via `anim-schema.json` (Phase 31), NOT picker rules. Immutable rules close off a whole class of hot-swap bugs and match the skeleton-only scope.

### Event Scope & Bus

- **D-11 All 17 ANIM-02 events are wired in this phase.** Full list: `direction_change, jump_start, jump_released, fall_start, land, wall_touch, wall_jump, drill_impact, fuse_start, fuse_end, ram_start, ram_impact, boost_tap, charge_shot_fire, spit, damaged, death`. Sixteen emit from `player.py` at their current ad-hoc transition sites; `spit` emits from `slime.py`. Fusion/ability emits (drill_impact, fuse_start, fuse_end, ram_start, ram_impact, boost_tap, charge_shot_fire) carry a short comment flagging Phase 32 re-homing — e.g. `# ANIM-02 emit; may move in Phase 32 per FUSION-DESIGN lock`.
- **D-12 Phase 32 owns migration of fusion/ability emit sites.** When Phase 32 rewrites the fusion code into `src/fusion/*`, its planner must re-emit the same event names from the new call sites. Phase 30's `FUSION-DESIGN.md` must preserve the event vocabulary or explicitly bless renames. This is recorded as a Phase 32 acceptance check: "fusion events from ANIM-02 still fire after the refactor, same names or blessed renames."
- **D-13 Debug subscriber is a pytest test.** `tests/test_event_bus.py` (planner-named) registers a capturing subscriber against the module-level bus, drives one frame (or a minimal sequence) of gameplay through known transitions for each of the 17 events, and asserts the expected events were emitted in the expected order. No runtime F-key subscriber, no print-to-stdout logger left in the game loop. Matches Phase 25's D-04c ethos ("no scaffolding that risks getting left in"). Phase 27 (diagnostic overlays) is the proper home for runtime event visibility if it's ever wanted.
- **D-13a Event bus is a module-level singleton.** `src/anim/event_bus.py` exposes a module-level bus (implementation detail — planner picks class-instance-module-global vs top-level `subscribe()`/`emit()` functions). No dependency injection through constructors. Every entity and every subscriber uses the same bus. Matches how `pyxel` itself works in this codebase. Tests reset the bus between cases via a pytest fixture.

### Driver Update Mechanics & Integration

- **D-14 Driver refresh is the last call in `player.update()`.** After all physics, state transitions, and flag flips have settled, `player.update()` calls `self._update_anim_driver()` as its final act before returning. The driver snapshot is the authoritative end-of-frame state. `player.draw()` then reads a consistent driver in the same frame.
- **D-15 Events emit inline at gameplay sites, separate from driver refresh.** `event_bus.emit("jump_start")` is called from inside `player.jump()` at the moment the jump actually executes. `event_bus.emit("land")` is called from inside the ground-contact resolution block. Driver refresh and event emission are parallel outputs of the same tick — neither derives from the other. This satisfies the ANIM-02 wording "emits from gameplay code" literally and keeps driver-diffing from becoming a dependency.
- **D-16 `PlayerAnimDriver` is a single instance, mutated in place.** `self._anim_driver = PlayerAnimDriver(...)` created once in `Player.__init__`. `_update_anim_driver()` mutates its fields. Zero per-frame dataclass allocations in the hot path. AnimFSM reads the same object every frame.
- **D-17 `player.draw()` calls `u = self._anim.current_frame_u()`.** Player holds `self._anim: AnimFSM` as instance state, constructed in `__init__` with its rules list and clip table. `current_frame_u()` is the single call that replaces the hardcoded `u = 16 + (pyxel.frame_count // 12 % 2) * 16` line. Under the hood: AnimFSM reads the driver → walks rules list → picks clip → advances/ticks `anim_player` → returns sprite `u` offset. The `facing_right` argument to `draw_sprite()` still comes from `self.facing_right` in player.py; the FSM does not flip sprites.

### Claude's Discretion

- **Exact file split within `src/anim/`** — the 5 files mandated by ANIM-01 are fixed, but responsibility shading between `state_machine.py` and `anim_player.py` (e.g., who owns the frame counter, who owns the clip-change detection) is planner's call. Clean factoring: `state_machine.py` is pure picker (rules → clip_id); `anim_player.py` is pure playback (clip_id → current frame with ticking); the `AnimFSM` class composes both or delegates.
- **Rules list literal form** — class member, module-level constant, builder function, or `@dataclass` of rules. All fine as long as D-10 (immutable after construction) holds.
- **Clip data location in skeleton** — hardcoded Python dict literal in `player_anim.py` is the expected approach. Phase 31 will migrate this to `assets/anim-schema.json` loaded via the Phase 24 tuning loader. Planner may use module-level constants or a builder function. Not JSON. Not tuning-loaded in Phase 26.
- **Predicate naming style** — pure lambdas (`lambda d: d.state == "RUNNING"`) or named functions (`def _is_running(d): return d.state == "RUNNING"`). Named is better when a predicate gets complex or warrants a unit test; lambdas are fine for the 3–4 trivial skeleton rules.
- **Test method names, fixture style, and how the debug subscriber test is structured** — planner may fold the event-bus test into a new `tests/test_event_bus.py` or into a broader `tests/test_anim.py`. Fixture for bus reset between tests is required.
- **Exact wording of the Phase 32 re-homing comment** on fusion emits — needs to be greppable and self-explanatory; planner picks the phrasing.
- **How the clip-change detection fires `on_enter` hooks** (if any) for clip events declared in `anim_clip.py` — ANIM-01 says `anim_clip.py` holds "clip data with frames/duration/events", but Phase 26 doesn't need per-clip events firing yet (Phase 31 does). Planner may stub the event-binding field on `AnimClip` without wiring the dispatch, or wire it minimally.
- **Error behavior when a rule references a `clip_id` missing from the clip table** — planner may raise at `AnimFSM` construction time (fail fast, loud) or at first lookup. Prefer construction-time validation.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & Roadmap (read first)
- `.planning/REQUIREMENTS.md` §Animation System — ANIM-01, ANIM-02, ANIM-03 are the acceptance anchors. Note that ANIM-04 through ANIM-07 are Phase 31 and explicitly out of scope for Phase 26.
- `.planning/ROADMAP.md` §Phase 26 — the three success criteria (package + 5 files + `fsm.current_frame()` replacing the hardcoded line; 17 events emitted + debug subscriber; v1.3 visual parity).

### Prior Phase Context (carry-forward decisions)
- `.planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md` — PEP 562 tuning loader. Relevant because Phase 31 will load `anim-schema.json` via the same loader; Phase 26 does NOT, but the planner should understand the pattern for forward compatibility.
- `.planning/phases/25-call-site-migration-constants-tuning/25-CONTEXT.md` — uniform `from src.core import tuning` import form (D-03). Any new file in `src/anim/` that reads tuned values uses this form. D-04c ("no scaffolding that risks getting left in") is the direct precedent for Phase 26's D-13 (pytest-only debug subscriber, no runtime F-key).

### Code To Read Before Touching
- `src/entities/player.py` — 822+ LOC. The line to replace is `u = 16 + (pyxel.frame_count // 12 % 2) * 16` in `draw()` (around line ~795 in current HEAD; grep for the string, line numbers drift). The ~11 state values that populate `driver.state`: `IDLE, RUNNING, JUMPING, FALLING, WALL_SLIDING, DIVING, RAMMING, DASHING, BOOSTING, CHARGING_SHOT, DEAD`. Player attributes used by the driver: `self.state`, `self.facing_right` (convert to ±1 int), `self.is_grounded`, `self.vy`.
- `src/entities/slime.py` — 360 LOC. Only touched for the `spit` event emit at the shoot-spit call site.
- `src/core/tuning.py` — the PEP 562 loader. Read the module docstring. Phase 26 does NOT load anim values from tuning; only relevant for understanding why Phase 31 will.
- `assets/physics-schema.json` — reference for the tuning shape. Not modified in Phase 26.

### Reanimator Reference Pattern (architecture inspiration)
- https://github.com/aarthificial/reanimation-demo — the Unity reference this architecture derives from. Used in the game Astortion. Key idea: drivers over events, first-match rules list over transition edges. Phase 26 adopts the pattern, NOT the Unity-specific visual node editor.

### Out-of-Scope Phase Dependencies (do NOT implement, but know they're coming)
- Phase 27 — diagnostic overlays; future subscriber of this bus
- Phase 30 — `FUSION-DESIGN.md` lock; must preserve event vocabulary from D-11 or explicitly bless renames
- Phase 31 — `assets/anim-schema.json` + transition content + particle bank split + hitbox-independence regression test (ANIM-04 through ANIM-07)
- Phase 32 — fusion manager refactor; owns migration of fusion/ability emit sites per D-12
- Phase 33, 34, 35 — per-ability feel, slime feel, juice polish; downstream consumers

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`pyxel.frame_count`** — global monotonic tick counter; `anim_player` can use it for clip frame advancement timing, or maintain its own per-clip counter (planner's call, D-07 says reset-on-change either way).
- **`tuning` module** — already imported across all 12 hot-path files (Phase 25). Phase 26 may read it from `src/anim/*` if anim timings ever want to be tuning-sourced in this phase (they shouldn't be — that's Phase 31's `anim-schema.json`).
- **`player.state` / `player.facing_right` / `player.is_grounded` / `player.vy`** — already exist, already updated every frame by existing physics code. The driver refresh is a pure read-side snapshot; no new player attributes needed.
- **pytest fixture patterns** — Phase 24's `tests/test_tuning.py` and Phase 25's `tests/test_tuning_livereach.py` establish the pattern for pytest fixtures that reset module-level state between tests. The event-bus test (D-13) mirrors this for bus reset.

### Established Patterns
- **Absolute imports** — `from src.core import tuning`, `from src.anim import event_bus` (or equivalent). No relative imports.
- **One import block at top of file** — new files in `src/anim/` follow the same convention.
- **Per-frame `update()` + `draw()` entity pattern** — player.update() is where driver refresh happens (D-14); player.draw() is where the sprite lookup happens (D-17). No new hot-path conventions introduced.
- **Greenfield package** — no existing `src/anim/`, no existing event bus, no existing `events.py` anywhere in the repo. The scout confirmed this. Phase 26 is pure additive code + one line modification in each of player.py and slime.py (plus scattered event emit sites).

### Integration Points
- **`Player.__init__`** — constructs `self._anim_driver` (D-16) and `self._anim: AnimFSM` (D-17). These are the only two new instance attributes on Player.
- **`Player.update()` end** — final call `self._update_anim_driver()` before return (D-14).
- **`Player.draw()` sprite lookup line** — `u = self._anim.current_frame_u()` replaces the hardcoded toggle (D-17).
- **Scattered player.py state-transition sites** — `event_bus.emit(...)` calls added inline at each transition (D-15). ~16 sites in player.py, 1 site in slime.py.
- **Module import order** — no ordering constraint introduced. `src/anim/event_bus.py` loads on first `from src.anim import event_bus`; state is empty until subscribers register. Player's AnimFSM construction happens at `Player.__init__` time, which is after the package has loaded.

### Two-Tier Extensibility (for future phases, informational only)
The `src/anim/` architecture deliberately supports two usage tiers without extra work in Phase 26:
- **Tier 1 (full stack: driver + picker rules + clip player)** — for state-driven entities with multiple clips and real transitions. Player uses tier 1 in Phase 26. Slime, boss, Snail, Bat fit tier 1 when their respective feel phases land (Phase 34 for slime; enemy polish is currently backlog).
- **Tier 2 (clip player only, skip the FSM)** — for entities with one or two clips and no real picker decision: effects, projectiles, items, save points, doors, stains. These can instantiate `AnimPlayer(clip)` directly from `anim_player.py` without a `AnimFSM` wrapper. Most are Phase 31 (effects) or future phases.
This factoring is a discipline note, not a requirement — the 5-file ANIM-01 layout already separates `anim_clip.py` + `anim_player.py` from `state_machine.py`, so tier 2 is naturally supported. Downstream phases pick their tier.

### Known Constraints
- **Frame-for-frame v1.3 parity is the acceptance bar.** The skeleton rules for player must collapse to the same sprite output as the hardcoded toggle. Any visual drift is a bug. The manual regression playthrough (inherited pattern from Phase 25) catches it.
- **Pyxel `blt` cannot procedurally scale sprites** — not a Phase 26 concern (no new content) but relevant for Phase 31's squash/stretch via frame swaps.
- **Single-threaded Pyxel game loop** — the event bus does not need thread safety. Synchronous `emit()` that walks the subscriber list inline is fine.
- **player.py is still under ~800 LOC and already hot** — Phase 26 adds ~30–50 lines net (driver dataclass import, instance attrs, `_update_anim_driver()` method, ~16 emit calls, draw line change). Planner should avoid any broader refactor; this phase stays focused.

</code_context>

<specifics>
## Specific Ideas

- **User reference: Aarthificial's Reanimator (Unity).** "I was looking into making something like reanimator: https://github.com/aarthificial/reanimation-demo." This is the load-bearing pattern for the phase — before the user mentioned it, the gray-area framing was classical mirror-FSM vs event-driven-FSM, both of which are worse fits. Reanimator's driver-based model flipped the default.
- **"Animation is a downstream mirror of gameplay state, not a commanded target."** This phrasing captures the pattern in one line. Gameplay code writes drivers; animation reads drivers; events are a side channel for non-animation consumers only. Use this sentence as the reviewer test: if a proposed change makes animation read events or makes gameplay call `play("jump")`, it violates the architecture.
- **v1.3 visual parity is trivial under Reanimator.** The skeleton rules list collapses to 1:1 `state → clip`, which produces identical sprite output to the hardcoded toggle. The architecture pays off starting in Phase 31 when branching rules slot in without touching player.py.
- **"FSM" compatibility note.** The user confirmed the class name `AnimFSM` can stay even though internals are a rules evaluator. This is a naming compromise for requirement traceability, not a design compromise. Planner and researcher should not see the name and assume classical FSM semantics.
- **Expandability to other entities was the user's gating concern.** Confirmed: every entity can eventually use tier 1 or tier 2 depending on animation complexity. Phase 26 wires only the player (D-09). This is recorded in the code-context section for downstream awareness.

</specifics>

<deferred>
## Deferred Ideas

- **Slime/boss/enemy AnimFSM instances** — architecture supports them (tier 1); wiring is Phase 34 (slime) and future enemy/boss polish phases.
- **Effects/projectiles/items/doors/save points/stains clip-player adoption** — architecture supports them (tier 2); wiring is Phase 31 (effects) and future phases.
- **`assets/anim-schema.json` loading via tuning loader** — Phase 31 (ANIM-05). Phase 26 keeps clip data as hardcoded Python.
- **Transition frame clips** (jump_crouch, land_recovery, turn-around, drill_recoil, fuse_flash) — Phase 31 (ANIM-04).
- **Particle image bank separation from map tileset** — Phase 31 (ANIM-06).
- **Hitbox-independence regression test** (assert animation state read never mutates `.w`/`.h`) — Phase 31 (ANIM-07).
- **Runtime F-key debug subscriber** — rejected for Phase 26 (D-13). Phase 27 diagnostic overlays is the proper home if ever wanted.
- **Live-tunable anim timings via Phase 28 panel** — out of scope for Phase 26; becomes possible once Phase 31 loads `anim-schema.json` through the tuning loader.
- **Driver-diff derived events** (e.g., `is_grounded` flipping true → synthesize `land` event) — rejected (D-15). Events emit at gameplay sites, decoupled from driver refresh.
- **Classical FSM transition edges** (`add_transition(A, B, on=event)`) — rejected (D-00a/D-04). Driver predicates are the model.
- **Mutable rules list / hot-swap at runtime** — rejected (D-10). Rules are immutable after AnimFSM construction.
- **Per-clip `reset_on_enter` flag** — rejected (D-07). Clip change always resets frame counter to 0.
- **Injected event bus (passed through constructors)** — rejected (D-13a). Module-level singleton matches Pyxel patterns and avoids constructor churn on ~8 entity classes.
- **Separate `src/anim/driver.py` file** — rejected (D-02). Each entity's driver dataclass lives in its own `*_anim.py` (player's in `player_anim.py`). Preserves the 5-file ANIM-01 layout.
- **Opt-in loop flag (`loop=True` explicit)** — rejected (D-08). Loop is the default; one-shots set `loop=False`.
- **Pre-factored separate unit test for tier-2 clip player in Phase 26** — deferred. Phase 26's test exercises the full player stack (tier 1). Tier 2 gets its own test when Phase 31 wires the first tier-2 entity.

</deferred>

---

*Phase: 26-event-bus-animation-fsm-skeleton*
*Context gathered: 2026-04-12*
