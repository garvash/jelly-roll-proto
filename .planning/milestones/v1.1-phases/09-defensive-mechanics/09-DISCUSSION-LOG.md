# Phase 09: Defensive Mechanics - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-28
**Phase:** 09-defensive-mechanics
**Areas discussed:** Shield behavior, Double Jump feel, Ability unlocks & input, Hazard tile types, Shield visual feedback, Charge shot recoil, Shield tier progression, Slime Boost naming, Ram commitment, Boost commitment model

---

## ABL-07 Reform Block — Scope Removal

**User clarification:** Reform Block was a misinterpretation of the existing destructible block regeneration system. The slime-gating happens when players cannot outpace block regeneration. No new ability needed.

**Result:** ABL-07 removed from Phase 9 scope. Phase 9 covers ABL-05 and ABL-06 only.

---

## Shield Behavior

### Activation Model

| Option | Description | Selected |
|--------|-------------|----------|
| X press = toggle on/off | Player presses X to activate, presses again to deactivate | |
| X press = timed burst | Fixed duration shield, costs flat juice on activation | |
| Auto on hit (passive) | Automatically absorbs next hit using juice | |

**User's choice:** None of the above. User clarified: Bubble Shield protects from environmental hazards (underwater, lava). Auto-activates when entering hazard zone at 100% juice. Not a combat ability.

### Shield + Fusion State

| Option | Description | Selected |
|--------|-------------|----------|
| Shield = fused state | Entering hazard at 100% juice auto-fuses | ✓ |
| Shield is separate | Bubble is own state, not fused | |
| You decide | Claude picks | |

**User's choice:** Shield = fused state.

### Juice Empty Consequence

| Option | Description | Selected |
|--------|-------------|----------|
| Rapid HP drain | Lose HP quickly, must escape or die | ✓ |
| Instant death | Juice empty = dead | |
| Eject + heavy damage | Forcefully ejected, takes 1-2 HP | |

**User's choice:** Rapid HP drain.

### Drain Rates

**User's choice:** Different per hazard type. Water/heat=slow, acid=mid, lava=fast. Higher tier bubble reduces drain by fixed amount so lower tier becomes free.

---

## Double Jump / Slime Boost

### Mechanical Style

| Option | Description | Selected |
|--------|-------------|----------|
| Slime sacrifice (Yoshi) | Slime launches downward for extra height | Partial |
| Juice-powered boost | Juice consumed for air jump, slime stays | |
| Fused-only air dash | Fused jump in air, costs fusion state | Partial |

**User's choice:** Combination — charge shot recoil gives emergent small upward momentum (bomb-climb style). Fused air ability is a juice-powered jetpack/burst (renamed to "Slime Boost").

### Fusion Requirement

| Option | Description | Selected |
|--------|-------------|----------|
| Always available | Works regardless of fusion | |
| Unfused only | Consumes juice unfused | |
| Fused only | Only while fused, ends fusion | ✓ |

**User's choice:** Fused only.

### Jetpack Mechanic

| Option | Description | Selected |
|--------|-------------|----------|
| Hold jump = hover | Sustained upward thrust while holding | |
| Tap jump = burst | Single upward burst per tap, multi-tap allowed | ✓ |
| Hold = slow fall + tap = burst | Combination hover and burst | |

**User's choice:** Tap jump = burst.

### Fusion End

| Option | Description | Selected |
|--------|-------------|----------|
| Stay fused, keep boosting | Doesn't end fusion, boost until juice empty | |
| Ends fusion after use | One boost then unfuse | Initially selected |

**User's clarification:** Multi-tap with re-commit window. Each tap is committed. Can chain boosts. Stops when player stops pressing or juice empties. If juice remains, slime drops normally. If juice empties, dissipation cooldown.

### Naming

| Option | Description | Selected |
|--------|-------------|----------|
| Slime Boost | Matches "Slime Ram" naming pattern | ✓ |
| Gel Jet | Short, punchy, alliterative | |
| Bounce Burst | Springy slime identity | |

