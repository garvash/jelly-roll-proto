"""Map-linked entities: Doors, Switches, etc."""
import pyxel


class Door:
    """A door entity that triggers room transitions when opened and touched.

    Doors start closed and can be opened by:
    - Player Kick (melee)
    - Slime Spit (projectile hit)

    Once open, colliding with the door triggers a WorldManager transition.
    """

    def __init__(self, x, y, target_level_id=None, direction="right"):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 24  # Doors are 1 tile wide, 3 tiles tall
        self.is_open = False
        self.target_level_id = target_level_id
        self.direction = direction  # "left", "right", "up", "down"
        self.open_timer = 0  # Animation timer

    def open(self):
        """Open the door (triggered by kick or projectile)."""
        if not self.is_open:
            self.is_open = True
            self.open_timer = 30  # Brief visual feedback

    def close(self):
        """Close the door (e.g., entrance door after player passes through)."""
        self.is_open = False
        self.open_timer = 0

    def update(self):
        """Update door animation state."""
        if self.open_timer > 0:
            self.open_timer -= 1

    def check_collision(self, x, y, w, h):
        """Returns True if the AABB overlaps this door."""
        return (x < self.x + self.w and x + w > self.x and
                y < self.y + self.h and y + h > self.y)

    def check_kick_hit(self, kick_x, kick_y, kick_w=8, kick_h=8):
        """Check if a kick hitbox hits this door."""
        return self.check_collision(kick_x, kick_y, kick_w, kick_h)

    def check_projectile_hit(self, proj_x, proj_y, proj_w, proj_h):
        """Check if a projectile hits this door."""
        return self.check_collision(proj_x, proj_y, proj_w, proj_h)

    def draw(self):
        """Draw the door. Closed doors are solid, open doors are transparent."""
        if self.is_open:
            # Open door: outline only
            pyxel.rectb(self.x, self.y, self.w, self.h, 6)
            # Indicate passage direction with a small arrow
            cx = self.x + self.w // 2
            cy = self.y + self.h // 2
            if self.direction == "right":
                pyxel.line(cx - 1, cy, cx + 2, cy, 6)
            elif self.direction == "left":
                pyxel.line(cx + 1, cy, cx - 2, cy, 6)
            elif self.direction == "up":
                pyxel.line(cx, cy + 1, cx, cy - 2, 6)
            elif self.direction == "down":
                pyxel.line(cx, cy - 1, cx, cy + 2, 6)
        else:
            # Closed door: solid block with a keyhole-like marking
            pyxel.rect(self.x, self.y, self.w, self.h, 4)
            pyxel.rectb(self.x, self.y, self.w, self.h, 9)
            # Keyhole (centered vertically in 24px tall door)
            ky = self.y + self.h // 2 - 1
            pyxel.pset(self.x + 3, ky, 0)
            pyxel.pset(self.x + 4, ky, 0)
            pyxel.pset(self.x + 3, ky + 1, 0)
            pyxel.pset(self.x + 4, ky + 1, 0)
