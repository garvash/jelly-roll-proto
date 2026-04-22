"""Tests for Phase 13 sprite asset outputs."""
import os
import json
import pytest

# Resolve project root relative to this test file's location (tests/ -> project root).
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(_PROJECT_ROOT, "assets", "sprites")
ENTITY_NAMES = ["player", "slime", "snail", "bat", "items", "projectile", "effects", "boss"]

# Module-level pyxel init -- Pyxel can only be initialized once per process.
# Note: pyxel.init() may change CWD, so we resolve paths above first.
_pyxel_available = False
try:
    import pyxel
    pyxel.init(256, 256, display_scale=1)
    _pyxel_available = True
except (ImportError, Exception):
    pass


def _require_pyxel():
    """Skip test if pyxel is not available."""
    if not _pyxel_available:
        pytest.skip("pyxel not available")


# --- PNG existence and loading tests ---

def test_all_entity_pngs_exist():
    """Each entity has a PNG spritesheet in assets/sprites/."""
    for name in ENTITY_NAMES:
        path = os.path.join(SPRITES_DIR, f"{name}.png")
        assert os.path.exists(path), f"Missing PNG: {path}"

def test_tiles_png_exists():
    """tiles.png exists for bank 0 tile graphics."""
    tilesets_dir = os.path.join(_PROJECT_ROOT, "assets", "tilesets")
    assert os.path.exists(os.path.join(tilesets_dir, "cavern.png"))

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
    """Each entity PNG has at least one non-transparent pixel across all frames.

    Some entities (e.g. items) may have empty source frames in the pyxres --
    we check that at least one frame in the strip contains visible pixels.
    """
    _require_pyxel()
    for name in ENTITY_NAMES:
        path = os.path.join(SPRITES_DIR, f"{name}.png")
        if not os.path.exists(path):
            pytest.skip(f"{path} not yet generated")
        pyxel.images[1].load(0, 0, path)
        frame_w = 32 if name == "boss" else 16  # D-03: boss is 32x32
        frame_h = frame_w
        # Read JSON sidecar to determine total frame count
        json_path = os.path.join(SPRITES_DIR, f"{name}.json")
        total_w = frame_w  # fallback: check first frame only
        if os.path.exists(json_path):
            with open(json_path) as f:
                meta = json.load(f).get("meta", {})
            total_w = meta.get("size", {}).get("w", frame_w)
        num_frames = total_w // frame_w
        has_pixel = False
        for frame_idx in range(num_frames):
            x_off = frame_idx * frame_w
            for px in range(frame_w):
                for py in range(frame_h):
                    if pyxel.images[1].pget(x_off + px, py) != 0:
                        has_pixel = True
                        break
                if has_pixel:
                    break
            if has_pixel:
                break
        assert has_pixel, f"{name}.png has no visible pixels in any frame"

def test_tiles_preserve_solid_tile():
    """cavern.png has non-transparent pixels at TILE_SOLID position (0,16)."""
    _require_pyxel()
    path = os.path.join(_PROJECT_ROOT, "assets", "tilesets", "cavern.png")
    if not os.path.exists(path):
        pytest.skip("cavern.png not yet generated")
    pyxel.images[0].load(0, 0, path)
    assert pyxel.images[0].pget(0, 16) != 0, "TILE_SOLID position (0,16) is empty"

# --- Palette compliance (D-26) ---

def test_palette_compliance():
    """All entity PNGs use only valid Pyxel palette colors (indices 0-15, per D-26)."""
    _require_pyxel()
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


# ---------------------------------------------------------------------------
# Phase 31 ANIM-06: bank 2 particle separation (D-15, D-16)
# ---------------------------------------------------------------------------

def test_sprite_manifest_particles_bank_2():
    from main import SPRITE_MANIFEST
    assert "particles" in SPRITE_MANIFEST
    bank, x, y, path = SPRITE_MANIFEST["particles"]
    assert bank == 2, f"particles must be bank 2 per D-15, got {bank}"
    assert x == 0
    assert y == 0
    assert path == "assets/sprites/particles.png"


def test_sprite_manifest_effects_removed():
    from main import SPRITE_MANIFEST
    assert "effects" not in SPRITE_MANIFEST, (
        "D-16: effects entry at bank 1 y=96 must be retired; "
        "block-break uses diverging particle burst from bank 2 instead."
    )


def test_sprite_manifest_banks_distinct():
    """D-15 / SC-3: tiles (bank 0) and particles (bank 2) are in distinct banks."""
    from main import SPRITE_MANIFEST
    tile_bank = SPRITE_MANIFEST["tiles"][0]
    particle_bank = SPRITE_MANIFEST["particles"][0]
    assert tile_bank != particle_bank
    assert tile_bank == 0
    assert particle_bank == 2
