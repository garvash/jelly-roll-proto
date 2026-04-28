"""Phase 32 FUS-04 charge controller (D-06, D-08, D-15, D-23).

Owns RECALL+WINDUP states + accelerated regen + free-cancel. Emits
`fuse_start` at the WINDUP->FUSED 200% latch (D-06), then hands control
to FusionManager via fusion_manager.latch_fuse(slime).

Tap/hold disambiguation note: Player.handle_input keeps the spit (tap)
branch since spit spawns a projectile. ChargeController is the per-frame
hold-recall driver: when Z is held and conditions are met (slime not
dissipated, not fused, not diving), it advances IDLE -> RECALL -> WINDUP.
The frame-threshold check is intentionally NOT replicated here — the
Wave 0 test contract (tests/test_fusion_fsm.py:158) mocks
input_manager.hold_frames as 0 and expects WINDUP within 10 frames when
the slime is already docked at full juice. ChargeController therefore
treats `btn("spit") held` as "recall intent active this frame"; the
existing Z-release branch cleanly cancels brief tap-presses (no juice
spent on a 1-frame recall blip).

Per CONTEXT § Claude's Discretion #8, accelerated regen is implemented
as ChargeController calling slime.refill(rate) per frame while Z held +
slime docked + not dissipated (vs adding a slime-mode flag).
"""
from src.fusion.manager import FusionManager
from src.anim import event_bus
from src.core import tuning


# --- Named constants (project memory: no magic numbers) ----------------------
# Phase 33 D-01: WINDUP_DURATION_FRAMES + ACCELERATED_REGEN_RATE migrated to
# assets/physics-schema.json (tuning.fusion group); read at use-site below.

# State string constants (consistent with Player.state == "DIVING" precedent).
_STATE_IDLE = "IDLE"
_STATE_RECALL = "RECALL"
_STATE_WINDUP = "WINDUP"


class ChargeController:
    """Per-frame Z-input driver for the recall + windup second-pass charge.

    Public API:
        handle_z_input(player, slime, input_manager) -> None
    """

    def __init__(self, fusion_manager: FusionManager) -> None:
        self._fusion_manager = fusion_manager
        # Private FSM state: "IDLE" | "RECALL" | "WINDUP".
        self._state: str = _STATE_IDLE
        # Second-pass progress 0.0 -> 1.0 over WINDUP_DURATION_FRAMES.
        # Reset to 0.0 on entering WINDUP, on cancel, on latch.
        self._windup_progress: float = 0.0

    def handle_z_input(self, player, slime, input_manager) -> None:
        """Per-frame state machine: IDLE -> RECALL -> WINDUP -> latch.

        Called every frame from Player.handle_input (Plan 06 wires this).
        Spit-on-tap remains on Player (different code path: spawns projectile);
        ChargeController only owns RECALL and WINDUP per D-06.

        Logic order (single pass per call):
        1. Hold + recall start: while Z held + not fused + not diving + not
           dissipated, ensure RECALL state (set if IDLE) and call slime.recall.
        2. RECALL state per-frame: tick slime.update_recall; on dock + Z held
           apply accelerated regen; on dock + full juice + Z held -> WINDUP.
        3. WINDUP state per-frame: cancel on Z release (free); else accumulate
           progress; at 1.0 emit fuse_start + manager.latch_fuse + IDLE.
        4. Z release while in RECALL: cancel cleanly back to IDLE.
        """
        # ---------- Step 1: hold + recall start ---------------------------
        # Tap/hold note: hold_frames threshold check is intentionally omitted —
        # see module docstring. Brief tap-presses are cancelled by step 4 on
        # Z release with no side effects.
        if (
            input_manager.btn("spit")
            and not self._fusion_manager.is_fused
            and getattr(player, "state", None) != "DIVING"
            and not slime.is_dissipated
        ):
            if self._state == _STATE_IDLE:
                self._state = _STATE_RECALL
            # slime.recall is idempotent — safe to call repeatedly while held.
            slime.recall(player.x, player.y)

        # ---------- Step 2: RECALL state per-frame ------------------------
        if self._state == _STATE_RECALL and slime.is_recalling:
            arrived = slime.update_recall(player.x, player.y)
            # Accelerated regen while docked + Z held + not dissipated
            # (CONTEXT § Claude's Discretion #8). Phase 33 may retune the rate.
            if arrived and not slime.is_dissipated and input_manager.btn("spit"):
                slime.refill(tuning.ACCELERATED_REGEN_RATE)
            # 100% gate consolidation (D-15): WINDUP entry requires full juice.
            if (
                arrived
                and slime.juice >= slime.max_juice
                and input_manager.btn("spit")
            ):
                self._state = _STATE_WINDUP
                self._windup_progress = 0.0
                # Emit at WINDUP entry so the convergence/blob buildup plays
                # DURING the 30-frame charge instead of only at the latch
                # climax. fuse_start stays at the latch as the state-change
                # canonical (per D-06).
                event_bus.emit("fuse_charging")

        # ---------- Step 3: WINDUP state per-frame ------------------------
        if self._state == _STATE_WINDUP:
            if not input_manager.btn("spit"):
                # D-23: free cancel on Z release. Slime returns to follow;
                # juice stays at 100% (no juice spent on cancelled WINDUP).
                self._state = _STATE_IDLE
                self._windup_progress = 0.0
                slime.is_recalling = False
                slime.recall_trail.clear()
                return
            # Second-pass fill: 100% -> 200% over WINDUP_DURATION_FRAMES.
            self._windup_progress += 1.0 / tuning.WINDUP_DURATION_FRAMES
            if self._windup_progress >= 1.0:
                # D-06: fuse_start emits HERE (at the 200% latch site), then
                # hand control to FusionManager.
                event_bus.emit("fuse_start")
                self._fusion_manager.latch_fuse(slime)
                self._state = _STATE_IDLE
                self._windup_progress = 0.0

        # ---------- Step 4: Z release while in RECALL ---------------------
        # WINDUP cancel is handled inline in step 3; this branch handles
        # cancelling a recall that has not yet reached the dock.
        if input_manager.btnr("spit") and self._state == _STATE_RECALL:
            self._state = _STATE_IDLE
            slime.is_recalling = False
            slime.recall_trail.clear()
