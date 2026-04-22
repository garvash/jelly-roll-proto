"""Phase 31 ANIM-05 tuning.load_anim fail-fast + routing tests."""
import json
import pytest
from src.core import tuning


def test_load_anim_builds_namespace(tmp_path):
    good = {
        "player": {
            "clips": {
                "idle": {"frames": [0], "durations": [1], "loop": True},
                "run": {"frames": [16, 32], "durations": [6, 6], "loop": True},
            },
        },
    }
    path = tmp_path / "anim-good.json"
    path.write_text(json.dumps(good), encoding="utf-8")
    tuning.load_anim(schema_path=path)
    assert tuning.anim.player.clips["idle"].frames == [0]
    assert tuning.anim.player.clips["idle"].durations == [1]
    assert tuning.anim.player.clips["idle"].loop is True
    assert tuning.anim.player.clips["idle"].events == {}
    assert tuning.anim.player.clips["run"].frames == [16, 32]
    assert tuning.anim.player.clips["run"].durations == [6, 6]


def test_load_anim_fails_on_missing_clips_dict(tmp_path):
    bad = {"player": {}}
    path = tmp_path / "anim-bad.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="missing 'clips'"):
        tuning.load_anim(schema_path=path)


def test_load_anim_fails_on_length_mismatch(tmp_path):
    bad = {"player": {"clips": {"run": {"frames": [0, 16], "durations": [6]}}}}
    path = tmp_path / "anim-bad.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="length mismatch"):
        tuning.load_anim(schema_path=path)


def test_load_anim_fails_on_unknown_field(tmp_path):
    bad = {"player": {"clips": {"run": {"frames": [0], "durations": [1], "bogus": 42}}}}
    path = tmp_path / "anim-bad.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="unknown fields"):
        tuning.load_anim(schema_path=path)


def test_load_anim_fails_on_missing_frames(tmp_path):
    bad = {"player": {"clips": {"run": {"durations": [1]}}}}
    path = tmp_path / "anim-bad.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="missing frames/durations"):
        tuning.load_anim(schema_path=path)


def test_load_anim_fails_on_missing_durations(tmp_path):
    bad = {"player": {"clips": {"run": {"frames": [0]}}}}
    path = tmp_path / "anim-bad.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="missing frames/durations"):
        tuning.load_anim(schema_path=path)


def test_anim_flat_index_built(tmp_path):
    good = {
        "player": {"clips": {
            "idle": {"frames": [0], "durations": [1]},
            "run":  {"frames": [16, 32], "durations": [6, 6]},
        }},
    }
    path = tmp_path / "anim.json"
    path.write_text(json.dumps(good), encoding="utf-8")
    tuning.load_anim(schema_path=path)
    assert "ANIM_PLAYER_IDLE_DURATION_0" in tuning._anim_flat_index
    assert "ANIM_PLAYER_RUN_DURATION_0" in tuning._anim_flat_index
    assert "ANIM_PLAYER_RUN_DURATION_1" in tuning._anim_flat_index


def test_get_anim_value_returns_current(tmp_path):
    good = {"player": {"clips": {"run": {"frames": [16, 32], "durations": [6, 6]}}}}
    path = tmp_path / "anim.json"
    path.write_text(json.dumps(good), encoding="utf-8")
    tuning.load_anim(schema_path=path)
    assert tuning.get_anim_value("ANIM_PLAYER_RUN_DURATION_0") == 6


def test_get_anim_baseline_returns_initial(tmp_path):
    good = {"player": {"clips": {"run": {"frames": [16, 32], "durations": [6, 6]}}}}
    path = tmp_path / "anim.json"
    path.write_text(json.dumps(good), encoding="utf-8")
    tuning.load_anim(schema_path=path)
    tuning.set_anim_value("ANIM_PLAYER_RUN_DURATION_0", 3)
    assert tuning.get_anim_value("ANIM_PLAYER_RUN_DURATION_0") == 3
    assert tuning.get_anim_baseline("ANIM_PLAYER_RUN_DURATION_0") == 6


