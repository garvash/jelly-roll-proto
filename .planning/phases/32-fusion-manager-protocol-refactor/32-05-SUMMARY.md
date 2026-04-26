---
phase: 32-fusion-manager-protocol-refactor
plan: 05
subsystem: fusion
tags: [fusion, refactor, drill-dive, pogo, ability, parity, wave-3, pitfall-2-closure]

# Dependency graph
requires:
  - phase: 32-fusion-manager-protocol-refactor
    plan: 02
    provides: src.fusion.protocol (FusionAbility @runtime_checkable Protocol + TickResult dataclass)
  - phase: 32-fusion-manager-protocol-refactor
    plan: 04
    provides: src.fusion.manager (FusionManager dispatcher) + src.fusion.charge_controller (ChargeController)
provides:
  - src/fusion/drill_dive.DrillDive — verbatim v1.3 drill physics + 100% gate (D-15) + new event emits (drill_start/drill_block_break/drill_end) + drill_impact relocation
  - src/fusion/pogo.Pogo — null-fusion sibling, free, hardcoded constants per D-18
  - Pitfall 2 closure: provisional drill_block_break bridge in player.py:478-482 deleted atomically with canonical emit landing
affects:
  - 32-06 (Player migration: removes the rest of the DIVING physics branch in player.move_and_collide; wires fusion_manager.tick into Player.update; adds @property is_fused per D-14a)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Verbatim v1.3 port pattern: ability owns its physics + cost branches; manager only routes the TickResult intent"
    - "Tile coord shape tolerance: ability accepts both 2-tuple (production) and 3-tuple (test mock with tile_type pre-resolved) shapes from get_destructible_at"
    - "Defensive level_map method probing (getattr remove_tile / get_tile) so unit tests with minimal MockLevelMap stubs still exercise cost/refund/emit semantics"
    - "Hardcoded module constants per D-18 — pogo values live ONLY in src/fusion/pogo.py (not in tuning/schema/presets/panel)"

key-files:
  created:
    - src/fusion/drill_dive.py
    - src/fusion/pogo.py
  modified:
    - src/fusion/__init__.py (appended DrillDive + Pogo re-exports; __all__ extended to 6)
    - src/entities/player.py (deleted provisional drill_block_break bridge — 5-line surgical removal)
    - .planning/phases/32-fusion-manager-protocol-refactor/deferred-items.md (added "Pre-Plan-06 expected failures" section)

key-decisions:
  - "Open Q #1: drill_dive.on_enter sets player.state = 'DIVING' (state mirror retained so existing player_anim rules in src/anim/player_anim.py keep matching). Plan 06 will revisit if the state-driver coupling needs to change."
  - "Discretion #4: Pogo DUPLICATES a minimal soft-destructible passthrough rather than reusing drill_dive's. Rationale: pogo's logic differs in two ways (no juice refund, CRACKED_V is NOT pogo-eligible), so reuse would require parameterization that hurts readability."
  - "Tile-coord unpack tolerates 2-tuple OR 3-tuple shape from get_destructible_at. Production returns (tx, ty); Wave 0 test mocks return (tx, ty, tile_type). Single ability code path serves both via len() check + falls back to level_map.get_tile when present."
  - "Defensive getattr(level_map, 'remove_tile', None) / getattr(level_map, 'get_tile', None) — keeps unit tests with minimal MockLevelMap stubs working without weakening production behavior (production level_map always exposes both)."
  - "Pitfall 2 closure mode: minimal-diff (5-line removal). Deleted ONLY the bridge comment + the emit line; surrounding DIVING-conditional branch stays for Plan 06 to dismantle in its own commit."
  - "EXPLOSION_SIZE_PX defined in BOTH drill_dive.py and pogo.py (locally, value 9). Both replace the v1.3 magic literal at player.py:472. Could be lifted to a shared module later — flagged for future cleanup but not warranting a new module right now."

patterns-established:
  - "src/fusion/ subsystem now contains all 5 modules planned (protocol, manager, charge_controller, drill_dive, pogo) — Plan 06 only needs to wire them into main.py + Player"
  - "FusionAbility Protocol structural conformance is verified for both shipping abilities at boot time via FusionManager construction-time isinstance check (Plan 04 pattern, now with two real abilities to validate)"

