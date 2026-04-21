# Phase 31: Animation Content + Particle Bank Separation - Research

**Researched:** 2026-04-21
**Domain:** Animation content authoring, schema-driven clip data, pyxel image-bank layout, hitbox-independence invariant
**Confidence:** HIGH

## Summary

Phase 31 is a **content + plumbing phase** on top of a solid Phase 26 skeleton. The Reanimator-style architecture (`PlayerAnimDriver` + `PLAYER_RULES` + `AnimFSM` + `AnimPlayer` + `event_bus`) is already in place and tested by `tests/test_anim.py`. No architectural revision is required. Phase 31 extends three existing surfaces and adds one new asset pair:

1. **`src/anim/player_anim.py`** — add two driver fields (`vx_sign`, `prev_facing`), add six new clips (or migrate all clips to `anim-schema.json`), reorder `PLAYER_RULES` so specific predicates beat generic ones.
2. **`src/anim/anim_player.py`** — add a `pause_for(n)` method that stalls `_clip_ticks` advancement for N frames (D-06).
3. **`src/core/tuning.py`** — add a parallel `load_anim()` loader producing a nested `tuning.anim` namespace that does NOT collide with the existing flat PEP-562 physics scalars.
4. **`assets/anim-schema.json` + `assets/sprites/particles.png`** — new files; bank-2 sprites replace `pset` rendering, and bank-1 y=96 explosion slot is reclaimed.

**Primary recommendation:** Plan six plans in this order: (1) extend `PlayerAnimDriver` + add placeholder frames on `player.png`, (2) add `AnimPlayer.pause_for(n)`, (3) author `anim-schema.json` + `tuning.load_anim()` + panel ANIM tab, (4) create `particles.png` bank-2 layout + migrate `Particle` to sprite-backed, (5) wire `fuse_start` / `drill_block_break` subscribers in `main.py`, (6) write `tests/test_anim_hitbox.py` as the ANIM-07 hard gate. All six plans share the same `PlayerAnimDriver` extension, so plan 1 is a blocking prerequisite; plans 2–5 can run in parallel after 1; plan 6 must run last.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**ANIM-04: Transition Encoding**
- **D-01:** Metroid jump split uses driver predicate on horizontal velocity. Extend `PlayerAnimDriver` with `vx_sign: int` (-1/0/+1). Two clips: `jump_stationary` (vx_sign == 0) and `jump_running` (vx_sign != 0). Picked via two rules in `PLAYER_RULES`. No player.py branching; pure Reanimator extension.
- **D-02:** Land recovery = 1-tick squash frame on `player.png`. Clip: `AnimClip(frames=[squash_u, idle_u], durations=[~4, 1], loop=False)`. Fires via driver predicate on first N frames after `is_grounded` flips true, OR via existing `land` event — planner's call.
- **D-03:** Turn-around = driver-edge detection + 1-tick skid frame. Extend driver with `prev_facing` diff detection; rule fires `turn_skid` clip for ~3 frames when `d.facing != d.prev_facing`. New skid sprite on `player.png`.
- **D-04:** Jump crouch = separate 1-2 tick anticipation clip (`jump_crouch`), `loop=False`. Fires on `jump_start` event OR first N frames of JUMPING.
- **D-05:** Drill spin = new 4-frame spin clip for DIVING state. Replaces Phase 26's single-frame drill placeholder. Loops.
- **D-06:** Drill recoil = animation-only frame pause on `drill_block_break` event. Pause drill spin frame counter for ~3 frames each time a block breaks. Requires new `pause_for(n_frames)` mechanism in `AnimPlayer`.
- **D-07:** Fuse flash = Megaman charge aesthetic on `fuse_start` event:
  - **D-07a:** Spawn 16 sprite-backed particles in ring at radius R around player; converge toward player center over ~12 frames (~0.2s @60fps).
  - **D-07b:** Circular blob sprite grows from convergence point as particles arrive. Blob does NOT pre-exist; born at impact. Placeholder via authored frames OR procedural `pyxel.circ()`.
  - **D-07c:** Blob remains as fused-form overlay after convergence. Persistence/fade-out is Phase 33.

**ANIM-05: anim-schema.json + Panel Integration**
- **D-08:** Schema shape = nested by entity, then by clip: `{ "player": { "clips": { "idle": {...}, ... } } }`. Mirrors Phase 26 PLAYER_CLIPS dict shape.
- **D-09:** Phase 31 schema scope = player only. Particle sprite refs live in code. Slime migrates in Phase 34.
- **D-10:** Loader = `tuning.load_anim()` as a second loader function with separate namespace. Access via `tuning.anim.player.clips['run']`. Does NOT go through flat PEP-562.
- **D-11:** Panel integration = durations only as scalar log2-scale sliders in new ANIM tab. Frame indices + event bindings stay JSON-editable. Panel exposes "Reload anim schema" button.
- **D-12:** Anim durations join existing Phase 28 preset dict. v1.3-baseline gets anim durations invented from Phase 26 hardcoded PLAYER_CLIPS values.
- **D-13:** Seed values = Phase 26 hardcoded PLAYER_CLIPS verbatim. New Phase 31 clips get hand-picked placeholder durations.
- **D-14:** Error behavior = fail fast at load. `tuning.load_anim()` raises on missing clip_id referenced by rules, frame/duration length mismatch, or unknown fields.

**ANIM-06: Particle Bank + Particle Technique**
- **D-15:** Bank 2 + new `assets/sprites/particles.png` loaded via existing `SPRITE_MANIFEST` pattern.
- **D-16:** Retire inherited explosion sprite (bank 1 y=96). Block-break triggers diverging particle burst — spawn ~12-16 sprite-backed particles radially outward. `Effect` class stripped to particle-spawner role or retired. Bank 1 y=96 slot reclaimed.
- **D-17:** All particles sprite-backed from bank 2. Current `pyxel.pset`-based `Particle` retires. Unified visual language.
- **D-18:** Pooling DEFERRED to Phase 35. Keep list-append spawning.
- **D-19:** Bank 2 strip layout = planner discretion. At minimum: convergence/burst particle + fused_blob growth frames. Pyxel cannot procedurally scale; fused_blob growth = multiple authored frames at progressive sizes.

**ANIM-07: Hitbox-Independence Test**
- **D-20:** Unit test driving Player through every clip, asserting (w, h) unchanged. `tests/test_anim_hitbox.py`.
- **D-21:** Player-only scope.
- **D-22:** Hard gate in default pytest invocation. Breach blocks commits.
- **D-23:** Coverage = state × vx_sign × vy_sign matrix. ~6 states × 3 vx_sign × 3 vy_sign = ~54 combos + facing flip.

### Claude's Discretion

- Exact Y-offsets and strip heights on `assets/sprites/particles.png`
- Fused_blob growth-frame count (3-6 likely)
- Placeholder blob technique (authored sprite vs. `pyxel.circ()`)
- Whether `Effect` class is retired entirely or stripped to spawner shell
- Driver predicate vs. event listener per transition where both viable
- Panel tab naming and slider grouping
- Test file organization (`test_anim_hitbox.py` vs. extending `test_anim.py`)
- `AnimPlayer.pause_for(n)` API shape (method vs. field)
- Whether `Particle` adopts tier-2 `AnimPlayer(clip)` wrapping or stays custom dx/dy/life

### Deferred Ideas (OUT OF SCOPE)

- Slime animation content (Phase 34)
- Fusion manager refactor emits (Phase 32 owns drill_start/drill_block_break/drill_end emit sites — Phase 31 only subscribes)
- Juice polish / pooled particles / camera shake / hitstop (Phase 35)
- Per-ability feel retuning (Phase 33)
- Fused-form overlay persistence duration (Phase 33)
- Runtime hitbox-independence wrapper (rejected)
- Event-driven hitbox-independence coverage (rejected)
- Panel editing for frame lists / event bindings (deferred)
- F-key shortcut for anim reload (rejected)
- Migrating slime/items/projectile clips to anim-schema.json (deferred)
- Separate A/B anim preset slots (rejected)
- Fused_blob real sprite authoring (user supplies later)

</user_constraints>

<phase_requirements>
## Phase Requirements

**Note:** `.planning/REQUIREMENTS.md` does not exist as a separate file in this project. Requirement IDs `ANIM-04` through `ANIM-07` are defined inline in `.planning/ROADMAP.md` §Phase 31 Success Criteria and elaborated in Phase 26 context carry-forward. The mapping below traces each ID to its research support.

