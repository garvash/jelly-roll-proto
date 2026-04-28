---
phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
plan: 01
type: execute
wave: 0
depends_on: []
files_modified:
  - tests/conftest.py
  - tests/test_destructive_drill.py
  - tests/test_daze_shot.py
  - tests/test_audio.py
  - tests/test_tuning_migration.py
autonomous: true
requirements: [FUS-06]
requirements_addressed: [FUS-06]
tags: [pyxel, audio, fusion, testing, tdd]

must_haves:
  truths:
    - "All four new test files exist and run as pytest collections"
    - "Tests are RED (xfail/skip-marked or asserting on not-yet-existent symbols) — green after later waves"
    - "conftest.py mock_pyxel exposes pyxel.sounds[N] subscriptable surface (Open Q #4)"
  artifacts:
    - path: "tests/test_destructive_drill.py"
      provides: "Wave 0 stubs covering drill_hits_enemy_and_continues, multi-enemy chain, no-exit, juice-empty Exit-b"
    - path: "tests/test_daze_shot.py"
      provides: "Wave 0 stubs covering fused tap fires daze + low-juice gate"
    - path: "tests/test_audio.py"
      provides: "Wave 0 stubs covering audio.init_sounds() + play_sfx routing"
    - path: "tests/test_tuning_migration.py"
      provides: "Wave 0 stubs covering 6 migrated keys readable + flat_index inclusion"
    - path: "tests/conftest.py"
      provides: "mock_pyxel.sounds = [MagicMock() for _ in range(64)] extension; pyxel.play MagicMock"
  key_links:
    - from: "tests/test_audio.py"
      to: "tests/conftest.py"
      via: "import pyxel after sys.modules['pyxel'] mock; pyxel.sounds[N].set must be callable"
      pattern: "mock_pyxel\\.sounds"
    - from: "tests/test_destructive_drill.py"
      to: "src.fusion.drill_dive (Wave 2)"
      via: "from src.fusion.drill_dive import DrillDive, DRILL_DAMAGE"
      pattern: "DRILL_DAMAGE"
---

<objective>
Land Wave 0 test scaffolding for Phase 33's new behaviors so all later-wave implementations have a Nyquist-compliant red→green target. Extend `tests/conftest.py` so mocked `pyxel.sounds[N].set(...)` does not raise (Open Question #4 from RESEARCH).

Purpose: every later task can include `<automated>pytest tests/test_*.py -x</automated>` in its verify block. Without these stubs, the audit gate "no 3 consecutive tasks without automated verify" fails.

Output: 4 new test files (RED stubs), one extended conftest.py.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-CONTEXT.md
@.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-RESEARCH.md
@.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-VALIDATION.md
@.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md
@tests/conftest.py
@tests/test_drill_dive_parity.py
@tests/test_pogo.py
@tests/test_tuning_livereach.py
@tests/test_event_bus.py

<interfaces>
<!-- Symbols Wave 2/3 will produce; tests reference them as RED stubs. -->

From src/fusion/drill_dive.py (Wave 2 will add):
```python
DRILL_DAMAGE = 1   # module-level constant per D-04
# DrillDive._scan_and_damage_enemies(player, slime) helper added inside on_tick
```

From src/core/audio.py (Wave 3 will add):
```python
SFX_FUSE_START = 0
SFX_DRILL_START = 1
SFX_DRILL_BLOCK_BREAK = 2
SFX_DRILL_ENEMY_HIT = 3
SFX_DRILL_IMPACT = 4
SFX_DAZE_FIRE = 5
SFX_POGO_BOUNCE = 6
def init_sounds() -> None: ...
def play_sfx(name: str) -> None: ...
```

From assets/physics-schema.json (Wave 1 will add):
```
tuning.WINDUP_DURATION_FRAMES, tuning.ACCELERATED_REGEN_RATE,
tuning.POGO_BOUNCE_VELOCITY, tuning.POGO_COOLDOWN_FRAMES,
tuning.DRILL_ENEMY_COST, tuning.SLIME_DAZE_COST
```

