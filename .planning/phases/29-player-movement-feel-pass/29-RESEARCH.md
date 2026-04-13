# Phase 29: Player Movement Feel Pass - Research

**Researched:** 2026-04-13
**Domain:** 2D platformer movement tuning (Pyxel engine, 60fps fixed timestep)
**Confidence:** HIGH

## Summary

Phase 29 is a tuning phase, not a code-architecture phase. The entire infrastructure -- live panel (F1), overlays (F2-F5), preset save/load, and use-site tuning reads -- was built in Phases 24-28. This phase uses that infrastructure to find good values through a human-playtest loop.

The core work is: (1) calculate feel targets from physics math, (2) build LDtk test rooms that exercise those targets, (3) iterate on values with the user via the panel, and (4) save distinct presets (v1.3 baseline, v2.0 default, tight, floaty). No new systems need to be built. The risk is scope creep into code changes that belong in later phases (fusion feel, juice polish).

**Primary recommendation:** Structure the phase as three sequential waves -- Ground, Air, Wall -- each with its own feel targets, test room, and playtest loop. Draft all feel targets upfront from Euler integration math, get user sign-off, then tune.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Feel targets use concrete gap/timing tests with pass/fail criteria. Format: table with ID, Test description, Pass condition, Fail condition.
- **D-02:** Claude drafts initial feel targets from current v1.3 physics values and tile math. User revises before tuning starts.
- **D-03:** Feel target document lives in `.planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md`.
- **D-04:** Tune systems in order: Ground (accel/friction/max speed) -> Air (gravity/jump/coyote/buffer) -> Wall (slide/jump). Each layer builds on the previous.
- **D-05:** Claude builds dedicated test rooms in LDtk with purpose-built platforming challenges. New dedicated LDtk level (e.g. "Level_Test"), separate from game content.
- **D-06:** Tuning is a human-playtest loop: Claude sets up scenarios and adjusts values via the panel API, user playtests and gives feedback, iterate until feel targets pass.
- **D-07:** "Tight" preset = Celeste-style: high accel, high friction, lower jump, fast fall, short coyote.
- **D-08:** "Floaty" preset = Hollow Knight-style: low gravity, high jump, long hang time, generous coyote.
- **D-09:** v1.3 baseline preset stays frozen as reference. Tuning produces v2.0 default alongside tight and floaty.
- **D-10:** Phase exits with 4 presets in `assets/presets/`: v1.3 baseline (frozen), v2.0 default (tuned), tight, floaty.

### Claude's Discretion
- Specific feel target values (calculated from physics math, revised by user)
- Test room layout and challenge design
- Exact slider values for tight/floaty presets
- Number of tuning iterations needed per system
- Whether additional test rooms are needed beyond the initial set

### Deferred Ideas (OUT OF SCOPE)
- Kick mechanic -- removed from the game, not present in codebase. Roadmap description references it but the mechanic does not exist in code.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MOV-04 | Movement feel tuning with written targets | Feel targets derived from Euler integration of v1.3 physics values; test room challenges map to each target |
| MOV-05 | Input buffering and forgiving mechanics audit | F4 overlay provides coyote/buffer/jump blips; audit covers all player states (ground, air, wall slide, diving, boosting, dashing) |
| MOV-06 | Preset system with distinct feel profiles | 4 preset slots (v1.3 baseline, v2.0 default, tight/Celeste, floaty/Hollow Knight) via existing save_preset/load_preset API |
</phase_requirements>

## Standard Stack

This phase uses NO new libraries. Everything is already in the codebase.

### Core (existing infrastructure)
| Module | Location | Purpose | Phase Origin |
|--------|----------|---------|--------------|
| tuning | `src/core/tuning.py` | `set_value()`, `get_baseline()`, `reset()`, `save()` | Phase 24 |
| panel | `src/ui/panel.py` | F1 panel with Move/Jump/Slime/Fuse tabs | Phase 28 |
| presets | `src/ui/presets.py` | `save_preset(slot, alias)`, `load_preset(slot)` | Phase 28 |
| overlays | `src/core/overlays.py` | F4 input blips (coyote/jump/land/buffer) | Phase 27 |

