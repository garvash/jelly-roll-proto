# Roadmap - Jelly Roll Proto

## Milestone v1.0: Core Vertical Slice (Complete)
- [x] Phase 1: Core Movement & Physics
- [x] Phase 2: Slime Companion & Fusion
- [x] Phase 3: Destructive World & Boss
- [x] Phase 4: Level Interactivity & Items
- [x] Phase 5: New Enemies & Player Health
- [x] Phase 6: Physics Refinement & Test Gaps

---

## Milestone v1.1: World Expansion & New Abilities

### Phase 07: Macro-Map & Room Persistence
**Goal:** Establish the 5x5 Z-Spiral world layout and ensure game state persists across room transitions.
- [ ] **MAP-01**: Implement 5x5 Grid room switching with camera snapping (128x128 px).
- [ ] **MAP-02**: Z-Spiral world layout with 20-25 unique rooms based on Design Guide.
- [ ] **MAP-03**: State persistence across rooms (broken blocks, collected items).
- [ ] **MAP-04**: Biome-specific tile identification (Cracked Wall, Goo-Mold).
**Success Criteria:**
1. Camera snaps correctly when moving between 128x128 grid cells.
2. 5x5 world layout (25 rooms) is traversable.
3. Broken blocks and collected items persist when re-entering a room.
4. Biome-specific tiles are correctly identified by the engine.

### Phase 08: Horizontal Mastery & Slime Control
**Goal:** Introduce the Slime Ram fusion and refine the player's ability to command the slime.
- [ ] **ABL-01**: Slime Ram fusion (Forward Dash) with horizontal gating capability.
- [ ] **ABL-03**: Directional Slime Hold (Tap left/right to position and freeze slime).
- [ ] **ABL-04**: Charge Slime Shot (Hold button to increase power/size).
**Success Criteria:**
1. Slime Ram dash breaks specific "horizontal" gates.
2. Slime can be positioned and frozen in place with tap-hold.
3. Charge Shot increases in size and power based on hold duration.

### Phase 09: Defense & Utility
**Goal:** Add defensive options and environmental manipulation tools.
- [ ] **ABL-05**: Bubble Shield (Consumes juice on hit).
- [ ] **ABL-06**: Yoshi-style Double Jump.
- [ ] **ABL-07**: Reform Block (Expend Max Juice to fill gaps in terrain).
**Success Criteria:**
1. Bubble Shield correctly mitigates damage at the cost of juice.
2. Yoshi-style double jump allows for extended air time.
3. Reform Block successfully fills gaps in terrain using Max Juice.

### Phase 10: Vertical Mastery & Endgame
**Goal:** Implement the final traversal ability for vertical exploration and endgame escape.
- [ ] **ABL-02**: Nitro-Ejection fusion (Infinite Jump) for vertical endgame traversal.
**Success Criteria:**
1. Nitro-Ejection allows for infinite upward traversal.
2. Vertical endgame gates are accessible using Nitro-Ejection.

### Phase 11: Systems, UI & Polish
**Goal:** Finalize the micro-Metroidvania experience with save points, a functional map, and meta-progression.
- [ ] **SYS-01**: Save Rooms/Checkpoints with JSON persistence.
- [ ] **SYS-02**: Mini-map HUD bar (showing room grid and current location).
- [ ] **SYS-03**: Pause Screen with full Macro-Map view.
- [ ] **SYS-04**: Heart Containers and Juice Capacity upgrade items.
**Success Criteria:**
1. Save points correctly serialize and deserialize game state.
2. Mini-map HUD shows current room position in the 5x5 grid.
3. Pause screen displays the full 5x5 macro-map.
4. Heart and Juice upgrades correctly increase player stats.
