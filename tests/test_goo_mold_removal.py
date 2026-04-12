"""Verify Goo-Mold (TILE_GOO_MOLD) completely removed from codebase (Phase 10 cleanup)."""
import unittest


class TestGooMoldRemoval(unittest.TestCase):
    def test_constants_no_goo_mold(self):
        """TILE_GOO_MOLD removed from constants.py."""
        with open("src/core/constants.py") as f:
            source = f.read()
        self.assertNotIn("TILE_GOO_MOLD", source)

    def test_map_no_is_goo_mold(self):
        """is_goo_mold() method removed from map.py."""
        with open("src/level/map.py") as f:
            source = f.read()
        self.assertNotIn("is_goo_mold", source)

    def test_map_is_solid_no_goo_mold(self):
        """is_solid() does not reference GOO_MOLD."""
        with open("src/level/map.py") as f:
            source = f.read()
        # Find is_solid method and check it doesn't contain GOO_MOLD
        lines = source.split('\n')
        in_is_solid = False
        for line in lines:
            if 'def is_solid' in line:
                in_is_solid = True
            elif in_is_solid and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                break
            if in_is_solid:
                self.assertNotIn("GOO_MOLD", line,
                    f"is_solid() should not reference GOO_MOLD: {line.strip()}")

    def test_map_no_goo_mold_import(self):
        """map.py does not import TILE_GOO_MOLD."""
        with open("src/level/map.py") as f:
            source = f.read()
        self.assertNotIn("TILE_GOO_MOLD", source)

    def test_entity_schema_no_goo_mold_at_10(self):
        """entity-schema.json IntGrid value 10 does not contain goo_mold."""
        import json
        with open("assets/entity-schema.json") as f:
            schema = json.load(f)
        self.assertNotIn("10", schema["intgrid"]["values"],
            "IntGrid value 10 (goo_mold) should be removed entirely")

    def test_map_no_goo_mold_reference(self):
        """map.py does not reference GOO_MOLD anywhere."""
        with open("src/level/map.py") as f:
            source = f.read()
        self.assertNotIn("GOO_MOLD", source)


if __name__ == "__main__":
    unittest.main()
