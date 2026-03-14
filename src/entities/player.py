import pyxel
from src.core.constants import *

class Player:
    def __init__(self, x, y, level_map, game=None):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.w = 8
        self.h = 8
        self.dx = 0
        self.dy = 0
        self.level_map = level_map
        self.game = game
        self.is_grounded = False
        self.is_alive = True
        self.facing_right = True
        self.state = "IDLE" # IDLE, RUNNING, JUMPING, FALLING, WALL_SLIDING, DASHING

        # Forgiving mechanics timers
        self.coyote_timer = 0
        self.jump_buffer_timer = 0
        self.is_wall_sliding = False
        self.wall_dir = 0 # -1 for left wall, 1 for right wall

        # Dash mechanics
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        self.can_dash = True
        self.dash_dir = (0, 0)

        # Fusion
        self.is_fused = False

    def update(self, slime):
        if not self.is_alive:
            return

        self.update_timers()
        self.handle_input(slime)
        if self.state == "DIVING":
            self.apply_diving_physics(slime)
            self.move_and_collide(slime)
        elif self.dash_timer > 0:
            self.apply_dash()
        else:
            self.apply_physics()
            self.move_and_collide()
        self.update_state()

    def die(self):
        if self.is_alive:
            self.is_alive = False
            self.dx = 0
            self.dy = 0
            self.state = "DEAD"

    def on_block_break(self):
        # Trigger juice effects
        if self.game:
            self.game.shake_timer = DRILL_SHAKE_DURATION
            self.game.stop_frames = DRILL_HITSTOP_FRAMES

    def update_timers(self):
        if self.is_grounded:
            self.coyote_timer = COYOTE_TIME
            self.can_dash = True
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1

        if pyxel.btnp(pyxel.KEY_SPACE):
            self.jump_buffer_timer = JUMP_BUFFER
        elif self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1

        if self.dash_timer > 0:
            self.dash_timer -= 1
        
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 1

    def handle_input(self, slime):
        # Slime Spit
        if pyxel.btnp(pyxel.KEY_Z) and not self.is_fused and self.state != "DIVING":
            import math
            target_dx = 1 if self.facing_right else -1
            target_dy = -0.5 # Default lob up

            # Auto-aim at boss if alive
            if self.game and self.game.mole and self.game.mole.is_alive:
                # Target slightly above center to account for arc
                vx = (self.game.mole.x + 8) - (slime.x + 4)
                vy = (self.game.mole.y + 0) - (slime.y + 4) # Aim at top of mole
                dist = math.sqrt(vx*vx + vy*vy)
                if dist > 0:
                    target_dx = vx / dist
                    target_dy = (vy / dist) - 0.3 # Extra lift for the arc

            proj = slime.spit(target_dx, target_dy, self.level_map)
            if proj and self.game:
                self.game.projectiles.append(proj)

        # Drill Dive Activation
        if (pyxel.btn(pyxel.KEY_DOWN) and pyxel.btnp(pyxel.KEY_SPACE) and 
            not self.is_grounded and slime.juice > 0 and self.state != "DIVING"):
            dist_sq = (self.x - slime.x)**2 + (self.y - slime.y)**2
            if dist_sq < SLIME_MAX_DIST**2:
                self.state = "DIVING"
                self.is_fused = True
                self.dy = DRILL_SPEED
                self.dx = 0
                self.dash_timer = 0
                slime.consume(DRILL_ACTIVATION_COST)
                return

        # Drill Dive Cancellation
        if self.state == "DIVING":
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.state = "FALLING"
                self.is_fused = False
                self.dy = 0 # Small boost or just stop? Plan says transition to FALLING.
            return

        # Horizontal Movement
        target_dx = 0
        move_input_x = 0
        if pyxel.btn(pyxel.KEY_LEFT):
            target_dx -= WALK_ACCEL
            move_input_x = -1
            self.facing_right = False
        if pyxel.btn(pyxel.KEY_RIGHT):
            target_dx += WALK_ACCEL
            move_input_x = 1
            self.facing_right = True

        # Vertical Movement (for dash direction)
        move_input_y = 0
        if pyxel.btn(pyxel.KEY_UP):
            move_input_y = -1
        if pyxel.btn(pyxel.KEY_DOWN):
            move_input_y = 1

        if self.dash_timer <= 0:
            if target_dx != 0:
                self.dx += target_dx
            else:
                # Friction
                if self.dx > 0:
                    self.dx = max(0, self.dx - WALK_FRICTION)
                elif self.dx < 0:
                    self.dx = min(0, self.dx + WALK_FRICTION)
            
            # Clamp horizontal speed
            self.dx = max(-MAX_WALK_SPEED, min(self.dx, MAX_WALK_SPEED))

        # Dash
        if pyxel.btnp(pyxel.KEY_X) and self.can_dash and self.dash_cooldown_timer <= 0:
            self.dash_timer = DASH_DURATION
            self.dash_cooldown_timer = DASH_COOLDOWN
            self.can_dash = False
            
            # Determine dash direction
            if move_input_x == 0 and move_input_y == 0:
                # Default to facing direction (if we tracked it, but for now just last dx)
                d_x = 1 if self.dx >= 0 else -1
                d_y = 0
            else:
                d_x = move_input_x
                d_y = move_input_y
            
            self.dash_dir = (d_x, d_y)
            # Normalize? For 8-way movement, diagonal should be slightly slower or we just use fixed values
            # For simplicity, let's just use fixed speed
            self.dx = self.dash_dir[0] * DASH_SPEED
            self.dy = self.dash_dir[1] * DASH_SPEED

        # Check for walls
        on_left_wall = self.level_map.check_collision(self.x - 1, self.y, 1, self.h)
        on_right_wall = self.level_map.check_collision(self.x + self.w, self.y, 1, self.h)
        
        self.is_wall_sliding = False
        self.wall_dir = 0
        if not self.is_grounded and self.dy > 0 and self.dash_timer <= 0:
            if on_left_wall and move_input_x == -1:
                self.is_wall_sliding = True
                self.wall_dir = -1
            elif on_right_wall and move_input_x == 1:
                self.is_wall_sliding = True
                self.wall_dir = 1

        # Jump
        if self.jump_buffer_timer > 0 and self.dash_timer <= 0:
            if self.coyote_timer > 0:
                self.dy = JUMP_FORCE
                self.is_grounded = False
                self.coyote_timer = 0
                self.jump_buffer_timer = 0
            elif self.is_wall_sliding or (on_left_wall and not self.is_grounded) or (on_right_wall and not self.is_grounded):
                # Wall Jump
                jump_dir = -1 if (on_right_wall) else 1
                self.dx = jump_dir * WALL_JUMP_X_IMPULSE
                self.dy = WALL_JUMP_Y_FORCE
                self.jump_buffer_timer = 0
                self.is_wall_sliding = False

        # Variable Jump Height (cut velocity on release)
        if pyxel.btnr(pyxel.KEY_SPACE) and self.dy < 0 and self.dash_timer <= 0:
            self.dy *= VARIABLE_JUMP_REDUCTION

    def apply_dash(self):
        # Sub-stepping collision for Dash
        steps = int(DASH_SPEED) # Move 1 pixel at a time max
        if steps == 0: steps = 1
        
        step_dx = self.dx / steps
        step_dy = self.dy / steps
        
        for _ in range(steps):
            # Move X
            self.x += step_dx
            if self.level_map.check_hazard(self.x, self.y, self.w, self.h):
                self.die()
                return

            if self.level_map.check_collision(self.x, self.y, self.w, self.h):
                if step_dx > 0:
                    self.x = (int((self.x + self.w - 1) // TILE_SIZE)) * TILE_SIZE - self.w
                elif step_dx < 0:
                    self.x = (int(self.x // TILE_SIZE) + 1) * TILE_SIZE
                self.dx = 0
                self.dash_timer = 0
                break
            
            # Move Y
            self.y += step_dy
            if self.level_map.check_hazard(self.x, self.y, self.w, self.h):
                self.die()
                return

            if self.level_map.check_collision(self.x, self.y, self.w, self.h):
                if step_dy > 0:
                    self.y = (int((self.y + self.h - 1) // TILE_SIZE)) * TILE_SIZE - self.h
                    self.is_grounded = True
                elif step_dy < 0:
                    self.y = (int(self.y // TILE_SIZE) + 1) * TILE_SIZE
                self.dy = 0
                self.dash_timer = 0
                break
        
        if self.dash_timer == 0:
            # End dash with some residual velocity?
            # Usually Dash just stops or transitions to fall
            pass

    def apply_diving_physics(self, slime):
        self.dy = DRILL_SPEED
        # Horizontal drift
        if pyxel.btn(pyxel.KEY_LEFT):
            self.dx = -DRILL_DRIFT_SPEED
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.dx = DRILL_DRIFT_SPEED
        else:
            self.dx = 0
            
        # Out of juice check
        if slime.juice <= 0:
            self.state = "FALLING"
            self.is_fused = False

    def apply_physics(self):
        # Weighted Gravity (increased gravity when falling)
        if self.is_wall_sliding:
            # Wall slide friction (reduced gravity)
            curr_gravity = GRAVITY
            self.dy = min(self.dy + curr_gravity * WALL_SLIDE_FRICTION, MAX_FALL_SPEED * 0.5)
        elif not self.is_grounded or self.state == "DIVING":
            curr_gravity = GRAVITY
            if self.dy > 0:
                curr_gravity *= FALLING_GRAVITY_MULTIPLIER
            self.dy += curr_gravity
            if self.dy > MAX_FALL_SPEED:
                self.dy = MAX_FALL_SPEED
        else:
            self.dy = 0

    def move_and_collide(self, slime=None):
        # Separate horizontal and vertical movement for simple collision
        # Move horizontal
        self.x += self.dx
        if self.level_map.check_hazard(self.x, self.y, self.w, self.h):
            self.die()
            return

        if self.level_map.check_collision(self.x, self.y, self.w, self.h):
            if self.dx > 0:
                self.x = (int((self.x + self.w - 1) // TILE_SIZE)) * TILE_SIZE - self.w
            elif self.dx < 0:
                self.x = (int(self.x // TILE_SIZE) + 1) * TILE_SIZE
            self.dx = 0

        # Move vertical
        self.y += self.dy
        if self.level_map.check_hazard(self.x, self.y, self.w, self.h):
            self.die()
            return

        # Collision detection
        collision = self.level_map.check_collision(self.x, self.y, self.w, self.h)
        
        # Grounding check (look 1px down) to maintain state and prevent jitter
        if not collision and self.dy >= 0:
            if self.level_map.check_collision(self.x, self.y + 1, self.w, self.h):
                collision = True

        if collision:
            if self.dy >= 0:
                # Check for destructible tiles during Drill Dive
                if self.state == "DIVING" and slime:
                    tile_coord = self.level_map.get_destructible_at(self.x, self.y, self.w, self.h)
                    if tile_coord:
                        tx, ty = tile_coord
                        self.level_map.remove_tile(tx, ty)
                        slime.refill(DRILL_BLOCK_REFUND)
                        self.on_block_break()
                        # Do not stop DIVING yet, let it continue through the broken block
                        return

                # Snap to floor
                target_row = int((self.y + self.h) // TILE_SIZE)
                self.y = target_row * TILE_SIZE - self.h
                self.is_grounded = True
                
                # Impact consumption
                if self.state == "DIVING" and slime:
                    slime.consume(DRILL_IMPACT_COST)
                    self.state = "IDLE" # Landed
                    self.is_fused = False
                
                self.dy = 0
            elif self.dy < 0:
                # Snap to ceiling
                self.y = (int(self.y // TILE_SIZE) + 1) * TILE_SIZE
                self.dy = 0
        else:
            self.is_grounded = False

    def update_state(self):
        if self.state == "DIVING":
            return # State managed by handle_input/physics/collision
        if self.dash_timer > 0:
            self.state = "DASHING"
        elif self.is_wall_sliding:
            self.state = "WALL_SLIDING"
        elif not self.is_grounded:
            if self.dy < 0:
                self.state = "JUMPING"
            else:
                self.state = "FALLING"
        elif self.dx != 0:
            self.state = "RUNNING"
        else:
            self.state = "IDLE"

    def draw(self):
        if not self.is_alive:
            # Flashing death effect
            if pyxel.frame_count % 4 < 2:
                # Draw player as a red block or flash
                pyxel.rect(self.x, self.y, self.w, self.h, 8) # 8 is red in default palette
            return

        # Draw player sprite (8x8) from image 0, at (8, 0)
        # Flip based on facing direction
        w = self.w if self.facing_right else -self.w
        pyxel.blt(self.x, self.y, 0, 8, 0, w, self.h, 0)
