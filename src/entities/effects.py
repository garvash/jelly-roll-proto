import pyxel
import random
from src.core import tuning
from src.core.sprite_utils import draw_sprite

class Effect:
    def __init__(self, x, y, effect_type="EXPLOSION"):
        self.x = x
        self.y = y
        self.effect_type = effect_type
        self.is_active = True
        self.frame = 0
        self.max_frames = 24 # 3 sprites * 8 frames each

    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.is_active = False

    def draw(self, cam_x, cam_y):
        if not self.is_active:
            return
        
        # Room boundary check (128x128 room)
        if (self.x < cam_x or self.x > cam_x + tuning.VIEWPORT_W or
            self.y < cam_y or self.y > cam_y + tuning.VIEWPORT_H):
            return

        if self.effect_type == "EXPLOSION":
            # 3 frames of animation at y=96 in bank 1, 16px stride
            u = (self.frame // 8) * 16
            draw_sprite(self.x, self.y, 16, 16, 1, u, 96,
                        tuning.SPRITE_SIZE, tuning.SPRITE_SIZE, True)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.color = color
        self.life = random.randint(20, 40)
        self.is_active = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.025 # gravity (quartered for 60fps)
        self.life -= 1
        if self.life <= 0:
            self.is_active = False

    def draw(self, cam_x, cam_y):
        if not self.is_active:
            return
            
        # Room boundary check
        if (self.x < cam_x or self.x > cam_x + tuning.VIEWPORT_W or
            self.y < cam_y or self.y > cam_y + tuning.VIEWPORT_H):
            return

        pyxel.pset(self.x, self.y, self.color)
