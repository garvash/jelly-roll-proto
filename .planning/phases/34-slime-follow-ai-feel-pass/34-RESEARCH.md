# Phase 34: Slime Follow / AI Feel Pass - Research

**Researched:** 2026-05-02
**Domain:** Companion-AI feel tuning (Ori/Sein-style hybrid float↔ground follower) layered on existing Gradius history-deque path-follow.
**Confidence:** HIGH for code-reuse paths and integration points (verified by direct file reads); MEDIUM for the recommended numeric values (derived from CONTEXT.md budget math + platformer-AI heuristics, must validate via panel during execution).

## Summary

Phase 34 retunes the slime to deliver an Ori-companion (Sein-style) feel — elastic catch-up, never visibly stuck, anticipatory lean, hybrid float↔ground state machine — without rewriting the underlying Gradius history-deque follow at `slime.py:146-176`. CONTEXT.md has already locked the model (D-03 hybrid, D-08 hybrid-by-state, D-09 sqrt ease-out, D-10 glow-fade reposition, D-11 dx+facing lookahead, D-13 60-frame / 10-tile budget). The researcher's job is therefore narrow and prescriptive: surface the concrete numeric seeds for the five `Claude's Discretion` tunables, validate the code-reuse paths CONTEXT.md flagged, and confirm three integration points (Phase 27 overlay extension, schema-driven panel auto-discovery, LDtk placeholder authoring).

The math says the 60-frame budget for a 160 px gap (D-13) closes cleanly with `SLIME_CATCHUP_CURVE_K ≈ 0.50` and `SLIME_MAX_FOLLOW_SPEED = 7.0`. The existing `Slime.dissipate()`/`Slime.reform()` primitive is reusable for D-10 stuck-recovery via a thin `reposition_with_fade(target_x, target_y)` helper that re-targets `reform()`'s output and reuses `dissipate_timer` for the fade arc. The Phase 27 overlay (`src/core/overlays.py`) is already structured for additive AI surfaces — the existing stuck-detection counter and catch-up arrow generalize to mode flag, lookahead bias arrow, and stuck-countdown bar without any module-level structural change. The schema-driven panel (`src/ui/panel.py`, `src/ui/presets.py`) auto-discovers any new key added under the `slime_follow` group with zero panel code changes.

**Primary recommendation:** Lock the seed values in §Recommended Tunable Seeds below as Phase 34 entry-point starting values, factor `reposition_with_fade()` as a thin helper on top of the existing dissipate/reform primitive, and extend `_draw_slime_overlay()` additively (not refactor) for the four new AI surfaces.

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Phase 27 Dependency**
- D-01: Run Phase 27 in full (F2-F5) before Phase 34 plan-phase. Existing plans 27-01 and 27-02 execute as-is.
- D-02: Phase 27 ships as-planned. Phase 34 extends the diagnostic overlay in passing as new AI state surfaces are added (catch-up boost active, stuck-recovery firing, mode = float|ground, lookahead bias amount).

**Behavior Model**
- D-03: Hybrid model. Existing `Slime.update()` Gradius history-deque path-follow (slime.py:146-176) is preserved as the base. New AI surfaces layer on top.
- D-04: Dead-code strip as Phase 34 housekeeping (separate plan, not bundled with feel tuning):
  - `is_punted` branch (slime.py:129-143)
  - `Slime.punt()` method (slime.py:178-182)
  - Dead instance attrs `accel`, `friction`, `max_speed`, `gravity`, `jump_force` (slime.py:40-44)
  - `main.py:912-916` punt collision block
- D-05: Magic-number promotion. `MAX_SHADOW_SPEED` (slime.py:157, hardcoded 4.0) → schema `slime_follow.SLIME_MAX_FOLLOW_SPEED`. `RECALL_TRAIL_MAX_LENGTH` (slime.py:74, hardcoded 6) stays as named module-level const in `slime.py`.
- D-06: Slime AnimFSM is OUT of scope. Deferred to a future phase.

**AI Features Scope (Ori-Vibe)**
- D-07: Ori-feel signatures targeted: elastic trail, never visibly stuck, anticipation lean.
- D-08: Reference model = Hybrid by state (closest to Sein in Ori BF/WotW). Slime floats when player is airborne; when player is grounded, slime grounds only if it can reach a tile within K frames.
- D-09: Catch-up curve = ease-out (sqrt). `speed = base + k * sqrt(distance_to_target)`, capped at `SLIME_MAX_FOLLOW_SPEED`.
- D-10: Stuck-recovery mechanism = glow-fade reposition (NOT hard teleport). Use existing `dissipate()`/`reform()` primitive.
- D-11: Look-ahead signal = `dx + facing direction`. `player.dx * SLIME_LOOKAHEAD_FRAMES`; when `|player.dx| < ε`, fall back to a small bias in `player.facing_right` direction.
- D-12: Terrain reactions deferred. Hybrid-by-state float mode handles "don't get blocked" implicitly.

**Feel Target Scenarios**
- D-13: Catch-up frame budget = **60 frames (1.0s) for the 10-tile (160 px) gap**.
- D-14: Must-pass scenario buckets — S-C, S-S, S-M, S-L, S-P.
- D-15: Test gyms — AccelRunway (S-C, S-L), ZigzagShaft + WallSlide (S-S, S-M), GapTrio + HeightSteps (S-M, S-S over gaps), plus new `Gym_SlimeFollow` (sealed 2x2 pocket).
- D-16: New gym authoring split — Plan-phase agent places an LDtk placeholder; user opens in LDtk to flesh out the sealed-pocket geometry.
- D-17: Document format = separate `34-FEEL-TARGETS.md` (already drafted at context-gathering, lives in phase dir, PENDING result column).

### Claude's Discretion
- Catch-up trigger threshold (where ease-out kicks above the existing follow-delay base) — informed by D-09 + D-13 budget math.
- Stuck-detection window (frames of no-progress before recovery fires) — typical 30-60f.
- Look-ahead frame count (`SLIME_LOOKAHEAD_FRAMES`) — should be ≤ `SLIME_FOLLOW_DELAY` (currently 16).
- Float↔ground mode-switch K-frames-to-reach-tile threshold — D-08's "within K frames" needs a concrete K.
- Stationary-lean ε for D-11 fallback (`|player.dx| < ε`).

### Deferred Ideas (OUT OF SCOPE)
- Slime AnimFSM tier-1 (driver + picker rules + clip set for idle/run/hop/recall/dissipate/fused). Phase 26 D-09 reservation, deferred.
- Terrain reactions (explicit nav) — slime jumping over solid tiles, falling through 1-tile gaps, wall-grabbing.
- Glide-around-corners (sub-case of terrain reactions).
- Direction-reversal overshoot characterization (treated as input-pattern test at AccelRunway, no new gym).
- Custom panel widgets for slime AI tunables (curve-shape preview).

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SLM-04 | (Not formally defined as a spec block in REQUIREMENTS.md per CONTEXT.md note. The three Phase 34 ROADMAP success criteria ARE the operational requirements.) | (See Success Criteria → Plan Mapping below.) |

**ROADMAP §Phase 34 Success Criteria → Research Support:**

| Success Criterion | Plan-relevant research |
|-------------------|------------------------|
| #1 — Slime reliably catches up to player across 10-tile gap within written frame budget | §Recommended Tunable Seeds (curve K + max speed math); §Architecture Patterns (Pattern 1 ease-out + cap) |
| #2 — Slime no longer gets permanently stuck on terrain geometry during full v1.0 vertical-slice | §Recommended Tunable Seeds (stuck window); §Code Reuse for D-10 (reposition_with_fade); §Architecture Patterns (Pattern 3 stuck recovery) |
| #3 — Slime follow tuning all reachable from live panel with smooth, continuous changes, no snap-back | §Integration Points (panel auto-discovery confirmation) |

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Path-follow base (Gradius history deque) | Entity (`Slime.update`) | — | Pre-existing; D-03 preserves as base, AI surfaces layer on top here. |
| Ease-out catch-up curve | Entity (`Slime.update`) | Schema (`tuning.SLIME_CATCHUP_CURVE_K`, `SLIME_MAX_FOLLOW_SPEED`) | Per-frame math runs in slime; tunables live in physics-schema (D-05). |
| Look-ahead bias | Entity (`Slime.update`) | Schema (`SLIME_LOOKAHEAD_FRAMES`, `SLIME_LOOKAHEAD_FALLBACK_BIAS`) | Reads `player.dx` and `player.facing_right`, biases history deque index. |
| Float↔ground mode FSM | Entity (`Slime.update`) | Schema (`SLIME_FLOAT_GROUND_K_FRAMES`) + Map (collision probe) | Mode flag is slime-internal; reach-tile probe queries `level_map`. |
| Stuck detection + glow-fade reposition | Entity (`Slime` — extend `dissipate`/`reform`) | Schema (`SLIME_STUCK_WINDOW_FRAMES`) | Reuses existing `dissipate_timer` + `recall_trail`; panel-tunable window. |
| New AI surface visualization | Overlay (`src/core/overlays.py`) | — | Phase 27 D-02 — extend `_draw_slime_overlay()` additively. |
| Live tunability of all new keys | Panel (`src/ui/panel.py`) — auto-discovery | Schema (group: `slime_follow`) | No panel code change; group auto-discovers (verified at `panel.py:95`). |
| `Gym_SlimeFollow` placeholder authoring | LDtk (`assets/output.ldtk`) | pml-to-ldtk pipeline | D-16 — agent places placeholder, user finalizes in LDtk. |
| Code-strip dead `is_punted` paths | Entity (`slime.py`, `main.py`) | Tests (regression) | D-04 — separate housekeeping plan from feel-tuning plan. |

## Standard Stack

This is a single-engine prototype. No external libraries are introduced by Phase 34 — all changes live in existing `src/` modules and `assets/physics-schema.json`.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pyxel | (project pin) | Render primitives + input — for the overlay extension | Existing engine; no alternative under consideration. |
| `src.core.tuning` | (project) | Schema-driven hot-reload of new `slime_follow.*` keys | Established source-of-truth since Phase 24. Verified `_flat_index` auto-routes new keys to panel (`presets.py:25-27`). |
| `src.anim.event_bus` | (project) | Event hookup if mode-switch should fire `slime_mode_change` | Established pattern (Phase 26). Optional for Phase 34 — overlay can read `slime.mode_is_float` directly without an event. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `src.core.overlays` | (project) | Extend `_draw_slime_overlay()` per D-02 | Whenever a new AI surface needs visualization (mode flag, lookahead bias, catch-up boost, stuck countdown). |
| `src.ui.panel` + `src.ui.presets` | (project) | Live tuning of new schema keys | Always — D-05 promotion of MAX_SHADOW_SPEED + 6 new keys all land here automatically via `slime_follow` group. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Reusing `dissipate()`/`reform()` directly | New `glow_fade_recover()` method | Direct reuse keeps render path single (one fade primitive, one reform primitive). Adding a new method duplicates the fade-render logic in `draw()` (slime.py:261-263). **Recommend reuse via thin helper.** |
| Storing mode flag on `Slime` | Storing on overlay-only debug state | Mode is gameplay-relevant (drives terrain probe + pathing), so it belongs on entity. Overlay reads, never writes (T-27-01 trust boundary already established). |
| Computing reach-tile probe via raycast | Computing via vertical drop simulation | Raycast is constant-time and matches Pyxel's `level_map.check_collision` API surface; vertical drop sim adds per-frame loops. **Recommend raycast probe.** |
| Adding lookahead via new buffer | Offsetting deque index read | Deque already has the data — offset the index at `slime.py:149` per CONTEXT.md `Code Insights` note. **Recommend index offset.** |

**Installation:** None. All work in existing project files.

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Player (entity)                                                         │
│   ├── x, y, dx, facing_right, is_grounded                                │
│   └── (read-only consumers downstream)                                   │
└──────────┬──────────────────────────────────────────────────────────────┘
           │ frame N position + velocity
           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Slime.update(player_x, player_y, player_facing_right, level_map, ...)  │
│                                                                          │
│   ├── early outs (dissipated → reform-tick; recalling; fused)           │
│   │   (PRESERVED as-is per D-03)                                        │
│   │                                                                      │
│   ├── self.history.append((player_x, player_y))                         │
│   │   (PRESERVED — D-03 base buffer at slime.py:146)                    │
│   │                                                                      │
│   ├── NEW: lookahead_idx = max(0, len(history) - SLIME_FOLLOW_DELAY     │
│   │       + sign(player.dx) * SLIME_LOOKAHEAD_FRAMES)                   │
│   │       (D-11 — read history at biased index instead of [0])          │
│   │                                                                      │
│   ├── NEW: target_x, target_y = history[lookahead_idx]                  │
│   │       + lookahead bias (player.dx * F or facing fallback)           │
│   │                                                                      │
│   ├── NEW: float↔ground mode FSM (D-08)                                 │
│   │   ├── if not player.is_grounded: mode = "float"                     │
│   │   ├── else: probe — can slime reach a tile in K frames?             │
│   │   │   ├── yes: mode = "ground"                                      │
│   │   │   └── no:  mode = "float" (sticky until reachable)              │
│   │   └── hysteresis: minimum-state-duration to prevent S-M3 jitter     │
│   │                                                                      │
│   ├── NEW: catch-up curve (D-09)                                        │
│   │   ├── dist = sqrt((target_x-x)² + (target_y-y)²)                    │
│   │   ├── speed = base + SLIME_CATCHUP_CURVE_K * sqrt(dist)             │
│   │   ├── speed = min(speed, SLIME_MAX_FOLLOW_SPEED)                    │
│   │   └── apply as direction*speed instead of raw target-pos delta      │
│   │                                                                      │
│   ├── NEW: stuck detection (D-10)                                       │
│   │   ├── if |delta_position| < ε for SLIME_STUCK_WINDOW_FRAMES:        │
│   │   │   └── trigger reposition_with_fade(target_x, target_y)          │
│   │   │       (reuses dissipate_timer + reform via thin helper)         │
│   │   └── else: counter resets                                          │
│   │                                                                      │
│   └── PRESERVED: collision push-out + grounded probe + reform-distance  │
│       trigger at slime.py:166-176                                       │
└──────────┬──────────────────────────────────────────────────────────────┘
           │ slime.x, slime.y, slime.mode_is_float, slime.stuck_frames
           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  src/core/overlays.py::_draw_slime_overlay(game)  [F5]                  │
│   ├── EXISTING: breadcrumb trail + distance circles + target dot        │
│   ├── EXISTING: stuck X (counts vel<0.1) + catch-up arrow               │
│   └── NEW: mode flag glyph, lookahead-bias arrow, stuck-countdown bar   │
│       (D-02 — extend additively, not refactor)                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure

No new directories. Surgical changes within existing layout:

```
assets/
├── physics-schema.json              # +6 keys under slime_follow group
└── output.ldtk                      # +1 placeholder level Gym_SlimeFollow
src/
├── entities/
│   └── slime.py                     # Path-follow extended in update();
│                                    # add reposition_with_fade() helper;
│                                    # add mode + stuck_frames instance attrs;
│                                    # strip is_punted (D-04, separate plan)
├── core/
│   └── overlays.py                  # _draw_slime_overlay() extended
└── ui/                              # NO CHANGES — auto-discovers schema keys
    ├── panel.py
    └── presets.py
main.py                              # -5 lines (D-04 punt collision block strip)
tests/
├── test_slime.py                    # +S-M / S-L / S-S unit tests
└── test_overlays.py                 # +mode/lookahead/countdown render tests
```

### Pattern 1: Sqrt Ease-Out Catch-Up Curve (D-09)

**What:** Speed scales with `k * sqrt(distance)`, capped at `SLIME_MAX_FOLLOW_SPEED`. Replaces any binary "falls behind > N tiles" threshold.
**When to use:** Always — D-09 locks this as the catch-up curve. Replaces the current naïve `dx = target - x` then clamp at slime.py:151-159.
**Math (verified for D-13 budget):**

```
Solve: dx/dt = -k*sqrt(x), x(0) = 160, x(60) = 0
Solution: x(t) = (sqrt(x₀) - k*t/2)²
For x(60) = 0: sqrt(160) = k*60/2  →  k = 2*12.65/60 ≈ 0.42

Recommend k = 0.50 (~20% headroom). Peak speed at t=0:
  v_peak = k * sqrt(160) = 0.50 * 12.65 ≈ 6.32 px/f
With cap at 7.0, the cap engages briefly at start; effective time ≤ 60f.
```

**Example (recommended slime.py replacement at L151-165):**
```python
# Source: derived from CONTEXT.md D-09 + D-13. Verified against
# Newton-equation closed form for dx/dt = -k*sqrt(x).
target_x, target_y = self._lookahead_target(player_x, player_y, player_facing_right)
delta_x = target_x - self.x
delta_y = target_y - self.y
dist = (delta_x * delta_x + delta_y * delta_y) ** 0.5

