"""Phase 24 source-of-truth tuning loader.

Reads ``assets/physics-schema.json`` (v0.3.x) at module import time and exposes
every leaf under ``tuning.*`` as a flat PEP 562 module attribute so call sites
can write ``from src.core import tuning; tuning.GRAVITY``.

Design decisions (see ``.planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md``):

* **D-01/D-02** — ``_model`` is the runtime source of truth. ``set_value`` mutates
  it only; no disk I/O.
* **D-03** — ``save()`` is the only function that touches disk. Atomic
  temp-file + ``os.replace`` idiom.
* **D-04** — ``_baseline`` is a frozen ``deepcopy`` of ``_model`` captured at
  ``load()`` time. ``reset(key=None)`` restores from it.
* **D-10/D-11** — ``bake_derived()`` is *never* called automatically. Only the
  explicit ``python -m src.core.tuning bake`` CLI (or Phase 36's ship bake)
  invokes it.
* **D-13/D-14** — Flat namespace. A one-time ``_flat_index: flat_key -> group``
  is built at load and used by ``__getattr__`` / ``set_value`` / ``get_group``.
* **D-15** — Duplicate flat keys across groups raise ``ValueError`` at load time.
* **D-18** — **No file watcher.** No modification-time polling, no third-party
  file-system-event library, no autosave, no quit hook. The Phase 28 panel is
  the only editing surface.
"""

import copy
import json
import os
import pathlib

# --- Module state -----------------------------------------------------------
# All module globals are initialised to sentinels. ``load()`` populates them.
_schema_path: pathlib.Path | None = None
_raw: dict | None = None
_model: dict | None = None
_baseline: dict | None = None
_flat_index: dict[str, str] = {}
__all__: list[str] = []

# Default schema path: <repo-root>/assets/physics-schema.json
# ``parents[2]`` climbs src/core/tuning.py -> src/core -> src -> <repo-root>.
_DEFAULT_SCHEMA = (
    pathlib.Path(__file__).resolve().parents[2] / "assets" / "physics-schema.json"
)

_SUPPORTED_SCHEMA_MAJOR = "0.3"


# --- Load / introspection ---------------------------------------------------
def load(schema_path: str | pathlib.Path | None = None) -> None:
    """Read the schema from disk and (re)populate the module state.

    Idempotent: calling ``load()`` twice replays the read and takes a fresh
    baseline. ``FileNotFoundError`` and ``json.JSONDecodeError`` propagate
    intentionally (T-24-08) so the game fails loudly on a broken schema
    rather than silently running with zeros.
    """
    global _schema_path, _raw, _model, _baseline, _flat_index

    path = pathlib.Path(schema_path) if schema_path is not None else _DEFAULT_SCHEMA
    _schema_path = path

    with open(path, encoding="utf-8") as f:
        _raw = json.load(f)

    version = _raw.get("version", "")
    if not isinstance(version, str) or not version.startswith(_SUPPORTED_SCHEMA_MAJOR):
        raise ValueError(
            f"Unsupported physics-schema version {version!r} at {path}; "
            f"expected {_SUPPORTED_SCHEMA_MAJOR}.x. Likely a stale v0.2.0 schema "
            f"that was never migrated to the v0.3.0 tuning.* layout."
        )

    tuning_block = _raw.get("tuning")
    if not isinstance(tuning_block, dict):
        raise ValueError(
            f"physics-schema at {path} has no top-level 'tuning' object; "
            f"cannot build flat-key index."
        )
    _model = tuning_block

    # Build flat-key index and enforce D-15 name-uniqueness across groups.
    new_index: dict[str, str] = {}
    for group_name, group_dict in _model.items():
        if not isinstance(group_dict, dict):
            raise ValueError(
                f"tuning group {group_name!r} must be an object, got "
                f"{type(group_dict).__name__}"
            )
        for leaf_name in group_dict:
            if leaf_name in new_index:
                first_group = new_index[leaf_name]
                raise ValueError(
                    f"Duplicate tuning leaf {leaf_name!r} in groups "
                    f"{first_group!r} and {group_name!r}"
                )
            new_index[leaf_name] = group_name
    _flat_index = new_index

    # D-04: baseline is a frozen deepcopy taken once per load().
    _baseline = copy.deepcopy(_model)

    # __all__ exposes every flat leaf for ``from src.core.tuning import *``.
    __all__[:] = sorted(_flat_index.keys())


