---
phase: 30
slug: fusion-lifecycle-design-doc
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-19
---

# Phase 30 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> **Phase 30 is design-only.** "Tests" are structural checks against the locked markdown file (`.planning/FUSION-DESIGN.md`). No pytest, no runtime validation. Per CONTEXT.md D-28, pytest stubs are explicitly NOT required.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual doc-content checks (grep + git) |
| **Config file** | none — no test framework |
| **Quick run command** | `test -f .planning/FUSION-DESIGN.md && head -10 .planning/FUSION-DESIGN.md \| grep -E '^(status\|locked_at):'` |
| **Full suite command** | See per-check commands in the Per-Task Verification Map below |
| **Estimated runtime** | ~2 seconds (greps only) |

**Rationale for no framework:** The deliverable is a locked markdown file. Doc-existence, frontmatter-presence, and section-heading-presence are each a one-line grep. A pytest wrapper would add zero value and pull pytest into a design phase. The grep checks below ARE the suite.

---

## Sampling Rate

- **After every task commit:** Run quick check (file exists + frontmatter present)
  `test -f .planning/FUSION-DESIGN.md && head -10 .planning/FUSION-DESIGN.md | grep -E '^(status|locked_at):'`
- **After every plan wave:** Run the full Per-Task Verification Map below.
- **Before phase close (gate):** All 18 checks pass AND `locked_commit` is a real SHA (not `TBD`) AND user signs off on the locked doc.
- **Max feedback latency:** ~2 seconds.

---

## Per-Task Verification Map

| Req ID | Behavior | Check Type | Command (run from repo root) | Expected Result |
|--------|----------|-----------|------------------------------|-----------------|
| FUS-01 | FSM section defines IDLE→RECALL→WINDUP→FUSED→EXIT | Section presence | `grep -n '^## .*FSM' .planning/FUSION-DESIGN.md` | ≥1 match naming the FSM section |
| FUS-01 | All five FSM states are named | Content presence | `for s in IDLE RECALL WINDUP FUSED EXIT; do grep -q "\b$s\b" .planning/FUSION-DESIGN.md \|\| echo "MISSING: $s"; done` | No MISSING output |
| FUS-01 | Juice-economy section includes 100% gate rule | Content presence | `grep -n '100%' .planning/FUSION-DESIGN.md` | ≥1 match near juice-economy section |
| FUS-01 | Second-pass charge ("200% to fuse") model documented (D-23a) | Content presence | `grep -n '200%' .planning/FUSION-DESIGN.md && grep -ni 'second-pass' .planning/FUSION-DESIGN.md` | ≥1 match each |
| FUS-01 | Imminent-fusion telegraph at 90%+ documented (D-23b) | Content presence | `grep -niE '(90%\|telegraph\|imminent\|pulse\|flash)' .planning/FUSION-DESIGN.md` | ≥1 match |
| FUS-01 | Cancel-window duration documented (D-23c, ~30 frames) | Content presence | `grep -niE 'cancel window\|~?30[[:space:]]*frame' .planning/FUSION-DESIGN.md` | ≥1 match |
| FUS-02 | Input model names Z and V with tap/hold semantic | Content presence | `grep -nE '(Z.*tap\|Z.*hold\|DOWN.*V)' .planning/FUSION-DESIGN.md` | ≥3 matches |
| FUS-02 | Tap/hold threshold is quantified (frame count) | Content presence | `grep -nE '[0-9]+[[:space:]]*frame' .planning/FUSION-DESIGN.md` | ≥1 match near input model section |
| FUS-03 | Drill-dive contract section exists | Section presence | `grep -n '^## .*[Dd]rill' .planning/FUSION-DESIGN.md` | ≥1 match |
| FUS-03 | DRILL_SPEED value documented | Content presence | `grep -n 'DRILL_SPEED' .planning/FUSION-DESIGN.md` | ≥1 match |
| FUS-03 | DRILL_IMPACT_COST value documented | Content presence | `grep -n 'DRILL_IMPACT_COST' .planning/FUSION-DESIGN.md` | ≥1 match |
| FUS-03 | CRACKED_V handling documented | Content presence | `grep -n 'CRACKED_V' .planning/FUSION-DESIGN.md` | ≥1 match |
| FUS-03 | Three exit conditions documented (solid, juice=0, manual cancel) | Content presence | `grep -nE '(solid\|juice.*0\|cancel)' .planning/FUSION-DESIGN.md \| wc -l` | ≥3 distinct matches |
| FUS-01/02/03 | Each REQ-ID appears as a bold or heading anchor | Content presence | `for r in FUS-01 FUS-02 FUS-03; do grep -qE "(^##.*$r\|\*\*$r\*\*)" .planning/FUSION-DESIGN.md \|\| echo "MISSING-DEF: $r"; done` | No MISSING-DEF output |
| LOCK-01 | Doc exists at expected path | File existence | `test -f .planning/FUSION-DESIGN.md && echo OK` | `OK` |
| LOCK-02 | Frontmatter `status: LOCKED` present | Frontmatter check | `head -10 .planning/FUSION-DESIGN.md \| grep -E '^status:\s*LOCKED'` | ≥1 match |
| LOCK-03 | Frontmatter `locked_at` is a date (YYYY-MM-DD) | Frontmatter check | `head -10 .planning/FUSION-DESIGN.md \| grep -E '^locked_at:\s*[0-9]{4}-[0-9]{2}-[0-9]{2}'` | ≥1 match |
| LOCK-04 | Frontmatter `locked_commit` is a 7+ char hex SHA | Frontmatter check | `head -10 .planning/FUSION-DESIGN.md \| grep -E '^locked_commit:\s*[0-9a-f]{7,40}'` | ≥1 match (post-lock-commit only — initial draft may use `TBD`) |
| CUT-01 | Cut abilities enumerated | Content presence | `for a in Ram "Directional Hold" "Charge Shot" "Bubble Shield" "Slime Boost"; do grep -q "$a" .planning/FUSION-DESIGN.md \|\| echo "MISSING-CUT: $a"; done` | No MISSING-CUT output |
| ACCEPT-01 | Acceptance-checklist section exists for Phase 32 | Section presence | `grep -n '^## .*[Aa]cceptance' .planning/FUSION-DESIGN.md` | ≥1 match |

