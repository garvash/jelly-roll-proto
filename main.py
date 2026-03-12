import pyxel
from src.level.map import LevelMap
# (import player later)

class Game:
    def __init__(self):
        pyxel.init(160, 120, title="Slime Drill Proto")
        # Load assets later
        # pyxel.load("assets/game.pyxres")
        self.level_map = LevelMap()
        # self.player = Player(40, 40, self.level_map)
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        # self.player.update()

    def draw(self):
        pyxel.cls(0)
        # Draw tilemap
        pyxel.bltm(0, 0, 0, 0, 0, 160, 120)
        # self.player.draw()

if __name__ == "__main__":
    Game()
