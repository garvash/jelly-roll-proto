# Phase 31: Animation Content + Particle Bank Separation - Context

**Gathered:** 2026-04-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Fill real animation content on top of the Phase 26 FSM skeleton:

1. **Transition clips** for jumping, landing, turning around, drilling, and entering fusion — procedural placeholders (new authored sprite frames, driver predicates, 1-tick holds, animation-only frame pauses, particle overlays).
2. **Particle bank separation** — bank 2 becomes the dedicated FX image bank; the inherited explosion sprite at bank 1 y=96 is retired.
3. **`assets/anim-schema.json`** — migrate Phase 26's hardcoded `PLAYER_CLIPS` to a JSON schema loaded via the tuning loader; duration values become live-tunable from Phase 28's slider panel.
4. **Hitbox-independence invariant** — unit-test enforcement that animation code never mutates `.w` / `.h`.

**Out of scope (other phases):**
- Slime/boss/enemy animation content — Phase 34 owns slime feel; boss/enemy polish is post-prototype.
- Fusion state machinery (FUSED latch emit, `drill_start` / `drill_block_break` / `drill_end` emits) — Phase 32 owns this. Phase 31 **subscribes** to these events, does not emit them.
- Juice polish layer (hitstop, camera shake, pooled-particle cap) — Phase 35.
- Per-ability feel tuning (drill spin timing, fuse-flash convergence duration, blob persistence) — Phase 33.

</domain>

<decisions>
## Implementation Decisions

### ANIM-04: Transition Encoding

- **D-01:** Jump split uses a driver predicate on horizontal velocity (Metroid-style). Extend `PlayerAnimDriver` with `vx_sign: int` (-1 / 0 / +1). Two clips: `jump_stationary` (vx_sign == 0) and `jump_running` (vx_sign != 0). Picked via two rules in `PLAYER_RULES`. No player.py branching; pure Reanimator extension.
- **D-02:** Land recovery = new 1-tick squash frame on `player.png`. Clip: `AnimClip(frames=[squash_u, idle_u], durations=[~4, 1], loop=False)`. Fires via driver predicate on the first N frames after `is_grounded` flips true, OR via the existing `land` event — planner's call.
- **D-03:** Turn-around = driver-edge detection + 1-tick skid frame. Extend driver with `prev_facing` diff detection; rule fires `turn_skid` clip for ~3 frames when `d.facing != d.prev_facing`. New skid sprite on `player.png`.
- **D-04:** Jump crouch = separate 1-2 tick anticipation clip (`jump_crouch`), `loop=False`. Fires on `jump_start` event OR first N frames of JUMPING, then jump_stationary/jump_running takes over.
- **D-05:** Drill spin = new **4-frame spin clip** for DIVING state (heroine rotating). Replaces Phase 26's single-frame drill placeholder. Clip loops by default.
- **D-06:** Drill recoil = **animation-only frame pause** on `drill_block_break` event. Pause drill spin's frame counter for ~3 frames each time a block breaks, then resume from the same frame. Gameplay keeps moving at `DRILL_SPEED`; only the sprite tick counter freezes. Requires a new `pause_for(n_frames)` mechanism in `AnimPlayer` (counter-freeze with tick budget). Distinct from Phase 35's gameplay hitstop.
- **D-07:** Fuse flash = Megaman-buster-charge aesthetic on `fuse_start` event (WINDUP→FUSED latch per FUSION-DESIGN):
  - **D-07a:** Spawn **16 sprite-backed particles** in a ring at radius R around the player; converge toward player center over **~12 frames (~0.2s @60fps)**.
  - **D-07b:** Circular **blob sprite grows from the convergence point** as particles arrive — blob does NOT pre-exist; it is born at impact. Placeholder authored in Phase 31 (hand-drawn frames OR procedural `pyxel.circ()`); real sprite supplied by user later.
  - **D-07c:** Blob remains as fused-form overlay after convergence completes; persistence/fade-out is Phase 33 tuning.

### ANIM-05: anim-schema.json + Panel Integration

