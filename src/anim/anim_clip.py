"""Phase 26 ANIM-01 clip data. Phase 31 will add event bindings per ANIM-04;
the events slot is reserved now so it is not a breaking change next phase."""
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class AnimClip:
    frames: list[int]           # sprite u offsets in pixels
    durations: list[int]        # per-frame duration in ticks
    loop: bool = True           # D-08 default
    events: dict = field(default_factory=dict)  # Phase 31 stub, empty for now

    def __post_init__(self) -> None:
        if len(self.frames) != len(self.durations):
            raise ValueError(
                f"AnimClip frames/durations length mismatch: "
                f"{len(self.frames)} vs {len(self.durations)}"
            )
