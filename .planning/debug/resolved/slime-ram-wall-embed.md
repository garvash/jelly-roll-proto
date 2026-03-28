---
status: resolved
trigger: "Slime Ram (V while fused) lodges player inside wall"
created: 2026-03-28T00:00:00Z
updated: 2026-03-28T12:00:00Z
---

## Current Focus

hypothesis: end_ram() is called but collision resolution runs AFTER it clears the RAMMING state, using dx=0 which produces wrong snap math
test: trace control flow in move_and_collide horizontal collision for RAMMING state
expecting: snap-to-surface code uses self.dx which was just zeroed by end_ram
next_action: return diagnosis

## Symptoms

expected: Player rams into solid wall, stops flush against the wall surface, ram ends
actual: Player gets embedded inside the wall after ram collision
errors: none (visual/gameplay bug)
reproduction: Fuse with slime, press V to ram, collide with solid wall
started: since ram implementation

## Eliminated

(none needed -- root cause found on first hypothesis)

## Evidence

- timestamp: 2026-03-28
  checked: move_and_collide lines 588-612, horizontal collision during RAMMING
  found: |
    Line 606-607: When ram hits non-CRACKED_H wall, end_ram(slime) is called.
    end_ram() sets self.dx = 0 (line 119-120).
    Then lines 608-612 run the snap logic which branches on self.dx > 0 / self.dx < 0.
    Since self.dx is now 0, NEITHER snap branch executes.
    The player position self.x already includes the full ram movement (line 578: self.x += self.dx)
    but is never snapped back to the tile boundary.
  implication: Player remains at the penetrating position inside the wall.

- timestamp: 2026-03-28
  checked: RAM_SPEED constant
  found: RAM_SPEED = 5.0 pixels/frame, TILE_SIZE = 8
  implication: At 5px/frame the player can penetrate up to 5 pixels into an 8-pixel tile in a single frame

## Resolution

root_cause: |
  In move_and_collide() lines 606-612, when RAMMING state hits a solid (non-cracked) wall:
  1. end_ram(slime) is called at line 607, which sets self.dx = 0 (line 119-120 of end_ram)
  2. The snap-to-surface code at lines 608-612 checks `if self.dx > 0` / `elif self.dx < 0`
  3. Since dx is now 0, neither branch runs -- the player is never pushed out of the wall

  The player's x position was already advanced by the full ram velocity (line 578: self.x += self.dx)
  before the collision check, so the player is now embedded inside the wall tile.

fix: |
  Save the ram direction BEFORE calling end_ram(), then use the saved direction for snap logic.
  Or: move the snap code BEFORE the end_ram() call so self.dx still has the ram velocity.

verification: (not yet applied)
files_changed: []
