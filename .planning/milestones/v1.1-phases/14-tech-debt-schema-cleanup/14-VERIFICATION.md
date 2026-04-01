---
phase: 14-tech-debt-schema-cleanup
verified: 2026-03-30T00:00:00Z
status: gaps_found
score: 16/17 must-haves verified
gaps:
  - truth: "slime.py has no hold_position method"
    status: failed
    reason: "hold_position method still exists at slime.py line 153. Plan 03 Summary incorrectly claimed it was already absent as pre-existing cleanup. In fact the method was never deleted and 4 tests in test_slime_hold.py actively test it — deleting it without updating those tests would break the suite."
    artifacts:
      - path: "src/entities/slime.py"
        issue: "def hold_position(self, direction, player_x, player_y, level_map) present at line 153"
      - path: "src/entities/slime.py"
        issue: "reposition() docstring at line 119 still references hold_position: 'Same position-finding logic as hold_position but does NOT set is_holding_position.'"
    missing:
      - "Delete hold_position method from src/entities/slime.py (lines 153 through end of method body)"
      - "Update reposition() docstring to remove hold_position reference (change to: 'Tap reposition without disabling follow (UAT gap fix).')"
      - "Update or delete test_slime_hold.py tests that call hold_position (test_hold_position_sets_flag, test_hold_position_right, test_hold_position_left, test_hold_position_cancels_punt)"
human_verification:
  - test: "Event door opens in-game after Mole boss defeat"
    expected: "Boss gate door (action='event', event_id='boss_defeated') becomes passable once the Mole is defeated"
    why_human: "No automated test exercises the full boss fight -> boss death -> event_flags['boss_defeated']=True -> room re-entry -> door.check_event_open flow in a running game"
  - test: "Runtime god-mode toggles fire correctly (Ctrl+1/2/3)"
    expected: "Pressing Ctrl+1 at runtime unlocks all abilities; Ctrl+2 grants invincibility; Ctrl+3 gives infinite juice. These are reset on game reset."
    why_human: "Key input requires a running Pyxel window; cannot be verified headlessly"
---

# Phase 14: Tech Debt Schema Cleanup — Verification Report

**Phase Goal:** Event-gated door system (add "event" action + event_id field, deprecate tile ID 4), fix map.py legacy gate scan, clean orphaned code, fix 6 test failures, verify Phase 10 ABL-02

**Verified:** 2026-03-30

**Status:** gaps_found

**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Door entity supports action='event' with an event_id field | VERIFIED | entity-schema.json line 81: `"event"` in enum; lines 90-95: `event_id` field defined |
| 2 | Boss defeat sets event_flags['boss_defeated']=True | VERIFIED | main.py line 389: `self.event_flags["boss_defeated"] = True` inside boss death handler |
| 3 | Event-gated doors open on room entry when their event flag is set | VERIFIED | main.py line 507: `door.check_event_open(self.event_flags)` after loading doors; map_entities.py line 38-42: check_event_open implementation |
| 4 | close_gates legacy scan uses VIEWPORT_W/VIEWPORT_H-derived tile counts, not hardcoded 16 | VERIFIED | map.py lines 197-198: `ty_start + tiles_h`, `tx_start + tiles_w`; no `+ 16` remaining in close_gates |
| 5 | Switch-triggered gates still work (close_gates/open_gates methods intact) | VERIFIED | map.py lines 176-200: open_gates and close_gates methods present and use tiles_w/tiles_h |
| 6 | DEBUG_ALL_ABILITIES constant no longer exists in constants.py | VERIFIED | grep for DEBUG_ALL_ABILITIES in src/ returns 0 matches |
| 7 | Player abilities all default to False in __init__ without any debug override | VERIFIED | player.py: DEBUG_ALL_ABILITIES block deleted; abilities (has_drill, has_dash, has_shield, has_shield_t2, has_boost) default to False |
| 8 | God-mode runtime toggles exist in src/core/debug.py with 3 tiers | VERIFIED | debug.py lines 9-11: god_abilities, god_invincible, god_infinite_juice all default to False; line 13: update() defined |
| 9 | debug.update() is called from Game.update() in main.py | VERIFIED | main.py line 14: `import src.core.debug as debug`; line 225: `debug.update()` |
| 10 | All 6 previously failing tests now pass | VERIFIED | pytest: 255 passed, 3 skipped — all previously failing tests (bubble shield, drill retcon, phase05 gaps, sprite scale) pass |
| 11 | Full test suite runs green (0 failures) | VERIFIED | `python -m pytest tests/ --tb=short` → 255 passed, 3 skipped, 0 failures |
| 12 | slime.py has no hold_position method | FAILED | hold_position method still present at slime.py line 153; reposition docstring still references it at line 119 |
| 13 | MAP-02 requirement text describes pml-to-ldtk pipeline with event-gated doors | VERIFIED | REQUIREMENTS.md: `[x] MAP-02: Room layouts driven by pml-to-ldtk pipeline with event-gated doors (replaces tile ID 4 boss gates). (2026-03-30)` |
| 14 | ABL-02 requirement text splits vertical gating (Phase 10) from infinite flight (Phase 11) | VERIFIED | REQUIREMENTS.md: `[x] ABL-02: CRACKED_V vertical gating via Drill Dive (down) and Slime Boost (up). Infinite flight capstone deferred to Phase 11 (requires SYS-04 Juice Capacity upgrades).` |
| 15 | entity-schema.json intgrid value 4 updated to event_marker semantics | VERIFIED | entity-schema.json line 25: `"4": { "name": "event_marker", "behavior": "collision+gate", ... }` |
| 16 | entity-schema.json version bumped | VERIFIED | entity-schema.json line 5: `"version": "0.3.0"` |
| 17 | CRACKED_V breaking via Drill Dive + Boost is verified as working | VERIFIED | constants.py lines 155-156: DRILL_CRACKED_V_COST=20.0, BOOST_CRACKED_V_COST=25.0; player.py lines 698-729: drill and boost CRACKED_V breaking; entity-schema.json intgrid 12: broken_by ["drill_dive", "slime_boost"] |

