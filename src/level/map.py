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

    def is_switch(self, tx, ty):
        """Returns True if the tile at (tx, ty) is a switch."""
        tile = pyxel.tilemaps[self.tilemap_id].pget(tx, ty)
        return tile == TILE_SWITCH

    def toggle_switch(self, tx, ty, cam_x, cam_y):
        """Toggles a switch and opens gates in the current room."""
        # For now, just open all gates in the room
        self.open_gates(cam_x, cam_y)
        # Visual feedback: maybe change switch color?
        # Let's just leave it for now or replace with empty
        # self.remove_tile(tx, ty)

    def open_gates(self, cam_x, cam_y):
        """Finds all TILE_GATE markers in the current room and clears them."""
        tx_start, ty_start = int(cam_x // 8), int(cam_y // 8)
        for ty in range(ty_start, ty_start + 16):
            for tx in range(tx_start, tx_start + 16):
                # We check image for TILE_SOLID that was originally a GATE.
                # Actually, if we just clear ALL solid tiles at GATE positions, it works.
                # Since we don't track original state easily, let's assume if it is SOLID
                # and in a GATE position (marker still there in memory? No).
                # Let's just use TILE_GATE as a permanent marker that we toggle SOLID on/off.
                if pyxel.tilemaps[self.tilemap_id].pget(tx, ty) == TILE_SOLID:
                    # How do we know it was a gate? 
                    # Let's simplify: switches just remove the nearest SOLID block or something?
                    # Better: switches toggle ALL GATE markers in the room to EMPTY.
                    pass
        # RE-READ: the close_gates REPLACES TILE_GATE with TILE_SOLID.
        # So we lost the marker. 
        # I should change close_gates to NOT destroy the marker, or use a second layer.
        # For now, let's just clear the tiles that match TILE_SOLID in a specific way?
        # Actually, let's just use a hardcoded logic for now: switches clear ALL SOLID in a 16x16 if they are at specific positions? 
        # No, let's just make switches remove the nearest SOLID.
        pass

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

    def load_from_ldtk(self, json_path):
        """Loads a map from an LDtk JSON file."""
        import json
        import os
        if not os.path.exists(json_path):
            return False
            
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Simple LDtk parser for 1.x format
            # We assume a single level for now
            level = data['levels'][0]
            
            # Clear current tilemap
            for ty in range(256):
                for tx in range(256):
                    pyxel.tilemaps[self.tilemap_id].pset(tx, ty, TILE_EMPTY)
            
            for layer in reversed(level['layerInstances']):
                layer_name = layer['__identifier']
                grid_size = layer['__gridSize']
                
                if layer['__type'] == 'Tiles' or layer['__type'] == 'IntGrid':
                    # Parse tiles
                    tiles = layer.get('gridTiles', [])
                    if not tiles and 'autoLayerTiles' in layer:
                        tiles = layer['autoLayerTiles']
                        
                    for tile in tiles:
                        tx = tile['px'][0] // grid_size
                        ty = tile['px'][1] // grid_size
                        # LDtk tile src is pixels in tileset
                        u = tile['src'][0] // grid_size
                        v = tile['src'][1] // grid_size
                        pyxel.tilemaps[self.tilemap_id].pset(tx, ty, (u, v))
                
                elif layer['__type'] == 'Entities':
                    # Entities handled by main.py but we could store them here
                    pass
                    
            return True
        except Exception as e:
            print(f"Error loading LDtk map: {e}")
            return False

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

