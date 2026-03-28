import pyxel
import random
import math
from src.core.constants import TILE_SIZE, BOSS_ROCK_SPEED, VIEWPORT_W, VIEWPORT_H, CULL_MARGIN

class BossRock:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx * BOSS_ROCK_SPEED
        self.dy = dy * BOSS_ROCK_SPEED
        self.w = 8
        self.h = 8
        self.is_active = True

    def update(self, player, cam_x, cam_y, slime=None):
        self.x += self.dx
        self.y += self.dy

        # Check collision with player
        if (self.x < player.x + player.w and
            self.x + self.w > player.x and
            self.y < player.y + player.h and
            self.y + self.h > player.y):
            player.take_damage(1, self.x + 4, slime=slime)
            self.is_active = False
            
        # Screen boundary check (relative to camera room)
        if (self.x < cam_x - CULL_MARGIN or self.x > cam_x + VIEWPORT_W + CULL_MARGIN or
            self.y < cam_y - CULL_MARGIN or self.y > cam_y + VIEWPORT_H + CULL_MARGIN):
            self.is_active = False

    def draw(self):
        # Draw as the boulder sprite at (32, 32) in image 1
        pyxel.blt(self.x, self.y, 1, 32, 32, 8, 8, 0)

class Mole:
    def __init__(self, x, y, level_map):
        self.x = x
        self.y = y
        self.w = 16
        self.h = 16
        self.level_map = level_map
        
        # States: BURROWED, EMERGING, VULNERABLE, DYING
        self.state = "BURROWED"
        self.state_timer = 0
        self.hp = 3
        self.is_alive = True
        
        # Burrow movement
        self.target_x = x
        self.move_speed = 1.0
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
        if self.state_timer > 60 and random.random() < 0.02:
            self.state = "EMERGING"
            self.state_timer = 0

    def update_emerging(self, projectiles, player, slime=None):
        # Contact damage
        if self.check_collision(player.x, player.y, player.w, player.h):
            player.take_damage(1, self.x + 8, slime=slime)

        # Throw rocks occasionally
        if self.state_timer == 10 or self.state_timer == 30:
            angle = math.atan2(player.y - self.y, player.x - self.x)
            dx = math.cos(angle)
            dy = math.sin(angle)
            self.rocks.append(BossRock(self.x + 8, self.y + 8, dx, dy))

        # Vulnerable to projectiles in this state
        for p in projectiles:
            if self.check_collision(p.x, p.y, p.w, p.h):
                p.is_active = False
                self.state = "VULNERABLE"
                self.state_timer = 0
                return
        
        # If not hit, after some time, go back to burrowed
        if self.state_timer > 45:
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

        if self.state_timer > 90: # 3 seconds vulnerable
            self.state = "BURROWED"
            self.state_timer = 0

    def update_dying(self):
        if self.state_timer > 30:
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

        # 2-frame animation offset
        u_anim = (pyxel.frame_count // 10 % 2) * 16

        if self.state == "BURROWED":
            if pyxel.frame_count % 4 < 2:
                pyxel.rect(self.x + 4, self.y + 12, 8, 4, 4)
        elif self.state == "EMERGING":
            dx = pyxel.rndi(-1, 1)
            w = 16 if self.facing_right else -16
            pyxel.blt(self.x + dx, self.y, 1, u_anim, 32, w, 16, 0)
        elif self.state == "VULNERABLE":
            w = 16 if self.facing_right else -16
            if pyxel.frame_count % 2 == 0:
                pyxel.blt(self.x, self.y, 1, u_anim, 32, w, 16, 0)
            else:
                pyxel.blt(self.x, self.y, 1, u_anim, 32, w, 16, 0)
                pyxel.rectb(self.x, self.y, 16, 16, 7)
        elif self.state == "DYING":
            pyxel.circ(self.x + 8, self.y + 8, self.state_timer // 2, 7)