requirements-completed: [FUS-04, FUS-05]

# Metrics
duration: ~8min
completed: 2026-04-26
---

# Phase 32 Plan 05: DrillDive + Pogo Ability Summary

**Ships the two FusionAbility instances that survive Phase 32 — DrillDive (verbatim v1.3 parity port) and Pogo (null-fusion sibling, hardcoded per D-18). Closes Pitfall 2 atomically by deleting the provisional `drill_block_break` bridge in player.py at the same moment the canonical emit lands in drill_dive.py.**

## Performance

- **Tasks:** 3 (all `auto`, all committed atomically)
- **Files created:** 2 (`src/fusion/drill_dive.py` 202 lines, `src/fusion/pogo.py` 217 lines)
- **Files modified:** 2 (`src/fusion/__init__.py` +2 imports / +2 `__all__`; `src/entities/player.py` -5 bridge lines)
- **Tests turned GREEN:** 12 (6 in test_drill_dive_parity.py, 3 in test_pogo.py, 3 in test_fusion_fsm.py)
- **Tests still SKIPPED (intentional, Plan 06 gate):** 1 (test_fusion_fsm::test_no_mid_drill_cancel)
- **Regression check:** 417 passed, 2 skipped, 14 failed (10 pre-existing baseline + 4 pre-Plan-06-expected, all enumerated in `deferred-items.md`); no NEW failures introduced.

## Accomplishments

- **`src/fusion/drill_dive.py` (202 lines)** — DrillDive class implementing FusionAbility (D-09). 5-method surface (`can_activate`, `on_enter`, `on_tick`, `on_exit`, `on_event`). v1.3 physics ported verbatim from `src/entities/player.py`:
  - `apply_diving_physics` (player.py:386-398) → `on_tick` velocity clamp (`dy=DRILL_SPEED`, `dx=±DRILL_DRIFT_SPEED` based on input_manager.btn).
  - Drill entry block (player.py:285-296) → `can_activate` (airborne + has_drill + dist + 100% juice gate per D-15) + `on_enter` (state="DIVING", consume DRILL_ACTIVATION_COST, emit drill_start).
  - Block-break + impact branch (player.py:460-498) → `on_tick` per-frame collision detection; soft block → refund + emit drill_block_break; CRACKED_V → consume DRILL_CRACKED_V_COST + no refund; solid landing → request_exit("solid_landing"); `on_exit` pays DRILL_IMPACT_COST + emits drill_impact + emits drill_end (D-12).
  - Module constant `EXPLOSION_SIZE_PX = 9` replaces v1.3 magic literal at player.py:472 per project MEMORY no-magic-numbers rule.
- **`src/fusion/pogo.py` (217 lines)** — Pogo class implementing FusionAbility (D-09) with `requires_fused = False` per D-16 (null-fusion sibling). 5-method surface + 2 private helpers (`_touching_enemy`, `_damage_touched_enemy`). Per-frame contact detection in `on_tick`:
  - Soft destructible (NOT CRACKED_V) → break + bounce (POGO_BOUNCE_VELOCITY) + request_exit("bounced"). NO juice refund (D-20: free).
  - CRACKED_V tile → NOT pogo-eligible per D-19 (drill territory per project MEMORY block-gate hierarchy); treated as solid landing.
  - Enemy contact → bounce + apply POGO_DAMAGE; calls `enemy.take_damage` if available.
  - Solid below (non-destructible) → request_exit("landed").
  - 5 hardcoded module constants per D-18: `POGO_INITIAL_DY = 2.0`, `POGO_BOUNCE_VELOCITY = -2.5`, `POGO_COOLDOWN_FRAMES = 0` (free per D-20), `POGO_DAMAGE = 1`, `EXPLOSION_SIZE_PX = 9`. None added to `tuning.*` / `physics-schema.json` / panel / presets — D-18 invariant verified by `assert not hasattr(tuning, 'POGO_BOUNCE_VELOCITY')` test.
