# Phase 10: Nitro-Ejection & Endgame (ABL-02) - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver CRACKED_V block breaking (Drill Dive downward + Boost upward), gamepad controller support, a full ability tuning pass with minimal VFX, and Goo-Mold tile cleanup. The original "Nitro-Ejection" concept from 5x5mapdesign.txt is **outdated** — "infinite jump" is an emergent result of collecting enough Juice Capacity upgrades (SYS-04, Phase 11) to hit the infinite threshold, not a separate ability. This phase focuses on completing vertical traversal gating and polishing all abilities with gamepad in hand.

</domain>

<decisions>
## Implementation Decisions

### CRACKED_V Block Breaking
- **D-01:** Drill Dive breaks CRACKED_V blocks on downward contact. Same pattern as existing TILE_DESTRUCTIBLE breaking — player dives through, blocks break as they pass. Consistent with current drill behavior.
- **D-02:** Slime Boost breaks CRACKED_V blocks on upward contact during flight. Mirrors Drill Dive symmetry — downward=Drill, upward=Boost. Enables two-way vertical passages through previously one-way routes.
- **D-03:** Both abilities break CRACKED_V on first contact — no multi-hit durability, no fused-only requirement.

### Gamepad Support
- **D-04:** Standard platformer button layout:
  - D-pad: movement (left/right/up/down)
  - A (bottom): Jump / Boost / Drill Dive (maps to SPACE)
  - B (right): Spit / Recall+Charge / Charge Shot (maps to Z/J)
  - X (left): Dash / Ram (maps to V/K)
  - Y (top): unused / reserved for future
  - Start: reserved for pause (Phase 11)
  - Shoulders/Triggers: unused / reserved for future
- **D-05:** Implementation via existing input abstraction layer (`_ACTION_MAP` in `src/core/input.py`). Add Pyxel gamepad constants (GAMEPAD1_BUTTON_A, GAMEPAD1_BUTTON_DPAD_*, etc.) to each action's key list. No new code patterns needed.

### Goo-Mold Removal
- **D-06:** Remove TILE_GOO_MOLD entirely from the codebase. It was a remnant of the "Reform Block" (ABL-07) misinterpretation, already removed in Phase 9 (D-21). Clean up:
  - `src/core/constants.py` — remove TILE_GOO_MOLD constant
  - `src/level/map.py` — remove is_goo_mold(), remove from collision checks (is_solid, is_destructible, is_cracked)
  - `assets/entity-schema.json` — remove IntGrid value 10 mapping
- **D-07:** No LDtk maps currently use Goo-Mold tiles, so no data migration needed. A new block type can be added later with a fresh design if needed.

### Ability Tuning Pass
- **D-08:** Full tuning pass across all 6 abilities: Dash, Ram, Drill Dive, Charge Shot, Bubble Shield, Slime Boost. Adjust constants, fix edge cases, improve feel with gamepad in hand.
- **D-09:** Focus areas: state transitions, collision edge cases, ability cancellation rules, and anything that feels broken during playtesting.

### Visual Feedback (VFX)
- **D-10:** Minimal VFX using Pyxel built-in drawing primitives (pyxel.pix/circ/rect). No sprite sheets needed. Target effects:
  - Ram impact: 3-frame screen shake
  - Drill block break: 2-3 pixel particles
  - Charge shot fire: brief flash
  - Boost tap: small upward trail
  - Shield hit: circle flash
- **D-11:** No audio/sound effects in this phase. Pyxel audio can be a separate pass later.

### Nitro-Ejection / Infinite Juice (Deferred)
- **D-12:** "Nitro-Ejection" from the old 5x5mapdesign.txt is not a separate ability. The "Infinite Jump" emerges when Juice Capacity upgrades (SYS-04) push max juice to ~255, at which point the game treats juice as infinite. Slime Boost becomes sustained flight naturally.
- **D-13:** The infinite juice threshold logic is a cherry-on-top feature, not immediately needed. Can be implemented alongside SYS-04 in Phase 11 or as a small addition later.

