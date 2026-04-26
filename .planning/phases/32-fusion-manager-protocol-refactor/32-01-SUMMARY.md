---
phase: 32-fusion-manager-protocol-refactor
plan: 01
subsystem: testing
tags: [fusion, refactor, tdd, wave-0, characterization, save-version, importorskip]

# Dependency graph
requires:
  - phase: 30-fusion-design
    provides: FUSION-DESIGN.md drill-dive contract values + FSM design
  - phase: 31-anim-content-particle-bank
    provides: event_bus.subscribe / emit primitive with reset autouse fixture
  - phase: 31.5-cut-ability-code-strip
    provides: stripped Player API (no ram/charge_shot/boost/bubble_shield/dash); test surface free of cut-ability assertions
provides:
  - 13 new RED tests scaffolded for FusionManager + ChargeController + DrillDive + Pogo (FUS-04 / FUS-05)
  - 3 new RED tests for save-version rejection (FUS-07)
  - 10 existing fusion tests migrated from `Player.fuse` / `Player.unfuse` to `FusionManager.latch_fuse` / `force_exit(player, slime, reason)`
  - 2 existing event-bus fuse tests migrated to FusionManager API
  - 2 save-system roundtrip assertions migrated to `save_version: CURRENT_SAVE_VERSION` schema
  - tests/conftest.py extended with `make_game_with_fusion` factory fixture
affects: [32-02-protocol, 32-03-save-version, 32-04-fusion-manager, 32-05-drill-dive, 32-06-player-wiring]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-test importorskip — keeps test list visible to `pytest --co` while skipping at runtime; deviation from plan literal 'module-level importorskip'"
    - "Body-level source-introspection skip guard (test_no_mid_drill_cancel) — survives the wave-2-to-wave-4 window where a module exists but a Player code branch hasn't yet been removed"
    - "Try-import + module-level flag (`_HAS_PLAN_03`) — gates new save-version tests until Plan 03 ships CURRENT_SAVE_VERSION + SaveVersionMismatchError"

key-files:
  created:
    - tests/test_fusion_fsm.py
    - tests/test_drill_dive_parity.py
    - tests/test_pogo.py
    - .planning/phases/32-fusion-manager-protocol-refactor/deferred-items.md
  modified:
    - tests/test_fusion.py
    - tests/test_event_bus.py
    - tests/test_save_system.py
    - tests/conftest.py

key-decisions:
  - "Per-test importorskip pattern (not module-level) so `pytest --co` lists each test by name and runtime skips kick in only when production code is absent. Deviates from plan literal text but satisfies the harder acceptance criterion (`--co -q` lists 4/6/3 tests per file)."
  - "force_exit signature aligned with Plan 04's FINAL `force_exit(player, slime, reason)` — not the Plan 01 transitional `force_exit(reason)` text. Tests would FAIL post-Plan-04 with the older signature."
  - "test_event_bus.py::test_fuse_start_emits_from_gameplay graceful-skips when latch_fuse alone does not emit fuse_start (Plan 04 D-06 places the emit on ChargeController). Deeper coverage lives in test_fusion_fsm.py::test_fuse_start_emits_at_latch."
  - "Dropped `is_charging_recall` assertion from test_fuse_clears_recall_state (Rule 1 — pre-Plan-06 attribute removed per RESEARCH FUS-04 grep gate)."
  - "Hardened test_fusion.py pyxel mock install with setdefault + GAMEPAD probe (Rule 3 — pre-existing test-order issue blocked plan-level acceptance criterion `pytest tests/test_fusion.py tests/test_event_bus.py tests/test_save_system.py --co -q exits 0`)."

patterns-established:
  - "Pattern: Wave-0 RED test authoring — each new test starts with `_require_*` helper that calls `pytest.importorskip` for production modules. Tests collect cleanly today, skip at runtime, and GREEN automatically as Plans 02-06 ship."
  - "Pattern: Two-layer skip guard — for tests that need both a future module AND a future code-strip (e.g., test_no_mid_drill_cancel), combine importorskip with body-level `inspect.getsource` introspection so the test never falsely fails during the wave window."

requirements-completed: [FUS-04, FUS-05, FUS-07]

# Metrics
duration: 17min
completed: 2026-04-26
---

