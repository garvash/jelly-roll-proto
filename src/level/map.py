import pyxel
from src.core.constants import (TILE_SIZE, TILE_EMPTY,
                                HAZARD_DRAIN_RATES,
                                VIEWPORT_W, VIEWPORT_H)
from src.core import schema
from src.level.world import LevelBounds

# 256px tileset / 16px tiles = 16 tiles per row
TILES_PER_ROW = 256 // TILE_SIZE

# Pyxel tilemaps use 8px cells internally. 16px tiles occupy 2x2 cells.
# 8px empty cell — maps to bottom-right of 256px image bank (empty area)
_EMPTY_8PX = (TILE_EMPTY[0] * 2, TILE_EMPTY[1] * 2)


def _pset_tile(tm_id, tx, ty, tile_uv):
    """Write a 16px tile as a 2x2 block of 8px tilemap cells."""
    u, v = tile_uv
    cx, cy = tx * 2, ty * 2
    u2, v2 = u * 2, v * 2
    tm = pyxel.tilemaps[tm_id]
    tm.pset(cx, cy, (u2, v2))
    tm.pset(cx + 1, cy, (u2 + 1, v2))
    tm.pset(cx, cy + 1, (u2, v2 + 1))
    tm.pset(cx + 1, cy + 1, (u2 + 1, v2 + 1))


