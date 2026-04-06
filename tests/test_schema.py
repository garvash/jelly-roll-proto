"""Tests for unified entity-schema.json (SCHEMA-01, SCHEMA-04, TILE-05)
and schema.py module (SCHEMA-02)."""
import json
import os

import pytest

from src.core import schema

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
    """Cavern biome tileset path points to assets/tiles.png (updated in 19-01)."""
    schema = _load_schema()
    assert schema["biomes"]["cavern"]["tileset"] == "assets/tiles.png"


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


# ---------------------------------------------------------------------------
# Phase 18 — schema.py module tests (SCHEMA-02)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=False)
def schema_loaded():
    """Load schema before each schema.py API test."""
    schema.init("assets/entity-schema.json")
    return schema


def test_schema_init_loads(schema_loaded):
    """After schema.init(), get_val_to_tile() returns a non-empty dict."""
    result = schema_loaded.get_val_to_tile()
    assert result is not None
    assert len(result) > 0


def test_val_to_tile_from_schema(schema_loaded):
    """get_val_to_tile() maps IntGrid values to correct (col, row) tuples."""
    expected = {
        1: (0, 1),
        2: (1, 1),
        3: (2, 1),
        5: (5, 1),
        6: (9, 1),
        7: (10, 1),
        8: (11, 1),
        11: (7, 1),
        12: (8, 1),
    }
    result = schema_loaded.get_val_to_tile()
    assert result == expected


def test_behavior_sets(schema_loaded):
    """Behavior sets correctly derived from schema behavior strings."""
    assert schema_loaded.get_solid_values() == {1, 3, 11, 12}
    assert schema_loaded.get_hazard_values() == {2}
    assert schema_loaded.get_destructible_values() == {3, 11, 12}
    assert schema_loaded.get_zone_hazard_values() == {6, 7, 8}
    assert schema_loaded.get_interactive_values() == {5}


def test_compound_behavior(schema_loaded):
    """IntGrid 3 (collision+destructible) appears in BOTH solid and destructible sets."""
    assert 3 in schema_loaded.get_solid_values()
    assert 3 in schema_loaded.get_destructible_values()


def test_missing_schema_crashes():
    """schema.init() with nonexistent path raises RuntimeError."""
    with pytest.raises(RuntimeError):
        schema.init("nonexistent_path.json")


def test_tileset_path(schema_loaded):
    """get_tileset_path() returns cavern biome tileset path."""
    assert schema_loaded.get_tileset_path() == "assets/tiles.png"


def test_layers(schema_loaded):
    """get_layers() returns 2 layers with correct names and scroll values."""
    layers = schema_loaded.get_layers()
    assert len(layers) == 2
    assert layers[0]["name"] == "bg"
    assert layers[0]["scroll"] == 0.5
    assert layers[1]["name"] == "terrain"
    assert layers[1]["scroll"] == 1.0


def test_hazard_drain_map(schema_loaded):
    """get_hazard_drain_map() returns IntGrid value to drain string mapping."""
    assert schema_loaded.get_hazard_drain_map() == {6: "slow", 7: "medium", 8: "fast"}


# ---------------------------------------------------------------------------
# Phase 18 Plan 03 — schema mutation & converter contract tests (SCHEMA-02, SCHEMA-03)
# ---------------------------------------------------------------------------

def test_schema_mutation():
    """Changing tile_coords in schema changes lookup result (Success Criterion 3, D-17).

    Proves the schema-driven system is truly dynamic: modify the data file,
    re-init, and the game's tile coordinate lookup reflects the change.
    """
    import tempfile
    import shutil

    # Load the real schema data
    with open(os.path.join(_PROJECT_ROOT, "assets", "entity-schema.json")) as f:
        data = json.load(f)

    # Mutate: IntGrid 1 (solid) coords from [0, 1] to [5, 5]
    data["biomes"]["cavern"]["tile_coords"]["1"] = [5, 5]

    # Write mutated schema to temp file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, dir=_PROJECT_ROOT
    ) as tmp:
        json.dump(data, tmp)
        tmp_path = tmp.name

    try:
        schema.init(tmp_path)
        result = schema.get_val_to_tile()
        assert result[1] == (5, 5), (
            f"Mutation not reflected: expected (5, 5), got {result[1]}"
        )
    finally:
        os.unlink(tmp_path)
        # Re-init with real schema so other tests are unaffected
        schema.init(os.path.join(_PROJECT_ROOT, "assets", "entity-schema.json"))


def test_converter_contract_sections():
    """Schema contains all sections needed by pml-to-ldtk converter (SCHEMA-03 partial).

    Note: This verifies the game-side contract -- that entity-schema.json
    contains converter_mapping, intgrid, entities, and simplified_export sections.
    Actual converter code consuming these sections is in the separate pml-to-ldtk
    repo and deferred per D-14.
    """
    with open(os.path.join(_PROJECT_ROOT, "assets", "entity-schema.json")) as f:
        data = json.load(f)
    assert "converter_mapping" in data, "Missing converter_mapping section"
    assert "intgrid" in data, "Missing intgrid section"
    assert "values" in data["intgrid"], "Missing intgrid.values"
    assert "entities" in data, "Missing entities section"
    assert "simplified_export" in data, "Missing simplified_export section"



def test_no_hardcoded_tile_constants():
    """Constants.py should not contain TILE_SOLID/TILE_HAZARD etc. after Plan 02."""
    constants_path = os.path.join(_PROJECT_ROOT, "src", "core", "constants.py")
    with open(constants_path) as f:
        source = f.read()
    forbidden = [
        "TILE_SOLID", "TILE_HAZARD", "TILE_DESTRUCTIBLE", "TILE_SWITCH",
        "TILE_CRACKED_H", "TILE_CRACKED_V", "TILE_WATER", "TILE_ACID", "TILE_LAVA",
    ]
    found = [name for name in forbidden if name in source]
    assert not found, f"Hardcoded tile constants still present: {found}"
