"""Regenerate assets/physics-schema.json from src/core/constants.py.

Run after any physics tuning:
    python scripts/update_physics_schema.py
"""
import json
import sys
import os

# Add project root to path so we can import constants
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.constants import (
    GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, MAX_FALL_SPEED,
    FALLING_GRAVITY_MULTIPLIER, TILE_SIZE,
)

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "physics-schema.json")
FPS = 60


def compute_jump_height():
    """Simulate Euler integration to find max jump height in pixels."""
    vy = JUMP_FORCE
    height = 0.0
    frames = 0
    while vy < 0:
        height += vy
        vy += GRAVITY
        frames += 1
    return abs(height), frames


def compute_jump_width(frames_up, peak_px):
    """Simulate fall from apex with gravity multiplier, return total air frames."""
    g_fall = GRAVITY * FALLING_GRAVITY_MULTIPLIER
    vy = 0.0
    fall_px = 0.0
    frames_down = 0
    while fall_px < peak_px:
        vy = min(vy + g_fall, MAX_FALL_SPEED)
        fall_px += vy
        frames_down += 1
    total_air = frames_up + frames_down
    horiz_px = MAX_WALK_SPEED * total_air
    return horiz_px, total_air


def main():
    peak_px, frames_up = compute_jump_height()
    horiz_px, total_air = compute_jump_width(frames_up, peak_px)

    peak_tiles_raw = peak_px / TILE_SIZE
    horiz_tiles_raw = horiz_px / TILE_SIZE

    # Safe values: floor to whole tiles with 1-tile landing margin
    safe_height = int(peak_tiles_raw) - 1
    safe_width = int(horiz_tiles_raw) - 1
    comfortable_height = max(1, safe_height - 2)
    comfortable_width = max(1, safe_width - 3)

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Jelly Roll Proto \u2014 Physics Contract",
        "description": "Derived physics constants for map generation. The pml-to-ldtk converter uses these to place stepping stones, validate gaps, and ensure traversability. Values are computed from the game's Euler integration at 60fps.",
        "version": "0.1.0",
        "updated": "auto-generated",

        "tile_size": TILE_SIZE,
        "fps": FPS,

        "player": {
            "hitbox_tiles": [1, 1],
            "hitbox_px": [8, 8],
            "visual_tiles": [2, 2],
            "visual_px": [16, 16],
            "note": "Collision box is 8x8 (1 tile). Visual sprite is 16x16 (2 tiles) via SPRITE_SCALE=2."
        },

        "jump": {
            "max_height_tiles": safe_height,
            "max_height_px": round(peak_px),
            "max_height_note": f"Absolute peak from Euler integration ({peak_tiles_raw:.2f} tiles). Floored to {safe_height} for safe platform placement.",

            "max_width_tiles": safe_width,
            "max_width_px": round(horiz_px),
            "max_width_note": f"Horizontal distance at full run speed over jump arc ({horiz_tiles_raw:.2f} tiles). Floored to {safe_width} for safe gap sizing.",

            "comfortable_height_tiles": comfortable_height,
            "comfortable_height_note": "Reachable without pixel-perfect timing. Use for standard platforming.",

            "comfortable_width_tiles": comfortable_width,
            "comfortable_width_note": "Reachable without a full-speed running start. Use for standard gaps."
        },

        "fall": {
            "damage_threshold_tiles": None,
            "damage_threshold_note": "No fall damage. Terminal velocity is capped. Any drop is safe."
        },

        "clearance": {
            "min_vertical_tiles": 2,
            "min_vertical_note": "Player visual is 2 tiles tall. Passages must be at least 2 tiles high.",
            "min_horizontal_tiles": 2,
            "min_horizontal_note": "Player visual is 2 tiles wide. Passages must be at least 2 tiles wide."
        },

        "placement_rules": {
            "description": "Rules the converter should follow when placing stepping stones and validating room traversability.",
            "max_gap_horizontal": {
                "value_tiles": safe_width,
                "note": "No horizontal gap wider than this without a platform."
            },
            "max_gap_vertical_up": {
                "value_tiles": safe_height,
                "note": "No upward gap taller than this without a reachable platform."
            },
            "max_gap_vertical_down": {
                "value_tiles": None,
                "note": "No limit — no fall damage. Any drop is safe."
            },
            "platform_min_width_tiles": 2,
            "platform_min_width_note": "Minimum landing platform width. 1 tile is too narrow for comfortable landing."
        },

        "source_constants": {
            "description": "Raw game constants these values derive from. Auto-populated from src/core/constants.py.",
            "GRAVITY": GRAVITY,
            "JUMP_FORCE": JUMP_FORCE,
            "MAX_WALK_SPEED": MAX_WALK_SPEED,
            "MAX_FALL_SPEED": MAX_FALL_SPEED,
            "FALLING_GRAVITY_MULTIPLIER": FALLING_GRAVITY_MULTIPLIER,
            "TILE_SIZE": TILE_SIZE
        }
    }

    with open(SCHEMA_PATH, "w") as f:
        json.dump(schema, f, indent=2)
        f.write("\n")

    print(f"Updated {SCHEMA_PATH}")
    print(f"  Jump height: {safe_height} tiles ({peak_px:.0f}px, raw {peak_tiles_raw:.2f})")
    print(f"  Jump width:  {safe_width} tiles ({horiz_px:.0f}px, raw {horiz_tiles_raw:.2f})")
    print(f"  Comfortable: {comfortable_height}h / {comfortable_width}w tiles")


if __name__ == "__main__":
    main()
