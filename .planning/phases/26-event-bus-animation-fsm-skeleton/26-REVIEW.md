---
phase: 26-event-bus-animation-fsm-skeleton
reviewed: 2026-04-12T12:00:00Z
depth: standard
files_reviewed: 11
files_reviewed_list:
  - src/anim/__init__.py
  - src/anim/event_bus.py
  - src/anim/anim_clip.py
  - src/anim/anim_player.py
  - src/anim/state_machine.py
  - src/anim/player_anim.py
  - src/entities/player.py
  - src/entities/slime.py
  - tests/conftest.py
  - tests/test_anim.py
  - tests/test_event_bus.py
findings:
  critical: 1
  warning: 2
  info: 2
  total: 5
status: issues_found
---

# Phase 26: Code Review Report

**Reviewed:** 2026-04-12T12:00:00Z
**Depth:** standard
**Files Reviewed:** 11
**Status:** issues_found

## Summary

The Phase 26 animation FSM skeleton and event bus are well-structured. The `AnimClip`/`AnimPlayer`/`AnimFSM` hierarchy is clean with proper validation and named constants. Event bus emissions in `player.py` correctly use prev-state snapshots (Pitfalls 3-5) for edge-only firing. One critical bug was found: `fire_charge_shot` bypasses the `unfuse()` method, violating the project's own Pitfall 3 contract and skipping the `fuse_end` event. Two warnings address a missing guard for empty clips and state mutation inside `draw()`.

## Critical Issues

### CR-01: fire_charge_shot bypasses unfuse(), skipping fuse_end event

**File:** `src/entities/player.py:626-628`
**Issue:** `fire_charge_shot` directly sets `self.is_fused = False` and `slime.is_fused = False` then calls `slime.dissipate()`, instead of calling `self.unfuse(slime, dissipate=True)`. The docstring on `unfuse()` (line 97) explicitly states "ALWAYS use this instead of setting is_fused directly (Pitfall 3)." This means the `fuse_end` event is never emitted for charge shots, which will break any downstream subscriber expecting to track fusion state transitions. Any future logic added to `unfuse()` will also be silently skipped for charge shots.
**Fix:**
```python
# Replace lines 626-629:
#   self.is_fused = False
#   slime.is_fused = False
#   slime.dissipate()
#   self.is_charging_recall = False
# With:
self.unfuse(slime, dissipate=True)
self.is_charging_recall = False
```

## Warnings

### WR-01: AnimPlayer crashes on empty AnimClip (no frames)

**File:** `src/anim/anim_player.py:22`
**Issue:** `AnimClip(frames=[], durations=[])` passes `__post_init__` validation (lengths match at 0), but `AnimPlayer.__init__` immediately accesses `self._clip.durations[self._frame_index]` where `_frame_index=0`, causing an `IndexError`. The same crash occurs from `AnimFSM.__init__` which creates an `AnimPlayer` with the fallback clip. While no current code path constructs an empty clip, the validation in `AnimClip.__post_init__` should reject it to fail fast.
**Fix:**
```python
# In src/anim/anim_clip.py, add to __post_init__:
def __post_init__(self) -> None:
    if not self.frames:
        raise ValueError("AnimClip requires at least one frame")
    if len(self.frames) != len(self.durations):
        raise ValueError(
            f"AnimClip frames/durations length mismatch: "
            f"{len(self.frames)} vs {len(self.durations)}"
        )
```

### WR-02: State mutation inside draw() -- shield_flash_timer decrement

**File:** `src/entities/player.py:854`
**Issue:** `self.shield_flash_timer -= 1` is decremented inside `draw()`. Mutating game state in the render path is an anti-pattern: if `draw()` is called at a different rate than `update()` (e.g., frame skip, pause screen, or future render-decouple), the timer will drift. This predates Phase 26 but is in a reviewed file.
**Fix:** Move the decrement to `update_timers()`:
```python
# In update_timers(), add:
if self.shield_flash_timer > 0:
    self.shield_flash_timer -= 1
```

## Info

### IN-01: AnimClip events field uses bare dict type hint

**File:** `src/anim/anim_clip.py:11`
**Issue:** `events: dict` is unparameterized. When Phase 31 populates this field, the lack of a typed hint will make the expected key/value types unclear.
**Fix:** Add a type parameter stub, e.g., `events: dict[int, str]` or `dict[str, str]` matching the planned Phase 31 schema, or at minimum `dict[str, Any]`.

### IN-02: Duplicate mock_level/mock_slime fixtures in test_anim.py shadow conftest.py

**File:** `tests/test_anim.py:199-215`
**Issue:** `test_anim.py` defines its own `mock_level` and `mock_slime` fixtures (lines 199-215) that shadow the more complete versions in `conftest.py` (which include `get_zone_hazard_type`, `get_destructible_at`, `get_cracked_h_at`, `get_cracked_v_at` stubs). The `test_anim.py` versions lack these stubs, which could cause `AttributeError` if tests evolve to exercise code paths that call those methods. The `test_event_bus.py` tests correctly rely on conftest.py's fixtures.
**Fix:** Remove the duplicate fixtures from `test_anim.py` and rely on `conftest.py`'s shared versions. If different defaults are needed, parameterize the shared fixture or override specific attributes in the test body.

---

_Reviewed: 2026-04-12T12:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
