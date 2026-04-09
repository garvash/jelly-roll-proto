---
gsd_state_version: 1.0
milestone: v1.3
milestone_name: 16x16 Tile Migration
status: Milestone complete
last_updated: "2026-04-09"
progress:
  total_phases: 4
  completed_phases: 4
  total_plans: 7
  completed_plans: 7
---

# Project State - Jelly Roll Proto

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-09)

**Core value:** Prototyping the satisfying "fusion" loop between a player and a companion slime.
**Current focus:** Planning next milestone

## Current Position

Milestone v1.3 complete. No active phase.

## Progress

[████████████████████] 100% -- v1.3 (4/4 phases, 7/7 plans)

## Recent Decisions

- v1.3 shipped: uniform 16x16 grid, entity-schema v2.0.0, physics-schema v0.2.0
- Boss entity changed to 32x32 in LDtk to match sprite size; spawn offset converts visual to hitbox position
- All LDtk entity pivots set to top-left for consistent coordinate handling

## Pending Todos

(None)

## Blockers/Concerns

(None)

## Accumulated Context

- entity-schema.json v2.0.0 with grid_size=16, rooms 20x11 tiles
- physics-schema.json v0.2.0 with tile-unit values halved from 8px base
- schema.py provides 9 public lookup functions for tile/entity definitions
- autoLayerTiles parsed from full LDtk project file (18,094 tiles, 32 variants)
- Multi-layer parallax pipeline: bg layer (scroll 0.5) + terrain layer (scroll 1.0)
- CONVERTER-HANDOFF.md documents all breaking changes for pml-to-ldtk converter
- All LDtk entity pivots now top-left (was center for some entities)
