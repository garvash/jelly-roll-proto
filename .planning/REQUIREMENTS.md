# Requirements - Jelly Roll Proto v1.1

## World & Exploration (MAP)
- [ ] **MAP-01**: Implement 5x5 Grid room switching with camera snapping (128x128 px).
- [ ] **MAP-02**: Z-Spiral world layout with 20-25 unique rooms based on Design Guide.
- [ ] **MAP-03**: State persistence across rooms (broken blocks, collected items).
- [ ] **MAP-04**: Biome-specific tile identification (Cracked Wall, Goo-Mold).

## Abilities & Fusion (ABL)
- [x] **ABL-01**: Slime Ram fusion (Forward Dash) with horizontal gating capability.
- [ ] **ABL-02**: Nitro-Ejection fusion (Infinite Jump) for vertical endgame traversal.
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
