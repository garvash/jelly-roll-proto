---
phase: 31
plan: 03
status: complete
completed: 2026-04-22
test_count_before: 45
test_count_after: 54
new_tests: 9
---

# Plan 31-03 SUMMARY — Particle Bank Separation (ANIM-06)

Separated the particle image bank from the map tileset (D-15), retired
the legacy `effects` slot at bank 1 y=96 (D-16), rewrote `Particle` to
be sprite-backed (D-17), and wired the `drill_block_break` subscriber
that pauses drill spin + spawns a 14-particle diverging burst.

## Final SPRITE_MANIFEST

```python
SPRITE_MANIFEST = {
    "tiles":      (0, 0, 0,   "assets/tiles.png"),
    "player":     (1, 0, 0,   "assets/sprites/player.png"),
    "slime":      (1, 0, 16,  "assets/sprites/slime.png"),
    "snail":      (1, 0, 32,  "assets/sprites/snail.png"),
    "bat":        (1, 0, 48,  "assets/sprites/bat.png"),
    "items":      (1, 0, 64,  "assets/sprites/items.png"),
    "projectile": (1, 0, 80,  "assets/sprites/projectile.png"),
    # Phase 31 D-16: effects entry retired (bank 1 y=96 slot reclaimed)
    "boss":       (1, 0, 128, "assets/sprites/boss.png"),
    "particles":  (2, 0, 0,   "assets/sprites/particles.png"),  # D-15
}
```

JSON sidecar loop now skips both `tiles` and `particles` (neither has a
`.json` sidecar in this phase).

## Retired Artifacts

| Artifact | Status | Rationale |
|----------|--------|-----------|
| `SPRITE_MANIFEST["effects"]` (bank 1 y=96) | Removed | D-16 reclaims slot; bursts come from bank 2 |
| `assets/sprites/effects.png` | Kept on disk | Phase 13 sprite asset tests still reference it; not loaded by manifest |
| `Effect` class | No-op shell | D-16 retire; instances inactive on construct, draw is no-op |
| `Particle(x, y, color)` legacy ctor | Removed | Sprite-backed kwargs-only constructor mandatory |
| `pyxel.pset` in Particle.draw | Removed | All draws via bank-2 `draw_sprite` |

## New Constants Exported (main.py)

| Constant | Value | Purpose |
|----------|-------|---------|
| `BURST_PARTICLE_COUNT` | 14 | Particles spawned per `spawn_particle_burst` call (D-16) |
| `BURST_PARTICLE_SPEED` | 1.5 | Pixels per frame outward |
| `BURST_PARTICLE_LIFE` | 20 | Frames before deactivation |
| `PARTICLE_BURST_U` | 0 | Bank-2 X offset for burst sprite |
| `PARTICLE_BURST_V` | 0 | Bank-2 Y offset |
| `PARTICLE_CONVERGE_U` | 16 | Bank-2 X offset for convergence sprite (Plan 04) |
| `PARTICLE_CONVERGE_V` | 0 | Bank-2 Y offset |

## New Constants Exported (src/entities/effects.py)

| Constant | Value | Purpose |
|----------|-------|---------|
| `PARTICLE_SIZE` | 4 | 4x4 on-screen render size |
| `PARTICLE_GRAVITY` | 0.025 | Inherited from legacy Particle |

## `spawn_particle_burst` Signature & Behavior

```python
def spawn_particle_burst(self, x, y, type="block_break") -> None:
    # Spawns BURST_PARTICLE_COUNT sprite-backed Particles in a radial
    # ring centred on (x + 4, y + 4). Each particle uses bank 2 with
    # bank_u=PARTICLE_BURST_U, bank_v=PARTICLE_BURST_V (4x4 sprite).
    # `type` is reserved for future variants; all current types use
    # the same burst sprite offsets.
```

## drill_block_break Subscriber

**Location:** `main.py:227-256` (inside `Game.__init__`, AFTER
`self.reset()` so `self.player` + `self.particles` exist; BEFORE
`pyxel.run`).

**Effect on emit (`tx`, `ty` are tile-grid coords):**
1. `self.player._anim.pause_for(DRILL_RECOIL_PAUSE_FRAMES)` -- D-06
   animation-only pause (gameplay `DRILL_SPEED` unchanged)
