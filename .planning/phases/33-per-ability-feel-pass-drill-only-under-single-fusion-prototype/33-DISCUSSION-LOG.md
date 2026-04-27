# Phase 33: Per-Ability Feel Pass (Drill-Only under single-fusion prototype) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-27
**Phase:** 33-per-ability-feel-pass-drill-only-under-single-fusion-prototype
**Areas discussed:** Tuning surface expansion, Test setup & feel-target format, Drill identity (particle + SFX), Pogo feel-pass scope

---

## Tuning surface expansion

### Q1: ChargeController hardcoded values migration

| Option | Description | Selected |
|--------|-------------|----------|
| Both — add to schema (Recommended) | Migrate WINDUP_DURATION_FRAMES (30) and ACCELERATED_REGEN_RATE (1.0) to physics-schema.json | ✓ |
| Windup only | Migrate only WINDUP_DURATION_FRAMES; ACCELERATED_REGEN_RATE stays hardcoded | |
| Accelerated regen only | Migrate only ACCELERATED_REGEN_RATE; WINDUP stays hardcoded | |
| Neither — keep hardcoded | Edit constants directly + restart between iterations | |

**User's choice:** Both — add to schema (Recommended)

### Q2: Pogo migration scope

| Option | Description | Selected |
|--------|-------------|----------|
| Bounce velocity + cooldown (Recommended) | Migrate POGO_BOUNCE_VELOCITY + POGO_COOLDOWN_FRAMES; keep POGO_INITIAL_DY (DRILL_SPEED visual parity) and POGO_DAMAGE = 1 hardcoded | ✓ |
| All four to a new pogo group | Move all 4 POGO_* constants into a new pogo group | |
| Bounce velocity only | Just the most-felt value | |
| None — keep all hardcoded | No pogo migration | |

**User's choice:** Bounce velocity + cooldown (Recommended)

### Q3: Drill iframes policy (FUSION-DESIGN Open-Q #1)

| Option | Description | Selected |
|--------|-------------|----------|
| Add tunable iframe knob, default 0 (Recommended) | DRILL_IFRAMES in drill group, default 0 = preserves v1.3 baseline | |
| Keep NONE, no knob | Lock to v1.3; no iframes, no knob | |
| Add fixed iframes (e.g. 12f), no panel exposure | Hardcoded constant in drill_dive.py | |
| Defer entirely — punt to a post-prototype | Don't address iframes in Phase 33 | |
| **Other (free-text)** | "drill is destructive action and should deal damage instead of exiting. direct upgrade of pogo. each hit should drain juice just like soft block destruction" | ✓ |

**User's choice:** Other — destructive-drill design pivot. Drill damages enemies on contact, drains juice per hit, continues through (no exit, no bounce). Replaces iframes question entirely.
**Notes:** This pivot expands FUSION-DESIGN's Drill-Dive Contract beyond tile interaction; triggers re-lock requirement (see D-21).

### Q3a: Enemy-hit cost model (disambiguation)

| Option | Description | Selected |
|--------|-------------|----------|
| Cost (drain) — like CRACKED_V (Recommended) | DRILL_ENEMY_COST consumes juice per hit | ✓ |
| Refund — like soft blocks | Each enemy hit REFUNDS juice | |
| Net-zero — cost equals projectile damage | Drill cost = daze-shot cost | |
| No juice change — free hits | No juice cost or refund per enemy hit | |

**User's choice:** Cost (drain) — like CRACKED_V (Recommended)

### Q3b: Drill damage per enemy hit

| Option | Description | Selected |
|--------|-------------|----------|
| Same as pogo — 1 damage per hit (Recommended) | DRILL_DAMAGE = POGO_DAMAGE = 1; chain frames multiply | ✓ |
| 2× pogo — 2 damage per hit | DRILL_DAMAGE = 2 | |
| Defer to playtest — add knob, start at 1 | Schema-tunable starting at 1 | |
| You decide | Claude picks | |

**User's choice:** Same as pogo — 1 damage per hit (Recommended)

### Q3c: Drill state on enemy hit

| Option | Description | Selected |
|--------|-------------|----------|
| Continue drilling (Recommended) | Pass through enemies like soft destructibles; no exit, no bounce | ✓ |
| Bounce on kill (pogo-style) | Bounce upward when enemy dies under drill | |
| Continue, but emit drill_enemy_hit event for hitstop/shake | Same mechanics + new event for Phase 35 hooks | |
| Hitstop briefly, then continue | DRILL_HITSTOP_FRAMES freeze on enemy hit | |

**User's choice:** Continue drilling (Recommended)

---

## Test setup & feel-target format

### Q1: Feel-targets format

