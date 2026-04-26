"""Phase 32 FUS-04 fusion ability protocol (D-09, D-10, D-11, D-12).

Defines the FusionAbility typing.Protocol and TickResult dataclass that
abilities (drill_dive, pogo) return from on_tick. CONTEXT D-09 mandates
typing.Protocol over abc.ABC for structural typing.

Per D-09: lifecycle + per-frame + event hook surface (5 methods, 2 class
attrs). Per D-10: ability owns its per-frame physics; on_tick returns dx/dy
intent via TickResult and FusionManager applies the intent. Per D-11:
on_event is the side-channel hook for events the ability cares about
(drill_block_break feedback into ability state). Per D-12: drill_start
emits from on_enter, drill_block_break from on_tick mid-detection,
drill_end from on_exit.

The Protocol shape is the FIXED contract that Plan 04 (FusionManager)
consumes via on_tick and Plan 05 (DrillDive, Pogo) implements. Do not
modify the surface here without re-locking CONTEXT D-09.
"""
from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class TickResult:
    """Per-frame intent returned by FusionAbility.on_tick.

    Phase 32 D-10: ability owns physics. This dataclass carries the dx/dy
    intent back to FusionManager and signals optional exit. FusionManager
    applies the intent and observes the exit signal (RESEARCH § Pattern 1).
    Frozen+slots mirrors src/anim/anim_clip.py precedent.
    """

    dx: float = 0.0
    dy: float = 0.0
    request_exit: bool = False
    exit_reason: Optional[str] = None  # "solid_landing" | "juice_empty" | None


@runtime_checkable
class FusionAbility(Protocol):
    """Per CONTEXT D-09. requires_fused=False for null-fusion (pogo, D-16).

    Per D-10: ability owns its per-frame physics. on_tick returns dx/dy intent
    via TickResult. FusionManager applies the intent and observes the exit
    signal.

    Per D-11: on_event is the side-channel hook for events the ability cares
    about (e.g., drill_block_break feedback into ability state).

    Per D-12: drill_start emits from on_enter, drill_block_break from on_tick
    mid-detection, drill_end from on_exit. Emission lives in the ability,
    not in FusionManager.

    @runtime_checkable enables `isinstance(x, FusionAbility)` at FusionManager
    construction time (Plan 04 wiring guard) and inside the test suite.
    """

    id: str
    requires_fused: bool

    def can_activate(self, player, slime) -> bool:
        """D-09: lifecycle gate. Returns True if the ability can activate this frame."""
        ...

    def on_enter(self, player, slime, context: dict) -> None:
        """D-09: lifecycle entry. D-12: drill_start emits here for DrillDive."""
        ...

    def on_tick(self, player, slime, dt: float) -> TickResult:
        """D-09: per-frame physics + exit signal. D-10: ability owns physics here.
        D-12: drill_block_break emits here mid-detection for DrillDive."""
        ...

    def on_exit(self, player, slime, reason: str) -> None:
        """D-09: lifecycle exit. D-12: drill_end emits here for DrillDive."""
        ...

    def on_event(self, name: str, data: dict) -> None:
        """D-11: side-channel hook for events the ability observes.
        Events inform the ability; they do not drive its FSM (Phase 26 MEMORY)."""
        ...
