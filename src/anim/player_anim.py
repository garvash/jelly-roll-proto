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
# Hardcoded formula replaced:  u = 16 + (pyxel.frame_count // 12 % 2) * 16
IDLE_U = 0
RUN_FRAME_A_U = 16
RUN_FRAME_B_U = 32
JUMP_U = 32
# Duration constants in pyxel ticks.
STATIC_CLIP_DURATION_TICKS = 1   # idle + jump are 1-frame holds
RUN_TOGGLE_DURATION_TICKS = 12   # v1.3 parity: 12 frames per run frame

# --- Player state name constants (mirror src/entities/player.py state strings) ---
STATE_IDLE = "IDLE"
STATE_RUNNING = "RUNNING"
STATE_JUMPING = "JUMPING"
STATE_FALLING = "FALLING"


@dataclass(slots=True)
class PlayerAnimDriver:
    state: str = STATE_IDLE
    is_grounded: bool = True
    facing: int = 1        # -1 or +1
    vy_sign: int = 0       # -1 / 0 / +1


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
