---
phase: 08-new-fusion-abilities
verified: 2026-03-28T07:10:00Z
status: human_needed
score: 12/12 must-haves verified
re_verification: false
human_verification:
  - test: "Hold Z unfused for >8 frames, release — verify slime zips toward player without firing spit"
    expected: "Slime moves visibly at high speed toward player; no projectile spawned"
    why_human: "Tap-vs-hold separation (was_tap threshold) requires live input timing to confirm; can't be verified by frame-by-frame grep"
  - test: "Tap left or right quickly while unfused (slime positioned elsewhere) — verify slime jumps to tapped direction without player walking"
    expected: "Slime repositions in tapped direction; player position unchanged; slime holds still until interacted with"
    why_human: "Tap threshold (HOLD_TAP_THRESHOLD=5 frames) requires real-time input and visual confirmation of slime position change vs walk"
  - test: "While fused, press V — verify ram starts, confirm breaking a CRACKED_H wall tile, confirm stop at solid wall"
    expected: "Player rams at high speed, CRACKED_H block disappears, player stops dead at solid block and unfuses"
    why_human: "Block breaking requires a live level with CRACKED_H tiles placed; wall-stop behavior is spatial and visual"
  - test: "ABL-04 requirements alignment: REQUIREMENTS.md says 'Hold button to increase power/size' but implementation fires at fixed max power with no charge levels (D-18)"
    expected: "Clarify whether ABL-04 as shipped (always-max-power release shot) satisfies the intent of the requirement, or whether a charge-level ramp is still needed"
    why_human: "Design intent question: D-18 explicitly says no charge levels, but ABL-04 in REQUIREMENTS.md implies hold-to-charge. One of these must be canonical."
---

# Phase 08: New Fusion Abilities Verification Report

**Phase Goal:** Charge-to-fuse ability system with Slime Ram, Directional Hold, and Charge Shot
**Verified:** 2026-03-28T07:10:00Z
**Status:** human_needed (all automated checks passed; 4 items need human/design confirmation)
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All player.py input checks use input_manager, not raw pyxel | VERIFIED | `grep pyxel.btn\|btnp\|btnr src/entities/player.py` returns 0 results |
| 2 | WASD+JK secondary mapping works for all existing controls | VERIFIED | `_ACTION_MAP` in input.py maps A/D/W/S and J/K to all actions |
| 3 | Hold duration tracking reports correct frame counts | VERIFIED | `hold_frames`, `was_tap`, `_prev_hold_frames` all present and tested (10 tests pass) |
| 4 | V unfused = basic dash; DOWN+V = drill dive | VERIFIED | `handle_input` lines 283-300: `btnp("dash")` block branches correctly |
| 5 | Kick mechanic fully removed | VERIFIED | `kick_timer`, `def kick(`, `KICK_DURATION`, `SLIME_PUNT_SPEED` absent from all files (test_kick_removal.py 4/4 pass) |
| 6 | DRILL item type replaced by DASH_PICKUP | VERIFIED | `items.py` line 18: `"DASH_PICKUP"` sets `player.has_dash = True`; entity-schema.json has `"DashPickup"` entity |
| 7 | Holding Z unfused recalls slime at high speed | VERIFIED | `slime.recall()` and `update_recall()` use `RECALL_SPEED=8.0`; wired from player.py `handle_input` lines 264-274 |
| 8 | Auto-fuse at JUICE_MAX when slime arrives | VERIFIED | `player.py` line 273: `if arrived and slime.juice >= slime.max_juice: self.fuse(slime)` |
| 9 | While fused, damage consumes juice (mana shield, 20/hit) | VERIFIED | `player.py` line 128: `slime.consume(MANA_SHIELD_COST)`; `MANA_SHIELD_COST=20.0` |
| 10 | Juice hitting 0 while fused triggers dissipation cooldown | VERIFIED | `player.py` line 130-133: juice<=0 calls `unfuse(slime, dissipate=True)`; `slime.dissipate()` sets `SLIME_DISSIPATE_COOLDOWN=120` frames |
| 11 | Tap LEFT/RIGHT repositions slime; hold walks normally (ABL-03) | VERIFIED | `player.py` lines 207-210: `was_tap("left/right", HOLD_TAP_THRESHOLD)` calls `slime.hold_position()`; hold path goes to normal movement |
| 12 | V while fused = Slime Ram breaking CRACKED_H blocks (ABL-01) | VERIFIED | `player.py` line 294: `elif self.is_fused: self.start_ram(slime)`; `move_and_collide` line 461: `get_cracked_h_at` called, `RAM_BLOCK_COST=15.0` consumed |
| 13 | Z release while fused = Charge Shot; dumps all juice; unfuses (ABL-04) | VERIFIED | `player.py` lines 213-214: `btnr("spit")` while `is_fused` calls `fire_charge_shot(slime)`; `slime.consume(slime.juice)` dumps all juice |
| 14 | Slime lands at charge shot impact point (ABL-04) | VERIFIED | `ChargeProjectile._reposition_slime()` teleports slime to impact `x,y` with solid safety check |
| 15 | Ram opens doors (replaces kick for door interaction) | VERIFIED | `main.py` line 385: `if self.player.state == "RAMMING"` checks `door.check_kick_hit()` |

