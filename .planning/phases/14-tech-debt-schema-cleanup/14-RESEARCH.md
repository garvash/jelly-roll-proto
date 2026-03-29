# Phase 14: Tech Debt & Schema Cleanup - Research

**Researched:** 2026-03-29
**Domain:** Pyxel game engine / entity schema / test infrastructure / code cleanup
**Confidence:** HIGH

## Summary

Phase 14 is a gap-closure phase addressing 6 distinct workstreams identified by the v1.1 milestone audit: (1) event-gated door system replacing IntGrid tile ID 4 boss gates, (2) map.py legacy gate scan fix, (3) DEBUG_ALL_ABILITIES removal + runtime god-mode, (4) 6 test failures, (5) orphaned code cleanup, and (6) Phase 10 ABL-02 verification + requirement text updates.

All workstreams are well-scoped with clear root causes confirmed by code inspection and test execution. The codebase is a Pyxel-based 2D game (~420 lines in map.py, ~300 lines in player.py relevant section) with 238 passing tests. The 6 failures have distinct, non-overlapping root causes that are straightforward to fix. The event-gated door system is the largest addition but follows an established pattern (Door entity + game_state dict check).

**Primary recommendation:** Execute as 3-4 coarse plans grouped by dependency: (1) schema + door system + gate scan fix, (2) DEBUG_ALL_ABILITIES removal + god-mode + test fixes, (3) orphaned code cleanup + Phase 10 verification + requirement rewrites.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Add `"event"` to Door entity's `action` enum in entity-schema.json. When action="event", the door checks a game_state dict for its event_id key.
- **D-02:** Add `event_id` field to Door entity as a free-form string (e.g. "boss_defeated", "puzzle_1_solved"). No enum constraint.
- **D-03:** Direct flag check pattern: doors check `game_state[event_id]` on room entry. Boss sets `game_state["boss_defeated"]=True` on death. No event bus needed.
- **D-04:** Doors reset on room entry -- re-check event flags each time. If flag is set, door opens. If not, stays closed.
- **D-05:** Repurpose IntGrid tile ID 4 from "gate" to "event_marker". Keep the ID slot occupied but change its semantic meaning.
- **D-06:** Update map.py `close_gates()`/`open_gates()` to work with new event-gated Door entities instead of scanning for tile ID 4.
- **D-07:** Rewrite MAP-02 from "Z-Spiral 20-25 unique rooms" to: "Room layouts driven by pml-to-ldtk pipeline with event-gated doors replacing tile ID 4 boss gates."
- **D-08:** Remove DEBUG_ALL_ABILITIES flag entirely. Tests run with normal ability state.
- **D-09:** Runtime key combo toggles during gameplay (debug builds only). Tiered: abilities, invincibility, infinite juice.
- **D-10:** God mode state lives in a debug module, not scattered across entity code.
- **D-11:** 3 bubble shield drain rate tests -- fix by removing DEBUG_ALL_ABILITIES dependency.
- **D-12:** Remaining 3 test failures -- Claude's discretion on individual fix vs shared conftest approach.
- **D-13:** Delete `slime.hold_position()` outright.
- **D-14:** Delete `ITEM_FRAMES["DRILL"]` from items.py.
- **D-15:** Verify CRACKED_V breaking (Drill Dive down + Slime Boost up).
- **D-16:** Update ABL-02 requirement text to split: vertical gating (Phase 10, done) vs infinite flight capstone (Phase 11).
- **D-17:** Nitro-Ejection / infinite flight stays in Phase 11 scope.
- **D-18:** Fix `close_gates()` lines 197-198 in map.py: replace hardcoded `+ 16` with `VIEWPORT_W // TILE_SIZE` and `VIEWPORT_H // TILE_SIZE`.
- **D-19:** Claude's discretion on schema version bump (v0.3.0 vs v1.0.0).

### Claude's Discretion
- D-12: Individual test fix vs shared conftest approach for 3 non-shield test failures
- D-19: Schema version bump magnitude

### Deferred Ideas (OUT OF SCOPE)
- Nitro-Ejection / Infinite Flight (Phase 11)
- 5x5mapdesign.txt cleanup
- Nyquist compliance for Phases 8-13
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MAP-02 | Room layout driven by pml-to-ldtk pipeline with event-gated doors (replaces tile ID 4 boss gates) | D-01 through D-07 define the event-gated door system. entity-schema.json Door entity needs action="event" + event_id field. map.py gate scan needs fixing. REQUIREMENTS.md text needs rewriting. |
| ABL-02 | Nitro-Ejection fusion (verification only) | D-15 through D-17: verify CRACKED_V breaking code exists and works, split requirement text for vertical gating vs infinite flight capstone. |
</phase_requirements>

## Architecture Patterns