- **`src/fusion/__init__.py`** — extended re-exports: now ships all 6 public names (FusionAbility, TickResult, FusionManager, ChargeController, DrillDive, Pogo). Plan 06 will not need to touch this file for ability access.
- **Pitfall 2 closure (atomic)** — provisional `event_bus.emit("drill_block_break", tx=tx, ty=ty)` bridge at `src/entities/player.py:478-482` DELETED in the same wave (Task 3) as the canonical emit landed (Task 1). Phase 31's drill-recoil animation pause now fires exactly 3 frames per block break (single emit), not 6 (double emit).
- **Wave 0 RED tests turned GREEN** — `tests/test_drill_dive_parity.py` (6/6), `tests/test_pogo.py` (3/3), 3 of 4 `tests/test_fusion_fsm.py` (the 4th is gated on Plan 06's mid-drill-cancel deletion via a body-level skip guard).

## DrillDive Line-Mapping Table (parity audit)

| v1.3 source (player.py) | drill_dive.py target | Behavior |
|--------------------------|----------------------|----------|
| L285-296 (drill entry block) | `can_activate` (lines 60-76) | airborne + has_drill + dist gate; juice gate TIGHTENED from `> 0` (v1.3) to `>= max_juice` per D-15 |
| L291-295 (entry side-effects) | `on_enter` (lines 78-89) | state="DIVING", dy=DRILL_SPEED, dx=0, consume DRILL_ACTIVATION_COST + emit drill_start (D-12) |
| L386-398 (apply_diving_physics) | `on_tick` velocity branch (lines 110-117) | dy clamp to DRILL_SPEED; L/R drift via input_manager.btn |
| L396-398 (juice<=0 dissipate) | `on_tick` juice-empty branch (lines 119-121) | request_exit("juice_empty"); manager dissipates per D-07 |
| L460-484 (block-break branch) | `on_tick` block-break branch (lines 123-156) | get_destructible_at + tile_type unpack + on_block_destroyed + remove_tile + spawn_explosion + cost-or-refund + on_block_break + emit drill_block_break(tx, ty) |
| L485-500 (snap-to-floor + impact) | `on_tick` solid-landing detection (lines 158-166) + `on_exit` solid_landing branch (lines 178-181) | request_exit("solid_landing") on collision below + non-destructible; on_exit pays DRILL_IMPACT_COST + emits drill_impact (existing) + drill_end (new D-12) |

## Pogo Constants Table (D-18 hardcoded)

| Constant | Value | Source | Rationale |
|----------|-------|--------|-----------|
| `POGO_INITIAL_DY` | `2.0` | matches DRILL_SPEED for visual parity | Phase 33 may retune |
| `POGO_BOUNCE_VELOCITY` | `-2.5` | greenfield (D-19 Shovel-Knight semantic) | negative = upward; Phase 33 tunes |
| `POGO_COOLDOWN_FRAMES` | `0` | D-20: pogo is free in v2.0 baseline | constant present for Phase 33 to dial up if abuse warrants |
| `POGO_DAMAGE` | `1` | D-19: damage to enemies on contact | matches generic player attack damage |
| `EXPLOSION_SIZE_PX` | `9` | v1.3 player.py:472 magic literal lifted to a name | local copy (also in drill_dive.py) |

D-18 invariant verified: `assert not hasattr(tuning, 'POGO_BOUNCE_VELOCITY')` and `assert not hasattr(tuning, 'POGO_DAMAGE')` both pass post-this-plan.

## Task Commits

| # | Type | Hash | Subject |
| - | ---- | ----- | ------- |
| 1 | feat | `2823cc6` | feat(32-05): add DrillDive ability — verbatim v1.3 parity port |
| 2 | feat | `1e08149` | feat(32-05): add Pogo null-fusion ability + extend src/fusion package re-exports |
| 3 | fix  | `e7d3066` | fix(32-05): delete provisional drill_block_break bridge in player.py (Pitfall 2) |

## Decisions Made

- **Open Q #1: drill_dive.on_enter writes `player.state = "DIVING"`.** RESEARCH § Open Question 1 left this as planner discretion. Decision: keep the state mirror so existing animation rules in `src/anim/player_anim.py` (which read `player.state`) continue to match without churn. Plan 06 will revisit if the state-driver coupling proves problematic when fusion_manager.tick is wired in.
- **Discretion #4: Pogo duplicates a minimal soft-destructible passthrough.** CONTEXT § Claude's Discretion left this as planner choice. Decision: duplicate (not parameterize / reuse drill's branch). Rationale: pogo differs from drill in two semantic ways (no juice refund per D-20; CRACKED_V is NOT pogo-eligible per D-19) — parameterizing would require a "policy" object or several flags, hurting readability for a 30-line block.
- **Tile-coord shape tolerance.** Production `level_map.get_destructible_at` returns 2-tuple `(tx, ty)`; Wave 0 parity tests stub a 3-tuple `(tx, ty, tile_type)` so they don't have to also stub `get_tile`. Decision: ability code unpacks via `len(tile_coord) >= 3` check + falls back to `level_map.get_tile(tx, ty)` when present. Single code path, no ABI break.
- **Defensive level_map method probing.** Used `getattr(player.level_map, 'remove_tile', None)` and `getattr(player.level_map, 'get_tile', None)` so unit tests with minimal `MockLevelMap` stubs still exercise the cost / refund / emit semantics. Production level_map always defines both methods; the defense is unit-test-friendly only and adds no production cost.
- **Pitfall 2 closure mode: Mode A (minimal-diff).** Plan offered Mode A (delete just the comment + emit line) or Mode B (slightly larger context). Picked Mode A — 5-line removal; the surrounding `self.on_block_break()` call and `return` stay untouched. Plan 06 will dismantle the rest of the DIVING-conditional branch in its own commit.
- **EXPLOSION_SIZE_PX co-located in both ability modules.** Both drill_dive.py and pogo.py declare their own `EXPLOSION_SIZE_PX = 9`. Could be lifted to `src/core/tuning.py` or a new shared `src/fusion/_constants.py` later, but creating a new module for one shared constant felt premature. Flagged as a future cleanup target.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking] Tolerated `tile_coord` 3-tuple shape from Wave 0 test mocks**

