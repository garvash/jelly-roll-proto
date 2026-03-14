import pyxel
from src.level.map import LevelMap
from src.entities.player import Player
from src.entities.slime import Slime
from src.entities.boss import Mole
from src.entities.enemies import Snail, Bat

class Game:
    def __init__(self):
        # 16x16 tiles room size = 128x128 pixels
        pyxel.init(128, 128, title="Slime Drill Proto")
        # Load assets
        pyxel.load("assets/game.pyxres")
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        # Reload assets to restore tilemap state (broken blocks, gates)
        pyxel.load("assets/game.pyxres")
        
        self.level_map = LevelMap()
        # Load external map if exists
        self.level_map.load_from_tiled("assets/map.json")
        
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
        self.projectiles = []
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

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
        if self.game_state == "WON":
            if pyxel.btnp(pyxel.KEY_R):
                self.reset()
            return

        # Hit-stop logic: freeze logic but allow drawing
        if self.stop_frames > 0:
            self.stop_frames -= 1
            return

        if not self.player.is_alive:
            self.death_timer += 1
            if self.death_timer >= 15:
                # Full reset to restore destroyed blocks, gates, and boss
                self.reset()
            return

        self.player.update(self.slime)
        self.slime.update(self.player.x, self.player.y, self.player.facing_right, self.player.is_fused)

        # Update Camera FIRST so projectiles can use it
        old_cam_x, old_cam_y = self.cam_x, self.cam_y
        self.cam_x = (self.player.x // 128) * 128
        self.cam_y = (self.player.y // 128) * 128
        
        # If camera changed, update room spawn point to player's current position (entry point)
        if self.cam_x != old_cam_x or self.cam_y != old_cam_y or (self.cam_x, self.cam_y) not in self.rooms_visited:
            self.room_spawn_x = self.player.x
            self.room_spawn_y = self.player.y
            if (self.cam_x, self.cam_y) not in self.rooms_visited:
                self.spawn_enemies()
                self.rooms_visited.add((self.cam_x, self.cam_y))

        # Dynamic Boss Spawning
        if not self.mole and not self.boss_triggered:
            # Scan only the current 16x16 tile room
            tx_start, ty_start = int(self.cam_x // 8), int(self.cam_y // 8)
            boss_tile = self.level_map.find_tile(4, 0, tx_start + 16, ty_start + 16)
            if boss_tile:
                bx, by = boss_tile
                # Ensure it's in the current room range
                if tx_start <= bx < tx_start + 16 and ty_start <= by < ty_start + 16:
                    self.mole = Mole(bx * 8, by * 8, self.level_map)
                    # Clear the 2x2 area where the boss tile was
                    for ty in range(by, by + 2):
                        for tx in range(bx, bx + 2):
                            self.level_map.remove_tile(tx, ty)
                    
                    self.level_map.close_gates(self.cam_x, self.cam_y)
                    self.boss_triggered = True

        # Update enemies
        for e in self.enemies:
            e.update(self.player, self.level_map)
        
        # Combat Collisions
        for e in self.enemies:
            if not e.is_alive: continue
            
            # Projectiles vs Enemies
            for p in self.projectiles:
                if p.is_active and e.check_collision(p.x, p.y, p.w, p.h):
                    e.take_damage()
                    p.is_active = False
            
            # Drill vs Enemies
            if self.player.state == "DIVING" and e.check_collision(self.player.x, self.player.y, self.player.w, self.player.h):
                e.take_damage()
                self.slime.refill(10)
                self.player.on_block_break()

        self.enemies = [e for e in self.enemies if e.is_alive]

        if self.mole:
            self.mole.update(self.projectiles, self.player)
            if not self.mole.is_alive:
                self.game_state = "WON"

        # Update projectiles with camera context
        for p in self.projectiles:
            p.update(self.cam_x, self.cam_y)
        self.projectiles = [p for p in self.projectiles if p.is_active]

        if self.shake_timer > 0:
            self.shake_timer -= 1

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
