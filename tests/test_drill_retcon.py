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

    def test_drill_activation_uses_jump_button(self):
        """Drill Dive activation uses 'jump' action with DOWN held (D-12 remap)."""
        with open("src/entities/player.py") as f:
            source = f.read()
        # The drill activation should be in the jump button block (D-12 remap)
        lines = source.split('\n')
        found_drill_in_jump_block = False
        for i, line in enumerate(lines):
            if 'has_drill' in line and 'btn("down")' in line:
                context = '\n'.join(lines[max(0, i - 5):i + 1])
                if 'btnp("jump")' in context:
                    found_drill_in_jump_block = True
        self.assertTrue(found_drill_in_jump_block,
            "Drill activation should use jump button with DOWN held (D-12)")

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
