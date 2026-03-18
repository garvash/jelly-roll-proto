# Codebase Concerns

**Analysis Date:** 2026-03-18

## Tech Debt

**LevelMap "God Object":**
- Issue: The `LevelMap` class handles level loading from multiple formats (Tiled, LDtk JSON, LDtk Simplified), collision detection, tile state (gates, switches), and entity metadata.
- Files: `src/level/map.py`
- Impact: Hard to maintain, complex initialization, and redundant code for different map formats.
- Fix approach: Separate map loading into a dedicated `LevelLoader` or `MapParser` hierarchy. Delegate entity spawning to a `Spawner` service.

**Duplicated Movement Logic:**
- Issue: Collision and movement logic (AABB vs tiles) is manually implemented and duplicated across `Player`, `Slime`, and `Enemies`.
- Files: `src/entities/player.py`, `src/entities/slime.py`, `src/entities/enemies.py`
- Impact: Bug fixes in collision must be applied in multiple places. Inconsistent behavior between entities.
- Fix approach: Extract common physics and collision logic into a `PhysicsBody` or `Movement` mixin/component.

**Asset Injection in Game Reset:**
- Issue: The `Game.reset()` method manually injects explosion sprites into `pyxel.images[1]` using `pset` loops.
- Files: `main.py`
- Impact: Visual assets are partially defined in code instead of asset files. Makes editing sprites difficult.
- Fix approach: Move these sprites into the `assets/game.pyxres` file or a dedicated asset generation script.

**Mixed UI and Game Logic:**
- Issue: `Game.draw()` contains both high-level rendering orchestration and low-level UI drawing (Health bar, Victory text).
- Files: `main.py`
- Impact: Difficult to theme or modify the UI without touching core game loop code.
- Fix approach: Create a `UI` or `HUD` class to handle health display and menu overlays.

## Known Bugs

**Manual Room Transition Sync:**
- Symptoms: Camera and room state (visited, enemies) are updated manually in `Game.update`.
- Files: `main.py`
- Trigger: Player crossing 128px boundaries.
- Workaround: A `pending_boss_trigger` flag is used to delay boss spawning until the player is safely inside the room.
- Fix approach: Implement a formal `RoomManager` to handle entry/exit events and state persistence.

**Tile Scanning Performance:**
- Symptoms: `LevelMap.find_tile` scans up to 256x256 tiles per call.
- Files: `src/level/map.py`
- Cause: Used for finding spawn markers and boss triggers.
- Improvement path: Index marker locations during map load instead of scanning the tilemap at runtime.

## Security Considerations

**Unprotected Asset Files:**
- Risk: Game logic relies on external JSON/CSV files which can be modified by users to cheat or break the game.
- Files: `assets/*.json`, `assets/*.csv`
- Current mitigation: None.
- Recommendations: Not a priority for a prototype, but for production, consider packing assets into a binary format or using checksums.

## Performance Bottlenecks

**Asset Reloading on Reset:**
- Problem: `pyxel.load("assets/game.pyxres")` is called every time the player dies or restarts.
- Files: `main.py`
- Cause: Used to restore the tilemap state (broken blocks, gates).
- Improvement path: Keep a "pristine" copy of the tilemap in memory and restore it without re-reading from disk, or only reset modified tiles.

## Fragile Areas

**Collision Data Desync:**
- Files: `src/level/map.py`
- Why fragile: Logic properties are stored in `collision_data` (dict) while visuals are in `pyxel.tilemaps`. Some methods (`remove_tile`) update both, but others might miss one.
- Safe modification: Always use `LevelMap.remove_tile` instead of direct `pset` to ensure consistency.
- Test coverage: Partially covered by `tests/test_destruction.py`.

**Auto-Aim Dependencies:**
- Files: `src/entities/player.py`
- Why fragile: Player input handling depends on `self.game` and its internal list of enemies to perform auto-aim.
- Safe modification: Ensure `self.game` is passed to `Player` during initialization.
- Test coverage: Gaps in testing the targeting logic itself.

## Scaling Limits

**Entity List Management:**
- Current capacity: Simple Python lists (`self.enemies`, `self.projectiles`).
- Limit: Performance may degrade with hundreds of active projectiles or particles.
- Scaling path: Implement spatial partitioning for entity lookups if entity counts increase significantly.

## Dependencies at Risk

**LDtk Simplified Export:**
- Risk: Relies on a specific LDtk export structure (`simplified/Level_X/data.json` and `IntGrid.csv`).
- Impact: Updating LDtk might break the loader if the export format changes.
- Migration plan: Move to a more robust LDtk parser or a custom binary export.

## Missing Critical Features

**Centralized Event System:**
- Problem: State changes (damage, block destruction, juice consumption) are handled by direct method calls across classes.
- Blocks: Hard to implement global effects (e.g., sound triggers, screen shake) without passing `Game` references everywhere.

## Test Coverage Gaps

**Player Unit Tests:**
- What's not tested: Complex movement states (Wall slide, Coyote time, Jump buffering).
- Files: `src/entities/player.py`
- Risk: Changes to physics constants might break "game feel" without warning.
- Priority: High.

**Level Loading Edge Cases:**
- What's not tested: Corrupt map files, missing levels in simplified export.
- Files: `src/level/map.py`
- Risk: Game crashes on startup or during room transition.
- Priority: Medium.

---

*Concerns audit: 2024-05-23*
