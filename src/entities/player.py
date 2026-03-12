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
        self.state = "IDLE" # IDLE, RUNNING, JUMPING, FALLING, WALL_SLIDING

        # Forgiving mechanics timers
        self.coyote_timer = 0
        self.jump_buffer_timer = 0
        self.is_wall_sliding = False
        self.wall_dir = 0 # -1 for left wall, 1 for right wall

    def update(self):
        self.update_timers()
        self.handle_input()
        self.apply_physics()
        self.move_and_collide()
        self.update_state()

    def update_timers(self):
        if self.is_grounded:
            self.coyote_timer = COYOTE_TIME
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1

        if pyxel.btnp(pyxel.KEY_SPACE):
            self.jump_buffer_timer = JUMP_BUFFER
        elif self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1

    def handle_input(self):
        # Horizontal Movement
        target_dx = 0
        move_input = 0
        if pyxel.btn(pyxel.KEY_LEFT):
            target_dx -= WALK_ACCEL
            move_input = -1
        if pyxel.btn(pyxel.KEY_RIGHT):
            target_dx += WALK_ACCEL
            move_input = 1

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

        # Check for walls
        on_left_wall = self.level_map.check_collision(self.x - 1, self.y, 1, self.h)
        on_right_wall = self.level_map.check_collision(self.x + self.w, self.y, 1, self.h)
        
        self.is_wall_sliding = False
        self.wall_dir = 0
        if not self.is_grounded and self.dy > 0:
            if on_left_wall and move_input == -1:
                self.is_wall_sliding = True
                self.wall_dir = -1
            elif on_right_wall and move_input == 1:
                self.is_wall_sliding = True
                self.wall_dir = 1

        # Jump
        if self.jump_buffer_timer > 0:
            if self.coyote_timer > 0:
                self.dy = JUMP_FORCE
                self.is_grounded = False
                self.coyote_timer = 0
                self.jump_buffer_timer = 0
            elif self.is_wall_sliding or (on_left_wall and not self.is_grounded) or (on_right_wall and not self.is_grounded):
                # Wall Jump
                jump_dir = -1 if (on_right_wall) else 1
                self.dx = jump_dir * WALL_JUMP_X_IMPULSE
                self.dy = WALL_JUMP_Y_FORCE
                self.jump_buffer_timer = 0
                self.is_wall_sliding = False

        # Variable Jump Height (cut velocity on release)
        if pyxel.btnr(pyxel.KEY_SPACE) and self.dy < 0:
            self.dy *= VARIABLE_JUMP_REDUCTION

    def apply_physics(self):
        # Weighted Gravity (increased gravity when falling)
        curr_gravity = GRAVITY
        if self.is_wall_sliding:
            # Wall slide friction (reduced gravity)
            self.dy = min(self.dy + curr_gravity * WALL_SLIDE_FRICTION, MAX_FALL_SPEED * 0.5)
        else:
            if self.dy > 0:
                curr_gravity *= FALLING_GRAVITY_MULTIPLIER
            self.dy += curr_gravity
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
        if self.is_wall_sliding:
            self.state = "WALL_SLIDING"
        elif not self.is_grounded:
            if self.dy < 0:
                self.state = "JUMPING"
            else:
                self.state = "FALLING"
        elif self.dx != 0:
            self.state = "RUNNING"
        else:
            self.state = "IDLE"

    def draw(self):
        # Placeholder player draw (a rectangle for now)
        # In final assets, this would be a blt call
        pyxel.rect(self.x, self.y, self.w, self.h, 11)
