# Phase 25: Call-Site Migration (constants → tuning) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-11
**Phase:** 25-call-site-migration-constants-tuning
**Areas discussed:** Caching policy, Migration scope, Player.py wildcard / import form, Verification strategy

---

## Caching Policy

### Initial framing (rejected after user pushback)

Three-option question: Mechanical rename vs Physics-only strict (`@property`-based live reads for instance-init captures) vs Partial per-file.

| Option | Description | Selected |
|--------|-------------|----------|
| Mechanical rename | 1-to-1 find-and-replace; `__init__` captures of non-feel values stay. Cleanest, matches Phase 24 D-13. | (not reached — reframed) |
| Physics-only strict | Every call site, including `__init__`, reads `tuning.*` fresh via `@property`. | (not reached — reframed) |
| Partial, per-file | Planner decides per file. | (not reached — reframed) |

**User's clarification:** "what is the biggest concern here? I thought the adjustment overlay was for physics controls."

This reframed the question. The Phase 28 panel is for physics/feel only — `GRAVITY`, `JUMP_FORCE`, `FRICTION`, `MAX_WALK_SPEED`, etc. Non-feel values like `PLAYER_MAX_HP`, `SAVE_FILE`, `SPRITE_SIZE` will never be scrubbed live, so `self.max_hp = tuning.PLAYER_MAX_HP`-style captures are fine as-is. The "physics-only strict" option was solving a problem that doesn't exist.

### Reframed question

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — mechanical rename | Per-frame physics reads become `tuning.X`; `__init__` captures of non-feel values stay. | ✓ |
| Yes, but flag edge cases | Same, but planner explicitly calls out ambiguous cases (read both in __init__ and update()). | |
| Something else | User has a different mental model. | |

**User's choice:** Yes — mechanical rename.
**Notes:** The panel scope (physics/feel only) is the load-bearing constraint. Captured non-feel values don't need live reach.

---

## Migration Scope

| Option | Description | Selected |
|--------|-------------|----------|
| 12 hot-path only; shim stays | Migrate the 12 files enumerated in Phase 24 CONTEXT. Tests and scripts stay on shim. Smallest diff. | ✓ |
| 12 hot-path + tests | Also migrate the 27 test files that import constants. | |
| Everything; delete shim | Migrate all callers including `export_tilemap_csv.py`, delete `constants.py`. Cleanest end state but highest risk. | |
| 12 hot-path + delete shim | Migrate 12 files, delete shim, force test migration via breakage. Aggressive. | |

**User's choice:** 12 hot-path only; shim stays.
**Notes:** Matches Phase 24's stated boundary. No forcing function to migrate tests — leave them alone.

---

## Player.py Wildcard / Import Form

| Option | Description | Selected |
|--------|-------------|----------|
| `from src.core import tuning` | Prefix every use site with `tuning.`. Explicit, matches Phase 24 D-13 example. | ✓ |
| `import src.core.tuning as t` | Short alias, less typing in dense physics code. | |
| Explicit from-import list | `from src.core.tuning import GRAVITY, ...` — re-introduces the bug this phase fixes. Listed only for explicit rejection. | |

**User's choice:** `from src.core import tuning`.
**Notes:** Explicit `tuning.` prefix at every use site is the point — a reviewer grepping for `tuning.` gets the exact set of live-tuning-reachable sites.

---

## Verification Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Unit test + manual playtest | Pytest asserts `set_value()` visibility via Player.update(); manual v1.3 regression playthrough for criterion #3. No keybinds, no replay rig. | ✓ |
| Unit test + temporary debug keybind | Same test plus a temporary F9 keybind to mutate `tuning.GRAVITY` live during playtest. Keybind reverted before commit. | |
| Unit tests only | Skip manual verification; trust the test and normal playthrough. | |
| Scripted playthrough diff | Record per-frame player state before/after migration, diff. Repeatable artifact for criterion #3. | |

**User's choice:** Unit test + manual playtest.
**Notes:** Temporary keybinds risk getting left in; scripted playthrough diff is overbuilt. Unit test + human playtest is the right cost/confidence tradeoff for a mechanical refactor.

---

## Claude's Discretion

- Plan decomposition (one big plan vs split by file) — planner's call.
- Atomic commit boundaries — planner's call.
- Test method names and pytest fixture style — planner's call.
- Test file location (alongside `test_tuning.py` vs new file) — planner's call.
- Order of operations for killing the player.py wildcard — planner's call.

## Deferred Ideas

- Migrating tests/ off the shim (future tests-modernization pass).
- Deleting `src/core/constants.py` entirely (blocked on test migration).
- Headless scripted playthrough diff (future regression-suite phase).
- Temporary debug keybind for live `set_value()` (Phase 28's panel replaces it).
- `@property`-based live `self.max_hp` (pre-empted by user's panel-scope reframing).
- Per-group namespace access (`tuning.movement.GRAVITY`) — already rejected in Phase 24 D-13.
