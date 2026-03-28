import pyxel
from src.core.constants import *
from src.entities.effects import Particle
import src.core.input as input_manager

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
        # Upgrades
        self.has_drill = False # Must find item to use Drill Dive
        self.has_dash = False  # Must find DashPickup item

        # Defensive abilities (Phase 9)
        self.has_shield = False     # Bubble Shield T1 (ABL-05, D-01)
        self.has_shield_t2 = False  # Bubble Shield T2 (D-05)
        self.has_boost = False      # Slime Boost (ABL-06, D-11)

        # Debug: unlock all abilities
        if DEBUG_ALL_ABILITIES:
            self.has_drill = True
            self.has_dash = True
            self.has_shield = True
            self.has_shield_t2 = True
            self.has_boost = True

        # Shield state
        self.shield_active = False
        self.shield_cooldown = 0    # Anti-flicker cooldown (Pitfall 2)
        self.hazard_hp_timer = 0    # Timer for HP drain in hazard zone without juice

        # Boost state
        self.boost_recommit_timer = 0  # Frames remaining in re-commit window

        # Dash (D-15)
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.dash_dx = 0
        self.dash_air_used = False  # Only one air dash per airborne

        # Fusion system (D-01 through D-05)
        self.is_charging_recall = False  # True when holding Z unfused (charging toward fusion)

        # Slime Ram (ABL-01, D-12)
        self.ram_dx = 0
        self.ram_dy = 0

        # Charge Shot Windup (gap fix)
        self.charge_windup_timer = 0

        # VFX state (D-10)
        self.shield_flash_timer = 0

    def fuse(self, slime):
        """Enter fused state. ALWAYS use this instead of setting is_fused directly (Pitfall 3)."""
        self.is_fused = True
        slime.is_fused = True
        slime.is_recalling = False
        slime.is_holding_position = False
        self.is_charging_recall = False

    def unfuse(self, slime, dissipate=False):
        """Exit fused state. ALWAYS use this instead of setting is_fused directly (Pitfall 3).
        If dissipate=True, slime enters burnout cooldown (D-05)."""
        self.is_fused = False
        slime.is_fused = False
        if dissipate:
            slime.dissipate()
        else:
            # Slime reforms near player
            slime.reform(self.x, self.y, self.facing_right, self.level_map)

    def start_ram(self, slime):
        """Activate Slime Ram -- fused V (D-12 through D-14). Shinespark/Crystal Dash style."""
        self.state = "RAMMING"
        self.ram_dx = RAM_SPEED if self.facing_right else -RAM_SPEED
        self.ram_dy = 0
        # Diagonal support: check UP/DOWN input for diagonal ram
        if input_manager.btn("up"):
            self.ram_dy = -RAM_SPEED * RAM_DIAGONAL_FACTOR
        elif input_manager.btn("down"):
            self.ram_dy = RAM_SPEED * RAM_DIAGONAL_FACTOR
        # Invincible during ram (D-12)
        self.invuln_timer = 9999  # Will be cleared on ram end

    def apply_ram_physics(self):
        """Ram movement: high speed in locked direction (D-12)."""
        self.dx = self.ram_dx
        self.dy = self.ram_dy

    def end_ram(self, slime):
        """End ram: unfuse, slime dissipates if juice empty (D-14)."""
        self.invuln_timer = DASH_IFRAMES  # Brief post-ram i-frames
        if slime.juice <= 0:
            self.unfuse(slime, dissipate=True)
        else:
            self.unfuse(slime)
        self.state = "FALLING" if not self.is_grounded else "IDLE"
        self.dx = 0
        self.dy = 0

    def update(self, slime):
        if not self.is_alive:
            return

        input_manager.update()  # Must run before any input checks
        self.update_timers()
        self.handle_input(slime)
        self.update_shield(slime)
        if self.state == "DIVING":
            self.apply_diving_physics(slime)
            self.move_and_collide(slime)
        elif self.state == "RAMMING":
            self.apply_ram_physics()
            self.move_and_collide(slime)
        elif self.state == "DASHING":
            self.apply_dash_physics()
            self.move_and_collide()
        elif self.state == "BOOSTING":
            self.update_boost(slime)
            self.apply_physics()  # Gravity applies during boost (player arcs between taps)
            self.move_and_collide(slime)
        elif self.state == "CHARGING_SHOT":
            self.update_charge_shot(slime)
            self.apply_physics()  # Gravity still applies during windup
            self.move_and_collide(slime)
        else:
            self.apply_physics()
            self.move_and_collide(slime)
        self.update_state()

    def take_damage(self, amount, source_x=None, slime=None):
        if self.invuln_timer > 0 or not self.is_alive:
            return False

        # Mana shield: fused damage consumes juice, not HP (D-04)
        if self.is_fused and slime and slime.juice > 0:
            slime.consume(MANA_SHIELD_COST)
            self.invuln_timer = INVULN_DURATION
            # Shield hit VFX (D-10): circle flash on damage absorption
            self.shield_flash_timer = 4
            # Check for juice-empty dissipation (D-05)
            if slime.juice <= 0:
                self.unfuse(slime, dissipate=True)
            # Apply knockback but no HP loss
            if source_x is not None:
                kx = -KNOCKBACK_FORCE_X if self.x < source_x else KNOCKBACK_FORCE_X
                self.dx = kx
                self.dy = KNOCKBACK_FORCE_Y
                self.knockback_timer = 10
                self.is_grounded = False
            return True

        self.hp -= amount
        self.invuln_timer = INVULN_DURATION

        # Reset dive states via unfuse if fused (Pitfall 3)
        if self.is_fused and slime:
            self.unfuse(slime)
        else:
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

        if input_manager.btnp("jump"):
            if self.state != "BOOSTING":  # Don't buffer jumps during boost (Pitfall 3)
                self.jump_buffer_timer = JUMP_BUFFER
        elif self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1

        if self.invuln_timer > 0:
            self.invuln_timer -= 1

        if self.knockback_timer > 0:
            self.knockback_timer -= 1

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.dash_timer > 0:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.state = "FALLING" if not self.is_grounded else "IDLE"

    def update_shield(self, slime):
        """Bubble Shield logic: auto-fuse on zone entry, passive drain, HP drain (ABL-05, D-01 through D-06)."""
        zone_type = self.level_map.get_zone_hazard_type(self.x, self.y, self.w, self.h)

        # Tick cooldown
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1

        # Auto-fuse on zone entry at full juice (D-01)
        if (zone_type and self.has_shield and not self.is_fused
                and not slime.is_dissipated and self.shield_cooldown <= 0
                and slime.juice >= slime.max_juice):
            self.fuse(slime)
            self.shield_active = True

        # Active shield drain
        if self.shield_active and self.is_fused:
            if zone_type:
                # Drain juice per hazard type (D-03)
                drain = HAZARD_DRAIN_RATES.get(zone_type, HAZARD_DRAIN_SLOW)
                if self.has_shield_t2:
                    drain = max(0, drain - SHIELD_T2_DRAIN_REDUCTION)
                if drain > 0:
                    slime.consume(drain)

                # Juice empty: unfuse + dissipate (D-04)
                if slime.juice <= 0:
                    self.unfuse(slime, dissipate=True)
                    self.shield_active = False
                    self.shield_cooldown = SHIELD_REACTIVATION_COOLDOWN
                    self.hazard_hp_timer = HAZARD_HP_DRAIN_INTERVAL
            else:
                # Left hazard zone: deactivate shield, unfuse normally
                self.shield_active = False
                self.shield_cooldown = SHIELD_REACTIVATION_COOLDOWN
                self.unfuse(slime)

        # HP drain when in hazard zone with no juice and no shield (D-04)
        if zone_type and not self.shield_active and not self.is_fused:
            if slime.juice <= 0 or slime.is_dissipated:
                if self.hazard_hp_timer > 0:
                    self.hazard_hp_timer -= 1
                else:
                    self.take_damage(1, slime=slime)
                    self.hazard_hp_timer = HAZARD_HP_DRAIN_INTERVAL

    def handle_input(self, slime):
        if self.knockback_timer > 0:
            return

        if self.state == "CHARGING_SHOT":
            return  # No input during windup

        # Directional Slime Hold (ABL-03, D-19): tap LEFT/RIGHT to reposition slime
        if not self.is_fused and not slime.is_dissipated:
            if input_manager.was_tap("left", HOLD_TAP_THRESHOLD):
                slime.reposition(-1, self.x, self.y, self.level_map)
            elif input_manager.was_tap("right", HOLD_TAP_THRESHOLD):
                slime.reposition(1, self.x, self.y, self.level_map)

        # Charge Shot: release Z while fused = enter windup then fire (D-06, D-16, gap fix)
        if self.is_fused and input_manager.btnr("spit") and self.state not in ("RAMMING", "CHARGING_SHOT"):
            self.state = "CHARGING_SHOT"
            self.charge_windup_timer = CHARGE_WINDUP_DURATION
            slime.is_being_absorbed = True
            return  # Lock input immediately on windup entry

        # Z button: tap = spit, hold = recall + charge toward fusion (D-06)
        if input_manager.was_tap("spit", SPIT_HOLD_THRESHOLD) and not self.is_fused and self.state != "DIVING" and self.state != "DASHING":
            # Tap Z = spit (fire on release for clean separation from hold-to-recall)
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
                    # Check if target is in current room (uses WorldManager bounds)
                    level = self.game.world.current_level
                    if level and not level.contains(target.x + target.w / 2,
                                                    target.y + target.h / 2):
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
        elif input_manager.btn("spit") and not self.is_fused and self.state != "DIVING" and self.state != "DASHING":
            # Z is held -- start/continue recall after threshold
            if input_manager.hold_frames("spit") >= SPIT_HOLD_THRESHOLD and not slime.is_dissipated:
                self.is_charging_recall = True
                slime.recall(self.x, self.y)

        # Each frame during recall, check if slime has arrived for auto-fuse (D-02)
        if self.is_charging_recall and slime.is_recalling:
            arrived = slime.update_recall(self.x, self.y)
            if arrived and slime.juice >= slime.max_juice:
                self.fuse(slime)

        # Cancel recall on Z release if was charging
        if input_manager.btnr("spit") and self.is_charging_recall:
            self.is_charging_recall = False
            slime.is_recalling = False
            slime.recall_trail.clear()

        # Dash / Ram activation (V button = horizontal only per D-12)
        if input_manager.btnp("dash") and self.state not in ("DIVING", "DASHING", "RAMMING"):
            if self.is_fused:
                # V while fused = Slime Ram (D-07, D-12)
                self.start_ram(slime)
            elif self.has_dash and self.dash_cooldown <= 0:
                # V while unfused = Basic Dash (D-15)
                if not self.is_grounded and self.dash_air_used:
                    pass  # Already used air dash
                else:
                    self.start_dash()

        # SPACE button: drill dive (DOWN+SPACE), boost (fused+air), or jump (D-12, D-13)
        # Drill dive check: must be airborne, holding down, has drill, has juice
        if input_manager.btnp("jump") and self.state not in ("DIVING", "DASHING", "RAMMING"):
            if (input_manager.btn("down") and self.has_drill
                    and not self.is_grounded and slime.juice > 0):
                # DOWN+SPACE = Drill Dive (D-12 remap from DOWN+V)
                dist_sq = (self.x - slime.x)**2 + (self.y - slime.y)**2
                if dist_sq < SLIME_MAX_DIST**2:
                    self.state = "DIVING"
                    self.fuse(slime)
                    self.dy = DRILL_SPEED
                    self.dx = 0
                    slime.consume(DRILL_ACTIVATION_COST)
                    return
            elif (self.is_fused and not self.is_grounded and self.has_boost
                    and self.state != "BOOSTING"):
                # SPACE while fused+airborne = Slime Boost (D-07)
                self.start_boost(slime)
                return  # Consume input, skip jump logic

        # Drill Dive Cancellation
        if self.state == "DIVING":
            if input_manager.btnp("jump"):
                self.state = "FALLING"
                self.unfuse(slime)
                self.dy = 0
            return

        # Horizontal Movement
        target_dx = 0
        move_input_x = 0
        if input_manager.btn("left"):
            target_dx -= WALK_ACCEL
            move_input_x = -1
            self.facing_right = False
        if input_manager.btn("right"):
            target_dx += WALK_ACCEL
            move_input_x = 1
            self.facing_right = True

        # Vertical Movement (for dash direction)
        move_input_y = 0
        if input_manager.btn("up"):
            move_input_y = -1
        if input_manager.btn("down"):
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

        # Jump (guard: not during boost to prevent post-boost ground jump -- Pitfall 3)
        if self.jump_buffer_timer > 0 and self.state != "BOOSTING":
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
        if input_manager.btnr("jump") and self.dy < 0:
            self.dy *= VARIABLE_JUMP_REDUCTION

    def start_boost(self, slime):
        """Activate Slime Boost -- fused SPACE in air (ABL-06, D-07).
        Each tap is a committed upward burst costing juice."""
        self.state = "BOOSTING"
        self.dy = BOOST_FORCE
        slime.consume(BOOST_JUICE_COST)
        self.boost_recommit_timer = BOOST_RECOMMIT_WINDOW
        self.jump_buffer_timer = 0  # Clear jump buffer (Pitfall 3)
        # Boost trail VFX (D-10): small downward trail particles
        if self.game:
            for _ in range(3):
                self.game.particles.append(Particle(self.x + 4, self.y + self.h, 11))  # Green
        # Check juice exhaustion (D-09)
        if slime.juice <= 0:
            self.end_boost(slime, dissipate=True)

    def update_boost(self, slime):
        """Update BOOSTING state: recommit window, chain taps, exit conditions (D-08, D-09)."""
        if self.state != "BOOSTING":
            return

        # Tick recommit timer
        self.boost_recommit_timer -= 1

        # Chain: SPACE tap during recommit window = another boost
        if input_manager.btnp("jump") and self.boost_recommit_timer > 0:
            self.dy = BOOST_FORCE
            slime.consume(BOOST_JUICE_COST)
            self.boost_recommit_timer = BOOST_RECOMMIT_WINDOW
            self.jump_buffer_timer = 0  # Clear buffer on each chain tap (Pitfall 3)
            # Boost chain trail VFX (D-10)
            if self.game:
                for _ in range(3):
                    self.game.particles.append(Particle(self.x + 4, self.y + self.h, 11))
            # Juice exhaustion check
            if slime.juice <= 0:
                self.end_boost(slime, dissipate=True)
                return

        # Exit: recommit window expired without tap
        if self.boost_recommit_timer <= 0:
            self.end_boost(slime, dissipate=False)

    def end_boost(self, slime, dissipate=False):
        """End Slime Boost (D-09). If dissipate=True, slime enters burnout."""
        self.state = "FALLING"
        self.jump_buffer_timer = 0  # Clear buffer on exit (Pitfall 3)
        self.boost_recommit_timer = 0
        if dissipate:
            self.unfuse(slime, dissipate=True)
        else:
            self.unfuse(slime)

    def start_dash(self):
        """Activate basic dash (D-15). Short combat dodge with i-frames."""
        self.state = "DASHING"
        self.dash_timer = DASH_DURATION
        self.dash_cooldown = DASH_COOLDOWN
        self.dash_dx = DASH_SPEED if self.facing_right else -DASH_SPEED
        if not self.is_grounded:
            self.dash_air_used = True
        # Grant i-frames
        self.invuln_timer = max(self.invuln_timer, DASH_IFRAMES)

    def fire_charge_shot(self, slime):
        """Fire charge shot -- slime IS the projectile (D-16, D-17, D-18).
        Dumps all remaining juice. Auto-unfuses."""
        from src.entities.projectile import ChargeProjectile
        # Direction based on facing
        dx = 1.0 if self.facing_right else -1.0
        dy = 0.0  # Flat trajectory for charge shot
        # Spawn at player center
        proj = ChargeProjectile(
            self.x + 2, self.y + 2,
            dx, dy,
            self.level_map, slime
        )
        if self.game:
            self.game.projectiles.append(proj)
            # Charge shot flash VFX (D-10): bright particles at fire point
            fire_x = self.x + (self.w if self.facing_right else -4)
            fire_y = self.y + self.h // 2
            for _ in range(4):
                self.game.particles.append(Particle(fire_x, fire_y, 10))  # Yellow
        # Dump all juice (D-16)
        slime.consume(slime.juice)
        # Charge shot recoil: upward impulse (D-17, bomb-climb exploit)
        self.dy = CHARGE_RECOIL_FORCE
        # Unfuse -- slime will be repositioned by ChargeProjectile on impact (D-17)
        self.is_fused = False  # Direct set: slime position handled by projectile
        slime.is_fused = False
        self.is_charging_recall = False

    def update_charge_shot(self, slime):
        """Tick CHARGING_SHOT windup. Slime absorbs into player, then fires (gap fix)."""
        if self.state != "CHARGING_SHOT":
            return
        self.charge_windup_timer -= 1
        # Lock movement during windup
        self.dx = 0
        if self.charge_windup_timer <= 0:
            slime.is_being_absorbed = False
            self.fire_charge_shot(slime)
            self.state = "FALLING" if not self.is_grounded else "IDLE"

    def apply_diving_physics(self, slime):
        self.dy = DRILL_SPEED
        # Horizontal drift
        if input_manager.btn("left"):
            self.dx = -DRILL_DRIFT_SPEED
        elif input_manager.btn("right"):
            self.dx = DRILL_DRIFT_SPEED
        else:
            self.dx = 0

        # Out of juice check
        if slime.juice <= 0:
            self.state = "FALLING"
            self.unfuse(slime, dissipate=True)

    def apply_dash_physics(self):
        """Dash movement: fixed horizontal speed, no gravity (D-15)."""
        self.dx = self.dash_dx
        self.dy = 0  # Freeze vertical during dash

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
            self.take_damage(1, slime=slime)
            if self.is_alive and self.game:
                self.x = self.game.room_spawn_x
                self.y = self.game.room_spawn_y
                self.dx = 0
                self.dy = 0
            return

        if self.level_map.check_collision(self.x, self.y, self.w, self.h):
            # Save movement direction BEFORE end_ram zeroes dx (gap fix: ram wall embed)
            move_direction = self.dx
            # RAMMING: check for CRACKED_H before stopping (D-13)
            if self.state == "RAMMING" and slime:
                tile_coord = self.level_map.get_cracked_h_at(self.x, self.y, self.w, self.h)
                if tile_coord:
                    tx, ty = tile_coord
                    if self.game:
                        self.game.on_block_destroyed(tx, ty, TILE_CRACKED_H)
                    self.level_map.remove_tile(tx, ty)
                    if self.game:
                        self.game.spawn_explosion(tx * TILE_SIZE, ty * TILE_SIZE, 9)
                    slime.consume(RAM_BLOCK_COST)
                    self.on_block_break()
                    # Check if juice ran out (D-14)
                    if slime.juice <= 0:
                        self.end_ram(slime)
                    return  # Continue through broken block
                else:
                    # Hit solid (non-CRACKED_H) wall -- stop ram (Pitfall 4)
                    # Ram wall impact VFX (D-10): 3-frame screen shake on solid wall hit
                    if self.game:
                        self.game.shake_timer = 3
                    self.end_ram(slime)
            # Snap to wall surface using saved direction (end_ram may have zeroed self.dx)
            if move_direction > 0:
                self.x = (int((self.x + self.w - 1) // TILE_SIZE)) * TILE_SIZE - self.w
            elif move_direction < 0:
                self.x = (int(self.x // TILE_SIZE) + 1) * TILE_SIZE
            self.dx = 0

        # Move vertical
        self.y += self.dy
        if self.level_map.check_hazard(self.x, self.y, self.w, self.h):
            self.take_damage(1, slime=slime)
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
                        tile_type = self.level_map.get_tile(tx, ty)
                        if self.game:
                            self.game.on_block_destroyed(tx, ty, tile_type)
                        self.level_map.remove_tile(tx, ty)
                        if self.game:
                            self.game.spawn_explosion(tx * TILE_SIZE, ty * TILE_SIZE, 9)
                        if tile_type == TILE_CRACKED_V:
                            slime.consume(DRILL_CRACKED_V_COST)  # Gate block costs juice (ABL-02)
                        else:
                            slime.refill(DRILL_BLOCK_REFUND)  # Soft block refunds juice
                        self.on_block_break()
                        return

                # Snap to floor
                target_row = int((self.y + self.h) // TILE_SIZE)
                self.y = target_row * TILE_SIZE - self.h
                self.is_grounded = True
                self.dash_air_used = False  # Reset air dash on landing

                # Impact consumption
                if self.state == "DIVING" and slime:
                    slime.consume(DRILL_IMPACT_COST)
                    self.state = "IDLE" # Landed
                    self.unfuse(slime)

                self.dy = 0
            elif self.dy < 0:
                # Check for CRACKED_V during Boost (ABL-02)
                if self.state == "BOOSTING" and slime:
                    cracked = self.level_map.get_cracked_v_at(self.x, self.y, self.w, self.h)
                    if cracked:
                        tx, ty = cracked
                        if self.game:
                            self.game.on_block_destroyed(tx, ty, TILE_CRACKED_V)
                        self.level_map.remove_tile(tx, ty)
                        if self.game:
                            self.game.spawn_explosion(tx * TILE_SIZE, ty * TILE_SIZE, 9)
                        slime.consume(BOOST_CRACKED_V_COST)
                        self.on_block_break()
                        if slime.juice <= 0:
                            self.end_boost(slime, dissipate=True)
                        return  # Continue through broken block
                # Snap to ceiling
                self.y = (int(self.y // TILE_SIZE) + 1) * TILE_SIZE
                self.dy = 0
        else:
            self.is_grounded = False

    def update_state(self):
        if self.state in ("DIVING", "DASHING", "RAMMING", "BOOSTING", "CHARGING_SHOT"):
            return  # State managed by physics/collision
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
        # Shield hit flash VFX (D-10)
        if self.shield_flash_timer > 0:
            pyxel.circb(self.x + self.w // 2, self.y + self.h // 2, 6, 12)  # Light blue
            self.shield_flash_timer -= 1
        self.draw_shield()

    def draw_shield(self):
        """Draw Bubble Shield VFX: circle outline with pulse/flicker (D-06)."""
        if not self.shield_active:
            return
        cx = self.x + self.w // 2
        cy = self.y + self.h // 2
        radius = 6  # Slightly larger than 8x8 sprite
        # Color per tier: blue=12 (T1), green=11 (T2) (D-06)
        color = 11 if self.has_shield_t2 else 12
        # Pulse: alternate radius by 1 pixel every 10 frames
        if (pyxel.frame_count // 10) % 2 == 0:
            radius += 1
        # Flicker: skip drawing for 2 frames every 40 frames
        if pyxel.frame_count % 40 < 2:
            return
        pyxel.circb(cx, cy, radius, color)
