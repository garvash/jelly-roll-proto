# Phase 32: Fusion Manager + Protocol Refactor - Research

**Researched:** 2026-04-26
**Domain:** Python game-architecture refactor — extracting fusion mechanics from a monolithic `Player` class into a `src/fusion/` package with a `typing.Protocol` boundary, an `ChargeController`+`FusionManager` FSM split, and a save-format version bump with hard-fail rejection
**Confidence:** HIGH (all primary claims verified directly against the post-Phase-31.5 codebase; FUSION-DESIGN locked SHA `9047b59` confirmed present in git via `git log --oneline -1 9047b590`)

## Summary

Phase 32 is a **pure refactor** of the v1.3 fusion + drill-dive mechanics into a new `src/fusion/` package. There is **zero feel intent** in this phase — the v1.3 `_v1.3-reference.json` preset and the FUSION-DESIGN.md Drill-Dive Contract (LOCKED at commit `9047b59`) are the parity targets. The four refactor verbs are:
1. **Move** drill code (`apply_diving_physics`, drill-entry branch, block-break branch, exit conditions, mid-drill jump-cancel deletion) from `src/entities/player.py` into `src/fusion/drill_dive.py`.
2. **Build** a `FusionAbility` `typing.Protocol`, a `FusionManager` (FUSED+EXIT FSM owner), a `ChargeController` (RECALL+WINDUP+tap/hold owner), and a `pogo` null-fusion sibling.
3. **Bump** the save format from `version: 1` to `save_version: 2` with hard-fail rejection on mismatch.
4. **Add** the unfused-DOWN+SPACE pogo branch (net-new code; v1.3 has no pogo today).

Two consolidations happen along the way: the drill-entry juice gate tightens from `>0` to `=100%` (aligning with the existing charge-to-fuse gate at `player.py:275`), and the mid-drill jump-cancel at `player.py:298-302` is deleted with no replacement. Phase 31's animation subscribers are downstream consumers — `fuse_start`, `drill_block_break`, `land`, `jump_start` events MUST keep their exact names through the refactor or animation breaks silently.

**Primary recommendation:** Execute as **5 internal waves** — Protocol/skeleton → ChargeController+FusionManager → drill_dive migration + pogo sibling → save-version bump → integration audit + parity smoke test. Use **D-14 option (a) `@property` forwarding** on `player.is_fused` (lowest churn, 8 callsites including main.py and overlays.py). Use **`SaveVersionMismatchError`** typed exception for rejection (caller already wraps `SaveManager.load()` in two distinct paths in `main.py` — typed exceptions are cleaner than result dicts for that shape). Use a **frozen `@dataclass` `TickResult`** as the `on_tick` return value (planner discretion per CONTEXT, but the codebase already uses frozen dataclasses for `AnimClip`).

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Code-strip prerequisite (Phase 31.5):**
- **D-01:** Cut-ability code-strip ships as dedicated Phase 31.5 (now COMPLETE per STATE.md and `31.5-PHASE-VERIFICATION.md` verdict PASS).
- **D-02:** Phase 31.5 scope was full-coverage (player.py + slime.py + schema + presets + input.py + save_manager.py + tests). [VERIFIED: STATE.md `last_activity: Phase 31.5 cut-ability-code-strip complete`]
- **D-03:** Cut tuning groups (`ram`, `charge_shot`, `boost`, `bubble_shield`) deleted entirely from `physics-schema.json`. [VERIFIED: `31.5-PHASE-VERIFICATION.md` § B.2 — schema retains 16 tuning groups, no cut groups]
- **D-04:** `dash` removed from `_ACTION_MAP` in `src/core/input.py`. [VERIFIED: `src/core/input.py:4-13` shows 8 actions, no `dash`]
- **D-05:** Save-format cut-flag drop (has_dash, has_shield, has_shield_t2, has_boost) happened in Phase 31.5. [VERIFIED: `src/core/save_manager.py:30-45` — only `max_hp` + `has_drill` in player block]

**Component boundaries — ChargeController / FusionManager:**
- **D-06:** ChargeController owns RECALL + WINDUP + tap/hold disambiguation, accelerated regen application, free-cancel paths, emits `fuse_start` at WINDUP→FUSED latch.
- **D-07:** FusionManager owns FUSED + EXIT, tracks `active_ability`, per-frame `tick(player, slime, dt)`, mana-shield cost application, EXIT handling (juice=0 → `slime.dissipate()` → 240-frame cooldown), emits `fuse_end`.
- **D-08:** Handoff method-shape is planner discretion; the responsibility split is fixed.

**FusionAbility Protocol shape:**
- **D-09:** Explicit `typing.Protocol` with `id: str`, `requires_fused: bool`, `can_activate`, `on_enter`, `on_tick`, `on_exit`, `on_event`. (Exact `TickResult` shape is planner discretion.)
- **D-10:** `apply_diving_physics` MOVES (not copies) into `src/fusion/drill_dive.py::on_tick`. Player no longer dispatches a DIVING branch.
- **D-11:** `on_event` is how abilities react to side-channel events (consistent with Phase 26 reanimator-side-channel constraint).
- **D-12:** Ability emits `drill_start` from `on_enter`, `drill_block_break` from block-break detection, `drill_end` from `on_exit`.

**Player ↔ FusionManager API:**
- **D-13:** `Player.fuse(slime)` and `Player.unfuse(slime, dissipate)` are **DELETED** — no shim.
- **D-14:** `player.is_fused` derivation strategy is planner discretion: (a) `@property` forward, (b) FusionManager mirrors flag, (c) remove attribute and migrate every consumer.
- **D-15:** Every fuse-entry and fuse-exit path is audited during the refactor.

**Pogo placement and dispatch:**
- **D-16:** `src/fusion/pogo.py` implements the FusionAbility Protocol with `requires_fused = False` (null-fusion sibling).
- **D-17:** `FusionManager.handle_jump_input(player, slime, input_manager)` is the single dispatcher for DOWN+SPACE airborne input.
- **D-18:** Pogo values are hardcoded named constants in `src/fusion/pogo.py` (no tuning group, no panel, no preset entry in Phase 32).
- **D-19:** Pogo bounces on enemies + breakables only; pure solid = land; takes damage on enemies; breaks softs (no juice refund — pogo is free).
- **D-20:** Pogo is free — no juice cost, no cooldown in v2.0 baseline.

**Save format versioning:**
- **D-21:** Existing `"version": 1` is **renamed** to `"save_version": 2`.
- **D-22:** `save_version` is an integer schema version; comparison is simple equality.
- **D-23:** `CURRENT_SAVE_VERSION = 2` defined at module level in `src/core/save_manager.py`.
- **D-24:** Mismatched/missing `save_version` → hard fail with clear message; file preserved on disk; no silent delete.
- **D-25:** User-facing error surface (menu text, button labels) is planner discretion.

### Claude's Discretion

- Exact `TickResult` shape (named tuple / dataclass / dict / tagged union). **This research recommends frozen `@dataclass`** (rationale § Architecture Patterns).
- Method names for latch-fuse / force-exit on FusionManager.
- D-14 `player.is_fused` derivation. **This research recommends (a) `@property`** (rationale § D-14 Trade-off Analysis).
- Whether pogo reuses drill's soft-destructible passthrough code or duplicates a minimal version.
- Exact pogo constant names (`POGO_BOUNCE_VELOCITY` vs `POGO_IMPULSE` etc.).
- Save-version rejection: typed exception vs. structured result dict. **This research recommends `SaveVersionMismatchError`** (rationale § Save-Version Rejection Mechanism).
- Phase 32 testing scope (smoke test only is acceptable per FUSION-DESIGN D-28; pytest characterization is optional).
- ChargeController-complete signaling shape (callback / polled flag / direct observation).
- Accelerated regen implementation layer.

### Deferred Ideas (OUT OF SCOPE)

- Accelerated-regen rate tuning → Phase 33.
- Tap/hold threshold retune to ~8 frames → Phase 33.
- Pogo values in tuning/presets → Phase 33.
- Drill i-frames → Phase 33 (currently NONE per v1.3).
- Manual mid-drill unfuse → permanently stripped (FUSION-DESIGN re-lock 2026-04-20).
- Five cut abilities (ram, hold, charge_shot, bubble_shield, boost) → post-prototype.
- CRACKED_H gates → become dead gates; level-design follow-up.
- Second-pass overlay visual polish → Phase 31 + Phase 33.
- Save migration path (v1→v2) → not built.
- Save-file UX polish (delete-save affordance, etc.) → Phase 35 or later.
- V button v2.0 rebinding → post-prototype.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **FUS-04** | `src/fusion/` package exists with `FusionAbility` Protocol, `FusionManager`, `ChargeController`, and a `drill_dive` module; old fusion code (including five cut-ability remnants) removed from `player.py`. | § Standard Stack lists the explicit file map; § Call Site Inventory enumerates every fuse/unfuse/drill site to remove from player.py post-31.5. |
| **FUS-05** | Regression playthrough confirms FUS-03 (drill-dive contract) behaves identically to v1.3 after refactor — drill velocity, per-block costs, exit conditions all parity. | § FUSION-DESIGN.md Drill-Dive Contract is the parity bar. § Validation Architecture ties REQ-IDs to smoke checklist + optional pytest. § Common Pitfalls flags every regression vector (mid-drill cancel removal, 100% gate consolidation, mana-shield routing). |
| **FUS-07** | Save files written by v2.0 contain a `save_version: 2` field; old v1.3 saves rejected with a clear message instead of silently corrupting state. | § Save-Version Rejection Mechanism analyses typed-exception vs. result-dict; § Validation Architecture defines the test for v1 save rejection. |

## Architectural Responsibility Map

This is a single-tier desktop game (Pyxel) — no client/server split. The "tiers" are **architectural layers** within the game process. The refactor's architectural value is moving fusion off the entity tier and into a dedicated subsystem tier.