### Tuning Keys In Scope
| Group | Keys | Panel Tab |
|-------|------|-----------|
| movement | WALK_ACCEL, WALK_FRICTION, MAX_WALK_SPEED | Move |
| movement | GRAVITY, MAX_FALL_SPEED, JUMP_FORCE, VARIABLE_JUMP_REDUCTION, FALLING_GRAVITY_MULTIPLIER | Jump |
| forgiving | COYOTE_TIME, JUMP_BUFFER | Jump |
| wall | WALL_SLIDE_FRICTION, WALL_JUMP_X_IMPULSE, WALL_JUMP_Y_FORCE | Jump |

**Installation:** None required. All infrastructure exists.

## Architecture Patterns

### Phase Structure (3 Waves + Bookends)

```
Wave 0: Feel Targets + Test Room Setup
  - Draft 29-FEEL-TARGETS.md from physics math
  - Build LDtk test level(s) with measured challenges
  - Freeze v1.3 baseline to slot_0

Wave 1: Ground Tuning (WALK_ACCEL, WALK_FRICTION, MAX_WALK_SPEED)
  - Test room: flat corridors with measured start/stop markers
  - Playtest loop with user

Wave 2: Air Tuning (GRAVITY, JUMP_FORCE, VARIABLE_JUMP, FALLING_GRAVITY_MULT, COYOTE_TIME, JUMP_BUFFER)
  - Test room: gap jumps, height challenges, coyote ledges, buffer platforms
  - Playtest loop with user

Wave 3: Wall Tuning (WALL_SLIDE_FRICTION, WALL_JUMP_X/Y)
  - Test room: vertical shafts, wall-jump sequences
  - Playtest loop with user

Wave 4: Preset Capture + Exit Criteria
  - Save v2.0 default to slot_1
  - Create tight preset (slot_2) and floaty preset (slot_3)
  - Verify all feel targets pass for v2.0 default
  - Check exit criteria
```

### Tuning Workflow Pattern (per wave)

1. Claude adjusts values via `tuning.set_value()` calls (or user drags panel sliders)
2. User playtests in test rooms with F4 overlay active
3. User gives feedback ("too floaty", "coyote feels generous", etc.)
4. Iterate until feel targets pass
5. Save to preset slot

### Preset Slot Mapping (D-10)

| Slot | Alias | Contents |
|------|-------|----------|
| slot_0 | v1.3-baseline | Frozen v1.3 values -- NEVER overwritten |
| slot_1 | v2.0-default | Tuned default from playtest loop |
| slot_2 | tight | Celeste-style: high accel/friction, fast fall, short coyote |
| slot_3 | floaty | Hollow Knight-style: low gravity, generous coyote, long apex |

### Anti-Patterns to Avoid
- **Tuning code instead of values:** This phase ONLY changes tuning values, never player.py logic. Code changes belong in later phases.
- **Tuning without targets:** Every slider change should be motivated by a feel target pass/fail. Random tweaking wastes time.
- **Changing multiple systems at once:** Ground -> Air -> Wall ordering exists because each layer depends on the previous. Don't tune jump while ground accel is still unsettled.

## V1.3 Baseline Physics Reference

Euler integration of current v1.3 values (verified by running simulation): [VERIFIED: local Euler integration script]

| Metric | Value | Notes |
|--------|-------|-------|
| Jump peak height | 62.0px (3.87 tiles) | Full hold, no variable cut |
| Jump peak frame | Frame 38 | Apex reached after 38 frames |
| Full jump airtime | 65 frames (1.08s) | Ascent + descent with fall multiplier |
| Full jump horiz distance | 81.2px (5.08 tiles) | At MAX_WALK_SPEED |
| Variable jump peak (instant release) | 15.9px (0.99 tiles) | Minimum jump height |
| Frames to max walk speed | 10 frames (167ms) | From standing |
| Frames to stop from max | 9 frames (150ms) | Friction decel |
| Coyote time | 12 frames (200ms) | Standard platformer range |
| Jump buffer | 8 frames (133ms) | Standard platformer range |
| Wall slide terminal velocity | 1.25 px/frame | Half of normal MAX_FALL_SPEED |
| Wall jump X impulse | 1.5 px/frame | Fixed, same as MAX_WALK_SPEED * 1.2 |
| Wall jump Y force | -1.75 | About 54% of normal JUMP_FORCE |

