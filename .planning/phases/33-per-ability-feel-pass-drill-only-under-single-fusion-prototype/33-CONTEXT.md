# Phase 33: Per-Ability Feel Pass (Drill-Only under single-fusion prototype) - Context

**Gathered:** 2026-04-27
**Status:** Ready for planning (gated on FUSION-DESIGN re-lock — see Pre-phase Hard Gate)

<domain>
## Phase Boundary

Retune drill-dive against the new lifecycle (windup → sustain → end) using the live panel; give drill a distinct particle + SFX identity that differentiates it from spit and the new daze shot; light-touch pogo retune; introduce the **destructive-drill** mechanic (drill damages enemies on contact, enemies drain juice on hit, drill continues through). Per-ability identity reduces to drill identity under the single-fusion prototype, with pogo as a sibling FusionAbility receiving panel-tunable values but no formal feel-targets table.

**Pre-phase Hard Gate — FUSION-DESIGN re-lock required before /gsd-plan-phase 33.** The destructive-drill mechanic (drill deals damage to enemies, drains juice per hit, continues through enemy clusters) expands the locked Drill-Dive Contract beyond tile interaction. FUSION-DESIGN.md must be UNLOCKed → Drill-Dive Contract amended with an enemy-interaction subsection (DRILL_DAMAGE, DRILL_ENEMY_COST, continue-through rule, exit conditions unchanged) → RELOCKed with new locked_commit SHA via the documented two-commit dance, BEFORE Phase 33 PLAN.md is authored. Recommend `/gsd-insert-phase` to create `32.5-fusion-design-destructive-drill-relock` as the formal hard-gate phase, OR a user-supervised manual two-commit dance.

**Out of scope (other phases):**
- Camera shake, pooled particles capped at ~128, gameplay hitstop with input-buffer protection, full sound channel map with debounce — Phase 35.
- Slime follow/AI feel pass — Phase 34.
- Final shipping preset bake + v1.0–v1.3 regression playthrough — Phase 36.
- Pogo feel-targets table — deferred to a future phase if light retune proves insufficient.
- Reintroduction of any of the five cut abilities — post-prototype.
- F2-F5 diagnostic overlays (Phase 27 still TBD; Phase 33 does not depend on them).

</domain>

<decisions>
## Implementation Decisions

### Tuning surface expansion

- **D-01:** **Migrate WINDUP_DURATION_FRAMES (30) and ACCELERATED_REGEN_RATE (1.0) from `src/fusion/charge_controller.py:33-34` into `assets/physics-schema.json`** so the panel surfaces both as live sliders. Both are FUSION-DESIGN draft values that Phase 33 must validate via playtest. Schema-group placement (extend `fusion` group vs. new `fusion_charge` group) is planner discretion.
- **D-02:** **Migrate POGO_BOUNCE_VELOCITY and POGO_COOLDOWN_FRAMES from `src/fusion/pogo.py:30-32` into `physics-schema.json`** under a new `pogo` group (or extension of an existing group — planner picks). Keep `POGO_INITIAL_DY = 2.0` hardcoded (must match `DRILL_SPEED` for visual parity per the Mario-64 ground-pound mental model — changing it desyncs the gesture). Keep `POGO_DAMAGE = 1` hardcoded (gameplay constant; see D-04 below for symmetric treatment).
- **D-03:** **Drill becomes destructive on enemy contact.** This replaces the FUSION-DESIGN Open-Q #1 iframes question entirely. Drill in flight that intersects an enemy AABB:
  - Deals damage to the enemy (does NOT take damage from the enemy).
  - Continues through the enemy (no exit, no bounce, no hitstop). Same passthrough behavior as soft destructibles.
  - Drains juice per hit per the cost model in D-05.
  - Mana shield path becomes irrelevant during DIVING since enemies cannot damage the drilling player.
