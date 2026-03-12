# Stack Research

**Domain:** Pyxel Metroidvania (Retro Indie Platformer)
**Researched:** 2025-03-12
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11+ | Runtime | Required for Pyxel. 3.11+ provides significant performance boosts (specialized opcodes) critical for Python game dev. |
| Pyxel | 2.1+ | Game Engine | Lightweight, retro-focused (16 colors, fixed resolutions), cross-platform, and has built-in asset editors. |
| uv | 0.4+ | Package & Env Management | Extremely fast Python package manager and project tool. Simplifies the "install Python and run" workflow for prototypes. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 8.0+ | Logic Testing | Use for testing non-Pyxel logic: Juice math, health scaling, and state machine transitions. |
| PyInstaller | 6.4+ | Distribution | Use when packaging the prototype for non-Python users (testers/collaborators). |
| mypy | 1.9+ | Static Type Checking | Prevents runtime "NoneType" errors in complex entity systems (Player/Slime interaction). |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Pyxel Editor | Sprite/Map/Sound design | Built-in via `pyxel edit assets.pyxres`. Best for rapid prototyping within Pyxel's constraints. |
| Aseprite | Advanced Pixel Art | Better for complex animations (Slime fusion/de-fusion). Export to `.png` and import into Pyxel. |
| BFxr / Chiptone | SFX Generation | Classic 8-bit sound effects. Pyxel can import `.wav` or recreate in its sound editor. |

## Installation

```bash
# Core & Dev Env (using uv)
uv init slime-drill-proto
uv add pyxel
uv add --dev pytest mypy

# Run Built-in Editor
uv run pyxel edit assets.pyxres
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Pyxel | Godot (C# / GDScript) | If performance requirements exceed Python or if a complex lighting/particle system is needed. |
| Pyxel | TIC-80 | If a "fantasy console" (all-in-one cartridge) format is preferred over a standard Python script. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Pygame | Too low-level for a rapid prototype; requires more boilerplate for sprite/tile management. | Pyxel |
| Traditional Venv | Slow to set up and manage compared to modern tools. | uv |

## Stack Patterns by Variant

**If Windows distribution is priority:**
- Use `PyInstaller --onefile`
- Because it bundles the Python interpreter and Pyxel DLLs into a single executable.

**If rapid asset iteration is priority:**
- Use the built-in Pyxel Editor (`.pyxres`)
- Because it allows modifying sprites and maps while the game is running (hot-reloading logic).

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Pyxel 2.x | Python 3.10+ | Earlier Python versions may lack performance for physics-heavy games. |
| uv | any Python | Tool-agnostic, ensures reproducible environments. |

## Sources

- [Pyxel Official Docs](https://github.com/kitao/pyxel) — Verified 2025 compatibility and feature set.
- [Python Performance 3.11](https://docs.python.org/3/whatsnew/3.11.html) — Benchmarks for game logic.
- [uv Documentation](https://docs.astral.sh/uv/) — Best practices for Python project management.

---
*Stack research for: Pyxel Metroidvania*
*Researched: 2025-03-12*