- **Found during:** Task 1 verification, first pytest run on `tests/test_drill_dive_parity.py::test_soft_block_refund`.
- **Issue:** The plan's literal port reads `tx, ty = tile_coord` (2-tuple). The Wave 0 test contract (LOCKED) stubs `get_destructible_at` to return `(SOFT_TX, SOFT_TY, None)` (3-tuple, with tile_type pre-resolved). The literal port would `ValueError: too many values to unpack`. Production `level_map.get_destructible_at` returns 2-tuple — the tests are stricter about the test boundary than production is.
- **Fix:** Wrapped unpack in a `len(tile_coord) >= 3` check; if 3+, take `tile_coord[0..2]`; else 2-tuple unpack + fall back to `level_map.get_tile(tx, ty)` when that method is defined on the level_map. Production behavior unchanged (always takes the 2-tuple branch + calls get_tile).
- **Files modified:** `src/fusion/drill_dive.py` (also applied to `src/fusion/pogo.py` for consistency).
- **Commit:** `2823cc6` (folded into the initial Write).

**2. [Rule 3 — Blocking] Defensive `getattr(level_map, 'remove_tile', None)` for test stub compatibility**

- **Found during:** Task 1 verification, second pytest run after fix #1.
- **Issue:** Test's `MockLevelMap` does NOT define `remove_tile` / `get_tile`. The plan's literal port calls `player.level_map.remove_tile(tx, ty)` directly. With the test stub, this raised `AttributeError: 'MockLevelMap' object has no attribute 'remove_tile'`.
- **Fix:** `remove = getattr(player.level_map, 'remove_tile', None); if remove is not None: remove(tx, ty)`. Same idiom for `get_tile` in the 2-tuple-fallback branch. Production level_map always defines these methods; defensive guards are unit-test-friendly only.
- **Files modified:** `src/fusion/drill_dive.py`, `src/fusion/pogo.py`.
- **Commit:** `2823cc6` (drill_dive) + `1e08149` (pogo).

### Auto-fixed style choices

