"""Colors, fonts and sizes taken from the prototype screens.

Change a color here and it changes in every screen.
"""
import customtkinter as ctk

# Backgrounds
BACKGROUND = "#111a2c"      # window background (darkest navy)
SURFACE = "#1e2d45"         # cards, panels and the top bar
SURFACE_HOVER = "#26385a"   # card under the mouse
ACCENT = "#22566a"          # navigation buttons, record buttons
ACCENT_HOVER = "#2c6c84"
ACCENT_ACTIVE = "#3a8aa6"   # navigation button of the current screen

# Text
TEXT = "#ffffff"
TEXT_MUTED = "#9fb0c8"
LABEL_YELLOW = "#f5c518"    # "Millisievert", "mSv"

# Value colors used on the crew detail screen
VALUE_BLUE = "#38b6ff"      # body temperature, intracranial pressure
VALUE_TEAL = "#2dd4bf"      # muscle mass, bone mineral density
VALUE_PURPLE = "#a78bfa"    # stress, fatigue, sleep

# Badges on the crew cards
SPO2_BADGE = "#22566a"
BPM_BADGE = "#7e9c6b"

# Dose rings
RING_OK = "#22c55e"

# Shapes
CORNER_RADIUS = 16
SMALL_RADIUS = 12
PAGE_PADDING = 40


def font(size: int, weight: str = "normal") -> ctk.CTkFont:
    """Return a font. Only call this after the main window exists."""
    return ctk.CTkFont(size=size, weight=weight)
