# Phase 32: Fusion Manager + Protocol Refactor - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Extract fusion mechanics from monolithic `src/entities/player.py` into a new `src/fusion/` package behind a stable `FusionAbility` Protocol, orchestrated by a `FusionManager` (latched FUSED+EXIT FSM driver) and a `ChargeController` (RECALL + WINDUP second-pass + tap/hold disambiguation). Ship **one** ability module: `drill_dive`. Add a sibling `pogo` module (null-fusion shape) for the DOWN+SPACE unfused branch. Consolidate the 100% juice gate across entry paths. Remove the v1.3 mid-drill jump-cancel. Version the save format via `save_version` (integer, bumped to 2) with hard-fail rejection of mismatched saves.

**Pure refactor** — no feel changes, no new values. Every drill behavior matches v1.3 (the `_v1.3-reference.json` preset). Phase 33 does feel tuning; Phase 32 ships parity.

**Pre-phase hard gate — Phase 31.5 cut-ability code-strip must ship first.** Cut-ability code (`start_ram`/`apply_ram_physics`/`end_ram`, `start_boost`/`end_boost`, `start_dash`/`apply_dash_physics`, `update_shield`, `update_charge_shot`, all `has_dash`/`has_shield`/`has_shield_t2`/`has_boost` flags and related state) still exists in `src/entities/player.py` today; `dash` is still in `_ACTION_MAP`. Phase 32 cannot start until Phase 31.5 removes that code.

**Out of scope (other phases):**
- Feel/tuning changes to drill values, pogo values, windup duration, tap/hold threshold, accelerated-regen multiplier — Phase 33.
- Slime follow AI feel pass — Phase 34.
- Camera shake, gameplay hitstop, pooled particles, impact flash, sound channel map — Phase 35.
- Boss/enemy balance or new content — post-prototype.
- Any reintroduction of the five cut abilities (ram, hold, charge shot, bubble shield, boost) — post-prototype.
- New UI surfaces (save/load prompts, version-mismatch overlay visual design) — Phase 32 ships the rejection path mechanically; visual polish is Phase 35 or later.

</domain>

<decisions>
## Implementation Decisions

### Code-strip prerequisite (Phase 31.5)

- **D-01:** Cut-ability code-strip ships as a **dedicated Phase 31.5** inserted via `/gsd-insert-phase` between Phase 31 and Phase 32. Separate PLAN / CONTEXT / SUMMARY / commits. Phase 32 does NOT begin until Phase 31.5 merges. Matches the HARD GATE framing in `.planning/FUSION-DESIGN.md` and `.planning/ROADMAP.md` literally.
- **D-02:** Phase 31.5 scope is **full-coverage** — `src/entities/player.py`, `src/entities/slime.py`, `assets/physics-schema.json`, every preset file (`_v1.3-reference.json`, `v2.0-default.json`, `tight.json`, `floaty.json`, autosave), `src/core/input.py`, `src/core/save_manager.py`, and any cut-ability test files. Not a code-only strip.
- **D-03:** Cut tuning groups `ram`, `charge_shot`, `boost`, `bubble_shield` are **deleted entirely** from `physics-schema.json`. All presets drop those groups. The loader stops looking for them. No "zero out + mark deprecated" half-state. `_v1.3-reference.json` also loses the groups — the v1.3 *behavioral* baseline is captured in FUSION-DESIGN.md Drill-Dive Contract; the preset file is a tuning artifact, not a historical archive.
- **D-04:** `dash` logical action is **removed from `_ACTION_MAP`** in `src/core/input.py`. V becomes unbound. Satisfies FUSION-DESIGN acceptance-checklist grep test (`grep -n '"dash"' src/core/input.py` returns no match).
- **D-05:** Save-format cleanup (dropping `has_dash`, `has_shield`, `has_shield_t2`, `has_boost` from the player block) happens in Phase 31.5 as part of the strip — NOT deferred to Phase 32. Phase 32 only owns the `save_version` bump + rejection path.

### Component boundaries — ChargeController / FusionManager

