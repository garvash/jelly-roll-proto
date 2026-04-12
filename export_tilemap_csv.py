import pyxel
import os

from src.core.constants import VIEWPORT_W, VIEWPORT_H, TILE_SIZE

def export_to_csv():
    # Load the resource file
    if not os.path.exists("assets/game.pyxres"):
        print("Error: assets/game.pyxres not found!")
        return

    try:
        # Try to init without a window if possible
        pyxel.init(1, 1, display="none")
    except Exception:
        pyxel.init(1, 1, title="Exporting CSV")
    
    pyxel.load("assets/game.pyxres")
    
    tm = pyxel.tilemaps[0]
    # Export area matches standard room dimensions (in tiles)
    width = VIEWPORT_W // TILE_SIZE   # 320 / 8 = 40 tiles
    height = VIEWPORT_H // TILE_SIZE  # 176 / 8 = 22 tiles
    
    csv_lines = []
    
    for y in range(height):
        row = []
        for x in range(width):
            u, v = tm.pget(x, y)
            # Convert (u,v) tileset coords to a single Tile ID
            # 256 pixels / 8 = 32 tiles per row in the tileset
            tile_id = v * 32 + u
            
            # Pyxel (0,0) empty is usually ID 0. 
            # If your map is mostly empty, LDtk likes -1 or 0 depending on setup.
            if u == 0 and v == 0:
                row.append("-1") # LDtk "Empty" tile
            else:
                row.append(str(tile_id))
        
        csv_lines.append(",".join(row))
    
    output_path = "assets/map_data.csv"
    with open(output_path, "w") as f:
        f.write("\n".join(csv_lines))
        
    print(f"Success! Tilemap data exported to: {output_path}")
    print("In LDtk: Create a Tiles layer, then use 'Import from CSV' and select this file.")
    pyxel.quit()

if __name__ == "__main__":
    export_to_csv()