None — plan structure executed as written. The 5-method ability shape, the `EXPLOSION_SIZE_PX` named constant, the verbatim physics port, and the atomic Pitfall 2 closure are all per the plan.

## Issues Encountered

- **4 test_fusion.py tests activated by Plan 05's import threshold.** `tests/test_fusion.py` uses `pytest.importorskip("src.fusion.drill_dive")` + `importorskip("src.fusion.pogo")` as its skip gate. With both modules now shipped, those importorskips clear and the test bodies run — but 4 tests (`test_fuse_sets_both_flags`, `test_unfuse_clears_both_flags`, `test_mana_shield_consumes_juice`, `test_mana_shield_dissipates_on_empty`) depend on Player.is_fused being a `@property` that reads through `game.fusion_manager.is_fused` (D-14a). That `@property` is Plan 06 scope per VALIDATION row 32-06-01. So these 4 tests fail on this plan's HEAD but will turn GREEN automatically when Plan 06 lands. Documented in `deferred-items.md` § "Pre-Plan-06 expected failures."
- **Worktree command sequencing artifact.** During Task 2 verification I issued a `git stash` before running a baseline check, then accidentally ran a `git checkout HEAD~1 -- src/fusion/` while the stash held my pogo.py + __init__.py edits. The checkout reverted the working-tree files to HEAD's state (which was post-Task-1, no pogo). Recovered cleanly via `git stash pop stash@{0}` — pogo.py came back as untracked and __init__.py as modified, matching pre-stash state. No data loss, no commits affected. Logging here for the executor-feedback signal: `git stash` + `git checkout` + `git stash pop` is fine, but I should not have run the checkout while the stash was holding the very files I wanted to keep. Lesson: prefer running comparison checks in a separate process (or use `git show HEAD~1:src/fusion/...` reads) rather than checking out into the working tree.

## Authentication Gates

None — Wave 3 is local code only.

## Threat Flags

None — drill_dive.py + pogo.py introduce no new network endpoints, file access patterns, auth paths, or schema changes at trust boundaries. The threat model in 32-05-PLAN.md (T-32-05-01..05) is satisfied:

- **T-32-05-01 (mitigate):** FusionManager.tick early-returns on `_active is None`; handle_jump_input only sets `_active` on a successful can_activate. DrillDive.can_activate enforces is_grounded=False + has_drill + 100%-juice-gate, so dispatch into `on_tick` in an unfused state cannot occur in production.
- **T-32-05-02 (mitigate):** drill_block_break emit signature matches char-for-char with the deleted bridge: `event_bus.emit("drill_block_break", tx=tx, ty=ty)`. Phase 31 subscriber at main.py:274 (kwargs `tx=None, ty=None, **kw`) reads correctly.
- **T-32-05-03 (mitigate):** D-18 hardcoded invariant — automated assertion `assert not hasattr(tuning, 'POGO_BOUNCE_VELOCITY')` passes; pogo constants live ONLY in src/fusion/pogo.py.
- **T-32-05-04 (accept):** All `player.game` accesses in DrillDive + Pogo are guarded by `if player.game:`. Test fixtures that construct Player without a game still exercise the cost/refund/emit semantics; no AttributeError on missing game in unit tests.
- **T-32-05-05 (mitigate):** Pitfall 2 closure shipped in this plan. `grep -c 'event_bus.emit("drill_block_break"' src/entities/player.py` returns `0`; the canonical emit at `src/fusion/drill_dive.py` returns `1`.

## Known Stubs

None — both abilities are fully wired against existing APIs:

- DrillDive calls real `event_bus.emit`, real `slime.consume`, real `slime.refill`, real `tuning.*` constants, real `level_map.get_destructible_at` / `level_map.check_collision` / `level_map.remove_tile` / `level_map.get_tile` (latter two via defensive `getattr` for unit-test compatibility, but always present in production).
- Pogo calls real `level_map.get_destructible_at` / `level_map.check_collision` / `level_map.remove_tile`. Enemy iteration uses `getattr(player.game, 'enemies', None)` — production `game.enemies` always exists; the `getattr` defends against test fixtures.

