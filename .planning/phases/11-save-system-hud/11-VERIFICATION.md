---
phase: 11-save-system-hud
verified: 2026-03-31T00:00:00Z
status: passed
score: 12/12 must-haves verified
gaps:
  - truth: "Save rooms shown green, boss rooms red, normal visited rooms gray on map"
    status: resolved
    reason: "get_room_color() now maps cell coordinates to level IDs and looks up room_types. Save=green(11), boss=red(8), normal=gray(5)."
  - truth: "LDtk rooms contain at least 2 ENERGY items and 2 MISSILE items (D-14, SYS-04)"
    status: resolved
    reason: "2 EnergyTank (Level_1, Level_2) and 2 MissileTank (Level_1, Level_2) placed in LDtk and exported."
human_verification:
  - test: "Visual playtest: Title screen, save point interaction, mini-map HUD, pause screen, death animation"
    expected: "JELLY ROLL title shows on launch; NEW GAME starts play; HP pips + mini-map + juice bar visible in HUD strip; ESC opens pause overlay with map/stats/abilities/menu; player death triggers freeze+fade then respawns at save room."
    why_human: "Pyxel rendering requires visual inspection. Cannot be verified programmatically without running the game."
  - test: "Mini-map visited room tracking: move to adjacent rooms and verify map fills in"
    expected: "Each new room entered causes a new cell to appear on the mini-map. Current room blinks white/black every ~15 frames."
    why_human: "Dynamic rendering behavior during gameplay requires running the game and interactive input."
  - test: "Save persistence round-trip: save via save point, quit to title, continue"
    expected: "After saving, selecting CONTINUE on title screen spawns player at save room with saved abilities/HP/juice."
    why_human: "End-to-end persistence requires running the game through multiple states."
---

# Phase 11: Save System & HUD Verification Report

**Phase Goal:** Save/load persistence, title screen, death rollback, mini-map HUD, pause screen
**Verified:** 2026-03-31
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | SaveManager.save() serializes player abilities, max_hp, max_juice, collected_iids, event_flags, save_room_id, visited_rooms to JSON | VERIFIED | `save_manager.py:20-53` — all fields serialized via json.dump; round-trip tests pass |
| 2  | SaveManager.load() returns dict with all saved fields or None if no file | VERIFIED | `save_manager.py:56-62` — returns json.load or None on missing file |
| 3  | SavePoint entity detects player proximity via AABB overlap | VERIFIED | `save_point.py:18-24` — is_player_near() checks all 4 AABB conditions |
| 4  | Capacity upgrade caps enforced at 5 HP and 300 juice | VERIFIED | `items.py:23,26` — min(x + 1, MAX_HP_CAP) and min(x + 50, MAX_JUICE_CAP); `restore_from_save` lines 838,847 also apply caps |
| 5  | Game starts on TITLE screen showing Continue (if save exists) or New Game | VERIFIED | `main.py:152` sets game_state="TITLE" on init; `_update_title/_draw_title` check `SaveManager.exists()` |
| 6  | On death (HP=0), game enters DEAD state with 30-frame freeze + 30-frame fade then reverts to last save | VERIFIED | `main.py:437-438` enters DEAD state; `_update_death:958-969` counts frames then calls `SaveManager.load()`; no save returns to TITLE |
| 7  | ESC opens pause, second ESC closes pause, frame consumed | VERIFIED | `input.py:12` maps "pause" to KEY_ESCAPE; `main.py:443` sets PAUSED; `_update_pause:983-989` returns on btnp("pause") |
| 8  | Mini-map in HUD strip shows visited rooms as colored rectangles between HP pips and juice bar | VERIFIED | `main.py:782-790` — `_draw_minimap` called from `_draw_hud` at center of HUD strip with white border |
| 9  | Current room blinks white/black every 15 frames on mini-map | VERIFIED | `get_room_color:97-99` — frame % 30 < 15 returns 7 (white) else 0 (black) |
| 10 | Save rooms shown green, boss rooms red, normal visited rooms gray on map | FAILED | `get_room_color:100-102` — room_types parameter accepted but never used; all non-current cells unconditionally return 5 (gray) |
| 11 | ESC opens pause screen with macro-map, stats, ability row, and Resume/Save/Quit menu | VERIFIED | `_draw_pause_overlay:1022-1079` — macro-map at 120x60, HP/JUICE stats, DSH/SHD/BST/RAM/CHG ability row, RESUME/SAVE/QUIT menu |
| 12 | LDtk rooms contain at least 2 ENERGY items and 2 MISSILE items (D-14, SYS-04) | FAILED | Grep of all simplified level data.json and cave.ldtk returns 0 matches for ENERGY and MISSILE. Documented gap in 11-03-SUMMARY. |

