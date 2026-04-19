# Phase 30: Fusion Lifecycle Design Doc - Context

**Gathered:** 2026-04-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Produce a locked `.planning/FUSION-DESIGN.md` that narrows the prototype to **one fusion mechanic (Drill Dive)**, defines the initiate/sustain/end FSM under a **100%-gated juice-as-mana economy**, specifies a unified single-button (Z) slime/fusion input model with a companion pogo-dive verb, captures v1.3 drill-dive behavior as the Phase 32 regression target, and lists behavioral acceptance checks Phase 32 must satisfy.

Design only. No code changes. No tuning changes.

**Out of scope (other phases):**
- Any code refactor (Phase 32)
- Any feel tuning / slider values (Phase 33)
- Animation content / particle bank (Phase 31)
- Slime follow/AI retune (Phase 34)
- Juice polish (shake, hitstop, pooled particles) (Phase 35)
- Cut-ability code removal — requires a new phase between 30 and 32 (see Deferred)

</domain>

<decisions>
## Implementation Decisions

### Scope pivot — one fusion, not six

- **D-01:** Prototype ships with **one fusion mechanic: Drill Dive**. The 5 other v1.1 fusion abilities (Slime Ram, Directional Hold, Charge Shot, Bubble Shield, Slime Boost) are cut from the prototype.
- **D-02:** FUSION-DESIGN.md explicitly lists the cut abilities as "out of prototype scope, revisit post-prototype." Code for the cut abilities is stripped in a follow-up phase between 30 and 32 (see Deferred → "New phase needed").
- **D-03:** The prototype's fusion loop is: **shoot to daze the boss → drill to finish**. That's the combat fantasy PROJECT.md already names ("using a companion slime to power a destructive Drill Dive that enables both exploration and combat").

### Base movement verb — Pogo Dive (unfused)

- **D-04:** Unfused **DOWN+V in air = pogo bounce** (Shovel Knight shovel-drop style). Strikes downward, bounces on contact with enemies and breakables only. Pure solid ground = no bounce, just lands.
- **D-05:** Pogo is **free** — no juice cost, no cooldown, always available. Juice is reserved for fusion.
- **D-06:** Pogo teaches the drill's downward commitment before the player ever fuses. Same input (DOWN+V air), fusion upgrades the outcome.

### Fusion verb — Drill Dive (fused)

- **D-07:** Fused **DOWN+V in air = pure plunge**. No bounce. Drills through soft/CRACKED blocks, consumes juice per block.
- **D-08:** Drill ends on: (a) hit truly solid (non-breakable) terrain, (b) juice hits 0 (auto-unfuse + dissipate), or (c) manual unfuse via Z-hold mid-drill (tunable — may be disabled if it feels wrong in playtest).
- **D-09:** Drill retains no pogo behavior. Commitment is the point.

### Unified input model — Z is the slime/fusion button

- **D-10:** Z semantic is uniform: **tap = projectile, hold = toggle fusion state**. No mode-specific rebinds.
- **D-11:** Tap-vs-hold disambiguation uses a short frame threshold (target ~8 frames, tuned in Phase 33). Tap below threshold fires spit/daze shot; hold past threshold begins recall.
- **D-12:** Unfused Z actions:
  - **Tap:** spit projectile (weak, free)
  - **Hold (juice < 100%):** recall slime + accelerated juice regen while held
  - **Hold (juice = 100% + slime docked at player):** auto-triggers windup → fuse (no re-press needed — continuous hold completes the ritual)
  - **Release any time before windup completes:** slime returns to follow mode (NOT freeze; freezing would conflict with spit responsiveness since Z is also the shoot button)
- **D-13:** Fused Z actions:
  - **Tap:** daze shot (same projectile sprite/physics as spit but upgraded — more damage, daze effect on hit, juice cost)
  - **Hold past threshold:** manual unfuse (short windup, then slime ejects back to follow)
- **D-14:** Daze shot is mechanically the same projectile as unfused spit with juice cost and daze-on-hit. Reuses spit implementation. Visual upgrade (larger sprite / particle trail) signals "this is a fused shot."

### Juice economy — juice-as-mana with a 100% gate

