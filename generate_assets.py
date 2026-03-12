import pyxel
import os

def generate():
    # Pyxel needs a window but we can try to use headless if supported, 
    # or just use a small window and quit.
    # In recent pyxel, there isn't a true headless mode for saving resources,
    # but we can try to just use pyxel.init and then save.
    try:
        # Try to init without a window if possible or just small
        pyxel.init(160, 120, display="none")
    except Exception:
        try:
            pyxel.init(160, 120, title="Asset Generator")
        except Exception as e:
            print(f"Could not initialize pyxel: {e}")
            return

    # Image 0: Player sprite (8x8) and Tiles (8x8)
    # Player at 0, 0
    # Let's make it a cyan player
    # 0 = transparent, 10 = light blue, 12 = blue, 7 = white
    for y in range(8):
        for x in range(8):
            color = 0
            if 1 <= x <= 6 and 2 <= y <= 7:
                color = 12
                if x == 2 or x == 5:
                    if y == 4: color = 7 # eyes
            pyxel.images[0].pset(x, y, color)

    # Slime at 8, 0
    # 11 = green, 3 = dark green
    for y in range(8):
        for x in range(8, 16):
            color = 0
            if 9 <= x <= 14 and 3 <= y <= 7:
                color = 11
                if x == 10 or x == 13:
                    if y == 5: color = 7 # tiny eyes
            pyxel.images[0].pset(x, y, color)

    # Drill at 16, 0 (8x8)
    # 14 = light pink/purple, 13 = grey
    for y in range(8):
        for x in range(16, 24):
            color = 0
            # A simple cone/drill shape
            # 16-23 is x
            rel_x = x - 16
            if y >= 2:
                width = (y - 2) + 1
                if width > 4: width = 4
                if abs(rel_x - 3.5) <= width:
                    color = 13 if y % 2 == 0 else 6
            pyxel.images[0].pset(x, y, color)

    # Tile at 0, 8 (solid block)
    # 12 = light blue, 5 = dark blue
    for y in range(8, 16):
        for x in range(0, 8):
            color = 12
            if x == 0 or x == 7 or y == 8 or y == 15:
                color = 5
            pyxel.images[0].pset(x, y, color)

    # Tilemap 0: Gym level
    # 0, 1 is the solid tile in image 0 (tile x=0, y=1 where tile size is 8)
    solid_tile = (0, 1) 

    # Floor
    for x in range(20):
        pyxel.tilemaps[0].pset(x, 14, solid_tile)
    
    # Left/Right Walls
    for y in range(15):
        pyxel.tilemaps[0].pset(0, y, solid_tile)
        pyxel.tilemaps[0].pset(19, y, solid_tile)

    # Platforms
    for x in range(4, 7):
        pyxel.tilemaps[0].pset(x, 11, solid_tile)
    
    for x in range(9, 12):
        pyxel.tilemaps[0].pset(x, 8, solid_tile)

    # Wall for wall jump (on the right)
    for y in range(4, 10):
        pyxel.tilemaps[0].pset(15, y, solid_tile)

    # Gap for dash
    for x in range(12, 18):
        pyxel.tilemaps[0].pset(x, 14, (0, 0)) # clear floor
    
    # Small pillar to dash over
    pyxel.tilemaps[0].pset(14, 13, solid_tile)

    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    pyxel.save("assets/game.pyxres")
    print("Assets saved to assets/game.pyxres")

if __name__ == "__main__":
    generate()