- **D-06:** **ChargeController owns RECALL + WINDUP + tap/hold disambiguation.** Responsibilities:
  - Z-button tap/hold disambiguation (the ~8-frame threshold against `input_manager.hold_frames("spit")`).
  - RECALL state: slime recall initiation, docked-detection (`distance ≤ RECALL_OVERLAP_DIST = 4 px`), accelerated regen application while docked+held.
  - WINDUP state: second-pass charge fill (100→200% of juice bar as a logical progress counter), imminent-fusion telegraph condition at ≥90% juice.
  - Free-cancel path on Z-release during RECALL or WINDUP (slime returns to follow, juice stays at 100% on WINDUP cancel).
  - Emits `fuse_start` at the WINDUP→FUSED latch (200% reached), then hands control to FusionManager.
- **D-07:** **FusionManager owns FUSED + EXIT** (and by extension the active-ability lifecycle). Responsibilities:
  - Track `active_ability: FusionAbility | None` (initially `drill_dive`, with `pogo` dispatched via `handle_jump_input` regardless of fused state).
  - Per-frame `tick(player, slime, dt)` that delegates to the active ability's `on_tick` when FUSED.
  - Mana-shield cost application on fused damage (`MANA_SHIELD_COST = 20.0 juice per hit`).
  - EXIT handling: juice=0 → `unfuse(dissipate=True)` → `slime.dissipate()` → 240-frame cooldown → slime reforms at full juice.
  - Emits `fuse_end` at FUSED→EXIT (juice=0 latch, before cooldown). Exit condition (a) from the drill contract (solid terrain landing) is the ability's exit path; FusionManager observes and emits `fuse_end` there as well.
- **D-08:** Handoff protocol: ChargeController sets internal `ready=True` when second-pass reaches 200%; FusionManager polls or is called via `on_charge_complete(slime)` to latch FUSED. Concrete method shape is planner's call; the responsibility split is fixed.

### FusionAbility Protocol shape

- **D-09:** Explicit `typing.Protocol` (runtime-checkable optional) with lifecycle + per-frame + event hooks:
  ```python
  class FusionAbility(Protocol):
      id: str
      requires_fused: bool   # True for drill_dive, False for pogo

      def can_activate(self, player, slime) -> bool: ...
      def on_enter(self, player, slime, context: dict) -> None: ...
      def on_tick(self, player, slime, dt: float) -> TickResult: ...
      def on_exit(self, player, slime, reason: str) -> None: ...
      def on_event(self, name: str, data: dict) -> None: ...
  ```
  Exact `TickResult` shape (state transition request, dx/dy intent, exit signal) is planner discretion — this CONTEXT fixes the hook surface only.
- **D-10:** The ability owns its **per-frame physics**. `apply_diving_physics` (currently in `src/entities/player.py`) moves into `src/fusion/drill_dive.py` as part of `on_tick`. Player no longer has a `DIVING`-branch in its own state dispatch; it calls `FusionManager.tick()` and lets the active ability do the work.
- **D-11:** `on_event` is how abilities react to side-channel events (e.g., `drill_block_break`). This is consistent with Phase 26 MEMORY (`project_reanimator_anim_architecture`): events are side-channel — they inform the ability, they don't drive gameplay FSM transitions.
- **D-12:** The ability emits `drill_start` from `on_enter`, `drill_block_break` from its block-break detection in `on_tick`, `drill_end` from `on_exit`. Emission lives in the ability, not in FusionManager. Planner confirms exact call sites.

### Player ↔ FusionManager API

- **D-13:** `Player.fuse(slime)` and `Player.unfuse(slime, dissipate)` are **DELETED**. All callers migrate to `game.fusion_manager.latch_fuse(slime)` / `game.fusion_manager.force_exit(reason)` (or whatever equivalent methods the planner picks). No thin-shim compatibility layer.
- **D-14:** `player.is_fused` is **derived from FusionManager state**, not a Player-owned flag. Options for implementation (planner picks): (a) `@property` on Player that reads `self._game.fusion_manager.is_fused`, (b) FusionManager writes `player.is_fused` as a visible mirror each frame, (c) remove `player.is_fused` entirely and have consumers read `game.fusion_manager.is_fused`. (c) is cleanest but highest callsite-churn; (a) minimizes diff. Decision deferred to planner.
- **D-15:** Every fuse-entry and fuse-exit path is **audited** during the refactor. Known call sites (from code archaeology): `src/entities/player.py:419-423` (charge-to-fuse), `src/entities/player.py:91-97` (fuse method), `src/entities/player.py:99-110` (unfuse method), `src/entities/player.py:672-675` (drill juice=0 auto-unfuse), `src/entities/player.py:797-802` (drill solid-terrain landing), `src/entities/player.py:188-193` (mana shield damage path). Plus any cut-ability call sites surviving into Phase 32 are bugs — Phase 31.5 should have removed them.