**Score:** 16/17 truths verified

---

## Required Artifacts

| Artifact | Status | Details |
|----------|--------|---------|
| `assets/entity-schema.json` | VERIFIED | action enum includes "event"; event_id field present (string, required=false); intgrid 4 = event_marker; version 0.3.0 |
| `src/entities/map_entities.py` | VERIFIED | Door.__init__ signature: `action=None, event_id=None`; check_event_open method at line 38 with `event_flags.get(self.event_id, False)` |
| `src/level/map.py` | VERIFIED | close_gates uses `tiles_w`/`tiles_h` (lines 197-198); no hardcoded +16 in method |
| `main.py` | VERIFIED | event_flags dict in reset() (line 96); boss death sets flag (line 389); door event check on room entry (line 507); Door instantiation passes action= and event_id= (lines 174-178); debug.update() called (line 225) |
| `tests/test_event_doors.py` | VERIFIED | 6 test methods in class format; all 6 pass |
| `src/core/debug.py` | VERIFIED | 3 flags default to False; update() with Ctrl+1/2/3 toggles |
| `src/core/constants.py` | VERIFIED | DEBUG_ALL_ABILITIES absent; all game constants intact |
| `src/entities/player.py` | VERIFIED | No DEBUG_ALL_ABILITIES block; imports debug module; checks debug.god_abilities at line 128 |
| `tests/test_debug.py` | VERIFIED | 5 tests all pass: 3 flag defaults, 1 player ability defaults, 1 constants check |
| `src/entities/slime.py` | FAILED | hold_position method NOT deleted (still at line 153); reposition docstring still references it (line 119) |
| `.planning/REQUIREMENTS.md` | VERIFIED | MAP-02 marked [x] with correct text; ABL-02 marked [x] with CRACKED_V + deferred infinite flight text |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| main.py | src/entities/map_entities.py | Door.check_event_open(self.event_flags) | WIRED | main.py line 507 calls check_event_open; map_entities.py line 38 implements it |
| main.py | event_flags dict | self.event_flags["boss_defeated"] = True on Mole death | WIRED | main.py line 389 |
| assets/entity-schema.json | src/entities/map_entities.py | Door schema defines action enum + event_id field | WIRED | Schema and Door class both define action/event_id |
| src/entities/player.py | src/core/debug.py | import debug; check debug.god_abilities in update | WIRED | player.py line 6: import; line 128: if debug.god_abilities |
| src/core/debug.py | pyxel key input | Ctrl+1/2/3 toggles in debug.update() | WIRED | debug.py lines 16-22: pyxel.btn(KEY_CTRL) + btnp checks |
| main.py | src/core/debug.py | Game.update() calls debug.update() | WIRED | main.py line 225 |

---

## Data-Flow Trace (Level 4)

