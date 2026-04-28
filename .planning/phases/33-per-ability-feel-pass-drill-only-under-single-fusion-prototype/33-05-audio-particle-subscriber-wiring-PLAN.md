---
phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
plan: 05
type: execute
wave: 3
depends_on: ["33-03", "33-04"]
files_modified:
  - src/core/audio.py
  - main.py
  - assets/sprites/particles.png
autonomous: true
requirements: [FUS-06]
requirements_addressed: [FUS-06]
tags: [audio, particles, event-bus, identity, pyxel]

must_haves:
  truths:
    - "src/core/audio.py module exists; init_sounds() defines 7 pyxel.sounds slots; play_sfx(name) routes to pyxel.play"
    - "Game.__init__ wires 7 audio subscribers (fuse_start, drill_start, drill_block_break, drill_enemy_hit, drill_impact, daze_fire, pogo_bounce) AND 1 particle subscriber (drill_enemy_hit -> spawn_particle_burst)"
    - "spawn_particle_burst(type=...) dispatch table routes 4 types to distinct (u, v) bank-2 cells"
    - "particles.png expanded with new y=32 row containing 3 new cells (drill_block_break, drill_enemy_hit, daze_splat)"
    - "Drill events fire pogo_bounce on the existing pogo bounce path"
    - "All subscribers wired in Game.__init__ (Phase 31 Pitfall 5 — never Player.__init__)"
  artifacts:
    - path: "src/core/audio.py"
      provides: "Phase 33 D-12 minimal audio surface — 7 named sound slot constants + _NAME_TO_SLOT map + _AUTO_CHANNEL + init_sounds() + play_sfx(name)"
      exports: ["SFX_FUSE_START", "SFX_DRILL_START", "SFX_DRILL_BLOCK_BREAK", "SFX_DRILL_ENEMY_HIT", "SFX_DRILL_IMPACT", "SFX_DAZE_FIRE", "SFX_POGO_BOUNCE", "init_sounds", "play_sfx"]
    - path: "main.py"
      provides: "audio.init_sounds() called once; 7 audio subscribers wired in Game.__init__; drill_enemy_hit particle subscriber wired; spawn_particle_burst PARTICLE_TYPE_TABLE dispatch; src/fusion/pogo.py event_bus.emit('pogo_bounce') on bounce"
      contains: "PARTICLE_TYPE_TABLE"
    - path: "assets/sprites/particles.png"
      provides: "Bank 2 expansion to include y=32 row with 3 new 16x16 cells at (0,32), (16,32), (32,32) using pyxel earthbound palette (4/9/10) for drill cells and blue/green for daze splat"
  key_links:
    - from: "main.py:Game.__init__"
      to: "src/core/audio.py"
      via: "audio.init_sounds() once + audio.play_sfx(name) per subscriber"
      pattern: "audio\\.play_sfx"
    - from: "src/fusion/pogo.py"
      to: "src/anim/event_bus.py"
      via: "event_bus.emit('pogo_bounce') at bounce site"
      pattern: "pogo_bounce"
    - from: "main.py:spawn_particle_burst"
      to: "PARTICLE_TYPE_TABLE"
      via: "type-keyed (u, v) lookup with safe default"
      pattern: "PARTICLE_TYPE_TABLE\\[.*\\]|PARTICLE_TYPE_TABLE\\.get"
---

<objective>
Land the audio identity + particle differentiation surface for Phase 33 per D-12, D-13, D-14, D-15, D-16, D-20: a minimal `src/core/audio.py` module with 7 named SFX cues, a particle dispatch table that routes the reserved `type` arg at `main.py:spawn_particle_burst` to distinct bank-2 cells, and Game.__init__ subscriber wiring for all new events.

Purpose: this plan is the "blindfolded observer" deliverable for FUS-06 — drill, daze, fusion, pogo each get a distinct sonic signature; drill block-break / enemy-hit / daze splat each get a distinct particle palette. Without this plan the new gameplay rules from Plans 03 and 04 fire silent and visually indistinguishable.

Output: src/core/audio.py module; PARTICLE_TYPE_TABLE in main.py; bank-2 expansion of particles.png; subscriber block in Game.__init__; pogo_bounce emit in pogo.py.
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
@src/core/debug.py
@src/core/overlays.py
@main.py
@src/fusion/pogo.py
@src/anim/event_bus.py
@tests/test_audio.py

