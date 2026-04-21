"""Phase 26 ANIM-01 generic animation decision class. Rules-list evaluator per
D-00a / D-04 (NOT a classical transition-edge FSM -- name is kept for
requirement traceability, not API semantics)."""
from typing import Callable, Any
from src.anim.anim_clip import AnimClip
from src.anim.anim_player import AnimPlayer

Rule = tuple[Callable[[Any], bool], str]  # (predicate, clip_id)


class AnimFSM:
    def __init__(self, rules: list[Rule], clips: dict[str, AnimClip]) -> None:
        # Construction-time validation: every clip_id referenced must exist.
        missing = [cid for _, cid in rules if cid not in clips]
        if missing:
            raise ValueError(
                f"AnimFSM rules reference missing clip_ids: {missing}"
            )
        self._rules = rules
        self._clips = clips
        # Start on fallback clip (last rule per D-06).
        self._player = AnimPlayer(clips[rules[-1][1]])
        self._last_clip_id: str | None = None

    def current_frame_u(self, driver: Any) -> int:
        for predicate, clip_id in self._rules:
            if predicate(driver):
                if clip_id != self._last_clip_id:
                    self._player.set_clip(self._clips[clip_id])  # D-07 reset
                    self._last_clip_id = clip_id
                self._player.tick()
                return self._player.current_u()
        # Unreachable: D-06 fallback guarantees a final always-true rule.
        raise RuntimeError("AnimFSM rules missing fallback")

    def pause_for(self, n: int) -> None:
        """Forward to the active AnimPlayer. Phase 31 D-06.

        Keeps _player private; subscribers call player._anim.pause_for(n)
        instead of reaching through to player._anim._player.
        """
        self._player.pause_for(n)
