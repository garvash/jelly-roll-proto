# Pitfalls Research

**Domain:** Game feel pass on existing Pyxel Metroidvania prototype (v1.3 → v2.0)
**Researched:** 2026-04-11
**Confidence:** HIGH (based on well-documented patterns from GMTK Platformer Toolkit, Celeste post-mortems, live-tuning workflows, and the specific shape of this codebase as captured in STATE.md)

This document catalogs mistakes specific to **adding game-feel systems to a working prototype**. The core risk of v2.0 is not "can we build the new systems" — it is "can we build them without regressing the v1.0–v1.3 gameplay that shipped." Every pitfall below is framed around that risk.

---

## Critical Pitfalls

### Pitfall 1: Schema Inversion Load Order / Circular Import Trap

**What goes wrong:**
Promoting `physics-schema.json` to source of truth breaks startup. `constants.py` currently imports cleanly from Python; inverting means `constants.py` (or a replacement) must parse JSON at import time. Any module imported during JSON load (logging, path helpers, validators) that itself imports constants creates a circular import, or the schema lookup fails before Pyxel's image bank init and the game crashes with a cryptic `KeyError` deep in the module graph.

**Why it happens:**
Developers treat "flip the source of truth" as a find-and-replace. They leave `from core.constants import GRAVITY` scattered across ~50 call sites, rewrite `constants.py` to read from JSON eagerly, and discover the schema loader itself depends on something constants used to provide (e.g., `ASSET_ROOT`, `TILE_SIZE`).

**How to avoid:**
1. Introduce a dedicated `src/core/tuning.py` module that owns the schema load. Do **not** repurpose `constants.py` — leave it as a thin shim that re-exports from `tuning` so the ~50 call sites keep working unchanged.
2. Load schema lazily behind a `get_tuning()` accessor, not at module import. First call happens after Pyxel init.
3. The shim `constants.py` must import nothing from game modules — only `json`, `pathlib`, and the schema file path. Any other import is a circular-import timebomb.
4. Run `python -c "import src.core.constants"` as a smoke test in CI before any game-level tests.

**Warning signs:**
- Import errors that change depending on which test runs first
- `ImportError: cannot import name 'GRAVITY'` during pytest collection
- Startup works from `python main.py` but fails from pytest
- Stack traces that bottom out in `json.load` during module import

**Phase to address:**
Phase 1 — Schema inversion must ship before any tuning pass. Gate the phase on: (a) game boots with schema-driven values, (b) all ~50 existing constants resolve to the same numeric values they had in v1.3, (c) the pml-to-ldtk converter contract still passes.

---

### Pitfall 2: Silent Type Coercion Drift (float vs int)

**What goes wrong:**
`constants.py` has values like `GRAVITY = 0.5`, `MAX_WALK_SPEED = 2`, `JUMP_FORCE = -6`. Python keeps `int` and `float` distinct; JSON has only `number`. After inversion, `MAX_WALK_SPEED` comes back as `2.0` instead of `2`, and `JUMP_FORCE` as `-6.0` instead of `-6`. In most places this is harmless, but:
- `range(MAX_WALK_SPEED)` becomes `TypeError`
- Pyxel blit calls `pyxel.blt(x, y, ...)` with float pixel coords silently render at truncated positions, and the player's collision box drifts by a subpixel each frame
- Tile indices `room[ty][tx]` with float indices raise `TypeError` in CPython but may "work" under numpy
- Comparisons `x == PLAYER_START_X` silently fail when the schema round-tripped `64` as `64.0`

Live-tuning panel writes back values from slider widgets that are always `float`, corrupting int-typed lookups mid-game.

**Why it happens:**
JSON has no int/float distinction, and Python's duck typing masks the problem until a specific code path hits the failing operator. The issue only surfaces after the tuning panel writes a value back, so it feels like "the panel broke things" when the type drift was already latent.

**How to avoid:**
1. Declare explicit type per field in the schema (`"gravity": {"value": 0.5, "type": "float"}` or a parallel types map).
2. Wrap schema reads in a typed accessor: `tuning.get_int("movement.max_walk_speed")`, `tuning.get_float("movement.gravity")`. No raw dict access.
3. Pyxel-specific: audit every call to `pyxel.blt`, `pyxel.rect`, `pyxel.rectb`, `pyxel.line` — these silently accept floats and truncate. Coerce at the draw boundary with `int(x)`.
4. Unit test: after load, assert `type(GRAVITY) is float`, `type(MAX_WALK_SPEED) is int`.

**Warning signs:**
- `TypeError: 'float' object cannot be interpreted as an integer` in range / list indexing
- Player looks "smooth but wrong" — movement feels fine but subtly off-grid
- Tests pass on the original constants but fail after schema round-trip
- Live-tuning slider "works" but changing back to original value doesn't restore original behavior

**Phase to address:**
Phase 1 (schema inversion) — types must be declared. Phase 2 (live-tuning panel) — writeback path must coerce through typed accessors.

---

### Pitfall 3: Converter Contract Break (pml-to-ldtk)

**What goes wrong:**
`pml-to-ldtk` converter already reads `physics-schema.json`. If v2.0 reshapes the schema (new keys, renamed sections, moved values from top-level to nested groups for the tuning panel UI), the converter silently produces wrong LDtk output or crashes when maintainers next run it. Since the converter is external, this may not surface until the next room layout update, at which point the breakage is far from the cause.

**Why it happens:**
The tuning panel needs grouped, labeled, ranged values (`movement.max_walk_speed` with min/max/step/display_name). The simplest schema restructure is to wrap every value in an object. This is the most natural form for the panel — and a breaking change for anyone reading the schema flat.

**How to avoid:**
1. **Preserve the existing flat value structure for any key the converter reads.** Add panel metadata as a parallel `_tuning_meta` section or use a schema that keeps raw values accessible via a stable key path.
2. Version the schema (`physics-schema.json` → `v0.3.0`) and update CONVERTER-HANDOFF.md with a diff before shipping. Same discipline as v1.3.
3. Write a one-shot test that mocks the converter's read path: loads the schema, extracts the fields pml-to-ldtk needs, asserts they're present with the expected type.
4. If grouping is unavoidable, provide both: nested form for panel, flat mirror generated at build time for the converter.

**Warning signs:**
- Converter maintainer reports "room layouts look wrong" weeks after v2.0 ships
- Schema diff shows key renames or type changes without a converter companion PR
- CONVERTER-HANDOFF.md not updated in the phase that changes the schema
- No test file that opens physics-schema.json from a "converter's perspective"