| ID | Description | Research Support |
|----|-------------|------------------|
| ANIM-04 | Transition frames for jump/land/turn/drill/fuse, FSM-driven, tunable from panel | §Extension paths for `src/anim/*`, §`AnimPlayer.pause_for(n)` design, §Procedural placeholder techniques |
| ANIM-05 | `anim-schema.json` loaded by `tuning.py`, durations live-editable via panel | §`tuning.load_anim()` implementation, §Panel ANIM tab integration |
| ANIM-06 | Particle sprites in dedicated bank separate from map tileset | §Particle bank 2 population, §`Effect` retirement |
| ANIM-07 | Automated regression test confirms anim state read never mutates `.w`/`.h` | §Hitbox-independence test architecture |

</phase_requirements>

## Project Constraints (from CLAUDE.md / MEMORY)

`./CLAUDE.md` does not exist in the repo root. Auto-memory from `~/.claude/projects/.../memory/MEMORY.md` imposes these constraints that affect Phase 31 planning:

- **Avoid magic numbers** — every numeric literal introduced in Phase 31 (squash duration, skid duration, convergence frame count = 12, particle count = 16, pause tick budget = 3, blob growth-frame count, ring radius) MUST be a named constant. Location options: co-located in `player_anim.py` constants section (preferred for driver-predicate thresholds), or in `anim-schema.json` (preferred for duration values that become panel-tunable).
- **Reanimator-style anim architecture** — driver mirrors gameplay state; events side-channel only. Never introduce `play("clip_name")` call sites. All clip picking goes through `PLAYER_RULES` first-match.
- **Worktree merges cause regressions** — if Phase 31 plans are executed across worktrees, instruct the user to push before spawning worktree agents, and always diff `src/anim/*` + `main.py` after merge.

## Architectural Responsibility Map

Phase 31 is a single-process Pyxel game. "Tiers" here map to architectural layers within the game loop rather than client/server split.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Gameplay state (position, velocity, state string) | Player entity | — | Already owned in `src/entities/player.py`. Phase 31 does NOT touch. |
| Animation state (which clip, which frame) | `src/anim/*` | — | Reanimator layer reads Player state via driver; returns a `u` offset. Phase 31 extends. |
| Event dispatch (side-channel signals) | `src/anim/event_bus.py` | — | Module-level pub-sub. Phase 31 adds two new subscribers (`fuse_start`, `drill_block_break`), does not touch emission. |
| Particle simulation (dx, dy, life) | `src/entities/effects.py` | — | Rewritten by Phase 31: same update loop, new sprite-backed render. |
| Particle/effect rendering | `src/entities/effects.py` draw methods | — | Replaces `pyxel.pset` with `draw_sprite` calls against bank 2. |
| Clip data (frames, durations, loop, events) | `assets/anim-schema.json` | `src/core/tuning.py` | NEW — JSON is the source of truth; tuning loader exposes it as a Python namespace. |
| Panel UI | `src/ui/panel.py` + `src/ui/widgets.py` | `src/ui/presets.py` | Adds ANIM tab, "Reload anim schema" button; presets.py extends to include anim durations. |
| Hitbox invariant enforcement | `tests/test_anim_hitbox.py` | `conftest.py` | Test-only artifact; not runtime. |
| Sprite asset bank 2 | `main.py` `SPRITE_MANIFEST` + `_load_sprites()` | — | Existing loader pattern extended with one entry. |

**Key tier rule:** The `src/anim/*` package reads driver fields only — it NEVER touches `player.w`, `player.h`, `player.x`, or `player.y` directly. This is the ANIM-07 invariant codified. Phase 31 extensions must preserve this.

## Standard Stack

**The project is on Pyxel.** No new third-party libraries are needed or recommended. All Phase 31 work happens inside the existing stack.

### Core (already installed; confirmed via imports)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pyxel | (project pinned) | Retro game engine — `pyxel.blt`, `pyxel.pset`, `pyxel.circ`, `pyxel.images[N].load()` | Only engine in the project; every FX path terminates in a Pyxel primitive. |
| Python stdlib `json` | stdlib | Load `anim-schema.json` | Already used by `src/core/tuning.py` and `src/core/schema.py`. |
| Python stdlib `dataclasses` | stdlib | `AnimClip`, `PlayerAnimDriver` | Already used. Slots-friendly. |
| pytest | (project pinned) | Test runner for ANIM-07 hard gate | Existing suite in `tests/`. |

### Supporting (no new deps)

| Path | Purpose | When to Use |
|------|---------|-------------|
| `src/core/sprite_utils.py::draw_sprite` | Bottom-center-anchored sprite draw with bank/u/v params | Particle rendering from bank 2; use this instead of raw `pyxel.blt` to preserve consistency. |
| `src/anim/event_bus.subscribe(name, cb)` | Register a frame-synchronous callback | Fuse-flash spawner, drill-recoil pause trigger. |
| `src/ui/widgets.Slider` | Log2-scale slider with baseline diff, autosave, reset | Anim duration sliders in ANIM tab — same widget, different key set. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom JSON-driven clip data in `tuning.anim` namespace | A dedicated `src/anim/schema.py` loader | User locked D-10 (tuning loader path) — panel integration stays free; separate module would duplicate reload plumbing. **Rejected.** |
| `pyxel.circ()` procedural fused_blob | Authored growth frames on `particles.png` | Pyxel cannot scale `blt` calls (STATE.md constraint). Procedural `circ` can scale radius but clashes with the bank-2 "all FX is sprite-backed" principle (D-17). **Planner discretion (D-19):** recommend authoring 3-5 progressive-radius frames on `particles.png` as default; keep `pyxel.circ` as fallback commented-out path if art authoring slips. |
| Test-driven hitbox invariant (D-20) | Static grep or runtime wrapper | User rejected both (CONTEXT D-20). Static grep misses indirect mutation; runtime wrapper adds hot-path cost. Unit test is the locked path. |

**Installation:** None. All work uses existing deps.

**Version verification:** Not applicable — no new packages.

## Architecture Patterns

### System Architecture Diagram

```
                    ┌──────────────────────────────────────────────┐
                    │  Pyxel frame (60 fps)                        │
                    │                                              │
                    │  Game.update()                               │
                    │     │                                        │
                    │     └─> Player.update()                      │
                    │          ├─> handle_input()                  │
                    │          │     └─> event_bus.emit(*)         │
                    │          │         (jump_start, fuse_start,  │
                    │          │          drill_block_break, ...)  │
                    │          │                                   │
                    │          ├─> move_and_collide()              │
                    │          │     └─> event_bus.emit("land")    │
                    │          │                                   │
                    │          └─> _update_anim_driver()  [LAST]   │
                    │                  │                           │
                    │                  │  mutates in place:        │
                    │                  │   state, is_grounded,     │
                    │                  │   facing, vy_sign,        │
                    │                  │   + NEW: vx_sign,         │
                    │                  │         prev_facing       │
                    │                  ▼                           │
                    │             PlayerAnimDriver                 │
                    │                                              │
                    │  Game.draw()                                 │
                    │     │                                        │
                    │     └─> Player.draw()                        │
                    │          └─> self._anim.current_frame_u(dr)  │
                    │                  │                           │
                    │                  └─> AnimFSM walks           │
                    │                      PLAYER_RULES (ordered)  │
                    │                      first-match wins        │
                    │                          │                   │
                    │                          └─> AnimPlayer      │
                    │                              .tick()         │
                    │                              (skipped if     │
                    │                              _pause_ticks>0) │
                    │                                              │
                    └──────────────────────────────────────────────┘

        ┌───────────────────────┐         ┌───────────────────────┐
        │ event_bus subscribers │         │ anim-schema.json      │
        │  (wired in main.py)   │         │  (loaded at boot      │
        │                       │         │   by tuning.load_anim)│
        │ "fuse_start" ─┬──> spawn 16 converging particles         │
        │              └──> start blob growth                      │
        │ "drill_block_break" ─> spawn 12-16 diverging particles   │
        │                   │                                       │
        │                   └──> player._anim._player.pause_for(3) │
        │                                                           │
        └───────────────────────┘         │                         │
                                          │  {"player": {           │
                                          │    "clips": {           │
        ┌───────────────────────┐         │      "idle": {...},     │
        │ Panel (F1)            │◄────────┤      "run": {...},      │
        │  ANIM tab             │         │      "jump_stationary": │
        │  sliders: durations[] │         │      "jump_running":... │
        │  button: Reload schema│         │      "turn_skid": ...   │
        └───────────────────────┘         │      "land_squash": ... │
                                          │      "jump_crouch": ... │
                                          │      "drill_spin": ...  │
                                          │    }                    │
                                          │  }}                     │
                                          └─────────────────────────┘
```

### Component Responsibilities

