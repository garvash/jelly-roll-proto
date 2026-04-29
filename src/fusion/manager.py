"""Phase 32 FUS-04 fusion FSM driver (D-07, D-13, D-15, D-17).

FusionManager owns FUSED+EXIT state and the active-ability lifecycle. Per
D-13 Player.fuse/unfuse are deleted; this is the new authoritative fusion
state owner. Per D-07, fuse_end emits live here at FUSED->EXIT. Per D-17,
handle_jump_input is the single dispatcher for DOWN+SPACE airborne input
(branches on is_fused -> drill_dive | pogo). Per D-15, the 100% juice gate
for drill activation is enforced inside DrillDive.can_activate, but the
manager still routes the activation request to the right ability.

Construction-time validation per PATTERNS analog (src/anim/state_machine.py):
each registered ability is checked against the FusionAbility Protocol via
isinstance (D-09 @runtime_checkable). Boot-time TypeError beats a silent
mid-frame AttributeError.
"""
from src.fusion.protocol import FusionAbility, TickResult
from src.anim import event_bus
from src.core import tuning


class FusionManager:
    """FUSED + EXIT FSM driver. Owns active-ability dispatch and mana shield.

    Public API (per Plan 04 contract):
        is_fused: bool                          # public read mirror; Player.is_fused @property forwards here
        tick(player, slime, dt)                 # per-frame dispatch to active ability
        handle_jump_input(player, slime, im)    # D-17 single dispatch for DOWN+SPACE airborne
        latch_fuse(slime)                       # WINDUP->FUSED transition (called by ChargeController)
        force_exit(player, slime, reason)       # outside-ability exit (mana shield, debug, etc.)
        apply_fused_damage(player, slime, src_x)  # mana shield routing
    """

    def __init__(self, abilities: dict[str, FusionAbility]) -> None:
        # Construction-time Protocol conformance check (D-09 @runtime_checkable).
        # Boot-time TypeError beats silent mid-frame AttributeError on a
        # missing on_tick / on_enter / etc. Mirrors AnimFSM construction-time
        # `missing clip_ids` validation in src/anim/state_machine.py.
        for aid, ability in abilities.items():
            if not isinstance(ability, FusionAbility):
                raise TypeError(
                    f"FusionManager: ability '{aid}' does not conform to "
                    f"FusionAbility Protocol"
                )
        self._abilities: dict[str, FusionAbility] = dict(abilities)
        self._active: FusionAbility | None = None
        # Public mirror — Player.is_fused @property reads through to this in Plan 06.
        self.is_fused: bool = False
        # Frames remaining on the slime-dissipate cooldown after juice_empty exit.
        # Decrements in tick(); reset to tuning.SLIME_DISSIPATE_COOLDOWN at the
        # juice_empty exit site (Phase 25 use-site read).
        self._exit_cooldown_frames: int = 0

    def tick(self, player, slime, dt: float) -> None:
        """Per-frame dispatch (D-07). Decrements EXIT cooldown, runs active
        ability on_tick, applies dx/dy intent, handles request_exit signal.

        Note: when an ability requests exit via TickResult, this method handles
        the cleanup directly (on_exit, dissipate, fuse_end emit) and does NOT
        call self.force_exit (which is for OUTSIDE-ability triggers). Avoiding
        double-emit is the reason force_exit and tick split the exit work.
        """
        if self._exit_cooldown_frames > 0:
            self._exit_cooldown_frames -= 1
        # Fused-idle juice check: when the player is fused but no ability is
        # active (e.g., fired daze-shots to 0 juice), nothing else observes
        # juice → must dissipate here. Drill/pogo abilities own their own
        # juice_empty exit via TickResult, so this only fires in the idle gap.
        if self._active is None:
            if self.is_fused and slime.juice <= 0:
                self.force_exit(player, slime, "juice_empty")
            return
        result: TickResult = self._active.on_tick(player, slime, dt)
        # Apply intent unconditionally — TickResult defaults to (0.0, 0.0)
        # and abilities are responsible for setting valid values per D-10.
        player.dx = result.dx
        player.dy = result.dy
        # Handle exit signal
        if result.request_exit:
            reason = result.exit_reason or "unknown"
            self._active.on_exit(player, slime, reason)
            self._active = None
            if reason == "juice_empty":
                slime.dissipate()
                self._exit_cooldown_frames = tuning.SLIME_DISSIPATE_COOLDOWN
            self.is_fused = False
            slime.is_fused = False  # Pitfall 4: overlays.py + slime.update read this.
            event_bus.emit("fuse_end")

    def handle_jump_input(self, player, slime, input_manager) -> None:
        """D-17: single dispatcher for DOWN+SPACE airborne input.

        Branches on is_fused:
        - is_fused -> drill_dive (per FUSION-DESIGN drill-entry contract)
        - !is_fused -> pogo (null-fusion sibling per D-16)

        Activation requires the ability's can_activate to return True
        (e.g., DrillDive enforces 100% juice + has_drill + dist gates here).
        """
        if not (
            input_manager.btnp("jump")
            and input_manager.btn("down")
            and not player.is_grounded
        ):
            return
        target_id = "drill_dive" if self.is_fused else "pogo"
        if target_id not in self._abilities:
            return  # Ability not registered (e.g., partial test setup); silently skip.
        ability = self._abilities[target_id]
        if not ability.can_activate(player, slime):
            return
        self._active = ability
        ability.on_enter(player, slime, context={})

    def latch_fuse(self, slime) -> None:
        """WINDUP->FUSED transition (D-13 / D-15 / Pitfall 4).

        Called by ChargeController at the WINDUP->FUSED 200% latch. Sets
        is_fused on BOTH the manager and the slime (Pitfall 4: slime.is_fused
        drives overlays.py and Slime.update — must be kept in sync).

        Does NOT emit fuse_start — that emit lives at the latch SITE in
        ChargeController per D-06. Does NOT consume juice — fuse entry is
        free; drill activation in DrillDive.on_enter pays the activation cost.
        """
        self.is_fused = True
        slime.is_fused = True
        slime.is_recalling = False  # Carry-over from Player.fuse pre-D-13 deletion.

    def force_exit(self, player, slime, reason: str) -> None:
        """Force fusion exit from OUTSIDE an ability tick (D-07).

        Used when the cause is not an ability's TickResult.request_exit
        (mana shield drained juice, debug command, etc.). Idempotent: bails
        early if already not fused. Mirrors what tick() does on a request_exit
        but is the entry point for non-ability triggers.

        Reason "juice_empty" -> dissipate + cooldown; otherwise -> reform near
        player. Always emits fuse_end (D-07).
        """
        if not self.is_fused:
            return
        if self._active is not None:
            self._active.on_exit(player, slime, reason)
            self._active = None
        self.is_fused = False
        slime.is_fused = False  # Pitfall 4
        if reason == "juice_empty":
            slime.dissipate()
            self._exit_cooldown_frames = tuning.SLIME_DISSIPATE_COOLDOWN
        else:
            slime.reform(player.x, player.y, player.facing_right, player.level_map)
        event_bus.emit("fuse_end")

    def apply_fused_damage(self, player, slime, source_x) -> bool:
        """Mana shield routing for fused damage (D-07).

        Returns True if damage was absorbed (caller should NOT decrement HP).
        Consumes MANA_SHIELD_COST per hit (Phase 25 use-site tuning read);
        triggers force_exit('juice_empty') if juice drains to 0.

        Knockback application stays on Player.take_damage post-routing —
        keeping it on Player minimizes Plan 06's diff (RESEARCH § Component
        Responsibilities row 5).
        """
        if not self.is_fused:
            return False
        if slime.juice <= 0:
            return False
        slime.consume(tuning.MANA_SHIELD_COST)
        player.invuln_timer = tuning.INVULN_DURATION
        if slime.juice <= 0:
            self.force_exit(player, slime, "juice_empty")
        return True
