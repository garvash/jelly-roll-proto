"""Phase 32 FUS-04 / FUS-05 drill-dive ability (D-09, D-10, D-12, D-15).

VERBATIM PORT of v1.3 drill physics from `src/entities/player.py`:
- `apply_diving_physics` (player.py:385-398) -> `on_tick` velocity clamp + juice-empty exit.
- Block-break / impact branch (player.py:460-498) -> `on_tick` per-frame collision
  detection + `on_exit` impact-cost / drill_impact emit.

Parity bar: FUSION-DESIGN.md (locked @ 9047b590) § Drill-Dive Contract. Every
drill behavior matches the v1.3 baseline (see _v1.3-reference.json), with one
intentional tightening per CONTEXT D-15: the entry juice gate moves from
`slime.juice > 0` (v1.3) to `slime.juice >= slime.max_juice` (the 100% gate
consolidation enforced in `can_activate`).

Per D-12, this file is the canonical source of `drill_start` / `drill_block_break`
/ `drill_end` event emits. The provisional bridge in player.py:478-482 is
DELETED in the same plan (Pitfall 2 — atomic with this canonical landing).

Per D-10, the ability owns its per-frame physics. `on_tick` returns dx/dy
intent via TickResult; FusionManager applies the intent and routes the exit
signal (juice_empty -> dissipate; solid_landing -> reform).
"""
import src.core.input as input_manager
from src.anim import event_bus
from src.core import tuning
from src.fusion.protocol import TickResult


# --- Named constants (project memory: no magic numbers) ----------------------
# Phase 32 FUS-04 — drill-dive hardcoded constants.
# EXPLOSION_SIZE_PX replaces the literal `9` at v1.3 player.py:472 (PATTERNS
# § "Anti-patterns" line 433 flag). Lifted to a module-level named constant
# so the magic-number rule is satisfied; value pinned to v1.3 for parity.
EXPLOSION_SIZE_PX = 9   # v1.3 parity (player.py:472)

# CRACKED_V tile-type sentinel — mirrors src/entities/player.py:10. Re-declared
# here so drill_dive does not depend on importing from a sibling entity module.
INTGRID_CRACKED_V = 12  # Vertical cracked block; matches player.py:10


