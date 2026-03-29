"""Tests for Phase 13 sprite asset outputs."""
import os
import json
import pytest

SPRITES_DIR = "assets/sprites"
ENTITY_NAMES = ["player", "slime", "snail", "bat", "items", "projectile", "effects", "boss"]

# --- PNG existence and loading tests ---

def test_all_entity_pngs_exist():
    """Each entity has a PNG spritesheet in assets/sprites/."""
    for name in ENTITY_NAMES:
        path = os.path.join(SPRITES_DIR, f"{name}.png")
        assert os.path.exists(path), f"Missing PNG: {path}"

def test_tiles_png_exists():
    """tiles.png exists for bank 0 tile graphics."""
    assert os.path.exists(os.path.join(SPRITES_DIR, "tiles.png"))

# --- JSON sidecar tests ---

def test_all_json_sidecars_exist():
    """Each entity has a JSON sidecar."""
    for name in ENTITY_NAMES:
        path = os.path.join(SPRITES_DIR, f"{name}.json")
        assert os.path.exists(path), f"Missing JSON: {path}"

def test_json_sidecar_structure():
    """Each JSON sidecar has meta.frameTags with name/from/to/direction."""
    for name in ENTITY_NAMES:
        path = os.path.join(SPRITES_DIR, f"{name}.json")
        if not os.path.exists(path):
            pytest.skip(f"{path} not yet generated")
        with open(path) as f:
            data = json.load(f)
        assert "meta" in data, f"{name}.json missing 'meta'"
        assert "frameTags" in data["meta"], f"{name}.json missing 'frameTags'"
        for tag in data["meta"]["frameTags"]:
            assert "name" in tag, f"{name}.json tag missing 'name'"
            assert "from" in tag, f"{name}.json tag missing 'from'"
            assert "to" in tag, f"{name}.json tag missing 'to'"
            assert "direction" in tag, f"{name}.json tag missing 'direction'"

# --- Pixel data tests (require pyxel) ---

def test_entity_sprites_have_pixel_data():
    """Each entity PNG has at least one non-transparent pixel in first frame."""
    try:
        import pyxel
    except ImportError:
        pytest.skip("pyxel not available")
    pyxel.init(256, 256, display_scale=1)
    for name in ENTITY_NAMES:
        path = os.path.join(SPRITES_DIR, f"{name}.png")
        if not os.path.exists(path):
            pytest.skip(f"{path} not yet generated")
        pyxel.images[1].load(0, 0, path)
        frame_w = 32 if name == "boss" else 16  # D-03: boss is 32x32
        frame_h = frame_w
        has_pixel = False
        for px in range(frame_w):
            for py in range(frame_h):
                if pyxel.images[1].pget(px, py) != 0:
                    has_pixel = True
                    break
            if has_pixel:
                break
        assert has_pixel, f"{name}.png first frame is all transparent"

def test_tiles_preserve_solid_tile():
    """tiles.png has non-transparent pixels at TILE_SOLID position (0,8)."""
    try:
        import pyxel
    except ImportError:
        pytest.skip("pyxel not available")
    pyxel.init(256, 256, display_scale=1)
    path = os.path.join(SPRITES_DIR, "tiles.png")
    if not os.path.exists(path):
        pytest.skip("tiles.png not yet generated")
    pyxel.images[0].load(0, 0, path)
    assert pyxel.images[0].pget(0, 8) != 0, "TILE_SOLID position (0,8) is empty"

# --- Palette compliance (D-26) ---

def test_palette_compliance():
    """All entity PNGs use only valid Pyxel palette colors (indices 0-15, per D-26)."""
    try:
        import pyxel
    except ImportError:
        pytest.skip("pyxel not available")
    pyxel.init(256, 256, display_scale=1)
    VALID_COLORS = set(range(16))  # Pyxel palette: indices 0-15
    for name in ENTITY_NAMES:
        path = os.path.join(SPRITES_DIR, f"{name}.png")
        if not os.path.exists(path):
            pytest.skip(f"{path} not yet generated")
        pyxel.images[1].load(0, 0, path)
        # Check first frame only (sufficient for upscaled sprites)
        frame_w = 32 if name == "boss" else 16
        frame_h = frame_w
        for px in range(frame_w):
            for py in range(frame_h):
                color = pyxel.images[1].pget(px, py)
                assert color in VALID_COLORS, (
                    f"{name}.png pixel ({px},{py}) has invalid color {color} "
                    f"-- must be 0-15 per D-26"
                )
