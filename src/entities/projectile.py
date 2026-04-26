import pyxel
from src.core import tuning

class Projectile:
    def __init__(self, x, y, dx, dy, level_map, target=None):
        self.x = x
        self.y = y
        self.dx = dx * tuning.PROJECTILE_SPEED
        self.dy = dy * tuning.PROJECTILE_SPEED
        self.w = 4
        self.h = 4
        self.level_map = level_map
        self.is_active = True
        self.grace_timer = 4
        self.gravity = 0.0375  # Parabolic arc (quartered for 60fps)

        if self.level_map.check_collision(self.x, self.y, self.w, self.h):
            self.is_active = False

    def update(self, cam_x, cam_y):
        if not self.is_active:
            from src.entities.stain import JuiceStain
            return JuiceStain(self.x, self.y)

        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity

        if self.grace_timer > 0:
            self.grace_timer -= 1
        else:
            if self.level_map.check_collision(self.x, self.y, self.w, self.h):
                self.is_active = False
                from src.entities.stain import JuiceStain
                return JuiceStain(self.x, self.y)

        if (self.x < cam_x - tuning.CULL_MARGIN or self.x > cam_x + tuning.VIEWPORT_W + tuning.CULL_MARGIN or
            self.y < cam_y - tuning.CULL_MARGIN or self.y > cam_y + tuning.VIEWPORT_H + tuning.CULL_MARGIN):
            self.is_active = False

        return None

    def draw(self):
        if not self.is_active:
            return
        # Spit: 8x8 source sprite drawn at native size (no upscale)
        w = tuning.TILE_SIZE if self.dx >= 0 else -tuning.TILE_SIZE
        pyxel.blt(self.x, self.y, 1, 0, 80, w, tuning.TILE_SIZE, 0)