| Capability | Primary Layer | Secondary Layer | Rationale |
|------------|--------------|-----------------|-----------|
| Fusion FSM (RECALL→WINDUP→FUSED→EXIT) | `src/fusion/` (new subsystem) | — | This is the refactor's whole reason: take the FSM off `Player`, where it currently couples with movement, and put it in a system that owns it cleanly. [VERIFIED: 32-CONTEXT D-06/D-07/D-13] |
| Per-ability physics (drill velocity clamp, block-break detection, exit on solid) | `src/fusion/drill_dive.py` | `src/level/map.py` (read-only — `get_destructible_at`, `remove_tile`) | D-10 is explicit: physics MOVES into the ability. Player calls `FusionManager.tick()` and the ability does the work. [VERIFIED: 32-CONTEXT D-10] |
| Tap/hold disambiguation + RECALL state | `src/fusion/charge_controller.py` | `src/core/input.py` (read-only — `was_tap`, `hold_frames`) | D-06 splits ChargeController out as the pre-manager. Input primitives stay in `src/core/input.py`. [VERIFIED: 32-CONTEXT D-06] |
| DOWN+SPACE airborne dispatch (pogo unfused / drill fused) | `src/fusion/manager.py::handle_jump_input` | `src/entities/player.py::handle_input` (calls into manager — no `is_fused` branch in Player) | D-17 is the single-entry-point invariant. [VERIFIED: 32-CONTEXT D-17] |
| Mana shield (fused damage drains juice) | `src/fusion/manager.py` (new home) | `src/entities/player.py::take_damage` (calls into manager) | Currently at `player.py:111-123`. D-07 explicitly puts mana-shield-cost application on FusionManager. [VERIFIED: 32-CONTEXT D-07] |
| `slime.juice` state, `consume()`, `refill()`, `dissipate()`, `recall()` | `src/entities/slime.py` (UNCHANGED) | — | Phase 32 wraps these in the new Manager/Controller surface but does not rewrite slime state. [VERIFIED: 32-CONTEXT § code_context Reusable Assets] |
| Save serialization + version check | `src/core/save_manager.py` | `main.py::Game._update_title_input` (load callsite), `main.py::Game._update_death` (death-respawn load callsite) | `CURRENT_SAVE_VERSION` co-located in save_manager per D-23. Caller surfaces the error. [VERIFIED: D-23, `main.py:1197`, `main.py:1249`] |
| `player.is_fused` flag (consumed by anim driver, overlays, slime.update) | `src/entities/player.py` (`@property` reading FusionManager — option a) | `src/fusion/manager.py` (authoritative source) | See § D-14 Trade-off Analysis. 8 read-callsites identified across main.py + overlays.py + tests; option (a) is lowest-churn. |
| Animation subscribers on `fuse_start`/`drill_block_break`/`land`/`jump_start` | `main.py::Game.__init__` (UNCHANGED — wired Phase 31) | — | These subscribers MUST keep working unchanged across the refactor. Phase 31 already hoisted them to `Game.__init__` (Pitfall 5). [VERIFIED: `main.py:274,285,286,313`] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `typing.Protocol` | stdlib (Python 3.13.11 confirmed) | Structural typing for `FusionAbility` | D-09 mandates explicit Protocol. Stdlib since 3.8. `runtime_checkable` decorator available. [VERIFIED: `python -c "import typing; print(hasattr(typing, 'Protocol'), hasattr(typing, 'runtime_checkable'))"` → `True True`] |
| `dataclasses` | stdlib | `TickResult`, `PlayerAnimDriver` precedent | Already used by `AnimClip` (frozen+slots) and `PlayerAnimDriver` (slots). Idiomatic. [VERIFIED: `src/anim/anim_clip.py:6-11`, `src/anim/player_anim.py:52-63`] |
| `pyxel` | already installed | Game runtime | No version bump needed for Phase 32. [VERIFIED: existing imports throughout] |
| `pytest` | 9.0.2 | Optional characterization tests | If planner opts for FSM-transition pytest, pytest is the established test runner. [VERIFIED: `python -c "import pytest; print(pytest.__version__)"` → `9.0.2`] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `unittest.mock.MagicMock` | stdlib | Mocking pyxel + level_map in characterization tests | Existing pattern in `tests/conftest.py` and `tests/test_input_remap.py` |
| `enum.Enum` (or string constants) | stdlib | FSM state names if the planner wants type-checked transitions | Planner discretion — current player.py uses bare strings (`"DIVING"`, `"FALLING"`); consistency suggests strings, but `Enum` is the safer choice in a new package |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `typing.Protocol` (D-09 locked) | `abc.ABC` + abstract methods | ABCs require explicit inheritance; Protocols are structural. CONTEXT locks Protocol — no choice to make. |
| Frozen dataclass `TickResult` | NamedTuple, dict, plain dataclass, tagged union (`Union[Continue, Exit, ...]`) | NamedTuple is fine but less extensible (no defaults, no methods); dict loses type info; tagged union is heaviest but most expressive. Frozen dataclass matches `AnimClip` precedent and is light. |
| Typed exception `SaveVersionMismatchError` | Result dict `{"error": "version_mismatch", "found": 1, "expected": 2}` | Result dict needs every caller to do an `if "error" in data:` check; current callers expect `data` to be `dict | None`. Typed exception is one `try/except` at each callsite. |
| `@property` forward (D-14a) | FusionManager-mirrors-attribute (D-14b) or remove entirely (D-14c) | See § D-14 Trade-off Analysis — (a) is lowest churn given 8 callsites including external file types (overlays.py, main.py, tests). |

**Installation:** No new packages. All standard-library + already-installed.

**Version verification:** Standard library — no `pip install` step. Python 3.13.11 ([VERIFIED: `python --version`]). All Protocol features (including `runtime_checkable`) stable since 3.8.

## Architecture Patterns

### System Architecture Diagram

```
                         ┌──────────────────────┐
                         │   Player.update()    │
                         │ (orchestrator only)  │
                         └──────────┬───────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
       ┌──────────────┐   ┌──────────────────┐   ┌──────────────┐
       │ handle_input │   │  charge_ctrl     │   │ fusion_mgr   │
       │ (movement +  │──►│  .handle_z_input │   │ .tick(p,s,dt)│
       │  jump only)  │   │  (RECALL,WINDUP, │   │ (FUSED+EXIT  │
       │              │   │   tap/hold)      │   │  dispatch)   │
       └──────┬───────┘   └────────┬─────────┘   └──────┬───────┘
              │                    │                    │
              │                    │  fuse_start emit   │
              │                    │  at 200% latch     │ on_tick →
              │ DOWN+SPACE         │                    │ active_ability
              │ in air             ▼                    ▼
              │              ┌──────────────────────────────────┐
              │              │  FusionManager.is_fused (auth.)  │
              │              └──────────────────────────────────┘
              │                    ▲                    │
              │  handle_jump_input │                    │
              ▼                                         ▼
       ┌──────────────────────────────────┐    ┌─────────────────┐
       │ FusionManager.handle_jump_input  │    │ Active ability  │
       │ (single dispatch point)          │    │ (drill_dive OR  │
       │                                  │    │  pogo)          │
       │ if is_fused: → drill_dive        │    │                 │
       │ else:        → pogo              │    │ on_tick returns │
       └────┬───────────────────┬─────────┘    │   TickResult    │
            │                   │              │ (dx,dy,exit?)   │
            ▼                   ▼              └────────┬────────┘
       ┌─────────┐         ┌─────────┐                  │
       │ pogo.py │         │drill_   │                  │
       │ (free,  │         │dive.py  │                  │
       │ bounces)│         │(juice $)│                  │
       └─────────┘         └─────────┘                  │
                                                        │
                              drill_start /             │ via FusionManager
                              drill_block_break /       │
                              drill_end emits ──────────┤
                                                        ▼
                                                ┌──────────────┐
                                                │ event_bus    │
                                                │ subscribers  │
                                                │ (anim, HUD)  │
                                                │ unchanged    │
                                                └──────────────┘
```

**Data flow:**
1. Per frame, `Player.update()` calls `input_manager.update()`, then `handle_input()` (movement + grounded-jump only — Z-button + DOWN+SPACE-air migrate out).
2. `handle_input()` delegates Z-button to `ChargeController.handle_z_input(player, slime, input_manager)` → ChargeController runs the RECALL→WINDUP FSM, calls `slime.recall()` / `slime.refill(accelerated_rate)`, and on second-pass-200%-latch calls `FusionManager.latch_fuse(slime)` and emits `fuse_start`.
3. `handle_input()` delegates DOWN+SPACE-air to `FusionManager.handle_jump_input(player, slime, input_manager)` → manager checks `is_fused` and dispatches to `drill_dive.can_activate()+on_enter()` (fused) or `pogo.can_activate()+on_enter()` (unfused).
4. `Player.update()` calls `FusionManager.tick(self, slime, dt)` which calls `active_ability.on_tick()` — drill physics happens here, no `Player.apply_diving_physics`. The ability returns a `TickResult` describing dx/dy intent + optional exit signal.
5. On block-break (drill), the ability emits `drill_block_break` via event_bus → existing subscribers in `main.py:274` (drill-recoil pause + diverging burst) keep firing unchanged.
6. On juice=0 inside FUSED, FusionManager emits `fuse_end`, calls `slime.dissipate()`, sets `EXIT` state, and the 240-frame cooldown ticks down via `slime.update_dissipation`.
7. On solid-terrain landing (drill exit a), the ability's `on_exit` emits `drill_end` and `drill_impact`; FusionManager calls `unfuse(dissipate=False)` equivalent (slime reforms next to player, no dissipate).

### Component Responsibilities

