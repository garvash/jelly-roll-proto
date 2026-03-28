# Phase 1: Core Movement & Physics - Context

**Gathered:** 2026-03-12
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers a player character with high-quality, responsive platforming physics (Celeste-style) including Walk, Jump, Wall Slide, and Dash. This is the foundation for all future movement and exploration.

</domain>

<decisions>
## Implementation Decisions

### Jump Physics
- **Weighted Variable Jump:** Variable jump height based on input duration, with gravity scaling up during the fall for a snappy, weighted feel.
- **Standard Buffer (0.1s):** Standard input buffering for jumps to make the controls feel more responsive and forgiving.

### Ground Feel
- **Snappy Modern:** High acceleration for immediate movement, with an instant stop (no sliding) for maximum precision in tight spaces.
- **Generous Coyote Time (20f):** A longer grace period for ledge jumps (approx. 20 frames) to make exploration feel safer and more fluid.

### Dash & Wall Behavior
- **Claude's Discretion:** Decisions on specific dash directions, cooldowns, and wall slide friction are left to the builder during the planning/research phase, provided they maintain the "snappy/weighted" core feel.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- (None) - Phase 1 starts from a clean slate.

### Established Patterns
- (None) - This phase will establish the initial coding and architecture patterns for the project using Pyxel.

### Integration Points
- **Pyxel.run:** The core game loop where the movement system will be integrated.

</code_context>

<specifics>
## Specific Ideas
- **Celeste-style physics:** A primary reference point for the intended feel of the movement (snappy, weighted, forgiving).

</specifics>

<deferred>
## Deferred Ideas
- (None)

</deferred>

---

*Phase: 01-core-movement-physics*
*Context gathered: 2026-03-12*
