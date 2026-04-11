# Phase 24: Tuning Foundation (Schema Inversion) - Context

**Gathered:** 2026-04-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Flip the source-of-truth relationship between `physics-schema.json` and `src/core/constants.py`. After this phase:

- `physics-schema.json` is the source of truth for tuning values, restructured into `tuning.*` (raw inputs grouped by system) and `derived.*` (converter-facing computed values).
- `src/core/tuning.py` loads the schema at boot, exposes flat PEP 562 attribute access, and provides a mutation/save API for the future Phase 28 panel.
- `src/core/constants.py` is rewritten as a passthrough compat shim that re-exports `tuning.*` names so existing import-site call sites keep working.
- Game boots from the new schema and plays frame-for-frame identically to v1.3 (no behavior change).
- The pml-to-ldtk converter contract is updated in `CONVERTER-HANDOFF.md` to reflect the new layout.

**Out of scope (other phases):**
- Phase 25 — migrating the 12 entity/level files from import-site to use-site reads
- Phase 28 — the live-tuning panel UI itself (this phase only ships the API the panel will call)
- Phase 36 — the final preset bake before v2.0 ship
- Editing JSON in a text editor while the game runs (FND-04 — see Requirement Changes below)

</domain>

<requirement_changes>
## Requirement Changes (must update REQUIREMENTS.md before plan)

**FND-04 is dropped.** Original wording:

> Hot-reload works — external file edits (git pull, text editor save) are detected and applied within one frame via mtime check in game loop.

User confirmed they will not text-edit `physics-schema.json` directly — the Phase 28 panel is the only intended editing surface. The mtime watcher was a temporary demo mechanism for the gap between Phase 24 and Phase 28; without text-editor editing, it carries cost (Windows file locks, partial-write handling, malformed-JSON recovery, mid-frame I/O) for no gameplay benefit.

**Replacement requirement (FND-04, revised):**

> Mutations via `tuning.set_value()` are visible to subsequent reads in the same process (verified via unit test). File-watch hot-reload is not implemented — the live-tuning panel (Phase 28) is the only editing interface. The git-pull workflow is "restart the game."

