---
phase: 22
slug: entity-alignment-physics-tuning
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-08
---

# Phase 22 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | none — Wave 0 installs |
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
| 22-01-01 | 01 | 1 | ENT-01 | unit | `python -m pytest tests/ -x -q` | ❌ W0 | ⬜ pending |
| 22-01-02 | 01 | 1 | ENT-02 | unit | `python -m pytest tests/ -x -q` | ❌ W0 | ⬜ pending |
| 22-01-03 | 01 | 1 | ENT-03 | unit | `python -m pytest tests/ -x -q` | ❌ W0 | ⬜ pending |
| 22-01-04 | 01 | 1 | ENT-04 | unit | `python -m pytest tests/ -x -q` | ❌ W0 | ⬜ pending |
| 22-01-05 | 01 | 1 | ENT-05 | unit | `python -m pytest tests/ -x -q` | ❌ W0 | ⬜ pending |
| 22-02-01 | 02 | 1 | PHYS-01 | unit | `python -m pytest tests/ -x -q` | ❌ W0 | ⬜ pending |
| 22-02-02 | 02 | 1 | PHYS-02 | unit | `python -m pytest tests/ -x -q` | ❌ W0 | ⬜ pending |
| 22-02-03 | 02 | 1 | PHYS-03 | unit | `python -m pytest tests/ -x -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_entity_hitboxes.py` — stubs for ENT-01 through ENT-05
- [ ] `tests/test_physics_schema.py` — stubs for PHYS-01 through PHYS-03
- [ ] `tests/conftest.py` — shared fixtures if needed

*Existing infrastructure covers framework install.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Player fits through 1-tile passages | PHYS-02 | Requires live gameplay | Launch game, navigate to narrow passage, verify player passes without getting stuck |
| Physics "feel" at new scale | PHYS-03 | Subjective feel | Play through a level, verify jump arcs and gravity feel correct |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
