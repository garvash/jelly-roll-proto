---
phase: 21
slug: tileset-ldtk-pipeline
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-08
---

# Phase 21 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | tests/ directory (existing) |
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
| 21-01-01 | 01 | 1 | LDTK-04 | integration | `python -m pytest tests/test_sprite_assets.py -v` | Yes | pending |
| 21-01-02 | 01 | 1 | LDTK-03 | unit | `python -m pytest tests/test_tilemap.py -v` | Yes | pending |
| 21-01-03 | 01 | 1 | LDTK-02, LDTK-03, LDTK-04 | unit | `python -m pytest tests/test_ldtk_migration.py -v` | Wave 0 (Task 3 creates) | pending |
| 21-02-01 | 02 | 2 | LDTK-02, LDTK-03 | unit | `python -m pytest tests/test_tilemap.py -v` | Yes | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_ldtk_migration.py` -- Created by Plan 01, Task 3 (per D-25). Validates migration output: defaultGridSize==16, IntGrid CSV 20x11, auto-tile src coords 16px-aligned, entity px multiples of 16, tileset relPath == tilesets/cavern.png.

---

## Requirement-to-Test Mapping

| Req ID | Behavior | Primary Test File | Secondary Coverage |
|--------|----------|-------------------|--------------------|
| LDTK-02 | output.ldtk has 16x16 defaultGridSize and 20x11 rooms | tests/test_ldtk_migration.py | tests/test_tilemap.py (grid math) |
| LDTK-03 | autoLayerTiles coordinates and tile IDs correct at 16x16 | tests/test_tilemap.py | tests/test_ldtk_migration.py (src alignment) |
| LDTK-04 | Tileset at tilesets/cavern.png, schema path correct | tests/test_schema.py, tests/test_sprite_assets.py | tests/test_ldtk_migration.py (relPath) |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual tile rendering correctness | LDTK-03 | Requires visual inspection of rendered tiles | Run game, verify no gaps/misalignment in cave tilemap |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
