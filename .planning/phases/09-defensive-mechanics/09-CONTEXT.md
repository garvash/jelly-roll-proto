# Phase 09: Defensive Mechanics - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver two new slime-powered abilities — Bubble Shield (ABL-05) and Slime Boost (ABL-06) — plus supporting infrastructure: hazard tile types, input remap for axis consistency, charge shot recoil physics, and ability unlock items. ABL-07 (Reform Block) is removed from scope — already covered by the existing block regeneration system from Phase 7.

</domain>

<decisions>
## Implementation Decisions

### Bubble Shield (ABL-05) — Passive Hazard Protection
- **D-01:** Bubble Shield is NOT a button-press ability. It auto-activates when the player enters a hazard zone with 100% juice. Entering a hazard zone at full juice triggers auto-fuse.
- **D-02:** Shield = fused state. Player is fused while in a hazard zone with active shield. Mana shield (D-04 from Phase 8) also applies while shielded.
- **D-03:** Juice drains passively at a rate determined by hazard type:
  - Water / High-temperature zone: **slow drain**
  - Acid: **medium drain**
  - Lava: **fast drain**
- **D-04:** Juice empty in hazard zone = rapid HP drain. Player must escape or die.
- **D-05:** Tiered progression (Varia/Gravity suit model):
  - **Tier 1 (Bubble Shield):** All hazard zones drain juice at their base rate. Unlocked via item pickup.
  - **Tier 2 (Enhanced Bubble):** Drain rates reduced by a fixed amount. Slow-drain hazards become free (0 cost). Medium becomes slow, fast becomes medium. Separate SHIELD_T2 item pickup deeper in the world.
- **D-06:** Visual: translucent circle outline around player that pulses/flickers as juice drains. Color shifts per tier (blue=T1, green=T2).

### Slime Boost (ABL-06) — Fused Vertical Burst
- **D-07:** Fused-only ability. While fused and airborne, tap SPACE for an upward burst. Each tap is a committed move that costs juice.
- **D-08:** Multi-tap chaining with re-commit window. Each individual boost is committed (one burst up). Between taps, player has a decision window to chain another boost or stop. This is "one big move with multiple committed beats."
- **D-09:** Exit conditions:
  - **Stop pressing:** Remaining slime drops from player, unfuse normally. Slime resumes follow AI.
  - **Juice empties:** Slime dissipates completely. Reform cooldown (SF6 burnout, same as Phase 8 D-05).
- **D-10:** Slime damages enemies below the player on each boost. Offensive + mobility utility.
- **D-11:** Unlocked via item pickup (BOOST_PICKUP). Follows has_dash/has_drill pattern.

### Input Remap — Axis Consistency (Amends Phase 8 D-22)
- **D-12:** Drill Dive moves from DOWN+V to DOWN+SPACE. V button is now purely horizontal movement (dash/ram). SPACE is purely vertical movement (jump/boost/drill dive with DOWN).
- **D-13:** Full input mapping after Phase 9:
  - SPACE = jump (ground) | Slime Boost (fused+air) | DOWN+SPACE = Drill Dive (air)
  - V/K = dash (unfused) | Slime Ram (fused) — horizontal only
  - Z/J = spit (unfused) | hold to recall+charge (unfused) | release for Charge Shot (fused)
  - Arrows/WASD = movement

### Hazard Tile Types
- **D-14:** New tile constants: TILE_WATER, TILE_ACID, TILE_LAVA. Each is a distinct tile type in the LDtk tileset with its own drain rate.
- **D-15:** Minimal pixel art for hazard tiles (simple but recognizable 8x8 tiles). Not final art, but playable for prototype.
- **D-16:** Existing TILE_HAZARD (spikes) remains unchanged — instant contact damage, not a zone hazard.

### Charge Shot Recoil
- **D-17:** Physics-based emergent vertical momentum when firing charge shot. Not an official mechanic — bomb-climb style exploit that expert players can abuse for shortcuts. Recoil force is proportional to shot power.
- **D-18:** Real progression gating uses doors/locks, not ability checks. Charge shot recoil is a reward for creative players, not a design requirement.

### Slime Ram Commitment (Clarifies Phase 8 D-12)
- **D-19:** Slime Ram is fully committed once activated. No cancel. Ram continues until wall contact or juice empty. Shinespark energy.
- **D-20:** Fused ability commitment spectrum:
  - Ram: One committed horizontal burst, no cancel
  - Charge Shot: One committed projectile, no cancel
  - Boost: One committed vertical burst per tap, re-commit window between taps

### ABL-07 Removal
- **D-21:** Reform Block (ABL-07) removed from Phase 9 scope. The "reform block" concept was a misinterpretation — it describes the existing block regeneration + juice-gating system from Phase 7. Players gate by outpacing block regeneration with sufficient juice/speed.

