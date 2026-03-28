---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: World Expansion & New Abilities
status: Ready to execute
stopped_at: Completed 12-03-PLAN.md (asset & schema updates)
last_updated: "2026-03-29T00:24:00.000Z"
progress:
  total_phases: 5
  completed_phases: 4
  total_plans: 14
  completed_plans: 14
---

# Project State - Jelly Roll Proto

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-28)

**Core value:** Prototyping the satisfying "fusion" loop between a player and a companion slime.
**Current focus:** Phase 12 — screen-size-expansion

## Current Position

Phase: 12 (screen-size-expansion) — EXECUTING
Plan: 3 of 3

## Progress

[████████░░] 50% Complete (2/5 phases done, Phase 8 complete)

## Recent Decisions

- **Entity schema 320x176:** default_room_size updated from [128,128] to [320,176] in shared contract (2026-03-29).
- **LDtk grid recalculation:** Level positions use formula new_worldX=(old/128)*320, new_worldY=(old/128)*176 (2026-03-29).
- **Ram invuln pattern:** Ram sets invuln_timer=9999 during flight, resets to DASH_IFRAMES on end (2026-03-28).
- **Charge shot direct unfuse:** Charge shot sets is_fused=False directly because slime position deferred to ChargeProjectile impact (2026-03-28).
- **Fusion fuse/unfuse atomic pair:** Always use player.fuse(slime)/unfuse(slime) instead of bare is_fused assignments (Pitfall 3) (2026-03-28).
- **Mana shield pattern:** Fused damage consumes juice (20/hit) instead of HP; juice empty triggers dissipation cooldown (2026-03-28).
- **Spit-on-release:** Z tap fires spit, Z hold triggers recall for clean input separation (Pitfall 2) (2026-03-28).
- **V button unified:** V=dash (unfused), DOWN+V=drill dive. Kick removed entirely (D-07, D-10, D-22) (2026-03-28).
- **Input abstraction pattern:** Logical action names (left/right/jump/spit/dash) mapped to physical key lists for easy remapping (2026-03-28).
- **Hold duration tracking:** _prev_hold_frames stores last held frame count for accurate tap detection on release frame (2026-03-28).
- **24-frame ease-out LERP:** Smooth camera slide for room transitions (~0.4s at 60fps) (2026-03-27).
- **IID-based item persistence:** Using LDtk instance IDs for permanent item tracking (2026-03-27).
- **Room-entry block reset:** All broken blocks reset on room entry to prevent soft-locks (2026-03-27).

## Pending Todos

- Begin Phase 09: Defensive Mechanics (ABL-05, ABL-06, ABL-07)

## Blockers/Concerns

(None)

## Session Continuity

**Last session:** 2026-03-29T00:24:00.000Z
**Stopped at:** Completed 12-03-PLAN.md (asset & schema updates)
