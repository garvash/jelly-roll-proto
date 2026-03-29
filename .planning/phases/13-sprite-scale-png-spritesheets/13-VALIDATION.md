---
phase: 13
slug: sprite-scale-png-spritesheets
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-29
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | tests/conftest.py |
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
| 13-01-01 | 01 | 1 | D-09,D-10,D-15 | integration | `python -m pytest tests/ -k "png or load" -x -q` | ❌ W0 | ⬜ pending |
| 13-02-01 | 02 | 1 | D-12,D-13 | unit | `python -m pytest tests/ -k "scale or offset or anchor" -x -q` | ❌ W0 | ⬜ pending |
| 13-03-01 | 03 | 2 | D-06,D-07,D-08 | integration | `python -m pytest tests/ -k "sprite or json or sidecar" -x -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_sprite_loading.py` — stubs for PNG loading and bank layout
- [ ] `tests/test_sprite_scale.py` — stubs for visual offset and anchor calculations

*Existing test infrastructure (pytest, conftest.py) covers framework needs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual sprite readability at 320x176 | D-01,D-02 | Subjective visual assessment | Run game, verify entities are visually 2x size against 8x8 tiles |
| Flip/mirror rendering correctness | D-14 | Requires visual inspection | Move player left/right, verify sprite flips correctly |
| Boss 32x32 visual proportions | D-03 | Visual assessment | Navigate to boss room, verify boss renders at correct scale |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