| File | Responsibility | Phase 31 Changes |
|------|---------------|------------------|
| `src/anim/player_anim.py` | Defines driver + clip table + rules + factory | Extend `PlayerAnimDriver` with `vx_sign`, `prev_facing`. Add ~6 new named-constant clip keys (IDs or remove in favor of JSON). Add ~6 new rules. |
| `src/anim/anim_clip.py` | Immutable clip dataclass | Unchanged (events slot already reserved). |
| `src/anim/anim_player.py` | Per-instance frame ticker | **Add `pause_for(n)` method** — stores `_pause_ticks: int`; `tick()` skips counter advance while `_pause_ticks > 0`, decrements each call. |
| `src/anim/state_machine.py` | Rules walker, first-match picker | Unchanged (construction-time validation already raises on missing clip_id). |
| `src/anim/event_bus.py` | Module-level pub-sub | Unchanged. |
| `src/anim/__init__.py` | Package marker | Optionally expose `load_clips_from_schema()` helper. |
| `src/entities/player.py` | Player gameplay logic | **`_update_anim_driver()`: add 2 lines** — `d.vx_sign = -1 if self.dx < 0 else (1 if self.dx > 0 else 0)`; `d.prev_facing` must snapshot BEFORE the new facing gets written back. Order matters (see §Pitfall 2). |
| `src/entities/effects.py` | Effect + Particle classes | **Particle.draw** rewritten to sprite-backed. **Effect** stripped to no-op shell OR deleted + call sites migrated. |
| `src/core/tuning.py` | Physics scalar loader | **Add `load_anim(path)` function** creating a separate `anim` sub-namespace object. Must NOT add anim keys to `_flat_index` (D-15 duplicate check would be harmless but D-10 wants isolation). |
| `src/ui/panel.py` | Panel overlay | **Add `"Anim"` tab** to `TAB_DEFS`. Add "Reload anim schema" button in panel chrome (distinct from Save button). |
| `src/ui/widgets.py` | Slider / BoolToggle / tab | Unchanged — reuse existing Slider for anim duration keys. May need a synthetic flat-key adapter for nested anim keys. |
| `src/ui/presets.py` | Preset save/load | **Extend `_feel_keys()` or add parallel `_anim_keys()`** so preset dict carries anim durations. v1.3-baseline (slot_1) gets anim durations invented from Phase 26 PLAYER_CLIPS. |
| `main.py` | Game bootstrap | **Add `tuning.load_anim()` after `schema.init()`**. **Add particles.png to SPRITE_MANIFEST** at bank 2. **Remove or zero-fill effects entry** at bank 1 y=96. **Wire fuse_start + drill_block_break subscribers** after Game instance constructed, before `pyxel.run`. **Retire `spawn_explosion`** or rewrite it to call the new particle spawner. |
| `tests/test_anim_hitbox.py` | NEW — hitbox invariant | Create test iterating state × vx_sign × vy_sign × facing matrix. |

### Recommended Project Structure (deltas only)

```
assets/
├── anim-schema.json          # NEW — player clip data
├── sprites/
│   ├── particles.png         # NEW — bank 2 sprites
│   ├── particles.json        # NEW (optional) — Aseprite sidecar for tag forward-compat
│   └── player.png            # EXTEND — add rows for squash, skid, jump_crouch,
│                             #         jump_stationary, jump_running, drill_spin (4 frames)
src/
├── anim/
│   └── (Phase 26 files extended in place, no new files)
└── ui/
    └── (panel.py + presets.py extended in place)
tests/
└── test_anim_hitbox.py       # NEW — ANIM-07 hard gate
```

### Pattern 1: Driver-Predicate Rule Addition (ANIM-04 D-01, D-03)

**What:** Add two scalar fields to the driver, walk ordered rules first-match.
**When to use:** Any new animation variant that depends on gameplay state (not events).
**Example:**
```python
# src/anim/player_anim.py — extension pattern

@dataclass(slots=True)
class PlayerAnimDriver:
    state: str = STATE_IDLE
    is_grounded: bool = True
    facing: int = 1
    vy_sign: int = 0
    # NEW (Phase 31):
    vx_sign: int = 0       # -1/0/+1 for Metroid jump split (D-01)
    prev_facing: int = 1   # facing one frame ago, for turn_skid edge (D-03)
    skid_ticks: int = 0    # countdown timer for turn_skid persistence (D-03)

# Rules reordered — specific before generic:
PLAYER_RULES: list[Rule] = [
    # 1. Turn skid — edge detection: facing changed AND still grounded + moving
    (lambda d: d.skid_ticks > 0, "turn_skid"),
    # 2. Metroid jump split — stationary vs running
    (lambda d: d.state == STATE_JUMPING and d.vx_sign == 0, "jump_stationary"),
    (lambda d: d.state == STATE_JUMPING and d.vx_sign != 0, "jump_running"),
    # 3. Drill spin
    (lambda d: d.state == "DIVING", "drill_spin"),
    # 4. Land squash — first few frames after is_grounded flips (see pattern 2)
    (lambda d: d.is_grounded and d.land_ticks > 0, "land_squash"),
    # 5. Existing rules
    (lambda d: d.state == STATE_RUNNING, "run"),
    (lambda d: d.state in (STATE_FALLING,), "jump"),  # fallback for falling
    (lambda d: True, "idle"),
]
```

### Pattern 2: Event-Triggered Transient Driver Counter (ANIM-04 D-02, D-04)

**What:** Short-lived one-shot clips can be modeled as **counter fields on the driver** that subscribe to events and decrement each frame. The rule fires while the counter is positive.
**Why:** Keeps the clip picker pure (reads driver only); keeps the event bus side-channel (event just sets a counter).
**Example:**
```python
# In Player._update_anim_driver (or via event subscription wired in __init__):

def _on_land(self, **kw):
    self._anim_driver.land_ticks = LAND_SQUASH_FRAMES  # e.g., 4

def _on_jump_start(self, **kw):
    self._anim_driver.crouch_ticks = JUMP_CROUCH_FRAMES  # e.g., 2

def _update_anim_driver(self):
    d = self._anim_driver
    d.state = self.state
    d.is_grounded = self.is_grounded
    d.prev_facing = d.facing   # snapshot BEFORE overwriting
    d.facing = 1 if self.facing_right else -1
    d.vy_sign = -1 if self.dy < 0 else (1 if self.dy > 0 else 0)
    d.vx_sign = -1 if self.dx < 0 else (1 if self.dx > 0 else 0)  # NEW
    # Skid edge detection
    if d.facing != d.prev_facing:
        d.skid_ticks = TURN_SKID_FRAMES  # e.g., 3
    # Tick down transient counters
    if d.skid_ticks > 0:  d.skid_ticks -= 1
    if d.land_ticks > 0:  d.land_ticks -= 1
    if d.crouch_ticks > 0: d.crouch_ticks -= 1
```
**Source:** Phase 26 `_update_anim_driver()` at `src/entities/player.py:847-858`, extended.

### Pattern 3: Animation-Only Frame Pause (ANIM-04 D-06)

**What:** `AnimPlayer.pause_for(n)` freezes `_clip_ticks` for N frames without touching `_frame_index`. Gameplay continues; only the sprite tick counter stalls.
**Design:** Add a `_pause_ticks: int = 0` field. In `tick()`, if `_pause_ticks > 0`, decrement and return early before advancing the frame counter.
**Composition with clip change:** When `set_clip()` is called, reset `_pause_ticks` to 0 (pause belongs to the outgoing clip; incoming clip starts fresh).
**Example:**
```python
# src/anim/anim_player.py — proposed extension

class AnimPlayer:
    def __init__(self, clip: AnimClip) -> None:
        self._clip = clip
        self._clip_ticks = 0
        self._frame_index = 0
        self._pause_ticks = 0  # NEW

    def set_clip(self, clip: AnimClip) -> None:
        self._clip = clip
        self._clip_ticks = 0
        self._frame_index = 0
        self._pause_ticks = 0  # NEW — pause doesn't survive clip change

    def pause_for(self, n: int) -> None:
        """Freeze the tick counter for n frames. Additive if already paused."""
        self._pause_ticks += n

    def tick(self) -> None:
        if self._pause_ticks > 0:
            self._pause_ticks -= 1
            return  # frame holds; no advance
        # existing tick() body unchanged
        if self._clip_ticks >= self._clip.durations[self._frame_index]:
            ...
```
**Access path from event subscriber:** `player._anim._player.pause_for(3)` — breaks encapsulation mildly. Preferred: expose a public method on `AnimFSM`: `AnimFSM.pause_for(n)` that forwards to its internal `_player`. Planner's call.
**Source:** Phase 26 `AnimPlayer.tick()` at `src/anim/anim_player.py:18-31`, with additive pause-counter pattern (standard game-feel technique — see also `game.stop_frames` at `src/entities/player.py:239` for gameplay hitstop, which is explicitly NOT what D-06 asks for).

