---
phase: 25-call-site-migration-constants-tuning
reviewed: 2026-04-12T00:00:00Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - src/entities/player.py
  - src/entities/slime.py
  - src/entities/projectile.py
  - src/entities/boss.py
  - src/entities/enemies.py
  - src/entities/effects.py
  - src/entities/save_point.py
  - src/entities/items.py
  - src/level/map.py
  - src/level/world.py
  - src/core/save_manager.py
  - src/core/sprite_utils.py
  - tests/test_tuning_livereach.py
findings:
  critical: 0
  warning: 3
  info: 6
  total: 9
status: issues_found
---

# Phase 25: Code Review Report

**Reviewed:** 2026-04-12
**Depth:** standard
**Files Reviewed:** 13
**Status:** issues_found

## Summary

The Phase 25 mechanical migration is structurally sound. A grep across
`src/` confirms the only residual `from src.core.constants import …`
lines are the two documented `HAZARD_DRAIN_RATES` exceptions
(`src/entities/player.py:3` and `src/level/map.py:7`). Every one of the
75 distinct `tuning.X` names used across the 12 migrated files resolves
cleanly against the live `src/core/tuning.py` `_flat_index` (verified by
import-time `getattr`), so there are **no typos** in migrated keys. The
`tests/test_tuning_livereach.py` suite correctly proves
`tuning.set_value()` round-trip for GRAVITY, JUMP_FORCE, MAX_WALK_SPEED,
and WALK_FRICTION — the harness, mocks, and assertions line up with the
actual player update loop, and the baseline values (WALK_ACCEL=0.125,
MAX_WALK_SPEED=1.25, WALK_FRICTION=0.15, GRAVITY=0.0875,
JUMP_FORCE=-3.25) all match the comments and saturation math in the
test.

However, the review found **three module-load-time value captures** that
are inconsistent with the migration's stated success criterion ("no
mid-run caching of physics values"). All three live *outside* the player
hot path, which is why the livereach test suite does not catch them:

1. `src/level/world.py` lines 28-29 — `WorldManager.SCREEN_W` /
   `SCREEN_H` are class attributes initialised from `tuning.VIEWPORT_W/H`
   at *class-definition* time.
2. `src/level/map.py` line 12 — `TILES_PER_ROW` captures
   `tuning.TILE_SIZE` at module-load time.
3. `src/level/map.py` line 16 — `_EMPTY_8PX` captures `tuning.TILE_EMPTY`
   at module-load time.

None of these keys is likely to be live-tuned in practice, but they are
exposed on the tuning module and Phase 28's panel could in theory edit
them, so `set_value('VIEWPORT_W', …)` would silently drift the camera
math vs. the actual viewport. These should either be migrated to
use-site reads or explicitly documented as "baked at import" in
25-CONTEXT.md alongside the HAZARD_DRAIN_RATES carve-out.

The default-argument capture in `src/core/sprite_utils.py:8-9` is
already explicitly documented in the docstring as a consciously accepted
D-01 exception, so it is reported only as an Info item.

A handful of unrelated pre-existing quality issues surfaced during the
read-through (bare except in `map.py:183`, unencoded file opens,
`SaveManager.load` lacking JSON error handling, magic numbers in
`player.py` / `slime.py`). These are not Phase 25 regressions and should
be triaged separately.

## Warnings

### WR-01: `WorldManager` class attributes capture viewport tuning at import time

**File:** `src/level/world.py:28-29`
**Issue:** `SCREEN_W = tuning.VIEWPORT_W` and `SCREEN_H = tuning.VIEWPORT_H`
are evaluated exactly once, when the `class WorldManager:` statement
runs at module import. Every subsequent `self.SCREEN_W` read inside
`get_camera_clamped`, `trigger_transition`, and the settle math
references that frozen snapshot, so a live `tuning.set_value("VIEWPORT_W", …)`
from the Phase 28 panel would not reach camera clamping until the next
full process restart. This violates the Phase 25 acceptance rule "no
mid-run caching of physics values" — the same rule the livereach test
enforces for the player hot path. The livereach test does not catch
this because it mocks the level and never exercises camera math.
**Fix:** Convert the class attributes into use-site reads. Either drop
the class attributes and read `tuning.VIEWPORT_W` / `tuning.VIEWPORT_H`
directly at each call site, or expose them as properties:
```python
class WorldManager:
    # Transition states
    STATE_PLAYING = "PLAYING"
    ...

    @property
    def SCREEN_W(self):
        return tuning.VIEWPORT_W

    @property
    def SCREEN_H(self):
        return tuning.VIEWPORT_H
```
Alternatively, if viewport tuning is deliberately *not* meant to be
live-edited, add an explicit carve-out note in 25-CONTEXT.md alongside
the existing HAZARD_DRAIN_RATES exception so future auditors do not
flag the same issue.

