---
phase: 27-diagnostic-overlays
reviewed: 2026-04-12T12:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - src/core/overlays.py
  - tests/test_overlays.py
findings:
  critical: 0
  warning: 2
  info: 1
  total: 3
status: issues_found
---

# Phase 27: Code Review Report

**Reviewed:** 2026-04-12T12:00:00Z
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Two source files reviewed: the diagnostic overlay manager (`src/core/overlays.py`, 479 lines) and its test suite (`tests/test_overlays.py`, 395 lines). The implementation is well-structured with clean separation of concerns, named constants throughout (no magic numbers), proper deque bounds, and idempotent initialization. Two logic bugs were found in the slime overlay's catch-up arrow computation and the stuck-detection counter placement. Test coverage is solid for toggle mechanics and state isolation but does not exercise the buggy catch-up arrow path.

## Warnings

### WR-01: Catch-up arrow direction vector uses mismatched coordinates

**File:** `src/core/overlays.py:468-476`
**Issue:** The distance used to normalize the direction vector (`dist`) is computed from the slime's top-left corner (`s.x`, `s.y`) to the target, but the direction numerator uses the slime's center (`scx`, `scy`). This produces an incorrect unit vector -- the arrow direction will be slightly off, especially when the slime sprite is large relative to the distance.

```python
# Current (line 468-476):
dist_to_target_sq = (s.target_x - s.x) ** 2 + (s.target_y - s.y) ** 2
# ...
dx_norm = (s.target_x - scx) / dist   # numerator uses center, denominator uses corner distance
dy_norm = (s.target_y - scy) / dist
```

**Fix:** Use center coordinates consistently for both distance and direction:

```python
dist_to_target_sq = (s.target_x - scx) ** 2 + (s.target_y - scy) ** 2
if dist_to_target_sq > SLIME_REFORM_DIST ** 2:
    dist = dist_to_target_sq ** 0.5
    if dist > 0:
        dx_norm = (s.target_x - scx) / dist
        dy_norm = (s.target_y - scy) / dist
```

Note: this requires moving the `scx`/`scy` assignments (currently on lines 470-471) above the `dist_to_target_sq` calculation, or computing them once at the top of the slime overlay function.

### WR-02: Stuck counter mutated inside draw function

**File:** `src/core/overlays.py:450-454`
**Issue:** `_slime_stuck_frames` is incremented/reset inside `_draw_slime_overlay()`, which is called from `draw()`. Draw functions should be side-effect-free. If `_draw_game_world()` were ever called more than once per frame (e.g., a future overlay compositing path), the stuck counter would double-increment. Currently this only fires once per frame, so the impact is low, but it violates the module's own "pure visual" contract stated in the docstring (line 1: "Pure visual").

**Fix:** Move stuck detection into `update()` where other per-frame state mutations already live:

```python
def update():
    # ... existing toggle logic ...
    _update_frame_time()
    _update_stuck_counter()   # <-- move stuck logic here
    # ... room transition detection ...

def _update_stuck_counter():
    global _slime_stuck_frames
    if _game_ref is None:
        return
    s = _game_ref.slime
    vel_mag = (s.dx ** 2 + s.dy ** 2) ** 0.5
    if vel_mag < STUCK_VEL_THRESHOLD:
        _slime_stuck_frames += 1
    else:
        _slime_stuck_frames = 0
```

Then `_draw_slime_overlay` just reads `_slime_stuck_frames` without modifying it.

## Info

### IN-01: Catch-up arrow distance threshold compared against corner, not center

**File:** `src/core/overlays.py:469`
**Issue:** Related to WR-01 -- the `dist_to_target_sq > SLIME_REFORM_DIST ** 2` check also uses corner coordinates. Since `SLIME_REFORM_DIST` is a gameplay constant calibrated against entity centers, the threshold comparison should also use center coordinates. This is already addressed by the fix in WR-01.

---

_Reviewed: 2026-04-12T12:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
