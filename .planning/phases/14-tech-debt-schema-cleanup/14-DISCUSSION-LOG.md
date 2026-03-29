# Phase 14: Tech Debt & Schema Cleanup - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-29
**Phase:** 14-tech-debt-schema-cleanup
**Areas discussed:** Event-gated door system, MAP-02 rewrite scope, Test fix strategy, Orphaned code policy, God mode implementation, Phase 10 verification scope, Schema version bump

---

## Event-Gated Door System

### Q1: How should event-gated doors trigger?

| Option | Description | Selected |
|--------|-------------|----------|
| Event bus pattern | Fire named events, doors listen for matching event_id. Decoupled. | |
| Direct flag check | Doors check game_state dict for event_id key. Boss sets flag on death. | ✓ |
| You decide | Claude picks simplest approach. | |

**User's choice:** Direct flag check
**Notes:** Simpler pattern, no event bus infrastructure needed.

### Q2: Should tile ID 4 (TILE_GATE) be removed or kept?

| Option | Description | Selected |
|--------|-------------|----------|
| Remove entirely | Delete from schema and constants. Maps must be updated. | |
| Keep as deprecated | Mark deprecated, log warning. Gradual migration. | |
| Keep but repurpose | Change meaning (e.g. "event_marker"). Reuse the slot. | ✓ |

**User's choice:** Keep but repurpose

### Q3: Event ID format?

| Option | Description | Selected |
|--------|-------------|----------|
| Free-form string | Any string. Flexible, no schema changes for new events. | ✓ |
| Enum in schema | Predefined list. Schema validates, needs updates for new types. | |
| You decide | Claude picks. | |

**User's choice:** Free-form string

### Q4: Door state persistence?

| Option | Description | Selected |
|--------|-------------|----------|
| Persist via save state | Once opened, stays open across room exits. | |
| Reset on room entry | Re-check event flags each entry. Simpler state management. | ✓ |
| You decide | Claude picks. | |

**User's choice:** Reset on room entry

---

## MAP-02 Rewrite Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Pipeline + event doors | Rewrite to focus on pml-to-ldtk pipeline + event door migration. | ✓ |
| Just mark satisfied | Mark done, room count is level-design scope. | |
| Split into two | MAP-02a (pipeline, satisfied) + MAP-02b (event doors, new). | |

**User's choice:** Pipeline + event doors

---

## Test Fix Strategy

### Q1: Bubble shield drain rate tests?

| Option | Description | Selected |
|--------|-------------|----------|
| Patch flag in tests | Set DEBUG_ALL_ABILITIES=False in each test. | |
| Update expected values | Change assertions to match T2 drain rates. | |
| Other | User provided custom input. | ✓ |

**User's choice:** God mode button for playtesting; normal tests run without debug flags.
**Notes:** User wants DEBUG_ALL_ABILITIES replaced with a runtime god-mode toggle. Tests should never be affected by debug playtesting state.

### Q2: Remaining 3 test failures?

| Option | Description | Selected |
|--------|-------------|----------|
| Fix individually | Targeted fix per test. Surgical changes. | |
| Batch with conftest | Shared pyxel mock fixtures and setup/teardown. | |
| You decide | Claude picks based on test structure. | ✓ |

**User's choice:** You decide

---

## Orphaned Code Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Delete both outright | Remove hold_position() and ITEM_FRAMES["DRILL"]. Git preserves history. | ✓ |
| Delete DRILL, keep hold_position | DRILL dead, hold_position might be useful later. | |
| You decide | Claude evaluates future value. | |

**User's choice:** Delete both outright

---

## God Mode Implementation

### Q1: Toggle mechanism?

| Option | Description | Selected |
|--------|-------------|----------|
| Runtime key combo | Key combo during gameplay (e.g. Ctrl+G). Debug builds only. | ✓ |
| Config flag at startup | GOD_MODE=True in config. Requires restart. | |
| You decide | Claude picks. | |

**User's choice:** Runtime key combo

### Q2: God mode scope?

| Option | Description | Selected |
|--------|-------------|----------|
| Abilities only | Toggle has_dash, has_shield, etc. Still takes damage/uses juice. | |
| Full god mode | All abilities + invincibility + infinite juice. One toggle. | |
| Tiered toggles | Separate keys for abilities, invincibility, infinite juice. | ✓ |

**User's choice:** Tiered toggles
**Notes:** Granular toggles allow testing specific scenarios.

---

## Phase 10 Verification Scope

**User's clarification:** Asked what documents say about Nitro-Ejection and Z-Spiral. After reviewing Phase 10 CONTEXT.md (which marks 5x5mapdesign.txt as outdated and defers infinite flight to Phase 11/SYS-04), user agreed with Claude's suggestion:

- Verify CRACKED_V breaking (what was built)
- Update ABL-02 requirement text to split vertical gating vs infinite flight
- Keep Nitro-Ejection for Phase 11 as a capstone power fantasy moment

**User's reasoning:** "Nitro-Ejection is a good way to end the prototype with feeling of power" — agreed it needs SYS-04 upgrades to deliver the earned power feeling.

---

## Schema Version Bump

| Option | Description | Selected |
|--------|-------------|----------|
| Bump to v0.3.0 | Semver minor bump for new fields. | |
| Bump to v1.0.0 | Mark schema as stable after gap closure. | |
| You decide | Claude picks based on schema maturity. | ✓ |

**User's choice:** You decide

---

## Claude's Discretion

- Schema version bump strategy (v0.3.0 vs v1.0.0)
- Test fix approach for remaining 3 failures (individual vs conftest)
- Specific key combos for god-mode toggles
- Exact semantic meaning of repurposed tile ID 4

## Deferred Ideas

- Nitro-Ejection / infinite flight — Phase 11 scope (needs SYS-04)
- 5x5mapdesign.txt cleanup — outdated doc still in repo
- Nyquist compliance for Phases 8-13
