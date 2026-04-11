# Architecture Research: Jelly Roll Proto v2.0 Game Feel

**Domain:** Pyxel (Python) Metroidvania prototype — live-tuning, animation FSM, fusion redesign
**Researched:** 2026-04-11
**Confidence:** HIGH (grounded in actual codebase inspection; patterns are standard Pyxel/Python idioms)

---

## 1. Schema-as-Source-of-Truth Inversion

### The core problem

Today the dataflow is:

```
constants.py (hand-edited)  ──►  build script  ──►  physics-schema.json
                         \                                 ▲
                          └──►  game (import constants)    └── pml-to-ldtk reads
```

The converter reads `physics-schema.json`, but the game imports `constants.py`. We need:

```
physics-schema.json (hand-edited / panel-edited)
         │
         ├──►  pml-to-ldtk (unchanged contract)
         │
         └──►  game tuning loader ──► every entity/system
                     ▲
                     │ (hot-reload via file mtime OR direct panel write)
              live-tuning panel
```

### Recommended Python pattern: a `tuning` module with attribute access + one compat shim

Create `src/core/tuning.py` modeled on the existing `src/core/schema.py` singleton pattern. It is the *only* new core module this milestone strictly requires.

```python
# src/core/tuning.py
"""Tuning loader for physics-schema.json (SoT inversion).

Loads the schema at startup, exposes values as module attributes via __getattr__,
supports hot-reload and in-memory mutation (for the live-tuning panel).
"""
import json
import os
import threading
from pathlib import Path

_PATH = Path("assets/physics-schema.json")
_data: dict | None = None          # full parsed schema
_flat: dict[str, float] = {}       # flattened "GROUP.KEY" -> value for fast lookup
_mtime: float = 0.0
_lock = threading.Lock()           # future-proof; Pyxel is single-threaded today
_listeners: list = []              # callables invoked on reload

# --- Public API ------------------------------------------------------------

def init(path: str | os.PathLike = _PATH) -> None:
    global _PATH
    _PATH = Path(path)
    _reload_from_disk()

def get(key: str, default=None):
    """Dotted-key lookup, e.g. get('movement.WALK_ACCEL')."""
    return _flat.get(key, default)

def set_value(key: str, value) -> None:
    """Live-tuning panel entry point. Updates in-memory + writes to disk."""
    _flat[key] = value
    _write_nested(_data, key, value)
    _save_to_disk()
    _notify()

def reload_if_changed() -> bool:
    """Call once per frame from game loop. Returns True if reloaded."""
    try:
        m = _PATH.stat().st_mtime
    except FileNotFoundError:
        return False
    if m > _mtime:
        _reload_from_disk()
        return True
    return False

def on_reload(fn) -> None:
    """Register a callback invoked whenever values change (reload or panel set)."""
    _listeners.append(fn)

# --- Attribute-style access (so old code reads 'tuning.GRAVITY') -----------

def __getattr__(name: str):
    # Flat top-level lookup first, then search all groups
    if name in _flat:
        return _flat[name]
    for k, v in _flat.items():
        if k.endswith("." + name):
            return v
    raise AttributeError(f"tuning has no value '{name}'")
```

Key properties:

- **`from src.core import tuning; tuning.GRAVITY`** works identically to the old `from src.core.constants import GRAVITY` — but `GRAVITY` is *looked up* each read, so hot-reload "just works" for callers that re-read per frame.
- **Callers that cached the value at import time** (e.g. `from src.core.constants import GRAVITY` as a module-level assignment inside player.py) will *not* pick up changes. See compat shim below.
- The JSON on disk remains the source of truth; `set_value()` is atomic (write temp file, `os.replace()`).

### The compat shim (keeps every existing caller working Day 1)

Rewrite `src/core/constants.py` into a **passthrough** that re-exports from `tuning`:

```python
# src/core/constants.py  (post-migration)
"""Backward-compatibility shim. New code should use src.core.tuning directly.

Every constant is re-read from the tuning module on attribute access, so hot-reload
works for call sites that do `from src.core.constants import GRAVITY` IF they
dereference `constants.GRAVITY` each frame. Module-level caching (top of file)
will NOT hot-reload — those sites must be migrated to `tuning.GRAVITY`.
"""
from src.core import tuning

# Non-tuning constants stay here (display, sprite size, tile size sentinels)
TILE_SIZE = 16
SCREEN_W, SCREEN_H = 320, 192
VIEWPORT_W, VIEWPORT_H = 320, 176
HUD_H = 16
SPRITE_SIZE = 16
BOSS_SPRITE_SIZE = 32
TILE_EMPTY = (15, 15)

def __getattr__(name):
    # PEP 562 module __getattr__ — consulted on attribute miss
    return getattr(tuning, name)
```

