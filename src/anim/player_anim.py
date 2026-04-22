"""Phase 26 ANIM-01 + ANIM-03 player-specific animation wiring.

Defines the PlayerAnimDriver dataclass (D-01), the player clip table and
rules list (D-04/D-06), and the build_player_fsm() factory called from
Player.__init__ (see 26-02-PLAN).

Skeleton content only -- Phase 31 migrates clip data to
assets/anim-schema.json per ANIM-05. Rules stay in Python per D-05.
"""
from dataclasses import dataclass
from src.anim.anim_clip import AnimClip
from src.anim.state_machine import AnimFSM, Rule

# --- Named constants (project memory: no magic numbers) ---------------------
# v1.3 sprite u offsets for the 16x16 player sheet (image bank 1).
# Hardcoded formula replaced:  u = 16 + (pyxel.frame_count // 6 % 2) * 16
IDLE_U = 0
RUN_FRAME_A_U = 16
RUN_FRAME_B_U = 32
JUMP_U = 32
# Duration constants in pyxel ticks.
STATIC_CLIP_DURATION_TICKS = 1   # idle + jump are 1-frame holds
RUN_TOGGLE_DURATION_TICKS = 6    # v1.3 parity: 6 frames per run frame (// 6)

# --- Player state name constants (mirror src/entities/player.py state strings) ---
STATE_IDLE = "IDLE"
STATE_RUNNING = "RUNNING"
STATE_JUMPING = "JUMPING"
STATE_FALLING = "FALLING"
STATE_DIVING = "DIVING"   # Phase 31: drill spin clip predicate (D-05)

# --- Phase 31 ANIM-04 constants (no magic numbers per MEMORY) ----------------
# Transient counter durations (D-02, D-03, D-04, D-06)
LAND_SQUASH_FRAMES = 4            # D-02: ticks after is_grounded flips
TURN_SKID_FRAMES = 3              # D-03: ticks after facing flips
JUMP_CROUCH_FRAMES = 2            # D-04: ticks after jump_start emit
DRILL_RECOIL_PAUSE_FRAMES = 3     # D-06: AnimPlayer.pause_for ticks per block-break

# New sprite U offsets on bank 1 row y=0 (16 px stride; existing IDLE_U=0, RUN=16/32, JUMP=32).
# Phase 31 authors placeholder frames at these offsets on assets/sprites/player.png.
LAND_SQUASH_U = 48
TURN_SKID_U = 64
JUMP_CROUCH_U = 80
JUMP_STATIONARY_U = 96
JUMP_RUNNING_U = 112
DRILL_SPIN_FRAME_0_U = 128
DRILL_SPIN_FRAME_1_U = 144
DRILL_SPIN_FRAME_2_U = 160
DRILL_SPIN_FRAME_3_U = 176


@dataclass(slots=True)
class PlayerAnimDriver:
    state: str = STATE_IDLE
    is_grounded: bool = True
    facing: int = 1           # -1 or +1
    vy_sign: int = 0          # -1 / 0 / +1
    # Phase 31 additions:
    vx_sign: int = 0          # D-01 Metroid jump split
    prev_facing: int = 1      # D-03 turn_skid edge detection
    skid_ticks: int = 0       # D-03 transient countdown
    land_ticks: int = 0       # D-02 transient countdown
    crouch_ticks: int = 0     # D-04 transient countdown


PLAYER_CLIPS: dict[str, AnimClip] = {
    "idle": AnimClip(
        frames=[IDLE_U],
        durations=[STATIC_CLIP_DURATION_TICKS],
        loop=True,
    ),
    "run": AnimClip(
        frames=[RUN_FRAME_A_U, RUN_FRAME_B_U],
        durations=[RUN_TOGGLE_DURATION_TICKS, RUN_TOGGLE_DURATION_TICKS],
        loop=True,
    ),
    "jump": AnimClip(
        frames=[JUMP_U],
        durations=[STATIC_CLIP_DURATION_TICKS],
        loop=True,
    ),
}

# Rules walked in order; first predicate that returns True wins.
# D-06 fallback rule is the final always-true entry.
PLAYER_RULES: list[Rule] = [
    (lambda d: d.state == STATE_RUNNING, "run"),
    (lambda d: d.state in (STATE_JUMPING, STATE_FALLING), "jump"),
    (lambda d: True, "idle"),
]


def build_player_fsm() -> AnimFSM:
    """Factory called from Player.__init__ (plan 26-02)."""
    return AnimFSM(rules=PLAYER_RULES, clips=PLAYER_CLIPS)
