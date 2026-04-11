---
phase: 24
plan: 03
subsystem: tuning-loader
tags: [loader, python, pep-562, mutation-api, foundation]
dependency_graph:
  requires:
    - "24-02 (assets/physics-schema.json v0.3.0 with tuning.* + derived.*)"
  provides:
    - "src/core/tuning.py — single-file loader, mutation API, atomic save, PEP 562 flat access"
    - "Flat-key namespace (87 leaves) consumed by Plan 04's compat shim and Phase 25's call-site migration"
    - "bake_derived() CLI for Phase 36's ship bake"
  affects:
    - "src/core/tuning.py (new)"
tech_stack:
  added: []
  patterns:
    - "PEP 562 module __getattr__ for flat attribute access over a nested dict"
    - "Eager auto-load at import time (idempotent load())"
    - "Atomic JSON save via temp-file + fsync + os.replace"
    - "Frozen-deepcopy baseline captured once per load()"
    - "Flat-key -> group index with global uniqueness invariant (D-15)"
key_files:
  created:
    - "src/core/tuning.py"
  modified: []
decisions:
  - "Put bake_derived() inside tuning.py rather than a separate src/core/derive.py (single-file loader keeps Plan 04 shim / Plan 05 tests simple; file is ~300 lines, well under any split threshold)"
  - "Eager auto-load at import time (`load()` at module bottom) so Plan 04's one-line compat shim (`from src.core.tuning import *`) works without any explicit init dance"
  - "Reset(full) rebinds _raw['tuning'] AND the module-level _model pointer so subsequent save() serialises reset values and attribute reads see the restored state"
  - "Version check uses prefix match on '0.3' (not equality) so future 0.3.x bumps don't require loader edits; only major jumps to 0.4+ will fail loudly"
  - "bake_derived() only touches the four numeric jump keys; leaves max_height_note, max_width_note, comfortable_* and the player/fall/clearance/placement_rules blocks verbatim (per plan §interfaces spec)"
metrics:
  duration_seconds: 360
  completed: 2026-04-11
  tasks: 1
  files_changed: 1
requirements_completed:
  - FND-02
---

# Phase 24 Plan 03: Tuning Loader Summary

**One-liner:** Single-file PEP 562 loader (`src/core/tuning.py`, 297 lines) that reads `physics-schema.json` v0.3.x at import time, exposes all 87 flat leaves via module `__getattr__`, and ships the full mutation/baseline/reset/atomic-save/bake API the Phase 28 panel will call — with zero disk I/O outside `save()` and zero file-watcher machinery.

## What Changed

### src/core/tuning.py (Task 1) — new, 297 lines

**Module state** (all globals initialised to sentinels, populated by `load()`):
- `_schema_path: pathlib.Path | None` — bound during `load()` so `save()` knows where to write
- `_raw: dict | None` — the full deserialised JSON
- `_model: dict | None` — points at `_raw['tuning']` (the live mirror)
- `_baseline: dict | None` — frozen `copy.deepcopy(_model)` taken once per `load()` (D-04)
- `_flat_index: dict[str, str]` — `flat_key -> group_name`, built once per `load()`
- `__all__: list[str]` — `sorted(_flat_index.keys())`, exposed for `from src.core.tuning import *` (D-16)

**Default schema path** uses `pathlib.Path(__file__).resolve().parents[2] / "assets" / "physics-schema.json"` — climbs `src/core/tuning.py -> src/core -> src -> <repo-root>`. Import-time sentinel constant, not computed per call.

**Public API** — exactly the interfaces contract from the plan:

| Function | Behaviour |
| --- | --- |
| `load(schema_path=None)` | Reads JSON, version-checks (`0.3.x` prefix), binds `_model`, builds `_flat_index` with D-15 uniqueness enforcement, deepcopies `_baseline`, rewrites `__all__`. Idempotent. FileNotFoundError / JSONDecodeError propagate unswallowed (T-24-08). |
| `set_value(key, value)` | Mutates `_model[_flat_index[key]][key]`. KeyError on unknown key (T-24-10). No disk I/O, no type coercion (D-02). |
| `save(schema_path=None)` | Atomic write: `json.dump` to `{path}.tmp`, flush, fsync, `os.replace` to target (D-03 / T-24-09). Does NOT call `bake_derived` (D-10). |
| `reset(key=None)` | If `key is None`: rebinds `_raw['tuning']` to a fresh `deepcopy(_baseline)` and re-points module `_model` at the new object. Else: single-leaf restore. KeyError on unknown key. |
| `get_baseline(key)` | Returns `_baseline[_flat_index[key]][key]`. Never mutates. |
| `get_group(key)` | Returns `_flat_index[key]`. |
| `bake_derived()` | Re-computes `_raw['derived']['jump']`'s four numeric members (`max_height_px`, `max_height_tiles`, `max_width_px`, `max_width_tiles`) via Euler integration. Leaves `max_height_note`, `max_width_note`, `comfortable_*`, and the player/fall/clearance/placement_rules blocks verbatim. Never called automatically (T-24-12). |
| `__getattr__(name)` | PEP 562 module-level lookup. If `name in _flat_index`: return `_model[_flat_index[name]][name]`. Else AttributeError. Raises RuntimeError if `_model is None` (defensive). |