2. Spawns `BURST_PARTICLE_COUNT` particles in a radial ring centred at
   `(tx*TILE_SIZE + 4, ty*TILE_SIZE + 4)` with bank-2 burst sprite

The subscriber listens on the **Plan 02 provisional bridge emit** at
`src/entities/player.py:788-793`. When Phase 32 relocates the canonical
emit to the fusion FSM site, this subscriber remains valid -- it does
not depend on the emit location, only on the event name and kwargs.

## Placeholder Art (Task 1 stubbed via auto-generation)

`assets/sprites/particles.png` (64×32, P-mode, palette preserved):

| Slot | Coords | Content | Marker color |
|------|--------|---------|--------------|
| burst | (0,0)..(15,15) | Bright cross with white centre | yellow/orange |
| convergence | (16,0)..(31,15) | Soft speck | cyan/white |
| blob_growth_0 | (0,16)..(15,31) | Tiny circle r=2 | mint green |
| blob_growth_1 | (16,16)..(31,31) | Medium circle r=4 | mint + dark rim |
| blob_growth_2 | (32,16)..(47,31) | Large circle r=5 | mint + dark rim |
| blob_growth_3 | (48,16)..(63,31) | Largest circle r=6 | mint + dark rim |

Note: blob_growth frames are authored now even though Plan 04 owns the
`fused_blob` clip. Plan 04 can reference these without re-extending the
PNG.

## Legacy Call Site Migrations

| Old call site | Replacement |
|---------------|-------------|
| `src/entities/player.py:573` `Particle(x, y, 11)` (boost trail) | `self.game.spawn_particle_burst(self.x, self.y + self.h - 8, type="boost_trail")` |
| `src/entities/player.py:597` `Particle(x, y, 11)` (boost chain) | same as above |
| `src/entities/player.py:649` `Particle(fire_x, fire_y, 10)` (charge) | `self.game.spawn_particle_burst(fire_x - 4, fire_y - 4, type="charge_flash")` |
| `main.py:828` inside `spawn_explosion` | Body now delegates to `spawn_particle_burst` (deprecation shim) |
| Other `spawn_explosion(...)` callers (main.py:647/652/658, player.py:737/790/830) | Unchanged -- deprecation shim keeps them working |

`from src.entities.effects import Particle` removed from
`src/entities/player.py:4` (no longer used).

## Test Count

- Baseline after Plan 31-02: 45 tests (test_anim.py)
- New tests added in Plan 31-03:
  - `tests/test_sprite_assets.py` +3 (manifest separation + bank distinct)
  - `tests/test_anim_events.py` +6 (Particle ctor + draw + drill subscriber)
- One existing test rewritten (test_phase22.py: Effect.draw assertion)
- Total Phase 31 anim-related tests passing: 54 anim/sprite tests + others

Pre-existing 9 unrelated tuning/physics/ldtk failures remain (baseline
drift from prior phases, untouched by Phase 31).

## Commits

- `eacac30` test(31-03): RED baseline + retire Effect-draw assertion
- `6deadbf` feat(31-03): bank-2 particles, sprite-backed Particle, drill subscriber

## Self-Check

- [x] particles.png exists at 64x32 with non-zero pixel data in 6 slots
- [x] SPRITE_MANIFEST has particles bank 2; effects entry removed
- [x] JSON sidecar loop skips particles (no .json sidecar)
- [x] BURST_PARTICLE_COUNT=14, BURST_PARTICLE_SPEED=1.5, BURST_PARTICLE_LIFE=20 named constants
- [x] `spawn_particle_burst` defined exactly once in main.py
- [x] `pyxel.pset` removed from Particle.draw (only mentioned in comments now)
- [x] `draw_sprite` called from Particle.draw with bank=2
- [x] `drill_block_break` subscriber: 1 wiring; calls `pause_for(DRILL_RECOIL_PAUSE_FRAMES)`
- [x] Subscriber wired AFTER `self.reset()` (line 186), BEFORE `pyxel.run` (line 258)
- [x] All 3 legacy `Particle(x,y,color)` call sites migrated to `spawn_particle_burst`
- [x] No new test failures introduced; pre-existing 9 unrelated failures unchanged

Self-Check: PASSED
