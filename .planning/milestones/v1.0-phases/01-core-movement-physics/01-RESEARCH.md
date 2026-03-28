# Phase 01: Core Movement & Physics - Research

**Objective:** Research and define the parameters, systems, and logic required to implement high-quality, "Celeste-style" platforming physics (MOV-01, MOV-02) in Pyxel.

## 1. The "Celeste-Style" Movement Feel
To achieve the requested "snappy, weighted, and forgiving" feel, the implementation must focus on several core mechanics:

### Game Feel Mechanics (Decided)
- **Coyote Time (20 frames):** Allows the player to jump for a short window after leaving a platform.
- **Jump Buffering (0.1s / ~6 frames):** Registers a jump input even if pressed shortly before landing, executing it immediately upon touching the ground.
- **Weighted Variable Jump:** Holding the jump button longer results in a higher jump. Gravity should scale up during the fall (Fast Falling) for a "snappy" landing.
- **Instant Stop:** High friction/acceleration to ensure the player doesn't slide when stopping, providing maximum precision.

## 2. Technical Implementation in Pyxel

### Physics Engine Strategy (AABB + Tilemap)
Pyxel does not have a built-in physics engine. We must implement a custom kinematic character controller.
- **Velocity-Based Movement:** Use `dx` and `dy` (delta x, delta y) to track movement per frame.
- **Tile-Based Collision:** Instead of pixel-perfect collision, check 4-8 specific points on the player's bounding box against the Pyxel tilemap (`pyxel.tilemap(0).pget(x, y)`).
- **Sub-Stepping:** To prevent tunneling (passing through walls at high speeds like Dashing), move the player in smaller increments and check for collisions at each step.

### Player State Machine (FSM)
To manage the complexity of Wall Sliding and Dashing, a Finite State Machine is required.
- **States:** `IDLE`, `RUNNING`, `JUMPING`, `FALLING`, `WALL_SLIDING`, `DASHING`.
- **Transitions:**
    - `JUMPING` -> `FALLING` (if velocity Y becomes positive/downward).
    - `FALLING` -> `WALL_SLIDING` (if touching a wall and moving downward).
    - `ANY` -> `DASHING` (if dash button pressed and cooldown is off).

## 3. Core Physics Constants (Estimates for Planning)
*Note: These will be tuned during execution.*

| Category | Parameter | Estimated Value | Purpose |
|----------|-----------|-----------------|---------|
| **General** | `GRAVITY` | 0.4 - 0.6 | Base downward force. |
| | `FALL_GRAVITY_MULT` | 1.5 - 2.0 | Increases gravity while falling for "weight." |
| | `MAX_FALL_SPEED` | 4.0 - 6.0 | Terminal velocity. |
| **Walk** | `ACCEL` | 0.8 - 1.2 | Speed gain per frame. |
| | `FRICTION` | 0.9 (or Instant) | Speed loss when no input. |
| | `MAX_RUN_SPEED` | 2.0 - 3.0 | Maximum horizontal speed. |
| **Jump** | `JUMP_FORCE` | -5.0 to -7.0 | Initial upward impulse. |
| | `COYOTE_TIME` | 20 frames | Grace period for ledge jumps. |
| | `JUMP_BUFFER` | 6 frames | Input window before landing. |
| **Wall** | `WALL_SLIDE_SPEED` | 0.5 - 1.0 | Fixed fall speed on walls. |
| | `WALL_JUMP_X` | 3.0 | Horizontal kick away from wall. |
| **Dash** | `DASH_SPEED` | 8.0 - 10.0 | High-speed burst. |
| | `DASH_DURATION` | 8 - 12 frames | How long the dash lasts. |

## 4. Pyxel Specific Constraints
- **Resolution:** 160x120 pixels (Standard 4:3 retro).
- **Update Rate:** 30 FPS (Standard Pyxel behavior).
- **Color Palette:** 16 fixed colors. Use high-contrast colors for the player (e.g., White/Blue) to ensure visibility in a "moody cavern."
- **Assets:** Use `pyxel edit` to create a 16x16 player sprite and an 8x8 tilemap for testing.

## 5. Potential Pitfalls & Solutions
- **Tunneling during Dash:** Solution: Check collisions multiple times during the dash move if speed exceeds tile size (8px).
- **Sticky Walls:** Solution: Only enter `WALL_SLIDE` if the player is actively pressing toward the wall, and allow a "neutral" fall if they pull away.
- **Floaty Jump:** Solution: Implement `FALL_GRAVITY_MULT` to make the downward arc faster than the upward arc.

## 6. Planning Recommendations
- **Module Structure:**
    - `src/core/constants.py`: Store all physics values for easy tuning.
    - `src/entities/player.py`: Encapsulate the FSM and movement logic.
    - `src/level/map.py`: Handle tilemap lookups and collision helpers.
- **Verification Strategy:** Create a "gym" level in `assets.pyxres` containing high walls, narrow gaps, and long pits to test every movement feature immediately.

---
*Phase: 01-core-movement-physics*
*Research completed: 2026-03-12*
