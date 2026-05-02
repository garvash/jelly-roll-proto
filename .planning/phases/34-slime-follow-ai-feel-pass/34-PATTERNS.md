# Phase 34: Slime Follow / AI Feel Pass - Pattern Map

**Mapped:** 2026-05-02
**Files analyzed:** 8 (5 modify, 3 create)
**Analogs found:** 8 / 8 (every file has a strong in-tree analog)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/entities/slime.py` (modify) | entity | per-frame transform (request-response on update) | self (extend in place — pattern at L46-98 dissipate/reform; L100-176 update) | exact (in-place extension) |
| `assets/physics-schema.json` (modify) | config | static load | self (existing `slime_follow` group at L60-65) | exact (additive) |
| `main.py` (modify) | entry / orchestrator | per-frame dispatch | self (existing `self.slime.update(...)` call site at L875; punt collision block at L912-916) | exact (in-place edit) |
| `src/core/overlays.py` (modify) | overlay/diagnostic | read-only render | self (`_draw_slime_overlay` at L430-491; catch-up arrow L478-490) | exact (additive extend) |
| `assets/output.ldtk` (modify — placeholder) | level data | static load | `Gym_AccelRunway` (L1-20 simplified/data.json — minimal level header pattern) | role-match (LDtk-authored, agent only places stub per D-16) |
| `tests/test_slime.py` (modify — extend) | test | unit | self (existing tests L1-117 for init/follow/regen/scaling/reform) | exact (additive test functions) |
| `tests/test_tuning_migration.py` (modify — extend) | test | unit | self (existing Phase 33 schema-key smoke tests L1-60) | exact (additive parametrize rows) |
| `tests/test_overlays.py` (modify — extend) | test | unit | self (existing MockSlime + draw-dispatch tests L1-60) | exact (additive test functions) |
| `.planning/phases/34-.../34-FEEL-TARGETS.md` (already drafted; verification fills Result column) | doc | audit-trail | `33-FEEL-TARGETS.md` (L1-119) | exact (format mirror) |

## Pattern Assignments

---

### `src/entities/slime.py` (entity, per-frame transform)

**Analog:** self — extend the existing `Slime.update()` (L100-176) and `dissipate()`/`reform()` primitive (L79-98, L234-253).

**Imports pattern** (slime.py L1-6 — already in place, no additions needed):
```python
import pyxel
from collections import deque
import src.core.debug as debug
from src.anim import event_bus
from src.core import tuning
from src.core.sprite_utils import draw_sprite
```
All new tunables resolve via the existing `tuning.X` PEP 562 `__getattr__` indirection (e.g. `tuning.SLIME_MAX_FOLLOW_SPEED`). No new imports needed for Wave 1 feel-tuning. If event-bus emission is desired for mode-switch (`slime_mode_change`), `event_bus` is already imported.

**`__init__` extension pattern** (mirror existing fusion-state initializer block at slime.py L27-31):
```python
# Fusion system state (D-01 through D-05)
self.is_recalling = False       # True when zipping toward player
self.is_dissipated = False      # True during burnout cooldown (D-05)
self.dissipate_timer = 0        # Frames remaining before reform
self.recall_trail = []          # List of (x, y) for visual trail
```
Phase 34 adds (same comment-block style):
```python
# Phase 34 AI surfaces (D-08 mode FSM, D-10 stuck recovery, D-11 lookahead)
self.mode_is_float = True              # D-08: True=float, False=ground
self.mode_frames_in_state = 0          # D-08 hysteresis counter
self.stuck_frames = 0                  # D-10: consecutive no-progress frames
self._stuck_recovery_target = None     # D-10: (x, y) target for fade-in reposition
```

**Reusable fade primitive** (slime.py L79-98 — `dissipate()` + `update_dissipation()`):
```python
def dissipate(self):
    """Slime burns out from juice empty while fused (D-05). SF6 burnout."""
    self.is_dissipated = True
    self.dissipate_timer = tuning.SLIME_DISSIPATE_COOLDOWN
    self.is_fused = False
    self.is_recalling = False
    self.is_being_absorbed = False
    self.recall_trail.clear()

def update_dissipation(self, player_x, player_y, player_facing_right, level_map):
    """Tick dissipation timer. Returns True when reform happens."""
    if not self.is_dissipated:
        return False
    self.dissipate_timer -= 1
    if self.dissipate_timer <= 0:
        self.is_dissipated = False
        self.juice = self.max_juice  # Reform at full juice (D-05)
        self.reform(player_x, player_y, player_facing_right, level_map)
        return True
    return False