if dist > 0.0:
    base = 0.0  # history deque already pulls slime; ease-out adds the catch-up.
    speed = base + tuning.SLIME_CATCHUP_CURVE_K * (dist ** 0.5)
    speed = min(speed, tuning.SLIME_MAX_FOLLOW_SPEED)
    self.dx = (delta_x / dist) * speed
    self.dy = (delta_y / dist) * speed
else:
    self.dx = 0.0
    self.dy = 0.0
```

[VERIFIED: Math closed-form, validated against `x(60)=0` boundary condition]
[ASSUMED: `base = 0.0` is correct for hold-still S-C1 case. If panel testing shows a "minimum follow rate" is needed for natural drift on slow player, promote `SLIME_FOLLOW_BASE_SPEED` to schema in execution. Marked for validation.]

### Pattern 2: Lookahead via Deque-Index Offset (D-11)

**What:** Bias the history deque read so slime targets a *future* player position instead of one `SLIME_FOLLOW_DELAY` frames in the past.
**When to use:** Always — D-11 is the locked anticipation mechanism, and S-L1 + S-L2 require a measurable lean.
**Why offset and not new buffer:** CONTEXT.md `Code Insights` confirms — the deque already holds the data; offset the read index at slime.py:149.

**Example:**
```python
def _lookahead_target(self, player_x, player_y, player_facing_right):
    # Source: D-11 + CONTEXT.md Code Reuse evaluation (slime.py:146 deque).
    # Index 0 = oldest (delay base); index -1 = newest player position.
    # Bias toward newer indices when player moves in the bias direction.
    if not self.history:
        return player_x, player_y

    # Direction signal (D-11): use player.dx if moving; else fall back to facing.
    # Note: player not passed; signal must come via update() args. See "Open Questions" #2.
    bias_dir = self._lookahead_bias_dir(player_facing_right)  # -1, 0, or +1

    base_idx = max(0, len(self.history) - tuning.SLIME_FOLLOW_DELAY)
    # Bias forward in deque when bias_dir matches the deque traversal direction.
    # (Deque goes oldest → newest; "newer" = closer to current player position)
    bias_frames = abs(bias_dir) * tuning.SLIME_LOOKAHEAD_FRAMES
    idx = min(len(self.history) - 1, base_idx + bias_frames)
    return self.history[idx]
```

[VERIFIED: Deque structure at slime.py:20 maxlen = SLIME_FOLLOW_DELAY+1 supports offset reads]
[ASSUMED: A read at `min(len-1, base+bias)` is preferable to a per-axis bias on the (x,y) tuple. The alternative — keep deque read at index 0 and add `player.dx * F` as a positional offset — is also valid and matches CONTEXT.md's literal D-11 phrasing more closely. **Recommend the positional-offset variant** to keep the deque untouched and to preserve the existing 16-frame trail "feel"; the index-offset variant collapses the trail visually at high `bias_dir`. See Pitfall 4.]

**Recommended D-11 implementation (positional-offset variant):**
```python
def _lookahead_target(self, player_x, player_y, player_dx, player_facing_right):
    # Source: D-11 literal — bias path-target by player.dx * SLIME_LOOKAHEAD_FRAMES;
    # fall back to small bias in player.facing_right when |player.dx| < ε.
    if len(self.history) >= tuning.SLIME_FOLLOW_DELAY:
        base_x, base_y = self.history[0]   # PRESERVED deque read at L149
    else:
        base_x, base_y = player_x, player_y

    if abs(player_dx) >= tuning.SLIME_LOOKAHEAD_EPSILON:
        bias_x = player_dx * tuning.SLIME_LOOKAHEAD_FRAMES
    else:
        sign = 1.0 if player_facing_right else -1.0
        bias_x = sign * tuning.SLIME_LOOKAHEAD_FALLBACK_BIAS
    return base_x + bias_x, base_y
```

This preserves the deque "trail feel" and matches D-11 phrasing literally.

[VERIFIED: `player.dx` is available — player.py:341-348 shows it is the canonical horizontal velocity. Slime.update() must accept it as a new argument from main.py.]

### Pattern 3: Stuck Detection + Glow-Fade Reposition (D-10)

**What:** Count consecutive frames where slime fails to make progress; when over `SLIME_STUCK_WINDOW_FRAMES`, trigger a fade-out → reposition along `recall_trail` → fade-in via the existing `dissipate_timer` arc.
**When to use:** Always — D-10 locks the visual contract (graceful, not snappy).
**Why reuse existing primitive:** `dissipate()` (slime.py:79-86) already sets `is_dissipated = True` + `dissipate_timer = SLIME_DISSIPATE_COOLDOWN`. `update_dissipation()` (slime.py:88-98) ticks the timer and calls `reform()` at zero. `draw()` already short-circuits while dissipated (slime.py:261-263). All three are reusable as-is.

**Recommended helper (factor onto Slime, do NOT duplicate dissipate/reform):**
```python
def reposition_with_fade(self, target_x, target_y, player_facing_right, level_map):
    """D-10 stuck-recovery: glow-fade out, reposition, glow-fade in.

    Reuses the existing dissipate/reform SF6-burnout primitive without
    resetting juice (the player did nothing wrong — slime got stuck).
    """
    self._stuck_recovery_target = (target_x, target_y)
    self.is_dissipated = True
    self.dissipate_timer = tuning.SLIME_STUCK_RECOVERY_COOLDOWN  # may equal SLIME_DISSIPATE_COOLDOWN
    self.recall_trail.clear()  # visual trail is breadcrumb-source for reform target
    # NOTE: do NOT reset juice. dissipate() sets juice=full as a punishment-mitigation
    # for fused-burnout; stuck-recovery is no-fault, juice unchanged.

def update_stuck_recovery(self, player_x, player_y, player_facing_right, level_map):
    """Tick stuck-recovery dissipation and reform at target on completion."""
    if not self.is_dissipated:
        return False
    self.dissipate_timer -= 1
    if self.dissipate_timer <= 0:
        self.is_dissipated = False
        # If we have a recovery target (stuck case), use it. Else fall back
        # to the SF6-burnout reform (juice-empty case). DISCRIMINATOR: if
        # _stuck_recovery_target is set, this is a stuck-recovery; clear it.
        target = getattr(self, "_stuck_recovery_target", None)
        if target is not None:
            self.x, self.y = target
            self.dx = 0
            self.dy = 0
            self.target_x, self.target_y = target
            self.history.clear()
            self._stuck_recovery_target = None
        else:
            self.juice = self.max_juice
            self.reform(player_x, player_y, player_facing_right, level_map)
        return True
    return False