**Score:** 10/12 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/core/save_manager.py` | SaveManager class with save, load, exists, delete static methods | VERIFIED | All 4 methods + `_get_save_path()` helper present. json.dump/load wired. |
| `src/entities/save_point.py` | SavePoint entity with proximity check, pulse animation, prompt state | VERIFIED | is_player_near(), on_save(), update(), draw() all present and substantive. |
| `tests/test_save_system.py` | Unit tests for save/load round-trip, capacity caps, SavePoint proximity, state machine, pause toggle | VERIFIED | 410 lines, 8 test classes: TestSaveManager, TestSaveRoundTrip, TestCapacityCaps, TestSavePoint, TestGameStates, TestRestoreFromSave, TestPauseToggle, TestCapacityUpgradeCaps |
| `main.py` | Extended state machine with TITLE/PLAYING/PAUSED/DEAD/WON states | VERIFIED | All 5 states wired in update() and draw() dispatch; contains `_draw_title`, `restore_from_save`, `SavePoint` spawning |
| `tests/test_minimap.py` | Unit tests for mini-map room scaling, color logic, visited-only filtering | VERIFIED | 82 lines, 4 test classes: TestClassifyRoomTypes, TestComputeMapRects, TestMapColors, TestVisitedFilter |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `save_manager.py` | `save.json` | json.dump / json.load | WIRED | Lines 53, 62 |
| `save_point.py` | player proximity | is_player_near AABB | WIRED | Lines 18-24 |
| `main.py:_update_death` | `save_manager.py:SaveManager.load` | death rollback | WIRED | `main.py:963` calls `SaveManager.load()` |
| `main.py:spawn_enemies` | `save_point.py:SavePoint` | entity instantiation from LDtk | WIRED | `main.py:282-283` — `elif etype == "SavePoint": self.save_points.append(SavePoint(ex, ey))` |
| `main.py:_update_title` | `SaveManager.exists/load` | title checks save, loads on Continue | WIRED | Lines 888, 911 |
| `main.py:_draw_minimap` | `self.world.levels` | iterates LevelBounds for room rects | WIRED | `main.py:815` — `compute_map_rects(self.world.levels, ...)` |
| `main.py:_draw_pause_overlay` | `main.py:_draw_minimap` | macro-map reuses map rendering | WIRED | `main.py:1032` calls `self._draw_minimap(map_center_x, ...)` |
| `main.py:_update_pause` | `SaveManager.save` | Save option triggers save | WIRED | `main.py:1011` — `SaveManager.save(self)` |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `_draw_minimap` | `self.rooms_visited` | `rooms_visited.add(snap_to_grid(...))` on room enter (lines 230, 400, 650) | Yes — populated during gameplay | FLOWING |
| `_draw_minimap` | `self.room_types` | `classify_room_types(self.world.levels, self.level_map.entities)` in reset() (line 233) | Yes — but no SavePoint/BossMole entities currently in LDtk levels, so all rooms classify as "normal" | PARTIAL — data flows but room types are all "normal" due to SYS-04 gap |
| `_draw_title` | `SaveManager.exists()` | Reads save.json from disk | Yes — real file check | FLOWING |
| `_update_death` | `SaveManager.load()` | Reads save.json from disk | Yes — returns None or dict | FLOWING |
| `restore_from_save` | `data["player"]`, `data["slime"]` | SaveManager.load() dict | Yes — matches save structure | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All save system tests pass | `python -m pytest tests/test_save_system.py tests/test_minimap.py -x -q` | 40 passed in 0.41s | PASS |
| Full test suite regression-free | `python -m pytest tests/ -x -q` | 286 passed, 3 skipped in 11.87s | PASS |
| SaveManager serializes to JSON | Pattern verified in save_manager.py | json.dump/json.load present with correct fields | PASS |
| Items enforce capacity caps | `items.py:23,26` | min(x+1, MAX_HP_CAP) and min(x+50, MAX_JUICE_CAP) | PASS |
| D-18: close_gates uses VIEWPORT_W/VIEWPORT_H | `map.py:187` | `tiles_w, tiles_h = VIEWPORT_W // TILE_SIZE, VIEWPORT_H // TILE_SIZE` — no hardcoded +16 | PASS |

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| SYS-01 | 11-01, 11-02 | Save Rooms/Checkpoints with JSON persistence | SATISFIED | SaveManager.save/load/exists/delete, SavePoint entity, title screen Continue/New Game, death rollback, restore_from_save |
| SYS-02 | 11-03 | Mini-map HUD bar (showing room grid and current location) | PARTIAL | Mini-map renders in HUD with viewport-cell tracking. Current room blinks. But save/boss room color-coding not implemented (get_room_color stub). |
| SYS-03 | 11-02, 11-03 | Pause Screen with full Macro-Map view | SATISFIED | Full _draw_pause_overlay with macro-map, HP/JUICE stats, ability row, RESUME/SAVE/QUIT menu. ESC toggle wired. Save-only-in-save-room logic present. |
| SYS-04 | 11-01, 11-02 | Heart Containers and Juice Capacity upgrade items | PARTIAL — CODE READY, CONTENT MISSING | MAX_HP_CAP=5 / MAX_JUICE_CAP=300 constants defined. ENERGY/MISSILE items enforced in items.py. Cap applied in restore_from_save. However, 0 ENERGY and 0 MISSILE entities exist in LDtk world data — capacity upgrade items are not accessible to the player in-game. |

