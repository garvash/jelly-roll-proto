---
phase: 5
slug: 05-enemies-player-health
status: verified
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-15
last_audit: 2026-03-16
---

# Phase 5 — Validation Strategy (Audited)

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | none |
| **Quick run command** | `python -m pytest tests/test_health.py tests/test_enemies.py tests/test_hazards.py` |
| **Full suite command** | `python -m pytest tests/test_health.py tests/test_enemies.py tests/test_hazards.py tests/test_phase05_gaps.py tests/test_phase05_nyquist.py` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_health.py tests/test_enemies.py`
- **After every plan wave:** Run `python -m pytest tests/test_health.py tests/test_enemies.py tests/test_hazards.py tests/test_phase05_gaps.py tests/test_phase05_nyquist.py`
- **Before /gsd:verify-work:** Full suite must be green (37/37 tests passed)
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 05-01-01 | 01 | 1 | Player Health (HP/Invuln/Knockback) | unit | `python -m pytest tests/test_health.py` | ✅ green |
| 05-01-02 | 01 | 1 | Hazard Damage (Respawn/Damage) | unit | `python -m pytest tests/test_hazards.py` | ✅ green |
| 05-01-03 | 01 | 1 | Death at 0 HP | unit | `python -m pytest tests/test_health.py::test_player_death` | ✅ green |
| 05-02-01 | 02 | 1 | Enemy Base Class | unit | `python -m pytest tests/test_enemies.py` | ✅ green |
| 05-02-02 | 02 | 1 | Snail AI (Turn at wall/ledge) | unit | `python -m pytest tests/test_enemies.py::test_snail_turn` | ✅ green |
| 05-02-03 | 02 | 1 | Bat AI (Dive/Return) | unit | `python -m pytest tests/test_phase05_gaps.py::test_bat_returning_state` | ✅ green |
| 05-02-04 | 02 | 1 | Spawning (Tiles/Duplication) | integration | `python -m pytest tests/test_phase05_gaps.py::test_spawning_logic` | ✅ green |
| 05-02-05 | 02 | 1 | Combat Integration (Spit/Drill vs Enemy) | integration | `python -m pytest tests/test_phase05_gaps.py::test_combat_projectile_collision` | ✅ green |
| 05-02-06 | 02 | 1 | Player Contact Damage | integration | `python -m pytest tests/test_phase05_gaps.py::test_player_contact_damage` | ✅ green |

---

## Nyquist Gap Coverage (Added 2026-03-16)

| Behavior | Test | Verification |
|----------|------|--------------|
| Input Buffering/Blocking | `tests/test_phase05_nyquist.py::test_input_ignored_during_knockback` | Confirmed input is ignored during stun. |
| Invuln Timer Logic | `tests/test_phase05_nyquist.py::test_invuln_timer_decreases` | Confirmed timer decrements per frame. |
| Bat Aggro Range | `tests/test_phase05_nyquist.py::test_bat_range_limit` | Confirmed Bat only dives when player is close (< 80px). |
| Room Entry Persistence | `tests/test_phase05_nyquist.py::test_room_spawn_update` | Confirmed `room_spawn_x/y` updates correctly on transition. |

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Health UI | Display hearts | Visual | Run `python main.py`, take damage, verify hearts change color. |
| Knockback Feel | Responsive movement | Subjective | Run `python main.py`, touch an enemy, verify knockback feels right. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** re-approved 2026-03-16
