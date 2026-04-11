---
phase: 24-tuning-foundation-schema-inversion
plan: 03
type: execute
wave: 2
depends_on: [24-01]
files_modified:
  - src/core/tuning.py
autonomous: true
requirements:
  - FND-02
tags: [loader, python, pep-562, mutation-api]
must_haves:
  truths:
    - "tuning.load() reads assets/physics-schema.json and populates _model + _baseline"
    - "tuning.GRAVITY returns 0.0875 via PEP 562 __getattr__"
    - "tuning.set_value('GRAVITY', 0.09) mutates _model; subsequent tuning.GRAVITY reads return 0.09"
    - "tuning.get_baseline('GRAVITY') always returns 0.0875 regardless of set_value calls"
    - "tuning.reset() restores all _model keys from _baseline"
    - "tuning.save() writes via atomic os.replace (temp file + rename) — no disk write elsewhere"
    - "tuning.bake_derived() recomputes derived.* from tuning.* values deterministically"
    - "Duplicate flat-key leaves across groups cause tuning.load() to raise at boot"
    - "tuning.get_group('GRAVITY') returns 'movement'"
    - "tuning.__all__ is derived from the loaded flat-key set"
  artifacts:
    - path: "src/core/tuning.py"
      provides: "Schema loader + mutation API + PEP 562 flat attribute access"
      exports: ["load", "set_value", "save", "reset", "get_baseline", "get_group", "bake_derived", "__getattr__", "__all__"]
  key_links:
    - from: "src/core/tuning.py __getattr__"
      to: "assets/physics-schema.json tuning.* groups"
      via: "flat-key → group index built once at load time"
      pattern: "_flat_index"
    - from: "src/core/tuning.py save()"
      to: "assets/physics-schema.json"
      via: "os.replace atomic rename after fsync"
      pattern: "os\\.replace"
---

<objective>
Write `src/core/tuning.py`, the single loader module that reads the v0.3.0 schema at boot, holds `_model` / `_baseline` dicts, exposes flat PEP 562 attribute access (`tuning.GRAVITY`), and provides the mutation/persistence API the Phase 28 panel will call.

Purpose: This is the heart of FND-02. After this plan, anyone can `from src.core import tuning` and read `tuning.GRAVITY` — the file backs the compat shim Plan 04 builds and the tests Plan 05 writes.

Output: `src/core/tuning.py` with load/set_value/save/reset/get_baseline/get_group/bake_derived and a module-level `__getattr__`, plus a `python -m src.core.tuning bake` CLI entry point.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md
@assets/physics-schema.json
@src/core/constants.py
@.planning/codebase/CONVENTIONS.md

<interfaces>
<!-- Public API. Downstream plans (04 shim, 05 tests, Phase 25 call-site migration, Phase 28 panel) import from here. -->

Module: src.core.tuning
Location: src/core/tuning.py

State (module globals, managed only through the functions below):
  _schema_path : pathlib.Path   # assets/physics-schema.json by default; set at load() time
  _raw         : dict           # the full loaded JSON (mutable)
  _model       : dict           # raw["tuning"] (the live mutable mirror) — flat-key writes route through here
  _baseline    : dict           # frozen deepcopy of _model taken at load() time, never mutated
  _flat_index  : dict[str, str] # flat_key → group_name, built once at load()
  __all__      : list[str]      # derived from _flat_index.keys(); used by `from src.core.tuning import *`

