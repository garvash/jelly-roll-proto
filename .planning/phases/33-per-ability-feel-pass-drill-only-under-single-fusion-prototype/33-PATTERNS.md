# Phase 33: Per-Ability Feel Pass (Drill-Only) — Pattern Map

**Mapped:** 2026-04-28
**Files analyzed:** 14 (9 modified + 5 new)
**Analogs found:** 14 / 14 (every file has at least one direct in-repo analog)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/core/audio.py` (NEW) | core module | event-driven (subscriber-fired) | `src/core/debug.py` (module-level globals + `update()`); `src/core/overlays.py` (named-constant block + module-level state) | role-match (no audio precedent in repo) |
| `src/fusion/drill_dive.py` (MOD) | fusion ability | per-frame transform (request-response via TickResult) | `src/fusion/pogo.py:130-218` (`_touching_enemy` + `_damage_touched_enemy`) | exact (sibling FusionAbility, mirrored AABB scan) |
| `src/fusion/charge_controller.py` (MOD) | fusion controller | per-frame state machine | `src/fusion/drill_dive.py:117-119` (use-site `tuning.X` reads); existing module-constant pattern at `:33-34` | exact (same module class) |
| `src/fusion/pogo.py` (MOD) | fusion ability | per-frame transform | `src/fusion/drill_dive.py:117-122` (use-site `tuning.X` reads replacing module constants) | exact (sibling refactor) |
| `src/entities/player.py:197` (MOD) | input handler | request-response (input → projectile spawn) | `src/entities/player.py:197-266` (existing spit branch — adding fused-branch in same handler) | exact (same code path with new branch) |
| `src/anim/event_bus.py` (no code MOD; new event names emitted only) | pub-sub primitive | event-driven | `src/anim/event_bus.py` itself (subscribe/emit primitives unchanged) | N/A (event bus is registry-free; just new emit/subscribe call sites) |
| `main.py:Game.__init__` (MOD ~line 320) | subscriber wiring | event-driven (subscribe → side effect) | `main.py:282-348` (`_on_drill_block_break`, `_on_fuse_charging`, `_on_land`, `_on_jump_start`) | exact |
| `main.py:spawn_particle_burst` (MOD line 941) | dispatch table | data-lookup transform | `main.py:155-180` (existing `PARTICLE_*_U/V` constant block + `SPRITE_MANIFEST` dict literal) | role-match |
| `assets/physics-schema.json` (MOD) | schema/config | static data (loaded once) | `assets/physics-schema.json:77-83` (`drill` group), `:94-101` (`fusion` group), `:66-71` (`slime_juice` group) | exact (extending existing groups) |
| `src/ui/panel.py` TAB_DEFS (MOD if new groups) | UI config | static data | `src/ui/panel.py:74-98` (`FEEL_GROUPS` set + `TAB_DEFS` list) | exact |
| `assets/sprites/particles.png` (MOD) | asset | binary sprite atlas | bank 2 layout doc'd at `main.py:158-180` (existing burst, converge, blob-growth cells) | exact |
| `assets/presets/slot_1.json` (MOD) | preset/config | static data | `assets/presets/slot_1.json:7-40` (existing `values` map keyed by flat tuning keys) | exact |
| `src/core/debug.py` (MOD) | debug utility | input-driven (key combo → flag set) | `src/core/debug.py:17-27` (existing `Ctrl+T` one-shot teleport_requested flag) | exact |
| `tests/test_destructive_drill.py` (NEW) | test | unit (mock pyxel + MockLevelMap + MagicMock slime) | `tests/test_drill_dive_parity.py:1-150` + `tests/test_pogo.py:1-100` | exact |
| `tests/test_daze_shot.py` (NEW) | test | unit (Player.handle_input with input_manager patches) | `tests/test_event_bus.py:118-130` (`patch.object(input_manager, ...)`) + `tests/test_drill_dive_parity.py:99-107` (`_stub_input_manager`) | exact |
| `tests/test_audio.py` (NEW) | test | unit (pyxel mock surface verification) | `tests/test_drill_dive_parity.py:22-46` (mock-pyxel preamble) + `tests/test_event_bus.py` (subscribe-then-emit pattern) | role-match (no audio test precedent) |
| `tests/test_tuning_migration.py` (NEW) | test | unit (`tuning.X` attribute readability) | `tests/test_tuning_livereach.py:1-90` (autouse `tuning.reset()`, `tuning.set_value` round-trip) | exact |
| `33-FEEL-TARGETS.md` (NEW doc) | sign-off doc | static data (markdown table) | `.planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md` | exact |

---

## Pattern Assignments

### `src/fusion/drill_dive.py` (MOD — fusion ability, per-frame transform)

**Analog:** `src/fusion/pogo.py:168-217` (the `_touching_enemy` and `_damage_touched_enemy` helper pair) **AND** `src/fusion/drill_dive.py:94-183` (the `on_tick` order-of-operations skeleton being extended).

**Why this analog:** Pogo already implements an enemy-AABB scan that hits exactly the same data shape (`player.game.enemies`, `enemy.is_alive`, `enemy.x/y/w/h`, `enemy.take_damage` fallback). Phase 33 D-03's destructive-drill is the same scan with two deltas: (1) iterate ALL intersecting enemies in one pass instead of returning on first hit, (2) call `slime.consume(tuning.DRILL_ENEMY_COST)` and `event_bus.emit("drill_enemy_hit", ...)` per hit, (3) DO NOT return a TickResult with `request_exit=True` — drill continues.

**Imports pattern** (already present at `drill_dive.py:22-25`, no change):
```python
import src.core.input as input_manager
from src.anim import event_bus
from src.core import tuning
from src.fusion.protocol import TickResult
```

**Enemy AABB scan to mirror — copy from `pogo.py:168-217`:**
```python
def _touching_enemy(self, player) -> bool:
    if not player.game:
        return False
    enemies = getattr(player.game, "enemies", None)
    if not enemies:
        return False
    for enemy in enemies:
        if not getattr(enemy, "is_alive", True):
            continue
        ew = getattr(enemy, "w", 0)
        eh = getattr(enemy, "h", 0)
        if (
            player.x < enemy.x + ew
            and player.x + player.w > enemy.x
            and player.y < enemy.y + eh
            and player.y + player.h > enemy.y
        ):
            return True
    return False
```

**Concrete code excerpt the executor must produce — destructive-drill helper** (mirrors pogo.py:194-217 with continue-through, juice consume, and event emit per hit):
```python
def _scan_and_damage_enemies(self, player, slime) -> None:
    """Phase 33 D-03/D-04/D-05: destructive-drill enemy AABB scan.

    Iterates ALL intersecting enemies in a single frame (vs. pogo's
    return-on-first-hit). Each hit deals DRILL_DAMAGE, drains
    DRILL_ENEMY_COST juice, and emits drill_enemy_hit. Drill continues
    regardless (no request_exit; mana-shield path irrelevant during DIVING).
    """
    if not player.game:
        return
    enemies = getattr(player.game, "enemies", None)
    if not enemies:
        return
    for enemy in enemies:
        if not getattr(enemy, "is_alive", True):
            continue
        ew = getattr(enemy, "w", 0)
        eh = getattr(enemy, "h", 0)
        if (
            player.x < enemy.x + ew
            and player.x + player.w > enemy.x
            and player.y < enemy.y + eh
            and player.y + player.h > enemy.y
        ):
            if hasattr(enemy, "take_damage"):
                enemy.take_damage(DRILL_DAMAGE)
            else:
                enemy.hp = getattr(enemy, "hp", 0) - DRILL_DAMAGE
            slime.consume(tuning.DRILL_ENEMY_COST)
            event_bus.emit(
                "drill_enemy_hit",
                x=enemy.x + ew // 2,
                y=enemy.y + eh // 2,
            )
