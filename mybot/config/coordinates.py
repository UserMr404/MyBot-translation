"""Screen coordinate constants translated from ScreenCoordinates.au3.

Each coordinate is a tuple:
  (x, y)                    - click position
  (x, y, color, tolerance)  - pixel check with color
  (x1, y1, x2, y2)          - rectangular region
"""

from mybot.constants import BOTTOM_OFFSET_Y, MID_OFFSET_Y

# ── Click Away Regions ───────────────────────────────────────────────────────

CLICK_AWAY_REGION_LEFT = (235, 10, 245, 30)
CLICK_AWAY_REGION_RIGHT = (640, 10, 650, 30)
CLICK_AWAY_REGION_LEFT2 = (75, 88, 145, 98)
CLICK_AWAY_REGION_RIGHT2 = (760, 176, 835, 185)

# ── Main Screen Detection ────────────────────────────────────────────────────

IS_MAIN = (378, 10, 0x7ABDE3, 15)  # Builder Info Icon
NO_SHIELD = (524, 18, 0x494C4D, 15)
HAVE_SHIELD = (523, 19, 0xEBF7FB, 15)
HAVE_PERSONAL_GUARD = (523, 19, 0x7E4CDB, 15)

# ── Attack Screen ────────────────────────────────────────────────────────────

ATTACK_BUTTON = (60, 614 + BOTTOM_OFFSET_Y)
FIND_MATCH_BUTTON = (470, 20 + BOTTOM_OFFSET_Y, 0xD8A420, 10)
IS_ATTACK_SHIELD = (250, 415 + MID_OFFSET_Y, 0xE8E8E0, 10)

# ── Army Overview ────────────────────────────────────────────────────────────

ARMY_CAMP_SIZE = (393, 212 + MID_OFFSET_Y)
SIEGE_MACHINE_SIZE = (707, 168 + MID_OFFSET_Y)
ARMY_SPELL_SIZE = (399, 321 + MID_OFFSET_Y)
ARMY_CC_SPELL_SIZE = (475, 436 + MID_OFFSET_Y)

# ── Battle Screen ────────────────────────────────────────────────────────────

SURRENDER_BUTTON = (70, 545 + BOTTOM_OFFSET_Y, 0xCE0D0E, 40)
END_FIGHT_SCENE_BTN = (429, 529 + MID_OFFSET_Y, 0xE1F989, 20)
RETURN_HOME_BUTTON = (430, 566 + MID_OFFSET_Y, 0x6CBB1F, 15)
REWARD_BUTTON = (430, 573 + MID_OFFSET_Y, 0x6BBF23, 15)

# ── Hero Health Bars ─────────────────────────────────────────────────────────
# Format: (x, y, color, tolerance, offset)
# x=-1 means dynamically determined from attack bar position

KING_HEALTH = (-1, 569 + BOTTOM_OFFSET_Y, 0x00D500, 15, 10)
QUEEN_HEALTH = (-1, 569 + BOTTOM_OFFSET_Y, 0x00D500, 15, 5)
PRINCE_HEALTH = (-1, 568 + BOTTOM_OFFSET_Y, 0x00D500, 15, 8)
WARDEN_HEALTH = (-1, 567 + BOTTOM_OFFSET_Y, 0x00D500, 15, 10)
CHAMPION_HEALTH = (-1, 566 + BOTTOM_OFFSET_Y, 0x00D500, 15, 2)

# ── Window Detection ─────────────────────────────────────────────────────────

IS_GEM_WINDOW = (608, 240 + MID_OFFSET_Y, 0xEB1617, 20)
IS_TRAIN_PAGE = (785, 146 + MID_OFFSET_Y, 0xFF8D95, 15)
TREASURY_WINDOW = (695, 138 + MID_OFFSET_Y, 0xFF8D95, 20)

# ── Builder Base ─────────────────────────────────────────────────────────────

IS_ON_BUILDER_BASE = (838, 16, 0xFFFF47, 10)
BB_GOLD_END = (632, 406 + MID_OFFSET_Y, 0xFFE649, 20)

# ── Account Switching ────────────────────────────────────────────────────────

LOGIN_WITH_SUPERCELL_ID = (280, 640 + MID_OFFSET_Y, 0xDCF684, 20)
BUTTON_SETTING = (824, 555 + MID_OFFSET_Y, 0xFFFFFF, 10)

# ── Personal Challenges ──────────────────────────────────────────────────────

PERSONAL_CHALLENGE_OPEN = (149, 631 + BOTTOM_OFFSET_Y, 0xB7D0E4, 20)
PERSONAL_CHALLENGE_CLOSE = (827, 100 + MID_OFFSET_Y, 0xEE1F23, 20)
