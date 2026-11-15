"""Colors, sizes and fonts taken from the prototype screens.

Change a color here and it changes in every screen.
"""
import sys

# Backgrounds
BACKGROUND = "#111a2c"      # window background (darkest navy)
SURFACE = "#1e2d45"         # cards, panels and the top bar
SURFACE_HOVER = "#26385a"   # card under the mouse
ACCENT = "#22566a"          # navigation buttons, record buttons
ACCENT_HOVER = "#2c6c84"
ACCENT_ACTIVE = "#3a8aa6"   # navigation button of the current screen
DIVIDER = "#9fb0c8"

# Text
TEXT = "#ffffff"
TEXT_MUTED = "#9fb0c8"
LABEL_YELLOW = "#f5c518"    # "Millisievert", "mSv"

# Value colors of the crew detail screen
VALUE_BLUE = "#38b6ff"      # body temperature, intracranial pressure
VALUE_TEAL = "#2dd4bf"      # muscle mass, bone mineral density
VALUE_PURPLE = "#a78bfa"    # stress, fatigue, sleep

# Badges of the crew cards
SPO2_BADGE = "#22566a"
BPM_BADGE = "#7e9c6b"

# Dose rings
RING_OK = "#22c55e"

# Placeholder pictures (drawn when an image file is missing)
PLACEHOLDER = "#5a6982"
PLACEHOLDER_CIRCLE = "#b0b2b6"
RECORD_BOARD = "#6e87b9"
RECORD_CLIP = "#fde047"
RECORD_LINES = "#c8cdd7"

# Shapes (pixels)
CORNER_RADIUS = 16
SMALL_RADIUS = 12
PAGE_MARGIN_X = 40
PAGE_MARGIN_Y = 24

# Window
WINDOW_SIZE = "1280x860"
WINDOW_MIN_WIDTH = 1100
WINDOW_MIN_HEIGHT = 720

# Fonts
FONT_FAMILY = "Segoe UI" if sys.platform == "win32" else "DejaVu Sans"


def font(size: int, bold: bool = False) -> tuple[str, int, str]:
    """Font tuple for CustomTkinter widgets: font(20, bold=True)."""
    return (FONT_FAMILY, size, "bold" if bold else "normal")
