# Phase 29: Player Movement Feel Pass - Context

**Gathered:** 2026-04-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Retune player movement feel — accel/friction, gravity/jump curves, variable jump, coyote, jump buffer, wall slide/jump — against written feel targets using the live panel and overlays. First feel phase; lowest-coupling system.

**Out of scope (other phases):**
- Phase 33 — per-ability feel pass (fusion abilities)
- Phase 34 — slime follow/AI feel pass
- Phase 35 — juice polish (shake, hitstop, particles)
- Kick mechanic — removed from the game; not present in codebase

</domain>

<decisions>
## Implementation Decisions

### Feel Target Format
- **D-01:** Feel targets use concrete gap/timing tests with pass/fail criteria. Format: table with ID, Test description, Pass condition, Fail condition. Example: "M-01 | Full-speed 4-tile gap | Land 1+ tile in | Fall short".
- **D-02:** Claude drafts initial feel targets from current v1.3 physics values and tile math (e.g. calculating gap clearance from JUMP_FORCE + GRAVITY + MAX_WALK_SPEED). User revises before tuning starts.
- **D-03:** Feel target document lives in `.planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md`.

### Tuning Methodology
- **D-04:** Tune systems in order: Ground (accel/friction/max speed) -> Air (gravity/jump/coyote/buffer) -> Wall (slide/jump). Each layer builds on the previous.
- **D-05:** Claude builds dedicated test rooms in LDtk with purpose-built platforming challenges — measured gaps, wall heights, coyote ledges — mapped to feel targets. New dedicated LDtk level (e.g. "Level_Test"), separate from game content.
- **D-06:** Tuning is a human-playtest loop: Claude sets up scenarios and adjusts values via the panel API, user playtests and gives feedback, iterate until feel targets pass.

### Preset Identity
- **D-07:** "Tight" preset = Celeste-style: high accel, high friction (instant response), lower jump height, fast fall, short coyote. Precise and punishing — rewards exact timing.
- **D-08:** "Floaty" preset = Hollow Knight-style: low gravity, high jump, long hang time at apex, generous coyote. Exploration-friendly, forgiving platforming.
- **D-09:** v1.3 baseline preset stays frozen as a reference point. Tuning produces a new "v2.0 default" preset alongside tight and floaty. The original v1.3 is always available for A/B comparison.
- **D-10:** Phase exits with 4 presets in `assets/presets/`: v1.3 baseline (frozen), v2.0 default (tuned), tight (Celeste-style), floaty (Hollow Knight-style).

### Claude's Discretion
- Specific feel target values (calculated from physics math, revised by user)
- Test room layout and challenge design
- Exact slider values for tight/floaty presets (guided by Celeste/Hollow Knight feel descriptions)
- Number of tuning iterations needed per system
- Whether additional test rooms are needed beyond the initial set

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Tuning system (Phase 24-25)
- `src/core/tuning.py` — mutation API: `set_value()`, `get_baseline()`, `reset()`, `save()`, `get_group()`, PEP 562 `__getattr__`
- `assets/physics-schema.json` — v0.3.x schema with movement, forgiving, wall groups. Source of truth for all tuning values.

### Player movement code
- `src/entities/player.py` — all movement physics: accel (~L463), friction (~L485), jump (~L512), wall jump (~L520), variable jump (~L528), gravity (~L668), coyote timer (~L240), jump buffer (~L246)

### Live panel (Phase 28)
- `src/core/tuning_panel.py` (or wherever Phase 28 placed it) — panel with Move and Jump tabs covering all relevant sliders
- `assets/presets/` — existing preset slots (slot_0 through slot_3)

### Diagnostic overlays (Phase 27)
- `src/core/overlays.py` — F4 input overlay with coyote/buffer spatial blips

### LDtk pipeline
- `assets/output.ldtk` — LDtk project file for adding test levels

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tuning.set_value(key, value)` — live mutation, next-frame visibility
- `tuning.get_baseline(key)` — frozen v1.3 values for reference/diff
- Panel Move/Jump tabs — all movement sliders already exposed
- Input overlay (F4) — coyote/buffer blips for verifying timing windows
- Preset save/load — `assets/presets/slot_N.json` system from Phase 28

### Established Patterns
- Use-site tuning reads in `player.py` — values read each frame, hot-reloadable
- Panel slider -> `tuning.set_value()` -> next frame reads new value (Phase 25 + 28 pipeline)
- Preset A/B switching via numbered hotkeys (Phase 28 D-11)

### Integration Points
- `assets/presets/` — new v2.0 default preset file alongside existing slots
- `assets/output.ldtk` — new test level added to LDtk project
- `.planning/phases/29-*/29-FEEL-TARGETS.md` — feel target document (new artifact)

</code_context>

<specifics>
## Specific Ideas

- Feel targets should be spatially grounded (tile gaps, wall heights) not abstract adjectives
- Tight preset inspired by Celeste: snappy, precise, punishing
- Floaty preset inspired by Hollow Knight: generous, exploratory, forgiving apex
- v1.3 baseline is sacred — never overwritten, always available for A/B
- Test rooms are purpose-built challenges, not gameplay levels

</specifics>

<deferred>
## Deferred Ideas

- Kick mechanic — removed from the game, no longer in scope for any phase. Roadmap description references it but the mechanic does not exist in code.

</deferred>

---

*Phase: 29-player-movement-feel-pass*
*Context gathered: 2026-04-13*