Public functions:

  def load(schema_path: str | pathlib.Path | None = None) -> None:
      """Idempotent. Reads schema from disk, rebuilds _model/_baseline/_flat_index/__all__.
      Raises ValueError on duplicate flat keys (D-15). Raises FileNotFoundError / json.JSONDecodeError
      on malformed input — DO NOT swallow these; a malformed schema must fail loudly so the game
      cannot silently start with zeros."""

  def set_value(key: str, value) -> None:
      """Mutates _model[group][key] where group = _flat_index[key].
      Raises KeyError if key is not in _flat_index (prevents arbitrary key injection).
      No type coercion — the panel is responsible for passing the right type.
      No disk I/O. O(1)."""

  def save(schema_path: str | pathlib.Path | None = None) -> None:
      """Atomic write. Serializes _raw (with _model embedded under _raw['tuning']) to
      `{schema_path}.tmp`, fsyncs it, then os.replace() to the target path.
      DOES NOT call bake_derived(). Phase 28 chooses when to persist."""

  def reset(key: str | None = None) -> None:
      """If key is None, restores ALL of _model from _baseline (deepcopy).
      If key is given, restores just that one flat leaf. Raises KeyError on unknown key."""

  def get_baseline(key: str):
      """Returns _baseline[group][key] — the boot-time value. Never mutates."""

  def get_group(key: str) -> str:
      """Returns the group name for a flat key, via _flat_index. Used by the panel for tab placement."""

  def bake_derived() -> None:
      """Recomputes _raw['derived'] from the current _model via Euler integration. Deterministic.
      Matches v1.3 hand-baked values when run against the baseline _model.
      Implementation is below under 'bake_derived behavior spec'.
      NEVER called automatically — only from save-time panel flows or the CLI."""

  def __getattr__(name: str):
      """PEP 562 module __getattr__. If name is in _flat_index, return _model[group][name].
      Otherwise raise AttributeError(f'module src.core.tuning has no attribute {name!r}').
      This is what makes `from src.core.tuning import *` and `tuning.GRAVITY` both work."""

