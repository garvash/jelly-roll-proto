# Phase 05: New Enemies & Player Health - RESEARCH

## Objective
Implement a robust player health system (HP, Invulnerability, Knockback) and introduce basic environmental enemies to populate the cavern biome.

## Player Health System (HP)
### Core Requirements
- **Max HP:** 3 Hearts/Points (standard for retro prototypes).
- **Invulnerability Frames (I-Frames):** 60 frames (2 seconds) of flashing/invulnerability after taking damage.
- **Knockback:** Slight upward and backward impulse when hit to prevent multi-hit death.
- **UI:** Simple heart/pip display in the corner.

### Implementation Ideas
- `Player.hp`: Current health.
- `Player.invuln_timer`: Countdown for I-frames.
- `Player.take_damage(amount, source_x)`: Handles HP reduction, I-frame start, and knockback direction.
- `main.py`: Update death logic to trigger only when `hp <= 0`.

## New Enemies
### 1. The Bat (Flying Enemy)
- **Behavior:** Sits on ceiling, dives when player is close, then flies back up.
- **HP:** 1 (dies to Slime Spit or Drill Dive).
- **Damage:** 1 HP on contact.
- **Sprite:** 8x8 flying animation.

### 2. The Snail (Crawling Enemy)
- **Behavior:** Paces back and forth on a platform, turns at edges/walls.
- **HP:** 1.
- **Damage:** 1 HP on contact.
- **Sprite:** 8x8 crawl animation.

### Future Enemies (Milestone 2)
- **Goblin:** Shielded enemy that requires Drill Dive to break guard.
- **Minion Mole:** Smaller version of the boss with basic dig attacks.

## Integration & Level Mapping
- **Enemy Spawning:** Use specific tile colors or IDs in the Tiled map (e.g., Row 1 of tileset) to mark enemy spawns.
- **Collision:** Enemies should collide with `LevelMap` solids (for Slugs) or ignore them (for Bats).
- **Combat Loop:** 
    - Slime Spit kills small enemies.
    - Drill Dive kills small enemies.
    - Contact damages player.

## Technical Risks
- **Knockback Interference:** Knockback might conflict with the `Player` state machine (e.g., interrupting a Dash).
- **I-Frame Visuals:** Flashing should be clear but not eye-straining.

## Next Steps
1. Define constants for HP and Invuln.
2. Update `Player` class with HP logic.
3. Create `Enemy` base class and specific `Bat`/`Slug` subclasses.
4. Update `main.py` to manage enemy list and collision.
