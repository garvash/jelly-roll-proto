---
phase: 09-defensive-mechanics
verified: 2026-03-28T00:00:00Z
status: gaps_found
score: 14/15 must-haves verified
re_verification: false
gaps:
  - truth: "SHIELD_PICKUP, BOOST_PICKUP, SHIELD_T2 items grant has_shield/has_boost/has_shield_t2"
    status: partial
    reason: "Item collection logic in items.py is correct and player flags are set, but main.py spawn_enemies() has no dispatch branches for ShieldPickup, BoostPickup, or ShieldT2 LDtk entity types. If placed in a level, these pickups will never be spawned in the game world."
    artifacts:
      - path: "main.py"
        issue: "spawn_enemies() missing elif etype == 'ShieldPickup', 'BoostPickup', 'ShieldT2' branches (lines 137-154). DashPickup branch exists as reference — same pattern needed."
    missing:
      - "Add elif etype == 'ShieldPickup': self.items.append(Item(ex, ey, 'SHIELD_PICKUP', iid=ent_iid)) in spawn_enemies()"
      - "Add elif etype == 'BoostPickup': self.items.append(Item(ex, ey, 'BOOST_PICKUP', iid=ent_iid)) in spawn_enemies()"
      - "Add elif etype == 'ShieldT2': self.items.append(Item(ex, ey, 'SHIELD_T2', iid=ent_iid)) in spawn_enemies()"
human_verification:
  - test: "Enter a hazard zone tile (water, acid, or lava) with has_shield=True and full juice"
    expected: "Player auto-fuses, blue circle VFX appears, juice drains at the zone-appropriate rate"
    why_human: "Visual output and auto-fuse feel require runtime observation; cannot verify pyxel.circb rendering or fuse animation from static analysis"
  - test: "Press DOWN+SPACE while airborne with drill and juice"
    expected: "Player enters DIVING state (not triggered by V/dash)"
    why_human: "Real input device binding and feel, not just mocked button logic"
  - test: "Fire a charge shot while fused"
    expected: "Player receives upward recoil impulse; can be chain-used for bomb-climb traversal"
    why_human: "Physics feel and exploitability require runtime play; recoil magnitude of -2.5 is verified in code but in-game feel is not"
  - test: "Press SPACE while fused and airborne with has_boost=True"
    expected: "Player boosts upward; tapping SPACE again within ~0.2s chains another boost; stopping tapping causes unfuse"
    why_human: "Multi-tap timing and Yoshi-style flutter feel require runtime observation"
  - test: "Place a BOOSTING player above an enemy and verify stomp damage"
    expected: "Enemy takes 1 damage per boost frame where hitbox overlaps enemy below"
    why_human: "Enemy damage feedback (sprite flash, HP reduction) requires a live level with placed enemies"
---

# Phase 9: Defensive Mechanics Verification Report