Every current `from src.core.constants import GRAVITY, WALK_ACCEL` keeps working. PEP 562 `__getattr__` fires on `constants.GRAVITY`, not on the star-import names already bound at import time — so the migration plan is:

1. Ship the shim. Nothing breaks because PEP 562 fallback handles `constants.X` attribute access paths.
2. Audit `from src.core.constants import X` import sites. Each one binds at import-time and will *not* hot-reload. These become the migration checklist — ~20 files in `src/entities/`.
3. Rewrite to `from src.core import tuning` and read `tuning.X` at use site, not import site. This is a mechanical sed-style change, one file at a time.

### Hot-reload mechanism

Two orthogonal triggers:

- **External edit (text editor, git pull):** `tuning.reload_if_changed()` called once per `update()` tick from `Game.update()`. Mtime check is nearly free (~microseconds).
- **Internal panel edit:** panel slider calls `tuning.set_value("movement.WALK_ACCEL", 0.13)`. This updates in-memory immediately (no file round-trip needed for display) *and* writes to disk so the converter sees it.

Both paths fire `_notify()` which calls registered `on_reload` listeners. Subsystems that precompute derived values (e.g. jump apex physics, animation frame timings) register a listener to recompute.

### Schema file restructure

`physics-schema.json` today has `source_constants` as a flat dict. Invert the structure so groups match existing `constants.py` comment sections. Keep the converter-facing top-level keys (`jump.max_height_tiles`, `placement_rules.*`) but compute them from the grouped raw values:

```jsonc
{
  "version": "1.0.0",
  "tile_size": 16,
  "fps": 60,
  "tuning": {
    "movement": {
      "WALK_ACCEL": 0.125,
      "WALK_FRICTION": 0.15,
      "MAX_WALK_SPEED": 1.25
    },
    "jump": {
      "GRAVITY": 0.0875,
      "JUMP_FORCE": -3.25,
      "MAX_FALL_SPEED": 2.5,
      "VARIABLE_JUMP_REDUCTION": 0.5,
      "FALLING_GRAVITY_MULTIPLIER": 1.8,
      "COYOTE_TIME": 12,
      "JUMP_BUFFER": 8
    },
    "wall": { "WALL_SLIDE_FRICTION": 0.2, "WALL_JUMP_X_IMPULSE": 1.5, "WALL_JUMP_Y_FORCE": -1.75 },
    "slime_follow": { "SLIME_FOLLOW_DELAY": 16, "SLIME_MAX_DIST": 100, "SLIME_REFORM_DIST": 8 },
    "juice": { "JUICE_MAX": 200.0, "JUICE_REGEN_RATE": 0.5, "SLIME_SPIT_COST": 10.0 },
    "drill": { "DRILL_SPEED": 2.0, "DRILL_IMPACT_COST": 20.0 },
    "ram": { "RAM_SPEED": 2.5, "RAM_DIAGONAL_FACTOR": 0.7 },
    "charge_shot": { "CHARGE_SHOT_SPEED": 3.0 },
    "boost": { "BOOST_FORCE": -1.75, "BOOST_JUICE_COST": 25.0 },
    "fusion": { "MANA_SHIELD_COST": 20.0, "RECALL_SPEED": 4.0 },
    "juice_effects": { "DRILL_SHAKE_DURATION": 12, "DRILL_HITSTOP_FRAMES": 6 }
  },
  "derived": {
    "jump": { "max_height_tiles": 3, "max_width_tiles": 5 },
    "placement_rules": { }
  },
  "player": { "hitbox_px": [10,14], "visual_px": [16,16] }
}
```

Add a **`derive.py` pass** that computes `derived.*` from `tuning.*` on every reload — same formulas as the current build script that generates `physics-schema.json` today, just inverted. The converter reads only `derived.*`/`player`/`placement_rules` — its contract is preserved if those sections stay stable after recompute.

**Confidence: HIGH** on the pattern (PEP 562 module `__getattr__` is a standard, boring Python idiom introduced in 3.7). The only risk is import-site caching, which the migration plan addresses explicitly.

---

## 2. Animation State Machine Architecture

### Problem context