class DrillDive:
    """v1.3 drill-dive ability (FusionAbility Protocol per D-09).

    Public surface (D-09):
        id: str = "drill_dive"
        requires_fused: bool = True

        can_activate(player, slime) -> bool
        on_enter(player, slime, context) -> None
        on_tick(player, slime, dt) -> TickResult
        on_exit(player, slime, reason) -> None
        on_event(name, data) -> None

    `requires_fused = True` per D-16 (drill is the fused branch of DOWN+SPACE
    airborne dispatch). Pogo is the unfused null-fusion sibling.
    """

    id: str = "drill_dive"
    requires_fused: bool = True

    def can_activate(self, player, slime) -> bool:
        """D-15 100% gate consolidation. v1.3 entry preconditions plus the
        new full-juice requirement.

        v1.3 source (player.py:285-290): airborne + has_drill + juice > 0 +
        distance < SLIME_MAX_DIST. Phase 32 tightens `juice > 0` to
        `juice >= max_juice` (CONTEXT specifics: "tightening the existing rule").
        """
        if not getattr(player, "has_drill", False):
            return False
        if player.is_grounded:
            return False
        if slime.juice < slime.max_juice:   # 100% gate (D-15) — was `> 0` in v1.3
            return False
        # Distance check from player.py:289-290 (squared for speed).
        dist_sq = (player.x - slime.x) ** 2 + (player.y - slime.y) ** 2
        if dist_sq >= tuning.SLIME_MAX_DIST ** 2:
            return False
        return True

    def on_enter(self, player, slime, context: dict) -> None:
        """v1.3 entry side-effects (player.py:291-295) + new drill_start emit (D-12).

        FusionManager has already called latch_fuse before this; we only
        handle the drill-specific entry: pin state to "DIVING" (Open Q #1
        keeps the state mirror so existing player_anim rules continue to
        match), set initial velocity, pay activation cost, emit drill_start.
        """
        player.state = "DIVING"
        player.dy = tuning.DRILL_SPEED
        player.dx = 0
        slime.consume(tuning.DRILL_ACTIVATION_COST)
        event_bus.emit("drill_start")  # D-12 — new event, no kwargs

    def on_tick(self, player, slime, dt: float) -> TickResult:
        """Per-frame drill physics + collision detection (D-09, D-10, D-12).

        Verbatim port of player.py:386-398 (apply_diving_physics) and the
        block-break / solid-landing branch from player.py:460-484.

        Order:
        1. Re-clamp velocity (drill is a CLAMP, not additive — gravity does
           NOT accumulate; v1.3 invariant).
        2. Juice-empty -> request exit (FusionManager dissipates).
        3. Block-break detection -> emit drill_block_break + cost/refund;
           drill continues.
        4. Solid-landing detection -> request exit (FusionManager handles
           cleanup; on_exit pays DRILL_IMPACT_COST + emits drill_impact).
        5. No contact -> drill continues.

        Note on tile_coord shape: production `level_map.get_destructible_at`
        returns `(tx, ty)` (2-tuple). The Wave 0 parity-test mocks return a
        3-tuple `(tx, ty, tile_type)` so the test suite can stub tile_type
        without also stubbing `get_tile`. We unpack flexibly so the same
        ability code works against both shapes.
        """
        # 1. Re-clamp velocity (verbatim from apply_diving_physics).
        dy = tuning.DRILL_SPEED
        if input_manager.btn("left"):
            dx = -tuning.DRILL_DRIFT_SPEED
        elif input_manager.btn("right"):
            dx = tuning.DRILL_DRIFT_SPEED
        else:
            dx = 0.0

        # 2. Juice empty -> exit (FusionManager owns slime.dissipate per D-07).
        if slime.juice <= 0:
            return TickResult(dx=dx, dy=dy, request_exit=True, exit_reason="juice_empty")

        # 3. Block-break detection (per-frame, before move_and_collide runs).
        # Look-ahead the AABB by dy so the row the player is about to enter is
        # included in the destructible scan. Without this, a player drilling
        # straight down at y=80 (AABB rows 5..5) never detects a tile at row 6
        # because move_and_collide snap-stops on top before the AABB overlaps —
        # which is why CRACKED_V tiles slid past the drill instead of breaking.
        tile_coord = player.level_map.get_destructible_at(
            player.x, player.y + dy, player.w, player.h
        )
        if tile_coord:
            # Flexible unpack: 3-tuple includes tile_type; 2-tuple looks it up.
            if len(tile_coord) >= 3:
                tx, ty, tile_type = tile_coord[0], tile_coord[1], tile_coord[2]
            else:
                tx, ty = tile_coord
                tile_type = player.level_map.get_tile(tx, ty)
            if player.game:
                player.game.on_block_destroyed(tx, ty, tile_type)
            # remove_tile is the production path; tolerate absence so unit
            # tests that stub level_map without this method still exercise
            # the cost/refund/emit semantics.
            remove = getattr(player.level_map, "remove_tile", None)
            if remove is not None:
                remove(tx, ty)
            if player.game:
                player.game.spawn_explosion(
                    tx * tuning.TILE_SIZE,
                    ty * tuning.TILE_SIZE,
                    EXPLOSION_SIZE_PX,
                )
            if tile_type == INTGRID_CRACKED_V:
                slime.consume(tuning.DRILL_CRACKED_V_COST)  # Gate block costs juice (ABL-02)
            else:
                slime.refill(tuning.DRILL_BLOCK_REFUND)     # Soft block refunds juice
            player.on_block_break()
            # Canonical drill_block_break emit (Pitfall 1 — char-for-char with
            # the deleted player.py:482 bridge; Phase 31 subscriber at
            # main.py:274 reads exactly these kwargs).
            event_bus.emit("drill_block_break", tx=tx, ty=ty)
            return TickResult(dx=dx, dy=dy)  # drill continues, no exit

        # 4. Solid-landing detection: collision below + no destructible there.
        if player.level_map.check_collision(
            player.x, player.y + 1, player.w, player.h
        ):
            below_tile = player.level_map.get_destructible_at(
                player.x, player.y + 1, player.w, player.h
            )
            if below_tile is None:
                return TickResult(
                    dx=dx, dy=dy, request_exit=True, exit_reason="solid_landing"
                )

        # 5. Drill continues.
        return TickResult(dx=dx, dy=dy)

    def on_exit(self, player, slime, reason: str) -> None:
        """D-12: drill_end emits on every exit. Per-reason side effects:
        - solid_landing: consume DRILL_IMPACT_COST + emit drill_impact + state -> IDLE.
        - juice_empty: state -> FALLING (FusionManager dissipates via tick exit path).
        - other: no per-reason side effects, just emit drill_end.

        drill_impact is the EXISTING event from v1.3 (player.py:496); MOVED
        here so the impact branch is co-located with drill_end (D-12).
        """
        if reason == "solid_landing":
            slime.consume(tuning.DRILL_IMPACT_COST)
            event_bus.emit("drill_impact")  # existing event, MOVED from player.py:496
            player.state = "IDLE"
        elif reason == "juice_empty":
            player.state = "FALLING"
            # FusionManager handles slime.dissipate via tick() exit-handling path.
        # Universal exit event (D-12).
        event_bus.emit("drill_end")

    def on_event(self, name: str, data: dict) -> None:
        """D-11 side-channel hook. DrillDive does not currently react to events;
        method is here for Protocol conformance and future extensibility."""
        pass
