# Phase 16: v1.1 Housekeeping & Verification - Context

**Gathered:** 2026-04-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Close 6 tech debt items from the v1.1 milestone audit: clean ABL-07 doc references, delete orphaned hold_position() (already done — verify), create Phase 10 VERIFICATION.md, fix stale ROADMAP checkboxes, and audit slime absorption draw path.

</domain>

<decisions>
## Implementation Decisions

### ABL-07 Cleanup
- **D-01:** Strike and archive — mark ABL-07 as "Removed (D-21)" in REQUIREMENTS.md, not just unchecked. Add strikethrough note in ROADMAP.md Phase 9 description.
- **D-02:** Prior CONTEXT.md files that reference D-21/ABL-07 are left as-is — they are historical record, not active docs.
- **D-03:** ABL-07 code is already gone from `src/` — verify no orphaned references remain in source code or tests.

### hold_position() Cleanup
- **D-04:** Phase 14 D-13 already deleted `hold_position()`. Verify it's gone from `src/entities/slime.py`. No further action if confirmed.

### Phase 10 VERIFICATION.md
- **D-05:** Create a retroactive verification doc — run existing test suite against Phase 10 features, grep for requirement coverage (ABL-02, gamepad, VFX), document pass/fail results.
- **D-06:** No new tests — capture current state only. The goal is documentation completeness, not backfilling test gaps.

### ROADMAP Staleness
- **D-07:** Phase 11 plan 11-03 (Mini-map HUD + pause screen) shipped but checkbox wasn't updated. Mark it `[x]` in ROADMAP.md.
- **D-08:** Scan all other phase entries for similar stale checkboxes and fix any found.

### Slime Absorption Draw Path Audit
- **D-09:** Audit both visual correctness AND state cleanup. Verify `is_being_absorbed` flag is properly cleared in all exit paths: death, room transition, unfuse, dissipation, reform.
- **D-10:** The pulsing shrink effect (slime.py ~line 337) should be visually verified via `run_and_capture` or equivalent. Check for edge cases like absorption interrupted mid-pulse.

### Claude's Discretion
- Fix approach for any additional stale checkboxes found during D-08 scan
- Whether to add a brief comment in slime.py if absorption exit paths are found to be incomplete

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & Roadmap
- `.planning/REQUIREMENTS.md` — ABL-07 line needs strike/archive treatment
- `.planning/ROADMAP.md` — Phase 9 ABL-07 mention, Phase 11 11-03 checkbox, Phase 16 entry

### Phase 10 Artifacts
- `.planning/phases/10-nitro-ejection-endgame/10-VALIDATION.md` — Existing validation strategy (basis for VERIFICATION.md)
- `.planning/phases/10-nitro-ejection-endgame/10-01-PLAN.md` — CRACKED_V breaking + Goo-Mold removal
- `.planning/phases/10-nitro-ejection-endgame/10-02-PLAN.md` — Gamepad controller support
- `.planning/phases/10-nitro-ejection-endgame/10-03-PLAN.md` — Ability VFX + gamepad tuning

### Phase 14 Context (Prior Decisions)
- `.planning/phases/14-tech-debt-schema-cleanup/14-CONTEXT.md` — D-13 (hold_position deletion), D-05 (IntGrid 4 rename)

### Source Code (Absorption Audit)
- `src/entities/slime.py` — `is_being_absorbed` flag, draw path (~line 337), reset/reform clearing
- `src/entities/player.py` — CHARGING_SHOT state that sets/clears absorption

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Phase 10 VALIDATION.md exists as a template for the VERIFICATION.md structure
- Existing test suite covers Phase 10 features (ABL-02, gamepad input) — run and document

### Established Patterns
- `is_being_absorbed` cleared in `slime.reset()` (line 103) and `slime.reform()` (line 302)
- Absorption draw effect: pulsing shrink using `frame_count % 4` modulo (line 337-340)
- Phase verification docs follow a standard format (see Phase 14, 15 verification docs)

### Integration Points
- REQUIREMENTS.md and ROADMAP.md are the main docs needing edits
- slime.py absorption state interacts with player.py CHARGING_SHOT state machine

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 16-v1-1-housekeeping-verification*
*Context gathered: 2026-04-02*
