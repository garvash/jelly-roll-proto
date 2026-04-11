# Codebase Structure

**Analysis Date:** 2026-03-18

## Directory Layout

```
jelly-roll-proto/
├── assets/         # Game resources (images, tilemaps, sounds)
│   ├── cave/       # LDtk simplified export directory
│   ├── cave.ldtk   # LDtk project file
│   ├── game.pyxres # Pyxel resource file
│   ├── map_data.csv# Exported map data
│   └── tileset.png # Raw sprite sheet
├── src/            # Core source code
│   ├── core/       # Global constants and shared logic
│   ├── entities/   # Object-oriented game entity implementations
│   └── level/      # Map loading and physics query abstractions
├── tests/          # Python test suite
├── main.py         # Primary entry point
├── build_web.ps1   # PowerShell script for web deployment
└── requirements.txt# Python dependencies
```

## Directory Purposes

**assets/:**
- Purpose: Stores all binary and data-driven game assets.
- Contains: Images, Pyxel resources, and map project files (LDtk/Tiled).
- Key files: `assets/game.pyxres`, `assets/cave.ldtk`.

**src/core/:**
- Purpose: Shared configuration and system constants.
- Contains: Global physics values, tile type identifiers, and UI settings.
- Key files: `src/core/tuning.py` (loads `assets/physics-schema.json` at import and exposes flat PEP 562 access like `tuning.GRAVITY`), `src/core/constants.py` (passthrough compat shim that re-exports `tuning.*` for legacy import-site callers).

**src/entities/:**
- Purpose: Logic for all game objects that exist in the world.
- Contains: Player movement, AI logic for enemies, item collection, and visual effects.
- Key files: `src/entities/player.py`, `src/entities/slime.py`.

**src/level/:**
- Purpose: Abstraction layer between raw map data and the game logic.
- Contains: Code for parsing map files and performing collision/spatial queries.
- Key files: `src/level/map.py`.

**tests/:**
- Purpose: Automated verification of game mechanics and logic.
- Contains: Unit tests for physics, boss behavior, and level loading.
- Key files: `tests/test_physics.py`, `tests/test_health.py`.

## Key File Locations

**Entry Points:**
- `main.py`: The starting script for the game application.

**Configuration:**
- `assets/physics-schema.json` (v0.3.x): Single source of truth for tuning values. `tuning.*` holds raw game inputs grouped by system; `derived.*` holds converter-facing computed values.
- `src/core/tuning.py`: Loads the schema at boot, exposes flat attribute access (`tuning.GRAVITY`), and provides the mutation/save API used by the live-tuning panel.
- `src/core/constants.py`: Passthrough compat shim — `from src.core.constants import GRAVITY` still works via `from src.core.tuning import *`.

**Core Logic:**
- `src/entities/player.py`: Primary player controller and state management.
- `src/entities/slime.py`: Slime companion logic and interaction mechanics.
- `src/level/map.py`: World representation and physics query API.

**Testing:**
- `tests/`: All test files are centralized here.

## Naming Conventions

**Files:**
- Snake Case: `player.py`, `level_map.py`, `test_physics.py`.

**Directories:**
- Snake Case: `src/entities/`, `src/core/`.

**Classes:**
- Pascal Case: `Player`, `Slime`, `LevelMap`, `Snail`.

**Variables/Functions:**
- Snake Case: `update_state()`, `check_collision()`, `hp`, `facing_right`.

## Where to Add New Code

**New Feature (e.g., a new mechanic):**
- Primary code: Within a relevant entity in `src/entities/` or as a new file in `src/entities/`.
- Tests: A corresponding test file in `tests/`.

**New Component/Module:**
- Implementation: Create a new file in the appropriate `src/` subdirectory (e.g., `src/entities/` for game objects, `src/core/` for new shared systems).

**Utilities:**
- Shared helpers: Should be placed in `src/core/` if they are truly global.

**New Assets:**
- Place raw assets (PNGs, LDtk files) in `assets/` and reference them in `main.py` or `src/level/map.py`.

## Special Directories

**tests/:**
- Purpose: Contains automated tests for the codebase.
- Generated: No.
- Committed: Yes.

**.venv/:**
- Purpose: Local Python virtual environment.
- Generated: Yes.
- Committed: No (listed in `.gitignore`).

---

*Structure analysis: 2025-01-24*
