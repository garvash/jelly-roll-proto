---
phase: 09
slug: defensive-mechanics
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-28
---

# Phase 09 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | none — Wave 0 installs if needed |
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
| 09-01-01 | 01 | 1 | ABL-05 | unit | `python -m pytest tests/test_hazard_zones.py -x -q` | ❌ W0 | ⬜ pending |
| 09-01-02 | 01 | 1 | ABL-05 | unit | `python -m pytest tests/test_bubble_shield.py -x -q` | ❌ W0 | ⬜ pending |
| 09-02-01 | 02 | 1 | ABL-06 | unit | `python -m pytest tests/test_slime_boost.py -x -q` | ❌ W0 | ⬜ pending |
| 09-03-01 | 03 | 2 | ABL-05 | manual | visual inspection | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_hazard_zones.py` — stubs for zone hazard tile types and drain rates
- [ ] `tests/test_bubble_shield.py` — stubs for shield auto-fuse, tier progression, juice drain
- [ ] `tests/test_slime_boost.py` — stubs for boost mechanics, multi-tap chaining, enemy damage

*Existing pytest infrastructure from prior phases covers framework installation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Shield VFX (translucent circle, color per tier) | ABL-05 | Visual rendering | Run game, enter hazard zone with full juice, verify shield circle appears blue (T1) or green (T2) |
| Slime Boost feel (committed beats, re-commit window) | ABL-06 | Game feel tuning | Run game fused+airborne, tap SPACE repeatedly, verify burst feel and chaining |
| Charge shot recoil momentum | D-17 | Physics feel | Fire charge shot, observe upward momentum, verify bomb-climb style exploit works |
| Input remap consistency | D-12/D-13 | Control feel | Verify DOWN+SPACE = drill dive, SPACE(air+fused) = boost, V = dash/ram |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
