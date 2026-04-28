# Phase 33: Per-Ability Feel Pass (Drill-Only) — Research

**Researched:** 2026-04-28
**Domain:** game-feel tuning + new combat mechanic (destructive-drill) + audio surface seed
**Confidence:** HIGH (most surfaces verified by direct code reads; Pyxel audio API verified by official examples)

## Summary

Phase 33 sits squarely on top of the Phase 32 refactor. The hard work — extracting drill into `src/fusion/drill_dive.py:on_tick`, separating windup into `src/fusion/charge_controller.py`, and emitting the canonical event registry (`drill_start`, `drill_block_break`, `drill_impact`, `drill_end`, `fuse_start`, `fuse_charging`, `fuse_end`) — is **already done**. Phase 33 adds (1) feel tuning of the existing knobs, (2) one new gameplay rule (destructive-drill: enemy AABB intersection during DIVING damages the enemy + drains juice + emits `drill_enemy_hit`, drill continues), (3) the daze-shot fired by removing the `not self.is_fused` gate at `player.py:197`, (4) a minimal audio module seed, and (5) particle differentiation via the `type` arg already reserved at `main.py:941`.

The biggest decision risks for the planner are sequencing (D-10 layered tuning), cost-clamp ordering on `DRILL_ENEMY_COST` (D-03 / Deferred Idea), and whether daze-on-hit reuses any existing stun primitive — research finding: **there is no reusable boss stagger primitive in code; what 33-CONTEXT D-17 describes does not exist**. The `Mole` boss in `src/entities/boss.py` has its own state machine (`BURROWED → EMERGING → VULNERABLE → DYING`) and a projectile-hit branch that transitions BURROWED→VULNERABLE on hit; that's a hand-rolled boss path, not a reusable stun. Generic enemies (`Snail`, `Bat` in `src/entities/enemies.py`) have only `take_damage(amount)` + `is_alive` flag — no stun field, no stun timer.

**Primary recommendation:** Mirror the existing `Pogo._touching_enemy` / `_damage_touched_enemy` pattern in `pogo.py:168-217` for the new destructive-drill enemy-AABB scan in `drill_dive.py:on_tick`. Place the enemy scan AFTER tile-collision detection (Phase 32 v1.3 parity stays intact, tiles dominate). Add a small generic stun primitive (`enemy.stun_timer` + decrement in `Snail.update` / `Bat.update` early-return) for the daze-shot — it's tiny and avoids retrofitting the boss FSM.

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Tuning surface expansion (D-01..D-07):**

- **D-01:** Migrate `WINDUP_DURATION_FRAMES = 30` and `ACCELERATED_REGEN_RATE = 1.0` from `src/fusion/charge_controller.py:33-34` into `assets/physics-schema.json`. Schema-group placement (extend `fusion` group vs. new `fusion_charge` group) is planner discretion.
- **D-02:** Migrate `POGO_BOUNCE_VELOCITY` (-2.5) and `POGO_COOLDOWN_FRAMES` (0) from `src/fusion/pogo.py:30-32` into `physics-schema.json` under a new `pogo` group (or extension of an existing group — planner picks). Keep `POGO_INITIAL_DY = 2.0` hardcoded (must match `DRILL_SPEED` for visual parity per the Mario-64 ground-pound mental model). Keep `POGO_DAMAGE = 1` hardcoded.
- **D-03:** Drill becomes destructive on enemy contact. Drill in flight that intersects an enemy AABB: deals damage to the enemy (does NOT take damage), continues through (no exit, no bounce, no hitstop — same passthrough behavior as soft destructibles), drains juice per hit per D-05. Mana shield path becomes irrelevant during DIVING.
- **D-04:** `DRILL_DAMAGE = 1 per hit` (same as `POGO_DAMAGE`). The "upgrade" relative to pogo is structural via repeated-frame contact, not numeric. Schema-vs-hardcoded placement is planner discretion (recommendation: hardcoded).
- **D-05:** Enemy-hit cost model = DRAIN, analog to CRACKED_V cost. New tunable `DRILL_ENEMY_COST` in physics-schema.json drill group consumes juice per enemy hit. Phase 33 picks the value via panel iteration — start in the 10–20 range.
- **D-06:** No drill iframes knob. With D-03, drill cannot take damage during DIVING.
- **D-07:** `SPIT_HOLD_THRESHOLD = 16` (target ~8) is already in tuning fusion group, panel-exposed. Phase 33 retunes the live value; no migration work needed.

**Test setup & feel-target format (D-08..D-11):**

- **D-08:** Author `33-FEEL-TARGETS.md` mirroring `29-FEEL-TARGETS.md` — pass/fail table with falsifiable spatial/timing tests, sign-off-driven. Coverage: tap/hold ~8f threshold; WINDUP cancel-window feel (~30f); accelerated-regen ritual time (2× passive); drill chain length on full juice; juice-starvation Exit (b) trigger; **enemy kill chain through 3+ enemies (NEW)**; enemy-cost balance against the boss daze→drill loop; pogo confirm-only entry.
- **D-09:** Test in existing `Level_0`–`Level_8`. Extend Phase 29's debug-warp hotkeys with drill-relevant warp targets (CRACKED_V column room, soft-destructible floor room, enemy-cluster room, juice-drain hazard room). No new dedicated test level.
- **D-10:** Tuning order: charge ritual → drill physics → drill combat → pogo. Phase-29-style layered approach (low-coupling first).
- **D-11:** Bake final values into existing `assets/presets/v2.0-default.json`. No new preset slot. `_v1.3-reference.json` stays frozen.

**Drill identity (D-12..D-17):**