The planner must apply this revision to `REQUIREMENTS.md` before execution begins, and adjust the Phase 24 success criteria in `ROADMAP.md` (success criterion #2 currently says "editing physics-schema.json in a text editor while the game is running causes the edited value to take effect within one frame without a restart" — replace with the test for set_value visibility).

</requirement_changes>

<decisions>
## Implementation Decisions

### Mutation & Persistence Model

- **D-01:** Internal in-memory model is the runtime source of truth; JSON is the persistence format. `tuning.py` holds two dicts: `_model` (live state) and `_baseline` (frozen snapshot taken at boot from the loaded JSON).
- **D-02:** `tuning.set_value(key, value)` mutates `_model` only. **No disk I/O.** Every call is O(1) memory.
- **D-03:** `tuning.save()` is the only function that writes to disk. Atomic write (write to `physics-schema.json.tmp`, fsync, rename). Phase 28's panel decides when to call it; Phase 24 ships **no autosave**, no journal, no quit-hook.
- **D-04:** `_baseline` is captured once at `tuning.load()` time and never mutated. `tuning.get_baseline(key)` exposes it for future A/B compare logic. `tuning.reset(key=None)` restores `_model[key]` from `_baseline` (or all keys when `key` is `None`).
- **D-05:** No baseline file on disk. The baseline is in-memory only; restart re-reads JSON and takes a fresh baseline. This is sufficient for Phase 28's A/B compare needs.

### Schema Layout (`physics-schema.json` v0.3.0)

- **D-06:** **Pure restructure.** Top-level keys become exactly: `$schema`, `title`, `description`, `version`, `updated`, `fps`, `tile_size`, `tuning`, `derived`. Existing top-level blocks (`player`, `jump`, `fall`, `clearance`, `placement_rules`) move INTO `derived.*`. The existing `source_constants` block is deleted — its values move into `tuning.*` with the rest of the constants.py raw values.
- **D-07:** This is a one-time breaking change for the external pml-to-ldtk converter. `CONVERTER-HANDOFF.md` must be updated in this phase with an old-path → new-path migration table for the converter team. Bump `physics-schema.json` version from `0.2.0` to `0.3.0`.
- **D-08:** `tuning.*` is grouped by system. The planner picks the exact group names but should mirror the comment-header sections of today's `constants.py` so the mapping stays obvious. Suggested groups: `display`, `hazards`, `movement`, `forgiving`, `wall`, `slime_follow`, `slime_juice`, `projectile`, `drill`, `health`, `dash`, `fusion`, `slime_ram`, `charge_shot`, `boost`, `gates`, `save`, `death`, `save_point`. Final list is the planner's call.
- **D-09:** `derived.*` mirrors the existing `player`, `jump`, `fall`, `clearance`, `placement_rules` blocks with no field renames. The converter team only has to learn "everything moved one level deeper under `derived.`" — field shapes are unchanged.

### Derived Values Lifecycle

- **D-10:** **Explicit bake only.** `tuning.bake_derived()` recomputes the `derived.*` block from `tuning.*` via Euler integration (jump max height/width, etc.). It is **never called automatically** — not on boot, not on `set_value()`, not on `save()`.
- **D-11:** Phase 24 ships `bake_derived()` and a manual invocation path (probably a CLI: `python -m src.core.tuning bake`). Phase 36's "preset bake + regression check" runs it before the v2.0 ship. Between Phase 24 and Phase 36, `derived.*` on disk may lag `tuning.*` and **that is acceptable** — the converter only matters at ship time, and gameplay reads `tuning.*` directly (after Phase 25), so in-game tweaks feel instant regardless of `derived.*` staleness.
- **D-12:** `bake_derived()` must be deterministic and produce values identical to today's hand-baked `derived.jump.max_height_tiles = 3`, etc., when run against v1.3 baseline `tuning.*` values. This is the FND-06 smoke test: bake against v1.3 → diff against current `physics-schema.json` derived blocks → must be zero diff (modulo the wrapper restructure).

### Namespace Shape (Python Access Pattern)

- **D-13:** **Flat aliases.** Python access is `tuning.GRAVITY`, `tuning.JUMP_FORCE`, etc. — names mirror today's `constants.py` exactly. PEP 562 `__getattr__` flattens the nested schema groups at attribute lookup time.
- **D-14:** `tuning.set_value("GRAVITY", 0.09)` takes a **flat key**. Internally the loader maintains a flat-key → group-name index built once at load time so the panel can ask `tuning.get_group("GRAVITY")` → `"movement"` for tab placement.
- **D-15:** **Name uniqueness invariant:** every leaf key under `tuning.*` must be globally unique across groups. Two groups cannot both contain a `MAX_SPEED`. The loader raises at boot if duplicates exist. This keeps the flat namespace unambiguous and lets Phase 25 do a mechanical rename without per-callsite group disambiguation.
- **D-16:** The compat shim in `constants.py` is a single line: `from src.core.tuning import *`, plus an `__all__` list maintained on the `tuning` side. (`tuning.py` defines `__all__` from the loaded flat-key set so the shim picks up new names automatically.)
- **D-17:** **Known limitation of the shim during Phase 24:** legacy import-site readers (`from src.core.constants import GRAVITY`) bind a local name at module-import time. They will NOT see runtime `set_value()` mutations until Phase 25 migrates them to use-site reads. This is expected and is the entire purpose of Phase 25 — Phase 24 only needs the imports to **work** (not crash) and return v1.3 baseline values at boot. Phase 24 acceptance does NOT require live mutation reaching legacy callers.

### Hot-Reload Robustness

- **D-18:** Resolved by FND-04 deletion (see Requirement Changes above). No file watcher, no mtime polling, no partial-write handling, no Windows file-lock retry. Deleted complexity is the right complexity.

### Claude's Discretion

- Exact group names under `tuning.*` (D-08) — planner picks, with the constraint that they mirror existing `constants.py` comment headers.
- The order of keys within each `tuning.*` group — planner picks; suggest preserving the order from `constants.py` for diff-friendliness.
- Implementation of atomic write in `save()` — planner picks (`os.replace` after temp file is the standard Python idiom).
- Whether `bake_derived()` lives in `tuning.py` or a separate `src/core/derive.py` module — planner picks based on file-size considerations.
- Loader caching strategy (lazy vs eager) — planner picks; eager is fine since the schema is small (~64 lines today).
- Test layout — planner picks. At minimum: load round-trip, set_value visibility, baseline reset, name-uniqueness violation raises, bake_derived determinism against v1.3 baseline, compat-shim import smoke test.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Schema & Converter Contract
- `assets/physics-schema.json` — current v0.2.0 schema (64 lines). The starting point for the v0.3.0 restructure.
- `CONVERTER-HANDOFF.md` — the contract document with the external pml-to-ldtk converter team. Must be updated in this phase to document the v0.3.0 layout change with an old-path → new-path table.

### Source of Raw Values
- `src/core/constants.py` — the 156-line constants file (~60 named constants in ~20 comment-header groups). Every named constant here must have a 1-to-1 entry under some `tuning.*` group in the new schema. Comment headers map to group names (D-08).

### Requirements
- `.planning/REQUIREMENTS.md` §Foundation (FND-01..06) — the locked acceptance criteria. **Note:** FND-04 needs revision per `<requirement_changes>` above.
- `.planning/ROADMAP.md` §Phase 24 — phase goal and success criteria. Success criterion #2 needs revision per `<requirement_changes>`.

### Codebase Maps
- `.planning/codebase/STRUCTURE.md`, `CONVENTIONS.md` — read for module placement conventions and import-style norms before adding `src/core/tuning.py`.

### Existing Callers (do NOT touch in Phase 24 — Phase 25's job)
The 12 files that import from `constants.py`:
- `src/entities/boss.py`, `slime.py`, `enemies.py`, `effects.py`, `player.py`, `save_point.py`, `items.py`, `projectile.py`
- `src/level/map.py`, `world.py`
- `src/core/save_manager.py`, `sprite_utils.py`

Phase 24 must keep all 12 of these working unchanged — verified by `python -c "import <each module>"` smoke test.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`assets/physics-schema.json`** — already exists with the converter-facing blocks (`player`, `jump`, `fall`, `clearance`, `placement_rules`). These move under `derived.*` unchanged in shape. Saves design work.
- **`source_constants` block** in current schema — already lists 6 raw values (GRAVITY, JUMP_FORCE, MAX_WALK_SPEED, MAX_FALL_SPEED, FALLING_GRAVITY_MULTIPLIER, TILE_SIZE) auto-mirrored from `constants.py`. Confirms the duplication problem this phase fixes; values become canonical under `tuning.*`.
- **Comment-header grouping in `constants.py`** — already partitions ~60 constants into ~20 logical groups (Movement, Slime Follow, Drill Dive, Charge Shot, Boost, etc.). These are the ready-made `tuning.*` group names (D-08).

### Established Patterns
- Schema-first: v1.2 already established that JSON schemas live in `assets/` and are the contract surface for external tools. Phase 24 extends this pattern to physics tuning.
- `src/core/` is the home for cross-cutting modules (`constants.py`, `save_manager.py`, `sprite_utils.py`). New `tuning.py` lives here.
- The codebase uses absolute imports (`from src.core.constants import X`). Compat shim must preserve this exact form.

### Integration Points
- **`tuning.py` import order** — the loader runs at module-import time. Must complete before any caller imports `constants.py` (since the shim re-exports from `tuning`). Python's import system handles this naturally as long as the shim's `from src.core.tuning import *` is the first statement in `constants.py`.
- **Boot sequence** — `tuning.load()` runs once at first import; `_baseline` is captured here. Subsequent imports get the cached module (Python's normal behavior). No game-loop integration needed for Phase 24.
- **Converter handoff** — `CONVERTER-HANDOFF.md` is the only deliverable for FND-06. The actual external converter is not in this repo and will be updated by its team using the handoff doc.

### Known Constraints
- Schema must remain valid JSON Schema 2020-12 (current `$schema` declaration) — restructure changes the shape but the meta-validation must still pass.
- The 12 legacy callers cannot be touched in Phase 24 (Phase 25's scope). The compat shim is the entire bridge.
- Frame-for-frame v1.3 parity is the boot acceptance test — any change in numerical values is a regression.

</code_context>

<specifics>
## Specific Ideas

- **Editing model the user described in their own words:** "the user is not live-editing the JSON. we can have an internal data model that links to the JSON so we can save to file when we need to." This single sentence reframed the entire phase from "file-watcher hot-reload" to "in-memory model with explicit save." It is the load-bearing constraint behind D-01 through D-05 and the FND-04 deletion.
- **The `tuning.GRAVITY` flat-access pattern** is chosen specifically to make Phase 25's call-site migration a 1-to-1 mechanical refactor (`from src.core.constants import GRAVITY` → `from src.core import tuning; ... tuning.GRAVITY`). Any other namespace shape would multiply Phase 25's effort.
- **Phase 24 ships no panel UI.** The mutation API exists and is unit-testable but is not exercised by gameplay until Phase 28. Phase 24's user-visible deliverable is essentially "the game still works exactly the same, but the schema and loader are in place."

</specifics>

<deferred>
## Deferred Ideas

- **File-watcher hot-reload** — explicitly killed (FND-04 deletion). If a future phase decides we want it back for some workflow we haven't anticipated, it can be added on top of the existing `tuning.py` API without restructuring.
- **Autosave / journal / save-on-quit hook** — Phase 28's call to make. Phase 24 deliberately ships no autosave so the persistence model stays minimal.
- **Baseline-as-disk-file** — kept in memory only (D-05). If Phase 28 finds in-memory baselines insufficient, it can add a sidecar file then.
- **Per-group attribute access (`tuning.movement.GRAVITY`)** — rejected in favor of flat access (D-13). Could be added later as a convenience layer over the flat namespace if desired, but adds rope.
- **Live-bake of `derived.*` on every set_value** — rejected as wasteful (D-10). Could be enabled with a config flag if some unforeseen workflow needs it.
- **Schema version negotiation** — the converter doesn't currently version-negotiate; CONVERTER-HANDOFF.md is the human-readable contract. If the converter team wants programmatic version checks, that's a future converter-side change.

</deferred>

---

*Phase: 24-tuning-foundation-schema-inversion*
*Context gathered: 2026-04-11*