`src/entities/player.py:790-800` today:

```python
u = 0
if self.state == "RUNNING":
    u = 16 + (pyxel.frame_count // 12 % 2) * 16
elif self.state == "JUMPING" or self.state == "FALLING":
    u = 32
```

This is a **display-time state read**, not an animation state machine. It has no concept of transitions, anticipation, recovery, or events. The player already has a gameplay FSM (`self.state` IDLE/RUNNING/JUMPING/FALLING) — the animation FSM should be a **separate, parallel FSM** that *observes* gameplay state and emits its own animation states, so gameplay logic doesn't get coupled to sprite concerns.

### Recommended architecture: two coupled FSMs + event bus

```
┌──────────────────────┐         ┌──────────────────────┐
│  Gameplay FSM        │ events  │  Animation FSM       │
│  (player.py state)   ├────────►│  (anim/player_anim)  │
│  IDLE/RUN/JUMP/FALL  │         │  idle/run/            │
│  - physics           │         │  jump_anticipation/   │
│  - input             │         │  jump_rising/         │
│  - collision         │         │  jump_apex/           │
└──────────┬───────────┘         │  fall/                │
           │                     │  land_recovery/       │
           │                     │  ...                  │
           │                     └──────┬───────────────┘
           │                            │
           │                            ▼
           │                     ┌──────────────┐
           │                     │ AnimPlayer   │ ──► draw() u,v,flip
           │                     │ - frame idx  │     + squash/stretch
           │                     │ - timer      │       transform
           │                     └──────────────┘
           ▼
    ┌─────────────┐
    │ EventBus    │ ◄── subscribes: AnimFSM, JuicePanel, Audio, VFX
    │ frame-local │
    └─────────────┘
```

### Files to add

```
src/anim/
├── __init__.py
├── event_bus.py         # tiny pub-sub, frame-local dispatch
├── state_machine.py     # generic AnimFSM class (not player-specific)
├── anim_player.py       # frame ticker, reads AnimClip, handles squash/stretch
├── anim_clip.py         # data class: frames, duration, loop, events, transforms
└── player_anim.py       # player-specific FSM wiring (imports event_bus)
```

### `event_bus.py` — dead simple pub-sub

```python
# src/anim/event_bus.py
_subs: dict[str, list] = {}

def subscribe(event: str, fn) -> None:
    _subs.setdefault(event, []).append(fn)

def emit(event: str, **payload) -> None:
    for fn in _subs.get(event, ()):
        fn(**payload)
```

No ordering guarantees, no queueing, no unsubscribe — it's a prototype. Called from gameplay code:

```python
# in player.py when input flips facing
if new_facing != self.facing_right:
    event_bus.emit("direction_change", entity="player", new_facing=new_facing)

# when grounded after airborne
if self.vy > 0 and self.on_ground and not prev_on_ground:
    event_bus.emit("land", entity="player", impact_vy=self.vy)

# when jump button pressed
if jump_pressed and can_jump:
    event_bus.emit("jump_start", entity="player")
```

Events to emit (from milestone doc): `direction_change`, `jump_start`, `jump_released`, `fall_start`, `land`, `wall_touch`, `wall_jump`, `drill_impact`, `fuse_start`, `fuse_end`, `ram_start`, `ram_impact`, `boost_tap`, `charge_shot_fire`, `spit`, `damaged`, `death`.

### `state_machine.py` — generic FSM

```python
# src/anim/state_machine.py
class AnimFSM:
    def __init__(self, states: dict, initial: str):
        self.states = states       # name -> AnimState
        self.current = initial
        self.timer = 0

    def update(self):
        self.timer += 1
        state = self.states[self.current]
        # Auto-transition on clip end (e.g. land_recovery -> idle)
        if state.auto_next and self.timer >= state.duration:
            self.transition(state.auto_next)

    def transition(self, name: str):
        if name == self.current:
            return
        self.states[self.current].on_exit and self.states[self.current].on_exit()
        self.current = name
        self.timer = 0
        self.states[name].on_enter and self.states[name].on_enter()
```

### `player_anim.py` — the wiring

