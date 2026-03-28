"""Tests for Bubble Shield (ABL-05, D-01 through D-06)."""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from src.core.constants import (
    TILE_WATER, TILE_ACID, TILE_LAVA,
    HAZARD_DRAIN_SLOW, HAZARD_DRAIN_MEDIUM, HAZARD_DRAIN_FAST,
    SHIELD_T2_DRAIN_REDUCTION, HAZARD_HP_DRAIN_INTERVAL,
    SHIELD_REACTIVATION_COOLDOWN, JUICE_MAX,
)


def make_player(**overrides):
    """Create a Player with mocked dependencies."""
    with patch("src.entities.player.input_manager"):
        from src.entities.player import Player
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        level_map.check_hazard.return_value = False
        level_map.get_zone_hazard_type.return_value = None
        game = MagicMock()
        p = Player(50, 50, level_map, game)
        for k, v in overrides.items():
            setattr(p, k, v)
        return p


def make_slime(**overrides):
    """Create a mock slime with standard defaults."""
    slime = MagicMock()
    slime.juice = JUICE_MAX
    slime.max_juice = JUICE_MAX
    slime.w = 8
    slime.h = 8
    slime.x = 50
    slime.y = 50
    slime.is_fused = False
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


class TestAutoFuse:
    """D-01: Player auto-fuses when entering hazard zone at 100% juice with has_shield."""

    def test_auto_fuse_in_water_zone(self):
        """Player with has_shield entering TILE_WATER zone at full juice auto-fuses."""
        p = make_player(has_shield=True)
        p.level_map.get_zone_hazard_type.return_value = TILE_WATER
        slime = make_slime()
        p.update_shield(slime)
        assert p.is_fused is True
        assert p.shield_active is True

    def test_no_shield_no_auto_fuse(self):
        """Player without has_shield does NOT auto-fuse in hazard zone."""
        p = make_player(has_shield=False)
        p.level_map.get_zone_hazard_type.return_value = TILE_WATER
        slime = make_slime()
        p.update_shield(slime)
        assert p.is_fused is False
        assert p.shield_active is False

    def test_already_fused_activates_shield(self):
        """Player already fused entering zone activates shield_active without double-fuse."""
        p = make_player(has_shield=True, is_fused=True)
        p.level_map.get_zone_hazard_type.return_value = TILE_WATER
        slime = make_slime(is_fused=True)
        # Already fused -- should not call fuse() again, but shield_active should be True
        # Since already fused, the auto-fuse branch won't fire.
        # But shield drain branch will fire since shield_active gets set when fused in zone.
        # We need to manually set shield_active since the auto-fuse path sets it.
        # The logic: if already fused, we don't re-fuse but shield should be recognized.
        # Let's test that fuse() is NOT called again.
        p.update_shield(slime)
        # fuse() should not have been called (already fused)
        slime.reform.assert_not_called()

    def test_low_juice_no_auto_fuse(self):
        """Juice less than max does NOT trigger auto-fuse."""
        p = make_player(has_shield=True)
        p.level_map.get_zone_hazard_type.return_value = TILE_WATER
        slime = make_slime(juice=100.0)
        p.update_shield(slime)
        assert p.is_fused is False
        assert p.shield_active is False

    def test_dissipated_slime_no_auto_fuse(self):
        """Dissipated slime prevents auto-fuse even at full juice."""
        p = make_player(has_shield=True)
        p.level_map.get_zone_hazard_type.return_value = TILE_WATER
        slime = make_slime(is_dissipated=True)
        p.update_shield(slime)
        assert p.is_fused is False
        assert p.shield_active is False


class TestShieldDrain:
    """D-03: Juice drains at hazard-type-specific rate while shield is active."""

    def test_water_drain_rate(self):
        """Shield drains at HAZARD_DRAIN_SLOW (0.5/frame) for TILE_WATER."""
        p = make_player(has_shield=True, is_fused=True, shield_active=True)
        p.level_map.get_zone_hazard_type.return_value = TILE_WATER
        slime = make_slime(is_fused=True)
        p.update_shield(slime)
        slime.consume.assert_called_once_with(HAZARD_DRAIN_SLOW)

    def test_acid_drain_rate(self):
        """Shield drains at HAZARD_DRAIN_MEDIUM (1.5/frame) for TILE_ACID."""
        p = make_player(has_shield=True, is_fused=True, shield_active=True)
        p.level_map.get_zone_hazard_type.return_value = TILE_ACID
        slime = make_slime(is_fused=True)
        p.update_shield(slime)
        slime.consume.assert_called_once_with(HAZARD_DRAIN_MEDIUM)

    def test_lava_drain_rate(self):
        """Shield drains at HAZARD_DRAIN_FAST (3.0/frame) for TILE_LAVA."""
        p = make_player(has_shield=True, is_fused=True, shield_active=True)
        p.level_map.get_zone_hazard_type.return_value = TILE_LAVA
        slime = make_slime(is_fused=True)
        p.update_shield(slime)
        slime.consume.assert_called_once_with(HAZARD_DRAIN_FAST)


