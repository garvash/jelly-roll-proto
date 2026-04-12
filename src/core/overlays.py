"""Diagnostic overlay manager — F2-F5 toggle flags and visual overlays.

Centralized post-draw overlay system (D-01). Separate from debug.py god-mode
toggles (D-02). Pure visual — no text readouts in overlays (D-03).

Phase 27 Plan 01: F2 hitbox wireframes, F3 velocity arrows + frame-time graph.
Phase 27 Plan 02: F4 input blips, F5 slime follow overlay.
"""
import time
from collections import deque

import pyxel

from src.core.constants import VIEWPORT_W, VIEWPORT_H

# --- Toggle flags (module-level, per D-01/D-02) ---
show_hitboxes = False   # F2
show_velocity = False   # F3
show_input = False      # F4
show_slime = False      # F5

# --- Pre-allocated buffers ---
_frame_times = deque(maxlen=64)   # 64 frames of timing data for graph
_last_frame_time = 0.0            # perf_counter timestamp of previous frame
_initialized = False              # Lazy init guard for event bus subscriptions

# --- Velocity arrow constants ---
VEL_SCALE = 8           # Pixels per unit velocity
ARROW_MIN_LEN = 8       # Minimum arrow length in pixels
ARROW_MAX_LEN = 32      # Maximum arrow length in pixels

# --- Hitbox palette colors (per UI-SPEC) ---
_PLAYER_COLOR = 8       # Red
_SLIME_COLOR = 11       # Green
_ENEMY_COLOR = 9        # Orange
_PROJ_COLOR = 10        # Yellow
_STATIC_COLOR = 6       # Light grey
_BOSS_COLOR = 2         # Dark purple

# --- Velocity palette colors ---
_H_VEL_COLOR = 8        # Red — horizontal component
_V_VEL_COLOR = 12       # Blue — vertical component

# --- Frame-time graph constants ---
_GRAPH_W = 64           # Width in pixels
_GRAPH_H = 24           # Height in pixels
_GRAPH_MARGIN = 2       # Margin from viewport edge
_GRAPH_MAX_MS = 33.0    # Y-axis ceiling in milliseconds
_TARGET_MS = 16.67      # 60fps target frame time
_GRAPH_BG_COLOR = 1     # Dark blue background
_GRAPH_GOOD_COLOR = 11  # Green — under budget
_GRAPH_BAD_COLOR = 8    # Red — over budget
_GRAPH_TARGET_COLOR = 6 # Light grey — target line

# --- Arrowhead size ---
_CHEVRON_SIZE = 2       # 2px chevron at arrow tip


def init(game):
    """Placeholder for Plan 02 event bus subscription initialization."""
    global _initialized
    _initialized = True


def update():
    """Toggle F2-F5 overlay flags and update frame-time buffer.

    Called from Game.update() after debug.update(). No Ctrl modifier needed
    (unlike debug.py).
    """
    global show_hitboxes, show_velocity, show_input, show_slime
    if pyxel.btnp(pyxel.KEY_F2):
        show_hitboxes = not show_hitboxes
    if pyxel.btnp(pyxel.KEY_F3):
        show_velocity = not show_velocity
    if pyxel.btnp(pyxel.KEY_F4):
        show_input = not show_input
    if pyxel.btnp(pyxel.KEY_F5):
        show_slime = not show_slime
    _update_frame_time()


def _update_frame_time():
    """Record frame delta in milliseconds using perf_counter."""
    global _last_frame_time
    now = time.perf_counter()
    if _last_frame_time > 0:
        delta_ms = (now - _last_frame_time) * 1000.0
        _frame_times.append(delta_ms)
    _last_frame_time = now


def draw(game):
    """Draw all active overlays in world-space. Called at end of _draw_game_world().

    Draw order per UI-SPEC: F5 slime (behind), F2 hitboxes, F3 velocity, F4 input (top).
    """
    if show_slime:
        _draw_slime_overlay(game)
    if show_hitboxes:
        _draw_hitbox_overlay(game)
    if show_velocity:
        _draw_velocity_overlay(game)
    if show_input:
        _draw_input_overlay(game)


def draw_indicator():
    """Draw toggle status text in screen-space (after camera reset).

    Active keys in white (palette 7), inactive in light grey (palette 13).
    Background: dark blue (palette 1) rect behind text for readability.
    Only shown when at least one overlay is active.
    """
    if not any([show_hitboxes, show_velocity, show_input, show_slime]):
        return  # No indicator when all overlays off
    labels = [("F2", show_hitboxes), ("F3", show_velocity),
              ("F4", show_input), ("F5", show_slime)]
    # Background bar — 4 labels * 16px spacing + 4px padding = 68px
    _LABEL_SPACING = 16
    _BAR_PADDING = 4
    bar_w = len(labels) * _LABEL_SPACING + _BAR_PADDING
    _BAR_HEIGHT = 10
    pyxel.rect(0, 0, bar_w, _BAR_HEIGHT, 1)
    x = 2  # status_text_margin per UI-SPEC
    _TEXT_Y = 2
    for label, active in labels:
        color = 7 if active else 13
        pyxel.text(x, _TEXT_Y, label, color)
        x += _LABEL_SPACING


