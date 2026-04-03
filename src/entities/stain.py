import pyxel

class JuiceStain:
    def __init__(self, x, y, duration=360):
        self.x = x
        self.y = y
        self.duration = duration
        self.is_active = True
        self.color = 11 # Slime green

    def update(self):
        self.duration -= 1
        if self.duration <= 0:
            self.is_active = False

    def draw(self):
        if not self.is_active:
            return
        # Simple irregular shape for juice
        pyxel.pset(self.x, self.y, self.color)
        pyxel.pset(self.x+1, self.y, self.color)
        pyxel.pset(self.x, self.y+1, self.color)
        
        # Flashing effect when about to disappear
        if self.duration > 60 or pyxel.frame_count % 8 < 4:
            pyxel.pset(self.x-1, self.y+1, self.color)
            pyxel.pset(self.x+1, self.y+1, self.color)
            pyxel.pset(self.x, self.y+2, self.color)