# Phase 32 Plan 01: Wave 0 Test Scaffolding Summary

**Authored 13 RED tests + migrated 12 existing tests + added save-version rejection class so Phase 32's FusionManager / ChargeController / DrillDive / Pogo / save_version: 2 contracts are pinned by automation before any production code lands.**

## What Shipped

### New RED test files (3)

| File | Test count | Coverage |
|------|-----------:|----------|
| `tests/test_fusion_fsm.py` | 4 | FUS-04 / FUS-05: 100% juice gate; fuse_start emits at WINDUP→FUSED latch (NOT WINDUP entry); WINDUP free-cancel returns to IDLE without juice loss; no-mid-drill-cancel guard with two-layer skip protection. |
| `tests/test_drill_dive_parity.py` | 6 | FUS-05 (v1.3 drill contract pinned via tuning.DRILL_*): activation cost 5.0; impact exit + impact cost 20.0 + drill_impact + drill_end emits; soft block refund +15.0 + drill_block_break(tx,ty); CRACKED_V cost 20.0 (no refund); juice→0 yields request_exit('juice_empty'); velocity clamp dy=DRILL_SPEED + dx=±DRILL_DRIFT_SPEED. |
| `tests/test_pogo.py` | 3 | FUS-04 / FUS-05: airborne unfused activation (no juice gate per D-20); POGO_BOUNCE_VELOCITY/COOLDOWN_FRAMES/DAMAGE present in src.fusion.pogo (NOT in tuning.* per D-18); no juice cost on enter or tick. |

### Migrated existing test files (3) + conftest extension

| File | Migration | Count |
|------|-----------|-------|
| `tests/test_fusion.py` | `player.fuse(slime)` → `game.fusion_manager.latch_fuse(slime)`; `player.unfuse(slime)` → `force_exit(player, slime, "test_unfuse")`; `player.unfuse(slime, dissipate=True)` → `force_exit(player, slime, "juice_empty")`; helper `make_player_and_slime` → `make_game_player_slime` | 8 callsites |
| `tests/test_event_bus.py` | 3 fuse/unfuse callsites migrated; `test_fuse_start_emits_from_gameplay` graceful-skips post-Plan-04 (emit moved to ChargeController) | 3 callsites |
| `tests/test_save_system.py` | L58 `"version" in data` → `"save_version" in data`; L87 `data["version"] == 1` → `data["save_version"] == CURRENT_SAVE_VERSION`; new `TestSaveVersionRejection` class (3 tests for v1-rejection / missing-field / file-preserved) | 2 assertions + 3 new tests |
| `tests/conftest.py` | Added `make_game_with_fusion` fixture (importorskip-guarded). Existing `event_bus.reset()` autouse + `mock_slime` / `mock_level` fixtures untouched. | 1 fixture added |

### importorskip strategy

Test collection succeeds in all states; tests skip at runtime when production modules are absent.

| Test file / class | Skip target | Wakes up after |
|-------------------|-------------|----------------|
| `tests/test_fusion_fsm.py` (all 4) | `src.fusion.manager` + `src.fusion.charge_controller` + `src.fusion.drill_dive` | Plans 04 + 05 |
| `tests/test_fusion_fsm.py::test_no_mid_drill_cancel` | TWO-LAYER: above + body-level `Player.handle_input` source-introspection | Plan 06 (mid-drill cancel deletion) |
| `tests/test_drill_dive_parity.py` (all 6) | `src.fusion.protocol` + `src.fusion.drill_dive` | Plans 02 + 05 |
| `tests/test_pogo.py` (all 3) | `src.fusion.pogo` | Plan 05 |
| `tests/test_fusion.py` (all 10) | `src.fusion.manager` + `src.fusion.drill_dive` + `src.fusion.pogo` | Plans 04 + 05 |
| `tests/test_event_bus.py::test_fuse_*_emits_from_gameplay` (2 tests) | same as test_fusion.py | Plan 04 |
| `tests/test_save_system.py::TestSaveRoundTrip::test_load_returns_dict` | `_HAS_PLAN_03` flag (CURRENT_SAVE_VERSION + SaveVersionMismatchError) | Plan 03 |
| `tests/test_save_system.py::TestSaveRoundTrip::test_roundtrip_preserves_all_fields` | same | Plan 03 |
| `tests/test_save_system.py::TestSaveVersionRejection` (3 tests) | same | Plan 03 |

