---
phase: 14
slug: tech-debt-schema-cleanup
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-29
---

# Phase 14 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | none — tests run from repo root |
| **Quick run command** | `python -m pytest tests/ -x -q` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 14-01-01 | 01 | 1 | MAP-02 | unit | `python -m pytest tests/ -x -q` | ✅ | ⬜ pending |
| 14-01-02 | 01 | 1 | ABL-02 | unit | `python -m pytest tests/ -x -q` | ✅ | ⬜ pending |
| 14-02-01 | 02 | 1 | — | unit | `python -m pytest tests/test_bubble_shield.py -v` | ✅ | ⬜ pending |
| 14-02-02 | 02 | 1 | — | unit | `python -m pytest tests/test_drill_retcon.py -v` | ✅ | ⬜ pending |
| 14-02-03 | 02 | 1 | — | unit | `python -m pytest tests/test_phase05_gaps.py -v` | ✅ | ⬜ pending |
| 14-02-04 | 02 | 1 | — | unit | `python -m pytest tests/test_sprite_scale.py -v` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Event-gated door opens on room entry when flag set | MAP-02 | Requires visual gameplay verification | 1. Defeat boss 2. Re-enter room 3. Confirm door is open |
| God-mode runtime toggles | — | Runtime key combo in debug build | 1. Launch debug build 2. Press toggle keys 3. Verify ability/invincibility/juice states |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
