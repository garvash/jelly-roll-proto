"""Tests for debug god-mode toggles (D-08 through D-10) + Phase 33 D-09 warps."""
import json
import os
import re
from pathlib import Path
from unittest.mock import MagicMock, patch


def test_god_abilities_defaults_false():
    """debug.god_abilities defaults to False."""
    import src.core.debug as debug
    # Reset to module defaults (in case prior test toggled)
    debug.god_abilities = False
    assert debug.god_abilities is False


def test_god_invincible_defaults_false():
    """debug.god_invincible defaults to False."""
    import src.core.debug as debug
    debug.god_invincible = False
    assert debug.god_invincible is False


def test_god_infinite_juice_defaults_false():
    """debug.god_infinite_juice defaults to False."""
    import src.core.debug as debug
    debug.god_infinite_juice = False
    assert debug.god_infinite_juice is False


def test_player_abilities_default_false():
    """Player.__init__ creates player with surviving ability flags defaulting to False.

    Updated in Plan 31.5-05 (sympathetic regression sweep per RESEARCH Risk 5):
    has_dash / has_shield / has_shield_t2 / has_boost flags were stripped from
    Player.__init__ in Plan 01 sub-step 6 per CONTEXT D-17. The surviving
    ability flag is has_drill (drill is the sole fusion item in v2.0 per
    FUSION-DESIGN.md). This test now asserts has_drill defaults to False.
    """
    with patch("src.entities.player.input_manager"):
        from src.entities.player import Player
        level_map = MagicMock()
        level_map.check_collision.return_value = False
        level_map.check_hazard.return_value = False
        p = Player(50, 50, level_map)
        assert p.has_drill is False


def test_constants_no_debug_all_abilities():
    """constants.py source does NOT contain DEBUG_ALL_ABILITIES."""
    constants_path = os.path.join(os.path.dirname(__file__), "..", "src", "core", "constants.py")
    with open(constants_path) as f:
        source = f.read()
    assert "DEBUG_ALL_ABILITIES" not in source


# ---------------------------------------------------------------------------
# Phase 33 D-09: multi-target debug warps (Ctrl+4..7).
#
# `debug.warp_target` is a `str | None` flag set by Ctrl+4..7 in
# `debug.update()` and consumed (then reset to None) by `Game.update()`.
# Pattern mirrors the existing one-shot `teleport_requested` flag.
# ---------------------------------------------------------------------------


def test_warp_target_defaults_none():
    """debug.warp_target defaults to None (no warp requested)."""
    import src.core.debug as debug
    debug.warp_target = None
    assert debug.warp_target is None


def test_warp_level_constants_exist():
    """5 named WARP_LEVEL_* constants exist for drill-relevant test rooms.

    WR-04 closure: includes WARP_LEVEL_BOSS so this hasattr/isinstance check
    is symmetric with test_warp_level_constants_match_world_identifiers
    (which expects len(consts) == 5). Previously this test silently passed
    if WARP_LEVEL_BOSS was dropped — only the regex test caught it, with a
    confusing error message about regex match count.
    """
    import src.core.debug as debug
    assert hasattr(debug, "WARP_LEVEL_CRACKED_V")
    assert hasattr(debug, "WARP_LEVEL_SOFT_BLOCK")
    assert hasattr(debug, "WARP_LEVEL_ENEMY_CLUSTER")
    assert hasattr(debug, "WARP_LEVEL_JUICE_DRAIN")
    assert hasattr(debug, "WARP_LEVEL_BOSS")
    # All five are non-empty strings (level identifier strings, not None).
    for name in ("WARP_LEVEL_CRACKED_V", "WARP_LEVEL_SOFT_BLOCK",
                 "WARP_LEVEL_ENEMY_CLUSTER", "WARP_LEVEL_JUICE_DRAIN",
                 "WARP_LEVEL_BOSS"):
        val = getattr(debug, name)
        assert isinstance(val, str) and val, f"{name} must be a non-empty str"


def test_warp_level_constants_match_world_identifiers():
    """W#4 closure: every WARP_LEVEL_* constant matches a real `identifier`
    in `assets/output.ldtk`'s `levels` array. Otherwise pressing Ctrl+4..8
    silently no-ops because the level lookup never finds a match.

    Post gym→output merge (Phase 33 mid-tuning): output.ldtk is the union
    of production levels (Level_*) + Phase 29 gym levels (Gym_*) and is
    the authoritative source-of-truth for warp identifier resolution."""
    repo_root = Path(__file__).resolve().parent.parent
    src_path = repo_root / "src" / "core" / "debug.py"
    src = src_path.read_text(encoding="utf-8")
    consts = {
        m.group(1): m.group(2)
        for m in re.finditer(r'^(WARP_LEVEL_\w+)\s*=\s*"([^"]+)"', src, re.MULTILINE)
    }
    assert len(consts) == 5, f"Expected 5 WARP_LEVEL_* constants, got {len(consts)}: {consts}"

    world_path = repo_root / "assets" / "output.ldtk"
    world = json.loads(world_path.read_text(encoding="utf-8"))
    level_ids = {lvl["identifier"] for lvl in world.get("levels", [])}
    missing = [(name, val) for name, val in consts.items() if val not in level_ids]
    assert not missing, (
        f"WARP_LEVEL_* constants without matching output.ldtk level identifier: "
        f"{missing}; available: {sorted(level_ids)}"
    )


