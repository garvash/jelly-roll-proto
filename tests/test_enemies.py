import pytest
from unittest.mock import MagicMock
from src.entities.enemies import Snail, Bat
from src.entities.player import Player

def test_snail_turn_at_wall():
    level_map = MagicMock()
    # Mock collision at x=10+0.5=10.5
    def mock_collision(x, y, w, h):
        return x > 10
    level_map.check_collision = mock_collision
    
    snail = Snail(10, 10)
    snail.dx = 0.5
    
    player = MagicMock()
    player.x = 0
    player.y = 0
    player.w = 10
    player.h = 14
    
    snail.update(player, level_map)
    
    assert snail.dx == -0.5
    assert snail.facing_right == False

def test_snail_turn_at_ledge():
    level_map = MagicMock()
    # Mock ground only at current position, not ahead
    def mock_collision(x, y, w, h):
        if y > 10: # Ground check
            return x < 11
        return False
    level_map.check_collision = mock_collision
    
    snail = Snail(10, 10)
    snail.dx = 0.5
    
    player = MagicMock()
    player.x = 0
    player.y = 0
    player.w = 10
    player.h = 14
    
    snail.update(player, level_map)
    
    assert snail.dx == -0.5

def test_bat_dive_logic():
    level_map = MagicMock()
    level_map.check_collision.return_value = False
    
    bat = Bat(100, 10)
    player = MagicMock()
    player.x = 110 # Close horizontally
    player.y = 50  # Below bat
    player.w = 10
    player.h = 14
    
    bat.update(player, level_map)
    assert bat.state == "DIVING"
    
    bat.update(player, level_map)
    assert bat.y > 10 # Moving down

def test_enemy_death():
    snail = Snail(10, 10)
    snail.take_damage()
    assert snail.is_alive == False


# --- Phase 33 D-17 / Open-Q #1: stun_timer primitive (Plan 03 Task 1) -------
# These tests verify the Enemy base class exposes a `stun_timer` field that
# subclass `update()` honors via early-return when > 0. Plan 04 (daze-shot)
# is the first call site to set stun_timer to a non-zero value; this plan
# only ships the primitive (Wave 2 groundwork).


def test_enemy_base_initializes_stun_timer_zero():
    """W#5 closure: Snail() instance has stun_timer=0 from base __init__."""
    snail = Snail(0, 0)
    assert snail.stun_timer == 0


def test_bat_initializes_stun_timer_zero():
    """W#5 closure: Bat() instance has stun_timer=0 from base __init__ via super()."""
    bat = Bat(0, 0)
    assert bat.stun_timer == 0


def test_snail_update_early_returns_when_stunned():
    """When stun_timer > 0, Snail.update decrements it and returns BEFORE
    advancing position/AI. Movement frozen until timer reaches 0."""
    level_map = MagicMock()
    level_map.check_collision.return_value = False

    snail = Snail(10, 10)
    snail.stun_timer = 3
    snail.dx = 0.5
    initial_x = snail.x
    initial_y = snail.y

    player = MagicMock()
    player.x = 0
    player.y = 0
    player.w = 10
    player.h = 14

    snail.update(player, level_map)

    # Timer ticked down by exactly 1.
    assert snail.stun_timer == 2
    # Movement frozen — no advance in either axis.
    assert snail.x == initial_x
    assert snail.y == initial_y


def test_bat_update_early_returns_when_stunned():
    """Bat.update honors stun_timer the same way Snail.update does."""
    level_map = MagicMock()
    level_map.check_collision.return_value = False

    bat = Bat(100, 10)
    bat.stun_timer = 5
    initial_state = bat.state
    initial_y = bat.y

    player = MagicMock()
    player.x = 110
    player.y = 50
    player.w = 10
    player.h = 14

    bat.update(player, level_map)

    assert bat.stun_timer == 4
    # State machine frozen — no transition into DIVING.
    assert bat.state == initial_state
    assert bat.y == initial_y


def test_snail_update_runs_normally_when_stun_timer_zero():
    """Default path (stun_timer=0) preserves prior behavior: Snail still
    turns at walls. Same setup as test_snail_turn_at_wall."""
    level_map = MagicMock()

    def mock_collision(x, y, w, h):
        return x > 10

    level_map.check_collision = mock_collision

    snail = Snail(10, 10)
    assert snail.stun_timer == 0  # default
    snail.dx = 0.5

    player = MagicMock()
    player.x = 0
    player.y = 0
    player.w = 10
    player.h = 14

    snail.update(player, level_map)

    assert snail.dx == -0.5
    assert snail.facing_right == False
