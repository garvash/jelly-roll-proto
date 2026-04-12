"""Compat shim for Phase 24 source-of-truth inversion.

The authoritative home for every named constant in this module is now
`src/core/tuning.py`, which reads `assets/physics-schema.json` at import time.
This file exists only so that legacy call sites doing

    from src.core.constants import GRAVITY

keep working without touching every caller in this phase. Phase 25 will
migrate callers to read `tuning.GRAVITY` at use time so that live-tuning
panel edits (Phase 28) reach their behavior in real time.

Known limitation (Phase 24, D-17): legacy `from` imports bind a local name
at module-import time, so `set_value('GRAVITY', 0.09)` will NOT be visible
to a caller that already imported `GRAVITY`. That is the exact problem
Phase 25 exists to solve; do not try to work around it here.
"""

from src.core.tuning import *  # noqa: F401,F403 — intentional wildcard re-export
from src.core import tuning as _tuning

# Non-scalar leaf fix-up: JSON serializes HAZARD_DRAIN_RATES's int keys as strings.
# Legacy callers index this dict with int IntGrid IDs (6/7/8), so we rebuild it
# with int keys here. The re-export above pulls in the string-keyed original; we
# shadow it with the int-keyed version.
HAZARD_DRAIN_RATES = {int(k): v for k, v in _tuning.HAZARD_DRAIN_RATES.items()}
