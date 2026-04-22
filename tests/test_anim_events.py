"""Phase 31 ANIM-04 / ANIM-06 event subscriber + particle integration tests."""
import sys
import math
from unittest.mock import MagicMock, patch
sys.modules.setdefault("pyxel", MagicMock())

import pytest


# ---------------------------------------------------------------------------
# Plan 31-03 Task 2: sprite-backed Particle
# ---------------------------------------------------------------------------

def test_particle_constructor_keyword_only():
    from src.entities.effects import Particle
    p = Particle(0, 0, dx=1.0, dy=0.5, life=10, bank_u=0, bank_v=0)
    assert p.x == 0 and p.y == 0
    assert p.dx == 1.0 and p.dy == 0.5
    assert p.life == 10
    assert p.bank_u == 0 and p.bank_v == 0
    assert p.is_active is True
    # positional past (x, y) must fail
    with pytest.raises(TypeError):
        Particle(0, 0, 1.0, 0.5, 10, 0, 0)


def test_particle_update_decrements_life():
    from src.entities.effects import Particle
    p = Particle(0, 0, dx=0, dy=0, life=3, bank_u=0, bank_v=0)
    for _ in range(3):
        assert p.is_active is True
        p.update()
    assert p.is_active is False


def test_particle_draw_uses_bank_2():
    from src.entities.effects import Particle
    p = Particle(50, 50, dx=0, dy=0, life=10, bank_u=0, bank_v=0)
    with patch("src.entities.effects.draw_sprite") as mock_draw:
        p.draw(0, 0)
    assert mock_draw.call_count == 1
    args, kwargs = mock_draw.call_args
    # draw_sprite(x, y, coll_w, coll_h, bank, u, v, visual_w, visual_h, facing_right)
    # bank is positional arg index 4.
    assert args[4] == 2, f"Particle must draw from bank 2, got bank {args[4]}"


def test_particle_draw_skips_when_inactive():
    from src.entities.effects import Particle
    p = Particle(50, 50, dx=0, dy=0, life=10, bank_u=0, bank_v=0)
    p.is_active = False
    with patch("src.entities.effects.draw_sprite") as mock_draw:
        p.draw(0, 0)
    assert mock_draw.call_count == 0


# ---------------------------------------------------------------------------
# Plan 31-03 Task 3: drill_block_break subscriber integration
# ---------------------------------------------------------------------------

def test_drill_block_break_spawns_burst_and_pauses_anim():
    """Phase 31 D-06 + D-16: drill_block_break handler pauses drill spin AND
    spawns a diverging burst. Tests the handler logic independent of main.py."""
    from src.anim import event_bus
    from src.anim.player_anim import DRILL_RECOIL_PAUSE_FRAMES

    class FakeAnim:
        def __init__(self):
            self.pause_for_calls = []
        def pause_for(self, n):
            self.pause_for_calls.append(n)

    class FakePlayer:
        def __init__(self):
            self._anim = FakeAnim()

    class FakeGame:
        def __init__(self):
            self.player = FakePlayer()
            self.particles = []

    game = FakeGame()
    import main as main_mod
    from src.entities.effects import Particle

    def _on_drill_block_break(tx=None, ty=None, **kw):
        game.player._anim.pause_for(DRILL_RECOIL_PAUSE_FRAMES)
        cx = tx * 16 + 4
        cy = ty * 16 + 4
        for i in range(main_mod.BURST_PARTICLE_COUNT):
            angle = (2 * math.pi * i) / main_mod.BURST_PARTICLE_COUNT
            game.particles.append(Particle(
                cx, cy,
                dx=math.cos(angle) * main_mod.BURST_PARTICLE_SPEED,
                dy=math.sin(angle) * main_mod.BURST_PARTICLE_SPEED,
                life=main_mod.BURST_PARTICLE_LIFE,
                bank_u=main_mod.PARTICLE_BURST_U,
                bank_v=main_mod.PARTICLE_BURST_V,
            ))

    event_bus.subscribe("drill_block_break", _on_drill_block_break)
    event_bus.emit("drill_block_break", tx=5, ty=7)

    assert game.player._anim.pause_for_calls == [DRILL_RECOIL_PAUSE_FRAMES]
    assert len(game.particles) == main_mod.BURST_PARTICLE_COUNT


def test_drill_block_break_particles_at_tile_center():
    """Spawned particles originate at the tile center (tx*16+4, ty*16+4)."""
    from src.anim import event_bus
    from src.entities.effects import Particle
    import main as main_mod

    class FakeAnim:
        def pause_for(self, n): pass
    class FakePlayer:
        def __init__(self):
            self._anim = FakeAnim()
    class FakeGame:
        def __init__(self):
            self.player = FakePlayer()
            self.particles = []

    game = FakeGame()

    def _sub(tx=None, ty=None, **kw):
        cx, cy = tx * 16 + 4, ty * 16 + 4
        for i in range(main_mod.BURST_PARTICLE_COUNT):
            angle = (2 * math.pi * i) / main_mod.BURST_PARTICLE_COUNT
            game.particles.append(Particle(
                cx, cy,
                dx=math.cos(angle) * main_mod.BURST_PARTICLE_SPEED,
                dy=math.sin(angle) * main_mod.BURST_PARTICLE_SPEED,
                life=main_mod.BURST_PARTICLE_LIFE,
                bank_u=0, bank_v=0,
            ))
    event_bus.subscribe("drill_block_break", _sub)
    event_bus.emit("drill_block_break", tx=5, ty=7)
    # Tile center at (5*16+4, 7*16+4) = (84, 116)
    assert all(p.x == 84 for p in game.particles)
    assert all(p.y == 116 for p in game.particles)
