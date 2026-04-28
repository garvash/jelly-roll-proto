"""Phase 33 D-12 minimal audio surface.

Defines `pyxel.sounds[N].set()` for the 7 Phase 33 SFX cues + a
`play_sfx(name)` wrapper. Phase 35 inherits and extends with a full
sound channel map + debounce; Phase 33's surface stays bounded.

Channel strategy: `pyxel.play(-1, sound_id)` for auto-channel pickup
(Pyxel idiom; verified via tests/conftest.py mock extension per
Plan 01). Phase 35 will replace channel strategy with per-cue channel
reservation + debounce.

Per project MEMORY (feedback_magic_numbers.md): all numeric literals
become named module-level constants — slot IDs, the auto-channel
sentinel, and (where load-bearing) tone/volume strings.
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

# Name -> slot routing table for play_sfx(name).
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
# Pyxel routes -1 to the next available channel automatically.
_AUTO_CHANNEL = -1


def init_sounds() -> None:
    """Define all SFX slots. Called once from Game.__init__.

    Per Pyxel API (verified github.com/kitao/pyxel/blob/main/python/pyxel/examples/04_sound_api.py):
        pyxel.sounds[N].set(notes, tones, volumes, effects, speed)
        notes:   [CDEFGAB] + [#-] + [0-4] for pitch, R for rest. Lowercase.
        tones:   [TSPN] (Triangle, Square, Pulse, Noise). Lowercase. Single
                 char repeats; longer string is per-note.
        volumes: [0-7]. Single char repeats; longer string is per-note.
        effects: [NSVF] (None, Slide, Vibrato, FadeOut). Lowercase. Per-note.
        speed:   integer; lower = faster.

    Cue choices below are feel sketches — D-13 (drill identity) + D-15
    (palette mapping) + D-20 (pogo confirm-only). Per CONTEXT § Claude's
    Discretion these can be tweaked via panel iteration in Plan 06.
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