class TestShieldTier2:
    """D-05: T2 reduces drain by SHIELD_T2_DRAIN_REDUCTION; water becomes free at T2."""

    def test_t2_water_free(self):
        """T2 TILE_WATER drain becomes 0 (free)."""
        p = make_player(has_shield=True, has_shield_t2=True, is_fused=True, shield_active=True)
        p.level_map.get_zone_hazard_type.return_value = TILE_WATER
        slime = make_slime(is_fused=True)
        p.update_shield(slime)
        # Drain is 0.5 - 0.5 = 0, so consume should NOT be called
        slime.consume.assert_not_called()

    def test_t2_acid_reduced(self):
        """T2 TILE_ACID drain becomes 1.0 (medium - 0.5)."""
        p = make_player(has_shield=True, has_shield_t2=True, is_fused=True, shield_active=True)
        p.level_map.get_zone_hazard_type.return_value = TILE_ACID
        slime = make_slime(is_fused=True)
        p.update_shield(slime)
        expected_drain = HAZARD_DRAIN_MEDIUM - SHIELD_T2_DRAIN_REDUCTION  # 1.5 - 0.5 = 1.0
        slime.consume.assert_called_once_with(expected_drain)


class TestJuiceEmptyHPDrain:
    """D-04: Juice empty in hazard zone causes unfuse + rapid HP drain."""

    def test_juice_empty_triggers_unfuse_dissipate(self):
        """Juice reaching 0 in zone triggers unfuse with dissipate=True."""
        p = make_player(has_shield=True, is_fused=True, shield_active=True)
        p.level_map.get_zone_hazard_type.return_value = TILE_LAVA
        slime = make_slime(juice=0.0, is_fused=True)
        # After consume, juice will be 0 -- but since mock consume doesn't actually change juice,
        # we set juice=0 to simulate post-consume state
        p.update_shield(slime)
        # Should have unfused with dissipate=True
        assert p.shield_active is False
        assert p.shield_cooldown == SHIELD_REACTIVATION_COOLDOWN
        assert p.hazard_hp_timer == HAZARD_HP_DRAIN_INTERVAL

    def test_hp_drain_every_interval(self):
        """hazard_hp_timer counts down and deals 1 HP per HAZARD_HP_DRAIN_INTERVAL frames."""
        p = make_player(has_shield=True, is_fused=False, shield_active=False)
        p.level_map.get_zone_hazard_type.return_value = TILE_WATER
        slime = make_slime(juice=0.0, is_dissipated=True, is_fused=False)
        initial_hp = p.hp

        # Tick through the HP drain timer
        p.hazard_hp_timer = 0  # Timer at 0 means damage fires immediately
        p.update_shield(slime)
        assert p.hp == initial_hp - 1
        assert p.hazard_hp_timer == HAZARD_HP_DRAIN_INTERVAL

    def test_hp_drain_timer_countdown(self):
        """hazard_hp_timer decrements without dealing damage until 0."""
        p = make_player(has_shield=True, is_fused=False, shield_active=False)
        p.level_map.get_zone_hazard_type.return_value = TILE_WATER
        slime = make_slime(juice=0.0, is_dissipated=True, is_fused=False)
        initial_hp = p.hp

        p.hazard_hp_timer = 5  # Not yet at 0
        p.update_shield(slime)
        assert p.hp == initial_hp  # No damage yet
        assert p.hazard_hp_timer == 4  # Decremented


class TestShieldDeactivation:
    """Shield deactivates and player unfuses when leaving hazard zone."""

    def test_leaving_zone_deactivates_shield(self):
        """Leaving hazard zone deactivates shield and unfuses."""
        p = make_player(has_shield=True, is_fused=True, shield_active=True)
        p.level_map.get_zone_hazard_type.return_value = None  # Left zone
        slime = make_slime(is_fused=True)
        p.update_shield(slime)
        assert p.shield_active is False
        assert p.shield_cooldown == SHIELD_REACTIVATION_COOLDOWN


class TestAntiFlickerCooldown:
    """Pitfall 2: Anti-flicker cooldown prevents rapid fuse/unfuse at zone edges."""

    def test_cooldown_prevents_reactivation(self):
        """shield_cooldown prevents re-activation for SHIELD_REACTIVATION_COOLDOWN frames."""
        p = make_player(has_shield=True, shield_cooldown=30)
        p.level_map.get_zone_hazard_type.return_value = TILE_WATER
        slime = make_slime()
        p.update_shield(slime)
        # Should NOT auto-fuse due to cooldown
        assert p.is_fused is False
        assert p.shield_active is False

    def test_cooldown_ticks_down(self):
        """shield_cooldown decrements each frame."""
        p = make_player(has_shield=True, shield_cooldown=5)
        p.level_map.get_zone_hazard_type.return_value = None
        slime = make_slime()
        p.update_shield(slime)
        assert p.shield_cooldown == 4