**Phase Goal:** Defensive mechanics — Bubble Shield (ABL-05) for hazard zone traversal, Slime Boost (ABL-06) for vertical mobility, charge shot recoil, input remap, and entity schema updates. ABL-07 removed per D-21.
**Verified:** 2026-03-28
**Status:** GAPS FOUND
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Zone hazard tiles (water/acid/lava) exist as distinct tile types with drain rates | VERIFIED | `TILE_WATER=(9,1)`, `TILE_ACID=(10,1)`, `TILE_LAVA=(11,1)` in constants.py lines 16-18; `HAZARD_DRAIN_RATES` dict lines 25-29 |
| 2 | Zone hazard tiles are NOT solid — player passes through them | VERIFIED | `is_solid()` checks only `(TILE_SOLID, TILE_DESTRUCTIBLE, TILE_GOO_MOLD, TILE_CRACKED_H, TILE_CRACKED_V)` — zone tiles absent (map.py line 140-141); confirmed by test_hazard_zones.py::test_zone_tiles_not_solid |
| 3 | Drill Dive triggers on DOWN+SPACE instead of DOWN+V (D-12) | VERIFIED | player.py line 361: `if input_manager.btnp("jump") and self.state not in ("DIVING", "DASHING", "RAMMING"):` with drill dive logic inside; confirmed passing by test_input_remap.py (5/5 tests pass) |
| 4 | V button still triggers dash (unfused) and ram (fused) without drill dive | VERIFIED | player.py lines 348-357: `if input_manager.btnp("dash")` block contains only `start_ram(slime)` and `start_dash()` — no `has_drill` check present; confirmed by test_input_remap.py::test_dash_button_no_drill_dive |
| 5 | Charge shot applies upward recoil impulse (D-17) | VERIFIED | player.py line 525: `self.dy = CHARGE_RECOIL_FORCE` inside `fire_charge_shot()`; `CHARGE_RECOIL_FORCE = -2.5` (constants.py line 134); confirmed by test_charge_recoil.py (2/2 pass) |
| 6 | SHIELD_PICKUP, BOOST_PICKUP, SHIELD_T2 items grant has_shield/has_boost/has_shield_t2 | PARTIAL | `items.py` collect() logic is correct (lines 26-31) and player flags exist (player.py lines 41-43). BUT `main.py spawn_enemies()` (lines 137-154) has no dispatch for `ShieldPickup`, `BoostPickup`, or `ShieldT2` entity types. Items placed in LDtk will never be spawned into the world. |
| 7 | ABL-07 is documented as removed per D-21 | VERIFIED | entity-schema.json `reserved_ranges` notes `"6-8": "Zone hazard tiles (water, acid, lava) — Phase 9"`. Plan 01 frontmatter includes ABL-07 in `requirements` with explicit removal note. REQUIREMENTS.md marks ABL-07 as checked (complete). |
| 8 | Player auto-fuses when entering hazard zone at 100% juice with has_shield (D-01) | VERIFIED | `update_shield()` in player.py lines 229-233; logic: `zone_type and self.has_shield and not self.is_fused and not slime.is_dissipated and self.shield_cooldown <= 0 and slime.juice >= slime.max_juice`; confirmed by test_bubble_shield.py (5 auto-fuse tests pass) |
| 9 | Juice drains at hazard-type-specific rate while shield is active (D-03) | VERIFIED | player.py lines 239-243: `HAZARD_DRAIN_RATES.get(zone_type)` with T2 reduction; confirmed by test_bubble_shield.py (3 drain rate tests pass) |
| 10 | Anti-flicker cooldown prevents rapid fuse/unfuse at zone edges (Pitfall 2) | VERIFIED | `self.shield_cooldown = SHIELD_REACTIVATION_COOLDOWN` set on deactivation (player.py lines 249, 254); guard `self.shield_cooldown <= 0` in auto-fuse condition; confirmed by test_bubble_shield.py (2 cooldown tests pass) |
| 11 | Fused + airborne + SPACE tap triggers BOOSTING state with upward burst (D-07) | VERIFIED | `start_boost()` in player.py lines 451-461; wired to handle_input lines 373-377 replacing placeholder `pass`; confirmed by test_slime_boost.py (4 trigger tests pass) |
| 12 | Multi-tap chaining works within BOOST_RECOMMIT_WINDOW (12 frames) (D-08) | VERIFIED | `update_boost()` in player.py lines 463-484; recommit timer checked before each chain tap; confirmed by test_slime_boost.py::test_boost_chain_within_window |
| 13 | Juice empties during boost: dissipate + burnout (D-09) | VERIFIED | `end_boost(slime, dissipate=True)` called on `slime.juice <= 0` check in both `start_boost()` and `update_boost()`; confirmed by test_slime_boost.py::test_boost_exit_juice_empty |
| 14 | Boost damages enemies below player on each tap (D-10) | VERIFIED | main.py lines 312-331: AABB stomp check during BOOSTING state using `BOOST_DOWNWARD_DAMAGE_W/H`; both regular enemies and boss checked; BOOSTING branch present after player.update() and before enemy updates |
| 15 | Jump buffer is cleared during boost to prevent post-boost ground jump (Pitfall 3) | VERIFIED | `update_timers()` line 202: `if self.state != "BOOSTING":` guard; `start_boost()` line 458, `update_boost()` line 476, `end_boost()` line 490 all set `self.jump_buffer_timer = 0`; handle_input line 433: `if self.jump_buffer_timer > 0 and self.state != "BOOSTING":` guard; confirmed by test_slime_boost.py (3 buffer tests pass) |