### Reference Ranges from Genre Standards

| Parameter | Celeste-ish | Hollow Knight-ish | v1.3 Current |
|-----------|-------------|-------------------|-------------|
| Accel to max | 2-4 frames | 8-12 frames | 10 frames |
| Stop from max | 2-4 frames | 8-12 frames | 9 frames |
| Jump height | 2-3 tiles | 4-5 tiles | 3.87 tiles |
| Fall multiplier | 2.0-3.0x | 1.2-1.5x | 1.8x |
| Coyote time | 3-6 frames (50-100ms) | 8-12 frames (133-200ms) | 12 frames (200ms) |
| Jump buffer | 4-6 frames | 8-12 frames | 8 frames |
| Variable jump ratio | 0.3-0.4 (aggressive cut) | 0.6-0.7 (gentle cut) | 0.5 |

[ASSUMED] -- Genre reference ranges are from general platformer design knowledge. Exact values from Celeste/Hollow Knight are approximations.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Live value editing | Custom debug menu | Existing panel (F1) | Phase 28 already built it |
| Preset persistence | Manual JSON editing | `presets.save_preset(slot, alias)` | Atomic write, schema-versioned |
| Input timing verification | Frame-counting code | F4 overlay blips | Visual coyote/buffer blips already exist |
| Physics simulation | In-game measurement | Euler integration script (offline) | Deterministic, no playtest needed for math |

## Common Pitfalls

### Pitfall 1: Changing Ground After Air Is Tuned
**What goes wrong:** Adjusting WALK_ACCEL or MAX_WALK_SPEED after jump distances are tuned invalidates all horizontal gap targets.
**Why it happens:** Jump horizontal distance = airtime * walk speed. Changing walk speed changes every gap clearance.
**How to avoid:** Strict Ground -> Air -> Wall ordering (D-04). Lock ground values before starting air tuning.
**Warning signs:** Previously passing gap targets start failing after ground changes.

### Pitfall 2: Derived Values Become Stale
**What goes wrong:** The `derived.jump.*` values in physics-schema.json (used by pml-to-ldtk converter) don't match actual tuned physics.
**Why it happens:** `bake_derived()` is never called automatically (D-10/D-11 from Phase 24). After tuning, derived values are still v1.3.
**How to avoid:** Run `python -m src.core.tuning bake` after finalizing v2.0 default values. This updates max_height_tiles, max_width_tiles, etc.
**Warning signs:** Converter places platforms based on old jump distances.

### Pitfall 3: Coyote Timer Interaction With Wall Slide
**What goes wrong:** Coyote time triggers when leaving a wall slide, giving an unexpected air jump after wall detach.
**Why it happens:** `coyote_timer` is set whenever `is_grounded` is true, and wall-slide-to-fall transitions may briefly set grounded.
**How to avoid:** Test coyote behavior specifically at wall-slide exit points. F4 overlay will show coyote blips at wall detach.
**Warning signs:** Green coyote blips appearing when player releases from wall.

### Pitfall 4: Variable Jump Feels Different Per Preset
**What goes wrong:** VARIABLE_JUMP_REDUCTION interacts with JUMP_FORCE multiplicatively. A small change in one amplifies the other.
**Why it happens:** `dy *= VARIABLE_JUMP_REDUCTION` on release means the cut height depends on both the initial force and the reduction factor.
**How to avoid:** Test both full-hold and instant-release jumps for every preset. Include both in feel targets.
**Warning signs:** Tight preset minimum jump is too low to clear 1-tile obstacles; floaty preset minimum jump is surprisingly high.