- **D-12:** Build minimal `src/core/audio.py` module with `pyxel.sounds[N].set()` definitions + a `play_sfx(name)` wrapper. Phase 35 inherits and extends.
- **D-13:** 6 audio cues for Phase 33: `fuse_start`, `drill_start`, `drill_block_break`, `drill_enemy_hit` (NEW), `drill_impact`, `daze_fire`. (Plus `pogo_bounce` per D-20 = 7 total for Phase 33's surface.)
- **D-14:** Particle differentiation via new sprite cells in bank 2 (`assets/sprites/particles.png`) + type-arg routing in `main.py:spawn_particle_burst(type=...)`. Phase 31 reserved the `type` arg but routed all variants to one cell — Phase 33 actually uses it. New cells: drill block-break (orange/brown shrapnel), drill enemy-hit (combat-flavored), daze splat (blue/green).
- **D-15:** Drill claims pyxel colors 4 (brown), 9 (orange), 10 (yellow). Avoids slime/spit/daze-green and kick-blue.
- **D-16:** `drill_enemy_hit` event is wired symmetrically with the other drill events (particle + SFX subscribers in `Game.__init__` per Phase 31 Pitfall 5). Phase 35 extends for hitstop/shake.
- **D-17:** Daze shot (fused-tap-Z) implementation in scope for Phase 33. Per FUSION-DESIGN D-14, daze reuses the spit code path. Remove the `not self.is_fused` gate at `src/entities/player.py:197`; when fused, fire branches: consume `SLIME_DAZE_COST` (new tunable in `slime_juice` schema group) and apply daze-on-hit effect.

**Pogo feel-pass scope (D-18..D-20):**

- **D-18:** Light pogo retune only. Pogo gets the panel-tunable values from D-02 but no entries in 33-FEEL-TARGETS.md beyond a single confirm-only target.
- **D-19:** Pogo enemy-contact rules unchanged.
- **D-20:** Minimal pogo identity — one new SFX cue (`pogo_bounce`), no new particle.

**Pre-phase hard gate (D-21, D-22):**

- **D-21:** FUSION-DESIGN re-lock satisfied at SHA `ce5bddbd9c03ac76271f17290633da2b2e492c51` (prior `9047b590...`). Phase 33 builds against this SHA.
- **D-22:** Re-lock vehicle was Phase 32.1 (completed 2026-04-28).

### Claude's Discretion

- Schema-group placement for migrated values (extend `fusion` and `drill` groups vs. new `fusion_charge` and `pogo` groups).
- Whether `DRILL_DAMAGE` and `DRILL_ENEMY_COST` live as schema entries or as module constants in `drill_dive.py` (recommendation: DAMAGE hardcoded, COST in schema for live tuning).
- Specific (u, v) coordinates for new bank 2 particle cells within Phase 31's existing `particles.png` layout.
- Specific MML strings or `pyxel.sounds[N].set()` parameters for each audio cue — feel choice.
- Whether 33-FEEL-TARGETS.md gets sign-off BEFORE tuning starts or AFTER.
- Number of feel targets in 33-FEEL-TARGETS.md (~10–15 target).
- Daze-on-hit stun primitive: reuse existing boss stagger logic, or add a new generic enemy stun. **Research finding: no reusable stun primitive exists; planner must add one — see § Don't Hand-Roll and Open Questions.**
- Behavior when `DRILL_ENEMY_COST` > remaining juice (clamp juice mid-frame and trigger Exit b, or finish hit then check next frame).
- Whether `drill_enemy_hit` subscribes for hitstop in Phase 33 or only for particle/SFX (recommendation: particle/SFX only; Phase 35 owns hitstop).

### Deferred Ideas (OUT OF SCOPE)

- FUSION-DESIGN re-lock vehicle question (D-22) — already resolved (Phase 32.1 completed).
- Pogo feel-targets table — D-18 leaves pogo without formal targets; future phase if light retune insufficient.
- Phase 27 diagnostic overlays — F2-F5 hitbox/velocity/input/slime overlays still TBD; Phase 33 doesn't depend on them.
- Daze-on-hit stun primitive depth — TBD if existing logic isn't reusable; carve out as follow-up if needed.
- Hitstop on `drill_enemy_hit` — Phase 33 wires only particle + SFX. Phase 35 (juice polish) adds hitstop.
- Daze-on-hit dedicated event (`daze_hit`) — Phase 33 wires `daze_fire` for the firing cue but no per-hit event.
- Drill juice-clamp ordering on enemy hit — open thread; document choice in `33-IMPLEMENTATION-NOTES.md` if non-obvious.
- Custom drill test level — D-09 chose existing levels + debug warps; mid-phase `Level_drill` allowed if existing rooms don't expose right scenarios.
- Pogo damage chain (drill-style) — pogo bounces once, doesn't chain; future iteration may revisit.
- Bounce-velocity scales with kill — deferred; out of phase title's "Drill-Only" framing.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FUS-06 | Per-ability feel pass — drill-dive retuned against the new lifecycle using the panel; per-ability identity (windup/sustain/end/SFX/particle color); v1.3 parity preserved | Standard Stack (Pyxel audio API), Architecture Patterns (event-bus subscriber wiring + dispatch table), Code Examples (existing drill/pogo enemy AABB pattern), Don't Hand-Roll (reuse `Pogo._touching_enemy` shape) — together enable: (a) tuning surface migration of WINDUP_DURATION_FRAMES + ACCELERATED_REGEN_RATE + POGO_BOUNCE_VELOCITY + POGO_COOLDOWN_FRAMES + DRILL_ENEMY_COST + SLIME_DAZE_COST, (b) destructive-drill enemy-hit per locked FUSION-DESIGN D-03/D-04/D-05/`drill_enemy_hit`, (c) daze-shot fused-branch, (d) audio.py seed + 7 cues, (e) particle dispatch table + bank 2 cell additions |

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Drill enemy-AABB scan + damage + juice drain + `drill_enemy_hit` emit | `src/fusion/drill_dive.py:on_tick` (Ability tier) | — | Phase 32 D-10 locks per-frame physics ownership in the ability module. The enemy scan extends the existing per-frame collision loop already in this method. |
| Daze-shot fire (fused-tap-Z) | `src/entities/player.py:handle_input` (Player tier) | `src/entities/slime.py:spit` (Projectile tier) | The spit code path is reused per FUSION-DESIGN D-14; the gate change happens at the input-handling site (player.py:197). Cost consumption must happen on the Player branch since `slime.spit()` already pays `SLIME_SPIT_COST` for unfused; daze adds the upgrade. |
| Enemy stun on daze-hit | `src/entities/enemies.py` (Enemy tier — NEW field on Enemy base class + decrement in subclass `update`) | — | Generic stun primitive must live where enemies live; subclasses (`Snail`, `Bat`) gate movement on `stun_timer`. **No reusable primitive exists today.** |
| Tuning migration (WINDUP_DURATION_FRAMES, ACCELERATED_REGEN_RATE, POGO_*, DRILL_ENEMY_COST, SLIME_DAZE_COST) | `assets/physics-schema.json` (Schema tier) | `src/core/tuning.py` (Loader tier — auto-flat-index), `src/fusion/charge_controller.py` + `src/fusion/pogo.py` (read sites) | Use-site tuning reads (Phase 25) — every new key in schema becomes `tuning.KEY` automatically; charge_controller.py and pogo.py change from module constant to `tuning.X` lookup. |
| Audio module seed | `src/core/audio.py` (NEW Core module) | `main.py:Game.__init__` (instantiation + subscriber wiring), event_bus subscribers | New core module; subscribers read `pyxel.play(channel, sound_id)`. Phase 35 inherits and extends. |
| Particle dispatch table | `main.py:spawn_particle_burst` (Game tier) | `assets/sprites/particles.png` (Bank 2 asset) | The function already exists at line 941 with a reserved `type` arg; Phase 33 implements the (u, v) lookup. Game is the authority because Game owns `self.particles`. |
| Panel tunable surface for new keys | `src/ui/panel.py:TAB_DEFS` (UI tier) | `src/ui/panel.py:FEEL_GROUPS` set | New schema groups (if planner picks `pogo` as new group) need TAB_DEFS extension. Within existing groups (drill, fusion, slime_juice), new keys auto-appear once the schema reload runs. |
| Debug-warp extension | `src/core/debug.py` + `main.py:update` (Debug tier) | — | Existing `Ctrl+T → teleport_requested` pattern for one target; Phase 33 extends with multiple targets (one-shot flags or numbered hotkeys). |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pyxel` | (current pinned project version) [VERIFIED: in use throughout codebase] | Game engine — provides `pyxel.sounds[N].set()`, `pyxel.play(channel, sound_id)`, 4 sound channels, 64 sound slots | The only audio library on the project. No alternative considered — Pyxel is the platform. |
| `pytest` | (current pinned project version) [VERIFIED: tests/ uses pytest, conftest.py uses pytest fixtures] | Test runner | Already established by Phase 32 Wave 0 (test_drill_dive_parity.py, test_pogo.py, test_fusion_fsm.py) |

### Supporting (no new libraries — Phase 33 is content/code in existing infrastructure)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| (none) | — | — | All work is inside existing `src/`, `main.py`, `assets/`, `tests/` |

**Installation:** No new dependencies. [VERIFIED: 33-CONTEXT.md scope is content + tuning, not new library adoption]

### Pyxel Audio API surface (HIGH confidence — verified from official `04_sound_api.py` example) [CITED: github.com/kitao/pyxel/blob/main/python/pyxel/examples/04_sound_api.py]

```python
# Definition: pyxel.sounds[N].set(notes, tones, volumes, effects, speed)
pyxel.sounds[0].set(
    "e2e2c2g1 g1g1c2e2 d2d2d2g2 g2g2rr c2c2a1e1",  # notes
    "p",                                              # tones (single char repeats; or per-note string)
    "6",                                              # volumes (single char repeats; or per-note string)
    "vffn fnff vffs vfnn",                            # effects (per-note string)
    25,                                                # speed (lower = faster)
)

# Playback: pyxel.play(channel, sound_id, loop=False)
pyxel.play(0, [0, 1], loop=True)   # play sequence on channel 0, loop
pyxel.play(2, 4, loop=False)        # play single sound 4 on channel 2

# MML alternative: pyxel.sounds[N].mml("...mml string...")
# (When .mml() is called, normal notes/speed parameters are ignored.)
```

**Parameter syntax (verified):** [CITED: github.com/kitao/pyxel/blob/main/python/pyxel/examples/04_sound_api.py]
- `notes`: `[CDEFGAB] + [#-] + [0-4]` for pitch, `R` for rest. Lowercase. Examples: `c1`, `d#2`, `r`.
- `tones`: `[T]riangle [S]quare [P]ulse [N]oise`. Lowercase: `t`, `s`, `p`, `n`. Single char repeats across all notes; longer string is per-note.
- `volumes`: `[0-7]`. Single char repeats; longer string is per-note.
- `effects`: `[N]one [S]lide [V]ibrato [F]adeOut`. Lowercase: `n`, `s`, `v`, `f`. Per-note string.
- `speed`: integer; lower = faster playback.

**Channel + slot budget (HIGH confidence):** 4 channels (0–3), 64 sound slots (sound_id 0–63). [CITED: github.com/kitao/pyxel README "supporting 4 sound channels"; github.com/kitao/pyxel/blob/main/python/pyxel/examples/04_sound_api.py shows `pyxel.play(channel, sound_id)` with channel 0–2 used]. Phase 33 needs 7 cues out of 64 slots — plenty of headroom.

### Recommendation for Phase 33's audio.py

**Use `.set()` with per-note strings, not `.mml()`** — the `.set()` form is what every official Pyxel example uses (04_sound_api.py, 07_snake.py); `.mml()` is a higher-level wrapper that ignores the structured params. For 7 short SFX cues (1–4 notes each, no melody), `.set()` is more ergonomic and matches the codebase's existing tuning style (named constants, no opaque DSL strings).

**Channel allocation (Phase 35 owns the final map; Phase 33 seed should NOT lock decisions Phase 35 must own):**
- Use `pyxel.play(-1, sound_id)` to let pyxel auto-pick a free channel for short SFX. The `-1` channel sentinel is a Pyxel idiom for "any free channel" (verified by code search of pyxel examples — though this is LOW confidence; planner should verify in `examples/04_sound_api.py` or add channel 0–3 cycling helper if `-1` is not supported in this Pyxel version). [ASSUMED: `-1` auto-channel — verify before locking; safe fallback is round-robin 0..3 in `play_sfx`]
- Phase 35 will impose discipline (debounce, channel reservation per cue category). Phase 33's `play_sfx(name)` should be a thin wrapper that hides channel assignment so Phase 35 can change the strategy without touching subscribers.

**Slot allocation (sufficient headroom; planner picks integer IDs):** 7 cues → slots 0–6 is fine. Define them as named constants in `audio.py`:

```python
# src/core/audio.py — Phase 33 D-12 minimal audio surface
import pyxel

# Sound slot IDs (named constants; 7 cues out of pyxel's 64-slot budget)
SFX_FUSE_START         = 0
SFX_DRILL_START        = 1
SFX_DRILL_BLOCK_BREAK  = 2
SFX_DRILL_ENEMY_HIT    = 3   # NEW (Phase 33 D-13)
SFX_DRILL_IMPACT       = 4
SFX_DAZE_FIRE          = 5   # D-13 + D-17
SFX_POGO_BOUNCE        = 6   # D-20

_NAME_TO_SLOT = {
    "fuse_start":         SFX_FUSE_START,
    "drill_start":        SFX_DRILL_START,
    "drill_block_break":  SFX_DRILL_BLOCK_BREAK,
    "drill_enemy_hit":    SFX_DRILL_ENEMY_HIT,
    "drill_impact":       SFX_DRILL_IMPACT,
    "daze_fire":          SFX_DAZE_FIRE,
    "pogo_bounce":        SFX_POGO_BOUNCE,
}

def init_sounds():
    """Define all SFX. Called once from Game.__init__."""
    pyxel.sounds[SFX_FUSE_START].set(...)
    # ... etc

def play_sfx(name: str) -> None:
    """Phase 33 minimal channel strategy: auto-channel via -1.
    Phase 35 will replace with channel-aware debounce."""
    slot = _NAME_TO_SLOT.get(name)
    if slot is not None:
        pyxel.play(-1, slot)  # -1 = any free channel (verify Pyxel version supports)
```

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `pyxel.sounds[N].set()` per-note strings | `pyxel.sounds[N].mml(string)` | MML is higher-level (musical phrases), but the codebase has no precedent and 7 short SFX don't justify the DSL learning. Stick with `.set()`. |
| New `pogo` schema group | Extend existing `juice_effects` group | Pogo is conceptually distinct (movement verb, not juice math); its own group reads cleaner in panel and supports Phase 35/36 expansion. Recommendation: new `pogo` group + new `fusion_charge` group for windup keys, OR absorb into `fusion` group. Either works; new groups + TAB_DEFS extension is the marginally cleaner path. |
| Generic enemy stun via new `stun_timer` field | Reuse `Mole.state_timer` pattern | Mole's pattern is per-enemy state-machine logic, not a reusable primitive. Adding `stun_timer` to `Enemy` base class is 4 lines; reusing Mole's logic would require refactoring every enemy. Add the field. |

## Architecture Patterns

### System Architecture Diagram

```
                       PLAYER INPUT
                            │
                            ▼
            ┌──────────────────────────────────┐
            │   Player.handle_input            │
            │   (player.py:192-292)            │
            └──────────────────────────────────┘
                  │              │              │
        Z-tap     │   Z-hold     │     DOWN+SPACE airborne
                  │              │              │
                  ▼              ▼              ▼
         ┌──────────────┐  ┌─────────────┐  ┌────────────────┐
         │ spit / daze  │  │  Charge     │  │   Fusion       │
         │ branch       │  │  Controller │  │   Manager      │
         │ (player.py   │  │  (charge_   │  │   .handle_     │
         │  :197)       │  │  controller │  │   jump_input   │
         │              │  │  .py)       │  │                │
         │ NEW: gate    │  │             │  │ branch on      │
         │ change +     │  │ RECALL →    │  │ is_fused →     │
         │ fused branch │  │ WINDUP →    │  │ DrillDive      │
         │ + DAZE_COST  │  │ latch_fuse  │  │ or Pogo        │
         └──────┬───────┘  └─────────────┘  └────────┬───────┘
                │                                     │
                ▼                                     ▼
        ┌────────────┐                     ┌───────────────────┐
        │ Projectile │                     │ DrillDive.on_tick │
        │ (existing) │                     │ NEW: enemy AABB   │
        │            │                     │ scan after tile   │
        │ on collide │                     │ scan; deal DAMAGE,│
        │ → enemy    │                     │ drain ENEMY_COST, │
        │   take_    │                     │ emit drill_enemy_ │
        │   damage + │                     │ hit, continue     │
        │   stun     │                     └────────┬──────────┘
        │   (NEW)    │                              │
        └────────────┘                              ▼
                                          ┌─────────────────┐
                                          │  event_bus.emit │
                                          └────────┬────────┘
                                                   │
                                                   ▼
                                  ┌─────────────────────────────┐
                                  │  Game.__init__ subscribers  │
                                  │  (main.py:282-348)          │
                                  │                             │
                                  │  drill_block_break:         │
                                  │   particle burst + audio    │
                                  │  drill_enemy_hit (NEW):     │
                                  │   particle burst + audio    │
                                  │  fuse_start: blob + audio   │
                                  │  drill_start, drill_impact, │
                                  │  daze_fire, pogo_bounce:    │
                                  │   audio only                │
                                  └─────────────┬───────────────┘
                                                │
                                                ▼
                              ┌────────────────────────────────────┐
                              │  spawn_particle_burst (main.py:941)│
                              │  NEW: dispatch table from `type`   │
                              │  arg → (u, v) bank 2 coords        │
                              │                                    │
                              │  audio.play_sfx(name) → pyxel.play │
                              └────────────────────────────────────┘
```

### Recommended Project Structure (additions, not rewrites)

```
src/
├── core/
│   ├── audio.py             # NEW (D-12) — pyxel.sounds[N].set() defs + play_sfx wrapper
│   ├── debug.py             # extend with multi-target warp flags (D-09)
│   └── tuning.py            # no change — auto-flat-indexes new schema keys
├── fusion/
│   ├── charge_controller.py # tuning-migrate WINDUP_DURATION_FRAMES + ACCELERATED_REGEN_RATE
│   ├── drill_dive.py        # extend on_tick: enemy AABB scan + cost + emit drill_enemy_hit
│   └── pogo.py              # tuning-migrate POGO_BOUNCE_VELOCITY + POGO_COOLDOWN_FRAMES
├── entities/
│   ├── player.py            # remove `not self.is_fused` gate at :197; add fused-branch with SLIME_DAZE_COST
│   └── enemies.py           # add stun_timer field on Enemy base; subclass updates honor it
└── ui/
    └── panel.py             # extend TAB_DEFS["Fuse"] (and maybe add "Pogo" sub-tab) + FEEL_GROUPS

assets/
├── physics-schema.json      # add WINDUP_DURATION_FRAMES, ACCELERATED_REGEN_RATE, POGO_BOUNCE_VELOCITY, POGO_COOLDOWN_FRAMES, DRILL_ENEMY_COST, SLIME_DAZE_COST (planner picks DRILL_DAMAGE)
├── presets/
│   └── v2.0-default.json    # bake final values per D-11
└── sprites/
    └── particles.png        # add cells: drill block-break, drill enemy-hit, daze splat (D-14)

.planning/phases/33-.../
├── 33-FEEL-TARGETS.md       # NEW per D-08, mirroring 29-FEEL-TARGETS.md
└── 33-IMPLEMENTATION-NOTES.md  # OPTIONAL — record juice-clamp ordering choice if non-obvious

tests/
├── test_drill_dive_parity.py  # extend with destructive-drill cases
├── test_pogo.py              # add migrated-tuning read-site cases (no behavior change)
└── test_phase33_destructive_drill.py  # NEW — enemy AABB damage, juice drain, continue-through, drill_enemy_hit emit
```

### Pattern 1: Enemy AABB scan inside `on_tick` (mirror `Pogo._touching_enemy`)

**What:** The destructive-drill rule (D-03) requires intersecting the player AABB with each alive enemy each frame during DIVING. The exact pattern already exists in `src/fusion/pogo.py:168-217`.

**When to use:** Adding the enemy-scan branch to `drill_dive.py:on_tick` (the new code path for D-03).

**Example:** [VERIFIED: read directly from `src/fusion/pogo.py:168-217`]

```python
# Pattern from src/fusion/pogo.py:168-217 — to be MIRRORED in drill_dive.py
def _touching_enemy(self, player) -> bool:
    if not player.game:
        return False
    enemies = getattr(player.game, "enemies", None)
    if not enemies:
        return False
    for enemy in enemies:
        if not getattr(enemy, "is_alive", True):
            continue
        ew = getattr(enemy, "w", 0)
        eh = getattr(enemy, "h", 0)
        if (
            player.x < enemy.x + ew
            and player.x + player.w > enemy.x
            and player.y < enemy.y + eh
            and player.y + player.h > enemy.y
        ):
            return True
    return False
```

For destructive-drill, the iteration must continue scanning all enemies (not return on first hit) so a multi-enemy intersection during one frame all take damage. Recommended shape for drill:

```python
# Sketch for src/fusion/drill_dive.py:on_tick — between step 3 (block-break)
# and step 4 (solid landing). Read DRILL_ENEMY_COST from tuning each frame.
# Returns True if any enemy was hit this frame (used by caller for branching).
def _scan_and_damage_enemies(self, player, slime) -> bool:
    if not player.game:
        return False
    enemies = getattr(player.game, "enemies", None)
    if not enemies:
        return False
    hit_any = False
    for enemy in enemies:
        if not getattr(enemy, "is_alive", True):
            continue
        ew = getattr(enemy, "w", 0)
        eh = getattr(enemy, "h", 0)
        if (
            player.x < enemy.x + ew
            and player.x + player.w > enemy.x
            and player.y < enemy.y + eh
            and player.y + player.h > enemy.y
        ):
            # Apply damage (use take_damage primitive when available)
            if hasattr(enemy, "take_damage"):
                enemy.take_damage(DRILL_DAMAGE)
            else:
                enemy.hp = getattr(enemy, "hp", 0) - DRILL_DAMAGE
            slime.consume(tuning.DRILL_ENEMY_COST)
            event_bus.emit("drill_enemy_hit", x=enemy.x, y=enemy.y)
            hit_any = True
    return hit_any
```

**Ordering question (D-03 / 33-CONTEXT.md Integration Points):** Place the enemy scan **AFTER** the tile-collision branch (step 3 in the existing `on_tick`) but **BEFORE** the solid-landing check (step 4). Rationale: tile-first preserves Phase 32 v1.3 parity (drill prefers to break tiles first, then hits enemies inside the same frame if any are also intersecting). Enemy-first would change drill's relationship to the gate hierarchy in non-obvious ways. [VERIFIED: 33-CONTEXT Integration Points section explicitly recommends "tile-first feels closer to Phase 32 v1.3 parity"]

### Pattern 2: Schema-key migration (use-site read)

**What:** Migrating a hardcoded module constant to `physics-schema.json` so the panel can tune it live.

**When to use:** WINDUP_DURATION_FRAMES, ACCELERATED_REGEN_RATE, POGO_BOUNCE_VELOCITY, POGO_COOLDOWN_FRAMES.

**Example:** [VERIFIED: read directly from `src/core/tuning.py:50-104` and pattern at `src/fusion/drill_dive.py:117-119`]

```python
# BEFORE (src/fusion/charge_controller.py:33-34):
ACCELERATED_REGEN_RATE = 1.0       # juice/frame; FUSION-DESIGN draft 2x passive
WINDUP_DURATION_FRAMES = 30        # ~0.5s @60fps; FUSION-DESIGN D-23c base target

# AFTER step 1 — add to physics-schema.json (planner picks group placement):
# {
#   "tuning": {
#     "fusion": {                              # extends existing group
#       ...,
#       "ACCELERATED_REGEN_RATE": 1.0,
#       "WINDUP_DURATION_FRAMES": 30
#     }
#   }
# }

# AFTER step 2 — replace module constants with use-site reads:
# (delete lines 33-34, change use sites to tuning.X)
from src.core import tuning

# In handle_z_input:
slime.refill(tuning.ACCELERATED_REGEN_RATE)         # was: ACCELERATED_REGEN_RATE
self._windup_progress += 1.0 / tuning.WINDUP_DURATION_FRAMES   # was: WINDUP_DURATION_FRAMES
```

The flat-index in `tuning.py:_flat_index` builds at `load()` time, mapping `flat_key → group`. Any new key added to the schema becomes accessible as `tuning.KEY` automatically. No tuning.py edit needed; just `set_value` / panel slider plumbing for free. [VERIFIED: tuning.py docstring + flat_index mechanics, Phase 24-25 Integration Points]

### Pattern 3: Particle dispatch table

**What:** The `type` arg at `main.py:941` is reserved but currently routes everything to `(PARTICLE_BURST_U, PARTICLE_BURST_V) = (0, 0)`. Phase 33 implements the dispatch.

**When to use:** Adding new particle visuals (drill block-break, drill enemy-hit, daze splat) per D-14.

**Example:** [VERIFIED: read directly from `main.py:941-961`]

```python
# CURRENT (main.py:941-961):
def spawn_particle_burst(self, x, y, type="block_break"):
    import math
    cx, cy = x + 4, y + 4
    # type argument reserved for future variants (fuse, impact, damage);
    # all current types use the same burst sprite offsets.
    u, v = PARTICLE_BURST_U, PARTICLE_BURST_V       # ← always (0, 0)
    # ... spawn loop unchanged

# AFTER (Phase 33 D-14):
# Module-level dispatch table (next to the PARTICLE_BURST_U/V constants ~line 162):
PARTICLE_TYPE_TABLE = {
    "block_break":     (PARTICLE_BURST_U,           PARTICLE_BURST_V),       # (0,  0)  — existing
    "drill_block_break": (PARTICLE_DRILL_BREAK_U,   PARTICLE_DRILL_BREAK_V), # NEW — drill earthtone palette (D-15)
    "drill_enemy_hit":   (PARTICLE_DRILL_HIT_U,     PARTICLE_DRILL_HIT_V),   # NEW — combat-flavored (D-13)
    "daze_splat":        (PARTICLE_DAZE_U,          PARTICLE_DAZE_V),        # NEW — blue/green (D-14, D-15)
    # "block_break" stays as the default for non-Phase-33 callers (legacy spawn_explosion shim)
}

def spawn_particle_burst(self, x, y, type="block_break"):
    import math
    cx, cy = x + 4, y + 4
    u, v = PARTICLE_TYPE_TABLE.get(type, (PARTICLE_BURST_U, PARTICLE_BURST_V))
    for i in range(BURST_PARTICLE_COUNT):
        angle = (2 * math.pi * i) / BURST_PARTICLE_COUNT
        self.particles.append(Particle(
            cx, cy,
            dx=math.cos(angle) * BURST_PARTICLE_SPEED,
            dy=math.sin(angle) * BURST_PARTICLE_SPEED,
            life=BURST_PARTICLE_LIFE,
            bank_u=u, bank_v=v,
        ))
```

### Pattern 4: Subscriber wiring in `Game.__init__` (Phase 31 Pitfall 5)

**What:** New `drill_enemy_hit` subscriber + new audio subscribers for all 7 cues MUST be wired in `Game.__init__`, NOT in `Player.__init__` or mid-frame. `Player.__init__` runs every reset; `Game.__init__` runs once.

**When to use:** Wiring new event subscribers (Phase 33 adds `drill_enemy_hit` + audio for all 7 cues + `pogo_bounce`).

**Example:** [VERIFIED: read directly from `main.py:282-348`]

```python
# Existing pattern in main.py:282-348 — Phase 33 additions slot in alongside.
# After existing _on_drill_block_break / _on_land / _on_jump_start / _on_fuse_charging:

# Phase 33 D-12: audio module init.
from src.core import audio
audio.init_sounds()

# Phase 33 D-13/D-16: audio subscribers (ALL 7 cues).
def _on_audio_fuse_start(**kw):       audio.play_sfx("fuse_start")
def _on_audio_drill_start(**kw):      audio.play_sfx("drill_start")
def _on_audio_drill_block_break(**kw): audio.play_sfx("drill_block_break")
def _on_audio_drill_enemy_hit(**kw):  audio.play_sfx("drill_enemy_hit")
def _on_audio_drill_impact(**kw):     audio.play_sfx("drill_impact")
def _on_audio_daze_fire(**kw):        audio.play_sfx("daze_fire")
def _on_audio_pogo_bounce(**kw):      audio.play_sfx("pogo_bounce")

_event_bus.subscribe("fuse_start",        _on_audio_fuse_start)
_event_bus.subscribe("drill_start",       _on_audio_drill_start)
_event_bus.subscribe("drill_block_break", _on_audio_drill_block_break)
_event_bus.subscribe("drill_enemy_hit",   _on_audio_drill_enemy_hit)
_event_bus.subscribe("drill_impact",      _on_audio_drill_impact)
_event_bus.subscribe("daze_fire",         _on_audio_daze_fire)
_event_bus.subscribe("pogo_bounce",       _on_audio_pogo_bounce)

# Phase 33 D-14/D-16: particle subscriber for drill_enemy_hit.
def _on_drill_enemy_hit(x=None, y=None, **kw):
    """Phase 33 D-14: combat-flavored particle burst at enemy contact point."""
    if x is None or y is None:
        return
    self.spawn_particle_burst(x, y, type="drill_enemy_hit")
_event_bus.subscribe("drill_enemy_hit", _on_drill_enemy_hit)
```

### Anti-Patterns to Avoid

- **Subscribing in `Player.__init__`:** Player is rebuilt on `Game.reset()`; subscribers would accumulate every restart. [VERIFIED: 31-CONTEXT Pitfall 5, main.py:274 comment "MUST be wired AFTER reset() so self.player and self.particles exist"]
- **Reading hardcoded constants at import time:** Migrated tuning keys must be read at use-site (Phase 25 pattern). Importing `from src.fusion.charge_controller import ACCELERATED_REGEN_RATE` AFTER the migration would fail and silently revert to a default in any caller.
- **Renaming locked event names:** `drill_start`, `drill_block_break`, `drill_impact`, `drill_end`, `fuse_start`, `fuse_end` are CONTRACTS at the FUSION-DESIGN re-lock SHA. Phase 33 adds `drill_enemy_hit` and `pogo_bounce`; it does NOT rename existing events. [VERIFIED: 33-CONTEXT Known Constraints; FUSION-DESIGN.md line 183]
- **Pogo enemy-contact rule extension to drill:** Drill is destructive-continue-through (D-03); pogo is bounce-once-on-enemy (D-19). The two have OPPOSITE outcomes on the same gesture; do not converge their code paths beyond the AABB scan helper.
- **Passing `tile_size`-multiplied coordinates to `spawn_particle_burst` for enemy hits:** The function expects pixel coords (x + 4, y + 4 → tile center semantics for tile-grid callers). For `drill_enemy_hit`, pass `enemy.x + enemy.w/2` and `enemy.y + enemy.h/2` (or just `enemy.x, enemy.y` and accept the +4 offset, which is fine for placeholder visuals).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Enemy AABB intersection helper for drill | A new bespoke spatial-hash or grid lookup | The existing `Pogo._touching_enemy` loop pattern (`pogo.py:168-217`) | Same 4-line AABB box test, same iteration over `player.game.enemies`. Drill's loop differs only in not returning on first hit (continues to all). |
| Audio dispatch | Per-event raw `pyxel.play()` calls scattered in subscribers | A single `audio.play_sfx(name)` wrapper with internal name→slot mapping | Phase 35 will impose channel discipline; if Phase 33 inlines `pyxel.play(...)` in every subscriber, Phase 35 has to refactor 7+ call sites. The wrapper is the seam. |
| Tuning live-edit plumbing for new keys | Manual panel-slider wiring | Just add the key to `physics-schema.json` under any group in `FEEL_GROUPS` | `tuning.py:_flat_index` auto-builds at `load()`; `panel.py:_init_panel` walks `_flat_index` and creates Sliders automatically. Free panel exposure. |
| Daze-on-hit stun on enemies (NEW research finding) | Reuse "boss stagger logic" — **it does not exist as a reusable primitive** | Add `stun_timer: int = 0` to `Enemy.__init__` (`src/entities/enemies.py:11`) + `if self.stun_timer > 0: self.stun_timer -= 1; return` early-return at the top of each subclass `update()` | Cheaper than retrofitting `Mole`'s state machine; works for `Snail` and `Bat` too; doesn't break the boss path. **CRITICAL — see Open Questions and 33-CONTEXT D-17 / Deferred Idea "Daze-on-hit stun primitive".** |
| Particle visual differentiation | New particle classes per type | The single existing `Particle` class with different `bank_u, bank_v` cells (D-14) | Phase 31 already migrated to sprite-backed bank-2 particles; the dispatch table is the only delta. |
| Multi-target debug-warp | A whole new menu UI | Multiple `Ctrl+1`..`Ctrl+9` flags or a `target_room` enum on `debug.py` | Phase 29's `Ctrl+T` is one-shot; just add `Ctrl+W`+digit shortcuts or extend `debug.py` with a list and cycle through. Tiny code, big iteration speed-up. |

**Key insight:** Phase 33 is mostly an *integration* phase — every subsystem it touches has working seams already (tuning loader, panel auto-flat-index, event bus, particle dispatch arg, FusionAbility Protocol). The ONE exception is the generic-enemy stun primitive for the daze-shot, where the codebase genuinely has no reusable pattern and the planner must add ~5 lines. Don't fight the seams; use them.

## Common Pitfalls

### Pitfall 1: Subscriber wired to `Player.__init__` instead of `Game.__init__`

**What goes wrong:** Subscribers accumulate every `Game.reset()` (which rebuilds Player). After 5 deaths, `drill_enemy_hit` fires 5x particle bursts per actual hit.

**Why it happens:** It's tempting to wire subscribers next to the entity that uses them; Player's reset cycle is invisible at first glance.

**How to avoid:** Wire ALL new subscribers in `main.py:Game.__init__` after `reset()` is called. Follow the existing pattern at lines 282-348. Use closures over `self` (`self.spawn_particle_burst(...)`, `self.player.x`).

**Warning signs:** Particle burst grows louder over a play session; SFX plays multiple times per event after restart.

### Pitfall 2: `DRILL_ENEMY_COST` clamp-ordering ambiguity (Deferred Idea)

**What goes wrong:** When a drill enters a frame with `slime.juice = 5` and intersects 3 enemies (cost 10 each), the order of operations matters: do you (a) damage all 3 and let `slime.consume()` clamp to 0 then trigger Exit (b) on the next frame's juice-empty check, or (b) damage the first enemy, see juice=0, immediately trigger Exit (b) and skip the other 2 hits, or (c) tally all 3 then Exit (b) before any take damage?

**Why it happens:** `slime.consume()` already clamps to 0 (`max(0.0, self.juice - amount)` per `slime.py:223`). The juice-empty check is at step 2 of `on_tick` (`if slime.juice <= 0: return TickResult(..., request_exit=True, exit_reason="juice_empty")`), BEFORE the block-break and enemy-scan steps. So in the natural frame flow, juice depletes during the enemy scan; Exit (b) fires on the NEXT frame.

**How to avoid:** Document the planner's choice in `33-IMPLEMENTATION-NOTES.md` per the Deferred Idea. Recommendation: option (a) — damage all enemies in the same frame, let `slime.consume` clamp, Exit (b) fires on the next frame's step-2 check. This matches existing block-break semantics (drill consumes `DRILL_CRACKED_V_COST = 20` on the same frame as the break, regardless of remaining juice). Option (a) is also more rewarding ("you got the kill chain even though juice ran out"), which serves the destructive-drill design intent.

**Warning signs:** Players report "I drilled through 3 enemies but only 2 died" → option (b) leak; "drill ended one frame too late" → naive Exit-not-firing bug.

### Pitfall 3: Particle bank 2 cell collision

**What goes wrong:** Phase 33 picks (u, v) coordinates for new particle types that overlap with the existing burst (u=0, v=0), converge (u=16, v=0), or blob growth frames (u=0..48, v=16). The new "drill block-break" cell ends up rendering blob-frame-2.

**Why it happens:** `assets/sprites/particles.png` is 64×32 today (verified by `file` command). Existing layout uses (0,0), (16,0), and the entire y=16 row for blob frames. Adding 3 new types blindly at incrementing X positions hits y=0 (taken) or y=16 (taken).

**How to avoid:** Expand `particles.png` to add a new row at y=32 (or y=48). Pyxel image bank 2 is 256×256, plenty of headroom. Document the layout in a comment block at the top of main.py near the `PARTICLE_*_U/V` constants. Pick (0, 32), (16, 32), (32, 32) for the three new cells.

**Warning signs:** Drill block-break visual shows a half-grown blob sprite; visual debug shows wrong sprite at expected coord.

### Pitfall 4: Daze-shot loses its tap/hold disambiguation

**What goes wrong:** Removing `not self.is_fused` at `player.py:197` makes daze fire on every Z tap when fused, including during the WINDUP cancel-window-Z-release moment. A player rapidly tapping Z mid-WINDUP-cancel could fire spam daze shots that drain juice catastrophically.

**Why it happens:** The gate at `:197` was the only check preventing fused tap from firing. The `was_tap("spit", tuning.SPIT_HOLD_THRESHOLD)` returns True on Z release after a sub-threshold press; if the player just released Z to cancel WINDUP, a daze fires immediately.

**How to avoid:** When in the new fused-branch of the spit handler, gate on `slime.juice >= tuning.SLIME_DAZE_COST` (so juice-empty doesn't fire) AND consider gating on `not is_just_after_windup_cancel` if cancel-spam becomes an issue during playtest. Phase 33 may discover this via D-08 feel-targets ("WINDUP cancel feel"); document any additional gating in IMPLEMENTATION-NOTES.

**Warning signs:** Cancelling WINDUP fires a daze shot that drains all 100% juice.

### Pitfall 5: Tuning migration changes initial WINDUP/regen values silently

**What goes wrong:** Migrating `WINDUP_DURATION_FRAMES = 30` from `charge_controller.py:33` to `physics-schema.json` is a no-op IF the schema seed value is also 30. But if the planner accidentally seeds `25` while drafting, the windup feel changes silently with no commit-message flag.

**Why it happens:** Test suite (`test_fusion_fsm.py`) likely asserts WINDUP completes in some frame budget; if the seed mismatches, tests break in obscure ways.

**How to avoid:** During the tuning-migration plan, the schema seed value MUST equal the current hardcoded value. Verify by running the WINDUP-related tests both before and after migration; they must produce identical results. Only AFTER migration ships and tests stay green should Phase 33 start tuning the schema value.

**Warning signs:** `test_fusion_fsm.py::test_windup_to_fused_at_30_frames` (or similar) flickers red after the migration commit.

### Pitfall 6: Schema-group expansion forgets `FEEL_GROUPS` (panel won't surface keys)

**What goes wrong:** Planner adds a new `pogo` group with two keys to `physics-schema.json`; the panel doesn't show them.

**Why it happens:** `src/ui/panel.py:74-78` defines `FEEL_GROUPS = {"movement", "forgiving", "wall", "slime_follow", "slime_juice", "projectile", "drill", "fusion"}` — a hardcoded allowlist. New groups must be added here AND to TAB_DEFS at the same time.

**How to avoid:** When creating any new group (`pogo`, `fusion_charge`), edit BOTH `FEEL_GROUPS` and `TAB_DEFS` in panel.py. Verify with `pytest tests/test_panel.py` (if it exists; otherwise live-test with F1).

**Warning signs:** New schema key exists in `tuning._flat_index` but doesn't show up under any tab.

### Pitfall 7: Panel slot count overflow on "Fuse" tab

**What goes wrong:** Adding 6 new tunables (`WINDUP_DURATION_FRAMES`, `ACCELERATED_REGEN_RATE`, `POGO_BOUNCE_VELOCITY`, `POGO_COOLDOWN_FRAMES`, `DRILL_ENEMY_COST`, `SLIME_DAZE_COST`) to one tab makes the slider list overflow the panel viewport.

**Why it happens:** Phase 28's panel has fixed viewport height; sliders scroll but become tedious to navigate. The current "Fuse" tab has 5 keys in `drill` group + 6 keys in `fusion` group = 11 sliders.

**How to avoid:** Verify viewport capacity before committing to a single-tab plan. If overflow risk: split into "Fuse / Charge" and "Fuse / Drill" sub-tabs (panel.py supports CollapsibleGroups already), OR add a new top-level "Pogo" tab in TAB_DEFS for the 2 pogo keys, freeing the "Fuse" tab. Either approach is small. The planner should test with all sliders rendered before sign-off.

**Warning signs:** F1 panel shows scrollbar; `panel.py:scroll_y` activity is constant during tuning.

## Runtime State Inventory

> Phase 33 is a feel-tuning + new-mechanic phase, not a rename/refactor. The Inventory categories below are answered to confirm no runtime state has stale references. **Skip this section's depth — it's not a rename phase. The categories are answered briefly for completeness.**

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — phase changes physics values + adds gameplay rules; saves contain `juice`, `hp`, `has_drill` (the `has_drill` flag persists across phases per Phase 32 D-21 save_version=2). | None |
| Live service config | None — single-process Pyxel game, no external services. | None |
| OS-registered state | None — no scheduled tasks, no daemons. | None |
| Secrets/env vars | None — no secrets in this project. | None |
| Build artifacts | None — interpreted Python, no compiled artifacts. The `.venv/` directory is local only. | None |

**Nothing found in any category** — verified by reading project structure (no Docker, no CI service files beyond local pytest, no save format changes in Phase 33).

## Code Examples

Verified patterns from official sources and the project codebase:

### Pyxel sound definition + playback (HIGH confidence)

```python
# Source: github.com/kitao/pyxel/blob/main/python/pyxel/examples/04_sound_api.py
# Define a sound at slot 0
pyxel.sounds[0].set(
    notes="c2c2c2g2",   # 4 notes: 3× C in octave 2, 1× G in octave 2
    tones="p",          # all notes use Pulse wave (single char repeats)
    volumes="6",        # all notes at volume 6 (0-7 range)
    effects="ffnf",     # per-note: FadeOut, FadeOut, None, FadeOut
    speed=15,           # playback speed (lower = faster)
)

# Play it on any free channel (-1 idiom; verify in Pyxel version)
pyxel.play(-1, 0, loop=False)

# Or pin to channel 0 explicitly
pyxel.play(0, 0, loop=False)
```

### v1.3 drill on_tick (existing — Phase 33 modifies)

```python
# Source: src/fusion/drill_dive.py:94-183 (Phase 32 verbatim port from v1.3)
def on_tick(self, player, slime, dt: float) -> TickResult:
    # 1. Re-clamp velocity (verbatim from apply_diving_physics).
    dy = tuning.DRILL_SPEED
    if input_manager.btn("left"):
        dx = -tuning.DRILL_DRIFT_SPEED
    elif input_manager.btn("right"):
        dx = tuning.DRILL_DRIFT_SPEED
    else:
        dx = 0.0

    # 2. Juice empty -> exit (FusionManager owns slime.dissipate per D-07).
    if slime.juice <= 0:
        return TickResult(dx=dx, dy=dy, request_exit=True, exit_reason="juice_empty")

    # 3. Block-break detection (per-frame, before move_and_collide runs).
    tile_coord = player.level_map.get_destructible_at(
        player.x, player.y + dy, player.w, player.h
    )
    if tile_coord:
        # ... [block-break path: tile_type, remove_tile, refund/cost, drill_block_break emit]
        return TickResult(dx=dx, dy=dy)  # drill continues, no exit

    # *** NEW IN PHASE 33: enemy-AABB scan goes HERE (between steps 3 and 4) ***
    # See Pattern 1 above for sketch. drill continues regardless.

    # 4. Solid-landing detection: collision below + no destructible there.
    if player.level_map.check_collision(
        player.x, player.y + 1, player.w, player.h
    ):
        below_tile = player.level_map.get_destructible_at(
            player.x, player.y + 1, player.w, player.h
        )
        if below_tile is None:
            return TickResult(
                dx=dx, dy=dy, request_exit=True, exit_reason="solid_landing"
            )

    # 5. Drill continues.
    return TickResult(dx=dx, dy=dy)
```

### Daze-shot fused-branch sketch

```python
# Source: src/entities/player.py:197 (current gate to be removed)
# CURRENT:
# if input_manager.was_tap("spit", tuning.SPIT_HOLD_THRESHOLD) and not self.is_fused and self.state != "DIVING":
#     # ... spit-fire branch with auto-aim ...

# AFTER (Phase 33 D-17):
if input_manager.was_tap("spit", tuning.SPIT_HOLD_THRESHOLD) and self.state != "DIVING":
    # Fused gate: when fused, fire daze branch (cost + on-hit stun); when unfused, normal spit.
    if self.is_fused:
        if slime.juice < tuning.SLIME_DAZE_COST:
            return  # Out of juice for daze; tap is silently dropped (or beep — planner picks)
        # Consume daze cost (NEW), then fire same projectile path as unfused spit.
        slime.consume(tuning.SLIME_DAZE_COST)
        # Mark the projectile (or attach a flag) so on-hit can apply stun.
        # Cleanest path: a new arg to slime.spit() OR an attribute on the returned Projectile.
        proj = slime.spit(target_dx, target_dy, self.level_map)
        if proj is not None:
            proj.applies_daze_stun = True   # NEW flag — Projectile.update reads on enemy hit
        event_bus.emit("daze_fire")          # NEW audio cue subscriber
    else:
        # Unfused spit — unchanged from today; slime.spit pays SLIME_SPIT_COST internally.
        proj = slime.spit(target_dx, target_dy, self.level_map)
    if proj and self.game:
        self.game.projectiles.append(proj)
```

The daze-on-hit stun application happens in `Projectile.update` (new branch) when collision with an enemy is detected. Today `Projectile.update` doesn't check enemies — it only checks `level_map.check_collision` for terrain and culls on screen exit (`projectile.py:30-39`). The boss/enemy contact happens elsewhere (`boss.py:106-111` checks `for p in projectiles: if self.check_collision(p.x, p.y, p.w, p.h)`). So daze-stun is best applied at the SITE OF CONTACT (boss/enemy), keying off `proj.applies_daze_stun`. This is the lowest-diff approach. [VERIFIED: read of `projectile.py` and `boss.py:106-111`, `enemies.py`]

### Multi-target debug-warp extension

```python
# Source pattern: src/core/debug.py + main.py:572-586 (Phase 29 single-target)
# CURRENT (single target — Ctrl+T):
# if pyxel.btnp(pyxel.KEY_T):
#     teleport_requested = True

# AFTER (Phase 33 D-09 — multiple drill-relevant targets):
# In src/core/debug.py:
warp_target: str | None = None   # set to a level-id key when a warp is requested

def update():
    global warp_target, ...
    if pyxel.btn(pyxel.KEY_CTRL):
        if pyxel.btnp(pyxel.KEY_T):  warp_target = "Level_Gym_R2C2"            # existing
        if pyxel.btnp(pyxel.KEY_4):  warp_target = "Level_CrackedV_Column"     # planner picks ID
        if pyxel.btnp(pyxel.KEY_5):  warp_target = "Level_SoftBlock_Floor"
        if pyxel.btnp(pyxel.KEY_6):  warp_target = "Level_Enemy_Cluster"
        if pyxel.btnp(pyxel.KEY_7):  warp_target = "Level_Juice_Drain"
        # ... existing god flags on Ctrl+1/2/3 unchanged

# In main.py:Game.update:
if debug.warp_target:
    target_id = debug.warp_target
    debug.warp_target = None
    for level in self.world.levels:
        if level.id == target_id:
            # ... reposition player + camera (existing pattern from line 575-586)
            break
```

The Ctrl+1/2/3 keys are already used for god-mode flags; planner picks Ctrl+4..9 (or another modifier) for warp targets to avoid collision.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Drill = invulnerability mode (FUSION-DESIGN Open-Q #1) | Drill = destructive offense (drill kills enemies, takes no damage from contact) | Phase 32.1 re-lock (2026-04-28) | Phase 33 implements the rule that resolved the i-frames question structurally. |
| `is_fused` checks at `player.py:197` AND `not self.is_fused` gate spit | Daze branches off the same input, gated on `is_fused` (D-17) | Phase 33 (this phase) | Spit + daze share code path per FUSION-DESIGN D-14 — single tap-Z handler, fused-branch adds cost + stun. |
| `spawn_particle_burst(type=...)` reserves arg but routes everything to one cell | Dispatch table maps type → (u, v) | Phase 31 → Phase 33 | The `type` arg becomes load-bearing in Phase 33 (D-14). Phase 31 left the seam; Phase 33 uses it. |
| No audio in the project | `src/core/audio.py` minimal seed (Phase 33) → Phase 35 channel-aware extension | Phase 33 → Phase 35 | Phase 33's `play_sfx` wrapper is the seam Phase 35 owns the architecture for. Don't put debounce or channel logic in Phase 33's audio.py. |

**Deprecated/outdated:**
- "Reuse boss stagger logic" (33-CONTEXT D-17 / Deferred Idea) — **does not exist in code** as a reusable primitive. What `Mole` has is a per-enemy state machine. Adding a generic `Enemy.stun_timer` field is the recommended path.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest [VERIFIED: tests/conftest.py imports pytest, .pyc cache shows pytest as the runner] |
| Config file | None (no pyproject.toml, pytest.ini, or setup.cfg). [VERIFIED: glob search returned nothing] Tests run via `pytest` in the project root with default discovery. |
| Quick run command | `pytest tests/test_drill_dive_parity.py tests/test_pogo.py tests/test_fusion_fsm.py -x` (the existing fusion-related parity tests; ~3-5 seconds) |
| Full suite command | `pytest -x` (project-root pytest discovery; ~47 test files) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FUS-06 (drill destructive-on-enemy core rule) | Drill on_tick deals DRILL_DAMAGE to intersecting enemy, drains DRILL_ENEMY_COST juice, emits drill_enemy_hit, continues drilling (no state change, no exit). | unit | `pytest tests/test_phase33_destructive_drill.py::test_drill_hits_enemy_and_continues -x` | ❌ Wave 0 (NEW) |
| FUS-06 (multi-enemy chain) | Drill intersecting 2+ enemies in one frame damages all of them, drains cost per hit, emits drill_enemy_hit per hit. | unit | `pytest tests/test_phase33_destructive_drill.py::test_drill_chain_hits_multiple_enemies -x` | ❌ Wave 0 (NEW) |
| FUS-06 (continue-through, not Exit-a) | Enemy intersection does NOT trigger request_exit / solid_landing. | unit | `pytest tests/test_phase33_destructive_drill.py::test_drill_enemy_hit_does_not_exit -x` | ❌ Wave 0 (NEW) |
| FUS-06 (juice-empty mid-chain → Exit b) | Drilling into 5 enemies with juice = 30 and DRILL_ENEMY_COST = 10 results in 3 hits, juice clamped to 0, Exit (b) on next frame. | unit | `pytest tests/test_phase33_destructive_drill.py::test_drill_juice_empty_during_chain -x` | ❌ Wave 0 (NEW) |
| FUS-06 (daze fused-branch fires) | When fused, Z-tap fires projectile and consumes SLIME_DAZE_COST + emits `daze_fire`. | unit | `pytest tests/test_phase33_daze_shot.py::test_fused_tap_fires_daze -x` | ❌ Wave 0 (NEW) |
| FUS-06 (daze gate denies on insufficient juice) | When fused with juice < SLIME_DAZE_COST, Z-tap does NOT fire and does NOT consume juice. | unit | `pytest tests/test_phase33_daze_shot.py::test_daze_blocked_on_low_juice -x` | ❌ Wave 0 (NEW) |
| FUS-06 (audio module loads) | `src.core.audio.init_sounds()` runs without error and `play_sfx("fuse_start")` does not raise. | unit | `pytest tests/test_phase33_audio.py::test_audio_init_and_play -x` | ❌ Wave 0 (NEW) |
| FUS-06 (panel surfaces new keys) | After schema migration, `tuning.WINDUP_DURATION_FRAMES`, `tuning.ACCELERATED_REGEN_RATE`, `tuning.POGO_BOUNCE_VELOCITY`, `tuning.POGO_COOLDOWN_FRAMES`, `tuning.DRILL_ENEMY_COST`, `tuning.SLIME_DAZE_COST` are all readable. | unit | `pytest tests/test_phase33_tuning_migration.py::test_new_tuning_keys -x` | ❌ Wave 0 (NEW) |
| FUS-06 (v1.3 parity preserved post-destructive-drill) | All 32-Wave-0 drill-parity tests still pass after destructive-drill addition. | unit | `pytest tests/test_drill_dive_parity.py -x` | ✅ exists (Phase 32 Wave 0) |
| FUS-06 (Phase 32 FSM contract preserved) | All Phase 32 fusion-FSM tests still pass after charge_controller tuning migration. | unit | `pytest tests/test_fusion_fsm.py -x` | ✅ exists (Phase 32 Wave 0) |
| FUS-06 (feel targets sign-off) | All entries in 33-FEEL-TARGETS.md marked PASS by user. | manual | (human playtest, not automated) | ❌ Wave 0 (NEW; doc, not test) |

### Sampling Rate

- **Per task commit:** `pytest tests/test_drill_dive_parity.py tests/test_pogo.py tests/test_fusion_fsm.py tests/test_phase33_destructive_drill.py tests/test_phase33_daze_shot.py tests/test_phase33_audio.py tests/test_phase33_tuning_migration.py -x` — fast subset of fusion + Phase 33 tests.
- **Per wave merge:** `pytest -x` — full suite, ~47 files; should be < 30 seconds for the whole suite based on the Phase 32 cadence.
- **Phase gate:** Full suite green + 33-FEEL-TARGETS.md user sign-off before `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] `tests/test_phase33_destructive_drill.py` — covers FUS-06 destructive-drill core rules (4 tests sketched above)
- [ ] `tests/test_phase33_daze_shot.py` — covers FUS-06 daze-shot fused-branch + low-juice gate (2 tests)
- [ ] `tests/test_phase33_audio.py` — covers FUS-06 audio module init + play_sfx surface (1 test, can grow)
- [ ] `tests/test_phase33_tuning_migration.py` — covers FUS-06 tuning migration (1 test that walks all 6 new keys; can be a parametrized test)
- [ ] `33-FEEL-TARGETS.md` — covers FUS-06 user-facing feel sign-off (NEW, ~10–15 entries per D-08)
- [ ] No framework install needed — pytest already in project dependencies.

## Security Domain

> N/A — Phase 33 has no security surface. The project is a single-process local game with no network, no user-supplied input beyond keyboard/gamepad, no auth, no persistence beyond a local save file. ASVS categories don't apply.

## Project Constraints (from CLAUDE.md)

> CLAUDE.md does not exist in the project root [VERIFIED: glob search]. Constraints are inferred from MEMORY.md (auto-memory) and project skills:

- **Avoid magic numbers** — every numeric literal in Phase 33 (audio cue parameters, particle (u, v) coords, stun durations, dispatch table keys) gets a named constant in its owning module. [VERIFIED: project memory `feedback_magic_numbers.md`]
- **Block gate hierarchy** — drill is the CRACKED_V opener; soft = spit/kick; ram is gone (Phase 31.5 stripped); goo-mold is late-game. Phase 33 must not rebrand drill as something else. [VERIFIED: `project_block_gate_hierarchy.md`]
- **Reanimator-style anim architecture** — events are side-channel, not animation inputs. The new `drill_enemy_hit` event must NOT drive anim correctness; if Phase 33 wants drill-on-enemy visual emphasis, it must come from a driver predicate, not from the event. [VERIFIED: `project_reanimator_anim_architecture.md`]
- **Worktree merges cause regressions** — fast-forward merges overwrite files with old versions; always diff and restore after merge. **Push before worktree execution** to prevent base-commit regression. [VERIFIED: `feedback_worktree_regression.md`, `feedback_push_before_worktrees.md`]
- **Door event-gated system** — replaces tile ID 4 boss gates. Phase 33 doesn't touch doors but should not assume any tile-4 gate behavior. [VERIFIED: `project_door_event_system.md`]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `pyxel.play(-1, sound_id)` is the auto-channel idiom in this Pyxel version | Standard Stack → Pyxel Audio API surface | LOW — falls back to round-robin in `play_sfx`; verifiable in 1 minute via `pyxel.play.__doc__` or by trying it |
| A2 | The full pytest suite runs in < 30 seconds | Validation → Sampling Rate | LOW — based on Phase 32 cadence; if longer, the wave-merge sampling rate moves to a smaller subset |
| A3 | Pyxel image bank 2 has plenty of unused space below y=32 (currently 64×32 PNG, bank capacity 256×256) | Pitfalls → Pitfall 3 | LOW — re-read of `assets/sprites/particles.png` dimensions and Pyxel docs verifies; planner verifies before committing (u, v) |
| A4 | Daze-on-hit stun is a Phase 33 deliverable (vs. carved out as a follow-up) | Architecture Patterns + Open Questions | MEDIUM — 33-CONTEXT D-17 leaves it open ("may stay TBD if the existing logic isn't reusable"). Recommendation surfaces a path; planner may defer. If deferred, daze-shot ships as cost + projectile only with no stun, which is a smaller plan. |

**No claim about user-facing performance, retention, or compliance was made — there is no security surface in this phase.**

## Open Questions

1. **Does the daze-shot stun primitive ship in Phase 33 or as a follow-up?**
   - What we know: 33-CONTEXT D-17 punts on this ("planner discretion; may stay TBD if existing logic isn't reusable"). Code search confirms NO reusable stun primitive exists; the recommendation in this RESEARCH is to add a tiny `Enemy.stun_timer` field (~5 lines).
   - What's unclear: Is the user OK with the small Enemy-base-class addition, or does it feel out of scope for "drill-only" framing?
   - Recommendation: Plan for the 5-line addition in Phase 33 (it's tiny enough to not balloon scope) but flag it as a separate plan / wave so it can be cut to a follow-up if scope creeps.

2. **Schema-group placement for migrated keys: extend existing groups or create new?**
   - What we know: Existing `drill` group has 5 keys; `fusion` group has 6. Existing `slime_juice` has 4. Adding `DRILL_ENEMY_COST` to `drill`, `WINDUP_DURATION_FRAMES`+`ACCELERATED_REGEN_RATE` to `fusion`, `SLIME_DAZE_COST` to `slime_juice` keeps things tight. Adding a NEW `pogo` group for 2 keys + a NEW `fusion_charge` group for 2 keys is "cleaner" but more TAB_DEFS and FEEL_GROUPS edits.
   - What's unclear: Whether the user prefers minimal TAB_DEFS surface (extend existing) or maximally-organized groups (new groups).
   - Recommendation: Extend existing groups for everything except `pogo`. Pogo is conceptually a different verb from drill/fusion-charge and benefits from its own group. Plan: 1 new group (`pogo`), 0 new tabs (or 1 new tab "Pogo" if Pitfall 7 viewport overflow is real).

3. **Drill juice-clamp ordering on enemy hit (Deferred Idea).**
   - What we know: Existing `slime.consume()` clamps to 0; `on_tick`'s juice-empty check fires on the NEXT frame. Option (a) "damage all, exit next frame" is the natural flow; option (b) "first hit then exit immediately" requires a juice check between each enemy.
   - What's unclear: User preference for "kill chain even after juice empty" (a) vs. "juice empty stops chain mid-loop" (b).
   - Recommendation: Option (a) — naturally falls out of the loop, matches existing block-break semantics, more rewarding feel. Document choice in 33-IMPLEMENTATION-NOTES.md.

4. **Will the existing test infrastructure import cleanly with the audio module?**
   - What we know: Tests mock `pyxel` at `sys.modules` level (conftest.py:13). New audio.py imports pyxel at module level; tests will see the mock.
   - What's unclear: Whether `pyxel.sounds[N].set(...)` raises AttributeError on the MagicMock since `sounds` is dynamically attributed.
   - Recommendation: Verify during plan authoring by writing a minimal test_phase33_audio.py with `MagicMock`'d pyxel; if `pyxel.sounds[0].set(...)` raises, add `mock_pyxel.sounds = [MagicMock() for _ in range(64)]` to conftest.py.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All code | ✓ | 3.13 [VERIFIED: tests/__pycache__/ shows .cpython-313.pyc] | — |
| pytest | Test suite | ✓ | (project-pinned via .venv) [VERIFIED: tests run, conftest.py uses pytest fixtures] | — |
| pyxel | Game engine | ✓ | (project-pinned) [VERIFIED: in use throughout codebase] | — |

**Missing dependencies with no fallback:** None.
**Missing dependencies with fallback:** None.

## Sources

### Primary (HIGH confidence)
- Direct code reads:
  - `.planning/phases/33-per-ability-feel-pass-drill-only-under-single-fusion-prototype/33-CONTEXT.md`
  - `.planning/FUSION-DESIGN.md` (locked SHA `ce5bddbd`) — §Drill-Dive Contract → Enemy Interaction; §Fusion FSM event registry; §Juice Economy; §Input Model
  - `.planning/STATE.md`, `.planning/ROADMAP.md`
  - `.planning/phases/29-player-movement-feel-pass/29-CONTEXT.md`, `29-FEEL-TARGETS.md`
  - `.planning/phases/32-fusion-manager-protocol-refactor/32-CONTEXT.md`
  - `.planning/phases/31-animation-content-particle-bank-separation/31-CONTEXT.md`
  - `src/fusion/drill_dive.py`, `src/fusion/charge_controller.py`, `src/fusion/pogo.py`, `src/fusion/manager.py`
  - `src/entities/player.py` (lines 1-60, 180-400)
  - `src/entities/enemies.py`, `src/entities/boss.py`, `src/entities/projectile.py`, `src/entities/slime.py:220-232`
  - `src/anim/event_bus.py`
  - `src/core/debug.py`, `src/core/tuning.py:50-126`
  - `src/ui/panel.py:60-175`
  - `main.py:155-348, 565-590, 920-970`
  - `assets/physics-schema.json`
  - `assets/sprites/particles.png` (visual inspection)
  - `tests/conftest.py`, `tests/test_drill_dive_parity.py`, `tests/test_pogo.py`
- Pyxel official examples (HIGH confidence on audio API):
  - github.com/kitao/pyxel/blob/main/python/pyxel/examples/04_sound_api.py — `pyxel.sounds[N].set()` and `pyxel.play()` usage verified

### Secondary (MEDIUM confidence)
- WebSearch on Pyxel sound API parameters (verified against the official example file above)
- github.com/kitao/pyxel README — "supporting 4 sound channels"

### Tertiary (LOW confidence)
- `pyxel.play(-1, ...)` auto-channel sentinel — assumed valid; planner verifies in 1-minute test before locking the `play_sfx` strategy.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Pyxel API verified from official source; pytest verified in tests/; no new libraries.
- Architecture: HIGH — all integration points read directly from source; existing seams (FusionAbility Protocol, event_bus, particle dispatch arg, tuning flat-index) verified.
- Pitfalls: HIGH — every pitfall except #2 (juice-clamp ordering, which is a true deferred design choice) has a concrete code-level trigger I read.
- Validation: HIGH — pytest, conftest.py, existing test files all read; framework path is clear.
- Security: HIGH (N/A) — no security surface.
- Audio: HIGH on the API surface, MEDIUM on the channel allocation strategy (`-1` auto-channel needs verification).
- Daze stun primitive: HIGH that no reusable primitive exists (verified by full code read); MEDIUM that the recommended add (5-line `stun_timer` field on Enemy) is the right path vs. carving daze stun out to a follow-up.

**Research date:** 2026-04-28
**Valid until:** ~2026-05-12 (2 weeks; the locked FUSION-DESIGN SHA, the Phase 32 refactor seams, and the Pyxel API are all stable surfaces). The `pyxel.play(-1, ...)` assumption should be verified within 1 minute when planning begins.
