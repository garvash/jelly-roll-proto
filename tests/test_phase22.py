"""Phase 22: Entity alignment regression tests.

Validates all entity collision boxes match 16x16 visual sprites after migration,
and that physics constants and door dimensions remain unchanged.
"""
import json
import pytest
from unittest.mock import MagicMock
import sys

# Mock pyxel before importing game modules
sys.modules.setdefault('pyxel', MagicMock())

from src.entities.enemies import Enemy, Snail, Bat
from src.entities.boss import BossRock, Mole
from src.entities.slime import Slime
from src.entities.player import Player
from src.entities.map_entities import Door
from src.core.constants import GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, TILE_SIZE


# --- Fixtures ---

class MockLevelMap:
    """Minimal level map mock for Player/Mole instantiation."""
    def __init__(self):
        self.w = 320
        self.h = 176
        self.entities = []

    def get_tile(self, tx, ty):
        return None

    def check_collision(self, x, y, w, h):
        return False


class MockGame:
    """Minimal game mock providing effects list."""
    def __init__(self):
        self.effects = []


# --- ENT-01, D-01: Player hitbox unchanged ---

def test_player_hitbox():
    level_map = MockLevelMap()
    game = MockGame()
    player = Player(0, 0, level_map, game)
    assert player.w == 10, f"Player width should be 10, got {player.w}"
    assert player.h == 14, f"Player height should be 14, got {player.h}"


# --- ENT-02: Enemy hitboxes 16x16 ---

def test_enemy_base_hitbox():
    enemy = Enemy(0, 0)
    assert enemy.w == 16, f"Enemy base width should be 16, got {enemy.w}"
    assert enemy.h == 16, f"Enemy base height should be 16, got {enemy.h}"


def test_snail_hitbox():
    snail = Snail(0, 0)
    assert snail.w == 16, f"Snail width should be 16, got {snail.w}"
    assert snail.h == 16, f"Snail height should be 16, got {snail.h}"


def test_bat_hitbox():
    bat = Bat(0, 0)
    assert bat.w == 16, f"Bat width should be 16, got {bat.w}"
    assert bat.h == 16, f"Bat height should be 16, got {bat.h}"


# --- D-05: Slime hitbox 16x16 ---

def test_slime_hitbox():
    slime = Slime(0, 0)
    assert slime.w == 16, f"Slime width should be 16, got {slime.w}"
    assert slime.h == 16, f"Slime height should be 16, got {slime.h}"


# --- ENT-03, D-04: Mole hitbox 24x28 ---

def test_boss_hitbox():
    level_map = MockLevelMap()
    mole = Mole(0, 0, level_map)
    assert mole.w == 24, f"Mole width should be 24, got {mole.w}"
    assert mole.h == 28, f"Mole height should be 28, got {mole.h}"


# --- D-05: BossRock hitbox 16x16 ---

def test_boss_rock_hitbox():
    rock = BossRock(0, 0, 1, 0)
    assert rock.w == 16, f"BossRock width should be 16, got {rock.w}"
    assert rock.h == 16, f"BossRock height should be 16, got {rock.h}"


# --- ENT-05, D-06: Effect draw uses 16x16 collision size ---

def test_draw_offset_simplified():
    """Verify Effect draw call passes 16, 16 as collision w/h."""
    from src.entities.effects import Effect
    effect = Effect(10, 20, "EXPLOSION")
    # Patch draw_sprite to capture call args
    import src.entities.effects as effects_mod
    original_draw = effects_mod.draw_sprite
    calls = []
    def capture_draw(*args, **kwargs):
        calls.append(args)
    effects_mod.draw_sprite = capture_draw
    try:
        effect.draw(0, 0)
        assert len(calls) == 1, f"Expected 1 draw_sprite call, got {len(calls)}"
        # draw_sprite(x, y, w, h, bank, u, v, sw, sh, flip)
        # args[2] and args[3] are the collision w and h
        assert calls[0][2] == 16, f"Effect collision w should be 16, got {calls[0][2]}"
        assert calls[0][3] == 16, f"Effect collision h should be 16, got {calls[0][3]}"
    finally:
        effects_mod.draw_sprite = original_draw


# --- ENT-04, D-02: Door dimensions match LDtk entity sizes ---

def test_door_vertical_dimensions():
    door = Door(0, 0, direction="right")
    assert door.w == 16, f"Side door width should be 16 (1 tile), got {door.w}"
    assert door.h == 32, f"Side door height should be 32 (2 tiles), got {door.h}"


def test_door_horizontal_dimensions():
    door = Door(0, 0, direction="up")
    assert door.w == 32, f"Top/bottom door width should be 32 (2 tiles), got {door.w}"
    assert door.h == 16, f"Top/bottom door height should be 16 (1 tile), got {door.h}"


def test_door_ldtk_width_height_override():
    door = Door(0, 0, direction="right", width=24, height=48)
    assert door.w == 24, f"Door should use LDtk width, got {door.w}"
    assert door.h == 48, f"Door should use LDtk height, got {door.h}"


# --- PHYS-01, D-03: Physics constants unchanged ---

def test_physics_constants_unchanged():
    assert GRAVITY == 0.0875, f"GRAVITY should be 0.0875, got {GRAVITY}"
    assert JUMP_FORCE == -3.25, f"JUMP_FORCE should be -3.25, got {JUMP_FORCE}"
    assert MAX_WALK_SPEED == 1.25, f"MAX_WALK_SPEED should be 1.25, got {MAX_WALK_SPEED}"


# --- PHYS-02: Passage clearance ---

def test_passage_clearance():
    """Player fits in a 1-tile passage: w < TILE_SIZE and h < TILE_SIZE."""
    level_map = MockLevelMap()
    game = MockGame()
    player = Player(0, 0, level_map, game)
    assert player.w < TILE_SIZE, f"Player w={player.w} must be < TILE_SIZE={TILE_SIZE}"
    assert player.h < TILE_SIZE, f"Player h={player.h} must be < TILE_SIZE={TILE_SIZE}"


# --- PHYS-03: Physics schema updated ---

def test_physics_schema_updated():
    """physics-schema.json reflects 16x16 base values (v0.3.0 layout)."""
    with open("assets/physics-schema.json", "r") as f:
        d = json.load(f)
    assert d["tile_size"] == 16, f"Schema tile_size should be 16, got {d['tile_size']}"
    assert d["derived"]["player"]["hitbox_px"] == [10, 14], (
        f"Schema derived.player.hitbox_px should be [10, 14], got {d['derived']['player']['hitbox_px']}"
    )
    assert d["tuning"]["movement"]["GRAVITY"] == 0.0875, (
        f"Schema tuning.movement.GRAVITY should be 0.0875, got {d['tuning']['movement']['GRAVITY']}"
    )
