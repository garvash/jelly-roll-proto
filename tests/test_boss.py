import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock pyxel
sys.modules['pyxel'] = MagicMock()

from src.entities.boss import Mole
from src.entities.projectile import Projectile
from src.entities.player import Player

class MockLevelMap:
    def check_collision(self, x, y, w, h):
        return False

def test_projectile_movement():
    level_map = MockLevelMap()
    proj = Projectile(10, 10, 1, 0, level_map)
    proj.update()
    assert proj.x > 10
    assert proj.is_active

def test_boss_fsm_stun():
    level_map = MockLevelMap()
    mole = Mole(50, 50, level_map)
    mole.state = "EMERGING"
    
    # Create a projectile hitting the mole
    proj = Projectile(50, 50, 1, 0, level_map)
    player = MagicMock()
    player.x, player.y = 0, 0
    player.w, player.h = 8, 8
    mole.update([proj], player)
    
    assert mole.state == "VULNERABLE"
    assert not proj.is_active

def test_boss_damage_only_vulnerable():
    level_map = MockLevelMap()
    mole = Mole(50, 50, level_map)
    player = MagicMock()
    player.state = "DIVING"
    player.x, player.y = 50, 50
    player.w, player.h = 8, 8
    
    # Try to damage while EMERGING
    mole.state = "EMERGING"
    mole.update([], player)
    assert mole.hp == 3
    
    # Stun it first
    mole.state = "VULNERABLE"
    mole.update([], player)
    assert mole.hp == 2
    assert mole.state == "BURROWED" # Resets after hit