**User's choice:** Slime Boost.
**Notes:** Can't call it "air-dash" because normal dash already works once in air.

---

## Ability Unlocks & Input

### Unlock Method

| Option | Description | Selected |
|--------|-------------|----------|
| Item pickups | Dedicated pickup items in world | ✓ |
| Boss rewards | Defeat bosses for abilities | |
| Juice capacity thresholds | Auto-unlock at juice milestones | |

**User's choice:** Item pickups for now. Boss event triggering item-like behavior can be added later.

### Input Mapping

| Option | Description | Selected |
|--------|-------------|----------|
| SPACE while fused+airborne | Jump button does double duty | ✓ |
| X while fused+airborne | Dedicated X button | |
| V while fused+airborne | Dash button context-switches | |

**User's choice:** SPACE while fused+airborne.
**Notes:** User suggested Drill Dive should also move to DOWN+SPACE for axis consistency (V=horizontal, SPACE=vertical). Confirmed.

---

## Hazard Tile Types

| Option | Description | Selected |
|--------|-------------|----------|
| New tile types per hazard | TILE_WATER, TILE_ACID, TILE_LAVA | ✓ |
| Single TILE_ZONE + metadata | One zone tile with entity field | |
| You decide | Claude picks | |

**User's choice:** New tile types per hazard.

---

## Shield Visual Feedback

| Option | Description | Selected |
|--------|-------------|----------|
| Translucent circle outline | Circular outline, color shifts per tier | ✓ |
| Slime wraps player | Slime coats player sprite | |
| You decide | Claude picks | |

**User's choice:** Translucent circle outline.

---

## Charge Shot Recoil

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit small boost | Defined upward nudge, documented mechanic | |
| Physics-based emergent | Recoil proportional to shot power, player discovers naturally | ✓ |
| No recoil | Skip this entirely | |

**User's choice:** Physics-based emergent. "Hacky solution like bomb climbing that the player can absolutely abuse." Real gating uses doors.

---

## Shield Tier Progression

| Option | Description | Selected |
|--------|-------------|----------|
| Separate pickup item | SHIELD_T2 pickup, fixed drain reduction | ✓ |
| Juice capacity gates it | Auto-unlock at juice threshold | |
| Defer to Phase 11 | Only Tier 1 in Phase 9 | |

**User's choice:** Separate pickup item.

---

## Slime Boost VFX & Damage

### Slime Behavior Post-Boost

**User's choice:** Multi-tap chaining. If juice remains after boost window, slime drops. If juice exhausted, slime dissipates with reform cooldown.

### Enemy Damage

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, slime damages below | Downward slime acts as projectile | ✓ |
| No, pure mobility | No damage component | |
| You decide | Claude picks | |

**User's choice:** Yes, slime damages below.

### Tile Art

| Option | Description | Selected |
|--------|-------------|----------|
| Placeholder colored tiles | Solid color blocks as temp art | |
| Minimal pixel art | Simple but recognizable 8x8 tiles | ✓ |
| You decide | Claude picks | |

**User's choice:** Minimal pixel art.

---

## Slime Ram Commitment

| Option | Description | Selected |
|--------|-------------|----------|
| Fully committed | No cancel, goes until wall or juice empty | ✓ |
| Cancel with penalty | Release V to stop, recovery frames + unfuse | |
| Freely cancellable | Release V to stop, normal unfuse | |

**User's choice:** Fully committed.
**Notes:** Discussion prompted by comparing Ram vs Boost commitment models. Final spectrum: Ram=no cancel, Charge Shot=no cancel, Boost=committed per tap with re-commit window.

---

## Claude's Discretion

- Specific juice drain rate numbers per hazard tier
- Slime Boost juice cost per tap
- Charge shot recoil force magnitude
- Shield VFX animation details
- Re-commit window duration between Boost taps

## Deferred Ideas

- ABL-07 Reform Block — removed, not a real ability (existing block regen system)
- Juice capacity upgrades affecting shield sustainability — Phase 11 (SYS-04)
- Additional hazard biomes beyond water/acid/lava — future expansion
