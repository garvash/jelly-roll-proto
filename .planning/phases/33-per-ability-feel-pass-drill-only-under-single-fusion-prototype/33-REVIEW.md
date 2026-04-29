---
phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
reviewed: 2026-04-29T00:00:00Z
depth: standard
files_reviewed: 21
files_reviewed_list:
  - main.py
  - src/core/audio.py
  - src/core/debug.py
  - src/entities/enemies.py
  - src/entities/player.py
  - src/entities/projectile.py
  - src/fusion/charge_controller.py
  - src/fusion/drill_dive.py
  - src/fusion/manager.py
  - src/fusion/pogo.py
  - src/ui/panel.py
  - src/ui/presets.py
  - assets/physics-schema.json
  - assets/presets/slot_1.json
  - tests/conftest.py
  - tests/test_audio.py
  - tests/test_daze_shot.py
  - tests/test_debug.py
  - tests/test_destructive_drill.py
  - tests/test_enemies.py
  - tests/test_fusion_fsm.py
  - tests/test_pogo.py
  - tests/test_tuning_migration.py
findings:
  blocker: 3
  warning: 8
  info: 5
  total: 16
status: issues_found
---

# Phase 33: Code Review Report

**Reviewed:** 2026-04-29
**Depth:** standard
**Files Reviewed:** 21
**Status:** issues_found

## Summary

Phase 33 lands a per-ability feel pass for the drill-only fusion: tuning-key migration (6 new keys), destructive-drill enemy interaction, daze-shot fused branch (Z-tap while fused), audio + particle subscriber wiring, debug warps (Ctrl+4..8), and a v2.0-default preset bake. The unit-test scaffolding is comprehensive and the fusion ability/manager split is generally clean.

The headline defect: **the daze-shot stun primitive does not work in production**. The new `apply_daze_stun_contacts` helper runs AFTER the existing per-frame projectile-vs-enemy combat loop in `Game.update`, which already consumes any colliding projectile (regardless of `applies_daze_stun`) and deals 1 damage. By the time the daze contact scan executes, daze projectiles are inactive and the target enemy has already been damaged or killed. The `test_daze_stun_applies_on_snail_contact` test passes because it bypasses `Game.update` and calls the helper directly, hiding the integration regression.

Two additional blockers: a `return` in the fused-branch low-juice guard skips the rest of `Player.handle_input` for that frame (no movement, no jump, no charge controller dispatch), and `Game.restore_from_save` writes attributes to `Player` (`has_dash`, `has_shield`, `has_shield_t2`, `has_boost`) that no longer exist on the class — saved-state reads of those fields are silently lost.

## Blocker Issues

### BL-01: Daze-shot stun is dead code in production — projectile loop consumes daze projectiles before the contact scan runs

**File:** `main.py:877-921`
**Issue:** In `Game.update`, the canonical per-frame enemy-projectile loop runs first (lines 877-901). For every active projectile that intersects an alive enemy, it calls `e.take_damage(getattr(p, 'damage', 1))` (defaults to 1 since `Projectile` has no `damage` attribute) and sets `p.is_active = False`. This consumes the projectile and damages/kills the enemy before any daze-specific handling runs. The new `apply_daze_stun_contacts(self.projectiles, self.enemies)` call at line 919 then iterates again, but every daze projectile is already inactive (line 236 `if not proj.is_active: continue` short-circuits), and any enemy with HP=1 is already dead.

The unit test `test_daze_stun_applies_on_snail_contact` (tests/test_daze_shot.py:107-145) does not catch this because it constructs a `Snail` and projectile in isolation and calls `apply_daze_stun_contacts` directly — bypassing the standard `Game.update` projectile loop. In actual gameplay, daze-flagged projectiles behave identically to regular spit shots (1 damage, no stun).

**Fix:** Either short-circuit the standard projectile loop for daze-flagged projectiles, or run `apply_daze_stun_contacts` BEFORE the enemy-projectile loop. Recommended (minimal-diff): handle daze first, so daze projectiles are consumed by the daze path and never reach the standard damage loop:

```python
# 5b. Apply daze stuns BEFORE the standard projectile-damage loop so daze
# projectiles never reach the regular take_damage path.
apply_daze_stun_contacts(self.projectiles, self.enemies)

# Update enemies & Combat
for e in self.enemies:
    e.update(self.player, self.level_map, slime=self.slime)
    if not e.is_alive: continue

    for p in self.projectiles:
        if p.is_active and e.check_collision(p.x, p.y, p.w, p.h):
            ...
```