```python
# src/anim/player_anim.py
from src.anim import event_bus
from src.anim.state_machine import AnimFSM
from src.anim.anim_clip import AnimClip
from src.core import tuning

def _build_states():
    return {
        "idle":         AnimClip(frames=[(0,0)],          duration=None, loop=True),
        "run":          AnimClip(frames=[(16,0),(32,0)],  duration=tuning.get("anim.RUN_FRAME_DUR", 12), loop=True),
        "jump_anticipation": AnimClip(frames=[(48,0)], duration=tuning.get("anim.JUMP_ANTICIPATION", 2),
                                      squash=(1.1, 0.9), auto_next="jump_rising"),
        "jump_rising":  AnimClip(frames=[(64,0)],         duration=None, loop=True, stretch=(0.9, 1.1)),
        "jump_apex":    AnimClip(frames=[(80,0)],         duration=None, loop=True),
        "fall":         AnimClip(frames=[(96,0)],         duration=None, loop=True),
        "land_recovery":AnimClip(frames=[(112,0)],        duration=tuning.get("anim.LAND_RECOVERY", 4),
                                 squash=(1.2, 0.8), auto_next="idle"),
        # ... drill, ram, boost, fuse, damaged, etc.
    }

fsm: AnimFSM | None = None

def init():
    global fsm
    fsm = AnimFSM(_build_states(), initial="idle")
    event_bus.subscribe("jump_start",   lambda **kw: fsm.transition("jump_anticipation"))
    event_bus.subscribe("fall_start",   lambda **kw: fsm.transition("fall"))
    event_bus.subscribe("land",         lambda **kw: fsm.transition("land_recovery"))
    event_bus.subscribe("direction_change", lambda **kw: None)  # could flash transition frame
    event_bus.subscribe("drill_impact", lambda **kw: fsm.transition("drill_impact_recoil"))
    tuning.on_reload(lambda: _rebuild_states())

def _rebuild_states():
    fsm.states = _build_states()  # durations may have changed
```

Then in `player.py::draw()`:

```python
clip = player_anim.fsm.states[player_anim.fsm.current]
u, v = clip.current_frame(player_anim.fsm.timer)
sx, sy = clip.squash_at(player_anim.fsm.timer)  # procedural squash/stretch scale
draw_sprite_scaled(self.x, self.y, u, v, sx, sy, self.facing_right)
```

### Where animation data lives

**Recommendation: separate `assets/anim-schema.json`**, not inside `physics-schema.json`.

Rationale:
- Physics schema is converter-facing (stable contract). Anim schema is game-only — don't risk converter breaks when tweaking animations.
- Anim data is structurally different: clip frames, durations, event bindings — not scalar tunables.
- The tuning loader can handle both files via the same `tuning` module (extend `init()` to load multiple schemas into a namespaced flat dict: `anim.player.run_frame_dur`).

The live-tuning panel treats both identically — they're just different category groups.

### Procedural squash/stretch

Handled by `AnimClip.squash_at(t)`: a function returning `(scale_x, scale_y)` given timer. Two modes:

1. **Easing curve** — `(1.2, 0.8)` at t=0 decaying linearly or via ease-out to `(1.0, 1.0)` at t=duration. Tunable start value + duration per state.
2. **Per-frame override** — override scale on specific frames in the clip.

Pyxel doesn't natively scale blits, so squash/stretch uses `pyxel.blt` with manual x/y offsets + either a rendering of pre-squashed sprites (ideal) or multi-blit trickery (hack). For prototype: accept that squash/stretch shifts the draw position but does *not* actually scale pixels — use +/- 1-2 px vertical offset on landing frames to fake the compression. Or rasterize squashed variants offline into the spritesheet and select them by scale factor.

**Confidence: MEDIUM** on Pyxel scaling — Pyxel's `blt()` does not support destination scaling; any true scaling would need per-pixel `pget/pset` loops (too slow). Recommendation: commit to **pre-authored squash frames** in the spritesheet. The squash/stretch "feature" becomes sprite selection, not transform. This keeps the FSM simple and Pyxel-native.

---

## 3. Live-Tuning Panel Architecture

### Where it sits in the loop

```
Game.update():
    tuning.reload_if_changed()        # external edits
    if panel.active:
        panel.update()                 # input routing: sliders, tabs
        if not panel.pause_game:
            world.update()             # game keeps running while tuning
    else:
        world.update()

Game.draw():
    world.draw()
    hud.draw()
    if panel.active:
        panel.draw()                   # overlays on top, semi-transparent bg
```

Two modes:
- **Overlay mode** (default): game keeps running, panel draws on top, input split between game and panel by held modifier key (e.g. Alt keeps game input active, else panel captures).
- **Paused mode**: `panel.pause_game = True`, world.update() skipped, game frozen while tuning.

