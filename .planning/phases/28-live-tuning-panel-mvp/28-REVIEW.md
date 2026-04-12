---
phase: 28-live-tuning-panel-mvp
reviewed: 2026-04-12T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - src/ui/widgets.py
  - src/ui/panel.py
  - src/ui/presets.py
  - src/ui/journal.py
  - main.py
findings:
  critical: 1
  warning: 6
  info: 4
  total: 11
status: issues_found
---

# Phase 28: Code Review Report

**Reviewed:** 2026-04-12
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Phase 28 adds a live-tuning overlay panel (F1), preset save/load, and a crash-recovery journal. The architecture is sound: widgets are well-isolated, the panel uses lazy initialization, and the atomic write pattern in `presets.py` is correctly implemented. The journal's per-edit fsync is intentional for crash safety and acceptable at this scale.

The main concerns are: a monkey-patch of `tuning.set_value` in `__init__` that silently swallows `AttributeError` (allowing an invalid key to produce a `None` old-value rather than erroring), an unclosed journal file handle on normal exit, and several places where the panel's restricted layout constants diverge from the imported UI-SPEC constants in a way that can cause invisible widgets or mis-aligned scroll math.

---

## Critical Issues

### CR-01: Journal file handle never closed on normal program exit

**File:** `main.py:184` / `src/ui/journal.py:24`

**Issue:** `self._tuning_journal = Journal()` opens a file handle in `Game.__init__`. `Journal.close()` exists but is never called. `pyxel.run()` blocks until the window is closed, then returns; nothing calls `self._tuning_journal.close()` after `pyxel.run()` returns. On most OSes this means the OS reclaims the handle, but on Windows buffered writes that were flushed to the OS but not closed can be left in an inconsistent state. More concretely, because `record()` calls `os.fsync()` on every write the data is safe, but the handle leaks and the session file is never explicitly closed, which will cause `ResourceWarning` in dev and could block the file on Windows if another process tries to read it while the game is still open.

**Fix:**
```python
# In main.py, after pyxel.run() returns:
pyxel.run(self.update, self.draw)
self._tuning_journal.close()   # Ensure file is closed on normal exit
```

---

## Warnings

### WR-01: `_journaled_set_value` silently swallows `AttributeError`, records `None` as old value

**File:** `main.py:198-210`

**Issue:** The monkey-patch wrapper catches `AttributeError` on `getattr(tuning, key)` and falls through with `old = None`, then calls the real `set_value`. If `set_value` itself raises `KeyError` for an unknown key the journal records `(key, None, value)` before the error propagates. This creates misleading journal entries and masks the real error. The `AttributeError` path should either re-raise or skip the journal entry entirely.

```python
def _journaled_set_value(key, value):
    if tuning_panel.show_panel:
        try:
            old = getattr(tuning, key)
        except AttributeError:
            old = None          # <-- recorded even if set_value is about to fail
        _original_set_value(key, value)   # may raise KeyError
        _journal_ref.record(key, old, value, pyxel.frame_count)
```

**Fix:**
```python
def _journaled_set_value(key, value):
    if tuning_panel.show_panel:
        old = getattr(tuning, key, None)   # None is fine as sentinel
        _original_set_value(key, value)    # let KeyError propagate unchanged
        _journal_ref.record(key, old, value, pyxel.frame_count)
    else:
        _original_set_value(key, value)
```

### WR-02: Panel content layout uses `PANEL_MAX_H` (60px) but widgets use `CONTENT_Y` (24px) as `content_top`

**File:** `src/ui/panel.py:221-227` and `src/ui/panel.py:239-243`

**Issue:** `CONTENT_Y` imported from `widgets.py` equals `TAB_BAR_H + HEADER_H = 24`. But the panel is top-justified and uses `PANEL_MAX_H = 60` to derive its layout. Inside `update()` the scroll math uses locally-derived `_content_y = PANEL_TOP + TAB_BAR_H + HEADER_H` (also 24) and `_content_h = PANEL_MAX_H - TAB_BAR_H - HEADER_H = 36`. Inside `_update_active_tab_widgets()` the same `content_top = 24` and `content_bottom = 24 + 36 = 60` are recalculated. This is self-consistent, **but** `widgets.py` also exports `CONTENT_H = 156` (the full-panel UI-SPEC value). Nothing in the draw path currently imports `CONTENT_H` from widgets and uses it instead of the locally-derived 36px height, so the current code is internally consistent — but the divergence is a latent bug: if someone replaces the local recalculation with the exported constant `CONTENT_H` the scroll bounds and clip rect will be wrong by 120px.

**Fix:** Remove or explicitly shadow `CONTENT_H` in `panel.py` to avoid the ambiguity:
```python
# At top of panel.py, after imports, add:
_CONTENT_H = PANEL_MAX_H - TAB_BAR_H - HEADER_H  # 36px (not the 156px full-screen value)
# Replace all three inline recalculations with _CONTENT_H
```

### WR-03: `_commit_edit` does not clamp when `baseline == 0` — any typed value is accepted

**File:** `src/ui/widgets.py:225-234`