**Phase to address:**
Phase 1 — schema inversion must ship with updated CONVERTER-HANDOFF.md and a contract test. Block phase completion on converter smoke test passing.

---

### Pitfall 4: Missing-Value Startup Crash (Schema Drift Between Repos)

**What goes wrong:**
Someone adds a new tuning value used by code (`COYOTE_FRAMES = 6`) but forgets to add it to `physics-schema.json`. Because the schema is now the source of truth, the old fallback path (hardcoded constant) doesn't exist anymore. The game crashes at startup with `KeyError: 'coyote_frames'`, or worse, the lookup returns `None` and silently becomes `0`, making the player feel unresponsive without any error.

**Why it happens:**
Inverting the source of truth removes the "Python has the value even if the JSON is wrong" safety net. Developers are used to `constants.py` being authoritative and update code first, schema second, and catch the mismatch at commit time. With inversion, code changes must be preceded by schema changes.

**How to avoid:**
1. Schema validation at load: every key referenced by `tuning.get_*` must resolve, or fail loudly at startup with the missing key name.
2. Introduce `tuning.require("movement.coyote_frames")` that raises with a clear message listing the schema file path and the missing key.
3. JSON schema (`physics-schema.schema.json`) validates `physics-schema.json` in CI — any required field missing fails the build.
4. Code review rule: any PR touching `tuning.get_*` must also touch `physics-schema.json` (enforce with a lint check that greps both files).

**Warning signs:**
- Startup works locally but fails for teammate who pulled schema from different branch
- "Player feels weird after the last commit" with no obvious gameplay change (silent `None` → `0`)
- Stack traces with `KeyError` in core loops
- Bisect lands on a commit that only touched Python, no schema change

**Phase to address:**
Phase 1 (schema inversion) — validation + require pattern. Every subsequent phase must pass the startup validator.

---

### Pitfall 5: Live-Tuning Panel Mid-Frame State Corruption

**What goes wrong:**
Player holds jump, panel is edited mid-flight, `JUMP_FORCE` writes to schema, the physics step on the *same frame* reads the new value, and the jump curve becomes a discontinuity — player teleports, clips through a ceiling, or ragdolls. Worse, values that get baked at state entry (`MAX_FALL_SPEED` captured at jump_start) diverge from values re-read every frame, producing nonsense trajectories.

**Why it happens:**
The natural implementation of a hot-reload panel is "writes go straight to the live dict." But physics is a stateful simulation where mid-frame value changes violate assumptions the integrator makes.

**How to avoid:**
1. **Double-buffer the tuning dict.** Panel writes to `tuning_pending`. At frame boundary (start of `update()`), `tuning_live = tuning_pending` is atomically swapped. Physics only reads `tuning_live`.
2. Never capture tuning values at state entry — always read at use site so values stay fresh without per-frame drift.
3. Panel widgets show the live value, not the pending value, after swap — so the user sees what physics sees.
4. For values that *should* persist through a motion (e.g., the jump arc uses the `JUMP_FORCE` at the moment of takeoff), capture explicitly: `self.jump_impulse_snapshot = tuning.JUMP_FORCE` at jump_start. Document which values are snapshotted vs. live.

**Warning signs:**
- "Panel freezes the game for 1 frame when I drag a slider"
- Player teleports when a slider is touched
- Value change takes effect "eventually" or "after I jump again" (inconsistent — some values are snapshotted, some live, no pattern)
- Crashes or clipping only reproducible while panel is open

**Phase to address:**
Phase 2 (live-tuning panel). Block on: physics simulation yields identical results frame-to-frame when the panel is open but values unchanged (bit-exact determinism test).

---

### Pitfall 6: Panel Input Bleed Into Gameplay

**What goes wrong:**
User types `2.5` in a slider input box. The `2` key is mapped to "swap weapon" in-game. Game consumes the key, swaps weapons, and the slider only sees `.5`. Or: user clicks a slider to grab it, click releases on the play area, player kicks a crate. Or: holding arrow keys to fine-tune a value causes the player to walk off a ledge in the background.

**Why it happens:**
Pyxel has no concept of UI focus — `pyxel.btn` / `pyxel.btnp` are global. Adding an imgui-style panel on top of gameplay means both the panel and the player poll the same input stream.

**How to avoid:**
1. Maintain a single `input_consumed_by_ui` flag checked at the start of gameplay input reading. When panel has "focus" (hover, drag, or text entry), flag is set, gameplay input reads return zero.
2. Pause the game while panel is in a text-entry mode — or give the panel a modal "pause" toggle that freezes time during edits.
3. Bind panel interactions to mouse only, never keyboard, so keyboard gameplay inputs never collide. Panel shortcuts (save preset, reset) use modifiers (`Ctrl+S`).
4. Draw the panel in a screen region that does not overlap the play area where possible (right gutter) — but still implement the focus flag because tooltips and dropdowns will spill.

**Warning signs:**
- "I changed a value and my player died"
- Player kicks / jumps when no one touched the gameplay controls
- Mouse clicks registering in both panel and gameplay
- Slider values jumping by integer steps (keyboard auto-repeat on arrow keys)

**Phase to address:**
Phase 2 (live-tuning panel). Success criterion: panel can be driven for 60 seconds with arbitrary inputs, and player position, velocity, and state remain unchanged from initial.

---

### Pitfall 7: Preset Save/Load "Stuck at Bad Values"

**What goes wrong:**
User tunes for an hour, finds a great set of values, crashes before saving. Or: saves a bad preset over the working baseline, loads it next session, doesn't realize, spends days tuning against broken baseline. Or: save format changes between panel revisions and old presets load as junk.

**Why it happens:**
Presets are the panel's "undo" system across sessions. If they're not robust, every crash loses work. If they're not diffable against a baseline, bad presets go undetected.

**How to avoid:**
1. **Auto-save every change to `tuning-autosave.json`** with timestamp. Keep last N (e.g., 20) autosaves. Recovery is always possible.
2. **Immutable baseline preset** — `tuning-baseline.json` represents the v1.3 shipping values and cannot be overwritten from the panel. Panel UI always shows "diff vs baseline" count so the user sees how far they've drifted.
3. **Version every preset file** with a `"schema_version"` key. On load, reject mismatched versions with a clear message; offer migration for minor bumps.
4. Panel "reset to baseline" button is one click, always available. One button away from a known-good state.
5. Checkpoint presets: label them (`"before-jump-redesign"`, `"fusion-pass-v1"`) so multi-day iteration can rewind.

