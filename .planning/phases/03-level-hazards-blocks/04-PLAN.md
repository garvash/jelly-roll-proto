# Phase 04 Plan: Giant Mole Boss & Progression

**Goal:** Implement the Giant Mole Boss, Slime Spit (Projectile), and the final victory flow to complete the prototype vertical slice.

## Tasks

### Wave 01: Slime Spit & Assets
- [ ] **SPR-01**: Update `generate_assets.py` with Mole (16x16) and Projectile (4x4) sprites.
- [ ] **SPR-02**: Run `generate_assets.py` to update `assets/game.pyxres`.
- [ ] **SLM-03**: Implement `src/entities/projectile.py`.
- [ ] **SLM-04**: Add `Slime.spit()` and `Player` input (Z-key) to trigger it.

### Wave 02: Giant Mole Entity
- [ ] **BOSS-01**: Implement `src/entities/boss.py` with FSM (Burrow, Emerge, Stunned).
- [ ] **BOSS-02**: Integrate Mole into `Game` class (Update/Draw).
- [ ] **BOSS-03**: Implement collision detection (Projectile vs Mole, Player vs Mole).

### Wave 03: Vulnerability & Damage
- [ ] **BOSS-04**: Implement Mole health (e.g., 3 hits).
- [ ] **BOSS-05**: Implement Drill Dive damage condition (Only while Stunned).
- [ ] **JUICE-01**: Balance Juice costs (Spit: 25, Drill Activation: 5, Impact: 15).

### Wave 04: Progression & Victory
- [ ] **PROG-01**: Add simple "Victory" screen (Game State: WON).
- [ ] **PROG-02**: Trigger Boss fight when reaching specific X/Y or clearing specific blocks.
- [ ] **TEST-01**: Add automated tests for Projectile and Boss FSM.

## Verification Strategy

### Automated Tests
- `test_projectile_movement`: Verify speed and direction.
- `test_projectile_collision`: Verify destruction on wall hit.
- `test_boss_fsm_transition`: Verify Burrow -> Emerge -> Stunned (on hit).
- `test_boss_damage`: Verify damage only taken during Stunned state via Drill Dive.

### Manual Verification
- Verify Boss visuals (multi-tile rendering).
- Verify Juice management loop (Spit -> Stun -> Dive -> Damage).
- Verify Victory screen trigger.

---
*Phase: 04-boss-progression*
*Plan created: 2026-03-14*
