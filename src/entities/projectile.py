import pyxel
from src.core.constants import PROJECTILE_SPEED, TILE_SIZE

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

    def update(self, cam_x, cam_y):
        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity

        # Check collision with walls/solid blocks
        if self.level_map.check_collision(self.x, self.y, self.w, self.h):
            self.is_active = False

        # Screen boundary check (relative to camera room)
        # 128x128 is the room size
        if (self.x < cam_x - 16 or self.x > cam_x + 144 or 
            self.y < cam_y - 16 or self.y > cam_y + 144):
            self.is_active = False
    Jonah

    def draw(self):
        if not self.is_active:
            return
        # Projectile is at (48, 0) in image 0, 4x4
        # Flip if dx < 0
        w = 4 if self.dx >= 0 else -4
        pyxel.blt(self.x, self.y, 0, 48, 0, w, 4, 0)

