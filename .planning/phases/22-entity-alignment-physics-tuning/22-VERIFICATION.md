---
phase: 22-entity-alignment-physics-tuning
verified: 2026-04-08T00:00:00Z
status: passed
score: 9/9 must-haves verified
re_verification: false
---

# Phase 22: Entity Alignment & Physics Tuning Verification Report

**Phase Goal:** Player, enemies, boss, and effect entities have collision boxes that match their 16x16 (or larger) visual sprites, with physics-schema.json reflecting the new tile base
**Verified:** 2026-04-08
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #  | Truth                                                          | Status     | Evidence                                                            |
|----|----------------------------------------------------------------|------------|---------------------------------------------------------------------|
| 1  | Slime collision box is 16x16                                   | VERIFIED   | `slime.py` line 27-28: `self.w = 16`, `self.h = 16`               |
| 2  | Snail and Bat collision boxes are 16x16                        | VERIFIED   | `enemies.py` line 6: `w=16, h=16` base default; both inherit it   |
| 3  | Boss (Mole) collision box is 24x28                             | VERIFIED   | `boss.py` lines 43-44: `self.w = 24`, `self.h = 28`               |
| 4  | BossRock collision box is 16x16                                | VERIFIED   | `boss.py` lines 13-14: `self.w = 16`, `self.h = 16`               |
| 5  | Explosion effect draw call passes 16x16 as collision w/h       | VERIFIED   | `effects.py` line 32: `draw_sprite(self.x, self.y, 16, 16, ...)`  |
| 6  | Legacy tile-scan spawn path uses TILE_SIZE instead of `* 8`    | VERIFIED   | `main.py` lines 362-381: all spawn coords use `TILE_SIZE`; no `tx * 8` remains |
| 7  | Player hitbox remains 10x14 (unchanged per D-01)               | VERIFIED   | `player.py` lines 18-19: `self.w = 10`, `self.h = 14`             |
| 8  | Door dimensions remain 8x32 / 32x8 (unchanged per D-02)       | VERIFIED   | `map_entities.py` lines 20-24: `w=8,h=32` / `w=32,h=8`            |
| 9  | physics-schema.json tile_size==16 with recalculated tile-units | VERIFIED   | `assets/physics-schema.json`: `"tile_size": 16`, `"hitbox_px": [10, 14]`, `"GRAVITY": 0.0875` |

**Score:** 9/9 truths verified

---

### Required Artifacts

| Artifact                       | Expected                                        | Status      | Details                                                   |
|--------------------------------|-------------------------------------------------|-------------|-----------------------------------------------------------|
| `tests/test_phase22.py`        | Regression tests for all entity hitbox sizes    | VERIFIED    | 13 tests present; all 13 pass                             |
| `src/entities/enemies.py`      | Enemy base class with 16x16 default hitbox      | VERIFIED    | Line 6: `w=16, h=16` in `__init__` signature             |
| `src/entities/slime.py`        | Slime with 16x16 collision                      | VERIFIED    | Lines 27-28: `self.w = 16`, `self.h = 16`                |
| `src/entities/boss.py`         | Mole 24x28, BossRock 16x16, centered spawn offsets | VERIFIED | Mole 24x28, BossRock 16x16, `self.w // 2` / `self.h // 2` used throughout |
| `src/entities/effects.py`      | Effect draw calls using 16x16 collision size    | VERIFIED    | Line 32: `draw_sprite(self.x, self.y, 16, 16, ...)`      |
| `assets/physics-schema.json`   | Physics contract with 16px tile-unit values     | VERIFIED    | `tile_size: 16`, version `0.2.0`, all tile-unit values halved |
| `tests/test_enemies.py`        | Enemy tests updated for 16x16 hitbox            | VERIFIED    | No stale `== 8` assertions; 4 tests pass                  |
| `tests/test_boss.py`           | Boss tests updated for 24x28 hitbox             | VERIFIED    | No stale 16x16 Mole assertions; 3 tests pass              |

---

### Key Link Verification