**Issue:** The clamp block is guarded by `if self.baseline != 0:`. When baseline is exactly 0 (e.g., a tuning key with a zero default), the parsed value is written directly to tuning with no range check. This is called out as T-28-02 behavior but is only partially addressed. A user can type `-9999` or `99999` into a zero-baseline slider and it will be applied.

**Fix:** Either document this as intentional and add a comment, or apply an absolute fallback clamp:
```python
if self.baseline != 0:
    low = self.baseline * 0.25
    high = self.baseline * 4.0
    if low > high:
        low, high = high, low
    parsed = max(low, min(high, parsed))
# else: zero baseline -- no ratio-relative clamp possible; value is written as-is
```
If zero-baseline keys exist in the schema, add a minimum absolute clamp (e.g., `max(0.0, parsed)`) to prevent negative values for non-negative quantities.

### WR-04: Preset load errors silently swallowed in `update()` — user gets no feedback

**File:** `main.py:444-451`

**Issue:** The preset hotkey handler catches all exceptions with `except Exception: pass`. When a slot file does not exist or is corrupt, the panel shows nothing (no error message). The `set_error()` API exists in `panel.py` specifically for this purpose but is not called here.

```python
except Exception:
    pass  # Load fail -- header shows error via panel
```
The comment says "header shows error via panel" but no code actually does that.

**Fix:**
```python
except Exception as exc:
    tuning_panel.set_error(f"Load failed: slot {slot}", duration=120)
```

### WR-05: `Slider.draw` reads live tuning value via `getattr(tuning, self.key)` — will raise `AttributeError` on deleted keys

**File:** `src/ui/widgets.py:244`

**Issue:** `current = getattr(tuning, self.key)` has no fallback. If a key is removed from the tuning schema after the panel is initialized (possible during hot-reload or schema evolution), the draw call raises an unhandled `AttributeError` which crashes the draw loop. The `load_preset` function in `presets.py` already guards against this for loading (line 61), but the display path does not.

**Fix:**
```python
current = getattr(tuning, self.key, self.baseline)
```

### WR-06: `save_preset` alias derived from `get_preset_alias` which reads the *existing* file — on first save the alias is always `"slot N"`

**File:** `main.py:188-193`

**Issue:** The `_panel_save` closure calls `presets.get_preset_alias(slot)` to get the alias, then passes it to `save_preset`. On a first save when no file exists, `get_preset_alias` returns `f"slot {slot}"` (the fallback). This is probably acceptable for the MVP, but it means the alias is always reset to the generic name on every save, overwriting any alias previously stored in the file.

**Fix:** Either pass the current `_active_preset_alias` from panel state instead, or document that aliases are read-only from file:
```python
def _panel_save():
    slot = tuning_panel.get_active_preset_slot()
    if slot >= 0:
        alias = tuning_panel._active_preset_alias  # use in-memory alias, not file
        presets.save_preset(slot, alias)
```

---

## Info

### IN-01: Magic number `6` for flash timer duration repeated in three places

**File:** `src/ui/widgets.py:181, 343`

**Issue:** `self.flash_timer = 6` appears twice (once in `Slider`, once in `BoolToggle`) without a named constant. Project memory notes to use named constants for all numeric literals.

**Fix:**
```python
_FLASH_DURATION = 6   # frames -- reset arrow yellow flash
# ...
self.flash_timer = _FLASH_DURATION
```

### IN-02: `BoolToggle` has `CHECKBOX_SIZE = 6` as a local variable inside `draw()`

**File:** `src/ui/widgets.py:359`

**Issue:** `CHECKBOX_SIZE = 6` is defined inside the method body on every call. This is a magic number defined as a local variable rather than a module-level constant. Minor but inconsistent with the rest of the layout constants at the top of `widgets.py`.

**Fix:** Move to module-level constants block:
```python
CHECKBOX_SIZE = 6     # px square -- bool toggle checkbox
```

### IN-03: `_draw_footer` slow-mo detection queries input directly rather than using the computed `_slow_mo` state

**File:** `src/ui/panel.py:402-404`

**Issue:** `_draw_footer` calls `pyxel.btn(pyxel.KEY_TAB)` directly instead of reading the computed `_slow_mo` variable from `update()`. This is fine functionally (same result), but the draw path and update path compute slow-mo state independently. If the slow-mo condition ever becomes more complex (e.g., gated on panel open), the footer could show a stale or inconsistent indicator.

**Fix:** Pass slow-mo state as a parameter or expose it as a module-level flag set in `update()`.

### IN-04: Preset hotkey import inside per-frame `update()` loop

**File:** `main.py:447`

**Issue:** `from src.ui import presets` is called inside `update()` on every key press. Python caches module imports so this is not a correctness problem, but it is a style inconsistency — all other imports are at the top of the file. The import inside `__init__` at line 187 already imports `presets`; the one inside `update()` is redundant.

**Fix:** Move the `presets` import to the top-level import block in `main.py` (it is already imported in `__init__`, so the per-frame import is purely redundant).

---

_Reviewed: 2026-04-12_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
