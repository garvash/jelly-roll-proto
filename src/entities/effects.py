"""Phase 31 ANIM-06 sprite-backed particles from bank 2.

D-15: Bank 2 is the dedicated FX image bank; assets/sprites/particles.png
loaded via SPRITE_MANIFEST. D-16: inherited explosion sprite (bank 1 y=96)
retired; Effect class stripped to a no-op shell for legacy-call-site safety.
D-17: all particles sprite-backed (no more pyxel.pset).
D-07b: BlobGrowth uses tier-2 AnimPlayer wrapping for multi-frame growth.
"""
from src.core import tuning
from src.core.sprite_utils import draw_sprite
from src.anim.anim_clip import AnimClip
from src.anim.anim_player import AnimPlayer


# --- Particle render constants (no magic numbers per MEMORY) -----------------
PARTICLE_SIZE = 4            # 4x4 pixel render size on-screen
PARTICLE_GRAVITY = 0.025     # inherited from legacy Particle


class Effect:
    """Phase 31 D-16: retired to a no-op shell.

    Legacy call sites constructing Effect(x, y) are migrated to
    Game.spawn_particle_burst(x, y, type="block_break"). This shell keeps
    Python import paths alive during migration; instances immediately
    deactivate and draw nothing. Scheduled for deletion in a future cleanup.
    """
    def __init__(self, x, y, effect_type="EXPLOSION"):
        self.x = x
        self.y = y
        self.effect_type = effect_type
        self.is_active = False  # D-16: always inactive

    def update(self):
        self.is_active = False

    def draw(self, cam_x, cam_y):
        return


class Particle:
    """Phase 31 D-17 sprite-backed particle.

    Keyword-only constructor (dx, dy, life, bank_u, bank_v). The legacy
    (x, y, color) signature is retired; all callers must migrate.
    """
    def __init__(self, x, y, *, dx, dy, life, bank_u, bank_v):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.life = life
        self.bank_u = bank_u
        self.bank_v = bank_v
        self.is_active = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += PARTICLE_GRAVITY
        self.life -= 1
        if self.life <= 0:
            self.is_active = False

    def draw(self, cam_x, cam_y):
        if not self.is_active:
            return
        # Room boundary check -- don't draw off-viewport particles.
        if (self.x < cam_x or self.x > cam_x + tuning.VIEWPORT_W or
            self.y < cam_y or self.y > cam_y + tuning.VIEWPORT_H):
            return
        # D-15/D-17: bank 2 sprite-backed draw (replaces pyxel.pset).
        draw_sprite(
            self.x, self.y,
            PARTICLE_SIZE, PARTICLE_SIZE,       # coll_w, coll_h
            2,                                   # bank -- D-15
            self.bank_u, self.bank_v,            # u, v into bank 2
            PARTICLE_SIZE, PARTICLE_SIZE,        # visual_w, visual_h
            True,                                # facing_right (no flip)
        )


class BlobGrowth:
    """Phase 31 D-07b sprite-backed blob that grows from a point.

    Uses AnimPlayer(clip) tier-2 wrapping (Open Question 3 hybrid): blob
    growth IS multi-frame progression and AnimPlayer already owns that
    logic. Single-sprite Particle stays custom; this class reuses the
    existing tick/current_u primitives.
    """

    def __init__(self, x, y, frames=4):
        # main.py imports are deferred so importing effects.py from a test
        # does not pull main.py at module load.
        from main import (
            BLOB_GROWTH_FRAME_0_U, BLOB_GROWTH_FRAME_1_U,
            BLOB_GROWTH_FRAME_2_U, BLOB_GROWTH_FRAME_3_U,
            BLOB_GROWTH_DURATION_PER_FRAME,
        )
        self.x = x
        self.y = y
        # Build a per-instance non-looping clip; the last frame holds while
        # _ticks_elapsed counts down to deactivation.
        frame_us = [
            BLOB_GROWTH_FRAME_0_U, BLOB_GROWTH_FRAME_1_U,
            BLOB_GROWTH_FRAME_2_U, BLOB_GROWTH_FRAME_3_U,
        ][:frames]
        durations = [BLOB_GROWTH_DURATION_PER_FRAME] * frames
        clip = AnimClip(frames=frame_us, durations=durations, loop=False)
        self._anim_player = AnimPlayer(clip)
        self._ticks_elapsed = 0
        self._total_lifetime_ticks = frames * BLOB_GROWTH_DURATION_PER_FRAME
        self.is_active = True

    def update(self):
        if not self.is_active:
            return
        self._anim_player.tick()
        self._ticks_elapsed += 1
        if self._ticks_elapsed > self._total_lifetime_ticks:
            self.is_active = False

    def current_u(self):
        return self._anim_player.current_u()

    def draw(self, cam_x, cam_y):
        if not self.is_active:
            return
        if (self.x < cam_x or self.x > cam_x + tuning.VIEWPORT_W or
            self.y < cam_y or self.y > cam_y + tuning.VIEWPORT_H):
            return
        from main import BLOB_SIZE, BLOB_GROWTH_V
        draw_sprite(
            self.x - BLOB_SIZE // 2, self.y - BLOB_SIZE // 2,
            BLOB_SIZE, BLOB_SIZE,                # coll_w, coll_h
            2,                                    # bank 2 (D-15)
            self._anim_player.current_u(),       # u advances with frame
            BLOB_GROWTH_V,                        # v (row y=16)
            BLOB_SIZE, BLOB_SIZE,                 # visual_w, visual_h
            True,                                 # facing_right N/A for symmetric blob
        )