**Score:** 15/15 truths verified (12 plan-declared must-haves + 3 additional truths from plan 04)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/core/input.py` | Input abstraction with btn/btnp/btnr/update/hold_frames/was_tap | VERIFIED | All 6 functions present, `_ACTION_MAP` with WASD+JK, 60 lines |
| `tests/test_input.py` | Unit tests for input module | VERIFIED | 10 tests, all pass |
| `src/entities/player.py` | DASHING state, start_dash; fuse/unfuse; RAMMING state, start_ram; fire_charge_shot | VERIFIED | All methods present; `DASHING`/`RAMMING`/`DIVING` all handled in `update()` and `update_state()` |
| `src/core/constants.py` | DASH_SPEED, RAM_SPEED, RAM_BLOCK_COST, CHARGE_SHOT_*, RECALL_SPEED, MANA_SHIELD_COST, HOLD_TAP_THRESHOLD | VERIFIED | All 13 new constants present |
| `tests/test_dash.py` | Basic dash unit tests | VERIFIED | 9 tests, all pass |
| `tests/test_kick_removal.py` | Verifies kick fully removed | VERIFIED | 4 tests, all pass |
| `tests/test_drill_retcon.py` | Verifies drill retcon and DashPickup | VERIFIED | 5 tests, all pass |
| `src/entities/slime.py` | recall(), update_recall(), dissipate(), hold_position() | VERIFIED | All 4 new methods present; `is_dissipated`, `is_recalling`, `is_holding_position` state flags present |
| `tests/test_fusion.py` | Fusion system unit tests | VERIFIED | 10 tests, all pass |
| `tests/test_slime_hold.py` | Directional slime hold unit tests | VERIFIED | 6 tests, all pass |
| `src/level/map.py` | `get_cracked_h_at()` for ram block detection | VERIFIED | Lines 278-289; calls `is_cracked_horizontal()` per tile in AABB |
| `src/entities/projectile.py` | ChargeProjectile class with slime teleport | VERIFIED | `class ChargeProjectile` at line 56; `_reposition_slime()` with solid safety nudge |
| `tests/test_ram.py` | Slime Ram unit tests | VERIFIED | 10 tests, all pass |
| `tests/test_charge_shot.py` | Charge Shot unit tests | VERIFIED | 9 tests, all pass |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/entities/player.py` | `src/core/input.py` | `import src.core.input as input_manager` | WIRED | Line 3 of player.py; `input_manager.update()` called first in `Player.update()` |
| `src/entities/player.py` | `src/core/input.py` | `input_manager.btnp("dash")` | WIRED | Line 283; confirmed no raw pyxel calls remain |
| `src/entities/player.py` | `src/entities/slime.py` | `def fuse(self, slime)` | WIRED | Lines 53-68; `fuse()` sets both `player.is_fused` and `slime.is_fused` atomically |
| `player.py take_damage` | `slime.py consume` | `slime.consume(MANA_SHIELD_COST)` | WIRED | Line 128; only fires when `self.is_fused and slime and slime.juice > 0` |
| `player.py RAMMING state` | `map.py get_cracked_h_at()` | Horizontal collision in `move_and_collide` | WIRED | Line 461; called only when `self.state == "RAMMING" and slime` |
| `player.py fire_charge_shot` | `projectile.py ChargeProjectile` | Inline import + instantiation | WIRED | Lines 390, 395; `ChargeProjectile(x, y, dx, dy, level_map, slime)` |
| `ChargeProjectile` | `slime.py` | `_reposition_slime()` on impact | WIRED | Lines 103-125; sets `slime.x`, `slime.y`, clears slime state flags |

---

### Data-Flow Trace (Level 4)

Not applicable — this phase implements game mechanics code (Python), not data-fetching components. All dynamic values flow through the game loop: `input_manager.update()` feeds `hold_frames` into `was_tap()` which routes to `slime.hold_position()` or `slime.recall()`. Traced above in key links.

---

