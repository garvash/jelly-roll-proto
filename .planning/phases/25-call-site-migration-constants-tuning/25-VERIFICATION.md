# Phase 25 — v1.3 Regression Playthrough Verification

**Purpose:** Acceptance artifact for Phase 25 ROADMAP success criterion #3
— "Regression playthrough produces identical behavior to v1.3 baseline."

**Specified by:** 25-CONTEXT.md D-04.2.

## Plans Tested

This playthrough verifies the state of the 12 Phase 25 target files after:

- Plan 25-01 — player.py migration (commit: `8671cc8` refactor(25-01): migrate player.py from constants wildcard to tuning reads)
- Plan 25-02 — tests/test_tuning_livereach.py (commit: `174c9a9` test(25-02): add livereach tests proving tuning mutations reach gameplay)
- Plan 25-03 — 7 small entity migrations (commit range: `996d68c` → `21947ea`; per-file commits enemies → effects → save_point → items → boss → projectile → slime)
- Plan 25-04 — level/map.py + world.py + save_manager.py + sprite_utils.py (commits: `ebd673c` refactor(25-04): migrate world.py/save_manager.py/sprite_utils.py + `161cf66` refactor(25-04): migrate map.py, keep HAZARD_DRAIN_RATES on shim)

**Merge commits that brought all four plans to `main`:**
- `5756545` chore: merge executor worktree (25-02 livereach-test)
- `3a614bf` chore: merge executor worktree (25-04 level-and-core)
- `4a02d47` chore: merge executor worktree (25-03 small-entities) — Phase 25 code-change HEAD at playthrough time

Automated proof already green at `4a02d47`:
- `pytest tests/test_tuning_livereach.py -q` → **4 passed in 0.19s**
- `pytest -q` (full suite) → **367 passed, 3 skipped in 38.48s**

## Pre-Flight Automated Checks (human runs these before the playthrough)

- [x] `pytest -q` exits 0 — **367 passed, 3 skipped** (pre-ran by Plan 25-05 executor at `4a02d47`)
- [x] `pytest tests/test_tuning_livereach.py -q` exits 0 — **4 passed**
- [x] `grep -rn "from src.core.constants" src/ | grep -v "HAZARD_DRAIN_RATES" | grep -v "src/core/constants.py"` returns 0 lines — **only a pycache binary match, zero source-file hits** (the two deliberate `HAZARD_DRAIN_RATES` exceptions in `player.py` + `map.py` plus the shim file itself are the entire surface)
- [x] `python -c "import src.entities.player; import src.entities.slime; import src.entities.projectile; import src.entities.boss; import src.entities.enemies; import src.entities.effects; import src.entities.save_point; import src.entities.items; import src.level.map; import src.level.world; import src.core.save_manager; import src.core.sprite_utils"` exits 0 — **"all 12 import OK"**

## Playthrough Route (D-04.2)

**Setup:** `python main.py` — fresh run from title screen, no prior save.

Mark each checkpoint as `[x] PASS` / `[ ] FAIL — <note>` after observation.

### 1. Room 0 baseline movement
- [ ] Walk speed feels identical to v1.3 (not obviously slower/faster)
- [ ] Jump height clears the same gap as v1.3
- [ ] Coyote time + jump buffer feel right (run off a ledge, jump after — should land)
- [ ] Falling gravity asymmetry feels right (jump feels floaty-up, heavy-down as in v1.3)
- [ ] Friction decelerates correctly when walk input released

### 2. Drill Dive on cracked-V block (ABL-02)
- [ ] DOWN + SPACE while fused triggers drill dive
- [ ] Dive speed and juice cost feel identical
- [ ] Cracked-V block breaks, juice consumed as expected
- [ ] Impact recoil and hitstop feel right

### 3. Ram on cracked-H block (ABL-01)
- [ ] Ram activation works
- [ ] Ram speed feels identical
- [ ] Cracked-H block breaks on contact
- [ ] Ram embed-in-wall behavior unchanged

### 4. Kick (walk jump mechanic)
- [ ] Wall slide friction feels right
- [ ] Wall jump X/Y impulse feels identical (same arc, same reach)

### 5. Bubble Shield (ABL-05)
- [ ] Auto-activates on hazard zone entry
- [ ] Drain rate feels identical to v1.3 (slow/medium/fast zones behave correctly — this is the HAZARD_DRAIN_RATES exception lookup proof)
- [ ] T1 and T2 shield behaviors unchanged

### 6. Save point
- [ ] Stand near save point, press UP, save is written to save.json
- [ ] `cat save.json` shows well-formed content

### 7. Reload from save
- [ ] Quit game (`Ctrl+C` or window close)
- [ ] Re-run `python main.py`
- [ ] Load saved game → player respawns at save point
- [ ] All earlier progress (abilities unlocked, broken blocks) matches save

### 8. Reach boss room
- [ ] Full route from Room 0 to boss room navigable without any "feel off" moment
- [ ] Boss room loads, BossRock projectiles fire at BOSS_ROCK_SPEED (should feel identical)

## Verdict

- [ ] **PASS** — all checkpoints green, frame-for-frame parity confirmed, Phase 25 closes on this commit
- [ ] **FAIL** — one or more checkpoints red; see Gap List below

## Gap List (fill only if FAIL)

For each failed checkpoint, record:
- What checkpoint failed
- What was observed vs. what was expected
- Suspected call site (which of the 12 files might have a missed prefix or typo)
- Minimum repro steps

If FAIL, this file becomes the input to `/gsd-plan-phase --gaps` to generate a follow-up gap-closure plan.

---

**Tester:** <fill in: "user" or "claude-autonomous-with-human-approval">
**Run date:** <fill in date of playthrough>
**Commit tested:** <fill in SHA of HEAD at test time>
