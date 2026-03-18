# Technology Stack

**Analysis Date:** 2024-10-24

## Languages

**Primary:**
- Python 3.10+ - Core game logic and engine scripts.

**Secondary:**
- PowerShell - Build and deployment automation (`build_web.ps1`).
- JSON/CSV - Map data formats (LDtk, Tiled).

## Runtime

**Environment:**
- Python 3 Runtime

**Package Manager:**
- pip - Standard Python package manager.
- Lockfile: None detected in root (rely on `.venv` or manual installation).

## Frameworks

**Core:**
- Pyxel (1.9+) - Retro game engine for graphics, input, and audio. Used for the entire game lifecycle.

**Testing:**
- pytest - Main testing framework (`tests/`).
- unittest.mock - Used for mocking `pyxel` and other dependencies during tests.

**Build/Dev:**
- Pyxel CLI - Used for `pyxel package` and `pyxel app2html` in `build_web.ps1`.

## Key Dependencies

**Critical:**
- `pyxel` - The engine powering the game.
- `pytest` - Required for running the test suite.

**Infrastructure:**
- `unittest.mock` - Essential for testing game logic without a GPU/window environment.

## Configuration

**Environment:**
- No `.env` files detected; configuration is primarily handled via `src/core/constants.py`.

**Build:**
- `build_web.ps1` - Controls the staging and packaging process for web builds.

## Platform Requirements

**Development:**
- Python 3.x
- Pyxel (requires SDL2 and other system dependencies depending on OS)
- LDtk (optional, for level editing)

**Production:**
- Web (HTML5/WebAssembly) via `pyxel app2html`.
- Desktop (Windows/Linux/macOS) via Python or standalone executable.

---

*Stack analysis: 2024-10-24*
