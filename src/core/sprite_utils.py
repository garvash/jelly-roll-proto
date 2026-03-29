"""Sprite drawing helpers for Phase 13 PNG spritesheet pipeline."""
import pyxel
import json
from src.core.constants import SPRITE_SIZE, BOSS_SPRITE_SIZE


def draw_sprite(x, y, coll_w, coll_h, bank, u, v,
                visual_w, visual_h, facing_right, colkey=0, scale=None):
    """Draw a sprite with bottom-center anchor offset (D-12).

    Args:
        x, y: collision box top-left position
        coll_w, coll_h: collision box dimensions (8x8 for standard entities)
        bank: image bank index (1 for entities)
        u, v: source coordinates in image bank
        visual_w, visual_h: sprite pixel dimensions (16x16 standard, 32x32 boss)
        facing_right: True for right-facing, False to flip horizontally
        colkey: transparent color index (default 0)
        scale: optional runtime scale factor (used by slime juice-depletion shrink)
    """
    # Apply scale to visual dimensions if provided
    if scale is not None:
        scaled_w = visual_w * scale
        scaled_h = visual_h * scale
        # Bottom-center anchor with scale: center horizontally, anchor at feet
        draw_x = x - (scaled_w - coll_w) / 2
        draw_y = y - (scaled_h - coll_h)
    else:
        draw_x = x - (visual_w - coll_w) // 2
        draw_y = y - (visual_h - coll_h)

    w = visual_w if facing_right else -visual_w
    pyxel.blt(draw_x, draw_y, bank, u, v, w, visual_h, colkey, scale=scale)


def load_sprite_tags(json_path):
    """Parse Aseprite JSON sidecar, return {tag_name: (start_frame, end_frame)}.

    Note (D-23/D-08): In this prototype phase, entity draw methods use hardcoded
    frame arithmetic rather than tag lookups. load_sprite_tags() provides
    forward-compatible metadata for the art pipeline -- when the artist replaces
    auto-upscaled PNGs with hand-drawn Aseprite exports, the JSON tags will
    drive frame selection automatically. For now, tags are loaded into
    Game.sprite_tags for reference but not consumed by draw methods.

    Args:
        json_path: path to .json sidecar file (e.g., 'assets/sprites/player.json')

    Returns:
        dict mapping tag names to (from_frame, to_frame) tuples
        e.g., {"idle": (0, 0), "walk": (1, 2)}
    """
    with open(json_path) as f:
        data = json.load(f)
    tags = {}
    if "meta" in data and "frameTags" in data["meta"]:
        for tag in data["meta"]["frameTags"]:
            tags[tag["name"]] = (tag["from"], tag["to"])
    return tags