- **D-04:** **DRILL_DAMAGE = 1 per hit (same as POGO_DAMAGE).** The "upgrade" relative to pogo is structural, not numeric: drill's 2px/frame plunge means a multi-tile-tall enemy gets hit ~7 times during a single drill chain, so drill out-damages pogo via repeated-frame contact. Cleanest semantics. Whether DRILL_DAMAGE moves to schema or stays as a module constant in `drill_dive.py` is planner discretion (schema if you want panel-tunable, hardcoded for stability — recommendation: hardcoded constant, since 1 is a gameplay choice not a feel choice).
- **D-05:** **Enemy-hit cost model = DRAIN, analog to CRACKED_V cost.** New tunable `DRILL_ENEMY_COST` in physics-schema.json (drill group) consumes juice per enemy hit. Phase 33 picks the value via panel iteration — start in the 10–20 range. Naturally caps drill chains; enemies become "tough destructibles you spend juice to kill." Reads as "killing enemies via drill takes resource."
- **D-06:** **No drill iframes knob.** With D-03's destructive-drill rule, drill cannot take damage during DIVING (enemies are damaged, not damaging). The FUSION-DESIGN Open-Q #1 invulnerability question is resolved by the design pivot — drill's safety comes from offense, not invulnerability.
- **D-07:** **Tap/hold threshold (`SPIT_HOLD_THRESHOLD = 16` → ~8 target)** is already in tuning (fusion group, panel-exposed). Phase 33 retunes the live value; no migration work needed. Validation target ~8f per FUSION-DESIGN Z input model.

### Test setup & feel-target format

- **D-08:** **Author `33-FEEL-TARGETS.md` mirroring `29-FEEL-TARGETS.md`** — pass/fail table with falsifiable spatial/timing tests, sign-off-driven. Coverage areas: tap/hold ~8f threshold (Z disambiguation feel); WINDUP cancel-window feel (~30f draft); accelerated-regen ritual time (2× passive draft); drill chain length on full juice; juice-starvation Exit (b) trigger; **enemy kill chain through 3+ enemies (new — destructive-drill validation)**; enemy-cost balance against the boss daze→drill loop (PROJECT.md combat fantasy); pogo confirm-only entry (FUSION-DESIGN D-04 rules unchanged after destructive-drill addition).
- **D-09:** **Test in existing `Level_0`–`Level_8`.** Extend Phase 29's debug-warp hotkeys with drill-relevant warp targets: CRACKED_V column room, soft-destructible floor room, enemy-cluster room, juice-drain hazard room. No new dedicated test level. Phase 29 set this precedent (29-CONTEXT D-05 had proposed a dedicated `Level_Test`, but the actual phase used existing levels — Phase 33 inherits the simpler pattern).
- **D-10:** **Tuning order: charge ritual → drill physics → drill combat → pogo.** Phase 29-style layered approach (low-coupling first):
  1. Charge ritual (windup, accel-regen, tap/hold threshold) — panel-only, no level dependency.
  2. Drill physics (DRILL_SPEED, DRILL_DRIFT_SPEED, per-block costs/refunds) — test in CRACKED_V column + soft-block rooms.
  3. Drill combat (DRILL_ENEMY_COST, kill chains, boss daze→drill loop) — test in enemy-cluster room + against existing boss.
  4. Pogo (BOUNCE_VELOCITY, COOLDOWN) — light retune, last.
- **D-11:** **Bake final values into existing `assets/presets/v2.0-default.json`.** No new preset slot. v1.3-reference stays frozen as A/B regression baseline. Phase 36 owns the milestone-cap final preset bake — Phase 33 contributes drill+pogo+charge values into the same v2.0-default file Phase 29 wrote movement values into.

### Drill identity (particle + SFX)

- **D-12:** **Build minimal `src/core/audio.py` module** with `pyxel.sounds[N].set()` definitions + a `play_sfx(name)` wrapper. Phase 35 inherits and extends with the full sound channel map / debounce rules. Phase 33's audio surface stays bounded.
- **D-13:** **5 audio cues + daze-fire = 6 total** for Phase 33's identity work:
  - `fuse_start` — commit chime at WINDUP→FUSED latch (FUSION-DESIGN-locked event).
  - `drill_start` — windup whir at drill activate (FUSION-DESIGN-locked event).
  - `drill_block_break` — per-tile crunch (FUSION-DESIGN-locked event).
  - `drill_enemy_hit` — **NEW event** added by Phase 33 for symmetric particle + SFX handling on enemy contact during drill (per D-03). Fired from `drill_dive.py:on_tick` when enemy AABB intersects.
  - `drill_impact` — Exit (a) thud on solid landing (FUSION-DESIGN-locked event).
  - `daze_fire` — fused-tap-Z projectile (per D-17 daze shot scope).
