# Jelly Roll Proto

A sideview exploration platformer (Metroidvania) built in Pyxel. This project serves as a rapid prototype for a full game to be developed in Godot or Unity, focusing on the "dual-hero" fusion mechanic between a player character and a companion slime.

## Core Value

The primary goal is to prototype the **satisfying "fusion" loop**: using a companion slime to power a destructive "Drill Dive" that enables both exploration (breaking paths) and combat (finishing bosses).

## Current State

Working on **v2.0 Game Feel** milestone. Phase 30 (fusion lifecycle design doc) complete — single-fusion scope pivot locked.

- **v1.0** (2026-03-28): Vertical slice — Celeste-style platforming, slime companion, Drill Dive fusion, Giant Mole boss, kick mechanic, collectibles, enemy encounters. Core gameplay loop validated.
- **v1.1** (2026-04-01): World expansion — Macro-Map with room persistence, 6 fusion abilities (Ram, Hold, Charge Shot, Bubble Shield, Slime Boost, CRACKED_V gating), save/checkpoint system, 320x180 display with 2x sprite scale, PNG spritesheet pipeline, event-gated door system, LDtk entity/door integration (entity-schema v0.4.0), full tech debt cleanup.
- **v2.0 Phase 28** (2026-04-12): Live-tuning panel MVP — F1 overlay with 4 feel-category tabs, log2-scale sliders, 4 preset slots (autosave + v1.3/tight/floaty), JSONL crash-recovery journal, slow-mo toggle, compact top-justified layout with dithered content overlay.
- **v2.0 Phase 29** (2026-04-19): Player movement feel pass — accel/gravity/jump curves/coyote/buffer/wall-jump retuned against written feel targets via the panel.
- **v2.0 Phase 30** (2026-04-20): Fusion lifecycle design doc locked — `.planning/FUSION-DESIGN.md` (locked_commit `2bc5cfd6`) narrows v2.0 to **one fusion mechanic (Drill Dive)**. Defines IDLE→RECALL→WINDUP→FUSED→EXIT FSM with 100%-juice gate, second-pass (100→200%) commitment ritual, and **single auto exit** (juice→0→dissipate; manual exit removed post-lock 2026-04-20). Captures v1.3 drill values as Phase 32 regression target. Cut abilities (Ram, Hold, Charge Shot, Bubble Shield, Slime Boost) enumerated; code-strip phase required as hard gate before Phase 32.
- **v2.0 Phase 31** (2026-04-22): Animation content + particle bank separation — Reanimator-style driver/picker mirrors gameplay state with 6 new transition clips (jump_stationary, jump_running, jump_crouch, land_squash, turn_skid, drill_spin); `pause_for(n)` primitive freezes anim ticks for drill recoil. `assets/anim-schema.json` is JSON source-of-truth for clip data; live-tunable via panel ANIM tab + Reload button (Pitfall 6 ANIM_ preset routing). Particle FX moved to dedicated bank 2 with sprite-backed `Particle` and `BlobGrowth` (tier-2 AnimPlayer wrapping); `effects` slot at bank 1 y=96 retired. drill_block_break + fuse_start subscribers wired in `Game.__init__` (Pitfall 5). 198-combo hitbox-independence hard gate enforces no `w`/`h` mutation by anim layer.

## Vision

- **Dual-Hero Dynamic:** An independent pet slime that follows the player and fuses with them to grant special abilities.
- **Destructive Exploration:** Using the "Drill Dive" to carve paths through "soft" ground in an interconnected cavern.
- **Tactical Combat:** Managing "slime juice" to fire projectiles and timing the "Drill Dive" to exploit boss weaknesses.
- **Retro Aesthetic:** A dark, moody, and cramped cavern atmosphere using Pyxel's limited color palette.

## Project Context

- **Platform:** Pyxel (Python-based retro engine).
- **Codebase:** ~83K LOC Python (includes generated assets).
- **Future Path:** Transition to Godot or Unity for the full-scale production.

## Requirements

### Validated

