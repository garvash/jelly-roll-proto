# Architecture Research

**Domain:** Pyxel Game Architecture (Slime-Drill)
**Researched:** 2025-03-12
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        [App Layer]                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Input   │  │ Logic   │  │ Physics │  │ Draw    │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │              │
├───────┴────────────┴────────────┴────────────┴──────────────┤
│                        [Manager Layer]                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │                GameState (FSM)                      │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                        [Entity Layer]                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │ Player   │  │  Slime   │  │  Level   │                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| App | Main Pyxel loop (Init, Update, Draw) | `main.py` entry point. |
| Player | Movement, Input handling, Fusion state | Class with a sub-state machine. |
| Slime | AI following, Juice resource, Projectile source | Independent class with "Leash" logic. |
| Level | Tilemap rendering, Collision lookups, Block destruction | Wrapper around Pyxel tilemaps + destruction dict. |
| GameState | Menus, Death, UI, Milestone tracking | Singleton or global state container. |

## Recommended Project Structure

```
src/
├── entities/           # Dynamic objects
│   ├── player.py       # Player logic (MOV-01/02)
│   ├── slime.py        # Slime behavior (SLM-01/02/03)
│   └── boss.py         # Boss Mole logic (BOSS-01)
├── level/              # Static & Destructible world
│   ├── map.py          # Tilemap & Collision (ENV-01)
│   └── blocks.py       # "Soft" block destruction logic (DRILL-02)
├── core/               # Engine & Managers
│   ├── constants.py    # Colors, Resolution, Physics tweakables
│   └── state.py        # Global GameState / Resource management
└── main.py             # Entry point (Main Loop)
```

### Structure Rationale

- **entities/:** Decouples player physics from Slime AI. Essential for managing the "Fusion" state where they merge.
- **level/:** Separates the visual map from the logical collision/destruction layer.
- **core/:** Centralizes constants like gravity/friction to make "tightening movement" easier.

## Architectural Patterns

### Pattern 1: Finite State Machine (FSM)

**What:** Explicitly defining player states (IDLE, RUN, JUMP, DRILL).
**When to use:** Crucial for the Player character to handle complex animation/physics transitions during Fusion.
**Trade-offs:** Avoids "if-else" hell, but requires more boilerplate.

**Example:**
```python
class Player:
    def update(self):
        if self.state == State.DRILLING:
            self.apply_drill_physics()
        elif self.state == State.AIRBORNE:
            self.apply_gravity()
```

### Pattern 2: Component-Based Destruction

**What:** Storing "damaged" blocks in a dictionary instead of modifying the tilemap directly.
**When to use:** When drilling through tiles to allow for "partial destruction" or regenerating blocks.
**Trade-offs:** Saves memory vs. re-drawing the whole tilemap.

### Pattern 3: Leash Follower AI

**What:** The Slime moves toward a "breadcrumb" list of player's previous positions.
**When to use:** For the Slime companion to follow the player smoothly over platforms.
**Trade-offs:** Feels natural but requires managing a list of coordinates.

## Data Flow

### Frame Flow

```
[Pyxel Loop]
    ↓
[Update] → [Input] → [State Update] → [Physics] → [Collision Resolve]
    ↓
[Draw] ← [Camera Offset] ← [Map Layer] ← [Entity Layer] ← [HUD]
```

### Slime Juice State Management

```
[Slime Juice]
    ↓ (consumption)
[Drill Ability] ←→ [Slime Size Calculation] → [HUD Display]
    ↓ (regeneration)
[Idle State / Pickups]
```

### Key Data Flows

1. **Drill Fusion:** Player triggers "Down + Jump" -> Checks Slime distance -> Merges -> Changes Physics profile.
2. **Tile Destruction:** Drill entity contacts "Soft Block" -> Decrements health in `destruction_map` -> If 0, removes tile from collision logic.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Prototype (1 Biome) | Single script or simple module structure. |
| Full Game (10+ Biomes) | Room-based loading, Entity Pooling, and a Scene Manager. |

### Scaling Priorities

1. **First bottleneck:** Collision checks with many destructible blocks. Fix by using a spatial hash or chunk-based collision.
2. **Second bottleneck:** Python execution speed in the `update` loop. Fix by optimizing entity updates (only update visible entities).

## Anti-Patterns

### Anti-Pattern 1: God Object (The `App` class)

**What people do:** Putting all logic, physics, and drawing inside the main `App` class.
**Why it's wrong:** Becomes unmanageable once the Slime and Boss are added.
**Do this instead:** Delegate logic to `Player` and `Slime` classes.

### Anti-Pattern 2: Per-Pixel Collision

**What people do:** Checking every pixel of a sprite against every pixel of the map.
**Why it's wrong:** Extremely slow in Python/Pyxel.
**Do this instead:** Use tile-based collision (check the 4-8 points around the bounding box).

## Integration Points

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Player ↔ Slime | State Sharing / Distance Check | Slime needs to know Player position; Player needs to know Slime "Juice" level. |
| Drill ↔ Level | Collision Callbacks | The Level needs to inform the Drill when a destructible block is hit. |

## Sources

- [Pyxel Examples (platformer.py)](https://github.com/kitao/pyxel/tree/main/python/pyxel/examples)
- [Game Programming Patterns (FSM)](https://gameprogrammingpatterns.com/state.html)
- [2D Platformer Physics (Sonic/Celeste)](https://celestegame.github.io/celeste-physics.html)

---
*Architecture research for: Slime-Drill Metroidvania*
*Researched: 2025-03-12*
