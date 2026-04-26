---
phase: 32
slug: fusion-manager-protocol-refactor
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-26
---

# Phase 32 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `pytest.ini` (existing) |
| **Quick run command** | `pytest tests/test_fusion.py tests/test_save_manager.py -x -q` |
| **Full suite command** | `pytest -x -q` |
| **Estimated runtime** | ~10-30 seconds (quick) / ~1-2 minutes (full) |

---

## Sampling Rate

- **After every task commit:** Run quick command
- **After every plan wave:** Run full suite command
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds (quick) / 120 seconds (full)

---

## Per-Task Verification Map

> Populated by planner during plan creation. Each task with code changes gets a row.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | FUS-04 / FUS-05 / FUS-07 | TBD | TBD | unit / smoke | TBD | TBD | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

> Wave 0 = test infrastructure prerequisites. Populated by planner from RESEARCH.md "Wave 0 Requirements" section.

- [ ] `tests/test_fusion.py` — extend with FusionManager FSM transition tests (or new `tests/test_fusion_manager.py`)
- [ ] `tests/test_save_manager.py` — extend with version-mismatch rejection tests
- [ ] `tests/conftest.py` — confirm no shared-fixture changes needed
- [ ] `tests/fixtures/v1_3_save.json` — frozen v1.3 save file fixture for rejection test (Wave 0 creates if missing)

*Final list: see RESEARCH.md `## Validation Architecture` and planner task breakdown.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| v1.3 drill parity (velocity, drift, three exit conditions) | FUS-04 | Subjective feel + frame-perfect timing too brittle for automated assertion | Boot game, charge to fuse, DOWN+SPACE airborne → drill engages, vertical descent matches v1.3, blocks break with cost, exits on solid landing / juice=0 / unfuse |
| Pogo bounce on enemies + breakables, no bounce on solid | FUS-05 | Multi-entity collision interaction, level-dependent | Boot game, jump on slime enemy → bounce + damage; jump on breakable → bounce + break; jump on solid floor → land, no bounce |
| Save-version rejection user-facing message | FUS-07 | UX/menu surface | Place v1.3 save at `tuning.SAVE_FILE`, boot game, attempt continue → clear error message, save file remains on disk |
| Mid-drill jump-cancel removed | FUS-04 (parity exclusion) | Negative test — pressing jump mid-drill must NOT cancel | Initiate drill, press jump/Z → drill continues uninterrupted |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s (quick) / 120s (full)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
