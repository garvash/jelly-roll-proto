"""Phase 31 ANIM-06 sprite-backed particles from bank 2.

D-15: Bank 2 is the dedicated FX image bank; assets/sprites/particles.png
loaded via SPRITE_MANIFEST. D-16: inherited explosion sprite (bank 1 y=96)
retired; Effect class stripped to a no-op shell for legacy-call-site safety.
D-17: all particles sprite-backed (no more pyxel.pset).
"""
from src.core import tuning
from src.core.sprite_utils import draw_sprite


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
