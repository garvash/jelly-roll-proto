import pyxel
from collections import deque
from src.core.constants import (
    SLIME_FOLLOW_DELAY, 
    SLIME_MAX_DIST, 
    SLIME_REFORM_DIST, 
    SLIME_LERP_FACTOR,
    JUICE_MAX,
    JUICE_REGEN_RATE,
    JUICE_MIN_SCALE,
    SLIME_SPIT_COST
)

class Slime:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8
        self.dx = 0
        self.dy = 0
        self.is_grounded = False
        self.target_x = x
        self.target_y = y
        # History queue to store (x, y) tuples
        self.history = deque(maxlen=SLIME_FOLLOW_DELAY + 1)
        self.facing_right = True
        self.max_juice = JUICE_MAX
        self.juice = JUICE_MAX
        self.is_fused = False
        self.is_punted = False
        
        # Physics constants (matching heroine but tuned for companion feel)
        self.accel = 0.2
        self.friction = 0.15
        self.max_speed = 3.0
        self.gravity = 0.2
        self.jump_force = -3.5

    def update(self, player_x, player_y, player_facing_right, level_map, is_fused=False):
        self.is_fused = is_fused
        self.facing_right = player_facing_right
        
        if self.is_fused:
            # Snap to player as a drill attachment (below player)
            self.x = player_x
            self.y = player_y + 4
            self.dx = 0
            self.dy = 0
            self.target_x = self.x
            self.target_y = self.y
            self.history.clear()
            self.is_punted = False
            return

        # Passive regeneration
        self.juice = min(self.max_juice, self.juice + JUICE_REGEN_RATE)

        if self.is_punted:
            # Gravity and Friction for punted state (Full physics)
            self.dy = min(4.0, self.dy + self.gravity)
            if self.is_grounded:
                self.dx *= 0.9 # Friction
                if abs(self.dx) < 0.5:
                    self.is_punted = False
            
            self.move_and_collide(level_map)
            
            # Reform logic (Distance check)
            dist_sq = (self.x - player_x)**2 + (self.y - player_y)**2
            if dist_sq > SLIME_MAX_DIST**2:
                self.reform(player_x, player_y, player_facing_right, level_map)
            return

        # --- Standard Path-Based Movement (Gradius Option Style) ---
        # Store the player's ACTUAL position in history to follow their exact path
        self.history.append((player_x, player_y))

        # Get target from history if delay has passed
        if len(self.history) >= SLIME_FOLLOW_DELAY:
            self.target_x, self.target_y = self.history[0]

        # Calculate delta to reach target
        # No acceleration/friction for the "shadow" feel
        self.dx = self.target_x - self.x
        self.dy = self.target_y - self.y
        
        # Clamp velocity to avoid teleporting if player moves very fast, 
        # but keep it high enough to feel perfectly responsive.
        # 4.0 is faster than player's max speed (2.5)
        MAX_SHADOW_SPEED = 4.0
        self.dx = max(-MAX_SHADOW_SPEED, min(self.dx, MAX_SHADOW_SPEED))
        self.dy = max(-MAX_SHADOW_SPEED, min(self.dy, MAX_SHADOW_SPEED))

        self.move_and_collide(level_map)

        # Update grounded state for punt/other logic
        self.is_grounded = level_map.check_collision(self.x, self.y + 1, self.w, self.h)

        # Reform logic (Distance check)
        dist_sq = (self.x - player_x)**2 + (self.y - player_y)**2
        if dist_sq > SLIME_MAX_DIST**2:
            self.reform(player_x, player_y, player_facing_right, level_map)

    def punt(self, dx, dy):
        self.dx = dx
        self.dy = dy
        self.is_punted = True
        self.history.clear()

    def move_and_collide(self, level_map):
        # Move horizontal
        self.x += self.dx
        if level_map.check_collision(self.x, self.y, self.w, self.h):
            if self.dx > 0:
                self.x = (int((self.x + self.w - 1) // 8)) * 8 - self.w
            elif self.dx < 0:
                self.x = (int(self.x // 8) + 1) * 8
            self.dx = 0

        # Move vertical
        self.y += self.dy
        collision = level_map.check_collision(self.x, self.y, self.w, self.h)
        
        # Grounding check (look 1px down)
        if not collision and self.dy >= 0:
            if level_map.check_collision(self.x, self.y + 1, self.w, self.h):
                collision = True

        if collision:
            if self.dy >= 0:
                # Snap to floor
                target_row = int((self.y + self.h) // 8)
                self.y = target_row * 8 - self.h
                self.is_grounded = True
                self.dy = 0
            elif self.dy < 0:
                # Snap to ceiling
                self.y = (int(self.y // 8) + 1) * 8
                self.dy = 0
        else:
            self.is_grounded = False

    def refill(self, amount):
        self.juice = min(self.max_juice, self.juice + amount)

    def consume(self, amount):
        self.juice = max(0.0, self.juice - amount)

    def spit(self, dx, dy, level_map):
        if self.juice >= SLIME_SPIT_COST:
            self.consume(SLIME_SPIT_COST)
            from src.entities.projectile import Projectile
            # Spawn at slime's center
            return Projectile(self.x + 2, self.y + 2, dx, dy, level_map)
        return None

    def reform(self, player_x, player_y, player_facing_right, level_map=None):
        # Snap slime behind player and clear history
        offset_x = -SLIME_REFORM_DIST if player_facing_right else SLIME_REFORM_DIST
        new_x = player_x + offset_x
        new_y = player_y
        
        # Safety check: if teleport destination is solid, snap to player exactly
        if level_map and level_map.check_collision(new_x, new_y, self.w, self.h):
            new_x = player_x
            new_y = player_y

        self.x = new_x
        self.y = new_y
        self.dx = 0
        self.dy = 0
        self.target_x = self.x
        self.target_y = self.y
        self.history.clear()

    @property
    def scale(self):
        # Scale between JUICE_MIN_SCALE and 1.0
        return JUICE_MIN_SCALE + (1.0 - JUICE_MIN_SCALE) * (self.juice / self.max_juice)

    def draw(self):
        if self.is_fused:
            # Draw drill sprite (16, 8) from image 1
            w = 8 if self.facing_right else -8
            pyxel.blt(self.x, self.y, 1, 16, 8, w, 8, 0)
            return

        # Regular slime sprite (0, 8) from image 1 with 2-frame animation
        u_offset = (pyxel.frame_count // 8 % 2) * 8
        s = self.scale
        size = 8 * s
        offset = (8 - size) / 2
        w = 8 if self.facing_right else -8
        pyxel.blt(self.x + offset, self.y + offset, 1, u_offset, 8, w, 8, 0, scale=s)

