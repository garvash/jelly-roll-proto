# Debug: unlock all abilities at start (set False for normal gameplay)
DEBUG_ALL_ABILITIES = True

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

# Biome-Specific Gates (ABL-01, ABL-02)
TILE_CRACKED_H = (7, 1)         # Horizontal cracked block (ABL-01 variant)
TILE_CRACKED_V = (8, 1)         # Vertical cracked block (ABL-02 variant)

# Zone Hazard Tiles -- passable zones with continuous juice drain (D-14)
TILE_WATER = (9, 1)    # IntGrid value 6: slow drain
TILE_ACID  = (10, 1)   # IntGrid value 7: medium drain
TILE_LAVA  = (11, 1)   # IntGrid value 8: fast drain

# Zone Hazard Drain Rates (juice per frame at 60fps) (D-03)
HAZARD_DRAIN_SLOW   = 0.5   # Water: ~6.7s full-to-empty (200 juice)
HAZARD_DRAIN_MEDIUM = 1.5   # Acid: ~2.2s full-to-empty
HAZARD_DRAIN_FAST   = 3.0   # Lava: ~1.1s full-to-empty

HAZARD_DRAIN_RATES = {
    TILE_WATER: HAZARD_DRAIN_SLOW,
    TILE_ACID:  HAZARD_DRAIN_MEDIUM,
    TILE_LAVA:  HAZARD_DRAIN_FAST,
}

# Shield Tier 2 drain reduction (D-05): flat subtraction from drain rate
SHIELD_T2_DRAIN_REDUCTION = 0.5  # Slow becomes 0 (free), medium becomes slow, fast becomes medium

# HP drain when juice empty in hazard zone (D-04)
HAZARD_HP_DRAIN_INTERVAL = 30  # Frames between HP ticks (0.5s at 60fps)

# Shield anti-flicker cooldown (Pitfall 2 from RESEARCH)
SHIELD_REACTIVATION_COOLDOWN = 60  # Frames before shield can re-activate after deactivation (1s)

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

# Slime Boost (ABL-06, D-07 through D-11)
BOOST_FORCE = -3.5           # Upward impulse per tap (similar to JUMP_FORCE)
BOOST_JUICE_COST = 25.0      # Juice per tap (~8 boosts from full 200)
BOOST_RECOMMIT_WINDOW = 12   # Frames between taps to chain (~0.2s at 60fps)
BOOST_DOWNWARD_DAMAGE_W = 12 # Hitbox width for enemy stomp damage
BOOST_DOWNWARD_DAMAGE_H = 8  # Hitbox height below player for enemy damage

# Charge Shot Recoil (D-17): physics-based bomb-climb exploit
CHARGE_RECOIL_FORCE = -2.5   # Upward impulse applied on charge shot fire

# Charge Shot Windup (gap fix: visual absorption before fire)
CHARGE_WINDUP_DURATION = 20  # Frames of windup (~0.33s at 60fps) before charge shot fires

# CRACKED_V Gate Breaking (ABL-02, D-01, D-02)
DRILL_CRACKED_V_COST = 20.0   # Juice cost per CRACKED_V broken via Drill Dive
BOOST_CRACKED_V_COST = 25.0   # Juice cost per CRACKED_V broken via Boost
