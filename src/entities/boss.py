import pyxel
import random
import math
from src.core.constants import TILE_SIZE, BOSS_ROCK_SPEED, VIEWPORT_W, VIEWPORT_H, CULL_MARGIN, SPRITE_SIZE, BOSS_SPRITE_SIZE
from src.core.sprite_utils import draw_sprite

class BossRock:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx * BOSS_ROCK_SPEED
        self.dy = dy * BOSS_ROCK_SPEED
        self.w = 16
        self.h = 16
        self.is_active = True

    def update(self, player, cam_x, cam_y, slime=None):
        self.x += self.dx
        self.y += self.dy

        # Check collision with player
        if (self.x < player.x + player.w and
            self.x + self.w > player.x and
            self.y < player.y + player.h and
            self.y + self.h > player.y):
            player.take_damage(1, self.x + self.w // 2, slime=slime)
            self.is_active = False
            
        # Screen boundary check (relative to camera room)
        if (self.x < cam_x - CULL_MARGIN or self.x > cam_x + VIEWPORT_W + CULL_MARGIN or
            self.y < cam_y - CULL_MARGIN or self.y > cam_y + VIEWPORT_H + CULL_MARGIN):
            self.is_active = False

    def draw(self):
        # Rock sprite at y=80 (projectile row), frame 1 (u=16) in bank 1
        draw_sprite(self.x, self.y, self.w, self.h, 1, 16, 80,
                    SPRITE_SIZE, SPRITE_SIZE, True)

class Mole:
    def __init__(self, x, y, level_map):
        self.x = x
        self.y = y
        self.w = 24
        self.h = 28
        self.level_map = level_map
        
        # States: BURROWED, EMERGING, VULNERABLE, DYING
        self.state = "BURROWED"
        self.state_timer = 0
        self.hp = 3
        self.is_alive = True
        
        # Burrow movement
        self.target_x = x
        self.move_speed = 0.5
        self.facing_right = True
        self.rocks = []

    def update(self, projectiles, player, cam_x, cam_y, slime=None):
        if not self.is_alive:
            return

        self.state_timer += 1

        # Update rocks
        for r in self.rocks:
            r.update(player, cam_x, cam_y, slime=slime)
        self.rocks = [r for r in self.rocks if r.is_active]
        
        if self.state == "BURROWED":
            self.update_burrowed(player)
        elif self.state == "EMERGING":
            self.update_emerging(projectiles, player, slime=slime)
        elif self.state == "VULNERABLE":
            self.update_vulnerable(player)
        elif self.state == "DYING":
            self.update_dying()

    def update_burrowed(self, player):
        # Move towards player's X but stay underground
        if self.x < player.x:
            self.x += self.move_speed
            self.facing_right = True
        elif self.x > player.x:
            self.x -= self.move_speed
            self.facing_right = False
            
        # Randomly decide to emerge
        if self.state_timer > 120 and random.random() < 0.01:
            self.state = "EMERGING"
            self.state_timer = 0

    def update_emerging(self, projectiles, player, slime=None):
        # Contact damage
        if self.check_collision(player.x, player.y, player.w, player.h):
            player.take_damage(1, self.x + self.w // 2, slime=slime)

        # Throw rocks occasionally
        if self.state_timer == 20 or self.state_timer == 60:
            angle = math.atan2(player.y - self.y, player.x - self.x)
            dx = math.cos(angle)
            dy = math.sin(angle)
            self.rocks.append(BossRock(self.x + self.w // 2, self.y + self.h // 2, dx, dy))

        # Vulnerable to projectiles in this state
        for p in projectiles:
            if self.check_collision(p.x, p.y, p.w, p.h):
                p.is_active = False
                self.state = "VULNERABLE"
                self.state_timer = 0
                return
        
        # If not hit, after some time, go back to burrowed
        if self.state_timer > 90:
            self.state = "BURROWED"
            self.state_timer = 0

    def update_vulnerable(self, player):
        # Vulnerable to Drill Dive
        if player.state == "DIVING":
            if self.check_collision(player.x, player.y, player.w, player.h):
                self.hp -= 1
                if self.hp <= 0:
                    self.state = "DYING"
                else:
                    self.state = "BURROWED"
                self.state_timer = 0
                player.on_block_break() # Visual feedback
                return

        if self.state_timer > 180: # 3 seconds vulnerable
            self.state = "BURROWED"
            self.state_timer = 0

    def update_dying(self):
        if self.state_timer > 60:
            self.is_alive = False

    def check_collision(self, x, y, w, h):
        return (self.x < x + w and
                self.x + self.w > x and
                self.y < y + h and
                self.y + self.h > y)

    def draw(self):
        if not self.is_alive:
            return
            
        for r in self.rocks:
            r.draw()

        # 2-frame animation offset (32px stride for 32x32 boss frames)
        u_anim = (pyxel.frame_count // 20 % 2) * 32

        if self.state == "BURROWED":
            if pyxel.frame_count % 8 < 4:
                # Dirt rumble at ground level (bottom of collision box)
                pyxel.rect(self.x + 8, self.y + self.h - 4, 8, 4, 4)
        elif self.state == "EMERGING":
            dx = pyxel.rndi(-1, 1)
            draw_sprite(self.x + dx, self.y, self.w, self.h, 1, u_anim, 128,
                        BOSS_SPRITE_SIZE, BOSS_SPRITE_SIZE, self.facing_right)
        elif self.state == "VULNERABLE":
            if pyxel.frame_count % 4 < 2:
                draw_sprite(self.x, self.y, self.w, self.h, 1, u_anim, 128,
                            BOSS_SPRITE_SIZE, BOSS_SPRITE_SIZE, self.facing_right)
            else:
                draw_sprite(self.x, self.y, self.w, self.h, 1, u_anim, 128,
                            BOSS_SPRITE_SIZE, BOSS_SPRITE_SIZE, self.facing_right)
                # Vulnerability indicator: rect around collision box
                pyxel.rectb(self.x, self.y, self.w, self.h, 7)
        elif self.state == "DYING":
            pyxel.circ(self.x + self.w // 2, self.y + self.h // 2, self.state_timer // 2, 7)
