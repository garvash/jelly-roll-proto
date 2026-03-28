---
status: resolved
trigger: "LEFT/RIGHT tap repositions slime but disables following behavior afterward"
created: 2026-03-28T00:00:00Z
updated: 2026-03-28T12:00:00Z
---

## Current Focus

hypothesis: hold_position() sets is_holding_position=True but nothing clears it after tap-reposition
test: trace all code paths that set is_holding_position=False
expecting: no path clears it after a tap reposition completes
next_action: return diagnosis

## Symptoms

expected: LEFT/RIGHT tap (<=5 frames) swaps player and slime positions, slime resumes following afterward
actual: Slime repositions correctly but never follows player again until a reform trigger
errors: none (behavioral bug)
reproduction: tap LEFT or RIGHT for <=5 frames while unfused with slime present
started: since ABL-03 implementation

## Eliminated

(none needed -- root cause found on first hypothesis)

## Evidence

- timestamp: 2026-03-28T00:00:00Z
  checked: slime.hold_position() method (slime.py lines 111-148)
  found: Sets self.is_holding_position = True on every call path (lines 128, 136, 146)
  implication: After tap-reposition, slime enters hold state permanently

- timestamp: 2026-03-28T00:00:00Z
  checked: slime.update() method (slime.py lines 150-236), specifically the hold branch
  found: Lines 179-190 -- when is_holding_position is True, slime skips the standard follow path entirely. The ONLY exit is if slime exceeds SLIME_MAX_DIST from player (line 187-189), which calls reform() and clears is_holding_position
  implication: After a tap reposition, slime is stuck in hold mode until player walks ~100px away

- timestamp: 2026-03-28T00:00:00Z
  checked: all places that set is_holding_position = False
  found: reform() (line 309), recall() (line 63), fuse() via player.py (line 79). No path clears it after a tap completes.
  implication: The design intent for ABL-03 "hold" is for HELD directions, but tap also triggers it with no auto-clear

## Resolution

root_cause: slime.hold_position() unconditionally sets is_holding_position=True (slime.py lines 128, 136, 146). This flag causes slime.update() to skip the standard follow path (line 180). For a TAP reposition (as opposed to a sustained hold), the flag is never cleared -- the only exits are: (1) player moves >100px away triggering reform, (2) recall, or (3) fuse. There is no "tap completed, resume following" path.
fix: (not applied -- diagnosis only)
verification: (not applied)
files_changed: []
