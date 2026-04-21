# Phase 31: Animation Content + Particle Bank Separation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `31-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-04-21
**Phase:** 31-animation-content-particle-bank-separation
**Areas discussed:** ANIM-04 (Transition encoding), ANIM-05 (anim-schema.json + panel), ANIM-06 (Particle bank + Particle technique), ANIM-07 (Hitbox-independence test)

---

## Gray Area Selection

| Option | Description | Selected |
|--------|-------------|----------|
| Transition encoding (ANIM-04) | Per-transition placeholder technique (sprite-sheet, palette-swap, y-offset, 1-tick hold) | ✓ |
| anim-schema.json + panel (ANIM-05) | Schema shape, entity scope, loader API, panel integration | ✓ |
| Particle bank + Particle technique (ANIM-06) | Bank assignment, migration of existing effects, particle tech (pset vs. sprite-backed) | ✓ |
| Hitbox-independence test (ANIM-07) | Test mechanism (unit test / static grep / runtime wrapper) | ✓ |

**User note at selection time:** "stationary jump and walking jump distinction like Metroid" — folded into ANIM-04 as Metroid-style jump variant question (vx_sign-driven driver predicate).

---

## ANIM-04: Transition Encoding

### Q1: Metroid-style stationary-vs-walking jump — how is the jump clip picked?

| Option | Description | Selected |
|--------|-------------|----------|
| Driver predicate on horizontal velocity | Add `vx_sign: int` to driver; two clips; rules select via `d.state == 'JUMPING' and d.vx_sign == 0` vs. `!= 0`. Pure Reanimator. | ✓ |
| Driver predicate on is_running flag | Add hysteretic `is_running: bool`; more stable at low speeds. | |
| Single jump clip, branch inside picker | Picker reads player attrs directly — violates Reanimator purity. | |

**User's choice:** Driver predicate on horizontal velocity (Recommended).

### Q2: Land recovery transition — placeholder technique

| Option | Description | Selected |
|--------|-------------|----------|
| 1-tick hold on new squash frame | New authored squash frame on player.png; `loop=False` clip. | ✓ |
| Y-offset + idle frame for N ticks | No new sprite; draw offset during N frames. | |
| pyxel.pal() palette dim | Reuse idle frame with brief palette shift. | |

**User's choice:** 1-tick hold on new squash frame (Recommended).

### Q3: Turn-around transition — placeholder technique

| Option | Description | Selected |
|--------|-------------|----------|
| Driver edge + 1-tick skid frame | `prev_facing` diff detection; new skid sprite; rule fires for ~3 frames on flip. | ✓ |
| 1-tick idle-frame hold | Reuse idle frame; no new sprite. | |
| Driver predicate with vx_sign opposite to facing | Detects "reversing-while-moving" skid more accurately. | |

**User's choice:** Driver edge + 1-tick skid frame (Recommended).

### Q4: Fuse flash transition — placeholder technique

| Option | Description | Selected |
|--------|-------------|----------|
| pyxel.pal() white-flash | Classic retro hit-flash; no new sprite. | |
| New fused-form overlay frame | Authored fused-player sprite; short one-shot hold. | |
| Bright-ring particle burst | Particle system spawns a ring of bright particles at fuse_start. | |
| **Other (user freeform)** | **Converging particles + circular blob forming from convergence point; sprite supplied later.** | ✓ |

**User's choice:** Converging-particle + circular blob forming (user-authored alternative).

**User notes:** "converging particles and circular blob forming around player. sprite can be supplied later"

---

### Q5: Drill recoil transition — placeholder technique (follow-up round)

Before asking, user provided the answer directly: "drill is likely 4 frame cycle of the heroine spinning. make the frame pause briefly so it looks like the drill is eating into the blocks."

**Interpretation captured:** 4-frame spin clip for DIVING state (base); animation frame counter pauses on each `drill_block_break` event. NOT a separate recoil clip — a frame-pause mechanism on the existing spin clip.

### Q6: How long should the drill spin frame pause on each drill_block_break?

| Option | Description | Selected |
|--------|-------------|----------|
| ~3 frames | Short bite-stutter. | ✓ |
| ~6 frames | Matches existing DRILL_HITSTOP_FRAMES. | |
| ~2 frames | Barely-visible flicker. | |

**User's choice:** ~3 frames (Recommended).

### Q7: Is jump crouch a separate clip, or collapsed?

| Option | Description | Selected |
|--------|-------------|----------|
| Separate 1-2 tick crouch clip | New jump_crouch clip; `loop=False`; fires on `jump_start`. | ✓ |
| Collapse into jump clips' first frames | Each jump clip's first frames ARE the crouch. | |
| Skip jump crouch | Drop anticipation from scope. | |