**Private helpers** — `_euler_jump_peak_px(gravity, jump_force)` and `_euler_jump_airtime(gravity, jump_force, fall_mult)` implement the frame-stepping simulation exactly per the plan's §interfaces spec (ascent until `vy >= 0`, then descent with asymmetric gravity multiplier until `y >= 0`).

**CLI entry point** — `python -m src.core.tuning bake` calls `load()`, `bake_derived()`, `save()` and prints the written path; `python -m src.core.tuning` (no arg) prints a usage hint.

**Auto-load at import time** — `load()` is called at the bottom of the module (after every `def` has been defined) so `from src.core.tuning import *` works without an explicit init dance. Plan 04's compat shim depends on this.

**Imports** — `json`, `os`, `pathlib`, `copy` only. **Deliberately does NOT import from `src.core.constants`** — `tuning.py` is self-contained so Plan 04 can rewrite `constants.py` as a one-line `from src.core.tuning import *` shim without a circular import.

## Tasks Completed

| Task | Name                                                                        | Commit  | Files                |
| ---- | --------------------------------------------------------------------------- | ------- | -------------------- |
| 1    | Write src/core/tuning.py (loader + mutation API + PEP 562 + CLI bake)       | 3b4f659 | src/core/tuning.py   |

## Verification

All plan acceptance criteria executed in-session:

```
test -f src/core/tuning.py                                                  OK
python -c "import src.core.tuning"                                          OK (auto-load succeeds)
from src.core import tuning; tuning.GRAVITY == 0.0875                       OK
tuning.JUMP_FORCE == -3.25                                                  OK
tuning.set_value('GRAVITY', 0.09); tuning.GRAVITY == 0.09                   OK
tuning.get_baseline('GRAVITY') == 0.0875 after mutation                     OK
tuning.reset('GRAVITY'); tuning.GRAVITY == 0.0875                           OK
tuning.reset(); full restore after multi-key mutation                       OK
tuning.get_group('GRAVITY') == 'movement'                                   OK
tuning.get_group('RAM_SPEED') == 'slime_ram'                                OK
'GRAVITY', 'JUMP_FORCE', 'RAM_INVINCIBLE' in tuning.__all__                 OK
len(tuning.__all__) == 87 (matches 24-02 schema leaf count)                 OK
tuning.set_value('NOT_A_KEY', 1) raises KeyError                            OK (T-24-10)
tuning.get_group('NOPE') / get_baseline('NOPE') / reset('NOPE') KeyError    OK
tuning.NOT_A_THING raises AttributeError                                    OK
tuning.bake_derived(); max_height_tiles == 3                                OK (FND-06)
tuning.bake_derived(); max_width_tiles == 5                                 OK (FND-06)
Duplicate-leaf synthetic schema raises "Duplicate tuning leaf ..."          OK (D-15)
grep "os.replace" src/core/tuning.py                                        OK (atomic save)
grep "def __getattr__" src/core/tuning.py                                   OK (PEP 562)
grep "Duplicate tuning leaf" src/core/tuning.py                             OK (D-15 message)
grep -E "mtime|watchdog|FileSystemEvent" src/core/tuning.py                 no matches (D-18)
python -m src.core.tuning bake (CLI round-trip)                             OK (schema restored)
src/core/constants.py still importable alongside tuning.py                  OK (no circular import)
```

**bake determinism against v1.3 baseline (FND-06 smoke test):**

With `GRAVITY=0.0875`, `JUMP_FORCE=-3.25`, `MAX_WALK_SPEED=1.25`, `FALLING_GRAVITY_MULTIPLIER=1.8`, `TILE_SIZE=16`:

| Derived key | Computed | Schema-authored | Match? |
| --- | --- | --- | --- |
| `max_height_px` | **62** (peak 61.9875) | 62 | yes |
| `max_height_tiles` | **3** (62 // 16) | 3 | yes |
| `max_width_px` | **84** (airtime 67f × 1.25) | **89** | **drift** |
| `max_width_tiles` | **5** (84 // 16) | 5 | yes (both floor to 5) |

The `max_width_tiles` acceptance check (`==5`) passes because `84//16==5` and `89//16==5` both floor to the same tile count. This is why the plan's explicit acceptance line (`max_height_tiles==3 and max_width_tiles==5`) is satisfied even though the underlying `max_width_px` drifts by 5 pixels.

**See "Deviations from Plan" below for the drift report required by the plan's §interfaces block.**

## Deviations from Plan

### Reported Drift (not auto-fixed)

**[Drift Report] bake_derived().max_width_px computes 84, schema authored 89**

- **Found during:** Task 1 verification
- **Computed value:** `round(67 frames * 1.25 px/frame) = round(83.75) = 84`
  - ascent: 37 frames (peak at y = -61.9875 px when vy first becomes >= 0)
  - descent: 30 frames under 1.8x gravity to reach y >= 0
  - total airtime: 67 frames at MAX_WALK_SPEED 1.25 → 83.75 px
- **Schema-authored value:** `max_width_px = 89` (from Wave 2's byte-identical lift-and-shift of the v0.2.0 `jump` block, which Plan 01 research notes tied to v1.3's hand-baked numbers)
- **Delta:** 89 - 84 = 5 px (0.31 tiles at TILE_SIZE 16)
- **Effect on acceptance test:** None. Both `84 // 16` and `89 // 16` equal 5, so `max_width_tiles == 5` passes either way. FND-06 smoke-test line in the plan passes literally.
- **Per plan's §interfaces instructions:** "If the numbers don't land on 62/89 exactly, the executor MUST NOT tweak the constants — they MUST report the drift in the task output so the planner can re-examine the v1.3-derivation formula."
- **What I did NOT do:** I did NOT edit GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, FALLING_GRAVITY_MULTIPLIER, or TILE_SIZE to coerce airtime*walk to 89. I did NOT edit the Euler helpers. I did NOT edit the schema's authored `max_width_px = 89`. The loader is implemented exactly per the plan's §interfaces code blocks.
- **Recommended follow-up (for the planner):** The delta is mechanical, not random — 89 suggests the original v1.3 formula either (a) used a slightly different Euler stepping convention (e.g. recording airtime *until y > 0* rather than *until y >= 0*, which adds ~4 frames), or (b) multiplied by a slightly higher effective horizontal speed (e.g. including the first frame of acceleration from rest), or (c) rounded a different intermediate value. The correct fix is a Plan 05 investigation task, not a Wave 3 loader tweak. Phase 36's "preset bake + regression check" is the natural place to reconcile the authored value against the canonical bake formula.

**Rule classification:** This is a **Rule 4 (architectural) observation**, not a Rule 1/2/3 auto-fix. The choice between "fix the formula", "fix the schema value", or "redefine which one is the ground truth" is a plan-level question that the planner owns. Per the plan's own explicit instruction I reported it here instead of changing anything.

### Auto-fixed Issues

**[Rule 3 - Blocker] Doc-string forbidden-substring collision**

- **Found during:** Task 1 verification
- **Issue:** The initial draft of `tuning.py` had a D-18 doc-string listing the things the loader *doesn't* do: "No mtime polling, no watchdog, ...". The plan's acceptance grep (`grep -E "mtime|watchdog|FileSystemEvent"`) is a substring check, not a semantic check, so it flagged the doc-string mentions as a failure.
- **Fix:** Rewrote the doc-string to describe the same absent machinery without using those literal identifiers ("No modification-time polling, no third-party file-system-event library"). Intent preserved, grep now returns no matches.
- **Files modified:** src/core/tuning.py (one doc-string paragraph)
- **Commit:** 3b4f659 (folded into the single Task 1 commit before push)

No other auto-fixes. No Rule 1 bugs, no Rule 2 missing critical functionality (everything was in the plan), no Rule 4 checkpoints (the drift above is reported, not escalated — the plan explicitly told me to report-and-continue).

## Auth Gates Hit

None.

## Deferred Issues

None.

## Known Stubs

None. The loader is complete API, not a placeholder. Plan 04 will add the one-line `constants.py` compat shim on top of this module. Plan 05 will add the unit tests.

## Threat Flags

None introduced. All threat-model mitigations from the plan's `<threat_model>` are implemented:

- **T-24-08** (malformed JSON DoS) — `FileNotFoundError` / `json.JSONDecodeError` propagate unswallowed; explicit version-prefix check catches stale v0.2.0 schemas with a clear error.
- **T-24-09** (save atomicity) — temp-file + fsync + `os.replace`.
- **T-24-10** (key injection) — `_flat_index` gate in `set_value`.
- **T-24-11** (duplicate leaf non-determinism) — ValueError at load, before any read.
- **T-24-12** (derived-bake EoP) — `bake_derived` only runs from the explicit CLI; neither `load`, `set_value`, nor `save` calls it.
- **T-24-13** (info disclosure) — accepted per the plan; no secrets in the schema.

## Self-Check: PASSED

- `src/core/tuning.py` — present (297 lines), parses, imports cleanly, PEP 562 `__getattr__` present, `os.replace` present, "Duplicate tuning leaf" message present, zero matches for `mtime|watchdog|FileSystemEvent`
- Commit `3b4f659` — found in `git log` (`feat(24-03): add src/core/tuning.py loader with flat PEP 562 access`)
- `.planning/phases/24-tuning-foundation-schema-inversion/24-03-tuning-loader-SUMMARY.md` — this file, present
- Worktree base rebased to `2f4187c` (per worktree_branch_check at start of session) before any edits — verified via `git merge-base`
- No unintended file modifications: `git status --short` after the Task 1 commit shows only this new SUMMARY as untracked; `assets/physics-schema.json` was temporarily written by the CLI round-trip test and restored from a pre-test backup before the final git state
