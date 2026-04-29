---
phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
fixed_at: 2026-04-29T09:20:12Z
review_path: .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-REVIEW.md
iteration: 1
findings_in_scope: 11
fixed: 8
skipped: 3
status: partial
---

# Phase 33: Code Review Fix Report

**Fixed at:** 2026-04-29T09:20:12Z
**Source review:** `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 11 (3 BLOCKER + 8 WARNING; 5 INFO out of scope)
- Fixed: 8 (3 BLOCKER + 5 WARNING)
- Skipped: 3 WARNING (documented below)

**Regression check:** Full Phase 33 test suite (113 tests) GREEN after all fixes:
`tests/test_destructive_drill.py tests/test_daze_shot.py tests/test_audio.py tests/test_pogo.py tests/test_fusion_fsm.py tests/test_drill_dive_parity.py tests/test_debug.py tests/test_enemies.py tests/test_event_bus.py tests/test_tuning_migration.py tests/test_fusion.py tests/test_fusion_protocol.py` — 113 passed, 1 skipped (pre-existing).

Broader suite check: 467 passed / 7 pre-existing failures (test_ldtk_migration, test_phase05_nyquist, test_phase22, test_physics, test_sprite_assets, test_tuning) — verified pre-existing by stash-comparison; not introduced by Phase 33 fixes.

## Fixed Issues

### BL-01: Daze-shot stun is dead code in production

**Files modified:** `main.py`
**Commit:** ce8cf0c
**Applied fix:** Moved `apply_daze_stun_contacts(self.projectiles, self.enemies)` from after the per-enemy projectile combat loop to BEFORE it. Previously the canonical loop called `e.take_damage(1)` and set `p.is_active = False` for every active projectile, consuming daze projectiles before the stun scan ever ran. The re-filter `self.projectiles = [p for p in self.projectiles if p.is_active]` now lives once after the stains update and absorbs both the daze-scan and combat-loop consumption. `test_daze_stun_applies_on_snail_contact` and the other 3 daze-shot tests still pass; integration regression test would require a Game.update fixture (out of scope for mechanical fix).

### BL-02: Fused low-juice daze guard early-returns from handle_input

**Files modified:** `src/entities/player.py`
**Commit:** 3d497a8
**Applied fix:** Replaced the bare `return` inside the `self.is_fused` low-juice branch with a fall-through pattern: `proj = None` is set up-front, the guard becomes `if slime.juice >= tuning.SLIME_DAZE_COST:` (positive branch fires + emits + flags), and the no-fire path falls through so movement/jump/charge-controller dispatch still run on the same frame. The `if proj and self.game:` append guard already handled `proj=None` correctly. All 4 daze-shot tests still pass.

### BL-03: Player ability attribute writes in restore_from_save

**Files modified:** `main.py`
**Commit:** 3be9583
**Applied fix:** Removed the four dead writes (`self.player.has_dash`, `has_shield`, `has_shield_t2`, `has_boost`) from `Game.restore_from_save`. These attributes were stripped from `Player.__init__` in Phase 31.5-05; nothing in `src/` reads them (verified with grep). `has_drill` write is preserved (still consumed by drill ability gates). All 32 save-system tests still pass.

### WR-01: FEEL_GROUPS duplicated between panel.py and presets.py

**Files modified:** `src/ui/panel.py`
**Commit:** 14aa087
**Applied fix:** Replaced the `FEEL_GROUPS = {...}` literal in `panel.py` with `from src.ui.presets import FEEL_GROUPS`. No circular-import risk verified (`presets.py` does not import from `panel.py`). `panel.FEEL_GROUPS is presets.FEEL_GROUPS` now holds (single object). Pogo + tuning_migration tests still pass.

### WR-02: pogo.py magic literal 16 for tile size

**Files modified:** `src/fusion/pogo.py`
**Commit:** 2e0bcd8
**Applied fix:** Replaced `tx * 16` / `ty * 16` with `tx * tuning.TILE_SIZE` / `ty * tuning.TILE_SIZE` in the soft-destructible spawn_explosion call. Matches sibling pattern in `src/fusion/drill_dive.py:168-170`. Removed the inline acknowledgement comment. `tuning` already imported at module top. Pogo tests pass.

### WR-04: test_warp_level_constants_exist asymmetry with regex test

**Files modified:** `tests/test_debug.py`
**Commit:** ac5906e
**Applied fix:** Added `assert hasattr(debug, "WARP_LEVEL_BOSS")` and included `"WARP_LEVEL_BOSS"` in the isinstance loop tuple. Both warp-constant tests now check 5 constants symmetrically. All 15 debug tests pass.

### WR-06: _panel_save dead slot >= 0 check

**Files modified:** `main.py`
**Commit:** 8de0aa2
**Applied fix:** Replaced `if slot >= 0:` with `assert slot >= 0, f"active preset slot must be non-negative, got {slot}"`. The defensive check was always-true under current invariants and silently swallowed any future API regression returning a negative slot. Assertion makes the invariant explicit.

### WR-07: presets.save_preset hardcoded schema_version

**Files modified:** `src/ui/presets.py`
**Commit:** cdfb9eb
**Applied fix:** Added `_current_schema_version()` helper that reads `tuning._raw["version"]` (fallback `"unknown"` if `_raw is None`), and replaced the hardcoded `"schema_version": "0.3.0"` literal with the helper call. Existing tests that construct preset dicts with `schema_version: "0.3.0"` are unaffected (those are input fixtures, not output assertions). Tuning-anim tests pass; pre-existing test_tuning failures (5) are unrelated to WR-07 — verified pre-existing by stash-comparison.

## Skipped Issues

### WR-03: Two-tuple-vs-three-tuple unpack of get_destructible_at

**File:** `src/fusion/drill_dive.py:151-157`, `src/fusion/pogo.py:92-101`
**Reason:** "skipped: design refactor too risky for mechanical fix — production tests use 3-tuple shape". The review recommends "Pick one shape and enforce it." Removing the test-mock branch would break `test_drill_dive_parity.py:206` (`return (SOFT_TX, SOFT_TY, None)`) and `test_drill_dive_parity.py:254` (`return (CRACKED_TX, CRACKED_TY, INTGRID_CRACKED_V_VALUE)`), both of which deliberately return 3-tuples. The alternative — promoting production `get_destructible_at` to return 3-tuples — is a wider API change (`src/level/map.py:375-386`) with cross-cutting impact on any caller. Either resolution requires human judgment about the canonical API shape; deferring to a follow-up phase.
**Original issue:** Production `get_destructible_at` returns 2-tuple per docstring; only test mocks return 3-tuple. The current dual-shape API is fragile (a 4-tuple would silently grab tile_coord[2] as wrong field).

### WR-05: Audio cues all share channel 0

**File:** `src/core/audio.py:42-43, 78-89`
**Reason:** "skipped: existing test contract pins channel 0; non-trivial refactor". `tests/test_audio.py:42-47` asserts `pyxel.play.assert_called_once_with(0, audio.SFX_DRILL_ENEMY_HIT)` — channel 0 is hard-pinned. Implementing per-cue channel routing or debounce requires updating this test contract and is a meaningful design decision (per the review, this is "Phase 35's problem"). Leaving for a follow-up phase as planned.
**Original issue:** Fast-fired SFX (drill_block_break + drill_enemy_hit on adjacent frames, daze_fire mid-drill, pogo_bounce after drill_block_break) cut each other off mid-playback because all 7 cues share channel 0.

### WR-08: Auto-aim skips slime.x in initial target_dx/target_dy

**File:** `src/entities/player.py:209-264`
**Reason:** "skipped: pre-existing pre-Phase-33 behavior; review explicitly notes 'or document the choice if intentional'". The review states "This is pre-existing behavior, not a Phase 33 regression." Worth noting because the daze branch inherits the bug, but the fix is a feel/design decision (aim from player intent vs aim from slime origin) that affects projectile arc behavior across all spit + daze fires. Cross-cutting feel change requires playtest validation, not mechanical edit.
**Original issue:** Lines 209-219 set target_dx/target_dy treating player position as origin; auto-aim block at 251-264 computes from slime origin. When auto-aim doesn't fire (best_enemy is None), the input-derived aim plus slime-spawned projectile creates a slight angle error in the spit arc.

---

_Fixed: 2026-04-29T09:20:12Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
