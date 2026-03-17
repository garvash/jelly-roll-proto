import pyxel
import os
from src.level.map import LevelMap

def export():
    # 128x128 tiles = 1024x1024 pixels (a large chunk of the total map)
    # Most Metroidvanias fit well in this space.
    EXPORT_WIDTH = 1024
    EXPORT_HEIGHT = 1024
    
    try:
        # Init in headless mode
        pyxel.init(EXPORT_WIDTH, EXPORT_HEIGHT, display="none")
    except Exception:
        pyxel.init(EXPORT_WIDTH, EXPORT_HEIGHT, title="Exporting...")

    # Load base assets
    if os.path.exists("assets/game.pyxres"):
        pyxel.load("assets/game.pyxres")
    
    # Load the map data using our game's priority logic
    lm = LevelMap()
    lm.load_from_tiled("assets/map.json")
    lm.load_from_ldtk("assets/map.ldtk")
    
    pyxel.cls(0)
    
    # Draw the full tilemap to the screen
    # bltm(x, y, tilemap_id, u, v, w, h)
    pyxel.bltm(0, 0, 0, 0, 0, EXPORT_WIDTH, EXPORT_HEIGHT)
    
    # Save the screen buffer to a PNG
    output_path = "assets/map_reference.png"
    pyxel.screen.save(output_path)
    
    print(f"Success! Map reference exported to: {output_path}")
    pyxel.quit()

if __name__ == "__main__":
    export()
