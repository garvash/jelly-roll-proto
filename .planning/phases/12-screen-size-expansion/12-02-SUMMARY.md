---
phase: 12-screen-size-expansion
plan: 02
subsystem: display/hud
tags: [draw-pipeline, hud, viewport-clip, screen-space-ui]
dependency_graph:
  requires: [12-01]
  provides: [draw-pipeline-clip, hud-strip, juice-meter]
  affects: [main.py]
tech_stack:
  added: []
  patterns: [clip-camera-reset, screen-space-hud]
key_files:
  created: []
  modified: [main.py]
decisions:
  - "HUD uses palette color 1 (dark blue) for background strip"
  - "Juice meter is 80px wide, right-aligned with 4px margin"
  - "Victory text centered using VIEWPORT_W/VIEWPORT_H constants"
metrics:
  duration: ~1min
  completed: 2026-03-28
---

# Phase 12 Plan 02: Draw Pipeline Restructure + HUD Strip Summary

Three-phase draw pipeline with viewport clipping, camera reset, and screen-space HUD strip showing HP pips and juice meter in bottom 16px.

## What Was Done

### Task 1: Restructure draw pipeline with clip/camera phases and add HUD (d64ca87)

Restructured `draw()` in main.py into three distinct phases:

1. **Phase 1 (Game World):** Added `pyxel.clip(0, 0, VIEWPORT_W, VIEWPORT_H)` to confine all game rendering to the top 320x176 pixels. All entity draws, tilemap, and victory overlay render within this clipped area.

2. **Phase 2 (Reset):** After game world drawing, `pyxel.clip()` and `pyxel.camera()` are called with no arguments to reset clipping and camera to screen-space origin. This ensures the HUD is immune to screen shake.

3. **Phase 3 (HUD):** New `_draw_hud()` method renders in screen-space coordinates:
   - HP pips on the left (4px margin, 10px spacing per pip)
   - Juice meter bar on the right (80px wide, green fill proportional to juice/JUICE_MAX)
   - Dark blue background strip at y=176 spanning full 320px width

Additional changes:
- Removed old world-space HP overlay (`cam_x + 4 + i * 10` pattern)
- Re-centered victory text for 320x176 viewport using `(VIEWPORT_W - box_w) // 2`
- Added `JUICE_MAX` to constants import

### Task 2: Visual verification (PENDING CHECKPOINT)

Awaiting human visual verification of viewport + HUD rendering.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Self-Check: PENDING

Task 1 committed. Task 2 awaiting human verification checkpoint.
