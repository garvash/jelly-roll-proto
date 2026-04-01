# Phase 16: v1.1 Housekeeping & Verification - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-02
**Phase:** 16-v1.1-housekeeping-verification
**Areas discussed:** ABL-07 cleanup scope, Phase 10 VERIFICATION.md, Slime absorption audit, ROADMAP staleness

---

## ABL-07 Cleanup Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Strike and archive | Mark ABL-07 as 'Removed' in REQUIREMENTS.md, add strikethrough in ROADMAP.md Phase 9. Prior CONTEXT.md files left as historical record. | ✓ |
| Full purge | Remove ABL-07 lines entirely from REQUIREMENTS.md and ROADMAP.md. Clean break. | |
| You decide | Claude picks the approach. | |

**User's choice:** Strike and archive (Recommended)
**Notes:** ABL-07 code already gone from src/. Only doc references remain.

---

## Phase 10 VERIFICATION.md

| Option | Description | Selected |
|--------|-------------|----------|
| Retroactive test + code audit | Run existing test suite, grep for requirement coverage, document results. No new tests. | ✓ |
| Full verification with new tests | Write missing test cases for Phase 10 features, run them, document results. | |
| Requirement sign-off only | Lightweight checklist confirming features shipped. No test runs. | |

**User's choice:** Retroactive test + code audit (Recommended)
**Notes:** Phase 10 has VALIDATION.md strategy but no VERIFICATION.md results doc.

---

## Slime Absorption Draw Path Audit

| Option | Description | Selected |
|--------|-------------|----------|
| Visual + state cleanup | Check draw effect AND verify is_being_absorbed cleared in all exit paths (death, room transition, unfuse, dissipation). | ✓ |
| Visual correctness only | Just verify pulsing shrink effect looks right. No state management audit. | |
| You decide | Claude determines depth based on code. | |

**User's choice:** Visual + state cleanup (Recommended)
**Notes:** is_being_absorbed flag in slime.py controls pulsing shrink during CHARGING_SHOT windup.

---

## ROADMAP Staleness

| Option | Description | Selected |
|--------|-------------|----------|
| It shipped — fix checkbox | 11-03 was completed, ROADMAP checkbox wasn't updated. Mark done. | ✓ |
| Descoped — note as gap | 11-03 didn't fully ship. Add note as known gap. | |
| Not sure — audit first | Claude checks git history to determine what shipped. | |

**User's choice:** It shipped — just fix the checkbox
**Notes:** Phase 11 marked complete but 11-03 still unchecked.

---

## Claude's Discretion

- Fix approach for additional stale checkboxes found during ROADMAP scan
- Whether to add comments in slime.py if absorption exit paths are incomplete

## Deferred Ideas

None — discussion stayed within phase scope