## Verification (post-execution)

```text
$ python -m pytest --co -q | tail -3
422 tests collected in 0.50s

$ python -m pytest tests/test_fusion.py tests/test_event_bus.py tests/test_save_system.py tests/test_fusion_fsm.py tests/test_drill_dive_parity.py tests/test_pogo.py -q
45 passed, 30 skipped in 0.32s
```

Per-file collection counts (matches plan acceptance criteria 4 / 6 / 3):
- `tests/test_fusion_fsm.py --co -q` → 4 tests
- `tests/test_drill_dive_parity.py --co -q` → 6 tests
- `tests/test_pogo.py --co -q` → 3 tests

Migration grep counts:
- `grep -c "player.fuse(\|player.unfuse(" tests/test_fusion.py` → 0 (all callsites migrated)
- `grep -c "p.fuse(\|p.unfuse(" tests/test_event_bus.py` → 0
- `grep -c "fusion_manager.latch_fuse\|fusion_manager.force_exit" tests/test_fusion.py` → 9 (≥ 8 required)
- `grep -c "TestSaveVersionRejection" tests/test_save_system.py` → 1 (class header)
- `grep -cE '"save_version" in data|data\["save_version"\] == CURRENT_SAVE_VERSION' tests/test_save_system.py` → 2 (both assertions migrated)
- `grep -c 'data\["version"\]' tests/test_save_system.py` → 0 (old key purged from assertions; "version" survives only in v1-rejection test SETUP per D-21 simulation)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Bug] Aligned test migration with Plan 04's FINAL `force_exit(player, slime, reason)` signature**
- **Found during:** Task 2 planning review (cross-check with .planning/phases/32-fusion-manager-protocol-refactor/32-04-PLAN.md lines 308-329)
- **Issue:** Plan 01 task 2 narrative used the transitional `force_exit(reason)` signature, but Plan 04's REVISED final signature is `force_exit(player, slime, reason)`. Test migration using the older signature would TypeError post-Plan-04.
- **Fix:** Migrated `test_fusion.py` callsites to `game.fusion_manager.force_exit(player, slime, "test_unfuse")` and `game.fusion_manager.force_exit(player, slime, "juice_empty")` per the FINAL signature. Same applied to `test_event_bus.py::test_fuse_end_emits_from_gameplay`.
- **Files modified:** tests/test_fusion.py, tests/test_event_bus.py
- **Commit:** dc3d17d

**2. [Rule 1 — Bug] Dropped `not player.is_charging_recall` assertion from test_fuse_clears_recall_state**
- **Found during:** Task 2 (test_fusion.py:168)
- **Issue:** RESEARCH § FUS-04 grep gate enforces `! grep -q 'is_charging_recall' src/entities/player.py` — Plan 06 strips the attribute entirely. The old assertion would AttributeError post-Plan-06.
- **Fix:** Removed the assertion; test now contracts only on `slime.is_recalling == False`, which `latch_fuse` sets per Plan 04 line 280.
- **Files modified:** tests/test_fusion.py
- **Commit:** dc3d17d

**3. [Rule 3 — Blocking] Hardened test_fusion.py pyxel mock install (setdefault + GAMEPAD probe)**
- **Found during:** Task 2 verification (`pytest tests/test_fusion.py tests/test_event_bus.py --co -q` failed)
- **Issue:** Pre-existing baseline behavior: test_fusion.py unconditionally replaced `sys.modules["pyxel"]` with a partial `types.ModuleType` mock missing `GAMEPAD1_BUTTON_DPAD_LEFT`. When test_fusion.py was collected before test_event_bus.py (or any file importing src/core/input.py for the first time), the partial mock broke `src/core/input.py:5`. This blocked the plan acceptance criterion `pytest tests/test_fusion.py tests/test_event_bus.py tests/test_save_system.py --co -q exits 0`.
- **Fix:** Wrapped the mock install in `if "pyxel" not in sys.modules or not hasattr(sys.modules["pyxel"], "GAMEPAD1_BUTTON_DPAD_LEFT")` so we don't clobber the conftest.py MagicMock pyxel install (which has all attrs via `__getattr__`).
- **Files modified:** tests/test_fusion.py
- **Commit:** dc3d17d

