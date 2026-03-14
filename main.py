import pyxel
from src.level.map import LevelMap
from src.entities.player import Player
from src.entities.slime import Slime
from src.entities.boss import Mole

class Game:
    def __init__(self):
        pyxel.init(160, 120, title="Slime Drill Proto")
        # Load assets
        pyxel.load("assets/game.pyxres")
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
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
        
        # Try to find boss spawn tile (4, 0) - Top left of 16x16 boss
        self.mole = None
        boss_tile = self.level_map.find_tile(4, 0)
        if boss_tile:
            bx, by = boss_tile
            self.mole = Mole(bx * 8, by * 8, self.level_map)
            # Clear the 2x2 area where the boss tile was
            for ty in range(by, by + 2):
                for tx in range(bx, bx + 2):
                    self.level_map.remove_tile(tx, ty)

        self.projectiles = []
        self.game_state = "PLAYING" # PLAYING, WON
        self.death_timer = 0
        self.shake_timer = 0
        self.stop_frames = 0

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
                self.player.x = self.player.start_x
                self.player.y = self.player.start_y
                self.player.is_alive = True
                self.player.state = "IDLE"
                self.death_timer = 0
                # Also reset slime? Usually good idea
                self.slime.x = self.player.x
                self.slime.y = self.player.y
            return

        self.player.update(self.slime)
        self.slime.update(self.player.x, self.player.y, self.player.facing_right, self.player.is_fused)
        
        if self.mole:
            self.mole.update(self.projectiles, self.player)
            if not self.mole.is_alive:
                self.game_state = "WON"

        # Update projectiles
        for p in self.projectiles:
            p.update()
        self.projectiles = [p for p in self.projectiles if p.is_active]

        if self.shake_timer > 0:
            self.shake_timer -= 1

    def draw(self):
        pyxel.cls(0)
        
        # Screen shake
        if self.shake_timer > 0:
            dx = pyxel.rndi(-2, 2)
            dy = pyxel.rndi(-2, 2)
            pyxel.camera(dx, dy)
        else:
            pyxel.camera(0, 0)

        # Draw tilemap
        pyxel.bltm(0, 0, 0, 0, 0, 160, 120)
        
        if self.mole:
            self.mole.draw()
            
        self.slime.draw()
        for p in self.projectiles:
            p.draw()
        self.player.draw()

        if self.game_state == "WON":
            pyxel.rect(30, 50, 100, 30, 0)
            pyxel.rectb(30, 50, 100, 30, 7)
            pyxel.text(60, 60, "VICTORY!", pyxel.frame_count % 16)
            pyxel.text(45, 70, "PRESS R TO RESTART", 7)

if __name__ == "__main__":
    Game()
