---
phase: 31
plan: 02
status: complete
completed: 2026-04-22
test_count_before: 32
test_count_after: 45
new_tests: 13
---

# Plan 31-02 SUMMARY — ANIM-04 Transitions Wired

Added 6 new `PLAYER_CLIPS` entries, reordered `PLAYER_RULES`
(specific-before-generic), extended `Player._update_anim_driver` with
transient counters and the D-01 Metroid jump split, wired `land` /
`jump_start` event subscribers, and shipped a provisional
`drill_block_break` bridge emit so the drill-recoil animation pause
fires on commit.

## Final PLAYER_CLIPS (9 entries)

| Key | Frames (U) | Durations | Loop | Rationale |
|-----|-----------|-----------|------|-----------|
| idle | [IDLE_U=0] | [1] | True | Phase 26 baseline |
| run | [RUN_FRAME_A_U=16, RUN_FRAME_B_U=32] | [6, 6] | True | Phase 26 baseline |
| jump | [JUMP_U=32] | [1] | True | FALLING fallback only |
| jump_stationary | [JUMP_STATIONARY_U=96] | [1] | True | D-01 Metroid straight-up |
| jump_running | [JUMP_RUNNING_U=112] | [1] | True | D-01 Metroid somersault |
| jump_crouch | [JUMP_CROUCH_U=80] | [JUMP_CROUCH_FRAMES=2] | False | D-04 anticipation |
| land_squash | [LAND_SQUASH_U=48, IDLE_U=0] | [LAND_SQUASH_FRAMES-1=3, 1] | False | D-02 squash -> idle |
| turn_skid | [TURN_SKID_U=64] | [TURN_SKID_FRAMES=3] | False | D-03 skid hold |
| drill_spin | [DRILL_SPIN_FRAME_0..3_U=128..176] | [2,2,2,2] | True | D-05 4-frame loop |

## Final PLAYER_RULES (9 rules, specific-before-generic)

```python
PLAYER_RULES = [
    # 1. Transient-counter rules (highest priority)
    (lambda d: d.skid_ticks > 0 and d.is_grounded, "turn_skid"),
    (lambda d: d.crouch_ticks > 0,                 "jump_crouch"),
    (lambda d: d.is_grounded and d.land_ticks > 0, "land_squash"),
    # 2. Specific state + driver-field combos
    (lambda d: d.state == STATE_JUMPING and d.vx_sign == 0, "jump_stationary"),
    (lambda d: d.state == STATE_JUMPING and d.vx_sign != 0, "jump_running"),
    (lambda d: d.state == STATE_DIVING,                      "drill_spin"),
    # 3. Generic state-only rules
    (lambda d: d.state == STATE_RUNNING, "run"),
    (lambda d: d.state == STATE_FALLING, "jump"),
    # 4. Fallback
    (lambda d: True, "idle"),
]
```

## Final `_update_anim_driver` body

```python
def _update_anim_driver(self):
    from src.anim.player_anim import TURN_SKID_FRAMES
    d = self._anim_driver
    d.state = self.state
    d.is_grounded = self.is_grounded
    # Pitfall 1: snapshot BEFORE overwriting facing
    d.prev_facing = d.facing
    d.facing = 1 if self.facing_right else -1
    d.vy_sign = -1 if self.dy < 0 else (1 if self.dy > 0 else 0)
    d.vx_sign = -1 if self.dx < 0 else (1 if self.dx > 0 else 0)
    # D-03 edge detection: facing flip + grounded -> arm skid counter
    if d.facing != d.prev_facing and d.is_grounded:
        d.skid_ticks = TURN_SKID_FRAMES
    # Pitfall 2: every transient counter decrements every frame
    if d.skid_ticks > 0:   d.skid_ticks -= 1
    if d.land_ticks > 0:   d.land_ticks -= 1
    if d.crouch_ticks > 0: d.crouch_ticks -= 1
```

## Event subscribers (`Player.__init__`)

```python
from src.anim.player_anim import LAND_SQUASH_FRAMES, JUMP_CROUCH_FRAMES
def _on_land(**kw):
    self._anim_driver.land_ticks = LAND_SQUASH_FRAMES
def _on_jump_start(**kw):
    self._anim_driver.crouch_ticks = JUMP_CROUCH_FRAMES
event_bus.subscribe("land", _on_land)
event_bus.subscribe("jump_start", _on_jump_start)
```

## Provisional drill_block_break bridge

**Location:** `src/entities/player.py:788-793` (inside the drill DIVING
block-break branch, immediately after `self.on_block_break()`).

**Code:**
```python
# Phase 31 provisional bridge: emit drill_block_break so the drill-
# recoil animation pause fires on commit. Phase 32 owns the canonical
# emit site per FUSION-DESIGN and MUST remove this bridge during its
# refactor.
event_bus.emit("drill_block_break", tx=tx, ty=ty)
```

**Removal instruction for Phase 32:**
When Phase 32 implements the canonical `drill_block_break` emit in its
fusion FSM refactor, delete the 5-line bridge block in
`src/entities/player.py` around line 788. Search for the comment
`Phase 31 provisional bridge` to locate. No other dependency chain —
tests verifying the bridge fired only depend on `event_bus.emit` itself,
which Phase 32 keeps.

**Bridge scope:** drill DIVING path ONLY. Ram `on_block_break` (line 729)
and boost CRACKED_V `on_block_break` (line 820) were intentionally NOT
modified — those are distinct abilities.

## Tests Updated (Phase 31 intentional behavior change)

| Old name | New name | Reason |
|----------|----------|--------|
| test_jumping_parity | test_jumping_stationary_parity | JUMPING+vx_sign=0 now picks jump_stationary (D-01) |
| test_fallback_states_parity | (same) | Dropped DIVING from fallback list (drill_spin rule) |
| test_player_draw_u_jumping_parity | (same) | Expects JUMP_STATIONARY_U for default dx=0 player |
| test_player_draw_u_fallback_parity | (same) | Dropped DIVING from fallback list |

## Test Count

- Baseline after Plan 31-01: 32 tests
- After Plan 31-02 Task 1 (7 new): 39 tests
- After Plan 31-02 Task 2 (6 new): 45 tests

All 45 pass. 4 existing parity tests updated to match Phase 31 intent.

## Known Limitation

Clip durations and frame arrays are hardcoded in `PLAYER_CLIPS`. Plan
31-05 migrates the clip table to `assets/anim-schema.json` with a
live-reload loader + panel integration. Rules stay in Python per D-05.

## Commits

- `9a71829` feat(31-02): add 6 transition clips and reorder PLAYER_RULES
- `4c32a1f` feat(31-02): extend _update_anim_driver, wire subscribers, bridge emit

## Self-Check

- [x] 6 new clip entries present with correct frame/duration/loop
- [x] Rules reordered: transient > specific state > generic > fallback
- [x] prev_facing snapshot at line 877, facing overwrite at line 878 (Pitfall 1 guarded by line ordering)
- [x] All 3 transient counters decrement every frame (Pitfall 2)
- [x] 'land' and 'jump_start' subscribers fire correctly (2 tests green)
- [x] drill_block_break emit present at exactly 1 location (drill DIVING path)
- [x] 45 test_anim.py tests pass; no cross-file regressions in anim/player code
- [x] Pre-existing tuning/physics/ldtk test failures are unrelated to Phase 31 (baseline drift from prior phases)

Self-Check: PASSED
