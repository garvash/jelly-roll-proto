"""Save system persistence manager for JSON-based single-slot saves.

Phase 32 FUS-07: save format bumped from `version: 1` to `save_version: 2`.
v1.3 saves rejected on load via SaveVersionMismatchError (D-21..D-24).
"""
import json
import os

from src.core import tuning

# D-23: Single source of truth for save schema version. Increment on breaking change.
CURRENT_SAVE_VERSION = 2


class SaveVersionMismatchError(Exception):
    """Raised when load() encounters a save with a save_version mismatch.

    The file is preserved on disk (D-24); caller surfaces the user-facing message.
    `found` may be None if the save predates the save_version field entirely (v1.3 saves).
    """
    def __init__(self, found, expected):
        self.found = found
        self.expected = expected
        super().__init__(
            f"Save file version {found} does not match expected {expected}. "
            f"Save preserved on disk."
        )


class SaveManager:
    """Static methods for saving/loading game state to a JSON file."""

    @staticmethod
    def _get_save_path():
        """Resolve save file path relative to project root (Pitfall 7)."""
        # Go up from src/core/ to project root
        core_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(core_dir))
        return os.path.join(project_root, tuning.SAVE_FILE)

    @staticmethod
    def save(game):
        """Serialize game state to JSON file.

        Saves max_hp/max_juice only (not current values) per D-04:
        player respawns at full HP/juice on load.
        """
        player = game.player
        slime = game.slime
        world = game.world

        data = {
            "save_version": CURRENT_SAVE_VERSION,
            "player": {
                "max_hp": player.max_hp,
                "has_drill": getattr(player, "has_drill", False),
            },
            "slime": {
                "max_juice": slime.max_juice,
            },
            "world": {
                "collected_iids": list(world.collected_iids),
            },
            "event_flags": dict(game.event_flags),
            "save_room_id": world.current_level.id,
            "visited_rooms": list(game.rooms_visited),
        }

        path = SaveManager._get_save_path()
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load():
        """Load game state from JSON file. Returns dict or None if missing.

        Raises SaveVersionMismatchError when the file exists but its
        `save_version` does not match CURRENT_SAVE_VERSION (D-24, Pitfall 8).
        Order: existence check, parse, version check — so a missing file
        still returns None and a missing key surfaces as `found=None` (not
        KeyError) per Pitfall 8 / T-32-03-01.
        """
        path = SaveManager._get_save_path()
        if not os.path.exists(path):
            return None  # 1. missing file path: unchanged
        with open(path, "r") as f:
            data = json.load(f)  # 2. parse JSON
        found = data.get("save_version")  # 3. version check (D-24, Pitfall 8)
        if found != CURRENT_SAVE_VERSION:
            raise SaveVersionMismatchError(found=found, expected=CURRENT_SAVE_VERSION)
        return data

    @staticmethod
    def exists():
        """Check if a save file exists."""
        return os.path.exists(SaveManager._get_save_path())

    @staticmethod
    def delete():
        """Remove save file if it exists. No-op if absent."""
        path = SaveManager._get_save_path()
        if os.path.exists(path):
            os.remove(path)
