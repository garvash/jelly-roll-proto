import pyxel
import os

def generate():
    # Pyxel needs a window but we can try to use headless if supported, 
    # or just use a small window and quit.
    try:
        # Try to init without a window if possible or just small
        pyxel.init(128, 128, display="none")
    except Exception:
        try:
            pyxel.init(128, 128, title="Asset Generator")
        except Exception as e:
            print(f"Could not initialize pyxel: {e}")
            return

    # Image 0: Player sprite (8x8), Slime (8x8), Drill (8x8) and Tiles (8x8)
    
    # Tile unit (0, 0) - PIXEL (0, 0) to (7, 7) is EMPTY (transparent)
    for y in range(8):
        for x in range(8):
            pyxel.images[0].pset(x, y, 0)

    # Player at (8, 0) - Tile column 1, row 0
    # Let's make it a cyan player
    # 0 = transparent, 10 = light blue, 12 = blue, 7 = white
    for y in range(8):
        for x in range(8, 16):
            color = 0
            rel_x = x - 8
            if 1 <= rel_x <= 6 and 2 <= y <= 7:
                color = 12
                if rel_x == 2 or rel_x == 5:
                    if y == 4: color = 7 # eyes
            pyxel.images[0].pset(x, y, color)

    # Slime at (16, 0) - Tile column 2, row 0
    # 11 = green, 3 = dark green
    for y in range(8):
        for x in range(16, 24):
            color = 0
            rel_x = x - 16
            if 1 <= rel_x <= 6 and 3 <= y <= 7:
                color = 11
                if rel_x == 2 or rel_x == 5:
                    if y == 5: color = 7 # tiny eyes
            pyxel.images[0].pset(x, y, color)

    # Drill at (24, 0) - Tile column 3, row 0
    # 14 = light pink/purple, 13 = grey
    for y in range(8):
        for x in range(24, 32):
            color = 0
            rel_x = x - 24
            if y >= 2:
                width = (y - 2) + 1
                if width > 4: width = 4
                if abs(rel_x - 3.5) <= width:
                    color = 13 if y % 2 == 0 else 6
            pyxel.images[0].pset(x, y, color)

    # --- NEW ASSETS FOR PHASE 4 ---

    # Mole Boss at (32, 0) - 16x16 sprite (takes 4 8x8 tiles)
    # 4 = brown, 9 = orange (nose), 7 = white (claws)
    for y in range(16):
        for x in range(32, 48):
            color = 0
            rel_x = x - 32
            rel_y = y
            # Simple oval body
            if (rel_x - 7.5)**2 / 7**2 + (rel_y - 7.5)**2 / 7**2 <= 1:
                color = 4
                # Eyes
                if rel_y == 5 and (rel_x == 5 or rel_x == 10):
                    color = 0
                # Nose
                if 7 <= rel_x <= 8 and 7 <= rel_y <= 8:
                    color = 9
                # Claws
                if rel_y >= 12 and (rel_x <= 3 or rel_x >= 12):
                    color = 7
            pyxel.images[0].pset(x, y, color)

    # Projectile at (48, 0) - 4x4 sprite (stored in 8x8 tile)
    # 11 = green (slime spit)
    for y in range(4):
        for x in range(48, 52):
            pyxel.images[0].pset(x, y, 11)

    # --- TILES IN ROW 1 (y = 8 to 15) ---

    # Tile at (0, 8) (solid block) - TILE_SOLID (0, 1)
    # 12 = light blue, 5 = dark blue
    for y in range(8, 16):
        for x in range(0, 8):
            color = 12
            if x == 0 or x == 7 or y == 8 or y == 15:
                color = 5
            pyxel.images[0].pset(x, y, color)

    # Tile at (8, 8) (hazard/spikes) - TILE_HAZARD (1, 1)
    # 8 = red, 2 = dark red
    for y in range(8, 16):
        for x in range(8, 16):
            color = 0 # transparent bg
            rel_x = x - 8
            rel_y = y - 8
            # Simple spikes
            if rel_y >= 4:
                if (rel_x + rel_y) % 4 == 0 or (rel_x - rel_y) % 4 == 0:
                    color = 8
            pyxel.images[0].pset(x, y, color)

    # Tile at (16, 8) (destructible) - TILE_DESTRUCTIBLE (2, 1)
    # 9 = orange, 4 = brown
    for y in range(8, 16):
        for x in range(16, 24):
            color = 9
            if (x + y) % 4 == 0:
                color = 4
            if x == 16 or x == 23 or y == 8 or y == 15:
                color = 4
            pyxel.images[0].pset(x, y, color)

    # Tile at (24, 8) (gate marker) - TILE_GATE (3, 1)
    # 2 = dark purple
    for y in range(8, 16):
        for x in range(24, 32):
            color = 2 if (x + y) % 2 == 0 else 0
            pyxel.images[0].pset(x, y, color)

    # Tilemap 0: Gym level
    solid_tile = (0, 1) 
    hazard_tile = (1, 1)
    destructible_tile = (2, 1)

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

    # Hazard Area
    for x in range(1, 4):
        pyxel.tilemaps[0].pset(x, 13, hazard_tile)

    # Destructible Platform
    for x in range(14, 18):
        pyxel.tilemaps[0].pset(x, 10, destructible_tile)

    # Wall for wall jump (on the right)
    for y in range(4, 10):
        pyxel.tilemaps[0].pset(15, y, solid_tile)

    # Small pillar to dash over
    pyxel.tilemaps[0].pset(14, 13, solid_tile)

    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    if os.path.exists("assets/game.pyxres"):
        print("assets/game.pyxres already exists. skipping save to protect user art.")
    else:
        pyxel.save("assets/game.pyxres")
        print("assets/game.pyxres saved.")

    # Always export as PNG for Tiled
    pyxel.images[0].save("assets/tileset.png", 1) 
    print("assets/tileset.png exported/updated.")

if __name__ == "__main__":
    generate()