Event door system data flow:

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| main.py event_flags | event_flags["boss_defeated"] | boss death handler (line 389) | Yes — set to True on Mole defeat | FLOWING |
| Door.check_event_open | event_flags.get(event_id) | passed by caller (main.py line 507) | Yes — reads live dict | FLOWING |
| Door.action / Door.event_id | LDtk customFields | main.py _load_room lines 174-175 | Yes — reads from entity data | FLOWING |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All event door tests pass | pytest tests/test_event_doors.py | 6 passed | PASS |
| All debug tests pass | pytest tests/test_debug.py | 5 passed | PASS |
| Full test suite green | pytest tests/ --tb=short | 255 passed, 3 skipped, 0 failures | PASS |
| close_gates uses tiles_w/tiles_h | grep "ty_start + tiles_h" map.py | line 197 matches | PASS |
| DEBUG_ALL_ABILITIES absent | grep "DEBUG_ALL_ABILITIES" src/ | 0 matches | PASS |
| event_flags wired in main.py | grep "event_flags" main.py | 3 occurrences (init, boss death, door check) | PASS |
| hold_position deleted from slime.py | grep "def hold_position" slime.py | Found at line 153 | FAIL |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| MAP-02 | 14-01-PLAN.md | Room layouts driven by pml-to-ldtk pipeline with event-gated doors | SATISFIED | REQUIREMENTS.md marked [x]; event door system implemented in main.py + map_entities.py |
| ABL-02 | 14-03-PLAN.md | CRACKED_V vertical gating verified (Phase 10); infinite flight deferred Phase 11 | SATISFIED | REQUIREMENTS.md marked [x]; DRILL_CRACKED_V_COST, BOOST_CRACKED_V_COST in constants.py; player.py lines 698-729 |

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| src/entities/slime.py | 119 | reposition() docstring references deleted method: "Same position-finding logic as hold_position" | Warning | Misleading documentation only; no runtime impact |
| src/entities/slime.py | 153 | def hold_position(...) still present despite Plan 03 requiring deletion | Warning | Dead code. Not called by any src/ or main.py code, but tested by test_slime_hold.py. Deleting it without updating tests would break 4 tests. |

---

## Human Verification Required

### 1. Event Door Opens In-Game After Boss Defeat

**Test:** Load the game, trigger the Mole boss encounter, defeat the Mole, then re-enter the room containing the event-gated door (action='event', event_id='boss_defeated').

**Expected:** The door should be open (passable) on room re-entry. If the door was previously blocking and now passable, the system is working end-to-end.

**Why human:** No automated test exercises the full boss fight -> boss death -> event_flags set -> room transition -> door.check_event_open flow in a running Pyxel game instance.

### 2. Runtime God-Mode Toggles (Ctrl+1/2/3)

**Test:** Run the game, press Ctrl+1 during gameplay, verify all abilities are now active. Press Ctrl+1 again to toggle off. Repeat for Ctrl+2 (invincibility) and Ctrl+3 (infinite juice).

**Expected:** Each Ctrl+N combination toggles the corresponding god-mode flag. Abilities reset to locked state on Ctrl+1 toggle-off. Game reset clears all flags.

**Why human:** Key input in debug.update() requires a running Pyxel window with frame-by-frame input polling. Cannot test headlessly.

---

## Gaps Summary

One gap blocks full phase goal achievement:

**Gap: hold_position not deleted from slime.py** — Plan 03 Truth 1 required deleting `hold_position` from `src/entities/slime.py`. The executing agent's SUMMARY (14-03-SUMMARY.md) incorrectly claimed the method was "already absent as pre-existing cleanup." The method is present at line 153 and the reposition docstring at line 119 still references it. Critically, 4 tests in `tests/test_slime_hold.py` actively call `slime.hold_position(...)`, so simply deleting the method would break the test suite. The fix requires coordinated deletion of the method AND update of those 4 tests (either convert to use `reposition` or delete the tests if `hold_position` was truly meant to be removed as orphaned code).

All other phase goals are fully achieved:
- Event-gated door system is complete and tested (6 tests pass)
- `DEBUG_ALL_ABILITIES` removed, god-mode debug module wired in
- All 6 previously failing tests now pass
- Full suite is green (255 passed, 3 skipped)
- `close_gates` scan fixed to use `tiles_w`/`tiles_h`
- Schema at v0.3.0 with event_marker, event_id field
- MAP-02 and ABL-02 requirements properly marked complete

---

*Verified: 2026-03-30*
*Verifier: Claude (gsd-verifier)*
