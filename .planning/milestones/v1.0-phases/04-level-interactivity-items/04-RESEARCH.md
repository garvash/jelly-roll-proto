# Phase 04 Research: Giant Mole Boss & Progression

**Domain:** Boss Mechanics & Game Flow
**Researched:** 2026-03-14
**Confidence:** HIGH

## Boss Mechanics (BOSS-01)

### Giant Mole FSM
- **HIDDEN:** Mole is underground, moving horizontally. Indicated by "dirt particles" on the floor. Invulnerable.
- **EMERGING:** Mole pops up at a target location. Deals damage if player is hit.
- **STUNNED/VULNERABLE:** If hit by "Slime Spit" while emerging, the Mole is stunned for a few seconds.
- **VULNERABILITY LOOP:** The only way to damage the Mole is via **Drill Dive** while it is in the STUNNED state.

### Multi-Tile Sprite Handling
- Since Pyxel tiles are 8x8, a "Giant" mole should be at least 16x16 or 24x24.
- Implementation: Use `pyxel.blt` with larger width/height, or composite multiple 8x8 sprites.

## Slime Spit (SLM-03)

### Mechanic
- **Input:** Press `Z` while not fused.
- **Cost:** High Juice cost (e.g., 20-30).
- **Behavior:** Straight-line projectile. Destroys itself on wall contact.
- **Integration:** 
    - `Slime.spit()` method.
    - `Projectile` class in `src/entities/projectile.py`.
    - `Game.projectiles` list for tracking.

## Progression & Level Flow (PROG-01)

### Room Transitions
- The current prototype is a single screen (160x120).
- **Boss Arena:** A dedicated area (possibly screen 2) triggered when the player reaches a specific coordinate.
- **Win State:** Defeating the boss triggers an "Exit" portal or a simple "Victory" screen.

## Implementation Plan (Draft)

1.  **Sprites:** Update `generate_assets.py` to include Mole (parts) and Projectile.
2.  **Projectile System:** Implement `Projectile` class and player input.
3.  **Mole Boss:** Implement `Mole` entity with FSM.
4.  **Collision Logic:** 
    - Projectile vs Mole (Stun trigger).
    - Player (Diving) vs Mole (Damage trigger).
5.  **Progression:** Simple state check in `Game.update` for "Boss Defeated" -> Show Victory.

## Technical Risks
- **Hitbox Accuracy:** Multi-tile boss needs accurate AABB checks.
- **Juice Balancing:** Ensure Slime Spit doesn't leave the player with too little juice to perform the follow-up Drill Dive.

---
*Phase: 04-boss-progression*
*Research gathered: 2026-03-14*
