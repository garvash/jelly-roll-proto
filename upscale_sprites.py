"""Migration tool: reads game.pyxres, outputs 2x upscaled PNG spritesheets + JSON sidecars.

Per D-05, D-19: Auto-upscaled PNGs serve as reference templates for the artist.
Per D-06: One PNG per entity in horizontal strip layout.
Per D-07: Frames laid out left to right.
Per D-08: Aseprite-format JSON sidecars with frameTags.
Per D-26: All sprites use only Pyxel's 16-color palette (indices 0-15).
"""
import pyxel
import json
import os

SPRITES_DIR = "assets/sprites"

# --- Pixel doubling ---

def upscale_frames(src_bank, frames, src_size, dst_img):
    """Pixel-double multiple frames from src_bank into dst_img as horizontal strip.

    Args:
        src_bank: source image bank index
        frames: list of (src_x, src_y) for each frame's top-left corner
        src_size: (width, height) of each source frame
        dst_img: destination pyxel.Image (already sized for 2x output)
    """
    src_w, src_h = src_size
    for i, (sx, sy) in enumerate(frames):
        dst_x_base = i * src_w * 2  # 2x width per frame
        for y in range(src_h):
            for x in range(src_w):
                color = pyxel.images[src_bank].pget(sx + x, sy + y)
                for dy in range(2):
                    for dx in range(2):
                        dst_img.pset(dst_x_base + x * 2 + dx, y * 2 + dy, color)


def generate_sidecar(tags, num_frames, frame_w, frame_h):
    """Generate Aseprite-compatible JSON sidecar.

    Args:
        tags: dict of {name: (from_frame, to_frame)}
        num_frames: total frame count
        frame_w: pixel width of each frame (after upscale)
        frame_h: pixel height of each frame (after upscale)
    """
    return {
        "meta": {
            "frameTags": [
                {"name": name, "from": start, "to": end, "direction": "forward"}
                for name, (start, end) in tags.items()
            ],
            "size": {"w": num_frames * frame_w, "h": frame_h}
        }
    }


def inject_explosion_sprites():
    """Inject runtime explosion sprites into bank 1 (matching main.py:28-45).

    These are NOT stored in game.pyxres -- they're generated at runtime.
    Must replicate them here before export.
    """
    # Frame 1 at (0, 48): inner white (7) dist<4, outer yellow (10) dist<9
    for y in range(48, 56):
        for x in range(0, 8):
            dist = (x - 3.5) ** 2 + (y - 51.5) ** 2
            if dist < 4:
                pyxel.images[1].pset(x, y, 7)
            elif dist < 9:
                pyxel.images[1].pset(x, y, 10)
    # Frame 2 at (8, 48): inner yellow (10) dist<9, outer orange (9) dist<16
    for y in range(48, 56):
        for x in range(8, 16):
            dist = (x - 11.5) ** 2 + (y - 51.5) ** 2
            if dist < 9:
                pyxel.images[1].pset(x, y, 10)
            elif dist < 16:
                pyxel.images[1].pset(x, y, 9)
    # Frame 3 at (16, 48): inner orange (9) dist<16, outer dark (4) dist<25
    for y in range(48, 56):
        for x in range(16, 24):
            dist = (x - 19.5) ** 2 + (y - 51.5) ** 2
            if dist < 16:
                pyxel.images[1].pset(x, y, 9)
            elif dist < 25:
                pyxel.images[1].pset(x, y, 4)


