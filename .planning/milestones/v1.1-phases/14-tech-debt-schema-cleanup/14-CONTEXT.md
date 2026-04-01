# Phase 14: Tech Debt & Schema Cleanup - Context

**Gathered:** 2026-03-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Close gaps identified by the v1.1 milestone audit: migrate boss gates from IntGrid tile ID 4 to event-gated Door entities, fix map.py legacy gate scan, clean orphaned code, fix 6 test failures, replace DEBUG_ALL_ABILITIES with runtime god-mode toggles, verify Phase 10 ABL-02 (CRACKED_V breaking only — infinite flight deferred to Phase 11), and rewrite MAP-02 requirement text.

</domain>

<decisions>
## Implementation Decisions

### Event-Gated Door System
- **D-01:** Add `"event"` to Door entity's `action` enum in entity-schema.json. When action="event", the door checks a game_state dict for its event_id key.
- **D-02:** Add `event_id` field to Door entity as a free-form string (e.g. "boss_defeated", "puzzle_1_solved"). No enum constraint — flexible for future event types.
- **D-03:** Direct flag check pattern: doors check `game_state[event_id]` on room entry. Boss sets `game_state["boss_defeated"]=True` on death. No event bus needed.
- **D-04:** Doors reset on room entry — re-check event flags each time. If flag is set, door opens. If not, stays closed. No persistent open/closed state tracking needed.
- **D-05:** Repurpose IntGrid tile ID 4 from "gate" to "event_marker". Keep the ID slot occupied but change its semantic meaning to align with the new event system.
- **D-06:** Update map.py `close_gates()`/`open_gates()` to work with the new event-gated Door entities instead of scanning for tile ID 4.

### MAP-02 Requirement Rewrite
- **D-07:** Rewrite MAP-02 from "Z-Spiral 20-25 unique rooms" to: "Room layouts driven by pml-to-ldtk pipeline with event-gated doors replacing tile ID 4 boss gates." Z-Spiral concept is obsolete — rooms come from LDtk level design.

### God Mode (Replacing DEBUG_ALL_ABILITIES)
- **D-08:** Remove DEBUG_ALL_ABILITIES flag entirely. Tests run with normal ability state — no debug flags in the test path.
- **D-09:** Runtime key combo toggles during gameplay (debug builds only). Tiered toggles:
  - Toggle 1: Unlock all abilities (has_dash, has_shield, has_boost, etc.)
  - Toggle 2: Invincibility (no damage taken)
  - Toggle 3: Infinite juice
- **D-10:** God mode state lives in a debug module, not scattered across entity code. Player/slime check debug flags during update.

### Test Fixes
- **D-11:** 3 bubble shield drain rate tests — fix by removing DEBUG_ALL_ABILITIES dependency. Tests should run with explicit ability state, not relying on a global debug flag.
- **D-12:** Remaining 3 test failures (DRILL dead entry, mock level_map, sprite test isolation) — Claude's discretion on individual fix vs shared conftest approach.

### Orphaned Code Cleanup
- **D-13:** Delete `slime.hold_position()` outright. ABL-03 long-hold path is unused — git history preserves it.
- **D-14:** Delete `ITEM_FRAMES["DRILL"]` from items.py. Dead mapping from pre-retcon design.

### Phase 10 ABL-02 Verification
- **D-15:** Verify CRACKED_V breaking (Drill Dive down + Slime Boost up) — the code that was actually implemented.
- **D-16:** Update ABL-02 requirement text to split: vertical gating (Phase 10, done) vs infinite flight capstone (Phase 11, needs SYS-04 Juice Capacity upgrades).
- **D-17:** Nitro-Ejection / infinite flight stays in Phase 11 scope. The power fantasy moment requires earning upgrades through exploration — it pairs with SYS-04 naturally.

### Legacy Gate Scan Fix
- **D-18:** Fix `close_gates()` lines 197-198 in map.py: replace hardcoded `+ 16` with `VIEWPORT_W // TILE_SIZE` and `VIEWPORT_H // TILE_SIZE`. Primary collision scan (lines 189-192) is already correct.