Toggle via a hotkey (e.g. `F1` or `~`). This is strictly debug UI — ship builds compile it out via `DEBUG = True` guard.

### Input routing

Pyxel provides `pyxel.btnp`, `pyxel.mouse_x/y`, `pyxel.btn(pyxel.MOUSE_BUTTON_LEFT)`. Recommended:

- **Mouse-first**: click slider handles, drag to adjust, click category tabs. Mouse is enabled via `pyxel.mouse(True)` when panel opens.
- **Keyboard fallback**: arrow keys navigate fields, +/- adjust selected field, Tab cycles categories. Essential for gamepad-less laptops but mouse is primary.
- **Gamepad**: defer. Mouse covers the 90% case for prototype iteration.

### Structure

```
src/debug/
├── __init__.py
├── panel.py              # Panel class — top-level overlay controller
├── slider.py             # Slider widget — draws + handles mouse drag
├── category.py           # Category (collapsible group of sliders)
├── presets.py            # Save/load named tuning snapshots to JSON
└── overlays.py           # Diagnostic overlays (velocity, hitbox, input state)
```

### Category pattern for 50+ sliders

Categories are declared once, sourced from the schema structure itself. Panel shows category tabs along the top (or a left sidebar); only the active category's sliders render. With 50+ values across 11 categories, each tab shows ~4-6 sliders, each slider occupies ~20px vertical, fits comfortably in 320x180 with ~120px panel height.

### Slider widget

Per-slider metadata: `{key, label, min, max, step, type}`. For prototype, hardcode ranges per category rather than storing ranges in schema — faster iteration. Slider drag calls `tuning.set_value(key, new_value)` which updates in-memory, writes JSON (debounced), fires `on_reload` listeners.

### Presets

`src/debug/presets.py` reads/writes `assets/presets/*.json` — named snapshots of the full tuning state. "Save Current", "Load: gmtk_loose", "Reset to Default". Prevents losing a good tuning state when experimenting.

### Diagnostic overlays

Separate from the panel — always-available toggles:

- **Velocity arrow** on player: line from center in direction of `(vx, vy)`.
- **Hitboxes**: `pyxel.rectb` around `.x, .y, .w, .h` for player, enemies, projectiles.
- **Input state strip** at top: shows held buttons, coyote timer, jump buffer, state name.
- **Animation state readout**: current clip name, timer, queued transitions.

Each overlay has a hotkey (`F2`, `F3`, `F4`, `F5`).

**Confidence: HIGH** — this is standard debug UI territory; Pyxel has all needed primitives (mouse, text, rect).

---

## 4. Fusion Lifecycle Redesign

### The abstraction

The old model couples trigger, state, and effect into one blob per ability. The redesign wants three clean phases:

```
initiate  ──►  sustain  ──►  end
 (trigger)     (state)      (effect finalize)
```

Each ability (drill, ram, hold, charge shot, bubble shield, boost) implements this interface. Pluggable, not inheritance-heavy.

### Recommended pattern: Protocol + registry

```python
# src/fusion/ability.py
from typing import Protocol

class FusionAbility(Protocol):
    name: str

    def can_initiate(self, player, slime, input_state) -> bool: ...
    def initiate(self, player, slime, ctx) -> None: ...
    def sustain(self, player, slime, ctx) -> None: ...
    def should_end(self, player, slime, ctx) -> bool: ...
    def end(self, player, slime, ctx) -> None: ...

    def juice_cost(self) -> float: ...
    def duration_cap(self) -> int: ...
```

Each ability is a class implementing this protocol, instantiated once, registered in a central `FusionManager`:

```
src/fusion/
├── __init__.py
├── ability.py             # Protocol + base class with common helpers
├── manager.py             # FusionManager — owns current ability + phase + timer
├── drill_dive.py          # DrillDive(FusionAbility)
├── slime_ram.py           # SlimeRam(FusionAbility)
├── slime_hold.py
├── charge_shot.py
├── bubble_shield.py
└── slime_boost.py
```

### `FusionManager` — the state machine shell

Phases: INACTIVE → INITIATING → SUSTAINING → ENDING → INACTIVE. Manager owns state, abilities are stateless(ish) — they read/write player/slime, not their own fields. Emits `fusion_phase_*` events on each transition.

### Clean separation

- **Trigger** = `can_initiate()`: reads input + resource + context, returns bool. Pure query.
- **State** = manager's `phase` + `phase_timer` + `active` reference.
- **Effect** = `initiate()`, `sustain()`, `end()` methods — they *do* things to player/slime/world.

If an ability genuinely needs private state (charge level, chain counter), store it on `ctx` or as an instance field initialized in `initiate()` and cleared in `end()`.

### Charge-to-fuse uniform entry

Per PROJECT.md key decision "Charge-to-fuse system: Hold fuse button to initiate fusion abilities." Implement as a **pre-manager** phase: the FusionManager only sees `input_state.fuse_charged == True` after the charge meter fills. The charge is driven by a small `ChargeController` sitting in front of the manager, reading fuse button + cancel windows, emitting `fuse_start` / `fuse_end` / `fuse_canceled` events.

This keeps individual abilities from reimplementing charge logic — they just check `input_state.direction` and `input_state.fuse_charged` in `can_initiate`.

### Integration with existing player.py

Today fusion logic is scattered through player.py. The cleanup:

1. Introduce `FusionManager` as `self.fusion = FusionManager(...)` on Player.
2. `Player.update()` calls `self.fusion.update(self, slime, input_state)`.
3. Old per-ability code in player.py becomes ability class methods — cut and paste, refactor access patterns.
4. Abilities emit events (`drill_impact`, `ram_start`, etc.) via `event_bus`, which the AnimFSM and juice FX systems subscribe to.

This is the **largest code move** in the milestone and should be its own phase, not mixed with other work.

**Confidence: HIGH** on the pattern. The fusion redesign document (per PROJECT.md, "locked design doc before re-implementation") must precede this so the protocol shape is nailed down.

---

## 5. Integration / Build Order

### Dependency graph

```
                         ┌───────────────────────────────┐
                         │ Phase 1: Tuning Foundation    │
                         │ - physics-schema restructure  │
                         │ - tuning.py loader            │
                         │ - constants.py compat shim    │
                         │ - hot-reload mtime check      │
                         │ - converter contract verify   │
                         └───────────┬───────────────────┘
                                     │
                    ┌────────────────┼──────────────────┐
                    │                │                  │
                    ▼                ▼                  ▼
         ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
         │ Phase 2:         │ │ Phase 3:     │ │ Phase 4:         │
         │ Call-site        │ │ Event Bus +  │ │ Debug Overlays   │
         │ migration        │ │ AnimFSM      │ │ (velocity, hit-  │
         │ (constants→tun.) │ │ skeleton     │ │  box, input)     │
         └────────┬─────────┘ └──────┬───────┘ └────────┬─────────┘
                  │                  │                  │
                  └──────┬───────────┘                  │
                         ▼                              │
              ┌─────────────────────┐                   │
              │ Phase 5: Live-      │◄──────────────────┘
              │ Tuning Panel MVP    │
              │ (sliders, presets)  │
              └──────────┬──────────┘
                         │
             ┌───────────┼─────────────────┐
             │           │                 │
             ▼           ▼                 ▼
      ┌────────────┐ ┌───────────┐ ┌──────────────┐
      │ Phase 6:   │ │ Phase 7:  │ │ Phase 8:     │
      │ Track A —  │ │ Fusion    │ │ Animation    │
      │ Player     │ │ Design    │ │ states +     │
      │ movement   │ │ Doc (no   │ │ transition   │
      │ feel pass  │ │ code)     │ │ frames       │
      └────────────┘ └─────┬─────┘ └──────┬───────┘
                           │              │
                           ▼              │
                ┌──────────────────┐      │
                │ Phase 9: Fusion  │      │
                │ Manager +        │      │
                │ Ability protocol │      │
                │ (refactor, no    │      │
                │  feel changes)   │      │
                └─────────┬────────┘      │
                          │               │
                          ▼               │
                ┌──────────────────┐      │
                │ Phase 10: Track  │◄─────┘
                │ B — per-ability  │
                │ feel pass        │
                │ (drill/ram/etc.) │
                └─────────┬────────┘
                          │
                          ▼
                ┌──────────────────┐
                │ Phase 11: Slime  │
                │ follow/AI pass   │
                └─────────┬────────┘
                          │
                          ▼
                ┌──────────────────┐
                │ Phase 12: Juice  │
                │ polish (shake,   │
                │ hitstop, VFX)    │
                └─────────┬────────┘
                          │
                          ▼
                ┌──────────────────┐
                │ Phase 13:        │
                │ Milestone cap —  │
                │ preset bake,     │
                │ regression check │
                └──────────────────┘
```

