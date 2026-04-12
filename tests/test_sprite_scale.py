"""Tests for Phase 13 sprite scale constants and draw helper."""
import json
import os
import tempfile
import pytest


def test_sprite_scale_constant():
    from src.core.constants import SPRITE_SCALE
    assert SPRITE_SCALE == 2, "SPRITE_SCALE must be 2"


def test_sprite_size_derived_from_tile():
    from src.core.constants import TILE_SIZE, SPRITE_SCALE, SPRITE_SIZE
    assert SPRITE_SIZE == TILE_SIZE * SPRITE_SCALE, "SPRITE_SIZE must be TILE_SIZE * SPRITE_SCALE"


def test_boss_sprite_size():
    from src.core.constants import SPRITE_SCALE, BOSS_SPRITE_SIZE
    assert BOSS_SPRITE_SIZE == 16 * SPRITE_SCALE, "BOSS_SPRITE_SIZE must be 32"


def test_draw_sprite_offset_standard(monkeypatch):
    """Bottom-center anchor: 8x8 collision in 16x16 visual -> draw_x = x-4, draw_y = y-8."""
    import pyxel
    captured = {}
    def mock_blt(dx, dy, bank, u, v, w, h, colkey, **kwargs):
        captured['dx'] = dx
        captured['dy'] = dy
    monkeypatch.setattr("src.core.sprite_utils.pyxel.blt", mock_blt)
    from src.core.sprite_utils import draw_sprite
    # Entity at collision pos (100, 200), collision 8x8, visual 16x16
    draw_sprite(100, 200, 8, 8, 1, 0, 0, 16, 16, True)
    assert captured['dx'] == 96, f"draw_x should be 100 - (16-8)//2 = 96, got {captured['dx']}"
    assert captured['dy'] == 192, f"draw_y should be 200 - (16-8) = 192, got {captured['dy']}"


def test_load_sprite_tags_valid_json():
    from src.core.sprite_utils import load_sprite_tags
    data = {
        "meta": {
            "frameTags": [
                {"name": "idle", "from": 0, "to": 0, "direction": "forward"},
                {"name": "walk", "from": 1, "to": 2, "direction": "forward"},
            ],
            "size": {"w": 48, "h": 16}
        }
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        tmp_path = f.name
    try:
        tags = load_sprite_tags(tmp_path)
        assert tags == {"idle": (0, 0), "walk": (1, 2)}
    finally:
        os.unlink(tmp_path)
