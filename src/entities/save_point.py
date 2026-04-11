"""Save point entity for save room interaction."""
import pyxel
from src.core import tuning


class SavePoint:
    """Interactive save station. Player stands nearby and presses UP to save."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 16   # Match LDtk entity size
        self.h = 16
        self.pulse_timer = 0
        self.prompt_state = None  # None, "SAVE?", or "SAVED!"
        self.prompt_timer = 0

    def is_player_near(self, player):
        """Check AABB overlap between player and save point."""
        return (player.x < self.x + self.w and
                player.x + player.w > self.x and
                player.y < self.y + self.h and
                player.y + player.h > self.y)

    def update(self, player):
        """Update pulse animation and prompt state."""
        self.pulse_timer = (self.pulse_timer + 1) % tuning.SAVE_PULSE_CYCLE

        if self.prompt_state == "SAVED!":
            self.prompt_timer -= 1
            if self.prompt_timer <= 0:
                self.prompt_state = None

        if self.is_player_near(player):
            if self.prompt_state != "SAVED!":
                self.prompt_state = "SAVE?"
        else:
            if self.prompt_state != "SAVED!":
                self.prompt_state = None

    def on_save(self):
        """Called after successful save to show confirmation."""
        self.prompt_state = "SAVED!"
        self.prompt_timer = tuning.SAVE_PROMPT_DURATION

    def draw(self):
        """Draw save point with pulsing color effect."""
        # Pulse between yellow (10) and orange (9) per D-05
        color = 10 if self.pulse_timer < tuning.SAVE_PULSE_HALF else 9
        vx = self.x
        vy = self.y
        pyxel.rect(vx, vy, 16, 16, color)
        # Inner detail
        pyxel.rect(vx + 4, vy + 2, 8, 6, 7)   # White crystal top
        pyxel.rect(vx + 2, vy + 10, 12, 6, color)  # Base

        # Draw prompt text above entity
        if self.prompt_state:
            text = self.prompt_state
            # Center text (4px per char in Pyxel default font)
            tx = self.x + self.w // 2 - len(text) * 2
            ty = self.y - 16  # Above the visual
            pyxel.text(tx, ty, text, 10)  # Yellow text per UI-SPEC