```

**Insertion site within `on_tick`** (between step 3 block-break and step 4 solid-landing per Research § Pattern 1 ordering rule "tile-first preserves Phase 32 v1.3 parity"):
```python
# in on_tick, AFTER the "if tile_coord:" block at lines 138-168 (which returns
# TickResult on a tile break) and BEFORE the solid-landing block at lines 170-180:

# *** PHASE 33 D-03: enemy-AABB scan (continue-through; no exit) ***
self._scan_and_damage_enemies(player, slime)
```

**Module-level constant to add at top** (next to `EXPLOSION_SIZE_PX` at line 33):
```python
# Phase 33 D-04: drill damage per enemy AABB intersection per frame.
# Hardcoded gameplay constant per CONTEXT recommendation; same value as
# POGO_DAMAGE so the two abilities differ structurally (drill chains via
# repeated frames) not numerically.
DRILL_DAMAGE = 1
```

**Differs from analog because:** Pogo returns `TickResult(..., request_exit=True, exit_reason="bounced")` on first enemy hit (one-shot). Drill must (a) iterate all intersecting enemies in one frame, (b) NOT return early or set `request_exit`, and (c) emit `drill_enemy_hit` with `x=`/`y=` kwargs (the canonical particle-position payload — Phase 31 subscribers consume `x=` `y=` per `main.py:282-304`).

---

### `src/fusion/charge_controller.py` (MOD — tuning migration)

**Analog:** `src/fusion/drill_dive.py:89-91, 117-122, 155-157` (use-site `tuning.X` reads).

**Why this analog:** drill_dive.py uses `tuning.DRILL_SPEED`, `tuning.DRILL_DRIFT_SPEED`, `tuning.DRILL_ACTIVATION_COST`, `tuning.DRILL_CRACKED_V_COST`, `tuning.TILE_SIZE` — all read at use-site (Phase 25 pattern). The two charge_controller.py module constants (`ACCELERATED_REGEN_RATE`, `WINDUP_DURATION_FRAMES`) need the same treatment.

**Use-site read pattern (verified at `drill_dive.py:89-91`):**
```python
player.dy = tuning.DRILL_SPEED
player.dx = 0
slime.consume(tuning.DRILL_ACTIVATION_COST)
```

**Concrete code excerpt — BEFORE → AFTER for charge_controller.py:**
```python
# BEFORE (charge_controller.py:33-34):
ACCELERATED_REGEN_RATE = 1.0       # juice/frame; FUSION-DESIGN draft 2x passive
WINDUP_DURATION_FRAMES = 30        # ~0.5s @60fps; FUSION-DESIGN D-23c base target

# AFTER step 1 — delete lines 33-34 from charge_controller.py.
# AFTER step 2 — replace use sites:

# Line 94 (was: slime.refill(ACCELERATED_REGEN_RATE)):
slime.refill(tuning.ACCELERATED_REGEN_RATE)

# Line 120 (was: self._windup_progress += 1.0 / WINDUP_DURATION_FRAMES):
self._windup_progress += 1.0 / tuning.WINDUP_DURATION_FRAMES
```

**Schema-side (assets/physics-schema.json) — add under existing `fusion` group:**
```json
"fusion": {
  "RECALL_SPEED": 4.0,
  "RECALL_OVERLAP_DIST": 4,
  "MANA_SHIELD_COST": 20.0,
  "SLIME_DISSIPATE_COOLDOWN": 240,
  "RECALL_TRAIL_COLOR": 11,
  "SPIT_HOLD_THRESHOLD": 16,
  "ACCELERATED_REGEN_RATE": 1.0,
  "WINDUP_DURATION_FRAMES": 30
}
```

**Differs from analog because:** drill_dive.py keeps `EXPLOSION_SIZE_PX = 9` and `INTGRID_CRACKED_V = 12` as module constants because they are gameplay-stable (no panel-tunable need). charge_controller.py migrates ONLY the two FUSION-DESIGN draft values (Phase 33 must validate via playtest); the state-string constants (`_STATE_IDLE`, `_STATE_RECALL`, `_STATE_WINDUP`) at lines 37-39 stay hardcoded.

---

### `src/fusion/pogo.py` (MOD — tuning migration; behavior unchanged)

**Analog:** Same as charge_controller.py — use-site `tuning.X` reads at `drill_dive.py:89-91`.

**Concrete code excerpt — BEFORE → AFTER for pogo.py:**
```python
# BEFORE (pogo.py:30-32):
POGO_BOUNCE_VELOCITY = -2.5    # negative = upward bounce on enemy / breakable
POGO_COOLDOWN_FRAMES = 0       # D-20: free, no cooldown in v2.0 baseline

# AFTER step 1 — delete lines 30-32 (keep POGO_INITIAL_DY at line 28, POGO_DAMAGE at line 33).
# AFTER step 2 — replace use sites at lines 117, 135 (both `dy=POGO_BOUNCE_VELOCITY`):
return TickResult(
    dx=0.0,
    dy=tuning.POGO_BOUNCE_VELOCITY,   # was: POGO_BOUNCE_VELOCITY
    request_exit=True,
    exit_reason="bounced",
)
```

**Schema-side — add new `pogo` group OR extend `fusion` group (planner discretion per CONTEXT D-02):**
```json
"pogo": {
  "POGO_BOUNCE_VELOCITY": -2.5,
  "POGO_COOLDOWN_FRAMES": 0
}
```

**Add import** (pogo.py top — currently only imports TickResult from `src.fusion.protocol`):
```python
from src.core import tuning
```

**Differs from analog because:** Pogo keeps `POGO_INITIAL_DY = 2.0` AND `POGO_DAMAGE = 1` AND `EXPLOSION_SIZE_PX = 9` AND `INTGRID_CRACKED_V = 12` hardcoded per CONTEXT D-02 (POGO_INITIAL_DY must equal DRILL_SPEED for Mario-64 visual parity; POGO_DAMAGE is a gameplay constant). Only the two retunable feel-values migrate.

---

### `src/entities/player.py:197` (MOD — daze-shot fused-branch)

**Analog:** `src/entities/player.py:197-266` (the existing spit-fire branch IN THE SAME FILE — Phase 33 adds a fused-branch sibling at the same call site).

**Why this analog:** Per FUSION-DESIGN D-14 / Phase 33 D-17, daze REUSES the spit code path. The cleanest diff is to keep the auto-aim, projectile-spawn, and `self.game.projectiles.append` logic, and only branch on `self.is_fused` for cost + stun-flag.

**Imports pattern** (already present at `player.py:1-7`, no change):
```python
import pyxel
from src.core import tuning
from src.core.sprite_utils import draw_sprite
import src.core.input as input_manager
import src.core.debug as debug
from src.anim import event_bus
from src.anim.player_anim import PlayerAnimDriver, build_player_fsm
```

**Concrete code excerpt — BEFORE → AFTER at line 197:**
```python
# BEFORE (player.py:197):
if input_manager.was_tap("spit", tuning.SPIT_HOLD_THRESHOLD) and not self.is_fused and self.state != "DIVING":
    import math
    # ... spit-fire branch with auto-aim (lines 198-263) ...
    proj = slime.spit(target_dx, target_dy, self.level_map)
    if proj and self.game:
        self.game.projectiles.append(proj)

