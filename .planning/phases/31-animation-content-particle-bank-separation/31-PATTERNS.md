# Phase 31: Animation Content + Particle Bank Separation - Pattern Map

**Mapped:** 2026-04-21
**Files analyzed:** 16 (4 new, 12 modified)
**Analogs found:** 16 / 16 (all targets have an in-repo analog)

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `assets/anim-schema.json` | asset/schema | file-I/O (load-time) | `assets/physics-schema.json` | role-match (nested vs flat; same JSON-on-disk contract) |
| `assets/sprites/particles.png` | asset/sprite-sheet | file-I/O (image bank load) | `assets/sprites/effects.png` (retiring) and `assets/sprites/player.png` | exact (bank-loaded strip, 16px Y stride) |
| `assets/sprites/player.png` | asset/sprite-sheet | file-I/O | self (Phase 26 baseline) | extend in place |
| `assets/sprites/effects.png` | asset/sprite-sheet | file-I/O | self (retire/zero at y=96) | mod-only |
| `src/anim/player_anim.py` | core-anim (driver + rules + clip factory) | request-response (snapshot driver → clip id) | self (`src/anim/player_anim.py:32-69`) | exact (extend, don't rewrite) |
| `src/anim/anim_player.py` | core-anim (frame ticker) | event-driven (per-frame tick) | self (`src/anim/anim_player.py:6-34`) | exact (add one method) |
| `src/anim/anim_clip.py` | core-anim (clip dataclass) | data-holder | self (`src/anim/anim_clip.py:6-18`) | exact (passthrough `events` dict — already reserved) |
| `src/anim/state_machine.py` | core-anim (picker) | request-response | self (`src/anim/state_machine.py:11-34`) | exact (surface unchanged; optional `pause_for` forward) |
| `src/entities/player.py` | entity (gameplay state) | event-emitting | self (`src/entities/player.py:847-858` + event emits) | extend in place |
| `src/entities/effects.py` | entity (particles) | event-driven (spawn + per-frame update/draw) | self (`src/entities/effects.py:35-62`) + `src/entities/projectile.py` draw pattern | mod-only (rewrite `draw`, change constructor) |
| `main.py` | bootstrap (manifest + subscribe) | bootstrap + event-wire | self (`main.py:144-154, 305-313, 825-828`) | extend in place |
| `src/core/tuning.py` | config loader | file-I/O (JSON → namespace) | self `load()` at `src/core/tuning.py:50-104` | role-match (sibling loader, nested namespace not flat) |
| `src/ui/tuning_panel.py` / `src/ui/panel.py` | ui (panel overlay) | request-response (mouse) | self (`src/ui/panel.py:70-75, 85-137`) | exact (add tab entry + button) |
| `src/ui/presets.py` | config (preset save/load) | file-I/O | self (`src/ui/presets.py:16-18, 21-63`) | extend (Pitfall 6 guard — split anim keys) |
| `tests/test_anim_hitbox.py` (NEW) | test (matrix unit) | unit | `tests/test_anim.py:199-205, 219-246` (Player fixture pattern) + RESEARCH §Hitbox-independence test skeleton | role-match (new file, matrix-style extension of test_anim conventions) |
| `tests/test_anim.py` (EXTEND) | test (unit) | unit | self (`tests/test_anim.py:36-73` ticker tests, `tests/test_anim.py:89-138` FSM tests) | exact (add new test functions in place) |
| `tests/test_tuning_anim.py` (NEW) | test (unit; fail-fast) | unit | `tests/test_tuning.py:140-167` (unknown-key + duplicate-leaf pytest.raises + tmp_path write_text) | exact (mirror the `test_name_uniqueness_raises` pattern) |

---

## Pattern Assignments

### `src/anim/player_anim.py` (core-anim, extend)

**Analog:** self — `src/anim/player_anim.py:1-69`

**Existing imports/constants pattern** (lines 1-30):
```python
"""Phase 26 ANIM-01 + ANIM-03 player-specific animation wiring.

Defines the PlayerAnimDriver dataclass (D-01), the player clip table and
rules list (D-04/D-06), and the build_player_fsm() factory called from
Player.__init__ (see 26-02-PLAN).
"""
from dataclasses import dataclass
from src.anim.anim_clip import AnimClip
from src.anim.state_machine import AnimFSM, Rule

# --- Named constants (project memory: no magic numbers) ---------------------
# v1.3 sprite u offsets for the 16x16 player sheet (image bank 1).
IDLE_U = 0
RUN_FRAME_A_U = 16
RUN_FRAME_B_U = 32
JUMP_U = 32
STATIC_CLIP_DURATION_TICKS = 1
RUN_TOGGLE_DURATION_TICKS = 6

STATE_IDLE = "IDLE"
STATE_RUNNING = "RUNNING"
STATE_JUMPING = "JUMPING"
STATE_FALLING = "FALLING"
```

**Existing driver dataclass pattern** (lines 32-37):
```python
@dataclass(slots=True)
class PlayerAnimDriver:
    state: str = STATE_IDLE
    is_grounded: bool = True
    facing: int = 1        # -1 or +1
    vy_sign: int = 0       # -1 / 0 / +1
```

**Phase 31 extension (D-01, D-03 + transient counters per RESEARCH Pattern 2):**
```python
@dataclass(slots=True)
class PlayerAnimDriver:
    state: str = STATE_IDLE
    is_grounded: bool = True
    facing: int = 1
    vy_sign: int = 0
    vx_sign: int = 0          # D-01 Metroid jump split
    prev_facing: int = 1      # D-03 turn_skid edge
    skid_ticks: int = 0       # D-03 transient counter
    land_ticks: int = 0       # D-02 transient counter
    crouch_ticks: int = 0     # D-04 transient counter
```

**Existing PLAYER_CLIPS pattern** (lines 40-56) — preserve shape when seeding `anim-schema.json`:
```python
PLAYER_CLIPS: dict[str, AnimClip] = {
    "idle": AnimClip(frames=[IDLE_U], durations=[STATIC_CLIP_DURATION_TICKS], loop=True),
    "run":  AnimClip(frames=[RUN_FRAME_A_U, RUN_FRAME_B_U],
                     durations=[RUN_TOGGLE_DURATION_TICKS, RUN_TOGGLE_DURATION_TICKS], loop=True),
    "jump": AnimClip(frames=[JUMP_U], durations=[STATIC_CLIP_DURATION_TICKS], loop=True),
}
```
**D-13 seed requirement:** `anim-schema.json` MUST reproduce these three clips verbatim (same frames list, same duration ints, same loop bool) so v1.3 parity tests (`tests/test_anim.py:145-173`) keep passing after migration.

**Existing rules-list pattern** (lines 60-64) — FIRST-MATCH ORDER IS LOAD-BEARING:
```python
PLAYER_RULES: list[Rule] = [
    (lambda d: d.state == STATE_RUNNING, "run"),
    (lambda d: d.state in (STATE_JUMPING, STATE_FALLING), "jump"),
    (lambda d: True, "idle"),
]
```

**Phase 31 rule extension (RESEARCH §Pattern 1, specific-before-generic ordering):**
```python
PLAYER_RULES: list[Rule] = [
    (lambda d: d.skid_ticks > 0, "turn_skid"),
    (lambda d: d.crouch_ticks > 0, "jump_crouch"),
    (lambda d: d.state == STATE_JUMPING and d.vx_sign == 0, "jump_stationary"),
    (lambda d: d.state == STATE_JUMPING and d.vx_sign != 0, "jump_running"),
    (lambda d: d.state == "DIVING", "drill_spin"),
    (lambda d: d.is_grounded and d.land_ticks > 0, "land_squash"),
    (lambda d: d.state == STATE_RUNNING, "run"),
    (lambda d: d.state == STATE_FALLING, "jump"),
    (lambda d: True, "idle"),
]
```

**Existing factory pattern** (lines 67-69) — rebind for JSON-backed clips:
```python
def build_player_fsm() -> AnimFSM:
    return AnimFSM(rules=PLAYER_RULES, clips=PLAYER_CLIPS)
```

**Phase 31 rewrite (consume `tuning.anim.player.clips`, RESEARCH §"Reading anim-schema.json durations"):**
```python
def build_player_fsm() -> AnimFSM:
    from src.core import tuning
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
**Re-bind path for "Reload anim schema" button:** panel callback → `tuning.load_anim()` → `player._anim = build_player_fsm()` (AnimClip is `frozen=True` at `src/anim/anim_clip.py:6`, so durations cannot be mutated in place).

---

### `src/anim/anim_player.py` (core-anim, add `pause_for`)

**Analog:** self — `src/anim/anim_player.py:6-34`

**Existing class shape (full file):**
```python
class AnimPlayer:
    def __init__(self, clip: AnimClip) -> None:
        self._clip = clip
        self._clip_ticks = 0
        self._frame_index = 0

    def set_clip(self, clip: AnimClip) -> None:
        # D-07 -- clip change resets frame counter to 0.
        self._clip = clip
        self._clip_ticks = 0
        self._frame_index = 0

    def tick(self) -> None:
        # Check-then-increment: the frame persists for its full duration
        # before advancing.
        if self._clip_ticks >= self._clip.durations[self._frame_index]:
            self._clip_ticks = 0
            if self._frame_index + 1 < len(self._clip.frames):
                self._frame_index += 1
            elif self._clip.loop:
                self._frame_index = 0
            else:
                # Non-looping clip -- hold on last frame.
                return
        self._clip_ticks += 1

    def current_u(self) -> int:
        return self._clip.frames[self._frame_index]
```

**Phase 31 `pause_for(n)` extension (RESEARCH §Pattern 3, additive per A2):**
```python
class AnimPlayer:
    def __init__(self, clip: AnimClip) -> None:
        self._clip = clip
        self._clip_ticks = 0
        self._frame_index = 0
        self._pause_ticks = 0           # NEW

    def set_clip(self, clip: AnimClip) -> None:
        self._clip = clip
        self._clip_ticks = 0
        self._frame_index = 0
        self._pause_ticks = 0           # NEW -- pause doesn't survive clip change

    def pause_for(self, n: int) -> None:
        """Freeze tick counter for n frames. Additive if already paused."""
        self._pause_ticks += n

    def tick(self) -> None:
        if self._pause_ticks > 0:       # NEW -- skip advance while paused
            self._pause_ticks -= 1
            return
        # existing tick() body unchanged below
        if self._clip_ticks >= self._clip.durations[self._frame_index]:
            ...
```

**Unit test idiom to mirror** from `tests/test_anim.py:36-54`:
```python
def test_player_tick_advances_frame():
    clip = AnimClip(frames=[0, 16], durations=[2, 2])
    player = AnimPlayer(clip)
    results = []
    for _ in range(4):
        player.tick()
        results.append(player.current_u())
    assert results == [0, 0, 16, 16]
```
New test (`test_pause_for_freezes_ticks`): create `AnimPlayer`, call `pause_for(3)`, tick 3× and assert `current_u()` unchanged; tick once more and assert the normal schedule resumes.

---

### `src/anim/state_machine.py` (core-anim, optional `pause_for` forward)

**Analog:** self — `src/anim/state_machine.py:11-34`

**Existing class (full, verbatim):**
```python
class AnimFSM:
    def __init__(self, rules: list[Rule], clips: dict[str, AnimClip]) -> None:
        missing = [cid for _, cid in rules if cid not in clips]
        if missing:
            raise ValueError(f"AnimFSM rules reference missing clip_ids: {missing}")
        self._rules = rules
        self._clips = clips
        self._player = AnimPlayer(clips[rules[-1][1]])
        self._last_clip_id: str | None = None

    def current_frame_u(self, driver: Any) -> int:
        for predicate, clip_id in self._rules:
            if predicate(driver):
                if clip_id != self._last_clip_id:
                    self._player.set_clip(self._clips[clip_id])
                    self._last_clip_id = clip_id
                self._player.tick()
                return self._player.current_u()
        raise RuntimeError("AnimFSM rules missing fallback")
```

**Phase 31 optional addition (planner choice per RESEARCH Open Question 2):**
```python
    def pause_for(self, n: int) -> None:
        """Forward to the active AnimPlayer; keeps _player private."""
        self._player.pause_for(n)
```
**Subscriber call site becomes:** `self.player._anim.pause_for(DRILL_RECOIL_PAUSE_FRAMES)` instead of reaching through to `_player`.

**Construction-time validation** at `state_machine.py:14-18` is the model for `tuning.load_anim()`'s fail-fast shape.

---

### `src/anim/anim_clip.py` (core-anim, passthrough only)

**Analog:** self — `src/anim/anim_clip.py:1-18`

**Existing dataclass (full, verbatim):**
```python
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

**Phase 31 action:** Per RESEARCH §Assumption A4, Phase 31 wires `events` dict passthrough **only** — JSON → `AnimClip.events` → no consumer yet. Frame-index event dispatch (firing named events at specific frame indices) is deferred. No class change required; `build_player_fsm` already passes `events=spec.events` in the new body.

---

### `src/entities/player.py` (entity, extend `_update_anim_driver` + add event listeners)

**Analog:** self — `src/entities/player.py:847-858` (`_update_anim_driver`) + existing event emits at lines 97, 259, 484, 520, 535, 543, 548, 556, 580, 634, 699, 731, 794, 800, 830.

**Existing `_update_anim_driver` (lines 847-858, verbatim):**
```python
def _update_anim_driver(self):
    """Phase 26 D-14: refresh the animation driver from end-of-frame state.

    Called as the last statement of update() so the driver snapshot
    reflects settled physics + state. Mutates the existing driver
    instance in place -- zero per-frame allocations (D-16).
    """
    d = self._anim_driver
    d.state = self.state
    d.is_grounded = self.is_grounded
    d.facing = 1 if self.facing_right else -1
    d.vy_sign = -1 if self.dy < 0 else (1 if self.dy > 0 else 0)
```

**Phase 31 extension (RESEARCH §Pattern 2 + Pitfall 1 — `prev_facing` MUST snapshot BEFORE `facing` overwrite):**
```python
def _update_anim_driver(self):
    d = self._anim_driver
    d.state = self.state
    d.is_grounded = self.is_grounded
    d.prev_facing = d.facing                                # D-03: snapshot BEFORE overwrite
    d.facing = 1 if self.facing_right else -1
    d.vy_sign = -1 if self.dy < 0 else (1 if self.dy > 0 else 0)
    d.vx_sign = -1 if self.dx < 0 else (1 if self.dx > 0 else 0)   # D-01
    # D-03 edge: facing changed this frame -> arm skid counter
    if d.facing != d.prev_facing and d.is_grounded:
        d.skid_ticks = TURN_SKID_FRAMES
    # Tick down transient counters (Pitfall 2: never forget the decrement)
    if d.skid_ticks > 0:   d.skid_ticks -= 1
    if d.land_ticks > 0:   d.land_ticks -= 1
    if d.crouch_ticks > 0: d.crouch_ticks -= 1
```

**Event emit pattern to read (existing, canonical emit sites):**
```python
# src/entities/player.py:535
event_bus.emit("jump_start")

# src/entities/player.py:794
event_bus.emit("land")

# src/entities/player.py:97
event_bus.emit("fuse_start")
```
**Phase 31 new subscriber hooks** go in `Player.__init__` (or in `main.py` after `reset()`):
```python
def _on_land(**kw):
    self._anim_driver.land_ticks = LAND_SQUASH_FRAMES

def _on_jump_start(**kw):
    self._anim_driver.crouch_ticks = JUMP_CROUCH_FRAMES

event_bus.subscribe("land", _on_land)
event_bus.subscribe("jump_start", _on_jump_start)
```

**Do NOT touch** `on_block_break` at `src/entities/player.py:235-239` — it sets gameplay hitstop (`game.stop_frames`), which is DISTINCT from D-06 animation pause. Leave it alone.

**Audit note per RESEARCH Pitfall 4:** `drill_block_break` event is NOT yet emitted anywhere. Planner decides whether Phase 31 adds a thin bridge emit at lines 729, 785, 817 (right after each `on_block_break()` call) or ships subscribers latent until Phase 32.

---

### `src/entities/effects.py` (entity, rewrite `Particle.draw` + retire `Effect`)

**Analog:** self — `src/entities/effects.py:35-62` (current pset Particle) + RESEARCH §Pattern 4.

**Existing Particle class (full, verbatim — lines 35-62):**
```python
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.color = color
        self.life = random.randint(20, 40)
        self.is_active = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.025 # gravity (quartered for 60fps)
        self.life -= 1
        if self.life <= 0:
            self.is_active = False

    def draw(self, cam_x, cam_y):
        if not self.is_active:
            return

        # Room boundary check
        if (self.x < cam_x or self.x > cam_x + tuning.VIEWPORT_W or
            self.y < cam_y or self.y > cam_y + tuning.VIEWPORT_H):
            return

        pyxel.pset(self.x, self.y, self.color)
```

**Phase 31 rewrite (RESEARCH §Pattern 4 + `draw_sprite` signature at `src/core/sprite_utils.py:7-39`):**
```python
class Particle:
    def __init__(self, x, y, *, dx, dy, life, bank_u, bank_v):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.life = life
        self.bank_u = bank_u
        self.bank_v = bank_v
        self.is_active = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += PARTICLE_GRAVITY   # only for physics-affected particles
        self.life -= 1
        if self.life <= 0:
            self.is_active = False

    def draw(self, cam_x, cam_y):
        if not self.is_active:
            return
        if (self.x < cam_x or self.x > cam_x + tuning.VIEWPORT_W or
            self.y < cam_y or self.y > cam_y + tuning.VIEWPORT_H):
            return
        draw_sprite(self.x, self.y, PARTICLE_SIZE, PARTICLE_SIZE,
                    2, self.bank_u, self.bank_v,
                    PARTICLE_SIZE, PARTICLE_SIZE, True)
```

**`Effect` class disposition** — per CONTEXT D-16 and RESEARCH A5, strip to a no-op spawner shell OR delete entirely. Planner's call. If deleted, also update `from src.entities.effects import Effect, Particle` at `main.py:126`.

**All `Particle(x, y, color)` call sites (old signature) that must migrate:**
- `main.py:828` (`self.particles.append(Particle(x + 4, y + 4, color))` inside `spawn_explosion`)
- `src/entities/player.py:563` (`Particle(self.x + 4, self.y + self.h, 11)` — green)
- `src/entities/player.py:587` (`Particle(self.x + 4, self.y + self.h, 11)` — green)
- `src/entities/player.py:639` (`Particle(fire_x, fire_y, 10)` — yellow)

Each becomes a `spawn_particle_burst(x, y, type=…)` call or a direct keyword-only `Particle(...)` construction with precomputed `dx/dy/life/bank_u/bank_v`.

**Consumer pattern to preserve** — `main.py:544-547`:
```python
# 2. Always update effects/particles
for eff in self.effects:
    eff.update()
self.effects = [eff for eff in self.effects if eff.is_active]
```
Same `is_active` filter + `update()`/`draw(cam_x, cam_y)` contract. Do not break.

---

### `main.py` (bootstrap, extend SPRITE_MANIFEST + load_anim + subscribers)

**Analog:** self — `main.py:144-154` (SPRITE_MANIFEST), `main.py:305-313` (_load_sprites), `main.py:825-828` (spawn_explosion).

**Existing SPRITE_MANIFEST (lines 144-154, verbatim):**
```python
SPRITE_MANIFEST = {
    "tiles":      (0, 0, 0,   "assets/tiles.png"),
    "player":     (1, 0, 0,   "assets/sprites/player.png"),
    "slime":      (1, 0, 16,  "assets/sprites/slime.png"),
    "snail":      (1, 0, 32,  "assets/sprites/snail.png"),
    "bat":        (1, 0, 48,  "assets/sprites/bat.png"),
    "items":      (1, 0, 64,  "assets/sprites/items.png"),
    "projectile": (1, 0, 80,  "assets/sprites/projectile.png"),
    "effects":    (1, 0, 96,  "assets/sprites/effects.png"),
    "boss":       (1, 0, 128, "assets/sprites/boss.png"),
}
```

**Phase 31 edit — add bank 2, remove/comment effects y=96:**
```python
SPRITE_MANIFEST = {
    "tiles":      (0, 0, 0,   "assets/tiles.png"),
    "player":     (1, 0, 0,   "assets/sprites/player.png"),
    "slime":      (1, 0, 16,  "assets/sprites/slime.png"),
    "snail":      (1, 0, 32,  "assets/sprites/snail.png"),
    "bat":        (1, 0, 48,  "assets/sprites/bat.png"),
    "items":      (1, 0, 64,  "assets/sprites/items.png"),
    "projectile": (1, 0, 80,  "assets/sprites/projectile.png"),
    # "effects":  (1, 0, 96,  "assets/sprites/effects.png"),  # RETIRED Phase 31 D-16
    "boss":       (1, 0, 128, "assets/sprites/boss.png"),
    "particles":  (2, 0, 0,   "assets/sprites/particles.png"),  # NEW Phase 31 D-15
}
```
**Gotcha:** `main.py:170-174` auto-loads `.json` sidecar for every manifest entry by swapping `.png → .json`. Add `assets/sprites/particles.json` (can be a stub with empty `frameTags`) OR skip particles in the sidecar loop. Skip is safer; gate with `if name in ("tiles", "particles"): continue`.

**Existing `_load_sprites` (lines 305-313, verbatim):**
```python
def _load_sprites(self):
    """Load all PNG spritesheets into image banks (D-09, D-11)."""
    for name, (bank, x, y, path) in SPRITE_MANIFEST.items():
        if name == "tiles":
            tileset_path = schema.get_tileset_path()
            pyxel.images[bank].load(x, y, path)
        else:
            pyxel.images[bank].load(x, y, path)
```
No change needed — generic over manifest; new entry loads automatically.

**Existing `spawn_explosion` (lines 825-828, verbatim):**
```python
def spawn_explosion(self, x, y, color):
    self.effects.append(Effect(x, y))
    for _ in range(8):
        self.particles.append(Particle(x + 4, y + 4, color))
```

**Phase 31 rewrite (RESEARCH §"Subscribing to drill_block_break"):**
```python
def spawn_particle_burst(self, x, y, type="block_break"):
    import math
    cx, cy = x + 4, y + 4
    for i in range(BURST_PARTICLE_COUNT):
        angle = (2 * math.pi * i) / BURST_PARTICLE_COUNT
        self.particles.append(Particle(
            cx, cy,
            dx=math.cos(angle) * BURST_PARTICLE_SPEED,
            dy=math.sin(angle) * BURST_PARTICLE_SPEED,
            life=BURST_PARTICLE_LIFE,
            bank_u=PARTICLE_BURST_U, bank_v=PARTICLE_BURST_V,
        ))
```
Callers at `main.py:647, 652, 658` and `src/entities/player.py:727, 780, 815` either keep calling `spawn_explosion` (renamed internally) or migrate to `spawn_particle_burst`.

**Phase 31 init-sequence edit** — after `schema.init()` at line 161, before `_load_sprites()`:
```python
schema.init()
from src.core import tuning
tuning.load_anim()          # NEW — D-10 parallel loader
self._load_sprites()        # existing
```

**Phase 31 subscriber wiring** — after `reset()` at line 175 / before `pyxel.run` at line 212. **Pitfall 5 of RESEARCH §Anti-Patterns:** must wire AFTER `reset()` so `self.player` and `self.particles` exist. Pattern from `src/anim/event_bus.py:13` subscribe API:
```python
from src.anim import event_bus
import math

def _on_fuse_start(**kw):
    cx = self.player.x + self.player.w // 2
    cy = self.player.y + self.player.h // 2
    for i in range(FUSE_PARTICLE_COUNT):
        angle = (2 * math.pi * i) / FUSE_PARTICLE_COUNT
        sx = cx + math.cos(angle) * FUSE_RING_RADIUS
        sy = cy + math.sin(angle) * FUSE_RING_RADIUS
        self.particles.append(Particle(
            sx, sy,
            dx=(cx - sx) / FUSE_CONVERGE_FRAMES,
            dy=(cy - sy) / FUSE_CONVERGE_FRAMES,
            life=FUSE_CONVERGE_FRAMES,
            bank_u=PARTICLE_CONVERGE_U, bank_v=PARTICLE_CONVERGE_V,
        ))
    self.fused_blobs.append(BlobGrowth(cx, cy, frames=BLOB_GROWTH_FRAMES))

def _on_drill_block_break(tx=None, ty=None, **kw):
    self.player._anim.pause_for(DRILL_RECOIL_PAUSE_FRAMES)
    self.spawn_particle_burst(tx * tuning.TILE_SIZE, ty * tuning.TILE_SIZE, "block_break")

event_bus.subscribe("fuse_start", _on_fuse_start)
event_bus.subscribe("drill_block_break", _on_drill_block_break)
```

---

### `src/core/tuning.py` (config, add `load_anim()` sibling loader)

**Analog:** self — `src/core/tuning.py:50-104` (`load()` body + `_flat_index` construction).

**Existing `load()` pattern (lines 50-104, excerpt):**
```python
def load(schema_path: str | pathlib.Path | None = None) -> None:
    global _schema_path, _raw, _model, _baseline, _flat_index

    path = pathlib.Path(schema_path) if schema_path is not None else _DEFAULT_SCHEMA
    _schema_path = path

    with open(path, encoding="utf-8") as f:
        _raw = json.load(f)

    version = _raw.get("version", "")
    if not isinstance(version, str) or not version.startswith(_SUPPORTED_SCHEMA_MAJOR):
        raise ValueError(
            f"Unsupported physics-schema version {version!r} at {path}; "
            f"expected {_SUPPORTED_SCHEMA_MAJOR}.x."
        )

    tuning_block = _raw.get("tuning")
    if not isinstance(tuning_block, dict):
        raise ValueError(
            f"physics-schema at {path} has no top-level 'tuning' object; "
            f"cannot build flat-key index."
        )
    _model = tuning_block

    new_index: dict[str, str] = {}
    for group_name, group_dict in _model.items():
        if not isinstance(group_dict, dict):
            raise ValueError(
                f"tuning group {group_name!r} must be an object, got "
                f"{type(group_dict).__name__}"
            )
        for leaf_name in group_dict:
            if leaf_name in new_index:
                first_group = new_index[leaf_name]
                raise ValueError(
                    f"Duplicate tuning leaf {leaf_name!r} in groups "
                    f"{first_group!r} and {group_name!r}"
                )
            new_index[leaf_name] = group_name
    _flat_index = new_index

    _baseline = copy.deepcopy(_model)
    __all__[:] = sorted(_flat_index.keys())
```

**Existing auto-load at bottom** (line 284): `load()` is called at module import time. `load_anim()` must NOT be auto-called at import (see Pitfall: tests monkey-patch `tuning.anim`).

**Phase 31 `load_anim()` (RESEARCH §"tuning.load_anim() implementation sketch"):**
```python
# --- Phase 31 anim loader (parallel to load()) ------------------------------
from types import SimpleNamespace

_anim_path: pathlib.Path | None = None
_anim_raw: dict | None = None
anim: SimpleNamespace | None = None

_DEFAULT_ANIM_SCHEMA = (
    pathlib.Path(__file__).resolve().parents[2] / "assets" / "anim-schema.json"
)

def load_anim(schema_path: str | pathlib.Path | None = None) -> None:
    """Load anim-schema.json into tuning.anim namespace. Fail fast (D-14)."""
    global _anim_path, _anim_raw, anim

    path = pathlib.Path(schema_path) if schema_path is not None else _DEFAULT_ANIM_SCHEMA
    _anim_path = path
    with open(path, encoding="utf-8") as f:
        _anim_raw = json.load(f)

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
                raise ValueError(
                    f"anim-schema: {entity_name}.{clip_id} missing frames/durations"
                )
            if len(frames) != len(durations):
                raise ValueError(
                    f"anim-schema: {entity_name}.{clip_id} frames/durations "
                    f"length mismatch ({len(frames)} vs {len(durations)})"
                )
            allowed = {"frames", "durations", "loop", "events"}
            extra = set(clip_spec) - allowed
            if extra:
                raise ValueError(
                    f"anim-schema: {entity_name}.{clip_id} unknown fields: {extra}"
                )
            clips[clip_id] = SimpleNamespace(
                frames=frames, durations=durations, loop=loop, events=events
            )
        entities_ns[entity_name] = SimpleNamespace(clips=clips)
    anim = SimpleNamespace(**entities_ns)
```
**D-10 isolation:** `load_anim` must NOT touch `_flat_index`, `_model`, `_baseline`, or `__all__`. Adding anim keys to `_flat_index` triggers the D-15 duplicate-check and pollutes `from tuning import *`.

**Fail-fast error model** comes directly from existing `load()` raises at `tuning.py:67-72, 76-79, 86-96` — `ValueError` with explicit message citing path + field.

---

### `src/ui/panel.py` + `src/ui/presets.py` (UI + preset plumbing)

**Analog:** self — `src/ui/panel.py:55-75, 85-137` (TAB_DEFS + _init_panel) + `src/ui/presets.py:16-63`.

**Existing TAB_DEFS pattern (`src/ui/panel.py:70-75`):**
```python
TAB_DEFS = [
    ("Move",  {"movement": lambda k: k not in JUMP_TAB_MOVEMENT_KEYS, "dash": None}),
    ("Jump",  {"movement": lambda k: k in JUMP_TAB_MOVEMENT_KEYS, "forgiving": None, "wall": None}),
    ("Slime", {"slime_follow": None, "slime_juice": None, "projectile": None}),
    ("Fuse",  {"drill": None, "fusion": None, "slime_ram": None, "charge_shot": None, "boost": None}),
]
```
Phase 31 adds a 5th tab entry. Since anim durations don't live in `_flat_index`, the existing `_init_panel` loop at `panel.py:98-134` won't find them — a NEW loop must synthesize flat keys from `tuning.anim.player.clips` and build `Slider` widgets against those.

**Existing Slider construction (`src/ui/panel.py:118-124`):**
```python
for key in keys_in_group:
    baseline = tuning.get_baseline(key)
    if isinstance(baseline, bool):
        sliders.append(BoolToggle(key))
    else:
        sliders.append(Slider(key))
```
**Gotcha:** `Slider(key)` at `src/ui/widgets.py:108-121` reads `tuning.get_baseline(key)` from `_flat_index`. To reuse Slider for anim keys, either (a) register anim flat keys in a parallel `_anim_flat_index` and extend `tuning.get_baseline` / `tuning.set_value` to dispatch, or (b) write an `AnimSlider` subclass/adapter that has its own baseline + set/get routing. Per RESEARCH §Open Question 4, path (a) — parallel `_anim_flat_index` with `tuning.get_anim_baseline(key)` / `tuning.set_anim_value(key, val)` — is the recommended split.

**Reload-anim-schema button** — add beside the existing Save button. Analog at `src/ui/panel.py:271-301` (`_handle_save_click`):
```python
def _handle_save_click():
    my = pyxel.mouse_y
    mx = pyxel.mouse_x
    if not pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
        return
    header_top = PANEL_TOP + TAB_BAR_H
    if not (header_top <= my < header_top + HEADER_H):
        return
    if not (_SAVE_BTN_X <= mx < _SAVE_BTN_X + _SAVE_BTN_W):
        return
    ...
```
Copy this hit-test shape for a new `_handle_reload_anim_click()` with a second rect + distinct callback that calls `tuning.load_anim(); self.player._anim = build_player_fsm()` (or equivalent re-bind).

**Existing `FEEL_GROUPS` + `_feel_keys` (`src/ui/presets.py:9-18`, verbatim):**
```python
FEEL_GROUPS = {
    "movement", "dash", "forgiving", "wall",
    "slime_follow", "slime_juice", "projectile",
    "drill", "fusion", "slime_ram", "charge_shot", "boost",
}

def _feel_keys():
    """Return list of feel-relevant tuning keys."""
    return [k for k, g in tuning._flat_index.items() if g in FEEL_GROUPS]
```

**Existing `load_preset` (verbatim, with Pitfall 6 trap — lines 47-63):**
```python
def load_preset(slot):
    """Load preset, apply all values via tuning.set_value() (D-11).

    Returns (slot, alias) or raises FileNotFoundError/JSONDecodeError.
    Wraps set_value in try/except KeyError for schema evolution safety --
    keys removed from the schema since the preset was saved are silently skipped.
    """
    path = PRESETS_DIR / f"slot_{slot}.json"
    with open(path, encoding="utf-8") as f:
        preset = json.load(f)
    alias = preset.get("alias", f"slot {slot}")
    for key, val in preset["values"].items():
        try:
            tuning.set_value(key, val)
        except KeyError:
            pass  # Key removed from schema -- skip
    return slot, alias
```
**Pitfall 6 fix pattern** (RESEARCH §Pitfall 6 + Open Question 4): add a prefix gate or second dispatch before `set_value`:
```python
for key, val in preset["values"].items():
    if key.startswith("ANIM_"):            # anim keys route to separate API
        try:
            tuning.set_anim_value(key, val)
        except KeyError:
            pass
    else:
        try:
            tuning.set_value(key, val)
        except KeyError:
            pass
```
Without this, Pitfall 6 fires: `KeyError` on anim keys is silently swallowed → preset slider changes don't stick.

**Existing `save_preset` (lines 21-44):** `values[key] = getattr(tuning, key)` reads flat attrs via PEP-562. For anim keys, the dual read path needs `getattr(tuning, key)` replaced with a `tuning.get_anim_value(key)` or similar for anim-prefixed keys.

---

### `tests/test_anim_hitbox.py` (NEW — ANIM-07 matrix, hard gate)

**Analog:** `tests/test_anim.py:199-205` (mock_level fixture) + `tests/test_anim.py:219-246` (Player fixture usage) + RESEARCH §"Hitbox-independence test skeleton".

**Existing fixture pattern from `tests/test_anim.py:199-205`:**
```python
@pytest.fixture
def mock_level():
    level = MagicMock()
    level.check_collision.return_value = False
    level.check_hazard.return_value = False
    level.is_switch.return_value = False
    return level
```
**Already exposed in conftest.py:28-37** — `mock_level` is autouse-scope-available. No new fixture needed.

**Existing Player instantiation pattern (`tests/test_anim.py:237-246`):**
```python
def test_player_update_anim_driver_reflects_state(mock_level):
    p = Player(0, 0, mock_level)
    p.state = "RUNNING"
    p.facing_right = False
    p.dy = -2.5
    p.is_grounded = False
    p._update_anim_driver()
    assert p._anim_driver.state == "RUNNING"
```

**Phase 31 new test (RESEARCH §"Hitbox-independence test skeleton"):**
```python
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

def test_hitbox_invariant_across_matrix(mock_level):
    """ANIM-07: no (state × vx_sign × vy_sign × facing) mutates w/h."""
    for state in HITBOX_STATES:
        for vxs in VX_SIGNS:
            for vys in VY_SIGNS:
                for facing in FACINGS:
                    p = Player(0, 0, mock_level)
                    initial_w, initial_h = p.w, p.h
                    p.state = state
                    p.dx = float(vxs) * 2.0
                    p.dy = float(vys) * 2.0
                    p.facing_right = facing
                    p._update_anim_driver()
                    for _ in range(60):
                        p._anim.current_frame_u(p._anim_driver)
                    assert p.w == initial_w, (
                        f"w mutated at state={state} vx={vxs} vy={vys} facing={facing}: "
                        f"{initial_w} -> {p.w}"
                    )
                    assert p.h == initial_h, (
                        f"h mutated at state={state} vx={vxs} vy={vys} facing={facing}"
                    )
```

---

### `tests/test_anim.py` (EXTEND with new clips + `pause_for` tests)

**Analog:** self — `tests/test_anim.py:21-74` (AnimClip + AnimPlayer unit tests), lines 145-188 (parity tests).

**Existing parity-test pattern (lines 145-153):**
```python
def test_running_parity():
    fsm = build_player_fsm()
    driver = PlayerAnimDriver(state="RUNNING")
    outputs = [fsm.current_frame_u(driver) for _ in range(48)]
    cycle = [RUN_FRAME_A_U] * RUN_TOGGLE_DURATION_TICKS + [RUN_FRAME_B_U] * RUN_TOGGLE_DURATION_TICKS
    expected = cycle * (48 // (RUN_TOGGLE_DURATION_TICKS * 2))
    assert outputs == expected
```

**Phase 31 new tests to add (RESEARCH §Phase Requirements → Test Map):**
- `test_metroid_jump_split` — `state=JUMPING, vx_sign=0` → jump_stationary U; `vx_sign=1` → jump_running U
- `test_land_squash_fires_on_land_event` — emit `"land"`, call `_update_anim_driver`, assert rule picks `land_squash` for N frames
- `test_turn_skid_on_facing_flip` — set `facing_right=True`, tick driver, flip to `False`, tick again, assert `skid_ticks > 0` and rule picks `turn_skid`
- `test_jump_crouch_triggers_on_jump_start` — emit `"jump_start"`, assert `crouch_ticks > 0` then holds last frame (non-looping)
- `test_drill_spin_4_frames_in_diving` — `state="DIVING"`, tick through full clip, assert 4 distinct u values cycle
- `test_pause_for_freezes_ticks` — pause_for(3), tick 3×, assert `current_u()` unchanged across all 3; tick 1 more, normal advance resumes

**Critical `build_player_fsm` test caveat:** After migration to JSON, `build_player_fsm` reads from `tuning.anim`. Tests MUST ensure `tuning.load_anim()` has been called before construction — add an autouse fixture in `tests/test_anim.py` (or extend `conftest.py`).

---

### `tests/test_tuning_anim.py` (NEW — fail-fast loader branches)

**Analog:** `tests/test_tuning.py:140-167` (existing raises-tests + `tmp_path.write_text` JSON fixture idiom).

**Existing pattern (verbatim, lines 140-167):**
```python
def test_set_value_unknown_key_raises():
    """set_value() rejects arbitrary keys (D-15 / T-24-10)."""
    with pytest.raises(KeyError):
        tuning.set_value("NOT_A_KEY", 1)


def test_name_uniqueness_raises(tmp_path):
    """D-15: duplicate flat leaf across groups raises at load time."""
    bad = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "conflict",
        "version": "0.3.0",
        "fps": 60, "tile_size": 16,
        "tuning": {
            "movement": {"GRAVITY": 0.1},
            "slime_juice": {"GRAVITY": 0.2},
        },
        "derived": {},
    }
    bad_path = tmp_path / "bad-schema.json"
    bad_path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate tuning leaf"):
        tuning.load(schema_path=bad_path)
    tuning.load()  # restore real schema for subsequent tests
```

**Phase 31 new tests (D-14 fail-fast branches):**
```python
def test_load_anim_fails_on_length_mismatch(tmp_path):
    bad = {"player": {"clips": {"run": {"frames": [0, 16], "durations": [6]}}}}
    bad_path = tmp_path / "anim-bad.json"
    bad_path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="length mismatch"):
        tuning.load_anim(schema_path=bad_path)

def test_load_anim_fails_on_unknown_field(tmp_path):
    bad = {"player": {"clips": {"run": {"frames": [0], "durations": [1], "bogus": 42}}}}
    bad_path = tmp_path / "anim-bad.json"
    bad_path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="unknown fields"):
        tuning.load_anim(schema_path=bad_path)

def test_load_anim_fails_on_missing_clips_dict(tmp_path):
    bad = {"player": {}}  # no 'clips' key
    bad_path = tmp_path / "anim-bad.json"
    bad_path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="missing 'clips'"):
        tuning.load_anim(schema_path=bad_path)

def test_load_anim_builds_namespace(tmp_path):
    good = {"player": {"clips": {"idle": {"frames": [0], "durations": [1]}}}}
    good_path = tmp_path / "anim-good.json"
    good_path.write_text(json.dumps(good), encoding="utf-8")
    tuning.load_anim(schema_path=good_path)
    assert tuning.anim.player.clips["idle"].frames == [0]
    assert tuning.anim.player.clips["idle"].durations == [1]
    assert tuning.anim.player.clips["idle"].loop is True  # default
```

---

## Shared Patterns

### Event Subscription (cross-cutting, used by `main.py`, potentially `player.py`)

**Source:** `src/anim/event_bus.py:13-19`
**Apply to:** `fuse_start` + `drill_block_break` subscribers in `main.py`; optionally `land` + `jump_start` subscribers on Player init.
```python
def subscribe(event_name: str, callback: Callable[..., None]) -> None:
    _subscribers.setdefault(event_name, []).append(callback)

def emit(event_name: str, **kwargs) -> None:
    for cb in _subscribers.get(event_name, ()):
        cb(**kwargs)
```
**Test hygiene:** `tests/conftest.py:19-24` already auto-resets the bus between tests. Any new test that emits must NOT call `event_bus.reset()` inside the test (the fixture handles teardown).

### No-Magic-Numbers (MEMORY constraint, cross-cutting)

**Source:** `src/anim/player_anim.py:14-23` (named constants block for v1.3 U offsets + durations)
**Apply to:** every Phase 31 numeric literal — examples:
- `LAND_SQUASH_FRAMES = 4`
- `TURN_SKID_FRAMES = 3`
- `JUMP_CROUCH_FRAMES = 2`
- `DRILL_RECOIL_PAUSE_FRAMES = 3`
- `FUSE_CONVERGE_FRAMES = 12`
- `FUSE_PARTICLE_COUNT = 16`
- `FUSE_RING_RADIUS = 24`
- `BURST_PARTICLE_COUNT = 14`
- `BURST_PARTICLE_SPEED = 1.5`
- `BURST_PARTICLE_LIFE = 20`
- `BLOB_GROWTH_FRAMES = 5`
- `PARTICLE_SIZE = 4` (or 8)
- `PARTICLE_GRAVITY = 0.025` (inherit from current `effects.py:48` literal)
- `PARTICLE_CONVERGE_U`, `PARTICLE_CONVERGE_V`, `PARTICLE_BURST_U`, `PARTICLE_BURST_V` (bank 2 offsets, planner discretion D-19)

Co-locate in `player_anim.py` constants section (driver thresholds) or in a new `src/anim/particle_bank.py` constants module (bank-2 U/V offsets) or hoist duration values into `anim-schema.json`.

### Fail-Fast JSON Load with `ValueError` (cross-cutting, schema validation)

**Source:** `src/core/tuning.py:67-72, 76-79, 86-96` — three consecutive `raise ValueError(f"...")` calls gating version, shape, and duplicate-leaf invariants.
**Apply to:** `tuning.load_anim()` — mirror the exact idiom (f-string with path + field name for grep-ability).

### Bottom-Center-Anchored Sprite Draw (cross-cutting, all particle rendering)

**Source:** `src/core/sprite_utils.py:7-39` — `draw_sprite(x, y, coll_w, coll_h, bank, u, v, visual_w, visual_h, facing_right, colkey=0, scale=None)`.
**Apply to:** `Particle.draw` + any blob-growth sprite draw. Use `bank=2`, `coll_w=coll_h=PARTICLE_SIZE` (particles have no collision), `colkey=0` (default black-transparent — Pitfall 5 applies: never draw with index 0 on `particles.png`).

### Atomic JSON Save + `try/except KeyError` Evolution Guard (preset I/O)

**Source:** `src/ui/presets.py:21-44` (atomic write: `.tmp` + `os.fsync` + `os.replace`) and lines 58-62 (silent KeyError skip).
**Apply to:** anim-duration preset extensions in `presets.py` — DO NOT remove the atomic pattern; DO split the `except KeyError` path so anim-prefixed keys route through `tuning.set_anim_value` (Pitfall 6 fix).

---

## No Analog Found

All 16 target files have an in-repo analog. Zero "new paradigm" introductions in Phase 31.

**Closest gaps** (still have an analog, but with caveats):
- `BlobGrowth` class (new concept for fused-blob multi-frame growth) — **closest analog:** `src/entities/effects.py:6-33` `Effect` class (multi-frame animated effect with frame counter + `is_active` + `draw(cam_x, cam_y)`). Reuse that shape, swap `pyxel.blt` to `draw_sprite` against bank 2 growth-frame strip. Per RESEARCH Open Question 3, blob growth is the one Phase 31 effect that genuinely benefits from tier-2 `AnimPlayer(clip)` wrapping.
- Anim-keys-in-preset-dict plumbing (`tuning.get_anim_value`, `tuning.set_anim_value`, `_anim_flat_index`) — **no direct analog;** pattern synthesized from existing flat `_flat_index` API. This is the one genuinely new API surface; planner should keep it minimal (same signatures as `get_baseline`/`set_value` but dispatching into the nested `SimpleNamespace` tree).

---

## Metadata

**Analog search scope:**
- `src/anim/` — all 5 files read
- `src/core/` — `tuning.py`, `sprite_utils.py`, `schema.py` (checked for load pattern)
- `src/entities/` — `player.py` (event emits, `_update_anim_driver`, on_block_break), `effects.py`, spot-checked `projectile.py`
- `src/ui/` — `panel.py`, `presets.py`, `widgets.py`
- `tests/` — `conftest.py`, `test_anim.py`, `test_tuning.py`, `test_sprite_assets.py`
- `main.py` — SPRITE_MANIFEST, `_load_sprites`, `spawn_explosion`, update/draw scaffolding
- `assets/` — verified `assets/anim-schema.json` does NOT yet exist; `assets/sprites/*.png` layout convention (16px Y stride on bank 1) confirmed

**Files scanned:** 19

**Key references cited above (abbreviated for planner):**
- `src/anim/player_anim.py:14-23, 32-37, 40-56, 60-64, 67-69`
- `src/anim/anim_player.py:6-34`
- `src/anim/state_machine.py:11-34`
- `src/anim/anim_clip.py:6-18`
- `src/anim/event_bus.py:13-19`
- `src/entities/player.py:97, 235-239, 259, 535, 563, 587, 639, 699, 727, 780, 785, 794, 815, 847-858`
- `src/entities/effects.py:6-33, 35-62`
- `src/core/tuning.py:50-104, 130-139, 266-276, 284`
- `src/core/sprite_utils.py:7-39`
- `src/ui/panel.py:55-75, 85-137, 271-301`
- `src/ui/presets.py:9-18, 21-44, 47-63`
- `src/ui/widgets.py:108-287, 378-399`
- `main.py:126, 144-154, 160-175, 264-276, 305-313, 544-547, 825-828`
- `tests/conftest.py:19-37`
- `tests/test_anim.py:36-54, 69-74, 89-138, 145-188, 199-205, 219-246`
- `tests/test_tuning.py:140-167`

**Pattern extraction date:** 2026-04-21
