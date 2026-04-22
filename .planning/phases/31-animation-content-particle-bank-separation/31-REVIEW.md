---
phase: 31-animation-content-particle-bank-separation
reviewed: 2026-04-22T00:00:00Z
depth: standard
files_reviewed: 16
files_reviewed_list:
  - assets/anim-schema.json
  - main.py
  - src/anim/anim_player.py
  - src/anim/player_anim.py
  - src/anim/state_machine.py
  - src/core/tuning.py
  - src/entities/effects.py
  - src/entities/player.py
  - src/ui/panel.py
  - src/ui/presets.py
  - src/ui/widgets.py
  - tests/test_anim.py
  - tests/test_anim_events.py
  - tests/test_anim_hitbox.py
  - tests/test_phase22.py
  - tests/test_sprite_assets.py
  - tests/test_tuning_anim.py
findings:
  critical: 0
  warning: 4
  info: 7
  total: 11
status: issues_found
---

# Phase 31: Code Review Report

**Reviewed:** 2026-04-22T00:00:00Z
**Depth:** standard
**Files Reviewed:** 16 (includes `tests/test_tuning_anim.py` supplied as the 17th path; note the `files_to_read` block shows 17 entries, tests/test_tuning_anim.py was reviewed as well)
**Status:** issues_found

## Summary

Phase 31 ships a coherent separation of animation content and particle effects from physics/gameplay. The work is well-structured: `pause_for` on `AnimPlayer`/`AnimFSM` cleanly implements the D-06 animation-only pause; `tuning.load_anim()` is a properly isolated parallel namespace with its own flat index; the ANIM-prefixed key routing in `presets.py` correctly addresses Pitfall 6; the 198-combination hitbox-independence hard gate is a sound fail-loud invariant.

The documented invariants are upheld in the code that was reviewed:

- **Pitfall 1 (prev_facing snapshot ordering)** — `_update_anim_driver` snapshots `d.prev_facing = d.facing` *before* `d.facing = ...`, and `test_update_anim_driver_snapshots_prev_facing` encodes it.
- **Pitfall 2 (transient counter decrement)** — all three counters (`skid_ticks`, `land_ticks`, `crouch_ticks`) unconditionally decrement every frame with a `>0` guard, enforced by `test_update_anim_driver_decrements_counters`.
- **Pitfall 3 (dynamic player position read)** — the fuse_start subscriber closes over `self` and reads `self.player.x` at emit time; `test_fuse_start_main_subscriber_uses_dynamic_player_position` regex-guards the source.
- **Pitfall 5 (subscriber-after-reset)** — Game-level drill_block_break / fuse_start subscribers are wired AFTER `self.reset()`. See WR-01 for a separate leaked-subscriber concern in Player.__init__.
- **Pitfall 6 (ANIM_ prefix routing)** — `presets.load_preset` branches on `key.startswith("ANIM_")` and routes to `set_anim_value`; `test_load_preset_routes_anim_keys` verifies.

Issues below group into (a) subscriber/lifetime concerns in Player re-creation, (b) brittle magic constants around the "tile center" burst origin, (c) a small amount of coupling (`effects.py → main.py`) introduced by BlobGrowth, and (d) minor test-quality and data-structure issues.

## Warnings

### WR-01: Player event subscribers leak on every `reset()`

**File:** `src/entities/player.py:85-96`
**Issue:** `Player.__init__` calls `event_bus.subscribe("land", _on_land)` and `event_bus.subscribe("jump_start", _on_jump_start)` with closures that capture `self._anim_driver`. Every call to `Game.reset()` (new game, death respawn, save-load path, `restore_from_save`) constructs a new `Player`, which appends a new pair of subscribers. The old subscribers are never removed, so:

1. The `_subscribers` dict grows unbounded across restarts.
2. Each `event_bus.emit("land")` fires N handlers, where N = number of `Player` instances ever created in this process.
3. Stale closures pin garbage-collectable `Player`/driver instances alive via the `_subscribers` list.

