---
phase: 31
plan: 04
status: complete
completed: 2026-04-22
test_count_before_anim_events: 6
test_count_after_anim_events: 12
new_tests: 6
---

# Plan 31-04 SUMMARY — Fuse-Flash + Blob-Growth (D-07)

Implements the Megaman-charge fuse-flash aesthetic and the multi-frame
BlobGrowth placeholder on top of Plan 03's particle bank.

## BlobGrowth Class

```python
class BlobGrowth:
    def __init__(self, x, y, frames=4):
        # Per-instance non-looping AnimClip from BLOB_GROWTH_FRAME_*_U
        clip = AnimClip(frames=frame_us, durations=[3]*frames, loop=False)
        self._anim_player = AnimPlayer(clip)
        self._ticks_elapsed = 0
        self._total_lifetime_ticks = frames * BLOB_GROWTH_DURATION_PER_FRAME
        self.is_active = True

    def update(self):
        if not self.is_active: return
        self._anim_player.tick()
        self._ticks_elapsed += 1
        if self._ticks_elapsed > self._total_lifetime_ticks:
            self.is_active = False

    def current_u(self):
        return self._anim_player.current_u()

    def draw(self, cam_x, cam_y):
        # bank 2, frame U = self._anim_player.current_u(),
        # row v = BLOB_GROWTH_V (16), 16x16 sprite, centred on (x, y)
```

**Open Question 3 hybrid resolution:** BlobGrowth uses tier-2
`AnimPlayer(clip)` wrapping because multi-frame growth is exactly what
AnimPlayer models. Single-sprite Particle (burst, convergence) stays
custom `dx/dy/life`. Two patterns coexist deliberately.

## Constants Added (main.py)

| Constant | Value | Purpose |
|----------|-------|---------|
| `FUSE_PARTICLE_COUNT` | 16 | D-07a converging particles |
| `FUSE_CONVERGE_FRAMES` | 12 | D-07a ~0.2s @ 60fps |
| `FUSE_RING_RADIUS` | 24 | D-07a px radius around player center |
| `BLOB_GROWTH_FRAMES` | 4 | Number of growth frames |
| `BLOB_GROWTH_DURATION_PER_FRAME` | 3 | Ticks per frame |
| `BLOB_GROWTH_FRAME_0_U` | 0 | Bank-2 frame offsets (row y=16) |
| `BLOB_GROWTH_FRAME_1_U` | 16 | |
| `BLOB_GROWTH_FRAME_2_U` | 32 | |
| `BLOB_GROWTH_FRAME_3_U` | 48 | |
| `BLOB_GROWTH_V` | 16 | Bank-2 row offset |
| `BLOB_SIZE` | 16 | Blob render size (16x16) |

## fuse_start Subscriber

**Location:** `main.py:273-298` (inside `Game.__init__`, between Plan
03's `drill_block_break` subscriber and `pyxel.run`).

**Body (verbatim):**
```python
def _on_fuse_start(**kw):
    """D-07a: 16 converging particles. D-07b: BlobGrowth at convergence point."""
    cx = self.player.x + self.player.w // 2
    cy = self.player.y + self.player.h // 2
    for i in range(FUSE_PARTICLE_COUNT):
        angle = (2 * _math.pi * i) / FUSE_PARTICLE_COUNT
        start_x = cx + _math.cos(angle) * FUSE_RING_RADIUS
        start_y = cy + _math.sin(angle) * FUSE_RING_RADIUS
        # Per-particle vector reaches center in FUSE_CONVERGE_FRAMES ticks
        dx = (cx - start_x) / FUSE_CONVERGE_FRAMES
        dy = (cy - start_y) / FUSE_CONVERGE_FRAMES
        self.particles.append(_Particle(
            start_x, start_y, dx=dx, dy=dy,
            life=FUSE_CONVERGE_FRAMES,
            bank_u=PARTICLE_CONVERGE_U, bank_v=PARTICLE_CONVERGE_V,
        ))
    # D-07b: blob born at convergence point
    self.fused_blobs.append(_BlobGrowth(cx, cy, frames=BLOB_GROWTH_FRAMES))

_event_bus.subscribe("fuse_start", _on_fuse_start)
```

## Pitfall 3 Defense — Dynamic Player Position

The subscriber reads `self.player.x` and `self.player.y` AT EMIT TIME
(not in a closure cache, not in a captured argument). This means when
**Phase 32 relocates the `fuse_start` emit** from `Player.fuse()`
(current v1.1 path) to the `WINDUP -> FUSED` latch in the fusion FSM,
the subscriber stays valid: it always anchors the converging ring at
wherever the player is when the event fires.

A unit test enforces this property:
`test_fuse_start_main_subscriber_uses_dynamic_player_position` parses
`main.py` and asserts the subscriber body contains
`self.player.x` (not a cached capture).

## Game Integration

| Hook | Location | Change |
|------|----------|--------|
| `self.fused_blobs = []` | `reset()` line 312 | Initialise alongside `self.particles` |
| Update loop | `main.py:602-606` | tick + filter on `is_active` (mirrors particles) |
| Draw loop | `main.py:990-993` | cam-aware draw (mirrors particles) |

## Phase 32 Pointer

**fuse_start emit relocation does NOT require subscriber changes.**
When Phase 32 implements the canonical `fuse_start` emit at
`WINDUP -> FUSED` in the fusion FSM, no edits are needed in the Plan 04
subscriber. The contract is: emit name `"fuse_start"`, kwargs `**kw`
ignored. Player position is read via `self.player.x/.y` at the moment
of emit, which is valid regardless of where in the call chain the emit
fires from.

## Test Count

- Baseline (after Plan 03): 6 tests in `tests/test_anim_events.py`
- After Plan 04 Task 2 (4 BlobGrowth tests): 10
- After Plan 04 Task 3 (2 fuse_start tests): 12

All 12 pass. Pre-existing 9 unrelated failures unchanged.

## Commits

- `c812d21` test(31-04): RED baseline for BlobGrowth and fuse_start subscriber
- `dd1bbc1` feat(31-04): BlobGrowth, FUSE/BLOB constants, fuse_start subscriber

## Self-Check

- [x] BlobGrowth class uses tier-2 AnimPlayer wrapping (1 instance, hybrid per Q3)
- [x] 11 new named constants exported (no magic numbers)
- [x] `self.fused_blobs = []` in reset()
- [x] update + draw loops mirror existing particles pattern (3 grep matches)
- [x] fuse_start subscriber reads `self.player.x` dynamically (Pitfall 3)
- [x] Subscribers ordered: reset (201) → drill subscribe (271) → fuse subscribe (298) → pyxel.run (300)
- [x] All 12 test_anim_events.py tests pass; no new regressions
- [x] Phase 32 emit relocation requires no subscriber edits

Self-Check: PASSED
