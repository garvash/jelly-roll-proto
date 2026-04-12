"""Tests for Phase 20 grid constants contract (replaces Phase 13 sprite scale tests)."""
import pytest


def test_tile_size_is_16():
    from src.core.constants import TILE_SIZE
    assert TILE_SIZE == 16, "TILE_SIZE must be 16 (16x16 base grid)"


def test_sprite_size_is_16():
    from src.core.constants import SPRITE_SIZE
    assert SPRITE_SIZE == 16, "SPRITE_SIZE must be 16 (native 16x16 sprites)"


def test_boss_sprite_size_is_32():
    from src.core.constants import BOSS_SPRITE_SIZE
    assert BOSS_SPRITE_SIZE == 32, "BOSS_SPRITE_SIZE must be 32 (2x TILE_SIZE)"


def test_sprite_scale_removed():
    """SPRITE_SCALE must no longer be importable from constants."""
    with pytest.raises(ImportError):
        from src.core.constants import SPRITE_SCALE


def test_tile_empty_updated():
    from src.core.constants import TILE_EMPTY
    assert tuple(TILE_EMPTY) == (15, 15), "TILE_EMPTY must be (15, 15) for 16px grid"
