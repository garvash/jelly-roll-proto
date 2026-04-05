---
phase: 17
slug: unified-schema-definition
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-05
---

# Phase 17 — Validation Strategy

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
| 17-01-01 | 01 | 1 | SCHEMA-01 | unit | `python -m pytest tests/test_schema.py -k "test_unified_schema_structure" -x` | ❌ W0 | ⬜ pending |
| 17-01-02 | 01 | 1 | SCHEMA-04 | unit | `python -m pytest tests/test_schema.py -k "test_biome_tileset_section" -x` | ❌ W0 | ⬜ pending |
| 17-01-03 | 01 | 1 | TILE-05 | unit | `python -m pytest tests/test_schema.py -k "test_intgrid_completeness" -x` | ❌ W0 | ⬜ pending |
| 17-01-04 | 01 | 1 | SCHEMA-04 | unit | `python -m pytest tests/test_schema.py -k "test_layer_definitions" -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_schema.py` — stubs for SCHEMA-01, SCHEMA-04, TILE-05 (unified schema validation tests)
- [ ] Existing `tests/test_sprite_assets.py` — update tileset path reference after file move

*Existing pytest infrastructure covers framework needs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Tileset image renders correctly | TILE-05 | Visual verification | Load game, confirm cavern tiles display as before |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
