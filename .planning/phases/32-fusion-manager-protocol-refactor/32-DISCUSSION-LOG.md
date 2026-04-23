# Phase 32: Fusion Manager + Protocol Refactor - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-23
**Phase:** 32-fusion-manager-protocol-refactor
**Areas discussed:** Cut-ability code-strip sequencing, Component boundaries + Protocol shape, Pogo placement in the package, Save format versioning

---

## Cut-ability code-strip sequencing

### Q1 — How should the cut-ability code-strip be sequenced?

| Option | Description | Selected |
|--------|-------------|----------|
| Insert as Phase 31.5 via /gsd-insert-phase (Recommended) | Dedicated phase with its own PLAN/CONTEXT/SUMMARY and its own commits. | ✓ |
| Fold into Phase 32 Plan 01 | Strip is the first plan of Phase 32, refactor is plans 02+. | |
| Inline prerequisite at top of Plan 01 | Plan 01 does strip-then-scaffold as a single task. | |

**User's choice:** Insert as Phase 31.5 via /gsd-insert-phase.
**Notes:** Matches HARD GATE framing in FUSION-DESIGN.md and ROADMAP.md literally; keeps refactor commits clean.

### Q2 — How should the cut tuning groups in physics-schema.json be handled?

| Option | Description | Selected |
|--------|-------------|----------|
| Drop them entirely (Recommended) | Delete ram/charge_shot/boost/bubble_shield groups from schema and every preset file. | ✓ |
| Keep groups, zero out / mark deprecated | Groups stay in schema, panel doesn't expose them, code doesn't read them. | |
| Drop schema, keep v1.3 preset frozen | Drop from code/schema; leave _v1.3-reference.json untouched as a historical artifact. | |

**User's choice:** Drop them entirely.
**Notes:** Clean break. Tuning artifacts are not archival; FUSION-DESIGN Drill-Dive Contract owns the v1.3 behavioral baseline.

### Q3 — What happens to the `dash` logical action in src/core/input.py?

| Option | Description | Selected |
|--------|-------------|----------|
| Remove dash from _ACTION_MAP (Recommended) | `dash` entry removed; V becomes unbound at OS level. | ✓ |
| Keep dash mapped, gate at code layer | Leave dash in _ACTION_MAP but strip every btnp('dash') caller. | |
| Rename V binding to a placeholder | Replace `dash` with e.g. `reserved` or comment-out. | |

**User's choice:** Remove dash from _ACTION_MAP.
**Notes:** Satisfies the FUSION-DESIGN acceptance-checklist grep test.

### Q4 — Strip scope

| Option | Description | Selected |
|--------|-------------|----------|
| Full coverage: player.py + slime.py + schema + presets + input.py + save_manager.py + tests (Recommended) | End-to-end strip in one phase. | ✓ |
| Code-only; save + tests roll into Phase 32 | Strip phase smaller; Phase 32 bigger. | |
| Code-only; tests stay, save unchanged | Minimum viable strip. | |

**User's choice:** Full coverage.
**Notes:** Save-format cleanup (dropping has_dash/has_shield/has_shield_t2/has_boost) is Phase 31.5 scope; Phase 32 only owns save_version bump.

---

## Component boundaries + Protocol shape

### Q1 — Where does ChargeController's responsibility end vs. FusionManager's?

| Option | Description | Selected |
|--------|-------------|----------|
| CC owns RECALL + WINDUP + tap/hold; Mgr owns FUSED + EXIT (Recommended) | Clean cut at 200% latch. | ✓ |
| CC owns only WINDUP 2nd pass; Mgr owns RECALL + FUSED + EXIT | Narrow CC; muddier Manager. | |
| CC is stateless — pure compute; Mgr owns full FSM | Single FSM state holder; loses 'pre-manager' framing. | |

**User's choice:** CC owns RECALL + WINDUP + tap/hold; Mgr owns FUSED + EXIT.

### Q2 — FusionAbility Protocol shape?

| Option | Description | Selected |
|--------|-------------|----------|
| Lifecycle + per-frame + event hooks (Recommended) | can_activate, on_enter, on_tick, on_exit, on_event. | ✓ |
| Minimal lifecycle only (enter/update/exit) | No event hooks; ability subscribes directly. | |
| Data-class + function dispatch | Dataclass with function fields. | |

**User's choice:** Lifecycle + per-frame + event hooks.

### Q3 — Where does per-frame drill physics live?

| Option | Description | Selected |
|--------|-------------|----------|
| Inside src/fusion/drill_dive.py (Recommended) | apply_diving_physics moves into the ability module. | ✓ |
| Stays in player.py; ability returns intent | Ability returns intent; Player applies. | |
| Shared helper in src/fusion/physics.py | Package-level helper. | |

**User's choice:** Inside src/fusion/drill_dive.py.

### Q4 — Preserve fuse()/unfuse() shims or delete?

| Option | Description | Selected |
|--------|-------------|----------|
| Delete; Player calls FusionManager directly (Recommended) | Remove player.fuse/unfuse entirely. | ✓ |
| Keep as thin shims that delegate | One-liner proxies to FusionManager. | |
| Keep; Player and FusionManager share is_fused state | Two owners. | |

**User's choice:** Delete; Player calls FusionManager directly.

---

## Pogo placement in the package

### Q1 — Where does pogo live?

