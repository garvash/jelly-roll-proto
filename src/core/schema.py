"""Schema loader for entity-schema.json (SCHEMA-02).

Module-level singleton that loads the unified schema at startup and exposes
typed lookup functions for tile coordinates, behavior sets, hazard drain
mapping, tileset path, and layer definitions.

Usage:
    from src.core import schema
    schema.init()  # call once at startup
    val_to_tile = schema.get_val_to_tile()
"""

import json
import os

_schema = None
_val_to_tile = None
_behavior_sets = None
_hazard_drain_map = None
_tileset_path = None
_layers = None

# Active biome -- hardcoded per D-11 (single biome for prototype)
_ACTIVE_BIOME = "cavern"


def init(schema_path="assets/entity-schema.json"):
    """Load schema and build all lookup structures. Call once at startup.

    Raises RuntimeError if file missing or malformed (D-02).
    """
    global _schema, _val_to_tile, _behavior_sets, _hazard_drain_map
    global _tileset_path, _layers

    if not os.path.exists(schema_path):
        raise RuntimeError(f"Schema file not found: {schema_path}")

    try:
        with open(schema_path) as f:
            _schema = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        raise RuntimeError(f"Failed to parse schema: {e}")

    _build_lookups()


def _build_lookups():
    """Build all derived lookup structures from loaded schema."""
    global _val_to_tile, _behavior_sets, _hazard_drain_map
    global _tileset_path, _layers

    biome_data = _schema["biomes"][_ACTIVE_BIOME]
    tile_coords = biome_data["tile_coords"]

    # Build val_to_tile: int -> (col, row) tuple
    _val_to_tile = {}
    for key, coords in tile_coords.items():
        if key == "description":
            continue
        _val_to_tile[int(key)] = tuple(coords)

    # Build behavior sets from intgrid.values
    _behavior_sets = {
        "collision": set(),
        "destructible": set(),
        "damage": set(),
        "zone_hazard": set(),
        "interactive": set(),
    }
    for key, entry in _schema["intgrid"]["values"].items():
        val = int(key)
        behavior = entry.get("behavior", "none")
        if behavior == "none":
            continue
        for part in behavior.split("+"):
            if part in _behavior_sets:
                _behavior_sets[part].add(val)

    # Build hazard drain map: IntGrid int -> drain speed string
    _hazard_drain_map = {}
    for key, entry in _schema["intgrid"]["values"].items():
        if "drain" in entry:
            _hazard_drain_map[int(key)] = entry["drain"]

    # Tileset path and layer definitions
    _tileset_path = biome_data["tileset"]
    _layers = biome_data["layers"]


def _check_init():
    """Guard: raise if init() has not been called."""
    if _schema is None:
        raise RuntimeError("schema.init() must be called before accessing schema data")


def get_val_to_tile():
    """Return IntGrid value -> (col, row) tile coordinate mapping.

    Returns:
        dict[int, tuple[int, int]]: Maps IntGrid values to tileset coordinates.
    """
    _check_init()
    return _val_to_tile


def get_solid_values():
    """Return set of IntGrid values with 'collision' behavior.

    Returns:
        set[int]: IntGrid values that are solid (block movement).
    """
    _check_init()
    return _behavior_sets["collision"]


def get_hazard_values():
    """Return set of IntGrid values with 'damage' behavior.

    Returns:
        set[int]: IntGrid values that deal contact damage.
    """
    _check_init()
    return _behavior_sets["damage"]


def get_zone_hazard_values():
    """Return set of IntGrid values with 'zone_hazard' behavior.

    Returns:
        set[int]: IntGrid values for passable hazard zones (water/acid/lava).
    """
    _check_init()
    return _behavior_sets["zone_hazard"]


def get_destructible_values():
    """Return set of IntGrid values with 'destructible' behavior.

    Returns:
        set[int]: IntGrid values that can be broken by abilities.
    """
    _check_init()
    return _behavior_sets["destructible"]


def get_interactive_values():
    """Return set of IntGrid values with 'interactive' behavior.

    Returns:
        set[int]: IntGrid values for switches and other interactables.
    """
    _check_init()
    return _behavior_sets["interactive"]


def get_hazard_drain_map():
    """Return IntGrid value -> drain speed string mapping.

    Returns:
        dict[int, str]: Maps zone hazard IntGrid values to drain speed
            strings ("slow", "medium", "fast").
    """
    _check_init()
    return _hazard_drain_map


def get_tileset_path():
    """Return active biome tileset PNG path.

    Returns:
        str: Relative path to the tileset image file.
    """
    _check_init()
    return _tileset_path


def get_layers():
    """Return active biome layer definitions.

    Returns:
        list[dict]: Layer objects with name, tilemap, z, scroll keys.
    """
    _check_init()
    return _layers
