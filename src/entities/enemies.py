import pyxel
from src.core.constants import TILE_SIZE, SPRITE_SIZE
from src.core.sprite_utils import draw_sprite

class Enemy:
    def __init__(self, x, y, w=8, h=8, game=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.game = game
        self.is_alive = True
        self.hp = 1
        self.facing_right = True

    def update(self, player, level_map, slime=None):
        pass

    def draw(self):
        pass

    def take_damage(self, amount=1):
        self.hp -= amount
        if self.hp <= 0:
            self.is_alive = False
            if self.game:
                from src.entities.effects import Effect
                self.game.effects.append(Effect(self.x, self.y, "EXPLOSION"))

    HURTBOX_MARGIN = 4  # Extra pixels around collision box for generous hit detection

    def check_collision(self, x, y, w, h):
        m = self.HURTBOX_MARGIN
        return (self.x - m < x + w and
                self.x + self.w + m > x and
                self.y - m < y + h and
                self.y + self.h + m > y)

class Snail(Enemy):
    def __init__(self, x, y, game=None):
        super().__init__(x, y, game=game)
        self.dx = 0.0625 # 16x slower movement (halved for 60fps)
        self.dy = 0
        self.gravity = 0.125

    def update(self, player, level_map, slime=None):
        if not self.is_alive:
            return

        # Apply gravity
        self.dy = min(self.dy + self.gravity, 2)
        
        # Vertical movement pass
        self.y += self.dy
        
        collision = level_map.check_collision(self.x, self.y, self.w, self.h)
        # 1px look-down to prevent jitter (same as player)
        if not collision and self.dy >= 0:
            if level_map.check_collision(self.x, self.y + 1, self.w, self.h):
                collision = True
        
        if collision:
            if self.dy >= 0:
                # Snap to floor precisely
                target_row = int((self.y + self.h) // 8)
                self.y = target_row * 8 - self.h
                self.dy = 0
            elif self.dy < 0:
                self.y = (int(self.y // 8) + 1) * 8
                self.dy = 0

        # Horizontal movement pass
        new_x = self.x + self.dx
        
        # Wall detection
        if level_map.check_collision(new_x, self.y, self.w, self.h):
            self.dx *= -1
            self.facing_right = not self.facing_right
        else:
            # Ledge detection
            # Check a point slightly inside the sprite's width to be more stable
            check_x = new_x + (self.w if self.dx > 0 else -1)
            if not level_map.check_collision(check_x, self.y + self.h, 1, 1):
                self.dx *= -1
                self.facing_right = not self.facing_right
            else:
                self.x = new_x

        # Player contact
        if self.check_collision(player.x, player.y, player.w, player.h):
            player.take_damage(1, self.x + self.w / 2, slime=slime)

    def draw(self):
        if not self.is_alive:
            return
        # Snail sprite at y=32 in bank 1, 16px stride for 16x16 frames
        u_anim = (int(self.x) % 2) * 16
        draw_sprite(self.x, self.y, self.w, self.h, 1, u_anim, 32,
                    SPRITE_SIZE, SPRITE_SIZE, self.facing_right)

class Bat(Enemy):
    def __init__(self, x, y, game=None):
        super().__init__(x, y, game=game)
        self.start_y = y + TILE_SIZE  # Offset down 1 tile from ceiling pivot
        self.y = self.start_y
        self.state = "HANGING" # HANGING, DIVING, RETURNING
        self.timer = 0

    def update(self, player, level_map, slime=None):
        if not self.is_alive:
            return

        if self.state == "HANGING":
            # Detect player within 64 pixels horizontally
            if abs(player.x - self.x) < 64 and player.y > self.y:
                self.state = "DIVING"
        
        elif self.state == "DIVING":
            self.y += 1.5 # Faster dive (halved for 60fps)
            # Hit ground or too far
            if level_map.check_collision(self.x, self.y, self.w, self.h) or self.y > self.start_y + 100:
                self.state = "RETURNING"
        
        elif self.state == "RETURNING":
            if self.y > self.start_y:
                self.y -= 0.75
            else:
                self.y = self.start_y
                self.state = "HANGING"

        # Player contact
        if self.check_collision(player.x, player.y, player.w, player.h):
            player.take_damage(1, self.x + self.w / 2, slime=slime)

    def draw(self):
        if not self.is_alive:
            return
        # Bat sprite at y=48 in bank 1: frame 0=hanging, frames 1-2=flying
        if self.state == "HANGING":
            u_anim = 0
        else:
            u_anim = 16 + (pyxel.frame_count // 12 % 2) * 16  # Alternate u=16 and u=32
        draw_sprite(self.x, self.y, self.w, self.h, 1, u_anim, 48,
                    SPRITE_SIZE, SPRITE_SIZE, self.facing_right)
