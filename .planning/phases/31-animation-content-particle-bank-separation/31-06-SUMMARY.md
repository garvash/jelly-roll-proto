---
phase: 31
plan: 06
status: complete
completed: 2026-04-22
matrix_combinations: 198
test_count: 5
runtime_seconds: 0.12
---

# Plan 31-06 SUMMARY — ANIM-07 Hitbox-Independence Hard Gate

Single new test file `tests/test_anim_hitbox.py` encodes the worst-case
silent-failure scenario (animation layer mutating `player.w` /
`player.h`) as an automatic, default-pytest fail-loud trip wire.

## Matrix Dimensions (D-23)

| Axis | Values | Count |
|------|--------|-------|
| state | IDLE, RUNNING, JUMPING, FALLING, DIVING, WALL_SLIDING, DASHING, RAMMING, BOOSTING, CHARGING_SHOT, DEAD | 11 |
| vx_sign | -1, 0, 1 | 3 |
| vy_sign | -1, 0, 1 | 3 |
| facing | True, False | 2 |
| **Total** | | **198 combinations** |

Each combination ticks the FSM 60 times → 11,880 FSM operations per matrix run.

## Test Functions (5 total)

| Function | Purpose |
|----------|---------|
| `test_hitbox_invariant_across_matrix` | Cartesian product matrix; cites failing combo in assertion message |
| `test_hitbox_invariant_with_land_event` | event_bus emit `land` → land_ticks → land_squash clip path |
| `test_hitbox_invariant_with_jump_start_event` | event_bus emit `jump_start` → crouch_ticks → jump_crouch clip path |
| `test_hitbox_invariant_with_drill_block_break_pause` | AnimFSM.pause_for(3) primitive preserves w/h |
| `test_hitbox_invariant_on_facing_edge_skid` | facing flip → skid_ticks → turn_skid clip path |

## Runtime

```
0.03s  test_hitbox_invariant_across_matrix
<0.005s each  rest
0.12s  total file
```

Well under the 5s budget.

## D-22 Hard Gate Confirmation

```
$ pytest -q --collect-only | grep test_hitbox_invariant | wc -l
5
```

Collected by default pytest invocation. No opt-in mark required. CI
and local runs alike block on this gate.

## Manual Smoke Test (Task 2)

**Status:** approved-with-notes (deferred to /gsd-verify-work).

Per user direction, the 8-section manual SC1-SC4 walkthrough was not
performed inline. SC4 (hitbox invariance) is fully automated and
green by construction. SC1-SC3 will be validated during the upcoming
verification pass (or on-demand whenever the user runs `python main.py`).

**Known limitations / deferred items:**

| Item | Status | Disposition |
|------|--------|-------------|
| Player sprite placeholder art | Auto-generated transforms + corner markers (Plan 01 Task 3) | Real pixel art deferred; user can author and replace `assets/sprites/player.png` any time without code changes |
| Particle sprite placeholder art | Auto-generated speck + circle placeholders (Plan 03 Task 1) | Same as above for `assets/sprites/particles.png` |
| BlobGrowth sprite real art | 4 procedural circles of growing radius (Plan 04 implicit; Plan 03 generation) | Per D-07b, real blob sprite supplied by user later |
| Manual SC1 transition visibility | Not validated this session | Deferred to `/gsd-verify-work` or user smoke test |
| Manual SC2 panel slider drag + Reload button | Not validated this session | Deferred (button + slider behaviour unit-tested via `test_panel_anim_tab_exists` and `test_panel_reload_anim_schema_rebinds_fsm`) |
| Manual SC3 visual particle / tile separation | Not validated this session | Bank distinctness automated via `test_sprite_manifest_banks_distinct` |
| Manual regression vs Phase 26 physics | Not validated this session | All Phase 26 / 28 / 29 unit tests still pass |

## Phase 32 Pointer

**Plan 02 provisional bridge MUST be removed when Phase 32 lands.** Search:

```
grep -n "Phase 31 provisional bridge" src/entities/player.py
# expected: src/entities/player.py:788 (drill DIVING block-break path)
```

When Phase 32 implements the canonical `drill_block_break` emit at the
fusion FSM level, delete the 5-line bridge block. The Plan 03
subscriber in `main.py` listens on the event name `"drill_block_break"`
and is stable across the move (no kwarg dependency).

Likewise, Plan 04's `fuse_start` subscriber reads `self.player.x` /
`self.player.y` at emit time, which is contract-stable across Phase 32's
relocation of the `fuse_start` emit from `Player.fuse()` to the
`WINDUP -> FUSED` latch in the fusion FSM.

## Commits

- `c92f34b` test(31-06): ANIM-07 hitbox-independence hard gate

## Self-Check

- [x] `tests/test_anim_hitbox.py` exists with 5 test functions
- [x] Matrix exercises 198 combinations across 11 states / 3 vx / 3 vy / 2 facings
- [x] Failure message cites the specific failing combo
- [x] All 5 tests pass on first run -- Phase 31 never mutates w/h
- [x] Default pytest invocation collects all 5 tests (D-22 hard gate satisfied)
- [x] Runtime well under 5s budget (matrix takes 30ms)
- [x] Manual smoke test deferred per user direction (approved-with-notes)
- [x] Phase 32 removal pointer documented for the provisional drill bridge

Self-Check: PASSED
