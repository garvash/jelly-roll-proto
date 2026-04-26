---
phase: 32
slug: fusion-manager-protocol-refactor
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-26
updated: 2026-04-26
---

# Phase 32 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `pytest.ini` (existing) |
| **Quick run command** | `pytest tests/test_fusion.py tests/test_save_system.py -x -q` |
| **Full suite command** | `pytest -x -q` |
| **Estimated runtime** | ~10-30 seconds (quick) / ~1-2 minutes (full) |

---

## Sampling Rate

- **After every task commit:** Run quick command
- **After every plan wave:** Run full suite command
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds (quick) / 120 seconds (full)

---

## Per-Task Verification Map

> Populated by planner during plan creation. Each task with code changes gets a row.
> File-Exists column is relative to Wave 0 (Plan 01) shipping the test files. ✅ post-W0 means the test exists after Plan 01 lands; ❌ until W0 means missing until Plan 01 ships.

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 32-01-01 | 01 (Wave 0 scaffold) | 0 | FUS-04, FUS-05 | unit (RED collection) | `python -m pytest tests/test_fusion_fsm.py tests/test_drill_dive_parity.py tests/test_pogo.py --co -q` | ✅ post-W0 (this task creates them) | ⬜ pending |
| 32-01-02 | 01 (Wave 0 scaffold) | 0 | FUS-04, FUS-05, FUS-07 | unit (RED collection) | `python -m pytest tests/test_fusion.py tests/test_event_bus.py tests/test_save_system.py --co -q` | ✅ post-W0 (migrates existing) | ⬜ pending |
| 32-02-01 | 02 (protocol package) | 1 | FUS-04 | unit (smoke import) | `python -c "from src.fusion.protocol import FusionAbility, TickResult; r = TickResult(dx=1.0, dy=2.0, request_exit=True, exit_reason='solid_landing'); assert r.dx == 1.0 and r.exit_reason == 'solid_landing'; print('OK')"` | n/a (greenfield) | ⬜ pending |
| 32-03-01 | 03 (save_manager) | 1 | FUS-07 | unit (rejection roundtrip) | `python -m pytest tests/test_save_system.py -x -q` (post-W0; uses TestSaveVersionRejection from Plan 01) | ✅ post-W0 | ⬜ pending |
| 32-04-01 | 04 (FusionManager) | 2 | FUS-04, FUS-05 | unit (Protocol conformance + API surface) | `python -c "from src.fusion.manager import FusionManager; from src.fusion.protocol import FusionAbility, TickResult; ...; m = FusionManager(abilities={'stub': StubAbility()}); assert m.is_fused == False; print('OK')"` (full block in Plan 04 Task 1 verify) | n/a (greenfield) | ⬜ pending |
| 32-04-02 | 04 (ChargeController) | 2 | FUS-04, FUS-05 | unit (constants + state init) | `python -c "from src.fusion.charge_controller import ChargeController, ACCELERATED_REGEN_RATE, WINDUP_DURATION_FRAMES; ...; cc = ChargeController(fusion_manager=fm); assert cc._state == 'IDLE' and ACCELERATED_REGEN_RATE == 1.0 and WINDUP_DURATION_FRAMES == 30; print('OK')"` | n/a (greenfield) | ⬜ pending |
| 32-05-01 | 05 (DrillDive) | 3 | FUS-04, FUS-05 | unit (Protocol conformance + parity assertions) | `python -c "from src.fusion.protocol import FusionAbility; from src.fusion.drill_dive import DrillDive, EXPLOSION_SIZE_PX; d = DrillDive(); assert d.id == 'drill_dive' and d.requires_fused and isinstance(d, FusionAbility) and EXPLOSION_SIZE_PX == 9; print('OK')"` | n/a (greenfield) | ⬜ pending |
| 32-05-02 | 05 (Pogo) | 3 | FUS-04, FUS-05 | unit (Protocol conformance + D-18 hardcoded invariant) | `python -c "from src.fusion.protocol import FusionAbility; from src.fusion.pogo import Pogo, POGO_BOUNCE_VELOCITY, POGO_DAMAGE; from src.core import tuning; p = Pogo(); assert isinstance(p, FusionAbility) and POGO_DAMAGE == 1 and not hasattr(tuning, 'POGO_BOUNCE_VELOCITY'); print('OK')"` | n/a (greenfield) | ⬜ pending |
| 32-05-03 | 05 (bridge deletion) | 3 | FUS-05 (Pitfall 2 closure) | unit (grep invariant) | `python -c "import subprocess; r1 = subprocess.run(['grep','-c','event_bus.emit(\"drill_block_break\"','src/entities/player.py'], capture_output=True, text=True); assert r1.stdout.strip()=='0'; r2 = subprocess.run(['grep','-c','event_bus.emit(\"drill_block_break\"','src/fusion/drill_dive.py'], capture_output=True, text=True); assert r2.stdout.strip()=='1'; print('OK')"` | n/a (player.py exists pre-W0) | ⬜ pending |
| 32-06-01 | 06 (Player migration) | 4 | FUS-04, FUS-05, FUS-07 | unit (deletion + property invariants) | `python -c "import src.entities.player as pmod; from src.entities.player import Player; import inspect; src = inspect.getsource(pmod); assert 'def fuse(self, slime):' not in src and 'def unfuse(self, slime' not in src and 'def apply_diving_physics' not in src and '@property' in src and 'def is_fused(self)' in src and 'fusion_manager.tick' in src; class M: pass; p = Player(0,0,M()); assert p.is_fused == False; print('OK')"` | n/a | ⬜ pending |
| 32-06-02 | 06 (main.py wiring) | 4 | FUS-04, FUS-05, FUS-07 | smoke (import + grep invariants) | `python -c "import main; src = open('main.py').read(); assert 'self.fusion_manager = FusionManager' in src and 'self.charge_controller = ChargeController' in src and src.count('except SaveVersionMismatchError') >= 2 and 'SAVE_VERSION_ERROR_VISIBLE_FRAMES' in src; print('OK')"` and full suite `python -m pytest -x -q` | n/a | ⬜ pending |
| 32-06-03 | 06 (manual smoke checkpoint) | 4 | FUS-04, FUS-05, FUS-07 | manual | 22-step manual smoke per FUSION-DESIGN.md § Acceptance Checklist (drill parity, pogo bounce, save rejection UX); see Plan 06 Task 3 `<how-to-verify>` | n/a (human verify) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