*Status (rolled up): ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

No test files needed. No fixtures. No framework install. No conftest. Per CONTEXT D-28, the design phase explicitly forbids authoring pytest stubs.

- [ ] `.planning/FUSION-DESIGN.md` (the deliverable itself; Wave 1 writes it)
- [ ] Lock-commit sequencing documented in Phase 30 PLAN (who runs `git rev-parse`, when the frontmatter amendment happens) — planner scope, not Wave 0.

**Framework install:** None.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `locked_commit` actually matches the commit the doc-author intended to lock to | LOCK-04 | Two-commit dance: write doc with `locked_commit: TBD`, commit, then amend frontmatter with the real SHA. Automated checks can verify the SHA is hex-shaped but not that it points to the *right* commit. | After lock commit lands, run `git log -1 --format=%H -- .planning/FUSION-DESIGN.md` and verify the SHA in frontmatter matches (or is the parent of) that hash. |
| User sign-off on locked design | ACCEPT-01, all FUS-XX | The doc is the user's contract for Phase 32. Automated checks verify structure, not whether the user agrees with the design. | User reviews the rendered doc, comments via thread/discuss-phase if changes needed, then explicitly OKs the lock commit. |

---

## Project Constraints (from `memory/MEMORY.md`)

- **Avoid magic numbers** — doc cites named constants (`DRILL_SPEED`, `DRILL_IMPACT_COST`); raw frame counts (e.g. ~8 for tap/hold) are accompanied by prose naming what they represent.
- **Block gate hierarchy** — drill-dive contract section explicitly ties DRILL to CRACKED_V.
- **Reanimator-style anim architecture** — new events (`drill_start`, `drill_block_break`, `drill_end`, `manual_unfuse_start`) are flagged as anim-side-channel hooks Phase 31 subscribes to, NOT as gameplay inputs that drive the anim FSM.
- **Worktree merges cause regressions** — relevant to lock-commit workflow; diff-verify nothing regressed before considering the phase closed.
- **Push before worktree execution** — Phase 30 is authorship-only; if planner splits into parallel tasks, include the "push before worktree agent" reminder.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify (grep commands above) or are manual-only
- [ ] Sampling continuity: every task commit triggers the quick check
- [ ] Wave 0 covers all MISSING references (none — Wave 0 is empty by design)
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter once all checks defined and accepted by planner

**Approval:** pending
