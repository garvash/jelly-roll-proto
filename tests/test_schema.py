"""Tests for unified entity-schema.json (SCHEMA-01, SCHEMA-04, TILE-05)."""
import json
import os

# Resolve project root relative to this test file's location (tests/ -> project root).
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_schema_cache = None


def _load_schema():
    """Load and cache entity-schema.json."""
    global _schema_cache
    if _schema_cache is None:
        schema_path = os.path.join(_PROJECT_ROOT, "assets", "entity-schema.json")
        with open(schema_path) as f:
            _schema_cache = json.load(f)
    return _schema_cache


def test_schema_version_is_1_0_0():
    """Schema version bumped to 1.0.0 for unified tile+entity schema."""
    schema = _load_schema()
    assert schema["version"] == "1.0.0"


def test_schema_has_biomes_key():
    """Schema contains a 'biomes' top-level key."""
    schema = _load_schema()
    assert "biomes" in schema


def test_schema_has_tiles_and_entities():
    """Schema contains both 'biomes' (tiles) and 'entities' keys (SCHEMA-01)."""
    schema = _load_schema()
    assert "biomes" in schema, "Missing 'biomes' key"
    assert "entities" in schema, "Missing 'entities' key"


def test_schema_biome_covers_all_intgrid_values():
    """Every active IntGrid value has a tile_coords entry in cavern biome (SCHEMA-04).

    Values '0' (empty) and '4' (deprecated) are excluded per D-16.
    """
    schema = _load_schema()
    excluded = {"0", "4"}
    intgrid_keys = set(schema["intgrid"]["values"].keys()) - excluded
    tile_coords = schema["biomes"]["cavern"]["tile_coords"]
    # Filter out description key
    tile_keys = {k for k in tile_coords if k != "description"}
    missing = intgrid_keys - tile_keys
    assert not missing, f"IntGrid values missing from tile_coords: {missing}"
    # D-16: excluded values must NOT appear
    for excl in excluded:
        assert excl not in tile_coords, f"Value '{excl}' must not be in tile_coords (D-16)"


def test_cavern_tile_coords_are_col_row_pairs():
    """Each tile_coords entry is a 2-element list of non-negative integers (D-04)."""
    schema = _load_schema()
    tile_coords = schema["biomes"]["cavern"]["tile_coords"]
    for key, val in tile_coords.items():
        if key == "description":
            continue
        assert isinstance(val, list), f"tile_coords[{key}] is not a list"
        assert len(val) == 2, f"tile_coords[{key}] has {len(val)} elements, expected 2"
        assert all(isinstance(v, int) and v >= 0 for v in val), (
            f"tile_coords[{key}] = {val} -- values must be non-negative integers"
        )


def test_cavern_tileset_path_in_schema():
    """Cavern biome tileset path points to assets/tilesets/cavern.png (D-07/D-08)."""
    schema = _load_schema()
    assert schema["biomes"]["cavern"]["tileset"] == "assets/tilesets/cavern.png"


def test_cavern_tileset_exists():
    """The cavern tileset PNG file exists on disk."""
    schema = _load_schema()
    tileset_path = schema["biomes"]["cavern"]["tileset"]
    full_path = os.path.join(_PROJECT_ROOT, tileset_path)
    assert os.path.exists(full_path), f"Tileset not found: {full_path}"


def test_cavern_layers_structure():
    """Cavern biome has 2 layers, each with name/tilemap/z/scroll keys (TILE-05)."""
    schema = _load_schema()
    layers = schema["biomes"]["cavern"]["layers"]
    assert len(layers) == 2, f"Expected 2 layers, got {len(layers)}"
    required_keys = {"name", "tilemap", "z", "scroll"}
    for i, layer in enumerate(layers):
        missing = required_keys - set(layer.keys())
        assert not missing, f"Layer {i} missing keys: {missing}"


def test_cavern_layer_values():
    """Layer 0 is bg (tilemap 1, z -1, scroll 0.5), layer 1 is terrain (D-10)."""
    schema = _load_schema()
    layers = schema["biomes"]["cavern"]["layers"]
    # Background layer
    bg = layers[0]
    assert bg["name"] == "bg", f"layers[0] name is '{bg['name']}', expected 'bg'"
    assert bg["tilemap"] == 1
    assert bg["z"] == -1
    assert bg["scroll"] == 0.5
    # Terrain layer
    terrain = layers[1]
    assert terrain["name"] == "terrain", f"layers[1] name is '{terrain['name']}', expected 'terrain'"
    assert terrain["tilemap"] == 0
    assert terrain["z"] == 0
    assert terrain["scroll"] == 1.0


def test_existing_sections_unchanged():
    """All pre-existing top-level sections still present (Pitfall 3 guard)."""
    schema = _load_schema()
    required_sections = [
        "converter_mapping",
        "entities",
        "intgrid",
        "pivot_convention",
        "simplified_export",
    ]
    for section in required_sections:
        assert section in schema, f"Missing existing section: '{section}'"
