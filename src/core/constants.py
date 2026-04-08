# Tile Constants (u, v) in tileset
TILE_SIZE = 16

# Screen / Display (D-01, D-02, D-08)
SCREEN_W = 320       # Full pyxel window width
SCREEN_H = 192       # Full pyxel window height
VIEWPORT_W = 320     # Playable area width (same as screen)
VIEWPORT_H = 176     # Playable area height (above HUD)
HUD_H = 16           # HUD strip height at bottom of screen

# Culling margin for off-screen entity despawn (boss, projectiles)
CULL_MARGIN = 16     # Extra pixels beyond viewport before culling

# Sprite Dimensions (Phase 20: direct values, no SPRITE_SCALE indirection)
SPRITE_SIZE = 16       # Standard entity visual dimensions (= TILE_SIZE)
BOSS_SPRITE_SIZE = 32  # Boss entity visual dimensions (= 2 * TILE_SIZE)

TILE_EMPTY = (15, 15)  # Empty tile sentinel: bottom-right of 256x256 bank at 16px grid

# Zone Hazard Drain Rates (juice per frame at 60fps) (D-03)
HAZARD_DRAIN_SLOW   = 0.25  # Water: ~6.7s full-to-empty (200 juice)
HAZARD_DRAIN_MEDIUM = 0.75  # Acid: ~2.2s full-to-empty
HAZARD_DRAIN_FAST   = 1.5   # Lava: ~1.1s full-to-empty

HAZARD_DRAIN_RATES = {
    6: HAZARD_DRAIN_SLOW,   # water (IntGrid 6)
    7: HAZARD_DRAIN_MEDIUM, # acid (IntGrid 7)
    8: HAZARD_DRAIN_FAST,   # lava (IntGrid 8)
}

# Shield Tier 2 drain reduction (D-05): flat subtraction from drain rate
SHIELD_T2_DRAIN_REDUCTION = 0.25  # Slow becomes 0 (free), medium becomes slow, fast becomes medium

# HP drain when juice empty in hazard zone (D-04)
HAZARD_HP_DRAIN_INTERVAL = 60  # Frames between HP ticks (1s at 60fps)

# Shield anti-flicker cooldown (Pitfall 2 from RESEARCH)
SHIELD_REACTIVATION_COOLDOWN = 120  # Frames before shield can re-activate after deactivation (2s)

# Horizontal Movement
WALK_ACCEL = 0.125
WALK_FRICTION = 0.15
MAX_WALK_SPEED = 1.25

# Vertical Movement
GRAVITY = 0.0875
MAX_FALL_SPEED = 2.5
JUMP_FORCE = -3.25  # ~10 tile jump height (80px)
VARIABLE_JUMP_REDUCTION = 0.5  # One-time multiplier on release, unchanged
FALLING_GRAVITY_MULTIPLIER = 1.8  # Ratio on gravity, unchanged

# Forgiving Mechanics
COYOTE_TIME = 12
JUMP_BUFFER = 8

# Wall Slide/Jump
WALL_SLIDE_FRICTION = 0.2  # Multiplier on gravity, unchanged (gravity already halved)
WALL_JUMP_X_IMPULSE = 1.5
WALL_JUMP_Y_FORCE = -1.75

# Slime Follow Constants
SLIME_FOLLOW_DELAY = 16
SLIME_MAX_DIST = 100
SLIME_REFORM_DIST = 8
SLIME_LERP_FACTOR = 0.4  # Imported but unused

# Slime Juice Resource
JUICE_MAX = 200.0
JUICE_REGEN_RATE = 0.5  # ~6.7s full recharge at 60fps
JUICE_MIN_SCALE = 0.25 # 2x2 vs 8x8 (0.25 * 8 = 2)
SLIME_SPIT_COST = 10.0

# Projectile
PROJECTILE_SPEED = 2.0  # Moderate spit speed — gives homing time to steer
SPIT_AIM_RANGE = 80     # Max auto-aim distance in pixels (~10 tiles)
BOSS_ROCK_SPEED = 1.0

# Drill Dive
DRILL_SPEED = 2.0
DRILL_DRIFT_SPEED = 0.5
DRILL_IMPACT_COST = 20.0
DRILL_ACTIVATION_COST = 5.0
DRILL_BLOCK_REFUND = 15.0

# Juice Effects
DRILL_SHAKE_DURATION = 12
DRILL_HITSTOP_FRAMES = 6

