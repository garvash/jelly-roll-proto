---
gsd_state_version: 1.0
milestone: v2.0
milestone_name: Game Feel
status: Defining requirements
last_updated: "2026-04-11"
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
---

# Project State - Jelly Roll Proto

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-11)

**Core value:** Prototyping the satisfying "fusion" loop between a player and a companion slime.
**Current focus:** v2.0 Game Feel — defining requirements

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-04-11 — Milestone v2.0 Game Feel started

## Progress

[                    ] 0% -- v2.0 (0/0 phases)

## Recent Decisions

- v2.0 Game Feel milestone started: live-tuning panel, animation state machine, fusion lifecycle redesign, systematic tuning pass
- physics-schema.json to be promoted to single source of truth (currently derived from constants.py)
- Fusion design pass precedes fusion tuning — charge-to-fuse, V button, entry/sustain/end model all open for reconsideration
- Animation system to gain state transition event hooks (direction_change, jump_start, land, etc.) with transition frame insertion

## Pending Todos

(None — requirements to be defined)

## Blockers/Concerns

(None)

## Accumulated Context

- entity-schema.json v2.0.0 with grid_size=16, rooms 20x11 tiles
- physics-schema.json v0.2.0 currently derived from src/core/constants.py source values (GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, etc.) — to be inverted so schema is source of truth
- src/core/constants.py holds ~50 tuning values across movement, jump, slime follow, juice, drill, ram, charge shot, boost, fusion/recall, mana shield
- schema.py provides 9 public lookup functions for tile/entity definitions
- autoLayerTiles parsed from full LDtk project file (18,094 tiles, 32 variants)
- Multi-layer parallax pipeline: bg layer (scroll 0.5) + terrain layer (scroll 1.0)
- pml-to-ldtk converter already reads physics-schema.json — inversion must preserve this contract
- Player animation is primitive: 2 frames switched by state with hardcoded u offsets in player.py:790; no transitions, no anticipation/recovery, no squash/stretch
- CONVERTER-HANDOFF.md documents all breaking changes for pml-to-ldtk converter
- All LDtk entity pivots now top-left (was center for some entities)
