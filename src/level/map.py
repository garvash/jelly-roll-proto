import pyxel
from src.core.constants import TILE_SIZE

class LevelMap:
    def __init__(self, tilemap_id=0):
        self.tilemap_id = tilemap_id
        # Define what tiles are solid (e.g., anything with index > 0)
        self.solid_tiles = [1] 

    def is_solid(self, tx, ty):
        """Returns True if the tile at (tx, ty) is solid."""
        tile = pyxel.tilemap(self.tilemap_id).pget(tx, ty)
        return tile[0] > 0 or tile[1] > 0 # Simple check for now: any non-zero tile

    def check_collision(self, x, y, width, height):
        """Returns True if the AABB overlaps any solid tile."""
        # Top-left tile
        x1 = int(x // TILE_SIZE)
        y1 = int(y // TILE_SIZE)
        # Bottom-right tile
        x2 = int((x + width - 1) // TILE_SIZE)
        y2 = int((y + height - 1) // TILE_SIZE)

        for ty in range(y1, y2 + 1):
            for tx in range(x1, x2 + 1):
                if self.is_solid(tx, ty):
                    return True
        return False
