---
type: bug
priority: medium
discovered: 2026-04-12
phase_context: 26
---

# Bug: Spit projectile doesn't break soft blocks

Projectile.update() in src/entities/projectile.py deactivates on wall collision
(check_collision) but never checks if the hit tile is destructible. Soft blocks
(IntGrid value 3) should be broken by spit per entity-schema.json, but the
projectile just dies and spawns a JuiceStain.

Fix: on collision, check is_destructible() at the impact tile. If true, clear
the tile (clear_tile + record_broken_block for regen) instead of just deactivating.
Same pattern used by drill_dive in player.py ~line 753.
