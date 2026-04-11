# Phase 25: Call-Site Migration (constants → tuning) - Context

**Gathered:** 2026-04-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Mechanical refactor. Rewrite the 12 hot-path files enumerated in Phase 24's CONTEXT so they read `tuning.*` at use site instead of importing names once at module load. After this phase:

- Every per-frame physics read in `src/entities/` and `src/level/` resolves against the live `_model` in `src/core/tuning.py`, so future `tuning.set_value()` calls (Phase 28 panel) reach gameplay on the next frame.
- Zero behavior change at v1.3 baseline values. Frame-for-frame parity with the pre-migration build is the acceptance bar.
- `src/core/constants.py` stays in place as the compat shim for tests, scripts, and any non-hot-path caller not migrated.

**Out of scope (other phases):**
- Phase 26 — event bus + animation FSM.
- Phase 28 — the live-tuning panel UI that will actually drive `set_value()` in real time.
- Migrating the 27 `tests/test_*.py` files or `export_tilemap_csv.py` — they keep the shim.
- Killing the shim — not until a future cleanup phase, if ever.
- Any refactor of non-feel state fields (HP, save file path, sprite dimensions). See D-01.

</domain>

<decisions>
## Implementation Decisions

### Caching Policy

- **D-01 Mechanical rename.** Every per-frame physics read of a constant becomes `tuning.X`. Instance-init captures of non-feel values (`self.max_hp = tuning.PLAYER_MAX_HP`, `self.save_file = tuning.SAVE_FILE`, `self.sprite_w = tuning.SPRITE_SIZE`, etc.) stay as plain captures — they are not values the Phase 28 panel will scrub live, and making them live properties would invite subtle state-tracking bugs (e.g. `self.hp` clamped against a cap that changed mid-run). The test in D-04 confirms live reach on physics values only; non-feel captures are accepted as static-at-spawn.
- **Rule of thumb for the planner:** if the name appears inside `update()`, `move()`, `apply_gravity()`, `jump()`, `drill_dive()`, or any other per-frame method, it must become `tuning.X`. If it appears inside `__init__` as `self.FOO = X`, leave the capture in place but update its RHS to `tuning.X` for consistency — the RHS is read once so it doesn't matter for hot-reload, but the grep story stays uniform.

### Migration Scope

- **D-02 Twelve hot-path files only.** The migration target is exactly the 12 files Phase 24's CONTEXT.md enumerated:
  - `src/entities/player.py` (~50 keys, dominated by `import *`)
  - `src/entities/slime.py` (~15 keys)
  - `src/entities/projectile.py` (~9 keys)
  - `src/entities/boss.py` (~7 keys)
  - `src/entities/enemies.py` (~2 keys)
  - `src/entities/effects.py` (~3 keys)
  - `src/entities/save_point.py` (~3 keys)
  - `src/entities/items.py` (~3 keys)
  - `src/level/map.py` (~5 keys)
  - `src/level/world.py` (~4 keys)
  - `src/core/save_manager.py` (~1 key)
  - `src/core/sprite_utils.py` (~2 keys)
- **D-02a Compat shim stays.** `src/core/constants.py` remains as a passthrough re-export (`from src.core.tuning import *` + `HAZARD_DRAIN_RATES` int-key fix-up). Tests and `export_tilemap_csv.py` continue to import from it unchanged. No cleanup in this phase.
- **D-02b No test migration.** The 27 `tests/test_*.py` files that `from src.core.constants import ...` are deliberately left alone. They test values at baseline, not live-mutation reach; the shim satisfies them. Migrating them is a churn tax without functional payoff.

### Import Form

- **D-03 Uniform `from src.core import tuning`.** Every migrated file uses `from src.core import tuning` as the single line added, then references `tuning.GRAVITY`, `tuning.JUMP_FORCE`, etc. at every use site.
  - **Rejected:** `from src.core.tuning import GRAVITY, JUMP_FORCE, ...` — this re-introduces the exact import-time binding bug that kills hot-reload. It must not appear anywhere in the 12 migrated files.
  - **Rejected:** short alias `import src.core.tuning as t` — saves characters but obscures that the read is live. The explicit `tuning.` prefix is the point: a reviewer grepping for `tuning.` gets the exact set of live-tuning-reachable sites.
- **D-03a player.py wildcard deletion.** `from src.core.constants import *` at `src/entities/player.py:2` is deleted. Every bare `GRAVITY`, `JUMP_FORCE`, `PLAYER_MAX_HP`, etc. in that file is prefixed with `tuning.`. This is the biggest single change in the phase: ~50 call sites in one 822-line file.
- **D-03b Other files' explicit from-imports rewrite the same way.** e.g. `src/entities/slime.py`'s `from src.core.constants import (...)` block is deleted entirely and replaced with `from src.core import tuning`. The previously-listed names are then prefixed at each call site.

### Verification

