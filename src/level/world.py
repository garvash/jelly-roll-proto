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
    """Manages the collection of levels, transitions, and state persistence."""

    # Screen dimensions (Pyxel window size)
    SCREEN_W = 128
    SCREEN_H = 128

    # Transition states
    STATE_PLAYING = "PLAYING"
    STATE_TRANSITIONING = "TRANSITIONING"

    # Transition duration in frames (~0.4s at 60fps)
    TRANSITION_FRAMES = 24

    def __init__(self, levels=None):
        """Initialize with a list of LevelBounds objects."""
        self.levels = levels or []
        self.current_level = None

        # Transition state
        self.state = self.STATE_PLAYING
        self.transition_timer = 0
        self.transition_from_cam = (0, 0)  # (cam_x, cam_y) at start
        self.transition_to_cam = (0, 0)    # (cam_x, cam_y) at end
        self.transition_target_level = None

        # Persistence: collected item IDs (never respawn)
        self.collected_iids = set()

        # Persistence: broken destructible blocks with regen timers
        # Key: (tx, ty), Value: frames remaining until regen
        self.broken_blocks = {}

        # Regen rate: 5 seconds at 60fps = 300 frames
        self.block_regen_frames = 300

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

    def trigger_transition(self, target_level, current_cam_x, current_cam_y, player_x=None, player_y=None):
        """Begin a freeze-and-slide transition to the target level.

        Args:
            target_level: LevelBounds of the destination room.
            current_cam_x: Current camera X position.
            current_cam_y: Current camera Y position.
            player_x: Player X position (used to compute target camera).
            player_y: Player Y position (used to compute target camera).
        """
        if self.state == self.STATE_TRANSITIONING:
            return  # Already transitioning

        self.state = self.STATE_TRANSITIONING
        self.transition_timer = 0
        self.transition_from_cam = (current_cam_x, current_cam_y)
        self.transition_target_level = target_level

        # Compute target camera clamped around the player's position in the
        # target room. If player position is not provided, fall back to the
        # room origin (top-left corner).
        if player_x is not None and player_y is not None:
            # Temporarily set current_level so get_camera_clamped uses target bounds
            prev_level = self.current_level
            self.current_level = target_level
            target_cam_x, target_cam_y = self.get_camera_clamped(player_x, player_y)
            self.current_level = prev_level
        else:
            target_cam_x = target_level.x
            target_cam_y = target_level.y
            max_x = target_level.x + target_level.w - self.SCREEN_W
            max_y = target_level.y + target_level.h - self.SCREEN_H
            target_cam_x = max(target_level.x, min(target_cam_x, max_x))
            target_cam_y = max(target_level.y, min(target_cam_y, max_y))

        self.transition_to_cam = (int(target_cam_x), int(target_cam_y))

    def update_transition(self):
        """Update the camera slide during transition. Returns (cam_x, cam_y).

        Should be called every frame while state is STATE_TRANSITIONING.
        Returns the interpolated camera position.
        When transition completes, sets state back to STATE_PLAYING.
        """
        if self.state != self.STATE_TRANSITIONING:
            return self.transition_to_cam

        self.transition_timer += 1
        t = min(self.transition_timer / self.TRANSITION_FRAMES, 1.0)

        # Ease-out quadratic for smooth deceleration
        t_eased = 1.0 - (1.0 - t) * (1.0 - t)

        from_x, from_y = self.transition_from_cam
        to_x, to_y = self.transition_to_cam

        cam_x = from_x + (to_x - from_x) * t_eased
        cam_y = from_y + (to_y - from_y) * t_eased

        if self.transition_timer >= self.TRANSITION_FRAMES:
            self.state = self.STATE_PLAYING
            self.current_level = self.transition_target_level
            return (int(to_x), int(to_y))

        return (int(cam_x), int(cam_y))

    def is_transitioning(self):
        """Returns True if a transition is currently in progress."""
        return self.state == self.STATE_TRANSITIONING

    # --- Item Persistence ---

    def is_item_collected(self, iid):
        """Check if an item with the given instance ID has been collected."""
        return iid in self.collected_iids

    def collect_item(self, iid):
        """Mark an item as permanently collected."""
        self.collected_iids.add(iid)

    # --- Block Regeneration ---

    def break_block(self, tx, ty, tile_data):
        """Record a broken destructible block for timed regeneration.

        Args:
            tx, ty: Tile coordinates of the broken block.
            tile_data: The original tile value (for restoration).
        """
        self.broken_blocks[(tx, ty)] = {
            "timer": self.block_regen_frames,
            "tile_data": tile_data
        }

    def update_block_regen(self, level_map):
        """Tick down regen timers and restore blocks that are ready.

        Args:
            level_map: The LevelMap instance to restore tiles on.
        """
        restored = []
        for (tx, ty), info in self.broken_blocks.items():
            info["timer"] -= 1
            if info["timer"] <= 0:
                restored.append((tx, ty))
                # Restore the tile in both collision data and visual tilemap
                level_map.restore_tile(tx, ty, info["tile_data"])

        for key in restored:
            del self.broken_blocks[key]

    def reset_blocks_for_room(self, level_map):
        """Reset all broken blocks instantly (called on room entry).

        Prevents soft-locks by restoring all destructible blocks when
        the player enters a new room.
        """
        for (tx, ty), info in self.broken_blocks.items():
            level_map.restore_tile(tx, ty, info["tile_data"])
        self.broken_blocks.clear()