# AFTER (Phase 33 D-17): remove `not self.is_fused` gate, add fused-branch
# AFTER projectile creation. Auto-aim and target_dx/target_dy logic UNCHANGED.
if input_manager.was_tap("spit", tuning.SPIT_HOLD_THRESHOLD) and self.state != "DIVING":
    import math
    # ... [auto-aim block unchanged from lines 199-263] ...

    # Phase 33 D-17: fused branch consumes SLIME_DAZE_COST + flags projectile
    # for daze-on-hit. Unfused branch unchanged (slime.spit pays SLIME_SPIT_COST).
    if self.is_fused:
        if slime.juice < tuning.SLIME_DAZE_COST:
            return  # Pitfall 4: gate on juice to prevent cancel-spam drain
        slime.consume(tuning.SLIME_DAZE_COST)
        proj = slime.spit(target_dx, target_dy, self.level_map)
        if proj is not None:
            proj.applies_daze_stun = True   # Boss/enemy contact site reads this
        event_bus.emit("daze_fire")
    else:
        proj = slime.spit(target_dx, target_dy, self.level_map)

    if proj and self.game:
        self.game.projectiles.append(proj)
```

**Differs from analog because:** Two new behaviors layer on top of the unchanged spit code: (1) `slime.consume(tuning.SLIME_DAZE_COST)` BEFORE `slime.spit(...)` (which itself pays SLIME_SPIT_COST internally — note the executor must verify this double-cost is the intended D-17 semantics, OR pay the full daze cost only and skip slime.spit's internal cost path; recommendation: skip slime.spit entirely on fused-branch and construct Projectile directly to avoid the double-charge), (2) `proj.applies_daze_stun = True` flag for Projectile/boss/enemy contact-site reads. Pitfall 4 (RESEARCH) flags the cancel-spam risk — gating on `slime.juice >= tuning.SLIME_DAZE_COST` is mandatory.

---

### `src/anim/event_bus.py` (NO MOD — new event names emitted/subscribed only)

**Analog:** `src/anim/event_bus.py:1-25` itself. The bus is registry-free; new events `drill_enemy_hit` and `pogo_bounce` are introduced by `event_bus.emit("drill_enemy_hit", ...)` call sites and `event_bus.subscribe("drill_enemy_hit", ...)` call sites.

**No code change in event_bus.py.** Phase 33's contract: new emit sites are in `drill_dive.py:on_tick` and `player.py:handle_input` (daze_fire); new subscribe sites are in `main.py:Game.__init__`.

---

### `main.py:Game.__init__` ~line 320 (MOD — subscriber wiring)

**Analog:** `main.py:282-348` — the existing subscriber block for `drill_block_break` (particle burst at lines 282-306), `land` + `jump_start` (lines 308-318), and `fuse_charging` (lines 320-348). All four follow the Phase 31 Pitfall 5 hoist-to-`Game.__init__` pattern.

**Why this analog:** This is the canonical pattern for new event subscribers. Phase 33 adds (1) audio init call, (2) 7 audio subscribers (one per cue), (3) one particle subscriber for `drill_enemy_hit`. All slot in alongside the existing block.

**Imports pattern** (`main.py:276-280`, plus new audio import):
```python
import math as _math
from src.anim import event_bus as _event_bus
from src.anim.player_anim import DRILL_RECOIL_PAUSE_FRAMES
from src.entities.effects import Particle as _Particle
from src.core import tuning as _tuning
from src.core import audio as _audio   # Phase 33 D-12 NEW
```

**Init pattern (audio module setup) — Phase 33 D-12 add right after `_audio` import:**
```python
# Phase 33 D-12: audio module init. Defines pyxel sound slots 0-6.
_audio.init_sounds()
```

**Subscriber pattern excerpt — copy structure from `main.py:282-306`:**
```python
def _on_drill_block_break(tx=None, ty=None, **kw):
    """Phase 31 D-06 + D-16: drill recoil pause + diverging burst."""
    self.player._anim.pause_for(DRILL_RECOIL_PAUSE_FRAMES)
    cx = tx * _tuning.TILE_SIZE + 4
    cy = ty * _tuning.TILE_SIZE + 4
    for i in range(BURST_PARTICLE_COUNT):
        angle = (2 * _math.pi * i) / BURST_PARTICLE_COUNT
        self.particles.append(_Particle(
            cx, cy,
            dx=_math.cos(angle) * BURST_PARTICLE_SPEED,
            dy=_math.sin(angle) * BURST_PARTICLE_SPEED,
            life=BURST_PARTICLE_LIFE,
            bank_u=PARTICLE_BURST_U, bank_v=PARTICLE_BURST_V,
        ))

_event_bus.subscribe("drill_block_break", _on_drill_block_break)
```

**Concrete code excerpt the executor must produce — Phase 33 NEW subscribers (insert after the existing `_on_fuse_charging` subscribe at line 348):**
```python
# Phase 33 D-13/D-16: audio subscribers (7 cues — drill events, fuse_start,
# daze_fire, pogo_bounce). Audio is a side-channel like particles.
def _on_audio_fuse_start(**kw):        _audio.play_sfx("fuse_start")
def _on_audio_drill_start(**kw):       _audio.play_sfx("drill_start")
def _on_audio_drill_block_break(**kw): _audio.play_sfx("drill_block_break")
def _on_audio_drill_enemy_hit(**kw):   _audio.play_sfx("drill_enemy_hit")
def _on_audio_drill_impact(**kw):      _audio.play_sfx("drill_impact")
def _on_audio_daze_fire(**kw):         _audio.play_sfx("daze_fire")
def _on_audio_pogo_bounce(**kw):       _audio.play_sfx("pogo_bounce")
_event_bus.subscribe("fuse_start",        _on_audio_fuse_start)
_event_bus.subscribe("drill_start",       _on_audio_drill_start)
_event_bus.subscribe("drill_block_break", _on_audio_drill_block_break)
_event_bus.subscribe("drill_enemy_hit",   _on_audio_drill_enemy_hit)
_event_bus.subscribe("drill_impact",      _on_audio_drill_impact)
_event_bus.subscribe("daze_fire",         _on_audio_daze_fire)
_event_bus.subscribe("pogo_bounce",       _on_audio_pogo_bounce)

# Phase 33 D-14/D-16: drill_enemy_hit particle subscriber (combat-flavored
# burst at enemy contact point).
def _on_drill_enemy_hit(x=None, y=None, **kw):
    if x is None or y is None:
        return
    self.spawn_particle_burst(x, y, type="drill_enemy_hit")
_event_bus.subscribe("drill_enemy_hit", _on_drill_enemy_hit)
```

**Differs from analog because:** Existing `_on_drill_block_break` (line 282) computes its own (cx, cy) from `tx, ty` grid coords + TILE_SIZE multiplication. The new `_on_drill_enemy_hit` receives `x=`/`y=` as pixel coords (already enemy-center; see drill_dive.py emit kwargs above) so it just forwards to `self.spawn_particle_burst` without TILE_SIZE math. Audio subscribers receive no kwargs (event-fire is the cue; data is irrelevant). Pitfall 5 from Phase 31: ALL these subscribers MUST live in `Game.__init__` (runs once), not `Player.__init__` (runs every reset — would accumulate).

---

### `main.py:spawn_particle_burst` line 941 (MOD — dispatch table)

**Analog:** `main.py:155-180` — the existing `PARTICLE_*_U/V` constant block plus the `SPRITE_MANIFEST` dict literal at line 155. The dispatch-table shape follows the same convention.

**Concrete code excerpt — BEFORE → AFTER:**
```python
# BEFORE (main.py:941-961):
def spawn_particle_burst(self, x, y, type="block_break"):
    """Phase 31 D-16: diverging particle burst at tile (x, y)."""
    import math
    cx, cy = x + 4, y + 4
    # type argument reserved for future variants; all variants use same offsets.
    u, v = PARTICLE_BURST_U, PARTICLE_BURST_V
    for i in range(BURST_PARTICLE_COUNT):
        angle = (2 * math.pi * i) / BURST_PARTICLE_COUNT
        self.particles.append(Particle(
            cx, cy,
            dx=math.cos(angle) * BURST_PARTICLE_SPEED,
            dy=math.sin(angle) * BURST_PARTICLE_SPEED,
            life=BURST_PARTICLE_LIFE,
            bank_u=u, bank_v=v,
        ))

# AFTER (Phase 33 D-14):
# Step 1 — add named (u, v) constants at the existing constant block ~line 162
# (next to PARTICLE_BURST_U/V):

# Phase 33 D-14/D-15: new bank-2 cells for particle differentiation.
# Drill claims earthbound palette (pyxel colors 4/9/10) per D-15.
# Layout per Pitfall 3 — extend particles.png to y=32 row.
PARTICLE_DRILL_BREAK_U = 0      # bank 2 x offset for drill block-break (orange/brown shrapnel)
PARTICLE_DRILL_BREAK_V = 32     # bank 2 y offset (NEW row — Pitfall 3 expansion)
PARTICLE_DRILL_HIT_U = 16       # bank 2 x offset for drill enemy-hit (combat-flavored)
PARTICLE_DRILL_HIT_V = 32
PARTICLE_DAZE_U = 32            # bank 2 x offset for daze splat (blue/green per D-15)
PARTICLE_DAZE_V = 32

# Step 2 — add module-level dispatch table next to the constants:
PARTICLE_TYPE_TABLE = {
    "block_break":      (PARTICLE_BURST_U,        PARTICLE_BURST_V),       # legacy default
    "drill_block_break": (PARTICLE_DRILL_BREAK_U, PARTICLE_DRILL_BREAK_V),
    "drill_enemy_hit":   (PARTICLE_DRILL_HIT_U,   PARTICLE_DRILL_HIT_V),
    "daze_splat":        (PARTICLE_DAZE_U,        PARTICLE_DAZE_V),
}

# Step 3 — replace the inline u, v assignment in spawn_particle_burst:
def spawn_particle_burst(self, x, y, type="block_break"):
    """Phase 31 D-16 + Phase 33 D-14: type-keyed bank 2 dispatch."""
    import math
    cx, cy = x + 4, y + 4
    u, v = PARTICLE_TYPE_TABLE.get(type, (PARTICLE_BURST_U, PARTICLE_BURST_V))
    for i in range(BURST_PARTICLE_COUNT):
        angle = (2 * math.pi * i) / BURST_PARTICLE_COUNT
        self.particles.append(Particle(
            cx, cy,
            dx=math.cos(angle) * BURST_PARTICLE_SPEED,
            dy=math.sin(angle) * BURST_PARTICLE_SPEED,
            life=BURST_PARTICLE_LIFE,
            bank_u=u, bank_v=v,
        ))
```

**Differs from analog because:** No prior dispatch table existed; this is a new pattern but mirrors `SPRITE_MANIFEST` (a dict keyed by string-name → sprite metadata tuple at `main.py:155`). The `type` arg was reserved at line 950 (currently a no-op comment); Phase 33 makes it load-bearing. Default fallback to `(PARTICLE_BURST_U, PARTICLE_BURST_V)` keeps `spawn_explosion` legacy callers (line 970) working without changes.

---

### `src/core/audio.py` (NEW — pyxel sound module)

**Analog:** `src/core/debug.py:1-27` (module-level globals + `update()` function pattern) AND `src/core/overlays.py:1-40` (named-constant block + module-level state). Both are simple, single-responsibility core modules.

**Why this analog:** No prior audio code exists in the project. The closest structural match is debug.py (module-level constants and functions, no class) — audio.py needs (1) named slot constants, (2) a name→slot map, (3) `init_sounds()` and `play_sfx()` functions, all module-level.

**Imports pattern** (mirror debug.py:1-7 and overlays.py:1-19):
```python
"""Phase 33 D-12 minimal audio surface.

Defines `pyxel.sounds[N].set()` for the 7 Phase 33 SFX cues + a `play_sfx(name)`
wrapper. Phase 35 inherits and extends with a full sound channel map +
debounce; Phase 33's surface stays bounded.

Channel strategy: `pyxel.play(-1, sound_id)` for auto-channel pickup. The
`-1` sentinel is the Pyxel idiom for "any free channel" — verify in the
pinned Pyxel version before locking. Round-robin 0..3 fallback if `-1`
is unsupported.
"""
import pyxel
```

**Constant block pattern** (mirror `overlays.py:31-40` palette constants):
```python
# --- Sound slot IDs (no magic numbers per project memory) -------------------
# Phase 33 uses 7 slots out of pyxel's 64-slot budget (slots 0-63).
SFX_FUSE_START         = 0
SFX_DRILL_START        = 1
SFX_DRILL_BLOCK_BREAK  = 2
SFX_DRILL_ENEMY_HIT    = 3   # Phase 33 D-13 NEW
SFX_DRILL_IMPACT       = 4
SFX_DAZE_FIRE          = 5   # Phase 33 D-13 + D-17
SFX_POGO_BOUNCE        = 6   # Phase 33 D-20

_NAME_TO_SLOT: dict[str, int] = {
    "fuse_start":         SFX_FUSE_START,
    "drill_start":        SFX_DRILL_START,
    "drill_block_break":  SFX_DRILL_BLOCK_BREAK,
    "drill_enemy_hit":    SFX_DRILL_ENEMY_HIT,
    "drill_impact":       SFX_DRILL_IMPACT,
    "daze_fire":          SFX_DAZE_FIRE,
    "pogo_bounce":        SFX_POGO_BOUNCE,
}

# Auto-channel sentinel per Pyxel API (verify in pinned version).
_AUTO_CHANNEL = -1
```

**Function pattern** (mirror debug.py:16-27 module-level `update()`):
```python
def init_sounds() -> None:
    """Define all SFX. Called once from Game.__init__.

    Per Pyxel API (verified github.com/kitao/pyxel/blob/main/python/pyxel/examples/04_sound_api.py):
        pyxel.sounds[N].set(notes, tones, volumes, effects, speed)
        notes:   [CDEFGAB] + [#-] + [0-4] for pitch, R for rest. Lowercase.
        tones:   [TSPN] (Triangle, Square, Pulse, Noise). Lowercase. Single
                 char repeats; longer string is per-note.
        volumes: [0-7]. Single char repeats; longer string is per-note.
        effects: [NSVF] (None, Slide, Vibrato, FadeOut). Lowercase. Per-note.
        speed:   integer; lower = faster.
    """
    # Specific note/tone/volume/effect/speed strings are feel choices made
    # during implementation per CONTEXT § Claude's Discretion. Sketch:
    pyxel.sounds[SFX_FUSE_START].set("c2e2g2", "p", "6", "n", 25)
    pyxel.sounds[SFX_DRILL_START].set("e1c1", "n", "5", "f", 20)
    pyxel.sounds[SFX_DRILL_BLOCK_BREAK].set("c2", "n", "6", "f", 10)
    pyxel.sounds[SFX_DRILL_ENEMY_HIT].set("g2c2", "p", "6", "f", 12)
    pyxel.sounds[SFX_DRILL_IMPACT].set("c1g0", "n", "7", "f", 15)
    pyxel.sounds[SFX_DAZE_FIRE].set("e2g2", "s", "5", "n", 18)
    pyxel.sounds[SFX_POGO_BOUNCE].set("g2c3", "s", "5", "n", 8)


def play_sfx(name: str) -> None:
    """Phase 33 D-12: thin wrapper. Phase 35 will replace channel strategy.

    Returns silently on unknown name (event-bus subscribers can fire any cue
    name; we do not raise on typos to avoid crashing the game on a
    subscriber bug).
    """
    slot = _NAME_TO_SLOT.get(name)
    if slot is None:
        return
    pyxel.play(_AUTO_CHANNEL, slot)