| File (NEW) | Purpose | Key APIs |
|------------|---------|----------|
| `src/fusion/__init__.py` | Package marker; may re-export FusionAbility, FusionManager, ChargeController for `from src.fusion import …` | (none) |
| `src/fusion/protocol.py` | `FusionAbility` `typing.Protocol` (D-09), `TickResult` dataclass | `class FusionAbility(Protocol): ...`, `@dataclass(frozen=True) class TickResult: dx: float, dy: float, request_exit: bool, exit_reason: str \| None` |
| `src/fusion/manager.py` | FusionManager — owns FUSED+EXIT, `active_ability`, `tick`, `handle_jump_input`, `latch_fuse`, `force_exit`, mana-shield application, dissipate cooldown handling | `class FusionManager`, `is_fused: bool`, `tick(player, slime, dt)`, `handle_jump_input(player, slime, input_manager)`, `latch_fuse(slime)`, `force_exit(reason)`, `apply_fused_damage(slime)` |
| `src/fusion/charge_controller.py` | ChargeController — owns RECALL+WINDUP, tap/hold disambiguation, accelerated regen condition, free-cancel paths, emits `fuse_start` at WINDUP→FUSED latch | `class ChargeController`, `handle_z_input(player, slime, input_manager)`, internal `state: "IDLE"|"RECALL"|"WINDUP"`, `windup_progress: float`, second-pass `200% target` |
| `src/fusion/drill_dive.py` | DrillDive ability implementing FusionAbility — `apply_diving_physics` MOVES here as `on_tick`; block-break branch and exit conditions live here; emits `drill_start`/`drill_block_break`/`drill_end` | `class DrillDive: id="drill_dive"; requires_fused=True`, `on_enter`, `on_tick`, `on_exit`, `can_activate` |
| `src/fusion/pogo.py` | Pogo null-fusion ability — DOWN+SPACE airborne unfused, free, bounces on enemies+breakables, lands on solid; hardcoded constants | `class Pogo: id="pogo"; requires_fused=False`, hardcoded `POGO_*` constants |

