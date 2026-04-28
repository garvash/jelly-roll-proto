---
phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
plan: 06
type: execute
wave: 4
depends_on: ["33-05"]
files_modified:
  - src/core/debug.py
  - main.py
  - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md
  - assets/presets/v2.0-default.json
autonomous: false
requirements: [FUS-06]
requirements_addressed: [FUS-06]
tags: [debug, feel-targets, preset, playtest, checkpoint]

must_haves:
  truths:
    - "Debug warp hotkeys (Ctrl+4..7) jump to drill-relevant test rooms identified by name from existing Level_0..Level_8 LDtk world"
    - "33-FEEL-TARGETS.md exists with ~10-15 falsifiable spatial/timing tests covering D-08 list (charge, drill physics, drill combat, pogo confirm)"
    - "Tuning iteration walks D-10 layered order: charge ritual → drill physics → drill combat → pogo (last)"
    - "All 33-FEEL-TARGETS.md entries marked PASS via human sign-off"
    - "Final values baked into assets/presets/v2.0-default.json (NOT _v1.3-reference.json)"
    - "v1.3-reference.json frozen (not modified by Phase 33)"
    - "Drill identity 'blindfolded observer' SFX test passes (D-08 / D-13 / D-20)"
    - "Particle palette reads as 'earth being broken' for drill cells (D-15)"
  artifacts:
    - path: "src/core/debug.py"
      provides: "Multi-target warp_target string flag set by Ctrl+4/5/6/7 hotkeys; named level-id constants for 4 drill-relevant rooms"
    - path: "main.py"
      provides: "Game.update consumer of debug.warp_target; repositions player + camera into target level (mirrors Ctrl+T pattern)"
    - path: ".planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md"
      provides: "Falsifiable feel targets (D-Cn charge / D-Dn drill physics / D-Kn drill combat / D-Pn pogo confirm / D-In identity) with PASS/FAIL columns and Sign-off section"
    - path: "assets/presets/v2.0-default.json"
      provides: "6 new tuned values baked: WINDUP_DURATION_FRAMES, ACCELERATED_REGEN_RATE, POGO_BOUNCE_VELOCITY, POGO_COOLDOWN_FRAMES, DRILL_ENEMY_COST, SLIME_DAZE_COST"
  key_links:
    - from: "33-FEEL-TARGETS.md"
      to: "assets/presets/v2.0-default.json"
      via: "PASS sign-off triggers preset bake at end-of-phase per D-11"
      pattern: "v2.0-default"
    - from: "src/core/debug.py:warp_target"
      to: "main.py:Game.update"
      via: "string-flag consume + reset to None pattern (mirrors teleport_requested)"
      pattern: "debug.warp_target"
---

<objective>
Land the iterative tuning surface for Phase 33: extend `src/core/debug.py` with multi-target debug warps; author `33-FEEL-TARGETS.md` mirroring `29-FEEL-TARGETS.md`; iterate values via the live panel through D-10 layered order (charge → drill physics → drill combat → pogo); sign off all targets; bake final values into `assets/presets/v2.0-default.json` per D-11.

Purpose: this is the human-in-the-loop feel pass. Plans 01-05 deliver the mechanism; Plan 06 delivers the *feel*. Without sign-off on 33-FEEL-TARGETS.md, FUS-06 success criterion #1 ("distinguishable windup → sustain → end curve tuned through the panel") cannot be claimed.

Output: debug warps; feel-targets doc; signed-off PASS markers; baked v2.0-default preset.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-CONTEXT.md
@.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-RESEARCH.md
@.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md
@.planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md
@src/core/debug.py
@main.py
@assets/presets/v2.0-default.json

<interfaces>
<!-- src/core/debug.py current surface (lines 1-27): god flags + Ctrl+T teleport_requested.
     Phase 33 extension: warp_target: str | None, set by Ctrl+4/5/6/7. Consumer in
     main.py:Game.update mirrors the existing teleport_requested handler at
     main.py:572-586 (single-target). -->

<!-- Level-id constants are placeholders — executor MUST verify against actual
     Level_0..Level_8 LDtk world IDs before locking. If a target room
     doesn't exist (e.g. no juice-drain hazard room in current LDtk world),
     reuse the closest analog and record the choice in the PLAN summary. -->

