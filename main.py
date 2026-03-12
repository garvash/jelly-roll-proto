import pyxel
from src.level.map import LevelMap
from src.entities.player import Player
from src.entities.slime import Slime

class Game:
    def __init__(self):
        pyxel.init(160, 120, title="Slime Drill Proto")
        # Load assets
        pyxel.load("assets/game.pyxres")
        self.level_map = LevelMap()
        self.player = Player(40, 40, self.level_map)
        self.slime = Slime(40, 40)
        self.death_timer = 0
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
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

    def draw(self):
        pyxel.cls(0)
        # Draw tilemap
        pyxel.bltm(0, 0, 0, 0, 0, 160, 120)
        self.slime.draw()
        self.player.draw()

if __name__ == "__main__":
    Game()
