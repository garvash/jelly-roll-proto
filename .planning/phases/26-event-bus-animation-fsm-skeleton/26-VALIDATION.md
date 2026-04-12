---
phase: 26
slug: event-bus-animation-fsm-skeleton
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-12
---

# Phase 26 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Source: `26-RESEARCH.md` §Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (inherited from Phase 24/25) |
| **Config file** | None — pytest default discovery |
| **Quick run command** | `python -m pytest tests/test_anim.py tests/test_event_bus.py -x -q` |
| **Full suite command** | `python -m pytest -x -q` |
| **Estimated runtime** | Quick: ~1–2s · Full: <30s |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_anim.py tests/test_event_bus.py -x -q`
- **After every plan wave:** Run `python -m pytest -x -q`
- **Before `/gsd-verify-work`:** Full suite must be green AND manual v1.3 regression playthrough per Phase 25 D-04 pattern must pass (Room 0 → boss room, all 11 player states exercised, visual parity confirmed)
- **Max feedback latency:** <2 seconds for the quick run

---

## Per-Task Verification Map

Task IDs are placeholders — the planner will assign `{phase}-{plan}-{task}` IDs when writing PLAN.md files. The table below is indexed by **requirement** so the planner can map each test to the task that creates the covered code.

| Req ID | Behavior | Test Type | Automated Command | Wave 0 |
|--------|----------|-----------|-------------------|--------|
| ANIM-01 | `src/anim/` package imports cleanly with 5 modules | import smoke | `python -c "from src.anim import event_bus, anim_clip, anim_player, state_machine, player_anim"` | ❌ |
| ANIM-01 | `AnimFSM` construction raises on missing clip_id | unit | `pytest tests/test_anim.py::test_fsm_raises_on_missing_clip -x` | ❌ |
| ANIM-01 | `AnimClip` length mismatch raises at construction | unit | `pytest tests/test_anim.py::test_clip_length_mismatch -x` | ❌ |
| ANIM-01 | `AnimPlayer.set_clip` resets counter to 0 (D-07) | unit | `pytest tests/test_anim.py::test_clip_change_resets_counter -x` | ❌ |
| ANIM-01 | `AnimClip(loop=False)` holds on last frame (Phase 31 readiness) | unit | `pytest tests/test_anim.py::test_non_looping_clip_holds -x` | ❌ |
| ANIM-02 | `event_bus.subscribe` + `emit` round-trip | unit | `pytest tests/test_event_bus.py::test_subscribe_emit_roundtrip -x` | ❌ |
| ANIM-02 | `event_bus.reset` clears subscribers (pytest fixture hygiene) | unit | `pytest tests/test_event_bus.py::test_reset_clears_subscribers -x` | ❌ |
| ANIM-02 | Each of the 17 events fires from gameplay code (one test per event) | integration | `pytest tests/test_event_bus.py -k "emits_from_gameplay" -x` | ❌ |
| ANIM-02 | `direction_change` fires exactly once on turn-around (Pitfall 3) | integration | `pytest tests/test_event_bus.py::test_direction_change_only_on_flip -x` | ❌ |
| ANIM-02 | `land` fires exactly once per landing (Pitfall 5) | integration | `pytest tests/test_event_bus.py::test_land_only_on_touchdown -x` | ❌ |
| ANIM-02 | `fall_start` fires exactly once per fall transition (Pitfall 4) | integration | `pytest tests/test_event_bus.py::test_fall_start_only_on_transition -x` | ❌ |
| ANIM-03 | Hardcoded `u = 16 + ...` line is gone | grep | `! grep -n "u = 16 + (pyxel.frame_count" src/entities/player.py` | — |
| ANIM-03 | RUNNING parity: 24 frames, alternating u=16 / u=32 every 12 frames | unit | `pytest tests/test_anim.py::test_running_parity -x` | ❌ |
| ANIM-03 | JUMPING / FALLING parity: constant u=32 | unit | `pytest tests/test_anim.py::test_jumping_parity -x && pytest tests/test_anim.py::test_falling_parity -x` | ❌ |
| ANIM-03 | IDLE parity: constant u=0 | unit | `pytest tests/test_anim.py::test_idle_parity -x` | ❌ |
| ANIM-03 | Fallback states (DIVING, RAMMING, DASHING, BOOSTING, CHARGING_SHOT, WALL_SLIDING) all render u=0 via tail rule | unit | `pytest tests/test_anim.py::test_fallback_states_parity -x` | ❌ |
| ANIM-03 | `player._anim_driver` is a single instance mutated in place (D-16) | unit | `pytest tests/test_anim.py::test_driver_single_instance -x` | ❌ |
| ANIM-03 | `_update_anim_driver()` is the last call in `player.update()` (D-14) | code grep | `grep -B1 "return" src/entities/player.py \| grep "_update_anim_driver"` returns match | — |
| ANIM-03 | v1.3 visual parity playthrough (Room 0 → boss room, all 11 states exercised) | manual | Documented playthrough log in VERIFICATION.md following Phase 25 D-04 pattern | — |

*Status per task: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky — tracked during execution.*

---

## Wave 0 Requirements

- [ ] `src/anim/__init__.py` — empty package marker
- [ ] `src/anim/event_bus.py` — module-level `subscribe(name, cb) / emit(name, **kwargs) / reset()` with `_subscribers: dict[str, list[Callable]]`
- [ ] `src/anim/anim_clip.py` — `@dataclass(slots=True) class AnimClip` with `frames: list[int]`, `durations: list[int]`, `loop: bool = True`, `__post_init__` length validation
- [ ] `src/anim/anim_player.py` — `class AnimPlayer` with `set_clip(clip)` that resets internal frame counter; `tick()`; `current_frame()`
- [ ] `src/anim/state_machine.py` — `class AnimFSM` taking `rules: list[tuple[Callable, str]]` and `clips: dict[str, AnimClip]`; construction-time raise on missing clip_id; `current_frame_u(driver) -> int`
- [ ] `src/anim/player_anim.py` — `@dataclass(slots=True) class PlayerAnimDriver` (`state`, `is_grounded`, `facing`, `vy_sign`); module-level `PLAYER_CLIPS` dict; module-level `PLAYER_RULES` list; `build_player_fsm() -> AnimFSM` factory
- [ ] `tests/test_anim.py` — 9+ unit tests covering AnimClip, AnimPlayer, AnimFSM, and parity for all 11 player states
- [ ] `tests/test_event_bus.py` — 17+ integration tests (one per event) + subscribe/emit/reset unit tests
- [ ] `tests/conftest.py` — autouse `event_bus.reset()` fixture + `sys.modules["pyxel"] = MagicMock()` headless harness (extract from `tests/test_tuning_livereach.py` if not already shared)
- [ ] Framework install: **none required** — pytest already present from Phase 24

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| v1.3 visual parity across a full playthrough | ANIM-03 | Sprite output is a rendered image stream; the unit tests prove `current_frame_u()` matches the old formula per-state, but cross-state transitions (e.g., JUMP→FALL→LAND→RUN) are easier to eyeball than to snapshot-diff | Load Room 0 at baseline. Route: walk right → jump a 2-tile gap → fall → land → drill-dive on cracked-V → ram on cracked-H → kick → bubble shield → save → reload. Confirm sprite output identical to v1.3 baseline (compare side-by-side if possible). Document in VERIFICATION.md per Phase 25 D-04 pattern. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify OR Wave 0 dependencies listed above
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all 9 MISSING files (6 source + 3 test)
- [ ] No watch-mode flags (`pytest -x -q` only, no `--watch`)
- [ ] Feedback latency < 2s on quick run
- [ ] `nyquist_compliant: true` set in frontmatter after all tests pass

**Approval:** pending
