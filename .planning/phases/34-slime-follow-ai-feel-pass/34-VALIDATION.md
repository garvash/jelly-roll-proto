---
phase: 34
slug: slime-follow-ai-feel-pass
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-02
---

# Phase 34 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | tests/conftest.py |
| **Quick run command** | `pytest tests/test_slime.py -x -q` |
| **Full suite command** | `pytest -x -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_slime.py -x -q`
- **After every plan wave:** Run `pytest -x -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | SLM-04 | — | N/A | TBD | TBD | ❌ W0 | ⬜ pending |

*Per-task rows will be filled by the planner. Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Note: Per-row validation map is filled in during planning. The planner MUST populate one row per task with the SLM-04 requirement reference and the appropriate test command.*

---

## Wave 0 Requirements

- [ ] `tests/test_slime_followai.py` — RED test stubs for SLM-04 (catch-up budget, stuck recovery, mode FSM, lookahead, schema migration)
- [ ] Re-use existing `tests/conftest.py` Pyxel mock fixtures (no new fixtures expected)

*Pre-existing pytest infrastructure covers all phase requirements; only one new test module needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| S-C catch-up feels elastic in 10-tile gap | SLM-04 #1 | Subjective "feel" pass | Run game → AccelRunway gym → walk far from slime → confirm catches up within ~1.0s without snapping |
| S-S stuck recovery never visibly stuck | SLM-04 #2 | Visual continuity check | Run game → Gym_SlimeFollow sealed pocket → teleport away → confirm slime fades out + reappears, no hard teleport |
| S-M float↔ground mode switch | SLM-04 (D-08) | Subjective "lands when it can" feel | Run game → ZigzagShaft + WallSlide → confirm slime grounds when reachable, floats otherwise |
| S-L look-ahead lean visible | SLM-04 (D-11) | Subjective lean amount | Run game → AccelRunway → reverse direction → confirm slime visibly leans toward player.dx |
| S-P panel smoothness | SLM-04 #3 | Live tunable smoothness | Run game with panel open → drag every new slime_follow.* slider → confirm smooth, no snap-back |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter
- [ ] 34-FEEL-TARGETS.md Result column flipped from PENDING to PASS for all 5 S-* rows (S-C/S-S/S-M/S-L/S-P)

**Approval:** pending
