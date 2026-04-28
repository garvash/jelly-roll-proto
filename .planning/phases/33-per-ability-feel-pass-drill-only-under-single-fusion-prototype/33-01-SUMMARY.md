---
phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
plan: 01
subsystem: testing

tags: [pyxel, audio, fusion, testing, tdd, conftest]

# Dependency graph
requires:
  - phase: 32-fusion-manager-protocol-refactor
    provides: src.fusion package (manager, drill_dive, pogo, charge_controller, protocol); make_game_with_fusion fixture; mock_pyxel default
  - phase: 32.1-fusion-design-destructive-drill-relock
    provides: FUSION-DESIGN.md cycle-3 SHA ce5bddbd with §Drill-Dive Contract Enemy Interaction subsection (D-03/D-04/D-05 destructive-drill rule)
provides:
  - 4 new RED test files scaffolding Wave 0 contracts for Phase 33
  - tests/test_destructive_drill.py — 4 tests pinning D-03/D-04/D-05 enemy-AABB rule for Wave 2 drill_dive.py changes
  - tests/test_daze_shot.py — 2 tests pinning D-17 fused-branch contract for Wave 2 player.py:197 changes
  - tests/test_audio.py — 3 tests pinning D-12/D-13 surface for Wave 3 src/core/audio.py
  - tests/test_tuning_migration.py — 9 tests pinning D-01/D-02/D-05/D-17 schema-seed migration for Wave 1
  - Extended tests/conftest.py — pyxel.sounds 64-element MagicMock list + pyxel.play MagicMock (closes RESEARCH Open Question #4)
affects: [33-02-tuning-schema-migration-wave-1, 33-03-drill-enemy-scan-wave-2, 33-04-daze-fused-branch-wave-2, 33-05-audio-module-wave-3, all later Phase 33 plans (every task can now include automated verify gates)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "pyxel.sounds[N] mock as 64-element list of MagicMocks pinned at conftest load — supports .set tracking across slot identity (Open Q #4 closure)"
    - "Module-level pytest.importorskip + per-test pytest.mark.skip combo — keeps pytest --co clean while exposing test names; flips to RED on later-wave imports"
    - "Use-site invariant tests (regex-based source scan) — pin migration completeness for tuning.X reads at the source line"

key-files:
  created:
    - tests/test_destructive_drill.py
    - tests/test_daze_shot.py
    - tests/test_audio.py
    - tests/test_tuning_migration.py
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-01-SUMMARY.md
  modified:
    - tests/conftest.py

key-decisions:
  - "FUSION-DESIGN.md SHA gate verified ce5bddbd9c03ac76271f17290633da2b2e492c51 (cycle-3 re-lock with destructive-drill Enemy Interaction subsection) — Phase 33 hard gate satisfied"
  - "conftest.py mock factory pre-pins pyxel.sounds as 64-element list rather than relying on default MagicMock subscription (closes Open Q #4 — default MagicMock returns new mock per __getitem__ call, breaks .set assertion identity across slots)"
  - "test_audio.py uses module-level importorskip (collection-time skip) while test_destructive_drill.py + test_daze_shot.py use per-test pytest.mark.skip — both are valid RED states per plan acceptance criteria"
  - "test_tuning_migration.py asserts on use-site reads (regex source scan of charge_controller.py + pogo.py) — provides Wave 1 completeness signal beyond simple attribute readability"

patterns-established:
  - "Phase 33 mock-pyxel preamble: tests creating pyxel module from scratch (test_destructive_drill, test_drill_dive_parity) keep their own preamble; tests piggybacking on conftest mock (test_daze_shot, test_audio, test_tuning_migration) rely on conftest's _make_pyxel_mock"
  - "EXPECTED_ named-constant baseline for tuning migrations — test files declare EXPECTED_X = value at module top, parametrize with (key, EXPECTED_X) tuples; pitfall 5 prevention by single-source-of-truth"
  - "pytest.mark.skip with reason='Wave N implements Y' — explicit RED→GREEN handoff between waves; reason string documents the gating wave for the next executor"

requirements-completed: [FUS-06]

# Metrics
duration: 5min
completed: 2026-04-29
---

# Phase 33 Plan 01: Test Scaffolding & Conftest Extension Summary

**Wave 0 RED test scaffolding for Phase 33 — 4 new test files + 1 conftest extension wiring Nyquist verify gates for Waves 1-3 destructive-drill, daze-shot, audio module, and tuning migration**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-04-28T17:15:08Z
- **Completed:** 2026-04-28T17:20:05Z
- **Tasks:** 3
- **Files modified:** 1 (conftest.py)
- **Files created:** 4 (test_destructive_drill.py, test_daze_shot.py, test_audio.py, test_tuning_migration.py)

## Accomplishments

- Verified FUSION-DESIGN.md cycle-3 SHA gate (`locked_commit: ce5bddbd9c03ac76271f17290633da2b2e492c51`) — Phase 33 hard gate satisfied with no SHA drift since Phase 32.1 re-lock.
- Closed RESEARCH Open Question #4 by extending `tests/conftest.py` with a `_make_pyxel_mock` factory that pins `pyxel.sounds` as a 64-element MagicMock list and `pyxel.play` as a MagicMock — audio tests can now call `pyxel.sounds[N].set(...)` and `pyxel.play(channel, sound_id)` without raising and with stable slot-mock identity across multiple calls.
- Landed 4 new test files totalling 18 RED tests (4 destructive_drill + 2 daze_shot + 3 audio + 9 tuning_migration) — every later-wave task can now include `<automated>pytest tests/test_*.py -x</automated>` in its verify block, satisfying the audit-gate "no 3 consecutive tasks without automated verify".
- Test suite count rose from 436 → 451 collected; pytest collection clean (no ImportError, no SyntaxError); Phase 32 regression suite (test_drill_dive_parity.py + test_pogo.py + test_fusion_fsm.py + test_event_bus.py + test_anim*.py = 101 tests) stayed green throughout.
- Encoded use-site-read invariants as RED tests (regex source scan of `src/fusion/charge_controller.py` and `src/fusion/pogo.py`) — Wave 1 tuning migration cannot accidentally leave dual-defined constants since the test will fail until the module-level assignments are deleted AND the `tuning.X` reads land at use-sites.

## Task Commits

Each task was committed atomically:

1. **Task 1: FUSION-DESIGN SHA gate + conftest mock_pyxel extension** — `a3f4194` (test)
2. **Task 2: Wave 0 test stubs — destructive_drill + daze_shot** — `ca2606e` (test)
3. **Task 3: Wave 0 test stubs — audio + tuning_migration** — `386bfb7` (test)

_Note: All three tasks ship test code only — no `feat` commits expected since the implementation lives in Waves 1-3._

## Files Created/Modified

- `tests/conftest.py` — Added `_make_pyxel_mock` factory exposing `pyxel.sounds` (64-element MagicMock list) and `pyxel.play` (MagicMock); Phase 32 fixtures (`mock_level`, `mock_slime`, `make_game_with_fusion`, `_reset_event_bus`) preserved verbatim.
- `tests/test_destructive_drill.py` (NEW) — 4 RED stubs covering D-03/D-04/D-05: single-enemy hit + DRILL_DAMAGE drain, multi-enemy chain on same frame, no-exit invariant (D-03 continue-through), juice-starvation Exit-(b) after 5-enemy stack with option-(a) clamp ordering. importorskip-guarded on `src.fusion.drill_dive` for `DRILL_DAMAGE` constant; `pytest.mark.skip` per test until Wave 2.
- `tests/test_daze_shot.py` (NEW) — 2 RED stubs covering D-17: fused Z-tap fires daze projectile + consumes `tuning.SLIME_DAZE_COST` + emits `daze_fire` event; low-juice cancel-spam guard (Pitfall 4). Uses `make_game_with_fusion` fixture from conftest. importorskip-guarded on `src.fusion.manager`.
- `tests/test_audio.py` (NEW) — 3 RED stubs covering D-12/D-13: `init_sounds()` calls `pyxel.sounds[0..6].set` (7 cues per D-13/D-20), `play_sfx("drill_enemy_hit")` routes to `pyxel.play(-1, SFX_DRILL_ENEMY_HIT)`, unknown cue silent return. Module-level importorskip on `src.core.audio` (Wave 3 ships).
- `tests/test_tuning_migration.py` (NEW) — 9 RED tests: 6 parametrized schema-seed readability checks (`WINDUP_DURATION_FRAMES=30`, `ACCELERATED_REGEN_RATE=1.0`, `POGO_BOUNCE_VELOCITY=-2.5`, `POGO_COOLDOWN_FRAMES=0`, `DRILL_ENEMY_COST=15.0`, `SLIME_DAZE_COST=20.0`), 1 `tuning._flat_index` inclusion check (Pitfall 6), 2 use-site invariants asserting no module-level constants in `charge_controller.py`/`pogo.py` AND `tuning.X` reads exist (D-01/D-02). `POGO_INITIAL_DY` and `POGO_DAMAGE` explicitly asserted to STAY hardcoded (D-02 anti-migration guard). All baseline values defined as `EXPECTED_*` named constants — no magic numbers per project memory.

## Decisions Made

- **conftest factory over inline assignment:** Chose `_make_pyxel_mock()` factory over assigning `mock.sounds = [...]` after `MagicMock()`, because each test file that piggybacks on `sys.modules["pyxel"]` should see a deterministic 64-slot list; the factory keeps that intent visible in source. Inline assignment would have left a comment-only documentation surface.
- **Module-level importorskip vs per-test skip:** `test_audio.py` uses module-level `pytest.importorskip("src.core.audio")` (skips collection of all 3 tests as a group) while `test_destructive_drill.py` and `test_daze_shot.py` use per-test `pytest.mark.skip`. Rationale: audio module is *one* delivery from Wave 3 (atomic gate); destructive-drill/daze-shot tests reference symbols that Wave 1 (`tuning.X`) and Wave 2 (`DRILL_DAMAGE`, `player.py:197` change) ship in stages, so per-test skips let later waves un-skip incrementally.
- **Use-site regex tests for migration:** `test_charge_controller_uses_tuning_at_use_site` and `test_pogo_uses_tuning_at_use_site` assert via `re.search` on file contents that module-level constant assignments are deleted AND `tuning.X` reads exist. This is stronger than the simple attribute-readability check because Wave 1 could pass `getattr(tuning, "WINDUP_DURATION_FRAMES")` while leaving the live use-site reading the stale module constant — the regex test catches that drift.

## Deviations from Plan

None — plan executed exactly as written. All three tasks committed in order with the exact code, constants, skip markers, and acceptance criteria specified in 33-01-PLAN.md. No Rule 1/2/3 auto-fixes were triggered (no bugs found, no missing critical functionality, no blockers); no Rule 4 architectural questions arose.

The plan's Task 2 acceptance criterion `grep -c "^def test_" tests/test_destructive_drill.py` was met directly (returns `4`) — no comment-line stripping was needed since no `def test_` lines appear inside doc-comments. Same for `test_daze_shot.py` (returns `2`).

## Issues Encountered

- **Standalone `python -c "import pyxel; ..."` does not load conftest.py.** The plan's Task 1 acceptance criterion mentions verifying `python -c "import pyxel; pyxel.sounds[0].set('c', 'p', '6', 'n', 25); pyxel.play(-1, 0)"` indirectly via pytest collection. A direct standalone `python -c` invocation imports the *real* pyxel module (not the mock), which raises on `pyxel.sounds[0].set('a','b','c','d',1)` due to invalid note string `'a'`. This is expected — the conftest mock only activates inside pytest. Open Q #4 closure was confirmed via successful `pytest tests/ -q --co` collection (451 tests collected, no ImportError) which DOES load conftest.

- **CRLF/LF warnings on Windows.** Each test file commit emitted `warning: in the working copy of '...', LF will be replaced by CRLF the next time Git touches it`. This is the normal Windows line-ending warning — git is configured to autocrlf on this checkout. Not a defect; no action needed.

## User Setup Required

None — no external service configuration required. All work is in-repo test scaffolding.

## Next Phase Readiness

- **Wave 1 (tuning schema migration) ready.** `test_tuning_migration.py` provides the RED→GREEN signal: Wave 1 lands the 6 keys in `assets/physics-schema.json` + makes `charge_controller.py` and `pogo.py` read `tuning.X` at use-sites, then 9 tests flip green.
- **Wave 2 (drill enemy scan + daze fused-branch) ready.** `test_destructive_drill.py` and `test_daze_shot.py` are import-stubbed and skip-marked; Wave 2 can remove the skip markers as it ships `DRILL_DAMAGE` constant + the on_tick AABB scan in `drill_dive.py` and the fused-branch in `player.py:197`.
- **Wave 3 (audio module) ready.** `test_audio.py` is importorskip-guarded; Wave 3 ships `src/core/audio.py` with `init_sounds()`, `play_sfx()`, and the 7 `SFX_*` constants, and the module-level importorskip auto-resolves to a green collection of 3 tests.

No blockers. The remaining Phase 33 plans can each cite this SUMMARY's `provides:` block as the @-context for their automated verify gates.

## Self-Check: PASSED

Verified via Read/Bash before writing this section:
- `tests/conftest.py` — FOUND, contains `_make_pyxel_mock`, `m.sounds = [MagicMock() for _ in range(64)]`, `m.play = MagicMock()`
- `tests/test_destructive_drill.py` — FOUND (4 test functions, references `DRILL_DAMAGE`, `tuning.DRILL_ENEMY_COST`, `drill_enemy_hit`)
- `tests/test_daze_shot.py` — FOUND (2 test functions, references `tuning.SLIME_DAZE_COST`, `daze_fire`)
- `tests/test_audio.py` — FOUND (3 test functions, references `audio.SFX_DRILL_ENEMY_HIT`)
- `tests/test_tuning_migration.py` — FOUND (9 collected tests including parametrized cases, references `EXPECTED_*` constants, `tuning._flat_index`, `POGO_INITIAL_DY`)
- Commit `a3f4194` — FOUND in `git log --oneline`
- Commit `ca2606e` — FOUND in `git log --oneline`
- Commit `386bfb7` — FOUND in `git log --oneline`
- Phase 32 regression suite — 101 tests pass / 1 unrelated skip after all changes
- Full-suite collection — 451 tests, no ImportError, no SyntaxError

---
*Phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype*
*Plan: 01*
*Completed: 2026-04-29*