In the current gameplay loop the visual impact is bounded (each stale handler assigns `land_ticks` on an orphaned driver that is no longer read), but the memory/subscriber-count leak is real and it sets the wrong precedent for subscribers that have side effects beyond driver-field mutation. The Game-level subscribers in `main.py:274, 301` don't leak because `Game.__init__` runs exactly once per process — but Player is re-created.

This is the same class of bug the RESEARCH doc calls out as "Pitfall 5 (subscriber after reset)" — the Game subscribers sidestep it by being wired post-reset; Player subscribers re-introduce it by subscribing inside a constructor that is called on every reset.

**Fix:** Either (a) store the bound closures on `self` and unsubscribe them in a `Player.dispose()` method called from `Game.reset()` before the new Player is constructed, or (b) move the two subscribe calls to `Game.__init__` alongside the drill_block_break / fuse_start subscribers and have them read through `self.game.player._anim_driver` at emit time. Option (b) is simpler and mirrors the Game-owned subscriber pattern already established in Phase 31:

```python
# main.py Game.__init__, alongside _on_drill_block_break/_on_fuse_start
from src.anim.player_anim import LAND_SQUASH_FRAMES, JUMP_CROUCH_FRAMES
def _on_land(**kw):
    self.player._anim_driver.land_ticks = LAND_SQUASH_FRAMES
def _on_jump_start(**kw):
    self.player._anim_driver.crouch_ticks = JUMP_CROUCH_FRAMES
_event_bus.subscribe("land", _on_land)
_event_bus.subscribe("jump_start", _on_jump_start)
# ...and drop the two subscribe calls at src/entities/player.py:95-96
```

### WR-02: `tile center` offset is wrong for TILE_SIZE=16 (magic `+4`)

**File:** `main.py:262-263` (subscriber), `main.py:930` (`spawn_particle_burst`)
**Issue:** The comment "diverging burst at tile center" and "Spawns BURST_PARTICLE_COUNT sprite-backed particles radially outward from (x + 4, y + 4) — the tile center" both describe `(+4, +4)` as the tile center. But `TILE_SIZE == 16` (verified at `assets/physics-schema.json:11`), so the tile center is `(+8, +8)`. The burst currently originates from the upper-left 8×8 sub-quadrant, not the tile center.

Additionally, `+4` is a bare magic literal with no named constant, violating the project memory rule "Avoid magic numbers — use named constants or comments for all numeric literals." The `4` is intended to be half a tile or half a sub-tile; it is not clear from the code which.

The test `test_drill_block_break_particles_at_tile_center` encodes `5*16+4=84` and `7*16+4=116` as the expected centers — so the test locks in the wrong offset. Fixing the bug requires updating the test.

**Fix:** Name the constant and use half-tile:

```python
# main.py, near the other Phase 31 particle constants
BURST_CENTER_OFFSET = tuning.TILE_SIZE // 2   # = 8 for 16x16 tiles

# in _on_drill_block_break and spawn_particle_burst:
cx = tx * _tuning.TILE_SIZE + BURST_CENTER_OFFSET
cy = ty * _tuning.TILE_SIZE + BURST_CENTER_OFFSET
```

Update `test_drill_block_break_particles_at_tile_center` to expect `5*16+8=88` and `7*16+8=120`. If the existing offset is actually the intended visual, rename/comment it (e.g. `BURST_SUBCELL_ANCHOR = 4`) and drop the misleading "tile center" comment.

### WR-03: `BlobGrowth` imports from `main` at instance construction and draw time

**File:** `src/entities/effects.py:95-99, 132`
**Issue:** `BlobGrowth.__init__` does `from main import (BLOB_GROWTH_FRAME_0_U, ...)` inside the constructor body, and `BlobGrowth.draw` does `from main import BLOB_SIZE, BLOB_GROWTH_V` inside every draw call. The docstring rightly calls out that the import is deferred to avoid pulling `main.py` when tests import `effects.py`, but this:

1. Inverts the dependency direction — a library module (`src.entities.effects`) depends on the application entry point (`main.py`). If a refactor splits `main.py`, the import path silently fails on first BlobGrowth construction rather than at module load.
2. Pays the `from main import ...` cost on every `draw()` call (every frame per active blob). Python caches module imports, so the cost is a dict lookup, but the pattern is a code smell for hot paths.
3. Makes `effects.py` untestable in the literal sense without also booting `main.py` — contradicting the stated motivation of the deferred import.

The cleaner home for `BLOB_GROWTH_FRAME_*_U`, `BLOB_GROWTH_DURATION_PER_FRAME`, `BLOB_GROWTH_V`, and `BLOB_SIZE` is a module that `effects.py` owns, e.g. `src/entities/effects.py` itself or `src/core/tuning.py` (since they are anim-layout constants, already part of the Phase 31 content migration).

**Fix:** Move the BLOB_GROWTH constants from `main.py:172-180` into `src/entities/effects.py` (or the anim-schema JSON if you want them tunable). Eliminate the `from main import ...` lines in both `__init__` and `draw`. This also lets `BLOB_SIZE` / `BLOB_GROWTH_V` be used at module scope inside `draw_sprite` calls without a function-local import.

### WR-04: `_scroll_y` list length silently coupled to `TAB_DEFS`

**File:** `src/ui/panel.py:54`
**Issue:** `_scroll_y = [0, 0, 0, 0, 0]` is a 5-element list hand-sized to match the 5-tab `TAB_DEFS` added in Phase 31 (the comment even flags "+1 for Anim tab"). Any future phase that adds a 6th tab but forgets to extend this list will IndexError on the first mouse-wheel event in the new tab. The existing comment does not prevent the bug — it just flags that this was manually bumped once.

**Fix:** Derive length from `TAB_DEFS`:

```python
_scroll_y = [0] * len(TAB_DEFS)   # Per-tab scroll offset
```

Or use a dict keyed by tab index with `defaultdict(int)`.

## Info

### IN-01: `test_drill_block_break_spawns_burst_and_pauses_anim` reimplements the subscriber body

**File:** `tests/test_anim_events.py:61-105`
**Issue:** The test constructs a local `_on_drill_block_break` closure that mirrors the handler in `main.py:250-272`, then subscribes and emits. This validates the test's own copy of the subscriber, not the one `Game.__init__` wires. If `main.py` diverges (e.g. the real handler stops calling `pause_for` or swaps particle constants), this test will still pass.

`test_fuse_start_main_subscriber_uses_dynamic_player_position` at `tests/test_anim_events.py:252` acknowledges this gap by regex-scanning the `main.py` source for `self.player.x`, but regex guards are a weak substitute for behavioural tests.

**Fix:** Extract the subscriber body into a module-level function in `main.py` (e.g. `handle_drill_block_break(game, tx, ty)`), have `Game.__init__` subscribe a `lambda` that calls it, and have tests call the extracted function directly. Similarly for `handle_fuse_start(game)`. This tests the real logic and drops the regex source-string guard.

### IN-02: Dead `type` argument on `spawn_particle_burst`

**File:** `main.py:922-942`
**Issue:** `spawn_particle_burst(self, x, y, type="block_break")` takes a `type` argument that the comment describes as "reserved for future variants (fuse, impact, damage)" but the function body reads `u, v = PARTICLE_BURST_U, PARTICLE_BURST_V` unconditionally. All four call sites pass `type="block_break"`, `type="boost_trail"`, or `type="charge_flash"`, and the function silently treats them identically. Shadowing the built-in `type` is also a style smell (the linter will flag it in most pyflakes-style configs).

**Fix:** Either branch on `type` (map string → (u, v) pair) or drop the argument until the Phase 32 variants land. If dropped, the deprecation shim `spawn_explosion` becomes simpler too. Rename the parameter to `burst_type` regardless, to avoid shadowing `type`.

### IN-03: Dead/ignored `color` argument on `spawn_explosion` shim

