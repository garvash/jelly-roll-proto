"""Runtime god-mode toggles + Phase 29/33 debug warp targets.

All flags default to False / None. Toggled at runtime via Ctrl+1/2/3/T/4..7.
Tests are never affected because flags only change via key press.
"""
import pyxel

# God-mode tier toggles (D-09)
god_abilities = False      # Toggle 1: unlock all abilities
god_invincible = False     # Toggle 2: no damage taken
god_infinite_juice = False # Toggle 3: infinite juice

# One-shot teleport flag (Phase 29): consumed by main.py after debug.update()
teleport_requested = False

# Phase 33 D-09: drill-relevant warp targets. Set to a level-id string when
# a warp key (Ctrl+4..7) is pressed; consumed by main.py:Game.update which
# repositions player + camera into the matching level and resets to None.
# Pattern mirrors `teleport_requested`.
warp_target: str | None = None

# Level-id constants per CONTEXT D-09 coverage. Active world is `assets/gym.ldtk`
# (verified by main.py boot path). gym.ldtk has 6 levels: Gym_AccelRunway,
# Gym_CoyoteTest, Gym_GapTrio, Gym_HeightSteps, Gym_WallSlide, Gym_ZigzagShaft.
#
# Substitution carve-outs (gym.ldtk content audit, Phase 33 Plan 06 Task 1):
#   - Only Gym_AccelRunway contains `cracked_V` tiles -> CRACKED_V slot.
#   - No gym level contains `soft_block` tiles -> SOFT_BLOCK uses Gym_GapTrio
#     (closest analog: gap-traversal level for drilling-style movement tests).
#   - No gym level contains Snail/Bat enemies -> ENEMY_CLUSTER uses Gym_HeightSteps
#     (closest analog: open playground room).
#   - No gym level has dedicated juice-hazard tiles -> JUICE_DRAIN uses
#     Gym_ZigzagShaft (vertical shaft, good for drilling-drain testing).
# Recorded in `.planning/phases/33-.../33-06-SUMMARY.md` per plan NOTE.
WARP_LEVEL_CRACKED_V = "Gym_AccelRunway"      # only level with cracked_V tiles
WARP_LEVEL_SOFT_BLOCK = "Gym_GapTrio"         # carve-out: no soft_block in gym
WARP_LEVEL_ENEMY_CLUSTER = "Gym_HeightSteps"  # carve-out: no enemies in gym
WARP_LEVEL_JUICE_DRAIN = "Gym_ZigzagShaft"    # carve-out: no juice hazard tiles


def update():
    """Check debug key combos. Call from Game.update()."""
    global god_abilities, god_invincible, god_infinite_juice
    global teleport_requested, warp_target
    if pyxel.btn(pyxel.KEY_CTRL):
        if pyxel.btnp(pyxel.KEY_1):
            god_abilities = not god_abilities
        if pyxel.btnp(pyxel.KEY_2):
            god_invincible = not god_invincible
        if pyxel.btnp(pyxel.KEY_3):
            god_infinite_juice = not god_infinite_juice
        if pyxel.btnp(pyxel.KEY_T):
            teleport_requested = True
        # Phase 33 D-09: drill-relevant warp hotkeys (Ctrl+4..7).
        if pyxel.btnp(pyxel.KEY_4):
            warp_target = WARP_LEVEL_CRACKED_V
        if pyxel.btnp(pyxel.KEY_5):
            warp_target = WARP_LEVEL_SOFT_BLOCK
        if pyxel.btnp(pyxel.KEY_6):
            warp_target = WARP_LEVEL_ENEMY_CLUSTER
        if pyxel.btnp(pyxel.KEY_7):
            warp_target = WARP_LEVEL_JUICE_DRAIN
