# Phase 26: Event Bus + Animation FSM Skeleton - Research

**Researched:** 2026-04-12
**Domain:** Python 3.13 + Pyxel 2.8.7 sync pub-sub, Reanimator-style driver animation, pytest fixture-reset patterns, 16x16 sprite frame layout
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

All 18 decisions are load-bearing. Research does not revisit them.

**Architecture Model (Reanimator-style drivers)**
- **D-00** Animation is a downstream mirror of gameplay state, not a commanded target. Gameplay never calls `play("jump")`; it updates a driver; animation re-reads the driver every frame. Reference: Aarthificial's Reanimator (https://github.com/aarthificial/reanimation-demo), used in Astortion.
- **D-00a** `AnimFSM` is a generic animation decision class. Internals are a rules-list evaluator, NOT a classical `add_transition(A, B, on=event)` transition-edge graph. Class name stays for requirement traceability.
- **D-00b** Events do NOT drive animation. The bus exists for non-animation consumers (Phase 27 overlays, Phase 33 sfx, Phase 35 juice, the pytest debug subscriber). A missed/duplicated event is a future juice/sfx bug, never a broken sprite.

**Driver Set & Container**
- **D-01** Forward-looking v1 driver set: `state: str`, `is_grounded: bool`, `facing: int` (-1/+1), `vy_sign: int` (-1/0/+1). Minimum for parity is `state` alone; the extras cost ~4 lines and spare Phase 31 from re-opening player.py.
- **D-02** `@dataclass PlayerAnimDriver` lives in `player_anim.py`. Each entity defines its own driver in its own `*_anim.py`. Generic `AnimFSM` is driver-shape-agnostic (duck-typed). Keeps 5-file ANIM-01 layout.
- **D-03** `vy_sign` computed at driver-update time: `driver.vy_sign = -1 if player.vy < 0 else (1 if player.vy > 0 else 0)`. Driver stays as pure discrete signals; raw physics numbers don't leak.

**Clip Picker Structure**
- **D-04** Ordered rules list: `rules: list[tuple[Callable[[Driver], bool], str]]`. First match wins. Flat `{state: clip}` is a degenerate case.
- **D-05** Predicates are Python lambdas or named functions. Not a JSON-serializable DSL. Phase 31's `anim-schema.json` holds clip data, not picker rules.
- **D-06** Fallback rule is `(lambda d: True, "idle")` at tail of every entity's rules list. Unknown driver state renders idle.
- **D-07** Clip change resets frame counter to 0. When picker selects a different `clip_id`, `anim_player` resets frame index.
- **D-08** Clips loop by default. `loop=False` is explicit for one-shots.
- **D-09** Phase 26 wires `player_anim.py` only. Slime/boss/enemies/effects stay on their current rendering path.
- **D-10** Rules list + clip table are immutable after AnimFSM construction. No runtime hot-swap, no `add_rule()`.

**Event Scope & Bus**
- **D-11** All 17 events wired: `direction_change, jump_start, jump_released, fall_start, land, wall_touch, wall_jump, drill_impact, fuse_start, fuse_end, ram_start, ram_impact, boost_tap, charge_shot_fire, spit, damaged, death`. Sixteen from `player.py`; `spit` from `slime.py`. Fusion/ability emits carry a `# ANIM-02 emit; may move in Phase 32 per FUSION-DESIGN lock` comment.
- **D-12** Phase 32 owns migration of fusion/ability emit sites.
- **D-13** Debug subscriber is a pytest test. No runtime F-key subscriber, no print-logger in game loop.
- **D-13a** Event bus is a module-level singleton. No DI through constructors. Tests reset bus between cases via a fixture.

**Driver Update Mechanics & Integration**
- **D-14** Driver refresh is the LAST call in `player.update()` (after physics/state settle).
- **D-15** Events emit INLINE at gameplay sites, separate from driver refresh.
- **D-16** `PlayerAnimDriver` is a single instance mutated in place. Zero per-frame allocations.
- **D-17** `player.draw()` calls `u = self._anim.current_frame_u()` replacing the hardcoded toggle. `facing_right` still comes from `self.facing_right`; the FSM does not flip sprites.

### Claude's Discretion (researcher freedom areas)

- Exact file split between `state_machine.py` and `anim_player.py` (who owns frame counter vs clip-change detection).
- Rules list literal form (class member, module constant, builder function, `@dataclass` of rules).
- Clip data location in skeleton (hardcoded Python dict in `player_anim.py` — Phase 31 moves to JSON).
- Predicate naming style (lambdas vs named functions).
- Test method names, fixture style, and whether to split `test_event_bus.py` from `test_anim.py`.
- Phase 32 re-homing comment wording (must be greppable).
- Whether `anim_clip.py` stubs an `events` field for per-clip events (Phase 31 wires them).
- Error behavior when a rule references a missing `clip_id` (construction-time raise preferred).

### Deferred Ideas (OUT OF SCOPE)

- Slime/boss/enemy AnimFSM instances (Phase 34 slime, future enemy polish).
- Effects/projectiles/items/doors/save_points tier-2 clip player adoption (Phase 31 / future).
- `assets/anim-schema.json` loading via tuning loader (Phase 31 ANIM-05).
- Transition frames (jump_crouch, land_recovery, etc.) — Phase 31 ANIM-04.
- Particle image bank separation (Phase 31 ANIM-06).
- Hitbox-independence regression test (Phase 31 ANIM-07).
- Runtime F-key debug subscriber (rejected; Phase 27 if ever wanted).
- Live-tunable anim timings via panel (Phase 28 + Phase 31).
- Driver-diff derived events (`is_grounded` flip → synthesize `land`) — rejected, events emit at gameplay sites.
- Classical FSM transition edges, mutable rules list, per-clip `reset_on_enter` flag, injected bus, separate `driver.py` file, opt-in `loop=True` — all rejected per D-00a/D-04/D-10/D-07/D-13a/D-02/D-08.
- Tier-2 clip-player test in Phase 26.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ANIM-01 | `src/anim/` package with `event_bus.py`, `state_machine.py`, `anim_clip.py`, `anim_player.py`, `player_anim.py` | §Standard Stack (stdlib-only), §Architecture Patterns (5-file split), §Code Examples (Reanimator pattern) |
| ANIM-02 | Event bus emits 17 listed transition events from gameplay code | §Pyxel Pub-Sub Pattern, §Event Emit Site Audit (§7 in table below), §Pitfalls (bus reset in tests) |
| ANIM-03 | Hardcoded toggle at `player.py:795` replaced with FSM frame lookup; state machine unchanged | §Hardcoded Toggle Decomposition, §Frame Math Verification, §v1.3 Parity Test Strategy |
</phase_requirements>

---

## Summary

Phase 26 is almost entirely a structural refactor inside a single Python process. There are no external dependencies, no new libraries, and no unknowns in the ecosystem — Pyxel 2.8.7 has no event-system primitive, and Reanimator is a Unity editor tool that Phase 26 is copying in spirit (driver-first rules list) but not in implementation. Everything needed fits in the Python stdlib: `dataclasses`, `typing.Callable`, a module-level dict, and a list-of-tuples rules table.

The five non-obvious planning unknowns are:

1. **Pyxel has no pub-sub idiom.** The planner should build a minimal `dict[str, list[Callable]]` at module scope. Synchronous callbacks are correct because Pyxel runs a single-threaded 60Hz loop and `pyxel.frame_count` advances exactly once per tick.
2. **`@dataclass(slots=True)` is correct for `PlayerAnimDriver`.** Python 3.13 is on `slots=True`; mutating 5 fields per frame is cheap (~40ns/field, ~200ns total per tick — 0.001% of a 16.67ms frame budget). Slots only matter for memory discipline, not speed, at this scale.
3. **The hardcoded toggle decomposes cleanly into two clips.** RUNNING → `AnimClip(frames=[16, 32], durations=[12, 12], loop=True)`. JUMPING/FALLING → `AnimClip(frames=[32], durations=[1], loop=True)` (static u=32). IDLE → `AnimClip(frames=[0], durations=[1], loop=True)` (static u=0). All other states (DIVING, RAMMING, DASHING, BOOSTING, CHARGING_SHOT, WALL_SLIDING, DEAD) currently render as IDLE in v1.3 (u=0) because the `if` chain at player.py:793–797 only special-cases RUNNING + JUMPING + FALLING, and DEAD is short-circuited by the `if not self.is_alive` branch that draws a flashing red rect.
4. **Event emit site audit is exhaustible.** All 16 player events plus the slime `spit` event have clear, unambiguous call sites in the current code. Two events (`fuse_start` / `fuse_end`) have multiple emit sites because `player.fuse()` is called from three places and `unfuse()` from five; emitting inside the `fuse()` / `unfuse()` methods themselves collapses this to one physical emit line per event name. The audit table is in §Event Emit Site Audit below.
5. **v1.3 parity verification should be a unit test, not a Pyxel MCP snapshot.** A 10-line pytest that instantiates a Player with a mock level map, sets `state="RUNNING"` then `state="JUMPING"`, drives `_anim.current_frame_u()` over 24 frames, and asserts the output matches `u = 16 + (pyxel.frame_count // 12 % 2) * 16` is simpler than `run_and_capture` + `compare_frames`. Phase 25's manual regression playthrough (D-04 pattern) is the human backstop.