### Pogo placement and dispatch

- **D-16:** `src/fusion/pogo.py` implements the FusionAbility Protocol with `requires_fused = False`. Treated as a "null-fusion" sibling of `drill_dive` — reuses Protocol infrastructure, one uniform ability shape across the package. The "fusion" in the name stretches slightly (pogo isn't fused) but keeps the DOWN+SPACE input flow cohesive and gives future movement verbs an existing pattern to slot into.
- **D-17:** **FusionManager.handle_jump_input(player, slime, input_manager)** is the single dispatcher for DOWN+SPACE airborne input. Called from `Player.handle_input` when `input_manager.btnp("jump") and input_manager.btn("down") and not self.is_grounded`. Manager checks `is_fused` → dispatches to `drill_dive.can_activate()+on_enter()` (fused) or `pogo.can_activate()+on_enter()` (unfused). One entry point; no `is_fused` branches in Player for this input.
- **D-18:** Pogo values are **hardcoded named constants in `src/fusion/pogo.py`** for Phase 32 (e.g., `POGO_BOUNCE_VELOCITY`, `POGO_COOLDOWN_FRAMES`, `POGO_CONTACT_BREAK_DAMAGE`). No `pogo` group in `physics-schema.json`; no panel sliders; no preset entries. Consistent with "Phase 32 is a pure refactor, no feel changes." Phase 33 may migrate pogo values to tuning if the feel-pass warrants live editing.
- **D-19:** Pogo contact rules per FUSION-DESIGN D-04 (Shovel Knight shovel-drop): strikes downward; bounces on contact with **enemies and breakables only**; pure solid ground = no bounce, just lands. Enemies take damage (reuse existing kick damage value or define a `POGO_DAMAGE` constant — planner picks). Breakables break (same passthrough path as drill for soft destructibles — but no juice refund, since pogo is free).
- **D-20:** Pogo is **free** — no juice cost, no cooldown in v2.0 baseline (D-05 of FUSION-DESIGN: "juice is reserved for fusion"). Cooldown constant is defined in pogo.py but defaults to 0; Phase 33 may dial it up if bouncing-repeatedly-on-the-same-enemy feels abusive.

### Save format versioning

- **D-21:** Existing `"version": 1` field is **renamed to `"save_version": 2`** in a single breaking change. v1.3 saves (with `version: 1`, missing `save_version`) fail the version check by field-absence → rejected. Matches ROADMAP Phase 32 goal wording ("save format gains a `save_version` field") literally.
- **D-22:** `save_version` value is an **integer schema version** (2, bumps to 3/4/... per future breaking schema change). Decoupled from game milestone strings. Compare: `data.get("save_version") != CURRENT_SAVE_VERSION` → reject. Simple equality; no semver parsing; no ordering semantics (old saves rejected regardless of how old).
- **D-23:** **Current version constant** is `CURRENT_SAVE_VERSION = 2` defined at module level in `src/core/save_manager.py`. Single source of truth; co-located with `save()` and `load()`. Version bump = one-line change.
- **D-24:** Mismatched / missing `save_version` → **hard fail with clear message, file preserved on disk**. `SaveManager.load()` raises a well-typed error (e.g., `SaveVersionMismatchError`) or returns a structured result (e.g., `{"error": "version_mismatch", "found": 1, "expected": 2}`). Caller (menu / game boot path) shows user-facing message: "Save file from older version of the game — not compatible with v2.0. Start a new game, or keep this save for a future update that supports migration." Save file untouched — user can back it up, wait for a future migration path, or manually delete. No silent delete. No migrate-and-strip. Matches ROADMAP goal #3 literally.
- **D-25:** The user-facing error surface (menu text, button labels, whether there's a "delete save" affordance) is **planner discretion** — the invariant is hard-fail + preserve-file + clear message. UX polish is Phase 35 or later.

### Claude's Discretion

- Exact `TickResult` shape (named tuple? dataclass? dict? tagged union of intents?) returned by `on_tick`.
- Exact method name for latch-fuse / force-exit on FusionManager (`latch_fuse` / `force_exit` / `enter_fused` / `trigger_exit` — planner's call).
- Whether `player.is_fused` stays as a property-forwarded read or migrates every callsite to `game.fusion_manager.is_fused`. Both acceptable.
- Whether pogo reuses the drill soft-destructible passthrough code path directly or duplicates a minimal version. Planner decides based on what feels more legible.
- Exact constant names for pogo (`POGO_BOUNCE_VELOCITY` vs `POGO_IMPULSE` vs `POGO_DY_ON_BOUNCE`, etc.).
- Whether the save-version rejection returns a structured result dict vs. raising a typed exception. Either pattern fits the codebase.
- Phase 32's testing approach — design doc (D-28) says smoke test is sufficient; pytest optional. Planner may author a FusionManager FSM-transition test suite, a characterization test that freezes the v1.3 drill contract as a refactor safety net, or stay pure-smoke. No directive from this CONTEXT.
- Whether ChargeController-complete signaling uses a callback (`on_charge_complete`) vs. a polled `ready` flag vs. FusionManager directly observing ChargeController's state enum. Planner picks.
- Phase 32's handling of accelerated regen: FUSION-DESIGN draft is 2× passive (1.0 juice/frame while Z held + slime docked + not dissipated). Phase 32 implements the conditional branch with the drafted value; Phase 33 tunes. Implementation layer (ChargeController calls slime.refill(accelerated_rate) vs Slime exposes an `accelerated_regen` mode flag) is planner discretion.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Locked Design Contract — read first

- `.planning/FUSION-DESIGN.md` — **LOCKED @`locked_commit: 9047b590cc648184f8c6c17c0ed3830296edc72c`**. The parity target. Phase 32's planner MUST verify this SHA exists in git history before writing PLAN.md. Read in full: § Input Model, § Fusion FSM, § Juice Economy, § Drill-Dive Contract, § Cut Abilities, § Acceptance Checklist, § Lock Protocol.

### Requirements & Roadmap

- `.planning/ROADMAP.md` §Phase 32 — Goal, dependencies (Phase 30 locked design doc + cut-ability code-strip hard gate), requirements (FUS-04, FUS-05, FUS-07 — defined inline in FUSION-DESIGN.md per D-32 of Phase 30).
- `.planning/ROADMAP.md` §Cut-ability code-strip callout (line 179) — formal inline spec of the Phase 31.5 scope.

### Prior Phase Context

- `.planning/phases/30-fusion-lifecycle-design-doc/30-CONTEXT.md` — Scope-pivot rationale (D-01/D-02/D-03), all design decisions informing the FSM, cut-ability list, and the "new phase needed between 30 and 32" deferred-idea that Phase 31.5 now answers.
- `.planning/phases/31-animation-content-particle-bank-separation/31-CONTEXT.md` — Event subscription map (line 144–152 of the file). Phase 31 subscribes to `fuse_start`, `land`, `jump_start`, `drill_block_break`; Phase 32's new emits must match those names exactly or Phase 31 animation breaks silently.
- `.planning/phases/26-event-bus-animation-fsm-skeleton/26-CONTEXT.md` — Reanimator-style constraint (MEMORY): events are side-channel; Phase 32's events inform Phase 31 anim content, they don't drive Phase 32's own FSM. Driver-based animation mirroring still owns correctness.

### Code — primary refactor targets

- `src/entities/player.py` — Every fuse/drill code path. Known hotspots: `fuse()` (L91-97), `unfuse()` (L99-110), `handle_input` (L324+), drill entry branch (L443-456), drill physics (`apply_diving_physics`, L661+), block-break branch (L770-786), exit conditions (L797-802 solid, L672-675 juice=0), mana shield (L184-193), mid-drill jump-cancel (L463-468 — REMOVED in Phase 32).
- `src/entities/slime.py` — `consume()`, `refill()`, `dissipate()`, passive regen (line 166 of the file), `recall()` state. Phase 32 adds the accelerated-regen conditional; post-Phase-31.5 there are no cut-ability hooks left here.
- `src/core/save_manager.py` — `CURRENT_SAVE_VERSION` constant lives here (D-23); `save()` (L20) and `load()` (L56) paths update for `save_version` (D-21) and rejection (D-24).
- `src/core/input.py` — `_ACTION_MAP` (L4-14). Post-Phase-31.5 has no `dash` entry. Phase 32 reads `btnp("jump") + btn("down") + not is_grounded` as the DOWN+SPACE dispatch condition.

### Code — consumers of fusion state (callsite audit)

- `src/anim/event_bus.py` — `fuse_start` / `fuse_end` subscribers (Phase 31 drives the fuse-flash particle spawner here). New events `drill_start`, `drill_block_break`, `drill_end` wire into this bus.
- `src/anim/player_anim.py` — `PlayerAnimDriver` reads `player.is_fused` indirectly via state mirror. If D-14 (c) is chosen (remove `player.is_fused` entirely), the driver gains a pointer to FusionManager.
- `src/ui/` (HUD rendering) — Juice bar reads `slime.juice`; second-pass overlay (WINDUP 100→200%) reads ChargeController state. Phase 32 implements the state read; Phase 31 / Phase 33 own visual polish.
- `src/entities/player.py` mana-shield path (L184-193) — damage handler consumes juice when fused. Reroutes through FusionManager's fused-damage handler.

### Assets & Schemas

- `assets/physics-schema.json` — Post-Phase-31.5 has groups: `player`, `slime`, `drill`, `gates`, `juice` (approximate list; Phase 31.5 confirms). Drill group holds `DRILL_SPEED`, `DRILL_DRIFT_SPEED`, `DRILL_ACTIVATION_COST`, `DRILL_IMPACT_COST`, `DRILL_BLOCK_REFUND`, `DRILL_HITSTOP_FRAMES`, `DRILL_SHAKE_DURATION`. Gates group holds `DRILL_CRACKED_V_COST`. No `pogo` group in Phase 32.
- `assets/presets/_v1.3-reference.json` — Frozen v1.3 baseline. **The parity target**. Drill-values, juice-values, dissipate-cooldown all read from here. Phase 31.5 drops the four cut groups; Phase 32 does NOT modify this file.

### Post-prototype / out-of-scope references (do NOT implement)

- Accelerated-regen rate tuning (draft is 2× passive; Phase 33 owns the final value).
- Drill-dive feel tuning (spin timing, impact juice, drift speed) — Phase 33.
- Pogo feel tuning (bounce velocity, cooldown, damage) — Phase 33.
- Tap/hold threshold retune to ~8 frames — Phase 33 (FUSION-DESIGN draft; current v1.3 `SPIT_HOLD_THRESHOLD = 16`).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`src/anim/event_bus.py`** — Existing `event_bus.emit()` + subscriber model. Phase 32 reuses as-is; new events `drill_start`, `drill_block_break`, `drill_end` are new string keys on the same bus.
- **`src/core/input.py` `hold_frames(action)` and `was_tap(action, threshold)` primitives** — ChargeController's tap/hold disambiguation uses these, not raw frame counting.
- **`src/entities/slime.py` `consume()` / `refill()` / `dissipate()` / `recall()`** — Phase 32 wraps these in the new Manager/Controller surface but does not rewrite slime state. Accelerated regen is a new call to `slime.refill(accelerated_rate)` under ChargeController's condition — or a new `slime.set_regen_mode("accelerated" | "passive" | "off")` method, planner's call.
- **`src/core/save_manager.py` existing structure** — JSON file at `tuning.SAVE_FILE` path, single-slot, `save()` / `load()` / `exists()` / `delete()`. Phase 32 extends schema + adds rejection; doesn't rewrite the persistence model.
- **`src/core/tuning.py` `load()` + `load_anim()` pattern** — Phase 32's save version check is a save-time concern, not a tuning-load concern. No `load_fusion` equivalent needed; drill values already live in physics-schema.json's `drill` group.

### Established Patterns
- **Use-site tuning reads (Phase 25)** — Drill values are read at use-site as `tuning.DRILL_SPEED`, `tuning.DRILL_ACTIVATION_COST`, etc. Phase 32 preserves this. The refactor moves *where the reads happen* (into `drill_dive.py`) but not *how they happen*.
- **No magic numbers (MEMORY feedback)** — Every new constant in Phase 32 (pogo values, `CURRENT_SAVE_VERSION`, any Controller/Manager threshold) needs a named constant. Co-located in its owning module (pogo.py, save_manager.py, charge_controller.py).
- **Event bus is side-channel (Phase 26 D-00b, MEMORY)** — Phase 32's new events mirror gameplay; they do NOT drive gameplay. The FusionManager FSM transitions independently; event emission is a side effect.
- **event_bus subscriber wiring in `Game.__init__` (Phase 31 MEMORY `feedback_worktree_regression` / Pitfall 5)** — Phase 32's `drill_start` / `drill_block_break` / `drill_end` subscribers (Phase 31 animation content, Phase 35 juice polish) must be hoisted to `Game.__init__`, not subscribed mid-frame.

### Integration Points
- **`Game.__init__` / `main.py`** — FusionManager and ChargeController instantiated here (one per game session, similar to `AnimFSM`). Reference to both handed to Player (or accessed via `self._game.fusion_manager`).
- **Player update loop** — `Player.update()` currently branches on `self.state` for RAMMING / DASHING / BOOSTING / DIVING / CHARGING_SHOT (first four gone after Phase 31.5). Post-Phase-32: the DIVING branch is gone; Player calls `game.fusion_manager.tick(self, slime, dt)` and the active ability handles the physics.
- **`Player.handle_input`** — Z-button handling migrates to ChargeController.handle_z_input. DOWN+SPACE airborne dispatch migrates to FusionManager.handle_jump_input. Other input (LEFT/RIGHT/UP/jump-while-grounded) stays on Player.
- **Save/load UX** — Mismatched-version error surface in the menu code (wherever Load is wired). Planner identifies the exact call site during planning.

### Known Constraints
- **v1.3 parity is the acceptance bar for drill behavior.** Any drift from `_v1.3-reference.json` drill values or the FUSION-DESIGN Drill-Dive Contract behavioral invariants is a Phase 32 failure. Regression method: inspection + smoke test per the Acceptance Checklist; optional pytest at planner's discretion.
- **Mid-drill jump-cancel MUST be removed entirely.** FUSION-DESIGN is explicit: no replacement input, no Z-hold bail, no jump-press cancel. The v1.3 path at `src/entities/player.py:463-468` is gone — drill cannot be aborted mid-flight.
- **Phase 31 subscribes to events by name.** If Phase 32 renames any of `fuse_start`, `fuse_end`, `drill_start`, `drill_block_break`, `drill_end`, `jump_start`, `land`, Phase 31 animation breaks silently. Event names are a cross-phase contract.
- **No v1.3 save round-trip.** STATE.md explicit: "Saves may break in v2.0 — v1.3 round-trip NOT required." The hard-fail rejection is the *intended* path, not a bug.
- **FUSION-DESIGN SHA is a build-against invariant.** If the design doc gets re-locked (e.g., for a future correction), in-flight Phase 32 PLANs referencing the old `locked_commit` must be re-verified against the new SHA before execution resumes (per Lock Protocol § Re-lock Policy).

</code_context>

<specifics>
## Specific Ideas

- **"One input, fusion mutates the verb" is load-bearing.** DOWN+SPACE airborne has to read as a single gesture the player learns once — unfused it pogos, fused it commits to a plunge. The FusionManager dispatcher is the code-level embodiment of that user-facing promise. Keep it a single entry point; resist the temptation to spread pogo logic into player.py's input handling.
- **"Shoot to daze → drill to finish" is the test loop.** Any refactor decision that makes this loop *harder to express* (e.g., ability dispatch requires an extra round-trip through Player, or fuse-entry needs a multi-frame state negotiation) is wrong. The loop should feel as direct post-refactor as it did in v1.3.
- **The 100% gate is a consolidation, not an invention.** Charge-to-fuse already gates on 100% juice (`player.py:419-423`). Phase 32 aligns drill-entry to the same gate. Frame it as "tightening the existing rule" in commit messages, not as "new behavior."
  - **PARTIALLY REVERTED in Phase 33 (2026-04-29).** Live tuning surfaced that the drill-entry 100% gate broke the daze→drill loop required by line 190 above (mathematically: any daze cost > 0 leaves you below 100%, so daze→drill is impossible). The "consolidation" framing obscured a real behavior change — v1.3 had two different gates by design: WINDUP entry at 100% (commitment ritual) and drill activation at `juice > 0` (drill is a reusable verb whose attack potential is itself juice-priced). Phase 33 restores the v1.3 split: drill-entry reverts to `juice > 0` (`src/fusion/drill_dive.py::can_activate`); the WINDUP 100% gate at `src/fusion/charge_controller.py` is unchanged.
- **Pogo is a null-fusion.** Stretching the FusionAbility name to cover pogo is a deliberate choice — it gives pogo free access to the Protocol's event hooks, per-frame physics delegation, and lifecycle, at the cost of a slight naming awkwardness. The alternative (pogo as a non-Protocol sibling) costs a second ability shape in the same package. Pick the awkwardness; save the complexity.
- **Save-version rejection is a feature, not a UX accident.** Showing a clear "this save is from an older version, keep it for a future migration" message respects the player's data. Silent-delete-and-new-game is a user-hostile default.
- **v1.3 `_v1.3-reference.json` preset is frozen, not historical.** Phase 31.5 drops the four cut groups from it — this is correct; those groups are tuning artifacts, not archival content. The v1.3 *behavioral* spec lives in FUSION-DESIGN.md Drill-Dive Contract, which is immutable under lock. The preset file is editable where it serves current tuning needs.

</specifics>

<deferred>
## Deferred Ideas

- **Accelerated-regen rate tuning** — Phase 33 picks the final multiplier (FUSION-DESIGN draft is 2× passive = 1.0 juice/frame).
- **Tap/hold threshold retune** — FUSION-DESIGN targets ~8 frames; current v1.3 `SPIT_HOLD_THRESHOLD = 16`. Phase 33 retunes live via panel.
- **Pogo values in tuning/presets** — Phase 32 ships hardcoded constants; Phase 33 may migrate pogo to `physics-schema.json` + panel + preset slots if feel-pass playtest warrants live editing.
- **Drill i-frames** — FUSION-DESIGN Open-Q #1 resolution: NONE in v1.3 baseline. Phase 33 may add if "drill feels punishing" during playtest.
- **Manual mid-drill unfuse** — Stripped from design 2026-04-20. Not returning to Phase 32 or any later phase without a re-lock of FUSION-DESIGN.
- **Five cut abilities (ram, hold, charge shot, bubble shield, boost)** — Post-prototype (Godot/Unity transition) revisit per Phase 30 Deferred Ideas.
- **CRACKED_H gates** — Become dead gates under single-fusion prototype. Level design follow-up: omit or convert during Phase 31.5 or earlier. Not a Phase 32 concern.
- **Second-pass overlay visual polish** — Color, pulse cadence, imminent-fusion telegraph pulse style — Phase 31 (particle) + Phase 33 (feel). Phase 32 implements the state; rendering is downstream.
- **Save migration path (v1.3 → v2.0)** — Explicitly not built. v1.3 saves are rejected with a message; the player preserves their old save on disk. If a future milestone wants forward-compat, it designs the migration then.
- **Save-file UX polish** — Menu text, delete-save affordance, confirmation prompts for the rejection path — Phase 35 or later.
- **V button v2.0 rebinding** — V is dead in v2.0 after `dash` is stripped. Future post-prototype phases may reclaim it; this phase does not specify.
- **Phase 32 pytest scope** — Planner discretion (D-28 allows smoke-test-only). Characterization tests freezing v1.3 drill behavior are a reasonable safety net; not mandatory.

</deferred>

---

*Phase: 32-fusion-manager-protocol-refactor*
*Context gathered: 2026-04-23*