### Current Gate System (Being Replaced)

The boss fight currently works as:
1. `main.py:214` -- Boss spawn calls `self.level_map.close_gates(cam_x, cam_y)`
2. `map.py:184-201` -- `close_gates()` scans collision_data for `TILE_GATE` tiles, adds to `locked_gates` set, updates visual tilemap to `TILE_SOLID`
3. `map.py:173-182` -- `open_gates()` removes from `locked_gates`, sets visual to `TILE_EMPTY`
4. `main.py:380` -- Boss death calls `self.level_map.open_gates(cam_x, cam_y)` and sets `self.game_state = "WON"`

### New Event-Gated Door Pattern (D-01 through D-06)

```
Game.game_state_flags = {}  # Dict[str, bool] -- NOT the existing game_state="PLAYING"/"WON" string

# Boss death (main.py ~line 380):
self.game_state_flags["boss_defeated"] = True

# Door entity (map_entities.py Door class):
class Door:
    def __init__(self, ..., action=None, event_id=None):
        self.action = action    # "spit", "kick", "event", etc.
        self.event_id = event_id  # "boss_defeated", "puzzle_1_solved"

    def check_event_open(self, game_state_flags):
        """For action='event' doors: open if flag is set."""
        if self.action == "event" and self.event_id:
            if game_state_flags.get(self.event_id, False):
                self.open()

# Room entry (_on_room_enter in main.py):
for door in self.doors:
    door.check_event_open(self.game_state_flags)
```

**IMPORTANT naming collision:** The existing `self.game_state` is a string (`"PLAYING"` / `"WON"`) used for win-screen logic. The new event flags dict MUST use a different name (e.g., `game_state_flags` or `event_flags`) to avoid collision.

### Recommended Project Structure Changes

```
src/
  core/
    constants.py     # Remove DEBUG_ALL_ABILITIES, keep TILE_GATE constant
    debug.py         # NEW: god-mode state + toggle functions
    input.py         # Existing _ACTION_MAP -- god-mode key combos added here or in debug.py
  entities/
    map_entities.py  # Door: add action="event" + event_id support
    player.py        # Remove DEBUG_ALL_ABILITIES import + block; check debug.god_mode flags
    slime.py         # Delete hold_position() method
    items.py         # Delete ITEM_FRAMES["DRILL"] entry
  level/
    map.py           # Fix close_gates() legacy scan hardcode
```

### Pattern: Debug Module (D-08 through D-10)

```python
# src/core/debug.py (NEW)
import pyxel

# Runtime god-mode toggles (D-09)
god_abilities = False    # Toggle 1: unlock all abilities
god_invincible = False   # Toggle 2: no damage
god_infinite_juice = False  # Toggle 3: infinite juice

# Key combos for debug builds
def update():
    """Call from Game.update() to check toggle keys."""
    global god_abilities, god_invincible, god_infinite_juice
    # Example: Ctrl+1, Ctrl+2, Ctrl+3
    if pyxel.btn(pyxel.KEY_CTRL) and pyxel.btnp(pyxel.KEY_1):
        god_abilities = not god_abilities
    if pyxel.btn(pyxel.KEY_CTRL) and pyxel.btnp(pyxel.KEY_2):
        god_invincible = not god_invincible
    if pyxel.btn(pyxel.KEY_CTRL) and pyxel.btnp(pyxel.KEY_3):
        god_infinite_juice = not god_infinite_juice
```

Player reads `debug.god_abilities` instead of `DEBUG_ALL_ABILITIES`. Key difference: debug flags are runtime toggles, never set at import time, so tests are unaffected.

### Anti-Patterns to Avoid
- **Naming collision with game_state:** Do NOT reuse `self.game_state` for event flags -- it's already a string for game flow state (`"PLAYING"` / `"WON"`).
- **Import-time side effects in debug:** God-mode flags must default to `False` and only change via runtime key press. Tests must NEVER import/depend on debug state.
- **Overly broad gate scan removal:** `close_gates()`/`open_gates()` are still used by switch tiles (TILE_SWITCH). Only the boss-trigger call site changes to use event flags instead. The methods themselves should still work for switch-triggered gates.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Event system | Event bus / pub-sub | Direct dict lookup `game_state_flags[event_id]` | D-03 explicitly locks this -- simplest pattern for a prototype |
| Test fixtures | Complex conftest hierarchy | Per-test explicit state setup via `make_player(**overrides)` | Existing pattern in test_bubble_shield.py works well |

## Common Pitfalls

### Pitfall 1: game_state Name Collision
**What goes wrong:** Adding event flags to `self.game_state` which is already the string `"PLAYING"`/`"WON"`.
**Why it happens:** Natural naming instinct. The CONTEXT.md references `game_state[event_id]` but main.py already uses `game_state` for something else.
**How to avoid:** Use `self.event_flags` or `self.game_state_flags` as a new dict attribute.
**Warning signs:** `game_state` becomes a dict somewhere and the win-screen check on line 288 (`if self.game_state == "WON"`) breaks.

