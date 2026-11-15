"""Reusable pieces shared by every screen.

Screens are built from these blocks, so all screens look the same:
navigation bar, clickable cards, stat tiles, dose rings, profile
panel and image loading (with drawn placeholders when an image file
is missing).
"""
import sqlite3
from pathlib import Path
from tkinter import messagebox
from typing import Callable

import customtkinter as ctk
from PIL import Image, ImageDraw

from app import config
from app.frontend import theme

# (key, text) of each navigation button, left to right.
NAV_ITEMS = [
    ("crew", "Crew"),
    ("diseases", "Diseases"),
    ("hazards", "Hazards"),
    ("treatments", "Treatments"),
    ("records", "Records"),
]


# ---------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------
def load_image(*candidates: Path | None, size: int, circle: bool = False,
               fallback: str = "generic") -> ctk.CTkImage:
    """Load the first candidate file that exists.

    If none exists, a placeholder is drawn instead, so a missing
    picture never crashes the app.
    """
    pixels = size * 2  # draw at double size so it stays sharp
    picture = None
    for path in candidates:
        if path is not None and Path(path).is_file():
            try:
                picture = Image.open(path).convert("RGBA")
                break
            except OSError:
                picture = None
    if picture is None:
        picture = draw_placeholder(fallback, pixels)
    picture = _square(picture, pixels)
    if circle:
        picture = _circle_crop(picture)
    return ctk.CTkImage(light_image=picture, dark_image=picture,
                        size=(size, size))


def icon(name: str, size: int, fallback: str = "generic") -> ctk.CTkImage:
    """Load assets/icons/<name>.png (or a placeholder)."""
    return load_image(config.ICONS_DIR / f"{name}.png", size=size,
                      fallback=fallback)


def draw_placeholder(kind: str, pixels: int) -> Image.Image:
    """Draw a simple picture: 'avatar', 'record', 'circle' or other."""
    scale = 4  # draw bigger, then shrink: smooth edges
    big = pixels * scale
    image = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    unit = big / 100

    def box(x1, y1, x2, y2):
        return [x1 * unit, y1 * unit, x2 * unit, y2 * unit]

    if kind == "avatar":
        white = (255, 255, 255, 255)
        draw.ellipse(box(30, 8, 70, 52), fill=white)
        draw.pieslice(box(12, 58, 88, 134), 180, 360, fill=white)
    elif kind == "record":
        draw.rounded_rectangle(box(20, 10, 80, 95), 6 * unit,
                               fill=(110, 135, 185, 255))
        draw.rectangle(box(26, 16, 74, 90), fill=(255, 255, 255, 255))
        draw.rectangle(box(38, 6, 62, 16), fill=(253, 224, 71, 255))
        for top in (28, 48, 68):
            draw.rectangle(box(31, top, 41, top + 10),
                           outline=(150, 160, 175, 255),
                           width=int(unit * 1.5))
            draw.line(box(33, top + 5, 36, top + 8)
                      + box(36, top + 8, 40, top + 2)[2:],
                      fill=(34, 197, 94, 255), width=int(unit * 2))
            draw.rectangle(box(46, top + 3, 69, top + 6),
                           fill=(200, 205, 215, 255))
    elif kind == "circle":
        draw.ellipse(box(0, 0, 100, 100), fill=(176, 178, 182, 255))
    else:
        draw.rounded_rectangle(box(5, 5, 95, 95), 20 * unit,
                               fill=(90, 105, 130, 255))
    return image.resize((pixels, pixels), Image.LANCZOS)


def _square(picture: Image.Image, pixels: int) -> Image.Image:
    """Crop the center square and resize it."""
    width, height = picture.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    picture = picture.crop((left, top, left + side, top + side))
    return picture.resize((pixels, pixels), Image.LANCZOS)


def _circle_crop(picture: Image.Image) -> Image.Image:
    """Make everything outside the inner circle transparent."""
    scale = 4
    width, height = picture.size
    mask = Image.new("L", (width * scale, height * scale), 0)
    ImageDraw.Draw(mask).ellipse(
        (0, 0, width * scale - 1, height * scale - 1), fill=255)
    mask = mask.resize((width, height), Image.LANCZOS)
    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    result.paste(picture, (0, 0), mask)
    return result