No orphaned requirements — all 4 phase 11 IDs (SYS-01, SYS-02, SYS-03, SYS-04) appear in plan frontmatter.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `main.py` | 100-102 | `get_room_color` accepts `room_types` dict but ignores it — `# Look up room type` comment with no implementation, falls through to `return 5` | Blocker | Save rooms will not appear green (11) and boss rooms will not appear red (8) on the mini-map. Color-coding is core to SYS-02 map readability. |
| `main.py` | 106 | `JUICE_MAX` imported but only used in Game constants import line — `_draw_hud` correctly uses `self.slime.max_juice` | Info | Dead import. No functional impact. |

### Human Verification Required

#### 1. Visual Playtest — Title Screen, HUD, Pause Screen

**Test:** Run `python main.py`. Observe title screen shows "JELLY ROLL" + "NEW GAME". Press Z to start. Verify bottom 16px HUD strip shows HP pips (left), mini-map with white border (center), juice bar (right).
**Expected:** Title renders correctly. HUD elements occupy correct positions. Mini-map shows current room blinking.
**Why human:** Pyxel rendering requires live visual inspection.

#### 2. Save Point Interaction

**Test:** Walk onto a SavePoint entity in a save room. Observe prompt changes from "SAVE?" to "SAVED!" after pressing UP.
**Expected:** Yellow/orange pulsing pedestal visible. "SAVE?" prompt appears on approach. UP key triggers save and shows "SAVED!" for ~1 second.
**Why human:** Requires LDtk SavePoint entity to be placed in the world, plus interactive gameplay.

#### 3. Death Animation and Rollback

**Test:** Let an enemy kill the player. Observe death sequence and respawn location.
**Expected:** ~0.5s freeze (game world frozen), ~0.5s fade to black, then respawn at last save room with full HP/juice. If no save, return to title screen.
**Why human:** Real-time animation and state transition require running the game.

#### 4. Save Persistence Round-Trip

**Test:** After saving at a save point, press ESC, select QUIT. On title, verify "CONTINUE" option is present. Select it.
**Expected:** "CONTINUE" appears only when save.json exists. Selecting it loads saved state with correct HP/juice/abilities and spawns at save room.
**Why human:** End-to-end persistence test spans multiple sessions and game states.

### Gaps Summary

Two gaps block full goal achievement:

**Gap 1 — get_room_color() room type lookup not implemented (blocker for SYS-02):**
The function `get_room_color` in main.py (lines 86-102) accepts a `room_types` dict parameter and documents the intent to color save rooms green and boss rooms red, but the implementation is incomplete. The code has a comment `# Look up room type by finding which level contains this cell` followed directly by `return 5` with no actual lookup. All visited non-current cells always render as gray (5). The fix is small: add a lookup that maps the cell_key coordinates back to a level ID via bounds check, then use `room_types[level_id]` to determine color. The tests in `test_minimap.py` were adapted to match the incomplete implementation (they only test that visited cells are gray, not that save/boss rooms have distinct colors).

**Gap 2 — SYS-04 capacity upgrade items not placed in LDtk world (content gap, not code gap):**
The code infrastructure is fully ready: ENERGY and MISSILE item types are handled in `items.py` with correct cap enforcement. However, 0 ENERGY and 0 MISSILE entities exist in any of the 5 LDtk level data files. This requires a manual LDtk editor session to place at least 2 ENERGY and 2 MISSILE entities in the world. This was documented as a known gap in 11-03-SUMMARY.md. Until placed, players cannot acquire the capacity upgrades and SYS-04 is technically unsatisfied in-game.

These two gaps are **independent**: Gap 1 requires a code fix in `get_room_color`; Gap 2 requires LDtk world authoring work.

---

_Verified: 2026-03-31_
_Verifier: Claude (gsd-verifier)_