- **D-15:** Fusion **requires 100% juice to initiate**. The juice bar becomes a binary readiness meter, not a fusion duration slider. Full = ready; anything less = waiting.
- **D-16:** The 100% gate enables the "oh I need 1 more juice for this puzzle" design primitive. Level design can intentionally put drill-required blocks adjacent to juice-starved zones.
- **D-17:** **Accelerated regen ritual:** while Z is held AND slime is active (not dissipated) AND slime is docked at the player, juice regenerates at an accelerated rate. This is the "power up for fusion" ritual — stand safe, pull slime in, charge, commit.
- **D-18:** Baseline (passive) juice regen continues at a slower rate any time the slime is active.
- **D-19:** Once fused, any remaining juice is spent by fused actions (daze shot, per-block drill cost). The 100% gate applies to *entering* fusion only, not staying fused.
- **D-20:** Fused duration = how much juice you had at fuse moment minus what your fused actions consumed.

### Fusion FSM — initiate/sustain/end

- **D-21:** FSM phases: `IDLE → RECALL → WINDUP → FUSED → EXIT`.
  - **IDLE:** slime following, player unfused
  - **RECALL:** Z held, slime moving toward player, accelerated regen active if slime docked
  - **WINDUP:** juice hit 100% with slime docked, Z still held — short merge animation (target 8-16 frames, tuned in Phase 33)
  - **FUSED:** latched state; Z is free for daze shot; DOWN+V air = drill
  - **EXIT:** auto (juice=0 → dissipate + cooldown) OR manual (Z-hold → windup → slime ejects unharmed)
- **D-22:** "Docked" is not a separate state — it's frame 0 of WINDUP. The moment slime contacts player with Z held AND juice=100%, WINDUP begins.
- **D-23:** WINDUP release = free cancel. Slime returns to follow. No cost, no punishment. Forgiving for prototype playtesting.
- **D-24:** Auto-unfuse on juice=0 → slime dissipates (v1.1 behavior D-05 retained). Dissipation imposes a cooldown before the slime can be recalled again — this is the real punishment for over-spending.

### Contract capture method

- **D-25:** Capture current v1.3 drill-dive behavior via **code archaeology + written spec**. Read `player.py` drill code, extract exact frame counts / velocity / juice costs / exit conditions into the doc. Regression target is "this spec."
- **D-26:** No video/input recordings required. No frame-by-frame diffing infrastructure.
- **D-27:** The drill-dive contract is a **behavioral checklist** Phase 32 must verify by inspection + smoke test. Example bullet form: "Drill starts within N frames of DOWN+V-fused-air input," "Drill breaks CRACKED_V at M juice/block," "Drill ends on solid contact or juice empty with dissipate."
- **D-28:** No pytest stubs required from Phase 30. Phase 32 may choose to author automated checks during its refactor, but the acceptance target is the checklist.

### Design doc structure & lock

- **D-29:** Single comprehensive file: `.planning/FUSION-DESIGN.md`. Covers: scope pivot rationale, input model, FSM, juice economy, drill-dive contract, cut-ability list + rationale, acceptance checklist for Phase 32.
- **D-30:** No separate contract files, no separate FSM diagram artifact. ASCII state table or Mermaid diagram inline in the doc is fine.
- **D-31:** Doc lock mechanism = **YAML frontmatter**:
  ```yaml
  ---
  status: LOCKED
  locked_at: YYYY-MM-DD
  locked_commit: <sha>
  ---
  ```
  Phase 32's plan references `locked_commit` to verify it is building against the agreed spec.
- **D-32:** FUS-01, FUS-02, FUS-03 were referenced in ROADMAP for Phase 30 but never formally defined. Phase 30 defines them inline in FUSION-DESIGN.md as requirements scoped to the locked design.

### Claude's Discretion

