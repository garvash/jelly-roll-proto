---
phase: 27-diagnostic-overlays
plan: 01
subsystem: debug-tools
tags: [pyxel, overlays, hitbox, velocity, frame-time, deque]

# Dependency graph
requires:
  - phase: 26-animation-system
    provides: event_bus subscribe/emit API for Plan 02
provides:
  - Overlay manager module with F2-F5 toggle flags
  - Hitbox wireframe overlay (F2) with per-entity-type palette colors
  - Velocity arrow overlay (F3) with frame-time graph
  - Stub functions for F4 input blips and F5 slime follow (Plan 02)
affects: [27-02-PLAN, 28-live-tuning-panel]

# Tech tracking
tech-stack:
  added: []
  patterns: [module-level boolean flags for overlay toggles, pre-allocated deque ring buffer for frame timing]

key-files:
  created: [src/core/overlays.py, tests/test_overlays.py]
  modified: []

key-decisions:
  - "Named constants for all palette colors and sizing values — no magic numbers"
  - "Frame-time measured at update() start via perf_counter delta, not wrapping draw()"
  - "Velocity arrows use separate H/V color channels (red/blue) per UI-SPEC"

patterns-established:
  - "Overlay toggle pattern: module-level booleans toggled by F-keys without modifier"
  - "Post-draw overlay pass: draw(game) called in world-space, draw_indicator() in screen-space"
  - "Ring buffer pattern: deque(maxlen=64) for bounded frame-time history"

requirements-completed: [TOOL-08]

# Metrics
duration: 3min
completed: 2026-04-12
---

# Phase 27 Plan 01: Overlay Manager Summary

**F2 hitbox wireframes and F3 velocity arrows with 64-frame timing graph using pre-allocated deque ring buffer**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-12T09:14:48Z
- **Completed:** 2026-04-12T09:17:29Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files modified:** 2

## Accomplishments
- Overlay manager with four independent F2-F5 toggle flags, defaulting to False
- Hitbox wireframe overlay drawing correct-palette-color rectb for player (red), slime (green), enemies (orange), projectiles (yellow), doors (grey), boss (purple)
- Velocity overlay with directional arrows (H=red, V=blue), VEL_SCALE=8, clamped 8-32px, 2px chevron arrowheads
- Frame-time graph: 64px wide, 24px tall, deque(maxlen=64), green/red coloring at 16.67ms threshold
- 8 unit tests covering toggle logic, buffer bounds, read-only entity access, no-op draw

## Task Commits

Each task was committed atomically:

1. **Task 1 (RED): Failing tests for overlay manager** - `f8817a5` (test)
2. **Task 1 (GREEN): Implement overlay manager** - `2651ae4` (feat)

## Files Created/Modified
- `src/core/overlays.py` - Overlay manager with toggle flags, hitbox/velocity draw, frame-time graph, indicator
- `tests/test_overlays.py` - 8 unit tests for toggle flags, buffer management, read-only access

## Decisions Made
- All numeric literals use named constants with comments explaining purpose
- Frame-time graph drawn in world-space offset by camera (per Pitfall 1 in RESEARCH.md)
- draw_indicator() is separate from draw() for screen-space vs world-space split (per Pitfall 2)

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

| File | Line | Stub | Reason |
|------|------|------|--------|
| src/core/overlays.py | ~208 | `_draw_input_overlay(game): pass` | Plan 02 implements F4 input blips with event bus |
| src/core/overlays.py | ~213 | `_draw_slime_overlay(game): pass` | Plan 02 implements F5 slime follow overlay |

These stubs are intentional architecture — Plan 02 fills them in.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 02 can extend overlays.py by filling in _draw_input_overlay and _draw_slime_overlay stubs
- init(game) placeholder ready for event bus subscriptions in Plan 02
- main.py integration (import + call sites) deferred to Plan 02 or post-phase wiring

---
*Phase: 27-diagnostic-overlays*
*Completed: 2026-04-12*
