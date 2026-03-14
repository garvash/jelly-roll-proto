import pyxel
from src.core.constants import TILE_SIZE, TILE_SOLID, TILE_HAZARD, TILE_DESTRUCTIBLE, TILE_EMPTY, TILE_GATE

class LevelMap:
    def __init__(self, tilemap_id=0):
        self.tilemap_id = tilemap_id

    def is_solid(self, tx, ty):
        """Returns True if the tile at (tx, ty) is solid, destructible, or a gate."""
        tile = pyxel.tilemaps[self.tilemap_id].pget(tx, ty)
        return tile == TILE_SOLID or tile == TILE_DESTRUCTIBLE or tile == TILE_GATE

    def is_hazard(self, tx, ty):
        """Returns True if the tile at (tx, ty) is a hazard (e.g., spikes)."""
        tile = pyxel.tilemaps[self.tilemap_id].pget(tx, ty)
        return tile == TILE_HAZARD

    def is_destructible(self, tx, ty):
        """Returns True if the tile at (tx, ty) is destructible."""
        tile = pyxel.tilemaps[self.tilemap_id].pget(tx, ty)
        return tile == TILE_DESTRUCTIBLE

    def get_tile(self, tx, ty):
        """Returns the (u, v) tuple of the tile at (tx, ty)."""
        return pyxel.tilemaps[self.tilemap_id].pget(tx, ty)

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
        pyxel.tilemaps[self.tilemap_id].pset(tx, ty, TILE_EMPTY)

    def find_tile(self, u, v, width=256, height=256):
        """Scans the map for a specific tile (u, v) and returns (tx, ty) or None."""
        for ty in range(height):
            for tx in range(width):
                if pyxel.tilemaps[self.tilemap_id].pget(tx, ty) == (u, v):
                    return (tx, ty)
        return None

    def close_gates(self, cam_x, cam_y):
        """Finds all TILE_GATE markers in the current room and replaces them with TILE_SOLID."""
        tx_start, ty_start = int(cam_x // 8), int(cam_y // 8)
        for ty in range(ty_start, ty_start + 16):
            for tx in range(tx_start, tx_start + 16):
                if pyxel.tilemaps[self.tilemap_id].pget(tx, ty) == TILE_GATE:
                    pyxel.tilemaps[self.tilemap_id].pset(tx, ty, TILE_SOLID)

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

    def load_from_tiled(self, json_path):
        """Loads a Tiled JSON map and populates the Pyxel tilemap."""
        import json
        import os
        if not os.path.exists(json_path):
            return False

        try:
            with open(json_path, 'r') as f:
                data = json.load(f)

            # Use the first tile layer
            layer = None
            for l in data.get('layers', []):
                if l.get('type') == 'tilelayer':
                    layer = l
                    break

            if not layer:
                return False

            width = layer['width']
            height = layer['height']
            tiles = layer['data']

            for i, tile_id in enumerate(tiles):
                if tile_id == 0:
                    # Clear tile in Pyxel
                    tx = i % width
                    ty = i // width
                    self.remove_tile(tx, ty)
                    continue

                # Tiled IDs are usually 1-based (firstgid=1)
                # Map to Pyxel (u, v)
                # Assumes 32 tiles per row in Image 0 (256 pixels / 8)
                real_id = tile_id - 1
                u = real_id % 32
                v = real_id // 32
                tx = i % width
                ty = i // width

                pyxel.tilemaps[self.tilemap_id].pset(tx, ty, (u, v))
            return True
        except Exception as e:
            print(f"Error loading Tiled map: {e}")
            return False