### Pitfall 2: Projectile Mock Returns Truthy MagicMock
**What goes wrong:** `Projectile.__init__` calls `self.level_map.check_collision()` on line 19 of projectile.py. If `level_map` is a bare MagicMock, `check_collision` returns a truthy MagicMock, and the projectile immediately deactivates.
**Why it happens:** Test creates `Game()` then replaces `game.level_map = MagicMock()` but doesn't configure return values.
**How to avoid:** Fix mock setup: `game.level_map.check_collision.return_value = False`. This is the root cause of test_phase05_gaps::test_combat_projectile_collision failure.
**Warning signs:** Projectile `is_active` is False immediately after construction.

### Pitfall 3: Shield Drain Tests and has_shield_t2
**What goes wrong:** `DEBUG_ALL_ABILITIES=True` sets `has_shield_t2=True` in Player.__init__ (line 52). Shield T2 reduces water drain from 0.5 to 0.0 via `max(0, drain - SHIELD_T2_DRAIN_REDUCTION)`. Zero drain means `slime.consume()` is never called, so tests asserting `consume.assert_called_once_with(0.5)` fail.
**Why it happens:** Tests use `make_player(has_shield=True)` which creates a real Player, but Player.__init__ runs the DEBUG_ALL_ABILITIES block before the override is applied.
**How to avoid:** Remove DEBUG_ALL_ABILITIES from constants.py. Player.__init__ abilities all default to False. Tests explicitly set needed flags via overrides.
**Warning signs:** Drain tests pass with `has_shield_t2=False` but fail when it's True.

### Pitfall 4: Sprite Test Isolation
**What goes wrong:** `test_draw_sprite_offset_standard` in test_sprite_scale.py fails when run in suite but passes in isolation.
**Why it happens:** Other test files (e.g., test_phase05_gaps.py) do heavy pyxel mocking at module level, replacing `pyxel.blt` before test_sprite_scale.py runs. The `monkeypatch.setattr(pyxel, 'blt', mock_blt)` then patches the already-mocked module.
**How to avoid:** Ensure test_sprite_scale.py's monkeypatch targets the correct object. The draw_sprite function imports pyxel at module level, so `monkeypatch.setattr("src.core.sprite_utils.pyxel.blt", mock_blt)` may be needed instead of patching pyxel directly.
**Warning signs:** KeyError or assertion failure only when running full suite, not in isolation.

### Pitfall 5: close_gates Still Needed for Switches
**What goes wrong:** Removing `close_gates()`/`open_gates()` entirely breaks switch-tile functionality.
**Why it happens:** The boss trigger in main.py is NOT the only caller -- `toggle_switch()` on line 170 calls `open_gates()`.
**How to avoid:** Keep the methods functional. Only change the boss-fight integration point in main.py to use event flags. The IntGrid value 4 ("gate") and TILE_GATE constant stay in the system for switch-triggered gates.
**Warning signs:** Switches stop working after "removing" gate logic.

## Code Examples

### Fix: close_gates() Legacy Scan (D-18)

Current (broken for 320px rooms):
```python
# map.py lines 197-198
for ty in range(ty_start, ty_start + 16):
    for tx in range(tx_start, tx_start + 16):
```

Fixed:
```python
for ty in range(ty_start, ty_start + tiles_h):
    for tx in range(tx_start, tx_start + tiles_w):
```

`tiles_w` and `tiles_h` are already computed on line 187: `tiles_w, tiles_h = VIEWPORT_W // TILE_SIZE, VIEWPORT_H // TILE_SIZE` (= 40, 22).

### Fix: Remove ITEM_FRAMES["DRILL"] (D-14)

Current (items.py:46):
```python
ITEM_FRAMES = {
    "ENERGY": 0,
    "MISSILE": 1,
    "DRILL": 2,      # <-- DELETE THIS LINE
    "DASH_PICKUP": 2,
    "SHIELD_PICKUP": 3,
    "BOOST_PICKUP": 4,
    "SHIELD_T2": 5,
}
```

### Fix: Bubble Shield Drain Tests (D-11)

Root cause: `DEBUG_ALL_ABILITIES=True` in constants.py sets `has_shield_t2=True` in Player.__init__.

Fix: Remove the entire `if DEBUG_ALL_ABILITIES:` block from player.py (lines 48-53) and the `DEBUG_ALL_ABILITIES = True` constant from constants.py (line 2). Tests already use `make_player(has_shield=True)` with explicit overrides.

### Fix: test_combat_projectile_collision (D-12)

