---
phase: 33
slug: per-ability-feel-pass-drill-only-under-single-fusion-prototype
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-28
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

> Populated by gsd-planner during PLAN.md authoring. Each PLAN.md task with `<automated>` verification adds a row here.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD     | TBD  | TBD  | FUS-06      | —          | N/A             | unit/smoke | `pytest tests/...` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Wave 0 stubs new test files for the destructive-drill mechanic and new modules introduced by Phase 33. Each test file starts as a failing skeleton; later waves fill in implementation.

- [ ] `tests/test_destructive_drill.py` — stubs covering: enemy AABB intersection during DIVING, DRILL_DAMAGE applied per hit, DRILL_ENEMY_COST drained per hit, drill continues through enemy (no exit), drill_enemy_hit event emitted, mana shield bypassed during DIVING (FUS-06)
- [ ] `tests/test_daze_shot.py` — stubs covering: spit fires when fused (D-17 gate removal at player.py:197), SLIME_DAZE_COST consumed in fused branch, daze_fire event emitted, daze-on-hit stun applies (or skip-marker if Open Q #1 defers stun primitive)
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

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (5 new test files + conftest extension)
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] 33-FEEL-TARGETS.md exists with ~10–15 falsifiable targets covering D-08 list
- [ ] Manual sign-off table in 33-FEEL-TARGETS.md fully checked before phase verification
- [ ] `nyquist_compliant: true` set in frontmatter once planner populates the verification map and Wave 0 tasks are scheduled

**Approval:** pending