def get_group(key: str) -> str:
    """Return the schema group name for a flat key (e.g. ``'GRAVITY' -> 'movement'``).

    Used by the Phase 28 panel for tab placement (D-14). Raises ``KeyError``
    on any key not present in the current flat index.
    """
    if key not in _flat_index:
        raise KeyError(f"unknown tuning key {key!r} (not in _flat_index)")
    return _flat_index[key]


def get_baseline(key: str):
    """Return the boot-time value of a flat key (D-04).

    Reads from ``_baseline``, never from ``_model``, so subsequent
    ``set_value`` calls do not change what this returns.
    """
    if key not in _flat_index:
        raise KeyError(f"unknown tuning key {key!r} (not in _flat_index)")
    return _baseline[_flat_index[key]][key]


# --- Mutation API -----------------------------------------------------------
def set_value(key: str, value) -> None:
    """Mutate ``_model[group][key] = value`` (D-02/D-14).

    No disk I/O, no type coercion, O(1). Rejects unknown keys with
    ``KeyError`` so the panel cannot inject arbitrary keys at runtime
    (T-24-10).
    """
    if key not in _flat_index:
        raise KeyError(f"unknown tuning key {key!r} (not in _flat_index)")
    _model[_flat_index[key]][key] = value


def reset(key: str | None = None) -> None:
    """Restore ``_model`` from ``_baseline`` (D-04).

    With ``key=None``, every leaf is restored. With an explicit flat ``key``,
    only that single leaf is touched. Raises ``KeyError`` on an unknown key.
    """
    global _model

    if key is None:
        # Full reset. Rebind _raw['tuning'] to a fresh deepcopy of the baseline
        # so later save() serialises the reset values, and re-point _model at
        # the same object so attribute reads see the restored state.
        _raw["tuning"] = copy.deepcopy(_baseline)
        _model = _raw["tuning"]
        return

    if key not in _flat_index:
        raise KeyError(f"unknown tuning key {key!r} (not in _flat_index)")
    group = _flat_index[key]
    _model[group][key] = copy.deepcopy(_baseline[group][key])