| Option | Description | Selected |
|--------|-------------|----------|
| Same as Phase 29 — written table with pass/fail (Recommended) | Author 33-FEEL-TARGETS.md mirroring 29-FEEL-TARGETS.md | ✓ |
| Lighter — narrative targets, no table | Prose-only goals | |
| Hybrid — numeric values + narrative for novel mechanic | Table for v1.3-baseline values; narrative for destructive-drill | |
| No written targets — panel-only iteration | Skip targets doc entirely | |

**User's choice:** Same as Phase 29 — written table with pass/fail (Recommended)

### Q2: Test world

| Option | Description | Selected |
|--------|-------------|----------|
| Existing Level_0–8 + drill-friendly debug warps (Recommended) | Extend Phase 29 debug-warp hotkeys with drill-relevant warp targets | ✓ |
| Author a dedicated drill test room (Level_drill) | Build one isolated LDtk level | |
| Both — dedicated test room AND game-world spot-checks | Lab + production validation | |
| You decide | Claude picks | |

**User's choice:** Existing Level_0–8 + drill-friendly debug warps (Recommended)

### Q3: Tuning order

| Option | Description | Selected |
|--------|-------------|----------|
| Charge ritual → drill physics → drill combat → pogo (Recommended) | Phase 29 layer-by-layer, low-coupling first | ✓ |
| Drill physics first — charge ritual settles itself | Physics + economics first | |
| Combat first — destructive-drill is the riskiest design | Validate the new mechanic first | |
| Parallel — hot-swap between layers per playtest | Iterate on whichever feels worst | |

**User's choice:** Charge ritual → drill physics → drill combat → pogo (Recommended)

### Q4: Preset capture

| Option | Description | Selected |
|--------|-------------|----------|
| Update v2.0-default preset + 33 sign-off (Recommended) | Bake into existing v2.0-default.json | ✓ |
| New v2.0-fusion preset slot | Don't overwrite Phase 29's preset | |
| Update v2.0-default + author drill-aggressive variant | Default + A/B variant | |
| You decide | Claude picks | |

**User's choice:** Update v2.0-default preset + 33 sign-off (Recommended)

---

## Drill identity (particle + SFX)

### Q1: SFX scope

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal SFX module + 4-cue map (Recommended) | New src/core/audio.py with pyxel.sounds[N].set() + play_sfx wrapper | ✓ |
| Inline pyxel.play in event subscribers | No module; direct calls in main.py | |
| Visual-only — defer all SFX to Phase 35 | No audio in Phase 33 | |
| Two cues only — drill_start + fuse_start | Just FSM-state-change cues | |

**User's choice:** Minimal SFX module + 4-cue map (Recommended) — actual cue count grew to 6 (5 drill events + daze + pogo) per Q3 below.

### Q2: Particle differentiation approach

| Option | Description | Selected |
|--------|-------------|----------|
| New sprite cells in bank 2, route via type (Recommended) | Add cells to particles.png; type-arg dispatch | ✓ |
| Palette swap at draw time | Single sprite with pyxel.pal() recolor | |
| Both — new sprite for drill, palette-swap for daze | Mixed approach | |
| You decide | Claude picks | |

**User's choice:** New sprite cells in bank 2, route via type (Recommended)

### Q3: Drill palette colors

| Option | Description | Selected |
|--------|-------------|----------|
| Earthbound — orange/brown shrapnel (Recommended) | Pyxel colors 4 (brown), 9 (orange), 10 (yellow) | ✓ |
| Hot — red/pink impact sparks | Colors 8 (red), 14 (pink) | |
| Cold — cyan/white kinetic streaks | Colors 6 (light gray), 7 (white), 12 (light blue) | |
| You decide | Claude picks | |

**User's choice:** Earthbound — orange/brown shrapnel (Recommended)

### Q4: Event cues + drill_enemy_hit

| Option | Description | Selected |
|--------|-------------|----------|
| Add drill_enemy_hit; symmetric particle + SFX per event (Recommended) | New event for enemy contact; 5 events trigger particle + SFX | ✓ |
| Reuse drill_block_break for enemy hits | Conflate tile-break and enemy-kill | |
| Audio only on three events — fuse_start, drill_start, drill_impact | State-change cues only | |
| Defer drill_enemy_hit to Phase 35 | Wire only the four FUSION-DESIGN events | |

**User's choice:** Add drill_enemy_hit; symmetric particle + SFX per event (Recommended)

### Q5: Daze shot scope