### Schema Version
- **D-19:** Claude's discretion on version bump (v0.3.0 vs v1.0.0) based on schema maturity assessment.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Entity Schema & Map Pipeline
- `assets/entity-schema.json` -- Shared schema with pml-to-ldtk converter. Door entity fields, IntGrid values, version field. Primary file being modified.
- `src/level/map.py` -- Tile collision system, gate open/close logic, legacy scan to fix.
- `src/core/constants.py` -- TILE_GATE, TILE_SIZE, VIEWPORT_W/H constants.

### Milestone Audit (Source of Truth for Gaps)
- `.planning/v1.1-MILESTONE-AUDIT.md` -- Complete gap analysis: 6 test failures, integration issues, orphaned exports, tech debt items.

### Phase 10 Context (ABL-02 Decisions)
- `.planning/phases/10-nitro-ejection-endgame/10-CONTEXT.md` -- D-01/D-02/D-03 define CRACKED_V breaking. D-12/D-13 defer infinite flight to Phase 11.

### Affected Source Files
- `src/entities/slime.py` -- hold_position() to delete.
- `src/entities/items.py` -- ITEM_FRAMES["DRILL"] to delete.
- `main.py` -- Boss gate trigger logic (close_gates/open_gates calls).
- `tests/test_bubble_shield.py` -- 3 drain rate test failures.
- `tests/test_drill_retcon.py` -- DRILL dead entry test.
- `tests/test_phase05_gaps.py` -- Mock level_map test.
- `tests/test_sprite_scale.py` -- Test isolation issue.

### Requirements
- `.planning/REQUIREMENTS.md` -- MAP-02 and ABL-02 text to update.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `LevelMap.open_gates()`/`close_gates()` -- Existing gate logic to refactor for event-gated doors.
- `LevelMap.is_solid()` -- Already checks `locked_gates` set. Event doors can reuse this pattern.
- `_ACTION_MAP` in input.py -- Key combo infrastructure exists for god-mode toggles.

### Established Patterns
- `has_*` boolean flags for ability gating (has_dash, has_shield, has_boost)
- `collision_data` dict for tile type lookups
- `game_state` dict pattern aligns with direct flag check for event doors
- Tile type constants in constants.py (TILE_SOLID, TILE_GATE, etc.)

### Integration Points
- `main.py` boss fight trigger -- Currently calls `close_gates()`/`open_gates()`. Needs to set `game_state["boss_defeated"]` instead.
- `entity-schema.json` Door entity -- Adding event action + event_id field. pml-to-ldtk converter must be updated in parallel.
- Test conftest/setup -- DEBUG_ALL_ABILITIES removal affects test environment initialization.

</code_context>

<specifics>
## Specific Ideas

- Event-gated doors use the simplest possible pattern: direct dict lookup, no event bus, no subscription system. `game_state[event_id]` is the entire mechanism.
- God mode uses tiered runtime toggles — abilities, invincibility, and infinite juice are separate so you can test specific scenarios (e.g. abilities on but still taking damage).
- Phase 10 verification is a closure task, not new work. Confirm CRACKED_V works, write VERIFICATION.md, update requirement text.
- All orphaned code gets deleted outright. Git history is the archive.

</specifics>

<deferred>
## Deferred Ideas

- **Nitro-Ejection / Infinite Flight (Phase 11):** Emerges when Juice Capacity upgrades (SYS-04) push max_juice to ~255 threshold. Power fantasy capstone — must be earned through exploration.
- **5x5mapdesign.txt cleanup:** Outdated document still in repo. Could be archived or removed.
- **Nyquist compliance for Phases 8-13:** Partial compliance flagged in audit. Can be addressed via `/gsd:validate-phase` per phase.

</deferred>

---

*Phase: 14-tech-debt-schema-cleanup*
*Context gathered: 2026-03-29*