bake_derived behavior spec (D-10, D-12):
  Inputs: tuning.movement.GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, MAX_FALL_SPEED, FALLING_GRAVITY_MULTIPLIER,
          tuning.tile.TILE_SIZE
  Outputs (written into _raw['derived']):
    derived.jump.max_height_px     = round(euler_jump_peak_px(GRAVITY, JUMP_FORCE))
    derived.jump.max_height_tiles  = max_height_px // TILE_SIZE       (integer floor)
    derived.jump.max_width_px      = round(euler_jump_airtime(GRAVITY, JUMP_FORCE, FALLING_GRAVITY_MULTIPLIER) * MAX_WALK_SPEED)
    derived.jump.max_width_tiles   = max_width_px // TILE_SIZE        (integer floor)
    derived.player.*, derived.fall.*, derived.clearance.*, derived.placement_rules.* are left UNCHANGED —
      Phase 24 only rebakes the jump block (the only block whose numeric members are algorithmically
      derived from tuning.* rather than hand-authored). The player/fall/clearance/placement_rules blocks
      are curation, not computation; they live in derived.* because the converter reads them, not because
      they are computed. This is the minimal deterministic bake that still satisfies FND-06's smoke
      test against v1.3 (derived.jump.max_height_tiles == 3 when run against v1.3 baseline values).
    derived.jump.comfortable_height_tiles and comfortable_width_tiles — NOT recomputed (they are authored
      curation, not integration output). Leave them unchanged across bakes.
    The "max_height_note" and "max_width_note" strings must be preserved unchanged (don't overwrite them).

  Euler integration implementation (matches v1.3 behavior; if any drift, the FND-06 smoke test in Plan 05 fails):

    def _euler_jump_peak_px(gravity: float, jump_force: float) -> float:
        """Simulate a jump with no input, step velocity += gravity each frame, stop when vy >= 0.
        Return the maximum (most-negative-y, most-up) displacement reached, in pixels, as positive number."""
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
        """Simulate a full jump including fall back to y=0; count frames. Uses fall_mult after apex."""
        vy = jump_force
        y = 0.0
        frames = 0
        # ascent
        while vy < 0:
            y += vy
            vy += gravity
            frames += 1
        # descent
        while y < 0:
            y += vy
            vy += gravity * fall_mult
            frames += 1
        return frames

  With v1.3 baseline (GRAVITY=0.0875, JUMP_FORCE=-3.25, MAX_WALK_SPEED=1.25, FALLING_GRAVITY_MULTIPLIER=1.8, TILE_SIZE=16):
    peak ≈ 62.05 px → max_height_px = 62 → max_height_tiles = 3  (matches schema D-12)
    airtime_frames * 1.25 ≈ 89 px → max_width_px = 89 → max_width_tiles = 5  (matches schema)

  If the numbers don't land on 62/89 exactly, the executor MUST NOT tweak the constants — they MUST
  report the drift in the task output so the planner can re-examine the v1.3-derivation formula. The
  current schema values 62/89 are the ground truth per D-12.

Atomic save idiom (D-03):

    def save(schema_path=None):
        path = pathlib.Path(schema_path or _schema_path)
        tmp = path.with_suffix(path.suffix + '.tmp')
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(_raw, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

Duplicate-key raise (D-15):

    During load(), walk _raw['tuning'].items() and for each (group, group_dict) accumulate leaf keys.
    If any leaf appears in two groups:
        raise ValueError(f"Duplicate tuning leaf {name!r} in groups {first_group!r} and {second_group!r}")

Key-not-registered raise (security — prevents arbitrary key injection via the panel):

    def set_value(key, value):
        if key not in _flat_index:
            raise KeyError(f"unknown tuning key {key!r} (not in _flat_index)")
        _model[_flat_index[key]][key] = value

CLI entry point (D-11):

    if __name__ == '__main__':
        import sys
        load()
        if len(sys.argv) > 1 and sys.argv[1] == 'bake':
            bake_derived()
            save()
            print(f"baked derived.* and saved to {_schema_path}")
        else:
            print("usage: python -m src.core.tuning bake")
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Write src/core/tuning.py (loader + mutation API + PEP 562)</name>
  <files>src/core/tuning.py</files>
  <read_first>
    - .planning/phases/24-tuning-foundation-schema-inversion/24-CONTEXT.md (§decisions D-01..D-18)
    - assets/physics-schema.json (so you know the exact keys the loader will encounter)
    - src/core/constants.py (to confirm the flat-name set you're exposing)
    - .planning/codebase/CONVENTIONS.md (snake_case, absolute imports, PEP 8)
  </read_first>
  <action>
    Create a new file `src/core/tuning.py`. Use the Write tool.

    Imports (top of file, in this order):
      import json
      import os
      import pathlib
      import copy

    Module state (module globals, initialised to sentinels):
      _schema_path: pathlib.Path | None = None
      _raw: dict | None = None
      _model: dict | None = None
      _baseline: dict | None = None
      _flat_index: dict[str, str] = {}
      __all__: list[str] = []

    Default schema path constant:
      _DEFAULT_SCHEMA = pathlib.Path(__file__).resolve().parents[2] / "assets" / "physics-schema.json"

    Implement load(schema_path=None) per the <interfaces> spec:
      - Sets _schema_path.
      - Reads _raw = json.load(open(_schema_path, encoding='utf-8')).
      - Asserts _raw['version'].startswith('0.3') — if not, raise ValueError with a clear message. This catches stale v0.2.0 schemas that were never migrated.
      - Binds _model = _raw['tuning'].
      - Builds _flat_index by walking _model.items(); on duplicate leaf names across groups, raise ValueError(f"Duplicate tuning leaf {name!r} in groups {first_group!r} and {second_group!r}") (D-15).
      - _baseline = copy.deepcopy(_model) — frozen reference snapshot (D-04).
      - __all__[:] = sorted(_flat_index.keys()) so `from src.core.tuning import *` picks up every leaf.
      - load() is idempotent: calling it twice just replays the load, taking a fresh baseline.

    Implement set_value(key, value) per spec (KeyError on unknown key, no disk I/O, D-02/D-14).

    Implement get_baseline(key) — returns _baseline[_flat_index[key]][key]. KeyError on unknown key. D-04.

    Implement get_group(key) — returns _flat_index[key]. KeyError on unknown key. D-14.

    Implement reset(key=None):
      - If key is None: _raw['tuning'] = copy.deepcopy(_baseline); then _model = _raw['tuning']; for group_name, group_dict in _model.items(): for k in group_dict: <no-op, the deepcopy already restored>. (The reassignment via _raw['tuning'] is necessary so later save() writes the reset values.) Also need to keep the module-level _model pointer pointing at the new _raw['tuning'] — use `global _model`.
      - If key is given: _model[_flat_index[key]][key] = copy.deepcopy(_baseline[_flat_index[key]][key])
      - KeyError on unknown key.

    Implement save(schema_path=None) — atomic write via temp file + fsync + os.replace per the <interfaces> idiom. Does NOT call bake_derived(). D-03.

    Implement bake_derived() per the spec in <interfaces>:
      - Private helpers _euler_jump_peak_px and _euler_jump_airtime as shown.
      - Reads the five movement constants and TILE_SIZE from _model.
      - Writes max_height_px / max_height_tiles / max_width_px / max_width_tiles into _raw['derived']['jump'].
      - Leaves derived.jump.max_height_note / max_width_note / comfortable_* strings and the rest of derived.* unchanged.
      - DO NOT call save() inside bake_derived() — the caller decides when to persist.

    Implement __getattr__(name) per PEP 562:
      - If _model is None: raise RuntimeError("tuning.load() has not been called") — this should never fire at runtime because Plan 04's compat shim imports this module and calls load() on first use, but the explicit error beats a mysterious None access.
      - If name in _flat_index: return _model[_flat_index[name]][name]
      - Else: raise AttributeError(f"module 'src.core.tuning' has no attribute {name!r}")

    Auto-load at module import time (so `from src.core.tuning import *` works without explicit load()):
      At the bottom of the module, AFTER defining everything, add:
          load()
      This is safe because load() is idempotent; Plan 05's tests can still call load() explicitly to reload after set_value mutations if needed.

    Add the `if __name__ == '__main__':` CLI block from the <interfaces> spec at the very bottom.

    Follow CONVENTIONS.md: snake_case function/variable names, absolute imports (`from src.core.tuning import ...`), PEP 8 spacing, module-level docstring at the top explaining this file is the Phase 24 source-of-truth loader.

    Do NOT:
    - import from src.core.constants (that file hasn't been rewritten yet; Plan 04 does that — tuning.py must be self-contained)
    - read or write any file other than assets/physics-schema.json
    - add autosave, journal, quit-hook, or mtime polling (D-03, D-18 — deliberately no file-watcher)
    - bake_derived() on load or set_value (D-10 — explicit bake only)
    - touch src/core/constants.py in this plan (Plan 04's job)
  </action>
  <verify>
    <automated>python -c "from src.core import tuning; assert tuning.GRAVITY==0.0875; assert tuning.JUMP_FORCE==-3.25; tuning.set_value('GRAVITY', 0.09); assert tuning.GRAVITY==0.09; assert tuning.get_baseline('GRAVITY')==0.0875; tuning.reset('GRAVITY'); assert tuning.GRAVITY==0.0875; assert tuning.get_group('GRAVITY')=='movement'; print('ok')"</automated>
  </verify>
  <acceptance_criteria>
    - `test -f src/core/tuning.py` exits 0
    - `python -c "import src.core.tuning"` exits 0 (no exceptions at import time — load() succeeds)
    - `python -c "from src.core import tuning; assert tuning.GRAVITY==0.0875"` exits 0
    - `python -c "from src.core import tuning; tuning.set_value('GRAVITY', 0.09); assert tuning.GRAVITY==0.09"` exits 0
    - `python -c "from src.core import tuning; tuning.set_value('GRAVITY', 0.09); assert tuning.get_baseline('GRAVITY')==0.0875"` exits 0
    - `python -c "from src.core import tuning; tuning.set_value('GRAVITY', 0.09); tuning.reset('GRAVITY'); assert tuning.GRAVITY==0.0875"` exits 0
    - `python -c "from src.core import tuning; assert tuning.get_group('GRAVITY')=='movement' and tuning.get_group('RAM_SPEED')=='slime_ram'"` exits 0
    - `python -c "from src.core import tuning; assert 'GRAVITY' in tuning.__all__ and 'JUMP_FORCE' in tuning.__all__ and 'RAM_INVINCIBLE' in tuning.__all__"` exits 0
    - `python -c "from src.core import tuning; \ntry: tuning.set_value('NOT_A_KEY', 1); raise SystemExit('should have raised')\nexcept KeyError: pass"` exits 0 (key-injection rejected)
    - `python -c "from src.core import tuning; tuning.bake_derived(); assert tuning._raw['derived']['jump']['max_height_tiles']==3 and tuning._raw['derived']['jump']['max_width_tiles']==5"` exits 0 (FND-06 determinism check)
    - `grep -q "os.replace" src/core/tuning.py` exits 0 (atomic save idiom present)
    - `grep -q "def __getattr__" src/core/tuning.py` exits 0 (PEP 562 present)
    - `grep -q "Duplicate tuning leaf" src/core/tuning.py` exits 0 (D-15 enforcement present)
    - `grep -E "mtime|watchdog|FileSystemEvent" src/core/tuning.py` returns NO matches (D-18: no file watcher)
  </acceptance_criteria>
  <done>src/core/tuning.py exists; `from src.core import tuning; tuning.GRAVITY` returns 0.0875; set_value/save/reset/get_baseline/get_group/bake_derived all callable; atomic save uses os.replace; PEP 562 __getattr__ implemented; load() raises on duplicate flat keys; no file-watcher code present; `python -m src.core.tuning bake` CLI runs without error.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| disk → loader | Malformed or corrupt physics-schema.json crossing into process memory |
| panel API → loader | set_value() accepts caller-provided key strings |
| loader → disk | save() writes persistent state |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-24-08 | Denial of Service | tuning.load() vs malformed JSON | mitigate | load() does NOT swallow FileNotFoundError or json.JSONDecodeError — the game fails loudly at import time instead of silently running with {} and zero-valued constants. Version check (0.3.x) also catches stale schemas. |
| T-24-09 | Tampering | tuning.save() atomicity | mitigate | Temp file + fsync + os.replace prevents torn writes. A crash mid-save leaves the original file intact because os.replace is atomic on POSIX and on Windows NTFS when source and target are on the same volume (which they are — both under assets/). |
| T-24-10 | Tampering | set_value arbitrary-key injection | mitigate | D-15 enforces a pre-registered flat-key index; set_value raises KeyError on any key not in _flat_index. Panel cannot create new schema keys at runtime. |
| T-24-11 | Tampering | duplicate flat keys → non-deterministic lookup | mitigate | load() walks _raw['tuning'] and raises ValueError if any leaf appears in two groups. Fails at boot, before _flat_index is ever used for a read. |
| T-24-12 | Elevation of Privilege | bake_derived() auto-running | mitigate | bake_derived() is NEVER called from load() or set_value() or save(). Only the explicit CLI and Phase 36's shipping bake invoke it. Prevents a panel slider drag from silently rewriting the converter contract. |
| T-24-13 | Information Disclosure | schema content | accept | Schema holds tuning values only, no secrets |
</threat_model>

<verification>
- `python -c "from src.core import tuning"` succeeds with no stderr
- set_value round-trip works (Plan 05 formalises this as a unit test)
- bake_derived is deterministic against v1.3 baseline (Plan 05 tests this)
- os.replace appears in tuning.py (atomic save verified by grep)
- No file-watcher primitives (watchdog/mtime/FileSystemEvent) appear in tuning.py
</verification>

<success_criteria>
- Module loads the v0.3.0 schema at import time
- Flat attribute access works for every leaf in constants.py's scope
- set_value / save / reset / get_baseline / get_group / bake_derived all behave per spec
- Name-uniqueness invariant raises at load time if violated
- bake_derived produces v1.3-identical values for max_height_tiles (3) and max_width_tiles (5)
- No disk I/O outside save(); no file watcher; no autosave
</success_criteria>

<output>
After completion, create `.planning/phases/24-tuning-foundation-schema-inversion/24-03-SUMMARY.md`
</output>
