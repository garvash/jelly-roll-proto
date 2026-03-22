import pyxel
from src.core.constants import TILE_SIZE

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

    def update(self, player, level_map):
        pass

    def draw(self):
        pass

    def take_damage(self):
        self.hp -= 1
        if self.hp <= 0:
            self.is_alive = False
            if self.game:
                from src.entities.effects import Effect
                self.game.effects.append(Effect(self.x, self.y, "EXPLOSION"))

    def check_collision(self, x, y, w, h):
        return (self.x < x + w and
                self.x + self.w > x and
                self.y < y + h and
                self.y + self.h > y)

class Snail(Enemy):
    def __init__(self, x, y, game=None):
        super().__init__(x, y, game=game)
        self.dx = 0.125 # 8x slower movement
        self.dy = 0
        self.gravity = 0.5

    def update(self, player, level_map):
        if not self.is_alive:
            return

        # Apply gravity
        self.dy = min(self.dy + self.gravity, 4)
        
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
            player.take_damage(1, self.x + self.w / 2)

    def draw(self):
        if not self.is_alive:
            return
        # Snail sprite at (0, 16) with 2-frame animation
        # Changes frame every 1 pixel of movement
        u_anim = (int(self.x) % 2) * 8
        
        w = self.w if self.facing_right else -self.w
        pyxel.blt(self.x, self.y, 1, u_anim, 16, w, self.h, 0)

class Bat(Enemy):
    def __init__(self, x, y, game=None):
        super().__init__(x, y, game=game)
        self.start_y = y
        self.state = "HANGING" # HANGING, DIVING, RETURNING
        self.timer = 0

    def update(self, player, level_map):
        if not self.is_alive:
            return

        if self.state == "HANGING":
            # Detect player within 64 pixels horizontally
            if abs(player.x - self.x) < 64 and player.y > self.y:
                self.state = "DIVING"
        
        elif self.state == "DIVING":
            self.y += 3 # Faster dive
            # Hit ground or too far
            if level_map.check_collision(self.x, self.y, self.w, self.h) or self.y > self.start_y + 100:
                self.state = "RETURNING"
        
        elif self.state == "RETURNING":
            if self.y > self.start_y:
                self.y -= 1.5
            else:
                self.y = self.start_y
                self.state = "HANGING"

        # Player contact
        if self.check_collision(player.x, player.y, player.w, player.h):
            player.take_damage(1, self.x + self.w / 2)

    def draw(self):
        if not self.is_alive:
            return
        # Bat sprite at (0, 24)
        # 2-frame flapping animation
        u_anim = (pyxel.frame_count // 6 % 2) * 8 if self.state != "HANGING" else 0
        pyxel.blt(self.x, self.y, 1, u_anim, 24, self.w, self.h, 0)
