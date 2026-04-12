"""Preset save/load for the live-tuning panel (D-11 through D-15)."""
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
    """Return list of feel-relevant tuning keys."""
    return [k for k, g in tuning._flat_index.items() if g in FEEL_GROUPS]


def save_preset(slot, alias=""):
    """Save current feel-relevant values to assets/presets/slot_N.json (D-13).

    Uses atomic write pattern: .tmp file + os.fsync + os.replace.
    """
    os.makedirs(PRESETS_DIR, exist_ok=True)
    values = {}
    for key in _feel_keys():
        values[key] = getattr(tuning, key)
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
    """Load preset, apply all values via tuning.set_value() (D-11).

    Returns (slot, alias) or raises FileNotFoundError/JSONDecodeError.
    Wraps set_value in try/except KeyError for schema evolution safety --
    keys removed from the schema since the preset was saved are silently skipped.
    """
    path = PRESETS_DIR / f"slot_{slot}.json"
    with open(path, encoding="utf-8") as f:
        preset = json.load(f)
    alias = preset.get("alias", f"slot {slot}")
    for key, val in preset["values"].items():
        try:
            tuning.set_value(key, val)
        except KeyError:
            pass  # Key removed from schema -- skip
    return slot, alias


def get_preset_alias(slot):
    """Read alias from preset file without loading values."""
    path = PRESETS_DIR / f"slot_{slot}.json"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f).get("alias", f"slot {slot}")
    except (FileNotFoundError, json.JSONDecodeError):
        return f"slot {slot}"
