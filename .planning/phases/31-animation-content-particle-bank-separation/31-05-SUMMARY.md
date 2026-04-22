---
phase: 31
plan: 05
status: complete
completed: 2026-04-22
tuning_anim_tests: 16
new_test_anim_tests: 4
---

# Plan 31-05 SUMMARY — ANIM-05 schema + loader + panel + presets

Clip data migrated from Python to JSON; parallel tuning namespace with
fail-fast validation and flat-key routing; panel ANIM tab with live
duration sliders + Reload button; preset save/load routes ANIM_ keys
through the anim API (Pitfall 6 fix at source).

## assets/anim-schema.json

Nested entity -> clips -> {frames, durations, loop, events} shape (D-08).
Seeded verbatim from Phase 31 Plan 02 PLAYER_CLIPS:

| Clip | Frames | Durations | Loop |
|------|--------|-----------|------|
| idle | [0] | [1] | true |
| run | [16, 32] | [6, 6] | true |
| jump | [32] | [1] | true |
| jump_stationary | [96] | [1] | true |
| jump_running | [112] | [1] | true |
| jump_crouch | [80] | [2] | false |
| land_squash | [48, 0] | [3, 1] | false |
| turn_skid | [64] | [3] | false |
| drill_spin | [128, 144, 160, 176] | [2, 2, 2, 2] | true |

**Total anim duration flat keys:** 13 (1+2+1+1+1+1+2+1+4).

## tuning.py additions (parallel to physics loader, no cross-contamination)

```python
def load_anim(schema_path=None) -> None: ...
def get_anim_baseline(key: str): ...    # boot-time value lookup (D-04 parity)
def get_anim_value(key: str): ...       # current runtime value
def set_anim_value(key: str, value) -> None: ...  # mutate live namespace

_anim_flat_index: dict[str, tuple] = {}  # "ANIM_PLAYER_RUN_DURATION_0" -> (entity, clip_id, i)
_anim_baseline:   dict | None = None     # deepcopy of raw JSON
anim:             SimpleNamespace | None = None  # tuning.anim.player.clips['run']
```

**Flat-key naming:** `ANIM_<ENTITY>_<CLIP>_DURATION_<i>` — e.g.
`ANIM_PLAYER_RUN_DURATION_0`, `ANIM_PLAYER_DRILL_SPIN_DURATION_3`.

**D-14 fail-fast validation (6 error modes):**
1. Missing 'clips' dict per entity
2. Non-object clip spec
3. Missing frames/durations lists
4. Length mismatch between frames and durations
5. Unknown fields (anything outside {frames, durations, loop, events})
6. Non-dict entity data

**D-10 isolation:** `load_anim()` never touches `_flat_index`, `_model`,
`_baseline`, or `__all__`. Physics and anim namespaces are fully parallel.

## build_player_fsm (rewritten)

```python
def build_player_fsm() -> AnimFSM:
    from src.core import tuning
    if tuning.anim is None:
        tuning.load_anim()
    clips: dict[str, AnimClip] = {}
    for clip_id, spec in tuning.anim.player.clips.items():
        clips[clip_id] = AnimClip(
            frames=list(spec.frames),
            durations=list(spec.durations),
            loop=spec.loop,
            events=dict(spec.events),
        )
    return AnimFSM(rules=PLAYER_RULES, clips=clips)
```

**Rules stay in Python** per D-05; only clip DATA moves to JSON.
AnimClip is frozen, so reload rebuilds the entire FSM rather than
mutating the existing one.

## Panel ANIM Tab

**Location:** `src/ui/panel.py` TAB_DEFS gains a 5th entry
`("Anim", {_ANIM_TAB_SENTINEL: None})`.

**Widget:** `AnimSlider(Slider)` overrides the 4 routing hooks:
- `_get_baseline` -> `tuning.get_anim_baseline(key)`
- `_get_current` -> `tuning.get_anim_value(key)`
- `_set_value(v)` -> `tuning.set_anim_value(key, v)`
- `_reset` -> `tuning.set_anim_value(key, tuning.get_anim_baseline(key))`