### WR-02: `map.py` captures `TILE_SIZE` / `TILE_EMPTY` at module-load time

**File:** `src/level/map.py:12,16`
**Issue:** Two module-level captures:
```python
TILES_PER_ROW = 256 // tuning.TILE_SIZE        # line 12
_EMPTY_8PX = (tuning.TILE_EMPTY[0] * 2,
              tuning.TILE_EMPTY[1] * 2)         # line 16
```
Both read `tuning.*` exactly once at import. `TILES_PER_ROW` is used
inside `load_from_ldtk_simplified` and `load_from_tiled` (lines 181,
497), and `_EMPTY_8PX` is used inside `_clear_tilemap` (line 42). If
Phase 28 were to live-edit `TILE_SIZE` or `TILE_EMPTY`, every subsequent
map reload would still use the stale derived values. TILE_SIZE is almost
certainly a "don't live-edit" value in practice, but the migration rule
from 25-CONTEXT D-04 does not grant it an exception.
**Fix:** Inline the reads at use sites, or convert into a small helper
function:
```python
def _tiles_per_row():
    return 256 // tuning.TILE_SIZE

def _empty_8px():
    return (tuning.TILE_EMPTY[0] * 2, tuning.TILE_EMPTY[1] * 2)
```
…and replace the six references accordingly. Alternatively, document
`TILE_SIZE` and `TILE_EMPTY` as additional named carve-outs in
25-CONTEXT.md next to HAZARD_DRAIN_RATES.

### WR-03: Bare `except:` swallows KeyboardInterrupt and SystemExit

**File:** `src/level/map.py:183`
**Issue:**
```python
try:
    v = int(val)
    if is_intgrid:
        ...
    else:
        ...
except: continue
```
A bare `except:` with no exception type catches `KeyboardInterrupt`,
`SystemExit`, and `GeneratorExit`. During a full LDtk reload this means
a Ctrl+C in the middle of parsing could be silently absorbed as "bad
tile data, skip", leaving the game in an inconsistent partially-loaded
state. Pre-existing, not a Phase 25 regression, but worth fixing.
**Fix:** Narrow to the exception types the parser actually expects:
```python
try:
    v = int(val)
    ...
except (ValueError, KeyError):
    continue
```

## Info

### IN-01: `draw_sprite` captures `SPRITE_SIZE` as a default argument (documented exception)

**File:** `src/core/sprite_utils.py:8-9`
**Issue:** `def draw_sprite(..., visual_w=tuning.SPRITE_SIZE, visual_h=tuning.SPRITE_SIZE, …)`
captures the sprite size at def-time. The docstring (lines 12-15)
explicitly labels this as an accepted D-01 decision consistent with the
"grep uniformity rule for module-load-time constants", and all on-path
callers in the 12 migrated files pass `tuning.SPRITE_SIZE` explicitly
(e.g. `slime.py:326`, `effects.py:33`, `items.py:57`), so the default is
only a fallback for callers that do not care. This is noted here only
for audit completeness — it is already a documented exception and no
action is required.
**Fix:** None. If the Phase 28 panel ever acquires the ability to live-
tune SPRITE_SIZE (it does not today), revisit this decision.

### IN-02: Livereach suite covers only 4 of ~75 migrated keys

**File:** `tests/test_tuning_livereach.py`
**Issue:** The test file proves live-reach for GRAVITY, JUMP_FORCE,
MAX_WALK_SPEED, and WALK_FRICTION. These are the four most gameplay-
critical keys, and the harness is correct for them. But the migration
touched ~75 distinct `tuning.*` names (DRILL_SPEED, BOOST_FORCE,
RAM_SPEED, DASH_SPEED, PROJECTILE_SPEED, etc.). If a future refactor
introduces a module-load-time capture for any of the untested keys, CI
will stay green. The test's own docstring frames it as the "acceptance
artifact" for FND-05, so this is a scope decision rather than a bug —
but it is worth recording in 25-VERIFICATION.md that the test is a
**sampling** check, not an exhaustive one.
**Fix:** Optional — add a parametrised meta-test that iterates over all
flat keys in `tuning._flat_index` and asserts that at least one caller
references them via `tuning.X` rather than a module-level capture. This
would use AST walking rather than runtime mutation and is a larger task;
record as backlog if not tackled now.

