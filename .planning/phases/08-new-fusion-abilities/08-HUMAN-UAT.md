---
status: diagnosed
phase: 08-new-fusion-abilities
source: [08-VERIFICATION.md]
started: "2026-03-28T07:00:00.000Z"
updated: "2026-03-28T09:00:00.000Z"
---

## Current Test

[testing complete]

## Tests

### 1. Tap-vs-hold Z threshold
expected: Z tap (<=8 frames) fires spit, Z hold (>8 frames) starts recall. No accidental spit when recalling.
result: pass

### 2. Directional hold tap-vs-walk threshold
expected: LEFT/RIGHT tap (<=5 frames) repositions slime, hold (>5 frames) walks normally.
result: issue
reported: "Tapping to reposition the slime disables the following behavior of the slime. Tapping should just swap position. Hold-to-reposition should be handled with a different method if we decide to implement it."
severity: major

### 3. Slime Ram in-level
expected: V while fused = high-speed horizontal dash, breaks CRACKED_H blocks, stops at solid walls, dissipates on juice empty.
result: issue
reported: "The ram lodges the player inside the wall they collide with and stays inside the block."
severity: blocker

### 4. ABL-04 design intent -- hold-to-charge vs always-max
expected: Confirm D-18 (no charge levels, always max power) is canonical, or clarify if hold-to-charge is still intended.
result: issue
reported: "Max charge shot just reduces the slime size and the slime is available the whole time before hitting max capacity. Expected: slime should be consumed/fused during charge."
severity: major

## Summary

total: 4
passed: 1
issues: 3
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "LEFT/RIGHT tap repositions slime without disabling follow behavior"
  status: failed
  reason: "User reported: Tapping to reposition disables slime following. Tap should just swap position, not change follow state."
  severity: major
  test: 2
  artifacts: []
  missing: []

- truth: "Slime Ram stops at solid walls without lodging player inside"
  status: failed
  reason: "User reported: Ram lodges player inside the wall they collide with and stays stuck."
  severity: blocker
  test: 3
  artifacts: []
  missing: []

- truth: "Charge shot consumes/fuses slime properly during charge-up"
  status: failed
  reason: "User reported: Max charge shot just reduces slime size, slime stays available the whole time before hitting max capacity."
  severity: major
  test: 4
  artifacts: []
  missing: []
