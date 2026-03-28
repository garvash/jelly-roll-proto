# Retrospective - Jelly Roll Proto

## Milestone: v1.0 — Vertical Slice

**Shipped:** 2026-03-28
**Phases:** 6 | **Plans:** 14

### What Was Built
- Celeste-style platforming with walk, jump, wall slide, and kick mechanics
- Independent slime companion with juice resource and shadow follow logic
- Drill Dive fusion ability for destructive traversal through soft blocks
- Giant Mole boss with spit-stun-drill combat loop
- Cavern biome with hazards, destructible blocks, and collectible items
- 3 HP health system with Snail and Bat enemies
- Physics refinement pass resolving tech debt from early phases

### What Worked
- **Rapid iteration speed:** 11-day timeline from first commit to playable vertical slice
- **Phase-based planning:** Breaking work into focused phases kept scope manageable
- **Automated test coverage:** Tests caught regressions early, especially during physics refinement (Phase 6)
- **LDtk integration:** Level editor enabled fast biome design without manual tile placement
- **Hit-stop and screen shake:** Small juice effects made drilling feel satisfying immediately

### What Was Inefficient
- **Phase 4 artifacts in Phase 3 directory:** Required cleanup in Phase 6 (ORG-01)
- **Dash mechanic built then removed:** MOV-02 (Dash) was implemented in Phase 1 then replaced by Kick in Phase 4 — could have been caught earlier in design
- **Nyquist validation gaps:** Phases 02 and 03 lack validation files; Phase 01 has stubs only

### Patterns Established
- Death state locking (bypass update when is_alive is False)
- Timer-based respawn loops
- Physics constants in `src/core/constants.py` for all numeric tuning values
- Entity schema contract (`assets/entity-schema.json`) shared with pml-to-ldtk converter

### Key Lessons
- **Validate mechanics in design before implementing:** The dash-to-kick pivot cost implementation time
- **Create phase directories upfront:** Prevents cross-phase artifact contamination
- **Physics-based movement > lerp-based:** Acceleration/friction feels more natural and integrates better with collision

---

## Cross-Milestone Trends

| Metric | v1.0 |
|--------|------|
| Phases | 6 |
| Plans | 14 |
| Timeline (days) | 11 |
| Requirements shipped | 15 |
| Audit result | Passed |
