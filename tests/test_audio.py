"""Phase 33 FUS-06 D-12/D-13 — audio module surface tests.

RED until Wave 3 ships src/core/audio.py.

Module surface (D-12, D-13):
- audio.init_sounds() runs without raising and calls pyxel.sounds[N].set
  on slots 0..6 (7 cues per D-13/D-20 — fuse_start, drill_start,
  drill_block_break, drill_enemy_hit, drill_impact, daze_fire, pogo_bounce).
- audio.play_sfx("drill_enemy_hit") routes to pyxel.play(0, SFX_DRILL_ENEMY_HIT).
- audio.play_sfx("not_a_real_cue") returns silently (no raise, no pyxel.play).

The conftest.py mock (Phase 33 Task 1) pre-populates pyxel.sounds as a
64-element MagicMock list and pyxel.play as a MagicMock, so the audio module
can be exercised without a real Pyxel runtime.
"""
import pytest
import pyxel  # provided by conftest mock (Task 1 extended sounds + play)

# Wave 3 ships src/core/audio.py — until then, importorskip keeps collection clean.
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
    """play_sfx('drill_enemy_hit') calls pyxel.play(0, SFX_DRILL_ENEMY_HIT).

    Pyxel `pyxel.play(ch, snd)` requires a non-negative channel index — there
    is no auto-channel sentinel. Phase 33 SFX share channel 0.
    """
    pyxel.play.reset_mock()
    audio.play_sfx("drill_enemy_hit")
    pyxel.play.assert_called_once_with(0, audio.SFX_DRILL_ENEMY_HIT)


def test_play_sfx_unknown_name_silent():
    """Unknown cue name returns silently (no raise, no pyxel.play call)."""
    pyxel.play.reset_mock()
    audio.play_sfx("not_a_real_cue")
    pyxel.play.assert_not_called()
