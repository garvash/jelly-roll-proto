---
phase: 25-call-site-migration-constants-tuning
verified: 2026-04-12T00:00:00Z
status: passed
score: 3/3 must-haves verified
overrides_applied: 0
requirements_verified:
  - FND-05
must_haves:
  truths:
    - "player.py, slime.py, projectile.py, and enemies/*.py read tuning.* values each frame instead of caching them at import time"
    - "Editing a movement value in physics-schema.json changes player behavior on the very next frame (verified against Phase 24 loader)"
    - "Regression playthrough (Room 0 -> boss room, drill dive, ram, kick, bubble shield) produces identical behavior to v1.3 baseline"
  artifacts:
    - path: "src/entities/player.py"
      provides: "Player entity reading tuning.* at every per-frame physics use site"
    - path: "src/entities/slime.py"
      provides: "Slime entity reading tuning.* at every per-frame use site"
    - path: "src/entities/projectile.py"
      provides: "Projectile entity reading tuning.* at every per-frame use site"
    - path: "src/entities/boss.py"
      provides: "BossRock entity reading tuning.* at every per-frame use site"
    - path: "src/entities/enemies.py"
      provides: "Enemy entity reading tuning.* at every per-frame use site"
    - path: "src/entities/effects.py"
      provides: "Effect/Particle entities reading tuning.* at every per-frame use site"
    - path: "src/entities/save_point.py"
      provides: "SavePoint entity reading tuning.* at every per-frame use site"
    - path: "src/entities/items.py"
      provides: "Item entity reading tuning.* at every per-frame use site"
    - path: "src/level/map.py"
      provides: "LevelMap reading tile/viewport tuning live; HAZARD_DRAIN_RATES preserved on shim"
    - path: "src/level/world.py"
      provides: "World / LevelBounds reading viewport tuning via tuning module"
    - path: "src/core/save_manager.py"
      provides: "SaveManager reading SAVE_FILE via tuning"
    - path: "src/core/sprite_utils.py"
      provides: "draw_sprite helper reading SPRITE_SIZE via tuning"
    - path: "tests/test_tuning_livereach.py"
      provides: "FND-05 acceptance artifact proving set_value reaches gameplay on next frame"
  key_links:
    - from: "src/entities/player.py"
      to: "src/core/tuning.py"
      via: "tuning.<NAME> module attribute reads at every per-frame use site"
    - from: "src/entities/player.py"
      to: "src/core/constants.py"
      via: "explicit HAZARD_DRAIN_RATES import (int-keyed dict, deliberate D-01 carve-out)"
    - from: "src/level/map.py"
      to: "src/core/constants.py"
      via: "explicit HAZARD_DRAIN_RATES import (int-keyed dict, deliberate D-01 carve-out)"
    - from: "tests/test_tuning_livereach.py"
      to: "src.entities.player.Player + src.core.tuning.set_value"
      via: "Player instantiation + player.update() + tuning.set_value round-trip"
human_verification_incorporated:
  source: "original D-04.2 playthrough artifact (now embedded in this verifier report)"
  tester: "garvash (human approval via orchestrator)"
  run_date: "2026-04-12"
  commit_tested: "43e490e (skeleton at 4a02d47 — merged HEAD of Plans 25-01..25-04)"
  verdict: "PASS"
  checkpoints_passed: 30
  checkpoints_failed: 0
---

# Phase 25: Call-Site Migration (constants -> tuning) Verification Report

**Phase Goal:** Move entity files from import-site constants to use-site `tuning.X` reads so hot-reload actually reaches gameplay values. Mechanical refactor with zero behavior change.
**Verified:** 2026-04-12
**Status:** passed
**Re-verification:** No — initial verification (replaces prior D-04.2 playthrough artifact with structured frontmatter report; playthrough evidence preserved below)

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `player.py`, `slime.py`, `projectile.py`, `enemies.py` read `tuning.*` values each frame instead of caching them at import time | PASS | Zero `from src.core.constants import *` remaining; all four files import `from src.core import tuning` (src/entities/player.py:2, slime.py:4, projectile.py:2, enemies.py:2). Per-frame `tuning.*` reference counts: player=75, slime=34, projectile=14, enemies=6. Bare-name spot-check at player.py:467-472, 491, 637-640 confirms `tuning.WALK_FRICTION`, `tuning.MAX_WALK_SPEED`, `tuning.JUMP_FORCE`, `tuning.GRAVITY` at hot-path use sites. 25-01-SUMMARY reports 90 `tuning.X` refs / 49 distinct keys migrated in player.py. |
| 2 | Editing a movement value in `physics-schema.json` changes player behavior on the very next frame | PASS | `tests/test_tuning_livereach.py` contains 4 hermetic tests (`test_livereach_gravity`, `test_livereach_jump_force`, `test_livereach_max_walk_speed`, `test_livereach_walk_friction`) driving `tuning.set_value(KEY, 10 * baseline)` between two `player.update()` calls and asserting behavior change. Re-ran: **4 passed in 0.08s**. Sanity check in 25-02-SUMMARY: NOPing `set_value` calls makes all 4 tests fail — proves tests genuinely depend on `set_value` reaching gameplay. |
| 3 | Regression playthrough (Room 0 -> boss room, drill dive, ram, kick, bubble shield) produces identical behavior to v1.3 baseline | PASS | Human tester `garvash` completed all 8 sections / 30 checkpoints of the D-04.2 regression route on 2026-04-12 at commit `43e490e` (skeleton at `4a02d47`, merged HEAD of Plans 25-01..25-04). Every checkpoint marked `[x] PASS`, explicit **PASS** verdict, Gap List intentionally empty. See **Human Playthrough Evidence** section below for full checkpoint log. |

**Score:** 3/3 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/entities/player.py` | reads `tuning.*` at per-frame use sites, HAZARD_DRAIN_RATES shim exception preserved | VERIFIED | `from src.core import tuning` at line 2; `from src.core.constants import HAZARD_DRAIN_RATES` at line 3; 75 `tuning.*` refs; `tuning.WALK_FRICTION/MAX_WALK_SPEED/JUMP_FORCE/GRAVITY` all confirmed at hot-path lines 467-640. `INTGRID_CRACKED_H/V = 11/12` local literals preserved at lines 10-11. |
| `src/entities/slime.py` | reads `tuning.*` at per-frame use sites | VERIFIED | `from src.core import tuning` at line 4; 34 `tuning.*` refs; 10 `tuning.SLIME_*` refs confirmed. |
| `src/entities/projectile.py` | reads `tuning.*` at per-frame use sites | VERIFIED | `from src.core import tuning` at line 2; 14 `tuning.*` refs; 7 `tuning.(PROJECTILE_SPEED|CHARGE_SHOT*)` refs confirmed. |
| `src/entities/boss.py` | reads `tuning.*` at per-frame use sites | VERIFIED | `from src.core import tuning` at line 4; 8 `tuning.*` refs. |
| `src/entities/enemies.py` | reads `tuning.*` at per-frame use sites | VERIFIED | `from src.core import tuning` at line 2; 6 `tuning.*` refs. |
| `src/entities/effects.py` | reads `tuning.*` at per-frame use sites | VERIFIED | `from src.core import tuning` at line 3. |
| `src/entities/save_point.py` | reads `tuning.*` at per-frame use sites | VERIFIED | `from src.core import tuning` at line 3. |
| `src/entities/items.py` | reads `tuning.*` at per-frame use sites | VERIFIED | `from src.core import tuning` at line 2. |
| `src/level/map.py` | reads `tuning.TILE_SIZE/TILE_EMPTY/VIEWPORT_*`; HAZARD_DRAIN_RATES shim exception preserved | VERIFIED | `from src.core import tuning` at line 2; explicit `from src.core.constants import HAZARD_DRAIN_RATES` at line 7 with documenting comment. |
| `src/level/world.py` | reads viewport tuning via tuning module | VERIFIED | `from src.core import tuning` at line 2. WorldManager.SCREEN_W/SCREEN_H at lines 28-29 are class-body captures (module-load-time) with rewritten RHS per D-01 rule-of-thumb — see Code Review Findings below. |
| `src/core/save_manager.py` | reads `tuning.SAVE_FILE` | VERIFIED | `from src.core import tuning` at line 5. |
| `src/core/sprite_utils.py` | reads `tuning.SPRITE_SIZE` via draw_sprite default args | VERIFIED | `from src.core import tuning` at line 4; explicitly documented D-01 default-argument exception. |
| `tests/test_tuning_livereach.py` | 4+ hermetic livereach tests (GRAVITY/JUMP_FORCE/MAX_WALK_SPEED/WALK_FRICTION) | VERIFIED | 4 test functions at lines 105/144/208/262 matching the plan's required names; autouse `tuning.reset()` fixture; 4 passed on re-run. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| src/entities/player.py | src/core/tuning.py | `tuning.<NAME>` reads inside update/move/apply_gravity/jump/drill_dive/etc. | WIRED | 75 `tuning.*` refs in player.py; spot-checks at lines 467 (WALK_FRICTION), 472 (MAX_WALK_SPEED), 491 (JUMP_FORCE), 637/640 (GRAVITY) land in per-frame code paths. |
| src/entities/player.py | src/core/constants.py | explicit `HAZARD_DRAIN_RATES` import (int-keyed dict, D-01 carve-out) | WIRED | Line 3 `from src.core.constants import HAZARD_DRAIN_RATES`; deliberate exception per D-01 / 25-CONTEXT "Known Constraints". |
| src/level/map.py | src/core/constants.py | explicit `HAZARD_DRAIN_RATES` import | WIRED | Line 7 `from src.core.constants import HAZARD_DRAIN_RATES`; line 338 indexed lookup `HAZARD_DRAIN_RATES[tile]` for IntGrid IDs 6/7/8. |
| src/level/map.py | src/core/tuning.py | `tuning.TILE_SIZE / TILE_EMPTY / VIEWPORT_*` reads | WIRED | Line 2 import; per-frame `tuning.TILE_SIZE` calls confirmed in draw/collision methods per 25-04-SUMMARY (30 refs). |
| tests/test_tuning_livereach.py | src.entities.player.Player + src.core.tuning.set_value | Player instantiation + `player.update()` + `tuning.set_value` round-trip | WIRED | Test functions construct `Player(...)`, mock `input_manager`, call `set_value(KEY, 10 * baseline)` between two `update()` calls, assert direction-of-change. Sanity-checked by NOP-ing set_value calls (all 4 fail). |

### Data-Flow Trace (Level 4)

Phase 25 is a mechanical refactor, not a data-rendering change. The relevant data flow is "schema -> tuning module -> entity per-frame read -> gameplay effect." Verified end-to-end by `tests/test_tuning_livereach.py`:

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| player.apply_gravity | dy after one frame | tuning.GRAVITY via PEP 562 `__getattr__` -> `_model['movement']['GRAVITY']` | yes (`tuning.set_value(..., 10*baseline)` -> `dy` grows ~10x) | FLOWING |
| player.handle_input (jump) | dy immediately after jump | tuning.JUMP_FORCE | yes (delta asserted equal to `9 * baseline_jump`) | FLOWING |
| player.handle_input (walk clamp) | dx after 16 walk frames | tuning.MAX_WALK_SPEED | yes (mutated dx > baseline cap) | FLOWING |
| player.handle_input (friction) | dx decay per frame | tuning.WALK_FRICTION | yes (10x friction clamps to zero) | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 12 target modules importable | `python -c "import src.entities.player; import src.entities.slime; ...; import src.core.sprite_utils"` | `all 12 import OK` | PASS |
| Livereach tests pass | `pytest tests/test_tuning_livereach.py -q` | `4 passed in 0.08s` | PASS |
| No wildcard constants imports in migrated files | `grep -r "from src\.core\.constants import \*" src/entities/ src/level/ src/core/` | 0 matches | PASS |
| Only deliberate shim carve-outs remain | `grep -rn "from src.core.constants" src/` | 3 hits: `src/core/constants.py:7` (docstring example), `src/entities/player.py:3` (HAZARD carve-out), `src/level/map.py:7` (HAZARD carve-out) | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FND-05 | 25-01, 25-02, 25-03, 25-04, 25-05 | "Call-site migration sweep — `src/entities/*.py` read `tuning.X` at use site (not import site) so hot-reload actually reaches entity values." | SATISFIED | All 12 target files now import `from src.core import tuning` and reference `tuning.X` at use sites. Automated livereach test suite (Plan 25-02) proves `set_value` reaches gameplay on next frame. Human D-04.2 regression playthrough (Plan 25-05) confirms zero drift from v1.3 baseline across all 30 checkpoints. |

No orphaned or unmapped requirements for Phase 25.

### Anti-Patterns Found

Sourced from 25-REVIEW.md (0 Critical / 3 Warning / 6 Info).

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| src/level/world.py | 28-29 | `WorldManager.SCREEN_W = tuning.VIEWPORT_W` / `SCREEN_H = tuning.VIEWPORT_H` — class-body module-load-time capture | Warning | Does NOT affect SC#1 (which names player/slime/projectile/enemies only). Explicitly matches D-01 rule-of-thumb: module-load-time captures rewrite RHS to `tuning.X` for grep uniformity, semantics remain "captured at import time". Viewport values are not slated for live-tuning by Phase 28. Accepted as intentional D-01 carve-out. |
| src/level/map.py | 12 | `TILES_PER_ROW = 256 // tuning.TILE_SIZE` — module-load-time derivation | Warning | Same D-01 rationale. `TILE_SIZE` is a grid invariant; pyxel image-bank layout is baked at load. Plan 25-04 action explicitly documents this tradeoff. |
| src/level/map.py | 16 | `_EMPTY_8PX = (tuning.TILE_EMPTY[0] * 2, tuning.TILE_EMPTY[1] * 2)` — module-load-time derivation | Warning | Same D-01 rationale. |
| src/level/map.py | 183 | Bare `except:` swallows KeyboardInterrupt/SystemExit | Info | Pre-existing, not a Phase 25 regression. Out of scope. |
| src/core/sprite_utils.py | 8-9 | `def draw_sprite(..., visual_w=tuning.SPRITE_SIZE, ...)` default-argument capture | Info | Documented D-01 exception. All 12 current callers pass `visual_w`/`visual_h` explicitly, so default is never hit at runtime. |
| tests/test_tuning_livereach.py | (scope) | Covers 4 of ~75 migrated keys | Info | Documented sampling decision per D-04.1. |
| multiple | various | File-open without `encoding=` (IN-03), SaveManager lacks JSON error handling (IN-04), magic numbers in player/slime/projectile/effects (IN-06) | Info | Pre-existing, not Phase 25 regressions. Belong on backlog. |

**Evaluation against phase goal:** None of the three Warning-level module-load captures violates Success Criterion #1, which names `player.py`, `slime.py`, `projectile.py`, and `enemies/*.py` specifically — NOT `map.py` or `world.py`. They also match D-01's explicit rule-of-thumb for non-per-frame captures. They are accepted as intentional design decisions with documented traceability in Plan 25-04 and 25-CONTEXT.md. If Phase 28 ever decides to live-tune viewport or tile dimensions, these captures would need conversion to properties/helper functions — recorded as future work, not a Phase 25 gap.

### Pre-existing Regression Not Attributable to Phase 25

The full `pytest -q` run reports **366 passed, 3 skipped, 1 failed**. The single failing test is `tests/test_ldtk_migration.py::test_tileset_relpath_cavern`. Investigation confirmed:
- The failure is caused by pre-existing uncommitted changes to `assets/output.ldtk` that existed in the working tree before Phase 25 began.
- Zero Phase 25 commits touch `assets/output.ldtk`.
- Reverting `assets/output.ldtk` to HEAD makes the test pass.

This is **not a Phase 25 regression** and does not block phase closure. The livereach suite (`pytest tests/test_tuning_livereach.py -q`) and the Phase 24 regression canary (`pytest tests/test_tuning.py -q`) are both green.

### Human Verification Required

None. Plan 25-05's D-04.2 human playthrough was completed and is preserved below.

### Human Playthrough Evidence (D-04.2, preserved from prior VERIFICATION.md)

**Tester:** garvash (human approval via orchestrator)
**Run date:** 2026-04-12
**Commit tested:** `43e490e` (skeleton authored at `4a02d47`, merged HEAD of Plans 25-01..25-04)

**Plans Tested:**
- Plan 25-01 — player.py migration — commit `8671cc8`
- Plan 25-02 — tests/test_tuning_livereach.py — commit `174c9a9`
- Plan 25-03 — 7 small entity migrations — commit range `996d68c` -> `21947ea`
- Plan 25-04 — map/world/save_manager/sprite_utils — commits `ebd673c`, `161cf66`

**Pre-flight automated checks (all green at 4a02d47):**
- `pytest -q` -> 367 passed, 3 skipped
- `pytest tests/test_tuning_livereach.py -q` -> 4 passed
- `grep -rn "from src.core.constants" src/ | grep -v HAZARD_DRAIN_RATES | grep -v constants.py` -> 0 source hits
- 12-file import smoke -> OK

**Checkpoint matrix (30/30 PASS):**

1. **Room 0 baseline movement** (5/5 PASS): walk speed identical to v1.3, jump height clears same gap, coyote+jump-buffer feel right, falling gravity asymmetry preserved, friction deceleration correct.
2. **Drill Dive on cracked-V block — ABL-02** (4/4 PASS): DOWN+SPACE triggers drill dive, dive speed/juice cost identical, cracked-V breaks as expected, impact recoil + hitstop feel right.
3. **Ram on cracked-H block — ABL-01** (4/4 PASS): ram activation works, ram speed identical, cracked-H breaks on contact, embed-in-wall behavior unchanged.
4. **Kick (wall jump)** (2/2 PASS): wall slide friction feels right, wall jump X/Y impulse identical.
5. **Bubble Shield — ABL-05** (3/3 PASS): auto-activation on hazard entry, drain rate identical (slow/medium/fast zones — HAZARD_DRAIN_RATES exception lookup proven at runtime), T1/T2 shield behaviors unchanged.
6. **Save point** (2/2 PASS): UP triggers save, save.json well-formed.
7. **Reload from save** (4/4 PASS): quit/restart, load save, respawn at save point, earlier progress matches save.
8. **Reach boss room** (2/2 PASS): full route navigable without "feel off" moment, BossRock projectiles fire at BOSS_ROCK_SPEED identical to v1.3.

**Verdict (preserved verbatim from D-04.2 artifact):**
> All 30 playthrough checkpoints marked PASS by human tester. Zero perceptible drift from v1.3 baseline across walk/jump/coyote/friction, drill dive + cracked-V, ram + cracked-H, kick/wall-jump, bubble shield + HAZARD_DRAIN_RATES zones, save-to-disk, reload-from-save, and boss room BossRock behavior. The mechanical `from src.core.constants import *` -> `tuning.*` rename across all 12 target files (Plans 25-01, 25-03, 25-04) plus the livereach test (Plan 25-02) produced exactly the zero-drift outcome predicted by D-04.2. Phase 25 ROADMAP success criterion #3 is closed.

**Gap List:** (intentionally empty — verdict PASS).

### Gaps Summary

None. All three observable truths are verified by a combination of: (a) mechanical grep + per-file import/reference counts for SC#1, (b) hermetic automated livereach tests for SC#2, and (c) human-judged D-04.2 regression playthrough for SC#3. The 3 Warning-level code-review findings are intentional D-01 carve-outs that do not intersect the Phase 25 Success Criteria and are traceable to plan decisions. The 6 Info-level findings are either documented exceptions or pre-existing issues out of scope. The single unrelated `test_ldtk_migration.py` failure is attributable to pre-Phase-25 uncommitted changes in `assets/output.ldtk` and is not a regression.

Phase 25 has achieved its goal: all 12 migration-target files now read `tuning.X` at per-frame use sites, `set_value` mutations demonstrably reach gameplay on the very next frame, and human-eyes regression playthrough confirms zero drift from the v1.3 baseline. Ready to transition to Complete in STATE.md / ROADMAP.md.

---

_Verified: 2026-04-12_
_Verifier: Claude (gsd-verifier)_
