---
status: complete
phase: 13-sprite-scale-png-spritesheets
source: [13-01-SUMMARY.md, 13-02-SUMMARY.md, 13-03-SUMMARY.md]
started: 2026-03-29T20:00:00+09:00
updated: 2026-03-29T20:15:00+09:00
---

## Current Test

[testing complete]

## Tests

### 1. Player sprite renders at 16x16 with walk animation
expected: Player appears as a 16x16 sprite (visually larger than 8x8 tiles). Idle shows frame 0, walking cycles between frames 1-2 smoothly. Feet align with ground tiles (bottom-center anchoring).
result: pass

### 2. Slime companion renders at 16x16 with scale effect
expected: Slime renders at 16x16 visual size, follows player. As juice depletes, slime visually shrinks via scale parameter. Fused state shows distinct sprite frame.
result: pass

### 3. Enemies render at 16x16 (Snail and Bat)
expected: Snail moves with 2-frame animation at 16x16. Bat hangs then dives at 16x16. Both visually larger than tiles but collision stays 8x8.
result: pass

### 4. Boss Mole renders at 32x32
expected: Boss appears at 32x32 visual size (2x its 16x16 collision box). Emerging/vulnerable states animate with 32px frame stride. Vulnerability flicker and death explosion still work.
result: pass

### 5. Projectiles and effects render at 16x16
expected: Spit projectile draws at 16x16 with correct facing direction. Explosion effects animate at 16x16 with 3-frame cycle. Charge shot projectile also renders correctly.
result: pass

### 6. Items render at 16x16 with bobbing
expected: Energy tanks, missile tanks, dash pickup, shield pickup, and boost pickup all render at 16x16 from bank 1 row y=64. Bobbing animation and shine effect still visible.
result: pass

### 7. PNG spritesheets load instead of pyxres sprites
expected: Game launches without errors. Sprites come from PNG files in assets/sprites/ rather than game.pyxres image banks. No blank/missing sprites visible during gameplay.
result: pass

### 8. Custom Aseprite player.png works in-game
expected: The hand-drawn player.png you created loads and displays correctly — idle, walk, and jump frames all show your custom art rather than auto-upscaled sprites.
result: pass

### 9. Entity-schema.json has sprite metadata
expected: assets/entity-schema.json contains sprite fields (sprite_sheet, sprite_size, sprite_row, frame_count) for entity types. JSON is valid and parseable.
result: pass

## Summary

total: 9
passed: 9
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none]