```

**Differs from analog because:** `debug.py` has no I/O surface beyond reading pyxel input; `audio.py` calls `pyxel.sounds[N].set()` and `pyxel.play(...)` (output side). The MagicMock'd `pyxel` in test fixtures (`tests/conftest.py:16`) MUST tolerate `pyxel.sounds[N].set(...)` — Open Question 4 in RESEARCH flags this; verify by writing test_audio.py first and adding `mock_pyxel.sounds = [MagicMock() for _ in range(64)]` to conftest.py if `pyxel.sounds[0].set(...)` raises.

---

### `assets/physics-schema.json` (MOD — schema entries)

**Analog:** `assets/physics-schema.json:77-83` (`drill` group), `:94-101` (`fusion` group), `:66-71` (`slime_juice` group).

**Concrete code excerpt — additions per D-01/D-02/D-05/D-17:**
```json
{
  "tuning": {
    "...": "...",
    "slime_juice": {
      "JUICE_MAX": 200.0,
      "JUICE_REGEN_RATE": 0.5,
      "JUICE_MIN_SCALE": 0.25,
      "SLIME_SPIT_COST": 10.0,
      "SLIME_DAZE_COST": 20.0
    },
    "drill": {
      "DRILL_SPEED": 2.0,
      "DRILL_DRIFT_SPEED": 0.5,
      "DRILL_IMPACT_COST": 20.0,
      "DRILL_ACTIVATION_COST": 5.0,
      "DRILL_BLOCK_REFUND": 15.0,
      "DRILL_ENEMY_COST": 15.0
    },
    "fusion": {
      "RECALL_SPEED": 4.0,
      "RECALL_OVERLAP_DIST": 4,
      "MANA_SHIELD_COST": 20.0,
      "SLIME_DISSIPATE_COOLDOWN": 240,
      "RECALL_TRAIL_COLOR": 11,
      "SPIT_HOLD_THRESHOLD": 16,
      "ACCELERATED_REGEN_RATE": 1.0,
      "WINDUP_DURATION_FRAMES": 30
    },
    "pogo": {
      "POGO_BOUNCE_VELOCITY": -2.5,
      "POGO_COOLDOWN_FRAMES": 0
    }
  }
}
```

**Differs from analog because:** New `pogo` group is the first group added in v0.3.0 since Phase 31.5 cut abilities. Phase 33 panel needs `FEEL_GROUPS` extension (Pitfall 6). Existing `gates` group at line 102 already houses `DRILL_CRACKED_V_COST = 20.0` — Phase 33 keeps `DRILL_ENEMY_COST` in `drill` (per RESEARCH § Open Question 2 recommendation).

---

### `src/ui/panel.py` TAB_DEFS (MOD if new groups added)

**Analog:** `src/ui/panel.py:74-98` (`FEEL_GROUPS` set + `TAB_DEFS` list).

**Concrete code excerpt — extension if planner picks new `pogo` group:**
```python
# BEFORE (panel.py:74-78):
FEEL_GROUPS = {
    "movement", "forgiving", "wall",
    "slime_follow", "slime_juice", "projectile",
    "drill", "fusion",
}

# AFTER (Phase 33 D-02 — only if new "pogo" group is added):
FEEL_GROUPS = {
    "movement", "forgiving", "wall",
    "slime_follow", "slime_juice", "projectile",
    "drill", "fusion", "pogo",   # NEW per D-02
}

# AFTER (Phase 33 — TAB_DEFS extension; absorb pogo into "Fuse" tab OR add
# new "Pogo" tab per Pitfall 7 viewport-overflow check):
TAB_DEFS = [
    ("Move",  {"movement": lambda k: k not in JUMP_TAB_MOVEMENT_KEYS}),
    ("Jump",  {"movement": lambda k: k in JUMP_TAB_MOVEMENT_KEYS, "forgiving": None, "wall": None}),
    ("Slime", {"slime_follow": None, "slime_juice": None, "projectile": None}),
    ("Fuse",  {"drill": None, "fusion": None, "pogo": None}),  # extended
    ("Anim",  {_ANIM_TAB_SENTINEL: None}),
]
```

**Differs from analog because:** Pitfall 6 (panel won't surface keys without FEEL_GROUPS edit) AND Pitfall 7 (viewport overflow on a single tab with 11+ sliders). If pogo stays inside an existing group (`fusion` extension) instead of becoming its own group, only TAB_DEFS auto-includes new keys — no FEEL_GROUPS edit. New keys added to existing groups (`SLIME_DAZE_COST` to `slime_juice`, `WINDUP_DURATION_FRAMES`/`ACCELERATED_REGEN_RATE` to `fusion`, `DRILL_ENEMY_COST` to `drill`) need NO panel.py edits — they auto-appear via `tuning._flat_index`.

---

### `assets/sprites/particles.png` (MOD — bank 2 expansion)

**Analog:** `main.py:158-180` (existing PARTICLE constant block documenting bank 2 layout). Current PNG is 64×32 (verified via `file` command).

**Layout extension per Pitfall 3:** Expand PNG to 64×48 (or 64×64) by adding a y=32 row. Existing layout uses (0,0), (16,0), and the entire y=16 row for blob frames; new y=32 row is empty and safe.

**New cells (planner picks final coordinates within the new row):**
- (0, 32) — drill block-break (orange/brown shrapnel; pyxel color 4 brown + 9 orange)
- (16, 32) — drill enemy-hit (combat-flavored; pyxel color 9 orange + 10 yellow)
- (32, 32) — daze splat (blue/green to differentiate from spit)

**Differs from analog because:** Phase 31 only used y=0 and y=16 rows; Phase 33 is the first to extend the PNG vertically. Verify PNG dimensions stay within Pyxel image bank 2 capacity (256×256 max) — 64×48 is well within budget.

---

### `assets/presets/slot_1.json` (MOD — preset bake)

**Analog:** `assets/presets/slot_1.json:7-40` — existing `values` dict keyed by flat tuning keys.

**Concrete code excerpt — additions:**
```json
{
  "version": "1.0",
  "schema_version": "0.3.0",
  "slot": 1,
  "alias": "v2.0-default",
  "timestamp": "2026-04-28T...",
  "values": {
    "...": "...",
    "DRILL_ENEMY_COST": 15.0,
    "WINDUP_DURATION_FRAMES": 30,
    "ACCELERATED_REGEN_RATE": 1.0,
    "POGO_BOUNCE_VELOCITY": -2.5,
    "POGO_COOLDOWN_FRAMES": 0,
    "SLIME_DAZE_COST": 20.0
  }
}
```

**Differs from analog because:** Phase 33 final values are determined via panel-iteration playtest before bake — the values shown above are the seed values from CONTEXT D-01/D-02 starting points. The bake happens at end-of-phase per D-11, after FEEL-TARGETS sign-off.

---

### `src/core/debug.py` (MOD — debug-warp extension)

**Analog:** `src/core/debug.py:13-27` (existing `Ctrl+T` one-shot teleport flag) + the consume site at `main.py:572-586`.

**Concrete code excerpt — BEFORE → AFTER for debug.py:**
```python
# BEFORE (debug.py:1-27):
"""Runtime god-mode toggles for debug playtesting (D-08, D-09, D-10)."""
import pyxel

god_abilities = False
god_invincible = False
god_infinite_juice = False
teleport_requested = False

def update():
    global god_abilities, god_invincible, god_infinite_juice, teleport_requested
    if pyxel.btn(pyxel.KEY_CTRL):
        if pyxel.btnp(pyxel.KEY_1):
            god_abilities = not god_abilities
        if pyxel.btnp(pyxel.KEY_2):
            god_invincible = not god_invincible
        if pyxel.btnp(pyxel.KEY_3):
            god_infinite_juice = not god_infinite_juice
        if pyxel.btnp(pyxel.KEY_T):
            teleport_requested = True

