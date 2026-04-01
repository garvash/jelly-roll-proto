---
phase: 10
slug: nitro-ejection-endgame
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-28
---

# Phase 10 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `pytest.ini` or `pyproject.toml` |
| **Quick run command** | `python -m pytest tests/ -x -q` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 10-01-01 | 01 | 1 | CRACKED_V drill break | unit | `python -m pytest tests/ -k "cracked_v" -x` | ❌ W0 | ⬜ pending |
| 10-01-02 | 01 | 1 | CRACKED_V boost break | unit | `python -m pytest tests/ -k "boost_break" -x` | ❌ W0 | ⬜ pending |
| 10-02-01 | 02 | 1 | Gamepad input mapping | unit | `python -m pytest tests/ -k "gamepad" -x` | ❌ W0 | ⬜ pending |
| 10-03-01 | 03 | 2 | Goo-Mold removal | unit | `python -m pytest tests/ -k "goo_mold" -x` | ❌ W0 | ⬜ pending |
| 10-04-01 | 04 | 2 | VFX triggers | manual | N/A — visual verification | N/A | ⬜ pending |
| 10-05-01 | 05 | 3 | Ability tuning | manual | N/A — gameplay feel | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_cracked_v.py` — stubs for CRACKED_V breaking (drill down + boost up)
- [ ] `tests/test_gamepad.py` — stubs for gamepad input mapping
- [ ] `tests/test_goo_mold_removal.py` — stubs verifying Goo-Mold constants/methods removed

*Existing pytest infrastructure covers framework needs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| VFX particle effects | D-10 | Visual feedback requires human eyes | Trigger each ability, verify particle/shake/flash effects appear |
| Ability tuning feel | D-08/D-09 | Subjective gameplay feel | Play with gamepad, verify each ability feels responsive and consistent |
| Gamepad button ergonomics | D-04 | Physical input comfort | Play with controller, verify button layout feels natural |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