| From                          | To                                   | Via                                            | Status  | Details                                                      |
|-------------------------------|--------------------------------------|------------------------------------------------|---------|--------------------------------------------------------------|
| `enemies.py` base class       | Snail, Bat subclasses                | `w=16, h=16` default propagates via `super().__init__` | WIRED | Snail/Bat call `super().__init__(x, y, game=game)` with no override |
| `boss.py` BossRock spawn      | Mole rock spawn offset               | `self.x + self.w // 2`, `self.y + self.h // 2` | WIRED | Line 103: `BossRock(self.x + self.w // 2, self.y + self.h // 2, ...)` |
| `assets/physics-schema.json`  | pml-to-ldtk converter (external)     | JSON contract consumed by converter            | VERIFIED (schema) | Schema has `tile_size: 16`, `"version": "0.2.0"` signaling breaking change |

---

### Data-Flow Trace (Level 4)

Not applicable — this phase modifies collision constants and a JSON file, not dynamic data rendering pipelines.

---

### Behavioral Spot-Checks

| Behavior                                    | Command                                                  | Result           | Status  |
|---------------------------------------------|----------------------------------------------------------|------------------|---------|
| All 13 phase-22 regression tests pass        | `pytest tests/test_phase22.py -v`                        | 13 passed        | PASS    |
| Full test suite passes (no regressions)      | `pytest tests/ -q`                                       | 352 passed, 3 skipped | PASS |
| No `tx * 8` or `ty * 8` in main.py spawn paths | `grep "tx \* 8\|ty \* 8" main.py`                     | (no output)      | PASS    |
| physics-schema.json tile_size == 16          | Python inline assert                                     | OK               | PASS    |

---

### Requirements Coverage

| Requirement | Source Plan | Description                                                          | Status    | Evidence                                                                            |
|-------------|-------------|----------------------------------------------------------------------|-----------|-------------------------------------------------------------------------------------|
| ENT-01      | 22-01       | Player collision box matches 16x16 visual sprite                     | SATISFIED | Player stays 10x14 with bottom-center overhang per D-01; test_player_hitbox passes  |
| ENT-02      | 22-01       | Enemy collision boxes (Snail, Bat) match 16x16 visual sprites        | SATISFIED | `enemies.py` w=16,h=16 default; Snail/Bat inherit it; tests pass                   |
| ENT-03      | 22-01       | Boss collision box scaled proportionally                             | SATISFIED | Mole at 24x28 (D-04 overrides REQUIREMENTS.md text of 32x32; research and plan agree on 24x28 proportional approach); test_boss_hitbox passes |
| ENT-04      | 22-01       | Door entity dimensions updated for 16x16 grid                        | SATISFIED | Doors remain 8x32/32x8 per D-02; test_door_* tests pass                             |
| ENT-05      | 22-01       | draw_sprite() offset math simplified — collision equals visual size  | SATISFIED | effects.py line 32 passes 16,16; test_draw_offset_simplified passes                 |
| PHYS-01     | 22-02       | Jump height and gravity tuned for 16x16 tile passages                | SATISFIED | Physics constants unchanged per D-03; schema documents new tile-unit values; test_physics_constants_unchanged passes |
| PHYS-02     | 22-02       | Minimum passage sizes defined in new tile units                      | SATISFIED | schema clearance: min_vertical=1, min_horizontal=1; test_passage_clearance passes   |
| PHYS-03     | 22-02       | physics-schema.json updated with 16x16 base values                  | SATISFIED | schema v0.2.0: tile_size=16, hitbox_px=[10,14], all tile-units halved; test_physics_schema_updated passes |

**Note on ENT-03 text discrepancy:** REQUIREMENTS.md states "32x32 collision, 32x32 visual" but the phase RESEARCH.md (D-04) documents the authoritative decision as 24x28 (same proportional overhang approach as the player). The PLAN, implementation, and tests all consistently use 24x28. The REQUIREMENTS.md text was written before the design decision was finalized and is slightly stale, but the intent (proportional collision for the boss) is fully satisfied.

**Orphaned requirements check:** No requirements mapped to Phase 22 in REQUIREMENTS.md that are missing from the plans. CONV-01, CONV-02, CONV-03 are mapped to Phase 23 (pending) — not orphaned here.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | — | — | — | — |

No TODOs, FIXMEs, hardcoded magic numbers in spawn paths, empty return stubs, or disconnected props found in the modified files.

---

### Human Verification Required

None — all observable truths are verifiable programmatically and test suite confirms correct behavior.

---

### Gaps Summary

No gaps. All must-haves are implemented, substantive, wired, and confirmed passing by the automated test suite (352 tests pass, 3 skipped).

---

_Verified: 2026-04-08_
_Verifier: Claude (gsd-verifier)_
