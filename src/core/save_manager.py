"""Save system persistence manager for JSON-based single-slot saves."""
import json
import os

from src.core import tuning


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
            "version": 1,
            "player": {
                "max_hp": player.max_hp,
                "has_drill": getattr(player, "has_drill", False),
                "has_dash": getattr(player, "has_dash", False),
                "has_shield": getattr(player, "has_shield", False),
                "has_shield_t2": getattr(player, "has_shield_t2", False),
                "has_boost": getattr(player, "has_boost", False),
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
        """Load game state from JSON file. Returns dict or None if missing."""
        path = SaveManager._get_save_path()
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            return json.load(f)

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
