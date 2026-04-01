---
status: complete
phase: 07-macro-map-room-persistence
source: [07-01-SUMMARY.md, 07-02-SUMMARY.md]
started: 2026-03-27T23:30:00Z
updated: 2026-03-27T23:30:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Camera Clamped to Room Bounds
expected: Move the player around the current room. The camera should stay within the room boundaries — no black space or out-of-bounds areas visible at the edges. If the room is the same size as the viewport, the camera should be locked (no scrolling). If larger, the camera should follow the player but stop at room edges.
result: issue
reported: "when you move into a vertical shaft, the screen smoothly transitions to the top room of the vertical shaft then abrupt camera shift happens in attempt to put the character at the center of the screen, this is a bit jarring and somehow bypasses the enemies spawning in the off screen part of the vertical shaft"
severity: major

### 2. Room Transition Trigger
expected: Walk the player to the edge of a room (or through a door). A room transition should trigger — gameplay freezes briefly and the camera slides smoothly to the next room. The slide should take roughly 0.4 seconds with a deceleration feel (fast start, slow finish).
result: pass

### 3. Player Position After Transition
expected: After a room transition completes, the player should be positioned inside the new room (not stuck on the boundary). Gameplay should resume immediately. Walking back toward the boundary should not re-trigger the transition instantly.
result: pass

### 4. Door Interaction
expected: Find a closed door in a room. Kick it (or hit it with a slime spit). The door should open. Walk through the open door to trigger a room transition to the connected room.
result: pass

### 5. Item Persistence Across Rooms
expected: Pick up a collectible item (Energy Tank or Missile Tank). Leave the room and come back. The item should NOT respawn — it stays collected permanently.
result: pass

### 6. Destructible Block Regeneration
expected: Drill through a destructible block. Wait about 5 seconds. The block should regenerate (reappear) in place. It should be solid again and drillable again.
result: pass

### 7. Block Reset on Room Re-entry
expected: Drill through some destructible blocks, then leave the room and come back. All broken blocks in that room should be fully restored immediately on re-entry (no waiting for the 5-second timer).
result: pass

### 8. Biome Gate Tiles
expected: Find Goo-Mold blocks or cracked blocks in a room. They should behave as solid (block movement) and be destructible with the drill, same as regular soft blocks.
result: resolved
reason: Superseded by Phase 08 destruction hierarchy redesign — Cracked-V is drill-gated, Cracked-H is ram-gated, Goo-Mold reserved for late-game ability. Original test premise no longer applies.

## Summary

total: 8
passed: 6
issues: 1
pending: 0
skipped: 0
skipped: 0
blocked: 0

## Gaps

- truth: "Camera should slide to where the player will be in the target room, with no snap after transition"
  status: resolved
  reason: "User reported: transition slides to top of vertical shaft then abruptly snaps to player center, bypasses enemy spawning in off-screen part"
  severity: major
  test: 1
  artifacts: [src/level/world.py:trigger_transition, main.py:spawn_enemies]
  missing: []
  root_cause: "trigger_transition() computed target camera as room origin instead of player-clamped position. spawn_enemies() used 128x128 viewport check instead of room bounds."
  resolution: "Axis-locked transitions with post-transition settle phase. Room-bounds spawning. Also fixed: slime auto-aim, enemy respawn, door rendering/collision/pivot/grace/auto-open."
