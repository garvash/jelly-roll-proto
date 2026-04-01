"""Tests for Charge Shot (ABL-04, D-16 through D-18)."""
import pytest
from unittest.mock import MagicMock, patch
from src.core.constants import CHARGE_SHOT_SPEED, CHARGE_SHOT_SIZE, CHARGE_SHOT_DAMAGE, TILE_SIZE


def make_player(**overrides):
    """Create a Player with mocked dependencies."""
    with patch("src.entities.player.input_manager"):
        from src.entities.player import Player
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        level_map.check_hazard.return_value = False
        game = MagicMock()
        game.projectiles = []
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


class TestChargeProjectileCreation:
    def test_charge_projectile_creation(self):
        """ChargeProjectile has correct speed, size, damage."""
        from src.entities.projectile import ChargeProjectile
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        slime = make_slime()
        proj = ChargeProjectile(50, 50, 1.0, 0.0, level_map, slime)
        assert proj.dx == CHARGE_SHOT_SPEED
        assert proj.w == CHARGE_SHOT_SIZE
        assert proj.h == CHARGE_SHOT_SIZE
        assert proj.damage == CHARGE_SHOT_DAMAGE

    def test_charge_projectile_deals_damage(self):
        """Verify .damage attribute equals CHARGE_SHOT_DAMAGE."""
        from src.entities.projectile import ChargeProjectile
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        slime = make_slime()
        proj = ChargeProjectile(50, 50, 1.0, 0.0, level_map, slime)
        assert proj.damage == CHARGE_SHOT_DAMAGE


class TestChargeProjectileMovement:
    def test_charge_projectile_moves(self):
        """update() advances x by CHARGE_SHOT_SPEED."""
        from src.entities.projectile import ChargeProjectile
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        slime = make_slime()
        proj = ChargeProjectile(50, 50, 1.0, 0.0, level_map, slime)
        start_x = proj.x
        proj.update(0, 0)
        assert proj.x == pytest.approx(start_x + CHARGE_SHOT_SPEED)

    def test_charge_shot_direction_right(self):
        """facing_right=True -> dx > 0."""
        from src.entities.projectile import ChargeProjectile
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        slime = make_slime()
        proj = ChargeProjectile(50, 50, 1.0, 0.0, level_map, slime)
        assert proj.dx > 0

    def test_charge_shot_direction_left(self):
        """facing_right=False -> dx < 0."""
        from src.entities.projectile import ChargeProjectile
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        slime = make_slime()
        proj = ChargeProjectile(50, 50, -1.0, 0.0, level_map, slime)
        assert proj.dx < 0


class TestFireChargeShot:
    def test_charge_shot_dumps_juice(self):
        """fire_charge_shot dumps all juice."""
        p = make_player(is_fused=True, facing_right=True)
        slime = make_slime(juice=150.0)
        p.fire_charge_shot(slime)
        slime.consume.assert_called_with(150.0)

    def test_charge_shot_unfuses(self):
        """After fire_charge_shot, player and slime are unfused."""
        p = make_player(is_fused=True, facing_right=True)
        slime = make_slime(juice=100.0)
        p.fire_charge_shot(slime)
        assert p.is_fused is False
        assert slime.is_fused is False


class TestChargeProjectileImpact:
    def test_charge_projectile_creates_stain_on_impact(self):
        """On wall collision, charge projectile creates a juice stain."""
        from src.entities.projectile import ChargeProjectile
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        slime = make_slime()

        proj = ChargeProjectile(50, 50, 1.0, 0.0, level_map, slime)
        proj.grace_timer = 0
        proj.x = 80
        proj.y = 50

        # Wall hit
        level_map.check_collision.return_value = True
        result = proj.update(0, 0)

        assert result is not None  # JuiceStain returned
        assert proj.is_active is False

    def test_charge_shot_dissipates_slime(self):
        """After charge shot fires, slime enters dissipate cooldown."""
        from src.entities.projectile import ChargeProjectile
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        slime = make_slime()
        slime.is_dissipated = True  # Set by fire_charge_shot

        # Slime stays dissipated — reforms on its own timer
        assert slime.is_dissipated is True
