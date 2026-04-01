# Phase 08: New Fusion Abilities - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver three new slime-powered abilities (Slime Ram, Directional Slime Hold, Charge Shot) built on a redesigned fusion system where charging juice to 100% triggers a fused power state. Includes retconning Drill Dive under the unified dash button, retiring the kick mechanic, and adding secondary WASD+JK input mapping.

</domain>

<decisions>
## Implementation Decisions

### Fusion System (Charge-to-Fuse)
- **D-01:** Fusion is NOT a toggle. Player must charge juice to 100% (JUICE_MAX), then hold Z to recall slime and fuse. Fusion is earned through gameplay (drill refunds, natural regen), inspired by Super Metroid charge beam.
- **D-02:** Hold Z = slime zips to player (rubber-band recall, ~4-6 frames) + charge builds visually. Auto-fuse when slime arrives and juice is at 100%.
- **D-03:** While fused, all abilities are enhanced. Each fused ability ends fusion on use — one charge, one big move.
- **D-04:** Mana shield while fused: juice absorbs ALL damage instead of HP (Protoss shields). Hits cost ~20 juice, no HP loss while fused.
- **D-05:** Juice empty while fused = slime dissipates completely (SF6 burnout). Cooldown before slime reforms at full size. Player is truly alone until reform. Highest stakes.

### Controls (Super Metroid Style — 4 Buttons)
- **D-06:** Z = tap to spit (unfused) | hold to recall slime + charge toward fusion (unfused) | release to fire charge shot (fused).
- **D-07:** V = basic dash (unfused) | Slime Ram (fused). DOWN+V = Drill Dive (unfused+fused).
- **D-08:** SPACE = jump only. Arrows = movement.
- **D-09:** Secondary input mapping: WASD mirrors arrow keys, J mirrors Z (spit/charge/fuse), K mirrors V (dash/drill), SPACE shared.
- **D-10:** Kick mechanic (V) retired entirely. Switch-flipping via spit or ram. Slime punting replaced by charge-shot slime fling.
- **D-11:** X button freed up, reserved for Phase 9 defensive abilities.

### Slime Ram (ABL-01 — Fused V)
- **D-12:** Shinespark/Crystal Dash style — high speed, invincible, directional freedom (horizontal + diagonal). Breaks CRACKED_H blocks.
- **D-13:** Juice-powered penetration: ram plows through CRACKED_H blocks as long as juice remains. Each block broken costs ~15 juice. More juice = deeper penetration. Enables juice-gated walls of varying thickness.
- **D-14:** Ram ending: juice empty during ram = stop, unfuse, slime dissipates.

### Basic Dash (Solo V)
- **D-15:** Short combat dodge (~2 tile burst in facing direction). ~8 frames of i-frames. Short cooldown (~20 frames). Can use in air (once per airborne). No damage, pure mobility. Celeste-style snappy feel.

### Charge Shot (ABL-04 — Fused Z Release)
- **D-16:** All-or-nothing: release Z while fused = always max power shot. Dumps all remaining juice. Slime IS the projectile — flings to destination.
- **D-17:** Auto-unfuse on fire. Slime lands at hit destination and resumes solo mode. This IS the tactical slime repositioning mechanic.
- **D-18:** No charge levels — every charge shot is the same big payoff. Simpler to balance.

### Directional Slime Hold (ABL-03 — Tap Movement While Unfused)
- **D-19:** Input duration threshold (~4-6 frames): quick tap LEFT/RIGHT = reposition slime, hold = normal walk. No extra button needed.
- **D-20:** On tap, slime moves to take cover in the tapped direction — finds next available tile to stand on. If player faces right and taps left, slime positions left (behind player, in front of firing line opposite direction).
- **D-21:** Slime acts as detached turret while unfused — R-Type Force pod analogy. Unfused = offensive advantage (turret positioning). Fused = defensive advantage (mana shield + enhanced abilities).

### Drill Dive Retcon
- **D-22:** Drill Dive moves from DOWN+SPACE to DOWN+V, unifying all burst movement under V button.
- **D-23:** DRILL item pickup removed. Drill Dive earned from defeating Mole Boss instead.
- **D-24:** Progression order: Start (walk/jump/spit) → Early (find dash ability, V unlocked) → Mole Boss (drill dive, DOWN+V unlocked) → Juice 100% (fuse for enhanced versions).

