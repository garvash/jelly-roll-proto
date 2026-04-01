# Phase 11: Save System & HUD - Context

**Gathered:** 2026-03-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver a complete save/load system with save rooms, a mini-map HUD element, a pause screen with full macro-map view, capacity upgrade items, death/respawn flow, and a simple title screen. Also verify the map.py +16 gate scan fix from Phase 14.

</domain>

<decisions>
## Implementation Decisions

### Save System (SYS-01)
- **D-01:** Save rooms — dedicated save point entities in specific rooms (Metroid-style save stations). Player walks onto save point and presses UP to save.
- **D-02:** Single save slot — one JSON file, overwritten each save. Per REQUIREMENTS.md out-of-scope note.
- **D-03:** Full game state saved — player state (HP, max_hp, unlocked abilities), slime state (juice, max_juice), world progress (collected_iids, event_flags, current save room coordinates, visited_rooms set).
- **D-04:** On load, player respawns at last save room with full HP and juice restored.
- **D-05:** Save point visual — glowing pedestal/crystal, floor-mounted, 8x8 or 16x16 sprite with Pyxel palette color pulse (e.g., color 10 yellow).

### Mini-Map HUD (SYS-02)
- **D-06:** Mini-map centered in the existing 16px HUD strip, between HP pips (left) and juice bar (right).
- **D-07:** Dot grid style — each room is a small square (2-3px). Only visited rooms shown (filled). Current room blinks/highlights. Unvisited rooms invisible.
- **D-08:** Color-coded rooms — save rooms green, boss rooms red, current room white/blinking, visited rooms gray.
- **D-09:** Visited rooms persisted in save file JSON alongside items and flags.

### Pause Screen & Macro-Map (SYS-03)
- **D-10:** ESC key opens/closes pause screen.
- **D-11:** Pause screen shows: full macro-map (5x5 room grid, larger than HUD version), player stats overlay (HP/max HP, juice/max juice, unlocked ability icons), and menu options (Resume, Save if in save room, Quit).
- **D-12:** Macro-map uses same color-coding as mini-map (save=green, boss=red, current=white, visited=gray). No item markers on map — clean display.

### Capacity Upgrades (SYS-04)
- **D-13:** Reuse existing ENERGY (+1 max_hp) and MISSILE (+50 max_juice) item types. Already implemented with IID-based persistence via collected_iids.
- **D-14:** 2 heart containers + 2 juice tanks in the world. Start: 3 HP / 200 juice. Max: 5 HP / 300 juice. Placed in LDtk rooms.

### Death & Respawn
- **D-15:** On death (HP=0), revert to last save state — world progress (items, flags) rolls back to what was saved. Classic Metroidvania stakes.
- **D-16:** Brief death animation — short freeze + fade to black (30-60 frames), then respawn at save room.

### Title Screen
- **D-17:** Simple title screen — game title + Continue (if save exists) / New Game. Minimal but functional entry point.

### Gate Scan Fix
- **D-18:** Verify map.py legacy gate scan +16 hardcode is fixed (likely done in Phase 14). Quick verification task to close the gap.

### Claude's Discretion
- Save file location and format details (filename, JSON structure)
- Save point sprite animation specifics (pulse rate, colors)
- Death animation exact timing and visual effect
- Title screen layout and font styling
- Pause screen layout (positioning of map, stats, menu)
- Mini-map exact pixel sizing within 16px HUD strip
- How to surface "Save?" prompt when on save point
- Gamepad mapping for ESC/pause (Start button)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Core Game Loop
- `main.py` — Game class with draw(), _draw_hud(), game_state, event_flags, death_timer, shake_timer
- `src/core/constants.py` — SCREEN_W/H, VIEWPORT_W/H, HUD_H, PLAYER_MAX_HP, JUICE_MAX, all game constants

### Persistence & World State
- `src/level/world.py` — WorldManager with collected_iids set, broken_blocks dict, room transitions, camera clamping
- `src/entities/items.py` — Item class with ENERGY/MISSILE types, IID-based persistence, collect() method
- `src/entities/map_entities.py` — Door class with event_id, check_event_open(event_flags)

### HUD & Display
- `main.py:598-631` — Existing _draw_hud() with HP pips (left) and juice meter (right) in 16px strip

### Level Data
- `assets/entity-schema.json` — Shared schema with pml-to-ldtk converter, needs SavePoint entity type
- `assets/cave.ldtk` — LDtk world file, rooms and entity placement

### Gate Scan (verification target)
- `src/level/map.py:184-201` — close_gates() method, currently uses VIEWPORT_W/VIEWPORT_H constants

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `collected_iids` set in WorldManager — already tracks collected items globally via LDtk IID
- `event_flags` dict in Game — already tracks boss defeats and event-gated doors
- `_draw_hud()` in main.py — 16px HUD strip with HP pips and juice meter, ready for mini-map addition
- `Item` class with ENERGY/MISSILE — collect() already handles max_hp/max_juice upgrades
- `game_state` string in Game — "PLAYING"/"WON" state machine, can extend with "PAUSED"/"TITLE"/"DEAD"

### Established Patterns
- IID-based item persistence — collected items never respawn (world.py:249-253)
- Room-entry block reset — broken blocks clear on room entry (world.py:292-294)
- Event flags for door gating — event_flags dict checked on room entry (main.py:505-507)
- 24-frame ease-out LERP room transitions — works with any screen size
- Sprite rendering via draw_sprite() and PNG spritesheet pipeline (Phase 13)

### Integration Points
- `Game.__init__()` in main.py — add save/load manager, title screen state
- `Game.update()` — add pause state handling, death respawn logic
- `Game.draw()` — add pause screen overlay, title screen rendering
- `Game._draw_hud()` — add mini-map between HP and juice
- `WorldManager` — expose room grid data for mini-map rendering
- `assets/entity-schema.json` — add SavePoint entity definition for LDtk placement

</code_context>

<specifics>
## Specific Ideas

- Save rooms like Metroid save stations — walk onto a glowing crystal pedestal and press UP
- Death reverts to last save state (full rollback) — meaningful stakes
- Mini-map dot grid centered in HUD strip — visited-only with color-coded special rooms
- Pause screen = full macro-map + stats + Resume/Save/Quit menu
- Title screen with Continue/New Game — auto-detect save file existence

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 11-save-system-hud*
*Context gathered: 2026-03-30*