- **D-08:** Schema shape = **nested by entity, then by clip**. Top-level keys are entity names (`player`); each entity has a `clips` dict keyed by `clip_id` with `frames`, `durations`, `loop`, `events` fields. Mirrors Phase 26's `PLAYER_CLIPS` dict shape — migration is a direct translation.
- **D-09:** Phase 31 schema scope = **player only**. Particle sprite refs live in code (Particle class reads bank-2 offsets). Slime and other entities stay on Phase 26 hardcoded / ad-hoc paths; Phase 34 migrates slime.
- **D-10:** Loader = `tuning.load_anim()` as a **second loader function with a separate namespace**. Entities access via `from src.core import tuning` then `tuning.anim.player.clips['run']`. Does NOT go through the flat PEP-562 namespace (reserved for physics scalars). Two load calls in `main.py`: physics at boot (existing), anim after.
- **D-11:** Panel integration = **durations only** as scalar log2-scale sliders in a new ANIM tab. Frame indices (lists) and event bindings stay JSON-editable; panel exposes a **"Reload anim schema"** button that re-runs `tuning.load_anim()` on click. Matches Phase 24's "no file watcher" precedent.
- **D-12:** Anim durations **join the existing preset dict**. Phase 28 preset slots (v1.3-baseline / v2.0-default / tight / floaty + autosave) now carry physics + anim durations in one package. v1.3-baseline gets anim durations invented from Phase 26 hardcoded PLAYER_CLIPS values (no v1.3 anim content existed).
- **D-13:** Seed values for initial `anim-schema.json` = **Phase 26 hardcoded PLAYER_CLIPS verbatim**. Idle/jump = 1-tick holds; run = 6-tick toggle. New Phase 31 clips get hand-picked placeholder durations (tuned in Phase 33).
- **D-14:** Error behavior = **fail fast at load with clear error**. `tuning.load_anim()` raises on missing clip_id referenced by rules, mismatched frames/durations lengths, or unknown fields. Bugs visible immediately, matches Phase 26 D-07 spirit.

### ANIM-06: Particle Bank + Particle Technique

- **D-15:** Particle image bank = **bank 2**. Banks 0 (tiles) and 1 (entities + current FX) stay untouched. New asset `assets/sprites/particles.png` loaded via the existing `SPRITE_MANIFEST` pattern in `main.py`.
- **D-16:** **Retire the inherited explosion sprite** (bank 1 y=96). On-block-break triggers a **diverging particle burst** — mirror of the fuse-flash converging ring: spawn ~12-16 sprite-backed particles radially outward from the break point with short lifetime. `Effect` class stripped to a particle-spawner role (or retired entirely; call sites migrate to `spawn_particle_burst(x, y, type="block_break")`). Bank 1 y=96 slot reclaimed.
- **D-17:** All particles are **sprite-backed from bank 2**. Current random-color `pyxel.pset`-based `Particle` class is retired; call sites migrate to sprite-backed. Unified visual language across fuse-flash convergence, block-break burst, and future Phase 35 impact particles.
- **D-18:** **Pooling deferred to Phase 35**. Phase 31 keeps existing list-append `Particle` spawning + per-frame active-filter. Phase 35 explicitly owns the 128-cap pool architecture per ROADMAP.
- **D-19:** Bank 2 strip layout is **planner discretion** — at minimum houses the convergence/burst particle sprite(s) + fused_blob growth frames. Pyxel cannot procedurally scale (STATE.md + FUSION-DESIGN); fused_blob growth means multiple authored frames at progressive sizes. Strip organization follows bank 1's Y-offset convention.

### ANIM-07: Hitbox-Independence Test

- **D-20:** Test mechanism = **unit test driving Player through every clip, asserting `w`/`h` unchanged**. `tests/test_anim_hitbox.py` instantiates a Player, snapshots `(w, h)` at init, iterates driver combinations, calls `current_frame_u()` + advances frames, asserts `(w, h)` invariant. Chosen over grep-based static check (too lexical) and runtime wrapper (hot-path cost).
- **D-21:** Test scope = **player only**. Matches Phase 31 implementation scope. Particles/effects don't have `(w, h)` collision boxes in the same sense.
- **D-22:** **Hard gate** — runs in the default pytest invocation. A breach means animation has started mutating physics, which is the architecture's worst failure mode. Non-negotiable at commit time.
- **D-23:** Coverage = **state × vx_sign × vy_sign matrix**. Cartesian product of ~6 states (IDLE, RUNNING, JUMPING, FALLING, DIVING, DEAD) × 3 vx_sign × 3 vy_sign = ~54 combos + facing flip. Catches every combined-predicate rule after Phase 31 adds vx_sign-based jump split.

### Claude's Discretion

