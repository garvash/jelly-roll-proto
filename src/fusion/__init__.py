"""Phase 32 FUS-04: Fusion subsystem.

Public surface:
    FusionAbility, TickResult        from .protocol
    FusionManager                    from .manager     (Plan 04)
    ChargeController                 from .charge_controller (Plan 04)
    DrillDive                        from .drill_dive  (Plan 05)
    Pogo                             from .pogo        (Plan 05)

Plan 32-02 ships only `protocol`. Plans 04 and 05 will Edit this file to
append their imports and `__all__` entries when they ship — see PATTERNS
§ "src/fusion/__init__.py" for the documented re-export discipline.
"""
from src.fusion.protocol import FusionAbility, TickResult
from src.fusion.manager import FusionManager
from src.fusion.charge_controller import ChargeController

__all__ = ["FusionAbility", "TickResult", "FusionManager", "ChargeController"]
