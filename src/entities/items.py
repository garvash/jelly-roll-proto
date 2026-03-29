import pyxel
from src.core.constants import SPRITE_SIZE
from src.core.sprite_utils import draw_sprite

class Item:
    def __init__(self, x, y, item_type, iid=None):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8
        self.item_type = item_type # "DASH_PICKUP", "ENERGY", "MISSILE"
        self.iid = iid  # LDtk instance ID for persistence tracking
        self.is_active = True
        self.bob_offset = 0

    def update(self):
        self.bob_offset = pyxel.sin(pyxel.frame_count * 10) * 2

    def collect(self, player, slime):
        if self.item_type == "DASH_PICKUP":
            player.has_dash = True
        elif self.item_type == "ENERGY":
            player.max_hp += 1
            player.hp = player.max_hp
        elif self.item_type == "MISSILE":
            slime.max_juice += 50
            slime.juice = slime.max_juice
        elif self.item_type == "SHIELD_PICKUP":
            player.has_shield = True
        elif self.item_type == "BOOST_PICKUP":
            player.has_boost = True
        elif self.item_type == "SHIELD_T2":
            player.has_shield_t2 = True

        self.is_active = False

    def draw(self):
        if not self.is_active:
            return
        
        # All items now on bank 1, row y=64 (16x16 frames)
        # Frame order: energy=0, missile=1, dash=2, shield=3, boost=4, shield_t2=5
        ITEM_FRAMES = {
            "ENERGY": 0,
            "MISSILE": 1,
            "DASH_PICKUP": 2,
            "SHIELD_PICKUP": 3,
            "BOOST_PICKUP": 4,
            "SHIELD_T2": 5,
        }
        frame = ITEM_FRAMES.get(self.item_type, 0)
        u = frame * 16
        # Items bob vertically -- apply bob to y before passing to draw_sprite
        draw_sprite(self.x, self.y + self.bob_offset, self.w, self.h, 1, u, 64,
                    SPRITE_SIZE, SPRITE_SIZE, True)
        
        # Shine effect
        if pyxel.frame_count % 20 < 5:
            pyxel.pset(self.x + 2, self.y + self.bob_offset + 2, 7)
