"""Phase 33 FUS-06 D-01/D-02/D-05/D-17 — tuning migration smoke tests.

RED until Wave 1 ships schema additions to assets/physics-schema.json.

Coverage:
- Six new keys (D-01: WINDUP_DURATION_FRAMES, ACCELERATED_REGEN_RATE;
  D-02: POGO_BOUNCE_VELOCITY, POGO_COOLDOWN_FRAMES; D-05: DRILL_ENEMY_COST;
  D-17: SLIME_DAZE_COST) read schema-seed values via getattr(tuning, key).
- All 6 keys present in tuning._flat_index (Pitfall 6 — panel surface
  contract).
- Use-site-read invariant: charge_controller.py and pogo.py read
  tuning.X (not module-level constants) post-migration. POGO_INITIAL_DY +
  POGO_DAMAGE STAY hardcoded per D-02 (gameplay/visual constants, not
  tuning surface).

Pitfall 5 prevention: schema-seed value MUST equal current hardcoded baseline,
otherwise downstream tests like test_fusion_fsm.py::test_windup_* flicker red.
"""
import re
from pathlib import Path
import pytest
from src.core import tuning


@pytest.fixture(autouse=True)
def _tuning_reset():
    """Restore baseline after each test (mirrors test_tuning_livereach.py:51-56)."""
    yield
    tuning.reset()


# Phase 33 D-01/D-02/D-05/D-17 — schema-seed baseline values (no magic numbers).
EXPECTED_WINDUP_DURATION_FRAMES = 30
EXPECTED_ACCELERATED_REGEN_RATE = 1.0
EXPECTED_POGO_BOUNCE_VELOCITY = -2.5
EXPECTED_POGO_COOLDOWN_FRAMES = 0
EXPECTED_DRILL_ENEMY_COST = 15.0   # CONTEXT D-05 starting point
EXPECTED_SLIME_DAZE_COST = 20.0    # CONTEXT D-17 starting point


@pytest.mark.parametrize("key,expected", [
    ("WINDUP_DURATION_FRAMES",  EXPECTED_WINDUP_DURATION_FRAMES),
    ("ACCELERATED_REGEN_RATE",  EXPECTED_ACCELERATED_REGEN_RATE),
    ("POGO_BOUNCE_VELOCITY",    EXPECTED_POGO_BOUNCE_VELOCITY),
    ("POGO_COOLDOWN_FRAMES",    EXPECTED_POGO_COOLDOWN_FRAMES),
    ("DRILL_ENEMY_COST",        EXPECTED_DRILL_ENEMY_COST),
    ("SLIME_DAZE_COST",         EXPECTED_SLIME_DAZE_COST),
])
def test_new_tuning_key_readable(key, expected):
    actual = getattr(tuning, key)
    assert actual == expected, (
        f"tuning.{key} expected {expected!r}, got {actual!r}. "
        f"Pitfall 5: schema-seed must equal current hardcoded baseline."
    )


def test_new_tuning_keys_in_flat_index():
    expected_keys = {"WINDUP_DURATION_FRAMES", "ACCELERATED_REGEN_RATE",
                     "POGO_BOUNCE_VELOCITY", "POGO_COOLDOWN_FRAMES",
                     "DRILL_ENEMY_COST", "SLIME_DAZE_COST"}
    missing = expected_keys - set(tuning._flat_index)
    assert not missing, f"Pitfall 6 — missing tuning keys: {missing}"


# Phase 33 D-01: use-site-read invariant. After Wave 1 migration,
# charge_controller.py MUST read tuning.X (not module-level constants).
def test_charge_controller_uses_tuning_at_use_site():
    cc_path = Path("src/fusion/charge_controller.py")
    text = cc_path.read_text(encoding="utf-8")
    # Module-level constant assignments must NOT exist post-migration.
    assert not re.search(r"^WINDUP_DURATION_FRAMES\s*=", text, re.MULTILINE), (
        "D-01: WINDUP_DURATION_FRAMES module constant should be deleted; "
        "use tuning.WINDUP_DURATION_FRAMES at use-site instead."
    )
    assert not re.search(r"^ACCELERATED_REGEN_RATE\s*=", text, re.MULTILINE), (
        "D-01: ACCELERATED_REGEN_RATE module constant should be deleted."
    )
    # Use-site reads must exist.
    assert "tuning.WINDUP_DURATION_FRAMES" in text, (
        "D-01: charge_controller.py must read tuning.WINDUP_DURATION_FRAMES"
    )
    assert "tuning.ACCELERATED_REGEN_RATE" in text, (
        "D-01: charge_controller.py must read tuning.ACCELERATED_REGEN_RATE"
    )


def test_pogo_uses_tuning_at_use_site():
    pogo_path = Path("src/fusion/pogo.py")
    text = pogo_path.read_text(encoding="utf-8")
    assert not re.search(r"^POGO_BOUNCE_VELOCITY\s*=", text, re.MULTILINE), (
        "D-02: POGO_BOUNCE_VELOCITY module constant should be deleted."
    )
    assert not re.search(r"^POGO_COOLDOWN_FRAMES\s*=", text, re.MULTILINE), (
        "D-02: POGO_COOLDOWN_FRAMES module constant should be deleted."
    )
    assert "tuning.POGO_BOUNCE_VELOCITY" in text
    # POGO_INITIAL_DY and POGO_DAMAGE STAY hardcoded per D-02.
    assert re.search(r"^POGO_INITIAL_DY\s*=", text, re.MULTILINE), (
        "D-02: POGO_INITIAL_DY MUST stay hardcoded (Mario-64 visual parity)."
    )
    assert re.search(r"^POGO_DAMAGE\s*=", text, re.MULTILINE), (
        "D-02: POGO_DAMAGE MUST stay hardcoded (gameplay constant)."
    )