# ---------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------
def show_error(title: str, message: str) -> None:
    """Pop-up window with an error message."""
    messagebox.showerror(title, message)


class MessageView(ctk.CTkFrame):
    """A centered message for empty lists and errors."""

    def __init__(self, master, title: str, message: str = ""):
        super().__init__(master, fg_color=theme.SURFACE,
                         corner_radius=theme.CORNER_RADIUS)
        ctk.CTkLabel(self, text=title, font=theme.font(24, "bold"),
                     text_color=theme.TEXT).pack(padx=40, pady=(40, 8))
        if message:
            ctk.CTkLabel(self, text=message, font=theme.font(16),
                         text_color=theme.TEXT_MUTED, wraplength=700,
                         justify="center").pack(padx=40, pady=(0, 40))


# ---------------------------------------------------------------------
# Navigation bar
# ---------------------------------------------------------------------
class NavBar(ctk.CTkFrame):
    """Top bar with one button per section of the app."""

    def __init__(self, master, on_navigate: Callable[[str], None]):
        super().__init__(master, fg_color=theme.SURFACE, corner_radius=0)
        self._buttons: dict[str, ctk.CTkButton] = {}
        for column, (key, text) in enumerate(NAV_ITEMS):
            self.grid_columnconfigure(column, weight=1)
            button = ctk.CTkButton(
                self,
                text=text,
                width=170,
                height=56,
                corner_radius=theme.SMALL_RADIUS,
                font=theme.font(20),
                fg_color=theme.ACCENT,
                hover_color=theme.ACCENT_HOVER,
                text_color=theme.TEXT,
                command=lambda selected=key: on_navigate(selected),
            )
            button.grid(row=0, column=column, padx=12, pady=20)
            self._buttons[key] = button

    def set_active(self, key: str) -> None:
        """Highlight the button of the screen being shown."""
        for button_key, button in self._buttons.items():
            active = button_key == key
            button.configure(
                fg_color=theme.ACCENT_ACTIVE if active else theme.ACCENT)


# ---------------------------------------------------------------------
# Screen base class
# ---------------------------------------------------------------------
class Screen(ctk.CTkFrame):
    """Base class of every screen.

    `app` is the main window. Screens use it to move to other screens,
    for example: self.app.open_crew_detail(astronaut_id).
    """

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._refresh_job = None
        self._refresh_callback = None
        self._refresh_interval = config.REFRESH_INTERVAL_MS

    def start_auto_refresh(self, callback: Callable[[], None],
                           interval_ms: int = config.REFRESH_INTERVAL_MS
                           ) -> None:
        """Call `callback` every `interval_ms` while the screen is open."""
        self._refresh_callback = callback
        self._refresh_interval = interval_ms
        self._schedule_refresh()

    def _schedule_refresh(self) -> None:
        self._refresh_job = self.after(self._refresh_interval,
                                       self._run_refresh)

    def _run_refresh(self) -> None:
        self._refresh_job = None
        try:
            self._refresh_callback()
        except sqlite3.Error as error:
            print("Refresh failed:", error)
        self._schedule_refresh()

    def destroy(self) -> None:
        """Stop the auto refresh before the screen disappears."""
        if self._refresh_job is not None:
            self.after_cancel(self._refresh_job)
            self._refresh_job = None
        super().destroy()


# ---------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------
class ClickableCard(ctk.CTkFrame):
    """A rounded card that reacts to the mouse as a whole.

    Subclasses create their labels first and then call
    self.make_clickable() at the end of __init__.
    """

    def __init__(self, master, command: Callable[[], None], **kwargs):
        kwargs.setdefault("fg_color", theme.SURFACE)
        kwargs.setdefault("corner_radius", theme.CORNER_RADIUS)
        super().__init__(master, cursor="hand2", **kwargs)
        self._command = command

    def make_clickable(self) -> None:
        for widget in self._widgets_inside(self):
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _widgets_inside(self, widget):
        yield widget
        for child in widget.winfo_children():
            if isinstance(child, ctk.CTkBaseClass):
                yield from self._widgets_inside(child)

    def _on_click(self, _event=None) -> None:
        self._command()

    def _on_enter(self, _event=None) -> None:
        self.configure(fg_color=theme.SURFACE_HOVER)

    def _on_leave(self, _event=None) -> None:
        self.configure(fg_color=theme.SURFACE)


