"""Phase 32 FUS-04 / FUS-05 pogo null-fusion ability (D-16, D-18, D-19, D-20).

DOWN+SPACE airborne unfused -> pogo strike. Bounces on enemies and soft
destructibles only (D-19); pure solid ground = land, no bounce. Pogo is
FREE — no juice cost, no cooldown active in v2.0 baseline (D-20).

Per D-18, all pogo constants are HARDCODED in this module. They do NOT
live in `tuning.*` / `physics-schema.json` / panel sliders / preset
entries. Phase 33 may migrate to tuning if a feel-pass warrants live
editing; until then, hardcoding keeps the v2.0 refactor pure (no new
tuning surface).

Per D-19, CRACKED_V tiles are NOT pogo-eligible (drill territory per
project MEMORY block-gate hierarchy). Pogo treats CRACKED_V as a solid
landing surface — it does NOT break and does NOT bounce.

Implements the FusionAbility Protocol (D-09) with `requires_fused = False`
so the FusionManager dispatcher (D-17) can route DOWN+SPACE airborne
unfused input to a uniform ability shape — same lifecycle hooks as
DrillDive, just a different rule set.
"""
from src.anim import event_bus
from src.core import tuning
from src.fusion.protocol import TickResult


# --- Named constants (project memory: no magic numbers) ----------------------
# Phase 33 D-02: POGO_BOUNCE_VELOCITY + POGO_COOLDOWN_FRAMES migrated to
# assets/physics-schema.json (tuning.pogo group); read at use-site below.
# POGO_INITIAL_DY + POGO_DAMAGE STAY hardcoded per D-02 (Mario-64 visual parity
# with DRILL_SPEED for INITIAL_DY; gameplay constant for DAMAGE).
POGO_INITIAL_DY = 2.0          # downward strike velocity on enter (matches
                                # DRILL_SPEED for visual parity, D-02)
POGO_DAMAGE = 1                # D-19: damage to enemies on contact (gameplay
                                # constant per Phase 33 D-02)
EXPLOSION_SIZE_PX = 9          # local copy; matches DrillDive (could lift to
                                # a shared location later)

# CRACKED_V tile-type sentinel — mirrors src/entities/player.py:10. Re-declared
# locally so pogo does not depend on importing from a sibling entity module.
INTGRID_CRACKED_V = 12  # Vertical cracked block; matches player.py:10