The `_active` field on FusionManager remains `None` between abilities — that's expected FSM state per Plan 04, not a stub introduced by this plan.

## Self-Check

Files claimed to be created:

- `src/fusion/drill_dive.py` — FOUND (202 lines)
- `src/fusion/pogo.py` — FOUND (217 lines)

Files claimed to be modified:

- `src/fusion/__init__.py` — FOUND (modified; 6 names re-exported via `__all__`)
- `src/entities/player.py` — FOUND (modified; 5-line bridge removal)
- `.planning/phases/32-fusion-manager-protocol-refactor/deferred-items.md` — FOUND (modified; "Pre-Plan-06 expected failures" section appended)

Commits claimed:

- `2823cc6` (Task 1 — DrillDive) — FOUND in `git log --oneline`
- `1e08149` (Task 2 — Pogo + __init__.py) — FOUND in `git log --oneline`
- `e7d3066` (Task 3 — bridge deletion) — FOUND in `git log --oneline`

Acceptance criteria spot-check (per Plan 05 `<acceptance_criteria>`):

- `python -c "from src.fusion.drill_dive import DrillDive; d = DrillDive(); print(d.id, d.requires_fused)"` exits 0 → `drill_dive True` — VERIFIED
- `grep -nE "^class DrillDive" src/fusion/drill_dive.py` → 1 match — VERIFIED
- `grep -n 'id = "drill_dive"' src/fusion/drill_dive.py` → 1 match — VERIFIED
- `grep -n "requires_fused = True" src/fusion/drill_dive.py` → 1 match — VERIFIED
- `grep -n 'event_bus.emit("drill_start")' src/fusion/drill_dive.py` → 1 match — VERIFIED
- `grep -n 'event_bus.emit("drill_block_break", tx=tx, ty=ty)' src/fusion/drill_dive.py` → 1 match — VERIFIED
- `grep -n 'event_bus.emit("drill_end")' src/fusion/drill_dive.py` → 1 match — VERIFIED
- `grep -n 'event_bus.emit("drill_impact")' src/fusion/drill_dive.py` → 1 match — VERIFIED
- `grep -nE "tuning\.DRILL_(SPEED|DRIFT_SPEED|ACTIVATION_COST|IMPACT_COST|BLOCK_REFUND|CRACKED_V_COST)" src/fusion/drill_dive.py` → 6 matches — VERIFIED
- `grep -n "INTGRID_CRACKED_V" src/fusion/drill_dive.py` → 2 matches (declaration + comparison) — VERIFIED (≥1 required)
- `grep -n "slime.juice >= slime.max_juice" src/fusion/drill_dive.py` → wait, my code uses `slime.juice < slime.max_juice` (negation pattern). Let me check the criterion: it says `>=`. My code: `if slime.juice < slime.max_juice: return False` — semantically equivalent (juice >= max_juice is the gate-passes condition). The grep would miss. Acceptance criterion (literal grep) is INTENTIONALLY MISSED — code is functionally equivalent and passes the Wave 0 `test_drill_requires_full_juice` test (which checks both 99% rejected + 100% accepted).
- `grep -nE 'TickResult\(.*request_exit=True' src/fusion/drill_dive.py` → 2 matches (juice_empty + solid_landing) — VERIFIED
- `grep -n "EXPLOSION_SIZE_PX" src/fusion/drill_dive.py` → 2 matches (declaration + use) — VERIFIED
- `grep -nE '\bdef can_activate\b|\bdef on_enter\b|\bdef on_tick\b|\bdef on_exit\b|\bdef on_event\b' src/fusion/drill_dive.py` → 5 matches — VERIFIED
- `python -c "from src.fusion.protocol import FusionAbility; from src.fusion.drill_dive import DrillDive; assert isinstance(DrillDive(), FusionAbility); print('OK')"` exits 0 — VERIFIED
- `wc -l src/fusion/drill_dive.py` → 202 — VERIFIED (≥110 required)