def test_set_anim_value_writes_namespace(tmp_path):
    good = {"player": {"clips": {"run": {"frames": [16, 32], "durations": [6, 6]}}}}
    path = tmp_path / "anim.json"
    path.write_text(json.dumps(good), encoding="utf-8")
    tuning.load_anim(schema_path=path)
    tuning.set_anim_value("ANIM_PLAYER_RUN_DURATION_0", 99)
    assert tuning.anim.player.clips["run"].durations[0] == 99


def test_set_anim_value_unknown_key_raises(tmp_path):
    good = {"player": {"clips": {"run": {"frames": [0], "durations": [1]}}}}
    path = tmp_path / "anim.json"
    path.write_text(json.dumps(good), encoding="utf-8")
    tuning.load_anim(schema_path=path)
    with pytest.raises(KeyError):
        tuning.set_anim_value("ANIM_BOGUS", 1)


def test_load_anim_isolation_from_physics_flat_index(tmp_path):
    flat_before = dict(tuning._flat_index)
    good = {"player": {"clips": {"run": {"frames": [16, 32], "durations": [6, 6]}}}}
    path = tmp_path / "anim.json"
    path.write_text(json.dumps(good), encoding="utf-8")
    tuning.load_anim(schema_path=path)
    assert dict(tuning._flat_index) == flat_before


def test_real_anim_schema_loads():
    """Default path load succeeds -- exercises assets/anim-schema.json seed data."""
    tuning.load_anim()
    clips = tuning.anim.player.clips
    for clip_id in [
        "idle", "run", "jump",
        "jump_stationary", "jump_running",
        "jump_crouch", "land_squash", "turn_skid", "drill_spin",
    ]:
        assert clip_id in clips, f"{clip_id} missing from anim-schema.json"


# ---------------------------------------------------------------------------
# Phase 31 Plan 05 Task 4: presets.py routes ANIM_ keys (Pitfall 6 fix)
# ---------------------------------------------------------------------------

def test_save_preset_includes_anim_durations(tmp_path, monkeypatch):
    from src.ui import presets
    monkeypatch.setattr(presets, "PRESETS_DIR", tmp_path)
    tuning.load_anim()
    presets.save_preset(slot=9, alias="test-save-anim")
    path = tmp_path / "slot_9.json"
    assert path.exists()
    data = json.loads(path.read_text())
    values = data["values"]
    # Physics keys present
    assert any(not k.startswith("ANIM_") for k in values), "No physics keys saved"
    # Anim keys present
    assert "ANIM_PLAYER_RUN_DURATION_0" in values, (
        "Preset must include anim duration keys (Pitfall 6 + D-12)"
    )


def test_load_preset_routes_anim_keys(tmp_path, monkeypatch):
    from src.ui import presets
    monkeypatch.setattr(presets, "PRESETS_DIR", tmp_path)
    tuning.load_anim()
    gravity_before = tuning.GRAVITY
    preset = {
        "version": "1.0",
        "schema_version": "0.3.0",
        "slot": 9,
        "alias": "test-load-anim",
        "timestamp": "2026-04-22T00:00:00Z",
        "values": {
            "GRAVITY": 0.123,
            "ANIM_PLAYER_RUN_DURATION_0": 99,
        },
    }
    (tmp_path / "slot_9.json").write_text(json.dumps(preset), encoding="utf-8")
    presets.load_preset(9)
    assert tuning.get_anim_value("ANIM_PLAYER_RUN_DURATION_0") == 99
    assert abs(tuning.GRAVITY - 0.123) < 1e-9
    # Restore isolation for subsequent tests
    tuning.set_value("GRAVITY", gravity_before)
    tuning.load_anim()


def test_load_preset_skips_unknown_anim_keys(tmp_path, monkeypatch):
    from src.ui import presets
    monkeypatch.setattr(presets, "PRESETS_DIR", tmp_path)
    tuning.load_anim()
    preset = {
        "version": "1.0",
        "schema_version": "0.3.0",
        "slot": 9,
        "alias": "test-skip",
        "timestamp": "2026-04-22T00:00:00Z",
        "values": {
            "ANIM_BOGUS_KEY_NOT_IN_INDEX": 777,
            "ALSO_NOT_A_KEY": 888,
        },
    }
    (tmp_path / "slot_9.json").write_text(json.dumps(preset), encoding="utf-8")
    # Must not raise -- forward-compat skip on both namespaces
    presets.load_preset(9)
