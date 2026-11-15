"""Tests of the main window and the crew screens.

They open real CustomTkinter windows, so they need a screen (on Linux
without one, run them with xvfb-run). Run from the project folder:

    python -m unittest discover -s tests -t .
"""
import unittest

from app import config
from app.frontend.crew_screens import (
    NOT_CONNECTED_TITLE,
    CrewDetailScreen,
    CrewListScreen,
)
from app.frontend.main_window import MainWindow, load_crew_service
from app.frontend.widgets import MessageView
from tests.frontend.fake_crew import FakeCrewSource


def find_messages(widget) -> list[str]:
    """Titles of every MessageView inside a widget (or the widget)."""
    titles = []
    if isinstance(widget, MessageView):
        titles.append(widget.title)
    for child in widget.winfo_children():
        titles.extend(find_messages(child))
    return titles


# One window for every test: creating many Tk windows in a row is slow
# and sometimes fails on Windows. Each test only swaps the crew data.
_window: MainWindow | None = None


def setUpModule():
    global _window
    _window = MainWindow(crew_source=FakeCrewSource())
    _window.update()


def tearDownModule():
    _window.update()
    _window.destroy()


class WindowTestCase(unittest.TestCase):
    """Shows the crew list of the shared window with new crew data."""

    def make_window(self, crew_source) -> MainWindow:
        _window.crew_source = crew_source
        _window.open_crew_list()
        _window.update()
        return _window


class CrewListTests(WindowTestCase):

    def setUp(self):
        self.source = FakeCrewSource()
        self.window = self.make_window(self.source)

    def test_starts_on_crew_list(self):
        screen = self.window.current_screen
        self.assertIsInstance(screen, CrewListScreen)
        self.assertEqual(len(screen.cards), 6)

    def test_crew_card_shows_name_and_badges(self):
        card = self.window.current_screen.cards[1]
        self.assertEqual(card.name_label.cget("text"), "Astronaut 1")
        self.assertEqual(card.spo2_badge.value(), "96")
        self.assertEqual(card.bpm_badge.value(), "61")

    def test_click_on_card_label_opens_detail(self):
        card = self.window.current_screen.cards[3]
        # Click on the Tk widget inside the name label, like a user.
        card.name_label.winfo_children()[-1].event_generate("<Button-1>")
        self.window.update()
        screen = self.window.current_screen
        self.assertIsInstance(screen, CrewDetailScreen)
        self.assertEqual(screen.body_panel.value("muscle"), "33 kg")

    def test_refresh_keeps_cards(self):
        screen = self.window.current_screen
        card = screen.cards[1]
        calls = self.source.calls
        screen.refresh()
        self.assertIs(screen.cards[1], card)
        self.assertEqual(self.source.calls, calls + 1)

    def test_navigation_destroys_old_screen(self):
        old_screen = self.window.current_screen
        self.window.open_crew_detail(2)
        self.assertFalse(old_screen.winfo_exists())
        self.assertIsNone(old_screen._after_id)

    def test_crew_button_is_active(self):
        crew = self.window.nav_bar.button("crew")
        records = self.window.nav_bar.button("records")
        self.assertNotEqual(crew.cget("fg_color"), records.cget("fg_color"))


class CrewDetailTests(WindowTestCase):

    def setUp(self):
        self.window = self.make_window(FakeCrewSource())
        self.window.open_crew_detail(3)
        self.screen = self.window.current_screen

    def test_shows_every_value(self):
        screen = self.screen
        self.assertEqual(screen.vitals.value("temperature"), "36.8 °C")
        self.assertEqual(screen.vitals.value("pressure"), "12 mmHg")
        self.assertEqual(screen.body_panel.value("muscle"), "33 kg")
        self.assertEqual(screen.body_panel.value("bone"), "1.25 g/cm²")
        self.assertEqual(screen.wellness.value("stress"), "10/100")
        self.assertEqual(screen.wellness.value("sleep"), "7:30 hr")
        self.assertEqual(screen.cumulative.ring.text(), "15")
        self.assertEqual(screen.daily.ring.text(), "0.1")

    def test_missing_metric_shows_dashes(self):
        self.assertEqual(self.screen.wellness.value("fatigue"), "--")

    def test_back_button_returns_to_list(self):
        self.window.nav_bar.button("crew").invoke()
        self.assertIsInstance(self.window.current_screen, CrewListScreen)

    def test_unknown_astronaut(self):
        self.window.open_crew_detail(999)
        screen = self.window.current_screen
        self.assertIsInstance(screen, CrewDetailScreen)
        self.assertEqual(find_messages(screen), ["Astronaut not found"])


class MissingPartsTests(WindowTestCase):

    def test_screens_not_merged_show_message(self):
        window = self.make_window(FakeCrewSource())
        for key in ("diseases", "hazards", "treatments", "records"):
            window.nav_bar.button(key).invoke()
            screen = window.current_screen
            self.assertIsInstance(screen, MessageView)
            self.assertEqual(screen.title, "This screen is not ready yet")

    def test_without_backend(self):
        window = self.make_window(None)
        self.assertEqual(find_messages(window.current_screen),
                         [NOT_CONNECTED_TITLE])

    def test_empty_crew(self):
        window = self.make_window(FakeCrewSource(count=0))
        self.assertEqual(find_messages(window.current_screen),
                         ["No crew members yet"])


@unittest.skipUnless(config.database_path().exists(),
                     "no database in data/ (run scripts/create_demo_db.py)")
class RealCrewServiceTests(WindowTestCase):
    """The default window loads Person 1's crew service and database."""

    def test_default_window_uses_crew_service(self):
        from app.backend import crew_service

        self.assertIs(load_crew_service(), crew_service)
        window = self.make_window(load_crew_service())
        screen = window.current_screen
        self.assertIsInstance(screen, CrewListScreen)
        self.assertEqual(len(screen.cards), len(crew_service.list_crew()))
        if screen.cards:
            first_id = next(iter(screen.cards))
            window.open_crew_detail(first_id)
            self.assertIsInstance(window.current_screen, CrewDetailScreen)
            self.assertEqual(find_messages(window.current_screen), [])


if __name__ == "__main__":
    unittest.main()
