---
phase: 32-fusion-manager-protocol-refactor
plan: 02
subsystem: fusion
tags: [fusion, refactor, protocol, package, typing-protocol, dataclass, runtime-checkable, wave-1]

# Dependency graph
requires:
  - phase: 30-fusion-lifecycle-design-doc
    provides: D-09 FusionAbility hook surface (locked in FUSION-DESIGN.md @ 9047b590)
  - phase: 31.5-cut-ability-code-strip
    provides: clean post-strip player.py / slime.py / physics-schema.json baseline
provides:
  - src/fusion/ package marker
  - src/fusion/protocol.FusionAbility (typing.Protocol, @runtime_checkable, 5 methods + 2 class attrs)
  - src/fusion/protocol.TickResult (frozen+slots dataclass, 4 fields with defaults)
  - tests/test_fusion_protocol.py — 11 contract tests freezing the D-09 surface
affects:
  - 32-03 (FusionManager / ChargeController scaffolding consumes Protocol)
  - 32-04 (FusionManager construction-time isinstance validation against FusionAbility)
  - 32-05 (DrillDive + Pogo implement FusionAbility structurally; return TickResult from on_tick)
  - 32-06 (wiring + integration; src/fusion package surface complete after Plans 04+05 ship)

# Tech tracking
tech-stack:
  added:
    - typing.Protocol (first use in this codebase per PATTERNS § "No Analog Found")
    - typing.runtime_checkable (enables FusionManager construction-time isinstance check)
  patterns:
    - "Frozen+slots dataclass for value-object intent return (TickResult mirrors src/anim/anim_clip.py)"
    - "Protocol-based structural typing for ability interface (D-09; replaces abc.ABC alternative)"
    - "Conservative __init__.py re-export — Plans 04+05 will Edit to append their classes"
    - "Module docstring cites phase + decision IDs (D-09/D-10/D-11/D-12) per PATTERNS § Module Docstring"

key-files:
  created:
    - src/fusion/__init__.py
    - src/fusion/protocol.py
    - tests/test_fusion_protocol.py
    - .planning/phases/32-fusion-manager-protocol-refactor/deferred-items.md
  modified: []

key-decisions:
  - "@runtime_checkable applied to FusionAbility (RESEARCH § Pattern 2 recommendation; cheap; enables Plan 04 isinstance guard)"
  - "TickResult uses frozen+slots dataclass (RESEARCH § Pattern 1 — matches src/anim/anim_clip.py precedent)"
  - "Conservative __init__.py: only protocol re-export — Plans 04 and 05 will Edit to append their classes (avoids dead try/except blocks during Wave 1)"
  - "TickResult.exit_reason typed as Optional[str] with documented values 'solid_landing' | 'juice_empty' | None (D-10 + RESEARCH § Pattern 1)"

patterns-established:
  - "typing.Protocol for cross-module ability/interface contracts (FIRST in codebase)"
  - "Phase 32 fusion subsystem package layout — src/fusion/{protocol,manager,charge_controller,drill_dive,pogo}.py"
  - "Per-D-09 method docstrings cite the relevant decision number for traceability"

requirements-completed: [FUS-04]

# Metrics
duration: 22min
completed: 2026-04-26
---

# Phase 32 Plan 02: Fusion Protocol Package Summary

**`src/fusion/` package keystone — FusionAbility typing.Protocol (5-method D-09 surface, @runtime_checkable) and TickResult frozen+slots dataclass land as the FIXED contract that Plans 04 (FusionManager) and 05 (DrillDive, Pogo) build against.**

## Performance

- **Duration:** ~22 min
- **Started:** 2026-04-26T12:13:30Z (approx. — plan invocation)
- **Completed:** 2026-04-26T12:34:31Z
- **Tasks:** 1 (TDD: RED + GREEN; no REFACTOR needed)
- **Files created:** 4 (2 source, 1 test, 1 docs)
- **Files modified:** 0
- **Tests added:** 11 (all passing)

## Accomplishments

- **`src/fusion/` package exists** with `__init__.py` (`from src.fusion.protocol import FusionAbility, TickResult` works) and `protocol.py` (the canonical D-09 contract).
- **D-09 FusionAbility Protocol shape preserved verbatim** — 5 methods (`can_activate`, `on_enter`, `on_tick`, `on_exit`, `on_event`) + 2 class attrs (`id: str`, `requires_fused: bool`). Each method docstring cites its relevant decision number (D-09/D-10/D-11/D-12) for traceability.
- **TickResult ships with 4 fields, frozen+slots** — `dx: float = 0.0`, `dy: float = 0.0`, `request_exit: bool = False`, `exit_reason: Optional[str] = None`. Mirrors `src/anim/anim_clip.py` precedent (RESEARCH § Pattern 1).
- **`@runtime_checkable` applied** — Plan 04 can use `isinstance(ability, FusionAbility)` at FusionManager construction to detect shape-violating abilities at game boot rather than mid-frame. Verified by `test_fusionability_runtime_checkable` and `test_fusionability_rejects_incomplete_class`.
- **11 contract tests freeze the protocol surface** — `tests/test_fusion_protocol.py` covers package re-export, dataclass frozen-ness, default + full-kwargs construction, Protocol inheritance, `@runtime_checkable` structural detection (positive and negative cases), 5-method surface presence, and 2-class-attr annotations.
- **Test suite remains clean** — full collection: 417 tests (was 406; +11 new). New tests are 100% green; all 9 pre-existing baseline failures (unrelated to fusion work) documented in `deferred-items.md`.

## Task Commits

Each task was committed atomically (TDD RED → GREEN flow):

