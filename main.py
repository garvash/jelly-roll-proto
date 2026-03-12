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
        self.player = Player(40, 40, self.level_map, self)
        self.slime = Slime(40, 40)
        self.death_timer = 0
        self.shake_timer = 0
        self.stop_frames = 0
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
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
        self.slime.draw()
        self.player.draw()

if __name__ == "__main__":
    Game()