### Build order rationale

- **Phase 1 is the keystone.** Nothing else can be tuned live until the schema is the source of truth and the loader is in place. Critically, Phase 1 must verify the pml-to-ldtk converter still reads a valid file after the restructure — this is the only external contract at risk.
- **Phase 2 is mechanical but tedious.** Migrating `from src.core.constants import X` sites to `tuning.X` reads. Can partially overlap with Phase 3-4 because the compat shim keeps old sites working.
- **Phase 3 (event bus + AnimFSM skeleton) and Phase 4 (overlays)** are independent and unblock Phase 5. They can be parallel.
- **Phase 5 (live-tuning panel MVP)** depends on the tuning loader being writable (Phase 1) and ideally overlays (Phase 4) for validation.
- **Phases 6 and 7 can parallelize.** Track A (player movement) needs the panel (Phase 5) to iterate. Fusion design doc (Phase 7) is design-only, no code.
- **Phase 8 (animation states + transition frames)** depends on AnimFSM skeleton (Phase 3); needs new sprite assets.
- **Phase 9 (fusion refactor)** prereq for Phase 10. Pure refactor phase with regression testing.
- **Phases 10-12** are the "feel" phases that the whole milestone is about. They consume the live panel heavily.
- **Phase 13** locks in presets and verifies nothing regressed.

### What must happen first (critical path)

**Phase 1 is the absolute prerequisite.** Without schema inversion + loader + compat shim + converter contract verification, nothing else in the milestone is unblocked.

Secondary foundations (event bus, overlays) can ship in Phase 3-4 in parallel but Phase 5 (the panel) is the real "milestone accelerator" — once sliders exist, every subsequent phase benefits from rapid iteration.

### Pragmatism callouts

- Don't build a generic widget framework. Hardcode slider layout in a single `panel.py` file.
- Don't store slider ranges in the schema. Hardcode in `SLIDER_RANGES` dict.
- Don't implement gamepad input for the debug panel. Mouse only.
- Don't build true squash/stretch transforms. Use pre-authored sprite frames selected by clip state.
- Don't make abilities inherit from a base class unless a concrete shared-helper emerges. Protocol + duck typing is enough.
- Don't try to migrate all `constants.py` call sites in one go. Use the compat shim and migrate per-subsystem across multiple phases.

---

## Integration Points Summary

### New files

| Path | Purpose | Depends on |
|------|---------|------------|
| `src/core/tuning.py` | Schema loader, hot-reload, attribute access | physics-schema.json restructure |
| `src/anim/event_bus.py` | Pub-sub event dispatcher | — |
| `src/anim/state_machine.py` | Generic AnimFSM class | — |
| `src/anim/anim_clip.py` | AnimClip data structure (frames, squash, events) | — |
| `src/anim/anim_player.py` | Frame ticker + draw helpers | anim_clip |
| `src/anim/player_anim.py` | Player-specific FSM wiring | event_bus, state_machine, tuning |
| `src/debug/panel.py` | Live-tuning panel controller | tuning, slider |
| `src/debug/slider.py` | Slider widget | — |
| `src/debug/category.py` | Category grouping | slider |
| `src/debug/presets.py` | Preset save/load | tuning |
| `src/debug/overlays.py` | Velocity/hitbox/input overlays | — |
| `src/fusion/ability.py` | FusionAbility protocol | — |
| `src/fusion/manager.py` | FusionManager state machine | event_bus |
| `src/fusion/drill_dive.py` | DrillDive implementation | ability |
| `src/fusion/slime_ram.py` | SlimeRam implementation | ability |
| `src/fusion/slime_hold.py` | SlimeHold implementation | ability |
| `src/fusion/charge_shot.py` | ChargeShot implementation | ability |
| `src/fusion/bubble_shield.py` | BubbleShield implementation | ability |
| `src/fusion/slime_boost.py` | SlimeBoost implementation | ability |
| `assets/anim-schema.json` | Animation clip definitions | — |
| `assets/presets/default.json` | Default tuning snapshot | tuning |

### Modified files

