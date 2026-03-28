"""Tests for Slime Ram (ABL-01, D-12 through D-14)."""
import pytest
from unittest.mock import MagicMock, patch
from src.core.constants import (
    RAM_SPEED, RAM_BLOCK_COST, RAM_DIAGONAL_FACTOR,
    TILE_CRACKED_H, TILE_SOLID, TILE_SIZE, DASH_IFRAMES
)


def make_player(**overrides):
    """Create a Player with mocked dependencies."""
    with patch("src.entities.player.input_manager"):
        from src.entities.player import Player
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        level_map.check_hazard.return_value = False
        game = MagicMock()
        p = Player(50, 50, level_map, game)
        for k, v in overrides.items():
            setattr(p, k, v)
        return p


def make_slime(**overrides):
    """Create a mock slime with standard defaults."""
    slime = MagicMock()
    slime.juice = 200.0
    slime.max_juice = 200.0
    slime.w = 8
    slime.h = 8
    slime.x = 50
    slime.y = 50
    slime.is_fused = True
    slime.is_dissipated = False
    slime.is_recalling = False
    slime.is_punted = False
    slime.is_holding_position = False
    slime.dx = 0
    slime.dy = 0
    slime.history = MagicMock()
    for k, v in overrides.items():
        setattr(slime, k, v)
    return slime


class TestStartRam:
    @patch("src.entities.player.input_manager")
    def test_ram_sets_state(self, mock_input):
        mock_input.btn.return_value = False
        p = make_player(is_fused=True, facing_right=True)
        slime = make_slime()
        p.start_ram(slime)
        assert p.state == "RAMMING"

    @patch("src.entities.player.input_manager")
    def test_ram_speed_right(self, mock_input):
        mock_input.btn.return_value = False
        p = make_player(is_fused=True, facing_right=True)
        slime = make_slime()
        p.start_ram(slime)
        assert p.ram_dx == RAM_SPEED

    @patch("src.entities.player.input_manager")
    def test_ram_speed_left(self, mock_input):
        mock_input.btn.return_value = False
        p = make_player(is_fused=True, facing_right=False)
        slime = make_slime()
        p.start_ram(slime)
        assert p.ram_dx == -RAM_SPEED

    @patch("src.entities.player.input_manager")
    def test_ram_invincible(self, mock_input):
        mock_input.btn.return_value = False
        p = make_player(is_fused=True)
        slime = make_slime()
        p.start_ram(slime)
        assert p.invuln_timer > 0

    @patch("src.entities.player.input_manager")
    def test_ram_diagonal_up(self, mock_input):
        def btn_side(action):
            return action == "up"
        mock_input.btn.side_effect = btn_side
        p = make_player(is_fused=True, facing_right=True)
        slime = make_slime()
        p.start_ram(slime)
        assert p.ram_dy == pytest.approx(-RAM_SPEED * RAM_DIAGONAL_FACTOR)


