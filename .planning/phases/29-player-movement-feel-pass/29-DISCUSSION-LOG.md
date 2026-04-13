# Phase 29: Player Movement Feel Pass - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-13
**Phase:** 29-player-movement-feel-pass
**Areas discussed:** Feel target format, Tuning methodology, Preset identity

---

## Feel Target Format

### Q1: How should feel targets be structured?

| Option | Description | Selected |
|--------|-------------|----------|
| Gap/timing tests | Spatial challenges with concrete pass/fail criteria | ✓ |
| Adjective targets | Descriptive feel goals, tuned by subjective feel | |
| Reference game targets | Compare against known games like Celeste, Hollow Knight | |

**User's choice:** Gap/timing tests
**Notes:** Concrete, playtestable, pass/fail format preferred.

### Q2: Who writes the feel target table?

| Option | Description | Selected |
|--------|-------------|----------|
| Claude drafts, I revise | Claude generates targets from physics math, user edits | ✓ |
| I write them fresh | User writes all targets from scratch | |
| Mix | Claude does spatial math, user adds subjective ones | |

**User's choice:** Claude drafts, I revise

### Q3: Where should the feel target document live?

| Option | Description | Selected |
|--------|-------------|----------|
| Phase dir | `.planning/phases/29-*/29-FEEL-TARGETS.md` | ✓ |
| Assets dir | `assets/feel-targets.md` | |

**User's choice:** Phase dir

---

## Tuning Methodology

### Q1: What order should systems be tuned in?

| Option | Description | Selected |
|--------|-------------|----------|
| Ground -> Air -> Wall | Accel/friction first, then gravity/jump, then wall last | ✓ |
| Core loop first | Jump arc first, then ground to match, then wall | |
| All at once | Holistic tuning, switching between systems freely | |

**User's choice:** Ground -> Air -> Wall

### Q2: How should tuning sessions be structured?

| Option | Description | Selected |
|--------|-------------|----------|
| Claude builds test rooms | Purpose-built LDtk levels with measured challenges | ✓ |
| Use existing rooms | Playtest in real game rooms | |
| You decide | Claude's discretion | |

**User's choice:** Claude builds test rooms

### Q3: New level or modify existing?

| Option | Description | Selected |
|--------|-------------|----------|
| New dedicated level | Add a new LDtk test level, separate from game content | ✓ |
| Modify existing level | Add test sections to existing level | |
| You decide | Claude's discretion | |

**User's choice:** New dedicated level

---

## Preset Identity

### Q1: What should 'tight' preset feel like?

| Option | Description | Selected |
|--------|-------------|----------|
| Celeste-style | High accel, high friction, lower jump, fast fall, short coyote | ✓ |
| Meat Boy-style | Very high speed, moderate friction, high jump | |
| Subtle tightening | 10-20% tighter across the board | |
| You decide | Claude picks based on geometry | |

**User's choice:** Celeste-style

### Q2: What should 'floaty' preset feel like?

| Option | Description | Selected |
|--------|-------------|----------|
| Hollow Knight-style | Low gravity, high jump, long hang time, generous coyote | ✓ |
| Kirby-style | Very low gravity, slow fall, almost hovering | |
| Subtle loosening | 10-20% looser than v1.3 | |
| You decide | Claude picks to contrast tight | |

**User's choice:** Hollow Knight-style

### Q3: Should v1.3 baseline be updated or frozen?

| Option | Description | Selected |
|--------|-------------|----------|
| Frozen reference | v1.3 stays untouched, new v2.0 default created alongside | ✓ |
| Evolve baseline | Baseline updated to new tuned values | |
| You decide | Claude's discretion | |

**User's choice:** Frozen reference

---

## Claude's Discretion

- Specific feel target values (physics math calculations)
- Test room layout and challenge design
- Exact preset slider values (guided by Celeste/HK feel descriptions)
- Number of tuning iterations per system
- Whether additional test rooms are needed

## Deferred Ideas

- Kick mechanic referenced in roadmap but removed from game long ago — not in scope for any phase