### Pitfall 5: Overwriting v1.3 Baseline Preset
**What goes wrong:** Accidentally saving tuned values to slot_0, destroying the A/B reference.
**Why it happens:** Panel defaults to autosave on slot_0; user or script saves to wrong slot.
**How to avoid:** Freeze slot_0 with alias "v1.3-baseline" in Wave 0 before any tuning begins. Panel has protected-slot confirmation (Phase 28).
**Warning signs:** slot_0.json timestamp changes after tuning starts.

### Pitfall 6: Test Room Not Accessible In-Game
**What goes wrong:** LDtk test level exists but game can't navigate to it.
**Why it happens:** Room switching uses door entities and the 5x5 macro-map. A disconnected test level has no door leading to it.
**How to avoid:** Either add a debug teleport key, or connect the test level to the existing room graph with a door. Debug approach is cleaner for a throwaway test level.
**Warning signs:** Test level exists in LDtk but player can never reach it.

## Code Examples

### Setting tuning values programmatically
```python
# Source: src/core/tuning.py (verified in codebase)
from src.core import tuning

# Read current value
current_gravity = tuning.GRAVITY  # PEP 562 flat access

# Mutate (next frame reads new value)
tuning.set_value("GRAVITY", 0.10)

# Reset single key to v1.3 baseline
tuning.reset("GRAVITY")

# Reset all keys to v1.3 baseline
tuning.reset()
```

### Saving/loading presets
```python
# Source: src/ui/presets.py (verified in codebase)
from src.ui.presets import save_preset, load_preset

# Save current feel values to slot 2 with alias
save_preset(2, alias="tight")

# Load preset (applies all values via tuning.set_value)
slot, alias = load_preset(2)
```

### Baking derived values after tuning
```bash
# Source: src/core/tuning.py __main__ block (verified in codebase)
python -m src.core.tuning bake
# Updates derived.jump.max_height_tiles, max_width_tiles, etc.
# Must be run after finalizing v2.0 default values
```

## LDtk Test Room Design

### Test Room Requirements
The test level needs purpose-built challenges mapped to feel targets. Based on physics analysis:

| Challenge | Tile Layout | Tests |
|-----------|-------------|-------|
| Flat corridor (20 tiles) | Long flat ground | Accel ramp-up, stop distance, max speed feel |
| 3-tile gap | Platform - 3 tile gap - platform | Comfortable gap clearance (no running start needed) |
| 4-tile gap | Platform - 4 tile gap - platform | Near-limit gap, requires running start |
| 5-tile gap | Platform - 5 tile gap - platform | Max range gap, requires full speed + full hold |
| 2-tile height | Ground - 2 tile wall | Comfortable jump height |
| 3-tile height | Ground - 3 tile wall | Near-max jump height |
| Coyote ledge | Platform with 1-tile overhang | Walk off edge, test late jump window |
| Buffer platform | High platform -> low platform | Fall onto platform, test early jump press |
| Wall shaft | 3-tile wide vertical shaft, 6+ tiles tall | Wall slide speed, wall jump ascent |
| Wall-jump zigzag | Alternating walls, 3 tiles apart | Wall jump X impulse vs shaft width |

### Adding LDtk Test Level
The game uses simplified LDtk export. New level needs:
1. Add "Level_Test" in LDtk editor (manual step -- LDtk is a GUI tool)
2. Re-export simplified data to `assets/output/simplified/Level_Test/`
3. Game level loader reads from simplified export directory

[ASSUMED] -- Exact LDtk workflow for adding a level may need user involvement since LDtk is a GUI editor.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Magic numbers in constants.py | Schema-driven tuning via physics-schema.json | Phase 24 (v2.0) | All values hot-reloadable via panel |
| Manual file editing for tuning | F1 live panel with sliders | Phase 28 (v2.0) | Real-time feedback during playtest |
| No visual timing feedback | F4 input overlay with blips | Phase 27 (v2.0) | Coyote/buffer windows visible |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Celeste/Hollow Knight reference ranges are approximate | V1.3 Baseline Physics Reference | Low -- these are starting points, user playtesting determines final values |
| A2 | LDtk test level requires manual GUI work | LDtk Test Room Design | Medium -- if game can't load a hand-created test level, test room approach needs rethinking |
| A3 | MOV-04/05/06 map to feel targets, input audit, presets | Phase Requirements | Low -- roadmap success criteria explicitly describe these three areas |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual playtest (human-in-the-loop) |
| Config file | `.planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md` |
| Quick run command | `python main.py` (launch game, F1 for panel, F4 for input overlay) |
| Full suite command | Manual: load each preset, run through all feel target tests |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MOV-04 | Feel targets pass with v2.0 default preset | manual-playtest | N/A -- human verifies pass/fail per target | N/A |
| MOV-05 | Coyote/buffer/cancel audited across all states | manual-playtest | N/A -- F4 overlay visual inspection | N/A |
| MOV-06 | 4 presets saved with distinct feels | smoke | `python -c "from src.ui.presets import load_preset; load_preset(0); load_preset(1); load_preset(2); load_preset(3)"` | No -- Wave 4 |