<!-- 33-FEEL-TARGETS.md format mirrors 29-FEEL-TARGETS.md exactly (ID/Test/
     Pass/Fail/Result columns; Sign-off section at bottom). ID prefix scheme:
     D-C# charge, D-D# drill physics, D-K# drill combat, D-P# pogo confirm,
     D-I# identity (SFX + particle). -->

<!-- assets/presets/v2.0-default.json — flat-key map of tuning values. Phase
     29 already wrote movement values; Phase 33 adds drill/pogo/charge/daze
     keys without removing or modifying any existing keys. -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Multi-target debug warps + feel-targets doc draft</name>
  <files>src/core/debug.py, main.py, .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md</files>
  <read_first>
    - src/core/debug.py (full file — note current Ctrl+T pattern at lines 17-27)
    - main.py:570-590 (existing teleport_requested consumer at lines 572-586 — reposition pattern to mirror)
    - main.py (search for `world.levels` iteration to confirm level-id matching syntax)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md (§ src/core/debug.py — full BEFORE/AFTER excerpt)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-CONTEXT.md (D-08 — feel-targets coverage list; D-09 — drill-relevant warp targets list)
    - .planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md (template — full file as exemplar)
    - assets/levels/ (or wherever LDtk world JSON lives — verify actual Level_0..Level_8 IDs by globbing or reading main.py world-load path)
  </read_first>
  <behavior>
    - debug.py adds module-level `warp_target: str | None = None` flag.
    - 4 named level-id constants:
      - WARP_LEVEL_CRACKED_V — CRACKED_V column room (drill physics test)
      - WARP_LEVEL_SOFT_BLOCK — soft-destructible floor room (drill physics + refund test)
      - WARP_LEVEL_ENEMY_CLUSTER — enemy-cluster room (drill combat + chain test)
      - WARP_LEVEL_JUICE_DRAIN — juice-drain hazard room (juice-starvation Exit-b test)
    - debug.update() handles Ctrl+4 → CRACKED_V, Ctrl+5 → SOFT_BLOCK, Ctrl+6 → ENEMY_CLUSTER, Ctrl+7 → JUICE_DRAIN.
    - main.py:Game.update consumer reads debug.warp_target, looks up the matching level by id in self.world.levels, repositions player + camera, resets warp_target to None.
    - 33-FEEL-TARGETS.md exists in phase dir as DRAFT with all entries marked Result=PENDING. Final sign-off happens after Task 2 playtest.
  </behavior>
  <action>
    Step 1 — Identify actual LDtk level IDs from the active world file. Verified during plan revision (W#4):
    - main.py:367 loads `assets/gym.ldtk` (the active world; `assets/output.ldtk` is the production world with `Level_0..Level_16` identifiers but is NOT what main.py boots).
    - `assets/gym.ldtk` has 6 level identifiers: `Gym_AccelRunway`, `Gym_CoyoteTest`, `Gym_GapTrio`, `Gym_HeightSteps`, `Gym_WallSlide`, `Gym_ZigzagShaft`.

    Run the discovery command to confirm before locking constants (the executor MUST verify against the live LDtk file at execution time — gym.ldtk may have evolved between plan and execute):

    ```bash
    grep -hoE '"identifier": *"[^"]*"' assets/gym.ldtk | grep -E "Gym_|Level_" | sort -u
    ```

    Pick the 4 closest matches for the drill-relevant test scenarios. Recommended mapping (verify against the gym world's actual level features — soft_block / cracked_V / Snail entities — before locking):
    - `WARP_LEVEL_CRACKED_V` → a Gym room with cracked_V tiles (planner discretion; if no gym room has cracked_V, fall back to `Gym_HeightSteps` and document the carve-out)
    - `WARP_LEVEL_SOFT_BLOCK` → a Gym room with soft_block tiles
    - `WARP_LEVEL_ENEMY_CLUSTER` → a Gym room with multiple Snail/Bat entities
    - `WARP_LEVEL_JUICE_DRAIN` → a Gym room with hazard tiles or just any room where juice can be drained organically

    Record the chosen IDs in the SUMMARY. If gym.ldtk lacks a feature, use the closest analog and note the substitution.

    **NOTE on world choice:** if Phase 33 playtest reveals gym.ldtk lacks the right scenarios for drill-feel testing, the planner-discretion option per CONTEXT D-09 is to either (a) extend gym.ldtk in-place with a new test room mid-phase OR (b) switch main.py:367 to load `assets/output.ldtk` (which has Level_0..Level_16) for the duration of Phase 33 tuning. Both are deferred to post-task-1 if they become necessary.

    Step 2 — Edit `src/core/debug.py` per 33-PATTERNS.md § src/core/debug.py:

    ```python
    """Runtime god-mode toggles + Phase 29/33 debug warp targets."""
    import pyxel

    god_abilities = False
    god_invincible = False
    god_infinite_juice = False
    teleport_requested = False  # Phase 29 Ctrl+T

    # Phase 33 D-09: drill-relevant warp targets. Set to a level-id string when
    # a warp key is pressed; consumed by main.py:Game.update and reset to None.
    warp_target: str | None = None

    # Level-id constants per CONTEXT D-09 coverage. Default mapping uses
    # gym.ldtk identifiers verified in Step 1 (W#4 closure). Executor MUST
    # confirm each value matches an actual `identifier` in the active LDtk
    # world file before completing this task; the acceptance criteria below
    # enforce this with a JSON parse + identifier-existence check.
    WARP_LEVEL_CRACKED_V = "Gym_ZigzagShaft"      # verify against gym.ldtk
    WARP_LEVEL_SOFT_BLOCK = "Gym_GapTrio"         # verify against gym.ldtk
    WARP_LEVEL_ENEMY_CLUSTER = "Gym_HeightSteps"  # verify against gym.ldtk
    WARP_LEVEL_JUICE_DRAIN = "Gym_AccelRunway"    # verify against gym.ldtk


    def update():
        global god_abilities, god_invincible, god_infinite_juice
        global teleport_requested, warp_target
        if pyxel.btn(pyxel.KEY_CTRL):
            if pyxel.btnp(pyxel.KEY_1):
                god_abilities = not god_abilities
            if pyxel.btnp(pyxel.KEY_2):
                god_invincible = not god_invincible
            if pyxel.btnp(pyxel.KEY_3):
                god_infinite_juice = not god_infinite_juice
            if pyxel.btnp(pyxel.KEY_T):
                teleport_requested = True
            if pyxel.btnp(pyxel.KEY_4):
                warp_target = WARP_LEVEL_CRACKED_V
            if pyxel.btnp(pyxel.KEY_5):
                warp_target = WARP_LEVEL_SOFT_BLOCK
            if pyxel.btnp(pyxel.KEY_6):
                warp_target = WARP_LEVEL_ENEMY_CLUSTER
            if pyxel.btnp(pyxel.KEY_7):
                warp_target = WARP_LEVEL_JUICE_DRAIN
    ```
    Replace placeholder level IDs with actual IDs from Step 1.

    Step 3 — Edit `main.py:Game.update`. After the existing teleport_requested block (~line 572-586), add:

    ```python
    # Phase 33 D-09: handle multi-target warp (Ctrl+4..7).
    if debug.warp_target:
        target_id = debug.warp_target
        debug.warp_target = None
        for level in self.world.levels:
            if level.id == target_id:
                self.player.x = level.x + 32
                self.player.y = level.y + 32
                self.player.dy = 0
                self.player.dx = 0
                self.world.current_level = level
                self.cam_x = level.x
                self.cam_y = level.y
                break
    ```
    Verify the exact reposition syntax matches the existing teleport_requested consumer body — copy-paste and only swap the level-lookup criterion.

    Step 4 — Create `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md` mirroring 29-FEEL-TARGETS.md format. Use the exact structure below; mark all Result cells as PENDING; mark header `> DRAFT` (Task 2's checkpoint flips to APPROVED). The doc structure has 5 sections: Charge Ritual (D-C1..C5), Drill Physics (D-D1..D4), Drill Combat (D-K1..K5), Pogo Confirm (D-P1), Identity (D-I1..I3). Total: 18 entries.

    Document content:
    - Header: `# Phase 33: Per-Ability Feel Targets (Drill-Only)` + `> DRAFT — pending sign-off after panel-iteration tuning per D-10 layered order.`
    - Section "Charge Ritual Targets" with 5 rows D-C1..D-C5 covering tap/hold disambiguation (~8f), tap/hold boundary, WINDUP cancel-window feel, WINDUP commit feel, accelerated-regen ritual time (~2× passive).
    - Section "Drill Physics Targets" with 4 rows D-D1..D-D4 covering chain on full juice (CRACKED_V column), drift, solid-landing exit (Exit a), juice-starvation Exit-b.
    - Section "Drill Combat Targets" with 5 rows D-K1..D-K5 covering single enemy kill, kill chain through 3+ enemies, juice-starvation mid-chain (Pitfall 2 option-a ordering), boss daze→drill loop (with carve-out caveat per D-17), daze low-juice gate (Pitfall 4).
    - Section "Pogo Confirm Target" with 1 row D-P1 covering FUSION-DESIGN D-04 unchanged after destructive-drill addition.
    - Section "Identity Targets (D-13 / D-15)" with 3 rows D-I1..D-I3 covering blindfolded SFX, drill earthbound palette, daze splat differentiation.
    - "Reference Values (Phase 33 starting point)" table mapping each tunable to its source group + value (use the Reference Values block from 33-PATTERNS.md or 33-CONTEXT.md as the data source — DRILL_SPEED, DRILL_DRIFT_SPEED, DRILL_ACTIVATION_COST, DRILL_BLOCK_REFUND, DRILL_CRACKED_V_COST, DRILL_ENEMY_COST=15.0, DRILL_DAMAGE=1, SLIME_SPIT_COST, SLIME_DAZE_COST=20.0, SPIT_HOLD_THRESHOLD=16, WINDUP_DURATION_FRAMES=30, ACCELERATED_REGEN_RATE=1.0, POGO_INITIAL_DY=2.0, POGO_BOUNCE_VELOCITY=-2.5, POGO_COOLDOWN_FRAMES=0, POGO_DAMAGE=1, STUN_DURATION_FRAMES=60).
    - "Results" section: empty placeholder `*(populated post-sign-off)*`.
    - "Sign-off" section: empty placeholder `*(populated post-sign-off)*`.

    Each row in the 5 target tables uses 5 columns: ID | Test | Pass Condition | Fail Condition | Result. Pass/Fail conditions must be falsifiable (specific frame counts, specific behaviors, specific palette colors) — not subjective ("feels good"). The full content is detailed enough that a different Claude instance can author the doc deterministically.

    Step 5 — LDtk world identifier validation (W#4 closure). After locking the 4 constants in Step 2, run a one-liner that parses the active LDtk world file and asserts EVERY WARP_LEVEL_* constant matches a real `identifier` in the JSON. The active world file is `assets/gym.ldtk` (verified main.py:367):

    ```bash
    python -c "
    import json, re
    from pathlib import Path
    src = Path('src/core/debug.py').read_text(encoding='utf-8')
    consts = {m.group(1): m.group(2) for m in re.finditer(r'^(WARP_LEVEL_\w+)\s*=\s*"([^"]+)"', src, re.MULTILINE)}
    assert len(consts) == 4, f'Expected 4 WARP_LEVEL_* constants, got {len(consts)}: {consts}'
    world = json.loads(Path('assets/gym.ldtk').read_text(encoding='utf-8'))
    level_ids = {lvl['identifier'] for lvl in world.get('levels', [])}
    missing = [(name, val) for name, val in consts.items() if val not in level_ids]
    assert not missing, f'WARP_LEVEL_* constants without matching gym.ldtk level identifier: {missing}; available: {sorted(level_ids)}'
    print('OK', consts)
    "
    ```

    Expected: prints `OK {'WARP_LEVEL_CRACKED_V': 'Gym_...', ...}` for all 4. If any constant is missing from gym.ldtk's levels, the executor either (a) picks a different existing identifier for that warp slot, or (b) extends gym.ldtk with a new test room (planner discretion per Step 1 NOTE).
  </action>
  <verify>
    <automated>pytest tests/ -x -q &amp;&amp; ls .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md</automated>
  </verify>
  <acceptance_criteria>
    - `grep "warp_target" src/core/debug.py` returns at least 5 matches (declaration + 4 assignments in update())
    - `grep "WARP_LEVEL_" src/core/debug.py` returns at least 4 matches
    - `grep "if pyxel.btnp(pyxel.KEY_4)" src/core/debug.py` returns 1 match
    - `grep "debug.warp_target" main.py` returns at least 2 matches (read + reset to None)
    - **W#4 closure (LDtk world identifier match):** the Step 5 one-liner exits 0 — every WARP_LEVEL_* constant in src/core/debug.py matches a real `identifier` in `assets/gym.ldtk`'s `levels` array. Failing this means a warp constant references a non-existent level (silent runtime no-op when Ctrl+4..7 is pressed).
    - `pytest tests/ -x -q` exits 0
    - `test -f .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md` exits 0
    - `grep -c "^| D-" .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md` returns at least 15 (5 + 4 + 5 + 1 + 3 = 18 row markers)
    - `grep -c "PENDING" .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md` returns at least 15 (every row Result starts as PENDING)
    - `grep "^> DRAFT" .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md` returns 1 match
    - `grep -E "## Reference Values|## Results|## Sign-off" .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md` returns 3 matches
  </acceptance_criteria>
  <done>debug.py has warp_target + 4 named level-id constants + Ctrl+4..7 hotkey assignments; main.py Game.update consumes warp_target; 33-FEEL-TARGETS.md exists as DRAFT with 18 PENDING rows + Reference Values table + empty Results/Sign-off sections; pytest GREEN.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: Tuning playtest — D-10 layered order + feel-targets sign-off</name>
  <what-built>
    Plans 01-05 + Plan 06 Task 1 deliver:
    - Tuning migration (6 keys panel-tunable)
    - Destructive drill (D-03/D-04/D-05 with drill_enemy_hit event + cost drain)
    - Daze shot (D-17 fused-tap-Z with SLIME_DAZE_COST gate + applies_daze_stun flag + Enemy.stun_timer primitive)
    - Audio module (7 distinct SFX cues via play_sfx wrapper)
    - Particle dispatch (3 new bank-2 cells: drill_block_break earthbound, drill_enemy_hit combat, daze_splat blue/green)
    - All Game.__init__ subscribers wired (Pitfall 5 closure)
    - 4 debug warps (Ctrl+4..7)
    - 33-FEEL-TARGETS.md draft with 18 PENDING rows

    The user must now play the game with F1 panel open, walk D-10 layered tuning order (charge → drill physics → drill combat → pogo), iterate values until each feel target reads PASS, then sign off.
  </what-built>
  <how-to-verify>
    **Setup:**
    1. Boot the game: `python main.py`
    2. Press F1 to open the live-tuning panel
    3. Open `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md` in a side editor

    **Tuning order (D-10 — preserve this order; later layers depend on earlier values being settled):**

    **Layer 1 — Charge Ritual (D-C1..C5):**
    - In panel "Fuse" tab, find SPIT_HOLD_THRESHOLD, WINDUP_DURATION_FRAMES, ACCELERATED_REGEN_RATE.
    - Iterate SPIT_HOLD_THRESHOLD toward ~8f; verify D-C1, D-C2 read PASS.
    - Iterate WINDUP_DURATION_FRAMES; verify D-C3, D-C4 read PASS.
    - Iterate ACCELERATED_REGEN_RATE; verify D-C5 reads PASS (~2× passive regen).
    - When all D-Cn rows read PASS, mark them in 33-FEEL-TARGETS.md (change PENDING → PASS).

    **Layer 2 — Drill Physics (D-D1..D4):**
    - Press Ctrl+4 to warp to CRACKED_V column room.
    - Verify D-D1 (chain on full juice) and D-D2 (drift).
    - Walk to a solid-floor room or use Ctrl+5 (SOFT_BLOCK); verify D-D3 (solid-landing exit).
    - Set juice low and verify D-D4 (juice-starvation Exit-b).
    - Mark D-Dn rows as PASS.

    **Layer 3 — Drill Combat (D-K1..K5):**
    - Ctrl+6 → ENEMY_CLUSTER room.
    - Iterate DRILL_ENEMY_COST in 10-20 range; verify D-K1 (single kill), D-K2 (3-enemy chain), D-K3 (juice-starvation mid-chain at option-a clamp ordering).
    - Test boss daze→drill loop: D-K4 (with carve-out caveat — boss may not visibly stun in Phase 33 per D-17 punt).
    - Iterate SLIME_DAZE_COST; verify D-K5 (low-juice gate; Pitfall 4 cancel-spam guard).
    - Mark D-Kn rows as PASS.

    **Layer 4 — Pogo (D-P1):**
    - Find airborne enemy + breakable + solid floor scenarios.
    - Iterate POGO_BOUNCE_VELOCITY; verify D-P1 reads PASS (FUSION-DESIGN D-04 unchanged).
    - Mark D-P1 as PASS.

    **Identity (D-I1..I3):**
    - D-I1: with eyes closed, fire each of the 7 cues and confirm each is distinguishable.
    - D-I2: drill into block then enemy; confirm earthbound palette + combat palette.
    - D-I3: fire daze at a block; confirm splat reads as blue/green.
    - Mark D-In rows as PASS.

    **Sign-off:**
    - Update header from `> DRAFT` to `> APPROVED YYYY-MM-DD` (today's date).
    - Populate ## Results section with: "All 18 feel targets verified PASS with `assets/presets/v2.0-default.json` (alias `v2.0-default`) loaded."
    - Populate ## Sign-off section: "Phase 33 approved by user on YYYY-MM-DD. Drill identity (windup → sustain → end + earthbound palette + 7-cue audio surface) signed off. Per-ability feel pass complete; FUS-06 ready for verification."

    **Resume:**
    - Type "approved" if all 18 targets PASS and sign-off is filled in.
    - If any target fails, describe the failing target ID + observation; the executor returns to the panel + iterates further OR carves out the issue as a follow-up if it requires structural changes (planner discretion).
  </how-to-verify>
  <resume-signal>Type "approved" once 33-FEEL-TARGETS.md is signed off (header reads APPROVED, all rows PASS, Results + Sign-off sections populated). If iteration produces unexpected blockers, describe the issue and the executor will decide whether to revise/carve-out.</resume-signal>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Bake final tuned values into v2.0-default.json</name>
  <files>assets/presets/v2.0-default.json</files>
  <read_first>
    - assets/presets/v2.0-default.json (current values — Phase 29 movement + Phase 32 fusion baseline)
    - assets/presets/_v1.3-reference.json (FROZEN — verify executor does NOT modify this file)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md (after Task 2 sign-off — reads the FINAL tuned values from the panel auto-save journal OR from current tuning.X reads after Task 2 completes)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md (§ assets/presets/slot_1.json — additions block)
  </read_first>
  <behavior>
    - assets/presets/v2.0-default.json gains 6 new keys in its values map: WINDUP_DURATION_FRAMES, ACCELERATED_REGEN_RATE, POGO_BOUNCE_VELOCITY, POGO_COOLDOWN_FRAMES, DRILL_ENEMY_COST, SLIME_DAZE_COST.
    - Optionally: SPIT_HOLD_THRESHOLD if Task 2 retuned it (D-07).
    - Each value is the TUNED final from Task 2 (NOT the schema-seed default unless Task 2 sign-off concluded the seed value passed all targets).
    - assets/presets/_v1.3-reference.json is NOT touched (verified by `git status` showing it unmodified).
    - JSON remains valid; existing keys preserved.
  </behavior>
  <action>
    Step 1 — After Task 2 sign-off, read the final tuned values. Two sources, pick whichever is more accurate:
    - Source A: panel auto-save journal at `assets/presets/slot_0.json` (Phase 28 wrote runtime auto-saves here)
    - Source B: live `tuning.X` reads after the game has been quit at the tuned state (read via Python REPL)

    Record the final values for: SPIT_HOLD_THRESHOLD, WINDUP_DURATION_FRAMES, ACCELERATED_REGEN_RATE, POGO_BOUNCE_VELOCITY, POGO_COOLDOWN_FRAMES, DRILL_ENEMY_COST, SLIME_DAZE_COST.

    Step 2 — Edit `assets/presets/v2.0-default.json` (or whichever slot file aliases as `v2.0-default` — likely `slot_1.json` per Phase 29). Add (or update if already present from earlier tuning) the 6-7 keys to the `values` dict:

    ```json
    {
      "version": "1.0",
      "schema_version": "0.3.0",
      "slot": 1,
      "alias": "v2.0-default",
      "timestamp": "2026-04-29T...",
      "values": {
        "...": "(existing Phase 29 movement values UNCHANGED)",
        "SPIT_HOLD_THRESHOLD": <tuned int>,
        "WINDUP_DURATION_FRAMES": <tuned int>,
        "ACCELERATED_REGEN_RATE": <tuned float>,
        "POGO_BOUNCE_VELOCITY": <tuned float>,
        "POGO_COOLDOWN_FRAMES": <tuned int>,
        "DRILL_ENEMY_COST": <tuned float>,
        "SLIME_DAZE_COST": <tuned float>
      }
    }
    ```

    Update the timestamp to the current date. Do NOT remove or modify any existing key. Do NOT change `slot`, `alias`, `schema_version`, `version`.

    Step 3 — Verify `_v1.3-reference.json` is NOT modified:
    ```bash
    git status assets/presets/_v1.3-reference.json
    ```
    Output must be empty (no changes).

    Step 4 — Verify the preset loads cleanly:
    ```bash
    python -c "from src.core import tuning; tuning.load_preset('v2.0-default'); print(tuning.WINDUP_DURATION_FRAMES, tuning.DRILL_ENEMY_COST, tuning.SLIME_DAZE_COST)"
    ```
    Output prints the tuned values without errors.

    Step 5 — Run the full test suite to confirm no regression:
    ```bash
    pytest tests/ -x -q
    ```
  </action>
  <verify>
    <automated>python -c "import json; d=json.load(open('assets/presets/v2.0-default.json')) if __import__('os').path.exists('assets/presets/v2.0-default.json') else json.load(open('assets/presets/slot_1.json')); v=d['values']; assert 'WINDUP_DURATION_FRAMES' in v; assert 'ACCELERATED_REGEN_RATE' in v; assert 'POGO_BOUNCE_VELOCITY' in v; assert 'POGO_COOLDOWN_FRAMES' in v; assert 'DRILL_ENEMY_COST' in v; assert 'SLIME_DAZE_COST' in v; print('OK')" &amp;&amp; pytest tests/ -x -q</automated>
  </verify>
  <acceptance_criteria>
    - `python -c "import json; json.load(open('assets/presets/v2.0-default.json'))"` exits 0 OR `python -c "import json; json.load(open('assets/presets/slot_1.json'))"` exits 0 (whichever is the v2.0-default alias)
    - The preset's `values` dict contains all 6 new keys: WINDUP_DURATION_FRAMES, ACCELERATED_REGEN_RATE, POGO_BOUNCE_VELOCITY, POGO_COOLDOWN_FRAMES, DRILL_ENEMY_COST, SLIME_DAZE_COST
    - `git diff assets/presets/_v1.3-reference.json` returns empty (frozen file untouched)
    - `pytest tests/ -x -q` exits 0
    - `grep "APPROVED" .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md` returns at least 1 match (sign-off complete)
    - `grep -c "PENDING" .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md` returns 0 (or ≤ deferred follow-up entries explicitly marked as such)
    - `grep -c "PASS" .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md` returns at least 15 (all 18 rows except any deferred)
  </acceptance_criteria>
  <done>v2.0-default.json has 6 new tuned values; _v1.3-reference.json unchanged; full pytest suite GREEN; 33-FEEL-TARGETS.md APPROVED with all PASS markers; Phase 33 ready for /gsd-verify-work.</done>
</task>

</tasks>

<verification>
- Pytest full suite: `pytest tests/ -x -q` exits 0.
- Phase 32 regression: `pytest tests/test_drill_dive_parity.py tests/test_fusion_fsm.py tests/test_pogo.py -x -v` exits 0.
- Phase 33 added tests: `pytest tests/test_destructive_drill.py tests/test_daze_shot.py tests/test_audio.py tests/test_tuning_migration.py -x -v` exits 0.
- 33-FEEL-TARGETS.md: header is APPROVED with date; Results + Sign-off sections populated; all rows PASS (excluding deferred boss-daze stun if explicitly carved out).
- Preset bake: v2.0-default contains the 6 new tuned keys; v1.3-reference unchanged.
- Audio identity smoke: blindfolded SFX test PASS in 33-FEEL-TARGETS.md.
- Particle palette: drill_block_break + drill_enemy_hit + daze_splat all visually distinct in playtest.
</verification>

<success_criteria>
- Debug warps land in 4 drill-relevant rooms via Ctrl+4..7
- 33-FEEL-TARGETS.md APPROVED with 15+ PASS markers (and any deferred entries explicitly carved out)
- v2.0-default.json contains 6 tuned values (panel-iterated)
- _v1.3-reference.json frozen
- Full pytest suite GREEN
- Phase 32 regression invariants preserved
- "Blindfolded observer" SFX test PASS
- Drill earthbound palette PASS
</success_criteria>

<output>
After completion, create `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-06-SUMMARY.md` per @$HOME/.claude/get-shit-done/templates/summary.md.
</output>
