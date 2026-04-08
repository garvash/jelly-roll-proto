---
phase: 20
slug: grid-constants-schema-metadata
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-08
---

# Phase 20 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | tests/ directory (existing) |
| **Quick run command** | `python -m pytest tests/test_sprite_scale.py tests/test_schema.py -x -q` |
| **Full suite command** | `python -m pytest tests/ -x -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_sprite_scale.py tests/test_schema.py -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 20-01-01 | 01 | 1 | GRID-01 | unit | `python -m pytest tests/test_sprite_scale.py -k "test_tile_size" -x -q` | ✅ | ⬜ pending |
| 20-01-02 | 01 | 1 | GRID-02 | unit | `python -m pytest tests/test_sprite_scale.py -k "test_sprite_scale_removed" -x -q` | ❌ W0 | ⬜ pending |
| 20-01-03 | 01 | 1 | GRID-03 | unit | `python -m pytest tests/test_sprite_scale.py -k "test_derived_constants" -x -q` | ❌ W0 | ⬜ pending |
| 20-01-04 | 01 | 1 | GRID-04 | unit | `python -m pytest tests/test_sprite_scale.py -k "test_room_dimensions" -x -q` | ❌ W0 | ⬜ pending |
| 20-02-01 | 02 | 1 | LDTK-01 | unit | `python -m pytest tests/test_schema.py -k "test_grid_size" -x -q` | ❌ W0 | ⬜ pending |
| 20-02-02 | 02 | 1 | LDTK-05 | unit | `python -m pytest tests/test_schema.py -k "test_schema_version" -x -q` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_sprite_scale.py` — update assertions for TILE_SIZE=16, SPRITE_SCALE removal, derived constants
- [ ] `tests/test_schema.py` — add grid_size=16 assertion, update version assertion to v2.0.0

*Existing test infrastructure covers framework and fixtures.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Game viewport renders at 320x176 | GRID-04 | Visual rendering check | Run game, verify window size and no visual artifacts |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
