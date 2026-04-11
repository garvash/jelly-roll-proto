---
phase: 25
plan: 05
type: execute
wave: 3
depends_on:
  - 25-01
  - 25-02
  - 25-03
  - 25-04
files_modified:
  - .planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md
autonomous: false
requirements:
  - FND-05
must_haves:
  truths:
    - "A human has played the v1.3 regression route (Room 0 → boss room via drill dive on cracked-V, ram on cracked-H, kick, bubble shield, save, reload) and observed identical behavior to v1.3 baseline"
    - "Observations are documented in 25-VERIFICATION.md with explicit PASS or FAIL per checkpoint"
    - "If any FAIL, a gap list exists for `/gsd-plan-phase --gaps` or `/gsd-execute-phase --gaps-only` follow-up"
  artifacts:
    - path: ".planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md"
      provides: "Phase 25 manual regression playthrough record — D-04.2 acceptance artifact"
      contains: "v1.3 Regression Playthrough"
  key_links:
    - from: "human player"
      to: "main.py entry point"
      via: "python main.py"
      pattern: "python main\\.py"
---

<objective>
Run the v1.3 regression playthrough defined in 25-CONTEXT.md D-04.2 — the human-eyes acceptance artifact for Phase 25. After Plans 01, 02, 03, and 04 land, every physics value in the 12 target files is a live read against `src/core/tuning._model`. Per D-04.2, the mechanical rename should produce zero drift by construction; this playthrough is the belt-and-braces check that nothing slipped through (e.g., a missed call site, an accidental boolean coercion, a typo like `tuning.GRAVIY`).

Purpose: Closes ROADMAP.md Phase 25 success criterion #3 ("Regression playthrough produces identical behavior to v1.3 baseline"). This is the only non-automatable artifact in Phase 25 because v1.3 "feel" is a human judgement that the unit tests cannot substitute for.

Output: `.planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md` with a step-by-step log of the playthrough and a PASS/FAIL verdict per checkpoint.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/25-call-site-migration-constants-tuning/25-CONTEXT.md
@.planning/ROADMAP.md

