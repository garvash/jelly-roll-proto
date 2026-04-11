---
phase: 25
plan: 03
subsystem: small-entities
tags: [refactor, tuning, constants-migration, call-sites, entities]
requires:
  - src/core/tuning.py (Phase 24 — tuning loader with PEP 562 flat access)
  - src/core/constants.py (compat shim, untouched by this plan)
  - 25-01 (Wave 1 — player migration landed; Wave 2 prerequisite satisfied)
provides:
  - src/entities/slime.py reads physics values live via tuning.X at every per-frame use site
  - src/entities/projectile.py reads physics values live via tuning.X
  - src/entities/boss.py reads physics values live via tuning.X
  - src/entities/enemies.py reads physics values live via tuning.X
  - src/entities/effects.py reads physics values live via tuning.X
  - src/entities/save_point.py reads physics values live via tuning.X
  - src/entities/items.py reads physics values live via tuning.X
affects:
  - Every per-frame physics read in the 7 "small" entity files is now hot-reloadable by the Phase 28 panel
  - FND-05 closed for the entity half of Phase 25 (player.py closed by 25-01; map.py/world.py still open for 25-04)
tech_stack:
  added: []
  patterns:
    - "from src.core import tuning + tuning.X at use site (D-03, identical pattern to 25-01)"
key_files:
  created: []
  modified:
    - src/entities/slime.py
    - src/entities/projectile.py
    - src/entities/boss.py
    - src/entities/enemies.py
    - src/entities/effects.py
    - src/entities/save_point.py
    - src/entities/items.py
decisions:
  - "Committed per-file for precise bisect if frame-for-frame drift surfaces in 25-05 playtest (plan allowed either strategy)"
  - "Dropped two dead imports in slime.py (SLIME_LERP_FACTOR, HOLD_TAP_THRESHOLD) — imported but never referenced in the module body; removing the import line is clean by construction"
  - "boss.py imported TILE_SIZE but had no use sites for it — import line removed, no prefix replacement needed"
  - "Used placeholder-token strategy for the SPRITE_SIZE vs BOSS_SPRITE_SIZE substring collision in boss.py (the only collision in the plan)"
  - "D-01 applied uniformly: __init__ RHS captures (self.dx = dx * PROJECTILE_SPEED, dy * BOSS_ROCK_SPEED, etc.) rewrite RHS to tuning.X for grep uniformity even though they are captured once"
metrics:
  duration: ~7min
  completed: 2026-04-12
  files_changed: 7
  tuning_refs_added: 73
  distinct_tuning_keys: 27
  commits: 7
requirements:
  - FND-05
---

# Phase 25 Plan 03: Small Entities Migration Summary

**One-liner:** Migrated seven entity files (slime, projectile, boss, enemies, effects, save_point, items) from `src.core.constants` explicit imports onto 73 use-site `tuning.X` reads across 27 distinct flat keys, closing the entity half of Phase 25 / FND-05.

## What Changed

Seven files edited, each committed individually for precise bisect:

| File | Keys used | tuning.* refs | Commit |
|------|-----------|---------------|--------|
| src/entities/enemies.py | 2 (TILE_SIZE, SPRITE_SIZE) | 6 | 996d68c |
| src/entities/effects.py | 3 (VIEWPORT_W, VIEWPORT_H, SPRITE_SIZE) | 5 | 3409ab8 |
| src/entities/save_point.py | 3 (SAVE_PULSE_CYCLE, SAVE_PULSE_HALF, SAVE_PROMPT_DURATION) | 3 | ac04dd1 |
| src/entities/items.py | 3 (SPRITE_SIZE, MAX_HP_CAP, MAX_JUICE_CAP) | 3 | e67cbc0 |
| src/entities/boss.py | 6 (BOSS_ROCK_SPEED, VIEWPORT_W, VIEWPORT_H, CULL_MARGIN, SPRITE_SIZE, BOSS_SPRITE_SIZE) | 8 | 45b69fe |
| src/entities/projectile.py | 9 (PROJECTILE_SPEED, TILE_SIZE, CHARGE_SHOT_SPEED, CHARGE_SHOT_SIZE, CHARGE_SHOT_DAMAGE, VIEWPORT_W, VIEWPORT_H, CULL_MARGIN, SPRITE_SIZE) | 14 | 8788c1d |
| src/entities/slime.py | 13 (SLIME_FOLLOW_DELAY, SLIME_MAX_DIST, SLIME_REFORM_DIST, JUICE_MAX, JUICE_REGEN_RATE, JUICE_MIN_SCALE, SLIME_SPIT_COST, RECALL_SPEED, RECALL_OVERLAP_DIST, SLIME_DISSIPATE_COOLDOWN, RECALL_TRAIL_COLOR, TILE_SIZE, SPRITE_SIZE) | 34 | 21947ea |
| **Total** | **27 distinct keys** (some shared across files) | **73** | 7 commits |

For each file the transformation is identical: delete the explicit `from src.core.constants import ...` line, insert `from src.core import tuning`, prefix every previously-imported name with `tuning.` at every use site.

## Per-file name counts swept (Grep-derived)

- **enemies.py** — TILE_SIZE swept at 4 sites (enemy collision snap + Bat init offset), SPRITE_SIZE at 2 sites (Snail + Bat draw). All sites per-frame or at spawn.
- **effects.py** — VIEWPORT_W/VIEWPORT_H each swept at 2 sites (Effect + Particle cull checks), SPRITE_SIZE at 1 site (Effect draw). All per-frame in `draw()`.
- **save_point.py** — SAVE_PULSE_CYCLE at 1 site (update pulse mod), SAVE_PULSE_HALF at 1 site (draw color pick), SAVE_PROMPT_DURATION at 1 site (on_save timer set). All live-reachable per-frame.
- **items.py** — SPRITE_SIZE at 1 site (draw), MAX_HP_CAP at 1 site (ENERGY pickup guard), MAX_JUICE_CAP at 1 site (MISSILE pickup guard). Pickup guards are D-01-style "arguably __init__-ish" — rewritten uniformly per D-01.
- **boss.py** — BOSS_ROCK_SPEED at 2 sites (BossRock `__init__` RHS capture for self.dx/self.dy per D-01), VIEWPORT_W/VIEWPORT_H/CULL_MARGIN at per-frame cull check sites, SPRITE_SIZE at 1 BossRock draw site, BOSS_SPRITE_SIZE at 3 Mole draw sites.
- **projectile.py** — PROJECTILE_SPEED at 2 Projectile `__init__` RHS captures (D-01), CHARGE_SHOT_SPEED at 2 ChargeProjectile `__init__` captures (D-01), CHARGE_SHOT_SIZE at 2 init sites, CHARGE_SHOT_DAMAGE at 1 init site, TILE_SIZE at 2 per-frame draw sites, VIEWPORT_W/VIEWPORT_H/CULL_MARGIN at 4 per-frame cull sites, SPRITE_SIZE at 1 ChargeProjectile draw site.
- **slime.py** — the biggest: SLIME_FOLLOW_DELAY at 2 sites (deque maxlen capture + per-frame len compare), SLIME_MAX_DIST at 3 sites (all per-frame distance checks), SLIME_REFORM_DIST at 3 sites (reform + reposition), SLIME_SPIT_COST at 2 sites (spit guard), SLIME_DISSIPATE_COOLDOWN at 1 site, JUICE_MAX at 2 sites (init captures), JUICE_REGEN_RATE at 1 per-frame regen site, JUICE_MIN_SCALE at 2 sites (scale property is per-frame via draw), RECALL_SPEED at 2 per-frame sites, RECALL_OVERLAP_DIST at 1 site, RECALL_TRAIL_COLOR at 1 per-frame draw site, TILE_SIZE at 8 collision-snap sites, SPRITE_SIZE at 6 draw sites.

## D-01 Application Notes

Several `__init__` RHS captures were encountered. Per D-01 ("RHS rewrite for grep uniformity"), these were rewritten even though the value is captured once at construction and does not become live-reachable:

- **BossRock.__init__** — `self.dx = dx * BOSS_ROCK_SPEED` → `self.dx = dx * tuning.BOSS_ROCK_SPEED`. Same for `self.dy`. The dx/dy values are captured at spawn; the rewrite is purely for grep hygiene.
- **Projectile.__init__** — `self.dx = dx * PROJECTILE_SPEED` → `self.dx = dx * tuning.PROJECTILE_SPEED`. Same for `self.dy`.
- **ChargeProjectile.__init__** — `self.dx = dx * CHARGE_SHOT_SPEED`, `self.w = CHARGE_SHOT_SIZE`, `self.damage = CHARGE_SHOT_DAMAGE`. All RHS rewrites; LHS captures left in place.
- **Slime.__init__** — `self.history = deque(maxlen=SLIME_FOLLOW_DELAY + 1)` → `tuning.SLIME_FOLLOW_DELAY + 1`. The deque's maxlen is captured at construction and is not live-adjustable by later `tuning.set_value()` calls. Rewritten per D-01 anyway.
- **Slime.__init__** — `self.max_juice = JUICE_MAX`, `self.juice = JUICE_MAX` → `tuning.JUICE_MAX`. Standard D-01 capture.
- **items.Item.collect** — `player.max_hp = min(player.max_hp + 1, MAX_HP_CAP)` and `slime.max_juice = min(..., MAX_JUICE_CAP)`. Per the plan's explicit note, these are arguably "per-frame-ish" upper-bound guards in pickup logic; rewritten uniformly per D-01.

Every other site (per-frame reads in `update()`, `draw()`, `move_and_collide()`, etc.) is a straightforward live-reachable tuning read after the rewrite — Phase 28's panel will reach them on the next frame.

## Dead Imports Pruned

Two names were imported but never used in the file body:

- **slime.py** — `SLIME_LERP_FACTOR` and `HOLD_TAP_THRESHOLD`. Both were in the multi-line import block but grep found zero use sites (excluding the import line itself). The new `from src.core import tuning` replaces the whole block, so the dead imports are naturally pruned. No replacement edit was needed for them.
- **boss.py** — `TILE_SIZE` was in the import list but had zero use sites in boss.py itself (BossRock and Mole both use `self.w`/`self.h` literals and pixel math, not tile-aligned snapping). Import line removed; no prefix edit was needed.

Total "keys used at a site" across the 7 files: **27 distinct tuning keys**. Total keys appearing in original import lines: **29** (27 + the 2 dead slime imports — boss's TILE_SIZE is also counted in the 27 because it's used in other files like projectile.py and enemies.py). The "dead import" prune is a free bonus from the rewrite.

## Substring Collision Handling

Only one collision existed in the 7 files: `SPRITE_SIZE` is a substring of `BOSS_SPRITE_SIZE` in boss.py. Naively running `replace_all("SPRITE_SIZE", "tuning.SPRITE_SIZE")` after `BOSS_SPRITE_SIZE` → `tuning.BOSS_SPRITE_SIZE` would have corrupted the latter into `tuning.BOSS_tuning.SPRITE_SIZE`.

**Strategy applied:** placeholder-token swap.
1. `BOSS_SPRITE_SIZE` → `__PH_BOSS_SPRITE_SIZE__` (isolates it from later SPRITE_SIZE replacement)
2. `SPRITE_SIZE` → `tuning.SPRITE_SIZE` (only matches the standalone BossRock draw site)
3. `__PH_BOSS_SPRITE_SIZE__` → `tuning.BOSS_SPRITE_SIZE`

On the first attempt the intermediate placeholder was itself corrupted (the `SPRITE_SIZE` replace_all also matched inside `__PH_BOSS_SPRITE_SIZE__`, turning it into `__PH_BOSS_tuning.SPRITE_SIZE__`). This was detected via post-edit Read + grep verification, and a second targeted replace_all fixed it: `__PH_BOSS_tuning.SPRITE_SIZE__` → `tuning.BOSS_SPRITE_SIZE`. Final state verified clean: zero bare `SPRITE_SIZE` (pre-dot), three `tuning.BOSS_SPRITE_SIZE`, one `tuning.SPRITE_SIZE` (BossRock draw), zero placeholder residue.

No other collision existed in the 7 files. In particular: `SLIME_MAX_DIST` / `SLIME_REFORM_DIST` / `SLIME_SPIT_COST` / `SLIME_FOLLOW_DELAY` / `SLIME_DISSIPATE_COOLDOWN` / `SLIME_LERP_FACTOR` share the `SLIME_` prefix but none is a substring of another. Same for `JUICE_MAX` / `JUICE_REGEN_RATE` / `JUICE_MIN_SCALE` vs `MAX_JUICE_CAP`: none is a substring of another.

## Verification

**All per-file import smoke tests pass:**
```
python -c "import src.entities.slime; import src.entities.projectile; import src.entities.boss; import src.entities.enemies; import src.entities.effects; import src.entities.save_point; import src.entities.items; import src.entities.player"
All 7 + player import OK
```

**Acceptance criteria (all 28 pass):**
- For each of 7 files: `grep -c "from src.core.constants"` returns 0 ✓
- For each of 7 files: `grep -c "from src.core import tuning"` returns 1 ✓
- `tuning.SLIME_FOLLOW_DELAY` in slime.py: 2 occurrences ✓
- `tuning.PROJECTILE_SPEED` in projectile.py: 2 occurrences ✓
- `tuning.BOSS_ROCK_SPEED` in boss.py: 2 occurrences ✓
- `tuning.CHARGE_SHOT_SPEED` in projectile.py: 2 occurrences ✓
- `python -c "import src.entities.<name>"` exits 0 for all 7 files ✓
- `python -m pytest -q` — **363 passed, 3 skipped** (identical to Plan 01 baseline) ✓
- `python -m pytest tests/test_tuning.py -q` — **11 passed** ✓
- `tests/test_tuning_livereach.py` — not yet present in tree (Plan 02 is the Wave 2 parallel agent responsible for creating it). Plan 02 is running in parallel via separate worktree. Not a regression.

**Scope check (`grep -rn "from src.core.constants" src/entities/`):**
```
src/entities/player.py:3:from src.core.constants import HAZARD_DRAIN_RATES
```
Only the one deliberate player.py `HAZARD_DRAIN_RATES` exception remains, exactly as planned (D-02a). No other entity file hits the shim.

## Deviations from Plan

**Rule 2 (micro) — Dead imports cleaned up.** Two names in slime.py (`SLIME_LERP_FACTOR`, `HOLD_TAP_THRESHOLD`) and one name in boss.py (`TILE_SIZE`) were imported from constants but never used in the file body. The plan said "prefix every previously-imported name," which is literally impossible for names with zero use sites; the cleanest execution is to drop them when the old import line is deleted (the new `from src.core import tuning` covers any future use). Noted here for traceability — not a scope change, just the correct handling of a minor specification gap.

**Other than that, the plan executed exactly as written**, following the 7-file-in-size-ascending-order recipe and committing each file individually.

## Auxiliary files in first commit

The first commit (`996d68c` for enemies.py) also contains two binary assets (`assets/sprites/tiles.png`, `assets/tileset.png`) that were staged as part of the worktree-realignment `git reset --soft` + `git checkout HEAD --` at the start of execution (known parallel-worktree Windows quirk where the branch was created from stale `main` and needed to be rebased onto the target base `9928995`). These assets are part of the phase-25 baseline (they landed between the branch point and the target base) and were swept up by `git add src/entities/enemies.py` only because they were already in the index from the reset. They are not part of the refactor itself. Subsequent commits are clean (only the single migrated .py file each).

## Notes

- **Duration:** ~7 minutes of wall-clock execution, dominated by editing and the single boss.py substring-collision recovery.
- **Frame-for-frame parity** is guaranteed by construction: every edit is a literal rename from `NAME` to `tuning.NAME`. No value changes, no control-flow changes, no new temp variables.
- **Plan 25-01 pattern reuse:** this plan copy-pastes the migration recipe from Plan 01's player.py sweep, scaled down to 7 smaller files. The `__init__` RHS rewrite convention, the `HAZARD_DRAIN_RATES` shim exception (N/A in this plan — none of the 7 files use it), and the per-file acceptance criteria style are all lifted unchanged from 25-01.
- **Wave 2 parallelism:** this plan ran concurrently with 25-02 (livereach test creation). Both only touch disjoint files (test file vs entity files), so there is no merge conflict surface. Plan 25-04 (map.py / world.py / core subset) will run in a later wave.

## Deferred Issues

None.

## Self-Check: PASSED

- FOUND: .planning/phases/25-call-site-migration-constants-tuning/25-03-SUMMARY.md (this file)
- FOUND: src/entities/enemies.py (modified in commit 996d68c)
- FOUND: src/entities/effects.py (modified in commit 3409ab8)
- FOUND: src/entities/save_point.py (modified in commit ac04dd1)
- FOUND: src/entities/items.py (modified in commit e67cbc0)
- FOUND: src/entities/boss.py (modified in commit 45b69fe)
- FOUND: src/entities/projectile.py (modified in commit 8788c1d)
- FOUND: src/entities/slime.py (modified in commit 21947ea)
- FOUND commit: 996d68c refactor(25-03): migrate enemies.py
- FOUND commit: 3409ab8 refactor(25-03): migrate effects.py
- FOUND commit: ac04dd1 refactor(25-03): migrate save_point.py
- FOUND commit: e67cbc0 refactor(25-03): migrate items.py
- FOUND commit: 45b69fe refactor(25-03): migrate boss.py
- FOUND commit: 8788c1d refactor(25-03): migrate projectile.py
- FOUND commit: 21947ea refactor(25-03): migrate slime.py
