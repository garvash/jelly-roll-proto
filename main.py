import pyxel
from src.level.map import LevelMap
from src.entities.player import Player
from src.entities.slime import Slime
from src.entities.boss import Mole
from src.entities.enemies import Snail, Bat
from src.entities.items import Item
from src.entities.effects import Effect, Particle

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
        
        # Default start position
        spawn_x, spawn_y = 40, 40
        
        # Try to find player spawn tile (1, 0)
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

    def spawn_enemies(self):
        # Scan current room for enemy spawn tiles
        tx_start, ty_start = int(self.cam_x // 8), int(self.cam_y // 8)
        for ty in range(ty_start, ty_start + 16):
            for tx in range(tx_start, tx_start + 16):
                tile = self.level_map.get_tile(tx, ty)
                if tile == (0, 2): # Snail Marker (Pixel 0, 16)
                    self.enemies.append(Snail(tx * 8, ty * 8))
                    self.level_map.remove_tile(tx, ty)
                elif tile == (0, 3): # Bat Marker (Pixel 0, 24)
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

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
        # 1. Early Room Transition Check
        # Compare player's CURRENT room position with the camera's LAST position
        curr_cam_x = (self.player.x // 128) * 128
        curr_cam_y = (self.player.y // 128) * 128
        
        if curr_cam_x != self.cam_x or curr_cam_y != self.cam_y:
            # Wipe everything from the previous room immediately
            self.projectiles = []
            self.stains = []
            self.effects = []
            self.particles = []
            
            # Sync camera
            self.cam_x = curr_cam_x
            self.cam_y = curr_cam_y
            
            # Handle room entry logic
            self.room_spawn_x = self.player.x
            self.room_spawn_y = self.player.y
            if (self.cam_x, self.cam_y) not in self.rooms_visited:
                self.spawn_enemies()
                self.rooms_visited.add((self.cam_x, self.cam_y))

        # 2. Always update effects/particles (Independent of hit-stop or WON state)
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

        # Dynamic Boss Spawning
        if not self.mole and not self.boss_triggered:
            tx_start, ty_start = int(self.cam_x // 8), int(self.cam_y // 8)
            boss_tile = self.level_map.find_tile(4, 0, tx_start + 16, ty_start + 16)
            if boss_tile:
                bx, by = boss_tile
                if tx_start <= bx < tx_start + 16 and ty_start <= by < ty_start + 16:
                    self.mole = Mole(bx * 8, by * 8, self.level_map)
                    for ty in range(by, by + 2):
                        for tx in range(bx, bx + 2):
                            self.level_map.remove_tile(tx, ty)
                    self.level_map.close_gates(self.cam_x, self.cam_y)
                    self.boss_triggered = True

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

        # Draw tilemap
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

        # Draw Health UI (top left of current room)
        for i in range(self.player.max_hp):
            color = 8 if i < self.player.hp else 5 # 8=Red, 5=Dark Grey
            pyxel.rect(self.cam_x + 4 + i * 10, self.cam_y + 4, 8, 8, 0)
            pyxel.rectb(self.cam_x + 4 + i * 10, self.cam_y + 4, 8, 8, 7)
            # Simple heart shape inside
            if i < self.player.hp:
                pyxel.rect(self.cam_x + 6 + i * 10, self.cam_y + 6, 4, 4, 8)
            else:
                pyxel.rect(self.cam_x + 7 + i * 10, self.cam_y + 7, 2, 2, 5)

        if self.game_state == "WON":
            # Draw UI relative to camera (centered in 128x128)
            pyxel.rect(self.cam_x + 14, self.cam_y + 49, 100, 30, 0)
            pyxel.rectb(self.cam_x + 14, self.cam_y + 49, 100, 30, 7)
            pyxel.text(self.cam_x + 44, self.cam_y + 59, "VICTORY!", pyxel.frame_count % 16)
            pyxel.text(self.cam_x + 29, self.cam_y + 69, "PRESS R TO RESTART", 7)

if __name__ == "__main__":
    Game()