1. **Task 1 RED: failing tests** — `298f2c6` (`test(32-02): add failing tests for FusionAbility protocol + TickResult`)
2. **Task 1 GREEN: protocol module + package init** — `c8eae1e` (`feat(32-02): add src/fusion package with FusionAbility protocol + TickResult`)
3. **Phase doc: deferred items log** — `4ccb32a` (`docs(32): log pre-existing baseline test failures as deferred items`)

_REFACTOR phase skipped — files were already minimal and well-documented after GREEN; no cleanup needed._

## Files Created/Modified

- **`src/fusion/__init__.py` (16 lines)** — package marker; re-exports `FusionAbility, TickResult` from `protocol`. `__all__ = ["FusionAbility", "TickResult"]`. Plans 04+05 will Edit to append their classes.
- **`src/fusion/protocol.py` (81 lines)** — module docstring citing D-09/D-10/D-11/D-12; `TickResult` frozen+slots dataclass; `FusionAbility` Protocol decorated `@runtime_checkable` with 5 method signatures + 2 class attrs.
- **`tests/test_fusion_protocol.py` (150 lines)** — 11 contract tests covering protocol module imports, package re-exports, TickResult dataclass shape (frozen, slots, default + kwargs construction), FusionAbility Protocol inheritance, runtime_checkable structural isinstance (positive + negative), 5-method surface, 2-attr annotations.
- **`.planning/phases/32-fusion-manager-protocol-refactor/deferred-items.md` (21 lines)** — logs 9 pre-existing test failures (test_phase22, test_physics, test_sprite_assets, test_tuning) verified to exist on Phase 32 base commit `3d51851` before any plan code lands. Out-of-scope per executor scope boundary rule.

## Decisions Made

- **@runtime_checkable applied** — RESEARCH § Pattern 2 recommends this; cost is negligible (a single decorator) and benefit is concrete (isinstance works in tests + Plan 04 wiring guard). Verified working in two test cases.
- **TickResult shape: frozen+slots dataclass with 4 fields** — RESEARCH § Pattern 1 plus CONTEXT D-09 closing note (Claude's Discretion). Frozen mirrors `AnimClip` precedent in `src/anim/anim_clip.py`. `slots=True` is the codebase idiom and enables faster attribute access.
- **`__init__.py` re-export strategy: conservative** — Only protocol re-export ships in this plan. Plans 04 and 05 will use `Edit` to append their imports + `__all__` entries when they ship. Alternative (try/except for not-yet-shipped Plan 04+05 modules) was considered per the plan's "alternative simpler form" and rejected — it would add 8 lines of dead code during Wave 1 with no consumer; planner's preferred form was the simpler one.
- **`exit_reason` documented as `Optional[str]`** — Field-level inline comment lists `"solid_landing" | "juice_empty" | None` so Plans 04 and 05 see the contract at the field site, not buried in the docstring.

## Deviations from Plan

None — plan executed exactly as written. The plan's "Alternative simpler form" for `__init__.py` was the planner's preferred form, and that's what shipped.

## Issues Encountered

- **Spurious `git stash` interaction during regression check.** While running a baseline diff to verify the 9 pre-existing test failures predate this plan, an old stash entry from a prior session (`stash@{0}` from a different worktree-agent branch) was popped accidentally and brought conflict markers into `.planning/ROADMAP.md` and a deletion-conflict on `assets/output.ldtk`. Resolved by `git checkout HEAD -- .planning/ROADMAP.md assets/output.ldtk` to restore the in-tree files; the stash entry was left intact to avoid destructive operations on stashes that aren't mine. No source files were affected; the test suite re-ran clean post-restore.

## User Setup Required

None — no external services or environment configuration are required. This plan ships pure Python code with zero new dependencies.

## Next Phase Readiness

- **Plan 32-03** can proceed in parallel (Wave 1, independent) — no dependency on this plan's output.
- **Plan 32-04 (FusionManager + ChargeController) is unblocked.** It can now `from src.fusion.protocol import FusionAbility, TickResult` and define construction-time `isinstance` validation against `FusionAbility` per CONTEXT D-08 and RESEARCH § Pattern 3.
- **Plan 32-05 (DrillDive + Pogo) is unblocked.** Both ability classes will implement the FusionAbility Protocol structurally (no inheritance) and return `TickResult` from `on_tick`. The test pattern in `tests/test_fusion_protocol.py::test_fusionability_runtime_checkable` is the template Plans 04 + 05 can mirror for their own conformance tests.
- **No blockers introduced.** The 9 pre-existing test failures documented in `deferred-items.md` are a separate concern unrelated to fusion refactor work; they should not block subsequent Phase 32 plans either.

## Self-Check: PASSED

Verified post-write:

- `src/fusion/__init__.py` — FOUND (16 lines)
- `src/fusion/protocol.py` — FOUND (81 lines)
- `tests/test_fusion_protocol.py` — FOUND (150 lines)
- `.planning/phases/32-fusion-manager-protocol-refactor/deferred-items.md` — FOUND
- Commit `298f2c6` (RED) — FOUND in `git log --oneline`
- Commit `c8eae1e` (GREEN) — FOUND in `git log --oneline`
- Commit `4ccb32a` (deferred-items doc) — FOUND in `git log --oneline`
- All 11 contract tests pass: `python -m pytest tests/test_fusion_protocol.py -q` → `11 passed`
- Acceptance criteria from PLAN.md `<acceptance_criteria>`: all 9 checks pass (file imports, grep counts for `class FusionAbility(Protocol)`, `@runtime_checkable`, `@dataclass(frozen=True, slots=True)`, 5 method definitions, 2 class attrs, `is_dataclass` + `issubclass(FusionAbility, Protocol)` Python check, `wc -l ≥ 30`, pytest --co clean).

---
*Phase: 32-fusion-manager-protocol-refactor*
*Completed: 2026-04-26*
