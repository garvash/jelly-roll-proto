# Phase 02: Slime Companion & Fusion - Context

**Gathered:** 2026-03-12
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase implements the dual-hero dynamic by introducing the companion slime, the juice resource system, and the core fusion mechanic (Drill Dive). 

- **In-Scope:** SLM-01 (Companion), SLM-02 (Juice), DRILL-01 (Drill Dive).
- **Out-of-Scope:** SLM-03 (Slime Spit), DRILL-02 (Destructive traversal).

</domain>

<decisions>
## Implementation Decisions

### Slime Follow Behavior (SLM-01)
- **Physics Leash:** The slime follows the player using a physics-based leash logic. It trails behind the player and intelligently switches sides when the player changes facing direction.
- **Dissipation/Reform:** To prevent the slime from getting stuck or being left behind, it will dissipate and reform near the player if the distance exceeds a certain threshold.

### Juice & Dissipation (SLM-02)
- **Visual Scaling:** The slime's size is a direct indicator of its resource level. It scales dynamically from 8x8 (100% juice) down to 2x2 (0% juice).
- **Passive Regeneration:** Juice replenishes automatically over time when the player is NOT in a fused state.
- **Resource Depletion:** At 0% juice, the slime remains in the world (2x2 size) but all fusion abilities are disabled.

### Drill Dive Mechanics (DRILL-01)
- **Activation:** Triggered by pressing **Down + Dash (KEY_X)** while in the air.
- **Movement:** A high-speed downward dive (faster than a normal dash) with vertical priority and slight horizontal drift for minor adjustments.
- **Impact Cost:** Instead of a constant drain, juice is consumed "per hit" when the drill impacts a surface or entity.
- **Disengagement:** Fusion automatically detaches at 0 juice or can be manually cancelled by the player pressing the **Jump (KEY_SPACE)** button.

### Fusion Visuals
- **Drill Attachment:** When fused, the slime instantly snaps to the player and transforms into a "drill attachment" sprite that remains visible on the character's body.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `assets/game.pyxres`: Contains existing player and tile assets.

### Established Patterns
- **FSM-based Player:** The `Player` class in `src/entities/player.py` uses a state machine (IDLE, RUNNING, etc.) which should be extended with `FUSED` or `DIVING` states.
- **Constants-driven Physics:** Physics parameters are centralized in `src/core/constants.py`.

### Integration Points
- **`Player.update`:** Needs to account for the presence of the slime and the fusion state.
- **`main.py`:** Needs to instantiate the `Slime` companion.

</code_context>

<specifics>
## Specific Ideas
- **Celeste-style Snappiness:** Maintain the weighted, responsive feel established in Phase 1 even during fusion moves.

</specifics>

<deferred>
## Deferred Ideas
- **SLM-03 (Slime Spit):** Combat projectiles deferred to Phase 3.
- **DRILL-02 (Destructive traversal):** Actual block-breaking logic deferred to Phase 3.

</deferred>

---

*Phase: 02-slime-companion-fusion*
*Context gathered: 2026-03-12*
