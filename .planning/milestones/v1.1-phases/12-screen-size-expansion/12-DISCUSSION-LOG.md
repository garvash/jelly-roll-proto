# Phase 12: Screen Size Expansion - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-28
**Phase:** 12-screen-size-expansion
**Areas discussed:** Display vs room sizing, LDtk level migration, Camera & entity bounds, Pixel scaling

---

## Display vs Room Sizing

### 12px Gap Handling

| Option | Description | Selected |
|--------|-------------|----------|
| HUD strip | 12px at bottom for HUD bar (HP, juice, minimap). Celeste pattern. | initial pick |
| Full 192px display | Change display to 320x192, no gap. Aspect 5:3. | |
| Letterbox | 6px black bars top/bottom | |
| Camera offset only | Accept 320x192 as display, extra visibility | |

**User's choice:** HUD strip — Super Metroid style with energy/ammo and minimap
**Notes:** User specifically referenced Super Metroid's bottom HUD bar as the ideal pattern

### HUD Strip Height

| Option | Description | Selected |
|--------|-------------|----------|
| 16px / 2 tiles | Display 320x184→192, game area 320x176. Room for HP, juice, minimap. | ✓ |
| 12px / 1.5 tiles | Display 320x180. HP + juice only, minimap on pause. | |

**User's choice:** 16px (2 tiles) — more room for HUD content
**Notes:** User pointed out 12px is too small for a minimap. Agreed 16px gives breathing room.

### HUD Content

**User's choice:** HP pips + juice meter minimum, fit whatever else works in 16px
**Notes:** Minimap if space allows, but not guaranteed

---

## LDtk Level Migration

| Option | Description | Selected |
|--------|-------------|----------|
| Re-author in LDtk | Manually resize and re-lay tiles | |
| Center-pad with solid | Script centers old content, pads edges | |
| Defer level redesign | Engine changes only, padding as bridge | |

**User's choice:** None of the above — PML-to-LDtk converter handles it
**Notes:** User clarified that ProMeLaGen-to-LDtk converter generates levels. Just need to hand it the new room dimensions (320x176, TILE_SIZE=8). Also specified rooms should not scroll — room height must match viewport (176px).

---

## Camera & Entity Bounds

| Option | Description | Selected |
|--------|-------------|----------|
| Central constants | SCREEN_W/H, VIEWPORT_W/H, HUD_H in constants.py | ✓ |
| Derive from pyxel | Use pyxel.width/height at runtime | |
| Room-relative only | Derive from current room dimensions | |

**User's choice:** Central constants
**Notes:** Clean separation between screen size (320x192), viewport (320x176), and HUD (16px)

---

## Pixel Scaling

| Option | Description | Selected |
|--------|-------------|----------|
| Pyxel default | Auto-scale to largest integer fit | ✓ |
| Force 3x (960x576) | Explicit 3x scaling | |
| Force 2x (640x384) | Compact window | |

**User's choice:** Pyxel default auto-scaling
**Notes:** No code needed, Pyxel handles it

---

## Claude's Discretion

- HUD layout within the 16px strip
- Draw order for HUD relative to game world and shake
- Whether to add visual separator between viewport and HUD

## Deferred Ideas

None
