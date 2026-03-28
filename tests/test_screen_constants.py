"""Tests for screen/display constants (D-01, D-02, D-08)."""
import pytest
from unittest.mock import MagicMock
import sys

# Mock pyxel to allow imports that transitively reference it
sys.modules.setdefault("pyxel", MagicMock())

from src.core.constants import (
    SCREEN_W, SCREEN_H, VIEWPORT_W, VIEWPORT_H, HUD_H, CULL_MARGIN, TILE_SIZE
)


class TestScreenConstants:
    def test_screen_w(self):
        assert SCREEN_W == 320

    def test_screen_h(self):
        assert SCREEN_H == 192

    def test_viewport_w(self):
        assert VIEWPORT_W == 320

    def test_viewport_h(self):
        assert VIEWPORT_H == 176

    def test_hud_h(self):
        assert HUD_H == 16

    def test_cull_margin(self):
        assert CULL_MARGIN == 16

    def test_screen_h_equals_viewport_h_plus_hud_h(self):
        """Consistency invariant: SCREEN_H == VIEWPORT_H + HUD_H."""
        assert SCREEN_H == VIEWPORT_H + HUD_H

    def test_viewport_w_tile_aligned(self):
        """VIEWPORT_W must be evenly divisible by TILE_SIZE."""
        assert VIEWPORT_W % TILE_SIZE == 0

    def test_viewport_h_tile_aligned(self):
        """VIEWPORT_H must be evenly divisible by TILE_SIZE."""
        assert VIEWPORT_H % TILE_SIZE == 0
