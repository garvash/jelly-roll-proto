"""Runtime god-mode toggles for debug playtesting (D-08, D-09, D-10).

All flags default to False. Toggled at runtime via Ctrl+1/2/3.
Tests are never affected because flags only change via key press.
"""
import pyxel

# God-mode tier toggles (D-09)
god_abilities = False      # Toggle 1: unlock all abilities
god_invincible = False     # Toggle 2: no damage taken
god_infinite_juice = False # Toggle 3: infinite juice

# One-shot teleport flag (Phase 29): consumed by main.py after debug.update()
teleport_requested = False

def update():
    """Check debug key combos. Call from Game.update()."""
    global god_abilities, god_invincible, god_infinite_juice, teleport_requested
    if pyxel.btn(pyxel.KEY_CTRL):
        if pyxel.btnp(pyxel.KEY_1):
            god_abilities = not god_abilities
        if pyxel.btnp(pyxel.KEY_2):
            god_invincible = not god_invincible
        if pyxel.btnp(pyxel.KEY_3):
            god_infinite_juice = not god_infinite_juice
        if pyxel.btnp(pyxel.KEY_T):
            teleport_requested = True
