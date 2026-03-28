# Tile Constants (u, v) in tileset
TILE_SIZE = 8
TILE_EMPTY = (31, 31)
TILE_SOLID = (0, 1)
TILE_HAZARD = (1, 1)
TILE_DESTRUCTIBLE = (2, 1)
TILE_GATE = (3, 1)
TILE_SWITCH = (5, 1)

# Biome-Specific Gates
TILE_GOO_MOLD = (6, 1)          # IntGrid value 10: Negative Space (Goo-Mold)
TILE_CRACKED_H = (7, 1)         # Horizontal cracked block (ABL-01 variant)
TILE_CRACKED_V = (8, 1)         # Vertical cracked block (ABL-02 variant)

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

# Basic Dash (D-15)
DASH_SPEED = 4.0        # Pixels/frame (~2 tiles in 8 frames)
DASH_DURATION = 8       # Frames of dash movement
DASH_IFRAMES = 8        # Frames of invulnerability during dash
DASH_COOLDOWN = 20      # Frames before dash can be used again
