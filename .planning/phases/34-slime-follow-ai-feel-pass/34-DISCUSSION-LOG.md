# Phase 34: Slime Follow/AI Feel Pass - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-02
**Phase:** 34-slime-follow-ai-feel-pass
**Areas discussed:** Phase 27 slime overlay dep, Behavior model — rewrite vs. tune, AI features scope (catch-up/stuck/look-ahead/terrain), Feel target scenarios

---

## Phase 27 Slime Overlay Dep

(Carried forward from prior session checkpoint — no question table available in resumed session.)

**User's choice:** Run Phase 27 in full (F2-F5) before Phase 34 plan-phase; existing plans 27-01 and 27-02 execute as-is. Phase 34 extends the overlay in passing as new AI state surfaces are added.

**Notes:** Phase 27 ships as planned. Phase 34 layers new state surfaces (catch-up, stuck, look-ahead, mode) into the existing overlay incrementally.

---

## Behavior Model — Rewrite vs. Tune

(Carried forward from prior session checkpoint — no question table available in resumed session.)

**User's choice:** Hybrid model — Gradius history-deque path-follow preserved as base; new AI state surfaces layer on top.

**Notes:**
- Strip is_punted branch + Slime.punt() + dead instance attrs (accel/friction/max_speed/gravity/jump_force) + main.py:912-916 punt collision block as Phase 34 housekeeping.
- MAX_SHADOW_SPEED → schema slime_follow group as SLIME_MAX_FOLLOW_SPEED.
- RECALL_TRAIL_MAX_LENGTH stays as named const in slime.py.
- Slime AnimFSM is OUT of scope; deferred to a future phase per Phase 26 D-09 reservation.

---

## AI Features Scope (Catch-up/Stuck/Look-ahead/Terrain)

### Question 1: Ori-feel signatures (multi-select)

| Option | Description | Selected |
|--------|-------------|----------|
| Elastic trail | Distance-proportional catch-up, no threshold flip | ✓ |
| Never visibly stuck | Aggressive recovery, graceful glide-to-player | ✓ |
| Anticipation lean | Look-ahead becomes core, slime leans toward player.dx | ✓ |
| Idle bob/breathing | Subtle position-level sine bob | (handled by future AnimFSM, not this phase) |

**User's choice:** Elastic trail + Never visibly stuck + Anticipation lean. Idle bob handled by animation frame.

### Question 2: Reference point

| Option | Description | Selected |
|--------|-------------|----------|
| Sein-floating | Companion floats freely, ignores gravity | |
| Grounded but smooth | Stays grounded, gets elastic + glide-around-corners | |
| Hybrid by state | Floats when player airborne/far, grounds when close + matching surface | ✓ |

**User's choice:** Hybrid by state.

### Question 3: Terrain reactions scope

| Option | Description | Selected |
|--------|-------------|----------|
| Defer entirely | Hybrid float-mode handles 'don't get blocked' implicitly | ✓ |
| Glide-around-corners only | Ease around corner tiles when grounded | |
| Glide + soft-jump mimic | Add visual arc-over for 1-tile lips | |

**User's choice:** Defer entirely.

### Question 4: Mode-switch trigger

| Option | Description | Selected |
|--------|-------------|----------|
| Player airborne OR far | Float when player.is_grounded == False OR distance > N | |
| Distance only | Float when distance > N tiles | |
| Player vertical + matching surface | Float whenever airborne; ground only if can reach tile within K frames | ✓ |

**User's choice:** Player vertical + matching surface (most fidelity to "lands when it can").

### Question 5: Catch-up curve shape

| Option | Description | Selected |
|--------|-------------|----------|
| Linear | speed = base + k * distance | |
| Ease-out (sqrt) | speed = base + k * sqrt(distance) | ✓ |
| Two-stage (cruise + sprint) | Below threshold = current deque; above = sprint with eased ramp | |

**User's choice:** Ease-out (sqrt).

### Question 6: Stuck-recovery mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Promote to float | Force float-mode, ease toward player along straight line | |
| Glow-fade reposition | Fade out, reposition along trail, fade back in | ✓ |
| Float + curve toward player | Promote to float AND curve along an arc | |

**User's choice:** Glow-fade reposition.
**Notes:** "I can make melt/reform animation if needed" — user is open to authoring custom anim. Researcher should evaluate whether existing dissipate()/reform() primitive (slime.py:79-98) and recall_trail can be reused first.

### Question 7: Look-ahead signal