def main():
    pyxel.init(256, 256, display_scale=1)
    pyxel.load("assets/game.pyxres")

    # Inject runtime-generated explosion sprites (Pitfall 3)
    inject_explosion_sprites()

    os.makedirs(SPRITES_DIR, exist_ok=True)

    # =========================================================================
    # Entity sprite inventory (bank 1 positions from current pyxres)
    # =========================================================================

    # --- Player: 3 frames at 8px stride, row 0 ---
    PLAYER_FRAMES = [(0, 0), (8, 0), (16, 0)]
    PLAYER_TAGS = {"idle": (0, 0), "walk": (1, 2), "jump": (2, 2),
                   "fall": (2, 2), "dash": (2, 2), "drill": (2, 2)}
    num = len(PLAYER_FRAMES)
    img = pyxel.Image(16 * num, 16)
    upscale_frames(1, PLAYER_FRAMES, (8, 8), img)
    img.save(os.path.join(SPRITES_DIR, "player.png"), 1)
    with open(os.path.join(SPRITES_DIR, "player.json"), "w") as f:
        json.dump(generate_sidecar(PLAYER_TAGS, num, 16, 16), f, indent=2)
    print(f"player.png: {num} frames (16x16 each)")

    # --- Slime: 3 frames -- normal0=(0,8), normal1=(8,8), fused=(16,8) ---
    SLIME_FRAMES = [(0, 8), (8, 8), (16, 8)]
    SLIME_TAGS = {"idle": (0, 1), "fused": (2, 2)}
    num = len(SLIME_FRAMES)
    img = pyxel.Image(16 * num, 16)
    upscale_frames(1, SLIME_FRAMES, (8, 8), img)
    img.save(os.path.join(SPRITES_DIR, "slime.png"), 1)
    with open(os.path.join(SPRITES_DIR, "slime.json"), "w") as f:
        json.dump(generate_sidecar(SLIME_TAGS, num, 16, 16), f, indent=2)
    print(f"slime.png: {num} frames (16x16 each)")

    # --- Snail: 2 frames at 8px stride, row at y=16 ---
    SNAIL_FRAMES = [(0, 16), (8, 16)]
    SNAIL_TAGS = {"walk": (0, 1)}
    num = len(SNAIL_FRAMES)
    img = pyxel.Image(16 * num, 16)
    upscale_frames(1, SNAIL_FRAMES, (8, 8), img)
    img.save(os.path.join(SPRITES_DIR, "snail.png"), 1)
    with open(os.path.join(SPRITES_DIR, "snail.json"), "w") as f:
        json.dump(generate_sidecar(SNAIL_TAGS, num, 16, 16), f, indent=2)
    print(f"snail.png: {num} frames (16x16 each)")

    # --- Bat: 2 frames at 8px stride, row at y=24 ---
    BAT_FRAMES = [(0, 24), (8, 24)]
    BAT_TAGS = {"hang": (0, 0), "flap": (0, 1)}
    num = len(BAT_FRAMES)
    img = pyxel.Image(16 * num, 16)
    upscale_frames(1, BAT_FRAMES, (8, 8), img)
    img.save(os.path.join(SPRITES_DIR, "bat.png"), 1)
    with open(os.path.join(SPRITES_DIR, "bat.json"), "w") as f:
        json.dump(generate_sidecar(BAT_TAGS, num, 16, 16), f, indent=2)
    print(f"bat.png: {num} frames (16x16 each)")

    # --- Projectile: spit (24,8) 4x4 padded to 8x8 + rock (32,32) 8x8 ---
    # Spit is only 4x4 but stored in 8x8 cell; upscale full 8x8 region
    PROJ_FRAMES = [(24, 8), (32, 32)]
    PROJ_TAGS = {"spit": (0, 0), "rock": (1, 1)}
    num = len(PROJ_FRAMES)
    img = pyxel.Image(16 * num, 16)
    upscale_frames(1, PROJ_FRAMES, (8, 8), img)
    img.save(os.path.join(SPRITES_DIR, "projectile.png"), 1)
    with open(os.path.join(SPRITES_DIR, "projectile.json"), "w") as f:
        json.dump(generate_sidecar(PROJ_TAGS, num, 16, 16), f, indent=2)
    print(f"projectile.png: {num} frames (16x16 each)")

    # --- Effects: 3 explosion frames at 8px stride, y=48 ---
    EFFECT_FRAMES = [(0, 48), (8, 48), (16, 48)]
    EFFECT_TAGS = {"explosion": (0, 2)}
    num = len(EFFECT_FRAMES)
    img = pyxel.Image(16 * num, 16)
    upscale_frames(1, EFFECT_FRAMES, (8, 8), img)
    img.save(os.path.join(SPRITES_DIR, "effects.png"), 1)
    with open(os.path.join(SPRITES_DIR, "effects.json"), "w") as f:
        json.dump(generate_sidecar(EFFECT_TAGS, num, 16, 16), f, indent=2)
    print(f"effects.png: {num} frames (16x16 each)")

    # --- Boss Mole: 2 frames at 16px stride, 16x16 source -> 32x32 output ---
    BOSS_FRAMES = [(0, 32), (16, 32)]
    BOSS_TAGS = {"idle": (0, 1)}
    num = len(BOSS_FRAMES)
    img = pyxel.Image(32 * num, 32)
    upscale_frames(1, BOSS_FRAMES, (16, 16), img)
    img.save(os.path.join(SPRITES_DIR, "boss.png"), 1)
    with open(os.path.join(SPRITES_DIR, "boss.json"), "w") as f:
        json.dump(generate_sidecar(BOSS_TAGS, num, 32, 32), f, indent=2)
    print(f"boss.png: {num} frames (32x32 each)")

    # --- Items: energy (56,0 bank1), missile (48,8 bank1),
    #            dash_pickup (24,0 bank0), shield_pickup (32,0 bank0),
    #            boost_pickup (40,0 bank0), shield_t2 (48,0 bank0) ---
    ITEM_SOURCES = [
        (1, 56, 0),   # energy tank
        (1, 48, 8),   # missile tank
        (0, 24, 0),   # dash pickup (Pitfall 2: items on bank 0)
        (0, 32, 0),   # shield pickup
        (0, 40, 0),   # boost pickup
        (0, 48, 0),   # shield T2
    ]
    ITEM_TAGS = {
        "energy": (0, 0), "missile": (1, 1),
        "dash_pickup": (2, 2), "shield_pickup": (3, 3),
        "boost_pickup": (4, 4), "shield_t2": (5, 5)
    }
    num = len(ITEM_SOURCES)
    img = pyxel.Image(16 * num, 16)
    for i, (bank, sx, sy) in enumerate(ITEM_SOURCES):
        dst_x_base = i * 16  # 16px per frame in output
        for y in range(8):
            for x in range(8):
                color = pyxel.images[bank].pget(sx + x, sy + y)
                for dy in range(2):
                    for dx in range(2):
                        img.pset(dst_x_base + x * 2 + dx, y * 2 + dy, color)
    img.save(os.path.join(SPRITES_DIR, "items.png"), 1)
    with open(os.path.join(SPRITES_DIR, "items.json"), "w") as f:
        json.dump(generate_sidecar(ITEM_TAGS, num, 16, 16), f, indent=2)
    print(f"items.png: {num} frames (16x16 each)")

    # =========================================================================
    # Tiles: full bank 0 export (8x8 cells, preserves bltm compatibility)
    # =========================================================================
    # Save scale=1 to get palette-indexed PNG at original resolution
    pyxel.images[0].save(os.path.join(SPRITES_DIR, "tiles.png"), 1)
    print("tiles.png: full bank 0 (256x256, 8x8 cells)")

    # =========================================================================
    # Summary
    # =========================================================================
    png_count = len([f for f in os.listdir(SPRITES_DIR) if f.endswith(".png")])
    json_count = len([f for f in os.listdir(SPRITES_DIR) if f.endswith(".json")])
    print(f"\nGenerated {png_count} PNGs and {json_count} JSON sidecars in {SPRITES_DIR}/")
    print("Done. These are reference templates for the artist (D-05).")


if __name__ == "__main__":
    main()