**User's choice:** Separate 1-2 tick crouch clip (Recommended).

### Q8: Converging-particle count for fuse flash

| Option | Description | Selected |
|--------|-------------|----------|
| ~16 particles | Visible but not overwhelming. | ✓ |
| ~32 particles | Denser ring. | |
| ~8 particles | Sparse ring. | |

**User's choice:** 16 particles.

**User notes:** "this should look like Megaman style charge. particles converge into the character center. the blob grows from the convergence point. 16 particles is good"

### Q9: Converging-particle travel duration

| Option | Description | Selected |
|--------|-------------|----------|
| ~12 frames / ~0.2s | Punchy; eye still tracks convergence. | ✓ |
| ~20 frames / ~0.33s | Slower, more deliberate "ritual" feel. | |
| ~6 frames / ~0.1s | Fast flash-burst. | |

**User's choice:** ~12 frames / ~0.2s (Recommended).

---

## ANIM-05: anim-schema.json + Panel Integration

### Q1: Schema shape

| Option | Description | Selected |
|--------|-------------|----------|
| Nested by entity, then by clip | Matches Phase 26 PLAYER_CLIPS dict shape. | ✓ |
| Flat clip_id keyed with entity prefix | Fits PEP-562 flat access. | |
| Two-tier: shared clips + entity refs | Enables clip sharing. | |

**User's choice:** Nested by entity, then by clip (Recommended).

### Q2: Schema scope — which entities migrate

| Option | Description | Selected |
|--------|-------------|----------|
| Player only | Matches roadmap's player-transition focus. | ✓ |
| Player + effects | Proves tier-2 pattern. | |
| Player + effects + slime | Biggest scope. | |

**User's choice:** Player only (Recommended).

### Q3: Loader API — how tuning.py exposes anim-schema.json

| Option | Description | Selected |
|--------|-------------|----------|
| Second loader function, separate namespace | `tuning.anim.player.clips['run']`. | ✓ |
| Merged into flat tuning namespace | Keys like `ANIM_PLAYER_RUN_FRAMES`. | |
| Dedicated `src/anim/schema.py` loader | Loses panel integration. | |

**User's choice:** Second loader function, separate namespace (Recommended).

### Q4: Panel scope — how much live-editing

| Option | Description | Selected |
|--------|-------------|----------|
| Durations only (scalar sliders) | Frame indices + event bindings JSON-edit + hot-reload. | ✓ |
| Full: durations + frame list + event bindings | Build new panel components. | |
| JSON hot-reload only | No panel tab; explicitly violates roadmap SC#2. | |

**User's choice:** Durations only, defer frame/event editing (Recommended).

### Q5: Reload mechanism for frame-list / event-binding edits

| Option | Description | Selected |
|--------|-------------|----------|
| Panel button "Reload anim schema" | Consistent with Phase 24 no-file-watcher decision. | ✓ |
| F-key shortcut (e.g., F6) | Faster iteration; adds another F-key. | |
| Require game restart | Simplest; slowest iteration. | |

**User's choice:** Panel button "Reload anim schema" (Recommended).

### Q6: Preset scope — do anim durations join Phase 28 preset slots

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — anim durations join existing preset dict | Physics + anim in one package. | ✓ |
| No — anim has own separate preset slots | Cleaner separation. | |
| No — anim durations are global | Simpler but no A/B compare. | |

**User's choice:** Yes — anim durations join existing preset dict (Recommended).

### Q7: Seed values — where do initial anim-schema.json durations come from

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 26 hardcoded PLAYER_CLIPS | Preserves Phase 26 visual parity as baseline. | ✓ |
| Fresh hand-authored values tuned during Phase 31 | Opens feel-pass mini-phase. | |

**User's choice:** Phase 26 hardcoded values (Recommended).

### Q8: Error behavior when clip_id missing

| Option | Description | Selected |
|--------|-------------|----------|
| Fail fast at load with clear error | Bugs visible immediately. | ✓ |
| Warn and fall back to idle clip | Game boots; easier iteration. | |
| Raise at first lookup (lazy) | Bugs surface only when bad state reached. | |

**User's choice:** Fail fast at load with clear error (Recommended).

---

## ANIM-06: Particle Bank + Particle Technique

### Q1: Image bank for new particle sprites

| Option | Description | Selected |
|--------|-------------|----------|
| Bank 2 | Only free bank. | ✓ |
| Bank 2, split across multiple regions | Pre-organized "FX bank". | |