**Warning signs:**
- "My values got wiped when Pyxel crashed"
- User can't articulate what changed since yesterday
- Preset files with no version field
- No "compare to baseline" UI element

**Phase to address:**
Phase 2 (live-tuning panel). Ship autosave + baseline diff as part of the panel, not as a follow-up.

---

### Pitfall 8: Slider Range Mismatch (Can't Reach Useful Values)

**What goes wrong:**
Slider for `MAX_WALK_SPEED` spans 0 to 5 because current value is 2. User wants to test 8 to evaluate weight feel. Slider won't go there. User edits JSON by hand. Panel out-of-sync with file. Tuning panel becomes "only useful for small deltas," which undermines the entire reason it exists.

**Why it happens:**
Default slider ranges are set from the current value ± some margin. Anyone doing a real "feel" pass needs to try values 2x–5x the current, including values that are clearly wrong (to understand the space).

**How to avoid:**
1. Declare `min`, `max`, `step` per field in schema metadata. Default to `[0, current * 4]` for floats, `[0, current * 4]` for ints, but **allow override**.
2. Support "unlocked mode" — a button that temporarily expands any slider to the full type range. The user opts in when exploring.
3. Log every value change to a tuning journal file so hand-edits show up as "external change detected" warnings in the panel.
4. Provide a numeric entry box next to every slider — slider for coarse, text entry for precise or out-of-range.

**Warning signs:**
- Developer editing `physics-schema.json` by hand while panel is open
- Sliders always hit their max during playtests
- "The panel doesn't let me try what I want"

**Phase to address:**
Phase 2 (live-tuning panel). Slider design must be validated with a 30-minute tuning session before the phase closes.

---

### Pitfall 9: Animation/Gameplay State Desync

**What goes wrong:**
Animation state machine listens for `jump_start` event, transitions to JUMP anim. Game state machine moves to AIRBORNE. But the player pressed JUMP while on a one-way platform, game vetoes the jump, animation never gets a corresponding "jump cancelled" event. Player is grounded, game says IDLE, anim says JUMP, and the jump frame is stuck on screen until the next transition triggers. User reports "sometimes the jump frame sticks."

**Why it happens:**
Event-based animation transitions assume every start has a matching end. Real game code has early-outs and vetoes everywhere. The animation state machine becomes a shadow state machine that drifts from the authoritative game state.

**How to avoid:**
1. **Animation state is derived from gameplay state, not parallel to it.** Each frame, the animation system reads `(player.state, player.velocity, player.facing, player.grounded)` and determines what animation *should* be playing. Events are for *transitions* (play a frame-1 anticipation sprite), not for driving state.
2. If event-driven is required, every `*_start` event has a matching `*_end` or cancel path, and the animation state machine has a "catch-up" rule: if the gameplay state doesn't match the anim state for 2+ frames, force anim to match.
3. Integrate a debug overlay showing `(game_state, anim_state)` side by side — desync is visible instantly.
4. Unit test: run the game for 10000 random inputs, assert gameplay state and anim state converge within 2 frames after every input.

**Warning signs:**
- "The jump animation sometimes stays on when I land"
- Developer adds a new gameplay feature and animation doesn't update
- Anim bugs only reproduce on specific terrain (one-way platforms, cracked blocks) where vetoes happen
- Fixing one anim bug creates another

**Phase to address:**
Phase 3 (animation state machine). Phase success criterion must include a gameplay-vs-anim convergence test.

---

### Pitfall 10: Transition Frame Non-Cancellable (Input Latency Regression)

**What goes wrong:**
"Transition frame insertion" — a 1-frame anticipation before a jump, a turnaround frame before direction change — adds polish. But if those frames are non-cancellable, the player has to wait for them to finish before the next input registers. Responsive controls that shipped in v1.0 suddenly feel laggy. The player can *see* the character acknowledge input but can't *interrupt* it.

**Why it happens:**
Transition frames are tempting to implement as "play this 1-frame animation, then execute the action." This moves the action to the frame *after* the input, introducing a minimum 1-frame input delay. At 60fps and for a platformer, 1 frame is perceptible and multiple stacked transitions (turn + jump + land) compound.

**How to avoid:**
1. **Physics executes on input frame; visuals lag.** The velocity change for a jump happens the frame the button is pressed. The anticipation sprite renders on top *without altering physics*. The player sees the squash frame but is already moving upward.
2. If you must delay physics (rare — e.g., a kick recovery), make the delay always cancellable by a higher-priority input (jump, dash). Document cancel priorities explicitly.
3. Measure input-to-response latency before and after the animation pass. Regression bar: no input must take more than the v1.3 baseline frame count to produce motion.
4. Record a "feel baseline" — a video and input log of v1.3 jumping, running, drilling — and replay on v2.0 to verify timing.

**Warning signs:**
- Playtester says "feels sluggish" after the animation pass even though code says it's not
- Input-to-movement frame count increased from baseline
- Players double-tap jump to "make sure" it registered
- New animations look beautiful but cause rage

**Phase to address:**
Phase 3 (animation state machine) must define physics-visual separation explicitly. Phase 6 (input responsiveness audit) must include a latency regression test vs. v1.3 baseline.

---

### Pitfall 11: Squash/Stretch Modifying Hit Volumes

**What goes wrong:**
Procedural squash/stretch scales the player sprite on landing / jumping. A naive implementation scales the collision hitbox along with it. Now the player's hitbox briefly extends below the floor on landing, clipping into a hazard tile, taking damage on every landing. Or the squash on jump lifts the hitbox 2 pixels, and the player can't pass under a ceiling they used to slide under.

**Why it happens:**
The "cleanest" squash implementation uses a sprite transform matrix applied to both draw and collision. Gameplay code and visual code share the same bounding box because that's how v1.0 was written.

**How to avoid:**
1. **Hitbox is constant. Visual transform is ornamental.** The collision box is the 10x14 rectangle defined in entity-schema. Squash/stretch only modifies a separate `visual_scale_x`, `visual_scale_y` used only by the blit call.
2. If you must vary hitbox (e.g., crouch), change it on game-state transitions (crouch_start → set hitbox to 10x8), not inside procedural animation.
3. Debug overlay: draw the collision box in a fixed color and the visual bounds in another. Any divergence during squash/stretch is immediately visible.
4. Regression test: snapshot pixel-perfect collision positions through a landing sequence, verify squash animation doesn't change collision results.

