"""The main window: navigation bar on top, one screen below.

Only one screen exists at a time. Opening a new screen destroys the
previous one, which also stops its auto refresh.

The screen modules are imported inside the open_* methods instead of
at the top of the file. This lets the app start while the team is
still merging: a screen whose file is not in main yet shows a
"not ready" message instead of crashing the whole app.
"""
import sqlite3
from typing import Callable

import customtkinter as ctk

from app import config
from app.backend.database import DatabaseNotFoundError
from app.backend.library_service import Category
from app.frontend import theme
from app.frontend.widgets import MessageView, NavBar


class MainWindow(ctk.CTk):
    """The application window."""

    def __init__(self):
        super().__init__()
        self.title(config.APP_NAME)
        self.geometry("1280x860")
        self.minsize(1100, 720)
        self.configure(fg_color=theme.BACKGROUND)

        self.nav_bar = NavBar(self, on_navigate=self.navigate)
        self.nav_bar.pack(fill="x")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True,
                            padx=theme.PAGE_PADDING, pady=24)

        self.open_crew_list()

    # -----------------------------------------------------------------
    # Navigation (screens call these methods through self.app)
    # -----------------------------------------------------------------
    def navigate(self, key: str) -> None:
        """Called by the navigation bar buttons."""
        if key == "crew":
            self.open_crew_list()
        elif key == "records":
            self.open_records()
        else:
            self.open_library(Category(key))

    def open_crew_list(self) -> None:
        def build(parent):
            from app.frontend.crew_screens import CrewListScreen
            return CrewListScreen(parent, self)
        self._show("crew", build)

    def open_crew_detail(self, astronaut_id: int) -> None:
        def build(parent):
            from app.frontend.crew_screens import CrewDetailScreen
            return CrewDetailScreen(parent, self, astronaut_id)
        self._show("crew", build)

    def open_library(self, category: Category) -> None:
        def build(parent):
            from app.frontend.library_screens import LibraryListScreen
            return LibraryListScreen(parent, self, category)
        self._show(category.value, build)

    def open_library_detail(self, category: Category, item_id: int) -> None:
        def build(parent):
            from app.frontend.library_screens import LibraryDetailScreen
            return LibraryDetailScreen(parent, self, category, item_id)
        self._show(category.value, build)

    def open_records(self) -> None:
        def build(parent):
            from app.frontend.records_screens import RecordsListScreen
            return RecordsListScreen(parent, self)
        self._show("records", build)

    def open_astronaut_records(self, astronaut_id: int) -> None:
        def build(parent):
            from app.frontend.records_screens import AstronautRecordsScreen
            return AstronautRecordsScreen(parent, self, astronaut_id)
        self._show("records", build)

    # -----------------------------------------------------------------
    def _show(self, nav_key: str,
              build_screen: Callable[[ctk.CTkFrame], ctk.CTkFrame]) -> None:
        """Destroy the current screen and build a new one."""
        self._clear()
        self.nav_bar.set_active(nav_key)
        try:
            screen = build_screen(self.container)
        except DatabaseNotFoundError as error:
            screen = self._error_view("Database not found", str(error))
        except sqlite3.Error as error:
            screen = self._error_view(
                "Database error", f"The data could not be read: {error}")
        except ImportError as error:
            screen = self._error_view(
                "This screen is not ready yet",
                f"Its code has not been merged into main: {error}")
        screen.pack(fill="both", expand=True)

    def _error_view(self, title: str, message: str) -> MessageView:
        self._clear()  # remove the half-built screen
        return MessageView(self.container, title, message)

    def _clear(self) -> None:
        """Destroy everything inside the screen container."""
        for child in self.container.winfo_children():
            child.destroy()