> Wave 0 = test infrastructure prerequisites. Populated from Plan 01 (32-01-PLAN.md). `wave_0_complete` flips to `true` when Plan 01 ships.

- [ ] `tests/test_fusion_fsm.py` — 4 RED tests for FUS-04 / FUS-05 FSM transitions (drill 100% gate, fuse_start latch, free-cancel, no-mid-drill-cancel)
- [ ] `tests/test_drill_dive_parity.py` — 6 RED parity tests for FUS-04 / FUS-05 (activation cost, impact, refund, CRACKED_V cost, juice-empty dissipate, velocity clamp)
- [ ] `tests/test_pogo.py` — 3 RED tests for FUS-05 / D-18 / D-20 (activation unfused, hardcoded constants, no juice cost)
- [ ] `tests/test_fusion.py` — 11 existing tests migrated from `Player.fuse`/`Player.unfuse` to `FusionManager.latch_fuse`/`force_exit`
- [ ] `tests/test_event_bus.py` — fuse_start / fuse_end emit tests migrated to FusionManager API
- [ ] `tests/test_save_system.py` — assertions migrated to `save_version: 2` + new `TestSaveVersionRejection` class with 3 RED tests for FUS-07
- [ ] `tests/conftest.py` — extension with `make_game_with_fusion()` fixture (importorskip-guarded)

*Final list: see Plan 01 (32-01-PLAN.md) `<success_criteria>`. Tracking flips to ✅ when Plan 01 ships. Until then, `wave_0_complete: false`.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| v1.3 drill parity (velocity, drift, three exit conditions) | FUS-04 | Subjective feel + frame-perfect timing too brittle for automated assertion | Boot game, charge to fuse, DOWN+SPACE airborne → drill engages, vertical descent matches v1.3, blocks break with cost, exits on solid landing / juice=0 / unfuse |
| Pogo bounce on enemies + breakables, no bounce on solid | FUS-05 | Multi-entity collision interaction, level-dependent | Boot game, jump on slime enemy → bounce + damage; jump on breakable → bounce + break; jump on solid floor → land, no bounce |
| Save-version rejection user-facing message | FUS-07 | UX/menu surface | Place v1.3 save at `tuning.SAVE_FILE`, boot game, attempt continue → clear error message, save file remains on disk |
| Mid-drill jump-cancel removed | FUS-04 (parity exclusion) | Negative test — pressing jump mid-drill must NOT cancel | Initiate drill, press jump/Z → drill continues uninterrupted |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (Plan 01 authors / migrates the 7 test surfaces enumerated above)
- [x] No watch-mode flags
- [x] Feedback latency < 30s (quick) / 120s (full)
- [x] `nyquist_compliant: true` set in frontmatter (each task has an `<automated>` verify command)

**Approval:** pending Plan 01 ship → flips `wave_0_complete: true` and updates Status column to ✅