<interfaces>
<!-- Phase 31 subscriber pattern at main.py:282-348 — Phase 33 additions slot
     in alongside. -->

<!-- audio.py public surface (per RESEARCH § Standard Stack): -->
```python
SFX_FUSE_START = 0
SFX_DRILL_START = 1
SFX_DRILL_BLOCK_BREAK = 2
SFX_DRILL_ENEMY_HIT = 3
SFX_DRILL_IMPACT = 4
SFX_DAZE_FIRE = 5
SFX_POGO_BOUNCE = 6
def init_sounds() -> None: ...   # called once from Game.__init__
def play_sfx(name: str) -> None: ...  # routes to pyxel.play(-1, slot)
```

<!-- Particle dispatch (33-PATTERNS.md § main.py:spawn_particle_burst):
     PARTICLE_TYPE_TABLE keyed by:
     - "block_break" -> existing (PARTICLE_BURST_U=0, PARTICLE_BURST_V=0)
     - "drill_block_break" -> NEW (0, 32) earthbound
     - "drill_enemy_hit" -> NEW (16, 32) combat-flavored
     - "daze_splat" -> NEW (32, 32) blue/green
-->

<!-- Pogo bounce emit site: src/fusion/pogo.py — emits from the same site that
     returns TickResult(request_exit=True, exit_reason="bounced"). One line
     change: event_bus.emit("pogo_bounce") immediately before that return. -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Create src/core/audio.py module</name>
  <files>src/core/audio.py</files>
  <read_first>
    - src/core/debug.py (lines 1-27 — module-level globals + update() function pattern)
    - src/core/overlays.py (lines 1-40 — named-constant block + module-level state)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md (§ src/core/audio.py — full code excerpt)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-RESEARCH.md (§ Standard Stack → Pyxel Audio API surface; § Open Question 4)
    - tests/test_audio.py (Wave 0 RED stubs; this task makes them GREEN)
    - tests/conftest.py (verify mock_pyxel.sounds and mock_pyxel.play exist post-Plan 01)
  </read_first>
  <behavior>
    - `src/core/audio.py` exists with module-level public constants `SFX_FUSE_START=0`, `SFX_DRILL_START=1`, `SFX_DRILL_BLOCK_BREAK=2`, `SFX_DRILL_ENEMY_HIT=3`, `SFX_DRILL_IMPACT=4`, `SFX_DAZE_FIRE=5`, `SFX_POGO_BOUNCE=6` (per D-13 + D-20).
    - Internal `_NAME_TO_SLOT` dict maps event names to slot ints.
    - Internal `_AUTO_CHANNEL = -1` (Pyxel auto-channel sentinel; verified by Open Q #4 — Plan 01 conftest extension makes mock work).
    - `init_sounds()` calls `pyxel.sounds[N].set(...)` for all 7 slots with concrete MML-style note/tone/volume/effect/speed parameters (feel-choice; planner picks distinguishable cues from RESEARCH § Recommendation excerpt).
    - `play_sfx(name)` routes to `pyxel.play(_AUTO_CHANNEL, slot)`; unknown names return silently (no raise, no pyxel.play call).
    - All 3 tests in `tests/test_audio.py` go GREEN.
  </behavior>
  <action>
    Step 1 — Create `src/core/audio.py` with the exact structure from 33-PATTERNS.md § src/core/audio.py. Full file contents:

    ```python
    """Phase 33 D-12 minimal audio surface.

    Defines `pyxel.sounds[N].set()` for the 7 Phase 33 SFX cues + a
    `play_sfx(name)` wrapper. Phase 35 inherits and extends with a full
    sound channel map + debounce; Phase 33's surface stays bounded.

    Channel strategy: `pyxel.play(-1, sound_id)` for auto-channel pickup
    (Pyxel idiom; verified via tests/conftest.py mock extension per
    Plan 01). Phase 35 will replace channel strategy.
    """
    import pyxel

    # --- Sound slot IDs (no magic numbers per project memory) -----------------
    # Phase 33 uses 7 slots out of pyxel's 64-slot budget (slots 0-63).
    SFX_FUSE_START = 0
    SFX_DRILL_START = 1
    SFX_DRILL_BLOCK_BREAK = 2
    SFX_DRILL_ENEMY_HIT = 3   # Phase 33 D-13 NEW (destructive-drill enemy contact)
    SFX_DRILL_IMPACT = 4
    SFX_DAZE_FIRE = 5         # Phase 33 D-13 + D-17 (fused tap-Z)
    SFX_POGO_BOUNCE = 6       # Phase 33 D-20

    _NAME_TO_SLOT: dict[str, int] = {
        "fuse_start": SFX_FUSE_START,
        "drill_start": SFX_DRILL_START,
        "drill_block_break": SFX_DRILL_BLOCK_BREAK,
        "drill_enemy_hit": SFX_DRILL_ENEMY_HIT,
        "drill_impact": SFX_DRILL_IMPACT,
        "daze_fire": SFX_DAZE_FIRE,
        "pogo_bounce": SFX_POGO_BOUNCE,
    }

    # Auto-channel sentinel per Pyxel API (verified mock extension Plan 01).
    _AUTO_CHANNEL = -1


    def init_sounds() -> None:
        """Define all SFX slots. Called once from Game.__init__.

        Per Pyxel API (verified github.com/kitao/pyxel/blob/main/python/pyxel/examples/04_sound_api.py):
            pyxel.sounds[N].set(notes, tones, volumes, effects, speed)
            notes: [CDEFGAB] + [#-] + [0-4] for pitch, R for rest. Lowercase.
            tones: [TSPN] (Triangle, Square, Pulse, Noise). Lowercase.
            volumes: [0-7]. Single char repeats; longer string is per-note.
            effects: [NSVF] (None, Slide, Vibrato, FadeOut). Lowercase.
            speed: integer; lower = faster.

        Cue choices (D-13 + D-15 earthbound drill / blue-green daze /
        springy pogo) — feel choices; tweak via panel iteration.
        """
        # Cue: fuse_start — bright commit chime at WINDUP->FUSED latch.
        pyxel.sounds[SFX_FUSE_START].set("c2e2g2", "p", "6", "n", 25)
        # Cue: drill_start — low whir/rumble at drill activation.
        pyxel.sounds[SFX_DRILL_START].set("e1c1", "n", "5", "f", 20)
        # Cue: drill_block_break — short noise crunch per tile.
        pyxel.sounds[SFX_DRILL_BLOCK_BREAK].set("c2", "n", "6", "f", 10)
        # Cue: drill_enemy_hit — combat-flavored dual-note (impact + thud).
        pyxel.sounds[SFX_DRILL_ENEMY_HIT].set("g2c2", "p", "6", "f", 12)
        # Cue: drill_impact — heavy thud on solid landing (Exit a).
        pyxel.sounds[SFX_DRILL_IMPACT].set("c1g0", "n", "7", "f", 15)
        # Cue: daze_fire — square-wave projectile launch.
        pyxel.sounds[SFX_DAZE_FIRE].set("e2g2", "s", "5", "n", 18)
        # Cue: pogo_bounce — fast springy ascending pair.
        pyxel.sounds[SFX_POGO_BOUNCE].set("g2c3", "s", "5", "n", 8)


    def play_sfx(name: str) -> None:
        """Phase 33 D-12: thin wrapper. Phase 35 will replace channel strategy
        (debounce + per-cue channel reservation).

        Returns silently on unknown name (event-bus subscribers can fire any
        cue name; we do not raise on typos to avoid crashing the game on a
        subscriber bug).
        """
        slot = _NAME_TO_SLOT.get(name)
        if slot is None:
            return
        pyxel.play(_AUTO_CHANNEL, slot)
    ```

    Step 2 — Run the audio test file. The `pytest.importorskip("src.core.audio", ...)` at the top of `tests/test_audio.py` becomes a no-op once the module exists; the 3 tests should go GREEN immediately.
  </action>
  <verify>
    <automated>pytest tests/test_audio.py -x -v</automated>
  </verify>
  <acceptance_criteria>
    - `ls src/core/audio.py` lists the file
    - `grep -c "^SFX_" src/core/audio.py` returns 7 (one per cue)
    - `grep "def init_sounds" src/core/audio.py` returns 1 match
    - `grep "def play_sfx" src/core/audio.py` returns 1 match
    - `grep "_NAME_TO_SLOT" src/core/audio.py` returns at least 2 matches
    - `grep "_AUTO_CHANNEL = -1" src/core/audio.py` returns 1 match
    - `grep -c "pyxel.sounds\\[" src/core/audio.py` returns 7 (one .set() per cue)
    - `pytest tests/test_audio.py -x -v` exits 0 (all 3 tests GREEN)
    - `python -c "from src.core import audio; audio.init_sounds(); audio.play_sfx('drill_enemy_hit'); audio.play_sfx('typo_unknown_cue')"` does not raise
  </acceptance_criteria>
  <done>src/core/audio.py exists with 7 named slot constants, init_sounds populates pyxel.sounds[0..6], play_sfx routes to pyxel.play(-1, slot) for known cues and silently no-ops for unknowns; all test_audio.py tests GREEN.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: particles.png bank-2 expansion + PARTICLE_TYPE_TABLE dispatch</name>
  <files>main.py, assets/sprites/particles.png</files>
  <read_first>
    - main.py:155-180 (existing PARTICLE_*_U/V constant block + SPRITE_MANIFEST dict reference layout)
    - main.py:935-970 (current spawn_particle_burst at line 941 + spawn_explosion shim at line 970)
    - assets/sprites/particles.png (current 64x32 layout — verify dimensions and existing cell occupancy)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md (§ main.py:spawn_particle_burst — concrete BEFORE/AFTER + PARTICLE_TYPE_TABLE; § assets/sprites/particles.png — bank 2 layout)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-RESEARCH.md (§ Pitfall 3 — bank 2 cell collision; § D-15 earthbound palette 4/9/10)
  </read_first>
  <behavior>
    - particles.png expanded from 64x32 to 64x48 (or 64x64 — planner discretion within Pyxel image bank 2 capacity 256x256). New y=32 row contains 3 16x16 cells.
    - Cell at (0, 32): drill block-break (orange/brown shrapnel; pyxel colors 4 brown + 9 orange per D-15).
    - Cell at (16, 32): drill enemy-hit (combat-flavored; pyxel colors 9 orange + 10 yellow per D-15).
    - Cell at (32, 32): daze splat (blue/green to differentiate from drill earthbound and slime green).
    - main.py gains 6 new (u, v) module-level constants in the existing PARTICLE_* block.
    - main.py gains module-level `PARTICLE_TYPE_TABLE` dict mapping type-name to (u, v).
    - main.py:spawn_particle_burst body changes from `u, v = PARTICLE_BURST_U, PARTICLE_BURST_V` to `u, v = PARTICLE_TYPE_TABLE.get(type, (PARTICLE_BURST_U, PARTICLE_BURST_V))` — default fallback preserves spawn_explosion legacy callers.
    - drill_dive.py is updated to call `spawn_particle_burst` (or its current emit subscriber chain) with `type="drill_block_break"` — verify whether the existing drill_block_break subscriber (main.py:282-306) needs to switch its hardcoded `(PARTICLE_BURST_U, PARTICLE_BURST_V)` arg over to `type="drill_block_break"`. If the subscriber currently uses raw u/v args, update to use the type-keyed path so the new earthtone cell renders.
  </behavior>
  <action>
    Step 1 — Expand `assets/sprites/particles.png` from 64x32 to 64x48 (add a new y=32 row of 16x16 cells). Use `pyxel` CLI or PIL to create the cells with the specified colors:
    - (0, 32) — drill block-break: 16x16 cell using pyxel palette colors 4 (brown) + 9 (orange). Pattern: scattered shrapnel sprite — central cluster of color 4 with color 9 highlights at edges.
    - (16, 32) — drill enemy-hit: 16x16 cell using pyxel colors 9 (orange) + 10 (yellow). Pattern: combat impact — radial burst with color 10 center, color 9 edges.
    - (32, 32) — daze splat: 16x16 cell using pyxel color 6 (light blue) + 11 (light green). Pattern: splat — color 11 dominant with color 6 droplets.

    The exact pixel art is procedural-placeholder (per project convention — real art deferred per STATE accumulated decision "Sprite assets use procedural placeholders in v2.0"). Use the pyxel MCP tools (`run_and_capture`, `inspect_bank`) to verify the cells render as expected after edit.

    Step 2 — Edit `main.py` PARTICLE constant block (around line 155-180). Add the 6 new constants AFTER the existing PARTICLE_BURST_U/V entries:

    ```python
    # Phase 33 D-14/D-15: new bank-2 cells for particle differentiation.
    # Drill claims earthbound palette (pyxel colors 4 brown + 9 orange + 10
    # yellow) per D-15. Daze claims blue/green per D-15. Layout per
    # 33-RESEARCH § Pitfall 3 — extend particles.png to y=32 row.
    PARTICLE_DRILL_BREAK_U = 0
    PARTICLE_DRILL_BREAK_V = 32
    PARTICLE_DRILL_HIT_U = 16
    PARTICLE_DRILL_HIT_V = 32
    PARTICLE_DAZE_U = 32
    PARTICLE_DAZE_V = 32
    ```

    Step 3 — Add module-level `PARTICLE_TYPE_TABLE` dict immediately AFTER the new constants:

    ```python
    # Phase 33 D-14: dispatch table for spawn_particle_burst type arg.
    # Default fallback (block_break) preserves spawn_explosion legacy callers
    # at line 970.
    PARTICLE_TYPE_TABLE = {
        "block_break":       (PARTICLE_BURST_U, PARTICLE_BURST_V),
        "drill_block_break": (PARTICLE_DRILL_BREAK_U, PARTICLE_DRILL_BREAK_V),
        "drill_enemy_hit":   (PARTICLE_DRILL_HIT_U, PARTICLE_DRILL_HIT_V),
        "daze_splat":        (PARTICLE_DAZE_U, PARTICLE_DAZE_V),
    }
    ```

    Step 4 — Edit `main.py:spawn_particle_burst` (around line 941). Replace the hardcoded `u, v = PARTICLE_BURST_U, PARTICLE_BURST_V` line with:

    ```python
    u, v = PARTICLE_TYPE_TABLE.get(type, (PARTICLE_BURST_U, PARTICLE_BURST_V))
    ```

    Step 5 — Update the existing `_on_drill_block_break` subscriber at main.py:282-306. It currently hardcodes `bank_u=PARTICLE_BURST_U, bank_v=PARTICLE_BURST_V` in the inline Particle constructor — change it to call `self.spawn_particle_burst(cx, cy, type="drill_block_break")` so the new earthtone cell renders. Computing `cx = tx * tuning.TILE_SIZE + 4; cy = ty * tuning.TILE_SIZE + 4` stays as-is; the visual change is just the cell type.

    NOTE on alignment: spawn_particle_burst expects pixel coords; the existing subscriber computes pixel coords from grid coords; the call signature already matches. Verify by reading the exact lines before editing.
  </action>
  <verify>
    <automated>pytest tests/ -x -q -k "not feel and not feel_targets"</automated>
  </verify>
  <acceptance_criteria>
    - `python -c "import pyxel; pyxel.init(64, 64); pyxel.images[2].load(0, 0, 'assets/sprites/particles.png'); print('OK')"` does NOT raise OR (if pyxel cannot init headless) `python -c "from PIL import Image; im = Image.open('assets/sprites/particles.png'); print(im.size); assert im.size[1] >= 48"` outputs `(64, 48)` or larger
    - `grep "PARTICLE_DRILL_BREAK_U" main.py` returns at least 1 match
    - `grep "PARTICLE_DRILL_HIT_U" main.py` returns at least 1 match
    - `grep "PARTICLE_DAZE_U" main.py` returns at least 1 match
    - `grep "PARTICLE_TYPE_TABLE" main.py` returns at least 2 matches (definition + use site)
    - `grep "PARTICLE_TYPE_TABLE.get(type" main.py` returns 1 match (the dispatch line in spawn_particle_burst)
    - `grep 'type="drill_block_break"' main.py` returns at least 1 match (the _on_drill_block_break subscriber updated)
    - `pytest tests/ -x -q -k "not feel and not feel_targets"` exits 0
  </acceptance_criteria>
  <done>particles.png has y=32 row with 3 new 16x16 cells; main.py defines 6 new PARTICLE_*_U/V constants + PARTICLE_TYPE_TABLE; spawn_particle_burst dispatches via the table with safe default; existing drill_block_break subscriber routes through type="drill_block_break".</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Game.__init__ subscriber wiring + pogo_bounce emit</name>
  <files>main.py, src/fusion/pogo.py</files>
  <read_first>
    - main.py:270-350 (Game.__init__ subscriber block — the canonical Phase 31 Pitfall 5 hoist site)
    - main.py:276-280 (existing imports — `import math as _math`, `from src.anim import event_bus as _event_bus`, `from src.entities.effects import Particle as _Particle`, `from src.core import tuning as _tuning`)
    - src/fusion/pogo.py (locate the bounce return site — `return TickResult(dx=0.0, dy=tuning.POGO_BOUNCE_VELOCITY, request_exit=True, exit_reason="bounced")` — the pogo_bounce emit goes IMMEDIATELY before this return)
    - src/anim/event_bus.py (verify subscribe/emit signatures)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md (§ main.py:Game.__init__ — concrete subscriber excerpt with closure pattern)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-CONTEXT.md (D-16, D-20, Pitfall 5 reminder)
  </read_first>
  <behavior>
    - main.py imports `from src.core import audio as _audio` (alongside existing _math/_event_bus/_Particle/_tuning imports).
    - Game.__init__ calls `_audio.init_sounds()` exactly once after the existing reset() call (the same point Phase 31 wires its subscribers).
    - 7 audio subscribers wired in Game.__init__ via closures over `self`: one per cue (fuse_start, drill_start, drill_block_break, drill_enemy_hit, drill_impact, daze_fire, pogo_bounce).
    - 1 NEW particle subscriber for `drill_enemy_hit`: receives `x=`/`y=` pixel coords (per drill_dive.py emit kwargs from Plan 03) and calls `self.spawn_particle_burst(x, y, type="drill_enemy_hit")`.
    - `src/fusion/pogo.py` emits `event_bus.emit("pogo_bounce")` right before each `return TickResult(... exit_reason="bounced")` site (verify Plan 04 didn't change this; pogo bounces remain unchanged behaviorally).
    - All wiring lives in Game.__init__ — NEVER Player.__init__ (Pitfall 5 — subscribers must not accumulate per Game.reset()).
  </behavior>
  <action>
    Step 1 — Edit `main.py` import block near line 276-280. Add:
    ```python
    from src.core import audio as _audio
    ```

    Step 2 — In `Game.__init__`, locate the existing subscriber block (around line 282-348). At the END of that block (after the last existing subscribe call), add:

    ```python
    # Phase 33 D-12: audio module init. Defines pyxel sound slots 0-6.
    _audio.init_sounds()

    # Phase 33 D-13/D-16: audio subscribers (7 cues — drill events, fuse_start,
    # daze_fire, pogo_bounce). Audio is a side-channel like particles.
    def _on_audio_fuse_start(**kw):        _audio.play_sfx("fuse_start")
    def _on_audio_drill_start(**kw):       _audio.play_sfx("drill_start")
    def _on_audio_drill_block_break(**kw): _audio.play_sfx("drill_block_break")
    def _on_audio_drill_enemy_hit(**kw):   _audio.play_sfx("drill_enemy_hit")
    def _on_audio_drill_impact(**kw):      _audio.play_sfx("drill_impact")
    def _on_audio_daze_fire(**kw):         _audio.play_sfx("daze_fire")
    def _on_audio_pogo_bounce(**kw):       _audio.play_sfx("pogo_bounce")
    _event_bus.subscribe("fuse_start",        _on_audio_fuse_start)
    _event_bus.subscribe("drill_start",       _on_audio_drill_start)
    _event_bus.subscribe("drill_block_break", _on_audio_drill_block_break)
    _event_bus.subscribe("drill_enemy_hit",   _on_audio_drill_enemy_hit)
    _event_bus.subscribe("drill_impact",      _on_audio_drill_impact)
    _event_bus.subscribe("daze_fire",         _on_audio_daze_fire)
    _event_bus.subscribe("pogo_bounce",       _on_audio_pogo_bounce)

    # Phase 33 D-14/D-16: drill_enemy_hit particle subscriber (combat-flavored
    # burst at enemy contact point). x/y are pixel coords from drill_dive.py.
    def _on_drill_enemy_hit(x=None, y=None, **kw):
        if x is None or y is None:
            return
        self.spawn_particle_burst(x, y, type="drill_enemy_hit")
    _event_bus.subscribe("drill_enemy_hit", _on_drill_enemy_hit)
    ```

    Step 3 — `src/fusion/pogo.py` — emit pogo_bounce.

    Find the return statement(s) for the bounce path: `return TickResult(dx=0.0, dy=tuning.POGO_BOUNCE_VELOCITY, request_exit=True, exit_reason="bounced")` (or similar; multiple sites if pogo bounces on multiple kinds of contact). Immediately BEFORE each such return, add:

    ```python
    event_bus.emit("pogo_bounce")
    ```

    Verify `from src.anim import event_bus` is imported at the top of pogo.py (Plan 02 may not have needed it; this plan does — add the import if missing).

    Step 4 — Manual smoke verification (post-completion): boot the game, fuse on the player, drill into an enemy — particle subscriber fires drill_enemy_hit and audio cue plays; pogo bounce on enemy plays the pogo_bounce SFX. (Not a pytest verification; smoke test for human playtest in Plan 06.)
  </action>
  <verify>
    <automated>pytest tests/ -x -q</automated>
  </verify>
  <acceptance_criteria>
    - `grep "from src.core import audio as _audio" main.py` returns 1 match
    - `grep "_audio.init_sounds()" main.py` returns 1 match
    - `grep -c "_event_bus.subscribe(" main.py` returns at least 12 (existing ~5 + 8 new from this task: 7 audio + 1 particle drill_enemy_hit)
    - `grep "_on_audio_drill_enemy_hit" main.py` returns at least 2 matches (definition + subscribe call)
    - `grep "_on_drill_enemy_hit" main.py` returns at least 2 matches (definition + subscribe — distinct from the audio version above by name; can collapse if planner renames)
    - `grep 'type="drill_enemy_hit"' main.py` returns 1 match (in the particle subscriber)
    - `grep "pogo_bounce" src/fusion/pogo.py` returns at least 1 match (event_bus.emit call)
    - `grep "pogo_bounce" main.py` returns at least 2 matches (subscribe + define)
    - `grep "from src.anim import event_bus" src/fusion/pogo.py` returns 1 match
    - `pytest tests/ -x -q` exits 0 (full suite GREEN)
    - `python -c "from main import Game" 2>&amp;1 | grep -E "error|Error"` returns no matches (module imports cleanly)
  </acceptance_criteria>
  <done>audio.init_sounds called once in Game.__init__; 7 audio subscribers wired; drill_enemy_hit particle subscriber wired; pogo_bounce emitted from pogo.py bounce path; all wiring in Game.__init__ (Pitfall 5 closure); full suite GREEN.</done>
</task>

</tasks>

<verification>
- `pytest tests/ -x -q` exits 0 (Plans 01-05 cumulative tests all GREEN).
- Manual smoke (deferred to Plan 06): fuse + drill into 3-enemy stack — visual: 3 distinct drill_enemy_hit particle bursts (orange/yellow combat palette, distinct from earthbound block-break); audio: 3 drill_enemy_hit cues distinguishable from drill_block_break.
- Pogo bounce manual smoke: airborne DOWN+SPACE on enemy — pogo_bounce SFX fires and is sonically distinct from drill_impact thud (D-20 "blindfolded observer" extension to pogo).
- Subscriber leak check: `python -c "import main; from src.anim import event_bus; print(len(event_bus._subscribers))"` (or equivalent introspection if event_bus exposes one) — count is constant after multiple `Game.reset()` calls (Pitfall 5 closure).
</verification>

<success_criteria>
- src/core/audio.py exists with 7 named slot constants + init_sounds + play_sfx
- All 3 tests in test_audio.py GREEN
- particles.png has bank-2 y=32 row with 3 new cells
- main.py PARTICLE_TYPE_TABLE dispatches type arg correctly
- spawn_particle_burst routes via PARTICLE_TYPE_TABLE.get with safe default
- 7 audio subscribers + 1 particle subscriber wired in Game.__init__
- pogo_bounce emitted from pogo.py bounce path
- ALL subscribers in Game.__init__ (Pitfall 5)
- Full pytest suite GREEN
</success_criteria>

<output>
After completion, create `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-05-SUMMARY.md` per @$HOME/.claude/get-shit-done/templates/summary.md.
</output>