From src/entities/player.py (Wave 2 will modify):
```
fused-branch in spit handler at line 197 emits "daze_fire" event
and consumes tuning.SLIME_DAZE_COST.
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: FUSION-DESIGN SHA gate + conftest mock_pyxel extension</name>
  <files>tests/conftest.py</files>
  <read_first>
    - tests/conftest.py (existing 92-line baseline)
    - .planning/FUSION-DESIGN.md (frontmatter `locked_commit:` field — read first 20 lines)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-CONTEXT.md (D-21 — locked_commit must equal ce5bddbd9c03ac76271f17290633da2b2e492c51)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-RESEARCH.md (Open Question #4 — mock_pyxel.sounds may need explicit list)
  </read_first>
  <behavior>
    - SHA gate: locked_commit field in FUSION-DESIGN.md frontmatter equals ce5bddbd9c03ac76271f17290633da2b2e492c51 (cycle 3 re-lock from Phase 32.1). If not, ABORT phase planning.
    - conftest.py mock_pyxel exposes a 64-element sounds list of MagicMocks; each element supports .set(...) without raising.
    - conftest.py mock_pyxel.play is a MagicMock so tests can assert it was called with (channel, sound_id).
  </behavior>
  <action>
    Step 1 — SHA gate (executor performs ONCE before any code edits):

    ```bash
    grep "^locked_commit:" .planning/FUSION-DESIGN.md
    ```

    Expected exact line: `locked_commit: ce5bddbd9c03ac76271f17290633da2b2e492c51`. If the SHA does not match, STOP and notify the user — a re-lock cycle has occurred and Phase 33 plans must be revised against the new SHA.

    Step 2 — Extend `tests/conftest.py` per D-12 / Open Question #4. Replace the line:

    ```python
    sys.modules.setdefault("pyxel", MagicMock())
    ```

    with a richer mock factory (defined just above the line) that pre-populates `pyxel.sounds` and `pyxel.play`:

    ```python
    def _make_pyxel_mock():
        m = MagicMock()
        # Phase 33 D-12 + Open Q #4: pyxel.sounds[N].set(...) must be callable;
        # the default MagicMock supports __getitem__ but the returned mock has
        # no .set tracked across slots. Pin a 64-element list so each slot is
        # the same MagicMock instance across calls.
        m.sounds = [MagicMock() for _ in range(64)]
        m.play = MagicMock()
        return m

    sys.modules.setdefault("pyxel", _make_pyxel_mock())
    ```

    Do NOT change any existing fixture (mock_level, mock_slime, make_game_with_fusion) or the `_reset_event_bus` autouse fixture. Keep imports at the top of the file ordered: `sys`, `unittest.mock.MagicMock`, the new helper, the sys.modules.setdefault line, then `import pytest` and `from src.anim import event_bus` AFTER the pyxel mock is installed.
  </action>
  <verify>
    <automated>pytest tests/ -x -q --co 2>&amp;1 | tail -5</automated>
  </verify>
  <acceptance_criteria>
    - `grep "^locked_commit: ce5bddbd9c03ac76271f17290633da2b2e492c51$" .planning/FUSION-DESIGN.md` returns a match
    - `grep -n "_make_pyxel_mock" tests/conftest.py` returns a match
    - `grep -n "m.sounds = \\[MagicMock() for _ in range(64)\\]" tests/conftest.py` returns a match
    - `grep -n "m.play = MagicMock()" tests/conftest.py` returns a match
    - `python -c "import pyxel; pyxel.sounds[0].set('c', 'p', '6', 'n', 25); pyxel.play(-1, 0)"` (after `pytest --co` has loaded conftest) does NOT raise — verified indirectly via pytest collection succeeding
    - `pytest tests/ -x -q --co 2>&amp;1 | grep -E "error|Error"` returns no matches
  </acceptance_criteria>
  <done>FUSION-DESIGN SHA verified equals ce5bddbd9c03ac76271f17290633da2b2e492c51; conftest.py mocks pyxel.sounds as a 64-element list and pyxel.play as a MagicMock; existing tests collect without errors.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Wave 0 test stubs — destructive_drill + daze_shot</name>
  <files>tests/test_destructive_drill.py, tests/test_daze_shot.py</files>
  <read_first>
    - tests/test_drill_dive_parity.py (lines 1-150 — full mock-pyxel preamble + MockLevelMap + make_player_and_slime + _stub_input_manager helper)
    - tests/test_pogo.py (lines 1-100 — Pogo enemy-contact tests)
    - tests/test_event_bus.py (lines 87-130 — `patch.object(input_manager, ...)` + _btn_map / _btnp_map / _btnr_map helpers)
    - tests/conftest.py (after Task 1 — make_game_with_fusion fixture, mock_slime fixture)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md (§ tests/test_destructive_drill.py and § tests/test_daze_shot.py — code excerpts)
    - src/fusion/pogo.py:168-217 (the AABB scan pattern Wave 2 will mirror in drill_dive.py)
  </read_first>
  <behavior>
    - test_destructive_drill.py asserts the destructive-drill rule (D-03/D-04/D-05) — RED until Wave 2 ships drill_dive.py changes:
      - Test 1: drill on_tick with intersecting alive enemy calls enemy.take_damage(DRILL_DAMAGE), drains tuning.DRILL_ENEMY_COST juice, emits drill_enemy_hit, returns TickResult(request_exit=False).
      - Test 2: drill intersecting 2 enemies in one frame damages both, drains 2x cost, emits drill_enemy_hit twice.
      - Test 3: enemy intersection does NOT trigger request_exit / "solid_landing" reason (continue-through invariant).
      - Test 4: 5 enemies stacked + juice=30 + DRILL_ENEMY_COST=10 → all 5 hit on the same frame, juice clamped to 0, Exit (b) fires on NEXT call (option (a) clamp ordering per RESEARCH Pitfall 2 recommendation).
    - test_daze_shot.py asserts the daze-shot rule (D-17) — RED until Wave 2 ships player.py:197 changes:
      - Test 1: fused player Z-tap fires projectile + consumes tuning.SLIME_DAZE_COST + emits daze_fire event.
      - Test 2: fused player with juice < tuning.SLIME_DAZE_COST does NOT fire and does NOT consume juice (Pitfall 4 cancel-spam guard).
  </behavior>
  <action>
    Create both test files with the exact mock-pyxel preamble from `tests/test_drill_dive_parity.py:19-46` (verbatim copy — same KEY_* constants, same btn/btnp/btnr/blt/rect/pset stubs). Use `from src.core import tuning` for cost reads (do NOT hardcode 15.0 or 20.0; tests must read live tuning values so post-migration the tests stay green).

    For `tests/test_destructive_drill.py`, create exactly four test functions matching the Test 1-4 list under <behavior>. Use the patterns from 33-PATTERNS.md § tests/test_destructive_drill.py — including:

    - `class MockLevelMap` (verbatim from test_drill_dive_parity.py)
    - `def make_player_and_slime(...)` factory
    - `def _make_alive_enemy(x, y, w=16, h=16, hp=1)` returning a MagicMock with x/y/w/h/hp/is_alive/take_damage attrs
    - Each test imports `from src.fusion.drill_dive import DrillDive, DRILL_DAMAGE` (RED until Wave 2). Mark these tests with `pytest.importorskip("src.fusion.drill_dive", reason="Wave 2 will add DRILL_DAMAGE constant")` at module level — this is sufficient to keep pytest collection green even though the constant does not exist yet.
    - `event_bus.subscribe("drill_enemy_hit", lambda **kw: captured.append(kw))` to capture emissions.
    - For Test 4, define `EXPECTED_KILLS_BEFORE_EXIT = 5` and `STARTING_JUICE = 30.0` as named constants at module top (no magic numbers).
    - `pytest.mark.skip(reason="Wave 2 implements destructive-drill scan")` on each test until Wave 2 lands; OR use `pytest.xfail(reason=...)` so collection succeeds.

    For `tests/test_daze_shot.py`, create exactly two test functions:

    ```python
    """Phase 33 FUS-06 D-17 — daze-shot fused-branch tests.

    RED until Wave 2 modifies src/entities/player.py:197 to remove the
    `not self.is_fused` gate and add the SLIME_DAZE_COST consume + daze_fire emit.
    """
    import pytest
    from unittest.mock import MagicMock, patch
    from src.anim import event_bus
    import src.core.input as input_manager
    from src.core import tuning

    pytest.importorskip("src.fusion.manager", reason="Wave 2 dep")


    def _btn_map_factory(**overrides):
        mapping = {"left": False, "right": False, "up": False, "down": False,
                   "jump": False, "spit": False}
        mapping.update(overrides)
        return lambda name: mapping.get(name, False)


    @pytest.mark.skip(reason="Wave 2 implements daze-shot fused-branch")
    def test_fused_tap_fires_daze(mock_level, mock_slime, make_game_with_fusion):
        captured = []
        event_bus.subscribe("daze_fire", lambda **kw: captured.append(kw))
        from src.entities.player import Player
        game = make_game_with_fusion()
        p = Player(100, 100, mock_level, game=game)
        p.is_grounded = True
        game.fusion_manager.latch_fuse(mock_slime)
        assert p.is_fused
        mock_slime.juice = tuning.SLIME_DAZE_COST + 10
        initial_juice = mock_slime.juice
        with patch.object(input_manager, "btn", side_effect=_btn_map_factory()), \
             patch.object(input_manager, "btnp", side_effect=_btn_map_factory()), \
             patch.object(input_manager, "btnr", side_effect=_btn_map_factory()), \
             patch.object(input_manager, "was_tap", return_value=True), \
             patch.object(input_manager, "hold_frames", return_value=0):
            p.handle_input(mock_slime)
        assert mock_slime.juice == initial_juice - tuning.SLIME_DAZE_COST
        assert len(captured) >= 1


    @pytest.mark.skip(reason="Wave 2 implements daze-shot fused-branch")
    def test_daze_blocked_on_low_juice(mock_level, mock_slime, make_game_with_fusion):
        captured = []
        event_bus.subscribe("daze_fire", lambda **kw: captured.append(kw))
        from src.entities.player import Player
        game = make_game_with_fusion()
        p = Player(100, 100, mock_level, game=game)
        p.is_grounded = True
        game.fusion_manager.latch_fuse(mock_slime)
        # Juice intentionally below SLIME_DAZE_COST
        mock_slime.juice = max(0.0, tuning.SLIME_DAZE_COST - 1)
        initial_juice = mock_slime.juice
        with patch.object(input_manager, "was_tap", return_value=True), \
             patch.object(input_manager, "btn", side_effect=_btn_map_factory()), \
             patch.object(input_manager, "btnp", side_effect=_btn_map_factory()), \
             patch.object(input_manager, "btnr", side_effect=_btn_map_factory()), \
             patch.object(input_manager, "hold_frames", return_value=0):
            p.handle_input(mock_slime)
        assert mock_slime.juice == initial_juice  # unchanged
        assert len(captured) == 0
    ```

    Note: `tuning.SLIME_DAZE_COST` does not exist yet (Wave 1 adds it); the `pytest.mark.skip` keeps collection green. Wave 1 unmarks (or removes the skip) once the schema migration ships; Wave 2 unmarks once the player.py change ships.
  </action>
  <verify>
    <automated>pytest tests/test_destructive_drill.py tests/test_daze_shot.py -v --co 2>&amp;1 | tail -10</automated>
  </verify>
  <acceptance_criteria>
    - `ls tests/test_destructive_drill.py tests/test_daze_shot.py` lists both files
    - `grep -c "^def test_" tests/test_destructive_drill.py` returns 4 (after stripping comment lines if any — use `grep -v '^#' tests/test_destructive_drill.py | grep -c '^def test_'` if needed)
    - `grep -c "^def test_" tests/test_daze_shot.py` returns 2
    - `grep "DRILL_DAMAGE" tests/test_destructive_drill.py` returns at least one match
    - `grep "tuning.DRILL_ENEMY_COST" tests/test_destructive_drill.py` returns at least one match
    - `grep "tuning.SLIME_DAZE_COST" tests/test_daze_shot.py` returns at least one match
    - `grep "drill_enemy_hit" tests/test_destructive_drill.py` returns at least one match
    - `grep "daze_fire" tests/test_daze_shot.py` returns at least one match
    - `pytest tests/test_destructive_drill.py tests/test_daze_shot.py -v --co 2>&amp;1 | grep -E "error|Error"` returns no matches (collection succeeds)
    - `pytest tests/test_destructive_drill.py tests/test_daze_shot.py -v 2>&amp;1 | grep -E "passed|skipped"` shows skipped tests (no failures yet)
  </acceptance_criteria>
  <done>Both test files exist with correct test counts; all tests collect without errors and are SKIP-marked pending Wave 1/2 implementations; uses `tuning.X` reads (not hardcoded values) so post-migration tests stay correct.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Wave 0 test stubs — audio + tuning_migration</name>
  <files>tests/test_audio.py, tests/test_tuning_migration.py</files>
  <read_first>
    - tests/conftest.py (after Task 1 — verifies pyxel.sounds and pyxel.play are pre-mocked)
    - tests/test_tuning_livereach.py (lines 1-90 — autouse `tuning.reset()` fixture pattern)
    - tests/test_tuning.py (lines 32-48 — constant-baseline assertions pattern)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-PATTERNS.md (§ tests/test_audio.py and § tests/test_tuning_migration.py — code excerpts)
    - .planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-RESEARCH.md (§ Validation → Phase Requirements → Test Map)
    - src/core/tuning.py:50-126 (_flat_index mechanics)
  </read_first>
  <behavior>
    - test_audio.py asserts the audio module surface (D-12, D-13) — RED until Wave 3 ships src/core/audio.py:
      - Test 1: audio.init_sounds() runs without raising; pyxel.sounds[0..6].set was called once each (7 cues per D-13/D-20).
      - Test 2: audio.play_sfx("drill_enemy_hit") calls pyxel.play(-1, audio.SFX_DRILL_ENEMY_HIT).
      - Test 3: audio.play_sfx("not_a_real_cue") returns silently (no pyxel.play call, no raise).
    - test_tuning_migration.py asserts the 6 migrated keys (D-01, D-02, D-05, D-17) — RED until Wave 1 ships schema additions:
      - Parametrized test: tuning.WINDUP_DURATION_FRAMES, tuning.ACCELERATED_REGEN_RATE, tuning.POGO_BOUNCE_VELOCITY, tuning.POGO_COOLDOWN_FRAMES, tuning.DRILL_ENEMY_COST, tuning.SLIME_DAZE_COST all read schema-seed values.
      - flat_index test: all 6 keys present in tuning._flat_index (Pitfall 6 prevention).
      - Use-site-read test: src/fusion/charge_controller.py source contains `tuning.WINDUP_DURATION_FRAMES` (use-site read post-migration), and contains NO `^WINDUP_DURATION_FRAMES = ` module-level assignment line.
  </behavior>
  <action>
    Create `tests/test_audio.py` with the following exact structure (slot count constant + 3 tests):

    ```python
    """Phase 33 FUS-06 D-12/D-13 — audio module surface tests.

    RED until Wave 3 ships src/core/audio.py.
    """
    import pytest
    import pyxel  # provided by conftest mock (Task 1 extended sounds + play)

    pytest.importorskip("src.core.audio", reason="Wave 3 ships audio module")
    from src.core import audio

    # Phase 33 D-13 + D-20: 7 cues across slots 0..6.
    EXPECTED_SLOT_COUNT = 7


    def test_audio_init_does_not_raise():
        """init_sounds() runs and calls pyxel.sounds[N].set on slots 0..6."""
        # Reset .set call counters first (each MagicMock slot tracks calls).
        for slot_id in range(EXPECTED_SLOT_COUNT):
            pyxel.sounds[slot_id].set.reset_mock()
        audio.init_sounds()
        for slot_id in range(EXPECTED_SLOT_COUNT):
            assert pyxel.sounds[slot_id].set.called, (
                f"slot {slot_id} not set; D-13 expects 7 cues"
            )


    def test_play_sfx_known_name_routes_to_pyxel_play():
        """play_sfx('drill_enemy_hit') calls pyxel.play(-1, SFX_DRILL_ENEMY_HIT)."""
        pyxel.play.reset_mock()
        audio.play_sfx("drill_enemy_hit")
        pyxel.play.assert_called_once_with(-1, audio.SFX_DRILL_ENEMY_HIT)


    def test_play_sfx_unknown_name_silent():
        """Unknown cue name returns silently (no raise, no pyxel.play call)."""
        pyxel.play.reset_mock()
        audio.play_sfx("not_a_real_cue")
        pyxel.play.assert_not_called()
    ```

    Create `tests/test_tuning_migration.py` with the following exact structure:

    ```python
    """Phase 33 FUS-06 D-01/D-02/D-05/D-17 — tuning migration smoke tests.

    RED until Wave 1 ships schema additions to assets/physics-schema.json.
    """
    import re
    from pathlib import Path
    import pytest
    from src.core import tuning


    @pytest.fixture(autouse=True)
    def _tuning_reset():
        yield
        tuning.reset()


    # Phase 33 D-01/D-02/D-05/D-17 — schema-seed baseline values.
    EXPECTED_WINDUP_DURATION_FRAMES = 30
    EXPECTED_ACCELERATED_REGEN_RATE = 1.0
    EXPECTED_POGO_BOUNCE_VELOCITY = -2.5
    EXPECTED_POGO_COOLDOWN_FRAMES = 0
    EXPECTED_DRILL_ENEMY_COST = 15.0   # CONTEXT D-05 starting point
    EXPECTED_SLIME_DAZE_COST = 20.0    # CONTEXT D-17 starting point


    @pytest.mark.parametrize("key,expected", [
        ("WINDUP_DURATION_FRAMES",  EXPECTED_WINDUP_DURATION_FRAMES),
        ("ACCELERATED_REGEN_RATE",  EXPECTED_ACCELERATED_REGEN_RATE),
        ("POGO_BOUNCE_VELOCITY",    EXPECTED_POGO_BOUNCE_VELOCITY),
        ("POGO_COOLDOWN_FRAMES",    EXPECTED_POGO_COOLDOWN_FRAMES),
        ("DRILL_ENEMY_COST",        EXPECTED_DRILL_ENEMY_COST),
        ("SLIME_DAZE_COST",         EXPECTED_SLIME_DAZE_COST),
    ])
    def test_new_tuning_key_readable(key, expected):
        actual = getattr(tuning, key)
        assert actual == expected, (
            f"tuning.{key} expected {expected!r}, got {actual!r}. "
            f"Pitfall 5: schema-seed must equal current hardcoded baseline."
        )


    def test_new_tuning_keys_in_flat_index():
        expected_keys = {"WINDUP_DURATION_FRAMES", "ACCELERATED_REGEN_RATE",
                         "POGO_BOUNCE_VELOCITY", "POGO_COOLDOWN_FRAMES",
                         "DRILL_ENEMY_COST", "SLIME_DAZE_COST"}
        missing = expected_keys - set(tuning._flat_index)
        assert not missing, f"Pitfall 6 — missing tuning keys: {missing}"


    # Phase 33 D-01: use-site-read invariant. After Wave 1 migration,
    # charge_controller.py MUST read tuning.X (not module-level constants).
    def test_charge_controller_uses_tuning_at_use_site():
        cc_path = Path("src/fusion/charge_controller.py")
        text = cc_path.read_text(encoding="utf-8")
        # Module-level constant assignments must NOT exist post-migration.
        assert not re.search(r"^WINDUP_DURATION_FRAMES\\s*=", text, re.MULTILINE), (
            "D-01: WINDUP_DURATION_FRAMES module constant should be deleted; "
            "use tuning.WINDUP_DURATION_FRAMES at use-site instead."
        )
        assert not re.search(r"^ACCELERATED_REGEN_RATE\\s*=", text, re.MULTILINE), (
            "D-01: ACCELERATED_REGEN_RATE module constant should be deleted."
        )
        # Use-site reads must exist.
        assert "tuning.WINDUP_DURATION_FRAMES" in text, (
            "D-01: charge_controller.py must read tuning.WINDUP_DURATION_FRAMES"
        )
        assert "tuning.ACCELERATED_REGEN_RATE" in text, (
            "D-01: charge_controller.py must read tuning.ACCELERATED_REGEN_RATE"
        )


    def test_pogo_uses_tuning_at_use_site():
        pogo_path = Path("src/fusion/pogo.py")
        text = pogo_path.read_text(encoding="utf-8")
        assert not re.search(r"^POGO_BOUNCE_VELOCITY\\s*=", text, re.MULTILINE), (
            "D-02: POGO_BOUNCE_VELOCITY module constant should be deleted."
        )
        assert not re.search(r"^POGO_COOLDOWN_FRAMES\\s*=", text, re.MULTILINE), (
            "D-02: POGO_COOLDOWN_FRAMES module constant should be deleted."
        )
        assert "tuning.POGO_BOUNCE_VELOCITY" in text
        # POGO_INITIAL_DY and POGO_DAMAGE STAY hardcoded per D-02.
        assert re.search(r"^POGO_INITIAL_DY\\s*=", text, re.MULTILINE), (
            "D-02: POGO_INITIAL_DY MUST stay hardcoded (Mario-64 visual parity)."
        )
        assert re.search(r"^POGO_DAMAGE\\s*=", text, re.MULTILINE), (
            "D-02: POGO_DAMAGE MUST stay hardcoded (gameplay constant)."
        )
    ```
  </action>
  <verify>
    <automated>pytest tests/test_audio.py tests/test_tuning_migration.py -v --co 2>&amp;1 | tail -10</automated>
  </verify>
  <acceptance_criteria>
    - `ls tests/test_audio.py tests/test_tuning_migration.py` lists both files
    - `grep -v '^#' tests/test_audio.py | grep -c '^def test_'` returns 3
    - `grep -c "EXPECTED_" tests/test_tuning_migration.py` returns at least 6 matches (one per migrated key)
    - `grep "tuning._flat_index" tests/test_tuning_migration.py` returns a match
    - `grep "POGO_INITIAL_DY" tests/test_tuning_migration.py` returns a match (anti-migration assertion present)
    - `grep "audio.SFX_DRILL_ENEMY_HIT" tests/test_audio.py` returns a match
    - `pytest tests/test_audio.py tests/test_tuning_migration.py -v --co 2>&amp;1 | grep -E "error|Error"` returns no matches
    - Either tests are SKIPPED (importorskip path) OR they FAIL — both are acceptable RED states.
  </acceptance_criteria>
  <done>Both test files exist; tests collect without errors; importorskip guards keep RED state from breaking pytest; baseline values are named constants (no magic numbers).</done>
</task>

</tasks>

<verification>
- pytest collection runs cleanly (no ImportError, no SyntaxError) on the entire suite after Task 1+2+3.
- All Phase 32 fusion regression tests still pass:
  - `pytest tests/test_drill_dive_parity.py tests/test_pogo.py tests/test_fusion_fsm.py -x` is GREEN (no Phase 33 changes broke Phase 32 invariants).
- 4 new test files all collect and contain the expected number of test functions:
  - test_destructive_drill.py: 4 tests
  - test_daze_shot.py: 2 tests
  - test_audio.py: 3 tests
  - test_tuning_migration.py: parametrized 6-case + 3 standalone = 9 collected (or close)
- conftest.py extension verified: `python -c "import pyxel; pyxel.sounds[0].set('a','b','c','d',1); pyxel.play(-1, 0)"` does not raise (Open Q #4 closure).
</verification>

<success_criteria>
- All Wave 0 test scaffolding files exist on disk in `tests/`
- Tests are SKIP-marked or importorskip-guarded so pytest collection passes
- conftest.py mocks `pyxel.sounds[N].set(...)` and `pyxel.play(...)`
- FUSION-DESIGN.md SHA gate verified: `locked_commit: ce5bddbd9c03ac76271f17290633da2b2e492c51`
- Phase 32 regression suite stays green
- Use-site-read invariants encoded as RED tests (will go GREEN after Wave 1 ships)
</success_criteria>

<output>
After completion, create `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-01-SUMMARY.md` per @$HOME/.claude/get-shit-done/templates/summary.md.
</output>
