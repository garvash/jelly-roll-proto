"""Diagnostic overlay manager — F2-F5 toggle flags and visual overlays.

Centralized post-draw overlay system (D-01). Separate from debug.py god-mode
toggles (D-02). Pure visual — no text readouts in overlays (D-03).

Phase 27 Plan 01: F2 hitbox wireframes, F3 velocity arrows + frame-time graph.
Phase 27 Plan 02: F4 input blips, F5 slime follow overlay.
"""
import time
from collections import deque

import pyxel

from src.core.constants import (
    VIEWPORT_W, VIEWPORT_H,
    SLIME_MAX_DIST, SLIME_REFORM_DIST,
)
from src.anim import event_bus

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

# --- F4 Input blip constants (D-04, UI-SPEC) ---
_coyote_blips = deque(maxlen=32)   # (x, y, frame_count) — ground-leave positions
_jump_blips = deque(maxlen=32)     # (x, y, frame_count) — jump-press positions
_land_blips = deque(maxlen=32)     # (x, y, frame_count) — landing positions
_buffer_blips = deque(maxlen=32)   # (x, y, frame_count) — early jump-press positions

BLIP_RADIUS = 2                   # Pixels
BLIP_FADE_FRAMES = 30             # 0.5s at 60fps — full color 15 frames, dim 15 frames
BLIP_FULL_FRAMES = 15             # First half at full color

# Blip palette colors (per UI-SPEC F4 contract)
_COYOTE_COLOR = 11       # Green — ground-leave blip
_COYOTE_DIM_COLOR = 13   # Light grey — faded coyote blip
_JUMP_COLOR = 8          # Red — jump-press blip
_JUMP_DIM_COLOR = 2      # Dark purple — faded jump blip
_CONNECTOR_COLOR = 10    # Yellow — coyote-to-jump connector line
_BUFFER_COLOR = 12       # Blue — buffer blip
_BUFFER_DIM_COLOR = 1    # Dark blue — faded buffer blip
_BUFFER_CONNECTOR_COLOR = 14  # Pink — buffer-to-land connector

# --- F5 Slime overlay constants (D-05, UI-SPEC) ---
_slime_stuck_frames = 0            # Consecutive frames with velocity < threshold
STUCK_VEL_THRESHOLD = 0.1         # Velocity magnitude threshold
STUCK_FRAME_THRESHOLD = 10        # Frames before stuck indicator shows
_STUCK_X_SIZE = 4                 # Arm length of flashing X indicator

# Slime trail age-band colors
_TRAIL_RECENT_COLOR = 11  # Green (indices 0-10)
_TRAIL_MID_COLOR = 3      # Dark green (indices 11-20)
_TRAIL_OLD_COLOR = 5      # Dark grey (indices 21+)

# Distance circle colors
_MAX_DIST_COLOR = 8       # Red — SLIME_MAX_DIST circle
_REFORM_DIST_COLOR = 10   # Yellow — SLIME_REFORM_DIST circle
_TARGET_DOT_COLOR = 14    # Pink — follow target point
_CATCHUP_COLOR = 12       # Blue — catch-up arrow
_CATCHUP_ARROW_LEN = 6    # Length in pixels of catch-up direction arrow

# --- Room transition blip clearing (Pitfall 6) ---
_prev_cam_x = 0.0
_prev_cam_y = 0.0
ROOM_CHANGE_THRESHOLD = 160  # Half viewport width — camera snap detection

# --- Game reference for event callbacks ---
_game_ref = None


def init(game):
    """Subscribe to event bus for F4 blip placement. Lazy init prevents
    duplicate subscriptions (T-27-03, Pitfall 5)."""
    global _initialized, _game_ref
    if _initialized:
        return
    _game_ref = game
    event_bus.subscribe("fall_start", _on_fall_start)
    event_bus.subscribe("jump_start", _on_jump_start)
    event_bus.subscribe("land", _on_land)
    _initialized = True