### IN-03: File opens without explicit encoding on Windows

**File:** `src/level/map.py:98,157,211,422,468`; `src/core/save_manager.py:52,61`
**Issue:** Every `open(...)` call in these files omits the `encoding=`
argument, so Python defaults to the platform locale encoding. On Windows
(the current dev environment per `<env>`) this is typically cp1252, not
UTF-8, which can corrupt LDtk JSON that contains non-ASCII level names
or non-ASCII fields in save files. Pre-existing, not introduced by
Phase 25.
**Fix:** Add `encoding="utf-8"` to every `open()` in these files:
```python
with open(path, "r", encoding="utf-8") as f:
    ...
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
```

### IN-04: `SaveManager.load` has no JSON error handling

**File:** `src/core/save_manager.py:55-62`
**Issue:** `load()` does `json.load(f)` with no try/except. A truncated,
malformed, or hand-edited save file will raise `json.JSONDecodeError`
straight into the Game boot path and crash the player into a traceback
with no recovery. Pre-existing, not a Phase 25 regression.
**Fix:** Wrap in a try/except and return None (same contract as
"missing file"):
```python
try:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
except (json.JSONDecodeError, OSError) as e:
    print(f"SaveManager.load: corrupted save at {path}: {e}")
    return None
```

### IN-05: `SaveManager.save` crashes if `world.current_level is None`

**File:** `src/core/save_manager.py:47`
**Issue:** `"save_room_id": world.current_level.id` will raise
`AttributeError` if `current_level` is None (e.g. SavePoint triggered
outside any level bounds, or during a transition edge case). The caller
(`game.save_game`) presumably guards this, but the manager itself has no
defensive check and gives a confusing traceback if the invariant is
violated. Pre-existing, not a Phase 25 regression.
**Fix:** Either guard at entry:
```python
if world.current_level is None:
    raise RuntimeError("SaveManager.save: no current_level")
```
…or make the field optional: `world.current_level.id if world.current_level else None`
and handle the None on load.

### IN-06: Magic numbers in player / slime / projectile / effects

**File:** multiple
**Issue:** Per the project-memory rule "Avoid magic numbers — use named
constants or comments for all numeric literals", several hand-picked
literals should live in `tuning.*` or at least as documented module
constants:
- `src/entities/player.py:110` — `self.invuln_timer = 9999` (ram
  invincibility, "Will be cleared on ram end"); a named
  `RAM_INVULN_SENTINEL = 9999` would make the special value searchable.
- `src/entities/player.py:175,184,202` — `shield_flash_timer = 8`,
  `knockback_timer = 10` (two sites).
- `src/entities/projectile.py:16,66` — `self.gravity = 0.0375` (normal
  spit) and `self.gravity = 0.0125` (charge shot). These are the exact
  values the auto-aim ballistic math at `player.py:376` silently
  duplicates (`0.5 * 0.0375 * t * t`), so a drift between the two
  sites is a real correctness risk.
- `src/entities/slime.py:41-45` — hardcoded companion physics
  (`accel=0.05`, `friction=0.0375`, `max_speed=1.5`, `gravity=0.05`,
  `jump_force=-1.75`). Probably intentional "companion feel" separation
  from player tuning, but none of them is commented as such.
- `src/entities/effects.py:13,42,48` — `max_frames=24`,
  `random.randint(20, 40)`, `dy += 0.025`.
- `src/entities/items.py:26` — `slime.max_juice + 50` for MISSILE
  pickup magnitude.

Pre-existing debt, not a Phase 25 regression. Worth adding to the
backlog next to the 25-CONTEXT carve-out list.
**Fix:** Promote into `assets/physics-schema.json` under a new
`projectile` / `companion` / `pickups` group and read via
`tuning.X` at the use sites, matching the pattern Phase 25 established
for player physics. Projectile gravity in particular should be a single
named value shared by `Projectile.__init__` and the auto-aim ballistic
compensation at `player.py:376`.

---

_Reviewed: 2026-04-12_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