class TestRamCollision:
    def test_ram_breaks_cracked_h(self):
        """RAMMING state + CRACKED_H tile = tile removed, juice consumed."""
        p = make_player(is_fused=True, facing_right=True, state="RAMMING")
        p.ram_dx = RAM_SPEED
        p.ram_dy = 0
        slime = make_slime(juice=200.0)

        # First call: horizontal move triggers collision
        p.level_map.check_collision.return_value = True
        p.level_map.get_cracked_h_at.return_value = (7, 5)
        p.level_map.check_hazard.return_value = False

        p.dx = RAM_SPEED
        p.move_and_collide(slime)

        p.level_map.remove_tile.assert_called_with(7, 5)
        slime.consume.assert_called_with(RAM_BLOCK_COST)
        assert p.state == "RAMMING"  # Continues through

    def test_ram_stops_at_solid(self):
        """RAMMING + solid (no CRACKED_H) = ram ends."""
        p = make_player(is_fused=True, facing_right=True, state="RAMMING")
        p.ram_dx = RAM_SPEED
        p.ram_dy = 0
        slime = make_slime(juice=200.0)

        p.level_map.check_collision.return_value = True
        p.level_map.get_cracked_h_at.return_value = None
        p.level_map.check_hazard.return_value = False

        p.dx = RAM_SPEED
        p.move_and_collide(slime)

        assert p.state != "RAMMING"

    def test_ram_continues_through_cracked(self):
        """After breaking CRACKED_H with juice remaining, state stays RAMMING."""
        p = make_player(is_fused=True, facing_right=True, state="RAMMING")
        p.ram_dx = RAM_SPEED
        slime = make_slime(juice=200.0)

        p.level_map.check_collision.return_value = True
        p.level_map.get_cracked_h_at.return_value = (7, 5)
        p.level_map.check_hazard.return_value = False

        p.dx = RAM_SPEED
        p.move_and_collide(slime)

        assert p.state == "RAMMING"

    def test_ram_ends_on_juice_empty(self):
        """Juice exactly enough for one block -> ram ends after breaking it."""
        p = make_player(is_fused=True, facing_right=True, state="RAMMING")
        p.ram_dx = RAM_SPEED
        slime = make_slime(juice=RAM_BLOCK_COST)

        # After consume, juice should be 0
        def consume_side(amount):
            slime.juice -= amount
        slime.consume.side_effect = consume_side

        p.level_map.check_collision.return_value = True
        p.level_map.get_cracked_h_at.return_value = (7, 5)
        p.level_map.check_hazard.return_value = False

        p.dx = RAM_SPEED
        p.move_and_collide(slime)

        assert p.state != "RAMMING"


    def test_ram_snaps_to_wall_right(self):
        """Ramming right into solid wall: player snaps to left edge of wall tile, not inside it."""
        p = make_player(is_fused=True, facing_right=True, state="RAMMING")
        p.ram_dx = RAM_SPEED
        p.ram_dy = 0
        slime = make_slime(juice=200.0)

        # Player at x=56 moving right, wall tile starts at x=64 (tile column 8)
        p.x = 56
        p.y = 48  # row 6
        p.dx = RAM_SPEED

        # After horizontal move: p.x = 56 + 5 = 61, collision detected
        def check_collision(x, y, w, h):
            # Solid wall at tile column 8 (x >= 64)
            return x + w > 64
        p.level_map.check_collision.side_effect = check_collision
        p.level_map.get_cracked_h_at.return_value = None
        p.level_map.check_hazard.return_value = False

        p.move_and_collide(slime)

        # Player should snap to left edge of wall: tile 8 * TILE_SIZE - player.w = 64 - 8 = 56
        expected_x = 8 * TILE_SIZE - p.w  # 56
        assert p.x == expected_x, f"Player embedded in wall: x={p.x}, expected {expected_x}"
        assert p.dx == 0

    def test_ram_snaps_to_wall_left(self):
        """Ramming left into solid wall: player snaps to right edge of wall tile, not inside it."""
        p = make_player(is_fused=True, facing_right=False, state="RAMMING")
        p.ram_dx = -RAM_SPEED
        p.ram_dy = 0
        slime = make_slime(juice=200.0)

        # Player at x=13 moving left at speed 5, wall tile at column 1 (x=8..15)
        # After move: x = 13 - 5 = 8, overlaps with wall at tile column 0 (x=0..7)
        p.x = 13
        p.y = 48
        p.dx = -RAM_SPEED

        # After horizontal move: p.x = 13 - 5 = 8, collision detected
        def check_collision(x, y, w, h):
            # Wall at tile column 0: anything with left edge < 8 collides
            # Also wall at column 1 occupies x=8..15, so player at x=8 with w=8 overlaps
            # Simulate: wall is solid at x < 9 (wall right edge)
            return x < 9
        p.level_map.check_collision.side_effect = check_collision
        p.level_map.get_cracked_h_at.return_value = None
        p.level_map.check_hazard.return_value = False

        p.move_and_collide(slime)

        # Player x after move = 8. Snap: (int(8 // 8) + 1) * 8 = (1+1)*8 = 16
        expected_x = 16
        assert p.x == expected_x, f"Player embedded in wall: x={p.x}, expected {expected_x}"
        assert p.dx == 0


class TestEndRam:
    @patch("src.entities.player.input_manager")
    def test_end_ram_unfuses(self, mock_input):
        mock_input.btn.return_value = False
        p = make_player(is_fused=True, state="RAMMING")
        slime = make_slime(juice=100.0)
        p.end_ram(slime)
        assert p.is_fused is False
        assert p.invuln_timer == DASH_IFRAMES
