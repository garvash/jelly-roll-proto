# Phase 03: Level Hazards & Blocks - Context

**Gathered:** 2026-03-12
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase implements the interaction between the Drill Dive and the environment, introducing destructible blocks and hazards (spikes).

- **In-Scope:** ENV-01 (Spikes), DRILL-02 (Destructible Blocks).
- **Out-of-Scope:** BOSS-01 (Mole Boss) - Deferred to a separate Phase 4 if needed, or focused on level hazards first.

</domain>

<decisions>
## Implementation Decisions

### Destructible Blocks (DRILL-02)
- **Soft Blocks:** Certain tile types (defined in Tilemap) that are removed when the player impacts them in a `DIVING` state.
- **Juice Refund:** Small amount of juice returned to the slime upon successful block destruction to encourage the loop.
- **Impact Feedback:** Screen shake or slight stall (hit-stop) on block break.

### Spikes & Hazards (ENV-01)
- **Static Hazards:** Tiles that cause instant "death" (reset to last safe position or restart level).
- **Collision Detection:** Expand `Player.move_and_collide` to check for hazard tiles.

### Level Expansion
- **Cavern Biome:** New tilemap area with tight corridors, vertical sections, and "block puzzles" requiring the Drill Dive to progress.

</decisions>

<code_context>
## Existing Code Insights

### Tilemap
- `src/level/map.py`: `check_collision` currently only returns True/False for solid. Needs to identify *what* was hit (Solid vs. Destructible vs. Hazard).

### Player FSM
- `src/entities/player.py`: `move_and_collide` and `apply_diving_physics` are the primary integration points.

</code_context>

<specifics>
## Specific Ideas
- **Hit-Stop:** A 2-3 frame pause when breaking a block to add "weight" to the drill.

</specifics>

---

*Phase: 03-level-hazards-blocks*
*Context gathered: 2026-03-12*
