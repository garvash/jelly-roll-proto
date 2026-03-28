"""Verify drill dive retcon and DASH_PICKUP replacement (D-22, D-23)."""
import unittest


class TestDrillRetcon(unittest.TestCase):
    def test_no_drill_item_type(self):
        """DRILL item type replaced by DASH_PICKUP (D-23)."""
        with open("src/entities/items.py") as f:
            source = f.read()
        # Should not have DRILL as item_type check
        self.assertNotIn('"DRILL"', source)
        self.assertIn('"DASH_PICKUP"', source)

    def test_drill_activation_uses_dash_button(self):
        """Drill Dive activation uses 'dash' action, not 'jump' (D-22)."""
        with open("src/entities/player.py") as f:
            source = f.read()
        # The drill activation should be in the dash button block
        # There should be no DOWN+jump drill activation pattern
        lines = source.split('\n')
        for i, line in enumerate(lines):
            if 'has_drill' in line and 'DIVING' not in line:
                # Check nearby lines don't use btnp("jump") for drill
                context = '\n'.join(lines[max(0, i - 3):i + 3])
                self.assertNotIn('btnp("jump")', context,
                    "Drill activation should use dash button, not jump")

    def test_dash_pickup_grants_has_dash(self):
        """DASH_PICKUP item sets player.has_dash = True."""
        with open("src/entities/items.py") as f:
            source = f.read()
        self.assertIn("has_dash", source)

    def test_entity_schema_uses_dash_pickup(self):
        """Entity schema uses DashPickup instead of Drill (D-23)."""
        import json
        with open("assets/entity-schema.json") as f:
            schema = json.load(f)
        self.assertIn("DashPickup", schema["entities"])
        self.assertNotIn("Drill", schema["entities"])

    def test_main_spawns_dash_pickup(self):
        """main.py spawns DashPickup entities, not Drill."""
        with open("main.py") as f:
            source = f.read()
        self.assertIn('"DashPickup"', source)
        self.assertNotIn('"Drill"', source)


if __name__ == "__main__":
    unittest.main()