| Option | Description | Selected |
|--------|-------------|----------|
| In scope for Phase 33 (Recommended) | Implement fused-tap-Z spit branch + SLIME_DAZE_COST + daze-on-hit | ✓ |
| Defer daze to a follow-up phase | Phase 33 ships drill vs spit only | |
| Daze identity only (visual/audio scaffold) — no gameplay effect | Visual scaffold without daze mechanic | |
| You decide | Claude picks | |

**User's choice:** In scope for Phase 33 (Recommended)

---

## Pogo feel-pass scope

### Q1: Pogo tuning depth

| Option | Description | Selected |
|--------|-------------|----------|
| Light retune — panel iteration only, no targets (Recommended) | Panel-tunable values; no entries in 33-FEEL-TARGETS.md | ✓ |
| Full pogo feel pass with targets | 5–7 pogo feel-targets in 33-FEEL-TARGETS.md | |
| Pogo touchpoint only on cooldown | Only adjust cooldown if abuse appears | |
| Pogo entirely deferred to a future phase | Roll back tuning-area pogo migration | |

**User's choice:** Light retune — panel iteration only, no targets (Recommended)

### Q2: Pogo combat rules

| Option | Description | Selected |
|--------|-------------|----------|
| Confirm only — pogo rules unchanged (Recommended) | FUSION-DESIGN D-04 + Phase 32 D-19 stay authoritative | ✓ |
| Pogo also deals chain damage like drill | Symmetric upgrade with drill | |
| Bounce velocity scales with enemy HP / kill | Variable bounce on kill | |
| You decide | Claude picks | |

**User's choice:** Confirm only — pogo rules unchanged (Recommended)

### Q3: Pogo identity (particle + SFX)

| Option | Description | Selected |
|--------|-------------|----------|
| Pogo gets minimal cue — bounce SFX only (Recommended) | New pogo_bounce SFX cue; no new particle | ✓ |
| Full pogo identity — particle + SFX | Dust-puff particle + SFX | |
| Reuse drill cues — no pogo-specific identity | drill_block_break for pogo too | |
| Defer pogo identity to Phase 35 | No pogo-specific cues in Phase 33 | |

**User's choice:** Pogo gets minimal cue — bounce SFX only (Recommended)

### Q4: FUSION-DESIGN re-lock policy

| Option | Description | Selected |
|--------|-------------|----------|
| Re-lock FUSION-DESIGN before Phase 33 plan (Recommended) | UNLOCK → add destructive-drill subsection → RELOCK with new SHA | ✓ |
| Document in 33-CONTEXT.md without re-lock | Treat as Phase 33-scoped expansion | |
| Re-lock AFTER Phase 33 ships, with playtested values | Implement first; lock final values at end | |
| You decide | Claude picks | |

**User's choice:** Re-lock FUSION-DESIGN before Phase 33 plan (Recommended)
**Notes:** Recommended vehicle is `/gsd-insert-phase 32.5-fusion-design-destructive-drill-relock` as a 1-plan hard-gate phase analog to Phase 31.5.

---

## Claude's Discretion

- Schema-group placement for migrated values (extend `fusion`/`drill` groups vs. new `fusion_charge`/`pogo` groups)
- Whether DRILL_DAMAGE moves to schema or stays as a module constant in drill_dive.py
- Specific (u, v) coordinates for new bank 2 particle cells within Phase 31's existing particles.png layout
- Specific MML strings or pyxel.sounds[N].set() parameters for each audio cue
- Whether 33-FEEL-TARGETS.md gets sign-off BEFORE tuning starts (Phase 29 did) or AFTER
- Number of feel targets in 33-FEEL-TARGETS.md (~10–15 mirrors Phase 29; smaller is fine)
- Daze-on-hit stun primitive: reuse existing boss stagger logic or add new generic stun
- Behavior when DRILL_ENEMY_COST > remaining juice (clamp + Exit b mid-frame, or finish hit then check next frame)
- Whether drill_enemy_hit subscribes for hitstop in Phase 33 or only for particle/SFX (recommendation: particle/SFX only; Phase 35 owns hitstop)

## Deferred Ideas

- FUSION-DESIGN re-lock as `/gsd-insert-phase 32.5-fusion-design-destructive-drill-relock` (vs. manual re-lock dance)
- Pogo feel-targets table — if light retune proves insufficient
- Phase 27 diagnostic overlays (F2-F5) — not blocking Phase 33 but would help drill tuning if landed
- Daze-on-hit stun primitive — reuse vs. new
- Hitstop on drill_enemy_hit — Phase 35
- daze_hit dedicated event — Phase 35
- Drill juice-clamp ordering on enemy hit — planner discretion, document choice
- Custom drill test level — fallback if existing levels don't expose the right scenarios mid-phase
- Pogo damage chain (drill-style) — future iteration
- Bounce-velocity scales with kill — future iteration