Alternatively, gate the standard loop with `if p.is_active and not getattr(p, 'applies_daze_stun', False) and ...`. Either fix must be backed by an integration test that exercises both branches via `Game.update` (or a tighter equivalent), since the existing helper-only test cannot detect the ordering regression.

---

### BL-02: Fused low-juice daze guard `return`s from handle_input mid-frame — drops movement, jump, and charge-controller input

**File:** `src/entities/player.py:273-276`
**Issue:** The cancel-spam guard for the fused daze branch:

```python
if self.is_fused:
    if slime.juice < tuning.SLIME_DAZE_COST:
        return  # <-- exits Player.handle_input entirely
```

This `return` exits `handle_input` for the rest of the frame, skipping horizontal movement (lines 313-345), wall detection (347-362), jump handling (364-395), the `charge_controller.handle_z_input` dispatch (297-298), and `fusion_manager.handle_jump_input` (305-306). It only fires on frames where `was_tap("spit")` is True (which happens at the moment of a Z release after a brief tap), so the impact is bounded to a single frame, but the asymmetry is real and observable: a fused player with insufficient juice who taps Z loses one frame of input agency. The matching unfused branch on line 283 falls through without `return`.

Test coverage gap: `test_daze_blocked_on_low_juice` only verifies juice and event count, not that subsequent input handling proceeds normally.

**Fix:** Replace the early `return` with a no-op that lets `handle_input` continue. Wrap the daze-fire logic in an `else` or guard the projectile spawn rather than aborting the function:

```python
if self.is_fused:
    if slime.juice >= tuning.SLIME_DAZE_COST:
        slime.consume(tuning.SLIME_DAZE_COST)
        from src.entities.projectile import Projectile
        proj = Projectile(slime.x + slime.w // 2 - 2, slime.y,
                          target_dx, target_dy, self.level_map)
        proj.applies_daze_stun = True
        event_bus.emit("daze_fire")
    else:
        proj = None  # insufficient juice; fall through to normal input
else:
    proj = slime.spit(target_dx, target_dy, self.level_map)
if proj and self.game:
    self.game.projectiles.append(proj)
```

Add a regression test asserting that, after a low-juice fused tap, `Player.handle_input` still applies left/right/jump input on the same frame.

---

### BL-03: `Game.restore_from_save` writes Player attributes that no longer exist — saved item state silently dropped

**File:** `main.py:1290-1293`
**Issue:** After Phase 31.5 stripped `has_dash`, `has_shield`, `has_shield_t2`, `has_boost` from `Player.__init__` (per the comment at `tests/test_debug.py:32-46`), `restore_from_save` still does:

```python
self.player.has_dash = p.get("has_dash", False)
self.player.has_shield = p.get("has_shield", False)
self.player.has_shield_t2 = p.get("has_shield_t2", False)
self.player.has_boost = p.get("has_boost", False)
```

These set arbitrary instance attributes on the Player (Python permits silent attribute creation on instances), but no game logic reads them anywhere — `grep -r "has_dash\|has_shield\|has_boost"` in `src/` returns zero matches. A save that previously set `has_drill=True` correctly restores; a save that set any of the other ability flags becomes a no-op. If those flags re-enter the codebase later, this code path will write stale values that desync from new logic.

This is also a load-time foot-gun: if any of these attribute names are later repurposed as `@property` (like `is_fused` was in this same phase), `restore_from_save` will raise `AttributeError: can't set attribute` at runtime when loading a save.

**Fix:** Delete the stale attribute writes (Phase 31.5 should have done this; it slipped through the sympathetic-regression sweep):

```python
self.player.has_drill = p.get("has_drill", False)
# has_dash / has_shield / has_shield_t2 / has_boost stripped in Phase 31.5
# (sole surviving fusion item in v2.0 is drill — see test_debug.py:32-46).
```

Verify save-file format compatibility (writers may still emit these keys; readers can `.get(..., False)` to discard them gracefully).

---

## Warnings

### WR-01: `FEEL_GROUPS` set duplicated between `panel.py` and `presets.py` — drift hazard

