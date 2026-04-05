---
phase: 18
slug: schema-driven-integration
status: draft
nyquist_compliant: false
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
| 18-01-01 | 01 | 1 | SCHEMA-02 | unit | `python -m pytest tests/test_schema.py -v` | ❌ W0 | ⬜ pending |
| 18-01-02 | 01 | 1 | SCHEMA-02 | unit | `python -m pytest tests/test_map.py -v` | ✅ | ⬜ pending |
| 18-02-01 | 02 | 2 | SCHEMA-03 | integration | `python -m pytest tests/test_schema_integration.py -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_schema.py` — stubs for schema loader unit tests (SCHEMA-02)
- [ ] `tests/test_schema_integration.py` — stubs for schema-driven integration tests (SCHEMA-03)

*Existing test_map.py and test_constants.py cover regression detection.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual tile rendering matches schema mappings | SCHEMA-03 | Requires visual inspection of Pyxel window | Run game, verify tiles render correctly after schema change |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
