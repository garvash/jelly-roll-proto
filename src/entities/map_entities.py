"""Map-linked entities: Doors, Switches, etc."""
import pyxel


class Door:
    """A door entity that triggers room transitions when opened and touched.

    Doors start closed and can be opened by:
    - Player Kick (melee)
    - Slime Spit (projectile hit)

    Once open, colliding with the door triggers a WorldManager transition.
    """

    def __init__(self, x, y, target_level_id=None, direction="right", action=None, event_id=None, width=None, height=None):
        self.x = x
        self.y = y
        # Use LDtk dimensions when provided, otherwise fall back to defaults
        if width is not None and height is not None:
            self.w = width
            self.h = height
        elif direction in ("left", "right"):
            self.w = 16
            self.h = 32  # 1x2 tiles
        else:
            self.w = 32  # 2x1 tiles
            self.h = 16
        self.is_open = False
        self.target_level_id = target_level_id
        self.direction = direction  # "left", "right", "up", "down"
        self.action = action  # Ability required to open: "spit", "kick", "event", etc.
        self.event_id = event_id  # For action="event": the event_flags key to check
        self.open_timer = 0  # Animation timer

    def open(self):
        """Open the door (triggered by kick or projectile)."""
        if not self.is_open:
            self.is_open = True
            self.open_timer = 60  # Brief visual feedback

    def close(self):
        """Close the door (e.g., entrance door after player passes through)."""
        self.is_open = False
        self.open_timer = 0

    def check_event_open(self, event_flags):
        """For action='event' doors: open if event flag is set. Per D-03, D-04."""
        if self.action == "event" and self.event_id:
            if event_flags.get(self.event_id, False):
                self.open()

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
            # Keyhole centered in door
            kx = self.x + self.w // 2 - 1
            ky = self.y + self.h // 2 - 1
            pyxel.pset(kx, ky, 0)
            pyxel.pset(kx + 1, ky, 0)
            pyxel.pset(kx, ky + 1, 0)
            pyxel.pset(kx + 1, ky + 1, 0)


class OneWay:
    """One-way platform/gate stub (D-07). Renders placeholder, no collision behavior yet."""

    def __init__(self, x, y, direction="right"):
        self.x = x
        self.y = y
        self.w = 16
        self.h = 16
        self.direction = direction

    def update(self):
        pass

    def draw(self):
        # Placeholder: directional arrow outline (color 13 = light blue)
        pyxel.rectb(self.x, self.y, 16, 16, 13)

    def check_collision(self, x, y, w, h):
        return (x < self.x + self.w and x + w > self.x and
                y < self.y + self.h and y + h > self.y)


class HiddenLoot:
    """Hidden loot container stub (D-08). Renders placeholder, no reveal mechanic yet."""

    def __init__(self, x, y, iid=None):
        self.x = x
        self.y = y
        self.w = 16
        self.h = 16
        self.iid = iid

    def update(self):
        pass

    def draw(self):
        # Placeholder: dashed outline (color 5 = dark gray, subtle)
        pyxel.rectb(self.x, self.y, 16, 16, 5)

    def check_collision(self, x, y, w, h):
        return (x < self.x + self.w and x + w > self.x and
                y < self.y + self.h and y + h > self.y)


class MapFixture:
    """Map wall fixture stub (D-09). Player interacts to reveal map areas. Stub only."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 16
        self.h = 16

    def update(self):
        pass

    def draw(self):
        # Placeholder: small indicator (color 12 = blue)
        pyxel.rectb(self.x, self.y, 16, 16, 12)

    def check_collision(self, x, y, w, h):
        return (x < self.x + self.w and x + w > self.x and
                y < self.y + self.h and y + h > self.y)
