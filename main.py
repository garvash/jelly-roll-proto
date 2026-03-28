import pyxel
from src.core.constants import SCREEN_W, SCREEN_H, VIEWPORT_W, VIEWPORT_H, HUD_H, CULL_MARGIN
from src.level.map import LevelMap
from src.entities.player import Player
from src.entities.slime import Slime
from src.entities.boss import Mole
from src.entities.enemies import Snail, Bat
from src.entities.items import Item
from src.entities.effects import Effect, Particle

class Game:
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, title="Jelly Roll Proto")
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
        
        # Initial room scan
        self.spawn_enemies()
        self.rooms_visited.add((0, 0))

    def spawn_enemies(self):
        # 1. Spawn from LDtk entity list (if current room matches)
        for ent in self.level_map.entities:
            # Check if entity is in current room
            if (self.cam_x <= ent["x"] < self.cam_x + VIEWPORT_W and
                self.cam_y <= ent["y"] < self.cam_y + VIEWPORT_H):

                etype = ent["type"]
                ex, ey = ent["x"], ent["y"]
                
                if etype == "Snail":
                    self.enemies.append(Snail(ex, ey))
                elif etype == "Bat":
                    self.enemies.append(Bat(ex, ey))
                # Note: BossMole handled by check_boss_trigger for safety margin
                elif etype == "Drill":
                    self.items.append(Item(ex, ey, "DRILL"))
                elif etype == "EnergyTank":
                    self.items.append(Item(ex, ey, "ENERGY"))
                elif etype == "MissileTank":
                    self.items.append(Item(ex, ey, "MISSILE"))

        # 2. Scan current room for enemy spawn tiles (Legacy fallback)
        tx_start, ty_start = int(self.cam_x // 8), int(self.cam_y // 8)
        tiles_w, tiles_h = VIEWPORT_W // 8, VIEWPORT_H // 8  # Room size in tiles
        for ty in range(ty_start, ty_start + tiles_h):
            for tx in range(tx_start, tx_start + tiles_w):
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

        # Check Entities
        for ent in self.level_map.entities:
            if (self.cam_x <= ent["x"] < self.cam_x + VIEWPORT_W and
                self.cam_y <= ent["y"] < self.cam_y + VIEWPORT_H):
                if ent["type"] == "BossMole":
                    self.mole = Mole(ent["x"], ent["y"], self.level_map)
                    self.level_map.close_gates(self.cam_x, self.cam_y)
                    self.boss_triggered = True
                    return

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
        # 1. Early Room Transition Check
        curr_cam_x = int((self.player.x // VIEWPORT_W) * VIEWPORT_W)
        curr_cam_y = int((self.player.y // VIEWPORT_H) * VIEWPORT_H)
        
        if curr_cam_x != self.cam_x or curr_cam_y != self.cam_y:
            # Sync camera immediately
            self.cam_x = curr_cam_x
            self.cam_y = curr_cam_y
            self.pending_boss_trigger = True
            
            # Handle room entry logic - IMMEDIATE for normal enemies
            self.room_spawn_x = self.player.x
            self.room_spawn_y = self.player.y
            if (self.cam_x, self.cam_y) not in self.rooms_visited:
                self.spawn_enemies()
                self.rooms_visited.add((self.cam_x, self.cam_y))

        # Handle delayed BOSS trigger (Safe Distance Check)
        if self.pending_boss_trigger:
            rel_x = self.player.x - self.cam_x
            rel_y = self.player.y - self.cam_y
            # Only trigger boss when player is safely inside (16px from edges)
            if 16 < rel_x < VIEWPORT_W - 16 and 16 < rel_y < VIEWPORT_H - 16:
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
            (self.slime.x < self.cam_x - 8 or self.slime.x > self.cam_x + VIEWPORT_W or
             self.slime.y < self.cam_y - 8 or self.slime.y > self.cam_y + VIEWPORT_H)):
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
        self.items = [it for it in self.items if it.is_active]

        if self.shake_timer > 0:
            self.shake_timer -= 1

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
