import pyxel
from collections import deque
import src.core.debug as debug
from src.core.constants import (
    SLIME_FOLLOW_DELAY,
    SLIME_MAX_DIST,
    SLIME_REFORM_DIST,
    SLIME_LERP_FACTOR,
    JUICE_MAX,
    JUICE_REGEN_RATE,
    JUICE_MIN_SCALE,
    SLIME_SPIT_COST,
    RECALL_SPEED,
    RECALL_OVERLAP_DIST,
    SLIME_DISSIPATE_COOLDOWN,
    RECALL_TRAIL_COLOR,
    HOLD_TAP_THRESHOLD,
    TILE_SIZE,
    SPRITE_SIZE,
)
from src.core.sprite_utils import draw_sprite

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

        # Fusion system state (D-01 through D-05)
        self.is_recalling = False       # True when zipping toward player
        self.is_dissipated = False      # True during burnout cooldown (D-05)
        self.dissipate_timer = 0        # Frames remaining before reform
        self.recall_trail = []          # List of (x, y) for visual trail

        # Charge shot windup absorption (gap fix)
        self.is_being_absorbed = False  # True during CHARGING_SHOT windup

        # Directional hold state (ABL-03)
        self.hold_x = None              # Target x for directional hold
        self.hold_y = None              # Target y for directional hold
        self.is_holding_position = False # True when slime is in hold position

        # Physics constants (matching heroine but tuned for companion feel)
        self.accel = 0.05
        self.friction = 0.0375
        self.max_speed = 1.5
        self.gravity = 0.05
        self.jump_force = -1.75

    def recall(self, player_x, player_y):
        """Start recalling slime toward player (D-25). Called when Z is held unfused."""
        if self.is_dissipated:
            return  # Can't recall dissipated slime
        self.is_recalling = True
        self.is_punted = False  # Override punt state
        self.is_holding_position = False  # Cancel hold
        self.history.clear()

    def update_recall(self, player_x, player_y):
        """Move slime toward player during recall. Returns True when overlapping."""
        if not self.is_recalling:
            return False
        dx = player_x - self.x
        dy = player_y - self.y
        dist = (dx**2 + dy**2) ** 0.5
        if dist <= RECALL_OVERLAP_DIST:
            self.x = player_x
            self.y = player_y
            self.is_recalling = False
            self.recall_trail.clear()
            return True  # Arrived
        # Move toward player at RECALL_SPEED
        nx = dx / dist
        ny = dy / dist
        self.x += nx * RECALL_SPEED
        self.y += ny * RECALL_SPEED
        # Trail for visual
        self.recall_trail.append((self.x, self.y))
        RECALL_TRAIL_MAX_LENGTH = 6
        if len(self.recall_trail) > RECALL_TRAIL_MAX_LENGTH:
            self.recall_trail.pop(0)
        return False

    def dissipate(self):
        """Slime burns out from juice empty while fused (D-05). SF6 burnout."""
        self.is_dissipated = True
        self.dissipate_timer = SLIME_DISSIPATE_COOLDOWN
        self.is_fused = False
        self.is_recalling = False
        self.is_being_absorbed = False
        self.recall_trail.clear()

    def update_dissipation(self, player_x, player_y, player_facing_right, level_map):
        """Tick dissipation timer. Returns True when reform happens."""
        if not self.is_dissipated:
            return False
        self.dissipate_timer -= 1
        if self.dissipate_timer <= 0:
            self.is_dissipated = False
            self.juice = self.max_juice  # Reform at full juice (D-05)
            self.reform(player_x, player_y, player_facing_right, level_map)
            return True
        return False

    def reposition(self, direction, player_x, player_y, level_map):
        """Reposition slime in tapped direction without disabling follow (UAT gap fix).
        Tap reposition without disabling follow (UAT gap fix)."""
        step = TILE_SIZE if direction > 0 else -TILE_SIZE
        HOLD_SCAN_RANGE = 4
        for i in range(HOLD_SCAN_RANGE):
            candidate_x = player_x + step * (i + 1)
            candidate_y = player_y
            if not level_map.check_collision(candidate_x, candidate_y, self.w, self.h):
                GROUND_SCAN_RANGE = 8
                for dy_check in range(GROUND_SCAN_RANGE):
                    ground_y = candidate_y + dy_check * TILE_SIZE
                    if level_map.check_collision(candidate_x, ground_y + self.h, self.w, 1):
                        self.x = candidate_x
                        self.y = ground_y
                        self.is_punted = False
                        self.history.clear()
                        self.dx = 0
                        self.dy = 0
                        return
                # No ground found, just place at candidate
                self.x = candidate_x
                self.y = candidate_y
                self.is_punted = False
                self.history.clear()
                self.dx = 0
                self.dy = 0
                return
        # Fallback: place next to player
        self.x = player_x + (SLIME_REFORM_DIST if direction > 0 else -SLIME_REFORM_DIST)
        self.y = player_y
        self.is_punted = False
        self.history.clear()
        self.dx = 0
        self.dy = 0

    def update(self, player_x, player_y, player_facing_right, level_map, is_fused=False):
        self.is_fused = is_fused
        self.facing_right = player_facing_right

        # Handle dissipation (slime is gone, ticking down to reform)
        if self.is_dissipated:
            self.update_dissipation(player_x, player_y, player_facing_right, level_map)
            return

        # Handle recall (zipping toward player)
        if self.is_recalling:
            self.update_recall(player_x, player_y)
            return

        if self.is_fused:
            # Snap to player center (fused = merged, not below)
            self.x = player_x
            self.y = player_y
            self.dx = 0
            self.dy = 0
            self.target_x = self.x
            self.target_y = self.y
            self.history.clear()
            self.is_punted = False
            return

        # Passive regeneration
        self.juice = min(self.max_juice, self.juice + JUICE_REGEN_RATE)

        # If holding position, don't follow player (ABL-03, D-21)
        if self.is_holding_position:
            # Still apply gravity and collision for the hold position
            self.dy = min(2.0, self.dy + self.gravity)
            self.move_and_collide(level_map)
            self.is_grounded = level_map.check_collision(self.x, self.y + 1, self.w, self.h)
            # Reform if too far from player
            dist_sq = (self.x - player_x)**2 + (self.y - player_y)**2
            if dist_sq > SLIME_MAX_DIST**2:
                self.is_holding_position = False
                self.reform(player_x, player_y, player_facing_right, level_map)
            return

        if self.is_punted:
            # Gravity and Friction for punted state (Full physics)
            self.dy = min(2.0, self.dy + self.gravity)
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
        self.history.append((player_x, player_y))

        if len(self.history) >= SLIME_FOLLOW_DELAY:
            self.target_x, self.target_y = self.history[0]

        self.dx = self.target_x - self.x
        self.dy = self.target_y - self.y

        # Clamp velocity to avoid teleporting if player moves very fast,
        # but keep it high enough to feel perfectly responsive.
        # 4.0 is faster than player's max speed (2.5)
        MAX_SHADOW_SPEED = 4.0
        self.dx = max(-MAX_SHADOW_SPEED, min(self.dx, MAX_SHADOW_SPEED))
        self.dy = max(-MAX_SHADOW_SPEED, min(self.dy, MAX_SHADOW_SPEED))

        # Follow mode: direct interpolation then push out of solids.
        # No 1px grounding lookahead — that causes oscillation when the
        # target sits on a tile boundary.
        self.x += self.dx
        self.y += self.dy
        if level_map.check_collision(self.x, self.y, self.w, self.h):
            # Snap feet to top of the solid tile below
            self.y = int((self.y + self.h) // TILE_SIZE) * TILE_SIZE - self.h

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
                self.x = (int((self.x + self.w - 1) // TILE_SIZE)) * TILE_SIZE - self.w
            elif self.dx < 0:
                self.x = (int(self.x // TILE_SIZE) + 1) * TILE_SIZE
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
                target_row = int((self.y + self.h) // TILE_SIZE)
                self.y = target_row * TILE_SIZE - self.h
                self.is_grounded = True
                self.dy = 0
            elif self.dy < 0:
                # Snap to ceiling
                self.y = (int(self.y // TILE_SIZE) + 1) * TILE_SIZE
                self.dy = 0
        else:
            self.is_grounded = False

    def refill(self, amount):
        self.juice = min(self.max_juice, self.juice + amount)

    def consume(self, amount):
        if debug.god_infinite_juice:
            return
        self.juice = max(0.0, self.juice - amount)

    def spit(self, dx, dy, level_map):
        if self.juice >= SLIME_SPIT_COST:
            self.consume(SLIME_SPIT_COST)
            from src.entities.projectile import Projectile
            # Spawn at slime's center (8x8 collision box)
            return Projectile(self.x + self.w // 2 - 2, self.y, dx, dy, level_map)
        return None

    def reform(self, player_x, player_y, player_facing_right, level_map=None):
        # Clear absorption state on reform
        self.is_being_absorbed = False
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
        self.is_holding_position = False

    @property
    def scale(self):
        # Scale between JUICE_MIN_SCALE and 1.0
        return JUICE_MIN_SCALE + (1.0 - JUICE_MIN_SCALE) * (self.juice / self.max_juice)

    def draw(self):
        if self.is_dissipated:
            # Don't draw slime while dissipated
            return

        # Draw recall trail (D-25)
        if self.is_recalling:
            for i, (tx, ty) in enumerate(self.recall_trail):
                pyxel.pset(int(tx + 4), int(ty + 4), RECALL_TRAIL_COLOR)

        if self.is_being_absorbed:
            # Pulsing shrink effect: slime rapidly scales down toward player
            pulse = (pyxel.frame_count % 8) / 8.0  # 0.0 to 0.875
            s = max(0.25, self.scale * (1.0 - pulse * 0.5))
            draw_sprite(self.x, self.y, self.w, self.h, 1, 0, 16,
                        SPRITE_SIZE, SPRITE_SIZE, self.facing_right, colkey=0, scale=s)
            return

        if self.is_fused:
            # Fused sprite is frame 2 (u=32) at y=16 in bank 1
            draw_sprite(self.x, self.y, self.w, self.h, 1, 32, 16,
                        SPRITE_SIZE, SPRITE_SIZE, self.facing_right)
            return

        # Regular slime sprite at y=16 in bank 1 with 2-frame animation
        u_offset = (pyxel.frame_count // 16 % 2) * 16
        s = self.scale
        # X: center anchor (no drift when shrinking), Y: bottom anchor (feet on ground)
        scaled_w = SPRITE_SIZE * s
        scaled_h = SPRITE_SIZE * s
        draw_x = round(self.x + self.w / 2 - scaled_w / 2)
        draw_y = round(self.y + self.h - scaled_h)
        w = SPRITE_SIZE if self.facing_right else -SPRITE_SIZE
        pyxel.blt(draw_x, draw_y, 1, u_offset, 16, w, SPRITE_SIZE, 0, scale=s)
