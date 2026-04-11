# Research Summary: Jelly-Roll v1.1

**Domain:** 2D Metroidvania Action-Platformer
**Researched:** 2026-03-12
**Overall confidence:** HIGH

## Executive Summary
Milestone v1.1 expands the Jelly-Roll prototype into a cohesive **5x5 Mini-World** focused on exploration and ability-based gating. The "Z-Spiral" map topology ensures players revisit the Central Hub with new traversal powers (Slime Ram, Nitro-Ejection), maximizing the value of the 25-room layout.

Technically, Pyxel's architecture is well-suited for this scale. A single 256x256 tilemap can house the entire 5x5 grid (80x80 tiles total). Persistence will be handled via standard JSON serialization for world state and player progress.

## Key Findings

**Stack:** Python/Pyxel + JSON Persistence + LDtk Super Simple Export.
**Architecture:** Camera Snapping (128x128 px) + Room-Based Spawning + Position History Buffer for Slime.
**Critical pitfall:** Tilemap destruction must use absolute world coordinates to prevent cross-room corruption.

## Implications for Roadmap

1. **Macro-Map & Persistence** - Foundation for the 5x5 world.
2. **Horizontal Mastery (Slime Ram)** - Core traversal update.
3. **Combat Refinement (Charge Shot/Shield)** - Defensive and offensive depth.
4. **Vertical Mastery (Nitro-Ejection)** - The endgame "reward" and escape mechanic.
5. **UI & Polish (Mini-map/Save Rooms)** - Finalizing the prototype experience.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Pyxel/Python limits are well understood. |
| Features | HIGH | Based on established shmup/platformer patterns. |
| Architecture | MEDIUM | Requires careful implementation of camera snapping. |
| Pitfalls | HIGH | Common 2D game dev issues identified. |

## Gaps to Address
- **Z-Spiral Logic:** The specific layout of the 5x5 grid in LDtk needs manual verification of traversal flow.
- **Slime Physics:** Forward Dash (Ram) may require sub-pixel collision tuning for 128x128 resolution.