# AFTER (Phase 33 D-09): add multi-target warp string flag.
"""Runtime god-mode toggles + Phase 29/33 debug warp targets."""
import pyxel

god_abilities = False
god_invincible = False
god_infinite_juice = False

# Phase 29: one-shot teleport flag for the Gym room (Ctrl+T).
teleport_requested = False

# Phase 33 D-09: drill-relevant warp targets. Set to a level-id string when
# a warp key is pressed; consumed by main.py:Game.update and reset to None.
# NOTE: Ctrl+1/2/3 are taken by god-mode toggles; Phase 33 uses Ctrl+4..7.
warp_target: str | None = None

# Level-id constants per CONTEXT D-09 coverage. Final IDs are level-name
# discretion — pick from existing Level_0..Level_8 rooms.
WARP_LEVEL_CRACKED_V = "Level_CrackedV_Column"     # planner picks actual level id
WARP_LEVEL_SOFT_BLOCK = "Level_SoftBlock_Floor"
WARP_LEVEL_ENEMY_CLUSTER = "Level_Enemy_Cluster"
WARP_LEVEL_JUICE_DRAIN = "Level_Juice_Drain"

def update():
    global god_abilities, god_invincible, god_infinite_juice
    global teleport_requested, warp_target
    if pyxel.btn(pyxel.KEY_CTRL):
        if pyxel.btnp(pyxel.KEY_1):
            god_abilities = not god_abilities
        if pyxel.btnp(pyxel.KEY_2):
            god_invincible = not god_invincible
        if pyxel.btnp(pyxel.KEY_3):
            god_infinite_juice = not god_infinite_juice
        if pyxel.btnp(pyxel.KEY_T):
            teleport_requested = True
        # Phase 33 D-09 — drill-relevant warps:
        if pyxel.btnp(pyxel.KEY_4):
            warp_target = WARP_LEVEL_CRACKED_V
        if pyxel.btnp(pyxel.KEY_5):
            warp_target = WARP_LEVEL_SOFT_BLOCK
        if pyxel.btnp(pyxel.KEY_6):
            warp_target = WARP_LEVEL_ENEMY_CLUSTER
        if pyxel.btnp(pyxel.KEY_7):
            warp_target = WARP_LEVEL_JUICE_DRAIN
```

**Consumer site at `main.py:572-586` — extend the existing teleport_requested block:**
```python
# Phase 33: handle multi-target warp BEFORE the existing teleport_requested
# block (or merge them — either works).
if debug.warp_target:
    target_id = debug.warp_target
    debug.warp_target = None
    for level in self.world.levels:
        if level.id == target_id:
            # Reposition player + camera (mirrors line 575-586 pattern).
            self.player.x = level.x + 32
            self.player.y = level.y + 32
            self.player.dy = 0
            self.player.dx = 0
            self.world.current_level = level
            self.cam_x = level.x
            self.cam_y = level.y
            break
```

**Differs from analog because:** Existing `teleport_requested` is a single boolean → single hardcoded level ID (`Level_Gym_R2C2`). Phase 33 generalizes to a string-typed `warp_target` with per-key constant level IDs. Ctrl+1/2/3 are claimed by god-mode toggles; Ctrl+T is claimed by gym warp; Ctrl+4..7 is the Phase 33 budget. Pitfall: the level IDs (`Level_CrackedV_Column`, etc.) are placeholders — the planner verifies against actual Level_0..Level_8 IDs in the LDtk world before locking.

---

### `tests/test_destructive_drill.py` (NEW)

**Analog:** `tests/test_drill_dive_parity.py:1-150` (mock-pyxel preamble, MockLevelMap, `make_player_and_slime` helper, `_stub_input_manager` helper) + `tests/test_pogo.py:1-100` (Pogo activation/contact tests).

**Imports + mock-pyxel preamble** (verbatim from `test_drill_dive_parity.py:19-46`):
```python
import sys
import types

# Mock pyxel before any game imports.
if "pyxel" not in sys.modules:
    mock_pyxel = types.ModuleType("pyxel")
    mock_pyxel.KEY_LEFT = 0
    mock_pyxel.KEY_RIGHT = 1
    # ... etc, full key + btn/btnp/btnr/blt/rect/pset stubs ...
    sys.modules["pyxel"] = mock_pyxel

import pytest
from unittest.mock import MagicMock
from src.anim import event_bus
from src.core import tuning
```

**Test fixtures** (mirror `test_drill_dive_parity.py:67-107`):
```python
class MockLevelMap:
    def __init__(self):
        self._destructibles = {}
        self._collisions = {}
    def check_collision(self, x, y, w, h):
        return False
    def check_hazard(self, x, y, w, h):
        return False
    def get_destructible_at(self, x, y, w, h):
        return None


def make_player_and_slime(px=50, py=50, sx=100, sy=50):
    from src.entities.player import Player
    from src.entities.slime import Slime
    level_map = MockLevelMap()
    player = Player(px, py, level_map)
    slime = Slime(sx, sy)
    return player, slime, level_map


def _stub_input_manager(left=False, right=False, down=False, jump=False):
    im = MagicMock()
    btn_map = {"left": left, "right": right, "down": down, "jump": jump,
               "spit": False, "up": False}
    im.btn = lambda name: btn_map.get(name, False)
    im.btnp = lambda name: False
    im.btnr = lambda name: False
    im.was_tap = lambda name: False
    im.hold_frames = lambda name: 0
    return im
```

**Test pattern — destructive-drill core rule** (mirror Pogo enemy-contact tests):
```python
def test_drill_hits_enemy_and_continues():
    """Phase 33 FUS-06: drill on_tick deals DRILL_DAMAGE to intersecting
    enemy, drains DRILL_ENEMY_COST juice, emits drill_enemy_hit, continues
    drilling (no request_exit, no state change).
    """
    from src.fusion.drill_dive import DrillDive, DRILL_DAMAGE
    captured = []
    event_bus.subscribe("drill_enemy_hit", lambda **kw: captured.append(kw))

    player, slime, level_map = make_player_and_slime(px=50, py=50)
    enemy = MagicMock()
    enemy.x = 50
    enemy.y = 50
    enemy.w = 16
    enemy.h = 16
    enemy.hp = 1
    enemy.is_alive = True
    player.game = MagicMock()
    player.game.enemies = [enemy]
    slime.juice = 200.0  # plenty for the cost drain

    drill = DrillDive()
    result = drill.on_tick(player, slime, dt=1.0)

    enemy.take_damage.assert_called_once_with(DRILL_DAMAGE)
    assert slime.juice == 200.0 - tuning.DRILL_ENEMY_COST
    assert len(captured) == 1
    assert result.request_exit is False  # CONTINUES — no exit
```

**Differs from analog because:** test_drill_dive_parity.py covers v1.3 parity (block-break, impact, refund); test_destructive_drill.py covers ONLY the new Phase 33 enemy-AABB rule (4 cases per RESEARCH § Validation table: single hit, multi-enemy chain, no-exit, juice-empty Exit-b). Reuses the same fixtures + mock-pyxel preamble verbatim.

---

### `tests/test_daze_shot.py` (NEW)

**Analog:** `tests/test_event_bus.py:118-130` (`patch.object(input_manager, "btn"/"btnp"/"btnr"/"was_tap"/"hold_frames", ...)`) + the `_btn_map` / `_btnp_map` / `_btnr_map` helpers at lines 87-115.

**Test pattern — daze fused-branch fires:**
```python
import pytest
from unittest.mock import MagicMock, patch
from src.anim import event_bus
import src.core.input as input_manager
from src.core import tuning


def _btn_map(**overrides):
    mapping = {"left": False, "right": False, "up": False, "down": False,
               "jump": False, "spit": False}
    mapping.update(overrides)
    return lambda name: mapping.get(name, False)


