---
phase: 07
slug: macro-map-room-persistence
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-22
---

# Phase 07 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x |
| **Config file** | none — using standard PYTHONPATH |
| **Quick run command** | `$env:PYTHONPATH="."; pytest tests/test_world_manager.py` |
| **Full suite command** | `$env:PYTHONPATH="."; pytest tests/test_world_manager.py tests/test_persistence.py` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `$env:PYTHONPATH="."; pytest tests/test_world_manager.py`
- **After every plan wave:** Run full suite command
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | MAP-01 | unit | `pytest tests/test_world_manager.py::test_camera_clamping` | ❌ W0 | ⬜ pending |
| 07-01-02 | 01 | 1 | MAP-03 | unit | `pytest tests/test_persistence.py::test_item_persistence` | ❌ W0 | ⬜ pending |
| 07-02-01 | 02 | 2 | MAP-01 | logic | `pytest tests/test_world_manager.py::test_transition_trigger` | ❌ W0 | ⬜ pending |
| 07-02-02 | 02 | 2 | MAP-03 | logic | `pytest tests/test_persistence.py::test_timed_block_regen` | ❌ W0 | ⬜ pending |

---

## Wave 0 Requirements

- [ ] `tests/test_world_manager.py` — Stubs for WorldManager logic and transitions.
- [ ] `tests/test_persistence.py` — Stubs for global items and local regenerative blocks.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Camera Slide Easing | MAP-01 | Visual | Trigger a room transition and verify the screen slide is smooth and matches Metroid feel. |
| Door Interaction | MAP-01 | Input/Visual | Shoot a door and verify it opens correctly and triggers the slide. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending 2026-03-22
