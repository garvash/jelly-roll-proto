# Phase 01: Core Movement & Physics - Plan

This phase implements the foundational movement system for Slime Drill Proto. It focuses on achieving a high-quality, responsive "Celeste-style" feel using a custom kinematic character controller in Pyxel.

## Plan Frontmatter
- **wave:** 1
- **depends_on:** []
- **files_modified:**
  - src/core/constants.py
  - src/entities/player.py
  - src/level/map.py
  - main.py
  - assets/game.pyxres
  - tests/test_physics.py
- **autonomous:** true

## Tasks

<tasks>
  <task id="01-01-00" requirement="MOV-01" wave="1">
    <description>Initialize project structure, Pyxel boilerplate, and testing infrastructure.</description>
    <step>Create `src/core/constants.py` with initial physics parameters (Gravity, Accel, Friction).</step>
    <step>Create `src/level/map.py` with basic tilemap collision detection logic (AABB against Tilemap).</step>
    <step>Setup `main.py` as the Pyxel application entry point with a basic update/draw loop.</step>
    <step>Initialize `tests/test_physics.py` with stubs for movement validation.</step>
  </task>

  <task id="01-01-01" requirement="MOV-01" wave="2">
    <description>Implement responsive Walk physics and Ground Feel.</description>
    <step>Create `Player` class in `src/entities/player.py` with a Finite State Machine (IDLE, RUNNING).</step>
    <step>Implement horizontal movement with high acceleration and instant stop (snappy feel).</step>
    <step>Verify walk speed and friction against `src/core/constants.py` values.</step>
  </task>

  <task id="01-01-02" requirement="MOV-01" wave="2">
    <description>Implement Weighted Variable Jump and forgiving jump mechanics.</description>
    <step>Add JUMPING and FALLING states to the Player FSM.</step>
    <step>Implement variable jump height (jump force stops on button release).</step>
    <step>Implement weighted gravity (increased fall gravity) for a "snappy" downward arc.</step>
    <step>Add Coyote Time (20 frames) and Jump Buffering (6 frames) for forgiving controls.</step>
  </task>

  <task id="01-01-03" requirement="MOV-01" wave="3">
    <description>Implement Wall Slide and Wall Jump mechanics.</description>
    <step>Add WALL_SLIDING state to the Player FSM.</step>
    <step>Implement detection for walls and apply reduced downward velocity while sliding.</step>
    <step>Implement Wall Jump with horizontal impulse away from the wall.</step>
  </task>

  <task id="01-01-04" requirement="MOV-02" wave="3">
    <description>Implement Grounded and Airborne Dash with collision safety.</description>
    <step>Add DASHING state to the Player FSM.</step>
    <step>Implement high-speed dash burst with fixed duration.</step>
    <step>Implement sub-stepping collision checks during Dash to prevent tunneling through tiles.</step>
    <step>Add dash cooldown and reset logic (reset on ground touch).</step>
  </task>

  <task id="01-01-05" requirement="MOV-01, MOV-02" wave="4">
    <description>Final polish, assets, and "Gym" level verification.</description>
    <step>Create `assets/game.pyxres` with basic 16x16 player sprite and 8x8 tilemap tiles.</step>
    <step>Design a "Physics Gym" level in the tilemap containing pits, high walls, and dash gaps.</step>
    <step>Final tuning of physics constants in `src/core/constants.py` to match "Celeste-style" feel.</step>
  </task>
</tasks>

## Verification Criteria

### Automated Tests
- `pytest tests/test_physics.py -k "walk"`: Verifies horizontal velocity and stopping.
- `pytest tests/test_physics.py -k "jump"`: Verifies jump impulse and gravity scaling.
- `pytest tests/test_physics.py -k "wall"`: Verifies wall slide friction and wall jump impulse.
- `pytest tests/test_physics.py -k "dash"`: Verifies dash speed and sub-stepping collision safety.

### Manual Verification
- **Coyote Time:** Confirm the player can jump for a short window after walking off a ledge.
- **Jump Buffering:** Confirm a jump executes if the button is pressed slightly before landing.
- **Variable Jump:** Confirm tapping jump results in a shorter hop than holding it.
- **Dash Feel:** Confirm the dash is fast but controllable and does not clip through walls.
- **Gym Level:** Successfully navigate all obstacles in the physics gym using the combined moveset.

## Must Haves (Goal-Backward)
- [x] Player moves horizontally with immediate response (MOV-01).
- [x] Player jumps with variable height and weighted falling physics (MOV-01).
- [x] Controls feel forgiving via Coyote Time and Jump Buffering (MOV-01).
- [x] Player can slide down and jump off walls (MOV-01).
- [x] Player can perform a directional dash in the air or on ground (MOV-02).
- [x] Collision system prevents clipping through tiles at high speeds (MOV-02).