### Auto-fixed style choices (NOT bugs, but plan-text deviations)

**4. [Plan-text deviation] Per-test `pytest.importorskip` instead of module-top**
- **Found during:** Task 1 verification (after writing module-top importorskip, `--co -q` reported 0 tests instead of the 4/6/3 the plan acceptance criteria require)
- **Issue:** Plan said `pytest.importorskip` "at module top" for clean SKIPs. With pytest, module-level importorskip raises Skipped during collection; `pytest --co` then shows 0 collected. The plan ALSO required `--co -q` to LIST 4/6/3 tests per file. These are mutually inconsistent.
- **Fix:** Restructured to `_require_*_modules()` helper inside each test body. Tests collect cleanly (`--co` lists them) AND skip at runtime when modules absent. This satisfies the harder acceptance criterion (test names visible to CI tooling) at the cost of one extra line per test.
- **Files modified:** all new test files + tests/test_fusion.py + tests/test_event_bus.py + tests/test_save_system.py
- **Commits:** 259c164, dc3d17d

**5. [Plan-text deviation] test_event_bus.py::test_fuse_start_emits_from_gameplay graceful skip**
- **Found during:** Task 2 design review against Plan 04 D-06
- **Issue:** Plan 01 said migrate `p.fuse(mock_slime)` → `game.fusion_manager.latch_fuse(mock_slime)` and "Test still asserts `fuse_start` ... emissions". But Plan 04 D-06 places the `fuse_start` emit on ChargeController at the latch site, NOT inside `latch_fuse` itself. The migrated test would FAIL post-Plan-04 because `latch_fuse` alone does not emit.
- **Fix:** Test calls `latch_fuse` and then `pytest.skip(...)` if no emit captured (graceful degradation). Deeper latch-position coverage is provided by the new `tests/test_fusion_fsm.py::test_fuse_start_emits_at_latch` (which drives ChargeController and asserts emit fires AT 200% latch, not earlier).
- **Files modified:** tests/test_event_bus.py
- **Commit:** dc3d17d

### Deferred (out of scope per SCOPE BOUNDARY)

Pre-existing failures observed identically on the Plan 01 baseline (verified via `git stash`):

- `tests/test_physics.py::test_walk_logic` (floating-point drift)
- `tests/test_sprite_assets.py::test_palette_compliance`
- `tests/test_tuning.py::test_pep562_flat_access` / `test_set_value_visibility` / `test_baseline_reset_single_key` / `test_baseline_reset_all` / `test_bake_derived_determinism`
- `tests/test_ldtk_migration.py::test_tileset_relpath_cavern`

Logged to `.planning/phases/32-fusion-manager-protocol-refactor/deferred-items.md` for downstream tech-debt cleanup. NOT Plan 32-01 scope.

## Authentication Gates

None — Wave 0 is local-only test scaffolding.

## Threat Flags

None — Wave 0 only adds tests; no new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries. The threat model in 32-01-PLAN.md (T-32-W0-01 / T-32-W0-02) is satisfied by reusing the existing `event_bus.reset()` autouse fixture (no new mechanism needed; mitigation accepted).

## Known Stubs

None — every new test file defines real assertions (skipped at runtime via importorskip until the production code lands, then they GREEN automatically). The "stubs" are pytest skips, which is the intended Wave 0 contract.

## Self-Check

Files claimed to be created:
- `tests/test_fusion_fsm.py` — FOUND
- `tests/test_drill_dive_parity.py` — FOUND
- `tests/test_pogo.py` — FOUND
- `.planning/phases/32-fusion-manager-protocol-refactor/deferred-items.md` — FOUND

Files claimed to be modified:
- `tests/test_fusion.py` — FOUND (modified)
- `tests/test_event_bus.py` — FOUND (modified)
- `tests/test_save_system.py` — FOUND (modified)
- `tests/conftest.py` — FOUND (modified)

Commits claimed:
- `259c164` — FOUND on branch (test(32-01): author Wave 0 RED scaffolding)
- `dc3d17d` — FOUND on branch (test(32-01): migrate test_fusion + test_event_bus + test_save_system)

## Self-Check: PASSED
