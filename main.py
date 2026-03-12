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
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
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
