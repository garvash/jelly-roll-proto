"""Sprite drawing utilities for bottom-center anchored entity rendering."""
import pyxel


def draw_sprite(x, y, coll_w, coll_h, bank, u, v,
                visual_w, visual_h, facing_right, colkey=0, scale=None):
    """Draw a sprite with bottom-center anchor offset.

    Args:
        x, y: Collision box top-left position.
        coll_w, coll_h: Collision box dimensions.
        bank: Pyxel image bank index.
        u, v: Source sprite coordinates in the bank.
        visual_w, visual_h: Visual sprite dimensions (pre-scale).
        facing_right: If False, flip sprite horizontally.
        colkey: Transparent color key (default 0).
        scale: Optional scale factor (e.g., for slime juice depletion).
    """
    if scale is not None:
        # Scaled drawing (e.g., slime shrink effect)
        scaled_w = visual_w * scale
        scaled_h = visual_h * scale
        # Bottom-center anchor: center horizontally on collision box, align bottom
        draw_x = x + (coll_w - scaled_w) / 2
        draw_y = y + coll_h - scaled_h
        w = visual_w if facing_right else -visual_w
        pyxel.blt(draw_x, draw_y, bank, u, v, w, visual_h, colkey, scale=scale)
    else:
        # Standard drawing: bottom-center anchor
        draw_x = x - (visual_w - coll_w) // 2
        draw_y = y - (visual_h - coll_h)
        w = visual_w if facing_right else -visual_w
        pyxel.blt(draw_x, draw_y, bank, u, v, w, visual_h, colkey)


def load_sprite_tags(json_path):
    """Load Aseprite JSON sidecar and return {tag_name: (start_frame, end_frame)}.

    Note: Tags loaded for forward compatibility. Entity draw methods use hardcoded
    frame arithmetic in this prototype phase (D-23/D-08).
    """
    import json
    with open(json_path) as f:
        data = json.load(f)
    tags = {}
    for tag in data.get("meta", {}).get("frameTags", []):
        tags[tag["name"]] = (tag["from"], tag["to"])
    return tags
