# Phase 11: Save System & HUD - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-30
**Phase:** 11-save-system-hud
**Areas discussed:** Save data & checkpoints, Mini-map in HUD, Pause screen & macro-map, Capacity upgrades, Death & respawn behavior, Save room entity design, Title screen / new game flow, Map.py +16 gate fix

---

## Save Data & Checkpoints

| Option | Description | Selected |
|--------|-------------|----------|
| Save rooms | Dedicated save point entity in specific rooms (Metroid save stations) | ✓ |
| Auto-save on room entry | Game saves every time you enter a new room | |
| Checkpoint crystals | Touch a crystal to activate as respawn + save (Hollow Knight) | |

**User's choice:** Save rooms
**Notes:** None

| Option | Description | Selected |
|--------|-------------|----------|
| All of the above | Full game state snapshot | ✓ |

**User's choice:** All — player state, slime state, world progress
**Notes:** None

| Option | Description | Selected |
|--------|-------------|----------|
| Last save room, full restore | Classic Metroid respawn at save room with full HP/juice | ✓ |
| Last save room, current stats | Keep HP/juice as saved (harsher) | |
| Current room, nearest safe spot | Resume exactly where you were | |

**User's choice:** Last save room with full HP/juice restored

| Option | Description | Selected |
|--------|-------------|----------|
| Single slot | One save file, overwritten each save | ✓ |
| Three slots | Classic 3-slot menu | |

**User's choice:** Single slot

---

## Mini-Map in HUD

| Option | Description | Selected |
|--------|-------------|----------|
| Center of HUD strip | 5x5 grid centered between HP and juice | ✓ |
| Far right, juice bar shifts | Mini-map at far right | |
| Above HUD strip | Floating overlay in game viewport | |

**User's choice:** Center of HUD strip

| Option | Description | Selected |
|--------|-------------|----------|
| Dot grid — visited only | Small squares, visited rooms filled, current blinks, unvisited invisible | ✓ |
| Dot grid — full layout | Show all rooms but dim unvisited | |
| Detailed tiles | Each room shows rough tile layout | |

**User's choice:** Dot grid, visited only

| Option | Description | Selected |
|--------|-------------|----------|
| Color-coded rooms | Save=green, boss=red, current=white, visited=gray | ✓ |
| Uniform color | All visited rooms same color | |
| You decide | Claude's discretion | |

**User's choice:** Color-coded rooms

| Option | Description | Selected |
|--------|-------------|----------|
| Persist visited rooms in save | visited_rooms set saved to JSON | ✓ |
| Session-only | Map resets on load | |

**User's choice:** Persist in save file

---

## Pause Screen & Macro-Map

| Option | Description | Selected |
|--------|-------------|----------|
| ESC key | Standard pause key | ✓ |
| TAB key | Quick-access like Hollow Knight | |
| P key | Classic retro pause key | |

**User's choice:** ESC key

**Pause content selected (multi-select):**
- ✓ Full macro-map (Required)
- ✓ Player stats overlay
- ✓ Resume/Save/Quit options
- ✗ "PAUSED" label only

| Option | Description | Selected |
|--------|-------------|----------|
| No item markers | Clean map, no uncollected item dots | ✓ |
| Show uncollected items | Mark rooms with uncollected items | |
| You decide | Claude's discretion | |

**User's choice:** No item markers

---

## Capacity Upgrades

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse ENERGY and MISSILE | Heart Container = ENERGY, Juice Tank = MISSILE | ✓ |
| New dedicated types | Create HEART_CONTAINER and JUICE_TANK | |
| You decide | Claude's discretion | |

**User's choice:** Reuse existing types

| Option | Description | Selected |
|--------|-------------|----------|
| 2 hearts + 2 juice | Start 3 HP/200 juice, max 5 HP/300 juice | ✓ |
| 3 hearts + 3 juice | Max 6 HP/350 juice | |
| You decide | Claude's discretion | |

**User's choice:** 2 hearts + 2 juice

---

## Death & Respawn Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Respawn at last save room | Full rollback to save state (classic Metroidvania) | ✓ |
| Respawn in current room | Softer penalty, keep progress (Celeste-like) | |
| Respawn at save, keep progress | Go back but keep items collected since save | |

**User's choice:** Respawn at last save room with full rollback

| Option | Description | Selected |
|--------|-------------|----------|
| Brief death animation | Short freeze + fade to black (30-60 frames) | ✓ |
| Instant respawn | Immediate teleport | |
| You decide | Claude's discretion | |

**User's choice:** Brief death animation

---

## Save Room Entity Design

| Option | Description | Selected |
|--------|-------------|----------|
| Walk onto + press UP | Floor entity, stand on it and press UP | ✓ |
| Auto-save on enter room | Just entering triggers save | |
| Dedicated key near it | New interaction key | |

**User's choice:** Walk onto + press UP

| Option | Description | Selected |
|--------|-------------|----------|
| Glowing pedestal/crystal | Floor-mounted crystal with light pulse | ✓ |
| Terminal/console | Sci-fi terminal look | |
| You decide | Claude's discretion | |

**User's choice:** Glowing pedestal/crystal

---

## Title Screen / New Game Flow

| Option | Description | Selected |
|--------|-------------|----------|
| Simple title screen | Title + Continue/New Game | ✓ |
| No title screen | Auto-load if save exists | |
| Title with map preview | Show explored % and play time | |

**User's choice:** Simple title screen

---

## Map.py +16 Gate Fix

| Option | Description | Selected |
|--------|-------------|----------|
| Verify and close in Phase 11 | Quick verification task | ✓ |
| Already fixed, skip | Trust Phase 14 | |

**User's choice:** Verify and close

---

## Claude's Discretion

- Save file location, filename, JSON structure details
- Save point sprite animation specifics
- Death animation exact timing and visual effect
- Title screen layout and font styling
- Pause screen layout positioning
- Mini-map exact pixel sizing
- Save prompt UX
- Gamepad mapping for pause

## Deferred Ideas

None — discussion stayed within phase scope