**File:** `src/ui/panel.py:74-78`, `src/ui/presets.py:18-22`
**Issue:** Both modules define an identical `FEEL_GROUPS` set. Phase 33 D-02 added `pogo` to both copies, but a future addition that updates only one will silently break either the panel display or the save persistence. `test_pogo_in_feel_groups_so_save_preset_persists_pogo_keys` only checks the `presets.py` copy.

**Fix:** Define `FEEL_GROUPS` once (e.g., in `src/ui/presets.py`) and import from `panel.py`:

```python
# src/ui/panel.py
from src.ui.presets import FEEL_GROUPS
```

Alternatively, lift it to `src/core/tuning.py` if other callers might need it.

---

### WR-02: `pogo.py:111-113` — magic literal `16` for tile-size; project memory rule violated

**File:** `src/fusion/pogo.py:111-113`
**Issue:**

```python
player.game.spawn_explosion(
    tx * 16,  # see EXPLOSION_SIZE_PX comment; tile coord
               # is multiplied by tile size at use-site.
    ty * 16,
    EXPLOSION_SIZE_PX,
)
```

Per the project's no-magic-numbers rule (`feedback_magic_numbers.md` in user memory), this should use `tuning.TILE_SIZE`. The sibling code in `drill_dive.py:168-170` already uses `tuning.TILE_SIZE` for the same operation. The inline comment acknowledges the magic number rather than fixing it.

**Fix:**

```python
player.game.spawn_explosion(
    tx * tuning.TILE_SIZE,
    ty * tuning.TILE_SIZE,
    EXPLOSION_SIZE_PX,
)
```

---

### WR-03: Two-tuple-vs-three-tuple unpack of `get_destructible_at` is test-only — production code never returns 3-tuple

**File:** `src/fusion/drill_dive.py:151-157`, `src/fusion/pogo.py:92-101`
**Issue:** Both files unpack `tile_coord` flexibly:

```python
if len(tile_coord) >= 3:
    tx, ty, tile_type = tile_coord[0], tile_coord[1], tile_coord[2]
else:
    tx, ty = tile_coord
    tile_type = player.level_map.get_tile(tx, ty)
```

The docstring for `LevelMap.get_destructible_at` (`src/level/map.py:375-386`) explicitly returns a 2-tuple, and Grep confirms no production return path emits a 3-tuple. The 3-tuple branch exists only to make Wave-0 mocks easier. Production gameplay always falls through to the `len(tile_coord) == 2` branch, which calls `get_tile` for every block-break/pogo-hit — an extra round-trip that mocks were supposed to avoid.

This is also fragile: if a future test stubs `get_destructible_at` to return a 4-tuple by accident, the `tile_coord[2]` indexing will silently grab the wrong field instead of failing.

**Fix:** Either update production `get_destructible_at` to return `(tx, ty, tile_type)` (one source-of-truth, drop the per-call `get_tile` lookup), or remove the test-mock branch and update mocks to return 2-tuples + stub `get_tile`. Pick one shape and enforce it; the current dual-shape API is a smell.

---

### WR-04: `test_warp_level_constants_match_world_identifiers` asserts `len(consts) == 5` while `test_warp_level_constants_exist` only checks 4