class ListCard(ClickableCard):
    """Big row with an icon and a title (diseases, hazards, records)."""

    def __init__(self, master, title: str, image: ctk.CTkImage,
                 command: Callable[[], None], subtitle: str = ""):
        super().__init__(master, command=command, height=150)
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        ctk.CTkLabel(self, text="", image=image).grid(
            row=0, column=0, rowspan=2, padx=(80, 60), pady=12)
        ctk.CTkLabel(self, text=title, font=theme.font(36),
                     text_color=theme.TEXT, anchor="w").grid(
            row=0, column=1, sticky="sw" if subtitle else "w",
            rowspan=1 if subtitle else 2, padx=(0, 24))
        if subtitle:
            ctk.CTkLabel(self, text=subtitle, font=theme.font(16),
                         text_color=theme.TEXT_MUTED, anchor="w").grid(
                row=1, column=1, sticky="nw", padx=(0, 24), pady=(4, 0))
        self.make_clickable()


# ---------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------
class StatTile(ctk.CTkFrame):
    """A title with a big colored value under it."""

    def __init__(self, master, title: str, color: str):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text=title, font=theme.font(20),
                     text_color=theme.TEXT).pack()
        self._value = ctk.CTkLabel(self, text="--", font=theme.font(38),
                                   text_color=color)
        self._value.pack(pady=(6, 0))

    def set_value(self, text: str) -> None:
        self._value.configure(text=text)


class StatPanel(ctk.CTkFrame):
    """A card with several StatTiles side by side.

    tiles: list of (key, title) pairs. Afterwards update a value with
    panel.set_value(key, "37.2 °C").
    """

    def __init__(self, master, tiles: list[tuple[str, str]], color: str):
        super().__init__(master, fg_color=theme.SURFACE,
                         corner_radius=theme.CORNER_RADIUS)
        self._tiles: dict[str, StatTile] = {}
        self.grid_rowconfigure(0, weight=1)
        for column, (key, title) in enumerate(tiles):
            self.grid_columnconfigure(column, weight=1, uniform="tile")
            tile = StatTile(self, title, color)
            tile.grid(row=0, column=column, padx=12, pady=20)
            self._tiles[key] = tile

    def set_value(self, key: str, text: str) -> None:
        self._tiles[key].set_value(text)


class DoseRing(ctk.CTkFrame):
    """A green ring with a number inside (radiation doses)."""

    def __init__(self, master, size: int = 110, color: str = theme.RING_OK):
        super().__init__(master, width=size, height=size,
                         corner_radius=size // 2, border_width=7,
                         border_color=color, fg_color=theme.SURFACE)
        self.pack_propagate(False)
        self._label = ctk.CTkLabel(self, text="--", font=theme.font(20),
                                   text_color=theme.TEXT)
        self._label.place(relx=0.5, rely=0.5, anchor="center")

    def set_value(self, text: str) -> None:
        self._label.configure(text=text)


# ---------------------------------------------------------------------
# Profile panel and buttons
# ---------------------------------------------------------------------
class ProfilePanel(ctk.CTkFrame):
    """Left panel with avatar, position and name.

    Callers pack more widgets into it (dose rings, voice records).
    """

    def __init__(self, master, name: str, position: str):
        super().__init__(master, fg_color=theme.SURFACE,
                         corner_radius=theme.CORNER_RADIUS)
        ctk.CTkLabel(self, text="",
                     image=icon("avatar", 150, fallback="avatar")).pack(
            pady=(36, 16))
        ctk.CTkLabel(self, text=position, font=theme.font(20),
                     text_color=theme.TEXT).pack()
        ctk.CTkLabel(self, text=name, font=theme.font(17),
                     text_color=theme.TEXT, wraplength=340).pack(
            pady=(4, 12), padx=16)


def back_button(master, text: str,
                command: Callable[[], None]) -> ctk.CTkButton:
    """Small 'Back to ...' button shown on detail screens."""
    return ctk.CTkButton(
        master,
        text=f"‹  {text}",
        width=10,
        height=34,
        font=theme.font(15),
        fg_color="transparent",
        hover_color=theme.SURFACE,
        text_color=theme.TEXT_MUTED,
        anchor="w",
        command=command,
    )
