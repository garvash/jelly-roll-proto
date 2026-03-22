# Technology Stack: Milestone v1.1

**Project:** Jelly-Roll
**Researched:** 2026-03-12

## Recommended Stack

### Core Framework
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Pyxel | 2.x | Retro Game Engine | Primary engine for 2D aesthetics and performance. |
| Python | 3.10+ | Programming Language | Core logic and scripting. |

### Data Persistence
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| JSON (Built-in) | N/A | Save System | Human-readable, easy to debug, perfect for simple state (visited rooms, HP, upgrades). |

### World Management
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| LDtk | 1.x | Level Design | Used for 5x5 macro-map design. The "Super Simple Export" fits the existing loader. |
| CSV (Built-in) | N/A | Layer Storage | Pyxel's `bltm` works best with data pre-loaded into tilemaps; CSVs are used as an intermediary. |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Persistence | JSON | Pickle | Pickle is faster but opaque (binary) and less secure for shared save files. |
| Map Format | LDtk | Tiled | LDtk's world-view and simplified export are more modern and match the project's current path. |

## Implementation

```python
import json
import os

def save_game(data, filename="save.json"):
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_game(filename="save.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return None
```

## Sources
- Pyxel Documentation: https://github.com/kitao/pyxel
- Python JSON module: https://docs.python.org/3/library/json.html
- LDtk Documentation: https://ldtk.io/docs/