**User's choice:** Bank 2 (Recommended).

### Clarification round — user asked about bank 1 contents

User asked: "what's in bank 1 right now? the original tiles? seems like the entire bank is dedicated for the explosion."

**Clarification provided:** Bank 0 = map tiles; Bank 1 = 8 sprite sheets stacked (player, slime, snail, bat, items, projectile, effects, boss) each at 16-pixel Y-offsets; Bank 2 = unused. Explosion is just the 16-pixel strip at bank 1 y=96.

### Q2: Explosion sprite fate

| Option | Description | Selected |
|--------|-------------|----------|
| Retire — replace with diverging particle burst | Mirror of fuse-flash convergence; bank 1 y=96 reclaimed. | ✓ |
| Move to bank 2 and redesign the sprite | Keep sprite paradigm; more art work. | |
| Move to bank 2 as-is | Relocation only; sprite persists. | |

**User's choice:** Retire — replace with diverging-particle burst (Recommended).

**User notes:** "the existing explosion feels very out of place and I didn't even make them."

### Q3: Particle class technique

| Option | Description | Selected |
|--------|-------------|----------|
| Sprite-backed particles from bank 2 | Unified visual language. | ✓ |
| Hybrid: pset for generic debris + sprite-backed for authored FX | Two code paths. | |
| All pset, multi-color-sampled | Can't reproduce blob aesthetic. | |

**User's choice:** Sprite-backed particles from bank 2 (Recommended).

### Q4: Pool cap

| Option | Description | Selected |
|--------|-------------|----------|
| Defer pooling to Phase 35 | Phase 35 explicitly owns it per ROADMAP. | ✓ |
| Ship pool now | Phase 31 owns architecture decision scoped to Phase 35. | |

**User's choice:** Defer pooling to Phase 35 (Recommended).

---

## ANIM-07: Hitbox-Independence Test

### Q1: Test mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Unit test driving Player through every clip | Catches real regressions including indirect mutation. | ✓ |
| Static grep-based pytest | Fast; only catches lexical assignment. | |
| Runtime wrapper assertion | Catches every regression live; hot-path cost. | |

**User's choice:** Unit test driving Player through every clip, assert w/h unchanged (Recommended).

### Q2: Test scope

| Option | Description | Selected |
|--------|-------------|----------|
| Player only | Matches Phase 31 scope. | ✓ |
| Player + any entity using AnimFSM/AnimPlayer | Future-proofs slime + enemies. | |

**User's choice:** Player only (Recommended).

### Q3: Enforcement

| Option | Description | Selected |
|--------|-------------|----------|
| Hard gate — failing test blocks commits | ANIM-07 is a load-bearing architectural invariant. | ✓ |
| Informational — runs but doesn't block | Weaker guarantee. | |

**User's choice:** Hard gate (Recommended).

### Q4: Coverage dimensions

| Option | Description | Selected |
|--------|-------------|----------|
| state × vx_sign × vy_sign matrix | ~54 combos + facing flip. | ✓ |
| Sampled states only (IDLE, RUNNING, JUMPING, DIVING) | Less thorough. | |
| Event-driven coverage | Different axis of coverage. | |

**User's choice:** state × vx_sign × vy_sign matrix (Recommended).

---

## Claude's Discretion Areas

Captured from "Claude's Discretion" section of CONTEXT.md — areas where the user did not specify a rigid choice:

- Exact Y-offsets and strip heights on `assets/sprites/particles.png`
- Fused_blob growth-frame count (3-6 frames likely)
- Placeholder blob rendering technique (authored sprite vs. `pyxel.circ()` procedural)
- Whether `Effect` class is entirely retired or stripped to a spawner shell
- Driver predicate vs. event listener choice per transition where both are viable
- Panel tab naming and slider grouping for anim durations
- Test file organization (`test_anim_hitbox.py` vs. extending `test_anim.py`)
- `AnimPlayer.pause_for(n)` API shape
- Whether `Particle` class adopts tier-2 `AnimPlayer(clip)` wrapping or stays as custom dx/dy/life class

## Deferred Ideas (Captured During Discussion)

No user-introduced scope-creep ideas surfaced during this discussion that required deferral — all extensions to original gray areas (e.g., Metroid jump distinction, drill recoil technique, Megaman-charge fuse flash, explosion retirement) fit within Phase 31's roadmap-scoped ANIM-04 through ANIM-07 requirements.

Standard deferred items (architectural rejections, phase-split punts) are captured in `31-CONTEXT.md` §Deferred Ideas.
