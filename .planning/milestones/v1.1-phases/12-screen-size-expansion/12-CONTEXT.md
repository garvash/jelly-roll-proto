# Phase 12: Screen Size Expansion - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Expand the game viewport from 128x128 to 320x192 display with a Super Metroid-style bottom HUD strip. Standard rooms become 320x176 (no scroll), camera and entity bounds use central constants, and the PML-to-LDtk converter receives updated room dimensions.

</domain>

<decisions>
## Implementation Decisions

### Display & Room Sizing
- **D-01:** Display size = 320x192 via `pyxel.init(320, 192)` — replaces current 128x128
- **D-02:** Game viewport = 320x176 (40x22 tiles) — the playable area above the HUD
- **D-03:** HUD strip = 16px (2 tiles) fixed at the bottom of the screen, Super Metroid-style — energy/ammo bar with game world above
- **D-04:** HUD content = HP pips + juice meter at minimum; minimap if space allows in 16px

### Room Dimensions
- **D-05:** Standard rooms = 320x176 (40x22 tiles) — camera locks perfectly, no scroll in standard rooms
- **D-06:** Large rooms (boss arenas, vertical shafts) use multiples like 320x352 (40x44) for intentional scrolling
- **D-07:** PML-to-LDtk converter handles level regeneration — hand over exact room dimensions (320x176) and TILE_SIZE (8) for correct output. No manual LDtk re-authoring needed.

### Code Architecture
- **D-08:** Central constants in constants.py: `SCREEN_W=320, SCREEN_H=192, VIEWPORT_W=320, VIEWPORT_H=176, HUD_H=16`
- **D-09:** Replace ALL hardcoded 128 values across the codebase (main.py, world.py, effects.py, boss.py, map.py) with the central constants

### Scaling
- **D-10:** Pyxel default auto-scaling — no explicit scale factor. Pyxel picks largest integer scale that fits the monitor.

### Claude's Discretion
- HUD layout within the 16px strip (positioning of HP pips vs juice bar)
- Draw order for HUD (drawn after game world, before/after shake offset)
- Whether to add a visual separator line between game viewport and HUD

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Engine & Display
- `main.py` — Game initialization (`pyxel.init`), camera draw offset, shake_timer, particle/effect rendering
- `src/level/world.py` — `SCREEN_W/H` constants, camera clamping (`get_camera_clamped`), room transitions, settle logic
- `src/core/constants.py` — `TILE_SIZE=8` and all game constants (target for new SCREEN_W/H/VIEWPORT_W/H/HUD_H)

### Entity Bounds (hardcoded 128 locations)
- `src/entities/effects.py` — Particle and Effect boundary culling (`cam_x + 128`, `cam_y + 128`)
- `src/entities/boss.py` — Boss screen boundary check
- `src/level/map.py` — Level width default (`128`)

### Level Generation
- `assets/entity-schema.json` — Shared schema with PML-to-LDtk converter
- `assets/cave.ldtk` — Current LDtk world file (worldGridWidth/Height: 128, defaultLevelWidth/Height: 128)
- `PML-to-LDtk Converter.md` — Converter documentation (needs updated room dimensions)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/level/world.py` already has `SCREEN_W`/`SCREEN_H` class constants — just need to point at central values
- Camera clamping (`get_camera_clamped`) already handles variable room sizes — just needs updated screen dimensions
- 24-frame ease-out LERP transitions (Phase 7) work with any screen size — no changes expected
- `spawn_explosion()` and `Particle` class are position-based, just need updated culling bounds

### Established Patterns
- All entity positions are pixel-based (not grid-relative), so they survive room resizing
- Room transitions use `SCREEN_W`/`SCREEN_H` for slide calculation — single constant change
- IID-based item persistence uses LDtk instance IDs, not positions — unaffected by room resize

### Integration Points
- `pyxel.init()` in main.py — width/height change
- `main.py` draw method — needs HUD rendering after game world draw
- `main.py` camera offset — clip game rendering to VIEWPORT_H, draw HUD below
- PML-to-LDtk converter — needs new room spec (320x176, TILE_SIZE=8)

### Hardcoded 128 Locations (grep results)
- `main.py:16` — `pyxel.init(128, 128, ...)`
- `main.py:123` — `room_w, room_h = 128, 128`
- `main.py:195` — `rx, ry, rw, rh = self.cam_x, self.cam_y, 128, 128`
- `main.py:230` — camera clamping comment
- `main.py:314-315` — slime boundary check (`cam_x + 128`, `cam_y + 128`)
- `world.py:27-28` — `SCREEN_W = 128`, `SCREEN_H = 128`
- `effects.py:23-24` — particle boundary (`cam_x + 128`, `cam_y + 128`)
- `effects.py:56-57` — effect boundary (`cam_x + 128`, `cam_y + 128`)
- `boss.py:28` — screen boundary check
- `map.py:61` — level width default
- `cave.ldtk:18-21` — worldGridWidth/Height, defaultLevelWidth/Height

</code_context>

<specifics>
## Specific Ideas

- Super Metroid-style HUD — energy bar with various ammo counts and minimap, all in the bottom strip separate from gameplay
- Celeste's 320x180 as the reference for motion freedom and screen feel
- Room height matches viewport exactly so camera locks (no scroll in standard rooms)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 12-screen-size-expansion*
*Context gathered: 2026-03-28*
