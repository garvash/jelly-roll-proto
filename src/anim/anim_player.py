"""Phase 26 ANIM-01 frame ticker. Phase 31 adds pause_for(n) primitive for D-06
drill-recoil animation-only pause (distinct from gameplay hitstop)."""
from src.anim.anim_clip import AnimClip


class AnimPlayer:
    def __init__(self, clip: AnimClip) -> None:
        self._clip = clip
        self._clip_ticks = 0
        self._frame_index = 0
        self._pause_ticks = 0   # Phase 31 D-06

    def set_clip(self, clip: AnimClip) -> None:
        # D-07 -- clip change resets frame counter to 0.
        self._clip = clip
        self._clip_ticks = 0
        self._frame_index = 0
        self._pause_ticks = 0   # Phase 31: pause does not survive clip change

    def pause_for(self, n: int) -> None:
        """Freeze the tick counter for n frames. Additive if already paused.

        Phase 31 D-06: animation-only pause for drill-recoil visual.
        Distinct from gameplay hitstop (game.stop_frames). See RESEARCH A2
        for additive-vs-overwrite rationale.
        """
        self._pause_ticks += n

    def tick(self) -> None:
        # Phase 31: pause suppresses frame advance; duration counter stays
        # at rest so the current frame holds visually.
        if self._pause_ticks > 0:
            self._pause_ticks -= 1
            return
        # Check-then-increment: the frame persists for its full duration
        # before advancing. With tick-then-read, a 2-tick duration frame
        # shows on both tick 1 and tick 2, advancing on tick 3.
        if self._clip_ticks >= self._clip.durations[self._frame_index]:
            self._clip_ticks = 0
            if self._frame_index + 1 < len(self._clip.frames):
                self._frame_index += 1
            elif self._clip.loop:
                self._frame_index = 0
            else:
                # Non-looping clip -- hold on last frame.
                return
        self._clip_ticks += 1

    def current_u(self) -> int:
        return self._clip.frames[self._frame_index]
