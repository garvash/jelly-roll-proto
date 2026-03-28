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

# Fusion System (D-01, D-02, D-04, D-05)
RECALL_SPEED = 8.0              # Slime zip speed toward player in pixels/frame (~4-6 frames to arrive) (D-25)
RECALL_OVERLAP_DIST = 4         # Pixel distance for slime to be "overlapping" player for fusion (D-26)
MANA_SHIELD_COST = 20.0         # Juice consumed per hit while fused (D-04)
SLIME_DISSIPATE_COOLDOWN = 120  # Frames (~2 sec) before slime reforms after juice-empty dissipation (D-05)

# Slime Recall Visual
RECALL_TRAIL_COLOR = 11         # Pyxel palette color for rubber-band trail (D-25)

# Spit vs Recall threshold
SPIT_HOLD_THRESHOLD = 8         # Frames: <= this on Z release = spit, > this = was charging/recalling (D-06)

# Directional Slime Hold (ABL-03, D-19)
HOLD_TAP_THRESHOLD = 5          # Frames: <= this on release = tap (reposition slime), > this = walk

# Slime Ram (ABL-01, D-12 through D-14)
RAM_SPEED = 5.0                 # High speed horizontal movement pixels/frame (D-12)
RAM_DIAGONAL_FACTOR = 0.7       # Y-component multiplier for diagonal ram
RAM_BLOCK_COST = 15.0           # Juice cost per CRACKED_H block broken (D-13)
RAM_INVINCIBLE = True           # Player is invincible during ram (D-12)

# Charge Shot (ABL-04, D-16 through D-18)
CHARGE_SHOT_SPEED = 6.0         # Projectile speed (faster than normal spit)
CHARGE_SHOT_SIZE = 8            # Larger projectile hitbox (vs 4 for normal spit)
CHARGE_SHOT_DAMAGE = 3          # High damage (D-16)
