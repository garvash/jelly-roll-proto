# Coding Conventions

**Analysis Date:** 2026-03-18

## Naming Patterns

**Files:**
- snake_case: `player.py`, `level_map.py`, `constants.py`.

**Functions:**
- snake_case: `update()`, `draw()`, `take_damage()`, `handle_input()`.

**Variables:**
- snake_case: `hp`, `is_alive`, `invuln_timer`, `facing_right`.

**Types/Classes:**
- PascalCase: `Player`, `Slime`, `LevelMap`, `Snail`, `Game`.

**Constants:**
- UPPER_SNAKE_CASE: `PLAYER_MAX_HP`, `TILE_SIZE`, `GRAVITY`. Defined in `src/core/constants.py`.

## Code Style

**Formatting:**
- PEP 8: Follows standard Python indentation (4 spaces) and formatting.

**Linting:**
- Not detected: No explicit `.flake8` or `pyproject.toml` linting configuration found.

## Import Organization

**Order:**
1. Library imports (e.g., `import pyxel`, `import math`).
2. Constants (frequently `from src.core.constants import *`).
3. Local modules/entities (e.g., `from src.entities.player import Player`).

**Path Aliases:**
- None: Standard absolute imports from `src.*`.

## Error Handling

**Patterns:**
- Logical Checks: Primarily uses `if` statements for validation (e.g., `if not self.is_alive: return`).
- Boolean Success: Methods like `take_damage()` return `True`/`False` to indicate success.

## Logging

**Framework:**
- Standard `print()`: Used for debugging and status messages, particularly during asset loading in `main.py`.

## Comments

**When to Comment:**
- Explaining magic numbers: Room dimensions, tile offsets.
- Clarifying logic: Physics timers, movement states.
- Section markers: `# Health & Combat`, `# Forgiving mechanics timers`.

**JSDoc/TSDoc:**
- Not applicable: Standard Python docstrings or inline comments are used.

## Function Design

**Size:**
- Methods are generally compact, focusing on specific logic (e.g., `update_timers`, `apply_physics`).

**Parameters:**
- Direct passing: Objects like `slime`, `level_map`, or `player` are often passed as arguments to update methods.

**Return Values:**
- Mixed: Boolean success or no return (side-effect heavy logic common in game engines).

## Module Design

**Exports:**
- Classes: Each entity file typically defines and exports a single primary class.

**Barrel Files:**
- `__init__.py` files are present in `src/` and subdirectories but mostly serve as package markers rather than aggregator exports.

---

*Convention analysis: 2025-05-22*
