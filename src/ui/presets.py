"""Preset save/load for the live-tuning panel (D-11 through D-15).

Phase 31 ANIM-05: anim duration keys (ANIM_ prefix) route through
tuning.get_anim_value / tuning.set_anim_value instead of the flat physics
set_value (which would silently swallow KeyError for anim keys per
Pitfall 6).
"""
import json
import os
import time
from pathlib import Path
from src.core import tuning

PRESETS_DIR = Path(__file__).resolve().parents[2] / "assets" / "presets"
FEEL_GROUPS = {
    "movement", "dash", "forgiving", "wall",
    "slime_follow", "slime_juice", "projectile",
    "drill", "fusion", "slime_ram", "charge_shot", "boost",
}


def _feel_keys():
    """Return list of feel-relevant physics tuning keys."""
    return [k for k, g in tuning._flat_index.items() if g in FEEL_GROUPS]


def _anim_keys():
    """Return list of anim duration flat keys (Phase 31 D-12)."""
    return list(tuning._anim_flat_index.keys())


def save_preset(slot, alias=""):
    """Save current feel-relevant values to assets/presets/slot_N.json (D-13).

    Phase 31: includes anim duration keys (ANIM_ prefix) alongside physics keys.
    Uses atomic write pattern: .tmp file + os.fsync + os.replace.
    """
    os.makedirs(PRESETS_DIR, exist_ok=True)
    values = {}
    # Physics keys
    for key in _feel_keys():
        values[key] = getattr(tuning, key)
    # Phase 31: anim duration keys
    for key in _anim_keys():
        values[key] = tuning.get_anim_value(key)
    preset = {
        "version": "1.0",
        "schema_version": "0.3.0",
        "slot": slot,
        "alias": alias,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "values": values,
    }
    path = PRESETS_DIR / f"slot_{slot}.json"
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(preset, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def load_preset(slot):
    """Load preset, apply values via tuning.set_value / tuning.set_anim_value (D-11).

    Phase 31 ANIM-05 Pitfall 6 fix: ANIM_-prefixed keys route to set_anim_value
    instead of set_value (which would silently swallow KeyError for anim keys
    not present in _flat_index).

    Returns (slot, alias) or raises FileNotFoundError/JSONDecodeError.
    Unknown keys (removed from schema since preset saved) are silently skipped
    per existing schema-evolution policy.
    """
    path = PRESETS_DIR / f"slot_{slot}.json"
    with open(path, encoding="utf-8") as f:
        preset = json.load(f)
    alias = preset.get("alias", f"slot {slot}")
    for key, val in preset["values"].items():
        if key.startswith("ANIM_"):
            try:
                tuning.set_anim_value(key, val)
            except KeyError:
                pass  # anim key removed -- forward-compat skip
        else:
            try:
                tuning.set_value(key, val)
            except KeyError:
                pass  # physics key removed -- forward-compat skip
    return slot, alias


def get_preset_alias(slot):
    """Read alias from preset file without loading values."""
    path = PRESETS_DIR / f"slot_{slot}.json"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f).get("alias", f"slot {slot}")
    except (FileNotFoundError, json.JSONDecodeError):
        return f"slot {slot}"