- **D-14:** **Particle differentiation via new sprite cells in bank 2** (`assets/sprites/particles.png`) + type-arg routing in `main.py:spawn_particle_burst(type=...)`. Phase 31 reserved the `type` arg but routed all variants to one cell — Phase 33 actually uses it. New cells needed: drill block-break (orange/brown shrapnel), drill enemy-hit (combat-flavored variant), daze-shot splat (blue/green to differentiate from spit).
- **D-15:** **Drill claims the earthbound palette: pyxel colors 4 (brown), 9 (orange), 10 (yellow).** Avoids slime/spit/daze-green and kick-blue. Reads as "earth being broken" — fits drill's tile-carving identity. Specific (u, v) coordinates for new bank 2 cells are planner discretion within Phase 31's existing layout.
- **D-16:** **`drill_enemy_hit` event** is wired symmetrically with the other drill events (particle + SFX subscribers in `Game.__init__` per Phase 31 Pitfall 5). Phase 35 extends the subscriber for hitstop/shake — Phase 33 wires only particle + SFX.
- **D-17:** **Daze shot (fused-tap-Z) implementation in scope for Phase 33.** Per FUSION-DESIGN D-14, daze reuses the spit code path. Phase 33 work:
  - Remove the `not self.is_fused` gate at `src/entities/player.py:197` so spit fires regardless of fusion state.
  - When fused, fire branches: consume `SLIME_DAZE_COST` (new tunable in `slime_juice` schema group) and apply daze-on-hit effect.
  - Daze-on-hit effect: stuns enemies briefly (reuse existing boss stagger logic where present; new stun primitive on regular enemies is planner discretion — may stay TBD if the existing logic isn't reusable).
  - Audio + particle identity for daze (D-13, D-14, D-15) bundled into the same Phase 33 work.

### Pogo feel-pass scope

- **D-18:** **Light pogo retune only.** Pogo gets the panel-tunable values from D-02 but **no entries in 33-FEEL-TARGETS.md** beyond a single confirm-only target ("FUSION-DESIGN D-04 rules still hold after destructive-drill addition"). Tune pogo via panel iteration in step 4 of the tuning order (D-10). Phase title "Drill-Only" stays the headline; pogo gets the minimum it needs to ride along.
- **D-19:** **Pogo enemy-contact rules unchanged.** FUSION-DESIGN D-04 (Shovel Knight shovel-drop style: bounces on enemies + breakables, lands without bounce on solid ground) and Phase 32 D-19 stay authoritative. The destructive-drill rule (D-03) does NOT propagate to pogo — pogo bounces, drill drills.
- **D-20:** **Minimal pogo identity — one new SFX cue, no new particle.** Add `pogo_bounce` to `audio.py` (springy/bouncy sound, distinct from `drill_impact` thud). No new particle cell — pogo bounces are short and frequent, particles would litter the screen. Differentiates the gesture audibly which satisfies the "blindfolded observer" success criterion implicitly extended to pogo.

### Pre-phase hard gate — FUSION-DESIGN re-lock

- **D-21:** **`.planning/FUSION-DESIGN.md` must be re-locked BEFORE `/gsd-plan-phase 33` runs.** The destructive-drill mechanic (D-03 / D-04 / D-05) expands the locked Drill-Dive Contract beyond pure tile interaction. Re-lock workflow per FUSION-DESIGN § Lock Protocol Re-lock Policy:
  1. UNLOCK: change frontmatter `status: LOCKED` → `status: UNLOCKED`.
  2. Add a new "Enemy Interaction" subsection to § Drill-Dive Contract documenting D-03 (continue-through), D-04 (DRILL_DAMAGE = 1), D-05 (DRILL_ENEMY_COST drain model). Cite Phase 33 33-CONTEXT.md as the design source.
  3. Re-lock via two-commit dance: doc-write commit, then frontmatter amendment with new `locked_commit` SHA. Update `prior_locked_commit` to the current `9047b590...` value.
  4. Bump or annotate FUS-03 contract reference if the requirement statement needs to mention enemies.
- **D-22:** **Recommended re-lock vehicle: `/gsd-insert-phase` to create `32.5-fusion-design-destructive-drill-relock`** as a 1-plan phase that does only the re-lock work. Analog to Phase 31.5's hard-gate framing. Alternative: user-supervised manual two-commit dance with no formal phase wrapper. Either is acceptable; the invariant is that Phase 33's planner reads the *new* `locked_commit` SHA (not the current `9047b590...`) when verifying the contract.

### Claude's Discretion

- Schema-group placement for migrated values (extend `fusion` and `drill` groups vs. new `fusion_charge` and `pogo` groups).
- Whether `DRILL_DAMAGE` and `DRILL_ENEMY_COST` live as schema entries or as module constants in `drill_dive.py` (recommendation: DAMAGE hardcoded, COST in schema for live tuning).
- Specific (u, v) coordinates for new bank 2 particle cells within Phase 31's existing `particles.png` layout.
- Specific MML strings or `pyxel.sounds[N].set()` parameters for each of the 6 audio cues — feel choice, picked during implementation.
- Whether 33-FEEL-TARGETS.md gets sign-off BEFORE tuning starts (Phase 29 did this) or AFTER (Phase 29 evolved targets during tuning then signed off at end).
- Number of feel targets in 33-FEEL-TARGETS.md (~10–15 mirrors Phase 29; smaller is fine if drill has fewer dimensions).
- Daze-on-hit stun primitive: reuse existing boss stagger logic, or add a new generic enemy stun. Depends on how reusable the boss-specific logic is.
- Behavior when DRILL_ENEMY_COST > remaining juice (clamp juice to 0 mid-frame and trigger Exit b, or finish the hit then check on next frame). Planner picks based on event-emission ordering preferences.
- Whether `drill_enemy_hit` subscribes for hitstop in Phase 33 or only for particle/SFX (recommendation: particle/SFX only; Phase 35 owns hitstop).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Locked design contracts — read first

- `.planning/FUSION-DESIGN.md` — **PHASE 33 PLANS AGAINST THE NEW SHA, NOT 9047b590...** Per D-21, FUSION-DESIGN must be re-locked with a destructive-drill subsection BEFORE Phase 33 PLAN.md is authored. Read the §Drill-Dive Contract (parity invariants), §Fusion FSM (event names — Phase 33 must not rename existing events), §Juice Economy (cost model templates that DRILL_ENEMY_COST follows), §Lock Protocol §Re-lock Policy (the workflow Phase 33 triggers).

### Requirements & Roadmap

- `.planning/ROADMAP.md` §Phase 33 — Goal, dependencies (Phase 32 refactor + Phase 28 panel + Phase 31 animation/particle bank), success criteria (FUS-06 implicit). NOTE: ROADMAP success #3 says "three exit conditions" — this is stale (FUSION-DESIGN locks two; manual exit removed 2026-04-20). Trust FUSION-DESIGN.

### Prior phase context

- `.planning/phases/32-fusion-manager-protocol-refactor/32-CONTEXT.md` — Read D-09 (FusionAbility Protocol shape), D-10 (per-frame physics ownership), D-12 (event emission per ability), D-18 (pogo tuning explicitly deferred to Phase 33), Deferred Ideas (drill i-frames flagged for Phase 33).
- `.planning/phases/30-fusion-lifecycle-design-doc/30-CONTEXT.md` — Scope-pivot rationale; Open-Q #1 (drill iframes baseline = NONE); Open-Q #5 (accel regen 2× draft).
- `.planning/phases/31-animation-content-particle-bank-separation/31-CONTEXT.md` — Bank 2 layout, sprite-backed Particle, BlobGrowth tier-2 wrapping; subscriber wiring in `Game.__init__` (Pitfall 5).
- `.planning/phases/29-player-movement-feel-pass/29-CONTEXT.md` — Feel-pass precedent (D-01 to D-10); test-room pattern; preset capture pattern.
- `.planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md` — 33-FEEL-TARGETS.md template/format reference (ID + Test + Pass + Fail columns, sign-off-driven).

### Code — primary modification targets

- `src/fusion/charge_controller.py:33-34` — `WINDUP_DURATION_FRAMES = 30` and `ACCELERATED_REGEN_RATE = 1.0` constants, both migrating to schema per D-01.
- `src/fusion/pogo.py:28-33` — `POGO_INITIAL_DY = 2.0` (keep hardcoded, D-02), `POGO_BOUNCE_VELOCITY = -2.5` (migrate, D-02), `POGO_COOLDOWN_FRAMES = 0` (migrate, D-02), `POGO_DAMAGE = 1` (keep hardcoded, D-02).
- `src/fusion/drill_dive.py` — `on_tick` per-frame physics. Phase 33 adds enemy AABB intersection detection + DRILL_ENEMY_COST consume + DRILL_DAMAGE damage + `drill_enemy_hit` event emit (D-03/D-04/D-05/D-13).
- `src/entities/player.py:197` — `if input_manager.was_tap("spit", tuning.SPIT_HOLD_THRESHOLD) and not self.is_fused and self.state != "DIVING":` — remove the `not self.is_fused` gate per D-17 daze shot scope; add fused-branch with SLIME_DAZE_COST and daze-on-hit effect.
- `src/anim/event_bus.py` — Add `drill_enemy_hit` event (D-13). Existing events `drill_start`, `drill_block_break`, `drill_impact`, `fuse_start` stay as-is.
- `main.py:Game.__init__` (around line 282 + the fuse-flash subscriber block ~line 320) — Wire new event subscribers for `drill_enemy_hit` (particle + SFX), `pogo_bounce` (SFX only). Hoist all subscribers to `Game.__init__` per Pitfall 5.
- `main.py:941 spawn_particle_burst(x, y, type="block_break")` — Implement type-arg routing per D-14: dispatch table from type name to (u, v) bank-2 sprite coordinates.
- `src/core/audio.py` — **NEW MODULE** per D-12. `pyxel.sounds[N].set()` definitions for 7 cues (5 drill events + daze_fire + pogo_bounce per D-13/D-20) + `play_sfx(name)` wrapper.
- `src/ui/panel.py` — TAB_DEFS already has "Fuse" tab covering drill+fusion groups. New schema groups (if planner picks new groups for D-01/D-02 migrations) need TAB_DEFS extension.

### Assets & Schemas

- `assets/physics-schema.json` — New keys per D-01 (WINDUP_DURATION_FRAMES, ACCELERATED_REGEN_RATE), D-02 (POGO_BOUNCE_VELOCITY, POGO_COOLDOWN_FRAMES), D-05 (DRILL_ENEMY_COST), D-17 (SLIME_DAZE_COST). Optionally D-04 (DRILL_DAMAGE) if planner moves it to schema.
- `assets/presets/v2.0-default.json` — Phase 33 final values bake in here per D-11. Phase 29 already wrote movement values; Phase 33 adds drill/pogo/charge/daze values.
- `assets/presets/_v1.3-reference.json` — **FROZEN.** Drill values stay at v1.3 baseline for A/B regression. Phase 33 does NOT modify this file.
- `assets/sprites/particles.png` — Bank 2 sprite sheet. New cells needed per D-14 (drill block-break, drill enemy-hit, daze splat). Layout coordinates planner discretion.

### Out-of-scope references (do NOT implement in Phase 33)

- Camera shake values, hitstop input-buffer protection, pooled-particle cap of ~128, full sound channel map with debounce — all Phase 35.
- Slime follow/AI tuning — Phase 34.
- Final shipping preset bake + v1.0–v1.3 regression playthrough — Phase 36.
- Reintroduction of any cut ability — post-prototype.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`src/ui/panel.py` "Fuse" tab** — Already exposes `drill` and `fusion` schema groups. New tunables from D-01/D-02/D-05/D-17 land here automatically once added to schema (TAB_DEFS may need extension if new groups are introduced).
- **`src/entities/effects.py:Particle`** — Sprite-backed particle from bank 2; Phase 33 reuses by passing new `(bank_u, bank_v)` per type-arg dispatch.
- **`main.py:spawn_particle_burst(x, y, type=...)`** — Type arg already reserved; Phase 33 implements the dispatch table.
- **`src/anim/event_bus.py`** — Standard subscribe/emit primitive. Phase 33 adds one new event (`drill_enemy_hit`).
- **`src/fusion/drill_dive.py:on_tick` collision loop** — Already iterates per-frame for tile collision; Phase 33 extends with enemy-AABB intersection check.
- **Phase 29 debug-warp hotkeys** — Existing infrastructure for jumping to specific levels during playtest. Phase 33 extends with drill-relevant warp targets.
- **`tuning.py:set_value` + panel slider plumbing** — Phase 24/25/28 pipeline already in place; new tunables get live-edit reach for free.

### Established Patterns

- **Use-site tuning reads** (Phase 25) — Drill values read at use-site (`tuning.DRILL_SPEED`, etc.). Phase 33 preserves; new tunables follow same pattern.
- **No magic numbers** (MEMORY feedback) — Every new constant in Phase 33 (DRILL_ENEMY_COST, SLIME_DAZE_COST, audio cue parameters) needs a named constant. Co-located in its owning module.
- **Event bus is side-channel** (Phase 26 D-00b, MEMORY) — Phase 33's new `drill_enemy_hit` event mirrors gameplay; it does NOT drive gameplay FSM. The damage + cost happen in `drill_dive.py:on_tick`; the event emission is a side effect.
- **`event_bus` subscriber wiring in `Game.__init__`** (Phase 31 Pitfall 5) — Phase 33's new subscribers must be hoisted to `Game.__init__`, not subscribed mid-frame or in `Player.__init__` (which runs every reset and would accumulate subscribers).
- **Phase 29 feel-targets format** — `29-FEEL-TARGETS.md` is the template. Pass/fail table; sign-off after every target passes; v1.3 baseline is the A/B reference.
- **Pyxel audio API** — `pyxel.sounds[N].set(notes, tones, volumes, effects, speed)` or `.mml(string)` for definition; `pyxel.play(channel, sound_id)` to fire. Phase 33's `audio.py` wraps both.

### Integration Points

- **`Game.__init__`** — Wire new subscribers for `drill_enemy_hit` and `pogo_bounce`; instantiate audio module if it exposes setup state.
- **`Player.handle_input`** — Spit/daze gate change at `player.py:197`. Daze branch consumes `SLIME_DAZE_COST` and applies daze-on-hit when fused.
- **`drill_dive.py:on_tick`** — Add enemy-AABB intersection scan; on hit, consume DRILL_ENEMY_COST, deal DRILL_DAMAGE, emit `drill_enemy_hit`, continue drill. Watch ordering: do this BEFORE the soft-block / CRACKED_V destructibles scan if you want enemies to take precedence; AFTER if tiles dominate. Planner picks; tile-first feels closer to Phase 32 v1.3 parity.
- **`physics-schema.json`** — New tunables per D-01/D-02/D-05/D-17. Schema-group placement is planner discretion.
- **Panel TAB_DEFS** — Extend if new schema groups are introduced. Existing "Fuse" tab can absorb extensions to existing groups.

### Known Constraints

- **FUSION-DESIGN locked SHA dependency.** Phase 33's planner verifies the *new* `locked_commit` SHA (after re-lock per D-21) before authoring PLAN.md. Verifying the *current* SHA `9047b590...` is wrong because the destructive-drill subsection won't be there yet.
- **v1.3 parity for tile interaction.** Phase 33 is permitted to retune drill values via the panel, but the Phase 30 Drill-Dive Contract behavioral invariants (two exit conditions, per-tile cost/refund pattern, mana shield rule, no mid-drill cancel) MUST hold. The destructive-drill addition is an *expansion* of the contract, not a contradiction.
- **Phase 31 event names are a contract.** Renaming `drill_start`, `drill_block_break`, `drill_impact`, `fuse_start` would silently break Phase 31 animation. Phase 33 only ADDS `drill_enemy_hit` and `pogo_bounce`; it does NOT rename existing events.
- **Panel slot count.** Phase 28's panel has limits on slider count per tab. New tunables should fit within the existing "Fuse" tab; if exceeded, planner adds a "Pogo" or "Charge" sub-tab (panel.py TAB_DEFS extension).
- **Bank 2 sprite budget.** Phase 31 already populated some `particles.png` cells; Phase 33's new cells must fit within the remaining capacity. Planner verifies the layout before committing to (u, v) coordinates.

</code_context>

<specifics>
## Specific Ideas

- **"Drill is destructive — direct upgrade of pogo."** The user's framing of D-03/D-04/D-05. Drill and pogo share a contract shape (downward strike + per-frame contact rules) but differ in outcome: pogo bounces and damages, drill plunges and damages. The "upgrade" is structural (drill chains via repeated frames; pogo bounces once and exits). Implementation should make this lineage visible — pogo and drill modules in the same `src/fusion/` package, both implementing the FusionAbility Protocol, with mirrored enemy-contact methods.
- **"Each hit drains juice like soft block destruction."** Specifically the *interaction shape*, not the cost direction. User chose DRAIN (CRACKED_V analog) over REFUND (soft block analog) when disambiguated. The model is "killing enemies costs resource"; soft blocks happen to refund as a separate mechanic.
- **Mario-64 ground-pound mental model still holds.** POGO_INITIAL_DY = DRILL_SPEED is preserved (D-02) — same input, same initial gesture, fusion mutates the outcome. Visual parity at the gesture moment is load-bearing.
- **Drill is the boss finisher.** PROJECT.md core fantasy: "drill to finish." FUSION-DESIGN named "shoot to daze → drill to finish" as the prototype loop. The destructive-drill addition (D-03/D-04/D-05) makes drill an actual combat tool against generic enemies, extending the boss-finisher framing to the whole game world.
- **Earthbound palette for drill.** Pyxel's 16-color palette is constrained; drill claims 4/9/10 (brown/orange/yellow). Reads as "earth being broken" — visual link to the cavern atmosphere and the soft-destructible / CRACKED_V tiles drill carves through. Not red (collides with HP feedback), not green (collides with slime/spit/daze).
- **Audio as identity, not polish.** Phase 33's `audio.py` is the seed of Phase 35's full sound channel map. Keeping the seed minimal (6 cues, no debounce, no mixing) lets Phase 35 own the architecture; Phase 33 just establishes the cues exist and have distinct sonic signatures.
- **Phase 29 layer-by-layer pattern matters.** Charge ritual first because it's panel-only (no level dependency); pogo last because it's the side-quest. Don't tune drill combat until charge feels right — combat tuning depends on charge values being settled.

</specifics>

<deferred>
## Deferred Ideas

- **FUSION-DESIGN re-lock as `/gsd-insert-phase 32.5-fusion-design-destructive-drill-relock`** — per D-22 the recommended vehicle, but the user may opt for a manual re-lock dance instead. Decided at the moment Phase 33 planning starts.
- **Pogo feel-targets table** — D-18 deliberately leaves pogo without formal targets. If the light retune proves insufficient, a future phase (e.g. 33.5 or post-prototype) authors `33.5-POGO-FEEL-TARGETS.md` and does a proper pogo feel pass.
- **Phase 27 diagnostic overlays** — F2-F5 hitbox / velocity / input / slime overlays still TBD. Phase 33 doesn't depend on them, but hitbox overlay would help visualize the new drill-enemy intersection during tuning. If overlays land before Phase 33 closes, use them; otherwise plain print debugging.
- **Daze-on-hit stun primitive** — D-17 punts on whether to reuse existing boss stagger logic or add a new generic enemy stun. Planner-decided during implementation; if the existing logic isn't reusable, may carve out as a follow-up.
- **Hitstop on `drill_enemy_hit`** — Phase 33 wires only particle + SFX. Phase 35 (juice polish) adds hitstop with input-buffer protection.
- **Daze-on-hit dedicated event (`daze_hit`)** — Phase 33 wires `daze_fire` for the firing cue, but no per-hit event. Phase 35 may add `daze_hit` for hitstop/screen-flash on stun success.
- **Drill juice-clamp ordering on enemy hit** — open thread: when DRILL_ENEMY_COST > remaining juice, does the hit complete before juice clamps to 0 (and Exit b triggers next frame), or does juice clamp mid-frame and Exit b fires immediately, possibly after drill_enemy_hit emits but before drill_end? Planner picks; document the choice in `33-IMPLEMENTATION-NOTES.md` if non-obvious.
- **Custom drill test level** — 33-CONTEXT D-09 chose existing levels + debug warps. If tuning loop reveals existing levels don't expose the right scenarios (e.g. juice-starvation chain hard to construct in current rooms), Phase 33 may author a dedicated `Level_drill` mid-phase. Not committed up-front.
- **Pogo damage chain (drill-style)** — pogo intentionally bounces once, doesn't chain through enemies (D-19). Future iteration may revisit if the bounce-vs-chain feel asymmetry between pogo and drill becomes a sore point.
- **Bounce-velocity scales with kill** — pogo bounces higher when it kills than when it just damages. Considered in discussion, deferred (would add kill detection + variable bounce; out of phase title's "Drill-Only" framing).

</deferred>

---

*Phase: 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype*
*Context gathered: 2026-04-27*
