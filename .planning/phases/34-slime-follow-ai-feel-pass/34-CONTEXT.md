# Phase 34: Slime Follow/AI Feel Pass - Context

**Gathered:** 2026-05-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Retune slime follow to deliver "Ori-companion" feel — elastic catch-up, never visibly stuck, anticipation lean, hybrid float↔ground state machine. Half of the dual-hero identity. Existing Gradius history-deque path-follow is preserved as the base; new AI surfaces layer on top. No new abilities, no AnimFSM, no terrain-reactive pathing.

</domain>

<decisions>
## Implementation Decisions

### Phase 27 Dependency

- **D-01:** Run Phase 27 in full (F2-F5) before Phase 34 plan-phase. Existing plans 27-01 and 27-02 execute as-is.
- **D-02:** Phase 27 ships as-planned. Phase 34 extends the diagnostic overlay in passing as new AI state surfaces are added (catch-up boost active, stuck-recovery firing, mode = float|ground, lookahead bias amount).

### Behavior Model

- **D-03:** **Hybrid model.** The existing `Slime.update()` Gradius history-deque path-follow (slime.py:146-176) is preserved as the base. New AI surfaces layer on top — catch-up, stuck detection/recovery, look-ahead, float↔ground mode switch.
- **D-04:** **Dead-code strip** as Phase 34 housekeeping (separate plan, not bundled with feel tuning):
  - `is_punted` branch (slime.py:129-143) — no live writers since Phase 31.5 strip
  - `Slime.punt()` method (slime.py:178-182)
  - Dead instance attrs `accel`, `friction`, `max_speed`, `gravity`, `jump_force` (slime.py:40-44)
  - `main.py:912-916` punt collision block
- **D-05:** **Magic-number promotion.** `MAX_SHADOW_SPEED` (slime.py:157, hardcoded 4.0) → schema `slime_follow.SLIME_MAX_FOLLOW_SPEED`. `RECALL_TRAIL_MAX_LENGTH` (slime.py:74, hardcoded 6) stays as named module-level const in `slime.py` (visual-only, not panel-tunable).
- **D-06:** **Slime AnimFSM is OUT of scope.** Deferred to a future phase per Phase 26 D-09 reservation. Idle bob/breathing comes from animation, not position-level math.

### AI Features Scope (Ori-Vibe)

- **D-07:** **Ori-feel signatures targeted:** elastic trail, never visibly stuck, anticipation lean. Idle bob is handled by future AnimFSM, not this phase.
- **D-08:** **Reference model = Hybrid by state** (closest to Sein in Ori BF/WotW). Slime floats when player is airborne; when player is grounded, slime grounds only if it can reach a tile within K frames, otherwise stays floating. Most fidelity to "lands when it can."
- **D-09:** **Catch-up curve = ease-out (sqrt).** `speed = base + k * sqrt(distance_to_target)`, capped at `SLIME_MAX_FOLLOW_SPEED`. Soft far-field, snappy near-field. Replaces any binary "falls behind > N tiles" threshold.
- **D-10:** **Stuck-recovery mechanism = glow-fade reposition.** When stuck-detection fires, slime fades out (alpha/glow), repositions along the breadcrumb trail (closer to player), fades back in. Researcher should evaluate whether the existing `dissipate()`/`reform()` SF6-burnout primitive (slime.py:79-98) and `recall_trail` (slime.py:31, 73) can be reused or repurposed before adding a new render hook. User can author a melt/reform animation later if needed.
- **D-11:** **Look-ahead signal = `dx + facing direction`.** Bias the path-target by `player.dx * SLIME_LOOKAHEAD_FRAMES`. When `|player.dx| < ε`, fall back to a small bias in `player.facing_right` direction so slime still leans during stationary aim.
- **D-12:** **Terrain reactions deferred.** Hybrid-by-state float mode handles "don't get blocked by terrain" implicitly — explicit jump/fall/wall-grab nav code is not in scope. (See Deferred Ideas.)

### Feel Target Scenarios