- Exact Y-offsets and strip heights on `assets/sprites/particles.png` (bank 2 layout)
- Fused_blob growth-frame count (3-6 frames likely)
- Placeholder blob rendering technique (authored sprite vs. `pyxel.circ()` procedural until real art arrives)
- Whether `Effect` class is entirely retired or stripped to a spawner shell
- Driver predicate vs. event listener choice per transition where both are viable (land recovery: `land` event OR `is_grounded` edge detection; fuse flash is event-only since it's an instantaneous latch)
- Panel tab naming and slider grouping for anim durations
- Test file organization (`test_anim_hitbox.py` vs. extending existing `test_anim.py`)
- `AnimPlayer.pause_for(n)` API shape (method vs. field assignment)
- Whether `Particle` class adopts tier-2 `AnimPlayer(clip)` wrapping or stays as a custom dx/dy/life class (both acceptable under Reanimator two-tier pattern)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & Architecture (read first)
- `.planning/ROADMAP.md` §Phase 31 — Goal, dependencies (Phase 26, Phase 24; implicitly Phase 28 for panel), four success criteria.
- `.planning/FUSION-DESIGN.md` §Fusion FSM event emissions — `fuse_start` (WINDUP→FUSED) is the authoritative "you are fused" moment and Phase 31's fuse-flash trigger. `drill_start` / `drill_block_break` / `drill_end` are Phase 32 emits; Phase 31 subscribes. **LOCKED at commit `9047b590`.**

### Prior Phase Context (carry-forward decisions)
- `.planning/phases/26-event-bus-animation-fsm-skeleton/26-CONTEXT.md` — Reanimator-style architecture: driver-based mirror (D-00), ordered rules first-match (D-04), events side-channel only (D-00b/D-13), clip change resets frame counter (D-07), clips loop by default (D-08), rules/clip table immutable post-construction (D-10), `PlayerAnimDriver` has state/is_grounded/facing/vy_sign (D-01 — Phase 31 extends with `vx_sign` and `prev_facing`). `anim-schema.json` holds CLIP DATA only; picker rules stay in Python (D-05).
- `.planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md` — Tuning loader pattern, no file watcher, panel is the editing path. Phase 31's `tuning.load_anim()` follows the same pattern as a sibling loader with its own namespace.
- `.planning/phases/28-live-tuning-panel-mvp/` — Panel UI conventions (log2 sliders, preset slots, baseline diff, autosave). Phase 31's ANIM tab follows the same conventions.

### Code To Read Before Touching
- `src/anim/player_anim.py` — Phase 26's `PLAYER_CLIPS` dict + `PLAYER_RULES` list + `PlayerAnimDriver`. Phase 31 migrates clip data to `anim-schema.json`; extends driver with `vx_sign` and `prev_facing`; adds rules for Metroid jump split, turn_skid, jump_crouch, land_squash.
- `src/anim/anim_clip.py` — `AnimClip` dataclass with reserved `events` dict slot. Phase 31 wires event-binding dispatch (fire named events at specific frame indices).
- `src/anim/anim_player.py` — Phase 26 frame ticker. Phase 31 adds **pause/hold** mechanism for D-06 drill recoil (freeze tick counter for N frames on command).
- `src/anim/state_machine.py` — Picker class (`AnimFSM`). Phase 31 adds new rules only; class surface unchanged.
- `src/entities/player.py` — `_update_anim_driver()` (extend with vx_sign, prev_facing); `jump_start` / `land` emit sites; `draw()` still calls `self._anim.current_frame_u()`.
- `src/entities/effects.py` — `Effect` class (retired/stripped) and `Particle` class (migrated to sprite-backed from bank 2). Call sites of `game.spawn_explosion` migrate to `spawn_particle_burst`.
- `main.py` §SPRITE_MANIFEST + `_load_sprites()` — add bank 2 entry for particles; remove (or zero-fill) bank 1 y=96 effects entry; call `tuning.load_anim()` during init after `schema.init()`.
- `src/core/tuning.py` — extend with `load_anim()` creating `tuning.anim` namespace (nested by entity); fail-fast validation.
- `src/ui/tuning_panel.py` + `src/ui/presets.py` — Phase 28 panel + preset infrastructure. Phase 31 adds ANIM tab, "Reload anim schema" button, and threads anim durations through preset save/load.

### Asset & Schema Targets
- `assets/anim-schema.json` (NEW) — `{ "player": { "clips": { "idle": {...}, "run": {...}, ... } } }`. Seed from Phase 26 `PLAYER_CLIPS`.
- `assets/sprites/particles.png` (NEW) — Bank 2 sprite sheet. Houses convergence/burst particles + fused_blob growth frames.
- `assets/sprites/player.png` — Extend with new placeholder frames: `land_squash`, `turn_skid`, `jump_crouch`, `jump_stationary`, `jump_running`, `drill_spin` (4 frames).
- `assets/sprites/effects.png` — retired or zeroed at bank 1 y=96; slot reclaimed.

### Out-of-Scope Phase Dependencies (do NOT implement)
- Phase 32 — fusion manager refactor; owns `drill_start` / `drill_block_break` / `drill_end` emits. Phase 31 subscribes but does not emit.
- Phase 33 — per-ability feel pass; owns retuning drill spin timing, fuse-flash convergence duration, blob persistence. Phase 31 ships placeholders.
- Phase 35 — pooled-particle cap (~128), camera shake, gameplay hitstop, impact flash. Phase 31 keeps the existing non-pooled list-append Particle system.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`src/anim/*` (Phase 26)** — Full 5-file package: `event_bus.py`, `state_machine.py`, `anim_clip.py`, `anim_player.py`, `player_anim.py`. Phase 31 extends, does not rewrite.
- **`src/core/tuning.py` PEP-562 loader** — Phase 31 adds `load_anim()` as a parallel loader on the same module; separate namespace avoids polluting the flat physics scalar space.
- **`src/ui/tuning_panel.py` + `src/ui/presets.py`** — Phase 28 panel infrastructure. Phase 31 adds ANIM tab + reload button; threads anim durations through preset save/load.
- **`src/entities/effects.py` Particle class** — Current pset-based. Phase 31 rewrites the render path to sprite-backed (bank 2) but preserves the update/lifetime logic (dx, dy, gravity, life).
- **`main.py` SPRITE_MANIFEST + `_load_sprites()`** — Established pattern for registering PNG assets into image banks. Phase 31 adds a bank-2 entry; removes bank-1 y=96 effects entry.

### Established Patterns
- **Reanimator-style driver/picker separation (Phase 26 D-00, MEMORY)** — Load-bearing. Phase 31 extends the driver (`vx_sign`, `prev_facing`) and adds rules; never introduces `play("jump")` calls or event-driven animation correctness.
- **Event bus is side-channel only (Phase 26 D-00b)** — `fuse_start`, `jump_start`, `land`, `drill_block_break` drive non-animation consumers (Phase 27 overlays, Phase 35 juice, Phase 31's fuse-flash particle spawner). Animation correctness depends only on drivers.
- **"No magic numbers" (MEMORY feedback)** — Every numeric literal introduced in Phase 31 (squash duration, skid duration, convergence frame count, particle count, pause tick budget) needs a named constant. Co-located in `player_anim.py` constants section or in `anim-schema.json`.
- **`tuning.X` read at use site (Phase 25)** — Panel-driven live values stay live. Phase 31's anim durations follow the same pattern via `tuning.anim.player.clips['run'].durations[0]` read at draw time.

### Integration Points
- **`Player._update_anim_driver()`** — Extend with `vx_sign = sign(self.dx)` (or equivalent) and `prev_facing` diff mechanism. Only driver refresh changes; `current_frame_u()` call stays at `Player.draw()`.
- **Event emit sites in `Player`** — `jump_start` (already emitted in Phase 26), `land` (ground-contact block). Phase 31 subscribers: clip picker inputs + particle-burst spawners.
- **`main.py` init sequence** — After `schema.init()`, call `tuning.load_anim()`. Before `pyxel.run(...)`, wire the fuse-flash subscriber that spawns converging particles on `fuse_start`.

### Known Constraints
- **Pyxel `blt` cannot procedurally scale** (STATE.md). Fused_blob growth = multiple authored frames at progressive sizes, not a runtime scale transform.
- **Pyxel has 3 image banks at 256×256** — bank 2 is the only free slot; no room to fragment particles across additional banks.
- **Phase 26 frame-for-frame parity is NOT a Phase 31 acceptance bar.** Phase 31 intentionally changes visuals (new transitions + jump variants). Regression target is "every v1.3 interaction still looks at least as readable as v1.3, plus new transitions."
- **`AnimPlayer.pause_for(n)` is a net-new addition** (D-06). Phase 26's ticker has no concept of pause. Keep the mechanism small; do not let it bleed into gameplay timing.

### Event Wiring Map

| Event | Emitter | Phase 31 Subscriber | Purpose |
|-------|---------|---------------------|---------|
| `jump_start` | `Player.jump()` (Phase 26) | jump_crouch clip trigger | fire anticipation frame |
| `land` | `Player.update()` ground-contact (Phase 26) | land_squash clip trigger (+ optional dust burst) | squash frame |
| `fuse_start` | WINDUP→FUSED latch (Phase 32) | fuse-flash particle spawner + blob growth starter | Megaman charge |
| `drill_block_break` | drill `move_and_collide` (Phase 32) | diverging particle burst + drill spin frame pause | block-bite |
| `drill_start` / `drill_end` | drill entry/exit (Phase 32) | informational; drill spin clip start/stop driven by DIVING state predicate | redundant with state driver |

</code_context>

<specifics>
## Specific Ideas

- **Metroid stationary-vs-walking jump distinction** (user reference: Super Metroid — Samus hops straight up stationary, somersaults when running). Phase 31 implements this as a driver predicate on `vx_sign`, not a code-side branch. One flag in the driver, two rules, two clips — load-bearing template for how future animation variants get added.
- **"Make the frame pause briefly so it looks like the drill is eating into the blocks."** User phrasing for drill recoil. 4-frame spin is the base clip; `drill_block_break` freezes the frame counter ~3 ticks. This is a **visual** hitstop, not a **gameplay** hitstop — drill keeps moving at DRILL_SPEED; only the sprite tick pauses. Phase 35's gameplay hitstop is a separate juice layer on top.
- **"Megaman-style charge"** — user phrasing for fuse flash. 16 particles converge to player center; circular blob GROWS from the convergence point (not pre-existing). Blob sprite supplied by user later; Phase 31 ships placeholder (authored frames or procedural `pyxel.circ()`).
- **"The existing explosion feels very out of place and I didn't even make them."** User signaled discomfort with inherited placeholder art at bank 1 y=96. Phase 31 retires the sprite and replaces EXPLOSION effect type with a diverging particle burst — visually consistent with fuse flash (same particle system, reversed vectors). Bank 1 y=96 slot reclaimed.

</specifics>

<deferred>
## Deferred Ideas

- **Slime animation content** — Phase 34 (slime follow/AI feel pass) owns slime visuals and tier-1 AnimFSM adoption.
- **Effects tier-2 AnimPlayer adoption** — Phase 26 flagged this for Phase 31. Phase 31 instead retires the animated-sprite paradigm for effects (replaced with particles), so tier-2 adoption for static-frame entities (items, doors, save points) is deferred to future phases. `Particle` class itself may still be tier-2 at planner discretion.
- **Pooled particles (~128 cap)** — Phase 35.
- **Camera shake, gameplay hitstop, impact flash, sound channel map** — Phase 35.
- **Drill spin timing, fuse-flash convergence duration, blob persistence** — Phase 33 (per-ability feel pass).
- **`drill_start` / `drill_block_break` / `drill_end` emit sites** — Phase 32 (fusion manager refactor).
- **Fused_blob growth-frame authoring** — Placeholder acceptable in Phase 31; real sprite supplied by user later.
- **Fused-form overlay persistence duration** — Phase 33 tuning.
- **Runtime hitbox-independence wrapper** — Rejected for Phase 31 (chose unit-test path). Re-evaluate only if unit test misses regressions a runtime wrapper would catch.
- **Event-driven hitbox-independence coverage** — Rejected (chose driver-matrix coverage). Event axis may be added if state-matrix proves insufficient.
- **Panel editing for frame lists / event bindings** — Deferred. Phase 31 scopes live-editing to scalar durations; frame lists edited in JSON + "Reload" button.
- **F-key shortcut for anim reload** — Rejected (panel button only). Re-evaluate if iteration velocity suffers.
- **Migrating slime/items/projectile clips to anim-schema.json** — Deferred. Phase 31 schema covers player only.
- **Separate A/B anim preset slots** — Rejected. Anim durations join the existing Phase 28 preset dict.
- **Retiring the pset-based Particle paradigm entirely** — Phase 31 migrates existing pset call sites to sprite-backed. Random-color psets may be re-introduced as a future tier if a case genuinely prefers them (tiny debris, rain, etc.).

</deferred>

---

*Phase: 31-animation-content-particle-bank-separation*
*Context gathered: 2026-04-21*
