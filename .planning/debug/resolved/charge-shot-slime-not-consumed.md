---
status: resolved
trigger: "During charge shot (ABL-04), slime just reduces in size and remains available instead of being consumed/fused during charge process per D-18"
created: 2026-03-28T00:00:00Z
updated: 2026-03-28T12:00:00Z
---

## Current Focus

hypothesis: Charge shot has no charge-up phase -- it fires instantly on Z release while fused, with no visual/mechanical fusion of slime into the shot
test: Read fire_charge_shot and the charge input flow
expecting: Missing charge-up state machine; slime shrinks from juice drain but is never visually consumed
next_action: Return structured diagnosis

## Symptoms

expected: Per D-18, slime should be consumed/fused during the charge process -- the slime IS the projectile, and charging should visually show the slime being absorbed into the player before firing
actual: Slime just shrinks (via juice-to-scale mapping) while remaining independently visible and available. There is no charge-up animation or fusion state -- the shot fires instantly on Z release
errors: No runtime errors; behavioral bug
reproduction: Fuse with slime, then release Z -- charge shot fires immediately with no charge-up phase
started: Since charge shot implementation

## Eliminated

(none needed -- root cause found on first investigation)

## Evidence

- timestamp: 2026-03-28
  checked: player.py handle_input lines 285-287
  found: Charge shot triggers on btnr("spit") while fused -- immediate fire on button release, no charge-up duration
  implication: There is no charging state machine at all

- timestamp: 2026-03-28
  checked: player.py fire_charge_shot lines 515-537
  found: Method dumps all juice via slime.consume(slime.juice), fires ChargeProjectile, then unfuses. All in one frame.
  implication: The "charge" in "charge shot" is a misnomer -- it is an instant dump, not a timed charge-up

- timestamp: 2026-03-28
  checked: slime.py scale property lines 311-314
  found: scale = JUICE_MIN_SCALE + (1 - JUICE_MIN_SCALE) * (juice / max_juice). Visual size is always proportional to current juice.
  implication: When juice is consumed by ANY ability, slime visually shrinks. This is the "shrinking" the user sees -- it is the passive regen cycle showing the slime at partial juice, not a deliberate charge-up visual.

- timestamp: 2026-03-28
  checked: slime.py draw lines 316-338 and update lines 150-174 (fused branch)
  found: When fused, slime draws drill sprite and snaps to player+4y. When NOT fused, slime draws at scale. There is no "being consumed" visual state.
  implication: No intermediate state between "fused companion" and "fired projectile"

- timestamp: 2026-03-28
  checked: constants.py lines 124-137
  found: CHARGE_SHOT constants exist (speed, size, damage, recoil) but no CHARGE_DURATION, CHARGE_JUICE_RATE, or similar timing constants
  implication: Confirms no charge-up mechanic was implemented

## Resolution

root_cause: The charge shot (ABL-04) has no charge-up phase. It fires instantly on Z release (player.py line 286-287). The slime "shrinking" the user observes is just the juice-to-scale visual feedback (slime.py line 314) responding to juice consumption from other abilities (spit, drill, shield drain, etc.) -- not from charging. The slime remains independently visible and available because it is never placed into a "being consumed" state during any charge-up period, because no such period exists.
fix: (not applied -- diagnosis only)
verification: (not applied)
files_changed: []