```
**D-10 `reposition_with_fade()` helper to add** — same structural shape as `dissipate()`:
- Set `is_dissipated = True`, set `dissipate_timer = tuning.SLIME_STUCK_RECOVERY_COOLDOWN`
- Stash `_stuck_recovery_target = (target_x, target_y)`
- Do **NOT** reset juice (the player did nothing wrong — slime got stuck)
- Reuse `update_dissipation()` discriminator: when `_stuck_recovery_target` is set, snap to that point and clear the field; else fall through to existing `juice = max_juice` + `reform()` path.

**Existing magic-number to promote** (slime.py L154-159 — D-05 promotion site):
```python
# Clamp velocity to avoid teleporting if player moves very fast,
# but keep it high enough to feel perfectly responsive.
# 4.0 is faster than player's max speed (2.5)
MAX_SHADOW_SPEED = 4.0
self.dx = max(-MAX_SHADOW_SPEED, min(self.dx, MAX_SHADOW_SPEED))
self.dy = max(-MAX_SHADOW_SPEED, min(self.dy, MAX_SHADOW_SPEED))
```
Replace the `MAX_SHADOW_SPEED = 4.0` literal with `tuning.SLIME_MAX_FOLLOW_SPEED` references; whole linear-clamp block is replaced by the sqrt ease-out per D-09 (RESEARCH §Pattern 1).

**Path-follow base (PRESERVED per D-03)** (slime.py L145-152):
```python
# --- Standard Path-Based Movement (Gradius Option Style) ---
self.history.append((player_x, player_y))

if len(self.history) >= tuning.SLIME_FOLLOW_DELAY:
    self.target_x, self.target_y = self.history[0]

self.dx = self.target_x - self.x
self.dy = self.target_y - self.y
```
D-11 lookahead bias attaches as a positional offset to `(target_x, target_y)` after the deque read — **do NOT** alter the deque, **do NOT** change the index.

**Dead-code strip targets (D-04 — separate plan):**
- Lines 25, 40-44 (instance attrs `is_punted`, `accel`, `friction`, `max_speed`, `gravity`, `jump_force`)
- Lines 129-143 (`if self.is_punted:` collision branch)
- Lines 178-182 (`def punt(self, dx, dy)`)
- `main.py` L912-916 (punt collision block)

---

### `assets/physics-schema.json` (config, static load)

**Analog:** self — existing `slime_follow` group at L60-65.

**Existing group** (L60-65):
```json
"slime_follow": {
  "SLIME_FOLLOW_DELAY": 16,
  "SLIME_MAX_DIST": 100,
  "SLIME_REFORM_DIST": 8,
  "SLIME_LERP_FACTOR": 0.4
},
```

**Phase 34 addition (additive — preserves existing keys):** Land 9 new keys (1 promoted + 8 new) inside the same `slime_follow` block — RESEARCH §Code Examples L478-494 has the full target shape:
```json
"slime_follow": {
  "SLIME_FOLLOW_DELAY": 16,
  "SLIME_MAX_DIST": 100,
  "SLIME_REFORM_DIST": 8,
  "SLIME_LERP_FACTOR": 0.4,
  "SLIME_MAX_FOLLOW_SPEED": 7.0,
  "SLIME_CATCHUP_CURVE_K": 0.50,
  "SLIME_LOOKAHEAD_FRAMES": 8,
  "SLIME_LOOKAHEAD_FALLBACK_BIAS": 4.0,
  "SLIME_LOOKAHEAD_EPSILON": 0.1,
  "SLIME_STUCK_WINDOW_FRAMES": 36,
  "SLIME_STUCK_RECOVERY_COOLDOWN": 30,
  "SLIME_FLOAT_GROUND_K_FRAMES": 12,
  "SLIME_MODE_HYSTERESIS_FRAMES": 6
}
```

**Auto-discovery contract:** group is already in `FEEL_GROUPS` (`src/ui/presets.py:18-22`) and the Slime tab (`src/ui/panel.py:95`). No panel code change required.

---

### `main.py` (entry / orchestrator, per-frame dispatch)

**Analog:** self — current call site at L875.

**Existing call site** (main.py L875):
```python
self.slime.update(self.player.x, self.player.y, self.player.facing_right, self.level_map, self.player.is_fused)
```

**Phase 34 extension:** thread `player.dx` and `player.is_grounded` through (per RESEARCH Pitfall 1 + Open Question 2 — pass explicit primitives, not a Player ref):
```python
self.slime.update(
    self.player.x, self.player.y, self.player.facing_right,
    self.level_map, self.player.is_fused,
    player_dx=self.player.dx,                    # D-11 lookahead bias
    player_is_grounded=self.player.is_grounded,  # D-08 mode FSM
)
```

**Dead-code strip site** (main.py L912-916 — D-04):
```python
if self.slime.is_punted and e.check_collision(self.slime.x, self.slime.y, self.slime.w, self.slime.h):
    e.take_damage()
    self.spawn_explosion(e.x, e.y, 10)
    self.slime.dx *= -0.5
    self.slime.dy = -2.0
