---
phase: 12-screen-size-expansion
verified: 2026-03-29T00:00:00Z
status: gaps_found
score: 8/11 must-haves verified
gaps:
  - truth: "No hardcoded 128 values remain in production Python files (src/ and main.py)"
    status: partial
    reason: "map.py open_gates and close_gates still use hardcoded '+ 16' tile range instead of VIEWPORT_W // TILE_SIZE derived value. Commit 6521cde correctly fixed this, but commit f512bc6 (from merged worktree) reverted the fix."
    artifacts:
      - path: "src/level/map.py"
        issue: "open_gates uses 'tx_start + 16' and 'ty_start + 16' instead of VIEWPORT_W//TILE_SIZE (40) and VIEWPORT_H//TILE_SIZE (22). Gate scan only covers 16 tiles (~128px) not 40 tiles (~320px)."
    missing:
      - "In open_gates: add 'tiles_w, tiles_h = VIEWPORT_W // TILE_SIZE, VIEWPORT_H // TILE_SIZE' and replace '+ 16' with '+ tiles_w' / '+ tiles_h'"
      - "In close_gates collision scan: same replacement"
      - "In close_gates tilemap scan loops: replace 'ty_start + 16' / 'tx_start + 16' with VIEWPORT_H//TILE_SIZE and VIEWPORT_W//TILE_SIZE"
  - truth: "Tests pass with updated room dimensions"
    status: failed
    reason: "3 test failures caused by commit f512bc6 reverting test fixture updates that commit 7e5a310 had correctly applied. The merge of worktree-agent-a907c741 introduced a reimplementation that reverted the Phase 12 test fixes."
    artifacts:
      - path: "tests/test_phase05_nyquist.py"
        issue: "test_room_spawn_update still asserts 'game.cam_x == 128' and moves player to x=200, both values from the pre-Phase-12 128x128 world. Should use VIEWPORT_W=320 as boundary."
      - path: "tests/test_phase05_gaps.py"
        issue: "test_duplication_prevention asserts 'game.cam_x == 128' after moving player to x=150. test_combat_projectile_collision fails due to missing entity/enemy reset that 7e5a310 added but f512bc6 removed."
    missing:
      - "tests/test_phase05_nyquist.py: restore 'game.player.x = VIEWPORT_W + 50' and 'assert game.cam_x == VIEWPORT_W'"
      - "tests/test_phase05_gaps.py test_duplication_prevention: restore 'game.player.x = 350' and 'assert game.cam_x == VW' (320)"
      - "tests/test_phase05_gaps.py test_spawning_logic: restore 'game.enemies = []' and 'game.level_map.entities = []' resets before spawn call"
human_verification:
  - test: "Run the game with 'python main.py'"
    expected: "Window opens at 320x192 pixels. Bottom 16px shows a dark blue HUD bar with red HP pips on the left and a green juice meter on the right. Game world renders in the top 320x176 area. Taking damage causes screen shake but HUD does not move."
    why_human: "Visual appearance, window size, HUD layout, and shake behavior cannot be verified programmatically without running Pyxel."
  - test: "Walk the player from Level_0 into Level_1 (cross right boundary)"
    expected: "Room transition slides smoothly to the next room. No visual glitch or HUD bleed."
    why_human: "Room transition feel and absence of rendering artifacts require visual confirmation."
---

# Phase 12: Screen Size Expansion — Verification Report