```

The existing `update_dissipation()` should remain for fused-burnout path; or it can be unified — but the discriminator on `_stuck_recovery_target` is cleaner and lower-risk.

**Reposition target selection (D-10 "along the breadcrumb trail"):**
```python
def _stuck_recovery_target(self, player_x, player_y):
    """Pick a reposition point closer to player along the trail."""
    if not self.recall_trail:
        # Fallback to player position if no trail (shouldn't happen with
        # RECALL_TRAIL_MAX_LENGTH=6 — but guard the empty case anyway).
        return player_x, player_y
    # Mid-trail = halfway between current slime position and the player.
    # CONTEXT.md D-10 phrasing: "repositions along the breadcrumb trail
    # (closer to player)".
    return self.recall_trail[len(self.recall_trail) // 2]
```

[VERIFIED: `recall_trail` is populated only during `update_recall()` (slime.py:73). For non-recall path-follow stuck-recovery, the trail will be empty. **This is a real gap** — see Open Questions #3.]

### Pattern 4: Hybrid Float↔Ground Mode FSM (D-08)

**What:** Slime is in `"float"` mode while player is airborne. When player grounds, slime probes — can it reach a tile within `SLIME_FLOAT_GROUND_K_FRAMES`? Yes → `"ground"` mode. No → stay `"float"`.
**When to use:** Always — D-08 is the locked reference model.

**Probe implementation (raycast-on-collision, NOT vertical drop sim):**
```python
def _can_reach_tile_in_k_frames(self, level_map, k_frames):
    """Probe: at SLIME_MAX_FOLLOW_SPEED downward, will slime hit a solid in k_frames?"""
    probe_y = self.y + tuning.SLIME_MAX_FOLLOW_SPEED * k_frames
    return level_map.check_collision(self.x, probe_y, self.w, self.h)

def _update_mode(self, player_is_grounded, level_map):
    if not player_is_grounded:
        self.mode_is_float = True
        return
    if self._can_reach_tile_in_k_frames(level_map, tuning.SLIME_FLOAT_GROUND_K_FRAMES):
        # Hysteresis: don't flip mode if we just flipped this frame
        if self.mode_frames_in_state >= tuning.SLIME_MODE_HYSTERESIS_FRAMES:
            self.mode_is_float = False
            self.mode_frames_in_state = 0
    self.mode_frames_in_state += 1
```

[VERIFIED: `level_map.check_collision(x, y, w, h)` API exists — used at slime.py:166, 187, 196. Probe call is constant-time.]

**Anti-jitter (S-M3):** Add `mode_frames_in_state` counter and `SLIME_MODE_HYSTERESIS_FRAMES` minimum-state-duration. Recommend = 6 frames (100ms at 60fps).

### Anti-Patterns to Avoid

- **Adding a new "follow speed" linear-clamp on top of the sqrt curve:** The current naïve `dx=target-x` then clamp at `±MAX_SHADOW_SPEED` is what we are *replacing*. Do not keep both — pick one. Per D-09, the answer is the sqrt curve.
- **Reading `player.is_grounded` from a stale frame:** main.py must pass the current-frame `player.is_grounded` to `slime.update()`. The current call site (`main.py` near `self.slime.update(...)`) does not pass this — verify the wiring task in the plan adds it.
- **Hard teleporting on stuck:** D-10 is explicit — fade-out, reposition, fade-in. Do not skip the dissipate timer.
- **Replacing the deque:** D-03 is explicit — preserve the Gradius history-deque base. New AI surfaces *layer* on top.
- **Adding the `is_punted` strip into the same plan as feel-tuning:** D-04 says housekeeping is a separate plan. Bundling them complicates rollback if feel-tuning needs a revert.
- **Promoting `RECALL_TRAIL_MAX_LENGTH` to schema:** D-05 is explicit — visual-only constants stay as named module consts.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Glow-fade alpha rendering | New alpha-buffer system | Existing `is_dissipated` short-circuit in `Slime.draw()` (slime.py:261-263) + `dissipate_timer` arc | Already in tree; reuse via `reposition_with_fade()` helper. |
| Position trail for breadcrumbs | New deque | Existing `self.history` (slime.py:20) and `self.recall_trail` (slime.py:31, 73) | Two trails already exist. Per CONTEXT.md, history serves lookahead and recall_trail serves stuck-recovery. |
| Frame-based stuck detection (overlay) | New counter | Existing `_slime_stuck_frames` in `src/core/overlays.py:83` | Overlay already counts and renders flashing-X. Move counter to entity (gameplay-relevant) and have overlay *read* it. **See Open Questions #4.** |
| Catch-up direction arrow | Custom render | Existing catch-up arrow in `src/core/overlays.py:478-490` | Already drawn when slime velocity > threshold and dist > REFORM_DIST. Add lookahead-bias arrow as additive overlay element using same primitives (`pyxel.line`). |
| Live tunable surface for new schema keys | Custom panel widget | Schema-driven panel auto-discovery (`src/ui/panel.py:95`, `src/ui/presets.py:18-22`) | `slime_follow` group is already in `FEEL_GROUPS` and `TAB_DEFS` Slime tab. Any key added to that schema group appears automatically. **Verified by direct code read.** |
| New gym authoring | Hand-edit `Gym_SlimeFollow/data.json` files | LDtk placeholder + user-finalize workflow (D-16, project memory `feedback_no_agent_level_authoring.md`) | Agent edits to simplified/ folder will be overwritten by next pml-to-ldtk run. Author in `assets/output.ldtk` only. |

**Key insight:** Phase 27 already paid the cost of building the slime-follow overlay framework. Phase 34 should *extend* it (3-4 additive elements), not duplicate or refactor it.

## Runtime State Inventory

This phase is a **feel-tuning + small refactor + dead-code strip**. Not a rename or migration. Most categories are N/A, but D-04 and D-05 do touch state:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — slime state is per-frame transient. Saves do not persist follow state. (Verified: `tests/test_save_system.py` does not reference `SLIME_FOLLOW_*` or follow-mode keys.) | None. |
| Live service config | None — single-process Pyxel game, no external services. | None. |
| OS-registered state | None — no scheduled tasks, no daemons. | None. |
| Secrets/env vars | None — no secrets in this prototype. | None. |
| Build artifacts | None — Python project, no compiled artifacts beyond `__pycache__/`. | None. |
| **Schema keys (D-05 promotion)** | `MAX_SHADOW_SPEED = 4.0` (slime.py:157, hardcoded module const). Renames to `tuning.SLIME_MAX_FOLLOW_SPEED` under `slime_follow` group. | **Schema edit task** — add new key to `assets/physics-schema.json`. **Code edit task** — replace `MAX_SHADOW_SPEED` reference at slime.py:157-159 with `tuning.SLIME_MAX_FOLLOW_SPEED`. **Preset migration:** all existing presets in `assets/presets/*.json` will be missing the new key on load — `tuning.load()` must seed defaults from schema (verify behavior matches Phase 33's tuning-migration pattern at `33-02-tuning-migration-schema-PLAN.md`). |
| **Dead-code residue (D-04)** | `is_punted` instance attr, `Slime.punt()` method, dead `accel`/`friction`/`max_speed`/`gravity`/`jump_force` attrs (slime.py:25, 40-44, 178-182), and `main.py:912-916` collision block. Tests: `test_slime.py` has no `is_punted` references (verified by direct read); `test_kick_removal.py` likely the historical home of any punt tests. | **Strip task (separate plan per D-04)** — delete code, run full suite, verify zero references via `grep` for `is_punted` and `punt(` in `src/`. |

## Common Pitfalls

### Pitfall 1: `is_grounded` not threaded into slime.update()
**What goes wrong:** D-08 mode FSM needs `player.is_grounded` *every frame*, but the current `slime.update()` signature is `(player_x, player_y, player_facing_right, level_map, is_fused=False)` — no grounded state.
**Why it happens:** Slime didn't need this before; previous pathing was purely position-based.
**How to avoid:** Plan must add `player_is_grounded: bool` parameter to `slime.update()` and update the call site in `main.py` (search for `self.slime.update(`). Also add `player_dx: float` for D-11 lookahead.
**Warning signs:** S-M1 / S-M2 fail because mode never flips, OR mode flips on stale state.

### Pitfall 2: Reform-distance trigger competes with stuck-recovery
**What goes wrong:** Existing `SLIME_MAX_DIST` reform check (slime.py:174-176) fires at distance > 100 px. New stuck-recovery (D-10) targets repositioning when *not making progress*. If slime is stuck very close to player (< 100 px), reform never fires; if stuck very far, reform fires *before* stuck-recovery has a chance to glow-fade.
**Why it happens:** Two reposition systems with overlapping trigger ranges.
**How to avoid:** Order in update flow: stuck detection → `if reposition fired: return`. Then existing reform-distance check. Document the ordering rule in slime.py.
**Warning signs:** S-S2 (sealed pocket) test passes but S-S1 (random terrain) shows hard-teleports without fade — means reform fired before stuck-recovery latched.

### Pitfall 3: Lookahead bias overshoots when player reverses direction
**What goes wrong:** Player runs right, slime leans right (positional offset = +bias). Player reverses to run left at frame N. For SLIME_LOOKAHEAD_FRAMES (recommend 8) frames, slime is offset *the wrong direction* until the bias updates with the new player.dx.
**Why it happens:** Bias is computed from current `player.dx`, but slime is already at the offset position from the previous direction.
**How to avoid:** This is the "direction-reversal overshoot" CONTEXT.md flagged as a Deferred Idea (Area 4). Acceptable for Phase 34 — handled by S-L1 testing at AccelRunway. If S-L tuning proves brittle, the deferred reversal-corridor gym ships in a follow-up.
**Warning signs:** S-L1 PASS but visible "skating" or "rubber-banding" during direction changes that the user dislikes during playtest.

### Pitfall 4: Index-offset lookahead collapses the visual trail
**What goes wrong:** If lookahead is implemented via deque-index offset (alternative considered in Pattern 2), at full lookahead the read index = `len(history)-1` = current player position, which makes slime sit *on* the player and the visual breadcrumb trail behind slime appears empty.
**Why it happens:** History is consumed as the lookahead source; visual trail and follow target share the deque.
**How to avoid:** Use the positional-offset variant (Pattern 2 recommended example), which preserves deque[0] as the base read.
**Warning signs:** S-L1 visually weird (slime shrinks distance to zero with player); breadcrumb trail in F5 overlay looks empty when player is moving.

### Pitfall 5: Stuck-counter ε too tight catches "barely moving" as stuck
**What goes wrong:** D-10 stuck detection on `|delta_position| < ε` for SLIME_STUCK_WINDOW_FRAMES will fire if the slime is making correct-but-tiny progress (e.g., approaching target asymptotically with the sqrt curve at small distances).
**Why it happens:** sqrt curve → near-zero speed at near-target distance. Stuck heuristic doesn't know about target.
**How to avoid:** Use **distance-to-target** as the secondary discriminator. Only count stuck-frames when `dist_to_target > tuning.SLIME_REFORM_DIST` (i.e., still has work to do). At `dist <= REFORM_DIST`, slime is "arrived" — reset counter.
**Warning signs:** Glow-fade fires while slime is just sitting near a stationary player — false positives.

### Pitfall 6: Schema key load order — new keys absent from presets cause AttributeError
**What goes wrong:** `tuning.SLIME_CATCHUP_CURVE_K` is read in `slime.update()` every frame. If `tuning.load()` doesn't seed defaults from the schema for keys missing from presets, the first frame with a v1.3 preset loaded raises AttributeError.
**Why it happens:** Phase 24 loader pattern is `getattr(tuning, "X")`; schema has the default but preset overrides win during load.
**How to avoid:** Verify `tuning.load()` falls through to schema defaults when a key is absent in the active preset (this is Phase 33's migration pattern — `33-02-tuning-migration-schema-PLAN.md` shows the seeding flow). Plan must include a tuning-migration test (`tests/test_tuning_migration.py` extension) that loads `_v1.3-reference.json` and asserts all 6 new `SLIME_*` keys have schema defaults.
**Warning signs:** Game crashes on F1 panel-load → `_v1.3-reference` preset slot click; or `python -c "from src.core import tuning; print(tuning.SLIME_CATCHUP_CURVE_K)"` raises AttributeError after `tuning.load(_v1.3-reference)`.

### Pitfall 7: Overlay reads `slime.mode_is_float` before it exists
**What goes wrong:** Phase 34 plans likely ship in waves. If overlay-extension wave runs before entity-state wave, `_draw_slime_overlay()` AttributeErrors on `s.mode_is_float`.
**Why it happens:** Cross-file dependency without a guard.
**How to avoid:** Overlay reads via `getattr(s, "mode_is_float", None)` and only draws the mode glyph if not None. Keeps the overlay backwards-compatible if a code path bypasses entity init.
**Warning signs:** F5 toggle crashes the game during inter-wave commits.

### Pitfall 8: Catch-up `base` of 0 starves slime when player is barely moving
**What goes wrong:** Pattern 1 example uses `base = 0.0`. At small distances and zero player movement, slime drifts at near-zero speed, looking laggy in S-L2 stationary-aim cases.
**Why it happens:** sqrt(small) is small; cap doesn't engage.
**How to avoid:** Either (a) accept this — D-11 lookahead bias should pull the *target* off-center so distance is never zero; (b) promote `SLIME_FOLLOW_BASE_SPEED` to schema (default 0.5 px/f) so there's always a minimum drift. **Recommend (a) first**; only ship (b) if S-L2 fails.
**Warning signs:** S-L2 stationary-aim lean fallback never visibly leans (slime sits exactly on player center).

## Code Examples

Verified patterns from existing project files (no external sources needed — single-engine prototype).

### Adding a new schema key under existing group (verified by `assets/physics-schema.json:60-65`)

```json
"slime_follow": {
  "SLIME_FOLLOW_DELAY": 16,
  "SLIME_MAX_DIST": 100,
  "SLIME_REFORM_DIST": 8,
  "SLIME_LERP_FACTOR": 0.4,
  "SLIME_MAX_FOLLOW_SPEED": 7.0,
  "SLIME_CATCHUP_CURVE_K": 0.50,
  "SLIME_LOOKAHEAD_FRAMES": 8,
  "SLIME_LOOKAHEAD_FALLBACK_BIAS": 4.0,
  "SLIME_LOOKAHEAD_EPSILON": 0.1,
  "SLIME_STUCK_WINDOW_FRAMES": 36,
  "SLIME_STUCK_RECOVERY_COOLDOWN": 30,
  "SLIME_FLOAT_GROUND_K_FRAMES": 12,
  "SLIME_MODE_HYSTERESIS_FRAMES": 6
}
```

[VERIFIED: existing `slime_follow` group at `assets/physics-schema.json:60-65` is the addition site. Group is in `FEEL_GROUPS` (`src/ui/presets.py:18-22`) and Slime tab (`src/ui/panel.py:95`). No panel code change needed.]

### Reading a new tunable in slime.update() (verified pattern from slime.py:127, 141, 148, 168)

```python
# Source: existing pattern at slime.py:127 (juice regen) and slime.py:148 (follow delay).
# tuning.X resolves via PEP 562 __getattr__ on src.core.tuning.
self.dx = (delta_x / dist) * min(
    tuning.SLIME_CATCHUP_CURVE_K * (dist ** 0.5),
    tuning.SLIME_MAX_FOLLOW_SPEED,
)
```

### Overlay extension — additive new element (verified pattern from `src/core/overlays.py:478-490`)

```python
# Source: existing catch-up arrow at overlays.py:478-490 (uses pyxel.line + normalized direction).
# New: lookahead bias arrow — same primitive, different source vector.
def _draw_lookahead_bias_arrow(s, player_dx, player_facing_right):
    if abs(player_dx) >= tuning.SLIME_LOOKAHEAD_EPSILON:
        bias_x = player_dx * tuning.SLIME_LOOKAHEAD_FRAMES
    else:
        bias_x = (1.0 if player_facing_right else -1.0) * tuning.SLIME_LOOKAHEAD_FALLBACK_BIAS
    scx = s.x + s.w // 2
    scy = s.y + s.h // 2
    end_x = scx + int(bias_x * 0.25)  # scale for screen-readability
    pyxel.line(scx, scy, end_x, scy, 7)  # white = lookahead intent
```

### Mode flag glyph (new pattern, simple text)

```python
# Source: pyxel.text usage from overlays.py:243.
# Mode glyph: "F" or "G" above slime head, color-coded.
mode = getattr(s, "mode_is_float", None)
if mode is not None:
    glyph = "F" if mode else "G"
    color = 12 if mode else 11  # blue = float, green = ground
    pyxel.text(s.x + s.w // 2 - 2, s.y - 8, glyph, color)
```

### Stuck countdown bar (new pattern, simple rect)

```python
# Source: pyxel.rect usage from overlays.py:238 (status bar).
# Countdown bar: width proportional to remaining frames before stuck-recovery fires.
stuck = getattr(s, "stuck_frames", 0)
window = tuning.SLIME_STUCK_WINDOW_FRAMES
if stuck > window // 2:  # only show when halfway to firing
    bar_w = max(1, int(s.w * (stuck / window)))
    pyxel.rect(s.x, s.y - 3, bar_w, 1, 8)  # red bar
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Naïve `dx = target - x` then `±MAX_SHADOW_SPEED` clamp at slime.py:151-159 | Sqrt ease-out curve `speed = base + k*sqrt(dist)`, capped (D-09) | Phase 34 | Soft far-field, snappy near-field; eliminates rubber-banding. |
| `MAX_SHADOW_SPEED = 4.0` hardcoded module const at slime.py:157 | `tuning.SLIME_MAX_FOLLOW_SPEED` schema-driven, panel-tunable (D-05) | Phase 34 | Live tunability + no magic number (project memory `feedback_magic_numbers.md`). |
| Implicit "always grounded" follow | Hybrid float↔ground FSM (D-08) | Phase 34 | Handles airborne player gracefully; foundation for "Sein-style" feel. |
| No anticipation — slime always lags | `dx + facing` lookahead bias (D-11) | Phase 34 | S-L1 + S-L2 measurable lean; "alive, not draggy" feel. |
| Reform-distance teleport (hard snap) | Glow-fade reposition reusing dissipate/reform (D-10) | Phase 34 (extends Phase 2 dissipate primitive) | "Never visibly stuck" without ugly teleport; reuses SF6-burnout primitive. |
| `is_punted` collision branch (slime.py:129-143) and `Slime.punt()` (slime.py:178-182) | (Stripped — D-04) | Phase 34 | Removes orphan code path with no live writers since Phase 31.5. |

**Deprecated/outdated:**
- `Slime.is_punted = True` setter — no live writers in `src/` since Phase 31.5 strip [VERIFIED: grep finds only the `__init__` setter at slime.py:25 and an unguarded write at main.py:912 inside the dead collision block]. Strip per D-04.
- Unused `Slime` instance physics constants (`accel = 0.05`, `friction = 0.0375`, etc.) at slime.py:40-44 — vestiges from earlier physics-driven follow; nothing reads them post-Phase-25 migration. Strip per D-04.

## Recommended Tunable Seeds

These are the seed values for the 7 new (or promoted) `slime_follow` keys. Final values bake into `assets/presets/v2.0-default.json` per FEEL-TARGETS.md; `_v1.3-reference.json` stays FROZEN.

| Tunable | Recommended Value | Source / Rationale | Confidence |
|---------|-------------------|---------------------|------------|
| `SLIME_MAX_FOLLOW_SPEED` | **7.0** | D-13 budget math: 60-frame closure of 160 px requires peak ≥ 6.32 px/f at curve k=0.5; 7.0 adds ~10% headroom. Replaces `MAX_SHADOW_SPEED=4.0` per D-05. | HIGH (math) |
| `SLIME_CATCHUP_CURVE_K` | **0.50** | D-13 + D-09 closed form: `k = 2*sqrt(160)/60 ≈ 0.42`; round up to 0.50 for 60f budget compliance with cap-clipping headroom. | HIGH (math) |
| `SLIME_LOOKAHEAD_FRAMES` | **8** | D-11 constraint: must be ≤ `SLIME_FOLLOW_DELAY` (16). At MAX_WALK_SPEED=1.9 px/f, 8 frames = 15.2 px ≈ 1 tile lean — visible per S-L1 ±2 px tolerance, well under "4 tiles ahead" fail threshold. Half of FOLLOW_DELAY = symmetric tradeoff. | MEDIUM (heuristic) |
| `SLIME_LOOKAHEAD_FALLBACK_BIAS` | **4.0** | D-11 stationary-aim case (S-L2). 4 px ≈ 0.25 tile lean — visible but well under "1 tile ahead" fail threshold. | MEDIUM (heuristic) |
| `SLIME_LOOKAHEAD_EPSILON` | **0.1** (px/frame) | D-11 stationary threshold. `MAX_WALK_SPEED * WALK_FRICTION = 1.9 * 0.2 = 0.38` px/f decel — 0.1 captures "essentially stopped" without false-positive on tiny drift. | MEDIUM (heuristic) |
| `SLIME_STUCK_WINDOW_FRAMES` | **36** (0.6s @ 60fps) | D-10 platformer-companion convention is 30-60f. 36 sits in the middle; long enough to ride past brief collision-edge touches in S-S1, short enough to feel reactive in S-S2 sealed-pocket. | MEDIUM (heuristic) |
| `SLIME_STUCK_RECOVERY_COOLDOWN` | **30** (0.5s @ 60fps) | D-10 fade-arc length. Half of `SLIME_DISSIPATE_COOLDOWN` (240) — graceful but not slow. Visually distinct from full burnout. | MEDIUM (heuristic) |
| `SLIME_FLOAT_GROUND_K_FRAMES` | **12** (0.2s @ 60fps) | D-08 reach-tile probe budget. At `SLIME_MAX_FOLLOW_SPEED=7.0`, probe distance = 84 px ≈ 5 tiles — covers typical 3-tile drop in HeightSteps without false-positive on tall pits. | MEDIUM (heuristic) |
| `SLIME_MODE_HYSTERESIS_FRAMES` | **6** (0.1s @ 60fps) | S-M3 anti-jitter floor. 6 frames is the minimum the eye perceives as a state change; below this, mode toggling is invisible noise. | MEDIUM (heuristic) |

[ASSUMED: All MEDIUM-confidence values are heuristics derived from Sein/Ori-companion patterns + the D-13 math anchor. Phase 34 execution should validate each via panel-tuning sessions; FEEL-TARGETS.md row Pass conditions are the falsifiable check.]

## Open Questions

1. **`base` term in catch-up curve** — Pattern 1 uses `base = 0.0`. Is a non-zero base needed for natural drift on slow-player-movement cases? S-L2 will reveal if "too floaty / drifty" or "perfectly responsive."
   - What we know: D-09 phrases the curve as `base + k*sqrt(d)` — implies base may be nonzero.
   - What's unclear: Whether D-09's `base` refers to the pre-existing deque-induced velocity (which is implicit in the path-follow), OR a new schema key.
   - Recommendation: Start with `base = 0.0`. If S-L2 fails, promote `SLIME_FOLLOW_BASE_SPEED` to schema and seed at 0.5 px/f.

2. **`player.dx` threading into `slime.update()`** — D-11 needs current `player.dx` for the lookahead bias; `slime.update()` signature today does not accept it. This is mechanical (add parameter, update call site) but should be planned explicitly.
   - What we know: Call site is in `main.py` near `self.slime.update(...)`. One call site per game-state branch.
   - What's unclear: Whether to thread `player.dx` and `player.is_grounded` as new explicit params, OR pass `self.player` once. **Recommend: pass explicit primitives (`player_dx`, `player_is_grounded`)** to keep `Slime.update()` testable without a Player mock. Pattern matches existing args (player_x, player_y, player_facing_right).

3. **Stuck-recovery target source when `recall_trail` is empty** — Pattern 3 example shows `recall_trail` is only populated during `update_recall()` (slime.py:73). Path-follow stuck-recovery has no trail to sample.
   - What we know: `recall_trail` only fills during the recall code path.
   - What's unclear: Whether to (a) populate `recall_trail` from `history` deque on the fly during stuck-recovery, or (b) just fall back to `(player_x, player_y)` directly, or (c) sample from `self.history` deque (which IS populated during path-follow at slime.py:146).
   - Recommendation: **Option (c) — sample from `self.history`**. Pick the midpoint of the history deque (which represents player position ~8 frames ago). This is "closer to player" per D-10 phrasing without inventing new buffer. Document in the helper.

4. **Stuck counter location — entity vs. overlay** — Today, stuck counter lives in `src/core/overlays.py:83` (`_slime_stuck_frames`). It's currently for *visualization* only. D-10 makes it gameplay-relevant (triggers reposition).
   - What we know: Overlay counter increments on `vel_mag < 0.1`. Gameplay needs a similar counter that triggers reposition_with_fade().
   - What's unclear: Whether to keep two counters (one overlay, one entity) or consolidate.
   - Recommendation: **Move counter to entity** (`Slime.stuck_frames`). Overlay reads via `getattr(s, "stuck_frames", 0)` per Pitfall 7 guard. Eliminates duplicate tick logic; overlay becomes a pure-read consumer.

5. **`Gym_SlimeFollow` placeholder dimensions** — D-15 says "sealed 2x2 pocket reachable only by player teleport." D-16 says agent places placeholder, user finalizes.
   - What we know: Existing gyms (Gym_AccelRunway, etc.) are in `assets/output.ldtk`. Pml-to-ldtk pipeline regenerates `assets/output/simplified/Gym_*/data.json` on each run.
   - What's unclear: The exact LDtk authoring API for adding a new level + IntGrid pocket programmatically.
   - Recommendation: Plan task for D-16 placeholder = "open `assets/output.ldtk` in LDtk, add new level Gym_SlimeFollow with default 5x3 tile size (placeholder), commit. User finalizes geometry." Plan should NOT attempt to hand-edit `output.ldtk` JSON — it is LDtk-authored.

## Environment Availability

> Skipped — phase has no new external dependencies beyond existing project tooling (Python, Pyxel, pytest, LDtk). All five are already installed and verified by recent phases (Phase 33 shipped 2026-04-29 against the same toolchain).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 7.x (project standard) |
| Config file | none — relies on `tests/conftest.py` for pyxel mock |
| Quick run command | `python -m pytest tests/test_slime.py tests/test_overlays.py tests/test_tuning_migration.py -x -q` |
| Full suite command | `python -m pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SC-1 (catch-up) | 60-frame closure of 160 px gap (S-C1) | unit | `pytest tests/test_slime.py::test_catchup_60f_budget -x` | ❌ Wave 0 (extend test_slime.py) |
| SC-1 (catch-up curve) | sqrt curve produces speed = k*sqrt(dist) | unit | `pytest tests/test_slime.py::test_catchup_curve_shape -x` | ❌ Wave 0 |
| SC-2 (stuck) | Stuck-window counter triggers reposition_with_fade after N frames | unit | `pytest tests/test_slime.py::test_stuck_recovery_fires -x` | ❌ Wave 0 |
| SC-2 (stuck integration) | reposition_with_fade reuses dissipate_timer arc | unit | `pytest tests/test_slime.py::test_stuck_recovery_uses_dissipate -x` | ❌ Wave 0 |
| SC-3 (panel reach) | All 9 new SLIME_* keys present in tuning._flat_index after schema reload | unit | `pytest tests/test_tuning_migration.py::test_phase34_keys_loaded -x` | ❌ Wave 0 (new file or extend Phase 33 file) |
| SC-3 (panel smoothness) | Setting SLIME_MAX_FOLLOW_SPEED via tuning.set_value reaches Slime.update() next frame | unit | `pytest tests/test_tuning_livereach.py::test_slime_max_follow_speed_livereach -x` | ❌ Wave 0 (extend) |
| D-04 (strip) | `is_punted`/`punt`/dead attrs absent from `src/entities/slime.py` and `main.py` | unit | `pytest tests/test_slime.py::test_punt_attrs_stripped -x` | ❌ Wave 0 |
| D-08 (mode FSM) | mode_is_float = True when player.is_grounded = False | unit | `pytest tests/test_slime.py::test_mode_float_when_player_airborne -x` | ❌ Wave 0 |
| D-08 (mode FSM probe) | mode_is_float = False when player grounded AND tile reachable in K frames | unit | `pytest tests/test_slime.py::test_mode_ground_when_reachable -x` | ❌ Wave 0 |
| D-08 (hysteresis) | mode does not flip every frame on rapid is_grounded toggle | unit | `pytest tests/test_slime.py::test_mode_hysteresis -x` | ❌ Wave 0 |
| D-11 (lookahead) | target_x bias matches player.dx * SLIME_LOOKAHEAD_FRAMES | unit | `pytest tests/test_slime.py::test_lookahead_bias_dx -x` | ❌ Wave 0 |
| D-11 (lookahead fallback) | target_x bias matches facing direction when |player.dx| < ε | unit | `pytest tests/test_slime.py::test_lookahead_fallback_facing -x` | ❌ Wave 0 |
| D-02 (overlay extension) | F5 overlay renders mode glyph + lookahead arrow + stuck-countdown bar without crash | unit | `pytest tests/test_overlays.py::test_slime_overlay_phase34_surfaces -x` | ❌ Wave 0 (extend) |
| All scenarios (S-C/S-S/S-M/S-L/S-P) | Falsifiable conditions PASS | manual | Human playtest via panel + 34-FEEL-TARGETS.md | ✅ FEEL-TARGETS.md exists |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_slime.py tests/test_overlays.py tests/test_tuning_migration.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`; manual S-* targets all PASS in 34-FEEL-TARGETS.md.

### Wave 0 Gaps
- [ ] `tests/test_slime.py` — extend with 11+ new tests (catch-up, stuck, mode, lookahead, strip-verification). Existing file at `tests/test_slime.py` covers init/follow/regen/scaling/reform/drill — no Phase 34 surface yet.
- [ ] `tests/test_overlays.py` — extend with overlay-extension test for new AI surfaces (mode glyph, lookahead arrow, stuck countdown bar).
- [ ] `tests/test_tuning_migration.py` — extend with `test_phase34_keys_loaded` asserting all 7 new schema keys (+ promoted SLIME_MAX_FOLLOW_SPEED) seed defaults.
- [ ] `tests/test_tuning_livereach.py` — extend with one livereach test for `SLIME_MAX_FOLLOW_SPEED` (verifies set_value → next-frame visibility per Phase 25 contract).
- [ ] No framework install needed. pyxel mock and event_bus reset autouse fixture already exist in `tests/conftest.py`.

### Manual-Only Verifications (FEEL-TARGETS.md)

The 13 S-* targets in `34-FEEL-TARGETS.md` are manual playtests by design (subjective "Ori-feel" cannot be automated). Verification phase fills the Result column in place.

## Project Constraints (from CLAUDE.md and project memory)

`./CLAUDE.md` does not exist in the working directory. The following project memory files are load-bearing for Phase 34:

| File | Directive | Phase 34 Application |
|------|-----------|----------------------|
| `feedback_magic_numbers.md` | Use named constants or comments for all numeric literals | Drives D-05 promotion of `MAX_SHADOW_SPEED → SLIME_MAX_FOLLOW_SPEED`. Also: keep `RECALL_TRAIL_MAX_LENGTH = 6` named (current state at slime.py:74 is correct). |
| `feedback_no_agent_level_authoring.md` | Level content goes in `.ldtk`, never `simplified/`; placeholders OK if user can finalize | Drives D-16 split. Plan task = LDtk placeholder only; user finalizes. **Do NOT** edit `assets/output/simplified/Gym_SlimeFollow/`. |
| `reference_schema_contract.md` | `assets/entity-schema.json` shared with pml-to-ldtk converter | `Gym_SlimeFollow` placeholder must respect entity-schema contract — same IntGrid values, same default room size (320x176 unless variable). |
| `project_reanimator_anim_architecture.md` | `src/anim/` mirrors gameplay state via driver dataclass | Reinforces D-06 — slime AnimFSM is OUT of scope this phase; idle bob etc. wait for the future Slime AnimFSM phase. |
| `project_door_event_system.md`, `project_block_gate_hierarchy.md`, `project_door_target_room_simplification.md` | Door/block hierarchy semantics | Not directly relevant to Phase 34 (no new doors / blocks). |
| `project_drill_entry_juice_gate.md` | Drill activates at any juice; WINDUP 100% gate is separate | Not directly relevant; just don't accidentally re-consolidate. |
| `feedback_pyxel_mock_false_positive.md` | conftest mock accepts any pyxel API call; verify against Pyxel source | Phase 34 overlay tests assert specific `pyxel.line/circ/text` calls — be careful not to assert call signatures that the real Pyxel doesn't accept. |
| `feedback_worktree_regression.md` + `feedback_push_before_worktrees.md` | Fast-forward merges overwrite files; push before worktree spawning | Operational reminder for the planner — not a research finding. |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `base = 0.0` in the sqrt curve is correct for S-C1 hold-still case | §Architecture Patterns Pattern 1, Open Question #1 | If wrong: slime drifts at near-zero speed near target; FEEL playtest reveals "laggy at close range." Fix: promote `SLIME_FOLLOW_BASE_SPEED` to schema. Recoverable in execution. |
| A2 | `SLIME_LOOKAHEAD_FRAMES = 8` produces a visible-but-not-overshooting lean | §Recommended Tunable Seeds | If wrong: S-L1 fails. Fix: panel-tune up or down. Recoverable. |
| A3 | `SLIME_STUCK_WINDOW_FRAMES = 36` is in the right band | §Recommended Tunable Seeds | If wrong: false positives (firing on every collision touch) or no firings (S-S2 sealed pocket fails). Fix: panel-tune. Recoverable. |
| A4 | `SLIME_FLOAT_GROUND_K_FRAMES = 12` covers HeightSteps drops without false-positive on tall pits | §Recommended Tunable Seeds | If wrong: S-M2 mode demote feels jerky (too short) or never demotes (too long). Fix: panel-tune. Recoverable. |
| A5 | Stuck-recovery target should be the midpoint of `self.history` (not `recall_trail`) | §Open Questions #3 | If wrong: reposition lands too far from player or too close. Fix: change midpoint to a different fraction. Recoverable. |
| A6 | The positional-offset variant of D-11 is preferable to the deque-index-offset variant | §Architecture Patterns Pattern 2 | If wrong: visual trail collapses (Pitfall 4). Fix: revert to positional offset. Recoverable. |
| A7 | `tuning.load()` falls through to schema defaults when a key is absent in the active preset | §Common Pitfalls Pitfall 6 | If wrong: game crashes on _v1.3-reference preset load with new keys. Fix: extend `tuning.load()` migration like Phase 33. **Verify in Wave 0.** |
| A8 | Player.dx and player.is_grounded should be threaded as explicit primitives into `slime.update()` (not as a Player reference) | §Open Questions #2 | If wrong: harder to test. Fix: refactor signature. Recoverable but mildly costly. |
| A9 | `_v1.3-reference.json` does not need updating — it stays FROZEN even though new schema keys exist | §Recommended Tunable Seeds, §FEEL-TARGETS context | If wrong: Phase 33 frozen-preset test (`test_v1_3_reference_preset_remains_frozen`) fires false-positive. Verify the test only checks keys present in v1.3, not new keys. **Verify in Wave 0.** |
| A10 | `Gym_SlimeFollow` LDtk placeholder authoring is best done by opening `assets/output.ldtk` in LDtk, not by JSON edit | §Open Questions #5 | If wrong: agent edits JSON, simplified/ regenerates wrong, level loads broken. Fix: use LDtk app. Already aligned with `feedback_no_agent_level_authoring.md`. |

## Sources

### Primary (HIGH confidence — verified by direct file read in this session)
- `src/entities/slime.py` (full file read, 294 lines) — slime path-follow code structure, dissipate/reform primitive, recall_trail, history deque, MAX_SHADOW_SPEED hardcode location
- `assets/physics-schema.json` (full file read, 188 lines) — slime_follow group structure, schema version, derived layout
- `src/core/overlays.py` (full file read, 491 lines) — F5 slime overlay extension points, existing stuck counter and catch-up arrow patterns, color palette in use
- `src/ui/panel.py` (lines 85-100) — TAB_DEFS Slime tab routing for slime_follow group (auto-discovery confirmed)
- `src/ui/presets.py` (lines 1-35) — FEEL_GROUPS includes `slime_follow`; key-discovery via `tuning._flat_index`
- `src/entities/player.py` (lines 315-360) — confirms `player.dx` is the canonical horizontal velocity (used in WALK_ACCEL/FRICTION/MAX_WALK_SPEED clamp at L351)
- `tests/test_slime.py` (full file read, 117 lines) — current test surface, no Phase 34 coverage yet
- `tests/conftest.py` (lines 1-80) — pyxel mock pattern + autouse event_bus reset fixture
- `.planning/phases/34-slime-follow-ai-feel-pass/34-CONTEXT.md` (full file read, 141 lines) — all 17 D-NN locked decisions
- `.planning/phases/34-slime-follow-ai-feel-pass/34-FEEL-TARGETS.md` (full file read, 89 lines) — already drafted at context-gathering, 13 S-* targets, reference values table
- `.planning/phases/27-diagnostic-overlays/27-CONTEXT.md` (full file read, 101 lines) — overlay design, D-05 slime overlay scope
- `.planning/phases/27-diagnostic-overlays/27-02-PLAN.md` (full file read, 432 lines) — F5 overlay implementation pattern (the reference for D-02 extension)
- `.planning/phases/27-diagnostic-overlays/27-VALIDATION.md` (lines 1-60) — validation framework template
- `.planning/phases/29-player-movement-feel-pass/29-FEEL-TARGETS.md` (full file read, 80 lines) — FEEL-TARGETS.md format template
- `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-FEEL-TARGETS.md` (full file read, 120 lines) — latest FEEL-TARGETS multi-prefix scheme example
- `.planning/STATE.md`, `.planning/PROJECT.md`, `.planning/ROADMAP.md` — phase position, success criteria, recent decisions
- `.planning/config.json` — `nyquist_validation: true` confirmed; Validation Architecture section required
- `main.py` lines 905-925 — D-04 punt collision strip target verified

### Secondary (MEDIUM confidence — derived but not externally cross-verified)
- D-13 catch-up budget math (closed-form solution to `dx/dt = -k*sqrt(x)`) — derived in this research; not externally verified but mathematically sound
- 30-60f stuck-detection convention for platformer companions — CONTEXT.md cites this as "typical platformer companion uses 30-60f"; not externally cross-verified to a specific reference

### Tertiary (LOW confidence — none)
None — every claim in this research is either verified by direct file read or derived from the locked CONTEXT.md decisions + closed-form math.

## Metadata

**Confidence breakdown:**
- Standard Stack: HIGH — single-engine prototype, no external deps, all libraries verified by direct read.
- Architecture (patterns 1-4): HIGH for Pattern 1 (math), MEDIUM for Patterns 2-4 (heuristic-driven design choices that need panel validation in execution).
- Code-reuse paths (D-10 reposition_with_fade, deque lookahead): HIGH — verified by direct read of slime.py:79-98 + slime.py:20, 146.
- Integration points (overlay, panel auto-discovery, LDtk pipeline): HIGH for overlay + panel (verified by direct read); MEDIUM for LDtk (project memory drives the workflow, but actual placeholder authoring path is user-driven).
- Pitfalls: MEDIUM-HIGH — Pitfalls 1, 6, 7 are verified gaps (need plan-level mitigation); Pitfalls 2-5, 8 are forecast risks based on the design.
- Numeric seeds: HIGH for `SLIME_CATCHUP_CURVE_K` and `SLIME_MAX_FOLLOW_SPEED` (math); MEDIUM for the other 7 (heuristics, panel-tune in execution).

**Research date:** 2026-05-02
**Valid until:** 30 days (no fast-moving external dependencies; project codebase is stable on this surface area)