def _draw_hitbox_overlay(game):
    """Draw wireframe hitboxes for all entities. Per UI-SPEC color contract.

    Pure visual per D-03 — NO text labels on any entity.
    All entity access is read-only (T-27-01).
    """
    # Player hitbox — red
    p = game.player
    pyxel.rectb(p.x, p.y, p.w, p.h, _PLAYER_COLOR)

    # Slime hitbox — green (only if visible)
    s = game.slime
    if not s.is_fused and not s.is_dissipated:
        pyxel.rectb(s.x, s.y, s.w, s.h, _SLIME_COLOR)

    # Enemy hitboxes — orange
    for e in game.enemies:
        pyxel.rectb(e.x, e.y, e.w, e.h, _ENEMY_COLOR)

    # Projectile hitboxes — yellow
    for proj in game.projectiles:
        pyxel.rectb(proj.x, proj.y, proj.w, proj.h, _PROJ_COLOR)

    # Door/static hitboxes — light grey
    for door in game.doors:
        pyxel.rectb(door.x, door.y, door.w, door.h, _STATIC_COLOR)

    # Boss hitbox — dark purple (only if boss exists)
    if game.mole:
        pyxel.rectb(game.mole.x, game.mole.y, game.mole.w, game.mole.h,
                     _BOSS_COLOR)


def _draw_velocity_overlay(game):
    """Draw velocity arrows for player and slime, plus frame-time graph.

    Arrow length = abs(velocity) * VEL_SCALE clamped to [ARROW_MIN_LEN, ARROW_MAX_LEN].
    Only draws component if abs(velocity) > 0.01.
    Arrowhead: 2px chevron at tip.
    """
    # Player velocity arrows
    p = game.player
    p_cx = p.x + p.w // 2
    p_cy = p.y + p.h // 2
    _draw_velocity_arrows(p_cx, p_cy, p.dx, p.dy)

    # Slime velocity arrows
    s = game.slime
    if not s.is_fused and not s.is_dissipated:
        s_cx = s.x + s.w // 2
        s_cy = s.y + s.h // 2
        _draw_velocity_arrows(s_cx, s_cy, s.dx, s.dy)

    # Frame-time graph (drawn in world-space, offset by camera)
    _draw_frame_time_graph(game)


def _draw_velocity_arrows(cx, cy, dx, dy):
    """Draw horizontal and vertical velocity arrows from a center point."""
    # Horizontal component — red
    if abs(dx) > 0.01:
        hlen = min(ARROW_MAX_LEN, max(ARROW_MIN_LEN, int(abs(dx) * VEL_SCALE)))
        end_x = cx + (hlen if dx > 0 else -hlen)
        pyxel.line(cx, cy, end_x, cy, _H_VEL_COLOR)
        # Arrowhead chevron
        chevron_dir = -1 if dx > 0 else 1
        pyxel.line(end_x, cy, end_x + chevron_dir * _CHEVRON_SIZE,
                   cy - _CHEVRON_SIZE, _H_VEL_COLOR)
        pyxel.line(end_x, cy, end_x + chevron_dir * _CHEVRON_SIZE,
                   cy + _CHEVRON_SIZE, _H_VEL_COLOR)

    # Vertical component — blue
    if abs(dy) > 0.01:
        vlen = min(ARROW_MAX_LEN, max(ARROW_MIN_LEN, int(abs(dy) * VEL_SCALE)))
        end_y = cy + (vlen if dy > 0 else -vlen)
        pyxel.line(cx, cy, cx, end_y, _V_VEL_COLOR)
        # Arrowhead chevron
        chevron_dir = -1 if dy > 0 else 1
        pyxel.line(cx, end_y, cx - _CHEVRON_SIZE,
                   end_y + chevron_dir * _CHEVRON_SIZE, _V_VEL_COLOR)
        pyxel.line(cx, end_y, cx + _CHEVRON_SIZE,
                   end_y + chevron_dir * _CHEVRON_SIZE, _V_VEL_COLOR)


def _draw_frame_time_graph(game):
    """Draw 64px wide, 24px tall frame-time graph at top-right of viewport.

    Drawn in world-space so must offset by camera position.
    Y-axis: 0ms at bottom, 33ms at top.
    Green (11) if under 16.67ms, red (8) if over.
    16.67ms target line in light grey (6).
    """
    graph_x = game.cam_x + VIEWPORT_W - _GRAPH_W - _GRAPH_MARGIN
    graph_y = game.cam_y + _GRAPH_MARGIN

    # Background rect
    pyxel.rect(graph_x, graph_y, _GRAPH_W, _GRAPH_H, _GRAPH_BG_COLOR)

    # Target line at 16.67ms
    target_y = graph_y + _GRAPH_H - int(_GRAPH_H * _TARGET_MS / _GRAPH_MAX_MS)
    pyxel.line(graph_x, target_y, graph_x + _GRAPH_W - 1, target_y,
               _GRAPH_TARGET_COLOR)

    # Draw frame-time columns (1px each, right-aligned)
    num_frames = len(_frame_times)
    for i, ft in enumerate(_frame_times):
        col_x = graph_x + (_GRAPH_W - num_frames) + i
        bar_h = min(_GRAPH_H, int(_GRAPH_H * ft / _GRAPH_MAX_MS))
        if bar_h < 1:
            bar_h = 1
        col_y = graph_y + _GRAPH_H - bar_h
        color = _GRAPH_GOOD_COLOR if ft <= _TARGET_MS else _GRAPH_BAD_COLOR
        pyxel.line(col_x, col_y, col_x, graph_y + _GRAPH_H - 1, color)


def _draw_input_overlay(game):
    """Stub — Plan 02 fills in coyote/buffer blip rendering."""
    pass


def _draw_slime_overlay(game):
    """Stub — Plan 02 fills in slime trail and distance circle rendering."""
    pass
