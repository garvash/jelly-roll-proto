import pyxel
from src.core.constants import *

class Player:
    def __init__(self, x, y, level_map):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8
        self.dx = 0
        self.dy = 0
        self.level_map = level_map
        self.is_grounded = False
        self.state = "IDLE" # IDLE, RUNNING

    def update(self):
        self.handle_input()
        self.apply_physics()
        self.move_and_collide()
        self.update_state()

    def handle_input(self):
        target_dx = 0
        if pyxel.btn(pyxel.KEY_LEFT):
            target_dx -= WALK_ACCEL
        if pyxel.btn(pyxel.KEY_RIGHT):
            target_dx += WALK_ACCEL

        if target_dx != 0:
            self.dx += target_dx
        else:
            # Friction
            if self.dx > 0:
                self.dx = max(0, self.dx - WALK_FRICTION)
            elif self.dx < 0:
                self.dx = min(0, self.dx + WALK_FRICTION)
        
        # Clamp horizontal speed
        self.dx = max(-MAX_WALK_SPEED, min(self.dx, MAX_WALK_SPEED))

    def apply_physics(self):
        # Gravity
        self.dy += GRAVITY
        if self.dy > MAX_FALL_SPEED:
            self.dy = MAX_FALL_SPEED

    def move_and_collide(self):
        # Separate horizontal and vertical movement for simple collision
        # Move horizontal
        self.x += self.dx
        if self.level_map.check_collision(self.x, self.y, self.w, self.h):
            if self.dx > 0:
                self.x = (int((self.x + self.w - 1) // TILE_SIZE)) * TILE_SIZE - self.w
            elif self.dx < 0:
                self.x = (int(self.x // TILE_SIZE) + 1) * TILE_SIZE
            self.dx = 0

        # Move vertical
        self.y += self.dy
        if self.level_map.check_collision(self.x, self.y, self.w, self.h):
            if self.dy > 0:
                self.y = (int((self.y + self.h - 1) // TILE_SIZE)) * TILE_SIZE - self.h
                self.is_grounded = True
            elif self.dy < 0:
                self.y = (int(self.y // TILE_SIZE) + 1) * TILE_SIZE
            self.dy = 0
        else:
            self.is_grounded = False

    def update_state(self):
        if self.dx != 0:
            self.state = "RUNNING"
        else:
            self.state = "IDLE"

    def draw(self):
        # Placeholder player draw (a rectangle for now)
        # In final assets, this would be a blt call
        pyxel.rect(self.x, self.y, self.w, self.h, 11)