### Behavioral Spot-Checks (Step 7b)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All phase-08 tests pass | `python -m pytest tests/test_input.py tests/test_dash.py tests/test_kick_removal.py tests/test_drill_retcon.py tests/test_fusion.py tests/test_slime_hold.py tests/test_ram.py tests/test_charge_shot.py -v` | 63/63 passed in 0.26s | PASS |
| No regressions in full suite | `python -m pytest tests/ -v` | 139 passed, 3 failed (all 3 are pre-existing failures from Phase 07 refactoring) | PASS |
| input.py module exports verify | `python -c "import src.core.input as m; [getattr(m, f) for f in ['btn','btnp','btnr','update','hold_frames','was_tap']]"` | No AttributeError | PASS |
| ChargeProjectile importable | `python -c "from src.entities.projectile import ChargeProjectile; print(ChargeProjectile)"` | `<class 'src.entities.projectile.ChargeProjectile'>` | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| ABL-01 | 08-04 | Slime Ram fusion (Forward Dash) with horizontal gating capability | SATISFIED | `start_ram()`, `RAMMING` state, `get_cracked_h_at()` in `move_and_collide`, `RAM_BLOCK_COST=15.0`; 10 ram tests pass |
| ABL-03 | 08-03 | Directional Slime Hold (Tap left/right to position and freeze slime) | SATISFIED | `was_tap("left/right", HOLD_TAP_THRESHOLD)` -> `slime.hold_position()`; 6 slime hold tests pass; REQUIREMENTS.md marks as `[x]` completed 2026-03-28 |
| ABL-04 | 08-04 | Charge Slime Shot | PARTIAL — see note | `fire_charge_shot()` implemented; Z release while fused fires `ChargeProjectile`; 9 charge shot tests pass. **Note:** REQUIREMENTS.md describes "Hold button to increase power/size" but implementation fires at fixed max power with no charge levels per D-18 ("no charge levels — every shot is the same"). This is a design-document vs requirements-document discrepancy. The implementation is consistent with D-18 but differs from the ABL-04 text. |

**Orphaned requirements check:** REQUIREMENTS.md Phase 08 traceability lists ABL-01, ABL-03, ABL-04 only. No orphaned requirements found.

---

### Anti-Patterns Found

No blockers or warnings found in phase-08 modified files:

- No TODO/FIXME/PLACEHOLDER comments in any of the 14 new/modified files
- No stub `return null` / `return []` patterns in game logic paths
- No hardcoded empty state flowing to rendering
- Kick removal confirmed: `kick_timer`, `def kick(`, `KICK_DURATION`, `SLIME_PUNT_SPEED` all absent (verified by passing test_kick_removal.py)
- The bare `self.is_fused = False` in `fire_charge_shot` (line ~404) is intentional and documented in the summary: "Charge shot sets is_fused=False directly (not via unfuse) because slime position is managed by ChargeProjectile." This is not a bug — slime state is reset by `ChargeProjectile._reposition_slime()` on impact.

---

### Human Verification Required

**1. Tap-vs-hold Z: recall does not fire spit**

**Test:** Hold Z for 9+ frames (without releasing), then release. Also tap Z quickly (1-4 frames) and release.
**Expected:** Long hold = slime zips toward player, no projectile; Quick tap = spit fires on release, slime does not start recalling.
**Why human:** `SPIT_HOLD_THRESHOLD=8` frame boundary requires real-time input timing. The logic uses `was_tap("spit", 8)` for spit and `hold_frames("spit") >= 8` for recall — the exact threshold behavior cannot be confirmed without playing.

**2. Directional hold tap-vs-walk separation**

**Test:** Hold left/right for 6+ frames (walk). Then tap left/right for 3 frames and release.
**Expected:** Hold = player walks, slime follows normally; Quick tap = slime repositions in tapped direction, player does not move.
**Why human:** `HOLD_TAP_THRESHOLD=5` frame boundary for `was_tap` requires live input to confirm the feel and threshold is correct. Walk vs reposition split is a UX quality check.

**3. Slime Ram: CRACKED_H breaking and solid stop**

**Test:** Enter a level with a CRACKED_H block. Get fused. Press V. Ram into CRACKED_H wall. Then ram into a solid wall.
**Expected:** CRACKED_H block destroyed (explosion visual), player continues through; solid wall stops player immediately, player unfuses.
**Why human:** Requires a live level with CRACKED_H tiles placed. Block destruction visual, juice cost deduction display, and the abrupt stop are all spatial/visual.

**4. ABL-04 design intent clarification (blocker for signoff)**

**Test:** Review ABL-04 in REQUIREMENTS.md against D-18 in the design notes.
**Expected:** Team confirms whether "always max power on release" (D-18, as implemented) or "hold to charge power level" (ABL-04 text) is the intended design. If hold-to-charge is required, ABL-04 is not fully satisfied.
**Why human:** This is a design decision. The code is internally consistent with D-18. The REQUIREMENTS.md description may be stale or aspirational. A human must confirm the canonical intent.

---

### Gaps Summary

No blocking code gaps found. All 15 truths are verified, all 14 artifacts exist, are substantive, and are wired. The 63 phase-08 tests all pass with no new regressions introduced (the 3 pre-existing failures in test_phase05_gaps.py and test_phase05_nyquist.py predate this phase and are unrelated to the new abilities).

The `human_needed` status is driven by:
1. Real-time input threshold UX (items 1-3 above) — these are inherently unverifiable by static analysis
2. ABL-04 requirements text vs implementation discrepancy (item 4) — needs design owner sign-off

If the ABL-04 "hold to increase power" wording is considered aspirational/outdated and D-18 (always-max-power) is the accepted design, then human items 1-3 are the only remaining verifications and the phase can be marked passed after playtest.

---

_Verified: 2026-03-28T07:10:00Z_
_Verifier: Claude (gsd-verifier)_