**Warning signs:**
- "I take damage every time I land near spikes"
- Player sometimes passes under a low ceiling, sometimes doesn't
- Hitbox debug overlay visibly breathes with the player sprite
- Collision bugs appear *after* the animation pass but existing level geometry is unchanged

**Phase to address:**
Phase 3 (animation state machine). Establish the "visual transform only" rule up front.

---

### Pitfall 12: Fusion Lifecycle Redesign Breaks Validated Ability Flows

**What goes wrong:**
Fusion activation is redesigned (V button, charge-to-fuse). During re-implementation, subtle behaviors that were correct in v1.1 break:
- Drill Dive no longer breaks cracked-V blocks (the block-break event was bound to the old activation path)
- Mana shield stops draining on hit (drain was attached to the old state-enter callback)
- Ram doesn't consume juice (consumption moved but costs weren't recalculated)
- Charge Shot charges while fused AND while unfused, double-drains

These are subtle because they pass unit tests (the *ability* still works), but fail integration (the *system* regressed).

**Why it happens:**
Fusion touches everything — juice, damage, abilities, collision, input. Redesigning the lifecycle means rewriting the spine. Each ability ties into the spine at a slightly different point. A clean rewrite tends to forget edge cases that the old spine accumulated over multiple bug fixes.

**How to avoid:**
1. **Document every existing fusion integration point before changing anything.** For each of the 6 abilities (ABL-01..06, minus 07), write a one-page "contract" describing: entry condition, state during, exit condition, juice cost, what breaks what, how damage interacts. Use this as the acceptance checklist.
2. Lock the fusion design doc **before** re-implementation starts. The research step is in the PROJECT doc — respect it.
3. Regression test suite: one scripted playthrough per ability, asserting key outcomes (drill breaks block, ram breaks horizontal, mana shield absorbs 1 hit, charge shot costs correct juice). Run every phase.
4. Do not delete the old fusion code until the new code passes all ability contracts. Keep old as `fusion_legacy.py` during transition, with a feature flag.

**Warning signs:**
- Ability unit tests pass but manual playthrough finds broken interactions
- A fusion ability "silently works" but juice isn't deducted / damage isn't applied
- Regressions discovered weeks later when the playtester uses an ability in a specific sequence
- No written contract for what each ability must do

**Phase to address:**
Phase 7 (fusion lifecycle design pass) — deliver the locked design doc and the ability contracts. Phase 8 (fusion re-implementation) — implement against the contracts and pass the regression suite.

---

### Pitfall 13: Save Format Incompatibility with v1.1 Saves

**What goes wrong:**
SYS-01 shipped JSON persistent saves in v1.1. v2.0 changes what's saved (new fusion state, new tuning references, new preset selection). A player who has a v1.3 save file loads it in v2.0 — game crashes on `KeyError`, or silently zeros out fields and the save is now broken. Prototype, but the user has been using the save system for months.

**Why it happens:**
Save migration is rarely designed up front. The save code is "whatever the fields were at time of shipping." New fields are added to `save()` and `load()` simultaneously, with no version field.

**How to avoid:**
1. Add a `save_version` field to save files now. Load path dispatches on version: `v1 → v2 migration` function handles missing fields with sensible defaults.
2. Test: keep a `test_save_v1_3.json` committed in the repo, verify it loads under v2.0 without error and with expected defaults.
3. Never remove fields. Deprecate with a comment, ignore on load, but keep reading them so downgrades also work.
4. If the save must be broken, show a migration prompt, not a crash: "This save is from v1.3, would you like to upgrade?"

**Warning signs:**
- `save.json` files with no version field
- Save loading code that uses `save["field"]` without `.get(field, default)`
- No test for loading old saves
- User reports "my save file doesn't work anymore"

**Phase to address:**
Phase 8 (fusion re-implementation) — if fusion state shape changes, add versioning in the same phase.

---

### Pitfall 14: Feel Tuning Has No Convergence Criteria

**What goes wrong:**
"Chase feel endlessly." The milestone never closes because "it doesn't feel right yet." Every new value creates new desires. Tuning sessions run for weeks without producing a shippable state. Or the opposite: the tuner declares victory on subjective feel, ships, and the playtester hates it.

**Why it happens:**
"Feel" is subjective. Without explicit exit criteria, there's no stop rule. Without comparison to a baseline, there's no way to know if "better" is better or just "different."

**How to avoid:**
1. **Record "feel targets" as testable micro-scenarios**, not vibes. Examples:
   - "Player can cross a 4-tile gap with a full jump and land exactly 1 tile into the far edge" → exact values
   - "Coyote frames allow a jump exactly 6 frames after walking off a ledge, 0 jump on frame 7"
   - "Drill Dive from 2 tiles up breaks exactly 1 cracked-V block"
   Each target is a pass/fail gate.
2. **A/B test harness**: press `F1` to swap between "current tuning" and "baseline tuning" live. Playtester compares without knowing which is which.
3. **Tuning journal**: every session logs what changed, why, subjective verdict. After 5 sessions, review — patterns ("every session I reduced gravity") reveal convergent direction.
4. **External playtester gate**: one external playtester must prefer the new tuning to the baseline on a blind A/B, with at least 3 of 5 feel targets.
5. **Time-box the tuning phase.** Target: 1 week per system (movement, slime, fusion). Hard stop at 1.5 weeks — ship the best-available and move on.

**Warning signs:**
- Phase runs 2x longer than estimate with "still tuning" as status
- "It feels worse now than last week" with no way to verify
- No written feel targets
- Playtester hasn't touched the build in 2 weeks

**Phase to address:**
Phase 5 (movement tuning), Phase 9 (ability feel pass). Each tuning phase ships with feel targets defined *up front*.

---

### Pitfall 15: A/B Comparison Is Impossible Without Infrastructure

**What goes wrong:**
Developer tunes for 3 hours, feels great, saves preset. Next day, tries to compare to yesterday's version by eye. Can't remember which values changed. Reverts one value at a time, each revert requires a mental reset of feel. A/B is effectively "reload the game with different values and try not to forget what the other one felt like."

**Why it happens:**
"A/B compare" is a tooling feature, not a workflow trick. Without infrastructure, comparison degrades to memory.

