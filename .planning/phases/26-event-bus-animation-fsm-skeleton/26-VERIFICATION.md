---
phase: 26-event-bus-animation-fsm-skeleton
verified: 2026-04-12T16:30:00Z
status: human_needed
score: 10/10
overrides_applied: 0
human_verification:
  - test: "Run the game and move the player through IDLE, RUNNING, JUMPING, FALLING states"
    expected: "Player sprite frames look identical to v1.3 -- same two frames per state, same toggle cadence, no visual glitches"
    why_human: "Frame-for-frame visual parity cannot be fully verified by unit tests alone -- need to confirm the FSM-driven output looks correct in the actual game with real sprite rendering"
---

# Phase 26: Event Bus + Animation FSM Skeleton Verification Report

**Phase Goal:** Stand up `src/anim/` with an event bus and a generic animation FSM wired to the player's existing IDLE/RUN/JUMP/FALL states, replacing the hardcoded sprite frame toggle in `player.py:790`. No new animation content yet -- the skeleton just reproduces current behavior.
**Verified:** 2026-04-12T16:30:00Z
**Status:** human_needed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | src/anim/ package exists with event_bus.py, state_machine.py, anim_clip.py, anim_player.py, player_anim.py | VERIFIED | All 5 source files + __init__.py exist (180 total lines); `from src.anim import event_bus, anim_clip, anim_player, state_machine, player_anim` works |
| 2 | Player sprite frames driven by fsm.current_frame_u() instead of hardcoded toggle | VERIFIED | `grep "u = 16 + (pyxel.frame_count" player.py` returns empty; line 846: `u = self._anim.current_frame_u(self._anim_driver)` |
| 3 | Event bus emits all 17 ANIM-02 events from gameplay code | VERIFIED | 16 unique events in player.py + spit in slime.py = 17/17; 25 integration tests all pass |
| 4 | Debug subscriber tests confirm all events fire | VERIFIED | tests/test_event_bus.py has per-event integration tests + 3 pitfall guards; 25 tests pass |
| 5 | Player visually identical to v1.3 (frame-for-frame parity) | VERIFIED | 8 parity tests in test_anim.py cover RUNNING (6-tick toggle), JUMPING, FALLING, IDLE, and 6 fallback states; all pass |
| 6 | Hardcoded sprite frame toggle removed | VERIFIED | `grep "u = 16 + (pyxel.frame_count" player.py` and `grep "u = 32 # Use run1" player.py` both return empty |
| 7 | _update_anim_driver() is last call in Player.update() (D-14) | VERIFIED | Line 177: `self._update_anim_driver()` immediately follows `self.update_state()` at line 176; no code between it and method end |
| 8 | Driver is single instance mutated in place (D-16) | VERIFIED | PlayerAnimDriver constructed once at line 83; _update_anim_driver mutates fields in place; test_player_driver_is_single_instance confirms id() stability |
| 9 | Fusion/ability emit sites carry Phase 32 re-homing comments (D-11/D-12) | VERIFIED | 8 grep-able `# ANIM-02 emit; may move in Phase 32 per FUSION-DESIGN lock` comments covering 7 fusion events (boost_tap has 2 sites) |
| 10 | Asymmetric events fire exactly once per transition | VERIFIED | 4 prev-state snapshots (prev_facing, prev_wall_sliding, prev_dy, was_grounded) guard direction_change, wall_touch, fall_start, land; 3 pitfall-guard tests confirm |