class Pogo:
    """Null-fusion DOWN+SPACE airborne ability (D-16, D-19, D-20).

    Public surface (D-09):
        id: str = "pogo"
        requires_fused: bool = False

        can_activate(player, slime) -> bool
        on_enter(player, slime, context) -> None
        on_tick(player, slime, dt) -> TickResult
        on_exit(player, slime, reason) -> None
        on_event(name, data) -> None
    """

    id: str = "pogo"
    requires_fused: bool = False

    def can_activate(self, player, slime) -> bool:
        """D-20: pogo is free. Only requires airborne. Manager dispatch (D-17)
        already verified is_fused == False before calling this, so we don't
        re-check the fusion flag here.

        No juice gate per D-20 — pogo is free even with empty slime.
        """
        return not player.is_grounded

    def on_enter(self, player, slime, context: dict) -> None:
        """Strike downward on activation. No juice cost (D-20)."""
        player.dy = POGO_INITIAL_DY
        player.dx = 0

    def on_tick(self, player, slime, dt: float) -> TickResult:
        """Per-frame contact detection (D-19).

        Order:
        1. Soft destructible (NOT CRACKED_V) -> break it, bounce upward, exit.
        2. CRACKED_V tile -> NOT pogo-eligible; treat as solid landing.
        3. Enemy contact -> bounce + damage, exit.
        4. Solid below (non-destructible) -> land, no bounce, exit.
        5. No contact -> keep plunging.

        Per D-20, pogo NEVER calls slime.consume / slime.refill — all
        block-break and bounce paths are free.
        """
        # 1. Check destructible directly below.
        tile_coord = player.level_map.get_destructible_at(
            player.x, player.y, player.w, player.h
        )
        if tile_coord:
            # Flexible unpack: 3-tuple includes tile_type; 2-tuple looks it up.
            if len(tile_coord) >= 3:
                tx, ty, tile_type = tile_coord[0], tile_coord[1], tile_coord[2]
            else:
                tx, ty = tile_coord
                tile_type = None
                get_tile = getattr(player.level_map, "get_tile", None)
                if get_tile is not None:
                    tile_type = get_tile(tx, ty)
            if tile_type != INTGRID_CRACKED_V:
                # Soft destructible — break it, bounce, NO juice refund (D-20).
                if player.game:
                    player.game.on_block_destroyed(tx, ty, tile_type)
                remove = getattr(player.level_map, "remove_tile", None)
                if remove is not None:
                    remove(tx, ty)
                if player.game:
                    player.game.spawn_explosion(
                        tx * 16,  # see EXPLOSION_SIZE_PX comment; tile coord
                                   # is multiplied by tile size at use-site.
                        ty * 16,
                        EXPLOSION_SIZE_PX,
                    )
                # Phase 33 D-20: pogo_bounce emit on the soft-destructible
                # bounce path (audio + future particle subscribers).
                event_bus.emit("pogo_bounce")
                # Bounce off
                return TickResult(
                    dx=0.0,
                    dy=tuning.POGO_BOUNCE_VELOCITY,
                    request_exit=True,
                    exit_reason="bounced",
                )
            # CRACKED_V tile — NOT pogo-eligible (D-19). Treat as solid:
            # land, no bounce.
            return TickResult(
                dx=0.0,
                dy=POGO_INITIAL_DY,
                request_exit=True,
                exit_reason="landed",
            )

        # 2. Check enemy contact.
        if player.game and self._touching_enemy(player):
            self._damage_touched_enemy(player)
            # Phase 33 D-20: pogo_bounce emit on the enemy-contact bounce path.
            event_bus.emit("pogo_bounce")
            return TickResult(
                dx=0.0,
                dy=tuning.POGO_BOUNCE_VELOCITY,
                request_exit=True,
                exit_reason="bounced",
            )

        # 3. Check solid (non-destructible) below — land.
        if player.level_map.check_collision(
            player.x, player.y + 1, player.w, player.h
        ):
            return TickResult(
                dx=0.0,
                dy=POGO_INITIAL_DY,
                request_exit=True,
                exit_reason="landed",
            )

        # 4. No contact yet — keep plunging.
        return TickResult(dx=0.0, dy=POGO_INITIAL_DY)

    def on_exit(self, player, slime, reason: str) -> None:
        """No event emit; pogo is silent in the event_bus contract for Phase 32.
        Player state stays as physics dictates (FALLING / IDLE based on
        subsequent move_and_collide / apply_physics)."""
        pass

    def on_event(self, name: str, data: dict) -> None:
        """Pogo does not subscribe to side-channel events in v2.0 baseline."""
        pass

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _touching_enemy(self, player) -> bool:
        """Returns True if player AABB overlaps any alive enemy.

        Reads from `player.game.enemies` (the existing code idiom). Returns
        False when game is None (test fixtures often construct Player
        without a game).
        """
        if not player.game:
            return False
        enemies = getattr(player.game, "enemies", None)
        if not enemies:
            return False
        for enemy in enemies:
            if not getattr(enemy, "is_alive", True):
                continue
            ew = getattr(enemy, "w", 0)
            eh = getattr(enemy, "h", 0)
            if (
                player.x < enemy.x + ew
                and player.x + player.w > enemy.x
                and player.y < enemy.y + eh
                and player.y + player.h > enemy.y
            ):
                return True
        return False

    def _damage_touched_enemy(self, player) -> None:
        """Apply POGO_DAMAGE to the first enemy intersecting player AABB."""
        if not player.game:
            return
        enemies = getattr(player.game, "enemies", None)
        if not enemies:
            return
        for enemy in enemies:
            if not getattr(enemy, "is_alive", True):
                continue
            ew = getattr(enemy, "w", 0)
            eh = getattr(enemy, "h", 0)
            if (
                player.x < enemy.x + ew
                and player.x + player.w > enemy.x
                and player.y < enemy.y + eh
                and player.y + player.h > enemy.y
            ):
                # Use existing enemy.take_damage if present, otherwise direct decrement.
                if hasattr(enemy, "take_damage"):
                    enemy.take_damage(POGO_DAMAGE)
                else:
                    enemy.hp = getattr(enemy, "hp", 0) - POGO_DAMAGE
                return
