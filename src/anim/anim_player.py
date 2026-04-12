"""Phase 26 ANIM-01 frame ticker. Does NOT import pyxel -- takes an internal
tick counter so unit tests can drive it without a pyxel mock."""
from src.anim.anim_clip import AnimClip


class AnimPlayer:
    def __init__(self, clip: AnimClip) -> None:
        self._clip = clip
        self._clip_ticks = 0
        self._frame_index = 0

    def set_clip(self, clip: AnimClip) -> None:
        # D-07 -- clip change resets frame counter to 0.
        self._clip = clip
        self._clip_ticks = 0
        self._frame_index = 0

    def tick(self) -> None:
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