### Claude's Discretion
- Specific tuning constant values (boost force, dash speed, i-frame durations, etc.)
- Exact VFX implementation details (particle count, shake magnitude, trail length)
- Order of ability tuning (which to address first)
- Edge case prioritization during the tuning pass

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Decisions (Active)
- `.planning/phases/08-new-fusion-abilities/08-CONTEXT.md` — Fusion system, controls, Ram (D-12-D-14), Charge Shot (D-16-D-18), Drill Dive retcon (D-22-D-24)
- `.planning/phases/09-defensive-mechanics/09-CONTEXT.md` — Bubble Shield (D-01-D-06), Slime Boost (D-07-D-11), input remap (D-12-D-13), ABL-07 removal (D-21)

### Technical
- `src/core/input.py` — Input abstraction layer (_ACTION_MAP). Gamepad constants go here.
- `src/entities/player.py` — Player state machine, all ability implementations, handle_input()
- `src/entities/slime.py` — Juice resource model, fused state, dissipation/reform
- `src/core/constants.py` — All physics/ability constants, tile type constants (TILE_CRACKED_V, TILE_GOO_MOLD to remove)
- `src/level/map.py` — Tile collision system, is_cracked_vertical(), is_goo_mold() (to remove)
- `assets/entity-schema.json` — Shared entity schema with pml-to-ldtk converter (Goo-Mold IntGrid removal)

### Outdated (Do NOT follow)
- `5x5mapdesign.txt` — **OUTDATED.** The 5x5 grid approach is replaced by direct LDtk map design. Do not reference Zone A-E, "dramatic escape," or "Nitro-Ejection" as a named ability. LDtk-based design scales from single biome to massive multi-biome worlds.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_ACTION_MAP` in `input.py` — Direct extension point for gamepad. Add GAMEPAD1_* constants to each action's key list.
- `Player.start_boost()/update_boost()` — Boost flight logic. CRACKED_V breaking hooks into collision during BOOSTING state.
- Drill Dive collision in `Player` — Already breaks TILE_DESTRUCTIBLE. Extend to include TILE_CRACKED_V.
- `LevelMap.is_cracked_vertical()` — Already defined, ready for use in break conditions.
- `TILE_CRACKED_V` constant — Already in constants.py and collision system.

### Established Patterns
- State-driven entity logic: Player.state string drives update/draw behavior
- `_ACTION_MAP` pattern: logical action -> list of physical keys (trivially extensible)
- Tile break pattern: `remove_tile()` called on collision during ability state
- `has_*` item unlock pattern for ability gating
- `fuse()`/`unfuse()` atomic pair (never set is_fused directly)

### Integration Points
- `Player` DIVING state collision handling — add CRACKED_V to breakable tile check
- `Player` BOOSTING state update — add upward CRACKED_V collision check + break
- `input.py _ACTION_MAP` — add GAMEPAD1_BUTTON_* and GAMEPAD1_BUTTON_DPAD_* constants
- `LevelMap` collision checks — remove TILE_GOO_MOLD from is_solid, is_destructible

</code_context>

<specifics>
## Specific Ideas

- "Symmetrical vertical traversal" — Drill Dive breaks CRACKED_V going down, Boost breaks them going up. Same blocks, two directions, makes previously one-way vertical passages accessible from both sides.
- "Gamepad-first tuning" — The ability tuning pass should be done with a gamepad plugged in. Analog feel reveals issues that keyboard testing misses (input timing, button responsiveness, thumb ergonomics).
- LDtk map design replaces the old 5x5 grid approach — more versatile for prototyping, scales from small to massive worlds without rigid room grid constraints.
- Infinite juice is emergent, not a pickup — collecting enough SYS-04 upgrades to hit ~255 max juice makes the game treat it as infinite. Slime Boost becomes sustained flight naturally.

</specifics>

<deferred>
## Deferred Ideas

- **Infinite juice threshold (SYS-04 dependent):** When max juice hits ~255, treat as infinite. Implement alongside Juice Capacity upgrades in Phase 11.
- **Pyxel audio/SFX:** Sound effects for abilities. Separate pass after visual feedback is dialed in.
- **New block type (replacing Goo-Mold slot):** IntGrid value 10 is freed up after Goo-Mold removal. Can be used for a future block type with a fresh design.
- **5x5mapdesign.txt cleanup:** The document is outdated but still in the repo. Could be archived or removed to avoid confusion.

</deferred>

---

*Phase: 10-nitro-ejection-endgame*
*Context gathered: 2026-03-28*