- **D-13:** **Catch-up frame budget** = **60 frames (1.0s)** for the 10-tile gap (success criterion #1). At player max walk = 1.25 px/f (~12.8 frames per tile), 10 tiles = 160 px. 60-frame budget implies ~2.7 px/f average; peak `SLIME_MAX_FOLLOW_SPEED` will need to bake higher (researcher to compute against the ease-out curve).
- **D-14:** **Must-pass scenario buckets** for sign-off:
  - **S-C** (catch-up) — anchors success criterion #1
  - **S-S** (stuck/recovery) — anchors success criterion #2
  - **S-M** (mode switch float↔ground) — tests the hybrid-state machine
  - **S-L** (look-ahead/anticipation) — own row to force a measurable lean amount; prevents planner under-tuning to 0
  - **S-P** (panel smoothness) — anchors success criterion #3
- **D-15:** **Test gyms:** AccelRunway (S-C, S-L), ZigzagShaft + WallSlide (S-S, S-M), GapTrio + HeightSteps (S-M ground-level changes, S-S over gaps). Plus **new `Gym_SlimeFollow`** with a sealed 2x2 pocket reachable only by player teleport — covers the forced-stuck S-S case that no existing gym exposes.
- **D-16:** **New gym authoring split:** Plan-phase agent places an LDtk placeholder for `Gym_SlimeFollow`; user opens in LDtk to flesh out the sealed-pocket geometry. (Per project memory: level content lives in .ldtk; placeholders OK if user can finalize.)
- **D-17:** **Document format:** Separate `34-FEEL-TARGETS.md` (skeleton with rows + Pass/Fail conditions, Result column = PENDING). Matches Phase 29/33 pattern. Verification phase fills the Result column in place. CONTEXT.md links to it under canonical_refs.

### Claude's Discretion

The following sub-tunings are left to researcher/planner judgment under the locked guidance:

- Catch-up trigger threshold (where ease-out kicks above the existing follow-delay base) — informed by D-09 + D-13 budget math
- Stuck-detection window (frames of no-progress before recovery fires) — typical platformer companion uses 30-60f
- Look-ahead frame count (`SLIME_LOOKAHEAD_FRAMES`) — should be ≤ `SLIME_FOLLOW_DELAY` (currently 16) to avoid lookahead overshooting the deque
- Float↔ground mode-switch K-frames-to-reach-tile threshold — D-08's "within K frames" needs a concrete K
- Stationary-lean ε for D-11 fallback (`|player.dx| < ε`)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Definition
- `.planning/ROADMAP.md` §Phase 34 — Goal text + 3 success criteria + dependency declaration (Phase 25, 27, 28). SLM-04 is not defined as a spec block in REQUIREMENTS.md; the success criteria in ROADMAP are the operational requirements.

### Prior Phase Context
- `.planning/phases/27-diagnostic-overlays/27-CONTEXT.md` — Slime overlay design, existing tunable surfaces
- `.planning/phases/27-diagnostic-overlays/27-02-PLAN.md` — Slime overlay extension points
- `.planning/phases/26-event-bus-animation-fsm-skeleton/26-CONTEXT.md` — Anim driver dataclass + D-09 (Slime AnimFSM reservation, explicitly cut from Phase 34)
- `.planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md` — Format template for 34-FEEL-TARGETS.md (M-G/M-A/M-W row pattern, Pass/Fail conditions, Reference Values, Sign-off)
- `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md` — Latest example of the FEEL-TARGETS format with multi-prefix scheme (D-C/D-D/D-K/...)

### Code Under Tune
- `src/entities/slime.py` — Slime.update() at L100-176 (path-follow), recall/dissipate/reform at L46-98 (potentially reusable for stuck-recovery glow-fade per D-10)
- `assets/physics-schema.json` — `slime_follow` group at L60-65 (where SLIME_MAX_FOLLOW_SPEED + new lookahead/stuck/mode-switch keys land)
- `src/main.py:912-916` — punt collision block scheduled for strip per D-04

### Project Memory (load-bearing for this phase)
- Project memory: `.claude/projects/.../memory/feedback_no_agent_level_authoring.md` — Drives D-16 split (agent places placeholder, user finalizes in LDtk)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`Slime.dissipate()` + `Slime.reform()` + `dissipate_timer`** (slime.py:79-98): SF6-burnout primitive — alpha-style fade-out, timer-driven, then reposition near player at full juice. **Strong candidate for D-10 glow-fade stuck-recovery** — researcher should evaluate whether to call it directly, factor out a `reposition_with_fade(target_x, target_y)` helper, or build a lighter version that reuses the trail without resetting juice.
- **`Slime.recall_trail`** (slime.py:31, populated at L73): list of (x, y) breadcrumbs already maintained during recall. Stuck-recovery's "reposition along the breadcrumb trail" (D-10) can sample from this directly.
- **`Slime.history` deque** (slime.py:20, populated at L146): existing Gradius path-follow buffer. Look-ahead bias (D-11) can simply offset the index read at L149 — no new buffer needed.
- **`tuning.SLIME_FOLLOW_DELAY`** + the `slime_follow` schema group: existing live-tuned surface. New keys (`SLIME_MAX_FOLLOW_SPEED`, `SLIME_LOOKAHEAD_FRAMES`, `SLIME_STUCK_WINDOW_FRAMES`, `SLIME_FLOAT_GROUND_K_FRAMES`) extend the same group — panel auto-discovers them.

### Established Patterns

- **Hardcoded magic numbers in slime.py get promoted to schema** when panel-tunability matters (D-05). Visual-only constants (RECALL_TRAIL_MAX_LENGTH) stay as named module consts (per project memory: avoid magic numbers, use named constants or comments).
- **FEEL-TARGETS.md as audit-trail format** (Phase 29 + 33): rows with falsifiable Pass/Fail conditions, Result column starts PENDING, verification phase flips to PASS in place. Sign-off block at bottom.
- **Schema groups drive panel grouping**: `slime_follow` group → "Slime Follow" panel section. New keys land in the existing group, no panel code change needed.

### Integration Points

- **`Slime.update()` entry point** (slime.py:100): the hybrid-state machine code lands here. Layers on top of the current control flow (dissipated → recall → fused → punted [stripped] → standard path-follow).
- **Phase 27 diagnostic overlay**: D-02 says Phase 34 extends the overlay opportunistically — new AI state surfaces (mode = float|ground, catch-up boost amount, stuck-detection countdown, lookahead bias) get drawn in the existing slime overlay panel.
- **Phase 28 live panel**: All new tunables auto-appear under the `slime_follow` group via the existing schema-driven panel — no panel code changes needed unless we want custom widgets.
- **LDtk pipeline (`pml-to-ldtk`)**: `Gym_SlimeFollow` placeholder must respect the entity-schema contract (per project memory `reference_schema_contract.md`). Plan-phase researcher to confirm placeholder authoring path.

</code_context>

<specifics>
## Specific Ideas

- **"Ori vibes"** is the user's reference. Concretely: Sein-style hybrid floating/grounded companion — elastic trail, anticipates motion, never visibly stuck, glides around obstacles via float-mode rather than explicit terrain nav.
- **Catch-up budget anchor:** 10-tile gap → 60 frames (1.0s). This is the load-bearing number — every catch-up tuning derives from it.
- **Stuck recovery should look graceful, not snappy.** Glow-fade reposition (not hard teleport) is the visual contract. User has flagged willingness to author melt/reform animation if researcher recommends it.
- **Look-ahead must be visible** — own S-L test row exists specifically to force planner to land a measurable lean (not 0).

</specifics>

<deferred>
## Deferred Ideas

- **Slime AnimFSM tier-1** — driver + picker rules + clip set for idle/run/hop/recall/dissipate/fused. Phase 26 D-09 originally reserved this for Phase 34, but D-06 here explicitly cuts it. Needs its own phase. Idle bob/breathing depends on this.
- **Terrain reactions (explicit nav)** — slime jumping over solid tiles, falling through 1-tile gaps, wall-grabbing. Hybrid-by-state float mode (D-08) handles the practical "don't get blocked" case implicitly. If a future phase wants the slime to feel *grounded* even when far from player, it would need terrain-reactive nav.
- **Glide-around-corners** (sub-case of terrain reactions) — softer scope than full nav, but still deferred. Float-mode subsumes the user-facing problem.
- **Direction-reversal overshoot** characterization — flagged during Area 4 as a real concern for S-L. Treated as an input-pattern test at AccelRunway (no new gym), but if S-L tuning proves brittle, a dedicated reversal-corridor gym may be needed in a follow-up.
- **Custom panel widgets** for slime AI tunables (e.g., a curve-shape preview for the ease-out catch-up). The schema-driven default panel is sufficient for Phase 34; richer widgets are a future polish phase.

</deferred>

---

*Phase: 34-slime-follow-ai-feel-pass*
*Context gathered: 2026-05-02*