**File:** `main.py:944-951`, call sites `src/entities/player.py:733, 786, 826`
**Issue:** `spawn_explosion(x, y, color)` is a documented no-op shim that ignores `color`. All three live call sites pass `color=9` (a bare magic number). This is code the phase deliberately chose not to migrate, but the cleanup is trivial and the comment at `main.py:949` says "remove this method once all call sites use spawn_particle_burst directly." Now is an easy time.

**Fix:** Replace the three `self.game.spawn_explosion(tx * tuning.TILE_SIZE, ty * tuning.TILE_SIZE, 9)` calls with `self.game.spawn_particle_burst(tx * tuning.TILE_SIZE, ty * tuning.TILE_SIZE, type="block_break")` and delete the `spawn_explosion` shim. Eliminates one magic number per call.

### IN-04: `BURST_PARTICLE_SPEED = 1.5` comment understates behavior

**File:** `main.py:160`
**Issue:** Comment reads "pixels per frame outward" but `Particle.update` at `src/entities/effects.py:60` applies `self.dy += PARTICLE_GRAVITY` each tick, so the trajectory is parabolic, not straight-line outward at 1.5 px/frame. Not a bug, just a misleading comment.

**Fix:** Update to "initial outward speed (px/frame); gravity applies afterwards."

### IN-05: `SPRITE_MANIFEST` `tiles` entry has irregular spacing

**File:** `main.py:144-156`
**Issue:** The manifest dict uses aligned-column formatting; the `particles` addition breaks alignment slightly. Minor, but `SPRITE_MANIFEST["tiles"][3]` is `"assets/tiles.png"` (literal string) while `_load_sprites` replaces it with the schema-driven `schema.get_tileset_path()` — the literal value is effectively ignored, which is a micro-surprise for readers.

**Fix:** Document (comment) that `SPRITE_MANIFEST["tiles"][3]` is overridden by `_load_sprites`, or set it to `None` so the override is obvious.

### IN-06: `_pause_ticks` underflow guard is correct but subtle

**File:** `src/anim/anim_player.py:32-34`
**Issue:** `if self._pause_ticks > 0: self._pause_ticks -= 1; return`. Correct but the sentinel path (`pause_ticks == 1` on entry → decrement to 0 → return without ticking the frame counter) means the frame advance is skipped for one extra tick compared to "frozen duration only." Tests `test_pause_for_freezes_ticks` verify and lock in the current behavior. No fix required, but worth adding a one-line comment explaining that on the resume tick the frame counter is NOT incremented (the pause consumes that tick fully).

**Fix:** Add clarifying comment:

```python
if self._pause_ticks > 0:
    self._pause_ticks -= 1
    return   # resume tick does NOT advance clip_ticks -- pause consumes the full tick
```

### IN-07: Test discovery order dependency via `tuning.load_anim()` side effects

**File:** `tests/test_tuning_anim.py:67, 82, 90, etc.`, `tests/test_anim.py:444-465`
**Issue:** Many tests call `tuning.load_anim()` at top of body or mutate it via `tuning.set_anim_value` and `tuning.load_anim(schema_path=tmp_path/...)`. Some restore state at the end (`test_load_preset_routes_anim_keys` at `tests/test_tuning_anim.py:180-182`), most do not. Test order becomes load-bearing: if `test_build_player_fsm_picks_up_new_durations_on_rebuild` is followed by `test_build_player_fsm_reads_from_tuning_anim`, the former restores the original duration before returning; but parallel tests (`pytest-xdist`) or different collection orders could expose brittleness.

No autouse fixture calls `tuning.load_anim()` to reset the anim namespace between tests.

**Fix:** Add a `conftest.py` autouse fixture that calls `tuning.load_anim()` before each test (mirroring the `event_bus.reset()` pattern mentioned in `event_bus.py:22`). Or document in a contributor note that anim tests must restore state and rely on `load_anim()` idempotence.

---

_Reviewed: 2026-04-22T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
