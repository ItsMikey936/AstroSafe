"""Reusable pieces shared by every screen.

Screens are built from these blocks, so they all look the same:
navigation bar, screen base class, clickable cards, stat tiles, dose
rings, profile panel and image loading (with drawn placeholders when
a picture file is missing).
"""
import logging
import tkinter
from pathlib import Path
from typing import Callable

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageOps

from app import config
from app.frontend import theme

logger = logging.getLogger(__name__)

# (key, text) of each navigation button, left to right.
NAV_ITEMS = [
    ("crew", "Crew"),
    ("diseases", "Diseases"),
    ("hazards", "Hazards"),
    ("treatments", "Treatments"),
    ("records", "Records"),
]

# Placeholders are drawn bigger than shown so they stay sharp.
_DRAW_SCALE = 2


# ---------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------
def make_label(master, text: str = "", size: int = 16,
               color: str = theme.TEXT, bold: bool = False,
               wrap: int = 0, anchor: str = "center", **kwargs
               ) -> ctk.CTkLabel:
    """CTkLabel with font size, color and alignment in one call.

    wrap: width in pixels where the text breaks into lines (0 = never).
    anchor: 'center', 'w' (left) or 'e' (right).
    """
    justify = {"w": "left", "e": "right"}.get(anchor, "center")
    return ctk.CTkLabel(master, text=text, font=theme.font(size, bold),
                        text_color=color, fg_color="transparent",
                        wraplength=wrap, anchor=anchor, justify=justify,
                        **kwargs)


def back_button(master, text: str, command: Callable[[], None]
                ) -> ctk.CTkButton:
    """Small 'Back to ...' link shown on detail screens."""
    return ctk.CTkButton(
        master, text=f"‹  {text}", command=command, font=theme.font(15),
        fg_color="transparent", hover_color=theme.SURFACE,
        text_color=theme.TEXT_MUTED, anchor="w", width=0, cursor="hand2")


def label_text(label: ctk.CTkLabel) -> str:
    """Text currently shown by a label."""
    return label.cget("text")


# ---------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------
def load_image(*candidates: Path | str | None, size: int,
               circle: bool = False, fallback: str = "generic"
               ) -> ctk.CTkImage:
    """Load the first candidate file that exists, as a size x size image.

    If none exists, a placeholder is drawn instead, so a missing
    picture never crashes the app. fallback: 'avatar', 'record',
    'circle' or 'generic'.
    """
    pixels = size * _DRAW_SCALE
    picture = None
    for path in candidates:
        if path is None or not Path(path).is_file():
            continue
        try:
            with Image.open(path) as opened:
                picture = ImageOps.fit(opened.convert("RGBA"),
                                       (pixels, pixels))
            break
        except OSError as error:
            logger.warning("Could not open image %s: %s", path, error)
    if picture is None:
        picture = draw_placeholder(fallback, pixels)
    if circle:
        picture = _circle_crop(picture)
    return ctk.CTkImage(light_image=picture, dark_image=picture,
                        size=(size, size))


def icon_image(name: str, size: int, fallback: str = "generic"
               ) -> ctk.CTkImage:
    """assets/icons/<name>.png, or a drawn placeholder."""
    return load_image(config.ICONS_DIR / f"{name}.png", size=size,
                      fallback=fallback)