### Sampling Rate
- **Per task commit:** Launch game, verify preset loads correctly
- **Per wave merge:** Playtest all feel targets for current tuning layer
- **Phase gate:** All feel targets pass for v2.0 default; tight and floaty are coherent and distinct

### Wave 0 Gaps
- [ ] `29-FEEL-TARGETS.md` -- feel target document with pass/fail criteria
- [ ] LDtk test level -- purpose-built platforming challenges
- [ ] v1.3 baseline frozen to slot_0 with correct alias

**Note:** This phase is primarily a manual-playtest phase. Automated validation is limited to preset file existence and load success. The core validation is human feel assessment against written targets.

## Open Questions

1. **How to access the test level in-game?**
   - What we know: Game uses door-based room switching on a macro-map grid. Test level would be disconnected.
   - What's unclear: Whether a debug teleport exists or needs to be added.
   - Recommendation: Add a simple debug key (e.g., Ctrl+T) to teleport to the test level. Keep it behind a debug flag. This is simpler than wiring doors.

2. **Should derived values be baked after each preset or only after v2.0 default?**
   - What we know: `bake_derived()` updates placement rules for the pml-to-ldtk converter. Tight/floaty presets are not used for level generation.
   - What's unclear: Whether tight/floaty presets need their own derived values.
   - Recommendation: Only bake for v2.0 default. Tight/floaty are gameplay options, not level-design parameters.

3. **LDtk test level creation is a manual GUI step**
   - What we know: LDtk is a desktop GUI editor. The simplified export is what the game reads.
   - What's unclear: Whether Claude can create a test level programmatically or if user must do it in LDtk.
   - Recommendation: Claude can potentially edit `assets/output.ldtk` JSON directly (it's a JSON file) and run simplified export. Alternatively, create simplified export files directly (IntGrid.csv + data.json) without LDtk. The game reads the simplified format, not the .ldtk file directly.

## Sources

### Primary (HIGH confidence)
- `assets/physics-schema.json` -- v0.3.0 schema with all tuning values, verified in codebase
- `src/core/tuning.py` -- mutation API, PEP 562 access, bake_derived, verified in codebase
- `src/entities/player.py` -- movement physics implementation, verified in codebase (lines 458-529 for movement, 663-680 for gravity)
- `src/ui/panel.py` -- panel tabs (Move/Jump/Slime/Fuse), slider system, verified in codebase
- `src/ui/presets.py` -- save_preset/load_preset with atomic write, verified in codebase
- `src/core/overlays.py` -- F4 input blips (coyote/jump/land/buffer), verified in codebase
- Local Euler integration script -- physics math verified against schema values

### Secondary (MEDIUM confidence)
- `assets/presets/slot_0.json` -- current preset format with version, schema_version, alias, values

### Tertiary (LOW confidence)
- Celeste/Hollow Knight reference ranges -- approximations from general platformer design knowledge, not measured from those games

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all infrastructure verified in codebase, no new dependencies
- Architecture: HIGH -- tuning workflow is straightforward, constrained by locked decisions
- Pitfalls: HIGH -- derived from code analysis of actual player.py physics implementation
- Feel targets: MEDIUM -- physics math is verified, but reference ranges are approximate

**Research date:** 2026-04-13
**Valid until:** 2026-05-13 (stable -- no external dependencies to go stale)
