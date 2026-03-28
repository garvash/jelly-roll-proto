---
phase: 01
slug: core-movement-physics
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-12
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `pytest tests/test_physics.py` |
| **Full suite command** | `pytest tests/` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_physics.py`
- **After every plan wave:** Run `pytest tests/`
- **Before /gsd:verify-work:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | MOV-01 | unit | `pytest tests/test_physics.py -k "walk"` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | MOV-01 | unit | `pytest tests/test_physics.py -k "jump"` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01 | 1 | MOV-01 | unit | `pytest tests/test_physics.py -k "wall"` | ❌ W0 | ⬜ pending |
| 01-01-04 | 01 | 1 | MOV-02 | unit | `pytest tests/test_physics.py -k "dash"` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_physics.py` — stubs for MOV-01, MOV-02
- [ ] `pytest install` — if no framework detected

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Game Feel (Coyote Time) | MOV-01 | Subjective / Timing | Play gym level, jump off ledge. Verify 20f grace period. |
| Game Feel (Jump Buffering) | MOV-01 | Subjective / Timing | Play gym level, jump before landing. Verify instant jump. |
| Dash Tunneling | MOV-02 | Collision Edge Case | Dash through 1px walls in gym level. Verify no tunneling. |

---

## Validation Sign-Off

- [ ] All tasks have <automated> verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