**Phase Goal:** Expand display from 128x128 to 320x192 with Super Metroid-style 16px bottom HUD strip, 320x176 game viewport, central screen constants, and updated LDtk assets
**Verified:** 2026-03-29
**Status:** gaps_found — 2 of 11 truths failed; 3 test failures; 1 functional regression in map.py gate scans
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All screen dimensions derive from named constants in constants.py | VERIFIED | SCREEN_W=320, SCREEN_H=192, VIEWPORT_W=320, VIEWPORT_H=176, HUD_H=16, CULL_MARGIN=16 all present in constants.py |
| 2 | Camera clamps to VIEWPORT_W/VIEWPORT_H (320x176), not SCREEN_W/SCREEN_H (320x192) | VERIFIED | world.py: SCREEN_W=VIEWPORT_W, SCREEN_H=VIEWPORT_H; camera math uses these |
| 3 | No hardcoded 128 values remain in production Python files | PARTIAL | `grep -rn "\b128\b" src/ main.py` returns CLEAN; however map.py gate scan loops use hardcoded `+ 16` (128px / 8 = 16 tiles) — a semantic equivalent that was correctly replaced by commit 6521cde but reverted by f512bc6 |
| 4 | Entity culling boundaries use VIEWPORT_W/VIEWPORT_H constants | VERIFIED | effects.py: `cam_x + VIEWPORT_W`, boss.py: `cam_x + VIEWPORT_W + CULL_MARGIN`, projectile.py: same pattern |
| 5 | Tests pass with updated room dimensions | FAILED | 3 failures: test_phase05_nyquist::test_room_spawn_update, test_phase05_gaps::test_duplication_prevention, test_phase05_gaps::test_combat_projectile_collision. Root cause: commit f512bc6 reverted fixtures that commit 7e5a310 had correctly updated. |
| 6 | Game world is clipped to the top 320x176 area — no entity bleeds into the HUD strip | VERIFIED | main.py draw() Phase 1: `pyxel.clip(0, 0, VIEWPORT_W, VIEWPORT_H)` confirmed |
| 7 | HUD strip renders at y=176..192 with HP pips and juice meter | VERIFIED | `_draw_hud()` exists; `hud_y = VIEWPORT_H`; HP pip loop and juice meter bar both present |
| 8 | HUD does not shake during screen shake | VERIFIED | clip reset `pyxel.clip()` and camera reset `pyxel.camera()` called before `_draw_hud()` in Phase 2 |
| 9 | Victory text is centered for the 320x176 viewport | VERIFIED | `box_x = self.cam_x + (VIEWPORT_W - box_w) // 2` confirmed |
| 10 | entity-schema.json declares default_room_size as [320, 176] | VERIFIED | `[320, 176]` confirmed; variable_rooms_note updated; date 2026-03-29 |
| 11 | cave.ldtk uses 320x176 as default level dimensions + all 8 levels resized | VERIFIED | worldGridWidth=320, worldGridHeight=176, defaultLevelWidth=320, defaultLevelHeight=176; all 8 levels at pxWid=320, pxHei=176 with recalculated worldX/worldY |

