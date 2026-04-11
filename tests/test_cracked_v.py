"""Verify CRACKED_V vertical gate breaking via Drill Dive and Slime Boost (ABL-02)."""
import unittest


class TestCrackedVBreaking(unittest.TestCase):
    def test_constants_has_drill_cracked_v_cost(self):
        """DRILL_CRACKED_V_COST constant exists for juice cost on drill-through-gate."""
        from src.core.constants import DRILL_CRACKED_V_COST
        self.assertIsNotNone(DRILL_CRACKED_V_COST)

    def test_constants_has_boost_cracked_v_cost(self):
        """BOOST_CRACKED_V_COST constant exists for juice cost on boost-through-gate."""
        from src.core.constants import BOOST_CRACKED_V_COST
        self.assertIsNotNone(BOOST_CRACKED_V_COST)

    def test_map_has_get_cracked_v_at(self):
        """LevelMap has get_cracked_v_at() method for vertical gate detection."""
        with open("src/level/map.py") as f:
            source = f.read()
        self.assertIn("def get_cracked_v_at", source)

    def test_player_uses_intgrid_cracked_v(self):
        """player.py uses INTGRID_CRACKED_V for drill collision branching."""
        with open("src/entities/player.py") as f:
            source = f.read()
        self.assertIn("INTGRID_CRACKED_V", source)

    def test_player_drill_uses_actual_tile_type(self):
        """Drill collision passes actual tile_type to on_block_destroyed (not hardcoded)."""
        with open("src/entities/player.py") as f:
            source = f.read()
        # The on_block_destroyed call near DIVING should use tile_type, not TILE_DESTRUCTIBLE
        self.assertIn("on_block_destroyed(tx, ty, tile_type)", source)

    def test_player_drill_costs_juice_for_cracked_v(self):
        """Drill Dive hitting CRACKED_V costs juice (consume, not refill)."""
        with open("src/entities/player.py") as f:
            source = f.read()
        self.assertIn("DRILL_CRACKED_V_COST", source)

    def test_player_boost_checks_cracked_v(self):
        """Boost ceiling collision checks for CRACKED_V before snapping."""
        with open("src/entities/player.py") as f:
            source = f.read()
        self.assertIn("get_cracked_v_at", source)

    def test_player_boost_costs_juice_for_cracked_v(self):
        """Boost breaking CRACKED_V costs juice."""
        with open("src/entities/player.py") as f:
            source = f.read()
        self.assertIn("BOOST_CRACKED_V_COST", source)

    def test_entity_schema_cracked_v_broken_by_boost(self):
        """Entity schema cracked_v broken_by includes slime_boost."""
        import json
        with open("assets/entity-schema.json") as f:
            schema = json.load(f)
        cracked_v = schema["intgrid"]["values"]["12"]
        self.assertIn("slime_boost", cracked_v["broken_by"])

    def test_entity_schema_cracked_v_broken_by_drill(self):
        """Entity schema cracked_v broken_by includes drill_dive."""
        import json
        with open("assets/entity-schema.json") as f:
            schema = json.load(f)
        cracked_v = schema["intgrid"]["values"]["12"]
        self.assertIn("drill_dive", cracked_v["broken_by"])


if __name__ == "__main__":
    unittest.main()
