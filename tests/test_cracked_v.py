"""Verify CRACKED_V vertical gate breaking via Drill Dive (ABL-02).

Updated in Plan 31.5-05 (sympathetic regression sweep per RESEARCH Risk 5):
the Slime Boost ability was stripped in Plans 01 + 03; surviving CRACKED_V
opener is Drill Dive only. Tests asserting boost-through-gate behavior were
removed because the behavior no longer exists post-strip.
"""
import unittest


class TestCrackedVBreaking(unittest.TestCase):
    def test_constants_has_drill_cracked_v_cost(self):
        """DRILL_CRACKED_V_COST constant exists for juice cost on drill-through-gate."""
        from src.core.constants import DRILL_CRACKED_V_COST
        self.assertIsNotNone(DRILL_CRACKED_V_COST)

    # test_constants_has_boost_cracked_v_cost deleted in Plan 31.5-05:
    # BOOST_CRACKED_V_COST stripped from gates group in Plan 03 per CONTEXT D-02.

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
        """Drill collision passes actual tile_type to on_block_destroyed (not hardcoded).

        Phase 32 D-10 / Plan 05 migration: drill block-break logic moved from
        Player.move_and_collide to src/fusion/drill_dive.py::on_tick. The
        on_block_destroyed(tx, ty, tile_type) call now lives there.
        """
        with open("src/fusion/drill_dive.py") as f:
            source = f.read()
        self.assertIn("on_block_destroyed(tx, ty, tile_type)", source)

    def test_player_drill_costs_juice_for_cracked_v(self):
        """Drill Dive hitting CRACKED_V costs juice (consume, not refill).

        Phase 32 D-10 / Plan 05 migration: cost branch moved to drill_dive.py.
        """
        with open("src/fusion/drill_dive.py") as f:
            source = f.read()
        self.assertIn("DRILL_CRACKED_V_COST", source)

    # test_player_boost_checks_cracked_v deleted in Plan 31.5-05:
    # boost ceiling check stripped from player.py in Plan 01 (start_boost /
    # update_boost / end_boost methods deleted per CONTEXT D-17 sub-step 2).

    # test_player_boost_costs_juice_for_cracked_v deleted in Plan 31.5-05:
    # boost juice cost path stripped with the boost methods in Plan 01.

    def test_entity_schema_cracked_v_broken_by_drill(self):
        """Entity schema cracked_v broken_by includes drill_dive."""
        import json
        with open("assets/entity-schema.json") as f:
            schema = json.load(f)
        cracked_v = schema["intgrid"]["values"]["12"]
        self.assertIn("drill_dive", cracked_v["broken_by"])

    # test_entity_schema_cracked_v_broken_by_boost was deleted alongside the
    # boost-cost sweep above; the Phase 31.5 strip leaves drill_dive as the
    # sole CRACKED_V opener. CRACKED_H tiles become permanently solid until
    # a future level-design pass removes them (CONTEXT Deferred Idea).


if __name__ == "__main__":
    unittest.main()