def draw_placeholder(kind: str, pixels: int) -> Image.Image:
    """Draw a simple picture when the real one is missing."""
    picture = Image.new("RGBA", (pixels, pixels), (0, 0, 0, 0))
    draw = ImageDraw.Draw(picture)
    unit = pixels / 100

    def box(x, y, width, height):
        return [x * unit, y * unit, (x + width) * unit, (y + height) * unit]

    if kind == "avatar":
        draw.ellipse(box(30, 8, 40, 44), fill=theme.TEXT)
        # Shoulders: a big circle cut by the bottom edge of the picture.
        draw.ellipse(box(12, 58, 76, 76), fill=theme.TEXT)
    elif kind == "record":
        draw.rounded_rectangle(box(20, 10, 60, 85), radius=6 * unit,
                               fill=theme.RECORD_BOARD)
        draw.rectangle(box(26, 16, 48, 74), fill=theme.TEXT)
        draw.rectangle(box(38, 6, 24, 10), fill=theme.RECORD_CLIP)
        for top in (30, 50, 70):
            draw.rectangle(box(46, top + 3, 23, 3), fill=theme.RECORD_LINES)
            draw.rectangle(box(31, top, 10, 10), fill=theme.RECORD_LINES)
    elif kind == "circle":
        draw.ellipse(box(0, 0, 100, 100), fill=theme.PLACEHOLDER_CIRCLE)
    else:
        draw.rounded_rectangle(box(5, 5, 90, 90), radius=20 * unit,
                               fill=theme.PLACEHOLDER)
    return picture


def _circle_crop(picture: Image.Image) -> Image.Image:
    """Make everything outside the inner circle transparent."""
    mask = Image.new("L", picture.size, 0)
    ImageDraw.Draw(mask).ellipse([0, 0, picture.width - 1,
                                  picture.height - 1], fill=255)
    result = Image.new("RGBA", picture.size, (0, 0, 0, 0))
    result.paste(picture, (0, 0), mask)
    return result


def image_label(master, image: ctk.CTkImage) -> ctk.CTkLabel:
    """A label that only shows a picture."""
    return ctk.CTkLabel(master, text="", image=image, fg_color="transparent")


# ---------------------------------------------------------------------
# Navigation bar
# ---------------------------------------------------------------------
class NavBar(ctk.CTkFrame):
    """Top bar with one button per section of the app.

    on_navigate(key) is called with the key of the clicked button
    ('crew', 'diseases', 'hazards', 'treatments' or 'records').
    """

    def __init__(self, master, on_navigate: Callable[[str], None]):
        super().__init__(master, fg_color=theme.SURFACE, corner_radius=0)
        self._buttons: dict[str, ctk.CTkButton] = {}
        for index, (key, text) in enumerate(NAV_ITEMS):
            self.grid_columnconfigure(index, weight=1)
            button = ctk.CTkButton(
                self, text=text, font=theme.font(20),
                width=170, height=56, corner_radius=theme.SMALL_RADIUS,
                fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
                text_color=theme.TEXT, cursor="hand2",
                command=lambda selected=key: on_navigate(selected))
            button.grid(row=0, column=index, padx=24, pady=20)
            self._buttons[key] = button

    def set_active(self, key: str) -> None:
        """Highlight the button of the screen being shown."""
        for button_key, button in self._buttons.items():
            active = button_key == key
            button.configure(
                fg_color=theme.ACCENT_ACTIVE if active else theme.ACCENT)

    def button(self, key: str) -> ctk.CTkButton:
        return self._buttons[key]


# ---------------------------------------------------------------------
# Screen base class and messages
# ---------------------------------------------------------------------
class Screen(ctk.CTkFrame):
    """Base class of every screen.

    `app` is the main window. Screens use it to move to other screens,
    for example: self.app.open_crew_detail(astronaut_id). The screen is
    created inside the window's content area; the window places it.
    """

    def __init__(self, app):
        super().__init__(app.container, fg_color="transparent",
                         corner_radius=0)
        self.app = app
        self._refresh_callback: Callable[[], None] | None = None
        self._refresh_interval_ms = config.REFRESH_INTERVAL_MS
        self._after_id: str | None = None

    def start_auto_refresh(self, callback: Callable[[], None],
                           interval_ms: int = config.REFRESH_INTERVAL_MS
                           ) -> None:
        """Call `callback` every `interval_ms` while the screen is open."""
        self.stop_auto_refresh()
        self._refresh_callback = callback
        self._refresh_interval_ms = interval_ms
        self._after_id = self.after(interval_ms, self._run_refresh)

    def stop_auto_refresh(self) -> None:
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None

    def destroy(self) -> None:
        self.stop_auto_refresh()
        super().destroy()

    def _run_refresh(self) -> None:
        self._after_id = None
        if self._refresh_callback is None:
            return
        try:
            self._refresh_callback()
        except Exception:  # keep the window alive if one refresh fails
            logger.exception("Refresh failed")
        self._after_id = self.after(self._refresh_interval_ms,
                                    self._run_refresh)


