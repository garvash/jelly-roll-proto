# Roadmap - Jelly Roll Proto

## Milestones

- ✅ **v1.0 Vertical Slice** — Phases 1-6 (shipped 2026-03-28)
- 🚧 **v1.1 World Expansion & New Abilities** — Phases 7-11 (in progress)

## Phases

<details>
<summary>✅ v1.0 Vertical Slice (Phases 1-6) — SHIPPED 2026-03-28</summary>

- [x] Phase 1: Core Movement & Physics (2/2 plans) — completed 2026-03-12
- [x] Phase 2: Slime Companion & Fusion (4/4 plans) — completed 2026-03-13
- [x] Phase 3: Destructive World & Boss (4/4 plans) — completed 2026-03-14
- [x] Phase 4: Level Interactivity & Items (2/2 plans) — completed 2026-03-15
- [x] Phase 5: New Enemies & Player Health (2/2 plans) — completed 2026-03-14
- [x] Phase 6: Physics Refinement & Test Gaps (1/1 plan) — completed 2026-03-22

</details>

### 🚧 v1.1 World Expansion & New Abilities (In Progress)

- [x] Phase 7: Macro-Map & Room Persistence (2/2 plans) — completed 2026-03-27
- [x] Phase 8: New Fusion Abilities (ABL-01, ABL-03, ABL-04) — completed 2026-03-28
  **Goal:** Charge-to-fuse ability system with Slime Ram, Directional Hold, and Charge Shot
  **Plans:** 6 plans
  Plans:
  - [x] 08-01-PLAN.md — Input abstraction layer + migrate player.py inputs
  - [x] 08-02-PLAN.md — Kick removal, drill retcon, DashPickup item, basic dash
  - [x] 08-03-PLAN.md — Fusion system core (recall, charge-to-fuse, mana shield, dissipation) + directional slime hold (ABL-03)
  - [x] 08-04-PLAN.md — Slime Ram (ABL-01) + Charge Shot (ABL-04)
  - [x] 08-05-PLAN.md — Gap fix: tap reposition follow + ram wall embed
  - [x] 08-06-PLAN.md — Gap fix: charge shot windup (CHARGING_SHOT state)
- [x] Phase 9: Defensive Mechanics (ABL-05, ABL-06, ABL-07) — completed 2026-03-28
  **Goal:** Bubble Shield (auto-fuse hazard protection), Slime Boost (fused vertical burst), input remap (axis consistency), charge shot recoil. ABL-07 removed per D-21.
  **Plans:** 3 plans
  Plans:
  - [x] 09-01-PLAN.md — Zone hazard tiles, input remap (drill to DOWN+SPACE), charge recoil, item pickups, entity schema
  - [x] 09-02-PLAN.md — Bubble Shield (ABL-05): auto-fuse, passive drain, tier progression, shield VFX
  - [x] 09-03-PLAN.md — Slime Boost (ABL-06): fused airborne burst, multi-tap chaining, enemy stomp damage
- [x] Phase 10: Nitro-Ejection & Endgame (ABL-02) (completed 2026-03-28)
  **Goal:** CRACKED_V vertical gate breaking (Drill Dive down + Boost up), gamepad controller support, minimal ability VFX, Goo-Mold cleanup, and ability tuning pass
  **Plans:** 3 plans
  Plans:
  - [x] 10-01-PLAN.md — CRACKED_V breaking (Drill Dive + Boost) + Goo-Mold removal
  - [x] 10-02-PLAN.md — Gamepad controller support via _ACTION_MAP extension
  - [x] 10-03-PLAN.md — Ability VFX + gamepad playtest tuning checkpoint
- [ ] Phase 11: Save System & HUD (SYS-01, SYS-02, SYS-03, SYS-04)
  **Goal:** Save rooms/checkpoints with JSON persistence, mini-map HUD bar, pause screen with macro-map view, heart/juice capacity upgrades, fix map.py legacy gate scan hardcoded +16
  **Requirements:** SYS-01, SYS-02, SYS-03, SYS-04
  **Gap Closure:** Closes remaining gaps from v1.1 milestone audit (4 unsatisfied SYS requirements + 1 low-severity integration fix)
- [x] Phase 12: Screen Size Expansion (320x180 display, 320x192 rooms) (completed 2026-03-28)
  **Goal:** Expand display from 128x128 to 320x192 with Super Metroid-style 16px bottom HUD strip, 320x176 game viewport, central screen constants, and updated LDtk assets
  **Plans:** 3 plans
  Plans:
  - [x] 12-01-PLAN.md — Central screen constants + hardcoded 128 replacement + test updates
  - [x] 12-02-PLAN.md — Draw pipeline restructure + HUD strip (HP pips, juice meter)
  - [x] 12-03-PLAN.md — Asset updates (LDtk, entity-schema, export script, converter docs)
- [x] Phase 13: Sprite Scale & PNG Spritesheet Support (SPR-01, SPR-02, SPR-03, SPR-04, SPR-05) (completed 2026-03-29)
  **Goal:** Draw all entities at 2x visual scale (16x16 rendered, 8x8 collision) for better readability at 320x176, replace Pyxel image bank sprites with PNG spritesheet loading (Aseprite workflow), and update entity-schema.json with sprite metadata for the map converter
  **Plans:** 3 plans
  Plans:
  - [x] 13-01-PLAN.md — Migration tool (upscale_sprites.py) + PNG/JSON asset generation
  - [x] 13-02-PLAN.md — Loading pipeline (PNG manifest replacing pyxres) + sprite constants + draw helper
  - [x] 13-03-PLAN.md — Entity draw updates (all 7 files to 16x16/32x32) + entity-schema sprite metadata
  **Dependencies:** Phase 12
- [x] Phase 14: Tech Debt & Schema Cleanup (completed 2026-03-30)
  **Goal:** Event-gated door system (add "event" action + event_id field, deprecate tile ID 4), fix map.py legacy gate scan, clean orphaned code, fix 6 test failures, verify Phase 10
  **Requirements:** MAP-02 (rewrite), ABL-02 (verification)
  **Gap Closure:** Closes gaps from v1.1 milestone audit
  **Plans:** 3 plans
  Plans:
  - [x] 14-01-PLAN.md -- Event-gated door schema + Door.check_event_open + event_flags integration
  - [x] 14-02-PLAN.md -- Debug decoupling (replace DEBUG_ALL_ABILITIES with god-mode module) + test fixes
  - [x] 14-03-PLAN.md -- Orphaned code cleanup, schema intgrid 4 rename, ABL-02 verification, requirement rewrites

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|---------------|--------|-----------|
| 1. Core Movement & Physics | v1.0 | 2/2 | Complete | 2026-03-12 |
| 2. Slime Companion & Fusion | v1.0 | 4/4 | Complete | 2026-03-13 |
| 3. Destructive World & Boss | v1.0 | 4/4 | Complete | 2026-03-14 |
| 4. Level Interactivity & Items | v1.0 | 2/2 | Complete | 2026-03-15 |
| 5. New Enemies & Player Health | v1.0 | 2/2 | Complete | 2026-03-14 |
| 6. Physics Refinement & Test Gaps | v1.0 | 1/1 | Complete | 2026-03-22 |
| 7. Macro-Map & Room Persistence | v1.1 | 2/2 | Complete | 2026-03-27 |
| 8. New Fusion Abilities | v1.1 | 6/6 | Complete | 2026-03-28 |
| 9. Defensive Mechanics | v1.1 | 3/3 | Complete | 2026-03-28 |
| 10. Nitro-Ejection & Endgame | v1.1 | 3/3 | Complete   | 2026-03-28 |
| 11. Save System & HUD | v1.1 | 0/? | Not started | - |
| 12. Screen Size Expansion | v1.1 | 3/3 | Complete    | 2026-03-28 |
| 13. Sprite Scale & PNG Spritesheets | v1.1 | 3/3 | Complete    | 2026-03-29 |
| 14. Tech Debt & Schema Cleanup | v1.1 | 3/3 | Complete    | 2026-03-29 |