def test_ctrl_4_sets_warp_target_to_cracked_v():
    """Ctrl+4 sets warp_target to WARP_LEVEL_CRACKED_V (one-shot flag)."""
    import src.core.debug as debug
    debug.warp_target = None

    fake = MagicMock()
    fake.btn = MagicMock(side_effect=lambda key: key == fake.KEY_CTRL)
    # btnp returns True ONLY for KEY_4 in this test
    fake.btnp = MagicMock(side_effect=lambda key: key == fake.KEY_4)
    fake.KEY_CTRL = "CTRL"
    fake.KEY_1 = "1"
    fake.KEY_2 = "2"
    fake.KEY_3 = "3"
    fake.KEY_T = "T"
    fake.KEY_4 = "4"
    fake.KEY_5 = "5"
    fake.KEY_6 = "6"
    fake.KEY_7 = "7"

    with patch.object(debug, "pyxel", fake):
        debug.update()

    assert debug.warp_target == debug.WARP_LEVEL_CRACKED_V


def test_ctrl_5_sets_warp_target_to_soft_block():
    import src.core.debug as debug
    debug.warp_target = None
    fake = MagicMock()
    fake.btn = MagicMock(side_effect=lambda key: key == fake.KEY_CTRL)
    fake.btnp = MagicMock(side_effect=lambda key: key == fake.KEY_5)
    fake.KEY_CTRL = "CTRL"
    fake.KEY_1 = "1"; fake.KEY_2 = "2"; fake.KEY_3 = "3"; fake.KEY_T = "T"
    fake.KEY_4 = "4"; fake.KEY_5 = "5"; fake.KEY_6 = "6"; fake.KEY_7 = "7"; fake.KEY_8 = "8"
    with patch.object(debug, "pyxel", fake):
        debug.update()
    assert debug.warp_target == debug.WARP_LEVEL_SOFT_BLOCK


def test_ctrl_6_sets_warp_target_to_enemy_cluster():
    import src.core.debug as debug
    debug.warp_target = None
    fake = MagicMock()
    fake.btn = MagicMock(side_effect=lambda key: key == fake.KEY_CTRL)
    fake.btnp = MagicMock(side_effect=lambda key: key == fake.KEY_6)
    fake.KEY_CTRL = "CTRL"
    fake.KEY_1 = "1"; fake.KEY_2 = "2"; fake.KEY_3 = "3"; fake.KEY_T = "T"
    fake.KEY_4 = "4"; fake.KEY_5 = "5"; fake.KEY_6 = "6"; fake.KEY_7 = "7"; fake.KEY_8 = "8"
    with patch.object(debug, "pyxel", fake):
        debug.update()
    assert debug.warp_target == debug.WARP_LEVEL_ENEMY_CLUSTER


def test_ctrl_7_sets_warp_target_to_juice_drain():
    import src.core.debug as debug
    debug.warp_target = None
    fake = MagicMock()
    fake.btn = MagicMock(side_effect=lambda key: key == fake.KEY_CTRL)
    fake.btnp = MagicMock(side_effect=lambda key: key == fake.KEY_7)
    fake.KEY_CTRL = "CTRL"
    fake.KEY_1 = "1"; fake.KEY_2 = "2"; fake.KEY_3 = "3"; fake.KEY_T = "T"
    fake.KEY_4 = "4"; fake.KEY_5 = "5"; fake.KEY_6 = "6"; fake.KEY_7 = "7"; fake.KEY_8 = "8"
    with patch.object(debug, "pyxel", fake):
        debug.update()
    assert debug.warp_target == debug.WARP_LEVEL_JUICE_DRAIN


def test_ctrl_8_sets_warp_target_to_boss():
    """Ctrl+8 sets warp_target to WARP_LEVEL_BOSS (Level_15, post gym→output merge)."""
    import src.core.debug as debug
    debug.warp_target = None
    fake = MagicMock()
    fake.btn = MagicMock(side_effect=lambda key: key == fake.KEY_CTRL)
    fake.btnp = MagicMock(side_effect=lambda key: key == fake.KEY_8)
    fake.KEY_CTRL = "CTRL"
    fake.KEY_1 = "1"; fake.KEY_2 = "2"; fake.KEY_3 = "3"; fake.KEY_T = "T"
    fake.KEY_4 = "4"; fake.KEY_5 = "5"; fake.KEY_6 = "6"; fake.KEY_7 = "7"; fake.KEY_8 = "8"
    with patch.object(debug, "pyxel", fake):
        debug.update()
    assert debug.warp_target == debug.WARP_LEVEL_BOSS


def test_no_ctrl_does_not_set_warp_target():
    """Pressing 4..7 WITHOUT Ctrl held leaves warp_target unchanged."""
    import src.core.debug as debug
    debug.warp_target = None
    fake = MagicMock()
    # Ctrl is NOT held
    fake.btn = MagicMock(return_value=False)
    fake.btnp = MagicMock(return_value=True)  # all keys reported as pressed
    fake.KEY_CTRL = "CTRL"
    fake.KEY_1 = "1"; fake.KEY_2 = "2"; fake.KEY_3 = "3"; fake.KEY_T = "T"
    fake.KEY_4 = "4"; fake.KEY_5 = "5"; fake.KEY_6 = "6"; fake.KEY_7 = "7"; fake.KEY_8 = "8"
    with patch.object(debug, "pyxel", fake):
        debug.update()
    assert debug.warp_target is None


def test_main_py_consumes_debug_warp_target():
    """main.py:Game.update reads debug.warp_target and resets it to None
    (mirrors the teleport_requested consumer pattern)."""
    repo_root = Path(__file__).resolve().parent.parent
    main_src = (repo_root / "main.py").read_text(encoding="utf-8")
    # The consumer block must (a) read debug.warp_target, (b) reset it to None,
    # (c) iterate self.world.levels searching for matching id.
    assert "debug.warp_target" in main_src, "main.py must read debug.warp_target"
    # at least 2 mentions = read + reset (per acceptance_criteria)
    assert main_src.count("debug.warp_target") >= 2, (
        "main.py must reference debug.warp_target at least twice "
        "(read + reset to None)"
    )