**File:** `tests/test_debug.py:73-111`
**Issue:** `test_warp_level_constants_exist` asserts the existence of `WARP_LEVEL_CRACKED_V`, `WARP_LEVEL_SOFT_BLOCK`, `WARP_LEVEL_ENEMY_CLUSTER`, `WARP_LEVEL_JUICE_DRAIN` — 4 constants. `test_warp_level_constants_match_world_identifiers` then does `assert len(consts) == 5` because Ctrl+8 added `WARP_LEVEL_BOSS`. The first test silently passes if `WARP_LEVEL_BOSS` is missing entirely (it doesn't iterate over a fifth name). If a refactor accidentally drops `WARP_LEVEL_BOSS`, only the regex/world-identifier test catches it — and that test's failure message is about the regex match count, not about the missing constant per se.

**Fix:** Update `test_warp_level_constants_exist` to include `WARP_LEVEL_BOSS` so all five constants are checked symmetrically:

```python
for name in ("WARP_LEVEL_CRACKED_V", "WARP_LEVEL_SOFT_BLOCK",
             "WARP_LEVEL_ENEMY_CLUSTER", "WARP_LEVEL_JUICE_DRAIN",
             "WARP_LEVEL_BOSS"):
    val = getattr(debug, name)
    assert isinstance(val, str) and val, f"{name} must be a non-empty str"
```

---

### WR-05: Audio cues all share channel 0 — fast-fired SFX cut each other off mid-playback

**File:** `src/core/audio.py:42-43, 78-89`
**Issue:** Module docstring acknowledges the issue:

> "This means a fast cue can cut off a previous one — acceptable for Phase 33's minimal surface."

But the use-site impact is concrete: when the player drills through a CRACKED_V tile and immediately hits an enemy on the next frame, `drill_block_break` and `drill_enemy_hit` both fire on channel 0 within ~16ms. The second cue truncates the first, and the player perceives a single muddy click instead of two distinct events. Same risk for `daze_fire` mid-drill, or `pogo_bounce` immediately after `drill_block_break`.

This is documented as Phase 35's problem, but it's a regression from the muted Phase 32 baseline — we now ship audible-but-broken audio rather than silent placeholder.

**Fix:** Either (a) reserve at least 2-3 channels and route by category (impacts vs. continuous, or drill vs. non-drill), or (b) gate non-essential cues behind a debounce so the spammy ones (`drill_block_break`) don't blow away the rare ones (`drill_impact`, `fuse_start`). Even a 4-frame debounce on `drill_block_break` would meaningfully improve the sound bed without increasing implementation surface.

---

### WR-06: `_panel_save` callback closure captures stale `tuning_panel.get_active_preset_slot` indirection

**File:** `main.py:290-295`
**Issue:**

```python
def _panel_save():
    slot = tuning_panel.get_active_preset_slot()
    if slot >= 0:
        alias = presets.get_preset_alias(slot)
        presets.save_preset(slot, alias)
tuning_panel._save_callback = _panel_save
```

`_active_preset_slot` defaults to `0` (`panel.py:58`), but the panel's "Save N" button text shows `Save -` only when `slot < 0` (`panel.py:444-447`). Since slot is always `>= 0` in practice, the `if slot >= 0:` branch always runs — the dead-code check is hiding the fact that there's no way to NOT save once the panel is open. This is a defensive check against a state that cannot occur, so an actual bug (e.g., slot=-1 from a future API change) would be silently swallowed instead of surfacing in tests.

**Fix:** Either remove the dead `if slot >= 0:` check (slot is always non-negative under current invariants), or document the invariant and add an assertion:

```python
def _panel_save():
    slot = tuning_panel.get_active_preset_slot()
    assert slot >= 0, f"active preset slot must be non-negative, got {slot}"
    alias = presets.get_preset_alias(slot)
    presets.save_preset(slot, alias)
```

---

### WR-07: `presets.save_preset` hardcodes `schema_version: "0.3.0"` — drifts from `physics-schema.json` version field

**File:** `src/ui/presets.py:50`
**Issue:**

```python
preset = {
    "version": "1.0",
    "schema_version": "0.3.0",  # hardcoded
    ...
}
```

The schema's actual version is read at module load (`assets/physics-schema.json:5` says `"version": "0.3.0"`), but `save_preset` writes a hardcoded literal. If the schema bumps to `0.3.1` or `0.4.0`, every freshly-saved preset will lie about the schema version it was generated against. This breaks any future migration tool that relies on `schema_version` to decide which fields to keep.

**Fix:** Read the schema version at save time:

```python
import json
import pathlib
_SCHEMA_PATH = pathlib.Path(__file__).resolve().parents[2] / "assets" / "physics-schema.json"
def _current_schema_version() -> str:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8")).get("version", "unknown")
# in save_preset:
"schema_version": _current_schema_version(),
```

Or expose the parsed version via `tuning._raw["version"]` and read from there.

---

### WR-08: Auto-aim skips `slime.x` in initial `target_dx`/`target_dy` — projectile origin and aim diverge

**File:** `src/entities/player.py:209-264`
**Issue:** Lines 209-219 set `target_dx`/`target_dy` based on player input direction, treating the player position as the origin. Auto-aim (lines 222-264) then computes `dx = (best_enemy.x + ...) - (slime.x + ...)` — using slime as origin. The projectile is finally spawned from `slime.x + slime.w // 2 - 2` (lines 278 fused / inside `slime.spit` unfused). When auto-aim fires, the aim is correct; when it doesn't (`best_enemy is None`), the input-derived `target_dx/target_dy` is used, but the projectile spawns from slime, not player, so a player-direction `(1, 0)` aim plus slime-spawned projectile creates a slight angle error in the spit arc.

This is pre-existing behavior, not a Phase 33 regression. Worth noting because Phase 33's daze branch reuses the same calculation and inherits the bug.

**Fix:** Compute `target_dx/target_dy` relative to the slime origin from the start:

```python
# Default forward lob — aim from slime, not player
slime_cx = slime.x + slime.w / 2
slime_cy = slime.y + slime.h / 2
# ... build aim vector from slime_cx/cy, not player.x/y
```

Or document the choice if "aim from player intent, fire from slime" is intentional.

---

## Info

### IN-01: Wave-0 / Wave-1 / Wave-2 import-skip pattern leaks into shipped tests

**File:** `tests/test_destructive_drill.py:46-47`, `tests/test_audio.py:20`, `tests/test_daze_shot.py:20`, `tests/test_pogo.py:48-49`, `tests/test_fusion_fsm.py:54-57`
**Issue:** Many tests use `pytest.importorskip("src.fusion.manager")` etc. with comments like "Wave 2 will add DRILL_DAMAGE constant". Phase 33 has shipped — these waves are complete. The `importorskip` clauses now serve no purpose except to silently skip if a developer accidentally breaks an import; the failure mode becomes "test count drops" rather than "test fails loudly".

**Fix:** Convert `importorskip` → direct `import` for shipped functionality. Reserve `importorskip` for genuinely optional dependencies. This makes broken-import regressions surface as test failures, not as shrinking test counts.

---

### IN-02: `pogo.py:36-37` — `EXPLOSION_SIZE_PX` duplicated from `drill_dive.py:34`

**File:** `src/fusion/pogo.py:36-37`
**Issue:**

```python
EXPLOSION_SIZE_PX = 9          # local copy; matches DrillDive (could lift to
                                # a shared location later)
```

Comment acknowledges the duplication. Two definitions; one will drift.

**Fix:** Lift to a shared module (e.g., `src/fusion/__init__.py` or `src/core/constants.py`) and import from there.

---

### IN-03: `WARP_NUDGE = 32` defined inside `Game.update` — local-scope magic constant

**File:** `main.py:696`
**Issue:**

```python
WARP_NUDGE = 32  # px; offset from level top-left so player isn't on a wall
```

Defined inside the function body instead of at module scope alongside other warp constants. This is the only `WARP_*` that lives in `main.py` instead of `src/core/debug.py` (where `WARP_LEVEL_*` constants live).

**Fix:** Move to `src/core/debug.py` next to the level constants:

```python
WARP_NUDGE_PX = 32  # offset from level top-left so player isn't on a wall
```

Then `main.py` reads `debug.WARP_NUDGE_PX`.

---

### IN-04: `test_drill_juice_starvation_after_kill_chain` mock enemy lacks juice-clamp behavior — relies on slime mock

**File:** `tests/test_destructive_drill.py:188-225`
**Issue:** The test asserts `slime.juice == 0.0` after 5 hits at 15 cost each from 30 starting juice. This works because `Slime.consume` clamps to zero (verified by inspection), but the test does not verify the clamp behavior — it depends on the implementation detail. If `Slime.consume` ever stops clamping (e.g., to allow negative juice as a debt mechanic), this test would surface a confusing `juice == -45.0` failure rather than a useful "clamp invariant broken" message.

**Fix:** Add a separate explicit clamp test, and in this test assert `slime.juice <= 0.0` rather than exact equality. Or use `assert slime.juice == 0.0, "Slime.consume must clamp at zero"` so the message is informative.

---

### IN-05: `audio.init_sounds` cue parameters are placeholders — pyxel notes "feel sketches" but commit ships them as final

**File:** `src/core/audio.py:62-75`
**Issue:** Docstring says: "Cue choices below are feel sketches — D-13 (drill identity) + D-15 (palette mapping) + D-20 (pogo confirm-only). Per CONTEXT § Claude's Discretion these can be tweaked via panel iteration in Plan 06."

Phase 33 IS Plan 06 (per the user prompt: "tuning bake. Mid-tuning fixes also rolled into scope"). If iteration didn't happen, ship the placeholder explicitly labeled — otherwise this looks like the user-signed-off cue values, but is actually placeholder content.

**Fix:** Either iterate the cue MML strings (panel-driven feel pass) or update the docstring to say "Phase 33 sign-off cues — re-iterate in Phase 35".

---

_Reviewed: 2026-04-29_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
