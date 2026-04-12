# Phase 27: Diagnostic Overlays - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-12
**Phase:** 27-diagnostic-overlays
**Areas discussed:** Overlay toggle & rendering, Information density, Slime follow overlay, Input state display

---

## Overlay Toggle & Rendering

| Option | Description | Selected |
|--------|-------------|----------|
| Same pattern as debug.py | Module-level flags, F2-F5 toggle, each entity checks in draw() | |
| Centralized overlay manager | New src/core/overlays.py, single post-draw pass, entities untouched | ✓ |
| You decide | Claude picks cleanest approach | |

**User's choice:** Centralized overlay manager
**Notes:** User asked about benefits of option 2 — draw order control, clean entity code, easier Phase 28 integration. Decided centralized approach pays for itself.

**Follow-up: Relationship with debug.py**

| Option | Description | Selected |
|--------|-------------|----------|
| Alongside | overlays.py for visuals, debug.py keeps god-mode. Clean separation. | ✓ |
| Absorb debug.py | Merge god-mode into overlay manager, one debug system | |
| You decide | | |

**User's choice:** Alongside — keep them separate

---

## Information Density

| Option | Description | Selected |
|--------|-------------|----------|
| Visual only | Colored rects, arrows, no text | ✓ |
| Visual + key numbers | Rects plus small text readouts, 2-3 numbers max | |
| Full telemetry | Numerical readouts for everything, corner panel | |
| You decide | | |

**User's choice:** Pure visual — no text/numbers
**Notes:** User pointed out that numerical values belong in Phase 28's live-tuning panel alongside sliders. Overlays should show what the panel can't: spatial information anchored to the game world.

---

## Slime Follow Overlay

| Option | Description | Selected |
|--------|-------------|----------|
| Follow path trail | Breadcrumb dots from position history deque, color-coded by age | |
| Distance thresholds | Circles showing SLIME_MAX_DIST, SLIME_REFORM_DIST around player | |
| Both | Trail + distance thresholds | ✓ |
| You decide | | |

**User's choice:** Both — trail and distance thresholds
**Notes:** User emphasized slime follow "feels very buggy" in current state. Thorough overlay data needed to diagnose problems before Phase 30 tuning pass.

---

## Input State Display

| Option | Description | Selected |
|--------|-------------|----------|
| Button state indicator | Corner HUD showing held/pressed buttons, speedrun stream style | |
| Just spatial blips | Coyote and buffer blips only, Phase 28 panel covers the rest | ✓ |
| You decide | | |

**User's choice:** Just spatial blips — can add button HUD later if needed
**Notes:** User described the blip concept: show where the actual jump happened (coyote) and where the player pressed jump (buffer) as ephemeral marks that fade, revealing the spatial gap.

---

## Claude's Discretion

- F-key assignment (which overlay on which key)
- Overlay colors (contrast with cavern tileset)
- Blip fade duration and visual style

## Deferred Ideas

None — discussion stayed within phase scope
