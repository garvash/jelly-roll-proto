import pyxel
from src.core import tuning
from src.core.sprite_utils import draw_sprite
import src.core.input as input_manager
import src.core.debug as debug
from src.anim import event_bus
from src.anim.player_anim import PlayerAnimDriver, build_player_fsm

# IntGrid values for cracked blocks (from entity-schema.json)
INTGRID_CRACKED_V = 12  # Vertical cracked block

class Player:
    def __init__(self, x, y, level_map, game=None):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.w = 10
        self.h = 14
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
        # Tracks btnr("jump") during an armed buffer so variable-jump reduction
        # applies when the buffered jump executes on landing (M-A04).
        self.jump_released_during_buffer = False
        self.is_wall_sliding = False
        self.wall_dir = 0 # -1 for left wall, 1 for right wall

        # Fusion
        self.is_fused = False

        # Health & Combat
        self.hp = tuning.PLAYER_MAX_HP
        self.max_hp = tuning.PLAYER_MAX_HP
        self.invuln_timer = 0
        self.knockback_timer = 0
        # Upgrades
        self.has_drill = False # Must find item to use Drill Dive

        # Fusion system (D-01 through D-05)
        self.is_charging_recall = False  # True when holding Z unfused (charging toward fusion)

        # Phase 26 ANIM-03: animation FSM (see src/anim/player_anim.py).
        # Phase 31 ANIM-04: 'land' and 'jump_start' subscribers are wired
        # in Game.__init__ (main.py) so they survive Game.reset() without
        # accumulating leaked closures across restarts (Pitfall 5).
        self._anim_driver = PlayerAnimDriver()
        self._anim = build_player_fsm()

    def fuse(self, slime):
        """Enter fused state. ALWAYS use this instead of setting is_fused directly (Pitfall 3)."""
        self.is_fused = True
        slime.is_fused = True
        slime.is_recalling = False
        # Hold-state reset removed in Plan 31.5-05 (Rule 1 auto-fix): Hold mode
        # was stripped from Slime in Plan 02 per CONTEXT D-06; the attribute
        # no longer exists so the reset would be a stale reference. The
        # surviving recall/dissipate state machine handles fuse-during-recall
        # via the is_recalling reset above.
        self.is_charging_recall = False
        # ANIM-02 emit; may move in Phase 32 per FUSION-DESIGN lock
        event_bus.emit("fuse_start")

    def unfuse(self, slime, dissipate=False):
        """Exit fused state. ALWAYS use this instead of setting is_fused directly (Pitfall 3).
        If dissipate=True, slime enters burnout cooldown (D-05)."""
        self.is_fused = False
        slime.is_fused = False
        # ANIM-02 emit; may move in Phase 32 per FUSION-DESIGN lock
        event_bus.emit("fuse_end")
        if dissipate:
            slime.dissipate()
        else:
            # Slime reforms near player
            slime.reform(self.x, self.y, self.facing_right, self.level_map)

    def update(self, slime):
        if not self.is_alive:
            return

        # God-mode ability override (D-10)
        if debug.god_abilities:
            self.has_drill = True

        input_manager.update()  # Must run before any input checks
        self.update_timers()
        self.handle_input(slime)
        if self.state == "DIVING":
            self.apply_diving_physics(slime)
            self.move_and_collide(slime)
        else:
            self.apply_physics()
            self.move_and_collide(slime)
        self.update_state()
        self._update_anim_driver()   # D-14: last call of update()

    def take_damage(self, amount, source_x=None, slime=None):
        if self.invuln_timer > 0 or not self.is_alive:
            return False

        # Mana shield: fused damage consumes juice, not HP (D-04)
        if self.is_fused and slime and slime.juice > 0:
            slime.consume(tuning.MANA_SHIELD_COST)
            self.invuln_timer = tuning.INVULN_DURATION
            # Check for juice-empty dissipation (D-05)
            if slime.juice <= 0:
                self.unfuse(slime, dissipate=True)
            # Apply knockback but no HP loss
            if source_x is not None:
                kx = -tuning.KNOCKBACK_FORCE_X if self.x < source_x else tuning.KNOCKBACK_FORCE_X
                self.dx = kx
                self.dy = tuning.KNOCKBACK_FORCE_Y
                self.knockback_timer = 10
                self.is_grounded = False
            return True

        self.hp -= amount
        event_bus.emit("damaged")
        self.invuln_timer = tuning.INVULN_DURATION

        # Reset dive states via unfuse if fused (Pitfall 3)
        if self.is_fused and slime:
            self.unfuse(slime)
        else:
            self.is_fused = False

        # Apply knockback
        if source_x is not None:
            kx = -tuning.KNOCKBACK_FORCE_X if self.x < source_x else tuning.KNOCKBACK_FORCE_X
            self.dx = kx
            self.dy = tuning.KNOCKBACK_FORCE_Y
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
            event_bus.emit("death")

    def on_block_break(self):
        # Trigger juice effects
        if self.game:
            self.game.shake_timer = tuning.DRILL_SHAKE_DURATION
            self.game.stop_frames = tuning.DRILL_HITSTOP_FRAMES

    def update_timers(self):
        if self.is_grounded:
            self.coyote_timer = tuning.COYOTE_TIME
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1

        # Capture release that happens while a buffer is armed; variable-jump
        # reduction applies at buffered-jump execution if this flag is set.
        if self.jump_buffer_timer > 0 and input_manager.btnr("jump"):
            self.jump_released_during_buffer = True

        if input_manager.btnp("jump"):
            self.jump_buffer_timer = tuning.JUMP_BUFFER
            self.jump_released_during_buffer = False  # fresh buffer window
            # Only treat as a pre-land buffer if we're genuinely airborne
            # with no coyote window (otherwise this is a grounded or coyote jump).
            if not self.is_grounded and self.coyote_timer <= 0:
                event_bus.emit("jump_press_airborne")
        elif self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1

        if self.invuln_timer > 0:
            self.invuln_timer -= 1

        if self.knockback_timer > 0:
            self.knockback_timer -= 1

    def handle_input(self, slime):
        if self.knockback_timer > 0:
            return

        # Z button: tap = spit, hold = recall + charge toward fusion (D-06)
        if input_manager.was_tap("spit", tuning.SPIT_HOLD_THRESHOLD) and not self.is_fused and self.state != "DIVING":
            import math
            # Directional aim: use held direction to bias spit angle
            aim_x = 1 if self.facing_right else -1
            aim_y = 0
            if input_manager.btn("up"):
                aim_y = -1
            elif input_manager.btn("down"):
                aim_y = 1

            if aim_y == 0:
                # No vertical input: default forward lob
                target_dx = aim_x
                target_dy = -0.5
            elif aim_x != 0 and aim_y != 0:
                # Diagonal: normalize
                target_dx = aim_x * 0.707
                target_dy = aim_y * 0.707
            else:
                target_dx = aim_x
                target_dy = aim_y

            # Auto-aim: compute ballistic launch angle to arc onto target
            if self.game:
                min_dist = tuning.SPIT_AIM_RANGE
                best_enemy = None

                all_potential_targets = []
                if self.game.mole and self.game.mole.is_alive:
                    all_potential_targets.append(self.game.mole)
                all_potential_targets.extend([e for e in self.game.enemies if e.is_alive])

                for target in all_potential_targets:
                    level = self.game.world.current_level
                    if level and not level.contains(target.x + target.w / 2,
                                                    target.y + target.h / 2):
                        continue

                    in_direction = (target.x > self.x) if self.facing_right else (target.x < self.x)
                    if not in_direction:
                        continue

                    dx = (target.x + target.w/2) - (slime.x + slime.w/2)
                    dy = (target.y + target.h/2) - (slime.y + slime.h/2)
                    dist = math.sqrt(dx*dx + dy*dy)

                    if dist >= min_dist:
                        continue

                    min_dist = dist
                    best_enemy = target

                if best_enemy:
                    # Collision course: aim at target with gravity compensation.
                    # Calculate how much the bullet drops during flight, aim that
                    # much higher so the arc passes through the enemy.
                    dx = (best_enemy.x + best_enemy.w/2) - (slime.x + slime.w/2)
                    dy = (best_enemy.y + best_enemy.h/2) - (slime.y + slime.h/2)
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        t = dist / tuning.PROJECTILE_SPEED  # Frames to reach target
                        gravity_drop = 0.5 * 0.0375 * t * t  # Matches Projectile.gravity
                        aim_dy = dy - gravity_drop  # Aim above to compensate
                        aim_dist = math.sqrt(dx*dx + aim_dy*aim_dy)
                        target_dx = dx / aim_dist
                        target_dy = aim_dy / aim_dist

            proj = slime.spit(target_dx, target_dy, self.level_map)
            if proj and self.game:
                self.game.projectiles.append(proj)
        elif input_manager.btn("spit") and not self.is_fused and self.state != "DIVING":
            # Z is held -- start/continue recall after threshold
            if input_manager.hold_frames("spit") >= tuning.SPIT_HOLD_THRESHOLD and not slime.is_dissipated:
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

        # SPACE button: drill dive (DOWN+SPACE) or jump (D-12, D-13)
        # Drill dive check: must be airborne, holding down, has drill, has juice
        if input_manager.btnp("jump") and self.state != "DIVING":
            if (input_manager.btn("down") and self.has_drill
                    and not self.is_grounded and slime.juice > 0):
                # DOWN+SPACE = Drill Dive (D-12 remap from DOWN+V)
                dist_sq = (self.x - slime.x)**2 + (self.y - slime.y)**2
                if dist_sq < tuning.SLIME_MAX_DIST**2:
                    self.state = "DIVING"
                    self.fuse(slime)
                    self.dy = tuning.DRILL_SPEED
                    self.dx = 0
                    slime.consume(tuning.DRILL_ACTIVATION_COST)
                    return

        # Drill Dive Cancellation
        if self.state == "DIVING":
            if input_manager.btnp("jump"):
                self.state = "FALLING"
                self.unfuse(slime)
                self.dy = 0
            return

        # Horizontal Movement
        prev_facing = self.facing_right  # Phase 26 ANIM-02 prev-state snapshot (Pitfall 3)
        target_dx = 0
        move_input_x = 0
        if input_manager.btn("left"):
            target_dx -= tuning.WALK_ACCEL
            move_input_x = -1
            self.facing_right = False
        if input_manager.btn("right"):
            target_dx += tuning.WALK_ACCEL
            move_input_x = 1
            self.facing_right = True
        if self.facing_right != prev_facing:
            event_bus.emit("direction_change")

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
                self.dx = max(0, self.dx - tuning.WALK_FRICTION)
            elif self.dx < 0:
                self.dx = min(0, self.dx + tuning.WALK_FRICTION)

        # Clamp horizontal speed
        self.dx = max(-tuning.MAX_WALK_SPEED, min(self.dx, tuning.MAX_WALK_SPEED))

        # Check for walls
        on_left_wall = self.level_map.check_collision(self.x - 1, self.y, 1, self.h)
        on_right_wall = self.level_map.check_collision(self.x + self.w, self.y, 1, self.h)

        prev_wall_sliding = self.is_wall_sliding  # Phase 26 ANIM-02 prev-state snapshot
        self.is_wall_sliding = False
        self.wall_dir = 0
        if not self.is_grounded and self.dy > 0:
            if on_left_wall and move_input_x == -1:
                self.is_wall_sliding = True
                self.wall_dir = -1
            elif on_right_wall and move_input_x == 1:
                self.is_wall_sliding = True
                self.wall_dir = 1
        if self.is_wall_sliding and not prev_wall_sliding:
            event_bus.emit("wall_touch")

        # Jump
        if self.jump_buffer_timer > 0:
            if self.coyote_timer > 0:
                self.dy = tuning.JUMP_FORCE
                # If the button was released during the buffer window, apply
                # variable-jump reduction on execution (M-A04: buffered jumps
                # must honor pre-land release, not just mid-ascent btnr).
                if self.jump_released_during_buffer:
                    self.dy *= tuning.VARIABLE_JUMP_REDUCTION
                self.is_grounded = False
                self.coyote_timer = 0
                self.jump_buffer_timer = 0
                self.jump_released_during_buffer = False
                event_bus.emit("jump_start")
            elif self.is_wall_sliding or (on_left_wall and not self.is_grounded) or (on_right_wall and not self.is_grounded):
                # Wall Jump
                jump_dir = -1 if (on_right_wall) else 1
                self.dx = jump_dir * tuning.WALL_JUMP_X_IMPULSE
                self.dy = tuning.WALL_JUMP_Y_FORCE
                self.jump_buffer_timer = 0
                self.is_wall_sliding = False
                event_bus.emit("wall_jump")

        # Variable Jump Height (cut velocity on release)
        if input_manager.btnr("jump") and self.dy < 0:
            self.dy *= tuning.VARIABLE_JUMP_REDUCTION
            event_bus.emit("jump_released")

    def apply_diving_physics(self, slime):
        self.dy = tuning.DRILL_SPEED
        # Horizontal drift
        if input_manager.btn("left"):
            self.dx = -tuning.DRILL_DRIFT_SPEED
        elif input_manager.btn("right"):
            self.dx = tuning.DRILL_DRIFT_SPEED
        else:
            self.dx = 0

        # Out of juice check
        if slime.juice <= 0:
            self.state = "FALLING"
            self.unfuse(slime, dissipate=True)

    def apply_physics(self):
        prev_dy = self.dy  # Phase 26 ANIM-02 prev-state snapshot (Pitfall 4)
        # Weighted Gravity (increased gravity when falling)
        if self.is_wall_sliding:
            # Wall slide friction (reduced gravity)
            curr_gravity = tuning.GRAVITY
            self.dy = min(self.dy + curr_gravity * tuning.WALL_SLIDE_FRICTION, tuning.MAX_FALL_SPEED * 0.5)
        elif not self.is_grounded or self.state == "DIVING":
            curr_gravity = tuning.GRAVITY
            if self.dy > 0:
                curr_gravity *= tuning.FALLING_GRAVITY_MULTIPLIER
            self.dy += curr_gravity
            if self.dy > tuning.MAX_FALL_SPEED:
                self.dy = tuning.MAX_FALL_SPEED
        else:
            self.dy = 0
        if prev_dy <= 0 and self.dy > 0 and not self.is_grounded:
            event_bus.emit("fall_start")

    def move_and_collide(self, slime=None):
        was_grounded = self.is_grounded  # Phase 26 ANIM-02 prev-state snapshot (Pitfall 5)
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
            # Snap to wall surface
            if self.dx > 0:
                self.x = (int((self.x + self.w - 1) // tuning.TILE_SIZE)) * tuning.TILE_SIZE - self.w
            elif self.dx < 0:
                self.x = (int(self.x // tuning.TILE_SIZE) + 1) * tuning.TILE_SIZE
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
                            self.game.spawn_explosion(tx * tuning.TILE_SIZE, ty * tuning.TILE_SIZE, 9)
                        if tile_type == INTGRID_CRACKED_V:
                            slime.consume(tuning.DRILL_CRACKED_V_COST)  # Gate block costs juice (ABL-02)
                        else:
                            slime.refill(tuning.DRILL_BLOCK_REFUND)  # Soft block refunds juice
                        self.on_block_break()
                        return

                # Snap to floor
                target_row = int((self.y + self.h) // tuning.TILE_SIZE)
                self.y = target_row * tuning.TILE_SIZE - self.h
                self.is_grounded = True
                if not was_grounded:
                    event_bus.emit("land")

                # Impact consumption
                if self.state == "DIVING" and slime:
                    slime.consume(tuning.DRILL_IMPACT_COST)
                    # ANIM-02 emit; may move in Phase 32 per FUSION-DESIGN lock
                    event_bus.emit("drill_impact")
                    self.state = "IDLE" # Landed
                    self.unfuse(slime)

                self.dy = 0
            elif self.dy < 0:
                # Snap to ceiling
                self.y = (int(self.y // tuning.TILE_SIZE) + 1) * tuning.TILE_SIZE
                self.dy = 0
        else:
            self.is_grounded = False
            # Ground→air edge (walk-off-ledge). Jumps set is_grounded=False in
            # jump(), so was_grounded is already False by the time we land here
            # on the next frame — emits correctly fire only for true ground-leave.
            if was_grounded:
                event_bus.emit("left_ground")

    def update_state(self):
        if self.state == "DIVING":
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

    def _update_anim_driver(self):
        """Phase 26 D-14 + Phase 31 ANIM-04: refresh driver from end-of-frame state.

        Phase 31 extensions:
        - prev_facing snapshotted BEFORE facing overwrite (Pitfall 1)
        - vx_sign computed from self.dx (D-01 Metroid jump split)
        - skid_ticks armed on facing edge while grounded (D-03)
        - All three transient counters decrement every frame (Pitfall 2)
        Mutates the existing driver in place (D-16 zero-allocation).
        """
        from src.anim.player_anim import TURN_SKID_FRAMES
        d = self._anim_driver
        d.state = self.state
        d.is_grounded = self.is_grounded
        # Pitfall 1: snapshot BEFORE overwriting facing
        d.prev_facing = d.facing
        d.facing = 1 if self.facing_right else -1
        d.vy_sign = -1 if self.dy < 0 else (1 if self.dy > 0 else 0)
        d.vx_sign = -1 if self.dx < 0 else (1 if self.dx > 0 else 0)
        # D-03 edge detection: facing flipped while grounded -> arm skid counter
        if d.facing != d.prev_facing and d.is_grounded:
            d.skid_ticks = TURN_SKID_FRAMES
        # Pitfall 2: every transient counter decrements every frame so
        # rules cannot lock on indefinitely.
        if d.skid_ticks > 0:   d.skid_ticks -= 1
        if d.land_ticks > 0:   d.land_ticks -= 1
        if d.crouch_ticks > 0: d.crouch_ticks -= 1

    def draw(self):
        if not self.is_alive:
            # Flashing death effect
            if pyxel.frame_count % 8 < 4:
                # Draw player as a red block or flash
                pyxel.rect(self.x, self.y, self.w, self.h, 8) # 8 is red in default palette
            return

        # Phase 26 ANIM-03: sprite u offset comes from the AnimFSM,
        # driven by self._anim_driver (refreshed at end of update()).
        u = self._anim.current_frame_u(self._anim_driver)

        # Draw player sprite from image bank 1 with bottom-center anchoring
        draw_sprite(self.x, self.y, self.w, self.h, 1, u, 0,
                    tuning.SPRITE_SIZE, tuning.SPRITE_SIZE, self.facing_right)
