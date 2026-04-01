---
phase: 15
slug: ldtk-entity-door-integration
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-01
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | none — existing pytest setup |
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
| 15-01-01 | 01 | 1 | INT-03 | unit | `python -m pytest tests/ -k "direction" -v` | ❌ W0 | ⬜ pending |
| 15-01-02 | 01 | 1 | INT-02 | unit | `python -m pytest tests/ -k "customfields" -v` | ❌ W0 | ⬜ pending |
| 15-02-01 | 02 | 1 | INT-01 | unit | `python -m pytest tests/ -k "entity_name" -v` | ❌ W0 | ⬜ pending |
| 15-03-01 | 03 | 2 | INT-04 | unit | `python -m pytest tests/ -k "spawn" -v` | ❌ W0 | ⬜ pending |
| 15-04-01 | 04 | 2 | — | manual | playtest | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_entity_integration.py` — stubs for direction normalization, customFields access, entity name matching, spawn lifecycle
- [ ] Fixtures for mock LDtk entity data with capitalized directions and nested customFields

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Save→Die→Reload E2E | INT-04 | Requires full game loop with save/load | 1. Save at SavePoint 2. Die 3. Reload — verify no duplicate entities |
| Room transition E2E | INT-04 | Requires room traversal in running game | 1. Enter door 2. Return — verify entity counts match expected |
| New entity stubs render | — | Visual verification needed | Place OneWay/HiddenLoot/Map in LDtk, load level, verify no crash |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
