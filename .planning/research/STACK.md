# Stack Research — v2.0 Game Feel (Jelly Roll Proto)

**Domain:** Pyxel retro platformer — in-game tuning/debug tooling & juice utilities
**Researched:** 2026-04-11
**Confidence:** HIGH (most decisions are "build custom" with well-understood patterns; the one library recommendation is low-risk)

## TL;DR — Opinionated Verdict

> **Add exactly ONE runtime dependency: `watchdog 6.0.0`** (for schema hot-reload).
> **Build everything else as ~500 lines of pure-Python utility modules.** Pyxel's draw model is too minimal and too opinionated to host any existing UI/animation/particle library, and every popular candidate (pygame-gui, imgui, arcade-particle, pytransitions) either requires a different render backend, pulls C extensions, or is overkill for ~50 tuning knobs and ~2-frame sprites.

| Area | Verdict | What |
|------|---------|------|
| Live tuning UI (sliders) | **BUILD CUSTOM** | ~200 LOC pure-Pyxel widget module |
| Schema hot-reload | **USE LIBRARY** | `watchdog 6.0.0` (with a 10-line mtime fallback) |
| Animation state machine | **BUILD CUSTOM** | ~150 LOC FSM + event bus in `src/core/` |
| Diagnostic overlays | **BUILD CUSTOM** | ~100 LOC using `pyxel.rectb/line/text` |
| Particles | **BUILD CUSTOM** | ~80 LOC pooled particle system |
| Screen shake | **BUILD CUSTOM** | ~30 LOC, integrated into existing Camera |
| Hitstop | **BUILD CUSTOM** | ~20 LOC timer hook in game loop |

**Total new code estimate: ~600 LOC across ~6 new modules. One new pip dependency.**

---

## Runtime Environment (baseline, for the record)

| Technology | Version | Status | Notes |
|------------|---------|--------|-------|
| Pyxel | 2.9.0 (2026-04-10) | already installed | Python >=3.10 required. Latest on PyPI. |
| Python | 3.10+ | assumed | Matches Pyxel's minimum. |

Pyxel 2.x exposes only primitive draw calls: `rect`, `rectb`, `line`, `circ`, `circb`, `text`, `blt`, `pset`. There is **no widget system, no sprite animation system, no particle system, no state machine, no tween library, no hot-reload hook**. This is why almost everything here is "build custom" — any external library would have to be reimplemented on top of those primitives anyway, and the reimplementation IS the work.