**Score:** 10/10 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/anim/__init__.py` | empty package marker | VERIFIED | 1 line docstring |
| `src/anim/event_bus.py` | module-level subscribe/emit/reset | VERIFIED | 24 lines; subscribe, emit, reset functions; module-level _subscribers dict |
| `src/anim/anim_clip.py` | @dataclass(frozen=True, slots=True) AnimClip | VERIFIED | 18 lines; frames/durations/loop/events fields; __post_init__ length validation |
| `src/anim/anim_player.py` | AnimPlayer with set_clip/tick/current_u | VERIFIED | 34 lines; check-then-increment tick model; no pyxel import |
| `src/anim/state_machine.py` | AnimFSM rules-list evaluator | VERIFIED | 34 lines; construction-time clip_id validation; current_frame_u(driver) |
| `src/anim/player_anim.py` | PlayerAnimDriver + clips + rules + build_player_fsm() | VERIFIED | 69 lines; 4-field slotted dataclass; named constants; 3 rules + fallback |
| `src/entities/player.py` | FSM-driven draw, 16 event emits, _update_anim_driver | VERIFIED | Import at line 8-9; init at 83-84; 16 emit sites; draw at 846; driver at 823-834 |
| `src/entities/slime.py` | spit event emit | VERIFIED | Line 282: `event_bus.emit("spit")` |
| `tests/test_anim.py` | Unit + parity tests for anim package + player wiring | VERIFIED | 24 tests; covers AnimClip, AnimPlayer, AnimFSM, driver, and 8 Player parity tests |
| `tests/test_event_bus.py` | Integration tests for all 17 events + pitfall guards | VERIFIED | 25 tests; 4 unit + 18 integration + 3 pitfall guards |
| `tests/conftest.py` | autouse event_bus.reset + shared fixtures | VERIFIED | 55 lines; pyxel mock, reset fixture, mock_level, mock_slime |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| src/anim/state_machine.py | src/anim/anim_player.py | AnimFSM composes AnimPlayer | WIRED | Line 6: `from src.anim.anim_player import AnimPlayer` |
| src/anim/player_anim.py | src/anim/state_machine.py | build_player_fsm() returns AnimFSM | WIRED | Line 12: `from src.anim.state_machine import AnimFSM`; line 69: `return AnimFSM(...)` |
| src/entities/player.py | src/anim/player_anim.py | Player.__init__ calls build_player_fsm() + PlayerAnimDriver() | WIRED | Line 9: import; lines 83-84: construction |
| src/entities/player.py::update | player.py::_update_anim_driver | Last call of update() | WIRED | Line 177 immediately after line 176 update_state() |
| src/entities/player.py::draw | src/anim/state_machine.py::current_frame_u | draw() computes u via FSM | WIRED | Line 846: `u = self._anim.current_frame_u(self._anim_driver)` |
| src/entities/player.py (16 sites) | src/anim/event_bus.py | event_bus.emit() at gameplay transitions | WIRED | 16 unique events emitted inline at transition sites |
| src/entities/slime.py::Slime.spit | src/anim/event_bus.py | event_bus.emit('spit') | WIRED | Line 282: `event_bus.emit("spit")` |
| tests/test_event_bus.py | src/anim/event_bus.py | subscribe + emit round-trip in tests | WIRED | 25 tests all exercise subscribe/emit |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| player.py draw() | u (sprite offset) | self._anim.current_frame_u(self._anim_driver) | Yes -- AnimFSM walks rules, ticks AnimPlayer, returns clip frame u offset | FLOWING |
| player.py _update_anim_driver | _anim_driver fields | self.state, self.is_grounded, self.facing_right, self.dy | Yes -- player physics state flows to driver each frame | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Anim package tests pass | `python -m pytest tests/test_anim.py -x -q` | 24 passed in 0.08s | PASS |
| Event bus tests pass | `python -m pytest tests/test_event_bus.py -x -q` | 25 passed in 0.08s | PASS |
| Combined anim+event tests | `python -m pytest tests/test_anim.py tests/test_event_bus.py -x -q` | 49 passed in 0.16s | PASS |
| Physics regression | `python -m pytest tests/test_physics.py -x -q` | passed | PASS |
| Tuning livereach regression | `python -m pytest tests/test_tuning_livereach.py -x -q` | passed | PASS |
| Hardcoded toggle removed | `grep "u = 16 + (pyxel.frame_count" src/entities/player.py` | No matches | PASS |
| Full suite (minus pre-existing failure) | `python -m pytest -x -q` | 1 failed (test_ldtk_migration -- Phase 21 pre-existing), 197 passed | PASS (pre-existing) |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| ANIM-01 | 26-01 | src/anim/ package with event_bus.py, state_machine.py, anim_clip.py, anim_player.py, player_anim.py | SATISFIED | All 5 source files exist, substantive, wired, tested (24 unit tests) |
| ANIM-02 | 26-03 | Event bus emits all 17 transition events from gameplay code | SATISFIED | 16 events in player.py + spit in slime.py = 17/17; 25 integration tests confirm |
| ANIM-03 | 26-02 | Hardcoded sprite frame toggle replaced with AnimFSM-driven frame lookup | SATISFIED | Line 846 uses FSM; old toggle line gone; 8 parity tests prove frame-for-frame match |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| tests/test_ldtk_migration.py | 103 | Pre-existing test failure (Phase 21) | Info | Unrelated to Phase 26; no regression introduced |

No Phase 26 anti-patterns found. No TODOs, FIXMEs, placeholders, empty implementations, or stub returns in any Phase 26 files.

### Human Verification Required

### 1. Visual Parity Playthrough

**Test:** Run the game and move the player through IDLE, RUNNING, JUMPING, and FALLING states. Observe sprite frame transitions.
**Expected:** Player sprite frames look identical to v1.3 -- same two-frame run toggle cadence, same jump/fall frame, same idle frame. No visual glitches, no flickering, no missed frames.
**Why human:** Unit tests prove the FSM outputs correct u offsets in isolation, but visual parity in the actual game with real sprite rendering and real physics timing can only be confirmed by watching it run.

### Gaps Summary

No gaps found. All 10 observable truths verified. All 3 requirements (ANIM-01, ANIM-02, ANIM-03) satisfied. All artifacts exist, are substantive, and are wired. All key links verified. All behavioral spot-checks pass.

The only open item is a visual parity playthrough to confirm the FSM-driven animation looks identical to v1.3 in the running game. The 26-03-SUMMARY.md notes "Visual regression playthrough approved by user" which suggests this was already done during execution, but it cannot be programmatically verified.

---

_Verified: 2026-04-12T16:30:00Z_
_Verifier: Claude (gsd-verifier)_
