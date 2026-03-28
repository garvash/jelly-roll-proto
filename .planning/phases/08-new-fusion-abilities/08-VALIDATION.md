---
phase: 8
slug: new-fusion-abilities
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-28
---

# Phase 8 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | unittest (stdlib) with unittest.mock |
| **Config file** | None (tests run directly) |
| **Quick run command** | `python -m unittest discover tests/ -v` |
| **Full suite command** | `python -m unittest discover tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m unittest discover tests/ -v`
- **After every plan wave:** Run `python -m unittest discover tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 08-01-01 | 01 | 1 | INPUT | unit | `python -m unittest tests.test_input -v` | ❌ W0 | ⬜ pending |
| 08-02-01 | 02 | 1 | RETCON | unit | `python -m unittest tests.test_drill_retcon -v` | ❌ W0 | ⬜ pending |
| 08-02-02 | 02 | 1 | RETCON | unit | `python -m unittest tests.test_kick_removal -v` | ❌ W0 | ⬜ pending |
| 08-03-01 | 03 | 2 | FUSION | unit | `python -m unittest tests.test_fusion -v` | ❌ W0 | ⬜ pending |
| 08-03-02 | 03 | 2 | DASH | unit | `python -m unittest tests.test_dash -v` | ❌ W0 | ⬜ pending |
| 08-04-01 | 04 | 3 | ABL-01 | unit | `python -m unittest tests.test_ram -v` | ❌ W0 | ⬜ pending |
| 08-04-02 | 04 | 3 | ABL-03 | unit | `python -m unittest tests.test_slime_hold -v` | ❌ W0 | ⬜ pending |
| 08-04-03 | 04 | 3 | ABL-04 | unit | `python -m unittest tests.test_charge_shot -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_input.py` — input abstraction module tests (WASD+JK mapping, hold tracking, tap detection)
- [ ] `tests/test_fusion.py` — fusion charge/trigger/unfuse/mana shield/dissipate
- [ ] `tests/test_dash.py` — basic dash i-frames, cooldown, air usage
- [ ] `tests/test_ram.py` — slime ram CRACKED_H breaking, juice cost, stop conditions
- [ ] `tests/test_charge_shot.py` — charge shot fire, slime repositioning
- [ ] `tests/test_slime_hold.py` — tap-vs-hold detection, slime repositioning
- [ ] `tests/test_drill_retcon.py` — DOWN+V activation, boss-grant instead of item
- [ ] `tests/test_kick_removal.py` — verify kick code fully removed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Recall rubber-band visual trail | D-25 | Visual effect quality | Hold Z while slime is distant, verify visible arc/trail in Pyxel palette color 11 |
| Fusion charge visual build-up | D-02 | Visual effect quality | Hold Z at 100% juice, verify visual charge indicator while slime zips |
| Ram "Shinespark feel" | D-12 | Game feel / responsiveness | Fuse + press V, verify high-speed movement feels powerful and snappy |
| Dash "Celeste-style snappy feel" | D-15 | Game feel / responsiveness | Press V unfused, verify 2-tile burst feels instant and responsive |

*All other phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