<!--
No source file context needed — this is a human-verification task.
The playthrough runs against `python main.py` in the local checkout
with all four preceding plans merged.
-->
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Author the 25-VERIFICATION.md skeleton ahead of the playthrough</name>
  <files>.planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md</files>
  <read_first>
    - .planning/phases/25-call-site-migration-constants-tuning/25-CONTEXT.md §D-04.2 (the regression route definition)
    - .planning/ROADMAP.md §Phase 25 (the three success criteria — SC#3 is the one this plan closes)
    - `.planning/phases/25-call-site-migration-constants-tuning/25-01-SUMMARY.md`, `25-02-SUMMARY.md`, `25-03-SUMMARY.md`, `25-04-SUMMARY.md` IF THEY EXIST — use them to timestamp which commits the playthrough is testing against
  </read_first>
  <action>
Create `.planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md` with a fillable template for the human playthrough that follows in Task 2. The skeleton must include the exact checkpoint list from D-04.2 so the human running the playthrough knows what to test and in what order.

Write the file with this structure (fill in the Plans Tested section using the actual commit SHAs from `git log --oneline -20` at the time of writing):

```markdown
# Phase 25 — v1.3 Regression Playthrough Verification

**Purpose:** Acceptance artifact for Phase 25 ROADMAP success criterion #3
— "Regression playthrough produces identical behavior to v1.3 baseline."

**Specified by:** 25-CONTEXT.md D-04.2.

## Plans Tested

This playthrough verifies the state of the 12 Phase 25 target files after:

- Plan 25-01 — player.py migration (commit: <fill in SHA>)
- Plan 25-02 — tests/test_tuning_livereach.py (commit: <fill in SHA>)
- Plan 25-03 — 7 small entity migrations (commit: <fill in SHA>)
- Plan 25-04 — level/map.py + world.py + save_manager.py + sprite_utils.py (commit: <fill in SHA>)

Automated proof already green: `pytest tests/test_tuning_livereach.py -q` and `pytest -q` (full suite).

## Pre-Flight Automated Checks (human runs these before the playthrough)

- [ ] `pytest -q` exits 0
- [ ] `pytest tests/test_tuning_livereach.py -q` exits 0
- [ ] `grep -rn "from src.core.constants" src/ | grep -v "HAZARD_DRAIN_RATES" | grep -v "src/core/constants.py"` returns 0 lines (only the two deliberate HAZARD_DRAIN_RATES exceptions plus the shim file itself)
- [ ] `python -c "import src.entities.player; import src.entities.slime; import src.entities.projectile; import src.entities.boss; import src.entities.enemies; import src.entities.effects; import src.entities.save_point; import src.entities.items; import src.level.map; import src.level.world; import src.core.save_manager; import src.core.sprite_utils"` exits 0

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
```

Commit this skeleton BEFORE the human playthrough task runs. The skeleton itself is a deterministic artifact; the playthrough fills in the checkboxes in Task 2.
  </action>
  <verify>
    <automated>test -f .planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md && grep -c "Playthrough Route" .planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md</automated>
  </verify>
  <acceptance_criteria>
    - File `.planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md` exists
    - `grep -c "Playthrough Route" .planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md` returns 1
    - `grep -c "Drill Dive on cracked-V" .planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md` returns 1
    - `grep -c "Ram on cracked-H" .planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md` returns 1
    - `grep -c "Bubble Shield" .planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md` returns 1
    - `grep -c "Save point" .planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md` returns 1
    - `grep -c "Pre-Flight Automated Checks" .planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md` returns 1
    - `grep -c "Gap List" .planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md` returns 1
    - Commit SHAs for 25-01, 25-02, 25-03, 25-04 are filled in (not left as `<fill in SHA>`)
  </acceptance_criteria>
  <done>
    25-VERIFICATION.md exists with the full checkpoint list from D-04.2 and the commit SHAs for the four preceding plans. Ready for the human playthrough in Task 2.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: Human v1.3 regression playthrough — fill out 25-VERIFICATION.md</name>
  <files>.planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md</files>
  <read_first>
    - .planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md (the skeleton authored in Task 1)
    - .planning/phases/25-call-site-migration-constants-tuning/25-CONTEXT.md §D-04.2
  </read_first>
  <what-built>
    The Phase 25 call-site migration is complete across all 12 target files (Plans 01, 03, 04), the automated livereach tests are green (Plan 02), and `25-VERIFICATION.md` contains an empty checklist covering the D-04.2 route. This task is the HUMAN playthrough step.
  </what-built>
  <how-to-verify>
1. **Pre-flight automated checks.** From the repo root, run:
   - `pytest -q` — must exit 0
   - `pytest tests/test_tuning_livereach.py -q` — must exit 0
   - `grep -rn "from src.core.constants" src/ | grep -v "HAZARD_DRAIN_RATES" | grep -v "src/core/constants.py"` — must return zero lines
   - `python -c "import src.entities.player; import src.entities.slime; import src.entities.projectile; import src.entities.boss; import src.entities.enemies; import src.entities.effects; import src.entities.save_point; import src.entities.items; import src.level.map; import src.level.world; import src.core.save_manager; import src.core.sprite_utils"` — must exit 0
   - Mark the four pre-flight checkboxes in 25-VERIFICATION.md before starting the playthrough.

2. **Launch the game.** `python main.py`. A pyxel window opens to the title screen.

3. **Run the full regression route** as defined in the 25-VERIFICATION.md "Playthrough Route" section:
   - Room 0 baseline movement (walk/jump/coyote/friction)
   - Drill dive on a cracked-V block
   - Ram on a cracked-H block
   - Kick (wall jump)
   - Bubble shield activation and hazard-zone drain
   - Save point interaction
   - Quit, reload, verify save state
   - Proceed to boss room and observe BossRock behavior

4. **Mark each checkpoint.** For every item in the checklist, mark `[x] PASS` if the behavior feels identical to v1.3, or `[ ] FAIL — <note>` with a specific observation if something is off. "Feels off" is a legitimate FAIL — Phase 25 is a mechanical rename and ANY perceptible drift is a bug.

5. **Fill in the Verdict section.** If every checkpoint passes, mark **PASS** — Phase 25 closes. If any checkpoint fails, mark **FAIL** and populate the Gap List with each failure's details.

6. **Fill in the trailer fields:** tester name, run date, commit SHA at HEAD.

7. **Commit the filled-in file.** `git add .planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md && git commit -m "docs(25): record Phase 25 v1.3 regression playthrough"`. This is the acceptance artifact for Phase 25 ROADMAP SC#3.

**If FAIL:** The filled-in 25-VERIFICATION.md becomes the input to `/gsd-plan-phase --gaps 25`. The orchestrator will generate a gap-closure plan (25-06 or numbered after existing plans) addressing the specific call-site misses. Do NOT ship Phase 25 until every gap is closed and the playthrough is re-run to PASS.

**If PASS:** Phase 25 is complete. All three ROADMAP success criteria are closed:
- SC#1 (12 files read `tuning.*` at use site) — covered by Plans 01, 03, 04 automated grep checks
- SC#2 (next-frame reach of mutations) — covered by Plan 02 `tests/test_tuning_livereach.py`
- SC#3 (regression playthrough produces identical behavior) — covered by this task
  </how-to-verify>
  <resume-signal>Type "approved" after filling in and committing 25-VERIFICATION.md with a PASS verdict. Type "gap list: <details>" if any checkpoint failed so the orchestrator can route to /gsd-plan-phase --gaps.</resume-signal>
  <action>
See the `<how-to-verify>` block above. This is a checkpoint task — the "action" is a human running the v1.3 regression route while filling out the checklist in 25-VERIFICATION.md. The checklist, pre-flight commands, route steps, and verdict protocol are all specified in `<how-to-verify>`.
  </action>
  <verify>
    <automated>grep -q "PASS" .planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md && grep -q "\[x\]" .planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md</automated>
  </verify>
  <acceptance_criteria>
    - `.planning/phases/25-call-site-migration-constants-tuning/25-VERIFICATION.md` has every checklist item marked `[x] PASS` OR has a populated Gap List with `[ ] FAIL — <note>` details per failed item
    - The "Verdict" section is explicitly marked PASS or FAIL (not left blank)
    - Tester name, run date, and commit SHA trailer are filled in
    - If PASS: the file is committed to git with message `docs(25): record Phase 25 v1.3 regression playthrough`
    - If FAIL: the Gap List has at least one entry with suspected call-site attribution, and the user is informed that `/gsd-plan-phase --gaps 25` is the next step
  </acceptance_criteria>
  <done>
    The human tester has completed the D-04.2 regression playthrough, filled out 25-VERIFICATION.md with per-checkpoint observations, rendered a PASS or FAIL verdict, and committed the result. On PASS, all three Phase 25 ROADMAP success criteria are closed and the phase is ready to mark complete in STATE.md / ROADMAP.md.
  </done>
</task>

</tasks>

<verification>
This plan's automated verification is already covered by Plans 01–04:
- `pytest -q` green (Plans 01, 03, 04 acceptance)
- `pytest tests/test_tuning_livereach.py -q` green (Plan 02 acceptance)
- `grep -rn "from src.core.constants" src/` returns only HAZARD_DRAIN_RATES exceptions plus the shim (Plans 01 + 04 acceptance)

The Plan 05 contribution is a single human-verified artifact: the filled-in `25-VERIFICATION.md` with a PASS verdict.
</verification>

<success_criteria>
- `25-VERIFICATION.md` exists, every checklist item is marked PASS, verdict section marked PASS, tester + date + commit SHA filled in
- The file is committed to git
- If any FAIL occurred, a Gap List is authored and the gap-closure workflow (`/gsd-plan-phase --gaps 25`) is invoked instead of closing the phase
</success_criteria>

<output>
After a PASS verdict, create `.planning/phases/25-call-site-migration-constants-tuning/25-05-SUMMARY.md` with:
- Final verdict (PASS or FAIL)
- Duration of playthrough (approximate)
- Any non-blocking observations (e.g., "boss rock feels 1 pixel off, within v1.3 jitter range")
- Confirmation that all three Phase 25 ROADMAP success criteria are now closed
- A note that the phase can now be transitioned to "Complete" in STATE.md and ROADMAP.md
</output>