def test_fused_tap_fires_daze(mock_level, mock_slime, make_game_with_fusion):
    """Phase 33 FUS-06: fused Z-tap fires projectile + consumes
    SLIME_DAZE_COST + emits daze_fire event."""
    captured = []
    event_bus.subscribe("daze_fire", lambda **kw: captured.append(kw))

    from src.entities.player import Player
    game = make_game_with_fusion()
    p = Player(100, 100, mock_level, game=game)
    p.is_grounded = True
    game.fusion_manager.latch_fuse(mock_slime)
    assert p.is_fused

    mock_slime.juice = tuning.SLIME_DAZE_COST + 10
    initial_juice = mock_slime.juice

    with patch.object(input_manager, "btn", side_effect=_btn_map()), \
         patch.object(input_manager, "btnp", side_effect=_btn_map()), \
         patch.object(input_manager, "btnr", side_effect=_btn_map()), \
         patch.object(input_manager, "was_tap", return_value=True), \
         patch.object(input_manager, "hold_frames", return_value=0):
        p.handle_input(mock_slime)

    assert mock_slime.juice == initial_juice - tuning.SLIME_DAZE_COST
    assert len(captured) >= 1


def test_daze_blocked_on_low_juice(mock_level, mock_slime, make_game_with_fusion):
    """Phase 33 FUS-06: fused Z-tap with juice < SLIME_DAZE_COST does NOT
    fire and does NOT consume juice (Pitfall 4 cancel-spam guard)."""
    # ... mirrors above; assert juice unchanged + no event captured ...
```

**Differs from analog because:** test_event_bus.py exercises Player.handle_input via input_manager patches but does NOT enter the fused-branch (which is new in Phase 33). The fused-branch needs `make_game_with_fusion` fixture (already in `tests/conftest.py:62-91`) to wire FusionManager + latch_fuse before driving input.

---

### `tests/test_audio.py` (NEW)

**Analog:** `tests/test_drill_dive_parity.py:22-46` (mock-pyxel preamble) + `tests/test_event_bus.py` (subscribe-then-emit pattern).

**Test pattern — audio module init + play_sfx surface:**
```python
import sys
import types
from unittest.mock import MagicMock

# Audio test needs a richer pyxel mock — `pyxel.sounds[N].set(...)` and
# `pyxel.play(channel, sound_id)` must be callable.
if "pyxel" not in sys.modules:
    mock_pyxel = types.ModuleType("pyxel")
    mock_pyxel.sounds = [MagicMock() for _ in range(64)]
    mock_pyxel.play = MagicMock()
    # ... full key + btn stubs as in test_drill_dive_parity.py:22-46 ...
    sys.modules["pyxel"] = mock_pyxel

import pytest
import pyxel
from src.core import audio


def test_audio_init_does_not_raise():
    """Phase 33 FUS-06 (audio module loads): init_sounds runs without error."""
    audio.init_sounds()
    # All 7 slots must have had .set() called once.
    for slot_id in range(7):
        assert pyxel.sounds[slot_id].set.called


def test_play_sfx_known_name():
    """Phase 33 FUS-06: play_sfx fires pyxel.play with the correct slot."""
    pyxel.play.reset_mock()
    audio.play_sfx("drill_enemy_hit")
    pyxel.play.assert_called_once_with(-1, audio.SFX_DRILL_ENEMY_HIT)


def test_play_sfx_unknown_name_silent():
    """Phase 33: unknown cue name returns silently (does not raise)."""
    pyxel.play.reset_mock()
    audio.play_sfx("not_a_real_cue")
    pyxel.play.assert_not_called()
```

**Differs from analog because:** No prior audio test exists. The mock-pyxel preamble must be EXTENDED with `mock_pyxel.sounds = [MagicMock() for _ in range(64)]` (Open Question 4 in RESEARCH) — the conftest.py default `MagicMock()` may not support subscription `pyxel.sounds[N]`. If conftest.py needs updating to add the same line, that's a 1-line change.

---

### `tests/test_tuning_migration.py` (NEW)

**Analog:** `tests/test_tuning_livereach.py:1-90` (autouse `tuning.reset()` fixture, `tuning.set_value` mutation pattern) + `tests/test_tuning.py:32-48` (constant-baseline assertions).

**Test pattern — new tuning keys readable post-migration:**
```python
import pytest
from src.core import tuning


@pytest.fixture(autouse=True)
def _tuning_reset_after_each_test():
    """Restore baseline after each test — mirrors test_tuning_livereach.py:51-56."""
    yield
    tuning.reset()


# Phase 33 D-01/D-02/D-05/D-17 — migrated keys (no magic numbers per project memory).
EXPECTED_WINDUP_DURATION_FRAMES = 30
EXPECTED_ACCELERATED_REGEN_RATE = 1.0
EXPECTED_POGO_BOUNCE_VELOCITY = -2.5
EXPECTED_POGO_COOLDOWN_FRAMES = 0
EXPECTED_DRILL_ENEMY_COST = 15.0   # CONTEXT D-05 starting point
EXPECTED_SLIME_DAZE_COST = 20.0    # CONTEXT D-17 starting point


@pytest.mark.parametrize("key,expected", [
    ("WINDUP_DURATION_FRAMES",  EXPECTED_WINDUP_DURATION_FRAMES),
    ("ACCELERATED_REGEN_RATE",  EXPECTED_ACCELERATED_REGEN_RATE),
    ("POGO_BOUNCE_VELOCITY",    EXPECTED_POGO_BOUNCE_VELOCITY),
    ("POGO_COOLDOWN_FRAMES",    EXPECTED_POGO_COOLDOWN_FRAMES),
    ("DRILL_ENEMY_COST",        EXPECTED_DRILL_ENEMY_COST),
    ("SLIME_DAZE_COST",         EXPECTED_SLIME_DAZE_COST),
])
def test_new_tuning_key_readable(key, expected):
    """Phase 33 FUS-06 (panel surfaces new keys): tuning.X reads return
    the schema-seed value after migration. Validates the use-site path
    (Phase 25 pattern) — getattr(tuning, key) routes through _flat_index
    to _model[group][key]."""
    actual = getattr(tuning, key)
    assert actual == expected, (
        f"tuning.{key} expected {expected!r}, got {actual!r}. "
        f"Possible Pitfall 5: schema-seed value drifted from hardcoded baseline."
    )


def test_new_tuning_key_in_flat_index():
    """All Phase 33 migrated keys must be in tuning._flat_index (panel
    surface contract — Pitfall 6 prevention)."""
    expected_keys = {"WINDUP_DURATION_FRAMES", "ACCELERATED_REGEN_RATE",
                     "POGO_BOUNCE_VELOCITY", "POGO_COOLDOWN_FRAMES",
                     "DRILL_ENEMY_COST", "SLIME_DAZE_COST"}
    missing = expected_keys - set(tuning._flat_index)
    assert not missing, f"missing tuning keys: {missing}"
