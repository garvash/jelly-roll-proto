# Phase 28: Live-Tuning Panel MVP - Context

**Gathered:** 2026-04-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Ship a GMTK-Platformer-Toolkit-style overlay panel (no pause) with mouse-driven sliders grouped by system, presets, autosave journal, baseline diff, and A/B compare. This is the milestone accelerator — every subsequent feel phase uses it.

**Out of scope (other phases):**
- Phase 29 — player movement feel pass (first consumer of the panel)
- Phase 36 — final preset bake before v2.0 ship
- Non-feel tuning groups (health, hazards, death, save, gates, tile, display, sprite) — excluded from the panel entirely
- Configurable slider shapes — future refinement

</domain>

<decisions>
## Implementation Decisions

### Panel Layout & Navigation
- **D-01:** Full-screen semi-transparent overlay. F1 toggles on/off. Game continues running underneath (no pause mode).
- **D-02:** 4 tabs, feel-relevant groups only:
  - **Move** — `movement` (walk speed, accel, friction, max speed), `dash`
  - **Jump** — gravity/jump from `movement`, `forgiving` (coyote, buffer), `wall` (slide/jump)
  - **Slime** — `slime_follow`, `slime_juice`, `projectile` (spit is a slime ability)
  - **Fuse** — `drill`, `fusion`, `slime_ram`, `charge_shot`, `boost`
- **D-03:** Non-feel groups (`health`, `hazards`, `death`, `save`, `gates`, `tile`, `display`, `sprite`, `juice_effects`) are excluded from the panel. They stay in the schema but are not exposed as sliders.
- **D-04:** Collapsible sub-groups within each tab. Each schema group (e.g. `forgiving`, `wall` under the Jump tab) is a collapsible section header. Click to expand/collapse its sliders.
- **D-05:** Optional slow-mo toggle — hold Tab to drop to half-speed for precision tuning. Release to return to full speed.

### Slider Interaction Model
- **D-06:** Slider ranges are percentage-of-baseline: 0.25x to 4x of the v1.3 baseline value. Baseline position is always the visual center of the slider range.
- **D-07:** Slider track color changes past the baseline position (e.g. one color below baseline, another color above). Gives instant visual feedback on drift direction.
- **D-08:** Click arrow icon next to each slider to reset that single value to v1.3 baseline (brief visual flash confirmation).
- **D-09:** Click the numeric value label next to a slider to enter keyboard edit mode. Type a number, Enter to confirm, Esc to cancel. Precision fallback for when drag is too coarse.
- **D-10:** Mouse click-and-drag on slider handles for primary interaction. `tuning.set_value()` called on each drag frame for live feedback.

### Preset & A/B System
- **D-11:** Numbered hotkey slots for instant preset loading. Press 1, 2, 3... to load that slot's preset. All tuning values swap at the next frame boundary. Panel header shows active slot and its alias.
- **D-12:** MVP ships with 3 preset slots: slot 1 = v1.3 baseline, slot 2 = "tight", slot 3 = "floaty". System supports additional slots.
- **D-13:** Save overwrites the active slot. Panel has a Save button that writes current values to `assets/presets/slot_N.json`. Optional alias (display name) stored inside the JSON.
- **D-14:** v1.3 baseline preset is protected but overridable. Protected by default (requires deliberate confirmation to overwrite), so you can always get back to the original feel. Can be "graduated" to a new baseline when intentional.
- **D-15:** Preset files are versioned JSON in `assets/presets/`. Each file stores the full set of feel-relevant tuning values plus metadata (alias, timestamp, schema version).

### Journal & Crash Safety
- **D-16:** Rolling journal file — every slider edit is appended to a JSONL file so a crash mid-session does not lose progress. One journal file per session.

### Claude's Discretion
- Journal entry format (key+old+new+timestamp vs minimal) — pick what best serves crash recovery
- Journal flush policy (immediate fsync vs batched) — pick based on Pyxel's I/O model and the crash safety requirement
- Slow-mo implementation (frame skip vs actual FPS change) — whatever Pyxel supports cleanly
- Overlay transparency level and background color
- Tab bar visual design and click targets
- Collapsible sub-group expand/collapse animation (if any)
- Slider handle size and drag dead zone
- Color choices for baseline drift indication
- Preset JSON schema fields beyond values + alias + timestamp

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Tuning system (Phase 24-25)
- `src/core/tuning.py` — mutation API: `set_value()`, `get_baseline()`, `reset()`, `save()`, `get_group()`, PEP 562 `__getattr__`
- `assets/physics-schema.json` — v0.3.x schema with 22 groups, 87 leaves. Source of truth for tuning values.
- `.planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md` — D-01 through D-18: mutation model, schema layout, baseline, no file watcher

### Game loop & overlays (Phase 27)
- `main.py` — game loop: `update()` then `draw()`, overlay integration points at lines ~407 and ~846
- `src/core/overlays.py` — F2-F5 overlay pattern, `update()` + `draw(game)` contract, module-level toggle booleans
- `.planning/phases/27-diagnostic-overlays/27-CONTEXT.md` — D-03: overlays are visual only, panel owns numbers

### Display constraints
- `src/core/constants.py` — `SCREEN_W=320`, `SCREEN_H=180`, `VIEWPORT_H=176`, `HUD_H=16` (via tuning shim)

### Existing input patterns
- `src/core/debug.py` — Ctrl+1/2/3 god-mode toggles, module-level booleans pattern

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tuning.set_value(key, value)` — O(1) in-memory mutation, no disk I/O, live on next frame read
- `tuning.get_baseline(key)` — frozen v1.3 value for diff display and reset
- `tuning.reset(key)` — restore single key or all keys from baseline
- `tuning.save()` — atomic write to `physics-schema.json`
- `tuning.get_group(key)` — returns schema group name for tab placement logic
- `tuning._flat_index` — dict mapping flat key names to group names (87 entries)
- `overlays.py` pattern — F-key toggle + module-level boolean + `update()` / `draw()` contract

### Established Patterns
- Module-level toggle booleans for debug/overlay features (overlays.py, debug.py)
- Post-draw overlay pass in world-space (`overlays.draw(self)` after all entity draws)
- Screen-space HUD drawing after `pyxel.clip()` / `pyxel.camera()` reset
- Pyxel mouse API: `pyxel.mouse_x`, `pyxel.mouse_y`, `pyxel.btn(MOUSE_BUTTON_LEFT)`

### Integration Points
- `main.py` `update()` — panel input handling must go here (after `overlays.update()`)
- `main.py` `draw()` — panel rendering in screen-space after `pyxel.clip()` / `pyxel.camera()` reset, before or after HUD
- F1 key is available (F2-F5 taken by overlays)
- `assets/presets/` directory — does not exist yet, must be created

</code_context>

<specifics>
## Specific Ideas

- User wants the panel to feel like GMTK's Platformer Toolkit — live tuning while the game runs, instant feedback
- Slider shapes should be configurable later (noted as deferred refinement)
- A/B system should be naturally extensible beyond 2 slots — numbered hotkeys (1, 2, 3...) support this
- Non-feel groups are explicitly excluded from the panel — the panel is a feel-tuning tool, not a general config editor

</specifics>

<deferred>
## Deferred Ideas

- Configurable slider shapes — user wants to be able to change slider visual style in the future
- Expanding preset slots beyond 3 — system supports it, but MVP ships with 3

None — discussion stayed within phase scope otherwise.

</deferred>

---

*Phase: 28-live-tuning-panel-mvp*
*Context gathered: 2026-04-12*