def update():
    """Toggle F2-F5 overlay flags and update frame-time buffer.

    Called from Game.update() after debug.update(). No Ctrl modifier needed
    (unlike debug.py).
    """
    global show_hitboxes, show_velocity, show_input, show_slime
    global _prev_cam_x, _prev_cam_y
    if pyxel.btnp(pyxel.KEY_F2):
        show_hitboxes = not show_hitboxes
    if pyxel.btnp(pyxel.KEY_F3):
        show_velocity = not show_velocity
    if pyxel.btnp(pyxel.KEY_F4):
        show_input = not show_input
    if pyxel.btnp(pyxel.KEY_F5):
        show_slime = not show_slime
    _update_frame_time()

    # Clear blips on room transition (Pitfall 6 — camera snap detection)
    if _game_ref is not None:
        dx = abs(_game_ref.cam_x - _prev_cam_x)
        dy = abs(_game_ref.cam_y - _prev_cam_y)
        if dx > ROOM_CHANGE_THRESHOLD or dy > ROOM_CHANGE_THRESHOLD:
            _coyote_blips.clear()
            _jump_blips.clear()
            _land_blips.clear()
            _buffer_blips.clear()
        _prev_cam_x = _game_ref.cam_x
        _prev_cam_y = _game_ref.cam_y


def _update_frame_time():
    """Record frame delta in milliseconds using perf_counter."""
    global _last_frame_time
    now = time.perf_counter()
    if _last_frame_time > 0:
        delta_ms = (now - _last_frame_time) * 1000.0
        _frame_times.append(delta_ms)
    _last_frame_time = now


# --- Event callbacks for F4 blip placement ---