def _pget_tile(tm_id, tx, ty):
    """Read 16px tile from top-left 8px cell of its 2x2 block."""
    cu, cv = pyxel.tilemaps[tm_id].pget(tx * 2, ty * 2)
    return (cu // 2, cv // 2)


def _clear_tilemap(tm_id):
    """Clear entire tilemap with empty 8px cells."""
    tm = pyxel.tilemaps[tm_id]
    for cy in range(256):
        for cx in range(256):
            tm.pset(cx, cy, _EMPTY_8PX)


# Schema-driven behavior caches (lazy-initialized after schema.init)
_solid_values = None
_hazard_values = None
_destructible_values = None
_zone_hazard_values = None
_interactive_values = None
_val_to_tile = None


def _ensure_schema_cache():
    """Initialize module-level schema caches on first use."""
    global _solid_values, _hazard_values, _destructible_values
    global _zone_hazard_values, _interactive_values, _val_to_tile
    if _val_to_tile is None:
        _val_to_tile = schema.get_val_to_tile()
        _solid_values = schema.get_solid_values()
        _hazard_values = schema.get_hazard_values()
        _destructible_values = schema.get_destructible_values()
        _zone_hazard_values = schema.get_zone_hazard_values()
        _interactive_values = schema.get_interactive_values()

class LevelMap:
    def __init__(self, tilemap_id=0):
        self.tilemap_id = tilemap_id
        self.entities = [] # List of {type, x, y} from LDtk
        self.collision_data = {} # Key: (tx, ty), Value: IntGrid int
        self.levels = {} # Key: level identifier, Value: LevelBounds

    def load_from_ldtk_simplified(self, root_dir):
        """Loads levels from the LDtk 'Super Simple Export' directory."""
        import json
        import os
        if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
            return False

        try:
            _ensure_schema_cache()

            # Clear current state (Once per full map load)
            self.entities = []
            self.collision_data = {}
            self.levels = {}
            pyxel.tilemaps[self.tilemap_id].imgsrc = 0
            _clear_tilemap(self.tilemap_id)

            # Pass 1: Find minimum world coordinates to normalize into tilemap bounds
            min_wx, min_wy = float('inf'), float('inf')
            level_data_cache = {}
            for level_name in os.listdir(root_dir):
                level_path = os.path.join(root_dir, level_name)
                if not os.path.isdir(level_path): continue
                data_json = os.path.join(level_path, "data.json")
                if not os.path.exists(data_json): continue
                with open(data_json, 'r') as f:
                    data = json.load(f)
                level_data_cache[level_name] = (level_path, data)
                min_wx = min(min_wx, data["x"])
                min_wy = min(min_wy, data["y"])

            # Snap origin offset to tile boundary
            origin_x = (min_wx // TILE_SIZE) * TILE_SIZE
            origin_y = (min_wy // TILE_SIZE) * TILE_SIZE

            # Pass 2: Load levels with normalized coordinates
            tiles_loaded = 0
            for level_name, (level_path, data) in level_data_cache.items():
                world_x = data["x"] - origin_x
                world_y = data["y"] - origin_y
                level_w = data.get("width", VIEWPORT_W)
                level_h = data.get("height", VIEWPORT_H)
                level_id = data.get("identifier", level_name)
                self.levels[level_id] = LevelBounds(
                    level_id, world_x, world_y, level_w, level_h
                )

                base_tx, base_ty = world_x // TILE_SIZE, world_y // TILE_SIZE

                # Entities
                for ent_type, instances in data.get("entities", {}).items():
                    for inst in instances:
                        ent_data = {
                            "type": ent_type,
                            "x": world_x + inst["x"],
                            "y": world_y + inst["y"],
                            "source_level": level_id,
                        }
                        # Capture LDtk instance ID for persistence tracking
                        if "iid" in inst:
                            ent_data["iid"] = inst["iid"]
                        # Capture custom fields (nested in LDtk simplified export)
                        # Normalize string enum values to lowercase (INT-03, D-01, D-02)
                        for key, val in inst.get("customFields", {}).items():
                            if isinstance(val, str):
                                ent_data[key] = val.lower()
                            else:
                                ent_data[key] = val
                        # Also capture top-level fields (width, height, etc.)
                        # Normalize string values to lowercase for direction etc.
                        for key, val in inst.items():
                            if key not in ("x", "y", "iid", "id", "layer", "color", "customFields"):
                                if isinstance(val, str):
                                    ent_data[key] = val.lower()
                                else:
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
                                    if v in _val_to_tile:
                                        # Store IntGrid int for behavior lookups
                                        self.collision_data[(tx, ty)] = v
                                        # Set visual tile from schema mapping (2x2 block)
                                        _pset_tile(self.tilemap_id, tx, ty, _val_to_tile[v])
                                        tiles_loaded += 1
                                else:
                                    # Set visual tilemap for standard tile layers (2x2 block)
                                    _pset_tile(self.tilemap_id, tx, ty, (v % TILES_PER_ROW, v // TILES_PER_ROW))
                                    tiles_loaded += 1
                            except: continue
            
            print(f"LDtk Load: {tiles_loaded} tiles across levels.")
            return True
        except Exception as e:
            print(f"Error loading LDtk simplified map: {e}")
            return False

    def load_autotiles_from_ldtk(self, ldtk_path):
        """Load autoLayerTiles from full LDtk project file into Pyxel tilemap.

        Overwrites visual tiles set by load_from_ldtk_simplified with proper
        auto-tile visuals (edges, corners, variation). Collision data in
        self.collision_data is NOT modified. (TILE-04, D-15, D-16)

        Args:
            ldtk_path: Path to the full LDtk project JSON file (e.g. assets/output.ldtk).

        Returns:
            int: Number of tiles loaded, or 0 on failure.
        """
        import json
        import os
        if not os.path.exists(ldtk_path):
            print(f"LDtk file not found: {ldtk_path}")
            return 0

        try:
            with open(ldtk_path, 'r') as f:
                data = json.load(f)

            levels = data["levels"]
            grid_size = TILE_SIZE  # 16px tile grid (migrated in 21-01)

            # Origin normalization -- same pattern as load_from_ldtk_simplified
            min_wx = min(lv["worldX"] for lv in levels)
            min_wy = min(lv["worldY"] for lv in levels)
            origin_x = (min_wx // grid_size) * grid_size
            origin_y = (min_wy // grid_size) * grid_size

            tiles_loaded = 0
            for level in levels:
                world_x = level["worldX"] - origin_x
                world_y = level["worldY"] - origin_y

                for layer in level.get("layerInstances", []):
                    for tile in layer.get("autoLayerTiles", []):
                        # Skip transparent tiles (D-03)
                        if tile.get("a", 1) == 0:
                            continue

                        # px is level-local pixel coords, convert to world tile coords
                        px_x = world_x + tile["px"][0]
                        px_y = world_y + tile["px"][1]
                        tx = px_x // grid_size
                        ty = px_y // grid_size

                        # src is tileset pixel coords, convert to tile coords
                        u = tile["src"][0] // grid_size
                        v = tile["src"][1] // grid_size

                        _pset_tile(self.tilemap_id, tx, ty, (u, v))
                        tiles_loaded += 1

            print(f"AutoTiles: {tiles_loaded} tiles loaded from {ldtk_path}")
            return tiles_loaded
        except Exception as e:
            print(f"Error loading autoLayerTiles: {e}")
            return 0

    def get_level_bounds_list(self):
        """Return all LevelBounds as a list for WorldManager initialization."""
        return list(self.levels.values())

    def is_solid(self, tx, ty):
        """Returns True if the tile at (tx, ty) is solid (collision behavior from schema)."""
        _ensure_schema_cache()
        tile = self.collision_data.get((tx, ty))
        return tile in _solid_values

    def is_hazard(self, tx, ty):
        """Returns True if the tile at (tx, ty) is a hazard (damage behavior from schema)."""
        _ensure_schema_cache()
        return self.collision_data.get((tx, ty)) in _hazard_values

    def is_destructible(self, tx, ty):
        """Returns True if the tile at (tx, ty) is destructible (from schema)."""
        _ensure_schema_cache()
        tile = self.collision_data.get((tx, ty))
        return tile in _destructible_values

    def is_switch(self, tx, ty):
        """Returns True if the tile at (tx, ty) is interactive (from schema)."""
        _ensure_schema_cache()
        return self.collision_data.get((tx, ty)) in _interactive_values

    def is_cracked(self, tx, ty):
        """Returns True if the tile is any type of cracked block."""
        tile = self.collision_data.get((tx, ty))
        return tile in (11, 12)  # IntGrid cracked_h and cracked_v

    def is_cracked_horizontal(self, tx, ty):
        """Returns True if the tile is a horizontal cracked block (ABL-01)."""
        return self.collision_data.get((tx, ty)) == 11  # IntGrid cracked_h

    def is_cracked_vertical(self, tx, ty):
        """Returns True if the tile is a vertical cracked block (ABL-02)."""
        return self.collision_data.get((tx, ty)) == 12  # IntGrid cracked_v

    def get_tile(self, tx, ty):
        """Returns the IntGrid int from collision data, or (u,v) tuple from tilemap."""
        # Preference to logic tiles for markers
        if (tx, ty) in self.collision_data:
            return self.collision_data[(tx, ty)]
        return _pget_tile(self.tilemap_id, tx, ty)

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
        """Returns the zone hazard IntGrid int overlapping the AABB, or None.
        Checks water(6)/acid(7)/lava(8) zone hazard tiles (NOT spike hazards).
        If multiple zone types overlap, returns the one with highest drain rate."""
        _ensure_schema_cache()
        x1 = int(x // TILE_SIZE)
        y1 = int(y // TILE_SIZE)
        x2 = int((x + width - 1) // TILE_SIZE)
        y2 = int((y + height - 1) // TILE_SIZE)
        worst = None
        for ty in range(y1, y2 + 1):
            for tx in range(x1, x2 + 1):
                tile = self.collision_data.get((tx, ty))
                if tile in _zone_hazard_values:
                    if worst is None or HAZARD_DRAIN_RATES[tile] > HAZARD_DRAIN_RATES.get(worst, 0):
                        worst = tile
        return worst

    def remove_tile(self, tx, ty):
        """Clears the tile at (tx, ty) from both visual and collision data."""
        if (tx, ty) in self.collision_data:
            del self.collision_data[(tx, ty)]
        _pset_tile(self.tilemap_id, tx, ty, TILE_EMPTY)

    def restore_tile(self, tx, ty, tile_data):
        """Restore a previously removed tile (for block regeneration).

        Args:
            tx, ty: Tile coordinates.
            tile_data: The IntGrid int value to restore (e.g., 3 for destructible).
        """
        self.collision_data[(tx, ty)] = tile_data
        _ensure_schema_cache()
        visual = _val_to_tile.get(tile_data, TILE_EMPTY)
        _pset_tile(self.tilemap_id, tx, ty, visual)

    def find_tile(self, u, v, width=256, height=256):
        """Scans both collision and visual data for a specific tile."""
        # 1. Scan collision data
        for (tx, ty), tile in self.collision_data.items():
            if tile == (u, v):
                return (tx, ty)
        
        # 2. Scan tilemap (16px tile coords)
        for ty in range(height):
            for tx in range(width):
                if _pget_tile(self.tilemap_id, tx, ty) == (u, v):
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
            _clear_tilemap(self.tilemap_id)
            
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
                        _pset_tile(self.tilemap_id, tx, ty, (u, v))

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
                # Assumes TILES_PER_ROW tiles per row in Image 0 (256px / TILE_SIZE)
                real_id = tile_id - 1
                u = real_id % TILES_PER_ROW
                v = real_id // TILES_PER_ROW
                tx = i % width
                ty = i // width

                _pset_tile(self.tilemap_id, tx, ty, (u, v))
            return True
        except Exception as e:
            print(f"Error loading Tiled map: {e}")
            return False
