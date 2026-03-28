import pyxel
import random
from src.core.constants import VIEWPORT_W, VIEWPORT_H

class Effect:
    def __init__(self, x, y, effect_type="EXPLOSION"):
        self.x = x
        self.y = y
        self.effect_type = effect_type
        self.is_active = True
        self.frame = 0
        self.max_frames = 12 # 3 sprites * 4 frames each

    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.is_active = False

    def draw(self, cam_x, cam_y):
        if not self.is_active:
            return
        
        # Room boundary check (128x128 room)
        if (self.x < cam_x or self.x > cam_x + VIEWPORT_W or
            self.y < cam_y or self.y > cam_y + VIEWPORT_H):
            return

        if self.effect_type == "EXPLOSION":
            # 3 frames of animation
            u = (self.frame // 4) * 8
            # In image 1, row 6 (y=48) to avoid tileset overlap
            pyxel.blt(self.x, self.y, 1, u, 48, 8, 8, 0)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.dx = random.uniform(-2, 2)
        self.dy = random.uniform(-2, 2)
        self.color = color
        self.life = random.randint(10, 20)
        self.is_active = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.1 # gravity
        self.life -= 1
        if self.life <= 0:
            self.is_active = False

    def draw(self, cam_x, cam_y):
        if not self.is_active:
            return
            
        # Room boundary check
        if (self.x < cam_x or self.x > cam_x + VIEWPORT_W or
            self.y < cam_y or self.y > cam_y + VIEWPORT_H):
            return

        pyxel.pset(self.x, self.y, self.color)