Root cause: `game.level_map = MagicMock()` returns truthy for all calls, including `check_collision()`. The Projectile constructor checks collision on init (projectile.py:19), so the projectile deactivates immediately.

Fix: Configure mock before creating projectile:
```python
game.level_map = MagicMock()
game.level_map.check_collision.return_value = False
game.level_map.find_tile.return_value = None
```

### Fix: test_sprite_scale.py Isolation (D-12)

Root cause: test_phase05_gaps.py replaces `sys.modules["pyxel"]` at module level (line 25). When test_sprite_scale.py runs after it in the suite, `pyxel` is the MagicMock, and `monkeypatch.setattr(pyxel, 'blt', mock_blt)` fails because the mock's attribute access works differently.

Fix: Patch the correct target in test_sprite_scale.py:
```python
monkeypatch.setattr("src.core.sprite_utils.pyxel.blt", mock_blt)
```
Or add pyxel mock setup at the top of test_sprite_scale.py matching the pattern used by other test files.

### Entity Schema Changes (D-01, D-02)

Add to Door entity in entity-schema.json:
```json
"action": {
    "type": "string",
    "required": false,
    "default": null,
    "enum": ["spit", "kick", "drill_dive", "slime_ram", "slime_boost", "event"],
    "description": "Ability required to open the door. 'event' checks game_state for event_id."
},
"event_id": {
    "type": "string",
    "required": false,
    "default": null,
    "description": "For action='event': the game_state flag key to check (e.g. 'boss_defeated')."
}
```

## Test Failure Root Cause Summary

| # | Test | Root Cause | Fix Strategy | Confidence |
|---|------|-----------|--------------|------------|
| 1-3 | test_bubble_shield.py drain tests (3) | DEBUG_ALL_ABILITIES forces has_shield_t2=True, water drain becomes 0 | Remove DEBUG_ALL_ABILITIES | HIGH |
| 4 | test_drill_retcon.py no_drill_item_type | ITEM_FRAMES["DRILL"] dead entry in items.py | Delete the "DRILL": 2 line | HIGH |
| 5 | test_phase05_gaps.py projectile_collision | MagicMock level_map returns truthy for check_collision, projectile self-deactivates | Configure mock return value | HIGH |
| 6 | test_sprite_scale.py draw_sprite_offset | pyxel module replaced by MagicMock from earlier test file, monkeypatch targets wrong object | Patch sprite_utils.pyxel.blt or add local pyxel mock | HIGH |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | none (default discovery) |
| Quick run command | `python -m pytest tests/ -x --tb=short` |
| Full suite command | `python -m pytest tests/ --tb=short` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MAP-02 | Event-gated doors open when game_state flag is set | unit | `python -m pytest tests/test_event_doors.py -x` | No -- Wave 0 |
| MAP-02 | close_gates legacy scan uses correct room dimensions | unit | `python -m pytest tests/test_gate_scan.py -x` | No -- Wave 0 |
| ABL-02 | CRACKED_V breaking via Drill Dive and Boost | manual | Visual verification + write VERIFICATION.md | N/A -- manual |
| TECH-DEBT | 6 test failures resolved (0 failures in suite) | regression | `python -m pytest tests/ --tb=short` | Yes -- existing |
| TECH-DEBT | DEBUG_ALL_ABILITIES removed, god-mode runtime | unit | `python -m pytest tests/test_debug.py -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/ -x --tb=short`
- **Per wave merge:** `python -m pytest tests/ --tb=short`
- **Phase gate:** Full suite green (0 failures) before /gsd:verify-work

### Wave 0 Gaps
- [ ] `tests/test_event_doors.py` -- covers event-gated door opening/closing on room entry
- [ ] `tests/test_debug.py` -- covers god-mode toggles don't affect default state
- [ ] No conftest changes needed -- existing test patterns are sufficient

## Sources

### Primary (HIGH confidence)
- Direct code inspection: map.py, player.py, slime.py, items.py, map_entities.py, main.py, constants.py
- Direct test execution: confirmed all 6 failures with root causes (pytest 9.0.2, Python 3.13.11)
- entity-schema.json: current v0.2.0 schema structure
- v1.1-MILESTONE-AUDIT.md: complete gap analysis

### Secondary (MEDIUM confidence)
- 14-CONTEXT.md: all decisions locked by user
- 14-DISCUSSION-LOG.md: background on DEBUG_ALL_ABILITIES decision

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - pure Pyxel/Python, no new libraries needed
- Architecture: HIGH - all patterns verified against existing codebase
- Pitfalls: HIGH - all 6 test failures reproduced and root-caused
- Test fixes: HIGH - each fix verified by tracing exact code paths

**Research date:** 2026-03-29
**Valid until:** 2026-04-28 (stable -- no external dependency changes expected)