**How to avoid:**
1. **Two-slot preset compare.** Panel has slots A and B. User plays in A, hits a hotkey to snapshot to B, keeps tuning A, toggles between A and B with a single key. Brain-in-the-game comparison.
2. **Deterministic playback.** Record an input sequence (jump, dash, land, jump, turn, fall). Replay under preset A, then preset B, same initial conditions. Visual diff of where the player ends up is quantitative.
3. **Frame-level metric logging.** During a tuning session, log peak jump height, time to max speed, stopping distance, and compare across presets. Numbers cut through vibes.
4. **Video recording per preset.** Use Pyxel's built-in GIF capture (pyxel has `pyxel.screenshot`) — hotkey that captures 5 seconds of gameplay. Label with preset name.

**Warning signs:**
- "I think this is better but I'm not sure"
- Flipflopping between values across sessions
- No way to re-experience yesterday's tuning without manually re-entering values

**Phase to address:**
Phase 2 (live-tuning panel). A/B compare is a first-class feature of the panel, not a later addition.

---

### Pitfall 16: Juice for Juice's Sake (Screen Shake Everywhere)

**What goes wrong:**
Screen shake gets added to every impact: jumps, landings, kicks, hits, block breaks, enemy deaths, pickups, pause. The screen is constantly vibrating. Readability tanks. Players get motion sick. The *important* shakes (boss hit, drill impact) blend into the noise and lose weight.

**Why it happens:**
Juice is exciting. Once the system is built, every "impact moment" looks like a candidate. Over-application is the default failure mode. (See: Dead Cells, Downwell, Celeste — all of which carefully *limit* juice despite being able to use more.)

