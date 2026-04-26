# Phase 32: Fusion Manager + Protocol Refactor — Pattern Map

**Mapped:** 2026-04-26
**Files analyzed:** 13 (6 new, 7 modified)
**Analogs found:** 12 / 13 (one new pattern: `typing.Protocol` is novel to the codebase)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| **NEW** `src/fusion/__init__.py` | package init | n/a | `src/anim/__init__.py` (if present) — otherwise convention-only | structural |
| **NEW** `src/fusion/protocol.py` | interface + value-object | request-response | `src/anim/anim_clip.py` (frozen dataclass) + new `typing.Protocol` (no in-tree analog) | partial — dataclass has analog, Protocol is new |
| **NEW** `src/fusion/manager.py` | service / FSM-shell | event-driven (per-frame tick + dispatcher) | `src/anim/state_machine.py::AnimFSM` | exact (state-shell with rules/clips → abilities/active; tick + transitions; instantiated once on Game) |
| **NEW** `src/fusion/charge_controller.py` | service / sub-FSM | request-response (input-driven) | `src/entities/player.py::handle_input` Z-block (L240-281) | role-match — extracts existing logic |
| **NEW** `src/fusion/drill_dive.py` | ability driver | request-response (per-frame physics) | `src/entities/player.py::apply_diving_physics` (L385-398) + `src/anim/player_anim.py::PlayerAnimDriver` (driver-style class) | exact — code MOVES verbatim per D-10 |
| **NEW** `src/fusion/pogo.py` | ability driver | event-driven (one-shot on enter, contact-resolved) | `src/fusion/drill_dive.py` (sibling) — fall back to player.py drill block-break branch (L460-484) for contact resolution | role-match — null-fusion sibling shape |
| **MOD** `src/entities/player.py` | entity | (delete-only for fusion paths) | self (post-Phase-31.5 file is its own analog for the surrounding shape) | self |
| **MOD** `src/entities/slime.py` | entity | CRUD on juice + FSM (recall/dissipate) | self (recommendation: do not modify; ChargeController calls existing API per D-Discretion #8) | self |
| **MOD** `src/core/save_manager.py` | persistence service | file-I/O | self + `src/anim/event_bus.py` (module-level pattern reference for `CURRENT_SAVE_VERSION` constant placement) | self |
| **MOD** `main.py` (Game.__init__) | composition root | wiring | `main.py:241-313` (existing event_bus subscriber wiring block) | exact — same instantiation idiom |
| **MOD** `tests/test_fusion.py` | test | unit | self (existing 11 test methods) — migrate `player.fuse(slime)` → `game.fusion_manager.latch_fuse(slime)` | self |
| **MOD** `tests/test_save_system.py` | test | unit | self — update `data["version"] == 1` → `data["save_version"] == 2`; add `TestSaveVersionRejection` class | self |
| **MOD (optional)** `src/anim/player_anim.py` | n/a | n/a | only if D-14 picks (b)/(c) — D-14 (a) means NO CHANGE | n/a |

---

## Pattern Assignments

### `src/fusion/__init__.py` (package init)

**Analog:** Standard Python package convention (no per-package `__init__.py` exporters required in this codebase — `from src.anim import event_bus` works against an empty `src/anim/__init__.py` today).

**Recommendation:** Empty file or shallow re-exports. RESEARCH § Component Responsibilities suggests:
```python
# src/fusion/__init__.py
"""Phase 32: Fusion subsystem (FUS-04).

Public surface:
    FusionAbility, TickResult        from .protocol
    FusionManager                    from .manager
    ChargeController                 from .charge_controller
    DrillDive                        from .drill_dive
    Pogo                             from .pogo
"""
from src.fusion.protocol import FusionAbility, TickResult
from src.fusion.manager import FusionManager
from src.fusion.charge_controller import ChargeController
from src.fusion.drill_dive import DrillDive
from src.fusion.pogo import Pogo

__all__ = [
    "FusionAbility", "TickResult",
    "FusionManager", "ChargeController",
    "DrillDive", "Pogo",
]
```
**What to copy:** module-level docstring style + `__all__` discipline.
**What to change:** none — this file is greenfield.
**Anti-patterns:** none flagged.

---

### `src/fusion/protocol.py` (interface + value-object, request-response)

**Analog 1 (TickResult):** `src/anim/anim_clip.py` — frozen-slots dataclass precedent.

**Imports + dataclass pattern** (`src/anim/anim_clip.py:1-19`):
```python
"""Phase 26 ANIM-01 clip data. Phase 31 will add event bindings per ANIM-04;
the events slot is reserved now so it is not a breaking change next phase."""
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
**What to copy:** `@dataclass(frozen=True, slots=True)`; module docstring style citing the phase + decision number; per-field inline comments.
**What to change:** `TickResult` fields are `dx: float`, `dy: float`, `request_exit: bool`, `exit_reason: Optional[str]` per RESEARCH § Pattern 1.

**Analog 2 (FusionAbility):** **NO IN-TREE ANALOG** — `Grep("Protocol", path="src/")` returned no matches. This is a **new pattern** for the codebase. RESEARCH § Pattern 2 supplies the canonical D-09 shape:
```python
# src/fusion/protocol.py — new pattern, no in-tree precedent
from typing import Protocol, runtime_checkable

@runtime_checkable
class FusionAbility(Protocol):
    """Per CONTEXT D-09. requires_fused=False for null-fusion (pogo, D-16)."""
    id: str
    requires_fused: bool

    def can_activate(self, player, slime) -> bool: ...
    def on_enter(self, player, slime, context: dict) -> None: ...
    def on_tick(self, player, slime, dt: float) -> "TickResult": ...
    def on_exit(self, player, slime, reason: str) -> None: ...
    def on_event(self, name: str, data: dict) -> None: ...
```
**What to copy:** D-09 verbatim — it IS the source.
**What to change:** nothing in the shape; planner decides whether `@runtime_checkable` decorator is applied (RESEARCH recommends yes — cheap and lets `isinstance(x, FusionAbility)` work in tests).
**Anti-patterns:** Do NOT use `abc.ABC` + abstract methods (D-09 locks Protocol; structural typing is the point).

---

### `src/fusion/manager.py` (service / FSM-shell, event-driven)

**Analog:** `src/anim/state_machine.py::AnimFSM`.

**Imports + class shell** (`src/anim/state_machine.py:1-23`):
```python
"""Phase 26 ANIM-01 generic animation decision class. Rules-list evaluator per
D-00a / D-04 (NOT a classical transition-edge FSM -- name is kept for
requirement traceability, not API semantics)."""
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
        # Start on fallback clip (last rule per D-06).
        self._player = AnimPlayer(clips[rules[-1][1]])
        self._last_clip_id: str | None = None
```
**What to copy:**
- Module docstring citing phase + decisions (D-06/D-07/D-13/D-17).
- Construction-time validation: `missing = [aid for aid in self._abilities ... if not isinstance(ability, FusionAbility)]`.
- Underscore-prefixed private state (`self._abilities`, `self._active`).
- Single-responsibility methods (one `tick`, one `handle_jump_input`).

**Per-frame tick pattern** (`src/anim/state_machine.py:25-34`):
```python
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
**What to copy:** the "delegate to active ability and let it do the work" shape. Translate as `result = self._active.on_tick(player, slime, dt); apply intent; emit on transition`.
**What to change:** AnimFSM evaluates rules to pick a clip per frame; FusionManager has a single `_active` ability set by `latch_fuse`/`handle_jump_input` and delegates. Skeleton sketched in RESEARCH § Code Examples (Recommended FusionManager.tick skeleton).

**Event emission pattern** (from `src/entities/player.py:71` + `src/anim/event_bus.py:17`):
```python
# emission idiom — single-line, kwargs by name
event_bus.emit("fuse_end")
event_bus.emit("drill_block_break", tx=tx, ty=ty)  # match existing kwargs
```
**What to copy:** kwarg signatures MUST match existing emit sites char-for-char (Pitfall 1, RESEARCH § Common Pitfalls). The provisional bridge at `player.py:482` uses `tx=tx, ty=ty`; the new emit in `drill_dive.py::on_tick` reuses these exact kwarg names.

**Mana shield routing pattern** (current `src/entities/player.py:110-124`):
```python
# Mana shield: fused damage consumes juice, not HP (D-04)
if self.is_fused and slime and slime.juice > 0:
    slime.consume(tuning.MANA_SHIELD_COST)
    self.invuln_timer = tuning.INVULN_DURATION
    # Check for juice-empty dissipation (D-05)
    if slime.juice <= 0:
        self.unfuse(slime, dissipate=True)
    # Apply knockback but no HP loss
    if source_x is not None:
        kx = -tuning.KNOCKBACK_FORCE_X if self.x < source_x else tuning.KNOCKBACK_FORCE_X
        self.dx = kx
        self.dy = tuning.KNOCKBACK_FORCE_Y
        self.knockback_timer = 10
        self.is_grounded = False
    return True
```
**What to copy:** the conditional + `slime.consume(MANA_SHIELD_COST)` + dissipate-on-empty pattern. Per D-07, this LOGIC moves into `FusionManager.apply_fused_damage(player, slime, source_x)` (or equivalent name). `Player.take_damage` becomes a thin caller that defers to the manager when fused.
**What to change:** the `self.unfuse(slime, dissipate=True)` call becomes `self._force_exit_dissipate(slime)` or equivalent internal manager method (D-13 deletes `Player.unfuse`).
**Magic number flag (MEMORY):** the literal `10` for knockback timer is already a magic number in current code — Phase 32 should not re-introduce it. Use `tuning.KNOCKBACK_DURATION_FRAMES` or `KNOCKBACK_TIMER_FRAMES` constant if not yet named.

**RESEARCH-supplied skeleton** (`32-RESEARCH.md` § Code Examples):
```python
# src/fusion/manager.py
class FusionManager:
    def __init__(self, abilities: dict[str, FusionAbility]):
        self._abilities = abilities
        self._active: FusionAbility | None = None
        self.is_fused: bool = False
        self._exit_cooldown_frames: int = 0  # SLIME_DISSIPATE_COOLDOWN ticks down here

    def tick(self, player, slime, dt: float) -> None:
        if self._exit_cooldown_frames > 0:
            self._exit_cooldown_frames -= 1
        if self._active is None:
            return
        result = self._active.on_tick(player, slime, dt)
        # Apply intent
        player.dx = result.dx if result.dx is not None else player.dx
        player.dy = result.dy if result.dy is not None else player.dy
        # Handle exit signal
        if result.request_exit:
            self._active.on_exit(player, slime, result.exit_reason or "unknown")
            self._active = None
            if result.exit_reason == "juice_empty":
                slime.dissipate()
                self._exit_cooldown_frames = tuning.SLIME_DISSIPATE_COOLDOWN
            self.is_fused = False
            slime.is_fused = False
            event_bus.emit("fuse_end")

    def handle_jump_input(self, player, slime, input_manager) -> None:
        if not (input_manager.btnp("jump") and input_manager.btn("down")
                and not player.is_grounded):
            return
        target_id = "drill_dive" if self.is_fused else "pogo"
        ability = self._abilities[target_id]
        if ability.can_activate(player, slime):
            self._active = ability
            ability.on_enter(player, slime, context={})
```
**What to copy:** verbatim as the seed.
**What to change:** add `latch_fuse(slime)`, `force_exit(reason)`, `apply_fused_damage(...)` per D-07/D-13/D-15. Also: `latch_fuse` MUST set `slime.is_fused = True` (Pitfall 4 — duplicate state, both flags drive different consumers).
**Anti-patterns to avoid:**
- Two-owner state (D-13 forbids `Player.fuse/unfuse` shims).
- Forgetting `slime.is_fused` write in `latch_fuse`/`force_exit` (Pitfall 4 — overlays.py and slime.update both check it).

---

### `src/fusion/charge_controller.py` (service / sub-FSM, request-response)

**Analog:** existing Z-button block in `src/entities/player.py::handle_input` (L240-281) — code MIGRATES here.

**Existing logic to migrate** (`src/entities/player.py:265-281`):
```python
elif input_manager.btn("spit") and not self.is_fused and self.state != "DIVING":
    # Z is held -- start/continue recall after threshold
    if input_manager.hold_frames("spit") >= tuning.SPIT_HOLD_THRESHOLD and not slime.is_dissipated:
        self.is_charging_recall = True
        slime.recall(self.x, self.y)

# Each frame during recall, check if slime has arrived for auto-fuse (D-02)
if self.is_charging_recall and slime.is_recalling:
    arrived = slime.update_recall(self.x, self.y)
    if arrived and slime.juice >= slime.max_juice:
        self.fuse(slime)

# Cancel recall on Z release if was charging
if input_manager.btnr("spit") and self.is_charging_recall:
    self.is_charging_recall = False
    slime.is_recalling = False
    slime.recall_trail.clear()
```
**What to copy:** every conditional, every `slime.*` call, every `tuning.*` reference. The state moves verbatim; only the owner changes from `Player.is_charging_recall` to `ChargeController._state` / `ChargeController._charging`.
**What to change:**
- `self.is_charging_recall = True` → `self._state = "RECALL"` (or equivalent enum/string).
- `self.fuse(slime)` → emit second-pass-200% latch logic per D-06; final 200% latch calls `self._fusion_manager.latch_fuse(slime)` and emits `fuse_start`.
- ADD WINDUP state: second-pass 100→200% accumulator. Increment from `slime.update_recall` arrival per D-06; gate on `slime.juice == slime.max_juice` (the existing 100% gate at L274 is the consolidation target).
- ADD accelerated-regen branch (CONTEXT § Claude's Discretion #8): per-frame `slime.refill(ACCELERATED_REGEN_RATE)` while Z held + slime docked + not dissipated.

**Input primitives** (`src/core/input.py:51-61`):
```python
def hold_frames(action):
    """Return the number of consecutive frames the action has been held."""
    return _hold_frames.get(action, 0)


def was_tap(action, threshold):
    """Check if the action was just released after being held for <= threshold frames."""
    if any(pyxel.btnr(k) for k in _ACTION_MAP[action]):
        prev = _prev_hold_frames.get(action, 0)
        return 0 < prev <= threshold
    return False
```
**What to copy:** call these directly per D-06. ChargeController never re-implements frame counting — it consumes `input_manager.hold_frames("spit")` and `input_manager.was_tap("spit", SPIT_HOLD_THRESHOLD)`.
**What to change:** nothing in `input.py`. ChargeController is a pure consumer.

**Slime API reuse** (`src/entities/slime.py:46-86, 217-223`):
```python
def recall(self, player_x, player_y):
    """Start recalling slime toward player (D-25). Called when Z is held unfused."""
    if self.is_dissipated:
        return  # Can't recall dissipated slime
    self.is_recalling = True
    ...

def update_recall(self, player_x, player_y):
    """Move slime toward player during recall. Returns True when overlapping."""
    ...
    if dist <= tuning.RECALL_OVERLAP_DIST:
        ...
        return True  # Arrived
    ...

def refill(self, amount):
    self.juice = min(self.max_juice, self.juice + amount)

def consume(self, amount):
    if debug.god_infinite_juice:
        return
    self.juice = max(0.0, self.juice - amount)
```
**What to copy:** call signatures unchanged. ChargeController calls `slime.recall(player.x, player.y)`, `slime.update_recall(player.x, player.y)`, `slime.refill(rate)`. **Do not** rewrite slime state.
**Anti-patterns:**
- Pitfall 6: `is_charging_recall` orphaned state. The Player attribute MUST be deleted in the same commit that introduces ChargeController, not left as a dead read.
- Magic number flag (MEMORY): `tuning.SPIT_HOLD_THRESHOLD` is correct — but if the planner picks a v2.0 retune (deferred to Phase 33), the constant lives in `physics-schema.json` already. ChargeController's tap/hold call: `input_manager.was_tap("spit", tuning.SPIT_HOLD_THRESHOLD)`.

---

### `src/fusion/drill_dive.py` (ability driver, request-response per-frame physics)

**Analog 1 (apply_diving_physics MOVES verbatim):** `src/entities/player.py:385-398`:
```python
def apply_diving_physics(self, slime):
    self.dy = tuning.DRILL_SPEED
    # Horizontal drift
    if input_manager.btn("left"):
        self.dx = -tuning.DRILL_DRIFT_SPEED
    elif input_manager.btn("right"):
        self.dx = tuning.DRILL_DRIFT_SPEED
    else:
        self.dx = 0

    # Out of juice check
    if slime.juice <= 0:
        self.state = "FALLING"
        self.unfuse(slime, dissipate=True)
```
**What to copy:** every line. This is the **v1.3 parity contract** (CONTEXT § Known Constraints).
**What to change:**
- `self.dy = tuning.DRILL_SPEED` → returned via `TickResult(dy=tuning.DRILL_SPEED, ...)` per RESEARCH § Pattern 1.
- The `slime.juice <= 0` branch becomes `request_exit=True, exit_reason="juice_empty"` in the returned TickResult (FusionManager handles the dissipate per D-07).
- The `self.state = "FALLING"` write — see Open Question #1 in RESEARCH. Recommendation: drill_dive's `on_exit` writes `player.state = "FALLING"` (juice-empty path) or `"IDLE"` (solid-landing path) as a transitional shim so existing animation rules in `player_anim.py:129` keep matching.

**Analog 2 (block-break + soft destructible passthrough):** `src/entities/player.py:460-498`:
```python
if collision:
    if self.dy >= 0:
        # Check for destructible tiles during Drill Dive
        if self.state == "DIVING" and slime:
            tile_coord = self.level_map.get_destructible_at(self.x, self.y, self.w, self.h)
            if tile_coord:
                tx, ty = tile_coord
                tile_type = self.level_map.get_tile(tx, ty)
                if self.game:
                    self.game.on_block_destroyed(tx, ty, tile_type)
                self.level_map.remove_tile(tx, ty)
                if self.game:
                    self.game.spawn_explosion(tx * tuning.TILE_SIZE, ty * tuning.TILE_SIZE, 9)
                if tile_type == INTGRID_CRACKED_V:
                    slime.consume(tuning.DRILL_CRACKED_V_COST)  # Gate block costs juice (ABL-02)
                else:
                    slime.refill(tuning.DRILL_BLOCK_REFUND)  # Soft block refunds juice
                self.on_block_break()
                # Phase 31 provisional bridge: emit drill_block_break so
                # the drill-recoil animation pause fires on commit. Phase 32
                # owns the canonical emit site per FUSION-DESIGN and MUST
                # remove this bridge during its refactor.
                event_bus.emit("drill_block_break", tx=tx, ty=ty)
                return

        # Snap to floor
        target_row = int((self.y + self.h) // tuning.TILE_SIZE)
        self.y = target_row * tuning.TILE_SIZE - self.h
        self.is_grounded = True
        if not was_grounded:
            event_bus.emit("land")

        # Impact consumption
        if self.state == "DIVING" and slime:
            slime.consume(tuning.DRILL_IMPACT_COST)
            # ANIM-02 emit; may move in Phase 32 per FUSION-DESIGN lock
            event_bus.emit("drill_impact")
            self.state = "IDLE" # Landed
            self.unfuse(slime)
```
**What to copy:** every conditional, every constant reference, every `slime.consume`/`slime.refill` call, the `event_bus.emit("drill_block_break", tx=tx, ty=ty)` kwarg signature **char-for-char** (Pitfall 1).
**What to change:**
- The branch lives in `drill_dive.py::on_tick` post-collision-detection, NOT in `Player.move_and_collide`. The planner picks how the ability sees the collision result — either (a) drill_dive owns its own `move_and_collide` adapted from player.py, or (b) Player.move_and_collide returns collision metadata for the ability to consume.
- `event_bus.emit("drill_block_break", tx=tx, ty=ty)` is the **canonical** emit site post-Phase-32. The provisional bridge at player.py:482 MUST be DELETED in the same commit (Pitfall 2).
- `self.unfuse(slime)` → return TickResult with `request_exit=True, exit_reason="solid_landing"` (D-13 deletes `Player.unfuse`; FusionManager handles).
- ADD `event_bus.emit("drill_start")` from `on_enter` (D-12).
- ADD `event_bus.emit("drill_end")` from `on_exit` (D-12). Existing `event_bus.emit("drill_impact")` at L496 stays at the impact moment (different event, both keep firing).

**100% gate consolidation** (current entry at `src/entities/player.py:283-296`):
```python
if input_manager.btnp("jump") and self.state != "DIVING":
    if (input_manager.btn("down") and self.has_drill
            and not self.is_grounded and slime.juice > 0):
        # DOWN+SPACE = Drill Dive (D-12 remap from DOWN+V)
        dist_sq = (self.x - slime.x)**2 + (self.y - slime.y)**2
        if dist_sq < tuning.SLIME_MAX_DIST**2:
            self.state = "DIVING"
            self.fuse(slime)
            self.dy = tuning.DRILL_SPEED
            self.dx = 0
            slime.consume(tuning.DRILL_ACTIVATION_COST)
            return
```
**What to copy:** the gate logic — `has_drill`, airborne, `slime.juice` check, `dist_sq < SLIME_MAX_DIST**2`.
**What to change:** the juice check tightens from `slime.juice > 0` to `slime.juice == slime.max_juice` (CONTEXT specifics — "tightening the existing rule"). This logic moves to `DrillDive.can_activate(player, slime)` per D-09. The dispatch lives in `FusionManager.handle_jump_input` per D-17.

**Mid-drill jump-cancel — DELETE ENTIRELY** (`src/entities/player.py:298-302`):
```python
# Drill Dive Cancellation
if self.state == "DIVING":
    if input_manager.btnp("jump"):
        self.state = "FALLING"
        self.unfuse(slime)
        self.dy = 0
    return
```
**What to copy:** NOTHING.
**What to change:** delete the 5-line block in the same commit. Pitfall 5 (RESEARCH): even the `if self.state == "DIVING": return` shell would shadow correct dispatch through FusionManager. Replace with a brief comment: `# Drill physics now owned by src/fusion/drill_dive.py per Phase 32 D-10`.

**Anti-patterns:**
- Reintroducing the mid-drill jump-cancel in any form (no Z-hold variant, no replacement input — FUSION-DESIGN re-lock 2026-04-20).
- Editing `_v1.3-reference.json` drill values (CONTEXT specifics — preset is frozen).
- Magic numbers: `9` (explosion size at `player.py:472`) is a magic number in current code. If the call moves into drill_dive.py, consider lifting to `EXPLOSION_SIZE_PX = 9` or read from the existing `tuning.EXPLOSION_SIZE` if present.

---

### `src/fusion/pogo.py` (ability driver, event-driven contact)

**Analog 1:** `src/fusion/drill_dive.py` (sibling — same Protocol shape, lower juice/cost behavior).

**Analog 2 (contact resolution against destructibles):** `src/entities/player.py:460-484` (drill block-break branch — pogo reuses the soft-destructible passthrough). Per CONTEXT D-19 + Discretion #4: "Whether pogo reuses the drill soft-destructible passthrough code path directly or duplicates a minimal version" — **planner picks**.

**Pattern (drill block-break, adapted)**:
```python
# Drill version (player.py:464-476):
tile_coord = self.level_map.get_destructible_at(self.x, self.y, self.w, self.h)
if tile_coord:
    tx, ty = tile_coord
    tile_type = self.level_map.get_tile(tx, ty)
    ...
    self.level_map.remove_tile(tx, ty)
    ...
    if tile_type == INTGRID_CRACKED_V:
        slime.consume(tuning.DRILL_CRACKED_V_COST)  # Gate block costs juice
    else:
        slime.refill(tuning.DRILL_BLOCK_REFUND)  # Soft block refunds juice
```
**What to copy:** the `get_destructible_at` + `remove_tile` flow.
**What to change:**
- D-19: pogo breaks **soft destructibles only** (no CRACKED_V — cracked blocks need drill). The branch becomes:
  ```python
  if tile_coord and tile_type != INTGRID_CRACKED_V:
      level_map.remove_tile(tx, ty)
      bounce = True
  ```
- D-19: **no juice refund** on pogo block-break (pogo is free per D-20 — `slime.refill` line is removed).
- D-19: pogo bounces on enemy contact (separate branch — no in-tree analog; planner introduces enemy-contact detection or relies on collision callbacks).

**Constants pattern** (`src/anim/player_anim.py:14-49`):
```python
# --- Named constants (project memory: no magic numbers) ---------------------
# v1.3 sprite u offsets for the 16x16 player sheet (image bank 1).
IDLE_U = 0
RUN_FRAME_A_U = 16
...
LAND_SQUASH_FRAMES = 4            # D-02: ticks after is_grounded flips
TURN_SKID_FRAMES = 3              # D-03: ticks after facing flips
JUMP_CROUCH_FRAMES = 2            # D-04: ticks after jump_start emit
DRILL_RECOIL_PAUSE_FRAMES = 3     # D-06: AnimPlayer.pause_for ticks per block-break
```
**What to copy:** module-level UPPER_SNAKE constants; one-line inline comment with phase + decision; `# --- Named constants (project memory: no magic numbers)` banner comment.
**What to change:** pogo's constants (per CONTEXT § Discretion #5):
```python
# src/fusion/pogo.py — Phase 32 D-18 / D-19 / D-20
# Hardcoded constants per D-18 (no tuning group, no panel, no preset entry).

POGO_BOUNCE_VELOCITY = -2.5      # negative = upward; planner picks final value
POGO_COOLDOWN_FRAMES = 0         # D-20: free, no cooldown in v2.0 baseline
POGO_DAMAGE = 1                  # D-19: damage to enemies on contact
POGO_INITIAL_DY = 2.0            # downward strike velocity on enter
```
**Anti-patterns:**
- ADDING a `pogo` group to `physics-schema.json` (D-18 explicitly hardcoded).
- ADDING juice cost to pogo (D-20 explicitly free).
- Reusing `DRILL_CRACKED_V_COST` for pogo cracked-block contact (D-19 — pogo cannot break cracked blocks; cracked-V is drill territory per MEMORY block-gate hierarchy).

---

### `src/entities/player.py` (entity, MODIFIED — delete-only for fusion paths)

**Analog:** self (post-Phase-31.5).

**`__init__` Fusion section** (current `src/entities/player.py:38-50`):
```python
# Fusion
self.is_fused = False

# Health & Combat
self.hp = tuning.PLAYER_MAX_HP
self.max_hp = tuning.PLAYER_MAX_HP
self.invuln_timer = 0
self.knockback_timer = 0
# Upgrades
self.has_drill = False # Must find item to use Drill Dive

# Fusion system (D-01 through D-05)
self.is_charging_recall = False  # True when holding Z unfused (charging toward fusion)
```
**What to change:**
- DELETE `self.is_fused = False` (line 39) — replaced by `@property` per D-14a.
- DELETE `self.is_charging_recall = False` (line 50) — moves to ChargeController per Pitfall 6.
- KEEP `has_drill`, `hp`, `max_hp`, `invuln_timer`, `knockback_timer` (unchanged).

**Add @property is_fused** (RESEARCH § Pattern 4 / D-14a):
```python
# Replace deleted self.is_fused = False (line 39) with:
@property
def is_fused(self) -> bool:
    """Phase 32 D-14a: derived from FusionManager. Single authoritative source.
    Returns False when game is None (test fixtures construct Player without game)."""
    return self.game is not None and self.game.fusion_manager.is_fused
```
**What to copy:** RESEARCH § D-14 Trade-off Analysis — the `self.game is None` short-circuit is **load-bearing** for `tests/test_fusion.py:48` which constructs `Player(px, py, level_map)` with no game.

**`fuse` and `unfuse` methods — DELETE** (current `src/entities/player.py:59-84`):
```python
def fuse(self, slime):
    """Enter fused state. ALWAYS use this instead of setting is_fused directly (Pitfall 3)."""
    self.is_fused = True
    slime.is_fused = True
    slime.is_recalling = False
    self.is_charging_recall = False
    event_bus.emit("fuse_start")

def unfuse(self, slime, dissipate=False):
    """Exit fused state. ALWAYS use this instead of setting is_fused directly (Pitfall 3).
    If dissipate=True, slime enters burnout cooldown (D-05)."""
    self.is_fused = False
    slime.is_fused = False
    event_bus.emit("fuse_end")
    if dissipate:
        slime.dissipate()
    else:
        slime.reform(self.x, self.y, self.facing_right, self.level_map)
```
**What to copy:** the **logic** moves into `FusionManager.latch_fuse` / `FusionManager.force_exit`. Specifically:
- `slime.is_fused = True` write — moves verbatim to `latch_fuse` (Pitfall 4).
- `slime.is_recalling = False` — moves to `latch_fuse` (or stays in ChargeController on the latch handoff).
- `event_bus.emit("fuse_start")` — moves to ChargeController per D-06 (NOT manager — emission lives at the latch site).
- `event_bus.emit("fuse_end")` — moves to FusionManager per D-07.
- `slime.dissipate()` — moves to `FusionManager.force_exit("juice_empty")` or `tick`-loop EXIT branch.
- `slime.reform(...)` — moves to `FusionManager.force_exit("solid_landing")` non-dissipate path.
**What to change:** DELETE both methods entirely. D-13 explicit: no shim layer.

**`update` DIVING branch** (current `src/entities/player.py:86-104`):
```python
def update(self, slime):
    if not self.is_alive:
        return

    # God-mode ability override (D-10)
    if debug.god_abilities:
        self.has_drill = True

    input_manager.update()  # Must run before any input checks
    self.update_timers()
    self.handle_input(slime)
    if self.state == "DIVING":
        self.apply_diving_physics(slime)
        self.move_and_collide(slime)
    else:
        self.apply_physics()
        self.move_and_collide(slime)
    self.update_state()
    self._update_anim_driver()   # D-14: last call of update()
```
**What to change:** Replace lines 97-99 with a call to `self.game.fusion_manager.tick(self, slime, dt)` BEFORE `move_and_collide`. The branch becomes:
```python
input_manager.update()
self.update_timers()
self.handle_input(slime)
if self.game:
    self.game.fusion_manager.tick(self, slime, dt=1.0)  # ability owns DIVING physics per D-10
self.apply_physics()  # NOTE: drill physics returned dx/dy via TickResult; apply_physics handles fall-through gravity for non-fused
self.move_and_collide(slime)
self.update_state()
self._update_anim_driver()
```
Open Question #1 in RESEARCH: planner decides exact ordering — preserved here as a sketch.

**`take_damage` mana-shield branch** (`src/entities/player.py:106-124` — quoted earlier):
**What to change:** routed through FusionManager. The `if self.is_fused and slime and slime.juice > 0:` block becomes:
```python
if self.is_fused and slime and slime.juice > 0:
    return self.game.fusion_manager.apply_fused_damage(self, slime, source_x)
```
The dissipate-on-empty path moves into FusionManager. The knockback application is the planner's call — keep on Player or push into the manager.

**Z-input handling** (`src/entities/player.py:240-281`): replace with a single delegation:
```python
# Replace L240-281 (Z-button block) with:
if self.game:
    self.game.charge_controller.handle_z_input(self, slime, input_manager)
```

**DOWN+SPACE handling** (`src/entities/player.py:283-304`): replace with a single delegation:
```python
# Replace L283-304 (drill-entry + mid-drill cancel) with:
if self.game:
    self.game.fusion_manager.handle_jump_input(self, slime, input_manager)
```
**Anti-patterns:**
- Keeping `Player.fuse`/`unfuse` as compatibility shims (D-13 forbids).
- Leaving the mid-drill cancel block in any form (Pitfall 5).
- Leaving the provisional `event_bus.emit("drill_block_break", tx=tx, ty=ty)` at L482 (Pitfall 2 — would double-emit).

---

### `src/entities/slime.py` (entity, optionally MODIFIED)

**Analog:** self (post-Phase-31.5).

**Recommendation per RESEARCH (matches CONTEXT Discretion #8):** **NO CHANGE** for Phase 32 baseline. ChargeController calls `slime.refill(ACCELERATED_REGEN_RATE)` per frame under the accelerated-regen condition. No new method required.

**Existing API to reuse unchanged** (`src/entities/slime.py:217-223`):
```python
def refill(self, amount):
    self.juice = min(self.max_juice, self.juice + amount)

def consume(self, amount):
    if debug.god_infinite_juice:
        return
    self.juice = max(0.0, self.juice - amount)
```
**What to copy:** call signatures stay identical. ChargeController uses `slime.refill(rate_per_frame)`; FusionManager uses `slime.consume(MANA_SHIELD_COST)`.
**What to change:** nothing (recommended). If planner prefers the alternative (`slime.set_regen_mode("accelerated")`), add a method to slime.py with mode field; that path is acceptable per D-Discretion #8.

**Anti-patterns:**
- Rewriting `consume` / `refill` / `dissipate` / `recall` (RESEARCH § Don't Hand-Roll: "Already correct; Phase 32 wraps them, doesn't rewrite them.").
- Adding a new fusion-state field to Slime — Slime owns `is_fused` / `is_recalling` / `is_dissipated` / `dissipate_timer` and that's the complete fusion-related slime surface. Adding more would create another sync point.

---

### `src/core/save_manager.py` (persistence service, file-I/O)

**Analog:** self.

**Existing save** (`src/core/save_manager.py:19-49`):
```python
@staticmethod
def save(game):
    """Serialize game state to JSON file.

    Saves max_hp/max_juice only (not current values) per D-04:
    player respawns at full HP/juice on load.
    """
    player = game.player
    slime = game.slime
    world = game.world

    data = {
        "version": 1,
        "player": {
            "max_hp": player.max_hp,
            "has_drill": getattr(player, "has_drill", False),
        },
        ...
    }
    path = SaveManager._get_save_path()
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
```
**What to change:**
- Rename `"version": 1` → `"save_version": CURRENT_SAVE_VERSION` (D-21).
- ADD module-level `CURRENT_SAVE_VERSION = 2` (D-23).
- Keep all other fields unchanged.

**Existing load** (`src/core/save_manager.py:51-58`):
```python
@staticmethod
def load():
    """Load game state from JSON file. Returns dict or None if missing."""
    path = SaveManager._get_save_path()
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)
```
**What to change:** add the version check **after** the JSON parse, **after** the existence check (Pitfall 8 — order matters):
```python
@staticmethod
def load():
    path = SaveManager._get_save_path()
    if not os.path.exists(path):
        return None                                        # 1. missing file path: unchanged
    with open(path, "r") as f:
        data = json.load(f)                                # 2. parse JSON
    found = data.get("save_version")
    if found != CURRENT_SAVE_VERSION:
        raise SaveVersionMismatchError(found=found, expected=CURRENT_SAVE_VERSION)
    return data                                            # 3. version OK
```
**SaveVersionMismatchError pattern** (RESEARCH § Save-Version Rejection Mechanism):
```python
class SaveVersionMismatchError(Exception):
    """Raised when load() encounters a save with a save_version mismatch.
    The file is preserved on disk; caller surfaces the user-facing message."""
    def __init__(self, found, expected):
        self.found = found
        self.expected = expected
        super().__init__(
            f"Save file version {found} does not match expected {expected}. "
            f"Save preserved on disk."
        )
```
**What to copy:** D-22/D-23/D-24 verbatim.
**Anti-patterns:**
- Calling `SaveManager.delete()` automatically on version mismatch (D-24 explicit: file preserved on disk).
- Migrating v1 → v2 in code (D-24 explicit: no silent migrate).
- Returning a structured result dict (RESEARCH § Save-Version Rejection — `if data:` truthiness check at `main.py:1249` would silently misroute on result-dict approach).
- Magic number flag (MEMORY): `CURRENT_SAVE_VERSION = 2` is the named constant — do NOT hardcode `2` anywhere in the file beyond the constant definition and the assertion.

---

### `main.py` (Game.__init__ — composition root)

**Analog:** existing event_bus subscriber wiring at `main.py:241-313`.

**Existing wiring pattern** (`main.py:241-275, 285-313`):
```python
# Phase 31 ANIM-06 event subscribers.
# MUST be wired AFTER reset() so self.player and self.particles exist
# (Pitfall 5 in 31-RESEARCH.md).
import math as _math
from src.anim import event_bus as _event_bus
from src.anim.player_anim import DRILL_RECOIL_PAUSE_FRAMES
from src.entities.effects import Particle as _Particle
from src.core import tuning as _tuning

def _on_drill_block_break(tx=None, ty=None, **kw):
    """Phase 31 D-06 + D-16: drill recoil pause + diverging burst."""
    self.player._anim.pause_for(DRILL_RECOIL_PAUSE_FRAMES)
    cx = tx * _tuning.TILE_SIZE + 4
    cy = ty * _tuning.TILE_SIZE + 4
    for i in range(BURST_PARTICLE_COUNT):
        ...

_event_bus.subscribe("drill_block_break", _on_drill_block_break)
...
_event_bus.subscribe("land", _on_land)
_event_bus.subscribe("jump_start", _on_jump_start)
...
_event_bus.subscribe("fuse_start", _on_fuse_start)
```
**What to copy:**
- Late-bound imports at the wiring site (`from src.fusion.manager import FusionManager`).
- `# MUST be wired AFTER reset()` comment idiom — Pitfall 5 (worktree regression / subscriber leak across resets).
- One-block-per-subsystem indentation.

**What to add (RESEARCH § Pattern 3):**
```python
# Phase 32 FUS-04: Fusion subsystem wiring.
# MUST be wired BEFORE the existing event_bus subscriber block so
# Player.handle_input can reach self.game.fusion_manager / self.game.charge_controller
# from frame 0 onward. Both objects survive Game.reset() since reset rebuilds
# Player but not the Game itself (parallel to event_bus subscribers being
# wired once in __init__ per Pitfall 5).
from src.fusion.manager import FusionManager
from src.fusion.charge_controller import ChargeController
from src.fusion.drill_dive import DrillDive
from src.fusion.pogo import Pogo

self.fusion_manager = FusionManager(
    abilities={"drill_dive": DrillDive(), "pogo": Pogo()},
)
self.charge_controller = ChargeController(
    fusion_manager=self.fusion_manager,
)
```

**SaveManager.load() callsite migration** (`main.py:1194-1208`):
```python
# Existing CONTINUE menu path (main.py:1194-1208):
if inp.btnp("confirm"):
    if has_save and self.title_cursor == 0:
        # CONTINUE
        data = SaveManager.load()
        self.reset()
        self.restore_from_save(data)
        self.game_state = "PLAYING"
    elif has_save and self.title_cursor == 1:
        ...
```
**What to change** (D-24 + RESEARCH § Save-Version Rejection — Option A typed exception):
```python
if has_save and self.title_cursor == 0:
    # CONTINUE
    try:
        data = SaveManager.load()
    except SaveVersionMismatchError as e:
        self._show_save_version_error(e)  # planner picks UX (D-25)
        return
    if data is None:
        return  # missing-file (existing path)
    self.reset()
    self.restore_from_save(data)
    self.game_state = "PLAYING"
```

**Death-respawn callsite migration** (`main.py:1244-1256`):
```python
def _update_death(self):
    """Death animation: 30 freeze + 30 fade, then load save (D-15, D-16)."""
    self.death_timer += 1
    total = DEATH_FREEZE_FRAMES + DEATH_FADE_FRAMES
    if self.death_timer >= total:
        data = SaveManager.load()
        if data:
            self.reset()
            self.restore_from_save(data)
            self.game_state = "PLAYING"
        else:
            self.game_state = "TITLE"
            self.title_cursor = 0
```
**What to change:**
```python
def _update_death(self):
    self.death_timer += 1
    total = DEATH_FREEZE_FRAMES + DEATH_FADE_FRAMES
    if self.death_timer >= total:
        try:
            data = SaveManager.load()
        except SaveVersionMismatchError:
            # Death-respawn against an incompatible save: fall back to TITLE.
            # Title screen will surface the rejection on the next CONTINUE attempt.
            self.game_state = "TITLE"
            self.title_cursor = 0
            return
        if data:
            self.reset()
            self.restore_from_save(data)
            self.game_state = "PLAYING"
        else:
            self.game_state = "TITLE"
            self.title_cursor = 0
```

**slime.update callsite** (`main.py:707`): NO CHANGE (D-14a is transparent — `self.player.is_fused` still resolves via the new `@property`).

**Anti-patterns:**
- Wiring fusion_manager / charge_controller inside `Game.reset()` (would re-instantiate per reset and orphan subscribers).
- Wiring inside `Player.__init__` (would lose ref on `Game.reset()` since reset rebuilds player).
- Forgetting to pass `dt=1.0` (or whatever scalar) to `fusion_manager.tick` — pyxel runs at fixed 60fps, so `dt` is constant; planner picks idiom.

---

### `tests/test_fusion.py` (test, unit)

**Analog:** self.

**Existing fuse/unfuse test pattern** (`tests/test_fusion.py:53-81`):
```python
def test_fuse_sets_both_flags():
    """fuse(slime) sets player.is_fused=True AND slime.is_fused=True."""
    player, slime, _ = make_player_and_slime()
    assert not player.is_fused
    assert not slime.is_fused
    player.fuse(slime)
    assert player.is_fused
    assert slime.is_fused


def test_unfuse_clears_both_flags():
    player, slime, _ = make_player_and_slime()
    player.fuse(slime)
    assert player.is_fused and slime.is_fused
    player.unfuse(slime)
    assert not player.is_fused
    assert not slime.is_fused


def test_unfuse_with_dissipate():
    player, slime, _ = make_player_and_slime()
    player.fuse(slime)
    player.unfuse(slime, dissipate=True)
    assert not player.is_fused
    assert not slime.is_fused
    assert slime.is_dissipated
    assert slime.dissipate_timer == SLIME_DISSIPATE_COOLDOWN
```
**What to change** (D-13 deletes `Player.fuse`/`Player.unfuse`):
- `make_player_and_slime` becomes `make_game_player_slime` returning `(game, player, slime, level_map)`. Game holds a `MagicMock`-or-real FusionManager.
- `player.fuse(slime)` → `game.fusion_manager.latch_fuse(slime)` (or whichever name planner picks).
- `player.unfuse(slime)` → `game.fusion_manager.force_exit("test")` (or equivalent).
- `player.unfuse(slime, dissipate=True)` → `game.fusion_manager.force_exit("juice_empty")` (which triggers dissipate per D-07).
- Assertions on `player.is_fused` / `slime.is_fused` stay (8 callsites: L56, 59, 67, 69, 78, 113, plus any added) — `@property` makes them transparent.

**RESEARCH-recommended test additions** (RESEARCH § Validation Architecture, Wave 0 Gaps):
```python
# tests/test_fusion_fsm.py — new file (3-4 tests recommended)
def test_fuse_start_emits_at_latch():
    """fuse_start fires at WINDUP→FUSED 200% latch, NOT at WINDUP begin."""
    ...
def test_drill_requires_full_juice():
    """100% gate: drill_dive.can_activate returns False when juice < max."""
    ...
```
**Anti-patterns:**
- Constructing a real `FusionManager` in unit tests when a `MagicMock` would do (matches `tests/conftest.py:42-56` pattern for slime).
- Forgetting `event_bus.reset()` between tests — autouse fixture in conftest.py:19-24 already handles this.

---

### `tests/test_save_system.py` (test, unit)

**Analog:** self.

**Existing assertions to update** (`tests/test_save_system.py:53-94`):
```python
def test_load_returns_dict(self, save_dir):
    game = _make_game(save_dir)
    SaveManager.save(game)
    data = SaveManager.load()
    assert isinstance(data, dict)
    assert "version" in data           # ← UPDATE TO "save_version"

...

def test_roundtrip_preserves_all_fields(self, save_dir):
    game = _make_game(save_dir)
    SaveManager.save(game)
    data = SaveManager.load()
    assert data["version"] == 1        # ← UPDATE TO data["save_version"] == 2
    ...
```
**What to change:**
- `"version"` → `"save_version"` (1 site at L58).
- `data["version"] == 1` → `data["save_version"] == CURRENT_SAVE_VERSION` (1 site at L87).
- ADD `TestSaveVersionRejection` class with 3 new tests (RESEARCH § Wave 0 Gaps):
  - `test_v1_save_rejected` — write `version: 1` file, assert `SaveVersionMismatchError` raised.
  - `test_missing_version_rejected` — write file with no version field, assert raise.
  - `test_file_preserved_after_rejection` — assert file exists on disk after the exception.

**Anti-patterns:**
- Importing `CURRENT_SAVE_VERSION` as a literal `2` in test code — use the named import (`from src.core.save_manager import CURRENT_SAVE_VERSION`).

---

### `src/anim/player_anim.py` (animation, OPTIONAL — only if D-14 = (b)/(c))

**Analog:** self.

**Decision:** D-14 (a) is **recommended** by RESEARCH. With (a), this file gets **NO CHANGES** — `PLAYER_RULES` lambda at L129 reads `d.state == STATE_DIVING` from the driver, which `Player._update_anim_driver` populates from `self.state`. As long as `Player.state` keeps the `"DIVING"` string set during a drill (planner preserves this in `FusionManager.latch_fuse` or `DrillDive.on_enter` per RESEARCH Open Question #1), no animation changes are required.

**If D-14 = (c) (remove `player.is_fused`):** Then this file might need a FusionManager pointer in `PlayerAnimDriver`. **NOT RECOMMENDED** — RESEARCH § D-14 Trade-off Analysis scores (c) as HIGH risk, 13+ test callsite churn.

---

## Shared Patterns

### Event Bus Emission

**Source:** `src/anim/event_bus.py:17-19` and `src/entities/player.py:71, 79, 482, 496`.

**Apply to:** all new emit sites in `src/fusion/`.

**Idiom:**
```python
from src.anim import event_bus

event_bus.emit("fuse_start")                       # no kwargs
event_bus.emit("fuse_end")                         # no kwargs
event_bus.emit("drill_start")                      # no kwargs (NEW per D-12)
event_bus.emit("drill_block_break", tx=tx, ty=ty)  # CHAR-FOR-CHAR match (Pitfall 1)
event_bus.emit("drill_end")                        # no kwargs (NEW per D-12)
event_bus.emit("drill_impact")                     # no kwargs (existing — keep)
```

**Cross-phase contract:** Phase 31 subscribes by exact string at `main.py:274, 285, 286, 313`. **Do NOT rename** any of `fuse_start`, `fuse_end`, `drill_start`, `drill_block_break`, `drill_end`, `jump_start`, `land`, `drill_impact`.

---

### tuning.* Use-Site Reads (Phase 25 pattern)

**Source:** `src/entities/player.py:43, 112, 293, 295, 386, 389-391, 474, 476, 494` — every drill/juice constant is read at use-site.

**Apply to:** `src/fusion/drill_dive.py`, `src/fusion/manager.py`.

**Idiom:**
```python
from src.core import tuning

# At use site, NOT cached at construction:
self.dy = tuning.DRILL_SPEED
slime.consume(tuning.DRILL_ACTIVATION_COST)
slime.consume(tuning.DRILL_IMPACT_COST)
slime.consume(tuning.DRILL_CRACKED_V_COST)
slime.refill(tuning.DRILL_BLOCK_REFUND)
slime.consume(tuning.MANA_SHIELD_COST)
self.dx = tuning.DRILL_DRIFT_SPEED
```
**Why:** the tuning panel mutates these values live; cached values would freeze. Phase 25 / RESEARCH § code_context confirms: "The refactor moves *where the reads happen* (into `drill_dive.py`) but not *how they happen*."

---

### Module Docstring + Decision Reference

**Source:** `src/anim/anim_clip.py:1-2`, `src/anim/state_machine.py:1-3`, `src/anim/event_bus.py:1-7`.

**Apply to:** all new files in `src/fusion/`.

**Idiom:**
```python
"""Phase 32 FUS-04 [component-purpose]. [Decision-numbers references].

[One paragraph context.]
"""
```
**Examples:**
```python
"""Phase 32 FUS-04 fusion ability protocol (D-09, D-10, D-12).

Defines the FusionAbility typing.Protocol and TickResult dataclass that
abilities (drill_dive, pogo) return from on_tick. CONTEXT D-09 mandates
typing.Protocol over abc.ABC for structural typing.
"""

"""Phase 32 FUS-04 fusion FSM driver (D-07, D-13, D-17).

FusionManager owns FUSED+EXIT state and the active-ability lifecycle.
Per D-13 Player.fuse/unfuse are deleted; this is the new authoritative
fusion state owner.
"""
```

---

### Named-Constants Discipline (MEMORY: no magic numbers)

**Source:** `src/anim/player_anim.py:14-49` (`# --- Named constants (project memory: no magic numbers) ---` banner + UPPER_SNAKE module-level block with inline comments).

**Apply to:** `src/fusion/pogo.py` (D-18 hardcoded), `src/fusion/charge_controller.py` (any internal thresholds), `src/core/save_manager.py` (`CURRENT_SAVE_VERSION`).

**Specific magic numbers to flag if encountered while migrating code:**
| Source line | Literal | Recommended named constant |
|-------------|---------|---------------------------|
| `player.py:122` | `10` (knockback_timer ticks) | `KNOCKBACK_DURATION_FRAMES` (lift to tuning) |
| `player.py:472` | `9` (explosion size px) | `DRILL_EXPLOSION_SIZE_PX` (or use existing `tuning.EXPLOSION_SIZE` if present) |
| `slime.py:74-75` | `RECALL_TRAIL_MAX_LENGTH = 6` | already named — keep (good example) |
| `pogo.py` (new) | bounce velocity, cooldown, damage | `POGO_BOUNCE_VELOCITY`, `POGO_COOLDOWN_FRAMES`, `POGO_DAMAGE`, `POGO_INITIAL_DY` (per D-18) |
| `save_manager.py:31` | `1` (version field value) | `CURRENT_SAVE_VERSION = 2` constant (D-23) |

---

### Reanimator Side-Channel Constraint (MEMORY)

**Source:** Phase 26 D-00b + MEMORY entry `project_reanimator_anim_architecture`.

**Apply to:** all event emissions in `src/fusion/`.

**Idiom:** events are **side-channel** — they inform Phase 31 animation but **do not drive** Phase 32's own FSM. The FusionManager FSM transitions on driver state and ChargeController progress; events are a parallel side-effect.

**Anti-pattern:** Calling `event_bus.emit("fuse_start")` and then in the same code path subscribing to `fuse_start` to drive a FusionManager state change. Events flow OUT of the FSM, never IN.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `src/fusion/protocol.py` (Protocol class only — TickResult HAS an analog) | interface | structural typing | `Grep("Protocol", path="src/")` returned no in-tree matches. Phase 32 introduces `typing.Protocol` for the first time. RESEARCH § Pattern 2 supplies the canonical D-09 shape. |

**Mitigation:** RESEARCH § Pattern 2 + Python `typing.Protocol` stdlib docs cover the new pattern. The shape is locked by D-09 — no design exploration needed.

---

## Cross-Cutting Concerns Summary

| Concern | Source File | Apply To |
|---------|-------------|----------|
| Frozen+slots dataclass | `src/anim/anim_clip.py` | `src/fusion/protocol.py` (TickResult) |
| FSM-shell with tick + per-frame delegation | `src/anim/state_machine.py::AnimFSM` | `src/fusion/manager.py::FusionManager` |
| Module-level singleton wired in `Game.__init__` | `main.py:241-313` (event_bus subscribers) | `main.py` (`fusion_manager`, `charge_controller`) |
| event_bus.emit kwarg signature | `src/anim/event_bus.py` + `player.py:482` | `src/fusion/drill_dive.py`, `src/fusion/manager.py` |
| `tuning.*` use-site reads | `src/entities/player.py:293-295, 474-476, 494` | `src/fusion/drill_dive.py`, `src/fusion/manager.py` |
| MagicMock test fixture for slime | `tests/conftest.py:40-55` | `tests/test_fusion.py` (extend with mock fusion_manager fixture) |
| Typed exception with structured fields | (no in-tree analog — RESEARCH § Save-Version) | `src/core/save_manager.py::SaveVersionMismatchError` |
| @property forward (`self.game is None` short-circuit) | (no in-tree analog — RESEARCH § Pattern 4) | `src/entities/player.py::is_fused` |

---

## Metadata

**Analog search scope:** `src/anim/`, `src/core/`, `src/entities/`, `tests/`, `main.py`.
**Files scanned:** 11 (event_bus, anim_clip, anim_player, player_anim, state_machine, save_manager, input, player, slime, main, conftest, test_fusion, test_save_system).
**Pattern extraction date:** 2026-04-26.
**Source of truth:** `32-CONTEXT.md` D-01..D-25 (locked) + `32-RESEARCH.md` (HIGH confidence) + post-Phase-31.5 codebase verified by direct Read.
**FUSION-DESIGN lock:** `9047b590` — verified present in git history per RESEARCH.
