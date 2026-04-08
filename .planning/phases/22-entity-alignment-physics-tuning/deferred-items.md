# Deferred Items - Phase 22

## Pre-existing Test Failures (from Phase 20/21 tile migration)

These tests were already failing before Phase 22 execution. They are out of scope for this phase.

1. **test_destruction.py::test_block_destruction_and_refund** - pset coordinates shifted due to 16px tiles
2. **test_hazard_zones.py** (2 tests) - zone detection math not updated for 16px
3. **test_map_identification.py** (2 tests) - check_hazard and get_destructible_at not updated for 16px
4. **test_phase05_gaps.py** (4 tests) - Game() constructor integration tests broken by LDtk 16px migration
5. **test_phase05_nyquist.py** (2 tests) - knockback force value changed; room_spawn_update broken by LDtk
6. **test_ram.py** (2 tests) - wall snap assertions stale for 16px grid
7. **test_save_system.py** (1 test) - death timer test broken by integration changes
