"""The main window: navigation bar on top, one screen below.

Only one screen exists at a time. Opening a new screen destroys the
previous one, which also stops its auto refresh.

The library and records screens (Person 4) are imported inside their
open_* methods instead of at the top of the file. This lets the app
start while the team is still merging: a screen whose code is not in
main yet shows "This screen is not ready yet" instead of crashing.
"""
import importlib
import logging
from typing import Callable

import customtkinter as ctk

from app import config
from app.frontend import theme
from app.frontend.crew_screens import CrewDetailScreen, CrewListScreen
from app.frontend.widgets import MessageView, NavBar

logger = logging.getLogger(__name__)

# Module with list_crew() and get_crew_detail() (Person 1).
CREW_SERVICE_MODULE = "app.backend.crew_service"

# Default value of MainWindow(crew_source=...): load the crew service.
LOAD_CREW_SERVICE = object()


def load_crew_service():
    """Import the backend crew service, or None if it is not available."""
    try:
        module = importlib.import_module(CREW_SERVICE_MODULE)
    except ImportError as error:
        logger.warning("Crew service not available: %s", error)
        return None
    if not (hasattr(module, "list_crew")
            and hasattr(module, "get_crew_detail")):
        logger.warning("%s has no list_crew()/get_crew_detail()",
                       CREW_SERVICE_MODULE)
        return None
    return module


class MainWindow(ctk.CTk):
    """The application window.

    crew_source: any object with list_crew() and get_crew_detail(id)
    (by default the crew service; tests pass fake data, None shows
    "Crew data is not connected yet").
    """

    def __init__(self, crew_source=LOAD_CREW_SERVICE):
        ctk.set_appearance_mode("dark")
        super().__init__(fg_color=theme.BACKGROUND)
        if crew_source is LOAD_CREW_SERVICE:
            crew_source = load_crew_service()
        self.crew_source = crew_source
        self.title(config.APP_NAME)
        self.geometry(theme.WINDOW_SIZE)
        self.minsize(theme.WINDOW_MIN_WIDTH, theme.WINDOW_MIN_HEIGHT)

        self.nav_bar = NavBar(self, on_navigate=self.navigate)
        self.nav_bar.pack(fill="x")

        self.container = ctk.CTkFrame(self, fg_color="transparent",
                                      corner_radius=0)
        self.container.pack(fill="both", expand=True,
                            padx=theme.PAGE_MARGIN_X,
                            pady=theme.PAGE_MARGIN_Y)

        self.current_screen: ctk.CTkFrame | None = None
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
            self.open_library(key)

    def open_crew_list(self) -> None:
        self._show("crew", lambda: CrewListScreen(self, self.crew_source))

    def open_crew_detail(self, astronaut_id: int) -> None:
        self._show("crew", lambda: CrewDetailScreen(
            self, self.crew_source, astronaut_id))

    def open_library(self, category) -> None:
        """category: 'diseases', 'hazards' or 'treatments'."""
        def build():
            from app.frontend.library_screens import LibraryListScreen
            return LibraryListScreen(self, category)
        self._show(_category_key(category), build)

    def open_library_detail(self, category, item_id: int) -> None:
        def build():
            from app.frontend.library_screens import LibraryDetailScreen
            return LibraryDetailScreen(self, category, item_id)
        self._show(_category_key(category), build)

    def open_records(self) -> None:
        def build():
            from app.frontend.records_screens import RecordsListScreen
            return RecordsListScreen(self)
        self._show("records", build)

    def open_astronaut_records(self, astronaut_id: int) -> None:
        def build():
            from app.frontend.records_screens import AstronautRecordsScreen
            return AstronautRecordsScreen(self, astronaut_id)
        self._show("records", build)

    # -----------------------------------------------------------------
    def _show(self, nav_key: str,
              build_screen: Callable[[], ctk.CTkFrame]) -> None:
        """Destroy the current screen and build a new one."""
        self._clear()
        self.nav_bar.set_active(nav_key)
        try:
            screen = build_screen()
        except ImportError as error:
            logger.info("Screen not available: %s", error)
            self._clear()
            screen = MessageView(
                self.container, "This screen is not ready yet",
                f"Its code has not been merged into main ({error}).")
        except Exception as error:  # database or file problems
            logger.exception("Could not build the screen")
            self._clear()
            screen = MessageView(self.container,
                                 "The data could not be loaded", str(error))
        if isinstance(screen, MessageView):
            # A message sits at the top instead of filling the page.
            screen.pack(fill="x", anchor="n")
        else:
            screen.pack(fill="both", expand=True)
        self.current_screen = screen

    def _clear(self) -> None:
        """Destroy everything in the content area (also half-built
        screens that failed while loading)."""
        for child in self.container.winfo_children():
            child.destroy()
        self.current_screen = None


def _category_key(category) -> str:
    """Accept 'diseases' or an Enum whose value is 'diseases'."""
    return getattr(category, "value", category)