# Player Health & Damage
PLAYER_MAX_HP = 3
INVULN_DURATION = 120
KNOCKBACK_FORCE_X = 1.0
KNOCKBACK_FORCE_Y = -1.25

# Basic Dash (D-15)
DASH_SPEED = 2.0        # Pixels/frame (~2 tiles in 16 frames)
DASH_DURATION = 16      # Frames of dash movement
DASH_IFRAMES = 16       # Frames of invulnerability during dash
DASH_COOLDOWN = 40      # Frames before dash can be used again

# Fusion System (D-01, D-02, D-04, D-05)
RECALL_SPEED = 4.0              # Slime zip speed toward player in pixels/frame (~8-12 frames to arrive) (D-25)
RECALL_OVERLAP_DIST = 4         # Pixel distance for slime to be "overlapping" player for fusion (D-26)
MANA_SHIELD_COST = 20.0         # Juice consumed per hit while fused (D-04)
SLIME_DISSIPATE_COOLDOWN = 240  # Frames (~4 sec) before slime reforms after juice-empty dissipation (D-05)

# Slime Recall Visual
RECALL_TRAIL_COLOR = 11         # Pyxel palette color for rubber-band trail (D-25)

# Spit vs Recall threshold
SPIT_HOLD_THRESHOLD = 16        # Frames: <= this on Z release = spit, > this = was charging/recalling (D-06)

# Directional Slime Hold (ABL-03, D-19)
HOLD_TAP_THRESHOLD = 10         # Frames: <= this on release = tap (reposition slime), > this = walk

# Slime Ram (ABL-01, D-12 through D-14)
RAM_SPEED = 2.5                 # High speed horizontal movement pixels/frame (D-12)
RAM_DIAGONAL_FACTOR = 0.7       # Y-component multiplier for diagonal ram (ratio, unchanged)
RAM_BLOCK_COST = 15.0           # Juice cost per CRACKED_H block broken (D-13)
RAM_INVINCIBLE = True           # Player is invincible during ram (D-12)

# Charge Shot (ABL-04, D-16 through D-18)
CHARGE_SHOT_SPEED = 3.0         # Projectile speed (faster than normal spit)
CHARGE_SHOT_SIZE = 8            # Larger projectile hitbox (vs 4 for normal spit)
CHARGE_SHOT_DAMAGE = 3          # High damage (D-16)

# Slime Boost (ABL-06, D-07 through D-11)
BOOST_FORCE = -1.75          # Upward impulse per tap (similar to JUMP_FORCE)
BOOST_JUICE_COST = 25.0      # Juice per tap (~8 boosts from full 200)
BOOST_RECOMMIT_WINDOW = 24   # Frames between taps to chain (~0.4s at 60fps)
BOOST_DOWNWARD_DAMAGE_W = 12 # Hitbox width for enemy stomp damage
BOOST_DOWNWARD_DAMAGE_H = 8  # Hitbox height below player for enemy damage

# Charge Shot Recoil (D-17): physics-based bomb-climb exploit
CHARGE_RECOIL_FORCE = -1.25  # Upward impulse applied on charge shot fire

# Charge Shot Windup (gap fix: visual absorption before fire)
CHARGE_WINDUP_DURATION = 40  # Frames of windup (~0.67s at 60fps) before charge shot fires

# CRACKED_V Gate Breaking (ABL-02, D-01, D-02)
DRILL_CRACKED_V_COST = 20.0   # Juice cost per CRACKED_V broken via Drill Dive
BOOST_CRACKED_V_COST = 25.0   # Juice cost per CRACKED_V broken via Boost

# Save System (Phase 11, SYS-01)
MAX_HP_CAP = 5           # Maximum heart containers (D-14: start 3, max 5)
MAX_JUICE_CAP = 300.0    # Maximum juice capacity (D-14: start 200, max 300)
SAVE_FILE = "save.json"  # Single save slot filename (D-02)

# Death Animation (D-16)
DEATH_FREEZE_FRAMES = 60   # 1s freeze before fade
DEATH_FADE_FRAMES = 60     # 1s fade to black

# Save Point Visual (D-05)
SAVE_PULSE_CYCLE = 120     # Total frames per pulse cycle
SAVE_PULSE_HALF = 60       # Frames per color phase (yellow/orange)
SAVE_PROMPT_DURATION = 120 # Frames to show "SAVED!" after saving