### Pattern 4: Sprite-Backed Particle (ANIM-06)

**What:** Migrate `Particle.draw` from `pyxel.pset(x, y, color)` to `draw_sprite(x, y, w, h, 2, u, v, ...)`.
**When to use:** Every particle spawned in Phase 31 (convergence, burst, blob, recall trail dots).
**Example:**
```python
# src/entities/effects.py — rewritten Particle

class Particle:
    def __init__(self, x, y, *, dx, dy, life, bank_u, bank_v):
        self.x = x
        self.y = y
        self.dx = dx          # no longer random — caller computes direction
        self.dy = dy
        self.life = life
        self.bank_u = bank_u  # u offset in bank 2
        self.bank_v = bank_v
        self.is_active = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += PARTICLE_GRAVITY  # only if physics-affected
        self.life -= 1
        if self.life <= 0:
            self.is_active = False

    def draw(self, cam_x, cam_y):
        if not self.is_active:
            return
        if (self.x < cam_x or self.x > cam_x + tuning.VIEWPORT_W or
            self.y < cam_y or self.y > cam_y + tuning.VIEWPORT_H):
            return
        # Use draw_sprite for consistency with player/slime rendering
        draw_sprite(self.x, self.y, PARTICLE_SIZE, PARTICLE_SIZE,
                    2, self.bank_u, self.bank_v,
                    PARTICLE_SIZE, PARTICLE_SIZE, True)
```
**Source:** Existing `Particle` class at `src/entities/effects.py:35-62`; `draw_sprite` signature at `src/core/sprite_utils.py:7-39`.

### Anti-Patterns to Avoid

- **Hand-rolling a `play("clip_name")` call site in Player.** Breaks the Reanimator invariant (MEMORY constraint). Every clip change must come from `PLAYER_RULES`.
- **Reading `d.vx_sign` from `self.dx` at draw time.** Driver must be refreshed once per frame in `_update_anim_driver()`; downstream reads are snapshots. Violating this is how frame-ordering bugs creep in.
- **Mutating `self.w` or `self.h` from animation code.** This is the ANIM-07 invariant — the test explicitly guards it. Any "visual squash" must happen via sprite frame (with the collision box unchanged), NOT by shrinking `self.h`.
- **Using `pyxel.rect` instead of `pyxel.circ` for the blob placeholder.** The D-07b aesthetic is a circle. If authored frames aren't ready, `pyxel.circ(cx, cy, r, color)` is the documented fallback (Pyxel docs §Graphics). `pyxel.circb` = outline only; `pyxel.circ` = filled.
- **Wiring subscribers in `Game.__init__` before the Player exists.** `fuse_start` spawner needs `self.game.particles.append(...)` and reads player position — wire it AFTER `reset()` completes so `self.particles` and `self.player` exist. Subscribe then via closure or bound method.
- **Mixing `tuning.anim` namespace into the flat `_flat_index`.** D-10 wants isolation. If `load_anim` registers anim keys in `_flat_index`, D-15's duplicate-key guard could fire on unrelated physics keys, and the panel's current tab-building loop (`src/ui/panel.py:104-108`) would try to render anim durations as scalar physics sliders.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON load with validation | Custom parse + custom error types | `json.load()` + explicit `ValueError` raises (mirror `src/core/tuning.py:60-99` pattern) | Existing pattern proven across `schema.py`, `tuning.py`, `presets.py`. Fail-fast is the locked policy (D-14). |
| Log2-scale duration slider | Custom ANIM slider widget | Reuse `Slider` from `src/ui/widgets.py:108` | Already implements log2, baseline diff, autosave, keyboard edit, reset. Zero reason to fork. |
| Event subscription | Direct callback storage | `event_bus.subscribe(name, cb)` (`src/anim/event_bus.py:13`) | Module-level singleton; reset between tests via existing conftest fixture. |
| Sprite-bank image load | Custom `pyxel.image.load` loop | Extend `SPRITE_MANIFEST` dict + let `_load_sprites()` handle it | `main.py:144-154, 305-313` already handles path + bank + xy. One new entry. |
| Preset serialization | Second preset file for anim | Join existing `_feel_keys()` set (`src/ui/presets.py:16`) + extend `_feel_keys` to yield anim flat-keys too | D-12 locked this. One preset dict, two concerns. |
| Hitstop-style frame counter for D-06 drill pause | Ad-hoc field on Player | Generic `AnimPlayer.pause_for(n)` | Animation-only pause is a reusable anim primitive; Phase 35 may want similar for other effects. |
| Converging particle math | Random dx/dy like existing `Particle` | Compute per-particle vector: `dx = (target_x - start_x) / FRAMES_TO_CONVERGE; dy = ...` | 16 particles each need a unique angle around the ring. Use `math.cos/sin(angle * i)` — stdlib, no extra deps. |

**Key insight:** Phase 31 is almost entirely a **composition of existing primitives**. The only genuinely new primitive is `AnimPlayer.pause_for(n)`.

## Runtime State Inventory

Phase 31 is a **content + plumbing phase**. It does not rename, rebrand, or migrate persistent identifiers. Most categories are N/A.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None. Preset JSON files (`assets/presets/slot_N.json`) will gain new anim-duration keys when saved post-Phase-31. Existing presets remain loadable because `load_preset` (`src/ui/presets.py:58-62`) already wraps `set_value` in `try/except KeyError`, silently skipping unknown keys. | Document in SUMMARY that slot files saved AFTER Phase 31 carry anim durations; slot files saved BEFORE will lack them and fall through to JSON defaults. This is forward-compatible; no data migration needed. |
| Live service config | None — single-process Pyxel game. | — |
| OS-registered state | None. | — |
| Secrets/env vars | None. | — |
| Build artifacts | `assets/sprites/player.json` (Aseprite sidecar) — will become stale after new frames are added to `player.png`. Re-export from Aseprite required after art authoring to keep tag metadata in sync. NOTE: tags are forward-compat only, not consumed by draw methods today (`src/core/sprite_utils.py:42-65` docstring). | Re-export `player.json` after Aseprite authoring, but not blocking — engine ignores it today. |

## Common Pitfalls

### Pitfall 1: `prev_facing` snapshot ordering (D-03)
**What goes wrong:** If `d.prev_facing` is assigned **after** `d.facing` in `_update_anim_driver`, they are always equal and the turn_skid edge NEVER fires.
**Why it happens:** Reflex from Phase 26's current code assigns `d.facing` first.
**How to avoid:** Assign `d.prev_facing = d.facing` (copy OLD value) BEFORE overwriting `d.facing = 1 if self.facing_right else -1`.
**Warning signs:** Unit test: drive driver with `facing_right=True`, call `_update_anim_driver`, flip `facing_right=False`, call again, assert `d.prev_facing == 1 and d.facing == -1 and d.skid_ticks > 0`.

### Pitfall 2: Non-looping clip stickiness after state exit
**What goes wrong:** `jump_crouch` is `loop=False`. Phase 26's `AnimPlayer.tick()` (line 28-30) "holds on last frame" when a non-looping clip completes. If the rule that picked `jump_crouch` stops matching, `AnimFSM.current_frame_u` picks a different clip and triggers `set_clip` → reset. Good. But if the rule KEEPS matching because e.g., `crouch_ticks` isn't decremented, the clip holds on the last frame forever, silently. Player appears "stuck" in crouch pose.
**Why it happens:** Event sets `crouch_ticks = N`; if decrement is missed, rule keeps firing, clip stays bound, no visible issue except a frozen stance.
**How to avoid:** Every transient counter (`skid_ticks`, `land_ticks`, `crouch_ticks`) MUST be decremented every frame in `_update_anim_driver` — belt-and-suspenders. Add a unit test: drive driver with `crouch_ticks=2` twice without other changes; assert rule stops matching after 2 ticks.
**Warning signs:** Visual: player freezes mid-crouch. Use Phase 27 overlay (if available) or `print(d)` to inspect.