| File (MODIFIED) | What Changes |
|-----------------|--------------|
| `src/entities/player.py` | DELETE `fuse()` (L59-71), `unfuse()` (L73-84), `apply_diving_physics()` (L385-398), the drill-entry branch in `handle_input` (L283-296), the mid-drill jump-cancel block (L298-302), the block-break branch in `move_and_collide` (L463-484), the solid-terrain drill-exit branch in `move_and_collide` (L493-498), the mana-shield branch in `take_damage` (L110-124), and `is_charging_recall` state (L50). ADD `@property is_fused` (D-14a) reading `self.game.fusion_manager.is_fused`. Replace Z-input block in `handle_input` (L194-281) with a single delegation `self.game.charge_controller.handle_z_input(self, slime, input_manager)`. Replace DOWN+SPACE-air block (L283-303) with `self.game.fusion_manager.handle_jump_input(self, slime, input_manager)`. Move the `if self.state == "DIVING": apply_diving_physics(slime)` branch (L97-99) — Player calls `self.game.fusion_manager.tick(self, slime, dt)` once per frame regardless of state; the ability owns DIVING physics. |
| `src/entities/slime.py` | LIKELY UNCHANGED for Phase 32 baseline. Optional: add `set_regen_mode("accelerated"\|"passive"\|"off")` if planner picks the slime-mode-flag implementation for accelerated regen (D-08 planner discretion). Default recommendation: ChargeController calls `slime.refill(ACCELERATED_REGEN_RATE)` per frame under the condition — no slime change. |
| `src/core/save_manager.py` | ADD `CURRENT_SAVE_VERSION = 2` module constant. ADD `class SaveVersionMismatchError(Exception): found, expected`. RENAME `"version": 1` → `"save_version": 2` in `save()` payload. ADD version check in `load()` that raises `SaveVersionMismatchError` when `data.get("save_version") != CURRENT_SAVE_VERSION`. File preserved on disk (no auto-delete). |
| `main.py` (Game class) | ADD `self.charge_controller = ChargeController(...)` and `self.fusion_manager = FusionManager(...)` in `Game.__init__` (similar to existing event_bus subscriber wiring). UPDATE `_update_title_input` (L1197) and `_update_death` (L1249) to wrap `SaveManager.load()` in `try/except SaveVersionMismatchError` and surface a user-facing rejection message (planner picks UX details per D-25). UPDATE `slime.update(...)` callsite (L707) — if D-14a: no change (`player.is_fused` still works). UPDATE the off-screen slime recovery check (L710) similarly. |
| `src/core/overlays.py` | If D-14a: NO CHANGE (reads `s.is_fused` on slime, not player; slime side stays). The existing `slime.is_fused` set inside `Player.fuse()`/`unfuse()` becomes a `FusionManager.latch_fuse()`/`force_exit()` responsibility — the new code MUST still write `slime.is_fused = True/False` to keep overlay rendering correct. [VERIFIED: `src/core/overlays.py:259, 295` reads `s.is_fused`] |
| `tests/test_fusion.py` | Existing 11 test methods drive `player.fuse(slime)` / `player.unfuse(slime)` directly — these MUST migrate to `game.fusion_manager.latch_fuse(slime)` / `game.fusion_manager.force_exit("test")`. **8 callsites in this file alone** (test_fusion.py:58, 66, 68, 76, 77, 87, 103, 166). |
| `tests/test_event_bus.py` | Two callsites (L256, L265, L269) drive `p.fuse(mock_slime)` / `p.unfuse(mock_slime)` to verify `fuse_start`/`fuse_end` emits. Migrate to FusionManager invocation. |
| `tests/test_save_system.py` | Existing tests assert `data["version"] == 1` (L87) and `"version" in data` (L58). UPDATE to `data["save_version"] == 2`. ADD a new test: writing a `version: 1` file then calling `load()` raises `SaveVersionMismatchError`. |
| `tests/conftest.py` | `mock_slime.is_fused = False` (L50) stays — `slime.is_fused` is unchanged. |
| `tests/test_input_remap.py` | `mock_slime.is_fused = False` (L41) stays. The test exercises the `state == "DIVING"` outcome of `Player.handle_input` — after refactor, this assertion still holds because FusionManager sets `state = "DIVING"` via the active ability (or the planner can keep `Player.state` mirroring as a transitional shim). [PROVISIONAL — depends on planner's DIVING-state ownership decision] |

### Pattern 1: Frozen Dataclass for `TickResult`

**What:** Use a frozen `@dataclass` with explicit fields for what `on_tick` returns to FusionManager.
**When to use:** Whenever the ability needs to communicate dx/dy intent and an optional exit request to FusionManager.
**Recommended shape:**
```python
# src/fusion/protocol.py
from dataclasses import dataclass
from typing import Protocol, Optional

@dataclass(frozen=True, slots=True)
class TickResult:
    """Per-frame intent returned by FusionAbility.on_tick.

    Phase 32: ability owns physics (D-10). This dataclass carries the
    dx/dy intent back to FusionManager and signals optional exit.
    """
    dx: float = 0.0
    dy: float = 0.0
    request_exit: bool = False
    exit_reason: Optional[str] = None  # "solid_landing" | "juice_empty" | None
```
**Source:** Frozen `@dataclass` precedent verified in `src/anim/anim_clip.py:6-11` (`AnimClip(frozen=True, slots=True)`). [VERIFIED: codebase grep]

**Why over alternatives:**
- **NamedTuple:** less extensible (no method support, no defaults pre-3.6.1).
- **dict:** loses type info; key typos go silent.
- **Tagged union (`Union[Continue, ExitSolid, ExitJuiceEmpty]`):** maximum expressiveness but heavier; planner can use this if `TickResult` ever needs to carry exit-specific payloads.

### Pattern 2: `typing.Protocol` for FusionAbility

**What:** Use a `Protocol` (D-09) to define the FusionAbility interface — abilities don't inherit; they conform structurally.
**When to use:** D-09 mandates this. Use as-is.
**Example:**
```python
# src/fusion/protocol.py
from typing import Protocol, runtime_checkable

@runtime_checkable
class FusionAbility(Protocol):
    """Interface for fusion abilities (drill_dive, pogo). Per CONTEXT D-09.

    `requires_fused = False` for null-fusion abilities like pogo (D-16).
    """
    id: str
    requires_fused: bool

    def can_activate(self, player, slime) -> bool: ...
    def on_enter(self, player, slime, context: dict) -> None: ...
    def on_tick(self, player, slime, dt: float) -> TickResult: ...
    def on_exit(self, player, slime, reason: str) -> None: ...
    def on_event(self, name: str, data: dict) -> None: ...
```
**Source:** [CITED: `typing.Protocol` Python 3 docs]; D-09 verbatim from CONTEXT.md.

### Pattern 3: Module-Level Singleton (FusionManager + ChargeController on Game)

**What:** One instance of FusionManager and ChargeController per game session, owned by `Game` (parallel to how `event_bus` is module-level singleton, but with explicit ownership).
**When to use:** D-07 + D-08 imply this — FusionManager holds state across frames and is read by Player + main.py.
**Wiring example:**
```python
# main.py Game.__init__
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
# Player accesses via self.game.fusion_manager (Player already has self.game ref)
```
**Source:** Existing pattern — `Game.__init__` wires event_bus subscribers per Pitfall 5 (`main.py:274,285,286,313`). FusionManager+ChargeController join this cohort.

### Pattern 4: `@property` Forward for `player.is_fused` (D-14a)

**What:** Keep `player.is_fused` as a read-only property that returns `self.game.fusion_manager.is_fused`. No setter.
**When to use:** Recommended over D-14b (mirror) and D-14c (delete) — see § D-14 Trade-off Analysis.
**Example:**
```python
# src/entities/player.py
@property
def is_fused(self) -> bool:
    """Phase 32 D-14a: derived from FusionManager. Read-only; FusionManager
    is the single authoritative source for fused state."""
    if self.game is None:
        return False  # tests construct Player without game (test_fusion.py)
    return self.game.fusion_manager.is_fused
```
**Source:** Inherited from D-14a; pattern is standard Python idiom.
**Note on test fixtures:** `tests/test_fusion.py:48` constructs `Player(px, py, level_map)` without a `game` argument (default None). The property must handle `self.game is None` gracefully or the entire test file breaks. The property approach handles this cleanly with a `None` short-circuit; D-14b/c would force every test to construct a mock game.

### Anti-Patterns to Avoid

- **Two-owner pattern for `is_fused`:** D-13 explicitly forbids keeping `Player.fuse/unfuse` as shims. The CONTEXT calls out two-owner state as a pitfall (Q4 of Discussion Log Component Boundaries: "Keep; Player and FusionManager share is_fused state — Two owners.").
- **Calling `play("jump")` style commanded animation:** Phase 26 D-00 (Reanimator-style) — gameplay never commands animation. Phase 32 events are SIDE-CHANNEL, they don't drive Phase 32's own FSM.
- **Renaming `fuse_start`, `fuse_end`, `drill_block_break`, `land`, or `jump_start`:** These are Phase 31's animation contract. Any rename = silent break. [VERIFIED: `main.py:274,285,286,313` subscribers; `31-CONTEXT.md` line 144-152 event wiring map]
- **Re-emitting events from new sites without removing old emit lines:** Especially the provisional `drill_block_break` bridge at `player.py:482` — Phase 31 added it as a bridge during Phase 32's gestation; Phase 32 MUST move emission to `drill_dive.py::on_tick` and DELETE the player.py bridge in the same commit. Double-emission would fire animation twice.
- **Reintroducing the mid-drill jump-cancel:** FUSION-DESIGN locked decision: drill cannot be aborted mid-flight. The `player.py:298-302` block must be deleted with no replacement. Specifically the four lines:
  ```python
  if self.state == "DIVING":
      if input_manager.btnp("jump"):
          self.state = "FALLING"
          self.unfuse(slime)
      return
  ```
  go away entirely (no Z-hold variant, no replacement input).
- **Editing `_v1.3-reference.json`:** Frozen baseline. Phase 32 reads it; never writes it. [VERIFIED: 32-CONTEXT line 144-145]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Pub-sub event dispatch | Custom callback list, observer pattern | Existing `src/anim/event_bus.py` (`subscribe`, `emit`, `reset`) | Already wired through Phase 26; Phase 31 subscribers depend on it. [VERIFIED: `src/anim/event_bus.py:13-24`] |
| Tap/hold disambiguation | Custom frame counters, `if pyxel.btn` chains | `input_manager.was_tap(action, threshold)` and `input_manager.hold_frames(action)` | Established primitives at `src/core/input.py:51-61`; ChargeController uses these directly per D-06. [VERIFIED: code] |
| Slime juice state machine | Re-implement consume/refill/dissipate/recall | `slime.consume()`, `slime.refill()`, `slime.dissipate()`, `slime.recall()`, `slime.update_recall()`, `slime.update_dissipation()` | Already correct; Phase 32 wraps them, doesn't rewrite them. [VERIFIED: `src/entities/slime.py:46-98, 217-223`] |
| JSON save persistence | Custom serializer, manual file I/O | `SaveManager.save()`, `SaveManager.load()`, `SaveManager.exists()`, `SaveManager.delete()` | Phase 32 only adds the version check; doesn't rewrite persistence. [VERIFIED: `src/core/save_manager.py`] |
| Structural typing for ability interface | Manual `hasattr` checks, abstract base class | `typing.Protocol` (`@runtime_checkable` if runtime checks needed) | Stdlib since 3.8; D-09 mandates it. |
| Animation-only frame pause (Phase 31's drill-recoil) | Custom counter | `player._anim.pause_for(n)` (added in Phase 31 D-06) | Already exists; Phase 32's `drill_dive.py` block-break branch should call it via `event_bus.emit("drill_block_break", tx=tx, ty=ty)` — the existing subscriber in `main.py:259` does the pause. Don't pause directly from drill_dive.py; let the event bus do it. [VERIFIED: `src/anim/anim_player.py:20-27`, `main.py:258-272`] |

**Key insight:** Phase 32 is plumbing, not new mechanics. Every new file is a boundary; the underlying behaviors already work. The risk is in WHERE state moves, not WHAT state does. Resist any urge to "improve" slime, juice, or input mechanics — that's Phase 33's authority.

## D-14 Trade-off Analysis: `player.is_fused` Derivation

CONTEXT D-14 leaves three options. This section enumerates callsites, scores each option, and recommends.

### Callsite Inventory (post-31.5)

**Reads `player.is_fused` (must keep working):**
1. `main.py:707` — `self.slime.update(self.player.x, ..., self.player.is_fused)` — passes is_fused into slime.update for fused-merge handling.
2. `main.py:710` — `if (not self.player.is_fused and ...):` — off-screen slime recovery condition.
3. `tests/test_fusion.py:56,59,69,78,113` — assertions on `player.is_fused`.
4. `tests/test_overlays.py:47` — sets `self.is_fused = False` on a mock player class.

**Reads `slime.is_fused` (separate from player flag — UNCHANGED):**
5. `src/core/overlays.py:259` — `if not s.is_fused and not s.is_dissipated:` — hitbox overlay visibility.
6. `src/core/overlays.py:295` — same condition for velocity overlay.
7. `tests/conftest.py:50` — `slime.is_fused = False` mock setup.
8. `tests/test_input_remap.py:41` — same mock setup.
9. `tests/test_slime.py:24` — `assert not slime.is_fused`.
10. `tests/test_fusion.py:57,60,67,70,79` — assertions on `slime.is_fused`.

**Writes `player.is_fused` (currently — to remove with fuse/unfuse deletion):**
11. `src/entities/player.py:39` — `self.is_fused = False` in `__init__`.
12. `src/entities/player.py:61` — `self.is_fused = True` in `fuse()`.
13. `src/entities/player.py:76` — `self.is_fused = False` in `unfuse()`.
14. `src/entities/player.py:134` — `self.is_fused = False` in `take_damage` (mana-shield-empty path).

**Total `player.is_fused` read sites:** 4 in production code (main.py x2, overlays.py reads `slime.is_fused` not player), plus 5 in test_fusion.py + test_overlays.py. The slime.is_fused side is independent and stays.

### Option Scoring

| Option | Description | Read-callsite churn | Test-callsite churn | Risk |
|--------|-------------|---------------------|---------------------|------|
| **(a) `@property` forward** | `player.is_fused` becomes a read-only property returning `self.game.fusion_manager.is_fused` | 0 (transparent to readers) | 0 (assertions still pass; reads are idempotent) | LOW — must handle `self.game is None` for test fixtures |
| **(b) FusionManager mirrors** | FusionManager writes `player.is_fused = True/False` each frame; the attribute is still a Player field | 0 | 0 | MEDIUM — two writers in the new world (FusionManager AND any leftover `take_damage` reset); easy to forget; introduces sync bugs |
| **(c) Remove attribute entirely** | Delete `player.is_fused` field; every reader reads `game.fusion_manager.is_fused` | 4+ in production (main.py x2, plus any new) | 13+ in tests (test_fusion.py x5, test_overlays.py, etc.) | HIGH — every test fixture needs a mock game with mock fusion_manager attribute; 13+ touch points; any miss = NameError at runtime |

### Recommendation

**Use option (a) — `@property` forward.** Lowest churn, highest test stability. The implementation is ~5 lines:

```python
@property
def is_fused(self) -> bool:
    """Phase 32 D-14a: derived from FusionManager. Single authoritative source.
    Returns False when game is None (test fixtures construct Player without game)."""
    return self.game is not None and self.game.fusion_manager.is_fused
```

Migrate the 4 writes (`__init__`, `fuse`, `unfuse`, `take_damage`) by:
- `__init__:39` — DELETE the `self.is_fused = False` line entirely (the property derives it).
- `fuse:61` / `unfuse:76` — DELETE both methods entirely (D-13).
- `take_damage:134` — replace `self.is_fused = False` with `self.game.fusion_manager.force_exit("damage_break")`.

`slime.is_fused` is a separate flag with separate consumers (overlays, slime.update). Keep as-is. The new FusionManager methods (`latch_fuse` / `force_exit`) take responsibility for setting `slime.is_fused = True/False` in their bodies — currently this is done inside `Player.fuse`/`unfuse`.

## Save-Version Rejection Mechanism

CONTEXT D-24 leaves "raise typed exception OR return structured result dict" to planner. This section analyzes both against the existing call sites.

### Existing `SaveManager.load()` callers (post-31.5)

[VERIFIED: grep + Read]

| Site | Code | Current Handling |
|------|------|-----------------|
| `main.py:1197` | `data = SaveManager.load(); self.reset(); self.restore_from_save(data)` | Assumes `data` is dict; no None-check before `restore_from_save`; called from CONTINUE menu path. |
| `main.py:1249` | `data = SaveManager.load(); if data: self.reset(); self.restore_from_save(data)` | Has `if data:` guard for missing-file case (load returns None). Called from death-respawn path. |
| `tests/test_save_system.py:56,61,85,99,110` | `data = SaveManager.load(); assert isinstance(data, dict); ...` or `assert SaveManager.load() is None` | Test asserts dict-or-None contract. |

### Option A — Typed Exception (recommended)

```python
# src/core/save_manager.py
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

CURRENT_SAVE_VERSION = 2

@staticmethod
def load():
    path = SaveManager._get_save_path()
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        data = json.load(f)
    found = data.get("save_version")
    if found != CURRENT_SAVE_VERSION:
        raise SaveVersionMismatchError(found=found, expected=CURRENT_SAVE_VERSION)
    return data
```

Caller migration is minimal:
```python
# main.py:1197 (CONTINUE menu path)
try:
    data = SaveManager.load()
except SaveVersionMismatchError as e:
    self._show_save_version_error(e)  # planner picks UX (D-25)
    return
if data is None:
    return  # missing-file (existing path)
self.reset()
self.restore_from_save(data)
```

**Pros:** No churn for missing-file callers (None-return path unchanged). Test assertions for the success case unchanged. Type-safe error info (`e.found`, `e.expected`).

**Cons:** Adds a `try/except` at each callsite (2 sites in main.py). New tests need to assert the exception is raised on v1 save.

### Option B — Structured Result Dict

```python
# load() returns either the data dict OR an error dict like:
# {"error": "version_mismatch", "found": 1, "expected": 2}
```

**Pros:** No exception flow control; linear caller code.

**Cons:** Every caller must inspect for `"error"` key; current callers (main.py:1197) don't check. Existing `if data:` truthiness check (main.py:1249) accidentally treats an error dict as success. **Both production callers would have new bugs.**

### Recommendation

**Option A — Typed `SaveVersionMismatchError`.** Cleaner caller migration, leverages existing None-return contract for the orthogonal missing-file case, and the existing `if data:` guards continue to work for missing-file. Two callsites need a new `try/except`; both are in `main.py` and both are localized (single-screen flows). Total added code: ~8 lines per callsite, two callsites.

## Runtime State Inventory

This is a refactor / rename phase. Each category answered explicitly per § Step 2.5.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| **Stored data** | The save file (`tuning.SAVE_FILE` — typically `save.json` at project root). Contains `"version": 1` field today. **No databases, no Mem0, no ChromaDB.** | **Data migration is NOT required and NOT performed.** D-21/D-24 lock the design: v1 saves are REJECTED with a clear message; the file stays on disk. The user can back it up or delete manually. No silent migrate, no silent delete. |
| **Live service config** | None. This is a desktop game — no n8n, no Datadog, no Tailscale, no external services. | None. |
| **OS-registered state** | None. Game runs from `python main.py`; no Task Scheduler entries, no pm2, no systemd, no launchd. | None. |
| **Secrets / env vars** | None — verified by grep for `.env`, `os.environ`, `os.getenv` in `src/`. The codebase has no secrets surface; gameplay is fully local. | None. |
| **Build artifacts / installed packages** | No compiled binaries; no pip eggs; no Docker images. The project is a Python-source game. | None. |

**The canonical question check:** *After every file in the repo is updated for Phase 32, what runtime systems still have the old string cached/stored/registered?*

**Answer:** **One** — the user's existing `save.json` file with `"version": 1`. **This is the intended rejection target.** Phase 32 does not edit it. The save-version-mismatch path is the design.

## Common Pitfalls

### Pitfall 1: Renaming an event Phase 31 subscribes to

**What goes wrong:** Phase 31 subscribed `fuse_start`, `land`, `jump_start`, `drill_block_break` in `Game.__init__` ([VERIFIED: `main.py:274,285,286,313`]). If Phase 32's new emit sites use a different name (e.g., `fusion_started` instead of `fuse_start`), the subscriber never fires — animation breaks silently.
**Why it happens:** The subscribers don't error on a missing event; `event_bus.emit("fusion_started")` silently does nothing if no subscriber listens. There is no event-name registry.
**How to avoid:** Treat the event names as a fixed contract:
- `fuse_start` — emitted from `ChargeController.handle_z_input` at WINDUP→FUSED latch (D-06 final bullet).
- `fuse_end` — emitted from `FusionManager.force_exit` (or equivalent) on EXIT (D-07 final bullet).
- `drill_start` / `drill_block_break` / `drill_end` — emitted from `drill_dive.py::on_enter`, mid-`on_tick`, and `on_exit` respectively (D-12).
- `jump_start` / `land` / `direction_change` / `jump_released` / `damaged` / `death` / `wall_touch` / `wall_jump` / `drill_impact` / `spit` / `left_ground` / `jump_press_airborne` — UNCHANGED. Verified emit sites at `player.py:127, 155, 180, 319, 355, 370, 378, 383, 417, 490, 496, 511`.
**Warning signs:** Animation looks identical-to-pre-refactor for normal jumping/landing but stops responding on fuse-flash or drill-recoil → check the new emit site names char-for-char against `main.py:274, 313`.

### Pitfall 2: Double-emission of `drill_block_break`

**What goes wrong:** The Phase 31 PROVISIONAL emit at `player.py:478-482` is documented as "Phase 32 owns the canonical emit site … MUST remove this bridge during its refactor." If Phase 32 adds emission inside `drill_dive.py::on_tick` but forgets to delete the player.py bridge, both emit and Phase 31's drill-recoil pause fires twice per block-break.
**Why it happens:** Code archaeology — the bridge looks innocuous; CONTEXT explicitly flags it must be removed.
**How to avoid:** In Phase 32's player.py edit task, explicitly grep for `event_bus.emit("drill_block_break"` and ensure it's gone after the edit. The single emit lives in `drill_dive.py`.
**Warning signs:** Drill-recoil animation pauses twice (frame counter freezes for 6 ticks instead of 3, since two `pause_for(3)` calls additively stack per `anim_player.py:20-27`).

### Pitfall 3: Test fixtures that construct `Player(x, y, level_map)` without a `game`

**What goes wrong:** `tests/test_fusion.py:48` creates `Player(px, py, level_map)` — game defaults to None. After Phase 32, the `is_fused` property would dereference `self.game.fusion_manager` and AttributeError on every test in the file (11 test methods).
**Why it happens:** Test fixtures pre-date the FusionManager world.
**How to avoid:** EITHER (a) make the property tolerate `self.game is None` (returning False — recommended), OR (b) update `make_player_and_slime` in test_fusion.py to construct a mock Game with a mock FusionManager. Option (a) is one-line; option (b) is per-test-helper migration. Recommend (a) for stability.
**Warning signs:** `pytest tests/test_fusion.py` ALL fail at the first `player.is_fused` access.

### Pitfall 4: Forgetting to set `slime.is_fused` from the new FusionManager methods

**What goes wrong:** `Player.fuse(slime)` currently sets BOTH `player.is_fused = True` AND `slime.is_fused = True` (player.py:61-62). If Phase 32's new `FusionManager.latch_fuse(slime)` only updates internal manager state and forgets `slime.is_fused = True`, then:
- `overlays.py:259` keeps drawing the slime hitbox even though the player is fused (visual bug).
- `slime.update(...)` early-returns on `is_fused` (snap-to-player logic) — without the flag, slime keeps following with its own AI even while merged into player.
**Why it happens:** The two flags look like duplicate state but serve different code paths.
**How to avoid:** `FusionManager.latch_fuse(slime)` must set `slime.is_fused = True`; `force_exit` must set `slime.is_fused = False`. Already part of the migration but easy to forget.
**Warning signs:** Slime sprite stays visible during fusion, OR slime keeps following via its history queue while fused.

### Pitfall 5: Mid-drill jump-cancel residue

**What goes wrong:** The `if self.state == "DIVING": if input_manager.btnp("jump"): self.state = "FALLING"; self.unfuse(slime); ... return` block at `player.py:298-302` MUST go entirely. If even the surrounding `if self.state == "DIVING": return` shell remains (without the jump cancel), it shadows correct dispatch through FusionManager.
**Why it happens:** The block looks like state-management housekeeping when read in isolation.
**How to avoid:** Delete `player.py:298-302` (5 lines) cleanly in the same commit that introduces FusionManager.tick. Replace with `# Drill physics now owned by src/fusion/drill_dive.py per Phase 32 D-10` if a comment helps.
**Warning signs:** Drill stops on first SPACE press; OR drill physics never executes (FusionManager.tick never called from Player.update).

### Pitfall 6: `is_charging_recall` orphaned state

**What goes wrong:** `Player.is_charging_recall` (player.py:50) is set/cleared in 3 places (player.py:268, 279, 69). After ChargeController takes over, this state belongs in ChargeController, not Player. If the field stays on Player and nobody writes it, downstream conditions like `if self.is_charging_recall and slime.is_recalling:` (player.py:272-275) silently never fire.
**Why it happens:** Migration cherry-picks the visible methods (`fuse/unfuse`) but leaves the state attributes.
**How to avoid:** Inventory `is_charging_recall` writes/reads when migrating handle_input's Z-block to ChargeController. Move the state into ChargeController as `self._charging = True/False`. Delete the Player attribute entirely.
**Warning signs:** Z-tap-during-recall fires a spit projectile (because the cancel-recall branch never triggers), OR slime never auto-fuses (because the arrived-and-100% branch never sees `is_charging_recall == True`).

### Pitfall 7: V-button "dash" residue check skipped

**What goes wrong:** Phase 31.5-PHASE-VERIFICATION.md flags one outstanding leftover at `main.py:497-499` — `Item("DASH_PICKUP")` legacy tile-marker fallback. If Phase 32 modifies main.py extensively for FusionManager wiring without cleaning this up, the "clean base" intent erodes.
**Why it happens:** The tile-marker fallback is dead in practice (no LDtk level uses tile (3,0)) but the literal string survives.
**How to avoid:** Phase 32's first plan should include a small hygiene step deleting `main.py:497-499` and `assets/physics-schema.json:38` (`SHIELD_T2_DRAIN_REDUCTION` orphan key). Both are documented in `31.5-PHASE-VERIFICATION.md` § Section C.1, C.2.
**Warning signs:** Phase 31.5 verifier flagged these as "dead in practice but contradicts CONTEXT D-04 intent."

### Pitfall 8: Save-version check executes on missing file

**What goes wrong:** If the version check is `data.get("save_version") != 2`, and `data` is None (file missing), `data.get` raises AttributeError. The current `load()` returns None for missing files (intentional — caller checks `if data:`). The version check must apply ONLY when a file exists and was successfully parsed.
**Why it happens:** Sequencing — file-existence check is first, JSON parse is second, version check is third. Easy to put the check in the wrong order.
**How to avoid:** Structure as:
```python
if not os.path.exists(path):
    return None              # 1. missing file path: unchanged
data = json.load(f)          # 2. parse JSON
if data.get("save_version") != CURRENT_SAVE_VERSION:
    raise SaveVersionMismatchError(...)
return data                  # 3. version OK
```
**Warning signs:** First-time-game launch (no save file) crashes instead of showing TITLE menu.

## Code Examples

Verified patterns from the existing codebase + recommended new patterns:

### Existing `slime.consume` / `slime.refill` (DO NOT REWRITE)
```python
# src/entities/slime.py:217-223 — already correct
def refill(self, amount):
    self.juice = min(self.max_juice, self.juice + amount)

def consume(self, amount):
    if debug.god_infinite_juice:
        return
    self.juice = max(0.0, self.juice - amount)
```
**Source:** `src/entities/slime.py:217-223` [VERIFIED]
**Use:** Phase 32 calls these from FusionManager (mana shield) and drill_dive.py (impact, block-break refund/cost). No need to wrap or extend.

### Existing event emission pattern (FOLLOW IDIOM)
```python
# src/anim/event_bus.py
def emit(event_name: str, **kwargs) -> None:
    for cb in _subscribers.get(event_name, ()):
        cb(**kwargs)
```
**Source:** `src/anim/event_bus.py:17-19` [VERIFIED]
**Use:** Inside `drill_dive.py::on_tick` block-break branch:
```python
event_bus.emit("drill_block_break", tx=tx, ty=ty)
```
Match the kwargs signature of the existing provisional emit at `player.py:482` for subscriber compatibility.

### Recommended FusionManager.tick skeleton
```python
# src/fusion/manager.py
class FusionManager:
    def __init__(self, abilities: dict[str, FusionAbility]):
        self._abilities = abilities
        self._active: FusionAbility | None = None
        self.is_fused: bool = False
        self._exit_cooldown_frames: int = 0  # SLIME_DISSIPATE_COOLDOWN ticks down here

    def tick(self, player, slime, dt: float) -> None:
        """Per-frame: dispatch active ability, handle EXIT cooldown, mana shield reset."""
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
        """Single dispatch point for DOWN+SPACE airborne input (D-17)."""
        if not (input_manager.btnp("jump") and input_manager.btn("down")
                and not player.is_grounded):
            return
        target_id = "drill_dive" if self.is_fused else "pogo"
        ability = self._abilities[target_id]
        if ability.can_activate(player, slime):
            self._active = ability
            ability.on_enter(player, slime, context={})
```
**Source:** Synthesized from CONTEXT D-07 + D-17 + Pattern 3 above. [PROVISIONAL — exact method signatures are planner's call.]

### Recommended save-version check
```python
# src/core/save_manager.py
CURRENT_SAVE_VERSION = 2

class SaveVersionMismatchError(Exception):
    def __init__(self, found, expected):
        self.found = found
        self.expected = expected
        super().__init__(
            f"Save version {found} != expected {expected}. File preserved."
        )

@staticmethod
def save(game):
    # ... existing player/slime/world dict construction ...
    data = {
        "save_version": CURRENT_SAVE_VERSION,  # was "version": 1
        "player": {...},
        # ...
    }
    # ... existing write logic ...

@staticmethod
def load():
    path = SaveManager._get_save_path()
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        data = json.load(f)
    found = data.get("save_version")
    if found != CURRENT_SAVE_VERSION:
        raise SaveVersionMismatchError(found=found, expected=CURRENT_SAVE_VERSION)
    return data
```
**Source:** Synthesized from D-21/D-22/D-23/D-24. Follows existing `SaveManager` static-method idiom.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Monolithic `Player.update()` with state branches for every ability (RAMMING, DASHING, BOOSTING, CHARGING_SHOT, DIVING) | Single ability owner: cut abilities deleted in 31.5; DIVING migrates to `src/fusion/` in 32 | Phase 31.5 + 32 | Player code shrinks ~30%; ability boundaries enforced via Protocol |
| Drill activation gated on `slime.juice > 0` | Drill activation gated on `slime.juice == slime.max_juice` (100%) | Phase 32 | Consolidates with charge-to-fuse gate already at 100%. Design primitive "I need 1 more juice for this puzzle" becomes felt. |
| Mid-drill jump-cancel allowed (player.py:298-302) | Removed entirely; drill cannot be aborted mid-flight | Phase 32 (per FUSION-DESIGN re-lock 2026-04-20) | Commitment is the point. Manual exit was stripped from design before Phase 32 spec. |
| `version: 1` flat key in save | `save_version: 2` integer schema version | Phase 32 D-21 | Old saves rejected on load; save file preserved on disk. |
| Ability methods on Player (`fuse`, `unfuse`, `apply_diving_physics`, etc.) | Methods on `FusionManager` + ability modules; Player calls into the manager | Phase 32 | Player.py loses ~150 lines; package structure visible to readers. |

**Deprecated/outdated:**
- Five v1.1 cut abilities (Slime Ram, Directional Hold, Charge Shot, Bubble Shield, Slime Boost) — stripped in Phase 31.5; not coming back in v2.0. [VERIFIED: 31.5-PHASE-VERIFICATION.md verdict PASS]
- The v1.3 `version: 1` save format — unsupported in v2.0; file preserved for hypothetical future migration; rejected on load.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The 8 read-callsites identified for `player.is_fused` are exhaustive | § D-14 Trade-off | If a missed callsite exists (e.g., a HUD module), option (a)'s zero-churn claim is wrong but still works (property still returns correct value). Low impact. |
| A2 | The `try/except SaveVersionMismatchError` migration only requires touching `main.py:1197` and `main.py:1249` | § Save-Version Rejection | If a third callsite exists outside main.py and tests, it would silently propagate the exception. LOW — verified via grep `SaveManager.load`. |
| A3 | `tests/test_input_remap.py::TestDrillDiveOnDownSpace` will continue to pass after FusionManager owns DIVING-state setting (assuming planner keeps `Player.state = "DIVING"` mirror) | § Component Responsibilities | If FusionManager doesn't set `Player.state = "DIVING"` and the test expects it, the test breaks. The test asserts `p.state == "DIVING"` directly — planner needs to either preserve this assignment in the new flow or update the test. |
| A4 | Phase 31's drill-recoil pause fires on the `drill_block_break` event regardless of which file emits it — i.e., emission relocation does not change subscriber behavior | § Pitfall 1 | Verified: subscriber at `main.py:259-274` reads only the kwargs (`tx, ty`); it has no check on emit source. Moving emission from `player.py:482` to `drill_dive.py::on_tick` is transparent IF kwargs match. |
| A5 | Recommended use of frozen `@dataclass` for `TickResult` is consistent with the codebase | § Standard Stack | Verified: `src/anim/anim_clip.py:6-11` uses `frozen=True, slots=True`. |
| A6 | The `provisional drill_block_break bridge` documented at player.py:478-482 is the ONLY duplicate emit risk | § Pitfall 2 | Moderate — verified by grep `event_bus.emit("drill_block_break"` returns only that one line. |

**No assumptions tagged `[ASSUMED]`** in factual claims about file contents, line numbers, or library availability — those are all verified by Read or Grep tool output. Assumptions above are about FUTURE Phase 32 implementation choices that the planner finalizes.

## Open Questions

1. **Where does `Player.state = "DIVING"` get set in the new flow?**
   - What we know: Currently `player.py:291` sets `state = "DIVING"` in the drill-entry branch. Phase 32 deletes that branch.
   - What's unclear: Does FusionManager keep writing `player.state = "DIVING"` (so existing animation rules in `player_anim.py:129` `(lambda d: d.state == STATE_DIVING, "drill_spin")` still match), or does it use a manager-side ability-id and rewire the animation rule to read from the manager?
   - Recommendation: Keep `player.state = "DIVING"` writes in `FusionManager.latch_fuse`/active-ability `on_enter` (drill_dive only) — avoids touching `player_anim.py` and `tests/test_input_remap.py`. Pogo's `on_enter` should NOT set `state = "DIVING"` (pogo is not drilling — keep state as `"FALLING"` or similar).

2. **Does ChargeController accept the slime+player at construction time, or per-call?**
   - What we know: Player is per-game-session (re-created on `Game.reset()`); ChargeController is per-session (also re-created).
   - What's unclear: Per-call signature `handle_z_input(player, slime, input_manager)` is one option; another is `ChargeController(player, slime)` and `handle_z_input(input_manager)`.
   - Recommendation: Per-call. ChargeController stays stateless about who it's controlling — easier to reset on `Game.reset()`.

3. **How does FusionManager know the `SLIME_DISSIPATE_COOLDOWN` value?**
   - What we know: It's `tuning.SLIME_DISSIPATE_COOLDOWN = 240` (frames; verified in `_v1.3-reference.json` slime group).
   - What's unclear: FusionManager reads `tuning.SLIME_DISSIPATE_COOLDOWN` at use-site, OR slime owns the cooldown timer (it already does — `slime.dissipate_timer` at slime.py:82).
   - Recommendation: Slime already owns the cooldown timer via `slime.dissipate()` + `slime.update_dissipation()`. FusionManager just calls `slime.dissipate()` on EXIT(juice=0) and lets the existing slime FSM tick the cooldown. No new state in FusionManager beyond what's in `slime.is_dissipated`/`slime.dissipate_timer`.

4. **Should the planner author pytest characterization tests?**
   - What we know: FUSION-DESIGN D-28 says "smoke test is sufficient; pytest optional." 32-CONTEXT § Claude's Discretion confirms this is planner's call.
   - What's unclear: How much regression coverage do we need to feel confident drill-dive parity holds?
   - Recommendation: **Yes — author 4-6 characterization tests** for the highest-risk paths: drill-entry juice-cost, block-break refund, CRACKED_V cost, drill-impact-cost, dissipate-on-juice-empty. The optional pytest is cheap (2-4 hours) and doubles as Phase 33's regression safety net. See § Validation Architecture for specifics.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.x with `typing.Protocol` + `runtime_checkable` | `src/fusion/protocol.py` | ✓ | 3.13.11 | — |
| `pyxel` | runtime imports across game | ✓ | (already installed; tests use MagicMock per `conftest.py:13`) | — |
| `pytest` | optional characterization tests | ✓ | 9.0.2 | If not available: smoke-test-only acceptance per FUSION-DESIGN D-28 |
| Git access to commit `9047b59` | FUSION-DESIGN.md lock verification | ✓ | confirmed via `git log --oneline -1 9047b590` | None — Phase 32 cannot start without this commit visible. **Status: PASS.** |

**Missing dependencies with no fallback:** None.
**Missing dependencies with fallback:** None.

## Validation Architecture

> Nyquist validation is enabled (`workflow.nyquist_validation: true` in `.planning/config.json`).

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` 9.0.2 |
| Config file | `pytest.ini` if present in repo (planner verifies); otherwise pytest defaults |
| Quick run command | `python -m pytest tests/test_fusion.py tests/test_save_system.py tests/test_input_remap.py tests/test_event_bus.py -x` |
| Full suite command | `python -m pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| **FUS-04** | `src/fusion/` package exists with Protocol/Manager/Controller/drill_dive | smoke | `python -c "from src.fusion import FusionManager, ChargeController; from src.fusion.drill_dive import DrillDive; from src.fusion.pogo import Pogo; from src.fusion.protocol import FusionAbility, TickResult"` | ❌ Wave 0 |
| **FUS-04** | `Player.fuse` and `Player.unfuse` deleted | grep | `! grep -q 'def fuse\|def unfuse' src/entities/player.py` (must return 0 lines) | ✓ shell |
| **FUS-04** | `is_charging_recall` removed from Player | grep | `! grep -q 'is_charging_recall' src/entities/player.py` | ✓ shell |
| **FUS-04** | `apply_diving_physics` removed from Player | grep | `! grep -q 'apply_diving_physics' src/entities/player.py` | ✓ shell |
| **FUS-04** | Mid-drill jump-cancel block deleted | grep | `! grep -nE 'state == "DIVING".*btnp\("jump"\)' src/entities/player.py` | ✓ shell |
| **FUS-05** | DrillDive activates on DOWN+SPACE airborne, fused, juice=100% | unit (existing test, updated) | `pytest tests/test_input_remap.py::TestDrillDiveOnDownSpace::test_drill_dive_on_down_space -x` | ✓ exists, needs update |
| **FUS-05** | DrillDive entry consumes `DRILL_ACTIVATION_COST = 5.0` juice | unit | `pytest tests/test_drill_dive_parity.py::test_activation_cost -x` | ❌ Wave 0 (optional pytest) |
| **FUS-05** | DrillDive impact on solid consumes `DRILL_IMPACT_COST = 20.0` juice; emits `drill_impact` + `drill_end` | unit + smoke | `pytest tests/test_drill_dive_parity.py::test_impact_exit -x`, OR manual smoke per FUSION-DESIGN Acceptance Checklist | ❌ Wave 0 (optional) |
| **FUS-05** | DrillDive block-break (soft) refunds `+15.0` juice; emits `drill_block_break` | unit | `pytest tests/test_drill_dive_parity.py::test_soft_block_refund -x` | ❌ Wave 0 (optional) |
| **FUS-05** | DrillDive CRACKED_V break consumes `20.0` juice (not refund) | unit | `pytest tests/test_drill_dive_parity.py::test_cracked_v_cost -x` | ❌ Wave 0 (optional) |
| **FUS-05** | DrillDive juice→0 mid-flight triggers `slime.dissipate()` + 240-frame cooldown; emits `fuse_end` + `drill_end` | unit | `pytest tests/test_drill_dive_parity.py::test_juice_empty_dissipate -x` | ❌ Wave 0 (optional) |
| **FUS-05** | NO mid-drill cancel input — pressing SPACE during drill does nothing | unit | `pytest tests/test_drill_dive_parity.py::test_no_mid_drill_cancel -x` (drives DIVING state, presses jump, asserts state stays DIVING) | ❌ Wave 0 (optional) |
| **FUS-05** | Mana shield: fused damage drains `MANA_SHIELD_COST = 20.0` juice | unit (existing test, updated) | `pytest tests/test_fusion.py::test_mana_shield_consumes_juice -x` | ✓ exists, needs FusionManager migration |
| **FUS-05** | Mana shield juice→0 triggers `slime.dissipate()` | unit (existing test, updated) | `pytest tests/test_fusion.py::test_mana_shield_dissipates_on_empty -x` | ✓ exists |
| **FUS-05** | Pogo activates on DOWN+SPACE airborne unfused | unit | `pytest tests/test_pogo.py::test_pogo_activates_unfused -x` | ❌ Wave 0 |
| **FUS-05** | Pogo bounces on enemy contact, lands on solid | manual smoke (Phase 32 has no enemies in test fixtures) | manual playtest in gym | manual |
| **FUS-05** | `fuse_start` emits at 200% second-pass latch (NOT at WINDUP begin, NOT at RECALL) | unit | `pytest tests/test_fusion_fsm.py::test_fuse_start_emits_at_latch -x` | ❌ Wave 0 (optional) |
| **FUS-05** | 100% gate: drill activation with juice=99% fails; with 100% succeeds | unit | `pytest tests/test_fusion_fsm.py::test_drill_requires_full_juice -x` | ❌ Wave 0 |
| **FUS-07** | Save written by v2.0 contains `save_version: 2` (no `version` key) | unit (existing test, updated) | `pytest tests/test_save_system.py::TestSaveRoundTrip::test_roundtrip_preserves_all_fields -x` | ✓ exists, assertion needs update L87 |
| **FUS-07** | `SaveManager.load()` raises `SaveVersionMismatchError` when file has `version: 1` | unit | `pytest tests/test_save_system.py::TestSaveVersionRejection::test_v1_save_rejected -x` | ❌ Wave 0 |
| **FUS-07** | `SaveManager.load()` raises `SaveVersionMismatchError` when `save_version` field is missing | unit | `pytest tests/test_save_system.py::TestSaveVersionRejection::test_missing_version_rejected -x` | ❌ Wave 0 |
| **FUS-07** | After failed load, save file is preserved on disk (not deleted) | unit | `pytest tests/test_save_system.py::TestSaveVersionRejection::test_file_preserved_after_rejection -x` | ❌ Wave 0 |
| **FUS-07** | Title-screen CONTINUE flow shows error UX on version mismatch (not crash) | manual smoke | manual playtest with planted v1 save | manual |
| **FUS-04 / FUS-05** | Boot smoke: `python main.py` runs to title without crash | smoke | `timeout 5 python main.py; test $? -eq 124` (clean timeout = booted, ran 5s, didn't raise) | ✓ shell |
| **FUS-05 (acceptance)** | FUSION-DESIGN.md § Acceptance Checklist all items pass on manual playtest | manual | go through `.planning/FUSION-DESIGN.md` § Input Model / FSM / Drill-Dive checklists | docs |

### Sampling Rate

- **Per task commit:** `python -m pytest tests/test_fusion.py tests/test_save_system.py tests/test_input_remap.py -x` (~3-5 seconds; covers the most-touched files).
- **Per wave merge:** `python -m pytest` full suite (~25s baseline per `31.5-PHASE-VERIFICATION.md` Gate 4).
- **Phase gate:** Full suite green + manual smoke against the FUSION-DESIGN.md § Acceptance Checklist before `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] `tests/test_drill_dive_parity.py` — covers FUS-05 (drill behavioral parity: activation cost, impact cost, soft-block refund, CRACKED_V cost, juice-empty dissipate, no-mid-drill-cancel). **6 tests recommended; optional per FUSION-DESIGN D-28 but high regression value.**
- [ ] `tests/test_fusion_fsm.py` — covers FUS-04/FUS-05 (FSM transitions: 100% gate, fuse_start latch position, free-cancel returns slime to follow without juice loss). **3-4 tests recommended.**
- [ ] `tests/test_pogo.py` — covers FUS-04/FUS-05 (pogo activation unfused, free, hardcoded constants present). **2-3 tests recommended.**
- [ ] `tests/test_save_system.py::TestSaveVersionRejection` — covers FUS-07 (rejection of `version: 1` saves; rejection of missing-field saves; file preservation). **3 new tests added to existing file.**
- [ ] Update `tests/test_fusion.py` — 11 existing tests need migration from `player.fuse(slime)` to `game.fusion_manager.latch_fuse(slime)` (or whichever method name planner picks). Mock-game fixture extension required.
- [ ] Update `tests/test_event_bus.py` — 3 callsites (L256, L265, L269) need `p.fuse(mock_slime)` → FusionManager invocation.
- [ ] Update `tests/test_save_system.py:87` — assertion `data["version"] == 1` → `data["save_version"] == 2`.

*If the planner opts for smoke-test-only per FUSION-DESIGN D-28, only the existing-test updates are mandatory. The optional Wave 0 test files (drill_dive_parity, fusion_fsm, pogo) are recommended-but-skippable.*

## Project Constraints (from CLAUDE.md)

**`./CLAUDE.md` does not exist** — no project-level enforced directives beyond the inherited memory entries. Treat MEMORY.md feedback (auto-loaded above) as authoritative:

| Memory Entry | Phase 32 Application |
|--------------|----------------------|
| Avoid magic numbers — use named constants | Every Phase 32 numeric literal (POGO_BOUNCE_VELOCITY, POGO_COOLDOWN_FRAMES, ACCELERATED_REGEN_RATE, CURRENT_SAVE_VERSION, etc.) MUST be a named constant. Co-located in its owning module per Phase 31 precedent (`player_anim.py` constant block). |
| Block gate hierarchy (soft=spit/kick, cracked-V=drill, cracked-H=ram, goo-mold=late-game) | Drill is the CRACKED_V opener. CRACKED_H becomes a dead gate post-31.5 (no opener) — flagged for level-design follow-up; not Phase 32's concern. |
| Entity schema contract — `assets/entity-schema.json` shared with pml-to-ldtk converter | No entity-schema changes in Phase 32. Confirmed: 31.5 verified entity-schema is clean (no DashPickup/etc.). |
| Door event-gated system — "event" action + event_id replaces tile ID 4 boss gates | No door changes in Phase 32. |
| MAP-02 outdated — Z-Spiral obsolete, rooms come from pml-to-ldtk pipeline | No map changes in Phase 32. |
| Door target_room unnecessary | No door changes. |
| Reanimator-style anim architecture — events are side-channel | **CRITICAL** for Phase 32. Events emitted by `drill_dive.py` and `manager.py` (`fuse_start`, `fuse_end`, `drill_start`, `drill_block_break`, `drill_end`) are SIDE-CHANNEL — they inform Phase 31 animation but DO NOT drive Phase 32's own FSM. The FSM transitions on driver state and ChargeController progress; events are emitted as a parallel side-effect. |
| Worktree merges cause regressions | Not directly applicable — Phase 32 is a single phase; no worktree spawning anticipated. If parallelization is used, diff-and-restore discipline still applies. |
| Push before worktree execution | Same as above — applies if Phase 32 plans use worktrees. |

## Threat Model Surface

Phase 32 has **one** externally-influenced input: the save-file JSON. All other state is internal to the game process.

### STRIDE for `SaveManager.load()`

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Type confusion (`save_version` is a string `"2"` not int `2`) | Tampering | Strict equality check `data.get("save_version") != CURRENT_SAVE_VERSION` (int) — string `"2"` is not equal to int 2; falls through to rejection. Consider `isinstance(found, int)` as defense-in-depth. |
| KeyError on missing `save_version` field (v1 saves) | DoS via crash | Use `.get("save_version")` not `data["save_version"]`. Returns None for missing key; None != 2 → rejected via SaveVersionMismatchError (intended path). |
| Malformed JSON (truncated, invalid UTF-8, etc.) | DoS via crash | `json.load(f)` raises `json.JSONDecodeError`. Currently uncaught at all `SaveManager.load()` callsites. **Out of scope for Phase 32** (existing behavior — same pre/post refactor) but flag as Phase 35+ hygiene. |
| File path injection (e.g., user-supplied filename) | Tampering / Information Disclosure | NOT applicable — `_get_save_path()` resolves to a fixed `tuning.SAVE_FILE` relative to project root. No user input controls the filename. [VERIFIED: `src/core/save_manager.py:11-17`] |
| JSON content carries malicious code (e.g., `__import__`-style payload) | Code Execution | NOT applicable — `json.load` parses to dict/list/scalar primitives only; no code paths execute strings from save data. |
| Save file written by attacker on disk (e.g., shared system) | Tampering | Out of scope for prototype. Future hardening would add HMAC signing, but the v2.0 prototype is single-user local game with trust on the local filesystem. |

### Applicable ASVS Categories

Per .planning/config.json `security_enforcement` is not explicitly set; default is enabled. For a desktop game with no network surface, only V5 applies non-trivially.

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No login system. |
| V3 Session Management | no | No sessions. |
| V4 Access Control | no | Single-user local game. |
| V5 Input Validation | yes | Save-file JSON: validate `save_version` type and value; reject on mismatch (D-24). Malformed-JSON case is out of scope but flagged. |
| V6 Cryptography | no | Prototype does not sign saves. Post-prototype hardening optional. |
| V7 Error Handling | yes | `SaveVersionMismatchError` carries no exploitable info; user-facing message is hardcoded. Acceptable. |

**Threat model verdict for Phase 32:** Save-version mismatch is a **planned and documented** rejection path, not an attack surface. The malformed-JSON case is the only hardening gap and is preserved-as-is from pre-refactor (out of Phase 32 scope per planner discretion).

## Sources

### Primary (HIGH confidence)
- `.planning/phases/32-fusion-manager-protocol-refactor/32-CONTEXT.md` — locked decisions D-01..D-25
- `.planning/FUSION-DESIGN.md` — LOCKED at commit `9047b590` (verified present in git history via `git log --oneline -1 9047b590`)
- `.planning/STATE.md` — Phase 31.5 status confirmed complete
- `.planning/ROADMAP.md` § Phase 32 — goal + success criteria
- `src/entities/player.py` — full file Read
- `src/entities/slime.py` — full file Read
- `src/core/save_manager.py` — full file Read
- `src/core/input.py` — full file Read
- `src/anim/event_bus.py` — full file Read
- `src/anim/player_anim.py` — full file Read
- `src/anim/anim_player.py` — full file Read
- `src/anim/anim_clip.py` — full file Read
- `src/anim/state_machine.py` — full file Read
- `tests/test_fusion.py`, `tests/conftest.py`, `tests/test_input_remap.py`, `tests/test_save_system.py` — full file Read
- `main.py` — relevant sections Read (subscribers L274/285/286/313, slime.update L707, save callsites L1197/L1249, Game.__init__ structure)
- `.planning/phases/31.5-cut-ability-code-strip/31.5-PHASE-VERIFICATION.md` — Phase 31.5 verifier verdict (PASS / CONDITIONAL_PASS); enumerates surviving cleanup items
- `.planning/phases/30-fusion-lifecycle-design-doc/30-CONTEXT.md` — scope-pivot rationale
- `.planning/phases/31-animation-content-particle-bank-separation/31-CONTEXT.md` — event subscription map (Phase 31 contract)
- `.planning/phases/26-event-bus-animation-fsm-skeleton/26-CONTEXT.md` — events-are-side-channel constraint
- `.planning/phases/32-fusion-manager-protocol-refactor/32-DISCUSSION-LOG.md` — alternatives considered for each decision
- `git log --oneline -1 9047b590` — verifies FUSION-DESIGN locked SHA exists

### Secondary (MEDIUM confidence)
- Python `typing.Protocol` — standard library docs (referenced behavior verified locally via `python -c`)
- pytest 9.0.2 — verified installed locally

### Tertiary (LOW confidence)
- None — every claim in this research is grounded in either a file Read or a verified shell command output.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every recommended library is stdlib + already in use
- Architecture: HIGH — file map, event names, callsites all verified by Read/Grep
- Pitfalls: HIGH — line numbers spot-checked against post-31.5 player.py
- D-14 callsite analysis: HIGH — exhaustive grep across `src/`, `main.py`, `tests/`
- Save-version mechanism: HIGH — both callers in main.py read directly; existing test fixtures Read
- Validation: HIGH — REQ-IDs map to either existing tests (verified to exist) or proposed test files

**Research date:** 2026-04-26
**Valid until:** 2026-05-26 (30 days for stable reference; the FUSION-DESIGN.md lock and the post-31.5 codebase are the static targets, so drift risk is low — only NEW Phase 32 implementation work would invalidate this research)

## RESEARCH COMPLETE

**Phase:** 32 — Fusion Manager + Protocol Refactor
**Confidence:** HIGH

### Key Findings
- Post-Phase-31.5 player.py state mapped: 4 fuse/unfuse callsites (L116, 132, 275, 292, 302, 398, 498), drill block-break branch at L463-484, mid-drill jump-cancel at L298-302 (TO DELETE), mana-shield at L110-124, charge-to-fuse at L272-275 (existing 100%-gate template). [VERIFIED]
- Event-name contract is fixed: `fuse_start`, `fuse_end`, `drill_start`, `drill_block_break`, `drill_end`, `jump_start`, `land`. Phase 31 subscribes at `main.py:274,285,286,313`. Renames break animation silently. [VERIFIED]
- D-14 recommendation: option (a) `@property` forward — 4 production read-callsites, 13+ test callsites; option (a) is zero-churn; options (b)/(c) churn is high. [VERIFIED via grep]
- Save-version: typed `SaveVersionMismatchError` recommended over result-dict — existing `if data:` truthiness check at `main.py:1249` would silently misroute on result-dict approach. [VERIFIED]
- FUSION-DESIGN locked SHA `9047b590` exists in git history. [VERIFIED via `git log`]
- Phase 31.5 verifier flagged 2 leftover dead-code items in main.py:497-499 and assets/physics-schema.json:38; recommend Phase 32 first plan picks these up as hygiene step.

### File Created
`C:/Github/jelly-roll-proto/.planning/phases/32-fusion-manager-protocol-refactor/32-RESEARCH.md`

### Confidence Assessment
| Area | Level | Reason |
|------|-------|--------|
| Standard Stack | HIGH | All stdlib (Protocol, dataclasses); pyxel + pytest verified locally |
| Architecture | HIGH | File map, callsite inventory, event-name contract all verified by direct file Read |
| Pitfalls | HIGH | Line numbers spot-checked against post-31.5 player.py; double-emission risk verified by grep |
| D-14 Trade-off | HIGH | Exhaustive grep across src/, main.py, tests/ |
| Save Mechanism | HIGH | Both callsites in main.py Read directly; current behavior verified |
| Validation Architecture | HIGH | REQ-IDs mapped; existing tests inspected; Wave 0 gaps enumerated |

### Open Questions
1. Where does `Player.state = "DIVING"` get set in the new flow? (Recommend: keep in FusionManager.latch_fuse / drill_dive.on_enter.)
2. ChargeController construction signature (per-call vs. constructor injection). (Recommend: per-call.)
3. Should planner author pytest characterization tests beyond smoke? (Recommend: yes, 4-6 tests for highest-risk drill paths.)

### Ready for Planning
Research complete. Planner can now create PLAN.md files. The 5-wave structure (Protocol/skeleton → ChargeController+FusionManager → drill_dive+pogo migration → save-version → integration audit) is concrete; D-14 and save-rejection mechanism trade-offs are resolved with specific recommendations.
