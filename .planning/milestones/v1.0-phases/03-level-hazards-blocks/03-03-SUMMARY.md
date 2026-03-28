# SUMMARY: 03-03 Destructible Blocks & Drill Interaction

## Completed Tasks
- [x] Task 1: Detect Destructible Tiles on Impact (Update `Player.move_and_collide`)
- [x] Task 2: Tile Removal in LevelMap (Implement `LevelMap.remove_tile`)
- [x] Task 3: Juice Refund Logic (Refill juice on block break)

## Key Changes
- **src/core/constants.py**: Added `DRILL_BLOCK_REFUND`.
- **src/level/map.py**: Added `TILE_EMPTY` to imports and implemented `remove_tile(tx, ty)`.
- **src/entities/player.py**:
  - Added `on_block_break()` placeholder.
  - Updated `move_and_collide` to check for destructible tiles when in `DIVING` state.
  - Implemented logic to remove tile, refund juice, and continue DIVING through the block.
- **tests/test_destruction.py**: Created new tests for destruction and juice refund logic.

## Verification
- **Automated Tests**: `tests/test_destruction.py` passed (2 tests).
- **Regression Tests**: All existing physics, slime, hazard, and map identification tests passed.
- **Manual Verification**: Ready for final integrated test in main loop.

## Decisions/Notes
- **DIVING continuity**: Chose to NOT stop DIVING when a destructible block is hit, allowing the player to "drill through" multiple blocks if they have juice. This feels more satisfying and aligns with the "Drill Dive" concept.
- **Juice Refund**: Added `DRILL_BLOCK_REFUND` to balance the `DRILL_IMPACT_COST` (though impact cost only triggers on solid ground, the dive itself consumes juice over time and activation).

## Next Steps
- 03-04-PLAN: Juice Polish & Final Verification
