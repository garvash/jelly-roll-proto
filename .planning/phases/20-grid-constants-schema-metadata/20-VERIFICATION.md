---
phase: 20-grid-constants-schema-metadata
verified: 2026-04-08T00:00:00Z
status: passed
score: 6/6 must-haves verified
re_verification: false
---

# Phase 20: Grid Constants & Schema Metadata Verification Report

**Phase Goal:** The codebase operates on a uniform 16x16 tile grid with no SPRITE_SCALE indirection
**Verified:** 2026-04-08
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | TILE_SIZE equals 16 and SPRITE_SCALE is gone from the codebase | VERIFIED | `constants.py` line 2: `TILE_SIZE = 16`. No `SPRITE_SCALE` assignment anywhere; `ImportError` confirmed via runtime test and grep. Only reference is a comment in a constant string in `scripts/update_physics_schema.py` (not a definition). |
| 2 | Room dimensions are 20x11 tiles (320x176 pixels) and the game viewport renders at the correct size | VERIFIED | `VIEWPORT_W=320, VIEWPORT_H=176, TILE_SIZE=16` → `320//16=20, 176//16=11`. `entity-schema.json` `variable_rooms_note` states "20x11 tiles". `export_tilemap_csv.py` computes `width = VIEWPORT_W // TILE_SIZE` (20 tiles). |
| 3 | entity-schema.json grid_size is 16 and schema version is bumped to reflect the breaking change | VERIFIED | `entity-schema.json`: `"version": "2.0.0"`, `"grid_size": 16`. Runtime assertion confirmed. |
| 4 | All derived constants (SPRITE_SIZE, BOSS_SPRITE_SIZE, room tile counts) are consistent with 16x16 base | VERIFIED | `SPRITE_SIZE = 16` (direct constant), `BOSS_SPRITE_SIZE = 32` (direct constant), `TILE_EMPTY = (15, 15)` (256/16=16 tiles, max index 15). No derived formula exists — all are direct assignments. |
| 5 | Tests assert the 16x16 contract and all pass | VERIFIED | `test_sprite_scale.py`: 5 tests covering TILE_SIZE==16, SPRITE_SIZE==16, BOSS_SPRITE_SIZE==32, TILE_EMPTY==(15,15), SPRITE_SCALE ImportError. `test_schema.py`: version==2.0.0, grid_size==16. 36 tests pass across `test_sprite_scale.py`, `test_schema.py`, `test_screen_constants.py`. |
| 6 | No SPRITE_SCALE indirection remains in the constants layer | VERIFIED | `grep SPRITE_SCALE src/**/*.py` returns only a comment line in `src/core/constants.py` (the phase migration comment) and `tests/test_sprite_scale.py` (the ImportError guard test). Zero functional uses. |

**Score:** 6/6 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/core/constants.py` | 16x16 grid constants, no SPRITE_SCALE | VERIFIED | `TILE_SIZE = 16`, `SPRITE_SIZE = 16`, `BOSS_SPRITE_SIZE = 32`, `TILE_EMPTY = (15, 15)`. No `SPRITE_SCALE` definition. |
| `assets/entity-schema.json` | Schema v2.0.0 with grid_size 16 | VERIFIED | `"version": "2.0.0"`, `"grid_size": 16`, `variable_rooms_note` has "20x11 tiles", `tile_coords.description` has "16px tile grid". |
| `export_tilemap_csv.py` | CSV export with 16 tiles per row | VERIFIED | `tile_id = v * 16 + u`, comments state "320 / 16 = 20 tiles", "176 / 16 = 11 tiles", "256 pixels / 16 = 16 tiles per row". No `v * 32` present. |
| `tests/test_sprite_scale.py` | 16x16 contract tests | VERIFIED | 5 tests: TILE_SIZE==16, SPRITE_SIZE==16, BOSS_SPRITE_SIZE==32, SPRITE_SCALE ImportError, TILE_EMPTY==(15,15). All pass. |
| `tests/test_schema.py` | Schema version and grid_size assertions | VERIFIED | `test_schema_version_is_2_0_0` and `test_schema_grid_size_is_16` both present and passing. |
| `PML-to-LDtk Converter.md` | Updated 16px/20x11 room references | VERIFIED | `Tile size | 16px`, `20x11 tiles` for standard rooms, `20x22` for tall shafts, `40x11` for wide arenas. Zero `8px` occurrences. |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/core/constants.py` | All entity/level files | `from src.core.constants import` | WIRED | Entity files import `TILE_SIZE`, `SPRITE_SIZE`, `BOSS_SPRITE_SIZE` by name — values automatically pick up 16x16 values. |
| `assets/entity-schema.json` | `src/core/schema.py` | `schema.init()` at startup | WIRED | `test_schema.py` calls `schema.init("assets/entity-schema.json")` and 14 schema tests pass including version and grid_size assertions. |
| `tests/test_sprite_scale.py` | `src/core/constants.py` | Import assertions | WIRED | File imports `TILE_SIZE`, `SPRITE_SIZE`, `BOSS_SPRITE_SIZE`, `TILE_EMPTY` directly from constants. ImportError guard catches any reintroduction of `SPRITE_SCALE`. |
| `tests/test_schema.py` | `assets/entity-schema.json` | JSON load and assert | WIRED | `schema["version"] == "2.0.0"` and `schema["level"]["grid_size"] == 16` assertions present and verified passing. |

---

### Data-Flow Trace (Level 4)

