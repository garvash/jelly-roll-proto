"""Verify kick mechanic is fully removed (D-10)."""
import unittest


class TestKickRemoval(unittest.TestCase):
    def test_no_kick_timer_attribute(self):
        """Verify kick_timer is not on Player."""
        with open("src/entities/player.py") as f:
            source = f.read()
        self.assertNotIn("kick_timer", source)

    def test_no_kick_method(self):
        """Verify kick() method is removed."""
        with open("src/entities/player.py") as f:
            source = f.read()
        self.assertNotIn("def kick(", source)

    def test_no_kick_constants(self):
        """Verify KICK_DURATION and SLIME_PUNT_SPEED removed."""
        with open("src/core/constants.py") as f:
            source = f.read()
        self.assertNotIn("KICK_DURATION", source)
        self.assertNotIn("SLIME_PUNT_SPEED", source)

    def test_no_kick_in_main(self):
        """Verify kick door-opening removed from main.py."""
        with open("main.py") as f:
            source = f.read()
        self.assertNotIn("kick_timer", source)


if __name__ == "__main__":
    unittest.main()