- Exact frame thresholds (tap-vs-hold disambiguation, windup duration, unfuse windup duration) — drafted from current v1.3 values where they exist; Phase 33 retunes.
- Exact juice costs (spit, daze shot, per-block drill) — carried forward from v1.3; Phase 33 retunes.
- Whether manual unfuse mid-drill is allowed — author as "permitted unless it feels wrong in playtest"; Phase 33 may disable.
- Daze-on-hit effect details (duration, stun behavior) — carried forward from existing boss stagger logic where one exists.
- How CRACKED_V vertical gating blocks behave under the single-fusion model — drill already handles them in v1.1; confirm via code archaeology, doc as-is.
- FSM diagram format (ASCII table vs Mermaid) — author's choice when writing the doc.
- Scope pivot rationale framing in the doc — Claude writes, user reviews the lock.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project-level framing
- `.planning/PROJECT.md` — core value ("destructive Drill Dive"), v1.0/v1.1 decision log including fusion rules D-01..D-05 (charge-to-fuse, mana shield, dissipation), 6-ability v1.1 list now being cut down to 1

### Prior context — movement feel pass
- `.planning/phases/29-player-movement-feel-pass/29-CONTEXT.md` — preset model, feel-target format, v1.3 baseline preservation rule. Drill must respect v2.0-default movement feel.

### Tuning system (Phase 24-25) — for documenting current values
- `src/core/tuning.py` — mutation API, `get_baseline()` returns v1.3 values used for regression target
- `assets/physics-schema.json` — v0.3.x schema; groups: `slime` (JUICE_MAX, JUICE_REGEN_RATE, JUICE_MIN_SCALE, SLIME_SPIT_COST), `drill` (drill speed, cost, iframes), `charge_shot`, `boost`, `bubble_shield`. Phase 30 reads these to document current v1.3 drill values.
- `assets/presets/_v1.3-reference.json` — frozen v1.3 preset. Canonical source of current-behavior values for the contract.

### Current fusion & slime code — primary source for code archaeology
- `src/entities/player.py` — `fuse()` / `unfuse()` (~L89-110), `start_ram()`/`apply_ram_physics()`/`end_ram()` (cut ability, for code-strip phase), mana shield (~L186-194), bubble shield logic (~L277-314, cut), charge shot (~L618-675, cut), start/end_boost (~L550-605, cut), drill dive entry and exit (search "drill" / DRILL_ in file)
- `src/entities/slime.py` — juice state, `dissipate()`, spit projectile spawn, follow AI. Juice drain/regen rates read at use-site from tuning.
- `src/core/event_bus.py` (wherever Phase 26 placed it) — `fuse_start`, `fuse_end`, `ram_start`, `charge_shot_fire` events. Phase 30 inherits these names; new events for drill lifecycle (drill_start/drill_block_break/drill_end) documented in the doc.

### Event + animation skeleton (Phase 26)
- `src/anim/player_anim.py` — FSM skeleton. Phase 30's drill lifecycle FSM aligns with the anim FSM's state hooks; Phase 31 fills in transition frames.

### Live panel (Phase 28) — for Phase 33 tuning later
- `src/core/tuning_panel.py` — Phase 33 uses this to retune drill + regen values against the locked design. No direct input into Phase 30.

### Assets relevant to cut abilities (inform what to strip)
- `src/entities/player.py` regions for ram_dx/ram_dy, shield_*, charge_shot_*, boost_*, has_shield/has_boost flags
- `assets/physics-schema.json` groups: `ram`, `charge_shot`, `boost`, `bubble_shield` — flagged for removal in the follow-up code-strip phase

### Historical context — v1.1 fusion design (informs what's being cut)
- `.planning/milestones/v1.1-REQUIREMENTS.md` — original ABL-01..06 requirements. Phase 30 supersedes these for the prototype.
- `.planning/milestones/v1.1-phases/08-new-fusion-abilities/` — plans 08-03, 08-04 documenting current-behavior semantics of charge-to-fuse, mana shield, ram, charge shot. Useful for understanding *why* current code looks the way it does.

**No external specs for Phase 30 requirements** — FUS-01/02/03 were never formally defined in a REQUIREMENTS file. Phase 30's FUSION-DESIGN.md defines them inline.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `event_bus` — `fuse_start` / `fuse_end` events already exist; Phase 30 doc introduces new drill-specific events (drill_start, drill_block_break, drill_end) and manual_unfuse_start to support the FSM
- `tuning.get_baseline()` — returns v1.3 frozen values; use to document current drill velocities / costs / frame counts
- `slime.dissipate()` — v1.1 burnout behavior carried forward for juice-empty auto-unfuse
- Spit projectile code path — reused verbatim for daze shot with juice cost + daze-on-hit layer added in Phase 32