- ✓ MOV-01: Classic platforming (Walk, Jump, Wall Slide) — v1.0
- ✓ MOV-02: Grounded and airborne Dash — v1.0 (later replaced by Kick)
- ✓ MOV-03: Core physics stability and kick mechanic — v1.0
- ✓ SLM-01: Companion slime with independent follow — v1.0
- ✓ SLM-02: Slime juice resource system — v1.0
- ✓ SLM-03: Slime Spit projectile combat — v1.0
- ✓ DRILL-01: Drill Dive fusion ability — v1.0
- ✓ DRILL-02: Destructive traversal — v1.0
- ✓ ENV-01: Cavern biome with hazards — v1.0
- ✓ BOSS-01: Giant Mole boss — v1.0
- ✓ PROG-01: Linear progression flow — v1.0
- ✓ HLT-01: Player health system (3 HP) — v1.0
- ✓ ENM-01: Snail and Bat enemies — v1.0
- ✓ INT-01: Kick, switches, and collectibles — v1.0
- ✓ MAP-01: 5x5 room switching and macro-map — v1.1
- ✓ MAP-02: Room layouts via pml-to-ldtk pipeline with event-gated doors — v1.1
- ✓ MAP-03: State persistence across rooms — v1.1
- ✓ MAP-04: Biome-specific tile identification — v1.1
- ✓ ABL-01: Slime Ram fusion with horizontal gating — v1.1
- ✓ ABL-02: CRACKED_V vertical gating (Drill Dive + Slime Boost) — v1.1
- ✓ ABL-03: Directional Slime Hold — v1.1
- ✓ ABL-04: Charge Slime Shot — v1.1
- ✓ ABL-05: Bubble Shield — v1.1
- ✓ ABL-06: Yoshi-style Double Jump — v1.1
- ✓ SYS-01: Save Rooms/Checkpoints with JSON persistence — v1.1
- ✓ SYS-02: Mini-map HUD bar — v1.1
- ✓ SYS-03: Pause Screen with Macro-Map view — v1.1
- ✓ SYS-04: Heart Containers and Juice Capacity upgrades — v1.1
- ✓ ANIM-04: Transition frames (jump crouch, land squash, turn skid, drill spin, fuse flash) — v2.0 Phase 31
- ✓ ANIM-05: JSON anim-schema live-editable via panel — v2.0 Phase 31
- ✓ ANIM-06: Particle image bank separate from map tileset — v2.0 Phase 31
- ✓ ANIM-07: Hitbox-independence hard gate (198-combo matrix, default pytest) — v2.0 Phase 31

### Active

(None — next milestone not yet planned. Run `/gsd:new-milestone` to define.)

### Out of Scope

- Mobile app — web-first approach
- Complex NPC Dialog — keep focus on mechanics
- Multiple Biomes — focus on Cavern first
- Inventory System — all upgrades are mechanical/physical (slime size)
- Dynamic lighting — stick to Pyxel's palette

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pyxel Engine | Fast prototyping of retro-style mechanics | ✓ Good — enabled 11-day v1.0 delivery |
| Dual-Hero Fusion | Creates unique resource-management layer to platforming | ✓ Good — core loop feels satisfying |
| Per-Block Consumption | Rewards precision and efficiency in drilling | ✓ Good — validated in v1.0 |
| Dissipating Slime | Adds high-stakes "vulnerability" state when juice is empty | ✓ Good — creates tension |
| Dash removed for Kick | Kick provides more interesting combat/puzzle interactions | ✓ Good — better gameplay variety |
| Physics-based slime follow | Replaced lerp with acceleration/friction for weight | ✓ Good — feels more natural |
| Room-entry block reset | Prevents soft-locks from permanent destruction | ✓ Good — pragmatic for prototype |
| IID-based item persistence | LDtk instance IDs for permanent item tracking | ✓ Good — clean integration |
| 24-frame ease-out LERP transitions | Smooth camera slide between rooms | ✓ Good — feels polished |
| Ground-pound verb on DOWN+SPACE (Phase 30, 2026-04-20 re-lock) | Mario-64 mental model: DOWN+SPACE in air is the universal ground-pound input; unfused = pogo bounce, fused = drill dive (D-06 "fusion upgrades a familiar verb" anchored on the most universal platformer button). Dash + kick + V-routed activation all dropped from prototype scope. | ✓ Locked in `FUSION-DESIGN.md`; matches v1.3 drill code so no Phase 32 input remap needed |
| Charge-to-fuse system | Hold fuse button to initiate fusion abilities | ✓ Good — unifies ability activation |
| Mana shield pattern | Fused damage drains juice instead of HP | ✓ Good — rewards staying fused |
| Event-gated doors | "event" action + event_id replaces tile ID 4 boss gates | ✓ Good — flexible gating |
| ABL-07 removed (D-21) | Reform Block cut — terrain fill too niche for prototype | ✓ Good — reduced scope |
| 320x180 display | Super Metroid-style layout with 16px HUD strip | ✓ Good — better readability |
| PNG spritesheet pipeline | Aseprite → PNG replacing Pyxel image banks | ✓ Good — standard workflow |
| Entity-schema v0.4.0 | Shared JSON schema between code and pml-to-ldtk converter | ✓ Good — single source of truth |
| v2.0 single-fusion scope pivot (Phase 30) | Six v1.1 fusion abilities cut to focus prototype on Drill Dive only; combat fantasy is "shoot to daze → drill to finish" | ✓ Locked in `FUSION-DESIGN.md` (`locked_commit: 2bc5cfd6`) |
| Manual fusion exit removed (Phase 30, 2026-04-20 re-lock) | Once FUSED, only auto-dissipate (juice→0) exits — no Z-hold bail-out, no mid-drill cancel; commitment ritual is binding once entered | ✓ Re-locked at `2bc5cfd6` (prior_locked_commit `e6263693`) |

## Constraints

- Pyxel 320x180 display (320x176 game viewport + 16px HUD strip)
- 16-color palette
- Prototype scope — validate mechanics, not production-quality art
- ~83K LOC Python codebase

---
*Last updated: 2026-04-20 after Phase 30 completion (fusion lifecycle design doc + post-lock manual-exit strip)*