**Score: 14/15 truths verified** (1 partial gap)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/core/constants.py` | TILE_WATER, TILE_ACID, TILE_LAVA, HAZARD_DRAIN_RATES, BOOST constants, CHARGE_RECOIL_FORCE | VERIFIED | All constants present: lines 16-29 (zone tiles + drain rates), lines 127-134 (boost + recoil) |
| `src/level/map.py` | `get_zone_hazard_type()` method | VERIFIED | Lines 238-253; imports `TILE_WATER, TILE_ACID, TILE_LAVA, HAZARD_DRAIN_RATES`; val_to_tile lines 45-47 map 6/7/8 |
| `src/entities/items.py` | SHIELD_PICKUP, BOOST_PICKUP, SHIELD_T2 collection logic | VERIFIED (collect logic) | collect() lines 26-31 correct; draw() lines 49-57 present with placeholder sprites |
| `src/entities/player.py` | update_shield(), draw_shield(), start_boost(), update_boost(), end_boost(), BOOSTING state, player flags | VERIFIED | All methods present; flags (has_shield, has_shield_t2, has_boost, shield_active, shield_cooldown, hazard_hp_timer, boost_recommit_timer) in __init__ lines 41-51 |
| `assets/entity-schema.json` | IntGrid values 6-8, ShieldPickup/BoostPickup/ShieldT2 entities | VERIFIED | intgrid.values lines 30-32; entities lines 127-148; reserved_ranges updated line 38 |
| `tests/test_hazard_zones.py` | Zone hazard tile tests | VERIFIED | 5 tests, all pass |
| `tests/test_input_remap.py` | Drill dive remap + boost trigger priority tests | VERIFIED | 5 tests, all pass |
| `tests/test_charge_recoil.py` | Charge shot recoil tests | VERIFIED | 2 tests, all pass |
| `tests/test_bubble_shield.py` | ABL-05 behavior tests | VERIFIED | 16 tests, all pass |
| `tests/test_slime_boost.py` | ABL-06 behavior tests | VERIFIED | 13 tests, all pass |
| `main.py` | Boost stomp damage check, BOOST_DOWNWARD_DAMAGE import, ShieldPickup/BoostPickup/ShieldT2 spawn | PARTIAL | Stomp damage wired (lines 312-331), import present (line 6). Missing: spawn_enemies() dispatch for the 3 new pickup entity types |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/level/map.py` | `src/core/constants.py` | HAZARD_DRAIN_RATES dict import | VERIFIED | map.py line 6: `from src.core.constants import (..., TILE_WATER, TILE_ACID, TILE_LAVA, HAZARD_DRAIN_RATES)` |
| `src/entities/items.py` | `src/entities/player.py` | has_shield/has_boost/has_shield_t2 flags | VERIFIED | items.py collect() sets `player.has_shield`, `player.has_boost`, `player.has_shield_t2`; flags defined in player.__init__ |
| `src/entities/player.py` | `src/level/map.py` | get_zone_hazard_type() call in update_shield() | VERIFIED | player.py line 222: `self.level_map.get_zone_hazard_type(self.x, self.y, self.w, self.h)` |
| `src/entities/player.py` | `src/core/constants.py` | HAZARD_DRAIN_RATES, SHIELD_T2_DRAIN_REDUCTION lookup | VERIFIED | player.py line 239: `HAZARD_DRAIN_RATES.get(zone_type, HAZARD_DRAIN_SLOW)`; line 241: `SHIELD_T2_DRAIN_REDUCTION` |
| `src/entities/player.py` | `src/core/constants.py` | BOOST_FORCE, BOOST_JUICE_COST, BOOST_RECOMMIT_WINDOW | VERIFIED | player.py lines 455-457 in start_boost(); uses wildcard `from src.core.constants import *` |
| `main.py` | `src/entities/player.py` | boost enemy damage check in game update | VERIFIED | main.py lines 312-331: `if self.player.state == "BOOSTING":` after player.update() |
| `main.py` | LDtk entities | ShieldPickup/BoostPickup/ShieldT2 spawn dispatch | NOT WIRED | spawn_enemies() (lines 137-154) has no `elif etype == "ShieldPickup"` etc. branches. These entity types are silently ignored at runtime. |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `player.py: update_shield()` | `zone_type` | `self.level_map.get_zone_hazard_type()` — queries `collision_data` dict, returns worst HAZARD_DRAIN_RATES tile or None | Yes — real spatial AABB query against loaded tile data | FLOWING |
| `player.py: start_boost()` | `slime.juice` after `slime.consume(BOOST_JUICE_COST)` | slime object's juice attribute; consume() mutates it | Yes — real resource drain | FLOWING |
| `main.py: stomp check` | `self.player.state` | Player state machine, set by start_boost() | Yes — live player state | FLOWING |
| `main.py: spawn_enemies()` | `ShieldPickup/BoostPickup/ShieldT2` items | LDtk entity list | No real data flows — entity types never dispatched | DISCONNECTED |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All Phase 9 tests pass | `python -m pytest tests/test_input_remap.py tests/test_charge_recoil.py tests/test_hazard_zones.py tests/test_bubble_shield.py tests/test_slime_boost.py -v` | 41/41 passed in 0.23s | PASS |
| Full test suite (pre-existing failures are out-of-scope) | `python -m pytest tests/ -v` | 180 passed, 3 pre-existing failures in test_phase05_gaps.py and test_phase05_nyquist.py (rooms_visited string vs tuple, camera update timing — documented in all three 09-xx SUMMARY files as out-of-scope) | PASS for Phase 9 scope |
| TILE_WATER constant defined | `grep "TILE_WATER" src/core/constants.py` | Match at line 16 | PASS |
| get_zone_hazard_type method defined | `grep "def get_zone_hazard_type" src/level/map.py` | Match at line 238 | PASS |
| CHARGE_RECOIL_FORCE wired in fire_charge_shot | `grep "CHARGE_RECOIL_FORCE" src/entities/player.py` | Match at line 525 | PASS |
| BOOSTING state in player update | `grep "BOOSTING" src/entities/player.py` | Multiple matches (lines 131, 202, 373, 451, 464, 465, 483, 487, 664) | PASS |
| Boost stomp in main.py | `grep "BOOST_DOWNWARD_DAMAGE" main.py` | Matches at lines 6, 314, 321, 323, 328, 330 | PASS |
| New pickup entities in spawn_enemies | `grep "ShieldPickup\|BoostPickup\|ShieldT2" main.py` | No matches | FAIL — missing spawn dispatch |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| ABL-05 | 09-01-PLAN, 09-02-PLAN | Bubble Shield (hazard zone protection with juice drain) | SATISFIED | update_shield() fully implements auto-fuse, drain, tier, HP drain, deactivation; 16 tests pass; marked `[x]` in REQUIREMENTS.md |
| ABL-06 | 09-01-PLAN, 09-03-PLAN | Yoshi-style Double Jump (Slime Boost) | SATISFIED | BOOSTING state machine complete with chaining, stomp damage, jump buffer guards; 13 tests pass; marked `[x]` in REQUIREMENTS.md |
| ABL-07 | 09-01-PLAN | Reform Block (removed per D-21) | SATISFIED (as removal) | No code changes needed; documented as removed in Plan 01 and schema reserved_ranges; marked `[x]` in REQUIREMENTS.md |