| Option | Description | Selected |
|--------|-------------|----------|
| Player.dx only | target_x += player.dx * SLIME_LOOKAHEAD_FRAMES | |
| dx + facing direction | Bias by dx; fall back to facing when \|dx\|<ε | ✓ |
| Velocity vector (dx + dy) | Bias both axes by player velocity | |

**User's choice:** dx + facing direction.

---

## Feel Target Scenarios

### Question 1: Catch-up frame budget

| Option | Description | Selected |
|--------|-------------|----------|
| 30 frames (500ms) | Aggressive — needs SLIME_MAX_FOLLOW_SPEED ≈ 5.3 px/f | |
| 60 frames (1.0s) | Comfortable middle — peak ≈ 2.7 px/f. Closest to Ori-Sein | ✓ |
| 90 frames (1.5s) | Gentle — peak ≈ 1.8 px/f. Risks feeling slow | |
| Tied to player max speed | Self-adjusts to player tuning | |

**User's choice:** 60 frames (1.0s).

### Question 2: Must-pass scenario buckets (multi-select)

| Option | Description | Selected |
|--------|-------------|----------|
| Catch-up (S-C) | 10-tile gap closure, dash-away reunion, mid-air gap chase | ✓ |
| Stuck/recovery (S-S) | Random terrain stuck cases + forced-stuck pocket | ✓ |
| Mode switch (S-M) | Float↔ground transitions, anti-oscillation | ✓ |
| Panel smoothness (S-P) | All slime tunables panel-reachable, no snap-back | ✓ |

**User's choice:** All four.

### Question 3: Look-ahead test row

| Option | Description | Selected |
|--------|-------------|----------|
| Own row (S-L) | S-L1 falsifiable test for measurable lean amount | ✓ |
| Polish under S-C | Implicit, no separate row | |

**User's choice:** Own row (S-L).

### Question 4: Test gyms (multi-select)

| Option | Description | Selected |
|--------|-------------|----------|
| AccelRunway | Long flat corridor for S-C, S-L | ✓ |
| ZigzagShaft + WallSlide | Vertical/wall geometry for S-S, S-M | ✓ |
| GapTrio + HeightSteps | Mixed traversal for S-M, S-S over gaps | ✓ |
| Build a new Slime gym | Author Gym_SlimeFollow with sealed pocket | (deferred to follow-up question) |

**User's choice:** All three existing gym groups, AND user asked clarifying question: "are we missing any required test cases for slime follow in the current gym setup?" — Claude identified two real gaps (forced-stuck pocket, direction-reversal overshoot) and routed to follow-up.

### Question 5: Doc format

| Option | Description | Selected |
|--------|-------------|----------|
| Separate 34-FEEL-TARGETS.md | Matches Phase 29/33 audit-trail pattern | ✓ |
| Inline in CONTEXT.md | One fewer file, loses pattern | |

**User's choice:** Separate 34-FEEL-TARGETS.md.

### Question 6: Forced-stuck S-S coverage

| Option | Description | Selected |
|--------|-------------|----------|
| New Gym_SlimeFollow | Author tiny new gym with sealed 2x2 pocket | ✓ |
| Extend WallSlide | Add sealed pocket region inside WallSlide | |
| Test via Ctrl-warp + free-fly | No level changes, relies on debug tooling | |

**User's choice:** New Gym_SlimeFollow.
**Notes:** Per project memory, agent places LDtk placeholder; user finalizes geometry in LDtk.

---

## Claude's Discretion

The following sub-tunings were left to researcher/planner judgment under the locked guidance:
- Catch-up trigger threshold for the ease-out curve
- Stuck-detection window (frames of no-progress before recovery fires)
- Look-ahead frame count (`SLIME_LOOKAHEAD_FRAMES`) — bounded by existing `SLIME_FOLLOW_DELAY`
- Float↔ground mode-switch K-frames-to-reach-tile threshold
- Stationary-lean ε for the look-ahead fallback

## Deferred Ideas

- Slime AnimFSM tier-1 (driver + picker + clip set for idle/run/hop/recall/dissipate/fused) — Phase 26 D-09 reserved for Phase 34 but explicitly cut here; needs its own phase.
- Terrain reactions (explicit nav: jump over tiles, fall through gaps, wall-grab) — float-mode subsumes the user-facing problem.
- Glide-around-corners (sub-case of terrain reactions) — softer scope, still deferred.
- Direction-reversal overshoot characterization for S-L — covered as input pattern at AccelRunway; dedicated gym only if S-L tuning proves brittle.
- Custom panel widgets for slime AI tunables (e.g., curve-shape preview).
