import pyxel
from src.core import tuning
from src.core.sprite_utils import draw_sprite

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


class ChargeProjectile:
    """Charge shot projectile -- slime IS the projectile (D-16, D-17).
    On impact, slime teleports to impact point and resumes solo mode."""

    def __init__(self, x, y, dx, dy, level_map, slime):
        self.x = x
        self.y = y
        self.dx = dx * tuning.CHARGE_SHOT_SPEED
        self.dy = dy * tuning.CHARGE_SHOT_SPEED
        self.w = tuning.CHARGE_SHOT_SIZE
        self.h = tuning.CHARGE_SHOT_SIZE
        self.level_map = level_map
        self.slime = slime  # Reference to slime for teleport on impact
        self.is_active = True
        self.gravity = 0.0125  # Much less arc than normal spit -- fast and flat
        self.grace_timer = 6
        self.damage = tuning.CHARGE_SHOT_DAMAGE

    def update(self, cam_x, cam_y):
        if not self.is_active:
            return self._on_impact()

        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity

        if self.grace_timer > 0:
            self.grace_timer -= 1
        else:
            if self.level_map.check_collision(self.x, self.y, self.w, self.h):
                self.is_active = False
                return self._on_impact()

        # Screen boundary check
        if (self.x < cam_x - tuning.CULL_MARGIN or self.x > cam_x + tuning.VIEWPORT_W + tuning.CULL_MARGIN or
            self.y < cam_y - tuning.CULL_MARGIN or self.y > cam_y + tuning.VIEWPORT_H + tuning.CULL_MARGIN):
            self.is_active = False

        return None

    def _on_impact(self):
        """Create juice stain at impact point."""
        from src.entities.stain import JuiceStain
        return JuiceStain(self.x, self.y)

    def draw(self):
        if not self.is_active:
            return
        # Charge shot: use slime's 3rd frame (fused/drill sprite) at u=32, v=16
        facing_right = self.dx >= 0
        draw_sprite(self.x, self.y, self.w, self.h, 1, 32, 16,
                    tuning.SPRITE_SIZE, tuning.SPRITE_SIZE, facing_right)

