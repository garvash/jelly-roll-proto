# Phase 07: Macro-Map & Room Persistence - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary
Deliver a robust 5x5 Metroidvania world system featuring level-clamped camera scrolling, "freeze-and-slide" room transitions triggered by Door entities, and intelligent state persistence (Permanent Items vs. Regenerative Blocks).
</domain>

<decisions>
## Implementation Decisions

### Room Transitions & Camera
- **Metroid-Style Camera:** The camera follows the player but is clamped to the current room's pixel bounds (defined in LDtk).
- **Freeze-and-Slide:** When a transition is triggered, gameplay freezes, and the camera slides over several frames to the next room's coordinate space.
- **Door Triggers:** Transitions are initiated by interacting with Door entities. Doors may require specific shots/actions to open.
- **Vertical Aiming:** Support player input bias for intentional vertical shooting to hit ceiling or floor doors.

### World Management
- **WorldManager:** Refactor room logic, spawning, and camera control into a dedicated `WorldManager` class to handle the 5x5 grid complexity.
- **Z-Spiral Topology:** Levels are manually placed at absolute world coordinates in LDtk to form the Z-Spiral layout.

### State Persistence
- **Global Persistence (Items):** Collected items (Energy/Missile Tanks) are tracked globally using their unique LDtk `iid`. They do not respawn.
- **Local Persistence (Blocks):** Destructible blocks are regenerative. They stay broken only while the player is in the room; re-entering a room resets them to prevent soft locks.

### Claude's Discretion
- The specific easing/duration of the camera slide.
- The data structure for the `WorldManager`'s room lookup.
</decisions>

<canonical_refs>
## Canonical References
- `5x5mapdesign.txt` — Blueprint for Z-Spiral layout and biome gating.
- `topics.txt` — Source for new ability concepts (vertical shooting, etc.).
- `.planning/research/SUMMARY.md` — Technical patterns for camera snapping and persistence.
</canonical_refs>

<code_context>
## Existing Code Insights
- `main.py`: Current room scanning logic needs to be migrated to `WorldManager`.
- `src/level/map.py`: `LevelMap` already loads absolute world coordinates; needs to expose room pixel bounds.
</code_context>

<specifics>
## Specific Ideas
- "Broken blocks should always regenerate so there will be no soft locks."
- "Door object that opens with different shots."
</specifics>

---
*Phase: 07-macro-map-room-persistence*
*Context gathered: 2026-03-22*
