---
phase: 18
slug: schema-driven-integration
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-05
---

# Phase 18 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | none — standard pytest discovery |
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
| 18-01-01 | 01 | 1 | SCHEMA-02 | unit (RED) | `python -m pytest tests/test_schema.py -x -q` | tests/test_schema.py ✅ | pending |
| 18-01-02 | 01 | 1 | SCHEMA-02 | unit (GREEN) | `python -m pytest tests/test_schema.py -x -q` | src/core/schema.py W0 | pending |
| 18-02-01 | 02 | 2 | SCHEMA-02 | integration | `python -m pytest tests/ -x -q` | all prod+test files ✅ | pending |
| 18-03-01 | 03 | 2 | SCHEMA-02, SCHEMA-03 | integration | `python -m pytest tests/test_schema.py::test_schema_mutation tests/test_schema.py::test_converter_contract_sections -x -q` | tests/test_schema.py ✅ | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_schema.py` — already exists from Phase 17; Plan 01 Task 1 adds new test functions (RED phase)
- [ ] `src/core/schema.py` — created by Plan 01 Task 2 (GREEN phase)

*Existing test files cover regression detection for the Plan 02 refactor.*

---

## Plan Structure (4 tasks across 3 plans)

| Plan | Tasks | Wave | Scope |
|------|-------|------|-------|
| 18-01 | 2 (TDD RED + GREEN) | 1 | schema.py module creation |
| 18-02 | 1 (atomic refactor) | 2 | Production + test migration to IntGrid ints |
| 18-03 | 1 (mutation + contract) | 2 | Schema mutation test + SCHEMA-03 partial |

---

## SCHEMA-03 Coverage Note

SCHEMA-03 (converter reads from schema) is **partially satisfied** in this phase:
- **Verified:** entity-schema.json contains all converter-needed sections (converter_mapping, intgrid, entities, simplified_export) — tested by `test_converter_contract_sections`
- **Deferred:** Actual converter code changes to consume the schema happen in the separate pml-to-ldtk repo (per D-14)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual tile rendering matches schema mappings | SCHEMA-02 | Requires visual inspection of Pyxel window | Run game, verify tiles render correctly after schema-driven loading |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify commands
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
