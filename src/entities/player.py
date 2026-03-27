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
        self.state = "IDLE" # IDLE, RUNNING, JUMPING, FALLING, WALL_SLIDING

        # Forgiving mechanics timers
        self.coyote_timer = 0
        self.jump_buffer_timer = 0
        self.is_wall_sliding = False
        self.wall_dir = 0 # -1 for left wall, 1 for right wall

        # Fusion
        self.is_fused = False

        # Health & Combat
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.invuln_timer = 0
        self.knockback_timer = 0
        self.kick_timer = 0

        # Upgrades
        self.has_drill = False # Must find item to use Drill Dive

    def update(self, slime):
        if not self.is_alive:
            return

        self.update_timers()
        self.handle_input(slime)
        if self.state == "DIVING":
            self.apply_diving_physics(slime)
            self.move_and_collide(slime)
        else:
            self.apply_physics()
            self.move_and_collide()
        self.update_state()

    def take_damage(self, amount, source_x=None):
        if self.invuln_timer > 0 or not self.is_alive:
            return False

        self.hp -= amount
        self.invuln_timer = INVULN_DURATION
        
        # Reset dive states
        self.is_fused = False
        
        # Apply knockback
        if source_x is not None:
            kx = -KNOCKBACK_FORCE_X if self.x < source_x else KNOCKBACK_FORCE_X
            self.dx = kx
            self.dy = KNOCKBACK_FORCE_Y
            self.knockback_timer = 10 # Disable input for a moment
            self.is_grounded = False

        if self.hp <= 0:
            self.die()
        
        return True

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
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1

        if pyxel.btnp(pyxel.KEY_SPACE):
            self.jump_buffer_timer = JUMP_BUFFER
        elif self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1

        if self.invuln_timer > 0:
            self.invuln_timer -= 1
        
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
        
        if self.kick_timer > 0:
            self.kick_timer -= 1

    def kick(self, slime):
        self.kick_timer = KICK_DURATION
        
        # Kick area: 8 pixels in front
        kx = self.x + (8 if self.facing_right else -8)
        ky = self.y
        
        # 1. Flip Switches
        tx, ty = int(kx // TILE_SIZE), int(ky // TILE_SIZE)
        if self.level_map.is_switch(tx, ty):
            if self.game:
                self.level_map.toggle_switch(tx, ty, self.game.cam_x, self.game.cam_y)
        
        # 2. Punt Slime
        # Simple AABB for kick vs slime
        if (kx < slime.x + slime.w and kx + 8 > slime.x and
            ky < slime.y + slime.h and ky + 8 > slime.y):
            # Punt!
            p_dx = SLIME_PUNT_SPEED if self.facing_right else -SLIME_PUNT_SPEED
            p_dy = -2.0 # Slight lift
            slime.punt(p_dx, p_dy)
            # Impact feedback
            self.on_block_break()

    def handle_input(self, slime):
        if self.knockback_timer > 0:
            return

        # Slime Spit
        if pyxel.btnp(pyxel.KEY_Z) and not self.is_fused and self.state != "DIVING":
            import math
            # Default lob direction
            target_dx = 1 if self.facing_right else -1
            target_dy = -0.5 # Default lob up
            
            # Auto-aim logic
            if self.game:
                best_target = None
                min_dist = 999999
                
                # Combine boss and standard enemies for targeting
                all_potential_targets = []
                if self.game.mole and self.game.mole.is_alive:
                    all_potential_targets.append(self.game.mole)
                all_potential_targets.extend([e for e in self.game.enemies if e.is_alive])
                
                for target in all_potential_targets:
                    # Check if target is in current room/camera view
                    t_cam_x = (target.x // 128) * 128
                    t_cam_y = (target.y // 128) * 128
                    if t_cam_x != self.game.cam_x or t_cam_y != self.game.cam_y:
                        continue
                        
                    # Filter by facing direction
                    in_direction = (target.x > self.x) if self.facing_right else (target.x < self.x)
                    if not in_direction:
                        continue
                        
                    # Find closest
                    dx = (target.x + target.w/2) - (slime.x + 4)
                    dy = (target.y + target.h/2) - (slime.y + 4)
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    if dist < min_dist:
                        min_dist = dist
                        best_target = (dx, dy)
                
                if best_target:
                    dx, dy = best_target
                    target_dx = dx / min_dist
                    target_dy = (dy / min_dist) - 0.2 # Slight lift for arc

            proj = slime.spit(target_dx, target_dy, self.level_map)
            if proj and self.game:
                self.game.projectiles.append(proj)

        # Drill Dive Activation
        if (self.has_drill and pyxel.btn(pyxel.KEY_DOWN) and pyxel.btnp(pyxel.KEY_SPACE) and 
            not self.is_grounded and slime.juice > 0 and self.state != "DIVING"):
            dist_sq = (self.x - slime.x)**2 + (self.y - slime.y)**2
            if dist_sq < SLIME_MAX_DIST**2:
                self.state = "DIVING"
                self.is_fused = True
                self.dy = DRILL_SPEED
                self.dx = 0
                slime.consume(DRILL_ACTIVATION_COST)
                return

        # Kick Implementation
        if pyxel.btnp(pyxel.KEY_V) and self.kick_timer <= 0 and self.state != "DIVING":
            self.kick(slime)

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

        # Check for walls
        on_left_wall = self.level_map.check_collision(self.x - 1, self.y, 1, self.h)
        on_right_wall = self.level_map.check_collision(self.x + self.w, self.y, 1, self.h)
        
        self.is_wall_sliding = False
        self.wall_dir = 0
        if not self.is_grounded and self.dy > 0:
            if on_left_wall and move_input_x == -1:
                self.is_wall_sliding = True
                self.wall_dir = -1
            elif on_right_wall and move_input_x == 1:
                self.is_wall_sliding = True
                self.wall_dir = 1

        # Jump
        if self.jump_buffer_timer > 0:
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
        if pyxel.btnr(pyxel.KEY_SPACE) and self.dy < 0:
            self.dy *= VARIABLE_JUMP_REDUCTION

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
            self.take_damage(1)
            if self.is_alive and self.game:
                self.x = self.game.room_spawn_x
                self.y = self.game.room_spawn_y
                self.dx = 0
                self.dy = 0
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
            self.take_damage(1)
            if self.is_alive and self.game:
                self.x = self.game.room_spawn_x
                self.y = self.game.room_spawn_y
                self.dx = 0
                self.dy = 0
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
                        # Record for regen before removing
                        if self.game:
                            self.game.on_block_destroyed(tx, ty, TILE_DESTRUCTIBLE)
                        self.level_map.remove_tile(tx, ty)
                        if self.game:
                            self.game.spawn_explosion(tx * 8, ty * 8, 9)
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
        if self.is_wall_sliding:
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

        # Animation logic
        u = 0 # Idle
        if self.state == "RUNNING":
            # Cycle between run0 (8, 0) and run1 (16, 0) every 6 frames
            u = 8 + (pyxel.frame_count // 6 % 2) * 8
        elif self.state == "JUMPING" or self.state == "FALLING":
            u = 16 # Use run1 as a "jump" frame for now

        # Draw player sprite (8x8) from image 1
        # Flip based on facing direction
        w = self.w if self.facing_right else -self.w
        pyxel.blt(self.x, self.y, 1, u, 0, w, self.h, 0)