```

**Differs from analog because:** test_tuning_livereach.py drives `Player.update` to verify physics-effect propagation; test_tuning_migration.py is a simpler smoke test that ONLY checks attribute readability + flat-index inclusion (Pitfall 5 + Pitfall 6 guards). Pitfall 5: schema-seed value MUST equal the current hardcoded value, otherwise tests like `test_fusion_fsm.py::test_windup_*` flicker red.

---

### `33-FEEL-TARGETS.md` (NEW doc)

**Analog:** `.planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md` (full file).

**Document structure to mirror:**
1. **Header** with `> APPROVED YYYY-MM-DD` (post-sign-off) — top-level acceptance gate.
2. **Sectioned tables** (Ground / Air / Wall in Phase 29; for Phase 33: Charge Ritual / Drill Physics / Drill Combat / Pogo Confirm).
3. **Columns:** ID | Test | Pass Condition | Fail Condition | Result.
4. **Reference Values** section linking each pass/fail criterion to the underlying tuning value (Phase 29 maps `frames-to-stop = 9 → WALK_FRICTION=0.15`, etc.).
5. **Results** section with PASS markers for each ID.
6. **Sign-off** section with date + active preset name.

**ID prefix scheme** (mirror Phase 29's M-G/M-A/M-W):
- D-Cn — Charge ritual (windup, accel-regen, tap/hold)
- D-Dn — Drill physics (chain length, drift, exits)
- D-Kn — Drill combat (kill chain, juice-starvation, boss daze→drill)
- D-Pn — Pogo confirm-only (single confirm-only entry per CONTEXT D-18)

**Coverage areas (per CONTEXT D-08):** tap/hold ~8f threshold; WINDUP cancel-window feel (~30f); accelerated-regen ritual time (2× passive); drill chain length on full juice; juice-starvation Exit (b); enemy kill chain through 3+ enemies (NEW); enemy-cost balance against boss daze→drill loop; pogo confirm-only entry.

**Differs from analog because:** Phase 33 has a new section (Drill Combat) without a Phase 29 precedent — RESEARCH § Validation table provides the test list for that section. Pogo gets ONE entry per D-18 (no full pogo table). Target count per CONTEXT § Claude's Discretion: ~10–15 total, pogo gets 1, the rest split across charge/drill physics/drill combat.

---

## Shared Patterns

### Pattern: Use-site `tuning.X` reads (Phase 25)

**Source:** `src/fusion/drill_dive.py:89-91, 117-122, 155-157`
**Apply to:** `src/fusion/charge_controller.py` (migration of WINDUP_DURATION_FRAMES + ACCELERATED_REGEN_RATE), `src/fusion/pogo.py` (migration of POGO_BOUNCE_VELOCITY + POGO_COOLDOWN_FRAMES), `src/entities/player.py:197` daze branch (read of SLIME_DAZE_COST), `src/fusion/drill_dive.py` enemy scan (read of DRILL_ENEMY_COST).
```python
# Pattern: read at the line of use, not at module import time.
slime.consume(tuning.DRILL_ENEMY_COST)         # NEW Phase 33
self._windup_progress += 1.0 / tuning.WINDUP_DURATION_FRAMES  # migrated
return TickResult(dx=0.0, dy=tuning.POGO_BOUNCE_VELOCITY, ...)  # migrated
```
This pattern lets `tuning.set_value(...)` from the panel reach gameplay on the next frame without rebinds (verified by Phase 25 livereach test).

---

### Pattern: Subscriber wiring in `Game.__init__` (Phase 31 Pitfall 5)

**Source:** `main.py:282-348`
**Apply to:** All Phase 33 new event subscribers (`drill_enemy_hit` audio + particle, `pogo_bounce` audio, `drill_start` / `drill_block_break` / `drill_impact` / `fuse_start` / `daze_fire` audio).
```python
# Closure captures self.player, self.particles, self.spawn_particle_burst.
def _on_drill_enemy_hit(x=None, y=None, **kw):
    if x is None or y is None:
        return
    self.spawn_particle_burst(x, y, type="drill_enemy_hit")
_event_bus.subscribe("drill_enemy_hit", _on_drill_enemy_hit)
```
Wired ONCE in `Game.__init__` — not in `Player.__init__` (which runs every `Game.reset()`, accumulating subscriber leaks).

---

### Pattern: Mock-pyxel preamble for tests

**Source:** `tests/test_drill_dive_parity.py:19-46` (full mock pyxel module install)
**Apply to:** `tests/test_destructive_drill.py`, `tests/test_audio.py`. test_daze_shot.py and test_tuning_migration.py rely on `tests/conftest.py:16` (`sys.modules.setdefault("pyxel", MagicMock())`), which is sufficient for non-`pyxel.sounds[N].set()` callers.
```python
import sys
import types
if "pyxel" not in sys.modules:
    mock_pyxel = types.ModuleType("pyxel")
    mock_pyxel.KEY_LEFT = 0  # ... all keys ...
    mock_pyxel.frame_count = 0
    mock_pyxel.btn = lambda k: False
    mock_pyxel.btnp = lambda k, **kw: False
    # ...
    sys.modules["pyxel"] = mock_pyxel
```
For audio tests, EXTEND with `mock_pyxel.sounds = [MagicMock() for _ in range(64)]` and `mock_pyxel.play = MagicMock()` (Open Question 4).

---

### Pattern: Named constants (project memory rule)

**Source:** Every module — examples at `src/fusion/pogo.py:25-39`, `src/fusion/drill_dive.py:28-37`, `main.py:158-180`.
**Apply to:** `src/core/audio.py` (slot IDs, name map, auto-channel sentinel), `main.py` PARTICLE_DRILL_*_U/V cells, `src/core/debug.py` warp-target level-id constants, all test files (EXPECTED_* baseline values).
```python
# Anti-pattern: pyxel.play(-1, 3)
# Pattern: pyxel.play(_AUTO_CHANNEL, SFX_DRILL_ENEMY_HIT)
```
Every numeric/string literal becomes a named constant in its owning module. MEMORY auto-rule (`feedback_magic_numbers.md`).

---

### Pattern: `event_bus.emit(name, **kwargs)` is side-channel only

**Source:** `src/anim/event_bus.py:1-25`, MEMORY `project_reanimator_anim_architecture.md`.
**Apply to:** `drill_enemy_hit` and `daze_fire` and `pogo_bounce` emit sites. Events MIRROR gameplay; they do NOT drive gameplay FSM. The damage + cost happen in `drill_dive.py:on_tick`; the event emission is a side effect for particle + SFX subscribers.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| (none) | — | — | Every Phase 33 file has a directly-applicable in-repo analog. |

The closest "no analog" risk was `src/core/audio.py` — but `src/core/debug.py` and `src/core/overlays.py` provide a sufficient module-shape template (named-constant block + module-level state + simple function surface). The Pyxel audio API itself is verified from official examples (RESEARCH § Standard Stack), so the `pyxel.sounds[N].set()` and `pyxel.play(...)` calls are NOT hand-rolled even though no in-repo audio precedent exists.

The `daze-on-hit stun primitive` on Enemy is technically un-analog'd in the existing codebase (RESEARCH § Don't Hand-Roll explicitly flags this — `Mole` boss has a state machine, not a reusable stun). The 5-line addition to `Enemy.__init__` (`self.stun_timer = 0`) and the early-return in each subclass `update()` is novel for this codebase, but it's small enough that the planner can decide whether to ship it in Phase 33 or carve it out per CONTEXT § Claude's Discretion + RESEARCH Open Question 1. Its analog is the `invuln_timer` field already on `Player.__init__:50` and decremented at `Player.update_timers:186-187` — same shape, different actor.

---

## Metadata

**Analog search scope:**
- `src/fusion/` (drill_dive.py, pogo.py, charge_controller.py, manager.py, protocol.py)
- `src/entities/` (player.py, slime.py, projectile.py, enemies.py, boss.py, effects.py)
- `src/anim/event_bus.py`, `src/core/` (debug.py, overlays.py, tuning.py, sprite_utils.py, input.py)
- `src/ui/panel.py` (FEEL_GROUPS + TAB_DEFS)
- `main.py` (subscriber wiring + spawn_particle_burst + spawn_explosion shim + debug-warp consume)
- `assets/physics-schema.json`, `assets/presets/slot_1.json`
- `tests/` (conftest.py, test_drill_dive_parity.py, test_pogo.py, test_fusion_fsm.py, test_tuning_livereach.py, test_tuning.py, test_event_bus.py)
- `.planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md`

**Files scanned:** ~25
**Pattern extraction date:** 2026-04-28