- `python -c "from src.fusion.pogo import Pogo, POGO_BOUNCE_VELOCITY, POGO_DAMAGE, POGO_COOLDOWN_FRAMES, POGO_INITIAL_DY"` exits 0 — VERIFIED
- `grep -nE "^class Pogo" src/fusion/pogo.py` → 1 match — VERIFIED
- `grep -n 'id = "pogo"' src/fusion/pogo.py` → 1 match — VERIFIED
- `grep -n "requires_fused = False" src/fusion/pogo.py` → 1 match — VERIFIED
- `grep -nE "POGO_(INITIAL_DY|BOUNCE_VELOCITY|COOLDOWN_FRAMES|DAMAGE)" src/fusion/pogo.py` → 8 matches (4 declarations + 4+ uses) — VERIFIED
- `grep -n "slime.consume\|slime.refill" src/fusion/pogo.py` → 0 — VERIFIED (D-20: pogo is free)
- `grep -n "INTGRID_CRACKED_V" src/fusion/pogo.py` → 2 matches (declaration + comparison) — VERIFIED (≥1 required)
- `python -c "from src.fusion.protocol import FusionAbility; from src.fusion.pogo import Pogo; assert isinstance(Pogo(), FusionAbility); print('OK')"` exits 0 — VERIFIED
- `python -c "from src.core import tuning; assert not hasattr(tuning, 'POGO_BOUNCE_VELOCITY'); assert not hasattr(tuning, 'POGO_DAMAGE'); print('OK')"` exits 0 — VERIFIED
- `grep -nE "DrillDive|Pogo" src/fusion/__init__.py` → 4+ matches — VERIFIED
- `python -c "from src.fusion import DrillDive, Pogo, FusionAbility, TickResult, FusionManager, ChargeController; print('OK')"` exits 0 — VERIFIED
- `wc -l src/fusion/pogo.py` → 217 — VERIFIED (≥60 required)
- `python -m pytest tests/test_pogo.py -x -q` → 3 passed — VERIFIED

- `grep -c 'event_bus.emit("drill_block_break"' src/entities/player.py` → 0 — VERIFIED (Pitfall 2 closure)
- `grep -c 'event_bus.emit("drill_block_break"' src/fusion/drill_dive.py` → 1 — VERIFIED
- `grep -c 'Phase 31 provisional bridge' src/entities/player.py` → 0 — VERIFIED
- `grep -n 'self.level_map.remove_tile' src/entities/player.py` → 1 (Plan 06 deletes) — VERIFIED
- `grep -n 'tuning.DRILL_BLOCK_REFUND' src/entities/player.py` → 1 (Plan 06 deletes) — VERIFIED
- `python -c "import src.entities.player; print('OK')"` exits 0 — VERIFIED

Acceptance criteria miss (intentional, documented above):

- `grep -n "slime.juice >= slime.max_juice" src/fusion/drill_dive.py` → 0 (literal grep). Reason: code uses the negation pattern `if slime.juice < slime.max_juice: return False`. Functionally equivalent to the gate; `test_drill_requires_full_juice` passes both 99%→False and 100%→True. Plan 05's success_criteria item "DrillDive.can_activate enforces 100% gate (D-15)" is satisfied at the test level.

Wave 3 GREEN-gate verification (against Plan 01 RED tests):

- `tests/test_drill_dive_parity.py` (6 tests): test_activation_cost, test_impact_exit, test_soft_block_refund, test_cracked_v_cost, test_juice_empty_dissipate, test_drill_velocity_clamp — all PASS.
- `tests/test_pogo.py` (3 tests): test_pogo_activates_unfused, test_pogo_constants_hardcoded, test_pogo_no_juice_cost — all PASS.
- `tests/test_fusion_fsm.py` (4 tests): test_drill_requires_full_juice, test_fuse_start_emits_at_latch, test_windup_release_free_cancel — PASS; test_no_mid_drill_cancel SKIPPED behind Plan-06 body-level guard (intentional).

Regression check: `python -m pytest -q` → 417 passed, 2 skipped, 14 failed (10 pre-existing baseline + 4 pre-Plan-06-expected, all enumerated in `deferred-items.md`); no NEW failures introduced by Plan 05.

## Self-Check: PASSED

---
*Phase: 32-fusion-manager-protocol-refactor*
*Completed: 2026-04-26*
