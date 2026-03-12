import pyxel
from src.core.constants import TILE_SIZE, TILE_SOLID, TILE_HAZARD, TILE_DESTRUCTIBLE, TILE_EMPTY

class LevelMap:
    def __init__(self, tilemap_id=0):
        self.tilemap_id = tilemap_id

    def is_solid(self, tx, ty):
        """Returns True if the tile at (tx, ty) is solid or destructible."""
        tile = pyxel.tilemap(self.tilemap_id).pget(tx, ty)
        return tile == TILE_SOLID or tile == TILE_DESTRUCTIBLE

    def is_hazard(self, tx, ty):
        """Returns True if the tile at (tx, ty) is a hazard (e.g., spikes)."""
        tile = pyxel.tilemap(self.tilemap_id).pget(tx, ty)
        return tile == TILE_HAZARD

    def is_destructible(self, tx, ty):
        """Returns True if the tile at (tx, ty) is destructible."""
        tile = pyxel.tilemap(self.tilemap_id).pget(tx, ty)
        return tile == TILE_DESTRUCTIBLE

    def check_collision(self, x, y, width, height):
        """Returns True if the AABB overlaps any solid tile."""
        x1 = int(x // TILE_SIZE)
        y1 = int(y // TILE_SIZE)
        x2 = int((x + width - 1) // TILE_SIZE)
        y2 = int((y + height - 1) // TILE_SIZE)

        for ty in range(y1, y2 + 1):
            for tx in range(x1, x2 + 1):
                if self.is_solid(tx, ty):
                    return True
        return False

    def check_hazard(self, x, y, width, height):
        """Returns True if the AABB overlaps any hazard tile."""
        x1 = int(x // TILE_SIZE)
        y1 = int(y // TILE_SIZE)
        x2 = int((x + width - 1) // TILE_SIZE)
        y2 = int((y + height - 1) // TILE_SIZE)

        for ty in range(y1, y2 + 1):
            for tx in range(x1, x2 + 1):
                if self.is_hazard(tx, ty):
                    return True
        return False

    def remove_tile(self, tx, ty):
        """Clears the tile at (tx, ty) from the tilemap."""
        pyxel.tilemap(self.tilemap_id).pset(tx, ty, TILE_EMPTY)

    def get_destructible_at(self, x, y, width, height):
        """Returns (tx, ty) of a destructible tile overlapping the AABB, or None."""
        x1 = int(x // TILE_SIZE)
        y1 = int(y // TILE_SIZE)
        x2 = int((x + width - 1) // TILE_SIZE)
        y2 = int((y + height - 1) // TILE_SIZE)

        for ty in range(y1, y2 + 1):
            for tx in range(x1, x2 + 1):
                if self.is_destructible(tx, ty):
                    return (tx, ty)
        return None