class MessageView(ctk.CTkFrame):
    """A centered message for empty lists, errors and missing parts."""

    def __init__(self, master, title: str, message: str = ""):
        super().__init__(master, fg_color=theme.SURFACE,
                         corner_radius=theme.CORNER_RADIUS)
        self.title_label = make_label(self, title, 24, bold=True)
        self.title_label.pack(padx=40, pady=(40, 8 if message else 40))
        self.message_label = None
        if message:
            self.message_label = make_label(self, message, 16,
                                            theme.TEXT_MUTED, wrap=900)
            self.message_label.pack(padx=40, pady=(0, 40))

    @property
    def title(self) -> str:
        return label_text(self.title_label)


# ---------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------
class ClickableCard(ctk.CTkFrame):
    """A rounded card that reacts to the mouse as a whole.

    Build the content of the card first, then call
    bind_click_to_children() so a click anywhere on it (also on its
    labels and pictures) runs `command`.
    """

    def __init__(self, master, command: Callable[[], None] | None = None,
                 **kwargs):
        kwargs.setdefault("fg_color", theme.SURFACE)
        kwargs.setdefault("corner_radius", theme.CORNER_RADIUS)
        super().__init__(master, **kwargs)
        self.command = command
        self._hovered = False

    def click(self) -> None:
        """Run the card's command (same as clicking it)."""
        if self.command is not None:
            self.command()

    def bind_click_to_children(self) -> None:
        """Make the card and everything inside it clickable."""
        self._bind_tree(self)

    def _bind_tree(self, widget: tkinter.Misc) -> None:
        # tkinter.Misc methods are used on purpose: CustomTkinter
        # widgets override bind/configure and only accept their own
        # options, while the plain Tk parts accept a cursor.
        tkinter.Misc.bind(widget, "<Button-1>", self._on_click, "+")
        tkinter.Misc.bind(widget, "<Enter>", self._on_enter, "+")
        tkinter.Misc.bind(widget, "<Leave>", self._on_leave, "+")
        try:
            tkinter.Misc.configure(widget, cursor="hand2")
        except tkinter.TclError:
            pass
        for child in widget.winfo_children():
            self._bind_tree(child)

    def _on_click(self, _event=None) -> None:
        self.click()

    def _on_enter(self, _event=None) -> None:
        self._set_hovered(True)

    def _on_leave(self, _event=None) -> None:
        # Moving from the card onto one of its labels also sends
        # <Leave>, so only remove the highlight when the mouse is
        # really outside the card.
        if not self.winfo_exists():
            return
        x, y = self.winfo_pointerxy()
        left, top = self.winfo_rootx(), self.winfo_rooty()
        inside = (left <= x < left + self.winfo_width()
                  and top <= y < top + self.winfo_height())
        self._set_hovered(inside)

    def _set_hovered(self, hovered: bool) -> None:
        if hovered == self._hovered or not self.winfo_exists():
            return
        self._hovered = hovered
        self.configure(
            fg_color=theme.SURFACE_HOVER if hovered else theme.SURFACE)


