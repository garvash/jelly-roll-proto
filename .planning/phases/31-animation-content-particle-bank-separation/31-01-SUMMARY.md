---
phase: 31
plan: 01
status: complete
completed: 2026-04-22
test_count_before: 24
test_count_after: 32
new_tests: 8
---

# Plan 31-01 SUMMARY — Phase 31 Core Primitives

Landed the three core primitives every other Phase 31 plan depends on:
`pause_for(n)` on AnimPlayer + AnimFSM, the extended `PlayerAnimDriver`
contract, and a 192×16 player sprite sheet with placeholder frames at
all 9 new U offsets.

## Final Signatures

### AnimPlayer.pause_for (Task 1)
```python
def pause_for(self, n: int) -> None:
    """Freeze the tick counter for n frames. Additive if already paused.
    Phase 31 D-06 - animation-only pause for drill-recoil visual."""
    self._pause_ticks += n
```

`_pause_ticks` field is initialised to 0 in both `__init__` and `set_clip`,
ensuring pause does not survive a clip change. `tick()` decrements
`_pause_ticks` and returns early while the counter is positive.

### AnimFSM.pause_for (Task 1)
```python
def pause_for(self, n: int) -> None:
    """Forward to the active AnimPlayer. Phase 31 D-06."""
    self._player.pause_for(n)
```

Subscribers call `player._anim.pause_for(n)`; `_player` stays private
(matches existing `current_frame_u` forwarding pattern).

### PlayerAnimDriver (Task 2)
```python
@dataclass(slots=True)
class PlayerAnimDriver:
    state: str = STATE_IDLE
    is_grounded: bool = True
    facing: int = 1
    vy_sign: int = 0
    # Phase 31 additions:
    vx_sign: int = 0          # D-01 Metroid jump split
    prev_facing: int = 1      # D-03 turn_skid edge detection
    skid_ticks: int = 0       # D-03 transient countdown
    land_ticks: int = 0       # D-02 transient countdown
    crouch_ticks: int = 0     # D-04 transient countdown
```

## Named Constants Exported (Task 2)

`src/anim/player_anim.py` now exports 13 new constants (no magic
numbers per project memory):

| Name | Value | Rationale |
|------|-------|-----------|
| `LAND_SQUASH_FRAMES` | 4 | D-02 ticks after `is_grounded` flips |
| `TURN_SKID_FRAMES` | 3 | D-03 ticks after `facing` flips |
| `JUMP_CROUCH_FRAMES` | 2 | D-04 ticks after `jump_start` emit |
| `DRILL_RECOIL_PAUSE_FRAMES` | 3 | D-06 `pause_for` ticks per block-break |
| `STATE_DIVING` | "DIVING" | D-05 drill-spin clip predicate |
| `LAND_SQUASH_U` | 48 | bank-1 row-0 sprite U offset |
| `TURN_SKID_U` | 64 | bank-1 row-0 sprite U offset |
| `JUMP_CROUCH_U` | 80 | bank-1 row-0 sprite U offset |
| `JUMP_STATIONARY_U` | 96 | bank-1 row-0 sprite U offset |
| `JUMP_RUNNING_U` | 112 | bank-1 row-0 sprite U offset |
| `DRILL_SPIN_FRAME_0_U` | 128 | bank-1 row-0 sprite U offset |
| `DRILL_SPIN_FRAME_1_U` | 144 | bank-1 row-0 sprite U offset |
| `DRILL_SPIN_FRAME_2_U` | 160 | bank-1 row-0 sprite U offset |
| `DRILL_SPIN_FRAME_3_U` | 176 | bank-1 row-0 sprite U offset |

`PLAYER_CLIPS`, `PLAYER_RULES`, and `build_player_fsm` are intentionally
unchanged — Plan 02 rewires those to consume the new clips and rules.

## Placeholder Sprite Art (Task 3)

`assets/sprites/player.png` extended from **48×16 (3 frames)** to
**192×16 (12 frames)**, mode `P`, palette preserved. Resolved via the
"auto-extend with procedural placeholders" path (Task 3 `resume-signal`
option for D-02/D-03/D-05 procedural placeholders).

Each new frame derived from the IDLE silhouette via a transform that
visually evokes its semantic, plus a 2×2 palette-indexed corner marker
for unambiguous identification when debugging:

| U | Name | Transform | Marker |
|---|------|-----------|--------|
| 48 | LAND_SQUASH | vertical squash → 12 rows | magenta (idx 3) |
| 64 | TURN_SKID | horizontal flip | orange (idx 5) |
| 80 | JUMP_CROUCH | vertical squash → 10 rows | yellow (idx 6) |
| 96 | JUMP_STATIONARY | shifted up 2px | teal (idx 8) |
| 112 | JUMP_RUNNING | shifted up+right 1px | mint (idx 9) |
| 128 | DRILL_SPIN_FRAME_0 | rotate 0° | pink (idx 12) |
| 144 | DRILL_SPIN_FRAME_1 | rotate 90° CW | pink (idx 12) |
| 160 | DRILL_SPIN_FRAME_2 | rotate 180° | pink (idx 12) |
| 176 | DRILL_SPIN_FRAME_3 | rotate 270° CW | pink (idx 12) |

Real pixel art (e.g. from `assets/sprites/player.aseprite`) can replace
these placeholders any time without source code changes.

## Test Count

- Baseline before Plan 31-01: 24 tests in `tests/test_anim.py`
- After Task 1 (4 pause_for tests): 28 tests
- After Task 2 (4 driver/constants tests): 32 tests
- After Task 3 (asset only, no test changes): 32 tests

All 32 pass. No existing parity test regressed.

## Key Files

### Modified
- `src/anim/anim_player.py` - `pause_for(n)` method, `_pause_ticks` field, tick-time pause logic
- `src/anim/state_machine.py` - `AnimFSM.pause_for(n)` forwarding method
- `src/anim/player_anim.py` - extended `PlayerAnimDriver` (5 new fields), 13 named constants, `STATE_DIVING`
- `assets/sprites/player.png` - extended to 192×16, 9 new placeholder frames
- `tests/test_anim.py` - 8 new unit tests (4 pause_for + 4 driver/constants)

## Commits
- `7576264` test(31-01): add failing tests for pause_for primitive
- `d21de4e` feat(31-01): implement pause_for on AnimPlayer and AnimFSM
- `3185be1` test(31-01): add failing tests for PlayerAnimDriver Phase 31 fields
- `e397ae3` feat(31-01): extend PlayerAnimDriver and add Phase 31 named constants
- `795cb8b` feat(31-01): extend player.png with placeholder frames at U=48..176

## Self-Check

- [x] All 4 pause_for tests pass (Task 1)
- [x] All 4 driver/constants tests pass (Task 2)
- [x] PNG is 192×16 P-mode and loads via PIL (Task 3)
- [x] All 9 new U slots contain non-zero pixel data (placeholder marker visible)
- [x] All 32 `tests/test_anim.py` tests pass — no regression on parity tests
- [x] No magic numbers introduced — every numeric literal is a named constant
- [x] `STATE_DIVING` constant added without changing existing rule table (Plan 02 will use it)

Self-Check: PASSED
