---
phase: 12
slug: screen-size-expansion
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-28
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | tests/conftest.py |
| **Quick run command** | `python -m pytest tests/ -x -q` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 1 | D-08 | unit | `grep -c "SCREEN_W = 320" src/core/constants.py` | ✅ | ⬜ pending |
| 12-01-02 | 01 | 1 | D-09 | grep | `grep -rn "128" main.py src/ --include="*.py" \| grep -v "SCREEN\|VIEWPORT\|HUD\|#"` | ✅ | ⬜ pending |
| 12-02-01 | 02 | 2 | D-03 | visual | `python -m pytest tests/ -k hud -x -q` | ❌ W0 | ⬜ pending |
| 12-03-01 | 03 | 2 | D-07 | file | `python -c "import json; d=json.load(open('assets/cave.ldtk')); print(d['defaultLevelWidth'])"` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_screen_size.py` — stubs for display constants, viewport bounds, HUD position
- [ ] Existing `tests/conftest.py` — shared fixtures already present

*Existing infrastructure covers most phase requirements. Wave 0 adds screen-size-specific assertions.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| HUD visual layout | D-04 | Visual appearance requires human eye | Run game, verify HP pips + juice bar visible in bottom 16px strip |
| Pyxel auto-scaling | D-10 | Monitor-dependent behavior | Run on different window sizes, verify integer scaling |
| Room transition feel | D-05 | Subjective smoothness | Transition between 3+ rooms, verify no visual glitch |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
