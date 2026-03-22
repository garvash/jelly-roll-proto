import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock pyxel
mock_pyxel = MagicMock()
sys.modules["pyxel"] = mock_pyxel

from src.entities.projectile import Projectile

@pytest.fixture
def mock_level():
    level = MagicMock()
    level.check_collision.return_value = False
    return level

def test_projectile_normal_spawn(mock_level):
    # Spawn in empty space
    mock_level.check_collision.return_value = False
    proj = Projectile(10, 10, 1, 0, mock_level)
    assert proj.is_active == True

def test_projectile_point_blank_collision(mock_level):
    # Spawn INSIDE a wall
    mock_level.check_collision.return_value = True
    proj = Projectile(10, 10, 1, 0, mock_level)
    
    # It should immediately be inactive
    assert proj.is_active == False
    
    # Update should return a JuiceStain and remain inactive
    with patch("src.entities.stain.JuiceStain") as mock_stain:
        stain = proj.update(0, 0)
        assert stain is not None
        mock_stain.assert_called_once_with(10, 10)
