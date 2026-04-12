# Phase 27: Diagnostic Overlays - Research

**Researched:** 2026-04-12
**Domain:** Pyxel debug overlay rendering, spatial visualization, frame-time measurement
**Confidence:** HIGH

## Summary

Phase 27 adds four independent debug overlays (F2-F5) to the Pyxel game loop, rendering hitbox wireframes, velocity vectors with a frame-time graph, input state spatial blips, and slime follow diagnostics. The implementation is architecturally simple: a new `src/core/overlays.py` module with module-level boolean flags (matching `debug.py`'s pattern), called at the end of the draw pass. All rendering uses Pyxel's built-in primitives (`rectb`, `line`, `pset`, `circ`, `circb`, `text`). No external libraries are needed.

The main complexity lies in (1) correctly accessing entity state without modifying it, (2) managing pre-allocated ring buffers for blip history and frame-time data, and (3) subscribing to the event bus for coyote/buffer blip placement. The UI-SPEC (27-UI-SPEC.md) is already approved and provides pixel-precise color, positioning, and sizing contracts.

**Primary recommendation:** Build a single `src/core/overlays.py` module with four independent draw functions, each gated by a module-level boolean flag. The overlay manager receives a reference to the Game instance (which holds player, slime, enemies, doors, etc.) and reads state without mutation. Frame-time measurement uses `time.perf_counter()` since Pyxel does not expose per-frame timing.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Centralized overlay manager in `src/core/overlays.py` with a single post-draw pass. All overlay rendering happens after game draw — entities do not check overlay flags in their own draw() methods.
- **D-02:** `src/core/debug.py` stays separate for god-mode toggles (Ctrl+1/2/3). Overlays are a new system, not an extension of debug.py.
- **D-03:** Pure visual overlays — no text or numerical readouts. Rects, arrows, path lines, color-coded states only. Phase 28's live-tuning panel owns all numbers and editing.
- **D-04:** Coyote time and jump buffer shown as ephemeral spatial blips: a blip where the actual jump/land happened (mechanic trigger) and a blip where the player pressed jump (input event). Blips fade after a short time, showing the spatial gap between trigger and press.
- **D-05:** Slime overlay shows both: (a) follow path trail — breadcrumb dots from the position history deque, color-coded by age; (b) distance threshold boundaries — circles/lines showing SLIME_MAX_DIST and SLIME_REFORM_DIST around the player.
- **D-06:** No button state HUD for now — spatial blips are sufficient alongside Phase 28 panel.

### Claude's Discretion
- F-key assignment (which overlay on which key) — choose sensible defaults
- Overlay colors — pick colors that contrast with the cavern tileset
- Blip fade duration and visual style

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TOOL-08 | Diagnostic overlays toggled independently via F2-F5: hitbox wireframes, velocity vectors, input state glyphs + coyote/buffer timers, frame-time graph | Overlay manager architecture, Pyxel draw primitives, ring buffer patterns, event bus subscription for blip triggers |
| TOOL-09 | Slime-specific diagnostic overlay showing follow anchor, target point, stuck detection state, catch-up state | Slime entity state access (history deque, target_x/y, dx/dy), distance threshold circles from tuning values |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pyxel | 2.x (existing) | Game engine — all draw primitives | Already the project's engine; `rectb`, `line`, `pset`, `circ`, `circb`, `text` cover all overlay needs [VERIFIED: codebase grep] |
| Python `time` | stdlib | `time.perf_counter()` for frame-time measurement | Pyxel does not expose per-frame wall-clock timing; `perf_counter()` is the standard high-resolution timer [ASSUMED] |
| `src/anim/event_bus.py` | Phase 26 | Subscribe to `jump_start`, `land`, `fall_start` events for blip placement | Already emits gameplay events from player.py [VERIFIED: codebase grep] |
| `src/core/tuning.py` | Phase 24 | Read `SLIME_MAX_DIST`, `SLIME_REFORM_DIST`, `SLIME_FOLLOW_DELAY` at draw time | PEP 562 flat-key access pattern [VERIFIED: codebase grep] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `collections.deque` | stdlib | Ring buffers for blip history (32 entries) and frame-time history (64 entries) | Pre-allocated fixed-size buffers per performance contract |

### Alternatives Considered
None. No external dependencies needed — Pyxel primitives and stdlib cover everything.

**Installation:**
```bash
# No new packages required
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── core/
│   ├── overlays.py      # NEW — overlay manager + four draw functions
│   ├── debug.py          # UNCHANGED — god-mode toggles (Ctrl+1/2/3)
│   └── tuning.py         # READ ONLY — slime distance thresholds
├── entities/
│   ├── player.py         # READ ONLY — hitbox, velocity, coyote/buffer state
│   └── slime.py          # READ ONLY — history deque, target_x/y, dx/dy
└── anim/
    └── event_bus.py      # SUBSCRIBE — jump_start, land, fall_start for blips
```

### Pattern 1: Module-Level Boolean Flags (matches debug.py)
**What:** Four module-level booleans (`show_hitboxes`, `show_velocity`, `show_input`, `show_slime`) toggled by F2-F5 keypresses.
**When to use:** Always — this is the established pattern from `src/core/debug.py` (D-02).
**Example:**
```python
# Source: src/core/debug.py established pattern [VERIFIED: codebase]
import pyxel

show_hitboxes = False      # F2
show_velocity = False      # F3
show_input = False         # F4
show_slime = False         # F5

def update():
    """Toggle overlay flags. Call from Game.update() AFTER debug.update()."""
    global show_hitboxes, show_velocity, show_input, show_slime
    if pyxel.btnp(pyxel.KEY_F2):
        show_hitboxes = not show_hitboxes
    if pyxel.btnp(pyxel.KEY_F3):
        show_velocity = not show_velocity
    if pyxel.btnp(pyxel.KEY_F4):
        show_input = not show_input
    if pyxel.btnp(pyxel.KEY_F5):
        show_slime = not show_slime
```

### Pattern 2: Post-Draw Pass with Game Reference
**What:** The overlay `draw()` function receives the Game instance and reads entity state through it, drawing after all game entities have been drawn.
**When to use:** Always — mandated by D-01.
**Example:**
```python
# Source: main.py _draw_game_world() pattern [VERIFIED: codebase]
def draw(game):
    """Draw all active overlays. Call at end of Game._draw_game_world()."""
    if show_slime:
        _draw_slime_overlay(game)
    if show_hitboxes:
        _draw_hitbox_overlay(game)
    if show_velocity:
        _draw_velocity_overlay(game)
    if show_input:
        _draw_input_overlay(game)
    _draw_toggle_indicator()
```

### Pattern 3: Pre-Allocated Ring Buffers
**What:** Fixed-size `deque(maxlen=N)` for blip history and frame-time data. No per-frame allocations.
**When to use:** For blip history (maxlen=32) and frame-time graph (maxlen=64).
**Example:**
```python
from collections import deque

# Pre-allocated at module load — no per-frame allocation
_frame_times = deque(maxlen=64)          # 64 frames of timing data
_coyote_blips = deque(maxlen=32)         # Spatial blip ring buffer
_buffer_blips = deque(maxlen=32)         # Jump buffer blip ring buffer
```

### Pattern 4: Event Bus Subscription for Blip Placement
**What:** Subscribe to `fall_start` (coyote trigger) and `jump_start` (jump trigger) events to record world-space positions where mechanics activated.
**When to use:** For F4 input state blips (D-04).
**Example:**
```python
from src.anim import event_bus

def _init_subscriptions(game):
    """Subscribe to events for blip placement. Call once at game init."""
    event_bus.subscribe("fall_start", lambda: _record_coyote_blip(game))
    event_bus.subscribe("jump_start", lambda: _record_jump_blip(game))
```

### Anti-Patterns to Avoid
- **Modifying entity state in draw:** Overlays must NEVER write to `player.x`, `slime.dx`, etc. Read-only access only.
- **Per-frame object allocation:** Do NOT append to unbounded lists or create objects in draw. Use pre-allocated deques with maxlen.
- **Checking overlay flags inside entity draw():** Per D-01, entities do not know about overlays. All overlay rendering happens in the centralized post-draw pass.
- **Using `pyxel.blt` or image banks:** Per UI-SPEC performance contract, overlays use only primitives (`rectb`, `line`, `pset`, `circ`, `circb`). No sprite sheet access.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Ring buffer | Custom list + index management | `collections.deque(maxlen=N)` | stdlib, O(1) append/pop, automatic eviction [VERIFIED: stdlib docs] |
| Event subscription | Custom callback registry | `src/anim/event_bus.subscribe()` | Already exists from Phase 26, synchronous, single-threaded safe [VERIFIED: codebase] |
| Tuning value access | Hardcoded distance thresholds | `tuning.SLIME_MAX_DIST`, `tuning.SLIME_REFORM_DIST` | Source of truth from Phase 24; live-mutable for Phase 28 [VERIFIED: codebase] |
| High-res timer | `time.time()` or `pyxel.frame_count` delta | `time.perf_counter()` | Microsecond resolution on all platforms, not affected by system clock changes [ASSUMED] |

**Key insight:** This phase has zero external dependencies. Every building block (draw primitives, event bus, tuning values, ring buffers) already exists in the codebase or stdlib.

## Common Pitfalls

### Pitfall 1: Camera Offset Not Applied to Overlay Drawing
**What goes wrong:** Overlays draw at world-space coordinates but the camera is offset, causing hitboxes and blips to appear displaced from their entities.
**Why it happens:** `pyxel.camera()` is set during `_draw_game_world()`. If overlay `draw()` is called after camera reset, world-space positions will be wrong.
**How to avoid:** Call `overlays.draw(game)` INSIDE `_draw_game_world()`, BEFORE `pyxel.clip()` / `pyxel.camera()` reset in the main `draw()` method. The camera must still be set to world-space offset when overlays draw. [VERIFIED: main.py line 770-772 shows clip/camera reset happens AFTER `_draw_game_world()` returns]
**Warning signs:** Hitboxes shift when the camera moves but entities don't.

### Pitfall 2: Toggle Indicator Needs Screen-Space, Not World-Space
**What goes wrong:** The "F2 F3 F4 F5" toggle indicator in the top-left scrolls with the camera.
**Why it happens:** It's drawn while `pyxel.camera()` is set to world offset.
**How to avoid:** Draw the toggle indicator in `Game.draw()` AFTER `pyxel.camera()` is reset to (0,0), not inside `_draw_game_world()`. This means the indicator draw call is separate from the main overlay draw call.
**Warning signs:** Toggle text scrolls off-screen when camera moves.

### Pitfall 3: Frame-Time Graph Measures Overlay Cost Too
**What goes wrong:** If frame time is measured around the entire update+draw cycle, the overlay drawing time is included, making the measurement non-representative of gameplay cost.
**Why it happens:** Naive measurement wraps the whole frame.
**How to avoid:** Measure `perf_counter()` delta between consecutive `update()` calls (or at the start of `update()`), not across draw. This captures the wall-clock time of one full frame including the previous draw, which is what matters for dropped-frame detection.
**Warning signs:** Frame-time graph shows spikes when overlays are toggled on.

### Pitfall 4: Slime Distance Circles Can Be Huge
**What goes wrong:** `SLIME_MAX_DIST` is 100 pixels — drawing `circb` with radius 100 creates a large circle that extends well beyond the 320x192 viewport.
**Why it happens:** Pyxel's `circb` draws the full circle even if most is off-screen. This is fine for performance (Pyxel clips internally) but may look odd.
**How to avoid:** This is expected behavior. The circle IS large — that's the point. Pyxel handles clipping internally. No action needed, but be aware the circle will dominate the screen. [VERIFIED: SLIME_MAX_DIST = 100 in physics-schema.json]
**Warning signs:** None — this is by design.

### Pitfall 5: Event Bus Subscriptions Not Cleaned Up
**What goes wrong:** If overlays.py subscribes to events at import time, and the module is re-imported (e.g., in tests), duplicate subscriptions accumulate.
**Why it happens:** Module-level side effects on import.
**How to avoid:** Use a lazy initialization pattern — subscribe on first `update()` call using a module-level `_initialized` flag. Or subscribe in a dedicated `init(game)` function called from `Game.__init__()`.
**Warning signs:** Blips appear duplicated or events fire multiple callbacks.

### Pitfall 6: Blip World Positions Become Invalid After Room Transition
**What goes wrong:** Coyote/buffer blips store world-space (x, y) from the previous room. After a room transition, the camera shows a different area, so old blips render in wrong positions or off-screen.
**How to avoid:** Clear the blip deques on room transition. Either subscribe to a room-change event or clear in `update()` when the camera snaps.
**Warning signs:** Ghost blips from previous rooms visible for 0.5 seconds after transition.

## Code Examples

### Entity Hitbox Access Pattern
```python
# Source: main.py entity lists [VERIFIED: codebase grep]
# Game instance holds all entity lists with .x, .y, .w, .h attributes

def _draw_hitbox_overlay(game):
    PLAYER_COLOR = 8   # Red
    SLIME_COLOR = 11   # Green
    ENEMY_COLOR = 9    # Orange
    PROJ_COLOR = 10    # Yellow
    STATIC_COLOR = 6   # Light grey
    BOSS_COLOR = 2     # Dark purple

    p = game.player
    pyxel.rectb(p.x, p.y, p.w, p.h, PLAYER_COLOR)

    s = game.slime
    if not s.is_fused and not s.is_dissipated:
        pyxel.rectb(s.x, s.y, s.w, s.h, SLIME_COLOR)

    for e in game.enemies:
        pyxel.rectb(e.x, e.y, e.w, e.h, ENEMY_COLOR)

    for proj in game.projectiles:
        pyxel.rectb(proj.x, proj.y, proj.w, proj.h, PROJ_COLOR)

    for door in game.doors:
        pyxel.rectb(door.x, door.y, door.w, door.h, STATIC_COLOR)

    if game.mole:
        pyxel.rectb(game.mole.x, game.mole.y, game.mole.w, game.mole.h, BOSS_COLOR)
```

### Velocity Arrow Drawing
```python
# Source: 27-UI-SPEC.md color contract [VERIFIED: UI-SPEC]
ARROW_MIN_LEN = 8       # Minimum arrow length in pixels
ARROW_MAX_LEN = 32      # Maximum arrow length in pixels
VEL_SCALE = 8           # Pixels per unit velocity
H_COLOR = 8             # Red — horizontal
V_COLOR = 12            # Blue — vertical

def _draw_velocity_arrow(cx, cy, dx, dy):
    # Horizontal component
    hlen = min(ARROW_MAX_LEN, max(ARROW_MIN_LEN, abs(dx) * VEL_SCALE))
    if abs(dx) > 0.01:
        end_x = cx + (hlen if dx > 0 else -hlen)
        pyxel.line(cx, cy, end_x, cy, H_COLOR)
    # Vertical component
    vlen = min(ARROW_MAX_LEN, max(ARROW_MIN_LEN, abs(dy) * VEL_SCALE))
    if abs(dy) > 0.01:
        end_y = cy + (vlen if dy > 0 else -vlen)
        pyxel.line(cx, cy, cx, end_y, V_COLOR)
```

### Frame-Time Measurement Pattern
```python
# Source: Python stdlib time module [ASSUMED]
import time

_frame_times = deque(maxlen=64)
_last_frame_time = 0.0

def _update_frame_time():
    global _last_frame_time
    now = time.perf_counter()
    if _last_frame_time > 0:
        delta_ms = (now - _last_frame_time) * 1000.0  # Convert to milliseconds
        _frame_times.append(delta_ms)
    _last_frame_time = now
```

### Slime Follow Overlay Pattern
```python
# Source: slime.py history deque + tuning values [VERIFIED: codebase]
def _draw_slime_overlay(game):
    s = game.slime
    p = game.player
    player_cx = p.x + p.w // 2
    player_cy = p.y + p.h // 2

    # Breadcrumb trail from history deque
    TRAIL_RECENT_COLOR = 11   # Green (0-10 entries)
    TRAIL_MID_COLOR = 3       # Dark green (11-20 entries)
    TRAIL_OLD_COLOR = 5       # Dark grey (21+ entries)
    for i, (hx, hy) in enumerate(s.history):
        if i <= 10:
            color = TRAIL_RECENT_COLOR
        elif i <= 20:
            color = TRAIL_MID_COLOR
        else:
            color = TRAIL_OLD_COLOR
        pyxel.pset(hx, hy, color)

    # Distance threshold circles centered on player
    pyxel.circb(player_cx, player_cy, tuning.SLIME_MAX_DIST, 8)    # Red
    pyxel.circb(player_cx, player_cy, tuning.SLIME_REFORM_DIST, 10) # Yellow

    # Follow target point
    pyxel.circ(s.target_x, s.target_y, 1, 14)  # Pink dot
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| No debug visualization | Module-level boolean flags (debug.py Ctrl+1/2/3) | Phase 7 (v1.0) | Established the pattern this phase extends |
| Hardcoded sprite frames | AnimFSM + event bus | Phase 26 (v2.0) | Event bus now available for overlay subscriptions |
| Constants in constants.py | tuning.py PEP 562 flat access | Phase 24 (v2.0) | Distance thresholds read via tuning.X, live-mutable |

## Integration Points (Critical)

### main.py Changes Required
1. **Import:** `from src.core import overlays` at top of main.py
2. **Update:** Add `overlays.update()` in `Game.update()` after `debug.update()` (line ~401)
3. **Draw (world-space):** Add `overlays.draw(self)` at end of `_draw_game_world()`, after `self.player.draw()` (line ~834), BEFORE the victory overlay
4. **Draw (screen-space):** Add `overlays.draw_indicator()` in `Game.draw()` after `pyxel.camera()` reset (line ~772), before `self._draw_hud()`

### Entity State Access (Read-Only)
| Entity | Attributes Read | Source |
|--------|----------------|--------|
| `game.player` | `.x`, `.y`, `.w`, `.h`, `.dx`, `.dy`, `.coyote_timer`, `.jump_buffer_timer` | player.py [VERIFIED] |
| `game.slime` | `.x`, `.y`, `.w`, `.h`, `.dx`, `.dy`, `.target_x`, `.target_y`, `.history`, `.is_fused`, `.is_dissipated` | slime.py [VERIFIED] |
| `game.enemies` | `[e].x`, `[e].y`, `[e].w`, `[e].h` | enemies.py [VERIFIED] |
| `game.projectiles` | `[p].x`, `[p].y`, `[p].w`, `[p].h` | player.py projectile list [VERIFIED] |
| `game.doors` | `[d].x`, `[d].y`, `[d].w`, `[d].h` | map_entities.py [VERIFIED] |
| `game.mole` | `.x`, `.y`, `.w`, `.h` (may be None) | boss.py [VERIFIED] |
| `tuning.SLIME_MAX_DIST` | Distance threshold (100) | physics-schema.json [VERIFIED] |
| `tuning.SLIME_REFORM_DIST` | Reform distance (8) | physics-schema.json [VERIFIED] |

### Event Bus Subscriptions
| Event | Emitter | Overlay Use |
|-------|---------|-------------|
| `jump_start` | player.py line 516 | Record jump-press blip position [VERIFIED] |
| `fall_start` | player.py (emitted on ground-leave) | Record coyote-trigger blip position [VERIFIED] |
| `land` | player.py | Record land position for buffer-to-land connector [VERIFIED: event_bus.py subscribe API] |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `time.perf_counter()` provides sufficient resolution for frame-time graphing at 60fps | Standard Stack / Code Examples | LOW — stdlib perf_counter has microsecond resolution on all major platforms; if wrong, `time.perf_counter_ns()` is available |
| A2 | Pyxel's `circb` handles large radii (100px) without performance issues | Pitfall 4 | LOW — Pyxel clips drawing to screen bounds internally; worst case is a few extra pixel calculations |
| A3 | `fall_start` event is emitted by player.py when the player leaves the ground | Integration Points | LOW — confirmed at player.py:680 [VERIFIED] |

## Open Questions (RESOLVED)

1. **Does `fall_start` event exist in current codebase?**
   - RESOLVED: Yes — player.py:680 confirms `event_bus.emit("fall_start")` is emitted when the player leaves the ground. No fallback needed.

2. **Stuck detection threshold for slime overlay**
   - RESOLVED: Overlay maintains its own stuck counter (0.1 velocity threshold, 10 consecutive frames). slime.py does not track stuck state — the counter is overlay-internal per D-05 read-only constraint.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | none — uses default discovery |
| Quick run command | `python -m pytest tests/test_overlays.py -x -q` |
| Full suite command | `python -m pytest tests/ -x -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TOOL-08a | F2-F5 toggle flags independently | unit | `pytest tests/test_overlays.py::test_toggle_flags -x` | Wave 0 |
| TOOL-08b | Hitbox overlay reads entity positions without mutation | unit | `pytest tests/test_overlays.py::test_hitbox_no_mutation -x` | Wave 0 |
| TOOL-08c | Frame-time ring buffer stays at maxlen=64 | unit | `pytest tests/test_overlays.py::test_frame_time_buffer -x` | Wave 0 |
| TOOL-08d | Blip ring buffer stays at maxlen=32 | unit | `pytest tests/test_overlays.py::test_blip_buffer_maxlen -x` | Wave 0 |
| TOOL-09a | Slime trail reads history deque without modification | unit | `pytest tests/test_overlays.py::test_slime_trail_readonly -x` | Wave 0 |
| TOOL-09b | Stuck detection counter increments on low velocity | unit | `pytest tests/test_overlays.py::test_stuck_detection -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_overlays.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_overlays.py` — covers TOOL-08, TOOL-09 (unit tests for flag toggling, buffer management, read-only access)
- No framework install needed — pytest already configured with conftest.py fixtures

## Security Domain

Not applicable. This phase adds debug visualization with no user input beyond F-key toggles, no network access, no file I/O, no data persistence. All overlay state is ephemeral in-memory booleans and ring buffers.

## Sources

### Primary (HIGH confidence)
- `src/core/debug.py` — established toggle pattern (module-level booleans, Ctrl+1/2/3)
- `main.py` — game loop structure, `_draw_game_world()` draw order, entity lists
- `src/entities/slime.py` — history deque, target_x/y, distance check logic
- `src/entities/player.py` — coyote_timer, jump_buffer_timer, dx/dy velocity
- `src/anim/event_bus.py` — subscribe/emit API
- `src/core/tuning.py` — PEP 562 flat access to SLIME_MAX_DIST (100), SLIME_REFORM_DIST (8)
- `assets/physics-schema.json` — slime_follow group with distance values
- `.planning/phases/27-diagnostic-overlays/27-UI-SPEC.md` — pixel-precise visual contract
- `.planning/phases/27-diagnostic-overlays/27-CONTEXT.md` — locked decisions D-01 through D-06

### Secondary (MEDIUM confidence)
- [Pyxel GitHub](https://github.com/kitao/pyxel) — draw primitive API reference

### Tertiary (LOW confidence)
- `time.perf_counter()` resolution assumption (A1) — based on Python stdlib documentation, not verified in this Pyxel context

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies, all primitives verified in codebase
- Architecture: HIGH — follows established debug.py pattern, integration points mapped precisely
- Pitfalls: HIGH — camera offset, screen-space vs world-space, and buffer management are well-understood from codebase analysis

**Research date:** 2026-04-12
**Valid until:** 2026-05-12 (stable — no external dependency drift risk)