```
Whole block deleted in the D-04 housekeeping plan (separate from feel-tuning plan).

---

### `src/core/overlays.py` (overlay/diagnostic, read-only render)

**Analog:** self — `_draw_slime_overlay()` at L430-491; existing catch-up arrow at L478-490; existing constants block at L82-98.

**Existing catch-up arrow primitive** (overlays.py L478-490):
```python
# Catch-up arrow — blue line from slime toward target when actively chasing
if vel_mag > STUCK_VEL_THRESHOLD:
    dist_to_target_sq = (s.target_x - s.x) ** 2 + (s.target_y - s.y) ** 2
    if dist_to_target_sq > SLIME_REFORM_DIST ** 2:
        scx = s.x + s.w // 2
        scy = s.y + s.h // 2
        dist = dist_to_target_sq ** 0.5
        if dist > 0:
            dx_norm = (s.target_x - scx) / dist
            dy_norm = (s.target_y - scy) / dist
            end_x = scx + int(dx_norm * _CATCHUP_ARROW_LEN)
            end_y = scy + int(dy_norm * _CATCHUP_ARROW_LEN)
            pyxel.line(scx, scy, end_x, end_y, _CATCHUP_COLOR)
```
**D-02 Phase 34 surfaces — copy this primitive shape for the lookahead-bias arrow.** Use a new color constant (e.g. `_LOOKAHEAD_COLOR = 7` white) added to the L82-98 constants block. Same `pyxel.line(scx, scy, end_x, end_y, ...)` shape; vector source = lookahead bias amount.

**Existing stuck-counter pattern** (overlays.py L83, L462-466) — currently overlay-internal, will become a **read** of entity state per Pitfall 7 + Open Question 4:
```python
_slime_stuck_frames = 0            # Consecutive frames with velocity < threshold
STUCK_VEL_THRESHOLD = 0.1         # Velocity magnitude threshold
STUCK_FRAME_THRESHOLD = 10        # Frames before stuck indicator shows
...
vel_mag = (s.dx ** 2 + s.dy ** 2) ** 0.5
if vel_mag < STUCK_VEL_THRESHOLD:
    _slime_stuck_frames += 1
else:
    _slime_stuck_frames = 0