No orphaned requirements: REQUIREMENTS.md Traceability section maps ABL-05, ABL-06, ABL-07 to Phase 09 — all three are accounted for in plan frontmatter.

**Note on ROADMAP.md:** ROADMAP.md still shows 09-02-PLAN.md and 09-03-PLAN.md as `[ ]` (unchecked). This is a documentation gap — the code, tests, and commit history all confirm these plans executed successfully. The ROADMAP.md progress table also shows Phase 9 as `1/3 plans complete`. This is stale documentation and does not reflect the actual codebase state.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/entities/items.py` | 52, 54, 56 | Sprite placeholder coordinates for Shield/Boost/ShieldT2 draw (`u, v = 32, 0`, `40, 0`, `48, 0`) | Info | Art pass needed; items draw using wrong sprite coordinates at runtime. Documented as known stub in 09-01-SUMMARY. |
| `main.py` | 137-154 | `spawn_enemies()` missing dispatch for ShieldPickup, BoostPickup, ShieldT2 entity types | Blocker | New ability pickups cannot be placed in levels. Without this, ABL-05 and ABL-06 can never be acquired in a real playthrough (only via has_shield/has_boost=True in code). |
| `.planning/ROADMAP.md` | 38-39 | Plans 09-02 and 09-03 marked as unchecked `[ ]` despite execution completion | Warning | Stale documentation; does not affect runtime behavior but creates false project state. |

---

### Human Verification Required

#### 1. Hazard Zone Visual and Feel

**Test:** Run the game, enter a water/acid/lava zone tile with full juice and has_shield=True.
**Expected:** Player auto-fuses (slime merges visually), blue circle VFX appears around player with pulse animation and flicker, juice bar drains at zone-appropriate rate.
**Why human:** pyxel.circb() rendering, pulse/flicker timing, and the visual fusion animation cannot be verified from static analysis.

#### 2. Input Remap Feel

**Test:** While airborne with has_drill=True and juice > 0, press DOWN+SPACE; separately test that pressing V+DOWN does not trigger drill.
**Expected:** SPACE+DOWN triggers drill dive; V+DOWN is simply blocked or horizontal-only behavior.
**Why human:** Real input device binding and timing window feel cannot be captured in unit tests.

#### 3. Charge Shot Bomb-Climb

**Test:** Fire a charge shot while fused and near a ceiling obstacle.
**Expected:** Player receives visible upward kick (-2.5 velocity impulse); chaining multiple shots allows ascending — the "bomb-climb exploit" intended by D-17.
**Why human:** Physics feel, chain timing, and height gain per shot require runtime evaluation.

#### 4. Slime Boost Multi-Tap Chaining

**Test:** While fused and airborne with has_boost=True, tap SPACE 3-4 times in quick succession (within 0.2s each).
**Expected:** Player rises with each tap (Yoshi flutter pattern); stopping for > 12 frames causes unfuse; juice depletes by 25 per tap.
**Why human:** Timing window feel, visual flutter effect, and multi-tap responsiveness require live playtesting.

---

## Gaps Summary

One gap blocks full goal achievement:

**Pickup Entity Spawning** — `main.py spawn_enemies()` handles `DashPickup`, `EnergyTank`, and `MissileTank` from LDtk entity lists, but has no dispatch branches for the three new Phase 9 pickups: `ShieldPickup`, `BoostPickup`, and `ShieldT2`. All other infrastructure is complete and correct — the `items.py` collection logic sets the right player flags, the player.py flags drive the right behaviors, and the entity schema documents these pickups correctly. The missing three `elif etype ==` branches in `spawn_enemies()` are the only thing preventing level designers from placing these items in LDtk and having them appear in-game.

The three pre-existing test failures in test_phase05_gaps.py and test_phase05_nyquist.py are explicitly out-of-scope for Phase 9 (documented in all three SUMMARY files and present before Phase 9 began).

The ROADMAP.md documentation showing plans 09-02 and 09-03 as incomplete is a stale document update and does not reflect the codebase.

---

_Verified: 2026-03-28_
_Verifier: Claude (gsd-verifier)_