| Path | Change | Risk |
|------|--------|------|
| `assets/physics-schema.json` | Restructure to `tuning.*` + `derived.*` | Converter must still parse — verify |
| `src/core/constants.py` | Becomes compat shim via PEP 562 `__getattr__` | Import-site caching won't hot-reload |
| `src/entities/player.py` | Strip fusion code → fusion/; strip anim code → anim/; add tuning.* reads | Large refactor, keep phases small |
| `src/entities/slime.py` | Add fusion phase hooks, read tuning.* | Medium |
| `src/entities/projectile.py` | Read tuning.* for speeds/costs | Low |
| `src/entities/enemies/*.py` | Read tuning.* for speeds | Low |
| `src/main.py` (Game class) | Call `tuning.init()`, `player_anim.init()`, wire panel toggle | Small |
| Any file with `from src.core.constants import X` at top | Migrate to `from src.core import tuning` + lookups at use site | Mechanical, per-file, tracked |

### Data flow changes

**Before:**
```
constants.py → import binds at module load → player.py uses GRAVITY directly
                        │
                        └──► build script → physics-schema.json → converter
```

**After:**
```
physics-schema.json (SoT)
       │
       ├──► tuning.py loader (hot-reload, in-memory flat dict)
       │           │
       │           ├──► player.py reads tuning.GRAVITY each frame
       │           ├──► slime.py, projectile.py, enemies/*.py
       │           ├──► fusion/*.py reads tuning.DRILL_SPEED etc.
       │           ├──► anim clips read tuning.anim.RUN_FRAME_DUR
       │           └──► debug/panel.py reads + writes via tuning.set_value()
       │
       ├──► derive pass → fills derived.* section on reload
       │
       └──► pml-to-ldtk converter reads derived.* + placement_rules (contract preserved)
```

### Event flow (new)

```
Input/Physics event in gameplay code
       │
       ▼
event_bus.emit("jump_start", ...)
       │
       ├──► player_anim.fsm.transition("jump_anticipation")
       ├──► vfx.spawn_dust_puff(player.x, player.y)
       ├──► audio.play_sound(JUMP_SOUND)
       └──► overlays.log_event("jump_start")  (when diag on)
```

---

## Anti-Patterns to Avoid

1. **Over-engineered widget framework.** This is a single-dev prototype. A 200-line `panel.py` with hardcoded layouts beats a 2000-line "UI system."
2. **Coupling gameplay FSM to animation FSM.** Gameplay should never check `player.anim.current == "land_recovery"`. Emit events, let animation react.
3. **Per-ability inheritance trees.** Protocol duck typing is enough — six abilities don't justify a class hierarchy.
4. **Caching tuning values at module top level.** Kills hot-reload. The whole point is that values are re-read per frame.
5. **Storing animation clip data in physics-schema.json.** Breaks the converter contract separation and mixes concerns. Keep anim-schema.json separate.
6. **Writing to physics-schema.json on every slider drag frame.** Disk I/O at 60fps. Debounce writes (write 200ms after last change) and keep in-memory authoritative during drag.
7. **Global mutable `_data` dict in tuning.py with direct access.** Always go through `get()` / `set_value()` / attribute access so hot-reload listeners fire reliably.
8. **Making the compat shim "smart."** It should be a dumb passthrough. Don't try to emit deprecation warnings or track migration — just re-export.

---

## Open Questions for the Requirements/Roadmap Phase

1. **Does the pml-to-ldtk converter read `source_constants` today, or only `derived.*`/`placement_rules`?** If it reads raw constants, Phase 1 must keep that section populated (even if generated from `tuning.*`). Check `CONVERTER-HANDOFF.md`.
2. **Does the live panel need to work in pause mode, overlay mode, or both?** Pause mode is simpler; overlay mode is better for feel-testing. Recommend both, pause as default.
3. **Fusion design doc must land before Phase 9.** If design is still open, phases 9-10 can't be sequenced confidently. Add a "design freeze" gate between Phase 7 and Phase 9.
4. **Sprite assets for transition frames.** Phase 8 depends on new spritesheet rows. Is the art pipeline ready? Flag as potential blocker.
5. **Preset file format stability.** If `tuning` schema shape changes mid-milestone, old presets break. Version the preset files from day 1.

---

**Files referenced:**
- `C:\Github\jelly-roll-proto\.planning\PROJECT.md`
- `C:\Github\jelly-roll-proto\.planning\STATE.md`
- `C:\Github\jelly-roll-proto\assets\physics-schema.json`
- `C:\Github\jelly-roll-proto\src\core\constants.py`
- `C:\Github\jelly-roll-proto\src\core\schema.py` (lines 1-100, singleton pattern precedent for `tuning.py`)
- `C:\Github\jelly-roll-proto\src\entities\player.py` (lines 780-810, current primitive animation call site)