### Slime Recall
- **D-25:** Hold Z (unfused) = slime zips to player at high speed (~4-6 frames). Visible rubber-band arc/trail effect. Satisfying slingshot feel.
- **D-26:** Slime must reach and overlap player before fusion can trigger. No instant teleport.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Game Design
- `topics.txt` — Original ability concepts (directional hold, barrel roll, charge shot, bubble shield)
- `5x5mapdesign.txt` — World layout and biome gating (CRACKED_H placement context)

### Technical
- `src/entities/player.py` — Player state machine (IDLE/RUNNING/JUMPING/FALLING/DIVING/WALL_SLIDING), input handling, drill dive activation/cancellation logic (must be refactored)
- `src/entities/slime.py` — Slime follow AI, punt(), spit(), consume(), refill(), reform(), fused state drawing
- `src/core/constants.py` — All physics constants, DRILL_* constants (must be refactored), KICK_DURATION/SLIME_PUNT_SPEED (to be removed)
- `src/entities/projectile.py` — Projectile system (charge shot will need new projectile type)
- `src/entities/items.py` — DRILL item type (must be removed/retconned)

### Existing Contracts
- `assets/entity-schema.json` — Shared entity schema with pml-to-ldtk converter
- `.planning/phases/07-macro-map-room-persistence/07-CONTEXT.md` — Room-entry block reset, TILE_CRACKED_H definition, WorldManager

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Slime.spit()` — Projectile spawning pattern, reusable for charge shot
- `Slime.punt()` — Launch mechanics, reference for slime fling trajectory
- `Slime.reform()` — Teleport-to-player logic, basis for recall zip
- `Player.kick()` — To be removed, but AABB detection pattern reusable
- `Player.state` machine — Extend with "DASHING", "RAMMING" states
- `TILE_CRACKED_H` constant — Already defined in constants.py for ram gating

### Established Patterns
- State-based entity logic: Player.state string drives behavior in update/draw
- Constants in `src/core/constants.py` with UPPER_SNAKE_CASE naming
- Juice consume/refill as resource gating (DRILL_IMPACT_COST, DRILL_BLOCK_REFUND pattern)
- `is_fused` boolean on both Player and Slime — needs expansion for new fusion system

### Integration Points
- `Player.handle_input()` — All new ability triggers go here. Must refactor drill activation (DOWN+SPACE → DOWN+V)
- `Game` class in `main.py` — Orchestrates update/draw loop, manages entity lists
- `LevelMap.check_collision()` — Ram needs block-type-aware collision (CRACKED_H detection)
- Input system: currently uses `pyxel.btn()`/`pyxel.btnp()` directly — secondary mapping (WASD+JK) needs input abstraction layer

</code_context>

<specifics>
## Specific Ideas

- "Base ability + fusion enhancement" pattern: every ability has a solo form and a powered-up fused form. Fusion is the universal modifier.
- "R-Type Force interaction" — slime as detachable turret (unfused) vs attached power source (fused). Strategic attach/detach loop.
- "Protoss shields" — juice absorbs all damage while fused, creating meaningful defense trade-off.
- "SF6 burnout" — slime dissipation on juice empty is high-stakes punishment that makes players manage resources carefully. Slime reforms at full size after cooldown.
- "Super Metroid charge beam" — hold Z to recall + charge. No separate fuse button. One input flow from spit to charge to fusion.
- "Shinespark/Crystal Dash" — Ram should feel powerful with setup investment. Juice-powered penetration rewards full charge.
- Player feedback requested WASD+JK as secondary controls.

</specifics>

<deferred>
## Deferred Ideas

- **Phase 9 (Defensive Mechanics):** X button reserved for Bubble Shield (ABL-05), Yoshi Double Jump (ABL-06), Reform Block (ABL-07). Mana shield in Phase 8 is the base defense — Phase 9 adds specialized defensive abilities.
- **Juice capacity upgrades:** Max juice increases could gate deeper CRACKED_H walls. Fits SYS-04 (Heart Containers and Juice Capacity upgrade items) in Phase 11.

</deferred>

---

*Phase: 08-new-fusion-abilities*
*Context gathered: 2026-03-28*
