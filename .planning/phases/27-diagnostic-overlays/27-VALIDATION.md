---
phase: 27
slug: diagnostic-overlays
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-12
---

# Phase 27 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | none — Wave 0 installs if needed |
| **Quick run command** | `python -m pytest tests/test_overlays.py -x -q` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_overlays.py -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 27-01-T1 | 01 | 1 | TOOL-08 | T-27-01, T-27-02 | Read-only entity access; deque(maxlen=64) bounds frame-time buffer | unit | `python -m pytest tests/test_overlays.py -x -q` | Wave 0 (created by task) | pending |
| 27-02-T1 | 02 | 2 | TOOL-08, TOOL-09 | T-27-02, T-27-03 | deque(maxlen=32) bounds blip buffers; lazy init prevents duplicate subscriptions | unit | `python -m pytest tests/test_overlays.py -x -q` | Extends Wave 1 file | pending |
| 27-02-T2 | 02 | 2 | TOOL-08, TOOL-09 | — | N/A | checkpoint:human-verify | Visual inspection (see plan) | N/A | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] Verify existing test infrastructure can import overlay module
- [ ] conftest.py pyxel mock covers overlay module import

*Existing infrastructure covers most phase requirements — pytest + conftest.py pyxel mock already in place.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Overlay renders on top without gameplay impact | TOOL-08 | Visual rendering order + performance | Toggle each overlay (F2-F5), play for 10s, confirm no gameplay change |
| Frame-time graph accuracy | TOOL-08 | Requires real-time visual inspection | F3 overlay, compare graph to actual frame rate |
| Slime overlay states match behavior | TOOL-09 | Requires observing slime during gameplay | F5 overlay, trigger stuck/catch-up states, verify indicators update |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** ready
