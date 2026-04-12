---
phase: 28-live-tuning-panel-mvp
plan: 01
subsystem: ui
tags: [panel, widgets, tuning, overlay, sliders]
dependency_graph:
  requires: [src/core/tuning.py]
  provides: [src/ui/panel.py, src/ui/widgets.py, src/ui/__init__.py]
  affects: [main.py]
tech_stack:
  added: []
  patterns: [immediate-mode-ui, module-level-state-toggle, log2-slider-scale]
key_files:
  created:
    - src/ui/__init__.py
    - src/ui/widgets.py
    - src/ui/panel.py
  modified: []
decisions:
  - "Log2 scale for sliders: 2**(ratio*4-2) maps 0->0.25x, 0.5->1x, 1->4x of baseline"
  - "Fuse tab defaults all sub-groups collapsed except drill (first group)"
  - "Movement group split hardcoded: 5 jump-related keys to Jump tab, rest to Move tab"
  - "BoolToggle as separate class (not Slider subclass) for simpler checkbox rendering"
  - "T-28-02 keyboard edit clamped to [0.25x, 4x] baseline range"
metrics:
  duration_seconds: 226
  completed: "2026-04-12T13:19:05Z"
  tasks_completed: 2
  tasks_total: 2
  files_created: 3
  files_modified: 0
---

# Phase 28 Plan 01: Core Panel UI Module Summary

Interactive tuning panel overlay with log2-scale sliders, 4-tab navigation, collapsible sub-groups, keyboard entry, reset arrows, scroll, and baseline diff visualization -- all hand-drawn with Pyxel primitives.

## Completed Tasks

| # | Task | Commit | Key Files |
|---|------|--------|-----------|
| 1 | Create src/ui/ package and widgets.py with all interactive widget classes | f9dfca3 | src/ui/__init__.py, src/ui/widgets.py |
| 2 | Create src/ui/panel.py -- panel module with toggle, tab content, scroll, and input gating | 46dade1 | src/ui/panel.py |

## Implementation Details

### widgets.py (310 lines)
- **Slider**: Log2-scale drag mapping (0.25x-4x baseline), keyboard edit with Enter/Esc/Backspace, reset-to-baseline with 6-frame yellow flash, track color split at baseline tick (palette 5 below, palette 8 above)
- **BoolToggle**: Checkbox toggle for boolean tuning keys (RAM_INVINCIBLE), click toggles True/False
- **CollapsibleGroup**: Expand/collapse header with child widget delegation, "v"/">" glyph indicator
- **TabBar**: 4 equal-width (80px) clickable tabs with active/inactive coloring
- All layout constants match UI-SPEC pixel-exact contract (8px rows, 320px total width)

### panel.py (250 lines)
- F1 toggle with `pyxel.mouse()` cursor control
- 4 tabs built from `tuning._flat_index` with movement-group split (5 jump keys separated)
- Mouse wheel scroll (8px per notch) with per-tab offset, clamped to content bounds
- `is_editing()` gate prevents key conflicts during keyboard entry (Pitfall 4)
- Header shows preset status ("Slot N: alias" or "Slot -: custom")
- Footer shows preset hints ("[1] v1.3  [2] tight  [3] floaty") and slow-mo hint
- Baseline slot 1 protection: 120-frame confirmation window for overwrite (D-14)
- Save button stub (`_save_callback`) ready for Plan 02 wiring

## Deviations from Plan

None -- plan executed exactly as written.

## Self-Check: PASSED

- [x] src/ui/__init__.py exists
- [x] src/ui/widgets.py exists (Slider, BoolToggle, CollapsibleGroup, TabBar importable)
- [x] src/ui/panel.py exists (show_panel, update, draw, is_editing importable)
- [x] FEEL_GROUPS has 12 groups, JUMP_TAB_MOVEMENT_KEYS has 5 keys
- [x] Commit f9dfca3 exists
- [x] Commit 46dade1 exists
