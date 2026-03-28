import pyxel
from src.core.constants import PROJECTILE_SPEED, TILE_SIZE, CHARGE_SHOT_SPEED, CHARGE_SHOT_SIZE, CHARGE_SHOT_DAMAGE

class Projectile:
    def __init__(self, x, y, dx, dy, level_map):
        self.x = x
        self.y = y
        self.dx = dx * PROJECTILE_SPEED
        self.dy = dy * PROJECTILE_SPEED
        self.w = 4
        self.h = 4
        self.level_map = level_map
        self.is_active = True
        self.gravity = 0.15 # Arched flight
        self.grace_timer = 2 # frames to ignore wall collision at spawn

        # PHY-03: Immediate collision check for point-blank shots
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
            # Check collision with walls/solid blocks
            if self.level_map.check_collision(self.x, self.y, self.w, self.h):
                self.is_active = False
                from src.entities.stain import JuiceStain
                return JuiceStain(self.x, self.y)

        # Screen boundary check (relative to camera room)
        # 128x128 is the room size
        if (self.x < cam_x - 16 or self.x > cam_x + 144 or 
            self.y < cam_y - 16 or self.y > cam_y + 144):
            self.is_active = False
        
        return None

    def draw(self):
        if not self.is_active:
            return
        # Projectile is at (24, 8) in image 1, 4x4
        # Flip if dx < 0
        w = 4 if self.dx >= 0 else -4
        pyxel.blt(self.x, self.y, 1, 24, 8, w, 4, 0)


class ChargeProjectile:
    """Charge shot projectile -- slime IS the projectile (D-16, D-17).
    On impact, slime teleports to impact point and resumes solo mode."""

    def __init__(self, x, y, dx, dy, level_map, slime):
        self.x = x
        self.y = y
        self.dx = dx * CHARGE_SHOT_SPEED
        self.dy = dy * CHARGE_SHOT_SPEED
        self.w = CHARGE_SHOT_SIZE
        self.h = CHARGE_SHOT_SIZE
        self.level_map = level_map
        self.slime = slime  # Reference to slime for teleport on impact
        self.is_active = True
        self.gravity = 0.05  # Much less arc than normal spit -- fast and flat
        self.grace_timer = 3
        self.damage = CHARGE_SHOT_DAMAGE

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
        if (self.x < cam_x - 16 or self.x > cam_x + 144 or
            self.y < cam_y - 16 or self.y > cam_y + 144):
            self.is_active = False
            self._reposition_slime()

        return None

    def _on_impact(self):
        """Slime teleports to impact point (D-17). Pitfall 6: safety check for solid."""
        self._reposition_slime()
        from src.entities.stain import JuiceStain
        return JuiceStain(self.x, self.y)

    def _reposition_slime(self):
        """Move slime to impact location with safety check (Pitfall 6)."""
        if self.slime:
            # Safety: if impact point is solid, nudge upward to find valid position
            if self.level_map.check_collision(self.x, self.y, self.slime.w, self.slime.h):
                for offset_y in range(0, 32, TILE_SIZE):
                    test_y = self.y - offset_y
                    if not self.level_map.check_collision(self.x, test_y, self.slime.w, self.slime.h):
                        self.slime.x = self.x
                        self.slime.y = test_y
                        break
                # Complete fallback: don't move slime if no valid position found
            else:
                self.slime.x = self.x
                self.slime.y = self.y

            self.slime.is_fused = False
            self.slime.is_punted = False
            self.slime.is_recalling = False
            self.slime.is_holding_position = False
            self.slime.dx = 0
            self.slime.dy = 0
            self.slime.history.clear()

    def draw(self):
        if not self.is_active:
            return
        # Draw as a larger glowing slime projectile
        w = self.w if self.dx >= 0 else -self.w
        # Use slime sprite scaled up -- (0, 8) from image 1
        pyxel.blt(self.x, self.y, 1, 0, 8, w, 8, 0)

