---
phase: 28-live-tuning-panel-mvp
status: secured
threats_total: 9
threats_open: 0
threats_closed: 9
audited: 2026-04-12
---

# Security Threat Verification: Phase 28

## Threat Register

| ID | Category | Component | Disposition | Status | Evidence |
|----|----------|-----------|-------------|--------|----------|
| T-28-01 | Tampering | Slider value injection | mitigate | CLOSED | `tuning.set_value()` rejects unknown keys via KeyError (inherited T-24-10). Panel only passes keys from `_flat_index`. |
| T-28-02 | Tampering | Keyboard numeric entry | mitigate | CLOSED | `widgets.py:_commit_edit` — try/except ValueError on float parse, clamp to [0.25x, 4x] baseline range. Note: WR-03 flagged baseline==0 edge case as partial coverage. |
| T-28-03 | DoS | Rapid slider drag | accept | CLOSED | `set_value` is O(1) dict write. No amplification. Acceptable risk for dev-only tool. |
| T-28-04 | Info Disclosure | _flat_index exposure | accept | CLOSED | Developer-only debug tool. All tuning keys intentionally visible. |
| T-28-05 | Tampering | Preset file injection | accept | CLOSED | Local JSON under version control. No code execution path. User explicitly loads presets. |
| T-28-06 | Tampering | Journal write path | mitigate | CLOSED | `journal.py:13` — `JOURNAL_DIR` is hardcoded `Path` derived from `__file__`. No user-supplied path input. |
| T-28-07 | DoS | Journal disk fill | mitigate | CLOSED | `journal.py:14` — `MAX_ENTRIES = 10000` cap per session file. Count checked before write at line 29. |
| T-28-08 | Tampering | set_value monkey-patch | accept | CLOSED | Wrapper only adds journal recording. Original `set_value` validation preserved (KeyError on unknown keys). Dev-only tool. |
| T-28-09 | Elevation | Preset overwrite baseline | mitigate | CLOSED | `panel.py:44-45` — `_confirm_timer` with `_CONFIRM_DURATION = 120` frames. Protected slot 1 requires double-click within window. |

## Trust Boundaries

| Boundary | Description | Mitigation |
|----------|-------------|------------|
| Tuning key validation | Panel passes key names to tuning.set_value() | Only keys from _flat_index used; set_value rejects unknown keys |
| Numeric input parsing | User types arbitrary strings in keyboard edit | try/except float(); ValueError rejected; value clamped to baseline range |
| File system (presets) | JSON read/write to assets/presets/ | Hardcoded path, atomic write (tmp+fsync+replace), no path traversal |
| File system (journal) | JSONL append to assets/journal/ | Hardcoded path, 10000-entry cap, gitignored |

## Accepted Risks

- **T-28-03**: Rapid drag is O(1), no DoS vector
- **T-28-04**: Tuning keys are intentionally exposed in dev tool
- **T-28-05**: Preset files are local, version-controlled, no code exec
- **T-28-08**: Monkey-patch preserves original validation

## Security Audit 2026-04-12

| Metric | Count |
|--------|-------|
| Threats found | 9 |
| Closed | 9 |
| Open | 0 |
