---
phase: 29
slug: player-movement-feel-pass
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-13
---

# Phase 29 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `python -m pytest tests/ -x -q` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 29-01-01 | 01 | 1 | MOV-04 | — | N/A | manual | playtest feel targets | N/A | ⬜ pending |
| 29-01-02 | 01 | 1 | MOV-05 | — | N/A | manual | verify coyote/buffer with overlay | N/A | ⬜ pending |
| 29-03-02 | 03 | 3 | MOV-06 | — | N/A | inline | `python -c "import json; [json.load(open(f'assets/presets/slot_{s}.json')) for s in range(4)]"` | inline in plan | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] No dedicated test files required — preset validation is covered by Plan 03 Task 2 inline `<automated>` verify (loads all 4 presets, checks aliases, verifies derived values baked)
- [x] Existing infrastructure covers movement physics (manual playtest required)

*Feel tuning is inherently manual — automated tests verify preset file integrity via inline verify commands, not a separate pytest file. The core validation is human feel assessment against written targets.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Ground movement feel (accel/friction) | MOV-04 | Subjective feel assessment | Playtest with panel, verify against feel targets |
| Air movement feel (jump/gravity/coyote/buffer) | MOV-05 | Timing-dependent human perception | Use input overlay (F4), verify coyote/buffer windows |
| Wall slide/jump feel | MOV-04 | Interaction feel requires human judgment | Playtest wall mechanics in test room |
| Tight preset identity | MOV-06 | Celeste-style feel is subjective | Load tight preset, verify snappy/precise feel |
| Floaty preset identity | MOV-06 | Hollow Knight-style feel is subjective | Load floaty preset, verify generous/exploratory feel |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or are manual-only (feel assessment)
- [x] Sampling continuity: manual playtest tasks are inherently continuous
- [x] No Wave 0 MISSING references — preset validation covered by inline verify
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved
