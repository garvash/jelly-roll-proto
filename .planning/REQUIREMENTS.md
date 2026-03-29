# Requirements - Jelly Roll Proto v1.1

## World & Exploration (MAP)
- [ ] **MAP-01**: Implement 5x5 Grid room switching with camera snapping (128x128 px).
- [x] **MAP-02**: Room layouts driven by pml-to-ldtk pipeline with event-gated doors (replaces tile ID 4 boss gates). (2026-03-30)
- [ ] **MAP-03**: State persistence across rooms (broken blocks, collected items).
- [ ] **MAP-04**: Biome-specific tile identification (Cracked Wall, Goo-Mold).

## Abilities & Fusion (ABL)
- [x] **ABL-01**: Slime Ram fusion (Forward Dash) with horizontal gating capability.
- [x] **ABL-02**: CRACKED_V vertical gating via Drill Dive (down) and Slime Boost (up). Infinite flight capstone deferred to Phase 11 (requires SYS-04 Juice Capacity upgrades). (2026-03-30)
- [x] **ABL-03**: Directional Slime Hold (Tap left/right to position and freeze slime). (2026-03-28)
- [x] **ABL-04**: Charge Slime Shot (Hold button to increase power/size).
- [x] **ABL-05**: Bubble Shield (Consumes juice on hit).
- [x] **ABL-06**: Yoshi-style Double Jump.
- [x] **ABL-07**: Reform Block (Expend Max Juice to fill gaps in terrain).

## Systems & UI (SYS)
- [ ] **SYS-01**: Save Rooms/Checkpoints with JSON persistence.
- [ ] **SYS-02**: Mini-map HUD bar (showing room grid and current location).
- [ ] **SYS-03**: Pause Screen with full Macro-Map view.
- [ ] **SYS-04**: Heart Containers and Juice Capacity upgrade items.

## Out of Scope
- Dynamic lighting (Stick to Pyxel's palette).
- Complex AI state machines (Keep shmup-style patterns).
- Multiple save slots (Single slot for prototype).

## Traceability
- **Phase 07**: MAP-01, MAP-02, MAP-03, MAP-04
- **Phase 08**: ABL-01, ABL-03, ABL-04
- **Phase 09**: ABL-05, ABL-06, ABL-07
- **Phase 10**: ABL-02
- **Phase 11**: SYS-01, SYS-02, SYS-03, SYS-04
- **Phase 14**: MAP-02 (rewrite), ABL-02 (verification)
