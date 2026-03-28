# Phase 05: New Enemies & Player Health - CONTEXT

**Gathered:** 2026-03-14
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase expands the combat loop by transitioning from "one-hit-death" to a health-based system and populating the world with standard enemies.

- **In-Scope:** 
    - Player Health (HP), Invulnerability Frames, Knockback.
    - Basic UI for HP (Hearts/Pips).
    - Enemy Base Class + 2 new enemies (Bat, Slug).
    - Combat interactions (Spit/Drill vs Enemies).
- **Out-of-Scope:** 
    - Healing items/Pickups (deferred).
    - Complex Enemy AI (pathfinding).
    - Shop or upgrade systems.
</domain>

<decisions>
## Implementation Decisions

### Player Health
- **HP Scale:** 3 points max.
- **Invulnerability:** 60 frames (2s). During this time, the player sprite flashes and ignores enemy/boss contact damage (but NOT hazards like spikes).
- **Knockback:** Fixed impulse of `(-2.0, -2.5)` away from the damage source.

### Enemies
- **Snail:** Crawls until it hits a wall or ledge, then turns. Sprite at (8, 8) in tileset.
- **Bat:** Hangs on ceiling. Dives vertically when player is within 64px horizontally. Sprite at (16, 8) in tileset.
- **HP:** Both have 1 HP and die to any player attack.

### Spawning
- **Tile IDs:**
    - Snail Spawn: Tile (1, 2) in tileset.
    - Bat Spawn: Tile (2, 2) in tileset.
</decisions>

<code_context>
## Existing Code Insights

### Player
- `Player.move_and_collide` currently calls `die()` on hazard. This should remain instant-death or take significant damage (e.g., 2 HP). Let's keep spikes as instant-death for now, or maybe 1 HP damage + teleport to safety.
- **User Hint:** Hazards usually feel better if they are high damage but not instant game-over if you have HP. Let's make Hazards do 1 HP damage and respawn the player at the room entrance for now.

### Main
- `main.py` update loop needs to handle a list of active enemies.

</code_context>

---
*Phase: 05-enemies-player-health*
*Context gathered: 2026-03-14*