# --- Persistence ------------------------------------------------------------
def save(schema_path: str | pathlib.Path | None = None) -> None:
    """Atomically persist ``_raw`` (with ``_model`` embedded) to disk (D-03).

    Writes to ``{path}.tmp``, flushes and fsyncs, then ``os.replace`` to the
    target. ``os.replace`` is atomic on POSIX and on Windows NTFS when source
    and target are on the same volume (they are — both under ``assets/``).

    DOES NOT call :func:`bake_derived`. The caller (Phase 28 panel / CLI) is
    the only thing that decides when derived values get recomputed (D-10).
    """
    path = pathlib.Path(schema_path) if schema_path is not None else _schema_path
    if path is None:
        raise RuntimeError("tuning.save() called before load() bound a schema path")

    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(_raw, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


# --- Derived-value bake -----------------------------------------------------
def _euler_jump_peak_px(gravity: float, jump_force: float) -> float:
    """Simulate a jump with no variable-jump input; return peak height in px.

    Matches v1.3 hand-baked ``derived.jump.max_height_px``. Step
    ``vy += gravity`` each frame, stop when ``vy >= 0``, return the
    most-negative-y (highest) displacement as a positive number.
    """
    vy = jump_force
    y = 0.0
    peak = 0.0
    while vy < 0:
        y += vy
        vy += gravity
        if -y > peak:
            peak = -y
    return peak


def _euler_jump_airtime(gravity: float, jump_force: float, fall_mult: float) -> int:
    """Simulate a full jump (ascent + descent back to y=0); return frame count.

    Uses ``fall_mult`` after apex to match the game's asymmetric gravity.
    """
    vy = jump_force
    y = 0.0
    frames = 0
    # Ascent
    while vy < 0:
        y += vy
        vy += gravity
        frames += 1
    # Descent
    while y < 0:
        y += vy
        vy += gravity * fall_mult
        frames += 1
    return frames


def bake_derived() -> None:
    """Recompute ``_raw['derived']['jump']`` from ``tuning.*`` values (D-10/D-12).

    Deterministic. Only the numeric members of the ``jump`` block are
    recomputed — ``max_height_note``, ``max_width_note``, and the
    ``comfortable_*`` values are curation, not integration output, and are
    left untouched. ``derived.player``, ``derived.fall``, ``derived.clearance``,
    and ``derived.placement_rules`` are not touched at all (they are
    hand-authored curation that the converter reads but which Phase 24 does
    not compute).

    Never called from :func:`load`, :func:`set_value`, or :func:`save`.
    """
    movement = _model["movement"]
    tile = _model["tile"]

    gravity = movement["GRAVITY"]
    jump_force = movement["JUMP_FORCE"]
    max_walk_speed = movement["MAX_WALK_SPEED"]
    fall_mult = movement["FALLING_GRAVITY_MULTIPLIER"]
    tile_size = tile["TILE_SIZE"]

    peak_px = _euler_jump_peak_px(gravity, jump_force)
    airtime_frames = _euler_jump_airtime(gravity, jump_force, fall_mult)
    width_px_float = airtime_frames * max_walk_speed

    max_height_px = round(peak_px)
    max_height_tiles = max_height_px // tile_size
    max_width_px = round(width_px_float)
    max_width_tiles = max_width_px // tile_size

    jump_block = _raw.setdefault("derived", {}).setdefault("jump", {})
    jump_block["max_height_px"] = max_height_px
    jump_block["max_height_tiles"] = max_height_tiles
    jump_block["max_width_px"] = max_width_px
    jump_block["max_width_tiles"] = max_width_tiles


# --- PEP 562 attribute access -----------------------------------------------
def __getattr__(name: str):
    """Module-level ``__getattr__`` (PEP 562) for flat attribute access (D-13).

    Allows ``tuning.GRAVITY``, ``tuning.JUMP_FORCE``, etc. to resolve to the
    appropriate leaf in ``_model`` without any intermediate group reference.
    """
    if _model is None:
        raise RuntimeError("tuning.load() has not been called")
    if name in _flat_index:
        return _model[_flat_index[name]][name]
    raise AttributeError(f"module 'src.core.tuning' has no attribute {name!r}")


# --- Eager auto-load at import time -----------------------------------------
# The loader runs once on first import so ``from src.core.tuning import *``
# and ``tuning.GRAVITY`` both work without an explicit ``load()`` call.
# ``load()`` is idempotent, so downstream tests may still call it to reload
# after experimental mutations.
load()


# ===========================================================================
# Phase 31 ANIM-05 parallel anim loader
# ===========================================================================
# D-10: Second loader with its own namespace; MUST NOT touch _flat_index,
#       _model, _baseline, or __all__ (physics state is fully isolated).
# D-14: Fail fast on load with explicit ValueError messages citing path + field.
# Pitfall 6 fix (Open Question 4): parallel _anim_flat_index + routing API.
# ---------------------------------------------------------------------------
from types import SimpleNamespace

_anim_path: pathlib.Path | None = None
_anim_raw: dict | None = None
_anim_baseline: dict | None = None
_anim_flat_index: dict[str, tuple] = {}   # "ANIM_PLAYER_RUN_DURATION_0" -> (entity, clip_id, dur_index)
anim: SimpleNamespace | None = None

_DEFAULT_ANIM_SCHEMA = (
    pathlib.Path(__file__).resolve().parents[2] / "assets" / "anim-schema.json"
)

_ALLOWED_CLIP_FIELDS = {"frames", "durations", "loop", "events"}


def load_anim(schema_path: str | pathlib.Path | None = None) -> None:
    """Load anim-schema.json into tuning.anim namespace. Fail fast (D-14).

    Builds _anim_flat_index mapping ANIM_<ENTITY>_<CLIP>_DURATION_<i> flat
    keys to nested paths so panel sliders and presets can use the existing
    Slider widget + get_anim_baseline / set_anim_value routing.
    """
    global _anim_path, _anim_raw, _anim_baseline, _anim_flat_index, anim

    path = pathlib.Path(schema_path) if schema_path is not None else _DEFAULT_ANIM_SCHEMA
    _anim_path = path

    with open(path, encoding="utf-8") as f:
        _anim_raw = json.load(f)

    entities_ns: dict[str, SimpleNamespace] = {}
    new_flat_index: dict[str, tuple] = {}

    for entity_name, entity_data in _anim_raw.items():
        if not isinstance(entity_data, dict) or "clips" not in entity_data:
            raise ValueError(
                f"anim-schema: entity {entity_name!r} at {path} missing 'clips' dict"
            )
        clips_ns: dict[str, SimpleNamespace] = {}
        for clip_id, clip_spec in entity_data["clips"].items():
            if not isinstance(clip_spec, dict):
                raise ValueError(
                    f"anim-schema: {entity_name}.{clip_id} at {path} must be an object"
                )
            frames = clip_spec.get("frames")
            durations = clip_spec.get("durations")
            loop = clip_spec.get("loop", True)
            events = clip_spec.get("events", {})
            if not isinstance(frames, list) or not isinstance(durations, list):
                raise ValueError(
                    f"anim-schema: {entity_name}.{clip_id} at {path} missing frames/durations lists"
                )
            if len(frames) != len(durations):
                raise ValueError(
                    f"anim-schema: {entity_name}.{clip_id} at {path} frames/durations "
                    f"length mismatch ({len(frames)} vs {len(durations)})"
                )
            extra = set(clip_spec) - _ALLOWED_CLIP_FIELDS
            if extra:
                raise ValueError(
                    f"anim-schema: {entity_name}.{clip_id} at {path} unknown fields: {sorted(extra)}"
                )
            clips_ns[clip_id] = SimpleNamespace(
                frames=list(frames),
                durations=list(durations),
                loop=bool(loop),
                events=dict(events),
            )
            for i in range(len(durations)):
                flat = f"ANIM_{entity_name.upper()}_{clip_id.upper()}_DURATION_{i}"
                new_flat_index[flat] = (entity_name, clip_id, i)
        entities_ns[entity_name] = SimpleNamespace(clips=clips_ns)

    anim = SimpleNamespace(**entities_ns)
    _anim_flat_index = new_flat_index
    _anim_baseline = copy.deepcopy(_anim_raw)


def get_anim_baseline(key: str):
    """Return boot-time value of an anim flat key (D-04 parity for anim)."""
    if key not in _anim_flat_index:
        raise KeyError(f"unknown anim key {key!r} (not in _anim_flat_index)")
    entity, clip_id, i = _anim_flat_index[key]
    return _anim_baseline[entity]["clips"][clip_id]["durations"][i]


def get_anim_value(key: str):
    """Return current runtime value of an anim flat key."""
    if key not in _anim_flat_index:
        raise KeyError(f"unknown anim key {key!r} (not in _anim_flat_index)")
    entity, clip_id, i = _anim_flat_index[key]
    return getattr(anim, entity).clips[clip_id].durations[i]


def set_anim_value(key: str, value) -> None:
    """Mutate the live anim namespace duration at key -> value."""
    if key not in _anim_flat_index:
        raise KeyError(f"unknown anim key {key!r} (not in _anim_flat_index)")
    entity, clip_id, i = _anim_flat_index[key]
    getattr(anim, entity).clips[clip_id].durations[i] = value


# --- CLI entry point (D-11) -------------------------------------------------
if __name__ == "__main__":
    import sys

    load()
    if len(sys.argv) > 1 and sys.argv[1] == "bake":
        bake_derived()
        save()
        print(f"baked derived.* and saved to {_schema_path}")
    else:
        print("usage: python -m src.core.tuning bake")
