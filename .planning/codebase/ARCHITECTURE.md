# Architecture

**Analysis Date:** 2026-03-18

## Pattern Overview

**Overall:** Main Game Loop (Update/Draw)

**Key Characteristics:**
- **Centralized Orchestration:** The `Game` class in `main.py` manages the initialization, asset loading, and the main lifecycle (update/draw) of all game components.
- **State-Based Entity Logic:** Entities (Player, Slime, Enemies) maintain internal state machines (e.g., `Player.state` for IDLE, RUNNING, DIVING) to manage complex behaviors.
- **Decoupled Physics & Level Data:** Physics and collision logic are abstracted into the `LevelMap` class, which handles various map formats (LDtk, Tiled) and provides spatial queries.

## Layers

**Entry Point Layer:**
- Purpose: Initialize the Pyxel engine, load resources, and run the main game loop.
- Location: `main.py`
- Contains: `Game` class.
- Depends on: `src/level/`, `src/entities/`, `src/core/`.
- Used by: Python interpreter (direct execution).

**Entity Layer:**
- Purpose: Houses the logic for all interactive objects in the game world.
- Location: `src/entities/`
- Contains: `player.py`, `slime.py`, `enemies.py`, `boss.py`, `items.py`, `projectile.py`, `effects.py`.
- Depends on: `src/level/` for collision detection and `src/core/` for physics constants.
- Used by: `main.py` (Game loop calls).

**Level/Infrastructure Layer:**
- Purpose: Manages world data, tilemaps, and spatial queries (collisions/hazards).
- Location: `src/level/`
- Contains: `map.py` (`LevelMap` class).
- Depends on: `src/core/` for tile type definitions.
- Used by: `main.py` and `src/entities/`.

**Core/Shared Layer:**
- Purpose: Load and expose global tuning values from `assets/physics-schema.json`.
- Location: `src/core/`
- Contains: `tuning.py` (schema loader + mutation/save API), `constants.py` (passthrough compat shim over `tuning.*`).
- Depends on: `assets/physics-schema.json`.
- Used by: Entire codebase.

## Data Flow

**Update Cycle:**

1. `Game.update()` captures global input (e.g., Quit, Restart).
2. Camera and room transitions are calculated based on Player position.
3. `Player.update()` handles input, movement, and interaction with `Slime`.
4. `Slime.update()` processes its own physics and juice consumption/regeneration.
5. `Enemies.update()` and `Boss.update()` process AI and collision with projectiles/player.
6. `LevelMap` provides collision results to all moving entities.
7. Secondary entities (Projectiles, Items, Effects) are updated and cleaned up if inactive.

**State Management:**
- **Game State:** Managed in `main.py` (e.g., `PLAYING`, `WON`).
- **Entity State:** Managed within individual entity classes (e.g., `Player.state`).
- **World State:** Managed in `LevelMap` (e.g., `locked_gates`, `collision_data`).

## Key Abstractions

**Entity Interface:**
- Purpose: Implicit interface for objects that can be updated and drawn.
- Examples: `src/entities/player.py`, `src/entities/enemies.py`.
- Pattern: Objects with `update(...)` and `draw()` methods.

**LevelMap:**
- Purpose: Provides a high-level API for interacting with the game world.
- Examples: `src/level/map.py`.
- Pattern: Repository/Data Access for tile data and collision queries.

## Entry Points

**Main Game Entry:**
- Location: `main.py`
- Triggers: User execution of the script.
- Responsibilities: Engine initialization, asset loading, state reset, and starting the `pyxel.run` loop.

## Error Handling

**Strategy:** Mostly implicit, with specific handlers for external resource loading.

**Patterns:**
- **Resource Loading Guard:** `try-except` blocks in `LevelMap` (`load_from_ldtk`, `load_from_tiled`) to prevent crashes on missing or malformed assets.
- **Defensive Entity Access:** Using `next((... for ...), None)` to safely find entities in the map data.

## Cross-Cutting Concerns

**Logging:** Basic console logging (`print`) for map loading events and debugging.
**Validation:** AABB (Axis-Aligned Bounding Box) collision detection against tile grids and between entities.
**Input Handling:** `pyxel.btn()` and `pyxel.btnp()` used within entity `update` methods and the main game loop.

---

*Architecture analysis: 2025-01-24*
