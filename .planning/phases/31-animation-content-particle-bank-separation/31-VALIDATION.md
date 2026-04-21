---
phase: 31
slug: animation-content-particle-bank-separation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-21
---

# Phase 31 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | pytest.ini / pyproject.toml (existing) |
| **Quick run command** | `pytest tests/test_anim.py tests/test_anim_hitbox.py -q` |
| **Full suite command** | `pytest -q` |
| **Estimated runtime** | ~10 seconds (anim suite), ~30 seconds (full) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_anim.py tests/test_anim_hitbox.py -q`
- **After every plan wave:** Run `pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

*Filled in by planner — see 31-PLAN.md files for automated verify commands per task. Table finalised during execution.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD     | TBD  | TBD  | ANIM-04/05/06/07 | — | N/A (gameplay feel, no security surface) | unit / manual | `pytest tests/test_anim*.py -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_anim_hitbox.py` — NEW file, state × vx_sign × vy_sign × facing matrix driving Player through every clip asserting `(w, h)` invariant (ANIM-07 / D-20/21/22/23)
- [ ] `tests/test_anim.py` — extend with coverage for new clips (land_squash, turn_skid, jump_crouch, jump_stationary/jump_running split, drill_spin) + `AnimPlayer.pause_for(n)` unit tests (ANIM-04 / D-01..D-06)
- [ ] `tests/test_tuning_anim.py` — NEW file, exercises `tuning.load_anim()` fail-fast branches: missing clip_id in rules, frames/durations length mismatch, unknown fields (ANIM-05 / D-14)
- [ ] Existing `tests/conftest.py` pyxel mock + `mock_level` fixture — reused, no install needed

*No new framework install required — pytest already in repo.*

---

## Success-Criterion Coverage Matrix

Each ROADMAP success criterion maps to measurable checks:

| SC | Criterion | Measurement | Test File | Manual? |
|----|-----------|-------------|-----------|---------|
| 1  | Jump / land / turn / drill / fuse each show a visible transition driven by FSM + tunable from panel | (a) `tests/test_anim.py` asserts each new clip appears in driver-matrix playback; (b) manual in-engine check with panel slider drag confirms duration change takes effect live | `tests/test_anim.py` + manual | Partial (visual confirmation of "looks like a transition" is subjective — automated covers clip triggering + duration live-read; manual covers the subjective visual) |
| 2  | `assets/anim-schema.json` exists, loaded by `tuning.py`, live-editable via panel | (a) `tests/test_tuning_anim.py` asserts `tuning.anim.player.clips['run']` returns expected object after `load_anim()`; (b) fail-fast unit tests for D-14 error branches; (c) manual "Reload anim schema" button re-runs loader | `tests/test_tuning_anim.py` + manual | Partial (button click is manual; loader logic + validation is automated) |
| 3  | Particle sprites live in a bank separate from the map tileset; no tile-slot competition | (a) unit assertion that `SPRITE_MANIFEST` entries for tiles and particles have distinct `bank` indices (bank 0 vs bank 2); (b) manual — load Level_0 with many particles, confirm tiles still render | `tests/test_sprite_manifest.py` (new or extended) + manual | Partial (automated bank-distinctness check; manual confirms runtime doesn't collide) |
| 4  | Automated regression test confirms no anim state read mutates `.w`/`.h` | `tests/test_anim_hitbox.py` — full state × vx_sign × vy_sign × facing matrix, snapshot `(w,h)` at init, drive driver combos for N ticks, assert invariant | `tests/test_anim_hitbox.py` | No (fully automated, hard gate per D-22) |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| "Looks like a transition" — visual readability of jump_crouch, land_squash, turn_skid, drill_spin 4-frame, fuse-flash convergence + blob growth | ANIM-04 (SC-1) | Subjective readability; automated can only confirm clip fires, not "reads as a transition to a human" | Run `python main.py`; perform each action (jump stationary, jump running, land hard, turn around mid-run, drill into cracked-V block, fuse). Verify each shows a visible frame change. |
| Panel "Reload anim schema" button re-applies edited JSON on click | ANIM-05 (SC-2) | UI button interaction | Run `python main.py`; edit `assets/anim-schema.json` (change a duration); click "Reload anim schema" in panel ANIM tab; confirm animation speed changes live. |
| No tile-slot contention under heavy particle load | ANIM-06 (SC-3) | Requires visual confirmation that map tiles still render while particles spawn | Run `python main.py`; enter a room; trigger repeated block-break bursts (drill through cracked-V field); confirm map tiles remain stable and no particle bleed overwrites tile graphics. |
| Anim durations persist in preset slots + autosave round-trip | ANIM-05 / Phase 28 preset integration | UI persistence across restarts | Edit anim duration via panel slider; save to preset slot; restart engine; reload preset; confirm duration restored. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (`tests/test_anim_hitbox.py`, `tests/test_tuning_anim.py`)
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
