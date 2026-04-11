# Feature Research — Jelly Roll Proto v2.0 Game Feel

**Domain:** 2D Metroidvania game-feel systems (subsequent milestone)
**Researched:** 2026-04-11
**Confidence:** MEDIUM-HIGH

## Context

This is **not a greenfield project**. The v1.x prototype already ships working movement, fusion, combat, bosses, save, and map systems. The user's verdict is "works to spec but doesn't feel right." v2.0 Game Feel is a polish/redesign milestone targeting five axes:

1. Live-tuning panel (GMTK Platformer Toolkit–style)
2. Animation state machine with transition frame insertion
3. Fusion lifecycle redesign (initiate/sustain/end)
4. Input responsiveness audit (beyond existing coyote/buffer)
5. Juice polish (squash/stretch, shake, hitstop, particles, sound)

All features below are scoped to these axes. Core gameplay (movement, abilities, enemies, rooms) is NOT in scope for fresh design — only for feel retuning.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features any well-regarded 2D platformer/Metroidvania is expected to have. Missing them = "why does this game feel off?"

#### Live-Tuning Panel

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Hot-reload of `physics-schema.json` on save | Dev can iterate without restart; this is the whole point of the milestone | LOW | File watcher + schema re-parse + re-bind to active systems; Pyxel has no reload hook so use mtime poll in `update()` |
| Grouped slider UI (Movement / Jump / Wall / Slime Follow / Fusion / Juice / Anim Timing) | GMTK Toolkit precedent — every modern tuning panel groups by system; flat lists are unusable past ~15 params | LOW-MED | Pyxel has no ImGui; build minimal slider widget (label + bar + numeric readout); ~30-50 params expected |
| Min/max/step per parameter declared in schema | Prevents invalid values (negative gravity, 0 friction) and gives the slider its range | LOW | Extend `physics-schema.json` with `{value, min, max, step}` tuples |
| Reset-to-default per parameter and per group | Essential — tweaking 10 params then losing track of what changed is the #1 tuning failure mode | LOW | Keep a copy of the on-disk values separate from the live values |
| Preset save/load (named JSON snapshots) | GMTK Toolkit has "floaty / tight / Celeste / Mario" presets; enables A/B comparison | LOW | Dump live schema to `.planning/presets/<name>.json`; load restores schema state |
| Pause-while-editing toggle | Some params (gravity, jump force) can't be safely changed mid-air — either pause or clamp on apply | LOW | Single bool; default on |
| Toggle panel visibility (tab/grave key) | Panel must not interfere with normal play; dev toggles it in/out | LOW | Single input binding |
| Schema is single source of truth (code reads from schema, not constants.py) | PROJECT.md explicitly requires this; without it, live-tuning changes don't propagate | MEDIUM | Replace ~50 constants in `constants.py` with schema lookups; preserve pml-to-ldtk converter contract |

