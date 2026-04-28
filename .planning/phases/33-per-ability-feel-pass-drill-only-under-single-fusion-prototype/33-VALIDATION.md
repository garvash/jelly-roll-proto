---
phase: 33
slug: per-ability-feel-pass-drill-only-under-single-fusion-prototype
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-28
updated: 2026-04-28
---

# Phase 33 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing — `tests/conftest.py` provides `mock_pyxel` fixture) |
| **Config file** | `pytest.ini` or pyproject toml (verify at plan time) |
| **Quick run command** | `pytest tests/ -x -q` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~5–10 seconds (existing fusion smoke tests are fast) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q`
- **After every plan wave:** Run `pytest tests/ -v` (full suite)
- **Before `/gsd-verify-work`:** Full suite must be green AND 33-FEEL-TARGETS.md sign-off complete
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

> Populated 2026-04-28 during planner revision (W#3 closure). Each PLAN.md task with `<automated>` verification has a row here. Status flips ⬜→✅ as each task lands GREEN during execution.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 33-01 T1 | 01 | 0 | FUS-06 | — | N/A | smoke (collection) | `pytest tests/ -x -q --co 2>&1 \| tail -5` | ❌ pending W0 | ⬜ pending |
| 33-01 T2 | 01 | 0 | FUS-06 | — | N/A | smoke (collection) | `pytest tests/test_destructive_drill.py tests/test_daze_shot.py -v --co 2>&1 \| tail -10` | ❌ pending W0 | ⬜ pending |
| 33-01 T3 | 01 | 0 | FUS-06 | — | N/A | smoke (collection) | `pytest tests/test_audio.py tests/test_tuning_migration.py -v --co 2>&1 \| tail -10` | ❌ pending W0 | ⬜ pending |
| 33-02 T1 | 02 | 1 | FUS-06 | — | N/A | unit (schema) | `python -c "import json; d=json.load(open('assets/physics-schema.json')); t=d['tuning']; keys=list(t.keys()); assert keys[-1]=='pogo'; assert t['slime_juice']['SLIME_DAZE_COST']==20.0; assert t['drill']['DRILL_ENEMY_COST']==15.0; assert t['fusion']['ACCELERATED_REGEN_RATE']==1.0; assert t['fusion']['WINDUP_DURATION_FRAMES']==30; assert t['pogo']['POGO_BOUNCE_VELOCITY']==-2.5; assert t['pogo']['POGO_COOLDOWN_FRAMES']==0; print('OK')"` | ✅ existing | ⬜ pending |
| 33-02 T2 | 02 | 1 | FUS-06 | — | N/A | unit (regression) | `pytest tests/test_tuning_migration.py tests/test_fusion_fsm.py tests/test_drill_dive_parity.py tests/test_pogo.py -x -q` | ❌ pending W0 | ⬜ pending |
| 33-03 T1 | 03 | 2 | FUS-06 | — | N/A | unit (regression) | `pytest tests/ -x -q -k "not destructive_drill and not daze_shot"` | ✅ existing | ⬜ pending |
| 33-03 T2 | 03 | 2 | FUS-06 | — | N/A | unit (TDD) | `pytest tests/test_destructive_drill.py tests/test_drill_dive_parity.py tests/test_fusion_fsm.py -x -v` | ❌ pending W0 | ⬜ pending |
| 33-04 T1 | 04 | 2 | FUS-06 | — | N/A | unit (regression) | `pytest tests/ -x -q -k "not daze_shot"` | ✅ existing | ⬜ pending |
| 33-04 T2 | 04 | 2 | FUS-06 | — | N/A | unit (TDD) | `pytest tests/test_daze_shot.py::test_fused_tap_fires_daze tests/test_daze_shot.py::test_daze_blocked_on_low_juice tests/test_drill_dive_parity.py tests/test_fusion_fsm.py -x -v` | ❌ pending W0 | ⬜ pending |
| 33-04 T3 | 04 | 2 | FUS-06 | — | N/A | unit (TDD + regression) | `pytest tests/test_daze_shot.py tests/test_destructive_drill.py tests/test_drill_dive_parity.py tests/test_fusion_fsm.py -x -v` | ❌ pending W0 | ⬜ pending |
| 33-05 T1 | 05 | 3 | FUS-06 | — | N/A | unit (TDD) | `pytest tests/test_audio.py -x -v` | ❌ pending W0 | ⬜ pending |
| 33-05 T2 | 05 | 3 | FUS-06 | — | N/A | unit (regression) | `pytest tests/ -x -q -k "not feel and not feel_targets"` | ✅ existing | ⬜ pending |
| 33-05 T3 | 05 | 3 | FUS-06 | — | N/A | unit (full suite) | `pytest tests/ -x -q` | ✅ existing | ⬜ pending |
| 33-06 T1 | 06 | 4 | FUS-06 | — | N/A | unit (full suite + doc-exists) | `pytest tests/ -x -q && ls .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md` | ✅ existing | ⬜ pending |
| 33-06 T2 | 06 | 4 | FUS-06 | — | manual sign-off | checkpoint (human-verify) | (manual — playtest + sign-off in 33-FEEL-TARGETS.md) | N/A | ⬜ pending |
| 33-06 T3 | 06 | 4 | FUS-06 | — | N/A | unit (preset-bake + full suite) | `python -c "import json; d=json.load(open('assets/presets/v2.0-default.json')) if __import__('os').path.exists('assets/presets/v2.0-default.json') else json.load(open('assets/presets/slot_1.json')); v=d['values']; assert all(k in v for k in ('WINDUP_DURATION_FRAMES','ACCELERATED_REGEN_RATE','POGO_BOUNCE_VELOCITY','POGO_COOLDOWN_FRAMES','DRILL_ENEMY_COST','SLIME_DAZE_COST')); print('OK')" && pytest tests/ -x -q` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Total:** 16 task rows (3 in Plan 01, 2 in Plan 02, 2 in Plan 03, 3 in Plan 04 [revised — Task 3 added per Blocker #2], 3 in Plan 05, 3 in Plan 06 — one of which is the manual-sign-off checkpoint).

**Sampling continuity check:** No 3 consecutive auto tasks lack an `<automated>` command. The Plan 06 Task 2 checkpoint is sandwiched between Task 1 (auto) and Task 3 (auto), each with their own automated commands; the checkpoint itself is excluded from sampling continuity per Nyquist rule (manual checkpoints are intentional pauses, not silent gaps).

---

## Wave 0 Requirements

Wave 0 stubs new test files for the destructive-drill mechanic and new modules introduced by Phase 33. Each test file starts as a failing skeleton; later waves fill in implementation.

- [ ] `tests/test_destructive_drill.py` — stubs covering: enemy AABB intersection during DIVING, DRILL_DAMAGE applied per hit, DRILL_ENEMY_COST drained per hit, drill continues through enemy (no exit), drill_enemy_hit event emitted, mana shield bypassed during DIVING (FUS-06)
- [ ] `tests/test_daze_shot.py` — Wave 0 stubs Test 1 + Test 2 (fused-tap-fires-daze, low-juice-gate); **Plan 04 Task 3 ADDS Test 3 (Snail stun on contact via main.py loop) + Test 4 (Boss-no-raise regression — W#6 closure)**. End state: 4 test functions, 0 skipped.
- [ ] `tests/test_audio.py` — stubs covering: src/core/audio.py imports without crashing, all 7 cues registered (fuse_start, drill_start, drill_block_break, drill_enemy_hit, drill_impact, daze_fire, pogo_bounce), play_sfx(name) routes to pyxel.play, mock_pyxel.sounds reachable
- [ ] `tests/test_tuning_migration.py` — stubs covering: WINDUP_DURATION_FRAMES, ACCELERATED_REGEN_RATE, POGO_BOUNCE_VELOCITY, POGO_COOLDOWN_FRAMES, DRILL_ENEMY_COST, SLIME_DAZE_COST all readable via `tuning.X`; charge_controller.py / pogo.py / drill_dive.py / player.py read from tuning at use-site (no module-level constants for these names after migration)
- [ ] `tests/test_v13_parity.py` *(extension of existing parity tests if present)* — confirm Phase 32 v1.3 regression tests still pass with destructive-drill addition (drill-tile interaction unchanged, two-exit FSM intact, per-block costs/refunds unchanged)
- [ ] `tests/conftest.py` — extend mock_pyxel with `sounds = [MagicMock() for _ in range(64)]` if not already present (RESEARCH.md flagged this as ASSUMED for 1-min verification at plan time)

---

## Manual-Only Verifications

Phase 33 is a feel-pass: many criteria are subjective ("feels confirmed", "reads as committed gesture") and live in `33-FEEL-TARGETS.md`, not pytest. The list below enumerates what must be verified manually with sign-off.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Tap/hold disambiguation feels natural at ~8f threshold | FUS-06 | Subjective input feel; user discrimination latency | Hold Z at boundary frames in panel; sign off when discrimination reads as confident |
| WINDUP cancel-window feels generous but committed (~30f draft) | FUS-06 | Subjective commit feel | Iterate WINDUP_DURATION_FRAMES via panel; sign off when "I can change my mind" + "I committed" both read |
| Accelerated-regen ritual time feels right (~2× passive draft) | FUS-06 | Subjective ritual pacing | Iterate ACCELERATED_REGEN_RATE; sign off when ritual reads as 2× faster than passive |
| Drill chain length on full juice feels appropriate | FUS-06 | Subjective combat pacing | Tune DRILL_ENEMY_COST in 10–20 range; chain through 3+ enemies feels neither too cheap nor too expensive |
| Juice-starvation Exit (b) trigger reads naturally | FUS-06 | Subjective gameplay clarity | Drain to 0 mid-chain; verify dissipate + cooldown reads as "ran out", not "broken" |
| Enemy kill chain through 3+ enemies feels powerful | FUS-06 | Subjective combat fantasy | Construct enemy stack in cluster room; drill through; sign off when "drill is a finisher" reads |
| Boss daze→drill loop feels tuned | FUS-06 | Subjective combat readability | Tune SLIME_DAZE_COST + DRILL_ENEMY_COST balance against existing boss; loop reads as PROJECT.md core fantasy |
| Pogo confirm-only entry (FUSION-DESIGN D-04 unchanged) | FUS-06 | Behavioral regression check | Bounce on enemies + breakables, land without bounce on solid ground; verify with sign-off |
| Drill identity differentiates from spit/daze/kick (blindfolded SFX test) | FUS-06 | Audio identity is subjective | Play 7 cues with eyes closed; each must be distinguishable; sign-off in 33-FEEL-TARGETS.md |
| Particle palette reads as "earth being broken" (D-15) | FUS-06 | Visual identity is subjective | Render drill block-break + enemy-hit; sign off when 4/9/10 palette reads as earthbound |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (16/16 task rows in the map; 1 is a manual checkpoint sandwiched between auto tasks)
- [x] Sampling continuity: no 3 consecutive auto tasks without automated verify
- [x] Wave 0 covers all MISSING references (5 new test files + conftest extension)
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [ ] 33-FEEL-TARGETS.md exists with ~10–15 falsifiable targets covering D-08 list (created by Plan 06 Task 1)
- [ ] Manual sign-off table in 33-FEEL-TARGETS.md fully checked before phase verification (Plan 06 Task 2 checkpoint)
- [x] `nyquist_compliant: true` set in frontmatter (W#3 closure 2026-04-28; per-task verification map populated above)

**Approval:** pending phase execution