def _on_fall_start():
    """Record where player left the ground (coyote trigger point)."""
    if _game_ref is None:
        return
    p = _game_ref.player
    _coyote_blips.append((p.x + p.w // 2, p.y + p.h, pyxel.frame_count))


def _on_jump_start():
    """Record where player pressed jump. If airborne without coyote, also
    record as a buffer blip."""
    if _game_ref is None:
        return
    p = _game_ref.player
    cx = p.x + p.w // 2
    by = p.y + p.h
    _jump_blips.append((cx, by, pyxel.frame_count))
    # Detect buffered jump: airborne and no coyote time remaining
    if not p.is_grounded and p.coyote_timer <= 0:
        _buffer_blips.append((cx, by, pyxel.frame_count))


def _on_land():
    """Record where player landed."""
    if _game_ref is None:
        return
    p = _game_ref.player
    _land_blips.append((p.x + p.w // 2, p.y + p.h, pyxel.frame_count))


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
    """Draw F4 input state blips: coyote/buffer spatial visualization (D-04).

    Coyote blips (green) at ground-leave positions, jump blips (red) at
    jump-press positions. Connector lines (yellow) show the spatial gap.
    Buffer blips (blue) for early jump presses, with pink connectors to land.
    Active timer indicators as single pixels below/above player.
    No text labels per D-03, D-06.
    """
    now = pyxel.frame_count
    p = game.player

    # Draw coyote blips (ground-leave positions)
    for bx, by, frame in _coyote_blips:
        age = now - frame
        if age > BLIP_FADE_FRAMES:
            continue
        color = _COYOTE_COLOR if age <= BLIP_FULL_FRAMES else _COYOTE_DIM_COLOR
        pyxel.circ(bx, by, BLIP_RADIUS, color)

    # Draw jump-press blips
    for bx, by, frame in _jump_blips:
        age = now - frame
        if age > BLIP_FADE_FRAMES:
            continue
        color = _JUMP_COLOR if age <= BLIP_FULL_FRAMES else _JUMP_DIM_COLOR
        pyxel.circ(bx, by, BLIP_RADIUS, color)

    # Draw connector line between most recent visible coyote and jump blips
    recent_coyote = _most_recent_visible(_coyote_blips, now)
    recent_jump = _most_recent_visible(_jump_blips, now)
    if recent_coyote and recent_jump:
        pyxel.line(recent_coyote[0], recent_coyote[1],
                   recent_jump[0], recent_jump[1], _CONNECTOR_COLOR)

    # Draw buffer blips (early jump presses while airborne)
    for bx, by, frame in _buffer_blips:
        age = now - frame
        if age > BLIP_FADE_FRAMES:
            continue
        color = _BUFFER_COLOR if age <= BLIP_FULL_FRAMES else _BUFFER_DIM_COLOR
        pyxel.circ(bx, by, BLIP_RADIUS, color)

    # Draw buffer-to-land connector
    recent_buffer = _most_recent_visible(_buffer_blips, now)
    recent_land = _most_recent_visible(_land_blips, now)
    if recent_buffer and recent_land:
        pyxel.line(recent_buffer[0], recent_buffer[1],
                   recent_land[0], recent_land[1], _BUFFER_CONNECTOR_COLOR)

    # Active coyote timer indicator — green pixel below player feet
    p_cx = p.x + p.w // 2
    if hasattr(p, "coyote_timer") and p.coyote_timer > 0:
        pyxel.pset(p_cx, p.y + p.h + 1, _COYOTE_COLOR)

    # Active buffer timer indicator — blue pixel above player head
    if hasattr(p, "jump_buffer_timer") and p.jump_buffer_timer > 0:
        pyxel.pset(p_cx, p.y - 1, _BUFFER_COLOR)


def _most_recent_visible(blip_deque, now):
    """Return (x, y) of most recent blip still within fade window, or None."""
    for bx, by, frame in reversed(blip_deque):
        if now - frame <= BLIP_FADE_FRAMES:
            return (bx, by)
    return None


def _draw_slime_overlay(game):
    """Draw F5 slime follow overlay: breadcrumb trail, distance circles,
    target dot, stuck detection, and catch-up arrow (D-05).

    All slime access is read-only (T-27-01). Stuck counter is overlay-internal
    state, not entity state.
    """
    global _slime_stuck_frames

    s = game.slime
    p = game.player
    player_cx = p.x + p.w // 2
    player_cy = p.y + p.h // 2

    # Breadcrumb trail from history deque — DO NOT modify deque (T-27-01)
    for i, (hx, hy) in enumerate(s.history):
        if i <= 10:
            color = _TRAIL_RECENT_COLOR
        elif i <= 20:
            color = _TRAIL_MID_COLOR
        else:
            color = _TRAIL_OLD_COLOR
        pyxel.pset(hx, hy, color)

    # Distance threshold circles centered on player
    pyxel.circb(player_cx, player_cy, int(SLIME_MAX_DIST), _MAX_DIST_COLOR)
    pyxel.circb(player_cx, player_cy, int(SLIME_REFORM_DIST), _REFORM_DIST_COLOR)

    # Follow target point — pink dot
    pyxel.circ(s.target_x, s.target_y, 1, _TARGET_DOT_COLOR)

    # Stuck detection — overlay-internal counter (not entity state)
    vel_mag = (s.dx ** 2 + s.dy ** 2) ** 0.5
    if vel_mag < STUCK_VEL_THRESHOLD:
        _slime_stuck_frames += 1
    else:
        _slime_stuck_frames = 0

    # Stuck indicator — flashing red X at slime center
    if _slime_stuck_frames > STUCK_FRAME_THRESHOLD:
        scx = s.x + s.w // 2
        scy = s.y + s.h // 2
        if pyxel.frame_count % 2 == 0:
            pyxel.line(scx - _STUCK_X_SIZE, scy - _STUCK_X_SIZE,
                       scx + _STUCK_X_SIZE, scy + _STUCK_X_SIZE, _JUMP_COLOR)
            pyxel.line(scx + _STUCK_X_SIZE, scy - _STUCK_X_SIZE,
                       scx - _STUCK_X_SIZE, scy + _STUCK_X_SIZE, _JUMP_COLOR)

    # Catch-up arrow — blue line from slime toward target when actively chasing
    if vel_mag > STUCK_VEL_THRESHOLD:
        dist_to_target_sq = (s.target_x - s.x) ** 2 + (s.target_y - s.y) ** 2
        if dist_to_target_sq > SLIME_REFORM_DIST ** 2:
            scx = s.x + s.w // 2
            scy = s.y + s.h // 2
            dist = dist_to_target_sq ** 0.5
            if dist > 0:
                dx_norm = (s.target_x - scx) / dist
                dy_norm = (s.target_y - scy) / dist
                end_x = scx + int(dx_norm * _CATCHUP_ARROW_LEN)
                end_y = scy + int(dy_norm * _CATCHUP_ARROW_LEN)
                pyxel.line(scx, scy, end_x, end_y, _CATCHUP_COLOR)