**Slider refactor** (widgets.py): the base `Slider` class now uses
`self._get_baseline / _get_current / _set_value / _reset` hooks instead
of direct `tuning.*` calls. Existing physics behaviour unchanged because
the default hooks delegate to `tuning.get_baseline / getattr(tuning,k) /
tuning.set_value / tuning.reset`.

**_init_panel branch:** when the Anim-tab sentinel is hit, the loop
reads `tuning._anim_flat_index` instead of `_flat_index` and wraps 13
`AnimSlider`s in a single `CollapsibleGroup("player_clips", expanded=True)`.

**Reload button:**
- `reload_anim_schema(player)` — re-runs `tuning.load_anim()`, rebinds
  `player._anim = build_player_fsm()`, marks panel as uninitialised so
  sliders rebuild on next draw
- `_handle_reload_anim_click(player)` — hit-tests an 80px button left of
  the Save button; only active when the Anim tab is selected
- `panel.update()` now accepts an optional `player` arg; main.py's call
  site at line 549 passes `self.player`

## presets.py Pitfall 6 fix

```python
def _anim_keys():
    return list(tuning._anim_flat_index.keys())

def save_preset(slot, alias=""):
    ...
    for key in _feel_keys():     # physics
        values[key] = getattr(tuning, key)
    for key in _anim_keys():     # NEW: anim duration flat keys
        values[key] = tuning.get_anim_value(key)
    ...

def load_preset(slot):
    ...
    for key, val in preset["values"].items():
        if key.startswith("ANIM_"):
            try:
                tuning.set_anim_value(key, val)  # Pitfall 6 fix
            except KeyError:
                pass
        else:
            try:
                tuning.set_value(key, val)
            except KeyError:
                pass
    ...
```

Before the fix, `tuning.set_value("ANIM_PLAYER_RUN_DURATION_0", v)` would
raise `KeyError` (anim key not in physics `_flat_index`); the existing
try/except silently ate that, so anim preset data never applied.

## Test Count

- `tests/test_tuning_anim.py` NEW — 16 tests (13 loader/routing + 3
  Pitfall 6 preset)
- `tests/test_anim.py` — 4 new tests (2 build_player_fsm + 2 panel/reload)
- Pre-existing 9 unrelated tuning/physics/ldtk failures unchanged

Total passing tests across Phase 31 plans: 462 -> 482 (+20). Full suite
after Plan 05: 482 pass / 9 fail / 3 skip.

## Commits

- `3f8a21a` test(31-05): RED baseline for anim schema + loader + panel + presets
- `68c26b1` feat(31-05): anim schema + loader + build_player_fsm + panel + presets

## Self-Check

- [x] `assets/anim-schema.json` exists with all 9 Phase 31 clips
- [x] `load_anim + 3 routing fns + _anim_flat_index + anim namespace` all live in tuning.py
- [x] 6 fail-fast validation branches unit-tested
- [x] D-10 isolation: physics `_flat_index` untouched by anim load (test verified)
- [x] `build_player_fsm` reads from `tuning.anim.player.clips` (2 grep refs)
- [x] `main.py` calls `tuning.load_anim()` exactly once in `Game.__init__`
- [x] Panel TAB_DEFS has 5 entries including `Anim`
- [x] `AnimSlider` overrides 4 routing hooks (Slider refactor keeps physics behaviour unchanged)
- [x] `reload_anim_schema(player)` + `_handle_reload_anim_click(player)` both present
- [x] `panel.update(player=None)` accepts optional player; main.py call site updated
- [x] `presets.save_preset` iterates `_anim_keys()` alongside `_feel_keys()`
- [x] `presets.load_preset` branches on `ANIM_` prefix and calls `set_anim_value`
- [x] All Phase 31 anim/tuning/panel tests pass (49 in test_anim.py + 16 in test_tuning_anim.py)
- [x] Pre-existing 9 failures unchanged (tuning/physics/ldtk drift, unrelated to Phase 31)

Self-Check: PASSED
