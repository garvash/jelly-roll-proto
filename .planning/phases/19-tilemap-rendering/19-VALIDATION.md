---
phase: 19
slug: tilemap-rendering
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-06
---

# Phase 19 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (convention-based) |
| **Config file** | none — tests in `tests/` directory |
| **Quick run command** | `py -m pytest tests/test_tilemap.py -x -q` |
| **Full suite command** | `py -m pytest tests/ -x -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `py -m pytest tests/test_tilemap.py tests/test_schema.py -x -q`
- **After every plan wave:** Run `py -m pytest tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 19-01-01 | 01 | 1 | TILE-01 | unit | `py -m pytest tests/test_tilemap.py::test_autotiles_parsed -x` | ❌ W0 | ⬜ pending |
| 19-01-02 | 01 | 1 | TILE-02 | unit | `py -m pytest tests/test_tilemap.py::test_autotiles_on_tilemap -x` | ❌ W0 | ⬜ pending |
| 19-01-03 | 01 | 1 | TILE-03 | unit | `py -m pytest tests/test_tilemap.py::test_flip_flag_warning -x` | ❌ W0 | ⬜ pending |
| 19-01-04 | 01 | 1 | TILE-04 | unit | `py -m pytest tests/test_tilemap.py::test_collision_visual_separation -x` | ❌ W0 | ⬜ pending |
| 19-02-01 | 02 | 2 | TILE-06 | manual | Visual inspection: bg layer scrolls slower than terrain | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_tilemap.py` — stubs for TILE-01, TILE-02, TILE-03, TILE-04
- [ ] Update `tests/test_schema.py` assertions for new tileset path if changed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Parallax scroll rates | TILE-06 | Visual depth effect requires visual inspection | Run game, move through room — background layer should scroll slower than terrain layer |
| Terrain edge/corner variation | TILE-02 | Visual tile variation is subjective | Run game, inspect terrain edges — should show distinct edge/corner/inner tiles, not uniform flat |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