class ListCard(ClickableCard):
    """Big row with an icon and a title (diseases, hazards, records)."""

    def __init__(self, master, title: str, image: ctk.CTkImage,
                 subtitle: str = "",
                 command: Callable[[], None] | None = None):
        super().__init__(master, command=command, height=150)
        self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        image_label(self, image).grid(row=0, column=0, padx=(80, 60),
                                      pady=12)
        text_box = ctk.CTkFrame(self, fg_color="transparent")
        text_box.grid(row=0, column=1, sticky="w", padx=(0, 24))
        self.title_label = make_label(text_box, title, 36, anchor="w")
        self.title_label.pack(anchor="w")
        if subtitle:
            make_label(text_box, subtitle, 16, theme.TEXT_MUTED,
                       anchor="w").pack(anchor="w")
        self.bind_click_to_children()


# ---------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------
class StatTile(ctk.CTkFrame):
    """A title with a big colored value under it."""

    def __init__(self, master, title: str, color: str):
        super().__init__(master, fg_color="transparent")
        make_label(self, title, 20).pack(pady=(0, 6))
        self.value_label = make_label(self, "--", 38, color)
        self.value_label.pack()

    def set_value(self, text: str) -> None:
        self.value_label.configure(text=text)

    def value(self) -> str:
        return label_text(self.value_label)


class StatPanel(ctk.CTkFrame):
    """A card with several StatTiles side by side.

    tiles: list of (key, title). Update a value with
    panel.set_value(key, "37.2 °C").
    """

    def __init__(self, master, tiles: list[tuple[str, str]], color: str):
        super().__init__(master, fg_color=theme.SURFACE,
                         corner_radius=theme.CORNER_RADIUS)
        self.grid_rowconfigure(0, weight=1)
        self._tiles: dict[str, StatTile] = {}
        for column, (key, title) in enumerate(tiles):
            self.grid_columnconfigure(column, weight=1, uniform="tile")
            tile = StatTile(self, title, color)
            tile.grid(row=0, column=column, padx=12, pady=20)
            self._tiles[key] = tile

    def set_value(self, key: str, text: str) -> None:
        self._tiles[key].set_value(text)

    def value(self, key: str) -> str:
        return self._tiles[key].value()


class DoseRing(ctk.CTkCanvas):
    """A colored ring with a number inside (radiation doses).

    background: color of the panel the ring sits on.
    """

    PEN_WIDTH = 7

    def __init__(self, master, size: int = 110, color: str = theme.RING_OK,
                 background: str = theme.SURFACE):
        super().__init__(master, width=size, height=size,
                         background=background, highlightthickness=0,
                         borderwidth=0)
        self._size = size
        self._color = color
        self._text = "--"
        half = self.PEN_WIDTH / 2
        self.create_oval(half, half, size - half, size - half,
                         outline=color, width=self.PEN_WIDTH)
        self._text_id = self.create_text(size / 2, size / 2,
                                         text=self._text,
                                         fill=theme.TEXT,
                                         font=theme.font(20))

    def set_value(self, text: str) -> None:
        self._text = text
        self.itemconfigure(self._text_id, text=text)

    def text(self) -> str:
        return self._text


# ---------------------------------------------------------------------
# Profile panel
# ---------------------------------------------------------------------
class ProfilePanel(ctk.CTkFrame):
    """Left panel with avatar, position and name.

    Callers add more widgets inside panel.body and pack them
    (dose rings, voice records):
        make_label(panel.body, "Millisievert").pack()
    """

    WIDTH = 400

    def __init__(self, master, name: str, position: str):
        super().__init__(master, width=self.WIDTH, fg_color=theme.SURFACE,
                         corner_radius=theme.CORNER_RADIUS)
        self.pack_propagate(False)
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=24, pady=(36, 24))
        image_label(self.body, icon_image("avatar", 150, fallback="avatar")
                    ).pack(pady=(0, 12))
        self.position_label = make_label(self.body, position, 20)
        self.position_label.pack()
        self.name_label = make_label(self.body, name, 17,
                                     wrap=self.WIDTH - 60)
        self.name_label.pack(pady=(0, 12))
