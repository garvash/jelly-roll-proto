# Phase 24: Tuning Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in 24-CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-11
**Phase:** 24-tuning-foundation-schema-inversion
**Areas discussed:** Mutation & persistence, Schema layout, Derived recomputation, Namespace shape, Hot-reload robustness

---

## Gray Area Selection

Claude proposed four gray areas. User selected ALL four and added a critical clarification in the notes field:

> "the user is not live-editing the JSON. we can have an internal data model that links to the JSON so we can save to file when we need to."

This note reframed the entire phase and led directly to the FND-04 deletion.

| Area | Selected |
|------|----------|
| Schema layout | ✓ |
| Namespace shape | ✓ |
| Mutation & persistence | ✓ |
| Hot-reload robustness | ✓ (resolved by user note before discussion) |

---

## Mutation & Persistence

User asked for a recommendation rather than picking from preset options. Claude recommended an in-memory model with explicit save, no autosave, and FND-04 deletion. User confirmed.

| Option | Description | Selected |
|--------|-------------|----------|
| Model owns runtime, JSON is preset | set_value memory-only, save() explicit, baseline in-memory | ✓ |
| Write-through every mutation | Every set_value writes disk | |
| Memory + journal, periodic flush | Autosave journal, flush on interval | |

**User's choice:** In-memory model + explicit save (the recommendation).
**Notes:** User instructed: "since the overlay controls are the best way to edit the values. the user will use that as the primary way to tweak the values. what would you suggest for this use case?" — this is the load-bearing constraint behind dropping FND-04.

### FND-04 disposition

| Option | Description | Selected |
|--------|-------------|----------|
| Drop FND-04 entirely | No file watcher, restart on git pull | ✓ |
| Keep soft version (manual reload_from_disk API) | Explicit dev API, no polling | |

**User's choice:** "option 1 is good. let's go with it"

---

## Schema Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Pure restructure | Top level = {tuning, derived, ...}; existing top-level blocks move into derived.* | ✓ |
| Add tuning.*, keep top-level derived in place | Less converter churn, derived.* doesn't exist as namespace | |
| Mirror layout (tuning + derived AND top-level) | Two sources of truth for derived values | |

**User's choice:** Pure restructure.
**Notes:** User selected with the schema preview showing the v0.3.0 shape. CONVERTER-HANDOFF.md gets updated with old-path → new-path table.

### Derived Recomputation

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit bake only | tuning.bake_derived() exists but is never called automatically | ✓ |
| Auto-bake on save() | save() always recomputes derived.* before writing | |
| Live-bake on every set_value() | Eager recompute on every mutation | |

**User's choice:** Explicit bake only. Phase 36 runs it before ship; intermediate staleness is acceptable.

---

## Namespace Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Flat aliases | tuning.GRAVITY mirrors constants.py exactly; PEP 562 flattens schema groups | ✓ |
| Nested attribute access | tuning.movement.GRAVITY mirrors schema | |
| Both — nested primary, flat shim | Most flexibility, most surface area | |

**User's choice:** Flat aliases.
**Notes:** Chosen specifically to make Phase 25's mechanical refactor a 1-to-1 rename. Schema groups exist for the panel only (panel reads metadata to know which slider goes in which tab).

---

## Hot-Reload Robustness

Resolved during the Mutation & Persistence area — FND-04 dropped, so the entire question collapses to "no file watcher, no edge cases, restart on git pull." No questions asked in this area.

---

## Claude's Discretion

Items the user delegated to the planner:
- Exact group names under `tuning.*` (with the constraint that they mirror existing constants.py comment headers)
- Order of keys within each tuning.* group
- Implementation of atomic write in save()
- Whether bake_derived() lives in tuning.py or a separate derive.py
- Loader caching strategy
- Test layout

## Deferred Ideas

- File-watcher hot-reload (explicitly killed via FND-04 deletion)
- Autosave / journal / save-on-quit hook (Phase 28's call)
- Baseline-as-disk-file (kept in memory only)
- Per-group attribute access (tuning.movement.GRAVITY)
- Live-bake of derived.* on every set_value
- Schema version negotiation