**Reference:** [GMTK Platformer Toolkit](https://gmtk.itch.io/platformer-toolkit) exposes ~30 variables grouped by jump/movement/polish; its "Behind The Code" devlog documents the architecture.

#### Animation State Machine

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Explicit FSM replacing hardcoded state toggle | Current system is a 2-frame switch on hardcoded u offsets (`player.py:790`); there is no real state machine, which is why transitions are impossible | MEDIUM | Classic platformer FSM: Idle → Run → Jump → Fall → Land → WallSlide → WallJump → Kick → Hitstun → Fuse → Ability; each state owns its frame list, loop/oneshot flag, and on-enter/on-exit callbacks |
| Event hooks: `direction_change`, `jump_start`, `land`, `fall_start`, `wall_touch`, `drill_impact`, `fuse_start`, `fuse_end` | Juice, sound, and particles all want to hook these moments. PROJECT.md already lists these as the target hook set | LOW-MED | Publish/subscribe pattern — systems register callbacks on events, FSM fires them on transitions |
| Transition frame insertion (jump anticipation, land recovery, turn-around, fall transition) | Celeste's squash-stretch precedent: even 1-2 frames inserted at the right moment makes the character feel responsive. 2-frame jump crouch makes jump feel instant despite adding latency | LOW-MED | Each transition frame is a one-shot state with a fixed duration (1-3 frames) that auto-transitions when done; blocks input queue vs. ignores it is a per-transition choice |
| Procedural squash/stretch overlay (scale X/Y) | Works alongside sprite frames — Celeste scales Madeline's sprite alongside frame animation; cheap in Pyxel via `pyxel.blt` with separate horizontal/vertical draws or via pre-baked variants | MEDIUM | Pyxel's blt can't actually scale; implement via 3-4 pre-rendered variants (tall-stretch, normal, squash, wide-squash) and switch based on a float `scale_phase` value |
| Animation-driven audio/particle triggers | Juice techniques all want "on land, play thud + dust"; event hook system delivers this | LOW | Subscriber system on FSM events |
| Facing flip with 1-frame turn-around pause | Instant flip feels robotic; a single-frame "braking" pose sells direction change | LOW | Insert `Turn` state between Run-left and Run-right (1-2 frame duration) |

**Reference:** [Celeste tiny animation article (Wayline)](https://www.wayline.io/blog/art-of-tiny-animations-game-feel); [Celeste Wiki](https://celeste.ink/wiki/Tech); [Sprite-AI 12 animation principles for pixel art](https://www.sprite-ai.art/guides/animation-principles).

#### Input Responsiveness

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Coyote time + jump buffer audit | Already exists; audit = verify timings are consistent across ground/wall/ledge, not split-brain | LOW | Check coyote applies BEFORE buffer resolution (standard priority per all tutorials) |
| Input-state visualizer (overlay showing pressed / held / buffered / consumed) | Dev-facing but required for audit to be meaningful; without the overlay, "feels laggy" is unfalsifiable | LOW | Draw small glyphs top-right showing raw vs. buffered state of each action |
| Cancel windows on ability/kick/ram moves | Standard action-game term: the N frames at the end of an attack where the next input is allowed; without it, every action commits for full duration and combat feels stiff | MED | Each ability state declares `cancel_window_start` / `cancel_window_end` frames; input consumed in window = immediate transition |
| Hold vs tap detection with `hold_threshold_frames` | Charge-to-fuse already exists but threshold is hardcoded; also needed for variable jump (tap = short hop, hold = full jump) | LOW | Single int in schema; `tap` = released before threshold, `hold` = still held after threshold |
| Input priority list (documented explicitly) | When drill-dive input overlaps with jump buffer and ram input on the same frame, deterministic priority prevents "sometimes it does X" bugs | LOW | Explicit ordered list in code/schema: Pause > Fuse > Ability > Jump > Move |
| Frame-accurate input capture (latch on button-down, don't sample during draw) | Standard; already likely present but worth confirming | LOW | Pyxel's `btnp` handles this; audit that all input checks use `btnp`/`btnr` not `btn` where edge is meant |

**Reference:** Hollow Knight's light input buffering (attacks only) contrasts Celeste's heavier buffering; both work because they're consistent. See [SMW Central "Tolerance Timer"](https://www.smwcentral.net/?p=section&a=details&id=26945) for coyote-before-buffer priority rule.

#### Juice Polish (the Nijman "30 tricks" tier)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Screen shake on landing, hit, impact | Nijman's "Art of Screenshake" pitch — the single highest ROI juice technique; 0.1-0.3 sec shake with easing taper | LOW | Global camera offset added during draw; decays each frame; shake direction randomized within a cone |
| Hitstop (freeze-frame on impact) | 3-8 frame freeze on enemy hit / boss hit / drill-dive connect. Makes hits feel weighty. Most cited juice technique after screen shake | LOW | Global timer that freezes `update()` (but not draw) for N frames |
| Dust particles on land / jump / skid / wall slide | Celeste's 3-frame dust poof (small → bigger → fading) makes landing feel grounded | LOW | Simple per-particle struct with position/velocity/ttl; 5-10 particles max per emit |
| Squash-stretch on jump/land | Already listed under animation but contributes here too; Celeste scales 1 row of pixels and it's transformative | MED | See animation section; cheap variant = global sprite scale factor with 3-4 stops |
| Impact flash (invert/white frame on damage taken) | Ubiquitous in Metroidvanias (Hollow Knight, Ori, Symphony of the Night); cheapest "I got hit" feedback | LOW | 1-frame color palette swap during `draw` |
| Hit sound layering (primary thud + secondary tail) | Two sounds on one event (punch + metal clink) sound massively more satisfying than one | LOW | Pyxel has 4 sound channels; fire two at slight offset |
| Juice resource flash/pulse when consuming | Reinforces the cost of fusion; players don't read the number, they notice the flash | LOW | HUD element pulses scale or brightness on change |
| Controller/keyboard rumble analog (screen edge flash) | No rumble in Pyxel; substitute = 1-frame edge-of-screen color flash | LOW | Draw colored rect on screen edge during hit event |
| "Landing reset" on any attack → fresh jump | Super Meat Boy / Celeste convention: hitting an enemy during dive resets your air state | LOW-MED | State machine hook on `drill_impact` event |

**Reference:** [Jan Willem Nijman's "Art of Screenshake"](https://theengineeringofconsciousexperience.com/jan-willem-nijman-vlambeer-the-art-of-screenshake/); [Wayline "Art of Tiny Animations"](https://www.wayline.io/blog/art-of-tiny-animations-game-feel); [Kai Clavier Super Game Feel Effects pack](https://kaiclavier.itch.io/super-game-feel-effects) documents screenshake/kickback/hitstop as the canonical trio.

#### Fusion Lifecycle Redesign

Fusion is the core differentiator of this game and the user explicitly flagged charge-to-fuse, V button mapping, and mana shield as **open for reconsideration**. These are table-stakes for ANY transformation mechanic.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Explicit initiate / sustain / end phases with distinct feel | Kirby Mouthful Mode, Metroid Morph Ball, Ori Bash — every "stance change" that feels good has a dedicated activation animation, a sustain where controls visibly change, and a dedicated exit. Current system elides the phases | MEDIUM | Each phase is its own FSM state with its own animation, input map, and exit conditions |
| Activation windup (distinct from instant switch) | Kirby's Mouthful pulls you toward the object; Bash in Ori freezes time. Both use the windup as a design beat, not a delay to hide | MEDIUM | Schema-tunable windup duration (0-20 frames); during windup input is ignored but animation + particles play |
| Sustain state with visible indicator (HUD / sprite tint / outline / particle aura) | Players need to know at a glance "I am fused right now"; ambiguity = user confusion = "feels wrong" | LOW-MED | Sprite overlay + HUD icon |
| Deliberate end: timeout / second press / resource depletion / impact | Kirby "press and hold Y to spit out"; makes exit feel intentional, not accidental | LOW | Per-ability exit condition in schema |
| Cancel out of fusion with dedicated input | Players must always have a way to bail; locked states = feel bad | LOW | Reserved cancel input (e.g., down+cancel) always ends fusion |
| Ability identity per fusion type (visual + audio + input map) | Drill Dive and Bubble Shield should feel like different creatures, not the same character with a palette swap | MEDIUM | Each ability gets: windup SFX, sustain loop, end SFX, color palette tint, particle color, distinct button map |
| Resource curve visibility (mana shield drain rate) | Player must see the drain so they feel the cost; invisible cost = "why did I die?" | LOW | HUD pulse + numeric readout during fusion |

**Reference:** [Kirby Mouthful Mode mechanics (Fandom)](https://kirby.fandom.com/wiki/Mouthful_Mode); [Anatomy of Metroid Fusion](https://www.anatomyofgames.com/2015/02/28/the-anatomy-of-metroid-fusion-1-disempowered-but-not-disenfranchised/).

---

### Differentiators (Competitive Advantage)

Features that separate "polished prototype" from "shippable feel." Not required but high-leverage.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Replay/timeline scrubber on tuning panel | Player records a 5-second jump, tunes params, replays with new values — iteration speed multiplier | HIGH | Record input sequence + initial state; replay deterministically; PROJECT.md doesn't require it but it's the difference between GMTK Toolkit and its imitators |
| Diff-two-presets side-by-side mode | Load preset A and preset B, toggle between them with a key while the game runs | MED | Trivial extension if presets already exist; dramatic for A/B testing |
| Per-ability tuning "playground room" | A dedicated test room with targets for each ability so you can tune without running the campaign | LOW | Just an LDtk room with drill-blocks, ram-blocks, bubble targets, etc. |
| Velocity + hitbox + ground-sensor visualizer overlay | Essential for diagnosing "why doesn't it feel right" — without visualizers the tuner is guessing | LOW | Debug draw mode; already in PROJECT.md's targets |
| Frame-by-frame step mode | Advance one frame at a time with a hotkey; see exactly what each frame of a transition looks like | LOW | Global pause + step-once input |
| Recording GIF of current session for devlog | Low-effort, high-visibility way to share tuning wins | MED | Pyxel has built-in capture (`pyxel.save`) — wire to hotkey |
| Slime-specific feel pass (acceleration/friction/look-ahead) | Slime companion is the other half of the dual-hero identity; if only the player feels good, half the game still feels off | MED | Schema section for slime follow: accel, max speed, catch-up threshold, stuck timeout, look-ahead distance |
| Camera smoothing / look-ahead tuning | Camera feel is 30% of platformer feel; Celeste, Hollow Knight all tune camera lead independently of player movement | MED | Existing camera is LERP; add look-ahead offset based on player velocity |
| Audio layer with pitch-shift on repeat hits | Prevents the "rattling" effect of identical sounds fired in rapid succession | LOW | Random ±5% pitch on sound triggers |
| Landing hitstop scaled by fall velocity | "Hard landing" vs "small hop" should feel different; scale hitstop 0-6 frames by fall distance | LOW | One multiplication in the land handler |

---

### Anti-Features (Do NOT Build)

Features that seem good but waste scope or actively damage the milestone. Several already flagged in PROJECT.md Out of Scope.

| Feature | Why Tempting | Why Problematic | Alternative |
|---------|--------------|-----------------|-------------|
| Full animation blending / interpolation system | Modern engines do this; feels "professional" | Pyxel is frame-based retro; blending breaks the aesthetic and adds enormous complexity. Celeste is pure frame-based and feels perfect | Discrete frame lists with 1-3 frame transitions; squash-stretch via pre-baked variants |
| Bone/skeletal animation | Cleaner rigs, reuse | Pyxel has no support; would require custom renderer; blows up the milestone | Sprite sheets + procedural scale |
| Mobile-style tuning UI with touch sliders | "Intuitive" | This is a dev tool run on desktop; mouse+keyboard sliders are strictly faster; mobile-style eats screen real estate | Compact desktop sliders |
| Inventory/loadout for fusion abilities | "RPG depth" | Already in Out of Scope (PROJECT.md). Inventory disrupts the immediate fusion loop. All abilities are mechanical, not items | Fusion abilities remain innate/context-driven |
| Skill tree for fusion upgrades | "Replayability" | Same as inventory — kills the moment-to-moment fusion loop by adding menus between player and action. Scope kill for a feel milestone | Heart/juice containers remain the only upgrade axis |
| Deep dialog/NPC system | "Character" | Already in Out of Scope. Cutscenes disrupt feel iteration | Zero dialog |
| Cinematic camera during fusion | "Cool reveal" | Takes control away from player; player presses button → loses agency → feels bad; violates responsiveness goal | Brief 1-2 frame zoom + shake instead |
| Custom shader chain (bloom, CRT, chromatic aberration) | "Modern indie look" | Pyxel doesn't support shaders cleanly; breaks retro palette constraint; distracts from feel tuning | Pyxel's native palette + dithering |
| Tutorial/help overlay for tuning panel | "Accessibility" | Dev tool for one developer; docs belong in `.planning/`, not in-game | Markdown doc in `.planning/tuning.md` |
| Multi-character tuning (tuning per save file) | "Player customization" | Not shipping to players; this is a dev iteration tool | One global `physics-schema.json` |
| Full rebinding UI for all actions | "Accessibility" | Out of scope for feel milestone; rebinding is a shipping-game concern | Hardcoded bindings, document them |
| Replacing the fusion mechanic entirely | User said "open to rethinking fundamentals" | Nuking the mechanic and starting over is not what "rethink fundamentals" means. The fusion LOOP is validated (PROJECT.md); the LIFECYCLE is what needs redesign | Preserve the drill-dive / charge-to-fuse loop; rework how it enters, sustains, and exits |
| Network replay sharing / cloud presets | "Community tuning" | This is a solo prototype | Local JSON preset files |
| Adding a second companion / party member | "More content" | Doubles slime-follow complexity; core loop is dual-hero not trio | Keep one slime |
| Per-frame tuning (exposing every magic number) | "Max flexibility" | Too many knobs = paralysis; tuning panels succeed by curation. GMTK Toolkit has ~30 params, not 500 | Curated ~30-50 params grouped by system |

---

## Feature Dependencies

```
physics-schema single source of truth
    └─requires─> constants.py migration
            └─enables─> Live-tuning panel
                    └─requires─> File hot-reload
                    └─requires─> Slider widget
                    └─enables─> Preset save/load
                    └─enables─> Replay/scrubber (differentiator)

Animation state machine (FSM)
    └─enables─> Transition frame insertion
    └─enables─> Event hook pub/sub
            └─enables─> Juice polish (particles, sound, shake)
            └─enables─> Fusion lifecycle visuals

Fusion lifecycle redesign
    └─requires─> Animation FSM (for initiate/sustain/end visuals)
    └─requires─> Input priority list (activation input conflict resolution)
    └─requires─> Schema tunables (windup/sustain/end durations)
    └─enables─> Per-ability feel pass

Input responsiveness audit
    └─requires─> Input-state visualizer (to make audit meaningful)
    └─enables─> Cancel windows on abilities
    └─enables─> Fusion activation input model

Juice polish
    └─requires─> Animation event hooks (triggers)
    └─requires─> Screen shake system
    └─requires─> Hitstop system
    └─requires─> Particle system
    └─enables─> Fusion lifecycle feedback (reuses same infra)
```

### Dependency Notes

- **Live-tuning panel requires schema-as-source-of-truth:** Tuning values in `constants.py` won't live-update the running game; inverting the dependency is a hard prerequisite. Preserving pml-to-ldtk converter contract is non-negotiable (it already reads the schema).
- **Juice polish requires animation events:** Without hook points, juice code must poll game state each frame and guess when to fire effects — slow, brittle, and wrong. Every juice feature lists an event it subscribes to.
- **Fusion lifecycle redesign requires animation FSM before it requires tuning:** You can't tune initiate/sustain/end durations until those phases exist as distinct states. The animation FSM delivery must precede the fusion design re-implementation.
- **Input visualizer must precede input audit:** The user's complaint is "feels off" — without a visualizer, every audit conclusion is a guess. Build the overlay first.
- **Cancel windows depend on the FSM:** Cancel-into-X requires named states with frame ranges; without the FSM there's nothing to cancel out of.
- **Fusion lifecycle is gated on a design doc:** PROJECT.md states "fusion design pass precedes fusion tuning" and explicitly wants a locked design doc before re-implementation. Treat this as a blocking deliverable, not just a prose section.

---

## MVP Definition

The milestone is itself a polish pass on an already-running prototype. The MVP here is "enough infrastructure to actually tune the game."

### Must Ship (v2.0 core)

- [ ] **Schema-as-source-of-truth migration** — physics-schema.json promoted, constants.py deprecated or sourced from schema. Without this, nothing else matters.
- [ ] **Live-tuning panel (minimal)** — hot-reload + grouped sliders + reset-to-default + toggle visibility. Presets can come after.
- [ ] **Animation FSM with event hooks** — replaces the 2-frame toggle; publishes `jump_start`, `land`, `direction_change`, `wall_touch`, `fuse_start`, `fuse_end`, `drill_impact`.
- [ ] **Transition frame insertion** — jump crouch, land squash, turn-around pause, drill impact flash. At least one per transition, even if ugly placeholders.
- [ ] **Input visualizer + input priority list** — so audit conclusions are falsifiable.
- [ ] **Movement/jump tuning pass** — accel, friction, gravity, jump curves, variable jump, coyote, buffer, wall jump, kick. The stuff the user actually wants to feel different.
- [ ] **Fusion lifecycle design doc** — locked before re-implementation; defines initiate/sustain/end model and chooses between current charge-to-fuse and alternatives.
- [ ] **Fusion lifecycle re-implementation** — initiate/sustain/end phases as real FSM states with schema-tunable timings.
- [ ] **Juice trio: screen shake + hitstop + dust particles** — the Nijman baseline. Hook to animation events, not polled.

### Should Ship (v2.0 polish tier)

- [ ] **Preset save/load** — 2-3 shipped presets ("current", "tight", "floaty") for A/B comparison.
- [ ] **Slime follow pass** — dual-hero means slime feel is half the identity.
- [ ] **Squash/stretch scale overlay** — pre-baked sprite variants switching on a scale_phase float.
- [ ] **Impact flash + hit sound layering** — cheap, huge perceived improvement.
- [ ] **Velocity / hitbox / ground-sensor overlay** — already in PROJECT.md target list.
- [ ] **Per-ability feel pass** — drill, ram, hold, charge shot, bubble, boost each get their own windup/sustain/end tuning.
- [ ] **Camera smoothing + look-ahead tuning.**

### Defer (v2.1+)

- [ ] **Replay/timeline scrubber** — high value but high complexity; fine to ship tuning without it.
- [ ] **Frame-by-frame step mode** — nice for bug hunts, not needed for feel iteration.
- [ ] **Side-by-side preset diff mode.**
- [ ] **GIF export hotkey.**
- [ ] **Landing hitstop scaled by fall velocity** — subtle refinement; land with base hitstop first.
- [ ] **Pitch-shifted repeat sounds** — polish layer on top of layered sounds.
- [ ] **Playground test room** — useful but the existing rooms serve.

---

## Feature Prioritization Matrix

| Feature | User Value | Impl Cost | Priority |
|---------|------------|-----------|----------|
| Schema-as-source-of-truth | HIGH | MEDIUM | P1 |
| Live-tuning panel (hot-reload + sliders) | HIGH | LOW-MED | P1 |
| Animation FSM + event hooks | HIGH | MEDIUM | P1 |
| Transition frame insertion | HIGH | LOW-MED | P1 |
| Movement/jump tuning pass | HIGH | LOW (given panel) | P1 |
| Input visualizer | HIGH (for dev) | LOW | P1 |
| Fusion lifecycle design doc | HIGH | LOW (prose) | P1 |
| Fusion lifecycle re-implementation | HIGH | MEDIUM | P1 |
| Screen shake | HIGH | LOW | P1 |
| Hitstop | HIGH | LOW | P1 |
| Dust particles | HIGH | LOW | P1 |
| Preset save/load | MED | LOW | P2 |
| Slime follow pass | HIGH | MEDIUM | P2 |
| Squash/stretch variants | HIGH | MEDIUM | P2 |
| Impact flash | HIGH | LOW | P2 |
| Velocity/hitbox overlay | MED (dev) | LOW | P2 |
| Per-ability feel pass | HIGH | MEDIUM | P2 |
| Camera smoothing/look-ahead | MED | MEDIUM | P2 |
| Cancel windows on abilities | MED | MEDIUM | P2 |
| Replay scrubber | HIGH | HIGH | P3 |
| GIF export | LOW | LOW | P3 |
| Frame-step mode | LOW | LOW | P3 |
| Preset diff mode | MED | LOW | P3 |

**P1:** Must ship, defines the milestone. Without these it's not v2.0.
**P2:** Should ship, each adds significant perceived quality.
**P3:** Defer — either low ROI or too complex for a feel milestone.

---

## Reference Game Analysis

| Feature | Celeste | Hollow Knight | Ori | GMTK Toolkit | Nuclear Throne | Jelly Roll v2.0 plan |
|---------|---------|---------------|-----|--------------|----------------|----------------------|
| Live tuning | N/A (shipped) | N/A | N/A | Yes, ~30 params grouped | N/A | Yes, ~30-50 params grouped by system |
| Squash/stretch | Aggressive, 1-2 frames | Subtle | Heavy | Sliders expose it | N/A | Pre-baked variants + scale phase |
| Coyote time | Yes | Yes | Yes | Yes | Yes | Already present, audit only |
| Jump buffer | Yes | Yes (attack only) | Yes | Yes | Yes | Already present, audit only |
| Cancel windows | Yes (dash cancels) | Yes (attack cancel into dash/jump) | Yes | N/A | Yes | New — add to ability states |
| Screen shake | Subtle | Heavy (controversial) | Moderate | Slider | Extreme | Moderate, tunable intensity in schema |
| Hitstop | Yes on boss hits | Yes on enemy hits | Yes | N/A | Yes | Yes, hook to drill/ram/hit events |
| Dust particles | 3-frame poof | Yes | Yes (heavy) | Yes (toggle) | Yes (heavy) | 3-frame Celeste-style |
| Transformation mechanic | N/A | N/A | N/A (ability toggles) | N/A | N/A | Kirby Mouthful model: windup/sustain/end |
| Input buffer size | Large | Small (tight) | Medium | Slider | Medium | Existing values, expose as slider |

**Reference takeaways:**
- **Celeste is the template for subtle juice** — 1-2 frame effects, aggressive but brief squash/stretch, frame-based not interpolated. Matches Pyxel's constraints.
- **Nijman (Nuclear Throne) is the template for maximum juice** — use as an upper bound but clamp below it; "Juice Problem" (Wayline) article warns over-juice causes fatigue and headaches, and Hollow Knight players complained about exactly that.
- **GMTK Platformer Toolkit is the template for the tuning panel UX** — curated param list, grouped by system, named presets for A/B.
- **Kirby Mouthful Mode is the closest analog to fusion lifecycle** — visible activation, explicit sustain with changed control map, deliberate exit via second press. Not Metroid Morph Ball (that's a toggle, not a full transformation).
- **Hollow Knight demonstrates the danger of no slider:** screen shake had no intensity control on release, generated years of complaints, and was eventually added in 1.5. Ship the slider from day one.

---

## Complexity & Risk Notes for Roadmap Sequencing

**Lowest-risk starting work (good Phase 1):**
- Input visualizer overlay (foundation for audit)
- Schema-as-source-of-truth migration (blocks everything else)
- Basic slider widget (blocks live tuning)

**Medium-risk mid-milestone work (good Phase 2-3):**
- Animation FSM + event hooks (architectural, touches many systems)
- Live-tuning panel full build
- Movement/jump tuning pass using the new panel
- Screen shake + hitstop + dust particles (depends on animation events)

**Highest-risk work, needs design lock before build (good Phase 4+):**
- Fusion lifecycle design doc (prose, then commit)
- Fusion lifecycle re-implementation (touches 6 abilities + charge system + V button mapping)
- Per-ability feel pass (only meaningful after fusion lifecycle redesign)

**Known Pyxel constraints that shape feasibility:**
- No native sprite scaling → squash/stretch via pre-baked variants, not transforms
- No ImGui → custom slider widget required (not hard, but real work)
- 16-color palette → impact flash done via palette swap, not color overlay
- 4 sound channels → layered hit sounds fit but burst sfx can starve music channel
- No shader pipeline → all effects via draw-order tricks and color manipulation
- File hot-reload requires mtime polling in `update()` (no native watcher)

---

## Confidence Assessment

| Area | Confidence | Reason |
|------|------------|--------|
| Live-tuning panel feature set | HIGH | GMTK Toolkit is a known reference point with published devlog; param groupings are standard |
| Animation FSM pattern | HIGH | Widely documented; same shape across Defold/Godot/Unity tutorials |
| Transition frame values | MEDIUM | Specific frame counts (1-2 for jump crouch, 3 for dust poof) are Celeste-derived but may need retuning for Pyxel's pace |
| Input responsiveness patterns | HIGH | Coyote-before-buffer, cancel windows are canonical |
| Juice polish ROI ranking | HIGH | Nijman's Screenshake talk + Swink's Game Feel book are industry consensus |
| Fusion lifecycle model (Kirby analog) | MEDIUM | Mouthful Mode is the closest analog found, but Jelly Roll's dual-hero slime-companion dynamic is genuinely novel; model is a starting point not a proven template |
| Pyxel-specific feasibility | MEDIUM | Based on PROJECT.md context and general Pyxel knowledge; specific APIs for file watching, scale, etc. should be verified during implementation |

---

## Sources

- [GMTK Platformer Toolkit](https://gmtk.itch.io/platformer-toolkit) — the reference implementation for live-tuning panels
- [GMTK Platformer Toolkit Behind The Code devlog](https://gmtk.itch.io/platformer-toolkit/devlog/395523/behind-the-code) — architecture and param list
- [Celeste Wiki — Tech](https://celeste.ink/wiki/Tech) — dash cancels, frame data
- [Celeste & Forgiveness by Maddy Thorson](https://maddythorson.medium.com/celeste-forgiveness-31e4a40399f1) — coyote time, buffer philosophy
- [Art of Tiny Animations (Wayline)](https://www.wayline.io/blog/art-of-tiny-animations-game-feel) — squash/stretch, transition frames, dust particles
- [12 animation principles for pixel art (Sprite-AI)](https://www.sprite-ai.art/guides/animation-principles) — frame-based squash/stretch guidance
- [Sprite animation frame counts (Sprite-AI)](https://www.sprite-ai.art/blog/sprite-animation-frames) — reference frame counts per animation type
- [Jan Willem Nijman — The Art of Screenshake](https://theengineeringofconsciousexperience.com/jan-willem-nijman-vlambeer-the-art-of-screenshake/) — Nuclear Throne juice breakdown
- [Game Feel (Steve Swink) review — Liz England](https://lizengland.com/blog/review-game-feel-by-steve-swink/) — responsiveness theory
- [Game Feel and Player Control lessons (Manas Dhanait)](https://medium.com/design-bootcamp/game-feel-and-player-control-lessons-from-steve-swink-beae0ea1987f) — ADSR model
- [The Juice Problem (Wayline)](https://www.wayline.io/blog/the-juice-problem-how-exaggerated-feedback-is-harming-game-design) — over-juice warning
- [Kirby Mouthful Mode (Fandom)](https://kirby.fandom.com/wiki/Mouthful_Mode) — transformation lifecycle reference
- [Mouthful Mode mechanics (WiKirby)](https://wikirby.com/wiki/Mouthful_Mode) — activation/sustain/end model
- [Anatomy of Metroid Fusion](https://www.anatomyofgames.com/2015/02/28/the-anatomy-of-metroid-fusion-1-disempowered-but-not-disenfranchised/) — stance and transformation feel
- [Defold Animation State Machine example](https://defold.com/examples/animation/animation_states/) — canonical FSM event list
- [State machines intro (Shaggy Dev)](https://shaggydev.com/2021/11/01/state-machines-intro/) — implementation pattern
- [Hollow Knight Screen Shake Service (GitHub)](https://github.com/Emik03/ScreenShakeService) — screen shake tunability lesson
- [SMW Central Tolerance Timer](https://www.smwcentral.net/?p=section&a=details&id=26945) — coyote-before-buffer priority
- [Flynn Advanced Jump Mechanics (GameMaker)](https://gamemaker.io/en/blog/flynn-advanced-jump-mechanics) — variable jump + buffer implementation
- [Dear ImGui](https://github.com/ocornut/imgui) — reference for grouped tuning panel UX (note: not usable in Pyxel, custom widget needed)
- [Super Game Feel Effects (Kai Clavier)](https://kaiclavier.itch.io/super-game-feel-effects) — screenshake/kickback/hitstop canonical trio

---
*Feature research for: Jelly Roll Proto v2.0 Game Feel milestone*
*Researched: 2026-04-11*
