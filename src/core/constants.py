# Tile Constants (u, v) in tileset
TILE_SIZE = 8

# Screen / Display (D-01, D-02, D-08)
SCREEN_W = 320       # Full pyxel window width
SCREEN_H = 192       # Full pyxel window height
VIEWPORT_W = 320     # Playable area width (same as screen)
VIEWPORT_H = 176     # Playable area height (above HUD)
HUD_H = 16           # HUD strip height at bottom of screen

# Culling margin for off-screen entity despawn (boss, projectiles)
CULL_MARGIN = 16     # Extra pixels beyond viewport before culling

TILE_EMPTY = (31, 31)
TILE_SOLID = (0, 1)
TILE_HAZARD = (1, 1)
TILE_DESTRUCTIBLE = (2, 1)
TILE_GATE = (3, 1)
TILE_SWITCH = (5, 1)

# Horizontal Movement
WALK_ACCEL = 0.5
WALK_FRICTION = 0.6
MAX_WALK_SPEED = 2.5

# Vertical Movement
GRAVITY = 0.25
MAX_FALL_SPEED = 3.5
JUMP_FORCE = -4.0
VARIABLE_JUMP_REDUCTION = 0.5
FALLING_GRAVITY_MULTIPLIER = 1.5

# Forgiving Mechanics
COYOTE_TIME = 6
JUMP_BUFFER = 4

# Wall Slide/Jump
WALL_SLIDE_FRICTION = 0.2
WALL_JUMP_X_IMPULSE = 3.0
WALL_JUMP_Y_FORCE = -3.5

# Slime Follow Constants
SLIME_FOLLOW_DELAY = 8
SLIME_MAX_DIST = 100
SLIME_REFORM_DIST = 8
SLIME_LERP_FACTOR = 0.4

# Slime Juice Resource
JUICE_MAX = 200.0
JUICE_REGEN_RATE = 0.5
JUICE_MIN_SCALE = 0.25 # 2x2 vs 8x8 (0.25 * 8 = 2)
SLIME_SPIT_COST = 10.0

# Projectile
PROJECTILE_SPEED = 4.0
BOSS_ROCK_SPEED = 2.0

# Drill Dive
DRILL_SPEED = 4.0
DRILL_DRIFT_SPEED = 1.0
DRILL_IMPACT_COST = 20.0
DRILL_ACTIVATION_COST = 5.0
DRILL_BLOCK_REFUND = 15.0

# Juice Effects
DRILL_SHAKE_DURATION = 6
DRILL_HITSTOP_FRAMES = 3

# Player Health & Damage
PLAYER_MAX_HP = 3
INVULN_DURATION = 60
KNOCKBACK_FORCE_X = 2.0
KNOCKBACK_FORCE_Y = -2.5

# Combat Mechanics
KICK_DURATION = 10
SLIME_PUNT_SPEED = 6.0
