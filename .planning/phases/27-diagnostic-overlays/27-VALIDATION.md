---
phase: 27
slug: diagnostic-overlays
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-12
---

# Phase 27 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | none — Wave 0 installs if needed |
| **Quick run command** | `python -m pytest tests/ -x -q` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 27-01-01 | 01 | 1 | TOOL-08 | — | N/A | visual | `mcp__pyxel__run_and_capture` | ❌ W0 | ⬜ pending |
| 27-01-02 | 01 | 1 | TOOL-08 | — | N/A | visual | `mcp__pyxel__run_and_capture` | ❌ W0 | ⬜ pending |
| 27-02-01 | 02 | 1 | TOOL-09 | — | N/A | visual | `mcp__pyxel__run_and_capture` | ❌ W0 | ⬜ pending |
| 27-02-02 | 02 | 1 | TOOL-09 | — | N/A | visual | `mcp__pyxel__run_and_capture` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Verify existing test infrastructure can import overlay module
- [ ] Pyxel MCP tools available for visual verification

*Existing infrastructure covers most phase requirements — overlays are primarily visual and verified via MCP capture tools.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Overlay renders on top without gameplay impact | TOOL-08 | Visual rendering order + performance | Toggle each overlay (F2-F5), play for 10s, confirm no gameplay change |
| Frame-time graph accuracy | TOOL-09 | Requires real-time visual inspection | F3 overlay, compare graph to actual frame rate |
| Slime AI state labels match behavior | TOOL-09 | Requires observing slime during gameplay | F5 overlay, trigger stuck/catch-up states, verify labels update |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