**How to avoid:**
1. **Juice budget.** Enumerate all "juice moments" and assign a level: NONE / SUBTLE / MEDIUM / BIG. Only the boss hit and drill impact earn BIG. Land without momentum = NONE. Land from a full-speed fall = SUBTLE. Document this before implementing.
2. **Shake trauma model** (from Jan Willem Nijman's "Art of Screenshake" talk): a single trauma variable that decays over time. New shakes add trauma, but the cap prevents pileups. Natural rate-limiting.
3. **Readability test**: can the player identify every enemy and tile type during a shake event? If not, reduce the shake.
4. **Comparison gate**: record v1.3 gameplay footage (no juice) alongside v2.0. If v2.0 obscures information v1.3 showed clearly, the juice went too far.

**Warning signs:**
- Playtester says "too much is happening"
- Developer says "more shake on everything"
- Jump + land + shoot all produce shake in the same half-second
- Camera is never still during normal gameplay

**Phase to address:**
Phase 10 (juice polish). Define the juice budget before implementation, not after.

---

### Pitfall 17: Hitstop Breaks Input Queuing

**What goes wrong:**
Hitstop (freezing the game for 2–5 frames on impact) is a classic feel boost. But if the game freezes including input processing, the player's press-during-hitstop gets lost. Combo inputs are dropped. The attack "eats" inputs and players feel the game stopped listening.

**Why it happens:**
Hitstop is typically implemented by pausing `update()`. All systems freeze, including the input buffer.

**How to avoid:**
1. **Input buffer keeps reading during hitstop.** Buffer presses, apply them on the frame after hitstop ends.
2. Only freeze physics and enemy AI, not input polling. Separate the pause domains.
3. Hitstop duration is short (2–4 frames max, at 60fps: 33–67ms). If longer, it's "slow motion," not hitstop, and needs different rules.
4. Test: during hitstop, press jump. Verify the jump fires on the first non-hitstop frame.

**Warning signs:**
- "I keep dropping combos after a hit"
- Jump pressed during enemy death doesn't register
- Hitstop is clearly freezing something it shouldn't

**Phase to address:**
Phase 10 (juice polish). Input buffer protection is part of the hitstop implementation, not separate.

---

### Pitfall 18: Pyxel Particle System Framerate Tank

**What goes wrong:**
Particles on every jump, land, kick, hit. Each particle is a `pyxel.pset` or `pyxel.rect`. At a few hundred active particles, 60fps drops. Pyxel is Python — rendering in a tight loop is expensive. The prototype, which ran smoothly through v1.3, stutters after juice is added.

**Why it happens:**
Particle systems are seductive. Developers think "it's just a few pixels." In Pyxel specifically, every draw call has overhead and there's no GPU batching.

**How to avoid:**
1. **Hard cap particle count.** Global cap, not per-emitter. E.g., 128 particles total. New particles evict oldest.
2. Profile at target particle density, not empty screen. Measure worst-case scenarios (boss fight + drill dive + multiple pickups).
3. Prefer short, punchy bursts (5 particles for 10 frames) over long trails (20 particles for 60 frames). Same visual impact, lower sustained load.
4. Pyxel-specific: `pyxel.pset` is faster than `pyxel.rect(x, y, 1, 1)`. Use it for single-pixel particles.
5. Framerate budget: v2.0 must maintain 60fps during worst-case combat. Measure this, don't assume.

**Warning signs:**
- FPS dips during combat that didn't exist in v1.3
- `pyxel.flip` time exceeds 16ms
- "Pyxel feels slow after the juice pass"

**Phase to address:**
Phase 10 (juice polish). Particle cap set in code, FPS test in phase success criteria.

---

### Pitfall 19: Sound Cues Firing Unpredictably

**What goes wrong:**
Sound is added to every gameplay event. Some fire every frame (walk sound plays 60 times/second). Others miss their trigger (jump sound only fires if velocity > threshold at the wrong frame). Players can't tell when they'll hear feedback. Audio becomes noise.

**Why it happens:**
Sound triggers are added as "when X happens, play sound Y." Without thinking about *how often* X happens, sounds fire every frame. Without thinking about *when exactly* X is measured, sounds miss.

**How to avoid:**
1. **Sound triggers off gameplay state transitions, not state.** `on_jump_start` plays the jump sound once. `is_jumping` does not.
2. **Debounce** repeatable sounds (step, hit) with a minimum interval — a walk sound can fire at most every 12 frames.
3. Pyxel has 4 sound channels. Reserve channels: ch0 = player actions (jump, land, kick), ch1 = enemy/impact, ch2 = ambient, ch3 = music. Channel discipline prevents sounds cutting each other off unpredictably.
4. Sound debug log: every sound fire logs `(frame, channel, sound_id, trigger)`. Scan after a session for 60-per-second fires.

**Warning signs:**
- Developer mentions "the walk sound is too loud" (actually: firing too often)
- Sound cutting out mid-play (channel collision)
- Jump sound missing 1 out of 3 times
- Audio describes "busy" or "grating"

**Phase to address:**
Phase 10 (juice polish). Sound channel map declared in code.

---

### Pitfall 20: Diagnostic Overlays Impact the Feel They Measure

**What goes wrong:**
Velocity overlay, hitbox overlay, input state visualizer are all drawn every frame via `pyxel.rect` and text. Each overlay costs frame time. When developer plays *with* overlays to diagnose feel, the game runs slower than it will ship. Tuning gets optimized for the overlay-on performance, and shipping game feels different than tuned game.

**Why it happens:**
Debug overlays are "free" until they're not. In Pyxel, every rectangle and text draw has non-trivial cost. Overlay-induced slowdown masks the actual feel.

**How to avoid:**
1. Profile overlays. If overlays cost >1ms, gate them behind F-key toggles and always test with overlays off before declaring feel "done."
2. One canonical "tuning mode" shortcut toggles panel + overlays together, "ship mode" turns them off. Tune → ship mode verify → tune → ship mode verify.
3. Render diagnostic text outside the play area (HUD strip) to avoid drawing order / layering confusion.
4. For heavy overlays (input trace, velocity graph), only draw when user holds a key, not every frame.

**Warning signs:**
- Feel differs with overlays on vs off
- Frame time jumps when a debug key is pressed
- Tuning feels great, playtest build feels different

**Phase to address:**
Phase 4 (diagnostic overlays). Overlay cost budget defined and tested.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Leave `constants.py` with real values, load schema "eventually" | Avoids the day-one inversion pain | Dual source of truth forever; tuning panel can't see the real values; converter contract unclear | Never — inversion must complete in Phase 1 |
| Skip preset versioning until "we have a stable format" | Ship panel faster | Every panel iteration breaks old presets; tuning work is lost | Never — version from day one, migration is cheap |
| Implement transition frames as "delay then act" | Matches how most tutorials show it | Input latency regression vs v1.3 baseline | Never — always decouple physics from visual |
| Animation events without cancel/end counterparts | Faster to add new anims | Anim state drifts from game state; ghost frames, stuck sprites | Never — every start needs an end or catch-up |
| Hand-editing physics-schema.json while panel is open | Fast path for values out of slider range | Panel writes clobber hand edits; developer confusion | Only with panel closed; otherwise add "external change detected" reload |
| Ship fusion redesign without regression tests for ABL-01..06 | Ships faster | Previously validated abilities silently break; discovered weeks later | Never — abilities must have contract tests |
| Uncapped particle pool | Simplest code | Framerate collapses during combat | Only during isolated feature work; cap before phase closes |
| Global screen shake on every impact | Easy to add, feels "juicy" | Readability gone, motion sickness, important hits lose weight | Only with explicit per-event shake level budget |
| Use v1.1 save format unchanged even when new fields are needed | No migration work | First save-invalidating change is a crash | Never — version saves from v2.0 onward |
| Tune by feel without feel targets | Feels like progress | Endless chase; no stop rule; ship subjective regression | Never — declare feel targets before tuning |

---

## Integration Gotchas

Common mistakes when connecting v2.0 systems to existing code and external tools.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `physics-schema.json` → pml-to-ldtk converter | Reshaping schema for panel UX without preserving flat reads | Version schema, keep flat form for converter or provide mirror, update CONVERTER-HANDOFF.md in same commit |
| `constants.py` → existing 50+ call sites | Rewriting `constants.py` to load JSON directly | Keep `constants.py` as a thin re-export from `tuning.py`; no call site changes |
| Tuning panel → physics step | Writing values directly to the live dict | Double-buffer: panel writes pending, frame boundary swaps live |
| Animation state machine → player state | Parallel state machine with its own events | Derive anim from game state + events as transition cues |
| Fusion redesign → ABL-01..06 | Assume unit tests cover integration | Write one-page contract per ability, regression playthrough suite |
| Save files → new fusion state | Add field, hope for the best | Add `save_version`, migration fn, load-old-save test |
| Squash/stretch → collision system | Scale both sprite and hitbox together | Separate `visual_scale` from `hitbox`, hitbox never transforms |
| Diagnostic overlays → tuning session | Tune with overlays on | Toggle overlays off for "ship feel" verification between sessions |
| Input buffer → hitstop | Pause all update() during hitstop | Pause physics/AI, keep input polling, apply buffered inputs on resume |
| Panel input → player input | Shared pyxel.btn reads | `input_consumed_by_ui` flag zeros gameplay input when panel has focus |
| Particle system → Pyxel draw budget | "Just a few pixels" assumption | Hard cap, profile worst case, prefer short bursts |

---

## Performance Traps

Patterns that work in isolation but degrade gameplay feel.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Uncapped particles | FPS drops during combat | Global cap (~128), oldest-evict policy | First boss fight + drill dive + pickups |
| `pyxel.rect` for single-pixel particles | Sustained slow draw | Use `pyxel.pset` for 1px particles | ~200+ particles |
| Animation system reads tuning dict every frame per entity | Minor slowdown scales with entity count | Cache lookups in the frame's physics step | Once multiple entities are animating (slime + player + enemies) |
| Diagnostic overlays always on during tuning | Feel differs ship vs dev | Toggle off between sessions, budget <1ms | During any heavy tuning session |
| Live-tuning panel redraws every frame regardless of change | Panel alone costs 2–3ms | Dirty-rect / redraw only on value change | When panel has 40+ sliders |
| JSON reload every frame for "hot reload" | 5–10ms per frame | Poll file mtime, reload only on change | With any file polling |
| Procedural squash math in Python per frame | Fine for 1 sprite, bad for many | Precompute scale lookup tables | Once enemies also squash |
| Sound debounce by checking every frame | Cheap but adds up | Event-driven, not polled | N/A — this one is usually fine, just watch the channel count |

---

## UX Pitfalls

Player-experience mistakes specific to a game-feel pass.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Tuning "responsiveness" by reducing input window | Feels twitchy, no coyote forgiveness | Tune responsiveness by reducing *output* latency (visual delay), keep input forgiveness |
| Adding squash/stretch that hides player frame | Player loses spatial awareness | Squash is subtle (10–20% max), never obscures silhouette |
| Drill Dive feels weighty by slowing down | Player waits for "their" input | Drill feels weighty by camera shake + sound + hitstop, not by input delay |
| Landing recovery frame that locks input | Player punished for successful landing | Recovery is always cancellable by directional input |
| Too-aggressive coyote time (10+ frames) | Feel cheap/forgiving | 4–6 frames is Celeste-range; more feels broken |
| Too-aggressive jump buffer (15+ frames) | Jump queues during running, unexpected jumps | 4–8 frames |
| Mana shield drain tied to damage frame, not swing-connect | Player takes damage they thought was shielded | Drain on incoming hit, not outgoing, and visually distinct |
| Fusion charge-to-fuse with no visual/audio feedback | Player can't tell charge state | Every charge frame has a visual tell; full charge has a distinct cue |
| Slime follow that catches up instantly | Breaks dual-hero feel, slime is "cheating" | Catch-up with acceleration curve; slime looks like it's *trying* |
| Bubble shield that silently deactivates | Player dies thinking shield was up | Shield down has audible + visual cue |

---

## "Looks Done But Isn't" Checklist

Things that appear complete in v2.0 but frequently ship broken.

- [ ] **Schema inversion:** Often missing converter contract test — verify pml-to-ldtk still reads physics-schema.json successfully
- [ ] **Schema inversion:** Often missing type declarations — verify `type(GRAVITY) is float` and `type(MAX_WALK_SPEED) is int` post-load
- [ ] **Schema inversion:** Often missing smoke test for empty/malformed schema — verify game fails loudly at startup with a readable error
- [ ] **Live-tuning panel:** Often missing input focus isolation — verify 60 seconds of panel interaction leaves player state unchanged
- [ ] **Live-tuning panel:** Often missing autosave — verify crash during tuning preserves last value
- [ ] **Live-tuning panel:** Often missing baseline preset — verify one-click reset to v1.3 values
- [ ] **Live-tuning panel:** Often missing A/B slot compare — verify two snapshots can be toggled without restart
- [ ] **Live-tuning panel:** Often missing slider range overrides — verify values can exceed current slider max through numeric entry
- [ ] **Animation state machine:** Often missing gameplay-state derivation check — verify anim state converges to game state within 2 frames under random input
- [ ] **Animation state machine:** Often missing physics/visual separation — verify input-to-movement latency unchanged from v1.3 baseline
- [ ] **Animation state machine:** Often missing transition-frame cancellability — verify next input interrupts any transition
- [ ] **Squash/stretch:** Often missing hitbox independence — verify collision results identical to non-squash build
- [ ] **Fusion redesign:** Often missing ability contracts — verify each of ABL-01..06 has a written contract with regression test
- [ ] **Fusion redesign:** Often missing legacy fallback — verify old fusion code is still runnable behind a feature flag until new passes all contracts
- [ ] **Fusion redesign:** Often missing juice-cost regression — verify each ability costs the same juice as v1.3 (unless design doc says otherwise)
- [ ] **Save compatibility:** Often missing version field — verify saves have `save_version: 2`
- [ ] **Save compatibility:** Often missing old-save test — verify a committed v1.3 save loads under v2.0
- [ ] **Tuning pass:** Often missing feel targets — verify each tuning phase has testable pass/fail criteria written before tuning starts
- [ ] **Tuning pass:** Often missing baseline comparison — verify A/B harness works
- [ ] **Tuning pass:** Often missing external playtest — verify at least one non-developer has played the build
- [ ] **Juice polish:** Often missing juice budget — verify every shake/particle/sound has a documented level (NONE/SUBTLE/MEDIUM/BIG)
- [ ] **Juice polish:** Often missing FPS test — verify 60fps during worst-case combat scenario
- [ ] **Juice polish:** Often missing input buffer through hitstop — verify jump during hitstop fires on first post-hitstop frame
- [ ] **Diagnostic overlays:** Often missing toggle discipline — verify "ship mode" test between tuning sessions
- [ ] **Input responsiveness audit:** Often missing v1.3 baseline — record input log from v1.3 and replay under v2.0 for direct comparison

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Schema inversion breaks startup | LOW | Revert to shim `constants.py` with values; reintroduce JSON load behind feature flag; fix missing fields; retry |
| Converter contract break | MEDIUM | Generate a flat-mirror `physics-schema-flat.json` from nested form as a build step; restore converter's expected read path |
| Type coercion drift | LOW | Add typed accessors `get_int`/`get_float`, rewrite call sites, add type assertions at load |
| Live-tuning mid-frame corruption | LOW | Add double-buffer swap at frame start; existing values unchanged |
| Missing schema value crash | LOW | Add `require()` with clear error; fix missing field in schema; add to CI validator |
| Panel input bleed | LOW | Add `input_consumed_by_ui` flag; zero gameplay input when set |
| Preset format regression | MEDIUM | Write migration function from old version; commit test preset of old format |
| Animation/gameplay desync | MEDIUM | Refactor anim as derived-from-game-state; add convergence test |
| Transition frame input latency | MEDIUM | Separate physics from visual; rewrite any "delay then act" transitions |
| Squash/stretch collision bug | LOW | Add `visual_scale` separate from hitbox; collision code reads hitbox only |
| Fusion redesign regression | HIGH | Keep legacy code behind flag; write ability contracts retroactively; each regression maps to a contract test |
| Save format break | HIGH | Add save migration from v1 to v2; ship with a "recover old save" flow; never delete v1.3 save format support |
| Tuning never converges | MEDIUM | Stop. Write feel targets. Resume tuning against targets only. Hard time-box |
| A/B compare not in panel | MEDIUM | Retrofit two-slot snapshot; requires panel rework but worth it |
| Screen shake overuse | LOW | Enumerate all shakes, set budget levels, remove unassigned shakes |
| Hitstop breaks input queue | LOW | Separate input polling from physics pause |
| Particle framerate tank | LOW | Add global cap with oldest-evict |
| Sound cue spam | LOW | Move from state-based to transition-based; add debounce table |
| Diagnostic overlay cost masking feel | LOW | Profile overlays, gate expensive ones behind hold-key, "ship mode" verify |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls. This table feeds directly into phase success criteria.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| 1. Schema inversion load order / circular imports | Phase 1 (schema inversion) | `python -c "import src.core.constants"` smoke test in CI |
| 2. Type coercion drift | Phase 1 (schema inversion) | Post-load type assertions; typed accessor lint |
| 3. Converter contract break | Phase 1 (schema inversion) | pml-to-ldtk read-path contract test; CONVERTER-HANDOFF.md updated |
| 4. Missing-value startup crash | Phase 1 (schema inversion) | Required-field validator at load; JSON schema file |
| 5. Live-tuning mid-frame corruption | Phase 2 (live-tuning panel) | Frame-boundary swap; determinism test with panel open |
| 6. Panel input bleed | Phase 2 (live-tuning panel) | 60s panel interaction leaves player state unchanged |
| 7. Preset stuck at bad values | Phase 2 (live-tuning panel) | Autosave file + immutable baseline + version field |
| 8. Slider range mismatch | Phase 2 (live-tuning panel) | 30-min tuning session report before phase close; numeric entry box present |
| 9. Animation/gameplay desync | Phase 3 (animation state machine) | Convergence test: anim state matches game state within 2 frames under random input |
| 10. Transition frame input latency | Phase 3 (animation state machine) + Phase 6 (input audit) | Input-to-movement latency <= v1.3 baseline |
| 11. Squash/stretch modifying hitbox | Phase 3 (animation state machine) | Collision position regression test through landing sequence |
| 12. Fusion redesign regressions | Phase 7 (fusion design pass) + Phase 8 (fusion re-implementation) | ABL-01..06 contract tests; legacy code flag until all pass |
| 13. Save format incompatibility | Phase 8 (fusion re-implementation) | Committed v1.3 save loads under v2.0 test |
| 14. Feel tuning no convergence | Phase 5 (movement tuning), Phase 9 (ability feel pass) | Written feel targets before tuning starts; time-box; external playtest gate |
| 15. No A/B compare infrastructure | Phase 2 (live-tuning panel) | Two-slot snapshot hotkey; determinism replay harness |
| 16. Juice-for-juice's-sake | Phase 10 (juice polish) | Juice budget document; shake trauma model; readability test |
| 17. Hitstop breaks input queue | Phase 10 (juice polish) | Jump-during-hitstop fires on first post-hitstop frame |
| 18. Pyxel particle framerate tank | Phase 10 (juice polish) | Global particle cap; 60fps worst-case combat test |
| 19. Sound cues unpredictable | Phase 10 (juice polish) | Sound channel map; transition-triggered fires; debounce table |
| 20. Diagnostic overlays affect feel | Phase 4 (diagnostic overlays) | Overlay cost budget <1ms; ship-mode verify between sessions |

---

## v1.0–v1.3 Regression Risk Register

**Everything that could silently regress.** Every phase must verify these still work.

| Validated Requirement | Risk From | How To Verify Still Works |
|-----------------------|-----------|---------------------------|
| MOV-01 walk/jump/wall slide | Schema inversion type drift; movement tuning | Scripted playthrough: 4-tile gap, wall kick, wall slide descent |
| MOV-03 kick | V button rebind; fusion redesign | Kick a crate, switch hit, kick enemy — all register |
| SLM-01 slime follow | Slime AI tuning pass | Slime catches up within N frames after warp; doesn't stick on walls |
| SLM-02 juice system | Fusion redesign juice-cost refactor | Each ability deducts same juice as v1.3 unless design doc says otherwise |
| DRILL-01/02 Drill Dive | Fusion redesign; squash collision bug | Drill from 2 tiles up breaks exactly 1 cracked-V block; path through a corridor |
| BOSS-01 Giant Mole | Any fusion or ability change | Full boss fight playthrough; stun windows work; final drill lands |
| MAP-01..04 rooms + persistence | Schema or save format changes | Save, reload, verify room state restored |
| ABL-01 Slime Ram horizontal gate | Fusion redesign | Ram breaks cracked-H block |
| ABL-02 CRACKED_V gating | Fusion redesign | Drill Dive + Slime Boost both break cracked-V |
| ABL-03 Directional Hold | Fusion redesign | Hold in 4 directions, each fires |
| ABL-04 Charge Shot | Fusion redesign charge-to-fuse collision | Charge, release, projectile fires at expected damage |
| ABL-05 Bubble Shield | Mana shield pattern change | Shield absorbs exactly 1 hit, drains exactly expected juice |
| ABL-06 Double Jump | Jump buffer / coyote tuning | Double jump still works at current air frame |
| SYS-01 saves/checkpoints | Fusion state shape change | v1.3 save loads in v2.0 without crash |
| SYS-03 pause macro-map | Panel input bleed | Pause while panel open still behaves |
| SCHEMA-01..04 unified schema | Schema inversion | Schema structure used by schema.py still valid |
| TILE-01..06 autoLayerTiles | None — visual only | Visual check: rooms still render |
| GRID-01..04 16x16 tiles | None — upstream from tuning | Tile math unaffected |
| PHYS-01..03 16x16 physics tuning | Movement tuning pass | Scripted playthrough matches v1.3 jump distances |

**Regression gate:** Every phase must run the regression checklist or a scripted version of it before phase completion. No phase closes with a regression outstanding.

---

## Sources

- **GMTK Platformer Toolkit** (game-feel.net / Game Maker's Toolkit) — the reference live-tuning panel this milestone is modeled on; demonstrates A/B compare, preset slots, and feel-targets-as-scenarios. HIGH confidence: directly cited by PROJECT.md.
- **Jan Willem Nijman — "The Art of Screenshake"** (Vlambeer talk) — trauma model, juice budget, readability-first approach. HIGH confidence: canonical source for game-feel shake discipline.
- **Celeste post-mortem + Matt Makes Games design notes** — coyote frames (6), jump buffer (5–6), variable jump implementation, physics/visual separation. HIGH confidence: public Maddy Thorson posts and open-source Celeste code.
- **Downwell dev notes** — minimal-particle-maximum-impact principle. MEDIUM confidence: community-sourced.
- **Pyxel documentation** (pyxel_info) — draw call costs, channel limits, frame timing. HIGH confidence: official docs.
- **STATE.md accumulated context** — current state of `constants.py`, schema versioning, converter handoff, ~50 tuning values, animation primitiveness. HIGH confidence: first-party project context.
- **MILESTONES.md** — validated requirements list for regression risk register. HIGH confidence: first-party.
- **Common platformer post-mortems** (various jam and indie dev blogs) on save migration, mid-frame physics corruption, animation state drift. MEDIUM confidence: aggregated community wisdom.

---

*Pitfalls research for: Jelly Roll Proto v2.0 Game Feel milestone*
*Researched: 2026-04-11*
