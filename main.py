import pyxel
from src.level.map import LevelMap
from src.level.world import WorldManager
from src.entities.player import Player
from src.entities.slime import Slime
from src.entities.boss import Mole
from src.entities.enemies import Snail, Bat
from src.entities.items import Item
from src.entities.effects import Effect, Particle
from src.entities.map_entities import Door

class Game:
    def __init__(self):
        # 16x16 tiles room size = 128x128 pixels
        pyxel.init(128, 128, title="Jelly Roll Proto")
        # Load assets
        pyxel.load("assets/game.pyxres")
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        # Reload assets to restore tilemap state (broken blocks, gates)
        pyxel.load("assets/game.pyxres")
        
        # Inject Explosion Sprites at (0, 48) in image 1 if not present
        # Frame 1
        for y in range(48, 56):
            for x in range(0, 8):
                dist = (x-3.5)**2 + (y-51.5)**2
                if dist < 4: pyxel.images[1].pset(x, y, 7)
                elif dist < 9: pyxel.images[1].pset(x, y, 10)
        # Frame 2
        for y in range(48, 56):
            for x in range(8, 16):
                dist = (x-11.5)**2 + (y-51.5)**2
                if dist < 9: pyxel.images[1].pset(x, y, 10)
                elif dist < 16: pyxel.images[1].pset(x, y, 9)
        # Frame 3
        for y in range(48, 56):
            for x in range(16, 24):
                dist = (x-19.5)**2 + (y-51.5)**2
                if dist < 16: pyxel.images[1].pset(x, y, 9)
                elif dist < 25: pyxel.images[1].pset(x, y, 4)

        self.level_map = LevelMap()
        # Load external map if exists
        self.level_map.load_from_tiled("assets/map.json")
        self.level_map.load_from_ldtk("assets/map.ldtk")
        # Priority: LDtk Super Simple Export
        success = self.level_map.load_from_ldtk_simplified("assets/cave/simplified")
        if success:
            print(f"Loaded LDtk map from simplified export. Entities: {len(self.level_map.entities)}")

        # Initialize WorldManager with level bounds from LDtk
        self.world = WorldManager(self.level_map.get_level_bounds_list())

        # Default start position
        spawn_x, spawn_y = 40, 40
        
        # 1. Spawn Player from LDtk entities
        player_ent = next((e for e in self.level_map.entities if e["type"] == "PlayerStart"), None)
        if player_ent:
            spawn_x, spawn_y = player_ent["x"], player_ent["y"]
        else:
            # Fallback to tile marker (1, 0)
            spawn_tile = self.level_map.find_tile(1, 0)
            if spawn_tile:
                tx, ty = spawn_tile
                spawn_x, spawn_y = tx * 8, ty * 8
                self.level_map.remove_tile(tx, ty)

        self.player = Player(spawn_x, spawn_y, self.level_map, self)
        self.slime = Slime(spawn_x, spawn_y)
        
        # Mole starts as None, will be spawned when room is entered
        self.mole = None
        self.enemies = []
        self.items = []
        self.projectiles = []
        self.stains = []
        self.effects = []
        self.particles = []
        self.doors = []
        self.game_state = "PLAYING" # PLAYING, WON
        self.death_timer = 0
        self.shake_timer = 0
        self.stop_frames = 0
        self.cam_x = 0
        self.cam_y = 0
        self.boss_triggered = False
        self.rooms_visited = set()
        # Track spawn for current room (for hazard respawn)
        self.room_spawn_x = spawn_x
        self.room_spawn_y = spawn_y
        self.pending_boss_trigger = True
        
        # Detect initial room and set camera
        player_cx = spawn_x + self.player.w / 2
        player_cy = spawn_y + self.player.h / 2
        initial_level = self.world.detect_level(player_cx, player_cy)
        self.cam_x, self.cam_y = self.world.get_camera_clamped(spawn_x, spawn_y)
        self.cam_x = int(self.cam_x)
        self.cam_y = int(self.cam_y)

        # Initial room scan
        self.spawn_enemies()
        initial_key = initial_level.id if initial_level else (self.cam_x, self.cam_y)
        self.rooms_visited.add(initial_key)

    def spawn_enemies(self):
        # 1. Spawn from LDtk entity list (if current room matches)
        # Use full room bounds (not just viewport) so entities in large rooms always spawn
        level = self.world.current_level
        if level:
            room_x, room_y = level.x, level.y
            room_w, room_h = level.w, level.h
        else:
            room_x, room_y = self.cam_x, self.cam_y
            room_w, room_h = 128, 128

        for ent in self.level_map.entities:
            if (room_x <= ent["x"] < room_x + room_w and
                room_y <= ent["y"] < room_y + room_h):
                
                etype = ent["type"]
                ex, ey = ent["x"], ent["y"]
                
                # Skip items that have already been collected
                ent_iid = ent.get("iid")
                if ent_iid and self.world.is_item_collected(ent_iid):
                    continue

                if etype == "Snail":
                    self.enemies.append(Snail(ex, ey, self))
                elif etype == "Bat":
                    self.enemies.append(Bat(ex, ey, self))
                # Note: BossMole handled by check_boss_trigger for safety margin
                elif etype == "Drill":
                    self.items.append(Item(ex, ey, "DRILL", iid=ent_iid))
                elif etype == "EnergyTank":
                    self.items.append(Item(ex, ey, "ENERGY", iid=ent_iid))
                elif etype == "MissileTank":
                    self.items.append(Item(ex, ey, "MISSILE", iid=ent_iid))
                elif etype == "Door":
                    target_id = ent.get("target_level_id")
                    direction = ent.get("direction", "right")
                    self.doors.append(Door(ex, ey, target_id, direction))

        # 2. Scan current room for enemy spawn tiles (Legacy fallback)
        tx_start, ty_start = int(room_x // 8), int(room_y // 8)
        tx_count = room_w // 8
        ty_count = room_h // 8
        for ty in range(ty_start, ty_start + ty_count):
            for tx in range(tx_start, tx_start + tx_count):
                tile = self.level_map.get_tile(tx, ty)
                if tile == (0, 2): # Snail Marker
                    self.enemies.append(Snail(tx * 8, ty * 8))
                    self.level_map.remove_tile(tx, ty)
                elif tile == (0, 3): # Bat Marker
                    self.enemies.append(Bat(tx * 8, ty * 8))
                    self.level_map.remove_tile(tx, ty)
                elif tile == (3, 0): # Drill Marker
                    self.items.append(Item(tx * 8, ty * 8, "DRILL"))
                    self.level_map.remove_tile(tx, ty)
                elif tile == (2, 2): # Energy Tank Marker
                    self.items.append(Item(tx * 8, ty * 8, "ENERGY"))
                    self.level_map.remove_tile(tx, ty)
                elif tile == (3, 2): # Missile Tank Marker
                    self.items.append(Item(tx * 8, ty * 8, "MISSILE"))
                    self.level_map.remove_tile(tx, ty)

    def check_boss_trigger(self):
        """Checks for BossMole entity in current room."""
        if self.mole or self.boss_triggered:
            return

        # Check Entities (use full room bounds for large rooms)
        level = self.world.current_level
        if level:
            rx, ry, rw, rh = level.x, level.y, level.w, level.h
        else:
            rx, ry, rw, rh = self.cam_x, self.cam_y, 128, 128

        for ent in self.level_map.entities:
            if (rx <= ent["x"] < rx + rw and
                ry <= ent["y"] < ry + rh):
                if ent["type"] == "BossMole":
                    self.mole = Mole(ent["x"], ent["y"], self.level_map)
                    self.level_map.close_gates(self.cam_x, self.cam_y)
                    self.boss_triggered = True
                    return

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # 0. Handle transition animation (freeze gameplay during slide)
        if self.world.is_transitioning():
            self.cam_x, self.cam_y = self.world.update_transition()
            if not self.world.is_transitioning():
                # Transition complete - finalize room entry
                self._on_room_enter()
            return

        # 1. Room Detection & Camera Clamping via WorldManager
        player_cx = self.player.x + self.player.w / 2
        player_cy = self.player.y + self.player.h / 2
        prev_level = self.world.current_level
        new_level = self.world.detect_level(player_cx, player_cy)

        # Camera clamping (works for both standard 128x128 and larger rooms)
        new_cam_x, new_cam_y = self.world.get_camera_clamped(self.player.x, self.player.y)
        new_cam_x = int(new_cam_x)
        new_cam_y = int(new_cam_y)

        # Detect room transition
        if new_level and new_level is not prev_level:
            # Nudge player first so transition targets the correct camera position
            self._nudge_player_into_level(new_level)
            # Trigger freeze-and-slide transition using nudged player position
            self.world.trigger_transition(new_level, self.cam_x, self.cam_y,
                                          self.player.x, self.player.y)
            return
        elif new_cam_x != self.cam_x or new_cam_y != self.cam_y:
            # Camera moved within a large room (scrolling)
            self.cam_x = new_cam_x
            self.cam_y = new_cam_y

        # Update block regeneration timers
        self.world.update_block_regen(self.level_map)

        # Handle delayed BOSS trigger (Safe Distance Check)
        if self.pending_boss_trigger:
            rel_x = self.player.x - self.cam_x
            rel_y = self.player.y - self.cam_y
            # Only trigger boss when player is safely inside (16px from edges)
            if 16 < rel_x < 112 and 16 < rel_y < 112:
                self.check_boss_trigger()
                self.pending_boss_trigger = False

        # 2. Always update effects/particles
        for eff in self.effects:
            eff.update()
        self.effects = [eff for eff in self.effects if eff.is_active]

        for part in self.particles:
            part.update()
        self.particles = [part for part in self.particles if part.is_active]

        # 3. WON State handling
        if self.game_state == "WON":
            if pyxel.btnp(pyxel.KEY_R):
                self.reset()
            return

        # 4. Hit-stop logic
        if self.stop_frames > 0:
            self.stop_frames -= 1
            return

        # 5. Death handling
        if not self.player.is_alive:
            self.death_timer += 1
            if self.death_timer >= 15:
                self.reset()
            return

        # 6. Main Logic Update
        self.player.update(self.slime)
        self.slime.update(self.player.x, self.player.y, self.player.facing_right, self.level_map, self.player.is_fused)

        # Off-screen slime recovery
        if (not self.player.is_fused and 
            (self.slime.x < self.cam_x - 8 or self.slime.x > self.cam_x + 128 or
             self.slime.y < self.cam_y - 8 or self.slime.y > self.cam_y + 128)):
            self.slime.reform(self.player.x, self.player.y, self.player.facing_right, self.level_map)

        # Update enemies & Combat
        for e in self.enemies:
            e.update(self.player, self.level_map)
            if not e.is_alive: continue
            
            for p in self.projectiles:
                if p.is_active and e.check_collision(p.x, p.y, p.w, p.h):
                    e.take_damage()
                    self.spawn_explosion(e.x, e.y, 10)
                    p.is_active = False
            
            if self.player.state == "DIVING" and e.check_collision(self.player.x, self.player.y, self.player.w, self.player.h):
                e.take_damage()
                self.spawn_explosion(e.x, e.y, 10)
                self.slime.refill(10)
                self.player.on_block_break()
            
            if self.slime.is_punted and e.check_collision(self.slime.x, self.slime.y, self.slime.w, self.slime.h):
                e.take_damage()
                self.spawn_explosion(e.x, e.y, 10)
                self.slime.dx *= -0.5
                self.slime.dy = -2.0

        self.enemies = [e for e in self.enemies if e.is_alive]

        if self.mole:
            self.mole.update(self.projectiles, self.player, self.cam_x, self.cam_y)
            if not self.mole.is_alive:
                self.level_map.open_gates(self.cam_x, self.cam_y)
                self.game_state = "WON"

        # Update secondary entities
        for p in self.projectiles:
            stain = p.update(self.cam_x, self.cam_y)
            if stain:
                self.stains.append(stain)
        self.projectiles = [p for p in self.projectiles if p.is_active]

        for s in self.stains:
            s.update()
        self.stains = [s for s in self.stains if s.is_active]

        for it in self.items:
            it.update()
            if it.is_active and (self.player.x < it.x + it.w and self.player.x + self.player.w > it.x and
                                 self.player.y < it.y + it.h and self.player.y + self.player.h > it.y):
                it.collect(self.player, self.slime)
                # Mark item as permanently collected via WorldManager
                if it.iid:
                    self.world.collect_item(it.iid)
        self.items = [it for it in self.items if it.is_active]

        # Update doors: check kick, projectile hits, and player entry
        for door in self.doors:
            door.update()

            # Kick opens door
            if not door.is_open and self.player.kick_timer > 0:
                kx = self.player.x + (8 if self.player.facing_right else -8)
                ky = self.player.y
                if door.check_kick_hit(kx, ky):
                    door.open()

            # Projectile opens door
            if not door.is_open:
                for p in self.projectiles:
                    if p.is_active and door.check_projectile_hit(p.x, p.y, p.w, p.h):
                        door.open()
                        p.is_active = False
                        break

            # Open door + player collision = transition
            if door.is_open and door.check_collision(
                    self.player.x, self.player.y, self.player.w, self.player.h):
                target = self._find_level_by_id(door.target_level_id)
                if target:
                    self._nudge_player_into_level(target)
                    self.world.trigger_transition(target, self.cam_x, self.cam_y,
                                                  self.player.x, self.player.y)
                    return

        if self.shake_timer > 0:
            self.shake_timer -= 1

    def _find_level_by_id(self, level_id):
        """Find a LevelBounds by its identifier string."""
        if level_id is None:
            return None
        for level in self.world.levels:
            if level.id == level_id:
                return level
        return None

    def _on_room_enter(self):
        """Handle room entry after transition completes."""
        level = self.world.current_level
        self.pending_boss_trigger = True
        self.room_spawn_x = self.player.x
        self.room_spawn_y = self.player.y

        # Reset broken blocks on room entry (prevent soft-locks)
        self.world.reset_blocks_for_room(self.level_map)

        # Clear transient entities from previous room
        self.enemies = []
        self.projectiles = []
        self.stains = []
        self.doors = []

        level_key = level.id if level else (self.cam_x, self.cam_y)
        if level_key not in self.rooms_visited:
            self.spawn_enemies()
            self.rooms_visited.add(level_key)

    def _nudge_player_into_level(self, target_level):
        """Reposition the player slightly into the target level to prevent re-triggering."""
        nudge = 4  # pixels
        px = self.player.x + self.player.w / 2
        py = self.player.y + self.player.h / 2

        # Nudge horizontally or vertically based on which edge was crossed
        if px < target_level.x:
            self.player.x = target_level.x + nudge
        elif px >= target_level.x + target_level.w:
            self.player.x = target_level.x + target_level.w - self.player.w - nudge
        if py < target_level.y:
            self.player.y = target_level.y + nudge
        elif py >= target_level.y + target_level.h:
            self.player.y = target_level.y + target_level.h - self.player.h - nudge

    def on_block_destroyed(self, tx, ty, tile_data):
        """Called when a destructible block is broken. Registers for regen."""
        self.world.break_block(tx, ty, tile_data)

    def spawn_explosion(self, x, y, color):
        self.effects.append(Effect(x, y))
        for _ in range(8):
            self.particles.append(Particle(x + 4, y + 4, color))

    def draw(self):
        pyxel.cls(0)
        
        # Screen shake + Camera follow
        offset_x = self.cam_x
        offset_y = self.cam_y
        if self.shake_timer > 0:
            offset_x += pyxel.rndi(-2, 2)
            offset_y += pyxel.rndi(-2, 2)
        
        pyxel.camera(offset_x, offset_y)

        # Draw tilemap from world origin
        pyxel.bltm(0, 0, 0, 0, 0, 2048, 2048)
        
        if self.mole:
            self.mole.draw()
        
        for e in self.enemies:
            e.draw()
            
        for s in self.stains:
            s.draw()
            
        for it in self.items:
            it.draw()
            
        for p in self.particles:
            p.draw(self.cam_x, self.cam_y)
            
        for eff in self.effects:
            eff.draw(self.cam_x, self.cam_y)
            
        self.slime.draw()
        for p in self.projectiles:
            p.draw()
        self.player.draw()

        # Draw Health UI
        for i in range(self.player.max_hp):
            color = 8 if i < self.player.hp else 5
            pyxel.rect(self.cam_x + 4 + i * 10, self.cam_y + 4, 8, 8, 0)
            pyxel.rectb(self.cam_x + 4 + i * 10, self.cam_y + 4, 8, 8, 7)
            if i < self.player.hp:
                pyxel.rect(self.cam_x + 6 + i * 10, self.cam_y + 6, 4, 4, 8)
            else:
                pyxel.rect(self.cam_x + 7 + i * 10, self.cam_y + 7, 2, 2, 5)

        if self.game_state == "WON":
            pyxel.rect(self.cam_x + 14, self.cam_y + 49, 100, 30, 0)
            pyxel.rectb(self.cam_x + 14, self.cam_y + 49, 100, 30, 7)
            pyxel.text(self.cam_x + 44, self.cam_y + 59, "VICTORY!", pyxel.frame_count % 16)
            pyxel.text(self.cam_x + 29, self.cam_y + 69, "PRESS R TO RESTART", 7)

if __name__ == "__main__":
    Game()
