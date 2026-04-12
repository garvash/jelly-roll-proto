# Phase 27: Diagnostic Overlays - Context

**Gathered:** 2026-04-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Ship per-system debug overlays (hitbox, velocity, input state, slime AI) toggled by F2-F5. Must exist before Phase 28 panel validation and Phase 29 input audit so that "feels off" becomes measurable. Overlays are purely visual — no numerical readouts (Phase 28 panel owns those).

</domain>

<decisions>
## Implementation Decisions

### Overlay Architecture
- **D-01:** Centralized overlay manager in `src/core/overlays.py` with a single post-draw pass. All overlay rendering happens after game draw — entities do not check overlay flags in their own draw() methods.
- **D-02:** `src/core/debug.py` stays separate for god-mode toggles (Ctrl+1/2/3). Overlays are a new system, not an extension of debug.py.

### Information Density
- **D-03:** Pure visual overlays — no text or numerical readouts. Rects, arrows, path lines, color-coded states only. Phase 28's live-tuning panel owns all numbers and editing.

### Input State Visualization
- **D-04:** Coyote time and jump buffer shown as ephemeral spatial blips: a blip where the actual jump/land happened (mechanic trigger) and a blip where the player pressed jump (input event). Blips fade after a short time, showing the spatial gap between trigger and press.

### Slime Follow Overlay
- **D-05:** Slime overlay shows both: (a) follow path trail — breadcrumb dots from the position history deque, color-coded by age; (b) distance threshold boundaries — circles/lines showing SLIME_MAX_DIST and SLIME_REFORM_DIST around the player. Slime follow is a known pain point and needs thorough visualization for Phase 30 tuning.

### Input HUD
- **D-06:** No button state HUD for now — can add later if needed. Spatial blips are sufficient alongside Phase 28 panel.

### Claude's Discretion
- F-key assignment (which overlay on which key) — choose sensible defaults
- Overlay colors — pick colors that contrast with the cavern tileset
- Blip fade duration and visual style

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing debug system
- `src/core/debug.py` — current god-mode toggle pattern (Ctrl+1/2/3), module-level booleans
- `main.py` — game loop structure, where draw() is called

### Tuning system (Phase 24-25)
- `src/core/tuning.py` — live values that overlays may reference
- `assets/entity-schema.json` — tile/entity definitions

### Slime follow system
- `src/entities/slime.py` — Slime class with position history deque, follow logic, distance thresholds
- `src/core/tuning.py` §SLIME_* values — follow delay, max dist, reform dist, lerp factor

### Animation system (Phase 26)
- `src/anim/event_bus.py` — event bus that overlays could subscribe to for blip triggers

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/core/debug.py`: Module-level boolean pattern for runtime toggles — overlay flags follow the same pattern
- `src/entities/slime.py`: Already maintains `self.history` deque with position trail — overlay can read this directly
- `src/anim/event_bus.py`: Can subscribe to jump_start, land, fall_start events for blip placement

### Established Patterns
- Pyxel draw primitives: `pyxel.rectb()` for hitboxes, `pyxel.line()` for vectors, `pyxel.pset()` for dots
- Entity draw methods use bottom-center anchoring with `draw_sprite()` from `src/core/sprite_utils.py`
- Game loop: `update()` then `draw()` — overlay manager draws last in the draw pass

### Integration Points
- `main.py` Game class: call `overlays.update()` in update loop, `overlays.draw()` at end of draw loop
- F2-F5 key detection: in `overlays.update()` or in `debug.update()`
- Entity access: overlay manager needs references to player, slime, and level_map

</code_context>

<specifics>
## Specific Ideas

- Coyote blip should show the spatial gap between where the player left the ground and where they pressed jump — GMTK Platformer Toolkit style visualization
- Slime follow overlay is high priority — current follow behavior "feels very buggy" and needs thorough visualization to diagnose before Phase 30 tuning pass
- Overlays complement Phase 28 panel: overlays = spatial/world-anchored, panel = numerical/editable

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 27-diagnostic-overlays*
*Context gathered: 2026-04-12*