- **D-04 Pytest + manual playtest, no keybinds, no replay rig.** Two artifacts prove the phase:
  1. **Unit test in `tests/test_tuning_livereach.py`** (or similar name — planner's call). For each of GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, FRICTION (at minimum), the test: (a) instantiates a Player, (b) drives one `player.update()` and snapshots the physics effect (e.g. `dy` after gravity), (c) calls `tuning.set_value('GRAVITY', 10 * baseline)`, (d) drives another `player.update()`, (e) asserts the physics effect changed in the expected direction. This is the automated proof of success criterion #2.
  2. **Manual v1.3 regression playthrough.** Room 0 → boss room via the standard route: drill dive on a cracked-V, ram on a cracked-H, kick, bubble shield, save, reload. Observe identical behavior to v1.3 baseline. This is the proof of success criterion #3. Document the playthrough in the phase's VERIFICATION.md.
- **D-04a `tuning.reset()` after each livereach test.** Tests must restore baseline in tearDown to avoid cross-test contamination. `tuning.reset()` (no key) restores the whole `_model` from `_baseline` in one call — planner should use a pytest fixture.
- **D-04b No headless replay diff.** Rejected as overbuilt. If the mechanical rename preserves physics, the manual playtest will catch any drift; if it doesn't, the unit test will.
- **D-04c No temporary debug keybind.** Rejected as scaffolding that risks getting left in. The unit test is sufficient automated proof.

### Claude's Discretion

- **Plan decomposition.** Whether to ship this as one big plan or split by file (e.g., `25-01-player.py` which is dominant, then `25-02-entities-small`, `25-03-level`, `25-04-core-subset`). Planner decides based on task-size rules.
- **Atomic commit boundaries.** Planner chooses whether each file gets its own commit or files get bundled. The constraint: every commit must leave the game booting and tests passing.
- **Exact test method names** and pytest fixture style in `test_tuning_livereach.py` (or whatever name). Not load-bearing.
- **Test location.** `tests/test_tuning_livereach.py` is a suggestion; planner may put it next to `test_tuning.py` from Phase 24 or combine them.
- **Handling of player.py's `INTGRID_CRACKED_H = 11` module-level constants** (lines 9–10). These are not from constants.py — they're local literals tagged to an entity schema. Leave untouched. If planner spots similar local constants in other files, same rule: out of scope.
- **Order of operations** for the player.py wildcard kill: the planner decides whether to (a) add the new import first then sweep the file, or (b) delete the wildcard first and let the interpreter find use sites via `NameError`. Both work; option (a) is safer for a 50-site file.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 24 Foundation (read first)
- `.planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md` — the source-of-truth inversion context. Every design decision in Phase 25 builds on D-13 (flat access), D-15 (unique keys), D-17 (the legacy-binding problem this phase solves).
- `src/core/tuning.py` — the PEP 562 loader, `set_value()`/`reset()` API, and flat attribute access. All 12 migrated files import this module. Read its module docstring before touching any call site.
- `src/core/constants.py` — the compat shim. Stays untouched in this phase. Understand the `HAZARD_DRAIN_RATES` int-key fix-up at line 26 so it's not accidentally broken by a renamed reference.
- `assets/physics-schema.json` — the v0.3.0 schema `tuning.py` loads at import time. Reference for which names exist under which groups. 87 flat keys across 22 groups.

### Requirements & Roadmap
- `.planning/REQUIREMENTS.md` §Foundation — FND-05 is the acceptance anchor for this phase. FND-02/04 are closed by Phase 24.
- `.planning/ROADMAP.md` §Phase 25 — the three success criteria (use-site reads, next-frame reach, v1.3 behavior parity).

### The 12 Files That Change
- `src/entities/player.py` — 822 LOC, ~50 tuning-key references, currently uses `from src.core.constants import *`. Dominant work item.
- `src/entities/slime.py` — 360 LOC, ~15 keys, explicit from-import block.
- `src/entities/projectile.py` — 104 LOC, ~9 keys.
- `src/entities/enemies.py` — 144 LOC, ~2 keys.
- `src/entities/boss.py` — 173 LOC, ~7 keys.
- `src/entities/effects.py` — 62 LOC, ~3 keys.
- `src/entities/save_point.py` — 63 LOC, ~3 keys.
- `src/entities/items.py` — 62 LOC, ~3 keys.
- `src/level/map.py` — 503 LOC, ~5 keys.
- `src/level/world.py` — 294 LOC, ~4 keys.
- `src/core/save_manager.py` — 74 LOC, ~1 key.
- `src/core/sprite_utils.py` — 59 LOC, ~2 keys.

**Total:** 2720 LOC, ~104 call sites. The key-count estimates are approximate (regex count of `\bKEY\b` across known flat keys) — planner should treat them as a work-size indicator, not a final count.

### Existing Test Infrastructure (for D-04)
- `tests/test_tuning.py` — Phase 24's test file. Patterns for loading tuning, mutating, resetting, and asserting baseline behavior. New livereach test should live alongside or inside this file.
- `tests/test_physics.py` — existing Player instantiation patterns. Steal the `Player(...)` setup so the livereach test doesn't reinvent the boot harness.

### Files That DO NOT Change in This Phase
- The 27 `tests/test_*.py` files that import from `src.core.constants` — stay on the shim (D-02b).
- `export_tilemap_csv.py` at repo root — stays on the shim.
- `src/core/constants.py` — stays as passthrough shim (D-02a).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`tuning.py` PEP 562 attribute access** — already wired and tested in Phase 24. No loader work needed in this phase; it's strictly a call-site rewrite.
- **`tuning.reset()`** — D-04a uses this to keep livereach tests from contaminating each other. Already exists, already tested.
- **Phase 24's `test_tuning.py`** — the livereach test can use the same schema-load setup.
- **The 22 tuning group names** (`movement`, `forgiving`, `wall`, `slime_follow`, `drill`, `charge_shot`, `boost`, `fusion`, etc.) — the planner doesn't need to touch groups at all since the namespace is flat. Listed here so the planner can sanity-check that every migrated name resolves.

### Established Patterns
- **Absolute imports** — the codebase uses `from src.X import Y`. Every migrated file already does this for `constants`; the rewrite preserves the form (`from src.core import tuning`).
- **One import block at top of file** — current pattern. New `from src.core import tuning` goes into the same block; the old `from src.core.constants import ...` line is deleted, not commented-out.
- **Per-frame update pattern** — every entity has an `update()` or `update(dt)` method that reads constants inline. This is why the rename is all that's needed: the read structure is already per-frame.

### Integration Points
- **Module import order** — `tuning.py` auto-loads on first import (line 284 of tuning.py: `load()` at module bottom). Any file in the 12 that now imports `tuning` will trigger the load if it hasn't happened yet. Order doesn't matter; load is idempotent.
- **Game boot sequence** — `main.py` (or equivalent entrypoint) imports the entities. The first entity import now triggers `tuning.load()`, which reads `physics-schema.json`, builds `_flat_index`, captures `_baseline`. All unchanged by Phase 25.
- **Test boot** — pytest imports the modules being tested. Same load trigger. The livereach test can call `tuning.reset()` in a fixture to get a clean slate between tests.

### Known Constraints
- **player.py's wildcard** is a local namespace pollution. Any local name in player.py that happens to collide with a tuning key (unlikely but possible) would shadow it after the wildcard is removed. Planner should grep player.py for name collisions before deleting the wildcard — a 5-second check.
- **Non-scalar `HAZARD_DRAIN_RATES`** — this is a dict, not a number. It lives in the shim with an int-key fix-up (constants.py line 26). Any migrated caller that uses `HAZARD_DRAIN_RATES` must either (a) keep importing from `constants.py` for the int-keyed form, or (b) re-do the int-key fix-up at the use site. Planner should grep the 12 files for `HAZARD_DRAIN_RATES` and decide per-case — probably option (a), because this value is read once by map.py and doesn't benefit from live-tuning.
- **Frame-for-frame parity is the acceptance bar.** Any numerical drift from the rename is a bug. The mechanical rename should produce zero drift by construction, but the unit test + playthrough catch anything unexpected.

</code_context>

<specifics>
## Specific Ideas

- **User's framing in discussion:** "I thought the adjustment overlay was for physics controls." This reframed the caching-policy question away from `self.max_hp`-style state toward the narrow concern: per-frame physics reads must reach use sites live. The panel will never scrub HP caps, so the migration only has to make GRAVITY-class values live. This pruned an entire branch of invasive `@property`-based refactors.
- **The entire point of Phase 25 is described in Phase 24's D-13/D-17** — the flat namespace was chosen specifically so Phase 25 could be a 1-to-1 mechanical rename. This phase is effectively executing on a design decision already made; the discussion above is about boundary conditions, not strategy.
- **player.py is the phase.** 50 of the ~104 call sites live in a single file. If player.py is migrated correctly and the livereach test passes on it, the other 11 files are low-risk copy-paste.

</specifics>

<deferred>
## Deferred Ideas

- **Migrating tests/ to tuning** — deliberately left on the shim (D-02b). If a future phase (maybe a tests-modernization pass) wants to cut the shim, it can migrate tests then.
- **Deleting `src/core/constants.py`** — can't happen until tests and `export_tilemap_csv.py` migrate, and there's no forcing function to do that. Deferred indefinitely.
- **Headless scripted playthrough diff** — rejected as overbuilt for this phase (D-04b), but the idea is sound for a future regression-suite phase if drift ever becomes a recurring problem.
- **Temporary debug keybind for live `set_value()`** — rejected (D-04c). Phase 28's panel replaces it properly.
- **`@property`-based live `self.max_hp`** — rejected as unnecessary given user's reframing (non-feel values don't need live reach). Could be revisited if a future design ever wants per-run HP scaling driven by the panel.
- **Per-group namespace access (`tuning.movement.GRAVITY`)** — already rejected in Phase 24 D-13. Stays rejected; no reason to revisit in Phase 25.

</deferred>

---

*Phase: 25-call-site-migration-constants-tuning*
*Context gathered: 2026-04-11*