Sources verified:
- [Pyxel 2.9.0 on PyPI](https://pypi.org/project/pyxel/) — latest release, Python >=3.10
- [kitao/pyxel GitHub](https://github.com/kitao/pyxel) — API surface unchanged between 2.x releases

---

## 1. Live In-Game Tuning UI (Sliders, Grouped Panels, Preset Save/Load)

### Verdict: BUILD CUSTOM — `src/debug/tuning_panel.py`

### Why not a library?

| Candidate | Why it fails |
|-----------|--------------|
| `pygame-gui` | Requires pygame as render backend. Incompatible with Pyxel's framebuffer. |
| `pygame_menu` | Same — pygame-based. |
| `pyimgui` / `imgui-bundle` | OpenGL backend required. Pyxel renders via its own WebGPU/SDL bridge; you cannot share a GL context. Also pulls a ~30MB C extension — overkill for ~50 sliders. |
| `dearpygui` | Runs in its own window/event loop. Cannot be composited into Pyxel's framebuffer. |
| `tkinter` in a second window | Possible but ugly — split attention across two windows breaks the GMTK Platformer Toolkit feel, which is the whole reference point. |
| Pyxel's own `pyxel.btnp` + `text` | Actually all you need. This is the recommendation. |

**The GMTK Platformer Toolkit model the user cites is literally "sliders drawn on top of the game, same window, same frame."** That requires the UI to live inside Pyxel's `draw()` phase and read Pyxel's input state directly. No external GUI library can do that without a different render backend.

### What to build

A `TuningPanel` class that:

1. **Renders with `pyxel.rect`, `pyxel.rectb`, `pyxel.text`** — a bordered side panel (e.g. 120px wide column overlayed on the right side, toggleable with F1).
2. **Reads input via `pyxel.btn/btnp` + `pyxel.mouse_x/mouse_y`** — Pyxel 2.x exposes mouse position and button state; that is all a slider needs.
3. **Binds each slider to a dotted schema path** — e.g. `"player.jump.jump_force"` — reading/writing the live config dict that the game loop already consults.
4. **Groups sliders into collapsible sections** — "Movement", "Jump", "Slime Follow", "Drill", "Fusion", "Juice". Pure draw logic.
5. **Pages vertically** if a section overflows — PgUp/PgDn or mouse wheel.
6. **Saves/loads presets as JSON** next to `physics-schema.json`:
   - `assets/presets/floaty.json`
   - `assets/presets/snappy.json`
   - `assets/presets/shipping.json`
   Each preset is just a flat `{dotted_path: value}` dict; applying it walks the live config and reassigns.
7. **Writes back to `physics-schema.json`** on demand (explicit "Save to schema" button) so the converter sees it on next run.

### Integration with existing code

- Lives in new `src/debug/tuning_panel.py`.
- Game constructs it once, calls `panel.update()` in `update()` and `panel.draw()` in `draw()` AFTER the game world, BEFORE the HUD.
- Needs a **ConfigStore** abstraction (see section 2) that everything else reads from instead of `from src.core.constants import GRAVITY`. This is the single most architecturally load-bearing change in v2.0.

### Widget primitives to implement

| Widget | Size | Purpose |
|--------|------|---------|
| `Slider(label, path, min, max, step)` | 1 line ~120×8px | float/int tuning knobs |
| `Toggle(label, path)` | 1 line ~120×8px | bool flags (e.g. debug overlays on/off) |
| `Button(label, onclick)` | 1 line ~120×10px | "Save preset", "Reset", "Reload schema" |
| `SectionHeader(label, collapsed)` | 1 line ~120×10px | collapsible group |

Total widget module: **~200 LOC.** Zero dependencies.

### Pitfalls to avoid

- **Don't use floats for slider `step`.** Round to `step` grain on every drag or slider values will drift and never match preset JSON on disk. Use `round(value / step) * step`.
- **Clip panel draw region** — Pyxel has `pyxel.clip(x, y, w, h)`; use it so a section that overflows doesn't paint over the game.
- **Mouse wheel scrolling** — Pyxel 2.x exposes `pyxel.mouse_wheel`; use for paging.
- **16-color palette clash** — pick panel colors that don't collide with player/enemy colors (suggest color 1 for bg, 7 for text, 5 for borders, 10 for active slider fill).

---

## 2. JSON Schema Hot-Reload / File Watch

### Verdict: USE LIBRARY — `watchdog 6.0.0`

### Why a library (this one time)?

Filesystem watching is **the one thing on this list where the OS APIs differ substantially per platform** (inotify/FSEvents/ReadDirectoryChangesW), and the user runs on Windows. A correct hand-rolled watcher is not 10 lines — it's platform-specific. `watchdog` wraps all three and is 1 dependency, 0 transitive deps, pure-Python shell over optional C accelerators.

| Option | Verdict |
|--------|---------|
| **`watchdog 6.0.0`** | **RECOMMENDED.** Mature, cross-platform, battle-tested. ~200KB. No C extension required (uses pure-Python fallback on Windows via ReadDirectoryChangesW ctypes binding). |
| `mtime polling in update()` | Acceptable FALLBACK. For ONE file this is genuinely 10 lines. See below. |
| `watchfiles` (Rust-backed) | Also fine, faster, but pulls a Rust wheel. Overkill for one file. |

### Recommended install

```bash
pip install "watchdog>=6.0.0,<7"
```

- [watchdog 6.0.0 on PyPI](https://pypi.org/project/watchdog/) — released 2024-11-01, Python >=3.9, compatible with Python 3.10+ Pyxel requires.
- [pytransitions/watchdog GitHub](https://github.com/gorakhargosh/watchdog)

### What to build around it

A `ConfigStore` class in `src/core/config_store.py` that:

1. **Loads `assets/physics-schema.json` once at startup** into a nested dict.
2. **Exposes `get(path, default)`** — e.g. `config.get("player.jump.jump_force")`.
3. **Exposes `set(path, value)`** for the tuning panel to write.
4. **Starts a `watchdog.observers.Observer` on `assets/physics-schema.json`.**
5. **On file-change event, re-reads the JSON and atomically swaps the live dict.** Guard with a `threading.Lock` — watchdog events fire on a worker thread, but Pyxel's game loop is single-threaded; take the lock in `update()` to check if a reload happened.
6. **Signals subscribers** (player, slime, fusion, camera) via a simple observer list that they should re-pull their derived cached values.

### The ConfigStore IS the architectural linchpin of v2.0

Right now `src/core/constants.py` hardcodes ~50 values and everything does `from src.core.constants import GRAVITY`. For hot-reload to work, **all consumers must route through ConfigStore at read time, not import time.** This is the single biggest refactor in v2.0 and should be its own phase.

Proposed migration pattern:

```python
# Before
from src.core.constants import GRAVITY, JUMP_FORCE
self.vy += GRAVITY

# After
from src.core.config_store import cfg
self.vy += cfg.player.jump.gravity
# or
self.vy += cfg["player.jump.gravity"]
```

The `cfg` object should be a module-level singleton that exposes dotted attribute OR key access. Use a `SimpleNamespace`-style wrapper that also supports `__getitem__` with dotted paths.

`constants.py` becomes either (a) deleted, or (b) a thin shim that re-exports `cfg.*` for backwards compatibility during migration. **Option (b) is recommended for incremental migration.**

### Fallback: mtime polling (10 lines, zero deps)

If `watchdog` turns out to cause issues (Windows permission quirks, thread-safety surprises), this is the drop-in replacement:

```python
# src/core/config_store.py
import os, json, time
class ConfigStore:
    def __init__(self, path):
        self.path = path
        self._mtime = 0
        self._data = {}
        self.reload()

    def reload(self):
        with open(self.path) as f:
            self._data = json.load(f)
        self._mtime = os.path.getmtime(self.path)

    def tick(self):  # called from game.update() once per frame
        try:
            m = os.path.getmtime(self.path)
            if m != self._mtime:
                self.reload()
        except OSError:
            pass  # file in mid-save, try next frame
```

**Recommendation:** ship with `watchdog`, keep `tick()` as a commented-out fallback. Polling once per frame for one file is literally free (~10µs) but thread-safety with a single-threaded poll is simpler.

### Pitfalls

- **Atomic write race:** editors often save via rename (write temp, rename over target). `watchdog` fires the event before the rename completes sometimes. Catch `JSONDecodeError` on reload and retry next frame.
- **Thread safety:** watchdog callbacks run on a worker thread. Do NOT mutate game state from the callback — set a `dirty` flag and swap in the main thread.
- **Schema version drift:** if the JSON on disk has a new key the game doesn't know about, ignore it (don't crash). If it's missing a key the game needs, fall back to the in-memory value (don't crash).
- **Converter contract:** `pml-to-ldtk` reads `physics-schema.json`. Hot-reload in-game is fine — but if the tuning panel writes back to disk, the next converter run will use those values. Document this clearly.

---

## 3. Animation State Machine with Transition Frames & Event Hooks

### Verdict: BUILD CUSTOM — `src/core/animation.py`

### Why not a library?

| Candidate | Why it fails |
|-----------|--------------|
| `pytransitions/transitions` | **4× the complexity you need.** Supports nested states, async, graphviz export, pickling. None of that matters when you have 6 animation states (idle/run/jump/fall/land/wallslide). Adds ~1500 LOC import weight. |
| `python-statemachine` | Same story — declarative class-based API designed for business workflows, not 60fps animation ticks. |
| `arcade`/`pygame` animation libs | Different render backend. |
| Aseprite JSON tags (already in `sprite_utils.load_sprite_tags`) | **Keep this** — it's the data format, not the state machine. Use it to drive frame sequences once the FSM picks a state. |

### What to build

A tiny hand-rolled FSM with three components:

#### 3a. `AnimState` dataclass

```python
@dataclass
class AnimState:
    name: str                       # "RUN", "JUMP_UP", "LAND"
    frames: list[int]               # u offsets into spritesheet
    durations: list[int]            # frames per sprite frame
    loop: bool = True
    next_state: str | None = None   # for one-shot transitions like "LAND" -> "IDLE"
    on_enter: Callable | None = None
    on_exit: Callable | None = None
```

#### 3b. `Animator` class (~80 LOC)

- Holds `states: dict[str, AnimState]`, `current: str`, `frame_idx: int`, `timer: int`.
- `tick()` advances `timer`, steps `frame_idx`, handles loop/end, triggers `next_state` transitions.
- `play(name, force=False)` switches state — if `force=False`, ignored if already playing.
- `current_uv() -> (u, v)` returns the sprite coords for `draw()` to blit.

#### 3c. `AnimEventBus` (~40 LOC)

A dead-simple pub-sub for the hooks the user listed (`direction_change`, `jump_start`, `land`, `fall_start`, `wall_touch`, `drill_impact`, `fuse_start`, `fuse_end`):

```python
class EventBus:
    def __init__(self):
        self.subs: dict[str, list[Callable]] = defaultdict(list)
    def on(self, event, fn): self.subs[event].append(fn)
    def emit(self, event, **kw):
        for fn in self.subs[event]:
            fn(**kw)
```

Player's `update()` emits events when state transitions occur; Animator subscribes and calls `play()` on the right key; particle/sound/hitstop systems also subscribe independently. Clean decoupling, 40 lines.

#### 3d. Transition frame insertion

The "even 1 frame at the right moment" insight is solved by giving each `AnimState` an optional **intro frame list** — when entering `RUN` from `IDLE`, play intro frames before main loop frames. Literally 5 extra lines in `tick()`:

```python
if self.in_intro:
    # play intro frames
    ...
    if intro_done:
        self.in_intro = False
else:
    # play main loop frames
```

#### 3e. Procedural squash/stretch

Wire this through the existing `draw_sprite(..., scale=None)` parameter in `src/core/sprite_utils.py` — it already supports scale. Add a second `scale_x, scale_y` pair (currently only uniform scale). The Animator exposes `scale_x, scale_y` which decay toward 1.0 each frame; on `jump_start` event, set `scale_y = 1.3, scale_x = 0.8`; on `land` event, set `scale_y = 0.7, scale_x = 1.2`. Procedural, no extra sprites needed.

**Integration pitfall:** `sprite_utils.draw_sprite` currently passes `scale` straight to `pyxel.blt`. Pyxel 2.x's `blt` only accepts a uniform scale. For non-uniform squash/stretch you'll need to manually set draw width/height per frame (dest w/h on `blt`), and Pyxel 2.x supports this via the negative-width flip trick combined with explicit dest sizing. **Verify before committing** — this is one of the few spots where Pyxel's API might force a compromise (uniform scale only, or manual per-pixel sprite scaling).

### Total new code: ~150 LOC in `src/core/animation.py` + ~30 LOC refactor in `src/entities/player.py`.

The existing hardcoded logic in `player.py:790-796` (`u = 16 + (pyxel.frame_count // 12 % 2) * 16`) becomes:

```python
self.animator.tick()
u, v = self.animator.current_uv()
draw_sprite(self.x, self.y, ..., u, v, ...)
```

All frame math moves into `AnimState` definitions at `__init__`, driven by values from `ConfigStore` so animation timings are also live-tunable via the slider panel.

---

## 4. Diagnostic Overlays (velocity/hitbox/input state)

### Verdict: BUILD CUSTOM — `src/debug/overlays.py`

### Why not a library?

There is no "retro game debug overlay library" for Pyxel. There isn't one for pygame either that's worth pulling in. Overlays are 100 lines of draw calls.

### What to build

A single `DebugOverlays` module with toggle flags (each bindable to a `Toggle` widget in the tuning panel):

| Overlay | Draw calls | LOC |
|---------|------------|-----|
| **Hitbox wireframes** | `pyxel.rectb` on every entity using its collision box | ~15 |
| **Velocity vectors** | `pyxel.line` from entity center, length ∝ `(vx, vy)` | ~10 |
| **Input state** | Bottom-left `pyxel.text` showing `L R U D V X J` with pressed letters highlighted | ~20 |
| **Coyote/buffer timers** | Bar charts using `pyxel.rect`, one for each active timer on player | ~15 |
| **Collision grid** | Draw tile-grid outline on IntGrid collision cells near player | ~20 |
| **Frame time graph** | Rolling 60-frame FPS history using `pyxel.line` | ~15 |
| **Slime follow target** | `pyxel.line` from slime to follow anchor + circle at target | ~10 |

Total: **~100 LOC, zero dependencies.** Every overlay is ≤20 lines because Pyxel's primitives are so direct.

### Integration

- Lives in `src/debug/overlays.py`.
- Game's `draw()` calls `overlays.draw(game_state)` AFTER the world draw, BEFORE the tuning panel draw.
- Each overlay reads its on/off state from a `debug` namespace in `ConfigStore`, so toggles are controlled by the tuning panel AND persist across restarts.

### Pitfalls

- **Overlay colors overlap game colors** — pin overlays to colors 8 (red), 11 (green), 12 (blue) exclusively. These are rarely used by tile art and read clearly on any background.
- **Performance** — drawing 200 hitboxes each frame is free in Pyxel; don't optimize prematurely.

---

## 5. Particles / Screen Shake / Hitstop

### Verdict: BUILD CUSTOM — three tiny modules

Every candidate particle library (`pyglet.particle`, `arcade.emitter`, `pygame-particles`) is tied to a different render backend. There is no Pyxel particle library. The GOOD NEWS is that particles for a 16-color retro game are the simplest possible particle system — they're literally colored pixels or 1-tile sprites with velocity and a lifetime.

### 5a. Particle system — `src/fx/particles.py` (~80 LOC)

**Pattern: pooled particle array, no allocations per frame.**

```python
@dataclass
class Particle:
    x: float; y: float
    vx: float; vy: float
    life: int
    max_life: int
    color: int
    gravity: float = 0.0
    kind: int = 0  # 0=pixel, 1=rect, 2=circ

class ParticleSystem:
    def __init__(self, capacity=256):
        self.pool = [Particle(0,0,0,0,0,0,0) for _ in range(capacity)]
        self.active = 0

    def emit(self, x, y, count, **kw):
        for _ in range(count):
            if self.active >= len(self.pool): return
            p = self.pool[self.active]; self.active += 1
            # ... assign fields
```

- **Pooling is mandatory** — Python's GC pauses are invisible at 60fps for a few hundred objects, but they compound. Reuse the pool.
- **Draw via `pyxel.pset/rect/circ`** — one primitive per particle. Pyxel can draw 1000+ primitives per frame without breaking 16ms.
- **Presets**: `burst_dust(x,y)`, `drill_impact(x,y)`, `jump_dust(x,y)`, `fuse_spark(x,y)`, `death_explode(x,y)`. Each is a ~5-line function that calls `emit()` with tuned parameters sourced from `ConfigStore` (so the tuning panel can tweak particle counts/lifetimes/colors live).

### 5b. Screen shake — extend existing Camera (~30 LOC)

The game already has a camera (room transition LERP lives somewhere). Add:

```python
class Camera:
    shake_trauma: float = 0.0    # 0..1
    shake_decay: float = 0.05    # per frame

    def add_shake(self, amount):
        self.shake_trauma = min(1.0, self.shake_trauma + amount)

    def _shake_offset(self):
        if self.shake_trauma <= 0: return 0, 0
        mag = self.shake_trauma ** 2 * MAX_SHAKE_PX
        return (random.uniform(-mag, mag), random.uniform(-mag, mag))

    def tick(self):
        self.shake_trauma = max(0.0, self.shake_trauma - self.shake_decay)
```

**Use trauma-squared, not linear.** This is the [GDC "Math for Game Programmers"](https://www.youtube.com/watch?v=tu-Qe66AvtY) pattern — linear shake feels floaty, squared shake has a satisfying snap-then-decay curve.

Shake presets: `light (0.2)`, `medium (0.4)`, `heavy (0.7)` — all driven by `ConfigStore` values. Subscribe to the AnimEventBus: `on("drill_impact", lambda: camera.add_shake(cfg.fx.drill_shake))`.

### 5c. Hitstop — new `src/fx/hitstop.py` (~20 LOC)

**Hitstop = pause game updates for N frames while still drawing.**

```python
class Hitstop:
    remaining: int = 0
    def freeze(self, frames): self.remaining = max(self.remaining, frames)
    def tick(self): 
        if self.remaining > 0:
            self.remaining -= 1
            return True  # skip updates this frame
        return False
```

In `Game.update()`:

```python
def update(self):
    if self.hitstop.tick():
        return   # drawing still happens, world doesn't advance
    # ... normal update
```

**Critical:** player input must still be buffered during hitstop (read into buffer even while world is frozen) so the player doesn't feel unresponsive. Pyxel's `btnp` already gives you a one-frame edge detect — save presses into a list and replay them on the first unfrozen frame.

Subscribe to AnimEventBus: `on("drill_impact", lambda: hitstop.freeze(cfg.fx.drill_hitstop_frames))`.

Typical values per research: 3-6 frames (50-100ms at 60fps). Make this live-tunable.

### Pitfalls for FX

- **Don't freeze audio during hitstop** — Pyxel plays sounds on a separate audio thread, so calling `play()` once before the freeze is fine. But don't call it repeatedly.
- **Particle `random` calls** — if you want deterministic replays, seed a dedicated `random.Random()` instance, don't use the module-global.
- **Screen shake + HUD** — shake offset should be applied to the game camera only, NOT to the 16px HUD strip. Render HUD after resetting draw offsets.
- **Overlapping hitstops** — use `max()`, not addition, so chained impacts don't stack into multi-second freezes.

---

## Full Recommended Stack Summary

### Runtime dependencies (new)

```bash
pip install "watchdog>=6.0.0,<7"
```

That's it. One line.

### New internal modules

| Path | LOC | Purpose |
|------|-----|---------|
| `src/core/config_store.py` | ~120 | Live schema store + hot-reload (uses watchdog) |
| `src/core/animation.py` | ~150 | FSM + event bus + animator |
| `src/debug/tuning_panel.py` | ~200 | Slider/toggle/button widgets + panel layout |
| `src/debug/overlays.py` | ~100 | Velocity/hitbox/input/timer visualizers |
| `src/fx/particles.py` | ~80 | Pooled particle system + presets |
| `src/fx/hitstop.py` | ~20 | Global frame-freeze timer |
| (patch) `src/core/camera.py` | +30 | Add shake trauma |
| (patch) `src/core/sprite_utils.py` | +20 | Non-uniform scale for squash/stretch |
| (patch) `src/entities/player.py` | +30/-50 | Replace hardcoded anim with Animator |

**Total new code: ~600 LOC across ~6 new files + 3 patches.**

### What NOT to use

| Avoid | Why | Use instead |
|-------|-----|-------------|
| `pygame-gui`, `pygame_menu` | pygame render backend, incompatible with Pyxel framebuffer | custom `tuning_panel.py` |
| `pyimgui`, `dearpygui` | Require OpenGL context; runs in separate window | custom `tuning_panel.py` |
| `tkinter` second window | Breaks single-window GMTK-toolkit feel | custom `tuning_panel.py` |
| `pytransitions`, `python-statemachine` | 10× heavier than needed; designed for business logic, not 60fps animation | custom ~150 LOC FSM |
| `arcade`, `pyglet` particle systems | Different render backends | custom pooled system |
| `watchfiles` (Rust) | Pulls Rust wheel; overkill for one file | `watchdog 6.0.0` is lighter and already mature |
| `mtime polling` as primary | Fine as fallback but `watchdog` gives instant, non-polled updates | `watchdog`, with polling as documented fallback |
| Pyxel's image-bank `u, v` hardcoded math (`u = 16 + ... % 2 * 16`) | This is the v1.x pattern; v2.0 is replacing it | `Animator.current_uv()` driven by `AnimState.frames` |

### Version Compatibility

| Package | Version | Compatible With | Notes |
|---------|---------|-----------------|-------|
| pyxel | 2.9.0 | Python >=3.10 | Already installed |
| watchdog | 6.0.0 | Python >=3.9 | Works on Windows without C extension; uses ctypes binding for ReadDirectoryChangesW |
| Python | 3.10+ | — | Match Pyxel's minimum |

No known conflicts. `watchdog` has zero transitive dependencies on Linux/macOS/Windows; on Windows it uses ctypes against the system DLL, no compilation needed.

### Stack Pattern Variants

**If hot-reload thread safety becomes a problem on Windows:**
- Drop watchdog, use the 10-line mtime polling fallback in `ConfigStore.tick()`.
- Cost: ~1 frame of latency before a save is picked up. Acceptable.

**If Pyxel's `blt` can't do non-uniform scale:**
- Drop procedural squash/stretch.
- Fall back to drawing one extra pre-baked squash frame per state. Animator already supports per-frame uv lookup so no code change needed — just more art.
- Squash/stretch is a "nice to have"; state machine + transition frames are the load-bearing feature.

**If the tuning panel proves too slow to build in Phase 1:**
- MVP = just print `cfg.player.jump.gravity = 0.0875` text at top of screen + 4 keybinds to adjust current-selected value by ±step. 30 LOC total. Ship this first, evolve into the full panel.

---

## Integration Considerations with Existing Patterns

### ConfigStore vs `constants.py`

**Biggest refactor in v2.0.** Strategy:

1. Phase A: Introduce `ConfigStore`, keep `constants.py` as-is.
2. Phase B: Rewrite `constants.py` to pull from `ConfigStore` at module load, re-export the names. Existing `from src.core.constants import GRAVITY` still works, but GRAVITY is now read from schema at import time (no hot-reload yet, but schema is source of truth).
3. Phase C: Migrate hot callers (Player, Slime, Camera) to read `cfg.player.jump.gravity` live each frame → enables hot-reload.
4. Phase D: Migrate cold callers (one-time-at-startup consumers) gradually.
5. Phase E: Delete `constants.py`.

**Do not try to do all 5 at once.** Phase A and B should be one commit; C should be per-system.

### `schema.py` lookup module

Already provides 9 public lookup functions for tile/entity definitions. **ConfigStore is a parallel module**, not a replacement — `schema.py` reads `entity-schema.json` (tile/entity/biome structure), `ConfigStore` reads `physics-schema.json` (tunable values). Keep them separate; they serve different purposes and have different hot-reload requirements (entity-schema changes require rebuilding the LDtk map, physics-schema changes should hot-reload live).

### `sprite_utils.load_sprite_tags`

Already exists and parses Aseprite JSON. Currently unused by draw methods (as documented in the docstring). **Use it now.** Each entity's `AnimState` dict should be built at startup by reading the Aseprite tags — `{"idle": (0,0), "run": (1,2), "jump": (3,3)}` — and converting them to `AnimState(name="RUN", frames=[1,2], ...)`. This replaces the hardcoded u-offset math entirely and makes the art pipeline drive animation data.

### `draw_sprite(..., scale=None)`

Already supports scale. For squash/stretch, extend to `draw_sprite(..., scale_x=None, scale_y=None)`. Existing callers pass `scale=0.5` — keep backwards compat by treating `scale` as uniform when `scale_x`/`scale_y` are None.

---

## Confidence Assessment

| Decision | Confidence | Why |
|----------|-----------|-----|
| Build custom tuning panel | **HIGH** | Pyxel has no widget system and no library can bridge a different render backend. This is not a choice. |
| Use watchdog 6.0.0 | **HIGH** | Verified latest version on PyPI. Stable since 2020, Python 3.10+ supported, zero transitive deps. |
| Build custom FSM | **HIGH** | Verified pytransitions and python-statemachine are overkill; 150 LOC FSM is well-understood pattern. |
| Build custom overlays | **HIGH** | Trivial with Pyxel primitives; no library exists. |
| Build custom particles | **HIGH** | Pool-backed particle systems are ~80 LOC and well-documented pattern. |
| Build custom shake (trauma-squared) | **HIGH** | Industry-standard pattern (GDC talk). |
| Build custom hitstop | **HIGH** | ~20 LOC; no library needed. |
| Non-uniform scale via `blt` | **MEDIUM** | Need to verify Pyxel 2.9.0's `blt` supports explicit dest w/h. Fallback exists (pre-baked frames). |
| ConfigStore phased migration | **HIGH** | Standard refactor pattern; low risk if done incrementally. |

---

## Sources

- [Pyxel 2.9.0 on PyPI](https://pypi.org/project/pyxel/) — verified latest version, Python >=3.10, released 2026-04-10
- [kitao/pyxel on GitHub](https://github.com/kitao/pyxel) — API surface (no widget/animation/particle system)
- [watchdog 6.0.0 on PyPI](https://pypi.org/project/watchdog/) — verified latest, released 2024-11-01, Python >=3.9
- [gorakhargosh/watchdog on GitHub](https://github.com/gorakhargosh/watchdog) — cross-platform filesystem events
- [pytransitions/transitions on GitHub](https://github.com/pytransitions/transitions) — evaluated and rejected (overkill)
- [python-statemachine docs](https://python-statemachine.readthedocs.io/) — evaluated and rejected (business-logic oriented)
- [Juice It Good: Camera Shake (Antonio Delgado)](https://gt3000.medium.com/juice-it-adding-camera-shake-to-your-game-e63e1a16f0a6) — trauma-squared shake pattern
- [Research on Screen Shake and Hit Stop Mechanisms (Oreate AI)](https://www.oreateai.com/blog/research-on-the-mechanism-of-screen-shake-and-hit-stop-effects-on-game-impact/decf24388684845c565d0cc48f09fa24) — typical hitstop durations (50-100ms)
- [GameDev Academy: Game Feel Tutorial](https://gamedevacademy.org/game-feel-tutorial/) — hitstop + screen shake + particle fundamentals
- [pygame GUIs wiki](https://www.pygame.org/wiki/gui) — confirmed pygame-gui requires pygame backend (incompatible with Pyxel)

---

*Stack research for: Pyxel retro platformer v2.0 Game Feel milestone*
*Researched: 2026-04-11*