### Claude's Discretion
- Specific juice drain rates per hazard tier (exact numbers)
- Slime Boost juice cost per tap
- Charge shot recoil force magnitude
- Shield circle VFX animation details (pulse frequency, flicker pattern)
- Re-commit window duration between Slime Boost taps

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Game Design
- `topics.txt` — Original ability concepts (bubble shield, double jump, reform block context)
- `5x5mapdesign.txt` — World layout, biome gating, hazard zone placement context

### Phase 8 Decisions (Amended)
- `.planning/phases/08-new-fusion-abilities/08-CONTEXT.md` — Fusion system, mana shield (D-04), dissipation (D-05), controls (D-06-D-11), Ram (D-12-D-14), Charge Shot (D-16-D-18). **D-22 amended by this phase's D-12.**

### Phase 7 Decisions
- `.planning/phases/07-macro-map-room-persistence/07-CONTEXT.md` — Room-entry block reset, state persistence, WorldManager

### Technical
- `src/entities/player.py` — Player state machine, jump logic (coyote time, jump buffer), fused ability triggers, take_damage() flow, input handling
- `src/entities/slime.py` — Juice resource model, fused state, dissipation/reform, consume/refill API
- `src/core/constants.py` — Physics constants, ability costs, tile type constants (new hazard tiles go here)
- `src/core/input.py` — Input abstraction layer (_ACTION_MAP). Drill Dive remap happens here.
- `src/level/map.py` — Tile collision system, remove_tile/restore_tile, hazard checking (needs zone hazard support)
- `src/entities/items.py` — Item pickup system (SHIELD_PICKUP, BOOST_PICKUP, SHIELD_T2 go here)
- `assets/entity-schema.json` — Shared entity schema with pml-to-ldtk converter

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Player.take_damage()` — Damage flow with mana shield check; Bubble Shield integrates here for hazard zone drain
- `Slime.consume()/refill()` — Juice resource API, reuse for all drain/cost operations
- `Slime.dissipate()/reform()` — Dissipation flow for juice-empty states, reuse for Boost juice exhaustion
- `Player.state` machine — Extend with shield/boost states if needed
- `has_dash`/`has_drill` item unlock pattern — Reuse for `has_shield`, `has_boost`, `has_shield_t2`
- `TILE_HAZARD` check pattern in LevelMap — Extend for zone-based hazard types
- Input abstraction layer — Clean extension point for remap

### Established Patterns
- State-driven entity logic: Player.state string drives update/draw behavior
- Constants in `src/core/constants.py` with UPPER_SNAKE_CASE naming
- Juice consume/refill as resource gating (DRILL_IMPACT_COST, RAM_BLOCK_COST pattern)
- `is_fused` boolean gates fused ability access
- `fuse()`/`unfuse()` atomic pair (Pitfall 3 — never set is_fused directly)

### Integration Points
- `Player.handle_input()` — Boost trigger (SPACE while fused+airborne), Drill Dive remap (DOWN+SPACE)
- `Player.update()` — Hazard zone juice drain tick, shield state management
- `LevelMap.check_hazard()` — Needs expansion for zone hazard types with drain rates
- `Game` class — Spawn new pickup items, hazard zone effects
- Input `_ACTION_MAP` — No new actions needed; SPACE and V already mapped. Drill Dive trigger logic changes in player code.

</code_context>

<specifics>
## Specific Ideas

- "Varia/Gravity suit" tiering — Tier 2 bubble knocks drain down by fixed amount so lower-tier hazards become free. Same progression feel as Metroid suit upgrades.
- "Bomb climbing" energy for charge shot recoil — hacky, exploitable, rewarding for skilled players. Not designed as a mechanic, just physics being abusable. Real gating uses doors.
- "One big move with multiple committed beats" — Slime Boost is committed per tap with re-commit windows. Different from Ram (single committed burst) but philosophically consistent.
- "Mario Kart triple mushrooms" feel for Slime Boost — each tap is a discrete boost from a set, with an expiration timer between taps. Use them or lose them.
- Endgame infinite juice upgrade makes Slime Boost into sustained flight — completionist players can breeze through the self-destruct escape sequence.
- Slime damages enemies below on boost — Yoshi ground-pound flavor adds offensive utility to a mobility move.
- Axis-consistent controls — V = horizontal (dash/ram), SPACE = vertical (jump/boost/drill). Clean mental model.

</specifics>

<deferred>
## Deferred Ideas

- **ABL-07 Reform Block:** Removed — concept was a misinterpretation of existing block regeneration + juice-gating. No new ability needed.
- **Juice capacity upgrades (SYS-04):** Max juice increases could affect shield drain sustainability. Belongs in Phase 11.
- **Additional hazard biomes:** More hazard zone types beyond water/acid/lava could come with future biome expansion.

</deferred>

---

*Phase: 09-defensive-mechanics*
*Context gathered: 2026-03-28*
