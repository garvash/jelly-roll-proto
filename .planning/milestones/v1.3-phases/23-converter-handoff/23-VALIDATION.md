---
phase: 23
slug: converter-handoff
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-08
---

# Phase 23 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual review (documentation phase) |
| **Config file** | N/A |
| **Quick run command** | `test -f CONVERTER-HANDOFF.md && echo PASS` |
| **Full suite command** | Manual review against CONV-01/02/03 criteria |
| **Estimated runtime** | ~1 second (existence check) |

---

## Sampling Rate

- **After every task commit:** Run `test -f CONVERTER-HANDOFF.md && echo PASS`
- **After every plan wave:** Manual review of document content against requirements
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 1 second

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 23-01-01 | 01 | 1 | CONV-01 | smoke | `test -f CONVERTER-HANDOFF.md && echo PASS` | ❌ W0 | ⬜ pending |
| 23-01-02 | 01 | 1 | CONV-02 | manual | `grep -c "Before\|After" CONVERTER-HANDOFF.md` | ❌ W0 | ⬜ pending |
| 23-01-03 | 01 | 1 | CONV-03 | manual | `grep -c "BREAKING" CONVERTER-HANDOFF.md` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. This is a documentation phase — no test framework needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Before/after values accurate | CONV-02 | Values must be cross-checked against git history | Compare each table entry against entity-schema.json v1.0.0 vs v2.0.0 |
| Self-contained readability | CONV-03 | Requires human judgment on clarity | Read document without opening any other file — all values should be present inline |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 1s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
