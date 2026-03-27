import pyxel

class Item:
    def __init__(self, x, y, item_type, iid=None):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8
        self.item_type = item_type # "DRILL", "ENERGY", "MISSILE"
        self.iid = iid  # LDtk instance ID for persistence tracking
        self.is_active = True
        self.bob_offset = 0

    def update(self):
        self.bob_offset = pyxel.sin(pyxel.frame_count * 10) * 2

    def collect(self, player, slime):
        if self.item_type == "DRILL":
            player.has_drill = True
        elif self.item_type == "ENERGY":
            player.max_hp += 1
            player.hp = player.max_hp
        elif self.item_type == "MISSILE":
            slime.max_juice += 50
            slime.juice = slime.max_juice
        
        self.is_active = False

    def draw(self):
        if not self.is_active:
            return
        
        # Determine sprite based on type
        img = 1 # Default for Energy/Missile tanks
        u, v = 0, 0
        if self.item_type == "DRILL":
            img = 0
            u, v = 24, 0
        elif self.item_type == "ENERGY":
            u, v = 56, 0
        elif self.item_type == "MISSILE":
            u, v = 48, 8
            
        # Draw with bobbing effect
        pyxel.blt(self.x, self.y + self.bob_offset, img, u, v, 8, 8, 0)
        
        # Shine effect
        if pyxel.frame_count % 20 < 5:
            pyxel.pset(self.x + 2, self.y + self.bob_offset + 2, 7)