### Established Patterns
- **Charge-to-fuse input model (v1.1 D-01/D-02):** hold Z to pull slime in, auto-fuse at contact+full juice. Phase 30 **preserves the continuous-hold ritual** but reframes it as "hold Z → accelerated regen → auto-fuse when 100%." User sees no behavioral break from v1.1 except the 100% gate.
- **Mana shield pattern (v1.1 D-04):** fused damage drains juice instead of HP. Phase 30 **retains this**, reframed as "any fused damage also counts toward the fusion timer."
- **Dissipation on juice empty (v1.1 D-05):** slime burns out with a cooldown. Phase 30 **retains this** as the forced-EXIT behavior.
- **Use-site tuning reads (Phase 25):** all drill values read from `tuning.X` at use-site. The design doc documents current values but does not dictate future ones — Phase 33 retunes live.

### Integration Points
- `.planning/FUSION-DESIGN.md` — new top-level doc under `.planning/` (sibling of PROJECT.md, ROADMAP.md). Locked via frontmatter.
- `.planning/ROADMAP.md` — Phase 30 completion triggers roadmap update: (a) add new code-strip phase between 30 and 32 with number 30b / 31 / or via `/gsd-insert-phase`; (b) shrink Phase 32 scope to single-ability refactor; (c) shrink Phase 33 scope to single-ability feel pass.
- Future (Phase 32): code reads `FUSION-DESIGN.md` frontmatter to verify `locked_commit` matches the commit the refactor is built against.

</code_context>

<specifics>
## Specific Ideas

- "Pogo = Shovel Knight, fusion = drill" — same DOWN+V air verb, fusion is the upgrade. Teaches muscle memory before introducing the mechanic.
- "Shoot to daze → drill to kill" is the boss fight. The whole input model exists to make that loop feel natural.
- "Oh I need 1 more juice for this puzzle" — the 100% gate is chosen specifically to create this felt design moment.
- Hold-Z-charge-to-fuse-while-standing-still has a Hollow Knight Focus-heal / Zelda boomerang-charge texture. Ritual, commitment, reward.
- Juice bar is a **readiness meter, not a duration bar**. Full = ready. Anything less = waiting.
- Every fused action burns the timer; the player is always trading "stay fused longer" against "drill/shoot now."
- The cut abilities are not defects of v1.1 — they're expansion-era content that doesn't earn its keep in a feel-first prototype. The doc frames the cut as prototype focus, not rejection.

</specifics>

<deferred>
## Deferred Ideas

- **NEW PHASE NEEDED — cut-ability code strip.** Phase 30 is design-only, but D-02 scopes out 5 abilities. A code-strip phase (proposed: 30b or inserted between 30 and 32 via `/gsd-insert-phase`) must remove ram/hold/charge_shot/bubble_shield/boost code from `player.py`, `slime.py`, tuning groups from `physics-schema.json`, and any references in plans/docs. Hard gate before Phase 32.
- **Phase 32 scope shrinks** to single-ability refactor: `src/fusion/` package with FusionAbility Protocol, FusionManager shell, **one** DrillDive module (not six). Protocol still future-proofs for post-prototype ability expansion.
- **Phase 33 scope shrinks** to drill-dive feel pass only. Windup/sustain/end curve, particle color, SFX, daze-shot texture. The per-ability identity goal reduces to drill identity.
- **Post-prototype abilities** (ram, hold, charge shot, bubble shield, boost) — not deleted from design thinking, just out of scope for this build. Post-prototype transition to Godot/Unity is the natural re-evaluation point.
- **Manual unfuse mid-drill** — allowed by default in the design doc but flagged for Phase 33 to disable if it feels wrong.
- **FUS-01/02/03** — defined inline in FUSION-DESIGN.md (not in a separate REQUIREMENTS file) since no v2.0 requirements doc exists.
- **Daze projectile distinctness** — prototype uses the same sprite/physics as spit with a visual upgrade. Post-prototype may differentiate (piercing, arc'd, slime-as-projectile) if playtest shows the upgrade isn't felt.

</deferred>

---

*Phase: 30-fusion-lifecycle-design-doc*
*Context gathered: 2026-04-19*
