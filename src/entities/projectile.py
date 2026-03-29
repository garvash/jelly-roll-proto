import pyxel
from src.core.constants import PROJECTILE_SPEED, TILE_SIZE, SPRITE_SIZE
from src.core.sprite_utils import draw_sprite

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

    def update(self, cam_x, cam_y):
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
        # Spit sprite at y=80 (projectile row), frame 0 in bank 1
        facing_right = self.dx >= 0
        draw_sprite(self.x, self.y, self.w, self.h, 1, 0, 80,
                    SPRITE_SIZE, SPRITE_SIZE, facing_right)