### Pitfall 3: `fuse_start` fires under Phase 31 tests but is relocated by Phase 32
**What goes wrong:** FUSION-DESIGN.md locked at commit 9047b590 relocates `fuse_start` emission from `Player.fuse()` to the WINDUP→FUSED transition owned by Phase 32. Phase 31 subscribers fire on the CURRENT emit site (`src/entities/player.py:97`, which fires on the v1.1 charge-to-fuse path). After Phase 32, the event will fire in a different FSM moment. Phase 31's behavior is "spawn converging ring wherever fuse_start comes from" — this subscriber contract is stable.
**Why it happens:** Layered phase boundaries. Each phase respects its emitter contract.
**How to avoid:** Subscribe to `fuse_start` by NAME. Do NOT call `Player.fuse()` directly. Do NOT hardcode the emit site. When Phase 32 moves the emit, Phase 31's subscriber works unchanged.
**Warning signs:** If the fuse-flash particle ring stops appearing after Phase 32 ships, check that Phase 32 still emits `fuse_start` (it should per FUSION-DESIGN §Fusion FSM).

### Pitfall 4: `drill_block_break` does not yet exist as an emit (Phase 32 introduces it)
**What goes wrong:** Phase 31 subscribes to an event that NO existing emitter fires. Currently `Player.on_block_break()` (line 235) sets shake + hitstop but does NOT call `event_bus.emit("drill_block_break")`. Phase 32 adds that emit. Phase 31's subscriber will exist but never fire until Phase 32 ships.
**Why it happens:** Clean phase boundary per FUSION-DESIGN §177-182 ("documented here; Phase 32 implements them").
**How to avoid:** Document in Phase 31 SUMMARY that drill-recoil pause + diverging burst are latent until Phase 32. Option: include a test that asserts the subscriber IS registered (not that it fires on a real drill) — e.g., `event_bus.emit("drill_block_break", tx=5, ty=5)` manually in a test and assert the spawner added particles. This closes the Phase 31 loop without depending on Phase 32's emit.
**Warning signs:** Manual playtest: drill into a block, no particle burst. Root cause: Phase 32 hasn't landed. Confirm with `grep -rn 'emit("drill_block_break"' src/` — should be empty until Phase 32.
**Mitigation:** Alternatively, Phase 31 can add the **single emit line** at `player.py:729` (drill block break site) and `player.py:783-785` (after on_block_break()) as a thin Phase-31-only bridge. This is out-of-scope per CONTEXT but risk-free — keep discussion open during planning.

### Pitfall 5: Bank-2 sprite transparency
**What goes wrong:** Pyxel uses `colkey` to pick a transparent index per `blt` call. `draw_sprite` defaults to `colkey=0` (`src/core/sprite_utils.py:9`). If `particles.png` uses black (index 0) for background AND for pixel content, background becomes transparent but black-on-black content is also transparent. Particles look like holes.
**Why it happens:** Pyxel default palette index 0 is black; artists often draw on black backgrounds.
**How to avoid:** Author `particles.png` with a non-used palette index as background (conventionally index 0 = transparent-black by convention, but verify by authoring content in any non-zero index). Or pass `colkey=some_other_index` explicitly for particles.
**Warning signs:** Particles render as black rectangles or invisible shapes. `pyxel.cls(0)` at frame start combined with `colkey=0` makes this subtle.

### Pitfall 6: `load_preset` silently skips unknown anim keys (forward-compat gotcha)
**What goes wrong:** Existing code at `src/ui/presets.py:58-62` wraps `set_value` in `try/except KeyError`. When anim durations join the preset dict, calling `tuning.set_value("PLAYER_RUN_DURATION_0", 6)` will raise `KeyError` because anim keys are NOT in `_flat_index` (they live under `tuning.anim.*`). The except clause swallows it silently. Anim preset data NEVER applies.
**Why it happens:** D-10 isolates anim from the flat namespace; presets.py was not designed for the dual namespace.
**How to avoid:** In `src/ui/presets.py`, add a second apply-path for anim keys: detect anim-flat-keys (e.g., prefix `ANIM_`) and route to a new `tuning.set_anim_value(path, value)` API that walks the nested `tuning.anim.player.clips[<name>].durations[<i>]` path. OR: expose anim durations in `_flat_index` as a separate `_flat_index_anim` dict and route in presets. Planner decides.
**Warning signs:** Save panel preset, reload — duration sliders snap back to default, not saved value. No error message; only empirical "preset didn't stick" symptom.

## Code Examples

Verified patterns from existing source:

### Subscribing to `fuse_start` in main.py (new Phase 31 wiring)
```python
# main.py — after reset(), before pyxel.run()
import math
from src.anim import event_bus

FUSE_CONVERGE_FRAMES = 12
FUSE_PARTICLE_COUNT = 16
FUSE_RING_RADIUS = 24

def _on_fuse_start(**kwargs):
    """Spawn 16 converging particles + start blob growth."""
    cx = self.player.x + self.player.w // 2
    cy = self.player.y + self.player.h // 2
    for i in range(FUSE_PARTICLE_COUNT):
        angle = (2 * math.pi * i) / FUSE_PARTICLE_COUNT
        start_x = cx + math.cos(angle) * FUSE_RING_RADIUS
        start_y = cy + math.sin(angle) * FUSE_RING_RADIUS
        # Converge: each frame moves (target - start) / FRAMES toward center
        dx = (cx - start_x) / FUSE_CONVERGE_FRAMES
        dy = (cy - start_y) / FUSE_CONVERGE_FRAMES
        self.particles.append(Particle(
            start_x, start_y, dx=dx, dy=dy,
            life=FUSE_CONVERGE_FRAMES,
            bank_u=PARTICLE_CONVERGE_U, bank_v=PARTICLE_CONVERGE_V,
        ))
    # Blob growth starter
    self.fused_blobs.append(BlobGrowth(cx, cy, frames=BLOB_GROWTH_FRAMES))

event_bus.subscribe("fuse_start", _on_fuse_start)
```
**Source:** `event_bus.subscribe` at `src/anim/event_bus.py:13`; `fuse_start` emit at `src/entities/player.py:97`.

### Subscribing to `drill_block_break` (animation pause + diverging burst)
```python
# main.py — same section as above

DRILL_RECOIL_PAUSE_FRAMES = 3
BURST_PARTICLE_COUNT = 14

def _on_drill_block_break(tx=None, ty=None, **kwargs):
    """Pause drill spin visually + spawn diverging burst."""
    # Animation-only pause (D-06)
    self.player._anim.pause_for(DRILL_RECOIL_PAUSE_FRAMES)  # or via _anim._player
    # Diverging burst at break point
    cx = tx * tuning.TILE_SIZE + tuning.TILE_SIZE // 2
    cy = ty * tuning.TILE_SIZE + tuning.TILE_SIZE // 2
    for i in range(BURST_PARTICLE_COUNT):
        angle = (2 * math.pi * i) / BURST_PARTICLE_COUNT
        speed = BURST_PARTICLE_SPEED  # e.g., 1.5
        self.particles.append(Particle(
            cx, cy,
            dx=math.cos(angle) * speed,
            dy=math.sin(angle) * speed,
            life=BURST_PARTICLE_LIFE,
            bank_u=PARTICLE_BURST_U, bank_v=PARTICLE_BURST_V,
        ))

event_bus.subscribe("drill_block_break", _on_drill_block_break)
```
**Source:** Subscriber pattern from event_bus; `AnimFSM.pause_for` is the proposed new public API, forwarding to its `_player`.

### `tuning.load_anim()` implementation sketch
```python
# src/core/tuning.py — new function, parallel to load()
from types import SimpleNamespace

_anim_path: pathlib.Path | None = None
_anim_raw: dict | None = None
anim: SimpleNamespace | None = None  # exposed at module level

_DEFAULT_ANIM_SCHEMA = (
    pathlib.Path(__file__).resolve().parents[2] / "assets" / "anim-schema.json"
)

def load_anim(schema_path=None) -> None:
    """Load anim-schema.json into tuning.anim namespace. Fail fast on errors (D-14)."""
    global _anim_path, _anim_raw, anim

    path = pathlib.Path(schema_path) if schema_path is not None else _DEFAULT_ANIM_SCHEMA
    _anim_path = path
    with open(path, encoding="utf-8") as f:
        _anim_raw = json.load(f)

    # Build nested SimpleNamespace tree with fail-fast validation
    entities_ns = {}
    for entity_name, entity_data in _anim_raw.items():
        if not isinstance(entity_data, dict) or "clips" not in entity_data:
            raise ValueError(f"anim-schema: entity {entity_name!r} missing 'clips' dict")
        clips = {}
        for clip_id, clip_spec in entity_data["clips"].items():
            frames = clip_spec.get("frames")
            durations = clip_spec.get("durations")
            loop = clip_spec.get("loop", True)
            events = clip_spec.get("events", {})
            if not isinstance(frames, list) or not isinstance(durations, list):
                raise ValueError(f"anim-schema: {entity_name}.{clip_id} missing frames/durations")
            if len(frames) != len(durations):
                raise ValueError(
                    f"anim-schema: {entity_name}.{clip_id} frames/durations length mismatch"
                )
            # Check for unknown fields (D-14)
            allowed = {"frames", "durations", "loop", "events"}
            extra = set(clip_spec) - allowed
            if extra:
                raise ValueError(f"anim-schema: {entity_name}.{clip_id} unknown fields: {extra}")
            clips[clip_id] = SimpleNamespace(
                frames=frames, durations=durations, loop=loop, events=events
            )
        entities_ns[entity_name] = SimpleNamespace(clips=clips)
    anim = SimpleNamespace(**entities_ns)
```
**Access pattern:** `tuning.anim.player.clips["run"].durations[0]`.
**Cross-validation with rules:** `AnimFSM` already validates at construction (`src/anim/state_machine.py:14-18`). `build_player_fsm()` must consume from `tuning.anim.player.clips` and pass to `AnimFSM(rules=PLAYER_RULES, clips=...)`.
**Source:** Phase 24 pattern at `src/core/tuning.py:50-104`; nested SimpleNamespace is stdlib idiom.

### Reading `anim-schema.json` durations at draw time (Phase 25 "read at use site" rule)
```python
# src/anim/player_anim.py — build_player_fsm rebuilt to pull from tuning.anim
from src.core import tuning
from src.anim.anim_clip import AnimClip

def build_player_fsm() -> AnimFSM:
    """Reconstruct FSM from current tuning.anim data. Called on boot and on panel reload."""
    clips: dict[str, AnimClip] = {}
    for clip_id, spec in tuning.anim.player.clips.items():
        clips[clip_id] = AnimClip(
            frames=spec.frames,
            durations=spec.durations,
            loop=spec.loop,
            events=spec.events,
        )
    return AnimFSM(rules=PLAYER_RULES, clips=clips)
```
**Panel reload:** "Reload anim schema" button calls `tuning.load_anim()` then `player._anim = build_player_fsm()` (or similar re-binding). Because `AnimClip` is `frozen=True` (`src/anim/anim_clip.py:6`), durations cannot be live-mutated in place — reload path rebuilds.
**Performance concern:** Rebuild on every slider tick would be expensive. Acceptable because D-11 specifies a **button**, not auto-reload.

### Sprite manifest with bank 2
```python
# main.py — extended SPRITE_MANIFEST
SPRITE_MANIFEST = {
    "tiles":      (0, 0, 0,   "assets/tiles.png"),
    "player":     (1, 0, 0,   "assets/sprites/player.png"),
    "slime":      (1, 0, 16,  "assets/sprites/slime.png"),
    "snail":      (1, 0, 32,  "assets/sprites/snail.png"),
    "bat":        (1, 0, 48,  "assets/sprites/bat.png"),
    "items":      (1, 0, 64,  "assets/sprites/items.png"),
    "projectile": (1, 0, 80,  "assets/sprites/projectile.png"),
    # "effects":    (1, 0, 96, "assets/sprites/effects.png"),  # REMOVED per D-16
    "boss":       (1, 0, 128, "assets/sprites/boss.png"),
    "particles":  (2, 0, 0,   "assets/sprites/particles.png"),  # NEW per D-15
}
```
**Source:** Existing `SPRITE_MANIFEST` at `main.py:144-154`.

### Hitbox-independence test skeleton (ANIM-07)
```python
# tests/test_anim_hitbox.py — NEW
import sys
from unittest.mock import MagicMock
sys.modules.setdefault("pyxel", MagicMock())

import pytest
from src.entities.player import Player
from src.anim.player_anim import (
    STATE_IDLE, STATE_RUNNING, STATE_JUMPING, STATE_FALLING,
)

HITBOX_STATES = (
    STATE_IDLE, STATE_RUNNING, STATE_JUMPING, STATE_FALLING,
    "DIVING", "WALL_SLIDING", "DASHING", "RAMMING", "BOOSTING",
    "CHARGING_SHOT", "DEAD",
)
VX_SIGNS = (-1, 0, 1)
VY_SIGNS = (-1, 0, 1)
FACINGS = (True, False)

@pytest.fixture
def mock_level():
    level = MagicMock()
    level.check_collision.return_value = False
    level.check_hazard.return_value = False
    return level

def test_hitbox_invariant_across_matrix(mock_level):
    """ANIM-07: no (state × vx_sign × vy_sign × facing) drives Player to mutate w/h."""
    for state in HITBOX_STATES:
        for vxs in VX_SIGNS:
            for vys in VY_SIGNS:
                for facing in FACINGS:
                    p = Player(0, 0, mock_level)
                    initial_w, initial_h = p.w, p.h

                    # Drive the combo
                    p.state = state
                    p.dx = float(vxs) * 2.0       # nonzero to set vx_sign
                    p.dy = float(vys) * 2.0       # nonzero to set vy_sign
                    p.facing_right = facing
                    p._update_anim_driver()

                    # Tick the FSM across a full clip window
                    for _ in range(60):  # > longest clip duration
                        p._anim.current_frame_u(p._anim_driver)

                    assert p.w == initial_w, (
                        f"w mutated at state={state} vx={vxs} vy={vys} facing={facing}: "
                        f"{initial_w} -> {p.w}"
                    )
                    assert p.h == initial_h, (
                        f"h mutated at state={state} vx={vxs} vy={vys} facing={facing}"
                    )
```
**Source:** Matrix coverage per D-23. Pattern extends `tests/test_anim.py` fixtures (`mock_level` at lines 199-205). `conftest.py` already mocks pyxel.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hardcoded v1.3 sprite toggle `u = 16 + (pyxel.frame_count // 6 % 2) * 16` in `Player.draw` | Reanimator driver/picker | Phase 26 (2026-04-12) | Phase 31 extends this architecture, does not revisit. |
| `pyxel.pset`-based debris particles | Sprite-backed particles from dedicated bank | Phase 31 (this phase) | Unified visual language across all FX. |
| `Effect` class with multi-frame inherited explosion art at bank 1 y=96 | Replaced by diverging particle burst on block-break | Phase 31 D-16 | Frees bank 1 y=96 slot; removes art user never authored. |
| Clip data hardcoded in `PLAYER_CLIPS` dict | JSON-backed `anim-schema.json` + `tuning.load_anim()` | Phase 31 D-08, D-10 | Live-tunable durations via panel; clip data lives with other authored content. |
| No hitbox/visual separation invariant test | Matrix unit test asserting `(w, h)` immutable during any anim tick | Phase 31 D-20 | Hard gate prevents regressions where anim code mutates collision state. |
| Gameplay hitstop (`game.stop_frames`) for drill block-break visual pause | Animation-only pause via `AnimPlayer.pause_for(n)` | Phase 31 D-06 | Decouples visual "bite" from gameplay time. Phase 35 may add gameplay hitstop on top. |

**Deprecated/outdated:**
- Bank 1 y=96 `effects` SPRITE_MANIFEST entry — removed per D-16.
- `Game.spawn_explosion(x, y, color)` at `main.py:825` — retire or rewrite to delegate to `spawn_particle_burst(x, y, type="block_break")`. Call sites: `main.py:647, 652, 658`, `src/entities/player.py:727, 780, 815`.
- Random-color `pset` particle rendering — retired per D-17 but the dx/dy/life update loop is preserved.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `PlayerAnimDriver.skid_ticks` / `land_ticks` / `crouch_ticks` as transient counter fields is the cleanest implementation of D-02, D-03, D-04. Alternative: pure edge-predicates without counters. | Pattern 2 | Counter approach adds 3 driver fields; edge-only approach adds none but is harder to reason about across state changes. Planner's call — tagged `[ASSUMED]` because CONTEXT D-01 through D-04 leave "driver predicate vs event listener" to planner discretion. |
| A2 | `pause_for(n)` should be additive (`_pause_ticks += n`) not overwrite. Avoids dropping a second event's pause if it arrives while the first is active. | Pattern 3 | If overwrite semantics preferred, user sees visible drill bite stop when two blocks break rapidly. Recommended as additive; planner may override. `[ASSUMED]` |
| A3 | `tuning.anim` exposed as nested `SimpleNamespace` (not dict, not frozen dataclass tree). Makes panel-reload rebinding simple: reassign `tuning.anim = new_ns`. | load_anim sketch | Alternative: dataclasses with `__slots__` for structural rigor. Both work; SimpleNamespace is lighter. `[ASSUMED]` |
| A4 | `AnimClip.events` field (reserved in Phase 26 at `src/anim/anim_clip.py:11`) is NOT wired in Phase 31 beyond data passthrough from JSON. Event-driven frame triggers (e.g., "fire footstep sound on frame 2 of run clip") are a future tier. | Clip load | Risk: if planner decides to implement frame-event dispatch, plan scope grows. `[ASSUMED]` out of scope. |
| A5 | Existing `Particle` constructor signature (`x, y, color`) will change to keyword-only `dx/dy/life/bank_u/bank_v`. Call sites at `src/entities/player.py:563, 587, 639` and `main.py:828` all need updates in the same plan. | Pattern 4 | Risk: partial migration leaves some call sites using old signature, breaking at runtime. Mitigation: rename old class to `LegacyParticle` during migration, delete once all sites updated. `[ASSUMED]` migration strategy. |
| A6 | Phase 31 does NOT add the emit for `drill_block_break` — Phase 32 owns it. Phase 31 subscribers exist but are latent. | Pitfall 4 | Planner may choose to add the single emit line as a Phase 31 bridge to avoid shipping latent subscribers. See §Pitfall 4 mitigation. `[ASSUMED]` respects CONTEXT scope as-is. |
| A7 | "Reload anim schema" button location: panel header bar, right side, next to existing Save button (or replaces it on the ANIM tab only). | Panel integration | `[ASSUMED]` — CONTEXT's Claude's Discretion says "panel tab naming and slider grouping" is free; button placement is implied. |
| A8 | `particles.png` strip layout: row 0 = convergence/burst single-sprite (directional-neutral), rows 1-N = fused_blob growth frames at progressive radii. Each frame 16×16 at bank 2 y-offsets matching bank 1 convention (16-pixel Y stride). | Bank 2 population | `[ASSUMED]` — CONTEXT D-19 delegates layout to planner. |

**If this table feels heavy:** Items A1, A5, A7, A8 are all **planner discretion** per CONTEXT — they are NOT being reopened as decisions, just flagged as "research assumed X; if planner picks Y, nothing breaks."

## Open Questions

1. **Should Phase 31 temporarily emit `drill_block_break` itself to avoid shipping latent subscribers?** (Pitfall 4)
   - What we know: Phase 32 owns the canonical emit per FUSION-DESIGN §177-182.
   - What's unclear: Whether user wants "Phase 31 ships fully working drill recoil" (requires temporary emit) vs "Phase 31 ships correct subscriber wiring; drill recoil activates when Phase 32 lands."
   - Recommendation: Discuss at planning time. A single emit line at `player.py:729` and `player.py:783-785` (just before/after `on_block_break()`) is low-risk and makes Phase 31's outcome user-visible on commit. Remove in Phase 32 if it conflicts with the refactor.

2. **`AnimFSM.pause_for(n)` as public API vs direct `player._anim._player.pause_for(n)` reach-through.**
   - What we know: Subscribers in `main.py` need to trigger pause on `drill_block_break`.
   - What's unclear: Whether `AnimFSM` (the picker) should forward `pause_for` to its internal `_player`, or whether subscribers should reach through to `_player` directly.
   - Recommendation: Forward via `AnimFSM.pause_for(n)` — keeps `_player` private, matches existing `current_frame_u` forwarding.

3. **`Particle` class: keep custom `dx/dy/life` or adopt tier-2 `AnimPlayer(clip)` wrapping?** (CONTEXT Claude's Discretion)
   - What we know: Tier-2 adoption was flagged in Phase 26 for Phase 31, but user narrowed Phase 31 scope to particle-paradigm migration, NOT static-sprite tier-2.
   - What's unclear: Whether the fused_blob growth animation (multiple progressive-size frames) wants tier-2 AnimPlayer wrapping (frame_index ticks through growth stages), or custom life-based index math.
   - Recommendation: Blob growth = tier-2 AnimPlayer(clip), since it IS a multi-frame animation. Simple one-sprite burst/convergence particles = custom dx/dy/life, since they have no frame progression. Hybrid approach matches the physics of each effect.

4. **Preset dict extension path: prefix-route anim keys, or second apply function?** (Pitfall 6)
   - What we know: `src/ui/presets.py:58-62` swallows `KeyError` silently. Anim keys are not in `_flat_index`.
   - What's unclear: Whether to (a) add anim flat-keys into `_flat_index` (breaks D-10 isolation), or (b) add a parallel `_anim_flat_index` in `tuning.py` and teach `presets.py` to route, or (c) detect prefix (e.g., `ANIM_`) in `load_preset` and call a dedicated setter.
   - Recommendation: Path (b) — parallel `_anim_flat_index` + `tuning.set_anim_value(flat_key, value)` API. Cleanest for panel widget reuse (Slider expects flat keys + `get_baseline` / `set_value` / `reset`).

## Environment Availability

Phase 31 has no external dependencies beyond what Phase 26/28 already require.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| pyxel | All draw + input | ✓ | project-pinned | — |
| pytest | ANIM-07 test | ✓ | existing suite | — |
| Python `math` (stdlib) | Converging-ring angle math | ✓ | stdlib | — |
| Python `json` (stdlib) | anim-schema.json load | ✓ | stdlib | — |
| Aseprite (optional) | Authoring new player.png frames + particles.png | ✗ (assumed, CLI not required) | — | Hand-edit PNGs in any editor; Aseprite JSON sidecar is forward-compat only and not consumed. |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:**
- Art authoring tool: user authors PNGs in their preferred tool; the engine only reads the binary PNG.

## Validation Architecture

> Nyquist validation is enabled (`.planning/config.json` absent → treat as enabled).

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (project-pinned) |
| Config file | `tests/conftest.py` (autouse pyxel mock + event_bus reset) |
| Quick run command | `pytest tests/test_anim.py tests/test_anim_hitbox.py -x -q` |
| Full suite command | `pytest -x -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ANIM-04 (D-01) | JUMPING with vx_sign=0 picks `jump_stationary`; vx_sign!=0 picks `jump_running` | unit | `pytest tests/test_anim.py::test_metroid_jump_split -x` | ❌ Wave 0 |
| ANIM-04 (D-02) | `land` event triggers `land_squash` clip for N frames | unit | `pytest tests/test_anim.py::test_land_squash_fires_on_land_event -x` | ❌ Wave 0 |
| ANIM-04 (D-03) | Flipping `facing_right` fires `turn_skid` for `TURN_SKID_FRAMES` ticks | unit | `pytest tests/test_anim.py::test_turn_skid_on_facing_flip -x` | ❌ Wave 0 |
| ANIM-04 (D-04) | `jump_start` event triggers `jump_crouch` clip; non-looping holds last frame | unit | `pytest tests/test_anim.py::test_jump_crouch_triggers_on_jump_start -x` | ❌ Wave 0 |
| ANIM-04 (D-05) | DIVING state picks `drill_spin` 4-frame loop | unit | `pytest tests/test_anim.py::test_drill_spin_4_frames_in_diving -x` | ❌ Wave 0 |
| ANIM-04 (D-06) | `pause_for(3)` freezes `_clip_ticks` for 3 ticks; frame counter unchanged | unit | `pytest tests/test_anim.py::test_pause_for_freezes_ticks -x` | ❌ Wave 0 |
| ANIM-04 (D-07a) | `fuse_start` event spawns 16 particles with converging vectors | integration | `pytest tests/test_anim_events.py::test_fuse_start_spawns_16_converging -x` | ❌ Wave 0 |
| ANIM-04 (D-07b) | Blob growth frame index ticks from 0 → N over `BLOB_GROWTH_FRAMES` | unit | `pytest tests/test_anim.py::test_blob_growth_frame_progression -x` | ❌ Wave 0 |
| ANIM-05 (D-08) | `anim-schema.json` loads into nested `tuning.anim.player.clips` namespace | unit | `pytest tests/test_tuning_anim.py::test_load_anim_builds_namespace -x` | ❌ Wave 0 |
| ANIM-05 (D-10) | `tuning.anim.player.clips['run'].durations[0]` == JSON value | unit | `pytest tests/test_tuning_anim.py::test_anim_access_path -x` | ❌ Wave 0 |
| ANIM-05 (D-11) | Slider value change visible at next `current_frame_u` call | integration | manual (in-engine) — drag panel slider, observe run cycle rate change | ❌ Manual (Wave 0 harness possible) |
| ANIM-05 (D-14) | Missing clip_id referenced by rule raises `ValueError` at `load_anim` | unit | `pytest tests/test_tuning_anim.py::test_load_anim_fails_on_missing_clip_ref -x` | ❌ Wave 0 |
| ANIM-05 (D-14) | Frame/duration length mismatch raises `ValueError` | unit | `pytest tests/test_tuning_anim.py::test_load_anim_fails_on_length_mismatch -x` | ❌ Wave 0 |
| ANIM-05 (D-14) | Unknown field on clip raises `ValueError` | unit | `pytest tests/test_tuning_anim.py::test_load_anim_fails_on_unknown_field -x` | ❌ Wave 0 |
| ANIM-06 (D-15) | `particles.png` loads into bank 2; bank 0 (tiles) + bank 1 (entities) unchanged | unit | `pytest tests/test_sprite_assets.py::test_particles_bank_2_populated -x` | ❌ Wave 0 (extend existing) |
| ANIM-06 (D-16) | Block-break triggers diverging burst (>= 12 particles) with outward vectors | integration | `pytest tests/test_anim_events.py::test_drill_block_break_spawns_burst -x` | ❌ Wave 0 |
| ANIM-06 (D-17) | `Particle.draw` uses `draw_sprite` against bank 2, not `pyxel.pset` | unit | `pytest tests/test_anim_events.py::test_particle_renders_from_bank_2 -x` | ❌ Wave 0 |
| ANIM-07 (D-20, D-23) | Matrix: state × vx_sign × vy_sign × facing — (w, h) immutable after 60 ticks | unit | `pytest tests/test_anim_hitbox.py::test_hitbox_invariant_across_matrix -x` | ❌ Wave 0 |
| ANIM-07 (D-22) | Test is a hard gate — runs in default `pytest` (no opt-in mark) | smoke | `pytest -x` (default invocation) | ❌ Wave 0 (new file auto-picked up) |

### Success Criteria → Validation

1. **Jumping / landing / turning / drilling / fusion each show a visible transition driven by FSM + tunable from panel.**
   - Validated by: ANIM-04 D-01..D-07 tests listed above, plus a **manual in-engine check** — boot game, jump from stationary (see `jump_stationary`), jump while running (see `jump_running`), land (see squash), turn around (see skid), drill into CRACKED_V (see 4-frame spin + 3-frame pause on break), fuse (see 16-particle converge + blob growth).
   - Panel-tunable check: F1 → ANIM tab → drag `run[0]` duration slider → observe run frame rate change live.

2. **`assets/anim-schema.json` exists, loaded by `tuning.py`, live-editable via panel.**
   - Validated by: ANIM-05 D-08, D-10, D-11, D-14 tests; manual check: open schema JSON, edit duration, click "Reload anim schema" button in panel, observe change live.

3. **Particle sprites live in a bank separate from map tiles; verified by loading a room with many particles.**
   - Validated by: ANIM-06 D-15, D-16, D-17 tests; manual check: boot game, spam block-breaks in a CRACKED_V-dense room, verify particle bursts render + no tile corruption in the map bank (bank 0) and no entity bank (bank 1) overwrite.

4. **Automated regression test confirms no anim state read ever mutates `.w`/`.h`.**
   - Validated by: ANIM-07 matrix test; enforced as HARD GATE in default `pytest` per D-22.

### Sampling Rate

- **Per task commit:** `pytest tests/test_anim.py tests/test_anim_hitbox.py -x -q` (fast — unit tests only)
- **Per wave merge:** `pytest -x -q` (full suite — catches integration regressions, e.g., panel/preset interactions)
- **Phase gate:** Full suite green before `/gsd-verify-work`; manual in-engine validation of all 4 success criteria.

### Wave 0 Gaps

- [ ] `tests/test_anim_hitbox.py` — NEW file; ANIM-07 matrix test (D-20, D-23)
- [ ] `tests/test_tuning_anim.py` — NEW file; ANIM-05 loader validation (D-14 fail-fast branches)
- [ ] `tests/test_anim_events.py` — NEW file; integration tests for `fuse_start` and `drill_block_break` subscribers (D-07a, D-16)
- [ ] `tests/test_anim.py` — EXTEND with new clip/rule tests (D-01..D-06)
- [ ] `tests/test_sprite_assets.py` — EXTEND with bank-2 load verification (D-15)
- [ ] Shared fixture: headless `Player` constructor helper is already present in `tests/test_anim.py:200-205` (`mock_level`) — reuse via conftest (already exposed).
- [ ] Framework install: none — pytest already on path.

## Sources

### Primary (HIGH confidence — verified via direct file read)
- `.planning/ROADMAP.md:180-189` — Phase 31 goal + 4 success criteria + depends on Phase 24/26
- `.planning/FUSION-DESIGN.md:14-18, 168-185, 300-320` — `fuse_start` / `drill_block_break` emission contract; Phase 31 subscribes
- `.planning/phases/31-animation-content-particle-bank-separation/31-CONTEXT.md` — D-01 through D-23 locked decisions (all 23 covered in User Constraints above)
- `.planning/phases/31-animation-content-particle-bank-separation/31-DISCUSSION-LOG.md` — Discussion audit trail (alternatives considered)
- `.planning/phases/26-event-bus-animation-fsm-skeleton/26-CONTEXT.md` — Reanimator architecture carry-forward
- `.planning/STATE.md` — Phase 30 just completed; Phase 31 is next
- `src/anim/player_anim.py` (69 lines) — verbatim PLAYER_CLIPS + PLAYER_RULES + PlayerAnimDriver; Phase 31 extends
- `src/anim/anim_clip.py` (18 lines) — AnimClip dataclass; `events` slot already reserved
- `src/anim/anim_player.py` (35 lines) — tick() implementation; Phase 31 adds `pause_for`
- `src/anim/state_machine.py` (35 lines) — AnimFSM; construction-time clip_id validation
- `src/anim/event_bus.py` (25 lines) — pub-sub primitives
- `src/entities/player.py` (897 lines, read in full) — `_update_anim_driver` at 847-858; event emit sites confirmed; `on_block_break` at 235-239
- `src/entities/effects.py` (62 lines) — current Effect + Particle classes
- `src/core/tuning.py` (298 lines) — PEP-562 loader pattern to mirror for `load_anim`
- `src/core/sprite_utils.py` (65 lines) — `draw_sprite` signature for sprite-backed particle rendering
- `src/ui/panel.py` (406 lines) — TAB_DEFS structure; add ANIM entry; F1 toggle; preset interaction
- `src/ui/presets.py` (73 lines) — FEEL_GROUPS-based preset saving; gotcha: KeyError-swallow behavior
- `src/ui/widgets.py` (464 lines) — Slider class to reuse for anim durations
- `main.py:144-154, 305-313, 825-828` — SPRITE_MANIFEST + `_load_sprites` + `spawn_explosion`
- `tests/test_anim.py` (302 lines) — existing ANIM tests; extension patterns for hitbox test
- `tests/test_event_bus.py` (466 lines) — subscriber test patterns with mock Player
- `tests/conftest.py` (56 lines) — autouse pyxel mock + event_bus reset
- `assets/sprites/` directory listing — effects.png is 396 bytes (16×16 strip); player.png is 324 bytes (3-frame strip at 48×16)
- `assets/presets/slot_0.json` — preset shape; forward-compat for anim key addition

### Secondary (MEDIUM — Pyxel API knowledge from project code + docs)
- Pyxel `pyxel.circ(x, y, r, col)` — filled circle primitive; documented fallback for fused_blob placeholder if art slips
- Pyxel `pyxel.blt` / `colkey` semantics — inferred from `src/core/sprite_utils.py:39` usage
- Python `SimpleNamespace` — stdlib `types.SimpleNamespace`, suitable for `tuning.anim` nested namespace

### Tertiary (LOW — not used; flagged for planner awareness)
- No WebSearch / WebFetch used. All research is in-repo. HIGH confidence because the project is closed-domain and all context is canonical in `.planning/` + `src/`.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Pyxel-only project, all deps already installed, no external lookups needed.
- Architecture: HIGH — Phase 26 skeleton is tested and stable; Phase 31 additions are well-scoped extensions.
- Pitfalls: HIGH — all six pitfalls trace to verifiable code paths in the repo (explicit file:line references).
- Validation architecture: HIGH — test patterns match existing `tests/test_anim.py` conventions.
- `AnimPlayer.pause_for(n)` design: MEDIUM — no direct precedent in codebase; pattern proposed is standard-idiom but not yet verified against runtime behavior. Planner should validate the additive-vs-overwrite semantics choice with a unit test.
- Preset routing for anim keys: MEDIUM — Pitfall 6 identifies a real risk; recommended solution (parallel `_anim_flat_index`) is sensible but untested.

**Research date:** 2026-04-21
**Valid until:** 2026-05-21 (30 days — stable Pyxel stack, stable project architecture post-Phase-30 lock)