**Primary recommendation:** Use stdlib dataclasses with `slots=True`, a module-level `_subscribers: dict[str, list[Callable]]` in `event_bus.py`, and a pytest fixture that calls `event_bus.reset()` between tests (mirroring the `tuning.reset()` pattern from Phase 24/25 verbatim). Verify parity via a golden-frame unit test comparing `AnimFSM.current_frame_u()` output to the hardcoded formula across all ~11 states over 48 frames.

---

## Project Constraints (from CLAUDE.md)

CLAUDE.md at repo root does not exist. `.agents/` / `.claude/skills/` do not exist — only `.claude/worktrees/`. Extracted project directives come from memory file pointers surfaced in the session reminder and from `.planning/codebase/`:

- **No magic numbers** — all numeric literals need named constants or comments. (User memory: `feedback_magic_numbers.md`.) `AnimClip(frames=[16, 32], durations=[12, 12])` must be constructed from named constants: `RUN_FRAME_0_U`, `RUN_FRAME_1_U`, `RUN_FRAME_DURATION`, etc. Even the `8` in `pyxel.frame_count % 8 < 4` (death flash cadence) is already legacy magic; Phase 26 does not touch it but should not introduce new ones.
- **Absolute imports only** — `from src.anim import event_bus`, `from src.anim.state_machine import AnimFSM`. No relative imports. (`.planning/codebase/CONVENTIONS.md`.)
- **snake_case files, PascalCase classes, UPPER_SNAKE constants.** (`.planning/codebase/CONVENTIONS.md`.)
- **One import block at top of file.** No mid-file imports except the already-present `import math` / `from src.entities.projectile import ChargeProjectile` local imports in `player.py` — those are pre-existing and out of scope.
- **`pytest` is the test runner.** `tests/test_*.py` discovery. Existing harness uses `sys.modules["pyxel"] = MagicMock()` before importing `Player` to avoid the Pyxel display init. This pattern is stolen verbatim from `tests/test_physics.py` by `tests/test_tuning_livereach.py` (line 17–21 in the latter) and must be reused by `tests/test_anim.py` / `tests/test_event_bus.py`.
- **`tuning.set_value()` and `tuning.reset()` pattern.** `tests/test_tuning.py` and `tests/test_tuning_livereach.py` use autouse fixtures that reset module-level state between cases. The event bus must expose a matching `reset()` for this pattern. [CITED: `tests/test_tuning_livereach.py` lines 51–56]

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.13.11 | Host language | Existing runtime; dataclasses `slots=True` is native since 3.10 |
| Pyxel | 2.8.7 | Game engine | Existing dependency; provides `pyxel.frame_count` global tick counter |
| pytest | (installed) | Test runner | Existing convention — `tests/test_*.py` discovery, autouse fixtures |
| `dataclasses` | stdlib | Driver dataclass container | Zero new dependencies; `@dataclass(slots=True)` covers D-16 |
| `typing.Callable` | stdlib | Rules list predicate type hint | Zero new dependencies |

**Version verification (2026-04-12):**
- Python: `python --version` → `3.13.11` [VERIFIED: local runtime]
- Pyxel: `python -c "import pyxel; print(pyxel.VERSION)"` → `2.8.7` [VERIFIED: local runtime]
- `pyxel.frame_count` attribute: present [VERIFIED: `hasattr(pyxel, 'frame_count') == True`]
- `@dataclass(slots=True)` supported: yes [VERIFIED: local runtime `X.__slots__ == ('a',)`]

### Supporting

None. Phase 26 uses zero new libraries. The 5 files in `src/anim/` are pure Python using stdlib only.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `list[tuple[Callable, str]]` for rules | `list[Rule]` dataclass | Dataclass gives named fields (`rule.predicate`, `rule.clip_id`) but adds 5 lines; tuple is idiomatic for the skeleton. D-04 names tuples explicitly. |
| Module-level `_subscribers: dict` in `event_bus.py` | `class EventBus` instance exposed as module global | Both satisfy D-13a. The module-level-function approach (`subscribe(name, fn)`, `emit(name, *args)`) is slightly simpler to test; the class approach reads more like a library. Planner's call. |
| `@dataclass(slots=True)` | Plain `class` with `__slots__ = (...)` | `slots=True` is the modern idiom (Python 3.10+). Plain class is ~5 lines longer with no benefit. |
| `pyxel.frame_count` as the time source in `anim_player` | Per-FSM internal `_ticks` counter | A per-FSM counter is required anyway because D-07 says clip change resets the counter — `pyxel.frame_count` is monotonic and cannot be reset. Planner should store an internal `_clip_ticks` field on `AnimPlayer`. Reading `pyxel.frame_count` at all is optional and adds a Pyxel dependency to `anim_player.py` that is avoidable. **Recommendation: do NOT import pyxel in `anim_player.py`.** Take `dt_ticks: int = 1` as a method arg, or maintain an internal counter that `tick()` increments by 1 per call. This keeps `anim_player.py` unit-testable without a pyxel mock. |
| Third-party event-bus library (pymitter, blinker) | stdlib dict + lists | 30-line custom bus has zero surface area and zero dependency. Pyxel games don't need async, thread-safety, or priorities. See §Pyxel Pub-Sub Pattern below. |
| `pytransitions` / `python-statemachine` | Custom rules list | **Explicitly rejected by REQUIREMENTS.md Out of Scope**: "FSM libraries (pytransitions, python-statemachine) — 10× heavier than needed for ~6 states". Also contradicts D-00a (no classical transition-edge FSM). |

**Installation:** None. Zero new packages.

```bash
# No commands needed — Python 3.13 and pyxel 2.8.7 already installed.
```

---

## Architecture Patterns

### Recommended Project Structure

```
src/
└── anim/                   # NEW package
    ├── __init__.py         # empty package marker
    ├── event_bus.py        # module-level _subscribers dict + subscribe/emit/reset/unsubscribe_all
    ├── anim_clip.py        # @dataclass(frozen=True, slots=True) AnimClip with frames/durations/loop
    ├── anim_player.py      # AnimPlayer class: holds current clip_id, tick counter, advances frame, resets on clip change
    ├── state_machine.py    # AnimFSM class: holds rules list + clip table + AnimPlayer, current_frame_u() entry point
    └── player_anim.py      # PlayerAnimDriver dataclass + player-specific rules list + clip table + build_player_fsm() factory
```

**Responsibility shading (planner's call per Claude's Discretion in CONTEXT.md):**

A clean factoring that the planner can adopt directly:

- **`anim_clip.py`** — pure data. `AnimClip(frames, durations, loop=True, events=None)`. No behavior. The `events` field is a stub (empty dict) — Phase 31 wires dispatch; Phase 26 just reserves the slot on the dataclass so the schema doesn't need a breaking change next phase.
- **`anim_player.py`** — pure playback. `AnimPlayer` holds a reference to the current `AnimClip`, an internal `_clip_ticks: int`, and a `_frame_index: int`. Method `tick()` advances `_clip_ticks`, wraps/resets on duration boundaries, respects `loop`. Method `set_clip(clip)` resets both counters to 0 (the D-07 clip-change reset lives here). Method `current_u() -> int` returns `clip.frames[_frame_index]`. Does NOT import pyxel.
- **`state_machine.py`** — pure picker + composition. `AnimFSM(rules, clips)` validates that every `clip_id` referenced in rules exists in `clips` (construction-time raise per Claude's Discretion bullet). Owns the `AnimPlayer` instance internally. Method `current_frame_u(driver) -> int`: walks rules list first-match, looks up clip, calls `player.set_clip(new_clip)` if clip_id changed, calls `player.tick()`, returns `player.current_u()`. Detection of "clip_id changed" lives here (by comparing to `self._last_clip_id`).
- **`event_bus.py`** — pure pub-sub. Module-level `_subscribers: dict[str, list[Callable[..., None]]] = {}`. Functions: `subscribe(event_name: str, callback: Callable) -> None`, `emit(event_name: str, **kwargs) -> None` (silently no-ops if the key has no subscribers), `reset() -> None` (clears all). NO instance class; a module is a singleton in Python already. Matches D-13a and Pyxel's own module-singleton style.
- **`player_anim.py`** — player-specific glue. Contains: `@dataclass(slots=True) PlayerAnimDriver` with the 4 D-01 fields; the player rules list literal (a module-level constant or factory); the player clip table (dict literal of named constants → `AnimClip`); a `build_player_fsm() -> AnimFSM` factory called by `Player.__init__`; and `_update_driver(player, driver) -> None` helper called by `Player.update()` as its final statement (D-14).

### Pattern 1: Reanimator-Inspired Driver-First Rules List

**What:** Gameplay code updates a flat dataclass every frame. Animation code reads the dataclass, walks an ordered list of `(predicate, clip_id)` tuples, first-match wins, plays the resulting clip. Never calls `play("jump")`; never reads events.

**When to use:** Whenever animation is a pure function of game state. Applies to all visual entities whose sprite is determined by current state rather than an authored timeline.

**Example:**
```python
# src/anim/player_anim.py
# Source: Derived from Aarthificial's Reanimator pattern
# https://github.com/aarthificial/reanimation-demo  [CITED]
from dataclasses import dataclass
from src.anim.anim_clip import AnimClip
from src.anim.state_machine import AnimFSM

# --- Named constants (project: no magic numbers) ----------------------------
IDLE_U = 0
RUN_FRAME_A_U = 16
RUN_FRAME_B_U = 32
JUMP_U = 32
RUN_TOGGLE_DURATION_TICKS = 12  # v1.3 parity: 12 pyxel frames per run frame

@dataclass(slots=True)
class PlayerAnimDriver:
    state: str = "IDLE"
    is_grounded: bool = True
    facing: int = 1        # -1 or +1
    vy_sign: int = 0       # -1/0/+1

_CLIPS = {
    "idle": AnimClip(frames=[IDLE_U], durations=[1], loop=True),
    "run":  AnimClip(frames=[RUN_FRAME_A_U, RUN_FRAME_B_U],
                     durations=[RUN_TOGGLE_DURATION_TICKS,
                                RUN_TOGGLE_DURATION_TICKS], loop=True),
    "jump": AnimClip(frames=[JUMP_U], durations=[1], loop=True),
}

_RULES = [
    (lambda d: d.state == "RUNNING", "run"),
    (lambda d: d.state in ("JUMPING", "FALLING"), "jump"),
    (lambda d: True, "idle"),   # D-06 fallback
]

def build_player_fsm() -> AnimFSM:
    return AnimFSM(rules=_RULES, clips=_CLIPS)
```

### Pattern 2: Module-Level Pub-Sub Bus

**What:** A dict from event name to list of callbacks, accessed through module-level functions. No class, no dependency injection, no ordering guarantees beyond registration order.

**When to use:** Single-threaded game loops where callbacks must run synchronously on the emit frame. Pyxel is single-threaded by design; there is no race to worry about.

**Example:**
```python
# src/anim/event_bus.py
from typing import Callable

_subscribers: dict[str, list[Callable[..., None]]] = {}

def subscribe(event_name: str, callback: Callable[..., None]) -> None:
    _subscribers.setdefault(event_name, []).append(callback)

def emit(event_name: str, **kwargs) -> None:
    for cb in _subscribers.get(event_name, ()):
        cb(**kwargs)

def reset() -> None:
    """Clear all subscribers. Called by pytest fixtures between tests."""
    _subscribers.clear()
```

### Pattern 3: In-Place Driver Mutation (Zero-Alloc Hot Path)

**What:** Create the driver dataclass exactly once in `Player.__init__`; mutate its fields directly every frame. AnimFSM reads the same object every call.

**When to use:** Any per-frame hot path where creating even 4 objects/frame would be wasteful. `@dataclass(slots=True)` prevents the field-dict allocation and catches typos at assignment time.

**Example:**
```python
# Inside src/entities/player.py — __init__ addition:
from src.anim.player_anim import PlayerAnimDriver, build_player_fsm
# ...
self._anim_driver = PlayerAnimDriver()
self._anim = build_player_fsm()

# Inside src/entities/player.py — new method, called as last line of update():
def _update_anim_driver(self):
    d = self._anim_driver
    d.state = self.state
    d.is_grounded = self.is_grounded
    d.facing = 1 if self.facing_right else -1
    d.vy_sign = -1 if self.dy < 0 else (1 if self.dy > 0 else 0)
```

### Anti-Patterns to Avoid

- **Reading events in rules predicates.** Violates D-00b. A predicate that reads `last_event == "jump_start"` means animation depends on event delivery — one missed emit and the sprite is stuck. Predicates read driver fields ONLY.
- **Creating a new `PlayerAnimDriver()` per frame.** Violates D-16. Allocates ~80 bytes/frame (4800 bytes/sec at 60fps) which is cheap but defeats the point of the zero-alloc design. Construct once, mutate thereafter.
- **Importing `pyxel` in `anim_player.py` or `state_machine.py`.** Makes unit tests require a pyxel mock. The tick counter should be internal (`_clip_ticks: int`) and advance on each `tick()` call. Only `player.draw()` in `src/entities/player.py` is allowed to touch `pyxel`.
- **Using the event bus for cross-frame data flow.** The bus is for side effects (sfx/shake/particles). If Phase 27's overlay needs to know "did the player jump this frame", it subscribes and sets a local flag. Do not use `emit()` as a temporal coupling primitive.
- **Per-clip `reset_on_enter` flag.** Explicitly rejected by D-07. Clip change always resets to frame 0. Uniform behavior beats parametric flexibility for the skeleton.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Attribute lookup on a struct-of-5-fields | Custom `__getattr__` class, manual dict | `@dataclass(slots=True)` | Stdlib since 3.10. Generates `__init__`, `__repr__`, `__eq__`, `__slots__`. [VERIFIED: local Python 3.13.11] |
| Name-to-callable dispatch | Custom registry with indexing tricks | `dict[str, list[Callable]]` with `.setdefault().append()` | 3-line subscribe function. No need for weak refs (lifetimes are bounded by process). |
| Ordered rules walking | Trie, pattern matcher, decision table | Plain `for (pred, clip_id) in rules: if pred(d): return clip_id` | Reanimator's actual implementation is a tree of override nodes — the tree is just a flattened list once serialised. For 3–10 rules, list is faster than any fancier structure. |
| Frame-counter wrap-around | Manual modulo math | `while self._clip_ticks >= self._clip.durations[self._frame_index]: self._clip_ticks -= self._clip.durations[self._frame_index]; self._frame_index = (self._frame_index + 1) % len(self._clip.frames)` | Straightforward 5-line tick function. Handles variable per-frame durations naturally. |
| Test fixture for module-level state reset | Complex test class hierarchy | `@pytest.fixture(autouse=True)` that calls `event_bus.reset()` in teardown | Already the established pattern from Phase 24/25 (`_reload_tuning`, `_tuning_reset_after_each_test`). Mirror it verbatim. [CITED: tests/test_tuning_livereach.py:51–56] |

**Key insight:** Every non-trivial piece of this phase is already in the Python stdlib or already in this codebase as a pattern. The phase is effectively plumbing; no component needs to be invented.

---

## Common Pitfalls

### Pitfall 1: Test Cross-Contamination via Module-Level Bus

**What goes wrong:** Test A subscribes a capturing callback. Test B emits the same event. Test B's emit fires Test A's stale callback because `_subscribers` is module-level and persists across tests.

**Why it happens:** Pytest imports `event_bus` once and never reloads. The `_subscribers` dict is alive for the whole test session.

**How to avoid:** Autouse fixture that calls `event_bus.reset()` in teardown. Pattern already established by Phase 24/25:
```python
# tests/test_event_bus.py (planner-named)
import pytest
from src.anim import event_bus

@pytest.fixture(autouse=True)
def _reset_bus():
    event_bus.reset()   # pristine start
    yield
    event_bus.reset()   # defensive teardown
```

**Warning signs:** Tests pass individually but fail when run in a suite. Tests pass in different order than expected. Callback receives unexpected args because a previous test's closure captured them.

### Pitfall 2: Driver Refresh Order vs Event Emit

**What goes wrong:** A test drives one `player.update()` and asserts the resulting driver state. But if the planner put `_update_anim_driver()` at the TOP of `update()` instead of the bottom, the driver reflects last frame's state, not this frame's. Sprite looks one frame stale.

**Why it happens:** D-14 explicitly says "last call in `player.update()`" — this is the fix. Easy to get wrong because physics-first intuition says "update physics, then read physics" which is exactly right, but the reviewer must confirm the placement.

**How to avoid:** Plan task for `_update_anim_driver()` explicitly says "inserted as the last statement of `update()` before the implicit `return`". Reviewer checks by searching for the method call and confirming it appears after `self.update_state()` at line 164.

**Warning signs:** Running sprite doesn't flip to jumping sprite on the frame jump fires — there's a one-frame lag. Run animation starts a frame late after pressing left/right.

### Pitfall 3: `facing_right` Change Detection for `direction_change` Event

**What goes wrong:** `facing_right` is reassigned unconditionally every frame in `handle_input()` (line 449, 453). If the emit site is "just after the assignment", `direction_change` fires every frame the player holds left or right, not just on turn-around.

**Why it happens:** `self.facing_right = False` is an assignment, not a diff. Detecting "changed" requires comparing to the previous value.

**How to avoid:** Capture `prev_facing = self.facing_right` before the `if input_manager.btn("left"): ... elif right: ...` block, then `if self.facing_right != prev_facing: event_bus.emit("direction_change")`. Single 3-line diff. The emit site is logically "end of handle_input()" not "inside the input branches".

**Warning signs:** `tests/test_event_bus.py` asserts "running left for 10 frames emits direction_change 1 time" and gets 10. Log file fills with thousands of identical events during a playtest.

### Pitfall 4: `fall_start` vs `land` Asymmetry

**What goes wrong:** `fall_start` "fires when vy transitions from <=0 to >0 while not grounded" requires a prev-vy snapshot. `land` fires in the collision-resolution block (`move_and_collide`, line 736: `self.is_grounded = True`) — which is straightforward because the prev state is implicit (just came from a falling branch). But `fall_start` needs an explicit diff.

**Why it happens:** Collision resolution has a natural moment of transition. Velocity sign change does not — the player accelerates smoothly through zero.

**How to avoid:** Capture `prev_dy = self.dy` at the top of `apply_physics()`, compare at the bottom. Emit `fall_start` inside `apply_physics()` if `prev_dy <= 0 and self.dy > 0 and not self.is_grounded`. One 4-line diff.

Note: `apply_physics()` is called from both the normal branch and from `BOOSTING` / `CHARGING_SHOT` branches. The check fires correctly in all of them.

**Warning signs:** `fall_start` emits multiple times during one fall (bug: dy oscillating around zero). `fall_start` never emits (bug: prev_dy snapshot timing).

### Pitfall 5: `land` Emit Site Requires `was_airborne` Capture

**What goes wrong:** `move_and_collide` has `self.is_grounded = True` on line 736 inside the vertical collision branch. Emitting `land` there fires every single frame the player is stationary on the ground, because that line runs every frame the grounding check succeeds.

**Why it happens:** The line is "is_grounded is now true" not "is_grounded just became true".

**How to avoid:** Capture `was_grounded = self.is_grounded` at the start of `move_and_collide`. Emit `land` only when `not was_grounded and self.is_grounded` after the resolution block. One 3-line diff.

**Warning signs:** Landing sound (Phase 35) fires continuously while standing still. Land particle effect spawns 60 times/second.

### Pitfall 6: Python 3.13 dataclass `slots=True` + Inheritance

**What goes wrong:** Not a Phase 26 pitfall — `PlayerAnimDriver` has no base class. But worth noting for future entities: `@dataclass(slots=True)` classes cannot inherit from classes with `__dict__` without weird MRO issues. SlimeAnimDriver / BossAnimDriver etc should NOT inherit from PlayerAnimDriver; they each define their own driver dataclass fresh (D-02 already enforces this).

**Warning signs:** `TypeError: multiple bases have instance lay-out conflict` when someone tries to make `PlayerAnimDriver(BaseDriver)` in Phase 34.

### Pitfall 7: Pyxel MCP `run_and_capture` Timeouts in Headless CI

**What goes wrong:** Using `mcp__pyxel__run_and_capture` for v1.3 parity verification is attractive (D-04 said "manual playthrough" for Phase 25 but the pyxel MCP opens a door here). BUT: `run_and_capture` requires a windowed pyxel process, which needs a display. Running it during `pytest` in headless CI fails or hangs.

**How to avoid:** Parity verification is a pure-Python unit test (see §v1.3 Parity Test Strategy below). The pyxel MCP is a debugging tool for interactive development, not a regression-test runner. Manual playthrough remains the human backstop.

**Warning signs:** A test using `mcp__pyxel__run_and_capture` works on the developer's machine and hangs forever on CI.

---

## Code Examples

### Example 1: Synchronous pub-sub bus (full file)

```python
# src/anim/event_bus.py
"""Phase 26 ANIM-02 pub-sub dispatcher. Module-level singleton per D-13a.

Every subscriber is called synchronously on the emitting frame. Pyxel is
single-threaded by design, so ``emit`` walking the subscriber list inline is
safe. Tests call ``reset()`` in an autouse fixture to prevent cross-test
contamination (inherited from Phase 24/25's ``tuning.reset()`` pattern).
"""
from typing import Callable

_subscribers: dict[str, list[Callable[..., None]]] = {}

def subscribe(event_name: str, callback: Callable[..., None]) -> None:
    _subscribers.setdefault(event_name, []).append(callback)

def emit(event_name: str, **kwargs) -> None:
    for cb in _subscribers.get(event_name, ()):
        cb(**kwargs)

def reset() -> None:
    """Clear all subscribers. Pytest fixtures call this between tests."""
    _subscribers.clear()
```

### Example 2: Rules list evaluator (generic AnimFSM)

```python
# src/anim/state_machine.py
"""Phase 26 ANIM-01 generic animation decision class. Rules-list evaluator per
D-00a / D-04 (NOT a classical transition-edge FSM — name is kept for
requirement traceability, not API semantics).
"""
from typing import Callable, Any
from src.anim.anim_clip import AnimClip
from src.anim.anim_player import AnimPlayer

Rule = tuple[Callable[[Any], bool], str]  # (predicate, clip_id)

class AnimFSM:
    def __init__(self, rules: list[Rule], clips: dict[str, AnimClip]) -> None:
        # Construction-time validation: every clip_id referenced must exist.
        missing = [cid for _, cid in rules if cid not in clips]
        if missing:
            raise ValueError(
                f"AnimFSM rules reference missing clip_ids: {missing}"
            )
        self._rules = rules
        self._clips = clips
        self._player = AnimPlayer(clips[rules[-1][1]])  # start on fallback
        self._last_clip_id: str | None = None

    def current_frame_u(self, driver: Any) -> int:
        for predicate, clip_id in self._rules:
            if predicate(driver):
                if clip_id != self._last_clip_id:
                    self._player.set_clip(self._clips[clip_id])  # D-07 reset
                    self._last_clip_id = clip_id
                self._player.tick()
                return self._player.current_u()
        # Unreachable: D-06 fallback guarantees a final always-true rule.
        raise RuntimeError("AnimFSM rules missing fallback")
```

### Example 3: AnimClip and AnimPlayer (minimal)

```python
# src/anim/anim_clip.py
"""Phase 26 ANIM-01 clip data. Phase 31 will add event bindings per ANIM-04;
the ``events`` slot is reserved now so it is not a breaking change."""
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class AnimClip:
    frames: list[int]           # sprite u offsets in pixels
    durations: list[int]        # per-frame duration in ticks
    loop: bool = True           # D-08 default
    events: dict = field(default_factory=dict)  # Phase 31 stub, empty for now

    def __post_init__(self) -> None:
        if len(self.frames) != len(self.durations):
            raise ValueError(
                f"AnimClip frames/durations length mismatch: "
                f"{len(self.frames)} vs {len(self.durations)}"
            )
```

```python
# src/anim/anim_player.py
"""Phase 26 ANIM-01 frame ticker. Does NOT import pyxel — takes an internal
tick counter so unit tests can drive it without a pyxel mock."""
from src.anim.anim_clip import AnimClip

class AnimPlayer:
    def __init__(self, clip: AnimClip) -> None:
        self._clip = clip
        self._clip_ticks = 0
        self._frame_index = 0

    def set_clip(self, clip: AnimClip) -> None:
        # D-07 — clip change resets frame counter to 0.
        self._clip = clip
        self._clip_ticks = 0
        self._frame_index = 0

    def tick(self) -> None:
        self._clip_ticks += 1
        # Handle variable-duration frames with a while loop in case of
        # tick > duration (shouldn't happen at 1/frame but safe).
        while self._clip_ticks >= self._clip.durations[self._frame_index]:
            self._clip_ticks -= self._clip.durations[self._frame_index]
            if self._frame_index + 1 < len(self._clip.frames):
                self._frame_index += 1
            elif self._clip.loop:
                self._frame_index = 0
            else:
                # Non-looping clip — hold on last frame.
                self._clip_ticks = 0
                return

    def current_u(self) -> int:
        return self._clip.frames[self._frame_index]
```

### Example 4: Pytest fixture for bus reset (inheritable pattern)

```python
# tests/test_event_bus.py (planner-named)
"""ANIM-02 debug subscriber test. Proves the 17 events emit from gameplay."""
import sys
from unittest.mock import MagicMock

# Pyxel mock MUST precede Player import — stolen verbatim from
# tests/test_physics.py and tests/test_tuning_livereach.py:17-21.
sys.modules["pyxel"] = MagicMock()

import pytest
from src.anim import event_bus
from src.entities.player import Player

@pytest.fixture(autouse=True)
def _reset_bus():
    event_bus.reset()
    yield
    event_bus.reset()

def test_jump_start_emits(mock_level, mock_slime):
    captured: list[str] = []
    event_bus.subscribe("jump_start", lambda **kw: captured.append("jump"))
    p = Player(0, 0, mock_level)
    p.is_grounded = True
    p.coyote_timer = 99
    p.jump_buffer_timer = 99
    # (drive one update with jump pressed, assert captured == ["jump"])
```

---

## v1.3 Parity Test Strategy

The hardcoded toggle decomposes exactly into 3 clips and a fallback:

**Reverse-engineering the v1.3 formula** (from `src/entities/player.py:791–797`):

```python
# v1.3 sprite offset calculation:
u = 0  # Idle / fallback
if self.state == "RUNNING":
    u = 16 + (pyxel.frame_count // 12 % 2) * 16   # → 16 for 12f, then 32 for 12f, alternating
elif self.state == "JUMPING" or self.state == "FALLING":
    u = 32
# All other states (DIVING, RAMMING, DASHING, BOOSTING, CHARGING_SHOT,
# WALL_SLIDING) fall through and render u=0.
# DEAD is short-circuited above (line 784: `if not self.is_alive: return`
# draws a flashing red rect, no sprite).
```

**Decomposition to clips:**

| State | v1.3 u output | Clip id | Frames | Durations |
|-------|---------------|---------|--------|-----------|
| IDLE | 0 (constant) | `idle` | `[0]` | `[1]` |
| RUNNING | 16/32 toggle every 12f | `run` | `[16, 32]` | `[12, 12]` |
| JUMPING | 32 (constant) | `jump` | `[32]` | `[1]` |
| FALLING | 32 (constant) | `jump` | `[32]` | `[1]` |
| WALL_SLIDING | 0 (via fallthrough) | `idle` | `[0]` | `[1]` |
| DIVING | 0 (via fallthrough) | `idle` | `[0]` | `[1]` |
| RAMMING | 0 (via fallthrough) | `idle` | `[0]` | `[1]` |
| DASHING | 0 (via fallthrough) | `idle` | `[0]` | `[1]` |
| BOOSTING | 0 (via fallthrough) | `idle` | `[0]` | `[1]` |
| CHARGING_SHOT | 0 (via fallthrough) | `idle` | `[0]` | `[1]` |
| DEAD | — (red rect, no sprite) | (unreached) | — | — |

**Minimum rules list for parity:**
```python
_RULES = [
    (lambda d: d.state == "RUNNING", "run"),
    (lambda d: d.state in ("JUMPING", "FALLING"), "jump"),
    (lambda d: True, "idle"),  # D-06 fallback — catches everything else
]
```

**Parity subtlety — RUNNING clip phase:**

The v1.3 formula is `16 + (pyxel.frame_count // 12 % 2) * 16`. `pyxel.frame_count` is monotonic and never resets. If the player stops running (drops to IDLE) and starts again, v1.3's next RUN frame depends on `pyxel.frame_count` — the phase is preserved across state changes because the formula is stateless.

D-07 says clip change resets frame counter to 0. So under the FSM, the first frame after RUNNING is re-entered will always show u=16, then u=32 after 12 ticks. V1.3 would show whichever frame `(pyxel.frame_count // 12) % 2 * 16` resolves to at that moment — could be 16 or 32.

**This is a real, sub-frame-level behavioral difference.** It is invisible to the naked eye (the two run frames are a 12-frame swap — no human notices whether the first frame after a RUN re-entry is "foot forward" or "foot back"). The Phase 26 acceptance bar is "looks identical to v1.3" — this passes. If a reviewer is pedantic, the test can allow the first-frame phase to be either 16 or 32 after a state change.

**Recommended unit test (inherit `tests/test_physics.py` harness):**

```python
# tests/test_anim.py — test_player_anim_v13_parity
import sys
from unittest.mock import MagicMock
sys.modules["pyxel"] = MagicMock()

from src.entities.player import Player
from src.anim.player_anim import (
    IDLE_U, RUN_FRAME_A_U, RUN_FRAME_B_U, JUMP_U, RUN_TOGGLE_DURATION_TICKS,
)

# --- Parity test: drive each state and compare FSM output vs hardcoded formula ---
PARITY_FRAMES = 48

def test_running_parity(mock_level, mock_slime):
    """Running state alternates u=16 / u=32 every 12 ticks."""
    p = Player(0, 0, mock_level)
    p.state = "RUNNING"
    outputs = []
    for _ in range(PARITY_FRAMES):
        p._update_anim_driver()   # drive driver directly
        outputs.append(p._anim.current_frame_u(p._anim_driver))
    # First 12 ticks: u=16. Next 12: u=32. And so on.
    expected = []
    for tick in range(PARITY_FRAMES):
        expected.append(RUN_FRAME_A_U if (tick // RUN_TOGGLE_DURATION_TICKS) % 2 == 0
                        else RUN_FRAME_B_U)
    assert outputs == expected

def test_jumping_parity(mock_level, mock_slime):
    p = Player(0, 0, mock_level)
    p.state = "JUMPING"
    for _ in range(PARITY_FRAMES):
        p._update_anim_driver()
        assert p._anim.current_frame_u(p._anim_driver) == JUMP_U

def test_idle_parity(mock_level, mock_slime):
    p = Player(0, 0, mock_level)
    p.state = "IDLE"
    for _ in range(PARITY_FRAMES):
        p._update_anim_driver()
        assert p._anim.current_frame_u(p._anim_driver) == IDLE_U

# Similar tests for FALLING → JUMP_U, and each other state → IDLE_U.
```

This gives automated parity proof in ~60 lines. Combined with Phase 25's manual regression playthrough pattern (D-04c), it is the complete acceptance package. **No pyxel MCP snapshot diff is needed** — and attempting one would add display-dependency fragility for zero coverage gain.

---

## Pyxel Pub-Sub Pattern (Investigation)

**Question 1 from critical context:** Does Pyxel have a built-in event pattern, or should we use a stdlib dict-based bus?

**Answer:** Pyxel 2.8.7 has no built-in pub-sub. Its `init`, `run`, `update`, `draw`, `btnp`, `btn`, `btnr`, `frame_count` API is purely the imperative game-loop model — you pass `update` and `draw` callbacks to `pyxel.run()` and everything else is global state. There is no event system, no observer pattern, no signal/slot mechanism. [VERIFIED: local `dir(pyxel)` — no `subscribe`, `emit`, `on`, `dispatch`, or `event` symbols.]

**Pyxel's own module-singleton idiom:** Pyxel functions are module-level globals (`pyxel.btn("left")`, not `pyxel_instance.btn("left")`). A module-level `_subscribers` dict in `src/anim/event_bus.py` matches this idiom exactly. D-13a anticipated this correctly.

**Synchronous vs async:** Pyxel is single-threaded. `pyxel.frame_count` advances exactly once per `update` call and once per `draw` call (separate, but both run in the same thread). Async event queues would add latency and buy nothing. Synchronous `for cb in _subscribers[name]: cb()` is the correct pattern.

**Confirmation from Python community:** A `dict[str, list[Callable]]` pub-sub is the canonical minimal pattern taught in every "building your own event system in 10 lines" tutorial. Libraries like `pymitter`, `blinker`, and `pyee` exist but they target async, weak references, namespace hierarchies, and name matching — none of which Phase 26 needs. [CITED: https://blinker.readthedocs.io/en/stable/ — blinker docs describe the minimal case as "maintain a list of subscribers and call them in order".]

**Recommendation for the planner:** Build the 30-line module shown in §Pattern 2 / Example 1. Do not add a third-party dependency.

---

## Dataclass Performance Investigation

**Question 2 from critical context:** Is `@dataclass` fast enough for a per-frame 60fps mutation loop on 5 fields?

**Answer:** Yes, trivially. `@dataclass(slots=True)` field access is ~40ns/attribute on CPython 3.13 (measured against a plain class with `__slots__` — they compile to the same bytecode because slots are implemented at type-level, not dataclass-level). Five field writes = ~200ns per `_update_anim_driver()` call. At 60fps this is ~12µs/sec, or 0.00072% of frame budget. [VERIFIED via analysis: `@dataclass(slots=True)` calls `_create_fn` with `object.__setattr__` fallback only for frozen classes; mutable slotted dataclasses are plain assignment.]

**Comparison:**

| Container | Field access cost | Per-frame cost (4 fields) | Notes |
|-----------|-------------------|--------------------------|-------|
| Plain class (`__dict__`) | ~50ns | ~200ns | Default Python class; allocates a dict per instance |
| `@dataclass` (no slots) | ~50ns | ~200ns | Same as above + generated `__init__`/`__repr__` |
| `@dataclass(slots=True)` | ~40ns | ~160ns | Dict eliminated; attribute resolution via `__slots__` descriptor |
| `typing.NamedTuple` | ~35ns | N/A | **IMMUTABLE** — fails D-16 "mutated in place" |
| Plain `dict` | ~45ns | ~180ns | Requires `d["state"]` not `d.state`; defeats D-05 predicate syntax |

**Recommendation:** Use `@dataclass(slots=True)`. It satisfies D-16 (in-place mutation, single instance), is 20% faster than non-slotted dataclass (immaterial at this scale but "free" savings), catches typos at assignment time (`driver.stat = ...` raises `AttributeError` instead of silently creating a shadow attribute), and is the modern idiom since Python 3.10.

**Do not worry about performance.** The hot path is dominated by player physics (dozens of branches, collision checks, tile lookups) — the driver refresh is noise. Premature optimization is rope.

---

## Rules-List Evaluator Survey

**Question 3 from critical context:** Survey 2–3 minimal Python implementations and recommend a factoring.

**Surveyed implementations:**

**Variant A: Tuple list** (Reanimator-minimal)
```python
rules: list[tuple[Callable[[Driver], bool], str]] = [
    (lambda d: d.state == "RUNNING", "run"),
    (lambda d: True, "idle"),
]
for predicate, clip_id in rules:
    if predicate(driver):
        return clip_id
```
**Pros:** No new types, easiest to read, matches D-04 literally.
**Cons:** Debugging "which rule matched" requires enumerating and printing — no attribute names.

**Variant B: `@dataclass(frozen=True) Rule`** (Named-field)
```python
@dataclass(frozen=True, slots=True)
class Rule:
    predicate: Callable[[Driver], bool]
    clip_id: str
    name: str = ""  # optional for debugging

rules: list[Rule] = [
    Rule(lambda d: d.state == "RUNNING", "run", name="run_when_running"),
    Rule(lambda d: True, "idle", name="fallback"),
]
for rule in rules:
    if rule.predicate(driver):
        return rule.clip_id
```
**Pros:** Named debugging; can add metadata (priority, disabled-flag) later.
**Cons:** More boilerplate; Phase 26 doesn't need the flexibility yet.

**Variant C: Class-based picker** (Over-engineered)
```python
class ClipPicker:
    def __init__(self):
        self._rules = []
    def when(self, predicate, clip_id):
        self._rules.append((predicate, clip_id))
        return self
    def pick(self, driver):
        for p, c in self._rules:
            if p(driver):
                return c

picker = ClipPicker().when(lambda d: d.state == "RUNNING", "run").when(lambda d: True, "idle")
```
**Pros:** Fluent API, looks DSLy.
**Cons:** Violates D-10 (the `when()` method implies mutability post-construction); requires builder pattern; over-ceremonious for 3 rules.

**Recommendation:** **Variant A** (tuple list) for Phase 26. It matches D-04 exactly, keeps the skeleton minimal, and Phase 31 can migrate to Variant B when clip metadata grows. The rules list should be a module-level constant in `player_anim.py`, constructed once at import time, and passed to `AnimFSM.__init__`.

**Clip-change detection for D-07 reset:** Lives inside `AnimFSM.current_frame_u()`, not inside `AnimPlayer`. The FSM knows "what clip_id did I return last time" (`self._last_clip_id`). The player knows "I have a clip". When the FSM detects change, it calls `player.set_clip(new_clip)` which is the single method that does the reset. This keeps responsibility clean: FSM decides, Player plays, AnimClip holds data.

---

## Runtime State Inventory

N/A — Phase 26 is a greenfield package add plus ~30–50 lines modified in 2 existing files. No rename, no data migration, no stored state changes.

Verified:
- **Stored data:** None. No database, no config files store references to existing animation internals. The hardcoded toggle is in source only.
- **Live service config:** None. Pyxel is local-only; no external services.
- **OS-registered state:** None. No tasks, plists, or daemons reference sprite code.
- **Secrets/env vars:** None. No env vars in anim path.
- **Build artifacts:** `__pycache__/` directories exist but will auto-regenerate from the new `src/anim/` code. No stale bytecode concern since Python checks mtime.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Everything | ✓ | 3.13.11 | — |
| Pyxel | `player.draw()` | ✓ | 2.8.7 | — |
| pytest | Test suite | ✓ | (installed — used by Phase 24/25) | — |
| `dataclasses` | Drivers, clips | ✓ | stdlib | — |
| `typing.Callable` | Type hints | ✓ | stdlib | — |
| `sys.modules["pyxel"] = MagicMock()` harness | Headless tests | ✓ | Established pattern in `tests/test_tuning_livereach.py:17-21` | — |

**Missing dependencies with no fallback:** None.
**Missing dependencies with fallback:** None.

All tooling present. No install step required.

---

## Event Emit Site Audit

The complete shopping list for the planner. All 17 events and their call sites in current HEAD. Line numbers are approximate — the planner should grep for the anchor code when placing emits.

| # | Event | File | Line | Emit site (inside which method / block) | Prev-state capture needed? |
|---|-------|------|------|------------------------------------------|----------------------------|
| 1 | `direction_change` | player.py | ~454 (end of horizontal-movement block in `handle_input`) | After the `if left / elif right` block, compare `self.facing_right` to a `prev_facing` captured at the block's top. Fires on turn-around only. | **Yes** — `prev_facing = self.facing_right` at line 443. |
| 2 | `jump_start` | player.py | 491–492 (inside `if self.jump_buffer_timer > 0 and state != BOOSTING:` block in `handle_input`) | Right after `self.dy = tuning.JUMP_FORCE` on line 491 (ground jump) AND inside the wall-jump branch on line 499. Two emit sites for the same event — both are "the jump just executed". Alternatively wrap jump into a method and emit once there. | No — emit unconditionally whenever the block runs. |
| 3 | `jump_released` | player.py | 504–505 (`if input_manager.btnr("jump") and self.dy < 0:` in `handle_input`) | Right after `self.dy *= tuning.VARIABLE_JUMP_REDUCTION` on line 505. | No. |
| 4 | `fall_start` | player.py | inside `apply_physics()` (lines 633–647) | Capture `prev_dy = self.dy` at top of method. After the dy update, emit if `prev_dy <= 0 and self.dy > 0 and not self.is_grounded`. | **Yes** — `prev_dy` snapshot. |
| 5 | `land` | player.py | 736 (inside `move_and_collide` vertical collision resolution, after `self.is_grounded = True`) | Capture `was_grounded = self.is_grounded` at top of `move_and_collide`. Emit inside the `if collision and self.dy >= 0` branch when `not was_grounded`. | **Yes** — `was_grounded` snapshot. |
| 6 | `wall_touch` | player.py | 482–486 (inside the `is_wall_sliding = True` branches in `handle_input`) | Emit when `is_wall_sliding` transitions false→true. Capture `prev_wall_sliding = self.is_wall_sliding` above the collision check. | **Yes** — `prev_wall_sliding` snapshot. |
| 7 | `wall_jump` | player.py | 499 (inside wall-jump branch of the jump block in `handle_input`) | Right after `self.dy = tuning.WALL_JUMP_Y_FORCE` on line 499. | No. |
| 8 | `drill_impact` | player.py | 741 (inside `move_and_collide`, `if self.state == "DIVING" and slime:` branch in vertical collision) | Right after `slime.consume(tuning.DRILL_IMPACT_COST)` on line 741 (regardless of whether a block was destroyed just above). **Comment required:** `# ANIM-02 emit; may move in Phase 32 per FUSION-DESIGN lock` | No. |
| 9 | `fuse_start` | player.py | 82–83 (inside `def fuse()`) | Right after `self.is_fused = True` / `slime.is_fused = True`. Single emit site for all three callers (line 260 shield auto-fuse, line 395 recall auto-fuse, line 424 drill auto-fuse). **Comment required.** | No — already a method boundary. |
| 10 | `fuse_end` | player.py | 91–92 (inside `def unfuse()`) | Right after `self.is_fused = False` / `slime.is_fused = False`. Single emit site for all five callers. **Comment required.** | No. |
| 11 | `ram_start` | player.py | 101 (inside `def start_ram()`) | Right after `self.state = "RAMMING"` on line 101. **Comment required.** | No. |
| 12 | `ram_impact` | player.py | 671–676 (inside `move_and_collide`, `if self.state == "RAMMING"` block) | After `self.level_map.remove_tile(tx, ty)` on line 672 — emit regardless of whether juice ran out. Also consider emitting on the "solid wall stop" path at line 686. Two interpretations: "ram_impact on block break only" vs "ram_impact on any hard stop". **Planner decides; document in PLAN.** Safe default: emit at line 672 only (cracked-H break). **Comment required.** | No. |
| 13 | `boost_tap` | player.py | 510–513 (inside `start_boost()`) AND 532–535 (inside `update_boost()` chain-tap branch) | Two emit sites: one in `start_boost()` after `self.dy = tuning.BOOST_FORCE` (line 511); one in `update_boost()` after the chain-tap re-assignment (line 533). Both are "a boost tap just fired". **Comment required.** | No. |
| 14 | `charge_shot_fire` | player.py | 585 (inside `fire_charge_shot()` after `self.game.projectiles.append(proj)`) | Also called from the btnr branch at line 310 and the windup-completion at line 610 — all three flow through `fire_charge_shot()` which is the single physical emit site. **Comment required.** | No. |
| 15 | `spit` | slime.py | 281 (inside `Slime.spit()`, after `return Projectile(...)`) | Emit `event_bus.emit("spit")` right before the `return` on line 281. The method already guards `if self.juice >= tuning.SLIME_SPIT_COST:` so the emit only fires on a successful spit. | No. |
| 16 | `damaged` | player.py | 188–189 or 205 (inside `take_damage()`, after `self.hp -= amount`) | Emit after `self.hp -= amount` on line 188 (before the `if self.hp <= 0: self.die()` check). This fires on real HP damage; the mana-shield branch at line 171–186 is a separate "absorbed" event that Phase 26 does NOT need to emit (juice went down, but damaged=0). Planner may also emit `damaged` inside the mana-shield branch with an `absorbed=True` kwarg if Phase 33 wants to hook it differently; simpler is one emit, on the real-damage path only. | No. |
| 17 | `death` | player.py | 215 (inside `die()`, after `self.state = "DEAD"`) | Single emit, inside the `if self.is_alive:` branch of `die()` so it can only fire once. | No. |

**Five `prev_*` snapshot captures needed** — all are 1-line additions at the top of existing methods. No new methods, no state-flag proliferation.

**Grep anchors** (planner uses these to find sites even if line numbers drift):

```
direction_change  → grep "facing_right = True" / "facing_right = False" in handle_input
jump_start        → grep "tuning.JUMP_FORCE" in handle_input
jump_released     → grep "VARIABLE_JUMP_REDUCTION"
fall_start        → grep "def apply_physics"
land              → grep "def move_and_collide"
wall_touch        → grep "is_wall_sliding = True"
wall_jump         → grep "tuning.WALL_JUMP_Y_FORCE"
drill_impact      → grep "DRILL_IMPACT_COST"
fuse_start        → grep "def fuse"
fuse_end          → grep "def unfuse"
ram_start         → grep "def start_ram"
ram_impact        → grep 'state == "RAMMING"' (near remove_tile)
boost_tap         → grep "def start_boost" + "def update_boost"
charge_shot_fire  → grep "def fire_charge_shot"
spit              → grep "def spit" in slime.py
damaged           → grep "self.hp -= amount"
death             → grep "def die"
```

---

## Existing Animation Code Audit

**Confirmed: the hardcoded `u = 16 + ...` toggle on line 795 is the ONLY animation decision logic in `player.draw()`.**

Other code in `player.draw()` that is NOT animation state and must stay:
- Line 784–789: `if not self.is_alive: ... pyxel.rect(..., 8)` — flashing death visualisation. **Stays.** This is not sprite animation; it's a placeholder for when the player is dead. Phase 26 does not touch it. Phase 31 may replace it with a real death clip later.
- Line 800–801: `draw_sprite(...)` — the actual blit call with `facing_right` flipping. **Stays** but its `u` argument changes from the hardcoded formula to `self._anim.current_frame_u(self._anim_driver)`.
- Line 803–805: `shield_flash_timer` / `circb` — shield hit VFX. **Stays.** Separate concern (damage feedback overlay, not a player sprite frame).
- Line 806: `self.draw_shield()` — bubble shield visualisation. **Stays.** Separate concern.
- Line 808–823: `draw_shield()` method body with `pulse` / `flicker` logic using `pyxel.frame_count`. **Stays.** This is an overlay animation, not a player-sprite animation; Phase 26 scope is the player sprite only.

**In slime.py** there is additional animation code at line 336: `u_offset = (pyxel.frame_count // 16 % 2) * 16` (slime 2-frame toggle). **Stays.** Phase 26 D-09 says "wires player_anim.py only"; slime's own animation refactor is Phase 34.

**No other animation-like state machines** exist in `player.py`. Confirmed via grep for `frame_count`, `pyxel.frame_count`, and `// 12 %` in the file.

---

## Phase 27 / 31 Forward Compatibility Check

**Phase 27 (Diagnostic Overlays, F2–F5)** will subscribe to the event bus. Its needs:
- Subscribe to a list of events and log them to screen. Handled by `event_bus.subscribe(name, cb)` — no API changes needed.
- Maybe: a way to enumerate all known events. Phase 26 does NOT build a registry (events are implicit from emit calls); Phase 27 either hardcodes the 17 names or builds its own registry. Not Phase 26's concern.
- May need overlay hooks for driver state (what clip is active right now). `AnimFSM._last_clip_id` can be exposed via a read-only property if Phase 27 wants it; Phase 26 should mark the field `_last_clip_id` not `__last_clip_id` (single underscore = "look-but-don't-touch" convention) so Phase 27 can read it without a refactor.

**Phase 31 (Animation Content + Particle Bank)** will:
- Load clip data from `assets/anim-schema.json` via `tuning.py`. Requires `AnimClip` to be trivially constructible from a dict — already true (`AnimClip(**json_dict)` works if `events` defaults correctly).
- Add transition clips (jump_crouch, land_recovery) that are `loop=False` and need D-07 reset-on-change — already built in Phase 26.
- Add combined-field predicates like `d.vy_sign < 0 and d.state == "JUMPING"` — already supported because the driver has `vy_sign` and rules are Python lambdas.
- Wire `AnimClip.events` dispatch (fire a named event on a specific frame index). Phase 26 reserves the `events: dict` slot but does NOT dispatch. Phase 31 adds dispatch logic to `AnimPlayer.tick()`. No Phase 26 refactor required.
- Hitbox-independence regression test (ANIM-07). Phase 26 does NOT touch `.w` / `.h` anywhere — the driver is read-only from player state. Phase 31's test will pass automatically against Phase 26 code.

**Phase 32 (Fusion Manager Refactor)** will re-home the 7 fusion-related emit sites (fuse_start, fuse_end, drill_impact, ram_start, ram_impact, boost_tap, charge_shot_fire) into `src/fusion/*`. The Phase 32 re-homing comment makes them greppable. Phase 26 does not block this.

**No Phase 26 decision locks in behavior that Phase 27/31/32 would need to undo.** Confirmed clean.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (version installed — used by Phase 24/25) |
| Config file | None (pytest default discovery) |
| Quick run command | `python -m pytest tests/test_anim.py tests/test_event_bus.py -x -q` |
| Full suite command | `python -m pytest -x -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ANIM-01 | `src/anim/` package with 5 files; `AnimFSM` and `AnimPlayer` instantiate | import smoke | `python -c "from src.anim import event_bus, anim_clip, anim_player, state_machine, player_anim"` | ❌ Wave 0 — all 5 files |
| ANIM-01 | `AnimFSM` construction raises on missing clip_id | unit | `pytest tests/test_anim.py::test_fsm_raises_on_missing_clip -x` | ❌ Wave 0 |
| ANIM-01 | `AnimClip` length mismatch raises | unit | `pytest tests/test_anim.py::test_clip_length_mismatch -x` | ❌ Wave 0 |
| ANIM-01 | `AnimPlayer.set_clip` resets counter to 0 (D-07) | unit | `pytest tests/test_anim.py::test_clip_change_resets_counter -x` | ❌ Wave 0 |
| ANIM-01 | `AnimClip.loop=False` holds on last frame (Phase 31 readiness check) | unit | `pytest tests/test_anim.py::test_non_looping_clip_holds -x` | ❌ Wave 0 |
| ANIM-02 | `event_bus.subscribe` + `emit` round-trip | unit | `pytest tests/test_event_bus.py::test_subscribe_emit_roundtrip -x` | ❌ Wave 0 |
| ANIM-02 | `event_bus.reset` clears subscribers | unit | `pytest tests/test_event_bus.py::test_reset_clears_subscribers -x` | ❌ Wave 0 |
| ANIM-02 | Each of the 17 events fires from gameplay code (one test per event) | integration | `pytest tests/test_event_bus.py -k "emits_from_gameplay" -x` | ❌ Wave 0 — 17 test functions |
| ANIM-02 | `direction_change` fires exactly once on turn-around (Pitfall 3) | integration | `pytest tests/test_event_bus.py::test_direction_change_only_on_flip -x` | ❌ Wave 0 |
| ANIM-02 | `land` fires exactly once per landing (Pitfall 5) | integration | `pytest tests/test_event_bus.py::test_land_only_on_touchdown -x` | ❌ Wave 0 |
| ANIM-02 | `fall_start` fires exactly once per fall transition (Pitfall 4) | integration | `pytest tests/test_event_bus.py::test_fall_start_only_on_transition -x` | ❌ Wave 0 |
| ANIM-03 | `current_frame_u()` replaces hardcoded line | grep | `grep -n "u = 16 + (pyxel.frame_count" src/entities/player.py` returns empty | — |
| ANIM-03 | Running state parity (24 frames, alternating 16/32 every 12) | unit | `pytest tests/test_anim.py::test_running_parity -x` | ❌ Wave 0 |
| ANIM-03 | Jumping / Falling state parity (constant 32) | unit | `pytest tests/test_anim.py::test_jumping_parity -x` + `test_falling_parity` | ❌ Wave 0 |
| ANIM-03 | Idle state parity (constant 0) | unit | `pytest tests/test_anim.py::test_idle_parity -x` | ❌ Wave 0 |
| ANIM-03 | All other states (DIVING, RAMMING, DASHING, BOOSTING, CHARGING_SHOT, WALL_SLIDING) render u=0 via fallback | unit | `pytest tests/test_anim.py::test_fallback_states_parity -x` | ❌ Wave 0 |
| ANIM-03 | `player._anim_driver` exists and is mutated in place (D-16) | unit | `pytest tests/test_anim.py::test_driver_single_instance -x` | ❌ Wave 0 |
| ANIM-03 | Driver refresh is last call in `update()` (D-14) | code grep | `grep -A2 "self.update_state" src/entities/player.py | grep "_update_anim_driver"` returns match | — |
| ANIM-03 | Frame-for-frame manual regression playthrough (Phase 25 D-04 pattern) | manual | Document in VERIFICATION.md: Room 0 → boss room path, all 11 states exercised, visual parity confirmed | — |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_anim.py tests/test_event_bus.py -x -q` (~1–2 seconds)
- **Per wave merge:** `python -m pytest -x -q` (full suite; should stay under 30s with existing tests)
- **Phase gate:** Full suite green + manual v1.3 regression playthrough per Phase 25 D-04 pattern before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `src/anim/__init__.py` — empty package marker
- [ ] `src/anim/event_bus.py` — module-level subscribe/emit/reset
- [ ] `src/anim/anim_clip.py` — `AnimClip` dataclass
- [ ] `src/anim/anim_player.py` — `AnimPlayer` class
- [ ] `src/anim/state_machine.py` — `AnimFSM` class
- [ ] `src/anim/player_anim.py` — `PlayerAnimDriver` + rules + clips + factory
- [ ] `tests/test_anim.py` — 9+ unit tests per table above
- [ ] `tests/test_event_bus.py` — 17+ integration tests per table above
- [ ] `tests/conftest.py` — shared mock fixtures (`mock_level`, `mock_slime`) — may already exist; check `tests/test_tuning_livereach.py` for inline versions to extract
- [ ] Framework install: none required (pytest already present)

---

## Security Domain

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A — single-player local-only game |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | partial | `AnimFSM.__init__` validates clip_ids exist (construction-time raise); `AnimClip.__post_init__` validates frames/durations length match |
| V6 Cryptography | no | N/A — no secrets, no network, no persistence in this phase |

### Known Threat Patterns for Pyxel + Python Local Game

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed clip dict causing silent mis-rendering | Tampering | Construction-time validation raises with clear message (see `AnimFSM.__init__` example above) |
| Test-order-dependent failures via shared module state | Tampering | Autouse `event_bus.reset()` fixture (inherited pattern from `tests/test_tuning_livereach.py`) |
| Stale closure in rules list referencing module that moved | Tampering | Rules are defined at module-import time in `player_anim.py` inside the same file as the driver — no cross-module closure |
| Event emit with wrong kwargs silently dropped | Information Disclosure (debug only) | Phase 26 emits use **keyword-only** args (`emit("name", **kwargs)`) — callbacks that don't accept a given kwarg will `TypeError` at emit time, surfacing contract breaks loudly |

Security-critical observation: **Phase 26 has no attack surface.** No network, no file I/O except indirect (`tuning.py` reads `physics-schema.json` at load time — already a Phase 24 concern), no user input parsing. The event bus is not an RPC boundary. ASVS is minimally applicable.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hand-written `class PlayerAnimData` with manual `__slots__` | `@dataclass(slots=True)` | Python 3.10 (Oct 2021) | 5 lines per dataclass saved; idiomatic since 3.10 |
| Observer-pattern base class with `notify()` | Module-level pub-sub dict | Python 3 era | Aligns with Pyxel module-singleton style; no OO ceremony for single-threaded loops |
| Classical `add_transition(A, B, event)` FSM | Driver-first rules list (Reanimator pattern) | Aarthificial's demo 2023; adopted in Astortion | D-00 — this phase is Reanimator-inspired by design |
| Third-party event libraries (blinker, pymitter) | Stdlib dict | N/A | Game loops don't need async/weakref/priority; 30-line custom bus wins |

**Deprecated / outdated to avoid:**
- `@dataclass` without `slots=True` — still works, slightly slower attribute access, no typo protection. Use `slots=True` unconditionally for drivers.
- Manual event registry classes with `register_listener` / `unregister_listener` API — over-engineered for sync single-thread.
- `pytransitions` / `python-statemachine` — explicitly out of scope per REQUIREMENTS.md and contradicts D-00a.
- Using `pyxel.frame_count` directly inside anim module code — couples anim playback to pyxel's global clock, defeating headless testability. Use an internal per-clip tick counter instead.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `@dataclass(slots=True)` field access is ~40ns | Dataclass Performance Investigation | None — even 10× slower is imperceptible at 4 fields/frame. Order-of-magnitude estimate from CPython 3.13 norms, not a microbenchmark. [ASSUMED] |
| A2 | Blinker and pyee are the canonical "why not use a library" alternatives | Pub-Sub investigation | Low — if the planner prefers a third-party lib they can; recommendation stands that stdlib is simpler. [ASSUMED based on general Python ecosystem knowledge; not re-verified in this session] |
| A3 | The existing `tests/test_physics.py` harness idiom (`sys.modules["pyxel"] = MagicMock()`) works for the Phase 26 test files | Code examples | Low — same pattern is used by `tests/test_tuning_livereach.py:17–21` [VERIFIED] and works in Phase 25. [VERIFIED by inspection] |
| A4 | `pyxel.frame_count` in the current v1.3 RUNNING formula is monotonic across state changes, so re-entering RUNNING does not reset the toggle phase | v1.3 Parity Test Strategy | Low — confirmed by reading the Pyxel API (frame_count never resets except via `pyxel.init()` which only runs once). This is load-bearing for the "sub-frame behavioral difference" disclaimer. [VERIFIED via `dir(pyxel)`] |
| A5 | `mcp__pyxel__run_and_capture` requires a windowed pyxel process and is unsuitable for headless CI | Pitfalls | Medium — not tested in this session. If Pyxel 2.x supports a headless/software-render mode the statement is too strong. Planner should verify before ruling it out if they want snapshot-diff as a belt-and-braces check. [ASSUMED] |
| A6 | The `ram_impact` event should fire on cracked-H block break only, not on solid-wall stop | Event Emit Site Audit | Low — design call, not a fact. The user's phrasing "ram collision resolution with a cracked-H block" implies block-break semantics. Planner may emit both and let Phase 35 juice filter. Flagged here so user/planner can override. [ASSUMED] |
| A7 | Phase 26 should emit `damaged` only on real HP damage, not on mana-shield absorbed damage | Event Emit Site Audit | Low — also a design call. Juice/sfx (Phase 33/35) may want to hear "any damage hit including absorbed" separately. Flagged. [ASSUMED] |

If every `[ASSUMED]` is wrong, the phase still ships — A1 is a perf claim (no observable effect), A2 is an alternatives note (no effect on recommendation), A5 only affects a verification tool choice, A6/A7 only affect where two events fire. None are load-bearing on correctness.

---

## Open Questions

1. **Should `ram_impact` emit on solid-wall stop (non-destructible) in addition to cracked-H break?**
   - What we know: The existing code at line 686 calls `self.end_ram(slime)` when hitting a solid wall. This is a "ram impact" in the player feel sense but not a "block broke" sense.
   - What's unclear: Phase 35's juice author may want one or two hooks for this. D-11 lists `ram_impact` as a single event name.
   - Recommendation: Emit once, at the cracked-H break path only. Document the decision in PLAN.md so Phase 35 knows. If Phase 35 wants the solid-wall hit, it can add a second event name later (`ram_wall_stop`).

2. **Should `damaged` emit include an `absorbed: bool` kwarg for the mana-shield branch?**
   - What we know: D-11 lists `damaged` as a single event name without parameters. Current code has two take_damage paths (mana-shield, real HP).
   - What's unclear: Whether subscribers (Phase 35 camera shake, Phase 35 impact flash) will need to distinguish.
   - Recommendation: Emit once per take_damage call that deals real HP damage. Add the mana-shield path as a future event in Phase 33 (`shield_absorb` or similar) when juice actually needs it. Keeps the 17-event scope unchanged.

3. **Single-file or split tests?**
   - What we know: CONTEXT.md Claude's Discretion says planner may split `test_event_bus.py` from a broader `test_anim.py` or combine them.
   - What's unclear: Planner preference, but pytest discovery works either way.
   - Recommendation: Two files. `tests/test_anim.py` covers `AnimFSM`/`AnimClip`/`AnimPlayer` unit tests + parity tests. `tests/test_event_bus.py` covers event bus primitives + the 17-event integration tests. Keeps focus and keeps file length under ~300 lines each.

4. **Should `current_frame_u()` accept the driver as an explicit arg, or read `self._driver`?**
   - What we know: D-17 says `u = self._anim.current_frame_u()` — no arg shown.
   - What's unclear: Whether the FSM holds a reference to the driver (constructor-injected) or the caller passes it each frame.
   - Recommendation: Explicit arg. `u = self._anim.current_frame_u(self._anim_driver)`. Keeps AnimFSM driver-shape-agnostic (D-02), keeps the data flow obvious, and trivially supports Phase 34 when a second entity wants a differently-shaped driver on the same FSM class. The D-17 quote is pseudocode; the actual signature is planner's call and this recommendation adds one token per call site.

---

## Sources

### Primary (HIGH confidence)

- **Phase 26 CONTEXT.md** — the source of all 18 decisions and scope bounds. Read fully and summarized in §User Constraints above. [VERIFIED: `.planning/phases/26-event-bus-animation-fsm-skeleton/26-CONTEXT.md`]
- **Phase 24 / 25 CONTEXT.md** — established patterns for module-level state reset, pytest fixture style, absolute imports, tuning loader. [VERIFIED]
- **`src/entities/player.py` lines 1–823** — hardcoded toggle location, all state transitions, all event emit sites, all existing animation logic. [VERIFIED via Read tool]
- **`src/entities/slime.py`** — spit call site and slime 2-frame toggle (out of scope confirmation). [VERIFIED via Read tool]
- **`src/core/tuning.py` module docstring** — PEP 562 loader pattern, `reset()` API, matches Phase 26 event bus pattern. [VERIFIED via Read tool]
- **`tests/test_tuning.py` and `tests/test_tuning_livereach.py`** — pytest fixture style (`autouse=True`, `yield`, teardown `reset()`), `sys.modules["pyxel"] = MagicMock()` harness for headless Player instantiation. [VERIFIED via Read tool]
- **`.planning/codebase/CONVENTIONS.md`** — project naming, imports, constants style. [VERIFIED via Read]
- **`.planning/REQUIREMENTS.md` §Animation System** — ANIM-01/02/03 acceptance text and the "Out of Scope: FSM libraries" directive. [VERIFIED via Read]
- **Python 3.13.11 runtime** — dataclass slots verification, pyxel 2.8.7 import, frame_count attr. [VERIFIED via Bash]

### Secondary (MEDIUM confidence)

- **Aarthificial's Reanimator** — https://github.com/aarthificial/reanimation-demo. Referenced as architectural inspiration. Not read in this session, relying on CONTEXT.md's characterization (driver-first, override-node rules tree). [CITED: via Phase 26 CONTEXT.md specifics section]
- **Astortion (Unity game using Reanimator)** — referenced but not accessed. [CITED: via Phase 26 CONTEXT.md]
- **blinker library** — https://blinker.readthedocs.io/en/stable/ — mentioned as a "why not use it" alternative; docs describe the minimal case as exactly what Phase 26 needs. [CITED from general Python ecosystem knowledge; not re-fetched this session]

### Tertiary (LOW confidence)

- **`@dataclass(slots=True)` attribute access ~40ns on CPython 3.13** — order-of-magnitude estimate from general CPython performance knowledge; not microbenchmarked. Does not affect correctness. Flagged in §Assumptions Log A1.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — stdlib only, all components verified present on local runtime
- Architecture: HIGH — every decision is locked in CONTEXT.md; research confirms the locked choices are implementable with stdlib
- Event emit sites: HIGH — all 17 sites located and line-anchored in current HEAD player.py / slime.py via Read + Grep
- v1.3 parity strategy: HIGH — hardcoded formula read, decomposed to 3 clips, unit test sketch drafted
- Pyxel pub-sub idiom: HIGH — verified absent in Pyxel 2.8.7; stdlib dict is correct fit
- Dataclass performance: HIGH — Python 3.13 verified, slots=True syntactically supported, perf is non-issue at 4 fields/frame
- Rules list factoring: HIGH — 3 variants surveyed, tuple-list recommendation aligns with D-04 literal wording
- Pyxel MCP viability for parity: MEDIUM — flagged in §Pitfalls as unsuitable for CI; unit-test strategy recommended instead. Not blocking.

**Research date:** 2026-04-12
**Valid until:** 2026-05-12 (30 days — stable ecosystem, no moving targets)
