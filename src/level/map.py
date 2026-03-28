import pyxel
from src.core.constants import (TILE_SIZE, TILE_SOLID, TILE_HAZARD, TILE_DESTRUCTIBLE,
                                TILE_EMPTY, TILE_GATE, TILE_SWITCH,
                                TILE_CRACKED_H, TILE_CRACKED_V,
                                TILE_WATER, TILE_ACID, TILE_LAVA,
                                HAZARD_DRAIN_RATES)
from src.level.world import LevelBounds

class LevelMap:
    def __init__(self, tilemap_id=0):
        self.tilemap_id = tilemap_id
        self.entities = [] # List of {type, x, y} from LDtk
        self.collision_data = {} # Key: (tx, ty), Value: (u, v) logic tile
        self.locked_gates = set() # Set of (tx, ty) coordinates
        self.levels = {} # Key: level identifier, Value: LevelBounds

    def load_from_ldtk_simplified(self, root_dir):
        """Loads levels from the LDtk 'Super Simple Export' directory."""
        import json
        import os
        if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
            return False
            
        try:
            # Clear current state (Once per full map load)
            self.entities = []
            self.collision_data = {}
            self.locked_gates = set()
            self.levels = {}
            pyxel.tilemaps[self.tilemap_id].imgsrc = 0
            
            for ty in range(256):
                for tx in range(256):
                    pyxel.tilemaps[self.tilemap_id].pset(tx, ty, TILE_EMPTY)

            val_to_tile = {
                1: TILE_SOLID,
                2: TILE_HAZARD,
                3: TILE_DESTRUCTIBLE,
                4: TILE_GATE,
                5: TILE_SWITCH,
                11: TILE_CRACKED_H,
                12: TILE_CRACKED_V,
                6: TILE_WATER,
                7: TILE_ACID,
                8: TILE_LAVA,
            }

            tiles_loaded = 0
            for level_name in os.listdir(root_dir):
                level_path = os.path.join(root_dir, level_name)
                if not os.path.isdir(level_path): continue
                
                # 1. Load Metadata
                data_json = os.path.join(level_path, "data.json")
                if not os.path.exists(data_json): continue
                with open(data_json, 'r') as f:
                    data = json.load(f)
                
                world_x, world_y = data["x"], data["y"]
                level_w = data.get("width", 128)
                level_h = data.get("height", 128)
                level_id = data.get("identifier", level_name)
                self.levels[level_id] = LevelBounds(
                    level_id, world_x, world_y, level_w, level_h
                )

                base_tx, base_ty = world_x // 8, world_y // 8

                # Entities
                for ent_type, instances in data.get("entities", {}).items():
                    for inst in instances:
                        ent_data = {
                            "type": ent_type,
                            "x": world_x + inst["x"],
                            "y": world_y + inst["y"]
                        }
                        # Capture LDtk instance ID for persistence tracking
                        if "iid" in inst:
                            ent_data["iid"] = inst["iid"]
                        # Capture custom fields (nested in LDtk simplified export)
                        for key, val in inst.get("customFields", {}).items():
                            ent_data[key] = val
                        # Also capture top-level fields (width, height, etc.)
                        for key, val in inst.items():
                            if key not in ("x", "y", "iid", "id", "layer", "color", "customFields"):
                                ent_data[key] = val
                        self.entities.append(ent_data)

                # 2. Load Layers
                for layer_file in os.listdir(level_path):
                    if not layer_file.endswith(".csv"): continue
                    
                    is_intgrid = (layer_file == "IntGrid.csv")
                    
                    with open(os.path.join(level_path, layer_file), 'r') as f:
                        lines = [l.strip() for l in f.readlines() if l.strip()]
                    
                    for ry, line in enumerate(lines):
                        vals =[v.strip() for v in line.split(',') if v.strip()]
                        for rx, val in enumerate(vals):
                            if is_intgrid and (val == "0" or val == "-1"): 
                                continue
                            if not is_intgrid and val == "-1": 
                                continue
                            
                            tx, ty = base_tx + rx, base_ty + ry
                            
                            try:
                                v = int(val)
                                if is_intgrid:
                                    if v in val_to_tile:
                                        # Store logic property (absolute)
                                        self.collision_data[(tx, ty)] = val_to_tile[v]
                                        # Set visual tile (The tilemap supports up to 256x256 tiles, so tx/ty are safe)
                                        pyxel.tilemaps[self.tilemap_id].pset(tx, ty, val_to_tile[v])
                                        tiles_loaded += 1
                                else:
                                    # Set visual tilemap for standard tile layers
                                    pyxel.tilemaps[self.tilemap_id].pset(tx, ty, (v % 32, v // 32))
                                    tiles_loaded += 1
                            except: continue
            
            print(f"LDtk Load: {tiles_loaded} tiles across levels.")
            return True
        except Exception as e:
            print(f"Error loading LDtk simplified map: {e}")
            return False

    def get_level_bounds_list(self):
        """Return all LevelBounds as a list for WorldManager initialization."""
        return list(self.levels.values())

    def is_solid(self, tx, ty):
        """Returns True if the tile at (tx, ty) is solid, destructible, cracked, or a locked gate."""
        if (tx, ty) in self.locked_gates:
            return True
        tile = self.collision_data.get((tx, ty))
        return tile in (TILE_SOLID, TILE_DESTRUCTIBLE,
                        TILE_CRACKED_H, TILE_CRACKED_V)

    def is_hazard(self, tx, ty):
        """Returns True if the tile at (tx, ty) is a hazard (e.g., spikes)."""
        return self.collision_data.get((tx, ty)) == TILE_HAZARD

    def is_destructible(self, tx, ty):
        """Returns True if the tile at (tx, ty) is destructible (standard or cracked)."""
        tile = self.collision_data.get((tx, ty))
        return tile in (TILE_DESTRUCTIBLE, TILE_CRACKED_H, TILE_CRACKED_V)

    def is_switch(self, tx, ty):
        """Returns True if the tile at (tx, ty) is a switch."""
        return self.collision_data.get((tx, ty)) == TILE_SWITCH

    def is_cracked(self, tx, ty):
        """Returns True if the tile is any type of cracked block."""
        tile = self.collision_data.get((tx, ty))
        return tile in (TILE_CRACKED_H, TILE_CRACKED_V)

    def is_cracked_horizontal(self, tx, ty):
        """Returns True if the tile is a horizontal cracked block (ABL-01)."""
        return self.collision_data.get((tx, ty)) == TILE_CRACKED_H

    def is_cracked_vertical(self, tx, ty):
        """Returns True if the tile is a vertical cracked block (ABL-02)."""
        return self.collision_data.get((tx, ty)) == TILE_CRACKED_V

    def toggle_switch(self, tx, ty, cam_x, cam_y):
        """Toggles a switch and opens gates in the current room."""
        self.open_gates(cam_x, cam_y)

    def open_gates(self, cam_x, cam_y):
        """Unlocks all gates in the current room."""
        tx_start, ty_start = int(cam_x // 8), int(cam_y // 8)
        # We need to iterate over a list because we're modifying the set
        for tx, ty in list(self.locked_gates):
            if tx_start <= tx < tx_start + 16 and ty_start <= ty < ty_start + 16:
                self.locked_gates.remove((tx, ty))
                # Restore visual to empty
                pyxel.tilemaps[self.tilemap_id].pset(tx, ty, TILE_EMPTY)

    def close_gates(self, cam_x, cam_y):
        """Finds all TILE_GATE markers in the current room and locks them."""
        tx_start, ty_start = int(cam_x // 8), int(cam_y // 8)
        # Scan collision data for gates
        for (tx, ty), tile in self.collision_data.items():
            if tx_start <= tx < tx_start + 16 and ty_start <= ty < ty_start + 16:
                if tile == TILE_GATE:
                    self.locked_gates.add((tx, ty))
                    # Also update visual tilemap to show solid gate
                    pyxel.tilemaps[self.tilemap_id].pset(tx, ty, TILE_SOLID)
        
        # Scan visual tilemap for legacy/unloaded gates
        for ty in range(ty_start, ty_start + 16):
            for tx in range(tx_start, tx_start + 16):
                if pyxel.tilemaps[self.tilemap_id].pget(tx, ty) == TILE_GATE:
                    self.locked_gates.add((tx, ty))
                    pyxel.tilemaps[self.tilemap_id].pset(tx, ty, TILE_SOLID)

    def get_tile(self, tx, ty):
        """Returns the (u, v) tuple of the tile at (tx, ty) from collision data or tilemap."""
        # Preference to logic tiles for markers
        if (tx, ty) in self.collision_data:
            return self.collision_data[(tx, ty)]
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

    def get_zone_hazard_type(self, x, y, width, height):
        """Returns the zone hazard tile type overlapping the AABB, or None.
        Checks TILE_WATER, TILE_ACID, TILE_LAVA (NOT TILE_HAZARD spikes).
        If multiple zone types overlap, returns the one with highest drain rate."""
        x1 = int(x // TILE_SIZE)
        y1 = int(y // TILE_SIZE)
        x2 = int((x + width - 1) // TILE_SIZE)
        y2 = int((y + height - 1) // TILE_SIZE)
        worst = None
        for ty in range(y1, y2 + 1):
            for tx in range(x1, x2 + 1):
                tile = self.collision_data.get((tx, ty))
                if tile in HAZARD_DRAIN_RATES:
                    if worst is None or HAZARD_DRAIN_RATES[tile] > HAZARD_DRAIN_RATES.get(worst, 0):
                        worst = tile
        return worst

    def remove_tile(self, tx, ty):
        """Clears the tile at (tx, ty) from both visual and collision data."""
        if (tx, ty) in self.collision_data:
            del self.collision_data[(tx, ty)]
        if (tx, ty) in self.locked_gates:
            self.locked_gates.remove((tx, ty))
        pyxel.tilemaps[self.tilemap_id].pset(tx, ty, TILE_EMPTY)

    def restore_tile(self, tx, ty, tile_data):
        """Restore a previously removed tile (for block regeneration).

        Args:
            tx, ty: Tile coordinates.
            tile_data: The tile value to restore (e.g., TILE_DESTRUCTIBLE).
        """
        self.collision_data[(tx, ty)] = tile_data
        pyxel.tilemaps[self.tilemap_id].pset(tx, ty, tile_data)

    def find_tile(self, u, v, width=256, height=256):
        """Scans both collision and visual data for a specific tile."""
        # 1. Scan collision data
        for (tx, ty), tile in self.collision_data.items():
            if tile == (u, v):
                return (tx, ty)
        
        # 2. Scan tilemap
        for ty in range(height):
            for tx in range(width):
                if pyxel.tilemaps[self.tilemap_id].pget(tx, ty) == (u, v):
                    return (tx, ty)
        return None

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

    def get_cracked_h_at(self, x, y, width, height):
        """Returns (tx, ty) of a CRACKED_H tile overlapping the AABB, or None.
        Used by Slime Ram (ABL-01) for horizontal gate breaking (D-12)."""
        x1 = int(x // TILE_SIZE)
        y1 = int(y // TILE_SIZE)
        x2 = int((x + width - 1) // TILE_SIZE)
        y2 = int((y + height - 1) // TILE_SIZE)
        for ty in range(y1, y2 + 1):
            for tx in range(x1, x2 + 1):
                if self.is_cracked_horizontal(tx, ty):
                    return (tx, ty)
        return None

    def get_cracked_v_at(self, x, y, width, height):
        """Returns (tx, ty) of a CRACKED_V tile overlapping the AABB, or None.
        Used by Drill Dive and Slime Boost for vertical gate breaking (ABL-02)."""
        x1 = int(x // TILE_SIZE)
        y1 = int(y // TILE_SIZE)
        x2 = int((x + width - 1) // TILE_SIZE)
        y2 = int((y + height - 1) // TILE_SIZE)
        for ty in range(y1, y2 + 1):
            for tx in range(x1, x2 + 1):
                if self.is_cracked_vertical(tx, ty):
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
            self.entities = []
            self.collision_data = {}
            self.locked_gates = set()
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