Not applicable for this phase. All artifacts are constants files, schema JSON, a CSV export utility, and test files — none render dynamic data through a fetch/state cycle.

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Constants module exports correct values | `python -c "from src.core.constants import TILE_SIZE, SPRITE_SIZE, BOSS_SPRITE_SIZE, TILE_EMPTY; assert TILE_SIZE==16; assert SPRITE_SIZE==16; assert BOSS_SPRITE_SIZE==32; assert TILE_EMPTY==(15,15)"` | Exit 0 | PASS |
| SPRITE_SCALE is not importable | `python -c "try: from src.core.constants import SPRITE_SCALE; ... except ImportError: print('OK')"` | "OK" | PASS |
| Schema JSON is valid with correct values | `python -c "import json; d=json.load(open('assets/entity-schema.json')); assert d['version']=='2.0.0'; assert d['level']['grid_size']==16; assert '20x11' in d['level']['variable_rooms_note']"` | Exit 0 | PASS |
| export_tilemap_csv.py has 16-tile formula | `grep "v \* 16 + u" export_tilemap_csv.py` | 1 match | PASS |
| Phase contract tests pass | `python -m pytest tests/test_sprite_scale.py tests/test_schema.py tests/test_screen_constants.py -q` | 36 passed | PASS |
| Room tile dimensions compute correctly | `python -c "from src.core.constants import VIEWPORT_W, VIEWPORT_H, TILE_SIZE; assert VIEWPORT_W // TILE_SIZE == 20; assert VIEWPORT_H // TILE_SIZE == 11"` | Exit 0 | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| GRID-01 | 20-01, 20-02 | Game uses 16x16 as the base tile size (TILE_SIZE=16) | SATISFIED | `constants.py` line 2: `TILE_SIZE = 16`. Runtime verified. |
| GRID-02 | 20-01, 20-02 | SPRITE_SCALE indirection removed — sprites render at native 16x16 | SATISFIED | No `SPRITE_SCALE` definition anywhere in `src/`. ImportError test guards against reintroduction. |
| GRID-03 | 20-01, 20-02 | All derived constants (SPRITE_SIZE, BOSS_SPRITE_SIZE, room dimensions) updated | SATISFIED | `SPRITE_SIZE = 16`, `BOSS_SPRITE_SIZE = 32`, `TILE_EMPTY = (15, 15)` as direct constants. Room tile counts (20x11) correct. |
| GRID-04 | 20-01, 20-02 | Room dimensions are 20x11 tiles (320x176 pixels) in the new grid | SATISFIED | `320 // 16 = 20`, `176 // 16 = 11` — documented in schema `variable_rooms_note`, `export_tilemap_csv.py` comments, and `PML-to-LDtk Converter.md`. |
| LDTK-01 | 20-01, 20-02 | entity-schema.json grid_size updated to 16 | SATISFIED | `"grid_size": 16` in schema. Runtime and test-asserted. |
| LDTK-05 | 20-01, 20-02 | Schema version bumped to reflect breaking grid change | SATISFIED | `"version": "2.0.0"` (major bump). `test_schema_version_is_2_0_0` passes. |

All 6 phase-20 requirements are SATISFIED. Requirements LDTK-02, LDTK-03, LDTK-04 (LDtk project reconfiguration) are correctly deferred to Phase 21 — none are claimed by Phase 20 plans.

**Orphaned requirements check:** REQUIREMENTS.md Phase 20 traceability maps exactly GRID-01, GRID-02, GRID-03, GRID-04, LDTK-01, LDTK-05 to Phase 20 — all claimed by plans. No orphaned requirements.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/core/constants.py` | 70 | `JUICE_MIN_SCALE = 0.25 # 2x2 vs 8x8 (0.25 * 8 = 2)` — stale comment referencing old 8x8 math | Info | Comment only; `JUICE_MIN_SCALE` is a dimensionless scale ratio, not a tile size. Does not affect behavior. |
| `src/level/map.py` | 181 | `grid_size = 8  # 8px tile grid (D-14, verified in output.ldtk)` | Info | This local variable correctly reflects the existing `output.ldtk` file which still uses 8px grid. Phase 21 migrates the LDtk project. Not a Phase 20 gap. |
| `scripts/update_physics_schema.py` | 77 | String literal containing `"via SPRITE_SCALE=2"` in a doc note written to physics-schema.json | Info | String content in a script that generates JSON documentation. Not an import or functional dependency. Phase 22 (physics tuning) is the correct scope for this update. |

No blocker or warning-severity anti-patterns found. All Info items are stale comments or string literals in out-of-scope files.

---

### Human Verification Required

None. All success criteria for Phase 20 are verifiable programmatically. Visual rendering at 16x16 tile scale (gameplay feel) is Phase 21-22 scope after the LDtk project is reconfigured.

---

### ROADMAP Tracking Note

`ROADMAP.md` shows `20-02-PLAN.md` as not checked (`[ ]`). Both plans are complete and both SUMMARYs exist. This is a documentation tracking inconsistency — the ROADMAP was not updated when plan 02 completed. Not a code gap.

---

## Gaps Summary

No gaps. All 6 must-haves verified, all 6 requirements satisfied, all 5 key links confirmed wired, all behavioral spot-checks pass.

The three Info-severity items (`JUICE_MIN_SCALE` comment, `map.py` local `grid_size = 8`, `update_physics_schema.py` string literal) are each correctly scoped to Phase 21 or Phase 22 and do not block Phase 20's goal.

---

_Verified: 2026-04-08_
_Verifier: Claude (gsd-verifier)_
