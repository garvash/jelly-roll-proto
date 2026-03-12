import pyxel
from collections import deque
from src.core.constants import (
    SLIME_FOLLOW_DELAY, 
    SLIME_MAX_DIST, 
    SLIME_REFORM_DIST, 
    SLIME_LERP_FACTOR
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

    def update(self, player_x, player_y, player_facing_right):
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

    def reform(self, player_x, player_y, player_facing_right):
        # Snap slime behind player and clear history
        offset_x = -SLIME_REFORM_DIST if player_facing_right else SLIME_REFORM_DIST
        self.x = player_x + offset_x
        self.y = player_y
        self.target_x = self.x
        self.target_y = self.y
        self.history.clear()

    def draw(self):
        # Temporary 8x8 slime sprite (image 0, 8, 0)
        # Assuming slime is at (8, 0) in assets (Phase 2 context says 8x8 to 2x2 juice later)
        # Using pyxel.blt(x, y, img, u, v, w, h, colkey)
        # Center the slime sprite (assuming 8x8)
        pyxel.blt(self.x, self.y, 0, 8, 0, 8, 8, 0)
