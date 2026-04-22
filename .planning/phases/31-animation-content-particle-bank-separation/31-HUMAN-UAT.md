---
status: partial
phase: 31-animation-content-particle-bank-separation
source: [31-VERIFICATION.md]
started: 2026-04-22T00:00:00Z
updated: 2026-04-22T00:00:00Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. SC1 — Visible transition frames in engine

expected: Each transition renders a distinct extra frame / pose beyond plain
idle/run/jump. Specifically:
- jump (stationary): jump_crouch frame briefly, then Metroid vertical hop
- jump (running): jump_crouch, then Metroid somersault
- land: 3-frame squash, then idle
- turn around: 3-frame skid frame before normal run resumes
- drill into a CRACKED_V block: 4-frame drill spin; on block break, spin
  briefly holds (pause_for) and a 14-particle diverging burst fires
- fuse: 16 converging particles followed by a growing blob at player center

result: [pending]

### 2. SC1 + SC2 — ANIM tab slider + Reload anim schema button

expected: F1 opens panel → click "Anim" tab → see "player_clips" collapsible
with 13 duration sliders. Drag ANIM_PLAYER_RUN_DURATION_0; run cycle ticks
faster/slower in real time. Reset arrow returns to baseline. Edit
assets/anim-schema.json on disk (e.g. set run.durations[0] from 6 to 2);
click "Reload anim schema" button → run cycle now ticks at duration=2.

result: [pending]

### 3. SC3 — Particle bank separation under load

expected: Drill through 5+ adjacent CRACKED_V blocks → one particle burst
per break. Map tiles continue rendering normally throughout and after; no
tile glyphs vanish or swap; no tile-slot competition under heavy particle load.

result: [pending]

### 4. SC1 tangential — drill_block_break bridge end-to-end

expected: Drilling a CRACKED_V tile emits exactly one drill_block_break
event from src/entities/player.py (provisional bridge); subscriber pauses
the drill_spin clip tick counter by DRILL_RECOIL_PAUSE_FRAMES and spawns
14 particles. No exceptions, no duplicate bursts.

result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps
