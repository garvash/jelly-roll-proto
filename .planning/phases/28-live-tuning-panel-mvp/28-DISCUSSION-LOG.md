# Phase 28: Live-Tuning Panel MVP - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-12
**Phase:** 28-live-tuning-panel-mvp
**Areas discussed:** Panel layout & navigation, Slider interaction model, Preset & A/B system, Journal & crash safety

---

## Panel Layout & Navigation

### Screen space

| Option | Description | Selected |
|--------|-------------|----------|
| Side panel (~100px wide) | Right-edge strip, game on left | |
| Bottom panel (~80px tall) | Bottom strip above HUD | |
| Full overlay (semi-transparent) | Full-screen translucent overlay, game runs underneath | ✓ |

**User's choice:** Full overlay (semi-transparent)
**Notes:** User noted slider shapes should be configurable later — deferred as future refinement.

### Tab organization

| Option | Description | Selected |
|--------|-------------|----------|
| 4 tabs: Move/Slime/Combat/Misc | Broad categories | |
| 5 tabs: Move/Jump/Slime/Fuse/Feel | Finer split | ✓ (refined) |

**User's choice:** Started with 5 tabs, then refined through discussion. User questioned why 22 groups were needed — many are structural constants, not feel values. User questioned the "Feel" grab-bag tab (projectile, health, hazards) — items don't belong together. Final decision: 4 tabs (Move, Jump, Slime, Fuse). Projectile moved to Slime. Health/hazards/death excluded from panel entirely — not platformer feel.
**Notes:** Key insight: the panel is a feel-tuning tool, not a general config editor. Only groups relevant to platformer feel belong in the panel.

### Game speed

| Option | Description | Selected |
|--------|-------------|----------|
| Full speed, no pause | Game runs at 30fps normally | |
| Optional slow-mo key | Hold Tab for half-speed | ✓ |
| You decide | Claude picks | |

**User's choice:** Optional slow-mo key (Tab)
**Notes:** None

### Scrolling within tabs

| Option | Description | Selected |
|--------|-------------|----------|
| Mouse wheel scroll | Vertical scroll, ~8 sliders visible | |
| Collapsible sub-groups | Schema groups as expandable sections | ✓ |
| You decide | Claude picks | |

**User's choice:** Collapsible sub-groups
**Notes:** None

---

## Slider Interaction Model

### Slider ranges

| Option | Description | Selected |
|--------|-------------|----------|
| Percentage of baseline (0.25x-4x) | Every slider ranges 25%-400% of v1.3 baseline | ✓ |
| Schema-defined min/max metadata | Add min/max/step per key in schema | |
| You decide | Claude picks | |

**User's choice:** Percentage of baseline (0.25x to 4x)
**Notes:** None

### Reset-to-baseline

| Option | Description | Selected |
|--------|-------------|----------|
| Click arrow icon next to slider | Small reset icon per slider, click to snap back | ✓ |
| Right-click the slider | Right-click anywhere on slider to reset | |
| You decide | Claude picks | |

**User's choice:** Click arrow icon next to slider
**Notes:** None

### Keyboard numeric entry

| Option | Description | Selected |
|--------|-------------|----------|
| Click the value label to type | Click readout, type number, Enter/Esc | ✓ |
| Select slider + type digits | Arrow keys to select, then type | |
| You decide | Claude picks | |

**User's choice:** Click the value label to type
**Notes:** None

### Baseline visual indicator

| Option | Description | Selected |
|--------|-------------|----------|
| Tick mark on track | Vertical line at baseline position | |
| Color change past baseline | Track color changes on either side of baseline | ✓ |
| You decide | Claude picks | |

**User's choice:** Color change past baseline
**Notes:** None

---

## Preset & A/B System

### A/B compare mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Hotkey flip (1/2 keys) | Press 1 for slot A, 2 for slot B | ✓ |
| Toggle key (single key flips) | One key toggles A↔B | |
| You decide | Claude picks | |

**User's choice:** Hotkey flip (numbered keys)
**Notes:** User noted this naturally extends beyond 2 presets — "this can expand to more than 2 presets."

### Baseline mutability

| Option | Description | Selected |
|--------|-------------|----------|
| Always immutable | v1.3 baseline can never be overwritten | |
| Protected but overridable | Protected by default, deliberate action can update | ✓ |
| You decide | Claude picks | |

**User's choice:** Protected but overridable
**Notes:** None

### Preset save mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Save to named slot | Save button, type name, writes to named file | |
| Save overwrites active slot | Save overwrites current slot's file | ✓ (with alias) |
| You decide | Claude picks | |

**User's choice:** Save overwrites active slot, but with optional alias (display name)
**Notes:** User specified "2 but optional alias" — the slot number is the file identity, but an alias can be stored inside the JSON for display purposes.

---

## Journal & Crash Safety

### Journal entry data

| Option | Description | Selected |
|--------|-------------|----------|
| Key + old value + new value + timestamp | Full audit trail per edit | |
| Key + new value only | Minimal, enough for final state reconstruction | |
| You decide | Claude picks | ✓ |

**User's choice:** You decide
**Notes:** None

### Flush policy

| Option | Description | Selected |
|--------|-------------|----------|
| Every edit (immediate flush) | Append + fsync per slider release | |
| Batched every N seconds | Buffer edits, flush periodically | |
| You decide | Claude picks | ✓ |

**User's choice:** You decide
**Notes:** None

---

## Claude's Discretion

- Journal entry format and flush policy
- Slow-mo implementation mechanism
- Overlay transparency and background color
- Tab bar visual design
- Collapsible sub-group animation
- Slider handle size and drag dead zone
- Baseline drift color choices
- Preset JSON schema fields beyond core data

## Deferred Ideas

- Configurable slider shapes — user wants to customize slider visuals in the future
- Expanding preset slots beyond 3 — system supports it, MVP ships with 3
