"""WorldManager and LevelBounds for 5x5 macro-map room management."""


class LevelBounds:
    """Stores the bounding rectangle of a single LDtk level."""

    def __init__(self, identifier, x, y, w, h):
        self.id = identifier
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def contains(self, px, py):
        """Returns True if the point (px, py) is inside this level."""
        return (self.x <= px < self.x + self.w and
                self.y <= py < self.y + self.h)

    def __repr__(self):
        return f"LevelBounds({self.id!r}, x={self.x}, y={self.y}, w={self.w}, h={self.h})"


class WorldManager:
    """Manages the collection of levels and provides camera clamping."""

    # Screen dimensions (Pyxel window size)
    SCREEN_W = 128
    SCREEN_H = 128

    def __init__(self, levels=None):
        """Initialize with a list of LevelBounds objects."""
        self.levels = levels or []
        self.current_level = None

    def detect_level(self, x, y):
        """Return the LevelBounds containing the point (x, y), or None.

        Uses the player's center-point to determine which room they occupy.
        Updates self.current_level as a side-effect.
        """
        for level in self.levels:
            if level.contains(x, y):
                self.current_level = level
                return level
        return None

    def get_camera_clamped(self, px, py):
        """Return clamped (cam_x, cam_y) for a given player position.

        Centers the camera on the player but clamps within the current
        level's bounds so no out-of-bounds area is visible.

        If no current_level is set, falls back to simple grid snapping
        (legacy behavior).
        """
        level = self.current_level
        if level is None:
            # Fallback: snap to 128x128 grid (legacy behavior)
            return (int(px // self.SCREEN_W) * self.SCREEN_W,
                    int(py // self.SCREEN_H) * self.SCREEN_H)

        # Center camera on player (offset by half screen minus half player ~4px)
        target_x = px - self.SCREEN_W // 2
        target_y = py - self.SCREEN_H // 2

        # Clamp so camera never shows outside level bounds
        min_x = level.x
        max_x = level.x + level.w - self.SCREEN_W
        min_y = level.y
        max_y = level.y + level.h - self.SCREEN_H

        # For rooms exactly 128x128, min == max, so camera locks perfectly
        cam_x = max(min_x, min(target_x, max_x))
        cam_y = max(min_y, min(target_y, max_y))

        return (cam_x, cam_y)
