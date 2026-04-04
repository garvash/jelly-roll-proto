import pyxel
from src.level.map import LevelMap
from src.level.world import WorldManager
from src.core.constants import VIEWPORT_W, VIEWPORT_H


# === Mini-map helper functions (Plan 03, SYS-02) ===
# Module-level for testability -- used by _draw_minimap and pause overlay.

def snap_to_grid(x, y):
    """Quantize a position to viewport-sized GridVania cells."""
    return ((x // VIEWPORT_W) * VIEWPORT_W, (y // VIEWPORT_H) * VIEWPORT_H)

def classify_room_types(levels, entities):
    """Classify rooms as 'save', 'boss', or 'normal' based on entity scan.

    Args:
        levels: list of LevelBounds objects
        entities: list of entity dicts from level_map.entities
    Returns:
        dict mapping level_id to 'save'|'boss'|'normal'
    """
    room_types = {level.id: "normal" for level in levels}
    for ent in entities:
        etype = ent["type"]
        etype = ENTITY_ALIASES.get(etype, etype)
        ex, ey = ent["x"], ent["y"]
        if etype in ("SavePoint", "BossMole"):
            for level in levels:
                if (level.x <= ex < level.x + level.w and
                    level.y <= ey < level.y + level.h):
                    if etype == "SavePoint":
                        room_types[level.id] = "save"
                    elif etype == "BossMole":
                        room_types[level.id] = "boss"
                    break
    return room_types


def compute_map_rects(levels, max_w, max_h, visited=None):
    """Compute scaled map rectangles for visited viewport-sized cells.

    Args:
        levels: list of LevelBounds (used to compute world bounds)
        max_w: max pixel width for the map display
        max_h: max pixel height for the map display
        visited: set of (cam_x, cam_y) tuples for visited cells (None = show all cells)
    Returns:
        list of (rx, ry, rw, rh, cell_key) tuples in pixel coordinates
    """
    if not levels:
        return []
    if visited is not None and not visited:
        return []

    # World bounds from all levels
    min_wx = min(l.x for l in levels)
    min_wy = min(l.y for l in levels)
    world_w = max(l.x + l.w for l in levels) - min_wx
    world_h = max(l.y + l.h for l in levels) - min_wy

    # Scale to fit within max_w x max_h
    scale_x = max_w / world_w if world_w > 0 else 1
    scale_y = max_h / world_h if world_h > 0 else 1
    scale = min(scale_x, scale_y)

    if visited is None:
        # Show all possible cells from all levels
        cells = []
        for level in levels:
            for cy in range(level.y, level.y + level.h, VIEWPORT_H):
                for cx in range(level.x, level.x + level.w, VIEWPORT_W):
                    cells.append((cx, cy))
    else:
        cells = visited

    rects = []
    for cx, cy in cells:
        rx = int((cx - min_wx) * scale)
        ry = int((cy - min_wy) * scale)
        rw = max(2, int(VIEWPORT_W * scale))
        rh = max(1, int(VIEWPORT_H * scale))
        rects.append((rx, ry, rw, rh, (cx, cy)))
    return rects


def get_room_color(cell_key, current_cell, room_types, frame=0, levels=None):
    """Get Pyxel palette color for a cell on the map (D-08).

    Args:
        cell_key: (cam_x, cam_y) of the cell to color
        current_cell: (cam_x, cam_y) of the player's current cell
        room_types: dict from classify_room_types (level_id -> type)
        frame: pyxel.frame_count for blink animation
        levels: list of LevelBounds to map cell to level ID
    Returns:
        int Pyxel palette color index
    """
    BLINK_HALF_CYCLE = 15
    if cell_key == current_cell:
        return 7 if frame % (BLINK_HALF_CYCLE * 2) < BLINK_HALF_CYCLE else 0
    # Map cell coordinates to level, then look up room type
    if levels:
        cx, cy = cell_key
        for level in levels:
            if (level.x <= cx < level.x + level.w and
                    level.y <= cy < level.y + level.h):
                room_type = room_types.get(level.id, "normal")
                if room_type == "save":
                    return 11  # Green
                elif room_type == "boss":
                    return 8   # Red
                break
    return 5  # Gray for normal visited
from src.entities.player import Player
from src.entities.slime import Slime
from src.core.constants import (BOOST_DOWNWARD_DAMAGE_W, BOOST_DOWNWARD_DAMAGE_H,
    SCREEN_W, SCREEN_H, VIEWPORT_W, VIEWPORT_H, HUD_H, CULL_MARGIN, JUICE_MAX,
    DEATH_FREEZE_FRAMES, DEATH_FADE_FRAMES, MAX_HP_CAP, MAX_JUICE_CAP)
from src.core.sprite_utils import load_sprite_tags
from src.entities.boss import Mole
from src.entities.enemies import Snail, Bat
from src.entities.items import Item
from src.entities.effects import Effect, Particle
from src.entities.map_entities import Door, OneWay, HiddenLoot, MapFixture
from src.core.save_manager import SaveManager
from src.entities.save_point import SavePoint
import src.core.input as inp
import src.core.debug as debug

# Entity name aliases: LDtk export names -> game code names (INT-01, D-05)
# Allows LDtk entities with alternate names to map to the game's internal types.
ENTITY_ALIASES = {
    "Save": "SavePoint",
    "FinalBoss": "BossMole",
}

# Sprite loading manifest (D-16): maps entity names to (bank, x, y, path)
# Bank 0 = tiles (8x8 cells), Bank 1 = entities (16x16/32x32 frames)
SPRITE_MANIFEST = {
    "tiles":      (0, 0, 0,   "assets/sprites/tiles.png"),
    "player":     (1, 0, 0,   "assets/sprites/player.png"),
    "slime":      (1, 0, 16,  "assets/sprites/slime.png"),
    "snail":      (1, 0, 32,  "assets/sprites/snail.png"),
    "bat":        (1, 0, 48,  "assets/sprites/bat.png"),
    "items":      (1, 0, 64,  "assets/sprites/items.png"),
    "projectile": (1, 0, 80,  "assets/sprites/projectile.png"),
    "effects":    (1, 0, 96,  "assets/sprites/effects.png"),
    "boss":       (1, 0, 128, "assets/sprites/boss.png"),
}

class Game:
    def __init__(self):
        # 16x16 tiles room size = 128x128 pixels
        pyxel.init(SCREEN_W, SCREEN_H, title="Jelly Roll Proto", fps=60, quit_key=pyxel.KEY_NONE)
        # Load PNG spritesheets into image banks (D-09, D-11)
        self._load_sprites()
        # Load animation tag metadata from JSON sidecars (D-08, D-23)
        # Note: Tags are loaded for forward compatibility with the Aseprite art pipeline.
        # Entity draw methods currently use hardcoded frame arithmetic -- when the artist
        # provides hand-drawn Aseprite exports, tag-based frame selection can replace
        # the hardcoded offsets. See sprite_utils.load_sprite_tags() docstring.
        self.sprite_tags = {}
        for name in SPRITE_MANIFEST:
            if name == "tiles":
                continue  # tiles have no animation tags
            json_path = SPRITE_MANIFEST[name][3].replace(".png", ".json")
            self.sprite_tags[name] = load_sprite_tags(json_path)
        self.reset()
        # Start on TITLE screen (Phase 11, SYS-01)
        self.game_state = "TITLE"
        self.title_cursor = 0
        self.title_confirm_active = False  # "ERASE SAVE?" sub-menu
        self.title_confirm_cursor = 1      # Default to NO
        pyxel.run(self.update, self.draw)

    def reset(self):
        # Reload PNG spritesheets to restore image bank state (D-09, D-11)
        self._load_sprites()

        self.level_map = LevelMap()
        # Load external map if exists
        self.level_map.load_from_tiled("assets/map.json")
        self.level_map.load_from_ldtk("assets/map.ldtk")
        # Priority: LDtk Super Simple Export
        success = self.level_map.load_from_ldtk_simplified("assets/cave/simplified")
        if success:
            print(f"Loaded LDtk map from simplified export. Entities: {len(self.level_map.entities)}")

        # Initialize WorldManager with level bounds from LDtk
        self.world = WorldManager(self.level_map.get_level_bounds_list())

        # Default start position
        spawn_x, spawn_y = 40, 40
        
        # 1. Spawn Player from LDtk entities
        player_ent = next((e for e in self.level_map.entities if e["type"] == "PlayerStart"), None)
        if player_ent:
            spawn_x, spawn_y = player_ent["x"], player_ent["y"]
        else:
            # Fallback to tile marker (1, 0)
            spawn_tile = self.level_map.find_tile(1, 0)
            if spawn_tile:
                tx, ty = spawn_tile
                spawn_x, spawn_y = tx * 8, ty * 8
                self.level_map.remove_tile(tx, ty)

        self.player = Player(spawn_x, spawn_y, self.level_map, self)
        self.slime = Slime(spawn_x, spawn_y)
        
        # Mole starts as None, will be spawned when room is entered
        self.mole = None
        self.enemies = []
        self.items = []
        self.projectiles = []
        self.stains = []
        self.effects = []
        self.particles = []
        self.doors = []
        self.save_points = []
        self.fixtures = []
        self.door_grace_frames = 0
        self._prev_level_id = None
        self._entrance_door = None
        self.event_flags = {}  # Dict[str, bool] for event-gated doors (D-03)
        # Note: game_state set by caller (TITLE on init, PLAYING on start/load)
        self.death_timer = 0
        self.shake_timer = 0
        self.stop_frames = 0
        self.cam_x = 0
        self.cam_y = 0
        self.boss_triggered = False
        self.rooms_visited = set()
        # Track spawn for current room (for hazard respawn)
        self.room_spawn_x = spawn_x
        self.room_spawn_y = spawn_y
        self.pending_boss_trigger = True
        
        # Detect initial room and set camera
        player_cx = spawn_x + self.player.w / 2
        player_cy = spawn_y + self.player.h / 2
        initial_level = self.world.detect_level(player_cx, player_cy)
        self.cam_x, self.cam_y = self.world.get_camera_clamped(spawn_x, spawn_y)
        self.cam_x = int(self.cam_x)
        self.cam_y = int(self.cam_y)

        # Initial room scan
        self.spawn_enemies()
        # Track visited cells as (cam_x, cam_y) — viewport-sized GridVania units
        self.rooms_visited.add(snap_to_grid(self.cam_x, self.cam_y))

        # Classify rooms for mini-map color-coding (SYS-02, D-08)
        self.room_types = classify_room_types(self.world.levels, self.level_map.entities)

    def _load_sprites(self):
        """Load all PNG spritesheets into image banks (D-09, D-11)."""
        for name, (bank, x, y, path) in SPRITE_MANIFEST.items():
            pyxel.images[bank].load(x, y, path)

    def spawn_enemies(self):
        # 1. Spawn from LDtk entity list (if current room matches)
        # Use full room bounds (not just viewport) so entities in large rooms always spawn
        level = self.world.current_level
        if level:
            room_x, room_y = level.x, level.y
            room_w, room_h = level.w, level.h
        else:
            room_x, room_y = self.cam_x, self.cam_y
            room_w, room_h = VIEWPORT_W, VIEWPORT_H

        for ent in self.level_map.entities:
            if (room_x <= ent["x"] < room_x + room_w and
                room_y <= ent["y"] < room_y + room_h):
                
                etype = ent["type"]
                etype = ENTITY_ALIASES.get(etype, etype)
                ex, ey = ent["x"], ent["y"]

                # Skip items that have already been collected
                ent_iid = ent.get("iid")
                if ent_iid and self.world.is_item_collected(ent_iid):
                    continue

                if etype == "Snail":
                    self.enemies.append(Snail(ex, ey, self))
                elif etype == "Bat":
                    self.enemies.append(Bat(ex, ey, self))
                # Note: BossMole handled by check_boss_trigger for safety margin
                elif etype == "DashPickup":
                    self.items.append(Item(ex, ey, "DASH_PICKUP", iid=ent_iid))
                elif etype == "DrillPickup":
                    self.items.append(Item(ex, ey, "DRILL_PICKUP", iid=ent_iid))
                elif etype == "EnergyTank":
                    self.items.append(Item(ex, ey, "ENERGY", iid=ent_iid))
                elif etype == "MissileTank":
                    self.items.append(Item(ex, ey, "MISSILE", iid=ent_iid))
                elif etype == "ShieldPickup":
                    self.items.append(Item(ex, ey, "SHIELD_PICKUP", iid=ent_iid))
                elif etype == "BoostPickup":
                    self.items.append(Item(ex, ey, "BOOST_PICKUP", iid=ent_iid))
                elif etype == "ShieldT2":
                    self.items.append(Item(ex, ey, "SHIELD_T2", iid=ent_iid))
                elif etype == "SavePoint":
                    self.save_points.append(SavePoint(ex, ey))
                elif etype == "Door":
                    # LDtk stores target as integer index; convert to identifier string
                    raw_target = ent.get("target_level_id")
                    target_id = f"Level_{raw_target}" if raw_target is not None else None
                    direction = ent.get("direction", "right")
                    # Flat read: customFields already flattened by map.py (INT-02, D-03)
                    action = ent.get("action")
                    event_id = ent.get("event_id")
                    # Normalize "none" string to None (LDtk enum default)
                    if action == "none":
                        action = None
                    # D-04 audit: Only Door uses customFields. All other entities use flat reads already.
                    hp = ent.get("hp", 1)
                    # LDtk center-pivot (8x8 marker): convert to top-left corner
                    self.doors.append(Door(ex - 4, ey - 4, target_id, direction,
                                           action=action, event_id=event_id))
                elif etype == "OneWay":
                    direction = ent.get("direction", "right")
                    self.fixtures.append(OneWay(ex, ey, direction))
                elif etype == "HiddenLoot":
                    ent_iid = ent.get("iid")
                    if ent_iid and self.world.is_item_collected(ent_iid):
                        continue  # Already collected
                    self.fixtures.append(HiddenLoot(ex, ey, iid=ent_iid))
                elif etype == "Map":
                    self.fixtures.append(MapFixture(ex, ey))
                else:
                    # Log unknown entity types for debugging (not PlayerStart, handled elsewhere)
                    if etype != "PlayerStart":
                        print(f"Unknown entity type: {etype} at ({ex}, {ey})")

        # 2. Scan current room for enemy spawn tiles (Legacy fallback)
        tx_start, ty_start = int(room_x // 8), int(room_y // 8)
        tx_count = room_w // 8
        ty_count = room_h // 8
        for ty in range(ty_start, ty_start + ty_count):
            for tx in range(tx_start, tx_start + tx_count):
                tile = self.level_map.get_tile(tx, ty)
                if tile == (0, 2): # Snail Marker
                    self.enemies.append(Snail(tx * 8, ty * 8))
                    self.level_map.remove_tile(tx, ty)
                elif tile == (0, 3): # Bat Marker
                    self.enemies.append(Bat(tx * 8, ty * 8))
                    self.level_map.remove_tile(tx, ty)
                elif tile == (3, 0): # Dash Pickup Marker
                    self.items.append(Item(tx * 8, ty * 8, "DASH_PICKUP"))
                    self.level_map.remove_tile(tx, ty)
                elif tile == (2, 2): # Energy Tank Marker
                    self.items.append(Item(tx * 8, ty * 8, "ENERGY"))
                    self.level_map.remove_tile(tx, ty)
                elif tile == (3, 2): # Missile Tank Marker
                    self.items.append(Item(tx * 8, ty * 8, "MISSILE"))
                    self.level_map.remove_tile(tx, ty)

    def check_boss_trigger(self):
        """Checks for BossMole entity in current room."""
        if self.mole or self.boss_triggered:
            return

        # Check Entities (use full room bounds for large rooms)
        level = self.world.current_level
        if level:
            rx, ry, rw, rh = level.x, level.y, level.w, level.h
        else:
            rx, ry, rw, rh = self.cam_x, self.cam_y, VIEWPORT_W, VIEWPORT_H

        for ent in self.level_map.entities:
            if (rx <= ent["x"] < rx + rw and
                ry <= ent["y"] < ry + rh):
                if ENTITY_ALIASES.get(ent["type"], ent["type"]) == "BossMole":
                    self.mole = Mole(ent["x"], ent["y"], self.level_map)
                    self.level_map.close_gates(self.cam_x, self.cam_y)
                    self.boss_triggered = True
                    return

    def update(self):
        debug.update()  # Process god-mode key toggles (D-09)

        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # State machine dispatch (Phase 11, SYS-01)
        if self.game_state == "TITLE":
            self._update_title()
            return
        if self.game_state == "DEAD":
            self._update_death()
            return
        if self.game_state == "PAUSED":
            self._update_pause()
            return

        # 0. Handle transition animation (freeze gameplay during slide)
        if self.world.is_transitioning():
            self.cam_x, self.cam_y = self.world.update_transition()
            if not self.world.is_transitioning():
                # Transition slide done — enter settle phase, finalize room entry
                self._on_room_enter()
            return

        # 0b. Post-transition camera settle (gameplay runs, camera lerps smoothly)
        if self.world.is_settling():
            settle_cam = self.world.update_settle(self.player.x, self.player.y)
            if settle_cam is not None:
                self.cam_x, self.cam_y = settle_cam

        # 1. Room Detection & Camera Clamping via WorldManager
        player_cx = self.player.x + self.player.w / 2
        player_cy = self.player.y + self.player.h / 2
        prev_level = self.world.current_level
        new_level = self.world.detect_level(player_cx, player_cy)

        # Camera clamping (works for both standard 128x128 and larger rooms)
        if not self.world.is_settling():
            new_cam_x, new_cam_y = self.world.get_camera_clamped(self.player.x, self.player.y)
            new_cam_x = int(new_cam_x)
            new_cam_y = int(new_cam_y)
        else:
            # During settle, don't override camera — settle lerp handles it
            new_cam_x, new_cam_y = self.cam_x, self.cam_y

        # Detect room transition
        if new_level and new_level is not prev_level:
            # Remember source room for entrance door auto-open
            self._prev_level_id = prev_level.id if prev_level else None
            # Nudge player first so transition targets the correct camera position
            self._nudge_player_into_level(new_level)
            # Trigger freeze-and-slide transition using nudged player position
            self.world.trigger_transition(new_level, self.cam_x, self.cam_y,
                                          self.player.x, self.player.y)
            return
        elif new_cam_x != self.cam_x or new_cam_y != self.cam_y:
            # Camera moved within a large room (scrolling)
            self.cam_x = new_cam_x
            self.cam_y = new_cam_y
            self.rooms_visited.add(snap_to_grid(self.cam_x, self.cam_y))

        # Update block regeneration timers
        self.world.update_block_regen(self.level_map)

        # Handle delayed BOSS trigger (Safe Distance Check)
        if self.pending_boss_trigger:
            rel_x = self.player.x - self.cam_x
            rel_y = self.player.y - self.cam_y
            # Only trigger boss when player is safely inside (16px from edges)
            if 16 < rel_x < VIEWPORT_W - 16 and 16 < rel_y < VIEWPORT_H - 16:
                self.check_boss_trigger()
                self.pending_boss_trigger = False

        # 2. Always update effects/particles
        for eff in self.effects:
            eff.update()
        self.effects = [eff for eff in self.effects if eff.is_active]

        for part in self.particles:
            part.update()
        self.particles = [part for part in self.particles if part.is_active]

        # 3. WON State handling
        if self.game_state == "WON":
            if pyxel.btnp(pyxel.KEY_R):
                self.reset()
                self.game_state = "PLAYING"
            return

        # 4. Hit-stop logic
        if self.stop_frames > 0:
            self.stop_frames -= 1
            return

        # 5. Death handling -- enter DEAD state for animation (D-15, D-16)
        if not self.player.is_alive:
            self.game_state = "DEAD"
            self.death_timer = 0
            return

        # 5b. Pause toggle (D-10, SYS-03)
        if inp.btnp("pause"):
            self.game_state = "PAUSED"
            return

        # 6. Main Logic Update
        self.player.update(self.slime)

        # Closed doors block player movement (suppressed during post-entry grace period)
        if self.door_grace_frames <= 0:
            for door in self.doors:
                if not door.is_open and door.check_collision(
                        self.player.x, self.player.y, self.player.w, self.player.h):
                    # Determine push direction based on player approach side
                    px_center = self.player.x + self.player.w / 2
                    door_center = door.x + door.w / 2
                    if px_center < door_center:
                        self.player.x = door.x - self.player.w
                    else:
                        self.player.x = door.x + door.w
                    self.player.dx = 0

        self.slime.update(self.player.x, self.player.y, self.player.facing_right, self.level_map, self.player.is_fused)

        # Off-screen slime recovery
        if (not self.player.is_fused and 
            (self.slime.x < self.cam_x - 8 or self.slime.x > self.cam_x + VIEWPORT_W or
             self.slime.y < self.cam_y - 8 or self.slime.y > self.cam_y + VIEWPORT_H)):
            self.slime.reform(self.player.x, self.player.y, self.player.facing_right, self.level_map)

        # Slime Boost enemy stomp damage (D-10)
        if self.player.state == "BOOSTING":
            stomp_x = self.player.x + (self.player.w - BOOST_DOWNWARD_DAMAGE_W) // 2
            stomp_y = self.player.y + self.player.h
            for enemy in self.enemies:
                if not enemy.is_alive:
                    continue
                # AABB overlap check for stomp hitbox below player
                if (stomp_x < enemy.x + enemy.w and
                    stomp_x + BOOST_DOWNWARD_DAMAGE_W > enemy.x and
                    stomp_y < enemy.y + enemy.h and
                    stomp_y + BOOST_DOWNWARD_DAMAGE_H > enemy.y):
                    enemy.take_damage(1)
            # Also check boss
            if self.mole and self.mole.is_alive:
                if (stomp_x < self.mole.x + self.mole.w and
                    stomp_x + BOOST_DOWNWARD_DAMAGE_W > self.mole.x and
                    stomp_y < self.mole.y + self.mole.h and
                    stomp_y + BOOST_DOWNWARD_DAMAGE_H > self.mole.y):
                    self.mole.take_damage(1)

        # Update enemies & Combat
        for e in self.enemies:
            e.update(self.player, self.level_map, slime=self.slime)
            if not e.is_alive: continue
            
            for p in self.projectiles:
                if p.is_active and e.check_collision(p.x, p.y, p.w, p.h):
                    dmg = getattr(p, 'damage', 1)
                    e.take_damage(dmg)
                    self.spawn_explosion(e.x, e.y, 10)
                    p.is_active = False
            
            if self.player.state == "DIVING" and e.check_collision(self.player.x, self.player.y, self.player.w, self.player.h):
                e.take_damage()
                self.spawn_explosion(e.x, e.y, 10)
                self.slime.refill(10)
                self.player.on_block_break()
            
            if self.slime.is_punted and e.check_collision(self.slime.x, self.slime.y, self.slime.w, self.slime.h):
                e.take_damage()
                self.spawn_explosion(e.x, e.y, 10)
                self.slime.dx *= -0.5
                self.slime.dy = -2.0

        self.enemies = [e for e in self.enemies if e.is_alive]

        if self.mole:
            self.mole.update(self.projectiles, self.player, self.cam_x, self.cam_y, slime=self.slime)
            if not self.mole.is_alive:
                self.level_map.open_gates(self.cam_x, self.cam_y)
                self.event_flags["boss_defeated"] = True
                self.game_state = "WON"

        # Update secondary entities
        for p in self.projectiles:
            stain = p.update(self.cam_x, self.cam_y)
            if stain:
                self.stains.append(stain)
        self.projectiles = [p for p in self.projectiles if p.is_active]

        for s in self.stains:
            s.update()
        self.stains = [s for s in self.stains if s.is_active]

        for it in self.items:
            it.update()
            if it.is_active and (self.player.x < it.x + it.w and self.player.x + self.player.w > it.x and
                                 self.player.y < it.y + it.h and self.player.y + self.player.h > it.y):
                it.collect(self.player, self.slime)
                # Mark item as permanently collected via WorldManager
                if it.iid:
                    self.world.collect_item(it.iid)
        self.items = [it for it in self.items if it.is_active]

        # Save point interaction (D-01: UP to save)
        for sp in self.save_points:
            sp.update(self.player)
            if sp.is_player_near(self.player) and inp.btnp("up"):
                SaveManager.save(self)
                sp.on_save()

        # Update fixtures (OneWay, HiddenLoot, MapFixture stubs)
        for fixture in self.fixtures:
            fixture.update()

        # Tick down door grace period (prevents instant re-transition after room entry)
        if self.door_grace_frames > 0:
            self.door_grace_frames -= 1
            # Close entrance door behind player when grace expires (Metroid-style)
            if self.door_grace_frames == 0 and self._entrance_door is not None:
                self._entrance_door.close()
                self._entrance_door = None

        # Update doors: check kick, projectile hits, and player entry
        for door in self.doors:
            door.update()

            # Projectile opens door
            if not door.is_open:
                for p in self.projectiles:
                    if p.is_active and door.check_projectile_hit(p.x, p.y, p.w, p.h):
                        door.open()
                        p.is_active = False
                        break

            # Ram opens door (D-10 -- ram replaces kick for door interaction)
            if not door.is_open and self.player.state == "RAMMING":
                px = self.player.x + (8 if self.player.facing_right else -8)
                py = self.player.y
                if door.check_kick_hit(px, py):
                    door.open()

            # Open door + player collision = transition (suppressed during grace period)
            if (self.door_grace_frames <= 0 and door.is_open and
                    door.check_collision(self.player.x, self.player.y,
                                         self.player.w, self.player.h)):
                target = self._find_level_by_id(door.target_level_id)
                if target:
                    # Remember source room for entrance door auto-open
                    self._prev_level_id = self.world.current_level.id if self.world.current_level else None
                    self._nudge_player_into_level(target)
                    self.world.trigger_transition(target, self.cam_x, self.cam_y,
                                                  self.player.x, self.player.y)
                    return

        if self.shake_timer > 0:
            self.shake_timer -= 1

    def _find_level_by_id(self, level_id):
        """Find a LevelBounds by its identifier string."""
        if level_id is None:
            return None
        for level in self.world.levels:
            if level.id == level_id:
                return level
        return None

    def _on_room_enter(self):
        """Handle room entry after transition completes."""
        level = self.world.current_level
        self.pending_boss_trigger = True
        self.room_spawn_x = self.player.x
        self.room_spawn_y = self.player.y
        # Grace period: suppress door transitions until player clears the entrance
        self.door_grace_frames = 30  # ~0.5s at 60fps

        # Reset broken blocks on room entry (prevent soft-locks)
        self.world.reset_blocks_for_room(self.level_map)

        # Clear transient entities from previous room
        self.enemies = []
        self.projectiles = []
        self.stains = []
        self.doors = []
        self.save_points = []
        self.fixtures = []

        # Always spawn enemies on room entry (Metroid-style: enemies respawn,
        # collected items stay gone via is_item_collected check in spawn_enemies)
        self.spawn_enemies()

        # Auto-open the entrance door and nudge player past it
        self._entrance_door = None
        prev_id = getattr(self, '_prev_level_id', None)
        if prev_id:
            for door in self.doors:
                if door.target_level_id == prev_id:
                    door.open()
                    self._entrance_door = door
                    # Nudge player to the far side of the entrance door
                    if door.direction == "right":
                        self.player.x = door.x - self.player.w - 1
                    elif door.direction == "left":
                        self.player.x = door.x + door.w + 1
                    elif door.direction == "up":
                        self.player.y = door.y - self.player.h - 1
                    elif door.direction == "down":
                        self.player.y = door.y + door.h + 1

        # Check event-gated doors on room entry (D-04)
        for door in self.doors:
            door.check_event_open(self.event_flags)

        self.rooms_visited.add(snap_to_grid(self.cam_x, self.cam_y))

    def _nudge_player_into_level(self, target_level):
        """Reposition the player slightly into the target level to prevent re-triggering."""
        nudge = 4  # pixels
        px = self.player.x + self.player.w / 2
        py = self.player.y + self.player.h / 2

        # Nudge horizontally or vertically based on which edge was crossed
        if px < target_level.x:
            self.player.x = target_level.x + nudge
        elif px >= target_level.x + target_level.w:
            self.player.x = target_level.x + target_level.w - self.player.w - nudge
        if py < target_level.y:
            self.player.y = target_level.y + nudge
        elif py >= target_level.y + target_level.h:
            self.player.y = target_level.y + target_level.h - self.player.h - nudge

    def on_block_destroyed(self, tx, ty, tile_data):
        """Called when a destructible block is broken. Registers for regen."""
        self.world.break_block(tx, ty, tile_data)

    def spawn_explosion(self, x, y, color):
        self.effects.append(Effect(x, y))
        for _ in range(8):
            self.particles.append(Particle(x + 4, y + 4, color))

    def draw(self):
        pyxel.cls(0)

        # State dispatch for draw (Phase 11, SYS-01)
        if self.game_state == "TITLE":
            self._draw_title()
            return
        if self.game_state == "DEAD":
            self._draw_death()
            return

        # PLAYING / WON / PAUSED all render the game world
        self._draw_game_world()

        # === Phase 2: Reset clip and camera for HUD ===
        pyxel.clip()       # Remove clipping -- full screen available
        pyxel.camera()     # Reset camera to (0,0) screen coords

        # === Phase 3: Draw HUD in screen space ===
        self._draw_hud()

        # Pause overlay drawn on top of everything
        if self.game_state == "PAUSED":
            self._draw_pause_overlay()

    def _draw_game_world(self):
        """Draw the game world: tilemap, entities, effects, victory overlay.
        Extracted so _draw_death and _draw_pause can reuse it."""
        # === Phase 1: Game world (clipped to viewport) ===
        pyxel.clip(0, 0, VIEWPORT_W, VIEWPORT_H)

        # Screen shake + Camera follow
        offset_x = self.cam_x
        offset_y = self.cam_y
        if self.shake_timer > 0:
            offset_x += pyxel.rndi(-2, 2)
            offset_y += pyxel.rndi(-2, 2)

        pyxel.camera(offset_x, offset_y)

        # Draw tilemap from world origin
        pyxel.bltm(0, 0, 0, 0, 0, 2048, 2048)

        if self.mole:
            self.mole.draw()

        for e in self.enemies:
            e.draw()

        for s in self.stains:
            s.draw()

        for it in self.items:
            it.draw()

        for door in self.doors:
            door.draw()

        for sp in self.save_points:
            sp.draw()

        for fixture in self.fixtures:
            fixture.draw()

        for p in self.particles:
            p.draw(self.cam_x, self.cam_y)

        for eff in self.effects:
            eff.draw(self.cam_x, self.cam_y)

        self.slime.draw()
        for p in self.projectiles:
            p.draw()
        self.player.draw()

        # Victory overlay (re-centered for 320x176 viewport, world-space with camera)
        if self.game_state == "WON":
            box_w, box_h = 100, 30
            box_x = self.cam_x + (VIEWPORT_W - box_w) // 2
            box_y = self.cam_y + (VIEWPORT_H - box_h) // 2
            pyxel.rect(box_x, box_y, box_w, box_h, 0)
            pyxel.rectb(box_x, box_y, box_w, box_h, 7)
            pyxel.text(box_x + 30, box_y + 10, "VICTORY!", pyxel.frame_count % 16)
            pyxel.text(box_x + 15, box_y + 20, "PRESS R TO RESTART", 7)

    def _draw_hud(self):
        """Draw HUD in the bottom 16px strip (screen-space). Per D-03, D-04."""
        hud_y = VIEWPORT_H  # 176 -- top of HUD strip

        # HUD background
        pyxel.rect(0, hud_y, SCREEN_W, HUD_H, 1)  # Dark blue (palette 1)

        # HP pips (left side) -- per D-04
        for i in range(self.player.max_hp):
            pip_x = 4 + i * 10
            pip_y = hud_y + 4
            # Background pip
            pyxel.rect(pip_x, pip_y, 8, 8, 0)
            pyxel.rectb(pip_x, pip_y, 8, 8, 7)
            if i < self.player.hp:
                # Filled heart (red)
                pyxel.rect(pip_x + 2, pip_y + 2, 4, 4, 8)
            else:
                # Empty heart (dark)
                pyxel.rect(pip_x + 3, pip_y + 3, 2, 2, 5)

        # Mini-map (center of HUD strip, D-06, D-07, SYS-02)
        # Available space: x=58 to x=232 = 174px wide, 16px tall
        minimap_center_x = 58 + 174 // 2  # = 145
        minimap_center_y = hud_y + HUD_H // 2  # = 184
        minimap_max_w = 60  # Compact map width
        minimap_max_h = 12  # Leave 2px top/bottom margin in 16px strip
        # Border around mini-map area
        border_x = minimap_center_x - minimap_max_w // 2 - 1
        border_y = minimap_center_y - minimap_max_h // 2 - 1
        pyxel.rectb(border_x, border_y, minimap_max_w + 2, minimap_max_h + 2, 7)
        self._draw_minimap(minimap_center_x, minimap_center_y,
                           minimap_max_w, minimap_max_h)

        # Juice meter (right side) -- per D-04
        bar_max_w = 80  # Max bar width in pixels
        bar_x = SCREEN_W - bar_max_w - 4  # Right-aligned with 4px margin
        bar_y = hud_y + 4
        juice_max = self.slime.max_juice if self.slime.max_juice > 0 else 1
        juice_pct = self.slime.juice / juice_max
        juice_fill_w = int(bar_max_w * juice_pct)
        # Bar background
        pyxel.rect(bar_x, bar_y, bar_max_w, 8, 5)  # Dark gray
        # Bar fill
        if juice_fill_w > 0:
            pyxel.rect(bar_x, bar_y, juice_fill_w, 8, 11)  # Green fill
        # Bar border
        pyxel.rectb(bar_x, bar_y, bar_max_w, 8, 7)  # White border

    def _draw_minimap(self, center_x, center_y, max_w, max_h):
        """Draw room map as colored rectangles.

        Args:
            center_x, center_y: center point for the map display (screen coords)
            max_w, max_h: maximum dimensions for the map
        """
        rects = compute_map_rects(self.world.levels, max_w, max_h,
                                  visited=self.rooms_visited)
        if not rects:
            return

        # Offset so map is centered on (center_x, center_y)
        total_w = max(rx + rw for rx, ry, rw, rh, _ in rects)
        total_h = max(ry + rh for rx, ry, rw, rh, _ in rects)
        ox = center_x - total_w // 2
        oy = center_y - total_h // 2

        current_cell = snap_to_grid(self.cam_x, self.cam_y)

        for rx, ry, rw, rh, cell_key in rects:
            color = get_room_color(cell_key, current_cell, self.room_types,
                                    pyxel.frame_count, levels=self.world.levels)
            pyxel.rect(ox + rx, oy + ry, rw, rh, color)

    # === State methods (Phase 11, SYS-01/SYS-03) ===

    def restore_from_save(self, data):
        """Apply saved state to current game. Called after reset() sets up the world."""
        p = data["player"]
        self.player.max_hp = min(p["max_hp"], MAX_HP_CAP)
        self.player.hp = self.player.max_hp  # Full HP on load (D-04)
        self.player.has_drill = p.get("has_drill", False)
        self.player.has_dash = p.get("has_dash", False)
        self.player.has_shield = p.get("has_shield", False)
        self.player.has_shield_t2 = p.get("has_shield_t2", False)
        self.player.has_boost = p.get("has_boost", False)

        s = data["slime"]
        self.slime.max_juice = min(s["max_juice"], MAX_JUICE_CAP)
        self.slime.juice = self.slime.max_juice  # Full juice on load (D-04)

        w = data.get("world", {})
        self.world.collected_iids = set(w.get("collected_iids", []))
        self.event_flags = dict(data.get("event_flags", {}))
        self.rooms_visited = set(tuple(r) for r in data.get("visited_rooms", []))

        # Teleport player to save room
        save_room_id = data.get("save_room_id")
        if save_room_id:
            for level in self.world.levels:
                if level.id == save_room_id:
                    # Try to spawn at SavePoint entity within room
                    spawned = False
                    for ent in self.level_map.entities:
                        if ENTITY_ALIASES.get(ent["type"], ent["type"]) == "SavePoint":
                            ex, ey = ent["x"], ent["y"]
                            # Inline bounds check (LevelBounds.contains exists but
                            # we use inline check to match plan convention)
                            if (level.x <= ex < level.x + level.w and
                                level.y <= ey < level.y + level.h):
                                self.player.x = ex
                                self.player.y = ey
                                spawned = True
                                break
                    if not spawned:
                        # Fallback: room center
                        self.player.x = level.x + level.w // 2
                        self.player.y = level.y + level.h // 2
                    self.world.detect_level(self.player.x + self.player.w / 2,
                                            self.player.y + self.player.h / 2)
                    self.cam_x, self.cam_y = self.world.get_camera_clamped(
                        self.player.x, self.player.y)
                    self.cam_x = int(self.cam_x)
                    self.cam_y = int(self.cam_y)
                    break
        # Defensive clear before spawn to prevent duplicates (INT-04, D-10)
        self.enemies = []
        self.items = []
        self.projectiles = []
        self.stains = []
        self.doors = []
        self.save_points = []
        self.fixtures = []
        self.spawn_enemies()

    def _update_title(self):
        """Title screen menu input (D-17)."""
        has_save = SaveManager.exists()
        max_cursor = 1 if has_save else 0

        if self.title_confirm_active:
            # "ERASE SAVE AND START OVER?" sub-menu
            if inp.btnp("up") or inp.btnp("down"):
                self.title_confirm_cursor = 1 - self.title_confirm_cursor  # Toggle YES/NO
            if inp.btnp("confirm"):
                if self.title_confirm_cursor == 0:  # YES
                    SaveManager.delete()
                    self.reset()
                    self.game_state = "PLAYING"
                else:  # NO
                    self.title_confirm_active = False
            return

        if inp.btnp("up"):
            self.title_cursor = max(0, self.title_cursor - 1)
        if inp.btnp("down"):
            self.title_cursor = min(max_cursor, self.title_cursor + 1)
        if inp.btnp("confirm"):
            if has_save and self.title_cursor == 0:
                # CONTINUE
                data = SaveManager.load()
                self.reset()
                self.restore_from_save(data)
                self.game_state = "PLAYING"
            elif has_save and self.title_cursor == 1:
                # NEW GAME with existing save -- confirm erase
                self.title_confirm_active = True
                self.title_confirm_cursor = 1  # Default to NO
            else:
                # NEW GAME (no existing save)
                self.reset()
                self.game_state = "PLAYING"

    def _draw_title(self):
        """Draw title screen (D-17). Per UI-SPEC layout."""
        pyxel.cls(0)
        has_save = SaveManager.exists()

        if self.title_confirm_active:
            # Erase confirmation sub-screen
            text = "ERASE SAVE AND START OVER?"
            tx = (SCREEN_W - len(text) * 4) // 2
            pyxel.text(tx, 80, text, 7)
            yes_x = (SCREEN_W - 12) // 2  # "YES" = 3 chars * 4px
            pyxel.text(yes_x, 100, "YES", 7 if self.title_confirm_cursor == 0 else 5)
            pyxel.text(yes_x, 112, "NO", 7 if self.title_confirm_cursor == 1 else 5)
            cursor_y = 100 + self.title_confirm_cursor * 12
            pyxel.text(yes_x - 8, cursor_y, ">", 10)
            return

        # Title text centered at y=60 per UI-SPEC
        title = "JELLY ROLL"
        tx = (SCREEN_W - len(title) * 4) // 2
        pyxel.text(tx, 60, title, 7)

        # Menu options starting at y=100 per UI-SPEC
        menu_x = tx
        if has_save:
            pyxel.text(menu_x, 100, "CONTINUE", 7 if self.title_cursor == 0 else 5)
            pyxel.text(menu_x, 112, "NEW GAME", 7 if self.title_cursor == 1 else 5)
        else:
            pyxel.text(menu_x, 100, "NEW GAME", 7)

        # Cursor indicator per UI-SPEC: ">" palette 10, 8px left
        cursor_y = 100 + self.title_cursor * 12
        pyxel.text(menu_x - 8, cursor_y, ">", 10)

    def _update_death(self):
        """Death animation: 30 freeze + 30 fade, then load save (D-15, D-16)."""
        self.death_timer += 1
        total = DEATH_FREEZE_FRAMES + DEATH_FADE_FRAMES
        if self.death_timer >= total:
            data = SaveManager.load()
            if data:
                self.reset()
                self.restore_from_save(data)
                self.game_state = "PLAYING"
            else:
                self.game_state = "TITLE"
                self.title_cursor = 0

    def _draw_death(self):
        """Draw death sequence: frozen world then fade to black (D-16)."""
        if self.death_timer < DEATH_FREEZE_FRAMES:
            # Freeze phase: draw game world frozen
            self._draw_game_world()
        else:
            # Fade phase: black screen
            pyxel.cls(0)

    def _update_pause(self):
        """Pause screen input: menu navigation + actions (D-10, D-11, SYS-03)."""
        # Determine menu items
        menu_items = ["RESUME"]
        in_save_room = any(sp.is_player_near(self.player) for sp in self.save_points)
        if in_save_room:
            menu_items.append("SAVE")
        menu_items.append("QUIT")

        if not hasattr(self, '_pause_cursor'):
            self._pause_cursor = 0
        max_cursor = len(menu_items) - 1

        # ESC closes pause (same as RESUME, consume frame per Pitfall 4)
        if inp.btnp("pause"):
            self._pause_cursor = 0
            self.game_state = "PLAYING"
            return

        if inp.btnp("up"):
            self._pause_cursor = max(0, self._pause_cursor - 1)
        if inp.btnp("down"):
            self._pause_cursor = min(max_cursor, self._pause_cursor + 1)

        if inp.btnp("confirm"):
            selected = menu_items[self._pause_cursor]
            if selected == "RESUME":
                self._pause_cursor = 0
                self.game_state = "PLAYING"
            elif selected == "SAVE":
                SaveManager.save(self)
                # Flash feedback -- find nearby save point
                for sp in self.save_points:
                    if sp.is_player_near(self.player):
                        sp.on_save()
                        break
            elif selected == "QUIT":
                self._pause_cursor = 0
                self.game_state = "TITLE"
                self.title_cursor = 0

    def _draw_pause_overlay(self):
        """Draw pause screen: black overlay + Macro-map + stats + menu (D-11, D-12, SYS-03)."""
        # Black overlay over frozen game world
        pyxel.rect(0, 0, SCREEN_W, SCREEN_H, 0)

        # === Macro-map (centered, y=16, ~120x60) ===
        map_center_x = SCREEN_W // 2  # 160
        map_center_y = 46  # Centered in y=16..y=76 region
        map_max_w = 120
        map_max_h = 60
        self._draw_minimap(map_center_x, map_center_y, map_max_w, map_max_h)

        # === Stats (below map, y=96) ===
        stats_y = 96
        hp_text = f"HP: {self.player.hp}/{self.player.max_hp}"
        juice_text = f"JUICE: {int(self.slime.juice)}/{int(self.slime.max_juice)}"
        # Center the two stats
        total_text = f"{hp_text}    {juice_text}"
        stats_x = (SCREEN_W - len(total_text) * 4) // 2
        pyxel.text(stats_x, stats_y, hp_text, 7)
        pyxel.text(stats_x + len(hp_text) * 4 + 16, stats_y, juice_text, 11)

        # === Ability row (y=108) ===
        abilities = [
            ("DSH", getattr(self.player, 'has_dash', False)),
            ("SHD", getattr(self.player, 'has_shield', False)),
            ("BST", getattr(self.player, 'has_boost', False)),
            ("RAM", True),  # Ram is always available (fused ability, no pickup)
            ("CHG", True),  # Charge shot always available (fused ability)
        ]
        ability_y = 108
        ability_spacing = 20  # ~20px per abbreviation
        total_ability_w = len(abilities) * ability_spacing
        ability_x = (SCREEN_W - total_ability_w) // 2
        for i, (abbr, unlocked) in enumerate(abilities):
            color = 7 if unlocked else 1  # White if unlocked, dark blue if locked
            pyxel.text(ability_x + i * ability_spacing, ability_y, abbr, color)

        # === Menu (y=124) ===
        menu_items = ["RESUME"]
        in_save_room = any(sp.is_player_near(self.player) for sp in self.save_points)
        if in_save_room:
            menu_items.append("SAVE")
        menu_items.append("QUIT")

        menu_y = 124
        menu_x = (SCREEN_W - 32) // 2  # Rough center for menu text
        cursor = getattr(self, '_pause_cursor', 0)
        for i, item in enumerate(menu_items):
            y = menu_y + i * 12
            is_selected = i == cursor
            pyxel.text(menu_x, y, item, 7 if is_selected else 5)
            if is_selected:
                pyxel.text(menu_x - 8, y, ">", 10)

if __name__ == "__main__":
    Game()