```
**Phase 34 conversion:** delete the local `_slime_stuck_frames` increment; read `getattr(s, "stuck_frames", 0)` instead (defensive guard per Pitfall 7). Keep `STUCK_FRAME_THRESHOLD` for the X-flash visual gate.

**Mode glyph + stuck countdown bar — new additive elements** (RESEARCH §Code Examples L526-547 has the recipes):
```python
# Mode glyph (overlay): F=float (blue 12) / G=ground (green 11)
mode = getattr(s, "mode_is_float", None)
if mode is not None:
    glyph = "F" if mode else "G"
    color = 12 if mode else 11
    pyxel.text(s.x + s.w // 2 - 2, s.y - 8, glyph, color)

# Stuck countdown bar — only shows when half-way to firing
stuck = getattr(s, "stuck_frames", 0)
window = tuning.SLIME_STUCK_WINDOW_FRAMES
if stuck > window // 2:
    bar_w = max(1, int(s.w * (stuck / window)))
    pyxel.rect(s.x, s.y - 3, bar_w, 1, 8)
```

**Trust boundary** (preserve T-27-01 — overlays read, never write entity state). The local `_slime_stuck_frames` counter is deletable because the new `s.stuck_frames` is canonical and the overlay is a pure consumer.

---

### `assets/output.ldtk` (level data, static load — placeholder per D-16)

**Analog:** `Gym_AccelRunway` minimal level shape (`assets/output/simplified/Gym_AccelRunway/data.json` L1-20):
```json
{
    "identifier": "Gym_AccelRunway",
    "uniqueIdentifer": "b7839ef0-21a0-11f1-be70-719aa0d6868c",
    "x": 2240,
    "y": 352,
    "width": 640,
    "height": 176,
    "bgColor": "#696A79",
    "neighbourLevels": [...],
    "customFields" : {},
    "layers": ["IntGrid.png"],
    "entities" : {}
}
```
**Note:** The simplified/data.json is REGENERATED by the pml-to-ldtk pipeline. **DO NOT edit `assets/output/simplified/Gym_SlimeFollow/`** (per project memory `feedback_no_agent_level_authoring.md`). Plan task = open `assets/output.ldtk` in LDtk app, add `Gym_SlimeFollow` level (default minimal placeholder), commit. User finalizes the sealed-pocket geometry. Agent does not hand-edit the LDtk JSON.

---

### `tests/test_slime.py` (test, unit) — extend

**Analog:** self — existing tests L1-117 (init, follow, regen, scaling, reform).

**Existing test pattern** (test_slime.py L1-17 — pyxel mock + MockLevelMap + import):
```python
import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock pyxel before importing classes that use it
mock_pyxel = MagicMock()
sys.modules['pyxel'] = mock_pyxel
mock_pyxel.btn.return_value = False
mock_pyxel.btnp.return_value = False

from src.entities.slime import Slime
from src.entities.player import Player
from src.core.constants import *

class MockLevelMap:
    def check_collision(self, x, y, w, h):
        return False
```

**Existing follow-test pattern** (test_slime.py L26-41 — multi-frame loop to fill history deque):
```python
def test_slime_follow_logic():
    slime = Slime(0, 0)
    player_x, player_y = 100, 100
    player_facing_right = True

    level_map = MagicMock()
    level_map.check_collision.return_value = False
    # Fill history to reach SLIME_FOLLOW_DELAY
    for i in range(SLIME_FOLLOW_DELAY + 1):
        slime.update(player_x, player_y, player_facing_right, level_map)
    # Slime should have moved towards target (in front of player)
    assert slime.x > 0
    assert slime.y > 0
    # Target is raw player position; front offset applied separately via lerp
    assert slime.target_x == player_x
    assert slime.target_y == player_y
```
Phase 34 RED stubs (RESEARCH §Validation Architecture Wave 0) follow the same shape:
- `test_catchup_60f_budget` — loop 60 frames at 10-tile gap, assert dist closed below threshold
- `test_catchup_curve_shape` — assert `speed = k*sqrt(dist)` at fixed dist
- `test_stuck_recovery_fires` — pin slime in collision, assert `is_dissipated == True` after `SLIME_STUCK_WINDOW_FRAMES`
- `test_stuck_recovery_uses_dissipate` — assert `dissipate_timer` ticks during stuck recovery
- `test_mode_float_when_player_airborne` — `player_is_grounded=False` → `mode_is_float == True`
- `test_mode_ground_when_reachable` — grounded + reachable tile → `mode_is_float == False`
- `test_mode_hysteresis` — flip is_grounded each frame, assert mode does NOT flip every frame
- `test_lookahead_bias_dx` — `player_dx > 0` → `target_x` biased forward
- `test_lookahead_fallback_facing` — `player_dx ≈ 0`, `facing_right=True` → small forward bias
- `test_punt_attrs_stripped` (D-04) — `assert not hasattr(Slime(0,0), "is_punted")`

**Existing reform test** (test_slime.py L103-116 — assertion shape for repositioning):
```python
def test_slime_reform_logic():
    slime = Slime(0, 0)
    player_x, player_y = 200, 200 # Far away
    ...
    # Should have reformed (teleported)
    assert slime.x == player_x - SLIME_REFORM_DIST
    assert slime.y == player_y
    assert len(slime.history) == 0
```
Same assertion shape works for the stuck-recovery target test (assert `slime.x, slime.y` after dissipate timer ticks down).

---

### `tests/test_tuning_migration.py` (test, unit) — extend

**Analog:** self — Phase 33 schema-key smoke tests (L1-60).

**Existing parametrized smoke pattern** (test_tuning_migration.py L46-60):
```python
@pytest.mark.parametrize("key,expected", [
    ("WINDUP_DURATION_FRAMES",  EXPECTED_WINDUP_DURATION_FRAMES),
    ("ACCELERATED_REGEN_RATE",  EXPECTED_ACCELERATED_REGEN_RATE),
    ("POGO_BOUNCE_VELOCITY",    EXPECTED_POGO_BOUNCE_VELOCITY),
    ("POGO_COOLDOWN_FRAMES",    EXPECTED_POGO_COOLDOWN_FRAMES),
    ("DRILL_ENEMY_COST",        EXPECTED_DRILL_ENEMY_COST),
    ("SLIME_DAZE_COST",         EXPECTED_SLIME_DAZE_COST),
])
def test_new_tuning_key_readable(key, expected):
    actual = getattr(tuning, key)
    assert actual == expected, (
        f"tuning.{key} expected {expected!r}, got {actual!r}. "
        f"Pitfall 5: schema-seed must equal current hardcoded baseline."
    )
```
**Phase 34 addition:** add a `test_phase34_keys_loaded` parametrize block with the 9 new SLIME_* keys (using RESEARCH-recommended seed values from §Recommended Tunable Seeds):
```python
@pytest.mark.parametrize("key,expected", [
    ("SLIME_MAX_FOLLOW_SPEED",       7.0),
    ("SLIME_CATCHUP_CURVE_K",        0.50),
    ("SLIME_LOOKAHEAD_FRAMES",       8),
    ("SLIME_LOOKAHEAD_FALLBACK_BIAS",4.0),
    ("SLIME_LOOKAHEAD_EPSILON",      0.1),
    ("SLIME_STUCK_WINDOW_FRAMES",    36),
    ("SLIME_STUCK_RECOVERY_COOLDOWN",30),
    ("SLIME_FLOAT_GROUND_K_FRAMES",  12),
    ("SLIME_MODE_HYSTERESIS_FRAMES", 6),
])
def test_phase34_slime_keys_readable(key, expected): ...
```
Reuse the existing `_tuning_reset` autouse fixture (L30-34) — no new fixture needed.

---

### `tests/test_overlays.py` (test, unit) — extend

**Analog:** self — existing MockSlime (L43-51) + draw-dispatch tests (L1-60).

**Existing pyxel-mock + MockSlime pattern** (test_overlays.py L9-51):
```python
# Mock pyxel before importing overlays — force-replace to handle test ordering
_pyxel_mock = MagicMock()
sys.modules["pyxel"] = _pyxel_mock

# Remove cached overlays module so it re-imports with our mock pyxel
for mod_key in list(sys.modules):
    if mod_key.startswith("src.core.overlays"):
        del sys.modules[mod_key]

import src.core.overlays as overlays
...
class MockSlime(MockEntity):
    """Slime entity mock with additional slime-specific attributes."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_fused = False
        self.is_dissipated = False
        self.target_x = 50
        self.target_y = 60
        self.history = deque(maxlen=32)
```
**Phase 34 extension:** add `mode_is_float`, `stuck_frames` attrs to `MockSlime` so the new overlay surfaces don't AttributeError, and assert `pyxel.text` / `pyxel.rect` / `pyxel.line` are called with the expected glyphs and colors. Per project memory `feedback_pyxel_mock_false_positive.md`, verify call signatures against real Pyxel — `pyxel.text(x, y, str, col)` and `pyxel.rect(x, y, w, h, col)` are the correct shapes.

---

### `34-FEEL-TARGETS.md` (doc, audit-trail)

**Status:** Already drafted at context-gathering (per CONTEXT.md D-17). Verification phase fills the Result column in place.

**Analog:** `33-FEEL-TARGETS.md` (L1-119 — the most recent example with multi-prefix scheme and Reference Values + Results + Sign-off blocks).

**Format excerpt** (33-FEEL-TARGETS.md L20-28 — row table shape):
```markdown
## Charge Ritual Targets (D-C1..C5)

| ID    | Test                                                                    | Pass Condition                                                              | Fail Condition                                                                | Result  |
| ----- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------- |
| D-C1  | Tap-Z disambiguation: Press Z, release before SPIT_HOLD_THRESHOLD frames | Spit (or daze if fused) fires at release; no RECALL/WINDUP enters            | RECALL/WINDUP enters on sub-threshold tap, OR no projectile fires             | PENDING |
| D-C2  | Hold-Z disambiguation: Press Z, hold past SPIT_HOLD_THRESHOLD (~8f target)| RECALL enters at frame ~8 (slime starts returning); no spit fires on release | Spit fires AND RECALL enters (double-action), OR threshold feels >12f         | PENDING |
```

**Reference values block** (33-FEEL-TARGETS.md L65-90) and **Sign-off block** (L115-119) are mirrored in 34-FEEL-TARGETS.md (already drafted). Phase 34 prefix scheme is **S-Cn / S-Sn / S-Mn / S-Ln / S-Pn** per CONTEXT.md D-14.

---

## Shared Patterns

### Schema-key reading via `tuning.X`
**Source:** `src/entities/slime.py:127, 141, 148, 168` (live use sites — `tuning.JUICE_REGEN_RATE`, `tuning.SLIME_MAX_DIST`, `tuning.SLIME_FOLLOW_DELAY`, `tuning.TILE_SIZE`)
**Apply to:** every read of a Phase 34 tunable in `slime.py` AND `overlays.py`.
```python
# Source: existing pattern at slime.py:127 (juice regen) and slime.py:148 (follow delay).
self.juice = min(self.max_juice, self.juice + tuning.JUICE_REGEN_RATE)
...
if len(self.history) >= tuning.SLIME_FOLLOW_DELAY:
```
**Critical:** `tuning.X` resolves via PEP 562 `__getattr__` on `src.core.tuning`. Reading at module scope (top of file) breaks live reload — always read inside the function body per frame.

### Defensive overlay attribute access
**Source:** RESEARCH Pitfall 7 — "Overlay reads `slime.mode_is_float` before it exists"
**Apply to:** every Phase 34 entity-state read inside `_draw_slime_overlay()`.
```python
mode = getattr(s, "mode_is_float", None)
if mode is not None:
    ...

stuck = getattr(s, "stuck_frames", 0)
```
Keeps F5 toggle from crashing if entity-state wave hasn't shipped yet (inter-wave commit safety).

### Pyxel-mock test isolation
**Source:** `tests/test_overlays.py:9-19` (force-replace pyxel mock + clear cached overlays module).
**Apply to:** any new test file that imports `src.core.overlays` after `tests/test_slime.py` may have set up its own pyxel mock.
```python
_pyxel_mock = MagicMock()
sys.modules["pyxel"] = _pyxel_mock
for mod_key in list(sys.modules):
    if mod_key.startswith("src.core.overlays"):
        del sys.modules[mod_key]
import src.core.overlays as overlays
```

### Tuning-reset fixture for live-reload tests
**Source:** `tests/test_tuning_migration.py:30-34`
**Apply to:** every Phase 34 test that mutates `tuning.X` (e.g. via `tuning.set_value` for livereach tests).
```python
@pytest.fixture(autouse=True)
def _tuning_reset():
    """Restore baseline after each test (mirrors test_tuning_livereach.py:51-56)."""
    yield
    tuning.reset()
```

### Named constants over magic numbers (project memory)
**Source:** project memory `feedback_magic_numbers.md`
**Apply to:** every numeric literal in slime.py / overlays.py / new tests.
- Panel-tunable numerics → schema (D-05 promotion path: `slime_follow.SLIME_X`)
- Visual-only numerics → named module-level constants (e.g. existing `RECALL_TRAIL_MAX_LENGTH = 6` at slime.py L74; new `_LOOKAHEAD_COLOR`, `_MODE_GLYPH_FLOAT_COLOR`, `_MODE_GLYPH_GROUND_COLOR` in overlays.py constants block at L82-98)

---

## No Analog Found

No files in this phase lack an in-tree analog. Every modification site has a strong existing pattern to copy from (this is the benefit of "feel pass" being a tuning + small-extension phase rather than a new-system phase).

---

## Metadata

**Analog search scope:**
- `src/entities/slime.py` (full read — 294 lines)
- `src/core/overlays.py` (targeted reads — L75-105, L420-491)
- `src/ui/panel.py` (targeted read — L80-130)
- `src/ui/presets.py` (L1-40)
- `assets/physics-schema.json` (full read — 188 lines)
- `tests/test_slime.py` (full read — 117 lines)
- `tests/test_tuning_migration.py` (L1-60)
- `tests/test_overlays.py` (L1-60)
- `main.py` (targeted reads — L875, L905-922)
- `assets/output/simplified/Gym_AccelRunway/data.json` (L1-20 — minimal level header analog)
- `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md` (full read — 119 lines)
- `.planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md` (L1-50)
- `.planning/phases/34-slime-follow-ai-feel-pass/34-FEEL-TARGETS.md` (L1-30 — already drafted)

**Files scanned:** 13
**Pattern extraction date:** 2026-05-02