| Option | Description | Selected |
|--------|-------------|----------|
| src/fusion/pogo.py as a FusionAbility-shaped 'null-fusion' (Recommended) | Pogo implements Protocol with requires_fused=False. | ✓ |
| src/fusion/pogo.py as a non-Protocol sibling | In package but different interface. | |
| src/movement/pogo.py — outside the fusion package | New src/movement module. | |

**User's choice:** null-fusion shape inside src/fusion/pogo.py.

### Q2 — Who owns the DOWN+SPACE airborne dispatch?

| Option | Description | Selected |
|--------|-------------|----------|
| FusionManager.handle_jump_input() (Recommended) | Single entry point on Manager. | ✓ |
| Player.handle_input branches explicitly | if is_fused checks in Player. | |
| Shared input router in src/fusion/input_router.py | New module owns branching. | |

**User's choice:** FusionManager.handle_jump_input().

### Q3 — Pogo tunable or hardcoded for Phase 32?

| Option | Description | Selected |
|--------|-------------|----------|
| Hardcoded constants in pogo.py for Phase 32 (Recommended) | No tuning group; Phase 33 may migrate. | ✓ |
| New tuning.pogo_* group in physics-schema.json now | Full tuning integration now. | |
| Tuning group + panel tab in Phase 32 | Violates 'pure refactor'. | |

**User's choice:** Hardcoded constants in pogo.py.

### Q4 — Pogo contact rules?

| Option | Description | Selected |
|--------|-------------|----------|
| Bounce on enemies + breakables; no-op on solid (Recommended) | Matches FUSION-DESIGN D-04 exactly. | ✓ |
| Bounce-on-contact-only + damage, no breakable interaction | No breakable passthrough. | |
| Damage-only strike; no bounce at all | No bounce. | |

**User's choice:** Bounce on enemies + breakables; no-op on solid.

---

## Save format versioning — field + rejection UX

### Q1 — How should the version field migrate?

| Option | Description | Selected |
|--------|-------------|----------|
| Rename `version` → `save_version`; bump to 2 (Recommended) | Single breaking change; matches ROADMAP wording. | ✓ |
| Keep `version`; bump to 2 (no rename) | Minimizes churn; drops ROADMAP literal wording. | |
| Add `save_version` alongside `version` | Transitional coexistence. | |
| Move versioning under a `meta` block | Biggest structural churn; richer metadata. | |

**User's choice:** Rename version → save_version; bump to 2.

### Q2 — Value format for save_version?

| Option | Description | Selected |
|--------|-------------|----------|
| Integer schema version (Recommended) | save_version: 2; monotonic increment on schema change. | ✓ |
| Semver string tied to milestone ("2.0.0") | Self-documenting; parsing cost. | |
| Milestone tag ("v2.0") | Short; imprecise. | |

**User's choice:** Integer schema version.

### Q3 — Rejection UX for mismatched save_version?

| Option | Description | Selected |
|--------|-------------|----------|
| Hard fail: clear message, refuse to load, keep file on disk (Recommended) | Matches ROADMAP goal #3 literally. | ✓ |
| Silent delete + start new game | Destroys user data. | |
| Migrate-and-strip (drop cut-ability flags, bump version) | Preserves progress; costs migration code. | |
| Warning overlay, let user confirm load anyway | Risky; prototype not designed for forward-compat. | |

**User's choice:** Hard fail: clear message, refuse to load, keep file on disk.

### Q4 — Where does the current version constant live?

| Option | Description | Selected |
|--------|-------------|----------|
| Module-level CURRENT_SAVE_VERSION in save_manager.py (Recommended) | Co-located with read/write. | ✓ |
| In tuning or schema module | Groups all versioning. | |
| In a project-level constants module | Broader reusability. | |

**User's choice:** Module-level CURRENT_SAVE_VERSION in save_manager.py.

---

## Claude's Discretion

- TickResult shape returned by on_tick (named tuple, dataclass, dict, tagged union).
- FusionManager method names for latch-fuse / force-exit.
- Whether player.is_fused stays as a property-forwarded read or removes every callsite.
- Whether pogo reuses drill's soft-destructible passthrough code or duplicates a minimal version.
- Exact pogo constant names (POGO_BOUNCE_VELOCITY, POGO_IMPULSE, etc.).
- Whether save-version rejection raises a typed exception or returns a structured result dict.
- Phase 32's pytest scope — design doc says smoke test is sufficient; planner decides.
- ChargeController-complete signaling (callback vs. polled flag vs. direct observation).
- Accelerated regen implementation layer (ChargeController → slime.refill vs. slime mode flag).

## Deferred Ideas

- Accelerated-regen rate tuning → Phase 33.
- Tap/hold threshold retune → Phase 33.
- Pogo values in tuning/presets → Phase 33.
- Drill i-frames → Phase 33 (currently NONE per v1.3).
- Manual mid-drill unfuse → permanently stripped.
- Five cut abilities → post-prototype.
- CRACKED_H gates become dead gates → level-design follow-up in Phase 31.5 or earlier.
- Second-pass overlay visual polish → Phase 31 + Phase 33.
- Save migration path → not built; future milestone if needed.
- Save-file UX polish → Phase 35 or later.
- V button v2.0 rebinding → post-prototype.
- Phase 32 pytest scope → planner discretion.