**Score:** 8/11 truths verified (2 failed, 1 partial with functional gap)

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/core/constants.py` | SCREEN_W, SCREEN_H, VIEWPORT_W, VIEWPORT_H, HUD_H, CULL_MARGIN | VERIFIED | All 6 constants present with correct values |
| `src/level/world.py` | WorldManager using VIEWPORT_W/VIEWPORT_H for camera math | VERIFIED | Imports VIEWPORT_W/VIEWPORT_H; SCREEN_W=VIEWPORT_W, SCREEN_H=VIEWPORT_H |
| `tests/test_screen_constants.py` | Constant consistency validation | VERIFIED | 9 tests all passing; includes SCREEN_H == VIEWPORT_H + HUD_H invariant |
| `main.py` | Draw pipeline with clip, camera reset, HUD rendering | VERIFIED | 3-phase draw, _draw_hud, clip/camera reset all present |
| `main.py` | `_draw_hud` method | VERIFIED | Present with hud_y=VIEWPORT_H, HP pips, juice meter |
| `assets/entity-schema.json` | default_room_size [320, 176] | VERIFIED | Confirmed |
| `assets/cave.ldtk` | defaultLevelWidth 320 | VERIFIED | All global and per-level dimensions updated |
| `export_tilemap_csv.py` | Uses VIEWPORT_W (no hardcoded 128) | VERIFIED | `VIEWPORT_W // TILE_SIZE` and `VIEWPORT_H // TILE_SIZE` |
| `tests/test_phase05_nyquist.py` | Updated for 320x176 room transition | FAILED | Still contains `game.player.x = 200` and `assert game.cam_x == 128` — pre-Phase-12 values |
| `tests/test_phase05_gaps.py` | Updated for 320px room boundary | FAILED | test_duplication_prevention uses x=150 and asserts cam_x==128 |
| `src/level/map.py` | Gate scan uses VIEWPORT-derived tile count | STUB | open_gates/close_gates use hardcoded `+ 16` (should be VIEWPORT_W//TILE_SIZE=40, VIEWPORT_H//TILE_SIZE=22) |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/core/constants.py` | `src/level/world.py` | `from src.core.constants import VIEWPORT_W, VIEWPORT_H` | WIRED | Line 2 of world.py |
| `src/core/constants.py` | `main.py` | `from src.core.constants import SCREEN_W, ...` | WIRED | Line 6-7 of main.py includes SCREEN_W, SCREEN_H, VIEWPORT_W, VIEWPORT_H, HUD_H, CULL_MARGIN, JUICE_MAX |
| `src/core/constants.py` | `src/entities/effects.py` | `from src.core.constants import VIEWPORT_W, VIEWPORT_H` | WIRED | Line 3 of effects.py |
| `main.py draw()` | `main.py _draw_hud()` | `pyxel.clip() + pyxel.camera() + self._draw_hud()` | WIRED | Pattern confirmed in draw() Phase 2 and Phase 3 |
| `src/core/constants.py` | `main.py _draw_hud()` | `hud_y = VIEWPORT_H` | WIRED | Line 576 of main.py |
| `assets/entity-schema.json` | `PML-to-LDtk converter` | `default_room_size.*320.*176` | WIRED | Pattern confirmed in schema; converter docs reference schema |

---

## Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `main.py _draw_hud()` | `self.player.hp`, `self.player.max_hp` | `Player` object updated each frame | Yes — live player state | FLOWING |
| `main.py _draw_hud()` | `self.slime.juice` | `Slime` object updated each frame | Yes — live slime state | FLOWING |
| `main.py _draw_hud()` | `JUICE_MAX` | `src.core.constants` | Yes — constant value 200.0 | FLOWING |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 6 screen constants correct | `python -c "from src.core.constants import SCREEN_W, SCREEN_H, VIEWPORT_W, VIEWPORT_H, HUD_H, CULL_MARGIN; assert all([SCREEN_W==320,SCREEN_H==192,VIEWPORT_W==320,VIEWPORT_H==176,HUD_H==16,CULL_MARGIN==16]); print('OK')"` | OK | PASS |
| Zero hardcoded 128 (grep) | `grep -rn "\b128\b" --include="*.py" src/ main.py` | CLEAN | PASS |
| Screen constants tests | `python -m pytest tests/test_screen_constants.py -q` | 9 passed | PASS |
| World manager tests | `python -m pytest tests/test_world_manager.py -q` | 22 passed | PASS |
| cave.ldtk global dims | `python -c "import json; d=json.load(open('assets/cave.ldtk')); assert d['defaultLevelWidth']==320"` | OK | PASS |
| entity-schema.json room size | `python -c "import json; d=json.load(open('assets/entity-schema.json')); assert d['level']['default_room_size']==[320,176]"` | OK | PASS |
| Full test suite | `python -m pytest tests/ -q` | 3 failed (229 passed) + 3 pre-existing bubble_shield fails | FAIL |
| map.py gate tile range | code inspection of open_gates / close_gates | Hardcoded `+ 16` present | FAIL |

---

## Requirements Coverage

The D-0x IDs are Phase 12-specific design decisions defined in `12-CONTEXT.md`, not entries in REQUIREMENTS.md (which uses MAP/ABL/SYS namespacing). Requirements.md has no D-0x entries and no Phase 12 traceability row — these IDs are internal design constraints for this phase only.

| Requirement | Plan(s) | Description | Status | Evidence |
|-------------|---------|-------------|--------|----------|
| D-01 | 12-01 | Display size = 320x192 via pyxel.init(320, 192) | SATISFIED | `pyxel.init(SCREEN_W, SCREEN_H)` where SCREEN_W=320, SCREEN_H=192 |
| D-02 | 12-01 | Game viewport = 320x176 (40x22 tiles) | SATISFIED | VIEWPORT_W=320, VIEWPORT_H=176 defined and used as camera bounds |
| D-03 | 12-02 | HUD strip = 16px fixed at bottom | SATISFIED | `pyxel.clip(0,0,VIEWPORT_W,VIEWPORT_H)` clips game; HUD_H=16 |
| D-04 | 12-02 | HUD content = HP pips + juice meter | SATISFIED | _draw_hud() renders both; confirmed wired to live player/slime state |
| D-05 | 12-01, 12-03 | Standard rooms = 320x176 | SATISFIED | WorldManager camera math uses VIEWPORT dims; cave.ldtk levels at 320x176 |
| D-06 | 12-03 | Large rooms use multiples like 320x352 | SATISFIED | Schema variable_rooms_note documents this; cave.ldtk supports variable sizes |
| D-07 | 12-03 | PML-to-LDtk converter updated with 320x176 | SATISFIED | PML-to-LDtk Converter.md created with 320x176 spec; entity-schema.json updated |
| D-08 | 12-01 | Central constants in constants.py | SATISFIED | All 6 constants present with correct values |
| D-09 | 12-01 | Replace ALL hardcoded 128 values | PARTIAL | grep is CLEAN; but map.py gate scans use hardcoded +16 tiles (semantic equivalent of 128px / 8) — functionally wrong for 320px rooms |
| D-10 | 12-01 | Pyxel default auto-scaling | SATISFIED | No explicit scale factor in pyxel.init call |

---

## Anti-Patterns Found

| File | Location | Pattern | Severity | Impact |
|------|----------|---------|----------|--------|
| `src/level/map.py` | `open_gates()` lines ~175-178 | `tx_start + 16` / `ty_start + 16` hardcoded tile range | Blocker | Gate scan covers only 16 tiles (~128px width) instead of 40 tiles (~320px). Boss gates in rooms wider than 128px will fail to open/close correctly. |
| `src/level/map.py` | `close_gates()` lines ~184-197 | Same `+ 16` pattern in both collision scan and tilemap scan | Blocker | Same impact as above — affects both `close_gates` and `open_gates` |
| `tests/test_phase05_nyquist.py` | `test_room_spawn_update` line 80-83 | `game.player.x = 200` / `assert game.cam_x == 128` | Blocker | Test asserts pre-Phase-12 128px room boundary; will fail when run; masks regression |
| `tests/test_phase05_gaps.py` | `test_duplication_prevention` | `game.player.x = 150` / `assert game.cam_x == 128` | Blocker | Same — pre-Phase-12 values that break with 320px rooms |
| `tests/test_phase05_gaps.py` | `test_spawning_logic` | Missing `game.enemies = []` and `game.level_map.entities = []` before spawn call | Blocker | Spawn test may count pre-existing enemies; assertion `len(game.enemies) == 2` will be wrong |

### Root Cause: Worktree Merge Regression

All three test failures and the map.py gate scan regression share a single root cause. Commit `7e5a310` correctly fixed these issues. Commit `f512bc6`, produced by a second worktree agent working independently, was a reimplementation that did not include those fixes. The merge commit `a4271f0` (merging `worktree-agent-a907c741`) landed `f512bc6` as the final state, overwriting the correct `7e5a310` changes. The SUMMARY for 12-01 claims these were fixed but the current HEAD does not reflect that.

---

## Human Verification Required

### 1. Window size and HUD visual

**Test:** Run `python main.py`
**Expected:** Window opens at approximately 320x192 pixels (auto-scaled by Pyxel). Bottom 16px shows a dark blue bar. Left side of bar has red/gray HP pip squares. Right side has a green-filled juice meter bar.
**Why human:** Window dimensions, color rendering, and HUD layout require visual confirmation.

### 2. Screen shake stability

**Test:** Run `python main.py`, walk into an enemy or boss projectile to take damage.
**Expected:** Game world shakes during invulnerability period but the HUD bar remains completely fixed at the bottom of the screen.
**Why human:** The clip-reset + camera-reset pipeline is verified in code, but the actual visual stability during shake can only be confirmed by watching the game run.

### 3. Room transition rendering

**Test:** Cross a room boundary through a door.
**Expected:** Smooth Metroid-style slide transition. No entities visually entering the HUD area during the transition. HUD remains stable throughout.
**Why human:** Real-time animation behavior and absence of rendering artifacts require human observation.

---

## Gaps Summary

Phase 12 is largely complete and well-implemented. The constants infrastructure (D-08), draw pipeline restructure (D-03/D-04), asset updates (D-05/D-06/D-07), and the vast majority of the magic-number elimination (D-09) are all verified at full depth (exist, substantive, wired, data-flowing).

Two issues block full goal achievement:

**Gap 1 — map.py gate scan regression (D-09):**
`open_gates()` and `close_gates()` use `+ 16` as the tile range, covering only 16 tiles (128px). With 320x176 rooms being 40x22 tiles, boss gates placed beyond tile 16 (x > 128) will not be found or cleared. The correct fix (`VIEWPORT_W // TILE_SIZE` = 40) was implemented in commit `6521cde` but reverted by the worktree merge commit `f512bc6`. This is a functional bug affecting boss fight gate mechanics in the new room size.

**Gap 2 — test regression (3 failures):**
`test_phase05_nyquist::test_room_spawn_update`, `test_phase05_gaps::test_duplication_prevention`, and `test_phase05_gaps::test_combat_projectile_collision` all fail because `f512bc6` reverted test fixture updates. These tests now assert 128px room boundaries. This breaks the verification contract of D-09 (no hardcoded 128 values) and makes CI misleading.

Both gaps have identical root cause and can be resolved in a single targeted commit restoring the three changes from `7e5a310` that were lost in the merge.

---

_Verified: 2026-03-29_
_Verifier: Claude (gsd-verifier)_
