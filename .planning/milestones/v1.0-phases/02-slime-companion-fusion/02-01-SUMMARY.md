---
phase: 02-slime-companion-fusion
plan: 01
subsystem: entities
tags: [slime, companion, physics, follow-logic]
requires: [SLM-01]
provides: [Slime entity, independent follow behavior]
affects: [main.py, src/entities/player.py]
tech-stack: [python, pyxel, collections.deque]
key-files: [src/entities/slime.py, src/core/constants.py, main.py, src/entities/player.py]
decisions:
  - "Slime follows player using a history queue for a trailing effect."
  - "Slime reforms behind player if it falls too far behind (e.g., player dashes)."
  - "Slime targets a position opposite to the player's facing direction."
metrics:
  duration: 15m
  completed_date: "2026-03-12T23:05:00.000Z"
---

# Phase 02 Plan 01: Core Slime Entity & Follow Logic Summary

## Implementation Overview
Successfully implemented the core `Slime` companion entity and its independent follow behavior. The slime is now a persistent presence in the game world that follows the player with a smooth, trailing effect.

### Key Changes
1.  **Slime Entity (`src/entities/slime.py`)**:
    - Created the `Slime` class using a `collections.deque` (history queue) to store previous player positions.
    - Implemented delayed follow logic: Slime targets the player's position from `SLIME_FOLLOW_DELAY` frames ago.
    - Added side-switching logic: The slime automatically moves to the opposite side of the player's current facing direction.
    - Implemented reform logic: If the slime falls too far behind (e.g., during a dash), it instantly snaps back to a position near the player and clears its movement history.
    - Added a temporary 8x8 sprite for visual representation.
2.  **Physics Constants (`src/core/constants.py`)**:
    - Added `SLIME_FOLLOW_DELAY` (12 frames), `SLIME_MAX_DIST` (48px), `SLIME_REFORM_DIST` (8px), and `SLIME_LERP_FACTOR` (0.2).
3.  **Player Entity (`src/entities/player.py`)**:
    - Added `facing_right` property to the `Player` class to allow the slime to determine which side to follow.
4.  **Main Game Loop (`main.py`)**:
    - Registered and integrated the `Slime` entity into the `Game` class.
    - Added update and draw calls for the slime companion.

## Deviations from Plan
- Added `facing_right` property to `Player` in `src/entities/player.py` to support slime side-switching logic, which wasn't explicitly mentioned as a required file in the plan frontmatter but was necessary for the "side-switching" requirement.

## Verification Results
- **Follow Logic**: Slime follows the player with a trailing delay. (Verified via code analysis and Task 1 automated test)
- **Reform Logic**: Slime snaps back to player if separated by too much distance. (Verified via automated test script)
- **Side Switching**: Slime moves to the correct side based on player facing direction. (Verified via code analysis of `update` logic)

## Self-Check: PASSED
- [x] Slime entity exists in the game world
- [x] Slime follows the player with a short lag
- [x] Slime reforms near player if it falls too far behind
- [x] All tasks committed individually
- [x] STATE.md and ROADMAP.md updated
