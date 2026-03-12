import pyxel
from collections import deque
from src.core.constants import (
    SLIME_FOLLOW_DELAY, 
    SLIME_MAX_DIST, 
    SLIME_REFORM_DIST, 
    SLIME_LERP_FACTOR,
    JUICE_MAX,
    JUICE_REGEN_RATE,
    JUICE_MIN_SCALE
)

class Slime:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        # History queue to store (x, y, facing_right) tuples
        self.history = deque(maxlen=SLIME_FOLLOW_DELAY + 1)
        self.facing_right = True
        self.juice = JUICE_MAX
        self.is_fused = False

    def update(self, player_x, player_y, player_facing_right, is_fused=False):
        self.is_fused = is_fused
        if self.is_fused:
            # Snap to player as a drill attachment (below player)
            self.x = player_x
            self.y = player_y + 4
            self.history.clear()
            return

        # Passive regeneration
        self.juice = min(JUICE_MAX, self.juice + JUICE_REGEN_RATE)

        # Determine the target position offset based on player facing direction
        offset_x = -8 if player_facing_right else 8
        target_pos = (player_x + offset_x, player_y)

        # Update history
        self.history.append(target_pos)

        # Get target from history if delay has passed
        if len(self.history) >= SLIME_FOLLOW_DELAY:
            self.target_x, self.target_y = self.history[0]

        # Lerp towards target
        self.x += (self.target_x - self.x) * SLIME_LERP_FACTOR
        self.y += (self.target_y - self.y) * SLIME_LERP_FACTOR

        # Reform logic (Distance check)
        dist_sq = (self.x - player_x)**2 + (self.y - player_y)**2
        if dist_sq > SLIME_MAX_DIST**2:
            self.reform(player_x, player_y, player_facing_right)

    def refill(self, amount):
        self.juice = min(JUICE_MAX, self.juice + amount)

    def consume(self, amount):
        self.juice = max(0.0, self.juice - amount)

    def reform(self, player_x, player_y, player_facing_right):
        # Snap slime behind player and clear history
        offset_x = -SLIME_REFORM_DIST if player_facing_right else SLIME_REFORM_DIST
        self.x = player_x + offset_x
        self.y = player_y
        self.target_x = self.x
        self.target_y = self.y
        self.history.clear()

    @property
    def scale(self):
        # Scale between JUICE_MIN_SCALE and 1.0
        return JUICE_MIN_SCALE + (1.0 - JUICE_MIN_SCALE) * (self.juice / JUICE_MAX)

    def draw(self):
        if self.is_fused:
            # Draw drill sprite (16, 0) - Centered under player
            # Slime is at player_x, player_y + 4
            pyxel.blt(self.x, self.y, 0, 16, 0, 8, 8, 0)
            return

        # Regular slime sprite (8, 0)
        # Using scale parameter in pyxel.blt
        # Offset x, y to center the scaled sprite (assuming original size 8x8)
        s = self.scale
        size = 8 * s
        offset = (8 - size) / 2
        pyxel.blt(self.x + offset, self.y + offset, 0, 8, 0, 8, 8, 0, scale=s)
