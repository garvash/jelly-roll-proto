---
phase: 26-event-bus-animation-fsm-skeleton
plan: 03
status: complete
started: 2026-04-12
completed: 2026-04-12
---

## Summary

Wired all 17 ANIM-02 gameplay events via `event_bus.emit()` at their line-anchored sites. 16 events emit from `src/entities/player.py` and 1 (`spit`) from `src/entities/slime.py`. Five asymmetric events use prev-state snapshots to fire exactly once per transition (direction_change, fall_start, land, wall_touch, wall_slide). 8 Phase 32 re-homing comments placed on fusion/ability emits.

## Key Files

### Created
- `tests/conftest.py` — autouse event_bus.reset() fixture + shared mock_level/mock_slime fixtures

### Modified
- `src/entities/player.py` — 16 event_bus.emit() calls + 4 prev-state snapshot attrs
- `src/entities/slime.py` — event_bus import + spit event emit
- `tests/test_event_bus.py` — 20 integration tests (one per event + 3 pitfall guards)

## Deviations

- Rule 1 auto-fix: conflict resolution during cherry-pick recovery required manual merge of event_bus.emit() lines with tuning.X constant style (worktree had stale bare-constant imports)

## Design Decisions

- `ram_impact` emits on cracked-H break only (not on solid-wall stop)
- `damaged` emits on real-HP damage only (not on mana-shield absorbed)

## Self-Check: PASSED

- [x] All 17 events emit from correct gameplay sites
- [x] 5 prev-state snapshots prevent per-frame duplicate emits
- [x] 8 Phase 32 re-homing comments on fusion/ability emits
- [x] 20 integration tests pass
- [x] 416 total tests pass, 3 skipped
- [x] Visual regression playthrough approved by user
